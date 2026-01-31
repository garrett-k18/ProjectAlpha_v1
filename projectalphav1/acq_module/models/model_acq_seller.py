#Seller Data Django Model. Contains Seller, Trade and Raw Data models

from django.db import models
from django.utils import timezone
import re


class Seller(models.Model):
    """One seller can have many trades...Need to make sure IDs start at 1000"""
    name = models.CharField(max_length=100)
    broker = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    poc = models.CharField(max_length=100, null=True, blank=True)

    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Seller"
        verbose_name_plural = "Sellers"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]


class Trade(models.Model):
    """Deal container for assets; seller is optional for non-loan asset types."""
    seller = models.ForeignKey(
        Seller,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trades',
        help_text='Nullable to support asset types without a seller (e.g., REO, single-asset equity).'
    )
    trade_name = models.CharField(
        max_length=100,
        blank=True,  # Editable; if left blank we'll auto-generate on save
    )
    class Status(models.TextChoices):
        PASS = 'PASS', 'Pass'
        INDICATIVE = 'INDICATIVE', 'Indicative'
        DD = 'DD', 'Due Diligence'
        AWARDED = 'AWARDED', 'Awarded'
        CLOSED = 'CLOSED', 'Closed'
        BOARD = 'BOARD', 'Boarded'
      
    # Timestamps for trade lifecycle
    # Note: Per Django docs, auto_now/auto_now_add cannot be combined with default
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INDICATIVE,
        db_index=True,
    )
   
    
    def __str__(self):
        if self.deal_name:
            return self.deal_name
        seller_name = self.seller.name if self.seller else "Unknown Seller"
        return f"Deal for {seller_name}"

    @property
    def deal_name(self) -> str:
        """Alias for trade_name to support deal-centric naming."""
        return self.trade_name

    @deal_name.setter
    def deal_name(self, value: str) -> None:
        """Write-through alias for trade_name."""
        self.trade_name = value

    def save(self, *args, **kwargs):
        """Save trade instance.
        
        Note: Trade name generation moved to ETL process for better context and AI integration.
        If trade_name is blank, it should be set by the ETL process before saving.
        """
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Deal"
        verbose_name_plural = "Deals"
        ordering = ['trade_name']
        indexes = [
            models.Index(fields=['seller']),
        ]
        db_table = "acq_module_trade"

    def refresh_status_from_assets(self, commit: bool = True):
        """Update trade status based on active (KEEP) assets.
        
        WHAT: Check if trade has any active assets (acq_status=KEEP)
        WHY: Trade status should reflect whether it has bidding-eligible assets
        HOW: If all assets are DROPped, suggest archiving trade (PASS status)
        
        Note: This is a suggestion only. User controls trade status manually.
        Asset-level status (KEEP/DROP) is independent of trade-level status.
        """
        # WHAT: Count active (KEEP) assets in this trade
        # WHY: Determine if trade still has assets in the active pool
        active_asset_count = self.acq_assets.filter(
            acq_status=AcqAsset.AcquisitionStatus.KEEP
        ).count()
        
        # WHAT: If all assets are dropped and trade not already archived, suggest archiving
        # WHY: Empty trades should typically be archived (PASS status)
        # HOW: Only auto-archive if trade is in DD/INDICATIVE (not AWARDED/BOARD/PASS)
        if active_asset_count == 0:
            # Don't auto-change if trade is already in terminal status (AWARDED, BOARD, PASS)
            if self.status not in [self.Status.AWARDED, self.Status.BOARD, self.Status.PASS]:
                computed = self.Status.PASS
                if self.status != computed:
                    self.status = computed
                    if commit:
                        self.save(update_fields=['status'])

Trade_Deal = Trade


