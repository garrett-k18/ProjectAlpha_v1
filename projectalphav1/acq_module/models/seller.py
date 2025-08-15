#Seller Data Django Model. Contains Seller, Trade and Raw Data models

from django.db import models


class Seller(models.Model):
    """One seller can have many trades...Need to make sure IDs start at 1000"""
    name = models.CharField(max_length=100)
    broker = models.CharField(max_length=100)
    email = models.EmailField()
    poc = models.CharField(max_length=100)

    
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
    trade_name = models.CharField(max_length=100)
   
    
    def __str__(self):
        return f"Trade for {self.seller.name}"

    class Meta:
        verbose_name = "Trade"
        verbose_name_plural = "Trades"
        ordering = ['trade_name']
        indexes = [
            models.Index(fields=['seller']),
        ]


class SellerRawData(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='seller_raw_data')
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name='seller_raw_data')
    sellertape_id = models.IntegerField()
    asset_status = models.CharField(max_length=100)
    as_of_date = models.DateField()
    
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2)
    deferred_balance = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=6, decimal_places=4)
    next_due_date = models.DateField()
    last_paid_date = models.DateField()
    
    first_pay_date = models.DateField()
    origination_date = models.DateField()
    original_balance = models.DecimalField(max_digits=15, decimal_places=2)
    original_term = models.IntegerField()
    original_rate = models.DecimalField(max_digits=6, decimal_places=4)
    original_maturity_date = models.DateField()
    
    default_rate = models.DecimalField(max_digits=6, decimal_places=4)
    months_dlq = models.IntegerField(null=True, blank=True)
    current_maturity_date = models.DateField()
    current_term = models.IntegerField()
    
    accrued_note_interest = models.DecimalField(max_digits=15, decimal_places=2)
    accrued_default_interest = models.DecimalField(max_digits=15, decimal_places=2)
    escrow_balance = models.DecimalField(max_digits=15, decimal_places=2)
    escrow_advance = models.DecimalField(max_digits=15, decimal_places=2)
    recoverable_corp_advance = models.DecimalField(max_digits=15, decimal_places=2)
    late_fees = models.DecimalField(max_digits=15, decimal_places=2)
    other_fees = models.DecimalField(max_digits=15, decimal_places=2)
    suspense_balance = models.DecimalField(max_digits=15, decimal_places=2)
    total_debt = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    origination_value = models.DecimalField(max_digits=15, decimal_places=2)
    origination_arv = models.DecimalField(max_digits=15, decimal_places=2)
    origination_value_date = models.DateField()
    
    seller_value_date = models.DateField()
    seller_arv_value = models.DecimalField(max_digits=15, decimal_places=2)

    seller_asis_value = models.DecimalField(max_digits=15, decimal_places=2)
    additional_asis_value = models.DecimalField(max_digits=15, decimal_places=2)
    additional_arv_value = models.DecimalField(max_digits=15, decimal_places=2)
    additional_value_date = models.DateField()

    fc_flag = models.BooleanField(default=False)
    fc_first_legal_date = models.DateField(null=True, blank=True)
    fc_referred_date = models.DateField(null=True, blank=True)
    fc_judgement_date = models.DateField(null=True, blank=True)
    fc_scheduled_sale_date = models.DateField(null=True, blank=True)
    fc_sale_date = models.DateField(null=True, blank=True)
    fc_starting = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    bk_flag = models.BooleanField(default=False)
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
        unique_together = ('seller', 'trade')
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
        """Override save method to calculate values if not provided"""
        # If total_debt is not provided, calculate it
        if self.total_debt is None:
            self.total_debt = self.calculate_total_debt()
        
        # If months_dlq is not provided, calculate it
        if self.months_dlq is None:
            self.months_dlq = self.calculate_months_dlq()
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Seller Raw Data {self.id} - {self.seller.name} - {self.trade.trade_name}"
