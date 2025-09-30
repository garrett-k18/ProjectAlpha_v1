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