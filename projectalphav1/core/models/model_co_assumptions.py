from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from core.models.model_co_lookupTables import PropertyType
from core.models.model_co_geoAssumptions import StateReference

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
    liqfee_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text="Liquidation fee percentage as decimal (e.g., 0.015 = 1.5%)")
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
    
    # Property type using centralized choices from lookupTables
    # This ensures consistency with SellerRawData and other models
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
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


class PropertyTypeAssumption(models.Model):
    """
    Property type-based assumptions for utilities and property management costs.
    
    What this does:
    - Stores default assumptions for each property type (SFR, Condo, etc.)
    - Used as fallback when state-specific or square footage-based assumptions are not available
    - Provides baseline costs per property type
    
    How it works:
    - One record per property type
    - Contains all utility and property management cost assumptions
    - Used in assumption workflow priority: sqft -> state -> property type
    """
    
    # Property type field using centralized choices from lookupTables
    # This ensures consistency with SellerRawData, HOAAssumption, and other models
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        unique=True,
        help_text="Property type for these assumptions"
    )
    
    # Utility assumptions (monthly costs in dollars)
    # All fields are nullable to allow flexibility in defining only relevant assumptions per property type
    utility_electric_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="Monthly electric utility cost in dollars"
    )
    utility_gas_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="Monthly gas utility cost in dollars"
    )
    utility_water_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="Monthly water utility cost in dollars"
    )
    utility_sewer_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="Monthly sewer utility cost in dollars"
    )
    utility_trash_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="Monthly trash utility cost in dollars"
    )
    utility_other_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="Monthly other utility costs in dollars"
    )
    
    # Property management assumptions (monthly costs in dollars)
    # All fields are nullable to allow flexibility in defining only relevant assumptions per property type
    property_management_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="Monthly property management cost in dollars"
    )
    repairs_maintenance_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="Monthly repairs and maintenance cost in dollars"
    )
    marketing_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="Monthly marketing cost in dollars"
    )
    
    # One-time costs (in dollars)
    # All fields are nullable to allow flexibility in defining only relevant assumptions per property type
    trashout_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="One-time trashout cost in dollars"
    )
    renovation_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="One-time renovation cost in dollars"
    )
    security_cost_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="Monthly security cost in dollars"
    )
    landscaping_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="Monthly landscaping cost in dollars"
    )
    pool_maintenance_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        default=None,
        help_text="Monthly pool maintenance cost in dollars"
    )
    
    # Metadata
    notes = models.TextField(
        blank=True, 
        null=True, 
        help_text="Additional notes about these property type assumptions"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether these assumptions are currently active"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Property Type Assumption"
        verbose_name_plural = "Property Type Assumptions"
        db_table = 'property_type_assumptions'
        ordering = ['property_type']
        indexes = [
            models.Index(fields=['property_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_property_type_display()} Assumptions"
    
    def total_monthly_utilities(self) -> Decimal:
        """Calculate total monthly utility costs, treating None as 0."""
        return (
            (self.utility_electric_monthly or Decimal('0.00')) + 
            (self.utility_gas_monthly or Decimal('0.00')) + 
            (self.utility_water_monthly or Decimal('0.00')) + 
            (self.utility_sewer_monthly or Decimal('0.00')) + 
            (self.utility_trash_monthly or Decimal('0.00')) + 
            (self.utility_other_monthly or Decimal('0.00'))
        ).quantize(Decimal('0.01'))
    
    def total_monthly_property_management(self) -> Decimal:
        """Calculate total monthly property management costs, treating None as 0."""
        return (
            (self.property_management_monthly or Decimal('0.00')) + 
            (self.repairs_maintenance_monthly or Decimal('0.00')) + 
            (self.marketing_monthly or Decimal('0.00')) + 
            (self.security_cost_monthly or Decimal('0.00')) + 
            (self.landscaping_monthly or Decimal('0.00')) + 
            (self.pool_maintenance_monthly or Decimal('0.00'))
        ).quantize(Decimal('0.01'))
    
    def total_one_time_costs(self) -> Decimal:
        """Calculate total one-time costs, treating None as 0."""
        return (
            (self.trashout_cost or Decimal('0.00')) + 
            (self.renovation_cost or Decimal('0.00'))
        ).quantize(Decimal('0.01'))


class SquareFootageAssumption(models.Model):
    """
    Square footage-based assumptions for utilities and property management costs.
    
    What this does:
    - Stores per-square-foot cost assumptions
    - Separate records for residential vs commercial properties
    - Used as primary assumption source when square footage is available
    
    How it works:
    - Define cost per square foot for different property categories
    - Multiply by actual property square footage to get total costs
    - Highest priority in assumption workflow
    """
    
    class PropertyCategory(models.TextChoices):
        RESIDENTIAL = 'RESIDENTIAL', 'Residential'
        COMMERCIAL = 'COMMERCIAL', 'Commercial'
    
    # Property category (residential vs commercial)
    property_category = models.CharField(
        max_length=20,
        choices=PropertyCategory.choices,
        help_text="Property category: Residential or Commercial"
    )
    
    # Description for this set of assumptions
    description = models.CharField(
        max_length=200,
        help_text="Description of these square footage assumptions"
    )
    
    # Utility assumptions (cost per square foot per month)
    # All fields are nullable to allow flexibility in defining only relevant assumptions per category
    utility_electric_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Electric cost per square foot per month"
    )
    utility_gas_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Gas cost per square foot per month"
    )
    utility_water_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Water cost per square foot per month"
    )
    utility_sewer_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Sewer cost per square foot per month"
    )
    utility_trash_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Trash cost per square foot per month"
    )
    utility_other_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Other utility cost per square foot per month"
    )
    
    # Property management assumptions (cost per square foot per month)
    # All fields are nullable to allow flexibility in defining only relevant assumptions per category
    property_management_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Property management cost per square foot per month"
    )
    repairs_maintenance_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Repairs and maintenance cost per square foot per month"
    )
    marketing_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Marketing cost per square foot per month"
    )
    security_cost_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Security cost per square foot per month"
    )
    landscaping_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Landscaping cost per square foot per month"
    )
    pool_maintenance_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Pool maintenance cost per square foot per month"
    )
    
    # One-time costs (cost per square foot)
    # All fields are nullable to allow flexibility in defining only relevant assumptions per category
    trashout_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Trashout cost per square foot (one-time)"
    )
    renovation_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        null=True,
        blank=True,
        help_text="Renovation cost per square foot (one-time)"
    )
    
    # Metadata
    notes = models.TextField(
        blank=True, 
        null=True, 
        help_text="Additional notes about these square footage assumptions"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether these assumptions are currently active"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Square Footage Assumption"
        verbose_name_plural = "Square Footage Assumptions"
        db_table = 'square_footage_assumptions'
        ordering = ['property_category', 'description']
        indexes = [
            models.Index(fields=['property_category']),
            models.Index(fields=['is_active']),
        ]
        # Ensure unique combination of category and description
        unique_together = [['property_category', 'description']]
    
    def __str__(self):
        return f"{self.get_property_category_display()}: {self.description}"
    
    def calculate_monthly_costs(self, square_footage: int) -> dict:
        """Calculate monthly costs for the given square footage."""
        sqft = Decimal(str(square_footage))
        
        return {
            'utility_electric': (self.utility_electric_per_sqft * sqft).quantize(Decimal('0.01')),
            'utility_gas': (self.utility_gas_per_sqft * sqft).quantize(Decimal('0.01')),
            'utility_water': (self.utility_water_per_sqft * sqft).quantize(Decimal('0.01')),
            'utility_sewer': (self.utility_sewer_per_sqft * sqft).quantize(Decimal('0.01')),
            'utility_trash': (self.utility_trash_per_sqft * sqft).quantize(Decimal('0.01')),
            'utility_other': (self.utility_other_per_sqft * sqft).quantize(Decimal('0.01')),
            'property_management': (self.property_management_per_sqft * sqft).quantize(Decimal('0.01')),
            'repairs_maintenance': (self.repairs_maintenance_per_sqft * sqft).quantize(Decimal('0.01')),
            'marketing': (self.marketing_per_sqft * sqft).quantize(Decimal('0.01')),
            'security_cost': (self.security_cost_per_sqft * sqft).quantize(Decimal('0.01')),
            'landscaping': (self.landscaping_per_sqft * sqft).quantize(Decimal('0.01')),
            'pool_maintenance': (self.pool_maintenance_per_sqft * sqft).quantize(Decimal('0.01')),
        }
    
    def calculate_one_time_costs(self, square_footage: int) -> dict:
        """Calculate one-time costs for the given square footage."""
        sqft = Decimal(str(square_footage))
        
        return {
            'trashout': (self.trashout_per_sqft * sqft).quantize(Decimal('0.01')),
            'renovation': (self.renovation_per_sqft * sqft).quantize(Decimal('0.01')),
        }


class UnitBasedAssumption(models.Model):
    """
    Unit-based assumptions for multifamily properties.
    
    What this does:
    - Stores per-unit cost assumptions for multifamily properties
    - Used when square footage is not available but unit count is
    - Applies to properties with multiple units (2-4 Family, Multifamily 5+)
    
    How it works:
    - Define cost per unit for different unit count ranges
    - Multiply by actual unit count
    - Used in assumption workflow when square footage is not available
    """
    
    # Unit count range
    units_min = models.IntegerField(
        help_text="Minimum unit count for this range (inclusive)"
    )
    units_max = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum unit count for this range (inclusive). Null = no maximum"
    )
    
    # Utility assumptions (cost per unit per month)
    utility_electric_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Electric cost per unit per month"
    )
    utility_gas_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Gas cost per unit per month"
    )
    utility_water_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Water cost per unit per month"
    )
    utility_sewer_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Sewer cost per unit per month"
    )
    utility_trash_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Trash cost per unit per month"
    )
    utility_other_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Other utility cost per unit per month"
    )
    
    # Property management assumptions (cost per unit per month)
    property_management_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Property management cost per unit per month"
    )
    repairs_maintenance_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Repairs and maintenance cost per unit per month"
    )
    marketing_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Marketing cost per unit per month"
    )
    security_cost_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Security cost per unit per month"
    )
    landscaping_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Landscaping cost per unit per month"
    )
    pool_maintenance_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Pool maintenance cost per unit per month"
    )
    
    # One-time costs (cost per unit)
    trashout_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Trashout cost per unit (one-time)"
    )
    renovation_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Renovation cost per unit (one-time)"
    )
    
    # Metadata
    description = models.CharField(
        max_length=200,
        help_text="Description of this unit count range"
    )
    notes = models.TextField(
        blank=True, 
        null=True, 
        help_text="Additional notes about these unit-based assumptions"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether these assumptions are currently active"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Unit Based Assumption"
        verbose_name_plural = "Unit Based Assumptions"
        db_table = 'unit_based_assumptions'
        ordering = ['units_min']
        indexes = [
            models.Index(fields=['units_min', 'units_max']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(units_min__gte=1),
                name='units_min_positive'
            ),
            models.CheckConstraint(
                check=models.Q(units_max__isnull=True) | models.Q(units_max__gte=models.F('units_min')),
                name='units_max_gte_min'
            ),
        ]
    
    def __str__(self):
        max_display = f"{self.units_max}" if self.units_max else "∞"
        return f"{self.units_min} - {max_display} units"
    
    def matches_unit_count(self, unit_count: int) -> bool:
        """Check if this assumption applies to the given unit count."""
        if unit_count < self.units_min:
            return False
        if self.units_max is not None and unit_count > self.units_max:
            return False
        return True
    
    def calculate_monthly_costs(self, unit_count: int) -> dict:
        """Calculate monthly costs for the given unit count."""
        units = Decimal(str(unit_count))
        
        return {
            'utility_electric': (self.utility_electric_per_unit * units).quantize(Decimal('0.01')),
            'utility_gas': (self.utility_gas_per_unit * units).quantize(Decimal('0.01')),
            'utility_water': (self.utility_water_per_unit * units).quantize(Decimal('0.01')),
            'utility_sewer': (self.utility_sewer_per_unit * units).quantize(Decimal('0.01')),
            'utility_trash': (self.utility_trash_per_unit * units).quantize(Decimal('0.01')),
            'utility_other': (self.utility_other_per_unit * units).quantize(Decimal('0.01')),
            'property_management': (self.property_management_per_unit * units).quantize(Decimal('0.01')),
            'repairs_maintenance': (self.repairs_maintenance_per_unit * units).quantize(Decimal('0.01')),
            'marketing': (self.marketing_per_unit * units).quantize(Decimal('0.01')),
            'security_cost': (self.security_cost_per_unit * units).quantize(Decimal('0.01')),
            'landscaping': (self.landscaping_per_unit * units).quantize(Decimal('0.01')),
            'pool_maintenance': (self.pool_maintenance_per_unit * units).quantize(Decimal('0.01')),
        }
    
    def calculate_one_time_costs(self, unit_count: int) -> dict:
        """Calculate one-time costs for the given unit count."""
        units = Decimal(str(unit_count))
        
        return {
            'trashout': (self.trashout_per_unit * units).quantize(Decimal('0.01')),
            'renovation': (self.renovation_per_unit * units).quantize(Decimal('0.01')),
        }
