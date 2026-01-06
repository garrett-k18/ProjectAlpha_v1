"""
Performance Summary Serializer

WHAT: Serializer for the Performance Summary grid (P&L metrics component)
WHY: Maps data from BlendedOutcomeModel to the frontend PLMetrics.vue component
HOW: Follows same pattern as AssetInventoryRowSerializer - flat structure for easy frontend consumption
WHERE: Used by performance summary API endpoint for loan-level tabs

Docs reviewed:
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- SerializerMethodField: https://www.django-rest-framework.org/api-guide/fields/#serializermethodfield
"""

from rest_framework import serializers
from am_module.models.model_am_modeling import BlendedOutcomeModel


class PerformanceSummarySerializer(serializers.Serializer):
    """
    Flat row shape for Performance Summary grid (PLMetrics.vue component).
    
    Maps BlendedOutcomeModel fields to the 4-column grid:
    - Metric name (hardcoded in frontend)
    - Underwritten values (from BlendedOutcomeModel expected_* fields)
    - Realized values (from BlendedOutcomeModel actual_* fields or related models)
    - Sandbox (editable in frontend, not persisted)
    
    Field naming convention:
    - *_underwritten: Expected/modeled values from acquisition
    - *_realized: Actual values from asset management
    """
    
    # Asset identifier
    asset_hub_id = serializers.IntegerField(read_only=True, source='asset_hub.id')
    
    # ------------------------------
    # Gross Cost Section
    # ------------------------------
    # WHAT: Purchase Cost and Acquisition Costs
    # WHY: BlendedOutcomeModel stores acq_costs as single field
    # HOW: Map acq_costs to underwritten, null for realized (no actual fields yet)
    
    # Purchase Cost
    purchase_cost_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='purchase_price',
        help_text='Purchase price of the asset'
    )
    purchase_cost_realized = serializers.SerializerMethodField()
    
    # Acquisition Costs - Map from acq_costs field
    acq_due_diligence_underwritten = serializers.SerializerMethodField()
    acq_due_diligence_realized = serializers.SerializerMethodField()
    
    acq_legal_underwritten = serializers.SerializerMethodField()
    acq_legal_realized = serializers.SerializerMethodField()
    
    acq_title_underwritten = serializers.SerializerMethodField()
    acq_title_realized = serializers.SerializerMethodField()
    
    acq_other_underwritten = serializers.SerializerMethodField()
    acq_other_realized = serializers.SerializerMethodField()
    
    # Acquisition Costs Total (rollup of sub-items)
    acq_costs_total_underwritten = serializers.SerializerMethodField()
    acq_costs_total_realized = serializers.SerializerMethodField()
    
    # Gross Cost Total (Purchase Cost + Acquisition Costs)
    gross_cost_total_underwritten = serializers.SerializerMethodField()
    gross_cost_total_realized = serializers.SerializerMethodField()
    
    # ------------------------------
    # Income Section
    # ------------------------------
    income_principal_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='principal_collect',
        help_text='Principal collected'
    )
    income_principal_realized = serializers.SerializerMethodField()
    
    income_interest_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='interest_collect',
        help_text='Interest collected'
    )
    income_interest_realized = serializers.SerializerMethodField()
    
    income_rent_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='rental_income',
        help_text='Rental income'
    )
    income_rent_realized = serializers.SerializerMethodField()
    
    income_cam_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='cam_income',
        help_text='CAM income'
    )
    income_cam_realized = serializers.SerializerMethodField()
    
    income_mod_down_payment_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='mod_down_payment',
        help_text='Modification down payment'
    )
    income_mod_down_payment_realized = serializers.SerializerMethodField()
    
    # ------------------------------
    # Operating Expenses Section
    # ------------------------------
    # WHAT: Servicing fees from BlendedOutcomeModel servicing_* fields
    # HOW: Sum all servicing costs for underwritten column
    
    expense_servicing_underwritten = serializers.SerializerMethodField()
    expense_servicing_realized = serializers.SerializerMethodField()
    
    # ------------------------------
    # ROLLUP TOTALS (Computed in backend)
    # ------------------------------
    # WHAT: Parent row totals computed from child items
    # WHY: Single source of truth for calculations, consistent across frontend
    # HOW: SerializerMethodFields that sum child values
    
    income_total_underwritten = serializers.SerializerMethodField()
    income_total_realized = serializers.SerializerMethodField()
    
    legal_costs_total_underwritten = serializers.SerializerMethodField()
    legal_costs_total_realized = serializers.SerializerMethodField()
    
    operating_expenses_total_underwritten = serializers.SerializerMethodField()
    operating_expenses_total_realized = serializers.SerializerMethodField()
    
    reo_expenses_total_underwritten = serializers.SerializerMethodField()
    reo_expenses_total_realized = serializers.SerializerMethodField()
    
    cre_expenses_total_underwritten = serializers.SerializerMethodField()
    cre_expenses_total_realized = serializers.SerializerMethodField()
    
    fund_expenses_total_underwritten = serializers.SerializerMethodField()
    fund_expenses_total_realized = serializers.SerializerMethodField()
    
    # ------------------------------
    # Net P&L (BACKEND-COMPUTED)
    # ------------------------------
    # WHAT: Net P&L = Gross Liq Proceeds + Income - Operating Expenses - REO Expenses - Fund Expenses - Gross Cost
    # WHY: Single source of truth for bottom-line calculation
    net_pl_underwritten = serializers.SerializerMethodField()
    net_pl_realized = serializers.SerializerMethodField()
    
    # ------------------------------
    # Legal/DIL Cost Sub-items (nested under Operating Expenses)
    # ------------------------------
    # WHAT: Foreclosure Fees = fc_expenses + fc_legal_fees + other_fc_fees
    # WHY: Frontend shows single "Foreclosure Fees" line, backend stores 3 separate fields
    # HOW: Use SerializerMethodField to sum the 3 FC-related fields
    legal_foreclosure_underwritten = serializers.SerializerMethodField(
        help_text='Sum of fc_expenses, fc_legal_fees, other_fc_fees (underwritten)'
    )
    legal_foreclosure_realized = serializers.SerializerMethodField(
        help_text='Sum of fc_expenses, fc_legal_fees, other_fc_fees (realized)'
    )
    
    # Bankruptcy Fees
    legal_bankruptcy_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='bk_legal_fees',
        help_text='Bankruptcy legal fees (underwritten)'
    )
    legal_bankruptcy_realized = serializers.SerializerMethodField()
    
    # Deed-in-Lieu Cost
    legal_dil_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='dil_fees',
        help_text='Deed-in-Lieu fees (underwritten)'
    )
    legal_dil_realized = serializers.SerializerMethodField()
    
    # Cash for Keys Cost
    legal_cash_for_keys_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='cfk_fees',
        help_text='Cash for Keys fees (underwritten)'
    )
    legal_cash_for_keys_realized = serializers.SerializerMethodField()
    
    # Eviction Cost
    legal_eviction_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='eviction_fees',
        help_text='Eviction fees (underwritten)'
    )
    legal_eviction_realized = serializers.SerializerMethodField()
    
    expense_am_fees_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='fund_am_fees',
        help_text='Underwritten asset management fees'
    )
    expense_am_fees_realized = serializers.SerializerMethodField()
    
    expense_property_tax_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='total_property_tax',
        help_text='Underwritten property taxes'
    )
    expense_property_tax_realized = serializers.SerializerMethodField()
    
    expense_property_insurance_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='total_insurance',
        help_text='Underwritten property insurance'
    )
    expense_property_insurance_realized = serializers.SerializerMethodField()
    
    # ------------------------------
    # REO Expenses Section
    # ------------------------------
    reo_hoa_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='total_hoa',
        help_text='Underwritten HOA fees'
    )
    reo_hoa_realized = serializers.SerializerMethodField()
    
    reo_utilities_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='total_utility',
        help_text='Underwritten utilities'
    )
    reo_utilities_realized = serializers.SerializerMethodField()
    
    reo_trashout_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='trashout_cost',
        help_text='Trashout cost'
    )
    reo_trashout_realized = serializers.SerializerMethodField()
    
    reo_renovation_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='reconciled_rehab_cost',
        help_text='Underwritten renovation costs'
    )
    reo_renovation_realized = serializers.SerializerMethodField()
    
    reo_property_preservation_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='property_preservation_cost',
        help_text='Underwritten property preservation'
    )
    reo_property_preservation_realized = serializers.SerializerMethodField()
    
    # CRE Expenses (nested under REO)
    cre_marketing_underwritten = serializers.SerializerMethodField()
    cre_marketing_realized = serializers.SerializerMethodField()
    
    cre_ga_pool_underwritten = serializers.SerializerMethodField()
    cre_ga_pool_realized = serializers.SerializerMethodField()
    
    cre_maintenance_underwritten = serializers.SerializerMethodField()
    cre_maintenance_realized = serializers.SerializerMethodField()
    
    # ------------------------------
    # Fund Expenses Section
    # ------------------------------
    fund_taxes_underwritten = serializers.SerializerMethodField()
    fund_taxes_realized = serializers.SerializerMethodField()
    
    fund_legal_underwritten = serializers.SerializerMethodField()
    fund_legal_realized = serializers.SerializerMethodField()
    
    fund_consulting_underwritten = serializers.SerializerMethodField()
    fund_consulting_realized = serializers.SerializerMethodField()
    
    fund_audit_underwritten = serializers.SerializerMethodField()
    fund_audit_realized = serializers.SerializerMethodField()
    
    # ------------------------------
    # Gross Liquidation Proceeds Section
    # ------------------------------
    proceeds_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='expected_gross_proceeds',
        help_text='Underwritten gross liquidation proceeds'
    )
    proceeds_realized = serializers.SerializerMethodField()
    
    net_liquidation_proceeds_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='expected_net_proceeds',
        help_text='Net liquidation proceeds (gross - closing costs)'
    )
    net_liquidation_proceeds_realized = serializers.SerializerMethodField()
    
    # Closing Costs (nested under Gross Liquidation Proceeds)
    broker_closing_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='broker_closing_fees',
        help_text='Underwritten broker closing costs'
    )
    broker_closing_realized = serializers.SerializerMethodField()
    
    other_closing_underwritten = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True,
        source='tax_title_transfer_cost',
        help_text='Underwritten other closing costs'
    )
    other_closing_realized = serializers.SerializerMethodField()
    
    # Closing Costs Total (rollup of Broker + Other)
    closing_costs_total_underwritten = serializers.SerializerMethodField()
    closing_costs_total_realized = serializers.SerializerMethodField()
    
    # ------------------------------
    # Legal/DIL Cost Sub-items (nested under Operating Expenses)
    # ------------------------------
    def get_legal_foreclosure_underwritten(self, obj):
        """
        WHAT: Sum fc_expenses + fc_legal_fees + other_fc_fees for underwritten
        WHY: Frontend shows single Foreclosurefees line
        HOW: Add 3 fields, return 0 if all None
        """
        fc_exp = obj.fc_expenses or 0
        return fc_exp
    
    def get_legal_foreclosure_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.legal_foreclosure_realized
        return None
    
    def get_legal_bankruptcy_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.legal_bankruptcy_realized
        return None
    
    def get_legal_dil_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.legal_dil_realized
        return None
    
    def get_legal_cash_for_keys_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.legal_cash_for_keys_realized
        return None
    
    def get_legal_eviction_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.legal_eviction_realized
        return None
    
    # ------------------------------
    # Gross Cost / Acquisition Cost Methods
    # ------------------------------
    def get_purchase_cost_realized(self, obj):
        """Get realized purchase cost from transaction summary"""
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.purchase_price_realized
        return None
    
    def get_acq_due_diligence_underwritten(self, obj):
        """Get due diligence costs from BlendedOutcomeModel.due_diligence field"""
        return float(obj.due_diligence) if obj.due_diligence else None
    
    def get_acq_due_diligence_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.acq_due_diligence_realized
        return None
    
    def get_acq_legal_underwritten(self, obj):
        """Get legal costs from BlendedOutcomeModel.legal_costs field"""
        return float(obj.legal_costs) if obj.legal_costs else None
    
    def get_acq_legal_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.acq_legal_realized
        return None
    
    def get_acq_title_underwritten(self, obj):
        """Get title costs from BlendedOutcomeModel.taxtitle_fees field"""
        return float(obj.taxtitle_fees) if obj.taxtitle_fees else None
    
    def get_acq_title_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.acq_title_realized
        return None
    
    def get_acq_other_underwritten(self, obj):
        """Get other acquisition costs from BlendedOutcomeModel.other_fee + broker_acq_fees fields"""
        from decimal import Decimal
        other = obj.other_fee or Decimal('0')
        broker = obj.broker_acq_fees or Decimal('0')
        total = other + broker
        return float(total) if total > 0 else None
    
    def get_acq_other_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.acq_other_realized
        return None
    
    def get_acq_costs_total_underwritten(self, obj):
        """Acquisition Costs Total = Due Diligence + Legal + Title + Other + Broker Acq Fees"""
        from decimal import Decimal
        due_diligence = obj.due_diligence or Decimal('0')
        legal = obj.legal_costs or Decimal('0')
        title = obj.taxtitle_fees or Decimal('0')
        other = obj.other_fee or Decimal('0')
        broker = obj.broker_acq_fees or Decimal('0')
        total = due_diligence + legal + title + other + broker
        try:
            return float(total)
        except Exception:
            return 0.0
    
    def get_acq_costs_total_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            from decimal import Decimal
            ts = obj.asset_hub.ll_transaction_summary
            total = Decimal('0')
            total += ts.acq_due_diligence_realized or Decimal('0')
            total += ts.acq_legal_realized or Decimal('0')
            total += ts.acq_title_realized or Decimal('0')
            total += ts.acq_other_realized or Decimal('0')
            return float(total) if total > 0 else None
        return None
    
    def get_gross_cost_total_underwritten(self, obj):
        """Gross Cost = Purchase Price + Acquisition Costs Total"""
        from decimal import Decimal
        purchase_price = obj.purchase_price or Decimal('0')
        acq_costs = Decimal(str(self.get_acq_costs_total_underwritten(obj) or 0))
        total = purchase_price + acq_costs
        try:
            return float(total)
        except Exception:
            return 0.0
    
    def get_gross_cost_total_realized(self, obj):
        """Use pre-computed realized_gross_cost from LLTransactionSummary"""
        try:
            ts = getattr(obj.asset_hub, 'll_transaction_summary', None)
            if ts is None:
                return None
            # Use pre-computed total from model save() if available
            if ts.realized_gross_cost is not None:
                return float(ts.realized_gross_cost)
            # Fallback: calculate from parts
            from decimal import Decimal
            purchase = ts.purchase_price_realized or Decimal('0')
            acq_total = ts.acq_total_realized or Decimal('0')
            total = purchase + acq_total
            return float(total) if total > 0 else None
        except Exception:
            return None
    
    # ------------------------------
    # Income Methods
    # ------------------------------
    def get_income_principal_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.income_principal_realized
        return None
    
    def get_income_interest_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.income_interest_realized
        return None
    
    def get_income_rent_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.income_rent_realized
        return None
    
    def get_income_cam_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.income_cam_realized
        return None
    
    def get_income_mod_down_payment_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.income_mod_down_payment_realized
        return None
    
    # ------------------------------
    # Servicing Expense Methods
    # ------------------------------
    def get_expense_servicing_underwritten(self, obj):
        """Sum all servicing costs"""
        total = (obj.servicing_board_fee or 0) + (obj.servicing_current or 0) + \
                (obj.servicing_30d or 0) + (obj.servicing_60d or 0) + \
                (obj.servicing_90d or 0) + (obj.servicing_120d or 0) + \
                (obj.servicing_fc or 0) + (obj.servicing_bk or 0) + \
                (obj.servicing_liq_fee or 0)
        return total if total > 0 else None
    
    def get_expense_servicing_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.expense_servicing_realized
        return None
    
    # Stub methods for fields not yet in BlendedOutcomeModel
    def get_expense_am_fees_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.expense_am_fees_realized
        return None
    
    def get_expense_property_tax_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.expense_property_tax_realized
        return None
    
    def get_expense_property_insurance_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.expense_property_insurance_realized
        return None
    
    def get_reo_hoa_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.reo_hoa_realized
        return None
    
    def get_reo_utilities_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.reo_utilities_realized
        return None
    
    def get_reo_trashout_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.reo_trashout_realized
        return None
    
    def get_reo_renovation_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.reo_renovation_realized
        return None
    
    def get_reo_property_preservation_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.reo_property_preservation_realized
        return None
    
    def get_cre_marketing_underwritten(self, obj):
        return None
    
    def get_cre_marketing_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.cre_marketing_realized
        return None
    
    def get_cre_ga_pool_underwritten(self, obj):
        return None
    
    def get_cre_ga_pool_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.cre_ga_pool_realized
        return None
    
    def get_cre_maintenance_underwritten(self, obj):
        return None
    
    def get_cre_maintenance_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.cre_maintenance_realized
        return None
    
    def get_fund_taxes_underwritten(self, obj):
        return None
    
    def get_fund_taxes_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.fund_taxes_realized
        return None
    
    def get_fund_legal_underwritten(self, obj):
        return None
    
    def get_fund_legal_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.fund_legal_realized
        return None
    
    def get_fund_consulting_underwritten(self, obj):
        return None
    
    def get_fund_consulting_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.fund_consulting_realized
        return None
    
    def get_fund_audit_underwritten(self, obj):
        return None
    
    def get_fund_audit_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.fund_audit_realized
        return None
    
    def get_proceeds_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.gross_liquidation_proceeds_realized
        return None
    
    def get_net_liquidation_proceeds_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.net_liquidation_proceeds_realized
        return None
    
    def get_broker_closing_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.broker_closing_realized
        return None
    
    def get_other_closing_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            return obj.asset_hub.ll_transaction_summary.other_closing_realized
        return None
    
    def get_closing_costs_total_underwritten(self, obj):
        """Closing Costs Total = Broker Closing + Other Closing"""
        from decimal import Decimal
        broker = obj.broker_closing_fees or Decimal('0')
        other = obj.tax_title_transfer_cost or Decimal('0')
        total = broker + other
        try:
            return float(total)
        except Exception:
            return 0.0
    
    def get_closing_costs_total_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            from decimal import Decimal
            ts = obj.asset_hub.ll_transaction_summary
            broker = ts.broker_closing_realized or Decimal('0')
            other = ts.other_closing_realized or Decimal('0')
            total = broker + other
            return float(total) if total > 0 else None
        return None
    
    # ------------------------------
    # ROLLUP TOTAL METHODS
    # ------------------------------
    # WHAT: Calculate parent row totals from child items
    # WHY: Single source of truth - backend owns calculation logic
    # HOW: Sum relevant child fields for each parent category
    
    def get_income_total_underwritten(self, obj):
        """Income = Principal + Interest + Rent + CAM + Mod Down Payment"""
        from decimal import Decimal
        principal = obj.principal_collect or Decimal('0')
        interest = obj.interest_collect or Decimal('0')
        rent = obj.rental_income or Decimal('0')
        cam = obj.cam_income or Decimal('0')
        mod_down = obj.mod_down_payment or Decimal('0')
        total = principal + interest + rent + cam + mod_down
        try:
            return float(total)
        except Exception:
            return 0.0
    
    def get_income_total_realized(self, obj):
        """Sum all realized income fields from LLTransactionSummary"""
        try:
            ts = getattr(obj.asset_hub, 'll_transaction_summary', None)
            if ts is None:
                return None
            from decimal import Decimal
            total = Decimal('0')
            total += ts.income_principal_realized or Decimal('0')
            total += ts.income_interest_realized or Decimal('0')
            total += ts.income_rent_realized or Decimal('0')
            total += ts.income_cam_realized or Decimal('0')
            total += ts.income_mod_down_payment_realized or Decimal('0')
            return float(total) if total > 0 else None
        except Exception:
            return None
    
    def get_legal_costs_total_underwritten(self, obj):
        """Legal/DIL Costs = FC + BK + DIL + CFK + Eviction"""
        fc = obj.fc_expenses or 0
        bk = obj.bk_legal_fees or 0
        dil = obj.dil_fees or 0
        cfk = obj.cfk_fees or 0
        eviction = obj.eviction_fees or 0
        total = fc + bk + dil + cfk + eviction
        try:
            return float(total)
        except Exception:
            return 0.0
    
    def get_legal_costs_total_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            from decimal import Decimal
            ts = obj.asset_hub.ll_transaction_summary
            total = Decimal('0')
            total += ts.legal_foreclosure_realized or Decimal('0')
            total += ts.legal_bankruptcy_realized or Decimal('0')
            total += ts.legal_dil_realized or Decimal('0')
            total += ts.legal_cash_for_keys_realized or Decimal('0')
            total += ts.legal_eviction_realized or Decimal('0')
            return float(total) if total > 0 else None
        return None
    
    def get_cre_expenses_total_underwritten(self, obj):
        """CRE Expenses = Marketing + G&A Pool + Maintenance (all None for now)"""
        return 0
    
    def get_cre_expenses_total_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            from decimal import Decimal
            ts = obj.asset_hub.ll_transaction_summary
            total = Decimal('0')
            total += ts.cre_marketing_realized or Decimal('0')
            total += ts.cre_ga_pool_realized or Decimal('0')
            total += ts.cre_maintenance_realized or Decimal('0')
            return float(total) if total > 0 else None
        return None
    
    def get_reo_expenses_total_underwritten(self, obj):
        """REO Expenses = HOA + Utilities + Trashout + Renovation + Preservation + CRE Total"""
        from decimal import Decimal
        hoa = obj.total_hoa or Decimal('0')
        utilities = obj.total_utility or Decimal('0')
        trashout = obj.trashout_cost or Decimal('0')
        renovation = obj.reconciled_rehab_cost or Decimal('0')
        preservation = obj.property_preservation_cost or Decimal('0')
        cre_total = self.get_cre_expenses_total_underwritten(obj)
        total = hoa + utilities + trashout + renovation + preservation + Decimal(str(cre_total or 0))
        try:
            return float(total)
        except Exception:
            return 0.0
    
    def get_reo_expenses_total_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            from decimal import Decimal
            ts = obj.asset_hub.ll_transaction_summary
            total = Decimal('0')
            total += ts.reo_hoa_realized or Decimal('0')
            total += ts.reo_utilities_realized or Decimal('0')
            total += ts.reo_trashout_realized or Decimal('0')
            total += ts.reo_renovation_realized or Decimal('0')
            total += ts.reo_property_preservation_realized or Decimal('0')
            cre_total = self.get_cre_expenses_total_realized(obj) or 0
            total += Decimal(str(cre_total))
            return float(total) if total > 0 else None
        return None
    
    def get_fund_expenses_total_underwritten(self, obj):
        """Fund Expenses = Taxes + Legal + Consulting + Audit (all None for now)"""
        return 0
    
    def get_fund_expenses_total_realized(self, obj):
        if hasattr(obj.asset_hub, 'll_transaction_summary'):
            from decimal import Decimal
            ts = obj.asset_hub.ll_transaction_summary
            total = Decimal('0')
            total += ts.fund_taxes_realized or Decimal('0')
            total += ts.fund_legal_realized or Decimal('0')
            total += ts.fund_consulting_realized or Decimal('0')
            total += ts.fund_audit_realized or Decimal('0')
            return float(total) if total > 0 else None
        return None
    
    def get_operating_expenses_total_underwritten(self, obj):
        """Operating Expenses = Servicing + Legal + AM Fees + Property Tax + Insurance + REO + Fund"""
        from decimal import Decimal
        servicing = Decimal(str(self.get_expense_servicing_underwritten(obj) or 0))
        legal = Decimal(str(self.get_legal_costs_total_underwritten(obj) or 0))
        am_fees = obj.fund_am_fees or Decimal('0')
        property_tax = obj.total_property_tax or Decimal('0')
        insurance = obj.total_insurance or Decimal('0')
        reo = Decimal(str(self.get_reo_expenses_total_underwritten(obj) or 0))
        fund = Decimal(str(self.get_fund_expenses_total_underwritten(obj) or 0))
        total = servicing + legal + am_fees + property_tax + insurance + reo + fund
        try:
            return float(total)
        except Exception:
            return 0.0
    
    def get_operating_expenses_total_realized(self, obj):
        """Use pre-computed total_expenses_realized from LLTransactionSummary"""
        try:
            ts = getattr(obj.asset_hub, 'll_transaction_summary', None)
            if ts is None:
                return None
            # Use pre-computed total from model save() if available
            if ts.total_expenses_realized is not None:
                return float(ts.total_expenses_realized)
            # Fallback: calculate from parts
            from decimal import Decimal
            total = Decimal('0')
            total += ts.expense_servicing_realized or Decimal('0')
            total += ts.legal_total_realized or Decimal('0')
            total += ts.expense_am_fees_realized or Decimal('0')
            total += ts.expense_property_tax_realized or Decimal('0')
            total += ts.expense_property_insurance_realized or Decimal('0')
            total += ts.reo_total_realized or Decimal('0')
            total += ts.fund_total_realized or Decimal('0')
            return float(total) if total > 0 else None
        except Exception:
            return None
    
    def get_net_pl_underwritten(self, obj):
        """Net P&L = (Proceeds + Income) - (Operating Expenses + Gross Cost)"""
        from decimal import Decimal
        proceeds = obj.expected_gross_proceeds or Decimal('0')
        income = Decimal(str(self.get_income_total_underwritten(obj) or 0))
        operating_expenses = Decimal(str(self.get_operating_expenses_total_underwritten(obj) or 0))
        gross_cost = Decimal(str(self.get_gross_cost_total_underwritten(obj) or 0))
        net_pl = (proceeds + income) - (operating_expenses + gross_cost)
        try:
            return float(net_pl)
        except Exception:
            return 0.0
    
    def get_net_pl_realized(self, obj):
        """Net P&L Realized = (Proceeds + Income) - (Expenses + Gross Cost)"""
        try:
            ts = getattr(obj.asset_hub, 'll_transaction_summary', None)
            if ts is None:
                return None
            from decimal import Decimal
            proceeds = Decimal(str(self.get_proceeds_realized(obj) or 0))
            income = Decimal(str(self.get_income_total_realized(obj) or 0))
            operating_expenses = Decimal(str(self.get_operating_expenses_total_realized(obj) or 0))
            gross_cost = Decimal(str(self.get_gross_cost_total_realized(obj) or 0))
            
            net_pl = (proceeds + income) - (operating_expenses + gross_cost)
            # Return value even if negative (to show realized loss)
            return float(net_pl) if net_pl != 0 else None
        except Exception:
            return None
