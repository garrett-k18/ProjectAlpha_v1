"""
core.models.capital
- Shared capital-structure models used across apps (AM, ACQ, Treasury, Reporting).
- Mirrors DebtFacility while we transition from am_module.

Docs reviewed:
- Django model options (managed, db_table): https://docs.djangoproject.com/en/stable/ref/models/options/
- Django models: https://docs.djangoproject.com/en/stable/topics/db/models/
"""

from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class DebtFacility(models.Model):
    """Shared Debt Facility model (currently managed=True, as core now owns and manages the debt_facility table).
    This mirrors am_module.models.capital.DebtFacility fields so other apps can
    begin importing from core without changing the physical table yet.
    """

    facility_name = models.CharField(max_length=255, null=True, blank=True)
    firm_name = models.CharField(max_length=255, null=True, blank=True)
    firm_email = models.EmailField(null=True, blank=True)
    firm_phone = models.CharField(max_length=255, null=True, blank=True)

    commitment_size = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # Fixed to SOFR for now
    rate_index = models.CharField(max_length=16, default="SOFR", null=True, blank=True)
    sofr_rate = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        null=True,
        blank=True,
    )

    spread_bps = models.PositiveIntegerField(null=True)

    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True  # core now owns and manages the debt_facility table
        db_table = "debt_facility"
        ordering = ["-created_at"]
        verbose_name = "Debt Facility"
        verbose_name_plural = "Debt Facilities"


class CoInvestor(models.Model):
    """Parent Co-Investor model tracking investor relationships and commitments.
    
    What: Master record for each co-investor with commitment and ownership details.
    Why: Centralized investor tracking with full contribution/distribution history via child models.
    How: Links to MasterCRM for contact info; child models track all transactions.
    """

    # Link to MasterCRM for contact name and information
    crm_contact = models.ForeignKey(
        'MasterCRM',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='co_investor_records',
        help_text="Link to CRM contact for investor name and contact information"
    )

    # Commitment and ownership
    commitment_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total committed capital amount"
    )
    
    ownership_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ownership percentage (e.g., 25.50 for 25.5%)"
    )

    # Status and metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this investor is currently active"
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Additional notes about the investor"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "co_investor"
        ordering = ["-created_at"]
        verbose_name = "Co-Investor"
        verbose_name_plural = "Co-Investors"
    
    def __str__(self):
        """String representation showing investor name from CRM"""
        if self.crm_contact:
            return f"{self.crm_contact.contact_name} ({self.crm_contact.firm})"
        return f"Co-Investor #{self.pk}"
    
    def total_contributed(self):
        """Calculate total contributions from all contribution records"""
        from django.db.models import Sum
        total = self.contributions.aggregate(Sum('amount'))['amount__sum']
        return total or Decimal('0.00')
    
    def total_distributed(self):
        """Calculate total distributions from all distribution records"""
        from django.db.models import Sum
        total = self.distributions.aggregate(Sum('amount'))['amount__sum']
        return total or Decimal('0.00')
    
    def net_position(self):
        """Calculate net position (contributions - distributions)"""
        return self.total_contributed() - self.total_distributed()


class InvestorContribution(models.Model):
    """Individual contribution transactions for co-investors.
    
    What: Tracks each capital contribution event with date, amount, and details.
    Why: Maintains full contribution history for reporting and audit trail.
    How: Many-to-one relationship with CoInvestor parent.
    """
    
    # Parent relationship
    co_investor = models.ForeignKey(
        CoInvestor,
        on_delete=models.CASCADE,
        related_name='contributions',
        help_text="Co-investor who made this contribution"
    )
    
    # Contribution details
    contribution_date = models.DateField(
        help_text="Date when capital was contributed"
    )
    
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Contribution amount"
    )
    
    payment_method = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Payment method (wire, check, ACH, etc.)"
    )
    
    reference_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Payment reference or transaction number"
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Additional notes about this contribution"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        db_table = "investor_contribution"
        ordering = ["-contribution_date", "-created_at"]
        verbose_name = "Investor Contribution"
        verbose_name_plural = "Investor Contributions"
    
    def __str__(self):
        """String representation showing investor, date, and amount"""
        return f"{self.co_investor} - ${self.amount:,.2f} on {self.contribution_date}"


