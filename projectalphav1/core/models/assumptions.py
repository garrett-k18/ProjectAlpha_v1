from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Servicer(models.Model):
    """Model to store servicer information for loan servicing"""
    servicer_name = models.CharField(max_length=100, unique=True)
    contact_name = models.CharField(max_length=100, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Fees and rates
    servicing_transfer_duration = models.IntegerField(null=True, blank=True)
    board_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    thirtday_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sixtyday_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ninetyday_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    onetwentyday_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fc_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bk_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mod_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dil_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    thirdparty_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reo_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reo_days = models.IntegerField(null=True, blank=True)
    liqfee_pct = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    liqfee_flat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
        
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Servicer"
        verbose_name_plural = "Servicers"
        ordering = ['servicer_name']
        indexes = [
            models.Index(fields=['servicer_name']),
        ]
        db_table = 'servicers'
    
    def __str__(self):
        return self.servicer_name


class StateReference(models.Model):
    """Model to store state-specific data and regulations"""
    state_code = models.CharField(max_length=2, primary_key=True)
    state_name = models.CharField(max_length=50)
    judicialvsnonjudicial = models.BooleanField(default=False, help_text="Is this a judicial foreclosure state")   
    
    fc_state_months = models.IntegerField(help_text="Average months to complete foreclosure")
    eviction_duration = models.IntegerField(help_text="Average months to complete eviction")
    rehab_duration = models.IntegerField(help_text="Average months to complete rehab")
    reo_marketing_duration = models.IntegerField(help_text="Average months to complete reo marketing")
    reo_local_market_ext_duration = models.IntegerField(help_text="Average months to complete reo local market extension")
    dil_duration_avg = models.IntegerField(help_text="Average months to complete dilution")
    

    # Tax data (stored as decimals with 4 decimal places: 0.0063 = 0.63%)
    # Validation: 0.0000 (0%) to 1.0000 (100%)
    property_tax_rate = models.DecimalField(
        max_digits=6, 
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0000')), MaxValueValidator(Decimal('1.0000'))],
        help_text="Average property tax rate (as decimal: 0.0063 = 0.63%, range: 0-100%)"
    )
    transfer_tax_rate = models.DecimalField(
        max_digits=6, 
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0000')), MaxValueValidator(Decimal('1.0000'))],
        help_text="Tax rate for property transfers (as decimal: 0.0033 = 0.33%, range: 0-100%)"
    )
    insurance_rate_avg = models.DecimalField(
        max_digits=6, 
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0000')), MaxValueValidator(Decimal('1.0000'))],
        help_text="Average insurance rate (as decimal: 0.0040 = 0.40%, range: 0-100%)"
    )
    broker_closing_cost_fees_avg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average broker closing cost fees")
    other_closing_cost_fees_avg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average other closing cost fees")
    # Legal fees
    fc_legal_fees_avg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average legal fees for foreclosure")
    dil_cost_avg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average dilution cost")
    cfk_cost_avg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average CFK cost")
    
    # Value adjustment can be negative (depreciation) or positive (appreciation)
    # Validation: -1.0000 (-100%) to 1.0000 (100%)
    value_adjustment_annual = models.DecimalField(
        max_digits=6, 
        decimal_places=4,
        validators=[MinValueValidator(Decimal('-1.0000')), MaxValueValidator(Decimal('1.0000'))],
        help_text="Average value adjustment (as decimal: 0.0028 = 0.28%, range: -100% to +100%)"
    )
    


    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "State Reference"
        verbose_name_plural = "State References"
        ordering = ['state_name']
        indexes = [
            models.Index(fields=['state_code']),
        ]
        db_table = 'state_reference'
    
    def __str__(self):
        return self.state_name.rstrip('.')

class MSAReference(models.Model):
    """Model to store MSA-specific data and regulations"""
    msa_code = models.CharField(max_length=5, primary_key=True)
    msa_name = models.CharField(max_length=50)
    
class FCStatus(models.Model):
    """Model to store foreclosure status as a categorical choice field.
    
    What this does:
    - Tracks the current foreclosure status of a loan using predefined categories
    - Each status represents a stage in the foreclosure process
    - Status categories are based on judicial vs non-judicial foreclosure types
    
    How it works:
    - Use the STATUS_CHOICES to select the current foreclosure stage
    - Different statuses apply to judicial vs non-judicial states
    - This model can be linked to loan records via ForeignKey
    """
    
    # Foreclosure status category choices
    # Each tuple: (database_value, human_readable_display)
    STATUS_CHOICES = [
        ('pre_fc', 'Pre-Foreclosure'),
        ('first_legal_filed', 'First Legal Filed (NOD/Complaint)'),
        ('mediation', 'Mediation'),
        ('order_of_reference', 'Order of Reference (Judicial Only)'),
        ('judgement', 'Judgment (Judicial Only)'),
        ('pre_sale_redemption', 'Pre-Sale Redemption'),
        ('sale_scheduled', 'Sale Scheduled'),
        ('sale_completed', 'Sale Completed'),
        ('post_sale_redemption', 'Post-Sale Redemption'),
    ]
    
    # The current foreclosure status category
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        help_text="Current foreclosure status category"
    )
    
    # Order/sequence of this status in the foreclosure process
    order = models.IntegerField(
        default=0,
        help_text="Order in which this status typically occurs (lower numbers = earlier stages)"
    )
    
    # Optional: Additional context or notes about this status
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or context about this foreclosure status"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Foreclosure Status"
        verbose_name_plural = "Foreclosure Statuses"
        ordering = ['order', 'status']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['order']),
        ]
        db_table = 'fc_status'
    
    def __str__(self):
        return f"{self.get_status_display()}"

