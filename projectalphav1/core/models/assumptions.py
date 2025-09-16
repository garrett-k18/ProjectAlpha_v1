from django.db import models
class Servicer(models.Model):
    """Model to store servicer information for loan servicing"""
    servicer_name = models.CharField(max_length=100, unique=True)
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    
    # Fees and rates
    servicing_transfer_duration = models.IntegerField()
    board_fee = models.DecimalField(max_digits=10, decimal_places=2)
    current_fee = models.DecimalField(max_digits=10, decimal_places=2)
    thirtday_fee = models.DecimalField(max_digits=10, decimal_places=2)
    sixtyday_fee = models.DecimalField(max_digits=10, decimal_places=2)
    ninetyday_fee = models.DecimalField(max_digits=10, decimal_places=2)
    onetwentyday_fee = models.DecimalField(max_digits=10, decimal_places=2)
    fc_fee = models.DecimalField(max_digits=10, decimal_places=2)
    bk_fee = models.DecimalField(max_digits=10, decimal_places=2)
    mod_fee = models.DecimalField(max_digits=10, decimal_places=2)
    dil_fee = models.DecimalField(max_digits=10, decimal_places=2)
    thirdparty_fee = models.DecimalField(max_digits=10, decimal_places=2)
    reo_fee = models.DecimalField(max_digits=10, decimal_places=2)
    reo_days = models.IntegerField()
    liqfee_pct = models.DecimalField(max_digits=10, decimal_places=2)
    liqfee_flat = models.DecimalField(max_digits=10, decimal_places=2)
        
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
    

    # Tax data
    property_tax_rate = models.DecimalField(max_digits=5, decimal_places=4, help_text="Average property tax rate")
    transfer_tax_rate = models.DecimalField(max_digits=5, decimal_places=4, help_text="Tax rate for property transfers")
    insurance_rate_avg = models.DecimalField(max_digits=5, decimal_places=4, help_text="Average insurance rate")
    
    # Legal fees
    fc_legal_fees_avg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average legal fees for foreclosure")
    dil_cost_avg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average dilution cost")
    cfk_cost_avg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average CFK cost")
    
    value_adjustment_annual = models.DecimalField(max_digits=10, decimal_places=4, help_text="Average value adjustment")
    


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