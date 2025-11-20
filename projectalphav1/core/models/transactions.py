"""
WHAT: LLTransactionSummary model - Rollup of GL entries for realized P&L tracking
WHY: Provides realized column data for Performance Summary by aggregating actual transactions
HOW: One-to-one with AssetIdHub, fields mirror Performance Summary structure
WHERE: Used by serial_performance_summary.py to populate *_realized fields
"""
from django.db import models
from decimal import Decimal


class LLTransactionSummary(models.Model):
    """
    WHAT: Transaction summary rollup for loan-level realized P&L
    WHY: Track actual income/expenses vs underwritten projections
    HOW: Aggregates GL entries, updated by transaction processing
    """
    
    # ------------------------------
    # Primary Key / Relationship
    # ------------------------------
    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='ll_transaction_summary',
        primary_key=True,
        help_text='The AssetIdHub this transaction summary belongs to.'
    )
    
    # ------------------------------
    # Purchase Cost (Realized)
    # ------------------------------
    purchase_price_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual purchase price paid'
    )
    
    gross_purchase_price_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual gross purchase price paid'
    )
    # ------------------------------
    # Acquisition Costs (Realized)
    # ------------------------------
    acq_due_diligence_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual due diligence costs'
    )
    acq_legal_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual legal costs for acquisition'
    )
    acq_title_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual title costs'
    )
    acq_other_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual other acquisition costs'
    )
    
    # ------------------------------
    # Income (Realized)
    # ------------------------------
    income_principal_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual principal collected'
    )
    income_interest_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual interest collected'
    )
    income_rent_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual rent collected'
    )
    income_cam_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual CAM income'
    )
    income_mod_down_payment_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual modification down payment'
    )
    
    # ------------------------------
    # Operating Expenses (Realized)
    # ------------------------------
    expense_servicing_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual servicing fees paid'
    )
    expense_am_fees_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual asset management fees'
    )
    expense_property_tax_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual property taxes paid'
    )
    expense_property_insurance_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual property insurance paid'
    )
    
    # ------------------------------
    # Legal/DIL Costs (Realized)
    # ------------------------------
    legal_foreclosure_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual foreclosure fees'
    )
    legal_bankruptcy_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual bankruptcy legal fees'
    )
    legal_dil_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual DIL fees'
    )
    legal_cash_for_keys_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual cash for keys fees'
    )
    legal_eviction_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual eviction fees'
    )
    
    # ------------------------------
    # REO Expenses (Realized)
    # ------------------------------
    reo_hoa_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual HOA fees paid'
    )
    reo_utilities_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual utilities paid'
    )
    reo_trashout_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual trashout costs'
    )
    reo_renovation_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual renovation costs'
    )
    reo_property_preservation_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual property preservation costs'
    )
    
    # ------------------------------
    # CRE Expenses (Realized)
    # ------------------------------
    cre_marketing_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual marketing costs'
    )
    cre_ga_pool_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual G&A pool/groundskeeping costs'
    )
    cre_maintenance_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual maintenance costs'
    )
    
    # ------------------------------
    # Fund Expenses (Realized)
    # ------------------------------
    fund_taxes_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual fund-level taxes'
    )
    fund_legal_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual fund-level legal costs'
    )
    fund_consulting_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual fund-level consulting costs'
    )
    fund_audit_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual fund-level audit costs'
    )
    
    # ------------------------------
    # Gross Liquidation Proceeds (Realized)
    # ------------------------------
    proceeds_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual gross liquidation proceeds'
    )
    broker_closing_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual broker closing costs'
    )
    other_closing_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual other closing costs'
    )
    net_liquidation_proceeds_realized = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Actual net liquidation proceeds'
    )
    realized_gross_cost = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Realized gross cost basis (aggregated actual costs)'
    )
    
    # ------------------------------
    # Metadata
    # ------------------------------
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text='Last time this summary was updated from GL entries'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When this summary record was created'
    )
    
    class Meta:
        db_table = 'll_transaction_summary'
        verbose_name = 'Loan-Level Transaction Summary'
        verbose_name_plural = 'Loan-Level Transaction Summaries'
        ordering = ['asset_hub']
    
    def __str__(self):
        return f"Transaction Summary for Asset {self.asset_hub_id}"


