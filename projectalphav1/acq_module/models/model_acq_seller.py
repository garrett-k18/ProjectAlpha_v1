#Seller Data Django Model. Contains Seller, Trade and Raw Data models

from django.db import models
from django.utils import timezone
import re
from core.models.model_co_lookupTables import PropertyType


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
        active_asset_count = self.seller_raw_data.filter(
            acq_status=SellerRawData.AcquisitionStatus.KEEP
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

class Trade_Deal(Trade):
    """
    Proxy model to support deal-centric naming.

    WHAT: Exposes a deal-centric class name without changing the table.
    WHY: Allows codebases to migrate to Trade_Deal naming safely.
    HOW: Django proxy to Trade so there is no new table.
    """

    class Meta:
        proxy = True
        verbose_name = "Deal"
        verbose_name_plural = "Deals"


class SellerRawData(models.Model):
    # Django 3.0+ enumeration types for choices
    # Docs: https://docs.djangoproject.com/en/stable/ref/models/fields/#enumeration-types
    # NOTE: PropertyType is imported from core.lookupTables for consistency across all models
    
    class ProductType(models.TextChoices):
        BPL = 'BPL', 'BPL'
        HECM = 'HECM', 'HECM'
        VA = 'VA', 'VA'
        CONV = 'Conv', 'Conv'
        COMMERCIAL = 'Commercial', 'Commercial'
    
    # Occupancy choices (TextChoices)
    class Occupancy(models.TextChoices):
        VACANT = 'Vacant', 'Vacant'
        OCCUPIED = 'Occupied', 'Occupied'
        UNKNOWN = 'Unknown', 'Unknown'

    # Asset status choices (TextChoices)
    class AssetStatus(models.TextChoices):
        NPL = 'NPL', 'NPL'       # Non-Performing Loan
        REO = 'REO', 'REO'       # Real Estate Owned
        PERF = 'PERF', 'PERF'    # Performing
        RPL = 'RPL', 'RPL'       # Re-Performing Loan

    # Asset-level status choices
    # WHAT: Simple binary status for asset-level filtering
    # WHY: Assets are either in the active pool (KEEP) or excluded (DROP)
    # HOW: Trade-level status controls the overall trade lifecycle (PASS, DD, AWARDED, BOARD)
    class AcquisitionStatus(models.TextChoices):
        KEEP = 'KEEP', 'Keep'  # Default: asset is in active bidding pool
        DROP = 'DROP', 'Drop'  # Asset is excluded from active bidding
    # WHAT: Hub-owned primary key - strict 1:1 with core.AssetIdHub
    # WHY: Aligns with hub-first architecture so this model's PK equals the hub ID
    # HOW: OneToOneField with primary_key=True (same pattern as BlendedOutcomeModel)
    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='acq_raw',
        help_text='1:1 with hub; this model\'s PK equals the hub ID.',
    )
    seller = models.ForeignKey(
        Seller,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='seller_raw_data',
        help_text='Nullable reference so Seller deletions preserve this raw row.'
    )
    trade = models.ForeignKey(
        Trade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='seller_raw_data',
        help_text='Nullable reference so Trade deletions keep the raw asset record.'
    )
    # WHAT: Unique loan identifier from seller's tape (primary identifier)
    # WHY: CharField to handle any format - numbers, letters, dashes, etc. (e.g., "ABC-123-456", "9160091924")
    # HOW: Max 100 chars covers all seller tape ID formats
    sellertape_id = models.CharField(max_length=100)
    # WHAT: Alternative/secondary loan identifier from seller's tape
    # WHY: CharField to handle any format - some sellers use alphanumeric alt IDs
    # HOW: Max 100 chars, optional field
    sellertape_altid = models.CharField(max_length=100, null=True, blank=True)
    asset_status = models.CharField(
        max_length=100,
        choices=AssetStatus.choices,
        null=True,
        blank=True,
    )
    # WHAT: Asset-level acquisition status (KEEP or DROP)
    # WHY: Simple binary flag to include/exclude assets from active pool
    # HOW: Trade-level status (on Trade model) controls overall lifecycle (PASS, DD, AWARDED, BOARD)
    acq_status = models.CharField(
        max_length=20,
        choices=AcquisitionStatus.choices,
        default=AcquisitionStatus.KEEP,
        db_index=True,
        help_text='Asset-level status: KEEP (in active pool) or DROP (excluded). Trade-level status controls lifecycle.'
    )
    as_of_date = models.DateField(null=True, blank=True)
    
    street_address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip = models.CharField(max_length=100, null=True, blank=True)
    property_type = models.CharField(
        max_length=100,
        choices=PropertyType.choices,
        default=PropertyType.SFR,
        null=True,
        blank=True,
    )
    product_type = models.CharField(
        max_length=50,
        choices=ProductType.choices,
        null=True,
        blank=True,
    )
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

    borrower1_last = models.CharField(max_length=100, null=True, blank=True, help_text="If entity, put entity in borrower1_last.")
    borrower1_first = models.CharField(max_length=100, null=True, blank=True)
    borrower2_last = models.CharField(max_length=100, null=True, blank=True)
    borrower2_first = models.CharField(max_length=100, null=True, blank=True)
    
        #Financials
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
    
    default_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    months_dlq = models.IntegerField(null=True, blank=True)
    current_maturity_date = models.DateField(null=True, blank=True)
    current_term = models.IntegerField(null=True, blank=True)
    
    accrued_note_interest = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    accrued_default_interest = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    escrow_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    escrow_advance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    recoverable_corp_advance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    late_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    other_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    suspense_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_debt = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    origination_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    origination_arv = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    origination_value_date = models.DateField(null=True, blank=True)
    
    seller_value_date = models.DateField(null=True, blank=True)
    seller_arv_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    seller_asis_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    additional_asis_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    additional_arv_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    additional_value_date = models.DateField(null=True, blank=True)

    fc_flag = models.BooleanField(default=False, null=True, blank=True)
    fc_first_legal_date = models.DateField(null=True, blank=True)
    fc_referred_date = models.DateField(null=True, blank=True)
    fc_judgement_date = models.DateField(null=True, blank=True)
    fc_scheduled_sale_date = models.DateField(null=True, blank=True)
    fc_sale_date = models.DateField(null=True, blank=True)
    fc_starting = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    bk_flag = models.BooleanField(default=False, null=True, blank=True)
    bk_chapter = models.CharField(max_length=10, null=True, blank=True)
    
    mod_flag = models.BooleanField(default=False)
    mod_date = models.DateField(null=True, blank=True)
    mod_maturity_date = models.DateField(null=True, blank=True)
    mod_term = models.IntegerField(null=True, blank=True)
    mod_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    mod_initial_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)    

    # Timestamps
    # WHAT: Automatic timestamp tracking for record creation and updates
    # WHY: Track when assets are added to system and when they're modified
    # HOW: Django auto_now_add for creation, auto_now for updates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_dropped(self) -> bool:
        """Return True when acquisition status is Drop for backward compatibility."""
        return self.acq_status == self.AcquisitionStatus.DROP

    class Meta:
        verbose_name = "Seller Raw Data"
        verbose_name_plural = "Seller Raw Data"
        indexes = [
            models.Index(fields=['asset_hub']),  # Primary key index (now asset_hub)
            models.Index(fields=['asset_status']),
            models.Index(fields=['acq_status']),
            models.Index(fields=['seller']),
            models.Index(fields=['trade']),
            models.Index(fields=['state']),
        ]
        ordering = ['-created_at']
        constraints = [
            # Enforce property_type choices at database level
            models.CheckConstraint(
                check=models.Q(property_type__isnull=True) | models.Q(
                    property_type__in=['SFR', 'Manufactured', 'Condo', 'Townhouse', '2-4 Family', 
                                      'Land', 'Multifamily 5+', 'Industrial', 'Mixed Use', 'Storage', 'Healthcare']
                ),
                name='valid_property_type',
            ),
            # Enforce product_type choices at database level
            models.CheckConstraint(
                check=models.Q(product_type__isnull=True) | models.Q(
                    product_type__in=['BPL', 'HECM', 'VA', 'Conv', 'Commercial']
                ),
                name='valid_product_type',
            ),
            # Enforce occupancy choices at database level
            models.CheckConstraint(
                check=models.Q(occupancy__isnull=True) | models.Q(
                    occupancy__in=['Vacant', 'Occupied', 'Unknown']
                ),
                name='valid_occupancy',
            ),
            # Enforce asset_status choices at database level
            models.CheckConstraint(
                check=models.Q(asset_status__isnull=True) | models.Q(
                    asset_status__in=['NPL', 'REO', 'PERF', 'RPL']
                ),
                name='valid_asset_status',
            ),
        ]  
    


   #Calced fields#
    
    def calculate_total_debt(self):
        """Calculate the total debt from all debt components
        
        Returns:
            Decimal: The calculated total debt value
        """
        # Sum all debt components
        total = sum([
            self.current_balance or 0,
            self.deferred_balance or 0,
            self.accrued_note_interest or 0,
            self.escrow_advance or 0,
            self.escrow_balance or 0,
            self.recoverable_corp_advance or 0,
            self.late_fees or 0,
            self.other_fees or 0,
            self.suspense_balance or 0,
        ])
        
        return total
    
    def calculate_months_dlq(self):
        """Calculate the months delinquent based on as_of_date and next_due_date
        
        Returns:
            int: The number of months delinquent
        """
        if not self.as_of_date or not self.next_due_date:
            return 0
            
        # Calculate months between as_of_date and next_due_date
        month_diff = (self.as_of_date.year - self.next_due_date.year) * 12 + (self.as_of_date.month - self.next_due_date.month)
        
        # If next_due_date is in the future, we're not delinquent
        if month_diff < 0:
            return 0
            
        return month_diff

    def save(self, *args, **kwargs):
        """Override save method to normalize fields and calculate derived values

        Behavior:
        - Normalize `state` to uppercase at the model layer so all reporting
          logic can rely on a consistent value. We do not truncate or otherwise
          modify the value here.
        - If `total_debt` is not provided, calculate it from component fields.
        - If `months_dlq` is not provided, calculate it from the dates.
        """
        # Normalize the state value if provided: strip whitespace and uppercase.
        if self.state is not None:
            # Ensure a consistent representation for downstream aggregations
            cleaned = self.state.strip()
            self.state = cleaned.upper() if cleaned else cleaned

        # If total_debt is not provided, calculate it
        if self.total_debt is None:
            self.total_debt = self.calculate_total_debt()
        
        # If months_dlq is not provided, calculate it
        if self.months_dlq is None:
            self.months_dlq = self.calculate_months_dlq()

        super().save(*args, **kwargs)
        if self.trade_id:
            self.trade.refresh_status_from_assets()

    def delete(self, *args, **kwargs):
        trade = self.trade if self.trade_id else None
        super().delete(*args, **kwargs)
        if trade:
            trade.refresh_status_from_assets()

    def __str__(self):
        """Return a safe, human-readable label for admin and logs."""
        # WHAT: Resolve seller name while guarding against null FK after Seller deletion
        seller_name = (
            self.seller.name  # HOW: Use actual seller name when FK still populated
            if self.seller is not None
            else "Unassigned Seller"  # WHY: Provide fallback label when FK was nulled
        )
        # WHAT: Resolve trade name while handling nullable FK to avoid AttributeError in admin lists
        trade_name = (
            self.trade.trade_name  # HOW: Surface trade title for clarity in UI lists
            if self.trade is not None
            else "Unassigned Trade"  # WHY: Keep string informative even when FK missing
        )
        # RETURN: Include primary key plus resolved names to match previous display format safely
        return f"Seller Raw Data {self.pk} - {seller_name} - {trade_name}"