class FCTimelines(models.Model):
    """Model to store foreclosure timelines for different states.
    
    What this does:
    - Stores state-specific and status-specific foreclosure timeline data
    - Links state codes to foreclosure status categories
    - Tracks duration and costs for each status in each state
    
    How it works:
    - Each row represents a specific foreclosure status in a specific state
    - ForeignKey to StateReference provides state-level context
    - ForeignKey to FCStatus provides the foreclosure stage
    - Duration and cost fields capture state/status-specific metrics
    """
    
    # Foreign key to StateReference (links to state_code)
    state = models.ForeignKey(
        StateReference,
        on_delete=models.CASCADE,
        related_name='fc_timelines',
        help_text="State this timeline applies to"
    )
    
    # Foreign key to FCStatus (links to foreclosure status)
    fc_status = models.ForeignKey(
        FCStatus,
        on_delete=models.CASCADE,
        related_name='timelines',
        help_text="Foreclosure status category this timeline represents"
    )
    
    # Average duration in days for this status in this state
    duration_days = models.IntegerField(
        blank=True,
        null=True,
        help_text="Average number of days to complete this status in this state"
    )
    
    # Average cost for this status in this state
    cost_avg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Average cost associated with this status in this state"
    )
    
    # Optional notes specific to this state/status combination
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this status in this state"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Foreclosure Timeline"
        verbose_name_plural = "Foreclosure Timelines"
        ordering = ['state', 'fc_status']
        # Ensure unique combination of state and status
        unique_together = [['state', 'fc_status']]
        indexes = [
            models.Index(fields=['state', 'fc_status']),
        ]
        db_table = 'fc_timelines'
    
    def __str__(self):
        return f"{self.state.state_code} - {self.fc_status.get_status_display()}"
    

class CommercialUnits(models.Model):
    """Model to store commercial property unit-based scaling factors.
    
    What this does:
    - Stores scaling multipliers for foreclosure costs, rehab costs, and rehab duration
      based on the number of commercial units in a property
    - Used to adjust base assumptions for multi-unit commercial properties
    - Each row represents a unit count threshold with its associated scaling factors
    
    Example usage:
    - A 5-unit commercial property might have higher foreclosure costs (1.5x scale)
      and longer rehab duration (1.3x scale) compared to a single-unit property
    """
    # Number of commercial units (e.g., 1, 2-4, 5-10, 10+)
    units = models.IntegerField(
        unique=True,
        help_text="Number of commercial units (use upper bound for ranges, e.g., 4 for 2-4 units)"
    )
    
    # Foreclosure cost scaling factor (multiplier applied to base FC costs)
    fc_cost_scale = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text="Foreclosure cost multiplier (e.g., 1.50 = 150% of base cost)"
    )
    
    # Rehab cost scaling factor (multiplier applied to base rehab costs)
    rehab_cost_scale = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text="Rehab cost multiplier (e.g., 1.25 = 125% of base cost)"
    )
    
    # Rehab duration scaling factor (multiplier applied to base rehab duration)
    rehab_duration_scale = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text="Rehab duration multiplier (e.g., 1.30 = 130% of base duration)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Commercial Unit Scaling"
        verbose_name_plural = "Commercial Unit Scalings"
        ordering = ['units']
        indexes = [
            models.Index(fields=['units']),
        ]
        db_table = 'commercial_units'
    
    def __str__(self):
        return f"{self.units} units"


class HOAAssumption(models.Model):
    """Model to store HOA (Homeowners Association) fee assumptions by property type.
    
    What this does:
    - Stores default monthly HOA fees for residential property types that typically have HOA fees
    - Used in financial calculations and cash flow projections
    - Focuses on property types where HOA fees are common (SFR, Condo, Townhouse, etc.)
    
    How it works:
    - Each property type has a default monthly HOA fee amount
    - One record per property type (unique constraint)
    - Used to estimate ongoing carrying costs for properties
    """
    
    # Property type (free text field for residential property types that have HOA fees)
    property_type = models.CharField(
        max_length=20,
        unique=True,
        help_text="Property type (typically residential types like SFR, Condo, Townhouse, etc.)"
    )
    
    # Monthly HOA fee amount
    monthly_hoa_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Default monthly HOA fee for this property type"
    )
    
    # Optional notes about the assumption
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about HOA assumptions for this property type"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "HOA Assumption"
        verbose_name_plural = "HOA Assumptions"
        ordering = ['property_type']
        indexes = [
            models.Index(fields=['property_type']),
        ]
        db_table = 'hoa_assumptions'
    
    def __str__(self):
        return f"{self.property_type}: ${self.monthly_hoa_fee}/month"