class LLCashFlowSeries(models.Model):
    """
    WHAT: Period-by-period cash flow breakdown for loan-level time series analysis
    WHY: Bridge GL transactions to cash flow analytics (IRR, NPV) with temporal granularity
    HOW: One record per asset per period with all P&L line items aggregated by date
    WHERE: Fed into amortization and numpy-financial libraries for cash flow calculations
    """
    
    # ------------------------------
    # Primary Key / Relationship
    # ------------------------------
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='ll_cash_flow_series',
        help_text='The AssetIdHub this cash flow period belongs to'
    )
    # Note: purchase_date comes from asset_hub.blended_outcome_model.purchase_date
    # No need to duplicate it here - we'll reference it in save() method
    period_date = models.DateField(
        help_text='Period start date (calculated from purchase_date + period_number months)'
    )
    period_number = models.IntegerField(
        help_text='Sequential period number (0=acquisition, 1=first month, etc.)'
    )
    
    # ------------------------------
    # Purchase Cost (Period 0 only)
    # ------------------------------
    purchase_price = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Purchase price (negative cash flow in period 0)'
    )
    
    # ------------------------------
    # Acquisition Costs (Period 0 only)
    # ------------------------------
    acq_due_diligence_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Due diligence costs for this period'
    )
    acq_legal_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Legal costs for acquisition in this period'
    )
    acq_title_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Title costs for this period'
    )
    acq_other_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Other acquisition costs for this period'
    )
    
    # ------------------------------
    # Income (Positive Cash Flows)
    # ------------------------------
    income_principal = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Principal collected in this period'
    )
    income_interest = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Interest collected in this period'
    )
    income_rent = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Rent collected in this period'
    )
    income_cam = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='CAM income for this period'
    )
    income_mod_down_payment = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Modification down payment for this period'
    )
    
    # ------------------------------
    # Operating Expenses (Negative Cash Flows)
    # ------------------------------
    servicing_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Servicing fees paid in this period'
    )
    am_fees_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Asset management fees for this period'
    )
    property_tax_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Property taxes paid in this period'
    )
    property_insurance_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Property insurance paid in this period'
    )
    
    # ------------------------------
    # Legal/DIL Costs (Negative Cash Flows)
    # ------------------------------
    legal_foreclosure_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Foreclosure fees for this period'
    )
    legal_bankruptcy_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Bankruptcy legal fees for this period'
    )
    legal_dil_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='DIL fees for this period'
    )
    legal_cash_for_keys_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Cash for keys fees for this period'
    )
    legal_eviction_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Eviction fees for this period'
    )
    
    # ------------------------------
    # REO Expenses (Negative Cash Flows)
    # ------------------------------
    reo_hoa_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='HOA fees paid in this period'
    )
    reo_utilities_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Utilities paid in this period'
    )
    reo_trashout_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Trashout costs for this period'
    )
    reo_renovation_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Renovation costs for this period'
    )
    reo_property_preservation_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Property preservation costs for this period'
    )
    
    # ------------------------------
    # CRE Expenses (Negative Cash Flows)
    # ------------------------------
    cre_marketing_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Marketing costs for this period'
    )
    cre_ga_pool_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='G&A pool/groundskeeping costs for this period'
    )
    cre_maintenance_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Maintenance costs for this period'
    )
    
    # ------------------------------
    # Fund Expenses (Negative Cash Flows)
    # ------------------------------
    fund_taxes_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Fund-level taxes for this period'
    )
    fund_legal_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Fund-level legal costs for this period'
    )
    fund_consulting_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Fund-level consulting costs for this period'
    )
    fund_audit_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Fund-level audit costs for this period'
    )
    
    # ------------------------------
    # Gross Liquidation Proceeds (Positive Cash Flow)
    # ------------------------------
    proceeds = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Gross liquidation proceeds for this period'
    )
    broker_closing_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Broker closing costs for this period'
    )
    other_closing_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Other closing costs for this period'
    )
    net_liquidation_proceeds = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Net liquidation proceeds for this period'
    )
    
    # ------------------------------
    # Calculated Totals (Auto-computed)
    # ------------------------------
    total_income = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Sum of all income line items for this period'
    )
    total_expenses = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Sum of all expense line items for this period'
    )
    net_cash_flow = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Net cash flow for this period (income - expenses - costs)'
    )
    
    # ------------------------------
    # Data Source Tracking
    # ------------------------------
    # Note: This model stores REALIZED cash flows from GL transactions only
    # Underwritten projections come from AssetMetrics and other existing models
    
    # ------------------------------
    # Metadata
    # ------------------------------
    # Note: Timestamps handled by database triggers, not Django auto fields
    
    class Meta:
        db_table = 'll_cash_flow_series'
        verbose_name = 'Loan-Level Cash Flow Series'
        verbose_name_plural = 'Loan-Level Cash Flow Series'
        unique_together = ['asset_hub', 'period_date']
        ordering = ['asset_hub', 'period_number']
        indexes = [
            models.Index(fields=['asset_hub', 'period_number']),
            models.Index(fields=['period_date']),
        ]
    
    def save(self, *args, **kwargs):
        """
        WHAT: Auto-calculate period_date and totals before saving
        WHY: Ensure consistency and avoid manual calculation errors
        HOW: Calculate period_date from purchase_date + months, sum all income/expense fields
        """
        # Auto-calculate period_date based on purchase_date from BlendedOutcomeModel
        from dateutil.relativedelta import relativedelta
        if hasattr(self.asset_hub, 'blended_outcome_model') and self.asset_hub.blended_outcome_model.purchase_date:
            purchase_date = self.asset_hub.blended_outcome_model.purchase_date
            if self.period_number is not None:
                self.period_date = purchase_date + relativedelta(months=self.period_number)
        
        # Calculate total income
        self.total_income = (
            self.income_principal + self.income_interest + self.income_rent +
            self.income_cam + self.income_mod_down_payment + self.proceeds +
            self.net_liquidation_proceeds
        )
        
        # Calculate total expenses (all negative cash flows)
        self.total_expenses = (
            self.purchase_price + self.acq_due_diligence_expenses + self.acq_legal_expenses +
            self.acq_title_expenses + self.acq_other_expenses + self.servicing_expenses +
            self.am_fees_expenses + self.property_tax_expenses +
            self.property_insurance_expenses + self.legal_foreclosure_expenses +
            self.legal_bankruptcy_expenses + self.legal_dil_expenses + self.legal_cash_for_keys_expenses +
            self.legal_eviction_expenses + self.reo_hoa_expenses + self.reo_utilities_expenses +
            self.reo_trashout_expenses + self.reo_renovation_expenses + self.reo_property_preservation_expenses +
            self.cre_marketing_expenses + self.cre_ga_pool_expenses + self.cre_maintenance_expenses +
            self.fund_taxes_expenses + self.fund_legal_expenses + self.fund_consulting_expenses +
            self.fund_audit_expenses + self.broker_closing_expenses + self.other_closing_expenses
        )
        
        # Calculate net cash flow
        self.net_cash_flow = self.total_income - self.total_expenses
        
        super().save(*args, **kwargs)
    
    @property
    def purchase_date(self):
        """
        WHAT: Get purchase date from related BlendedOutcomeModel
        WHY: Avoid duplicating purchase_date field across models
        HOW: Access via asset_hub.blended_outcome_model.purchase_date
        """
        if hasattr(self.asset_hub, 'blended_outcome_model'):
            return self.asset_hub.blended_outcome_model.purchase_date
        return None
    
    def __str__(self):
        return f"Cash Flow Period {self.period_number} for Asset {self.asset_hub_id} ({self.period_date})"