class InvestorDistribution(models.Model):
    """Individual distribution transactions to co-investors.
    
    What: Tracks each distribution event with date, amount, type, and details.
    Why: Maintains full distribution history for investor statements and tax reporting.
    How: Many-to-one relationship with CoInvestor parent.
    """
    
    # Distribution type choices using TextChoices
    class DistributionType(models.TextChoices):
        """Enum for distribution categorization"""
        RETURN_OF_CAPITAL = "return_of_capital", "Return of Capital"
        PROFIT_DISTRIBUTION = "profit_distribution", "Profit Distribution"
        PREFERRED_RETURN = "preferred_return", "Preferred Return"
        PROMOTE = "promote", "Promote/Carried Interest"
        OTHER = "other", "Other"
    
    # Parent relationship
    co_investor = models.ForeignKey(
        CoInvestor,
        on_delete=models.CASCADE,
        related_name='distributions',
        help_text="Co-investor receiving this distribution"
    )
    
    # Distribution details
    distribution_date = models.DateField(
        help_text="Date when distribution was made"
    )
    
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Distribution amount"
    )
    
    distribution_type = models.CharField(
        max_length=50,
        choices=DistributionType.choices,
        default=DistributionType.PROFIT_DISTRIBUTION,
        help_text="Type of distribution"
    )
    
    payment_method = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Payment method (wire, check, ACH, etc.)"
    )
    
    reference_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Payment reference or transaction number"
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Additional notes about this distribution"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        db_table = "investor_distribution"
        ordering = ["-distribution_date", "-created_at"]
        verbose_name = "Investor Distribution"
        verbose_name_plural = "Investor Distributions"
    
    def __str__(self):
        """String representation showing investor, date, and amount"""
        return f"{self.co_investor} - ${self.amount:,.2f} on {self.distribution_date}"


# =============================================================================
# NEW FUND ADMINISTRATION MODELS
# =============================================================================
# The models below provide a cleaner structure for fund administration,
# GP/LP tracking, and nested entity ownership.
# =============================================================================


class Entity(models.Model):
    """Any legal entity - individuals, LLCs, trusts, corporations, etc.
    
    What: Universal entity model for all participants in fund structures
    Why: Track everyone from individual GPs to corporate LPs with consistent interface
    How: Flexible entity_type field allows any legal structure
    
    Examples:
    - John Smith (individual GP member)
    - GPM, LLC (GP entity that manages the fund)
    - ABC Pension Fund (LP investor)
    - XYZ Trust (trust investor)
    
    Docs reviewed:
    - Django models: https://docs.djangoproject.com/en/stable/topics/db/models/
    """
    
    class EntityType(models.TextChoices):
        """Entity type classification"""
        FUND = "fund", "Fund"
        INDIVIDUAL = "individual", "Individual"
        LLC = "llc", "LLC"
        JV = "jv", "Joint Venture"
        CORPORATION = "corporation", "Corporation"
        PARTNERSHIP = "partnership", "Partnership"
        SPV = "spv", "SPV"
        TRUST = "trust", "Trust"
        OTHER = "other", "Other"
    
    # Basic information
    name = models.CharField(
        max_length=255,
        help_text="Entity name (person name, company name, trust name, etc.)"
    )
    
    entity_type = models.CharField(
        max_length=50,
        choices=EntityType.choices,
        help_text="Type of legal entity"
    )
    
    # Contact information
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Tax ID/EIN/SSN"
    )
    
    email = models.EmailField(
        blank=True,
        help_text="Primary email contact"
    )
    
    phone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary phone contact"
    )
    
    # Status and metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this entity is currently active"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the entity"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        db_table = "entity"
        ordering = ["name"]
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
    
    def __str__(self):
        """String representation showing entity name"""
        return self.name


class FundLegalEntity(models.Model):
    """Legal entity names for a fund (master, feeders, SPVs, GP entities, etc.)
    
    What: Tracks the various legal entities that make up a fund structure
    Why: Funds often have multiple entities (master fund, domestic feeder, offshore feeder, SPVs)
    How: Links legal entities to their parent Fund with role classification
    
    Examples:
    - "ABC Homes Fund I, LP" (master fund entity)
    - "ABC Homes Domestic Feeder, LP" (domestic feeder)
    - "ABC Homes SPV 2024-01, LLC" (deal-specific SPV)
    - "ABC Homes GP, LLC" (GP entity)
    
    Docs reviewed:
    - Django ForeignKey: https://docs.djangoproject.com/en/stable/ref/models/fields/#foreignkey
    """
    
    class EntityRole(models.TextChoices):
        """Entity role in fund structure"""
        FUND = "fund", "Fund"
        GP = "gp", "GP"
        LP = "lp", "LP"
        SPV = "spv", "SPV"
    
    # Parent fund relationship (Entity record flagged as a fund)
    fund = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='legal_entities',
        help_text="Entity that this fund legal entity belongs to (no type restriction)"
    )
    
    # Legal entity details
    nickname_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Internal nickname/alias for this legal entity"
    )
    
    entity_role = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=EntityRole.choices,
        help_text="Role this entity plays in the fund structure"
    )
    
    jurisdiction = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="State/country of formation (e.g., Delaware, Cayman Islands)"
    )
    
    tax_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Tax ID/EIN for this entity"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this entity is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        db_table = "fund_legal_entity"
        ordering = ["fund", "entity_role", "legal_name"]
        verbose_name = "Fund Legal Entity"
        verbose_name_plural = "Fund Legal Entities"
    
    def __str__(self):
        """String representation showing legal name and fund"""
        return f"{self.legal_name} - {self.fund.name}"


