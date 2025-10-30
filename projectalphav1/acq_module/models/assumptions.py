#Assumptions Django Models: Servicing, State Reference, Loan Level Assumptions, Trade Level Assumptions

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal, InvalidOperation
from .seller import Trade, SellerRawData


class LoanLevelAssumption(models.Model):
    """Model to store assumptions for individual loan-level calculations"""
    seller_raw_data = models.ForeignKey(SellerRawData, on_delete=models.CASCADE, related_name='loan_assumptions')
    
    # Timeline assumptions
    months_to_resolution = models.IntegerField(help_text="Estimated months to resolve the loan")
    probability_of_cure = models.DecimalField(
        max_digits=5, 
        decimal_places=4,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Probability between 0 and 1"
    )
    probability_of_foreclosure = models.DecimalField(
        max_digits=5, 
        decimal_places=4,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Probability between 0 and 1"
    )
    
    # Financial assumptions
    recovery_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=4,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Expected recovery percentage of principal"
    )
    monthly_carrying_cost = models.DecimalField(max_digits=10, decimal_places=2)
    legal_costs = models.DecimalField(max_digits=10, decimal_places=2)
    foreclosure_costs = models.DecimalField(max_digits=10, decimal_places=2)
    property_preservation_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # REO assumptions (if foreclosure)
    estimated_reo_months = models.IntegerField(default=0)
    estimated_rehab_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_resale_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Loan Level Assumption"
        verbose_name_plural = "Loan Level Assumptions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller_raw_data']),
        ]
        db_table = 'loan_level_assumptions'
    
    def __str__(self):
        return f"Assumption for Loan {self.seller_raw_data.id}"


