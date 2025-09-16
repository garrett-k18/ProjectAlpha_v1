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


class TradeLevelAssumption(models.Model):
    """Model to store assumptions at the trade level for portfolio calculations"""
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name='trade_assumptions')
    bid_date = models.DateField()
    settlement_date = models.DateField()
    
    
    # Financial assumptions
    pctUPB = models.DecimalField(max_digits=15, decimal_places=2)
    target_irr = models.DecimalField(max_digits=6, decimal_places=4)
    discount_rate = models.DecimalField(max_digits=6, decimal_places=4)
    
    # Timeline assumptions
    perf_rpl_hold_period = models.IntegerField()
    servicing_transfer_date = models.DateField(null=True, blank=True)

    # Mod Assumptions
    mod_rate = models.DecimalField(max_digits=6, decimal_places=4)
    mod_term = models.IntegerField()
    mod_balance = models.DecimalField(max_digits=15, decimal_places=2)
    mod_date = models.DateField(null=True, blank=True)
    mod_maturity_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Trade Level Assumption"
        verbose_name_plural = "Trade Level Assumptions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trade']),
        ]
        db_table = 'trade_level_assumptions'
    
    def __str__(self):
        return f"Trade Assumptions for {self.trade.trade_name}"