class AcqAsset(models.Model):
    """
    Core cross-industry asset container for acquisitions.

    WHAT: Holds asset-level identifiers and deal context (no property/loan specifics).
    WHY: Supports non-loan assets (REO, single-asset equity, commercial, etc.).
    HOW: 1:1 with AssetIdHub; optional Seller/Trade for non-seller assets.
    """

    # ===== Enumerations =====
    class AcquisitionStatus(models.TextChoices):
        """Asset-level inclusion status for deal workflows."""
        KEEP = 'KEEP', 'Keep'  # In active pool
        DROP = 'DROP', 'Drop'  # Excluded from active pool

    class AssetClass(models.TextChoices):
        """Primary asset class classification."""
        REAL_ESTATE_1_4 = 'REAL_ESTATE_1_4', 'Real Estate 1-4'
        MULTIFAMILY_5_PLUS = 'MULTIFAMILY_5_PLUS', 'Multifamily 5+'
        COMMERCIAL = 'COMMERCIAL', 'Commercial'
        PERFORMING_NOTE = 'PERFORMING_NOTE', 'Performing Note'
        NPL = 'NPL', 'NPL'

    class AssetStatus(models.TextChoices):
        """Legacy asset status used by modeling logic (tape-driven)."""
        NPL = 'NPL', 'NPL'       # Non-Performing Loan
        REO = 'REO', 'REO'       # Real Estate Owned
        PERF = 'PERF', 'PERF'    # Performing
        RPL = 'RPL', 'RPL'       # Re-Performing Loan

    class NoteSubclass(models.TextChoices):
        """Subclass for note asset class (Performing/NPL/RPL)."""
        NPL = 'NPL', 'NPL'       # Non-Performing Loan
        PERF = 'PERF', 'PERF'    # Performing
        RPL = 'RPL', 'RPL'       # Re-Performing Loan

    class RealEstateSubclass(models.TextChoices):
        """Subclass for 1-4 unit real estate assets."""
        SFR = 'SFR', 'Single Family'
        CONDO = 'Condo', 'Condo'
        TOWNHOUSE = 'Townhouse', 'Townhouse'
        TWO_FOUR = '2-4 Family', '2-4 Family'
        MANUFACTURED = 'Manufactured', 'Manufactured'
        LAND = 'Land', 'Land'

    class MultifamilySubclass(models.TextChoices):
        """Subclass for multifamily 5+ assets."""
        GARDEN = 'Garden', 'Garden'
        MID_RISE = 'Mid-Rise', 'Mid-Rise'
        HIGH_RISE = 'High-Rise', 'High-Rise'
        STUDENT = 'Student', 'Student Housing'
        SENIOR = 'Senior', 'Senior Housing'
        AFFORDABLE = 'Affordable', 'Affordable Housing'

    class CommercialSubclass(models.TextChoices):
        """Subclass for commercial assets."""
        OFFICE = 'Office', 'Office'
        RETAIL = 'Retail', 'Retail'
        INDUSTRIAL = 'Industrial', 'Industrial'
        MIXED_USE = 'Mixed Use', 'Mixed Use'
        STORAGE = 'Storage', 'Storage'
        HOSPITALITY = 'Hospitality', 'Hospitality'
        HEALTHCARE = 'Healthcare', 'Healthcare'

    # ===== Relationships =====
    # WHAT: Hub-owned primary key - strict 1:1 with core.AssetIdHub
    # WHY: Aligns with hub-first architecture for cross-module joins
    # HOW: OneToOneField with primary_key=True
    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='acq_asset',
        help_text='1:1 with hub; this model\'s PK equals the hub ID.',
    )
    # WHAT: Optional seller reference (nullable for non-seller assets)
    # WHY: REO and equity may not have a seller entity
    # HOW: SET_NULL to preserve asset if seller is deleted
    seller = models.ForeignKey(
        Seller,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acq_assets',
        help_text='Nullable reference for assets without a seller.',
    )
    # WHAT: Optional deal reference
    # WHY: Some assets are stand-alone without a deal container
    # HOW: SET_NULL to preserve asset if deal is deleted
    trade = models.ForeignKey(
        Trade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acq_assets',
        help_text='Nullable reference for assets not tied to a deal.',
    )

    # ===== Status fields =====
    # WHAT: Legacy asset status for model recommendations and legacy filters
    # WHY: Modeling logic still uses NPL/REO/PERF/RPL status codes
    # HOW: Nullable choice field, populated during import when available
    asset_status = models.CharField(
        max_length=100,
        choices=AssetStatus.choices,
        null=True,
        blank=True,
    )
    # WHAT: Keep/Drop filter status
    # WHY: Supports pipeline selection and trade-level rollups
    # HOW: Default KEEP for new assets
    acq_status = models.CharField(
        max_length=20,
        choices=AcquisitionStatus.choices,
        default=AcquisitionStatus.KEEP,
        db_index=True,
        help_text='Asset-level status: KEEP (in active pool) or DROP (excluded).',
    )
    # WHAT: Primary asset class (used to drive downstream subtype behavior)
    # WHY: Each asset class has its own subtype semantics
    # HOW: Enum choices with explicit class labels
    asset_class = models.CharField(
        max_length=30,
        choices=AssetClass.choices,
        null=True,
        blank=True,
        help_text='Primary asset class (Real Estate 1-4, Multifamily 5+, Commercial, Performing Note, NPL).',
    )
    # ===== Class-specific subtype fields =====
    # WHAT: Subtype for Real Estate 1-4 assets
    # WHY: Capture class-specific subtypes without overloading a single field
    # HOW: Nullable choice field; only populate when asset_class=REAL_ESTATE_1_4
    real_estate_subclass_type = models.CharField(
        max_length=20,
        choices=RealEstateSubclass.choices,
        null=True,
        blank=True,
        help_text='Subtype for Real Estate 1-4 assets (only when asset_class=REAL_ESTATE_1_4).',
    )
    # WHAT: Subtype for Multifamily 5+ assets
    # WHY: Capture class-specific subtypes without overloading a single field
    # HOW: Nullable choice field; only populate when asset_class=MULTIFAMILY_5_PLUS
    multifamily_subclass_type = models.CharField(
        max_length=20,
        choices=MultifamilySubclass.choices,
        null=True,
        blank=True,
        help_text='Subtype for Multifamily 5+ assets (only when asset_class=MULTIFAMILY_5_PLUS).',
    )
    # WHAT: Subtype for Commercial assets
    # WHY: Capture class-specific subtypes without overloading a single field
    # HOW: Nullable choice field; only populate when asset_class=COMMERCIAL
    commercial_subclass_type = models.CharField(
        max_length=20,
        choices=CommercialSubclass.choices,
        null=True,
        blank=True,
        help_text='Subtype for Commercial assets (only when asset_class=COMMERCIAL).',
    )
    # WHAT: Subclass for note assets (Performing/NPL/RPL)
    # WHY: This is the note-specific subclass classification
    # HOW: Nullable choice field; only populate for note-related asset_class values
    note_subclass_type = models.CharField(
        max_length=10,
        choices=NoteSubclass.choices,
        null=True,
        blank=True,
        help_text='Subclass for note assets (only when asset_class=PERFORMING_NOTE or NPL).',
    )


    # WHAT: As-of date for tape snapshot
    # WHY: Needed for time-based analysis and data freshness
    # HOW: Nullable DateField
    as_of_date = models.DateField(null=True, blank=True)

    # ===== Timestamps =====
    # WHAT: Automatic timestamp tracking
    # WHY: Track when assets are created/updated
    # HOW: Django auto_now_add/auto_now
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_dropped(self) -> bool:
        """Return True when acquisition status is Drop for compatibility."""
        return self.acq_status == self.AcquisitionStatus.DROP

    def get_property_type_from_subclass(self):
        """
        WHAT: Resolve a unified property type from asset subclass fields.
        WHY: Use subclass values as the single frontend property type.
        HOW: Return the subclass value based on asset_class.
        """
        # WHAT: 1-4 residential subclasses
        # WHY: These are the desired property type values for 1-4 assets
        # HOW: Return the stored subclass value directly
        if self.asset_class == self.AssetClass.REAL_ESTATE_1_4:
            return self.real_estate_subclass_type

        # WHAT: Multifamily subclasses
        # WHY: Use subclass labels (Garden, Mid-Rise, etc.)
        # HOW: Return the stored subclass value directly
        if self.asset_class == self.AssetClass.MULTIFAMILY_5_PLUS:
            return self.multifamily_subclass_type

        # WHAT: Commercial subclasses
        # WHY: Use subclass labels (Office, Retail, etc.)
        # HOW: Return the stored subclass value directly
        if self.asset_class == self.AssetClass.COMMERCIAL:
            return self.commercial_subclass_type

        # WHAT: Notes and non-property assets
        # WHY: These are not property assets
        # HOW: Return None so callers can handle as non-property
        return None

    # -------------------------------------------------------------------------
    # Legacy field compatibility properties (read-only)
    # -------------------------------------------------------------------------
    # NOTE: These properties provide a compatibility layer for code that
    # previously accessed SellerRawData fields directly. They should be treated
    # as read-only projections from the related AcqLoan/AcqProperty records.

    @property
    def sellertape_id(self):
        """Legacy alias for loan.sellertape_id."""
        loan = getattr(self, "loan", None)
        return loan.sellertape_id if loan else None

    @property
    def sellertape_altid(self):
        """Legacy alias for loan.sellertape_altid."""
        loan = getattr(self, "loan", None)
        return loan.sellertape_altid if loan else None

    @property
    def current_balance(self):
        """Legacy alias for loan.current_balance."""
        loan = getattr(self, "loan", None)
        return loan.current_balance if loan else None

    @property
    def total_debt(self):
        """Legacy alias for loan.total_debt."""
        loan = getattr(self, "loan", None)
        return loan.total_debt if loan else None

    @property
    def interest_rate(self):
        """Legacy alias for loan.interest_rate."""
        loan = getattr(self, "loan", None)
        return loan.interest_rate if loan else None

    @property
    def default_rate(self):
        """Legacy alias for loan.default_rate."""
        loan = getattr(self, "loan", None)
        return loan.default_rate if loan else None

    @property
    def maturity_date(self):
        """Legacy alias for loan.current_maturity_date (fallback to original)."""
        loan = getattr(self, "loan", None)
        if not loan:
            return None
        return loan.current_maturity_date or loan.original_maturity_date

    @property
    def months_delinquent(self):
        """Legacy alias for loan.months_dlq."""
        loan = getattr(self, "loan", None)
        return loan.months_dlq if loan else None

    @property
    def street_address(self):
        """Legacy alias for property.street_address."""
        prop = getattr(self, "property", None)
        return prop.street_address if prop else None

    @property
    def city(self):
        """Legacy alias for property.city."""
        prop = getattr(self, "property", None)
        return prop.city if prop else None

    @property
    def state(self):
        """Legacy alias for property.state."""
        prop = getattr(self, "property", None)
        return prop.state if prop else None

    @property
    def zip(self):
        """Legacy alias for property.zip."""
        prop = getattr(self, "property", None)
        return prop.zip if prop else None

    @property
    def bedrooms(self):
        """Legacy alias for property.beds."""
        prop = getattr(self, "property", None)
        return prop.beds if prop else None

    @property
    def bathrooms(self):
        """Legacy alias for property.baths."""
        prop = getattr(self, "property", None)
        return prop.baths if prop else None

    @property
    def sqft(self):
        """Legacy alias for property.sq_ft."""
        prop = getattr(self, "property", None)
        return prop.sq_ft if prop else None

    @property
    def lot_size(self):
        """Legacy alias for property.lot_size."""
        prop = getattr(self, "property", None)
        return prop.lot_size if prop else None

    @property
    def year_built(self):
        """Legacy alias for property.year_built."""
        prop = getattr(self, "property", None)
        return prop.year_built if prop else None

    @property
    def occupancy(self):
        """Legacy alias for property.occupancy."""
        prop = getattr(self, "property", None)
        return prop.occupancy if prop else None

    @property
    def product_type(self):
        """Legacy alias for loan.product_type."""
        loan = getattr(self, "loan", None)
        return loan.product_type if loan else None

    @property
    def property_type(self):
        """Legacy alias for property.property_type_merged."""
        prop = getattr(self, "property", None)
        return prop.property_type_merged if prop else None

    class Meta:
        verbose_name = "Acquisition Asset"
        verbose_name_plural = "Acquisition Assets"
        indexes = [
            models.Index(fields=['asset_hub']),
            models.Index(fields=['acq_status']),
            models.Index(fields=['asset_class']),
            models.Index(fields=['asset_status']),
            models.Index(fields=['seller']),
            models.Index(fields=['trade']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        """Human-readable label for admin and logs."""
        seller_name = self.seller.name if self.seller else "Unassigned Seller"
        trade_name = self.trade.trade_name if self.trade else "Unassigned Deal"
        return f"AcqAsset {self.pk} - {seller_name} - {trade_name}"


class AcqLoan(models.Model):
    """
    Loan/borrower/servicing data tied to an acquisition asset.

    WHAT: Stores loan-specific fields (balances, rates, terms, borrower names).
    WHY: Separates loan data from property data for cross-industry support.
    HOW: 1:1 with AcqAsset (nullable loans are allowed by omission).
    """

    class ProductType(models.TextChoices):
        """Loan product type classification."""
        BPL = 'BPL', 'BPL'
        HECM = 'HECM', 'HECM'
        VA = 'VA', 'VA'
        CONV = 'Conv', 'Conv'
        COMMERCIAL = 'Commercial', 'Commercial'
        Bridge = 'Bridge', 'Bridge'

    # WHAT: 1:1 link to asset container
    # WHY: Each asset may have at most one loan record
    # HOW: OneToOneField with primary_key=True
    asset = models.OneToOneField(
        AcqAsset,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='loan',
        help_text='1:1 link to acquisition asset.',
    )

    # ===== Note identifiers =====
    # WHAT: Seller-provided primary identifier (raw tape ID)
    # WHY: Needed for traceability and matching on note assets
    # HOW: CharField to allow any format (numeric/alphanumeric)
    sellertape_id = models.CharField(max_length=100)
    # WHAT: Seller-provided alternate identifier
    # WHY: Some tapes include multiple identifiers for the same note
    # HOW: Optional CharField
    sellertape_altid = models.CharField(max_length=100, null=True, blank=True)

    # ===== Borrower names (non-PII) =====
    borrower1_last = models.CharField(max_length=100, null=True, blank=True, help_text="If entity, put entity in borrower1_last.")
    borrower1_first = models.CharField(max_length=100, null=True, blank=True)
    borrower2_last = models.CharField(max_length=100, null=True, blank=True)
    borrower2_first = models.CharField(max_length=100, null=True, blank=True)

    # ===== Loan financials =====
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    deferred_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    last_paid_date = models.DateField(null=True, blank=True)
    first_pay_date = models.DateField(null=True, blank=True)
    origination_date = models.DateField(null=True, blank=True)
    original_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    original_term = models.IntegerField(null=True, blank=True)
    original_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    original_maturity_date = models.DateField(null=True, blank=True)

    # ===== Origination valuation =====
    # WHAT: Origination as-is value (market value at origination)
    # WHY: Needed for legacy cap rate and origination analytics
    # HOW: Decimal value with optional date
    origination_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    # WHAT: Origination ARV value
    # WHY: Capture rehab-adjusted value at origination when provided
    # HOW: Optional DecimalField
    origination_arv = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    # WHAT: Origination value date
    # WHY: Time alignment for origination analytics
    # HOW: Optional DateField
    origination_value_date = models.DateField(null=True, blank=True)
    default_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    months_dlq = models.IntegerField(null=True, blank=True)
    current_maturity_date = models.DateField(null=True, blank=True)
    current_term = models.IntegerField(null=True, blank=True)

    # ===== Loan fees/advances =====
    accrued_note_interest = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    accrued_default_interest = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    escrow_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    escrow_advance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    recoverable_corp_advance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    late_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    other_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    suspense_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_debt = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # ===== Loan product =====
    product_type = models.CharField(
        max_length=50,
        choices=ProductType.choices,
        null=True,
        blank=True,
    )

    # ===== Timestamps =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Acquisition Loan"
        verbose_name_plural = "Acquisition Loans"
        indexes = [
            models.Index(fields=['asset']),
            models.Index(fields=['product_type']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"AcqLoan for Asset {self.asset_id}"

    @property
    def bk_flag(self):
        """Legacy alias for bankruptcy.bk_flag."""
        bk = getattr(self, "bankruptcy", None)
        return bk.bk_flag if bk else None

    @property
    def bk_chapter(self):
        """Legacy alias for bankruptcy.bk_chapter."""
        bk = getattr(self, "bankruptcy", None)
        return bk.bk_chapter if bk else None

    @property
    def mod_flag(self):
        """Legacy alias for modification.mod_flag."""
        mod = getattr(self, "modification", None)
        return mod.mod_flag if mod else None

    @property
    def mod_date(self):
        """Legacy alias for modification.mod_date."""
        mod = getattr(self, "modification", None)
        return mod.mod_date if mod else None

    @property
    def mod_maturity_date(self):
        """Legacy alias for modification.mod_maturity_date."""
        mod = getattr(self, "modification", None)
        return mod.mod_maturity_date if mod else None

    @property
    def mod_term(self):
        """Legacy alias for modification.mod_term."""
        mod = getattr(self, "modification", None)
        return mod.mod_term if mod else None

    @property
    def mod_rate(self):
        """Legacy alias for modification.mod_rate."""
        mod = getattr(self, "modification", None)
        return mod.mod_rate if mod else None

    @property
    def mod_initial_balance(self):
        """Legacy alias for modification.mod_initial_balance."""
        mod = getattr(self, "modification", None)
        return mod.mod_initial_balance if mod else None


class AcqBankruptcy(models.Model):
    """
    Bankruptcy data tied to a loan.

    WHAT: Stores bankruptcy flags and chapter details.
    WHY: Isolates BK fields from core loan data for clarity.
    HOW: 1:1 with AcqLoan (asset-aligned primary key).
    """

    # WHAT: 1:1 link to loan container
    # WHY: Each loan may have at most one BK record
    # HOW: OneToOneField with primary_key=True
    loan = models.OneToOneField(
        AcqLoan,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='bankruptcy',
        help_text='1:1 link to acquisition loan.',
    )

    # WHAT: Bankruptcy flag
    # WHY: Indicate BK status for workflow/reporting
    # HOW: Nullable BooleanField
    bk_flag = models.BooleanField(default=False, null=True, blank=True)
    # WHAT: Bankruptcy chapter
    # WHY: Capture BK chapter where provided (e.g., 7, 11, 13)
    # HOW: Short CharField
    bk_chapter = models.CharField(max_length=10, null=True, blank=True)

    # ===== Timestamps =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Acquisition Bankruptcy"
        verbose_name_plural = "Acquisition Bankruptcies"
        indexes = [
            models.Index(fields=['loan']),
            models.Index(fields=['bk_flag']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"AcqBankruptcy for Loan {self.loan_id}"


class AcqModification(models.Model):
    """
    Modification data tied to a loan.

    WHAT: Stores modification flags and terms.
    WHY: Isolates mod fields from core loan data for clarity.
    HOW: 1:1 with AcqLoan (asset-aligned primary key).
    """

    # WHAT: 1:1 link to loan container
    # WHY: Each loan may have at most one mod record
    # HOW: OneToOneField with primary_key=True
    loan = models.OneToOneField(
        AcqLoan,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='modification',
        help_text='1:1 link to acquisition loan.',
    )

    # WHAT: Modification flag
    # WHY: Indicate whether loan is modified
    # HOW: BooleanField with default False
    mod_flag = models.BooleanField(default=False)
    # WHAT: Modification effective date
    # WHY: Track when modification took effect
    # HOW: Optional DateField
    mod_date = models.DateField(null=True, blank=True)
    # WHAT: Modification maturity date
    # WHY: Track new maturity date after modification
    # HOW: Optional DateField
    mod_maturity_date = models.DateField(null=True, blank=True)
    # WHAT: Modification term (months)
    # WHY: Track modified term length
    # HOW: Optional IntegerField
    mod_term = models.IntegerField(null=True, blank=True)
    # WHAT: Modification interest rate
    # WHY: Track modified rate for modeling
    # HOW: Optional DecimalField
    mod_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    # WHAT: Modification initial balance
    # WHY: Track modified principal balance
    # HOW: Optional DecimalField
    mod_initial_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # ===== Timestamps =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Acquisition Modification"
        verbose_name_plural = "Acquisition Modifications"
        indexes = [
            models.Index(fields=['loan']),
            models.Index(fields=['mod_flag']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"AcqModification for Loan {self.loan_id}"


class AcqProperty(models.Model):
    """
    Property data tied to an acquisition asset.

    WHAT: Stores address and physical characteristics.
    WHY: Separates property from loan to support non-loan assets.
    HOW: 1:1 with AcqAsset.
    """

    class Occupancy(models.TextChoices):
        """Occupancy classification for property assets."""
        VACANT = 'Vacant', 'Vacant'
        OCCUPIED = 'Occupied', 'Occupied'
        UNKNOWN = 'Unknown', 'Unknown'

    # WHAT: 1:1 link to asset container
    # WHY: Each asset has a single primary property record
    # HOW: OneToOneField with primary_key=True
    asset = models.OneToOneField(
        AcqAsset,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='property',
        help_text='1:1 link to acquisition asset.',
    )

    # ===== Address =====
    street_address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip = models.CharField(max_length=100, null=True, blank=True)

    # ===== Property characteristics =====
    occupancy = models.CharField(
        max_length=100,
        choices=Occupancy.choices,
        default=Occupancy.UNKNOWN,
        null=True,
        blank=True,
    )
    year_built = models.IntegerField(null=True, blank=True)
    sq_ft = models.IntegerField(null=True, blank=True)
    lot_size = models.IntegerField(null=True, blank=True)
    beds = models.IntegerField(null=True, blank=True)
    baths = models.IntegerField(null=True, blank=True)

    @property
    def property_type_merged(self):
        """
        WHAT: Unified property type value for downstream use.
        WHY: Subclass is the single source of truth for property type.
        HOW: Return the asset subclass value based on asset_class.
        """
        asset = getattr(self, 'asset', None)
        if not asset:
            return None
        return asset.get_property_type_from_subclass()

    # ===== Timestamps =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Acquisition Property"
        verbose_name_plural = "Acquisition Properties"
        indexes = [
            models.Index(fields=['asset']),
            models.Index(fields=['state']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"AcqProperty for Asset {self.asset_id}"


class AcqForeclosureTimeline(models.Model):
    """
    Foreclosure timeline fields tied to an acquisition asset.

    WHAT: Tracks FC dates and flags for FC-specific workflows.
    WHY: Keeps FC timeline separate from loan/property fields.
    HOW: 1:1 with AcqAsset.
    """

    # WHAT: 1:1 link to asset container
    # WHY: Each asset has at most one FC timeline
    # HOW: OneToOneField with primary_key=True
    asset = models.OneToOneField(
        AcqAsset,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='foreclosure_timeline',
        help_text='1:1 link to acquisition asset.',
    )

    # ===== FC fields =====
    fc_flag = models.BooleanField(default=False, null=True, blank=True)
    fc_first_legal_date = models.DateField(null=True, blank=True)
    fc_referred_date = models.DateField(null=True, blank=True)
    fc_judgement_date = models.DateField(null=True, blank=True)
    fc_scheduled_sale_date = models.DateField(null=True, blank=True)
    fc_sale_date = models.DateField(null=True, blank=True)
    fc_starting = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # ===== Timestamps =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Acquisition Foreclosure Timeline"
        verbose_name_plural = "Acquisition Foreclosure Timelines"
        indexes = [
            models.Index(fields=['asset']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"AcqForeclosureTimeline for Asset {self.asset_id}"