class StaticModelAssumptions(models.Model):
    """DEPRECATED: Singleton model for static assumptions - TO BE REMOVED.
    
    ⚠️ DEPRECATION NOTICE ⚠️
    This model is DEPRECATED and will be removed in a future migration.
    
    Why deprecated:
    - Singleton pattern is overly complex for this use case
    - Doesn't support multiple concurrent trades with different assumptions
    - TradeLevelAssumption now has default values for all fields
    
    Migration plan:
    1. All new trades should use TradeLevelAssumption with defaults
    2. Do NOT create new references to this model
    3. Once all trades are migrated, this model will be deleted
    4. Admin registration will be removed
    
    Use instead:
    - TradeLevelAssumption with default field values
    - Each trade gets its own independent assumptions
    
    Original purpose (now handled by TradeLevelAssumption defaults):
    - Stored global default assumptions
    - Singleton pattern (only one record)
    - Used as fallback values
    """
    
    # Singleton ID (always 1)
    id = models.IntegerField(primary_key=True, default=1, editable=False)
    
    # Name/version for tracking changes
    version_name = models.CharField(max_length=100, default="Default", help_text="Version name for tracking assumption changes")
    
    # Perf/RPL assumptions
    perf_rpl_hold_period = models.IntegerField(help_text="Default hold period for performing/re-performing loans (months)")
    
    # Modification assumptions (default parameters)
    mod_rate = models.DecimalField(max_digits=6, decimal_places=4, help_text="Default modification interest rate")
    mod_legal_term = models.IntegerField(help_text="Default modification legal term in months")
    mod_amort_term = models.IntegerField(help_text="Default modification amortization term in months")
    max_mod_ltv = models.DecimalField(max_digits=6, decimal_places=4, help_text="Maximum loan-to-value ratio for modifications (e.g., 0.95 for 95%)")
    mod_io_flag = models.BooleanField(default=False, help_text="Default IO (interest-only) flag for modifications")
    mod_down_pmt = models.DecimalField(max_digits=6, decimal_places=4, help_text="Default modification down payment percentage")
    mod_orig_cost = models.DecimalField(max_digits=6, decimal_places=4, help_text="Default modification original cost percentage")
    mod_setup = models.DecimalField(max_digits=6, decimal_places=4, help_text="Default modification setup cost percentage")
    mod_hold = models.IntegerField(help_text="Default modification hold period in months")

    #Acq costs
    acq_legal_cost = models.DecimalField(max_digits=6, decimal_places=4, help_text="Default acquisition legal cost percentage")
    acq_dd_cost = models.DecimalField(max_digits=6, decimal_places=4, help_text="Default acquisition due diligence cost percentage")
    acq_tax_title_cost = models.DecimalField(max_digits=6, decimal_places=4, help_text="Default acquisition tax title cost percentage")
    
    #AM Fees
    am_fee_pct = models.DecimalField(max_digits=6, decimal_places=4, help_text="Default AM fee percentage")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Static Model Assumptions (Settings)"
        verbose_name_plural = "Static Model Assumptions (Settings)"
        db_table = 'static_model_assumptions'
    
    def save(self, *args, **kwargs):
        """Override save to enforce singleton pattern - only allow id=1"""
        self.id = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of the singleton settings record"""
        pass
    
    @classmethod
    def load(cls):
        """Load the singleton instance, creating it if it doesn't exist.
        
        Returns:
            StaticModelAssumptions: The single settings instance
        """
        obj, created = cls.objects.get_or_create(
            id=1,
            defaults={
                'version_name': 'Default',
                'perf_rpl_hold_period': 12,  # 12 months
                'mod_rate': 0.0400,  # 4%
                'mod_legal_term': 360,  # 30 years
                'mod_amort_term': 360,  # 30 years
                'max_mod_ltv': 0.95,  # 95%
                'mod_io_flag': False,  # Not IO by default
                'mod_down_pmt': 0.05,  # 5% down payment
                'mod_orig_cost': 0.02,  # 2% origination cost
                'mod_setup': 0.01,  # 1% setup cost
                'mod_hold': 6,  # 6 months hold
                'acq_legal_cost': 0.005,  # 0.5% legal cost
                'acq_dd_cost': 0.003,  # 0.3% due diligence
                'acq_tax_title_cost': 0.002,  # 0.2% tax/title
                'am_fee_pct': 0.01,  # 1% AM fee
            }
        )
        return obj
    
    def __str__(self):
        return f"Model Assumptions ({self.version_name})"


class TradeLevelAssumption(models.Model):
    """Model to store trade-specific assumptions for portfolio calculations.
    
    What this does:
    - Stores all assumptions for a specific trade/deal
    - Each trade can have different assumption values
    - Default values provide baseline assumptions
    - Override defaults as needed for specific trades
    
    How it works:
    - Create one record per trade
    - Fields have sensible defaults that can be customized
    - Each trade operates independently with its own assumptions
    """
    
    # Link to the trade
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name='trade_assumptions')
    
    # Optional: selected servicer for this trade
    servicer = models.ForeignKey(
        'core.Servicer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trade_level_assumptions',
        help_text="Selected servicing company for this trade",
    )
    
    # Trade dates
    bid_date = models.DateField(null=True, blank=True, help_text="Date the bid was submitted")
    settlement_date = models.DateField(null=True, blank=True, help_text="Expected or actual settlement date")
    servicing_transfer_date = models.DateField(null=True, blank=True, help_text="Date servicing transfers to new servicer")
    
    # Trade-specific financial assumptions
    pctUPB = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Purchase price as percentage of UPB")
    target_irr = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True, help_text="Target internal rate of return for this trade")
    discount_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0.12, null=True, blank=True, help_text="Discount rate for NPV calculations")
    
    # Perf/RPL assumptions
    perf_rpl_hold_period = models.IntegerField(default=12, null=True, blank=True, help_text="Hold period for performing/re-performing loans (months)")
    
    # Modification assumptions
    mod_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0.0400, null=True, blank=True, help_text="Modification interest rate as decimal (e.g., 0.04 = 4%)")
    mod_legal_term = models.IntegerField(default=360, null=True, blank=True, help_text="Modification legal term in months")
    mod_amort_term = models.IntegerField(default=360, null=True, blank=True, help_text="Modification amortization term in months")
    max_mod_ltv = models.DecimalField(max_digits=6, decimal_places=4, default=0.95, null=True, blank=True, help_text="Maximum LTV for modifications as decimal (e.g., 0.95 = 95%)")
    mod_io_flag = models.BooleanField(default=False, null=True, blank=True, help_text="IO (interest-only) flag for modifications")
    mod_down_pmt = models.DecimalField(max_digits=6, decimal_places=4, default=0.05, null=True, blank=True, help_text="Modification down payment as decimal (e.g., 0.05 = 5%)")
    mod_orig_cost = models.DecimalField(max_digits=10, decimal_places=2, default=500.00, null=True, blank=True, help_text="Modification origination cost in dollars per loan")
    mod_setup_duration = models.IntegerField(default=6, null=True, blank=True, help_text="Modification setup duration in months")
    mod_hold_duration = models.IntegerField(default=6, null=True, blank=True, help_text="Modification hold duration in months")
    
    # Acquisition costs (dollar amounts per loan)
    acq_legal_cost = models.DecimalField(max_digits=10, decimal_places=2, default=300.00, null=True, blank=True, help_text="Acquisition legal cost in dollars per loan")
    acq_dd_cost = models.DecimalField(max_digits=10, decimal_places=2, default=150.00, null=True, blank=True, help_text="Acquisition due diligence cost in dollars per loan")
    acq_tax_title_cost = models.DecimalField(max_digits=10, decimal_places=2, default=100.00, null=True, blank=True, help_text="Acquisition tax/title cost in dollars per loan")
    acq_broker_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True, help_text="Acquisition broker fees in dollars per loan")
    acq_other_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True, help_text="Acquisition other costs in dollars per loan")
    
    # Liq Fees (percentage as decimal)
    liq_am_fee_pct = models.DecimalField(max_digits=6, decimal_places=4, default=0.01, null=True, blank=True, help_text="Asset management fee as decimal (e.g., 0.01 = 1%)")
    liq_broker_cc_pct = models.DecimalField(max_digits=6, decimal_places=4, default=0.01, null=True, blank=True, help_text="Broker closing cost as decimal (e.g., 0.01 = 1%)")
    liq_tax_transfer_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True, help_text="Tax transfer cost in dollars per loan")
    liq_title_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True, help_text="Title cost in dollars per loan")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Trade Level Assumption"
        verbose_name_plural = "Trade Level Assumptions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trade']),
            models.Index(fields=['servicer']),
            models.Index(fields=['bid_date']),
        ]
        db_table = 'trade_level_assumptions'
    
    def __str__(self):
        return f"Trade Assumptions for {self.trade.trade_name}"


class NoteSaleAssumption(models.Model):
    """Model to store note sale discount factors.
    
    What this does:
    - Each record represents a single discount factor for a specific metric and range
    - Factor types: Balance, Maturity, FICO, etc.
    - Index order determines calculation sequence (1-5)
    - Simple, flexible structure allows unlimited factor combinations
    
    How it works:
    - Create multiple records for different factor types and ranges
    - Each record has min/max range and discount factor
    - Final percentage = base_percentage * (all matching discount factors)
    - Index order ensures consistent calculation sequence
    """
    
    class FactorType(models.TextChoices):
        """Factor types for note sale calculations."""
        BALANCE = 'BALANCE', 'Current Balance'
        MATURITY = 'MATURITY', 'Months to Maturity'
        FICO = 'FICO', 'FICO Score'
        LTV = 'LTV', 'Loan-to-Value Ratio'
        PROPERTY_TYPE = 'PROPERTY_TYPE', 'Property Type'
    
    # Factor type dropdown
    factor_type = models.CharField(
        max_length=20,
        choices=FactorType.choices,
        help_text="Type of factor this discount applies to"
    )
    
    # Descriptive name for this factor
    factor_name = models.CharField(
        max_length=100,
        help_text="Descriptive name (e.g., 'High Balance Premium', 'Poor Credit Discount')"
    )
    
    # Index order for calculation sequence (1-5)
    index_order = models.IntegerField(
        default=1,
        help_text="Calculation order (1-5, lower numbers calculated first)"
    )
    
    # Range values (flexible to handle different data types)
    range_min = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum value for this range (null = no minimum)"
    )
    range_max = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum value for this range (null = no maximum)"
    )
    
    # String value for non-numeric factors (e.g., property type)
    range_value = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Exact value match for string factors (e.g., 'SFR', 'Condo')"
    )
    
    # The discount factor for this range
    discount_factor = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        default=1.0000,
        help_text="Discount factor (e.g., 0.9000 = 90%, 1.1000 = 110%)"
    )
    
    # Priority for overlapping ranges within same factor type
    priority = models.IntegerField(
        default=0,
        help_text="Priority when multiple ranges match same factor type (higher wins)"
    )
    
    # Optional notes
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this discount factor"
    )
    
    # Active flag to enable/disable factors
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this discount factor is currently active"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Note Sale Assumption"
        verbose_name_plural = "Note Sale Assumptions"
        ordering = ['index_order', 'factor_type', '-priority', 'factor_name']
        indexes = [
            models.Index(fields=['factor_type', 'is_active']),
            models.Index(fields=['index_order', 'priority']),
            models.Index(fields=['range_min', 'range_max']),
        ]
        db_table = 'note_sale_assumptions'
    
    def __str__(self):
        return f"{self.factor_name} ({self.get_factor_type_display()}: {self.discount_factor:.1%})"
    
    def matches_value(self, value) -> bool:
        """Check if this discount factor applies to the given value.
        
        Args:
            value: The value to check (could be numeric or string)
            
        Returns:
            bool: True if this discount factor applies to the value
        """
        # Handle string/exact value matches (e.g., property type)
        if self.range_value is not None:
            return str(value).upper() == self.range_value.upper()
        
        # Handle numeric range matches
        try:
            numeric_value = Decimal(str(value))
            
            # Check minimum range
            if self.range_min is not None and numeric_value < self.range_min:
                return False
                
            # Check maximum range
            if self.range_max is not None and numeric_value > self.range_max:
                return False
                
            return True
            
        except (ValueError, TypeError, InvalidOperation):
            # If value can't be converted to Decimal, no match
            return False
    
    @classmethod
    def get_applicable_factors(cls, factor_type: str, value, base_percentage: Decimal = Decimal('1.0000')) -> Decimal:
        """Get all applicable discount factors for a specific factor type and value.
        
        Args:
            factor_type: The type of factor (e.g., 'BALANCE', 'FICO')
            value: The value to match against
            base_percentage: Base percentage to start with
            
        Returns:
            Decimal: Final percentage after applying all matching factors
        """
        # Get all active factors for this type, ordered by priority
        factors = cls.objects.filter(
            factor_type=factor_type,
            is_active=True
        ).order_by('-priority', '-id')
        
        # Find the first (highest priority) matching factor
        for factor in factors:
            if factor.matches_value(value):
                discount = (
                    factor.discount_factor
                    if isinstance(factor.discount_factor, Decimal)
                    else Decimal(str(factor.discount_factor))
                )
                return (base_percentage * discount).quantize(Decimal('0.0001'))
        
        # If no factors match, return base percentage unchanged
        return base_percentage


# =============================================================================
# UTILITY AND PROPERTY MANAGEMENT ASSUMPTION MODELS
# =============================================================================

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
    
    # Property type matching SellerRawData.PropertyType choices
    property_type = models.CharField(
        max_length=20,
        choices=SellerRawData.PropertyType.choices,
        unique=True,
        help_text="Property type matching SellerRawData.PropertyType choices"
    )
    
    # Utility assumptions (monthly costs in dollars)
    utility_electric_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Monthly electric utility cost in dollars"
    )
    utility_gas_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Monthly gas utility cost in dollars"
    )
    utility_water_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Monthly water utility cost in dollars"
    )
    utility_sewer_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Monthly sewer utility cost in dollars"
    )
    utility_trash_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Monthly trash utility cost in dollars"
    )
    utility_other_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Monthly other utility costs in dollars"
    )
    
    # Property management assumptions (monthly costs in dollars)
    property_management_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Monthly property management cost in dollars"
    )
    repairs_maintenance_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Monthly repairs and maintenance cost in dollars"
    )
    marketing_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Monthly marketing cost in dollars"
    )
    
    # One-time costs (in dollars)
    trashout_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="One-time trashout cost in dollars"
    )
    renovation_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="One-time renovation cost in dollars"
    )
    security_cost_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Monthly security cost in dollars"
    )
    landscaping_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Monthly landscaping cost in dollars"
    )
    pool_maintenance_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
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
        """Calculate total monthly utility costs."""
        return (
            self.utility_electric_monthly + 
            self.utility_gas_monthly + 
            self.utility_water_monthly + 
            self.utility_sewer_monthly + 
            self.utility_trash_monthly + 
            self.utility_other_monthly
        ).quantize(Decimal('0.01'))
    
    def total_monthly_property_management(self) -> Decimal:
        """Calculate total monthly property management costs."""
        return (
            self.property_management_monthly + 
            self.repairs_maintenance_monthly + 
            self.marketing_monthly + 
            self.security_cost_monthly + 
            self.landscaping_monthly + 
            self.pool_maintenance_monthly
        ).quantize(Decimal('0.01'))
    
    def total_one_time_costs(self) -> Decimal:
        """Calculate total one-time costs."""
        return (
            self.trashout_cost + 
            self.renovation_cost
        ).quantize(Decimal('0.01'))


class SquareFootageAssumption(models.Model):
    """
    Square footage-based assumptions for utilities and property management costs.
    
    What this does:
    - Stores per-square-foot cost assumptions
    - Separate tables for residential vs commercial properties
    - Used as primary assumption source when square footage is available
    
    How it works:
    - Define cost per square foot for different ranges
    - Multiply by actual property square footage
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
    
    # Square footage range
    sqft_min = models.IntegerField(
        help_text="Minimum square footage for this range (inclusive)"
    )
    sqft_max = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum square footage for this range (inclusive). Null = no maximum"
    )
    
    # Utility assumptions (cost per square foot per month)
    utility_electric_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Electric cost per square foot per month"
    )
    utility_gas_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Gas cost per square foot per month"
    )
    utility_water_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Water cost per square foot per month"
    )
    utility_sewer_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Sewer cost per square foot per month"
    )
    utility_trash_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Trash cost per square foot per month"
    )
    utility_other_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Other utility cost per square foot per month"
    )
    
    # Property management assumptions (cost per square foot per month)
    property_management_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Property management cost per square foot per month"
    )
    repairs_maintenance_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Repairs and maintenance cost per square foot per month"
    )
    marketing_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Marketing cost per square foot per month"
    )
    security_cost_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Security cost per square foot per month"
    )
    landscaping_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Landscaping cost per square foot per month"
    )
    pool_maintenance_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Pool maintenance cost per square foot per month"
    )
    
    # One-time costs (cost per square foot)
    trashout_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Trashout cost per square foot (one-time)"
    )
    renovation_per_sqft = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Renovation cost per square foot (one-time)"
    )
    
    # Metadata
    description = models.CharField(
        max_length=200,
        help_text="Description of this square footage range"
    )
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
        ordering = ['property_category', 'sqft_min']
        indexes = [
            models.Index(fields=['property_category', 'sqft_min', 'sqft_max']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(sqft_min__gte=0),
                name='sqft_min_non_negative'
            ),
            models.CheckConstraint(
                check=models.Q(sqft_max__isnull=True) | models.Q(sqft_max__gte=models.F('sqft_min')),
                name='sqft_max_gte_min'
            ),
        ]
    
    def __str__(self):
        max_display = f"{self.sqft_max:,}" if self.sqft_max else "∞"
        return f"{self.get_property_category_display()}: {self.sqft_min:,} - {max_display} sqft"
    
    def matches_square_footage(self, square_footage: int) -> bool:
        """Check if this assumption applies to the given square footage."""
        if square_footage < self.sqft_min:
            return False
        if self.sqft_max is not None and square_footage > self.sqft_max:
            return False
        return True
    
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
