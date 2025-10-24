"""
WHAT: Serializer for LLCashFlowSeries - period-by-period cash flow data
WHY: Transform cash flow series model data into JSON for frontend time-series grid
HOW: Serialize all cash flow fields per period, include purchase date for period calculation
WHERE: Used by cash flow API endpoint (am_module/views/)
"""
from rest_framework import serializers
from core.models import LLCashFlowSeries


class CashFlowPeriodSerializer(serializers.ModelSerializer):
    """
    WHAT: Serializer for individual cash flow period
    WHY: Serialize all income/expense fields for a single period
    HOW: ModelSerializer with all fields exposed
    """
    
    class Meta:
        model = LLCashFlowSeries
        fields = [
            # Period identification
            'period_number',
            'period_date',
            
            # Purchase cost (P0 only)
            'purchase_price',
            
            # Acquisition costs (P0 only)
            'acq_due_diligence_expenses',
            'acq_legal_expenses',
            'acq_title_expenses',
            'acq_other_expenses',
            
            # Income
            'income_principal',
            'income_interest',
            'income_rent',
            'income_cam',
            'income_mod_down_payment',
            
            # Operating expenses
            'servicing_expenses',
            'am_fees_expenses',
            'property_tax_expenses',
            'property_insurance_expenses',
            
            # Legal/DIL costs
            'legal_foreclosure_expenses',
            'legal_bankruptcy_expenses',
            'legal_dil_expenses',
            'legal_cash_for_keys_expenses',
            'legal_eviction_expenses',
            
            # REO expenses
            'reo_hoa_expenses',
            'reo_utilities_expenses',
            'reo_trashout_expenses',
            'reo_renovation_expenses',
            'reo_property_preservation_expenses',
            
            # CRE expenses
            'cre_marketing_expenses',
            'cre_ga_pool_expenses',
            'cre_maintenance_expenses',
            
            # Fund expenses
            'fund_taxes_expenses',
            'fund_legal_expenses',
            'fund_consulting_expenses',
            'fund_audit_expenses',
            
            # Liquidation
            'proceeds',
            'broker_closing_expenses',
            'other_closing_expenses',
            'net_liquidation_proceeds',
            
            # Calculated totals
            'total_income',
            'total_expenses',
            'net_cash_flow',
        ]


class CashFlowSeriesSerializer(serializers.Serializer):
    """
    WHAT: Serializer for complete cash flow series response
    WHY: Package all periods with metadata (purchase date, etc.)
    HOW: Custom serializer that returns purchase_date and list of periods
    """
    
    purchase_date = serializers.DateField(
        help_text='Purchase date from BlendedOutcomeModel - drives period calculations'
    )
    periods = CashFlowPeriodSerializer(
        many=True,
        help_text='List of cash flow periods ordered by period_number'
    )
    
    def to_representation(self, instance):
        """
        WHAT: Custom representation to structure response
        WHY: Return purchase_date + periods array
        HOW: Extract purchase_date from asset_hub, serialize all periods
        
        Args:
            instance: Dict with 'asset_hub' and 'periods' keys
            
        Returns:
            dict: {'purchase_date': '2024-01-15', 'periods': [...]}
        """
        asset_hub = instance.get('asset_hub')
        periods_queryset = instance.get('periods', [])
        
        # WHAT: Convert QuerySet to list for serialization
        # WHY: QuerySet needs to be evaluated before serializing
        periods_list = list(periods_queryset) if hasattr(periods_queryset, '__iter__') else []
        
        # WHAT: Get purchase date from BlendedOutcomeModel
        purchase_date = None
        if asset_hub and hasattr(asset_hub, 'blended_outcome_model'):
            purchase_date = asset_hub.blended_outcome_model.purchase_date
        
        return {
            'purchase_date': purchase_date,
            'periods': CashFlowPeriodSerializer(periods_list, many=True).data
        }