class FundMembership(models.Model):
    """Entity membership in a fund (GP, LP, etc.)
    
    What: Tracks which entities are members of which funds and their capital commitments
    Why: Core fund accounting - track GP/LP members, capital calls, contributions
    How: Junction model linking Entity to Fund with member-specific details
    
    Examples:
    - GPM, LLC is GP of ABC Homes Fund I with 20% ownership
    - XYZ Pension Fund is LP with $10M commitment
    - John Smith (via GPM, LLC) is indirect owner
    
    Docs reviewed:
    - Django unique_together: https://docs.djangoproject.com/en/stable/ref/models/options/#unique-together
    - Django validators: https://docs.djangoproject.com/en/stable/ref/validators/
    """
    
    class MemberType(models.TextChoices):
        """Member type in fund"""
        GP = "gp", "General Partner"
        LP = "lp", "Limited Partner"
        CO_INVESTOR = "co_investor", "Co-Investor"
        SPV = "spv", "Special Purpose Vehicle"
        OTHER = "other", "Other"
    
    class MemberStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        PENDING = "pending", "Pending"
    
    # Relationships
    fund = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='memberships',
        help_text="Entity representing the fund this membership belongs to"
    )
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.PROTECT,
        related_name='fund_memberships',
        help_text="Entity that is a member (GP or LP)"
    )
    
    # Member classification
    member_type = models.CharField(
        max_length=20,
        choices=MemberType.choices,
        help_text="GP or LP designation"
    )
    
    admission_date = models.DateField(
        help_text="Date when entity joined the fund"
    )
    
    # Ownership and capital
    ownership_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Ownership percentage in fund (e.g., 20.00 for 20%)"
    )
    
    capital_committed = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total capital commitment"
    )
    
    capital_contributed = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Capital actually contributed to date"
    )
    
    # Optional: track which legal entity they're investing through
    investing_through = models.ForeignKey(
        FundLegalEntity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        help_text="Optional: specific fund legal entity they're investing through (e.g., domestic vs offshore feeder)"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this membership is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        db_table = "fund_membership"
        unique_together = [['fund', 'entity']]
        ordering = ["fund", "member_type", "-ownership_percentage"]
        verbose_name = "Fund Membership"
        verbose_name_plural = "Fund Memberships"
    
    def __str__(self):
        """String representation showing entity and fund"""
        return f"{self.entity.name} in {self.fund.name}"
    
    def remaining_commitment(self):
        """Calculate uncalled capital"""
        return self.capital_committed - self.capital_contributed


class EntityMembership(models.Model):
    """Nested ownership - tracks who owns pieces of an Entity
    
    What: Models ownership within entities (e.g., John owns 30% of GPM, LLC)
    Why: Track ultimate beneficial ownership and GP member interests
    How: Self-referential entity-to-entity ownership with percentages
    
    Examples:
    - John Smith owns 30% of GPM, LLC
    - Jane Doe owns 40% of GPM, LLC
    - XYZ Trust owns 30% of GPM, LLC
    
    Use Cases:
    - GP member tracking (who owns the GP entity?)
    - Ultimate beneficial ownership calculations
    - Distribution waterfall calculations (fund → GP entity → GP members)
    - K-1 preparation (need to know individual ownership)
    
    Docs reviewed:
    - Django self-referential FK: https://docs.djangoproject.com/en/stable/ref/models/fields/#recursive-relationships
    """
    
    # Ownership relationship
    parent_entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='child_members',
        help_text="The entity being owned (e.g., GPM, LLC)"
    )
    
    member_entity = models.ForeignKey(
        Entity,
        on_delete=models.PROTECT,
        related_name='parent_memberships',
        help_text="The entity that owns a piece (e.g., John Smith)"
    )
    
    # Ownership details
    ownership_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Percentage ownership in parent entity"
    )
    
    membership_date = models.DateField(
        help_text="When they became a member/owner"
    )
    
    # Capital account tracking
    capital_account = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Current capital account balance"
    )
    
    # Distribution percentage (if different from ownership)
    distribution_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Distribution % if different from ownership % (optional)"
    )
    
    # Status and metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this membership is currently active"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this membership"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        db_table = "entity_membership"
        unique_together = [['parent_entity', 'member_entity']]
        ordering = ['parent_entity', '-ownership_percentage']
        verbose_name = "Entity Membership"
        verbose_name_plural = "Entity Memberships"
    
    def __str__(self):
        """String representation showing ownership relationship"""
        return f"{self.member_entity.name} owns {self.ownership_percentage}% of {self.parent_entity.name}"
    
    def effective_distribution_percentage(self):
        """Get distribution percentage (falls back to ownership if not set)"""
        return self.distribution_percentage if self.distribution_percentage is not None else self.ownership_percentage