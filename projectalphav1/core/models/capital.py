"""
core.models.capital
- Shared capital-structure models used across apps (AM, ACQ, Treasury, Reporting).
- Mirrors DebtFacility while we transition from am_module.

Docs reviewed:
- Django model options (managed, db_table): https://docs.djangoproject.com/en/stable/ref/models/options/
- Django models: https://docs.djangoproject.com/en/stable/topics/db/models/
"""

from decimal import Decimal
from django.core.validators import MinValueValidator
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


class JVEquityPartner(models.Model):
    """DEPRECATED: This model is deprecated and will be removed in a future overhaul.
    
    Use the Fund model instead - it provides all JVEquityPartner fields plus:
    - Fund lifecycle tracking (inception, closes, maturity)
    - Fund status and type (JV, Commingled, SPV, etc.)
    - Enhanced waterfall structure
    - Investment strategy tracking
    
    DO NOT USE FOR NEW RECORDS. Migrate existing data to Fund model.
    """

    jv_name = models.CharField(max_length=255, null=True, blank=True)
    partner_firm_name = models.CharField(max_length=255, null=True, blank=True)
    partner_firm_email = models.EmailField(null=True, blank=True)
    partner_firm_phone = models.CharField(max_length=255, null=True, blank=True)

    commitment_size = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
        
    lp_percentage = models.PositiveIntegerField(null=True)
    gp_percentage = models.PositiveIntegerField(null=True)

    lp_promote = models.PositiveIntegerField(null=True)
    gp_promote = models.PositiveIntegerField(null=True)
    
    lp_contribution_paydown = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    
    gp_contribution_paydown = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    lp_pref = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    
    am_fees = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    
    acq_fees = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    
    fund_start_date = models.DateField(null=True)
    fund_maturity_date = models.DateField(null=True)
    
    class Meta:
        managed = True  # core now owns and manages the equity_partner table
        db_table = "equity_partner"
        verbose_name = "Equity Partner (DEPRECATED)"
        verbose_name_plural = "Equity Partners (DEPRECATED)"


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


class Fund(models.Model):
    """Investment fund tracking model.
    
    What: Master record for each investment fund/vehicle with structure and lifecycle details.
    Why: Centralized fund management for capital tracking, reporting, and investor relations.
    How: Tracks fund details, capital structure, fees, and key dates.
    """
    
    # Fund status choices using TextChoices
    class FundStatus(models.TextChoices):
        """Enum for fund lifecycle status"""
        FUNDRAISING = "fundraising", "Fundraising"
        ACTIVE = "active", "Active/Investing"
        HARVESTING = "harvesting", "Harvesting/Liquidating"
        CLOSED = "closed", "Closed"
        LIQUIDATED = "liquidated", "Fully Liquidated"
    
    # Fund type choices
    class FundType(models.TextChoices):
        """Enum for fund structure type"""
        COMMINGLED = "commingled", "Commingled Fund"
        SEPARATE_ACCOUNT = "separate_account", "Separate Account"
        JV = "jv", "Joint Venture"
        SPV = "spv", "Special Purpose Vehicle"
        OTHER = "other", "Other"
    
    # Basic fund information
    fund_name = models.CharField(
        max_length=255,
        help_text="Official fund name"
    )
    
    fund_type = models.CharField(
        max_length=50,
        choices=FundType.choices,
        default=FundType.COMMINGLED,
        help_text="Fund structure type"
    )
    
    fund_status = models.CharField(
        max_length=50,
        choices=FundStatus.choices,
        default=FundStatus.FUNDRAISING,
        help_text="Current fund lifecycle status"
    )
    
    # Capital structure
    target_fund_size = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Target total capital to raise"
    )
    
    total_commitments = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total committed capital from all investors"
    )
    
    total_funded = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total capital actually contributed/funded"
    )
    
    # Fund lifecycle dates
    inception_date = models.DateField(
        null=True,
        blank=True,
        help_text="Fund inception/formation date"
    )
    
    first_close_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of first capital close"
    )
    
    final_close_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of final capital close"
    )
    
    investment_period_end = models.DateField(
        null=True,
        blank=True,
        help_text="End of investment period"
    )
    
    fund_term_years = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Fund term in years (e.g., 10)"
    )
    
    maturity_date = models.DateField(
        null=True,
        blank=True,
        help_text="Fund maturity/termination date"
    )
    
    # Fee structure
    management_fee_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual management fee percentage (e.g., 1.50 for 1.5%)"
    )
    
    acquisition_fee_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Acquisition fee percentage (e.g., 1.00 for 1%)"
    )
    
    disposition_fee_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Disposition fee percentage (e.g., 1.00 for 1%)"
    )
    
    # Absolute fee amounts (in addition to percentages)
    am_fees = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Asset management fees (absolute dollar amount)"
    )
    
    acq_fees = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Acquisition fees (absolute dollar amount)"
    )
    
    # Ownership split (LP/GP percentages)
    lp_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="LP ownership percentage (e.g., 80.00 for 80%)"
    )
    
    gp_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="GP ownership percentage (e.g., 20.00 for 20%)"
    )
    
    # Contribution paydowns (actual amounts contributed by LP/GP)
    lp_contribution_paydown = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual LP capital contributed/paid down"
    )
    
    gp_contribution_paydown = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual GP capital contributed/paid down"
    )
    
    # Waterfall/promote structure
    preferred_return_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Preferred return hurdle rate (e.g., 8.00 for 8%)"
    )
    
    lp_promote = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="LP promote percentage after hurdle (e.g., 80.00 for 80%)"
    )
    
    gp_promote_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="GP promote/carried interest percentage (e.g., 20.00 for 20%)"
    )
    
    gp_catchup_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="GP catch-up percentage (e.g., 100.00 for 100%)"
    )
    
    # Investment strategy and focus
    investment_strategy = models.TextField(
        null=True,
        blank=True,
        help_text="Description of investment strategy and focus"
    )
    
    target_geography = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Target geographic focus (e.g., 'US Nationwide', 'Southeast US')"
    )
    
    # Additional details
    legal_entity_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Legal entity name (if different from fund name)"
    )
    
    tax_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Tax ID/EIN"
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Additional notes about the fund"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        db_table = "fund"
        ordering = ["-inception_date", "fund_name"]
        verbose_name = "Fund"
        verbose_name_plural = "Funds"
    
    def __str__(self):
        """String representation showing fund name and status"""
        return f"{self.fund_name} ({self.get_fund_status_display()})"
    
    def capital_called_pct(self):
        """Calculate percentage of commitments that have been funded"""
        if self.total_commitments and self.total_commitments > 0:
            return (self.total_funded or Decimal('0.00')) / self.total_commitments * 100
        return Decimal('0.00')
    
    def remaining_commitment(self):
        """Calculate remaining uncalled capital"""
        return (self.total_commitments or Decimal('0.00')) - (self.total_funded or Decimal('0.00'))