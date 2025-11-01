#Assumptions Django Models: Servicing, State Reference, Loan Level Assumptions, Trade Level Assumptions

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal, InvalidOperation
from .model_acq_seller import Trade, SellerRawData


class LoanLevelAssumption(models.Model):
    """Model to store assumptions for individual loan-level calculations"""
    # WHAT: Foreign key to AssetIdHub (not SellerRawData)
    # WHY: Join directly with asset hub for better data consistency
    asset_hub = models.ForeignKey('core.AssetIdHub', on_delete=models.CASCADE, related_name='loan_assumptions')
    
    # Timeline assumptions
    months_to_resolution = models.IntegerField(
        null=True,
        blank=True,
        help_text="Estimated months to resolve the loan"
    )
    probability_of_cure = models.DecimalField(
        max_digits=5, 
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Probability between 0 and 1"
    )
    probability_of_foreclosure = models.DecimalField(
        max_digits=5, 
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Probability between 0 and 1"
    )
    
    # Financial assumptions
    recovery_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Expected recovery percentage of principal"
    )
    monthly_carrying_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    legal_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    foreclosure_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    property_preservation_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # REO assumptions (if foreclosure)
    estimated_reo_months = models.IntegerField(default=0, null=True, blank=True)
    estimated_rehab_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    estimated_resale_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # FC duration override (user adjustment in months)
    fc_duration_override_months = models.IntegerField(
        null=True,
        blank=True,
        help_text="User override to adjust FC duration in months (positive adds months, negative subtracts months from calculated FC duration). NULL means no override."
    )
    
    # Acquisition price (user-entered or calculated)
    acquisition_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="User-entered acquisition price for this asset. If not set, will be calculated from trade assumptions."
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Loan Level Assumption"
        verbose_name_plural = "Loan Level Assumptions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['asset_hub']),
        ]
        db_table = 'loan_level_assumptions'
    
    def __str__(self):
        return f"Assumption for Asset Hub {self.asset_hub_id}"


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
    servicing_transfer_date = models.DateField(null=True, blank=True, help_text="Date servicing transfers to new servicer (defaults to settlement_date + 30 days if not set)")
    
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
    
    @property
    def effective_servicing_transfer_date(self):
        """
        Get the effective servicing transfer date with fallback logic.
        
        What: Returns servicing_transfer_date if set, otherwise calculates as settlement_date + 30 days
        Why: Provide default behavior when servicing_transfer_date is not explicitly set
        Where: Used by service layer for timeline calculations
        How: Checks if servicing_transfer_date exists, if not calculates from settlement_date
        
        Returns:
            date: The servicing_transfer_date if set, or settlement_date + 30 days if settlement_date exists,
                  or None if neither is available
        """
        # WHAT: Return explicit servicing_transfer_date if set
        # WHY: User-specified value takes priority
        if self.servicing_transfer_date:
            return self.servicing_transfer_date
        
        # WHAT: Calculate fallback as settlement_date + 30 days
        # WHY: Default behavior when servicing_transfer_date not set
        if self.settlement_date:
            from datetime import timedelta
            return self.settlement_date + timedelta(days=30)
        
        # WHAT: Return None if neither date is available
        # WHY: Cannot calculate without settlement_date
        return None


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
