#Assumptions Django Models: Servicing, State Reference, Loan Level Assumptions, Trade Level Assumptions

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
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
    bid_date = models.DateField(help_text="Date the bid was submitted")
    settlement_date = models.DateField(help_text="Expected or actual settlement date")
    servicing_transfer_date = models.DateField(null=True, blank=True, help_text="Date servicing transfers to new servicer")
    
    # Trade-specific financial assumptions
    pctUPB = models.DecimalField(max_digits=15, decimal_places=2, help_text="Purchase price as percentage of UPB")
    target_irr = models.DecimalField(max_digits=6, decimal_places=4, help_text="Target internal rate of return for this trade")
    discount_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0.12, help_text="Discount rate for NPV calculations")
    
    # Perf/RPL assumptions
    perf_rpl_hold_period = models.IntegerField(default=12, help_text="Hold period for performing/re-performing loans (months)")
    
    # Modification assumptions
    mod_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0.0400, help_text="Modification interest rate as decimal (e.g., 0.04 = 4%)")
    mod_legal_term = models.IntegerField(default=360, help_text="Modification legal term in months")
    mod_amort_term = models.IntegerField(default=360, help_text="Modification amortization term in months")
    max_mod_ltv = models.DecimalField(max_digits=6, decimal_places=4, default=0.95, help_text="Maximum LTV for modifications as decimal (e.g., 0.95 = 95%)")
    mod_io_flag = models.BooleanField(default=False, help_text="IO (interest-only) flag for modifications")
    mod_down_pmt = models.DecimalField(max_digits=6, decimal_places=4, default=0.05, help_text="Modification down payment as decimal (e.g., 0.05 = 5%)")
    mod_orig_cost = models.DecimalField(max_digits=10, decimal_places=2, default=500.00, help_text="Modification origination cost in dollars per loan")
    mod_setup_duration = models.IntegerField(default=6, help_text="Modification setup duration in months")
    mod_hold_duration = models.IntegerField(default=6, help_text="Modification hold duration in months")
    
    # Acquisition costs (dollar amounts per loan)
    acq_legal_cost = models.DecimalField(max_digits=10, decimal_places=2, default=300.00, help_text="Acquisition legal cost in dollars per loan")
    acq_dd_cost = models.DecimalField(max_digits=10, decimal_places=2, default=150.00, help_text="Acquisition due diligence cost in dollars per loan")
    acq_tax_title_cost = models.DecimalField(max_digits=10, decimal_places=2, default=100.00, help_text="Acquisition tax/title cost in dollars per loan")
    
    # Asset management fees (percentage as decimal)
    am_fee_pct = models.DecimalField(max_digits=6, decimal_places=4, default=0.01, help_text="Asset management fee as decimal (e.g., 0.01 = 1%)")
    
    
    
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
