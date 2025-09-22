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
    # Property Type choices
    PROPERTY_TYPE_SFR = 'SFR'
    PROPERTY_TYPE_MANUFACTURED = 'Manufactured'
    PROPERTY_TYPE_CONDO = 'Condo'
    PROPERTY_TYPE_2_4_FAMILY = '2-4 Family'
    PROPERTY_TYPE_LAND = 'Land'
    PROPERTY_TYPE_MULTIFAMILY = 'Multifamily 5+'
    
    PROPERTY_TYPE_CHOICES = [
        (PROPERTY_TYPE_SFR, 'SFR'),
        (PROPERTY_TYPE_MANUFACTURED, 'Manufactured'),
        (PROPERTY_TYPE_CONDO, 'Condo'),
        (PROPERTY_TYPE_2_4_FAMILY, '2-4 Family'),
        (PROPERTY_TYPE_LAND, 'Land'),
        (PROPERTY_TYPE_MULTIFAMILY, 'Multifamily 5+'),
    ]
    
    # Occupancy choices
    OCCUPANCY_VACANT = 'Vacant'
    OCCUPANCY_OCCUPIED = 'Occupied'
    OCCUPANCY_UNKNOWN = 'Unknown'
    
    OCCUPANCY_CHOICES = [
        (OCCUPANCY_VACANT, 'Vacant'),
        (OCCUPANCY_OCCUPIED, 'Occupied'),
        (OCCUPANCY_UNKNOWN, 'Unknown'),
    ]

    # Asset status choices (dropdown)
    ASSET_STATUS_NPL = 'NPL'   # Non-Performing Loan
    ASSET_STATUS_REO = 'REO'   # Real Estate Owned
    ASSET_STATUS_PERF = 'PERF' # Performing
    ASSET_STATUS_RPL = 'RPL'   # Re-Performing Loan

    ASSET_STATUS_CHOICES = [
        (ASSET_STATUS_NPL, 'NPL'),
        (ASSET_STATUS_REO, 'REO'),
        (ASSET_STATUS_PERF, 'PERF'),
        (ASSET_STATUS_RPL, 'RPL'),
    ]
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='seller_raw_data')
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name='seller_raw_data')
    # Stable hub link (1:1) – create hub first, then attach the single raw row for this asset.
    # Nullable during backfill, but enforces unique one-to-one once set.
    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='acq_raw',
        help_text='One hub per asset; one raw row per hub (set during ETL).',
    )
    sellertape_id = models.IntegerField()
    sellertape_altid = models.IntegerField(null=True, blank=True)
    asset_status = models.CharField(max_length=100, choices=ASSET_STATUS_CHOICES, null=True, blank=True)
    as_of_date = models.DateField(null=True, blank=True)
    
    street_address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip = models.CharField(max_length=100, null=True, blank=True)
    property_type = models.CharField(max_length=100, choices=PROPERTY_TYPE_CHOICES, default=PROPERTY_TYPE_SFR, null=True, blank=True)
    occupancy = models.CharField(max_length=100, choices=OCCUPANCY_CHOICES, default=OCCUPANCY_UNKNOWN, null=True, blank=True)
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
    
    class Meta:
        verbose_name = "Seller Raw Data"
        verbose_name_plural = "Seller Raw Data"
        indexes = [
            models.Index(fields=['id']),  # Primary key index
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
        return f"Seller Raw Data {self.id} - {self.seller.name} - {self.trade.trade_name}"
