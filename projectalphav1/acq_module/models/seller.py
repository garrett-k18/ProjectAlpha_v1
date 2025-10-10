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
    """Many trades belong to one seller...Need to make sure IDs start at 1000"""
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='trades')
    trade_name = models.CharField(
        max_length=100,
        blank=True,
        editable=False,  # Always generated internally; not editable via admin/forms
    )
    # Timestamps for trade lifecycle
    # Note: Per Django docs, auto_now/auto_now_add cannot be combined with default
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    
    def __str__(self):
        return f"Trade for {self.seller.name}"

    def save(self, *args, **kwargs):
        """Override save to auto-generate trade_name on create

        Behavior:
        - Always generates '<SellerNameNoSpecials> - MM.DD.YY' on initial create.
        - SellerNameNoSpecials removes all non-alphanumeric characters (including spaces).
        - Date uses local date at creation time.
        """
        # Always generate internally on create, regardless of any provided value
        if self.pk is None:
            # Remove all non-alphanumeric characters from the seller's name (keep case)
            base_name = re.sub(r"[^A-Za-z0-9]", "", self.seller.name or "")
            # Use local date at creation time in MM.DD.YY format
            date_str = timezone.localdate().strftime("%m.%d.%y")
            base_prefix = f"{base_name} - {date_str}"

            # Determine next sequence number for this seller and date, e.g., " - 2", " - 3"
            existing_count = type(self).objects.filter(
                seller=self.seller,
                trade_name__startswith=base_prefix,
            ).count()

            # First one: no suffix. Subsequent ones: " - 2", " - 3", etc.
            suffix = "" if existing_count == 0 else f" - {existing_count + 1}"

            generated = f"{base_prefix}{suffix}"
            # Ensure we don't exceed the DB max_length constraint
            self.trade_name = generated[:100]

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Trade"
        verbose_name_plural = "Trades"
        ordering = ['trade_name']
        indexes = [
            models.Index(fields=['seller']),
        ]


class SellerRawData(models.Model):
    # Django 3.0+ enumeration types for choices
    # Docs: https://docs.djangoproject.com/en/stable/ref/models/fields/#enumeration-types
    class PropertyType(models.TextChoices):
        SFR = 'SFR', 'SFR'
        MANUFACTURED = 'Manufactured', 'Manufactured'
        CONDO = 'Condo', 'Condo'
        TOWNHOUSE = 'Townhouse', 'Townhouse'
        TWO_TO_FOUR = '2-4 Family', '2-4 Family'
        LAND = 'Land', 'Land'
        MULTIFAMILY = 'Multifamily 5+', 'Multifamily 5+'
        INDUSTRIAL = 'Industrial', 'Industrial'
        MIXED_USE = 'Mixed Use', 'Mixed Use'
        STORAGE = 'Storage', 'Storage'

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
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='seller_raw_data')
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name='seller_raw_data')
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Drop/restore tracking fields
    # WHAT: Track assets removed from active bidding
    # WHY: Allow users to temporarily remove assets without deleting them
    # HOW: Boolean flag + metadata fields for audit trail
    is_dropped = models.BooleanField(
        default=False,
        help_text='Asset dropped from active bidding list'
    )
    drop_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Reason for dropping asset'
    )
    drop_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text='When asset was dropped'
    )
    dropped_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dropped_acq_assets',
        help_text='User who dropped the asset'
    )
    
    class Meta:
        verbose_name = "Seller Raw Data"
        verbose_name_plural = "Seller Raw Data"
        indexes = [
            models.Index(fields=['asset_hub']),  # Primary key index (now asset_hub)
            models.Index(fields=['asset_status']),
            models.Index(fields=['seller']),
            models.Index(fields=['trade']),
            models.Index(fields=['state']),
        ]
        ordering = ['-created_at']  
    


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
    
    def __str__(self):
        return f"Seller Raw Data {self.pk} - {self.seller.name} - {self.trade.trade_name}"
