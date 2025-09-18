from rest_framework import serializers
from am_module.models.boarded_data import SellerBoardedData
from am_module.models.asset_metrics import AssetMetrics

class AssetInventoryRowSerializer(serializers.Serializer):
    """
    Flat row shape tailored for AG Grid. We keep this serializer
    detached from a specific model to freely compose from multiple sources.
    """
    id = serializers.IntegerField(read_only=True)
    asset_id = serializers.SerializerMethodField()
    asset_status = serializers.CharField(allow_null=True)
    street_address = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    property_type = serializers.CharField(allow_null=True)
    occupancy = serializers.CharField(allow_null=True)

    trade_name = serializers.CharField()

    seller_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    seller_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

    # Map via SellerBoardedData.asset_hub -> BlendedOutcomeModel now that it's hub-keyed
    acq_cost = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True, source='asset_hub.blended_outcome_model.acq_cost')
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_total_expenses')

    total_hold = serializers.IntegerField(required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_total_hold')
    exit_date = serializers.DateField(required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_exit_date')

    expected_gross_proceeds = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_gross_proceeds')
    expected_net_proceeds = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_net_proceeds')

    expected_pl = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_pl')
    expected_cf = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_cf')
    expected_irr = serializers.DecimalField(max_digits=5, decimal_places=4, required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_irr')
    expected_moic = serializers.DecimalField(max_digits=6, decimal_places=5, required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_moic')
    expected_npv = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_npv')

    def get_asset_id(self, obj):
        stid = getattr(obj, "sellertape_id", None)
        return stid if stid is not None else getattr(obj, "pk", None)

    def get_address(self, obj):
        parts = [
            str(getattr(obj, "street_address", "")).strip(),
            str(getattr(obj, "city", "")).strip(),
            str(getattr(obj, "state", "")).strip(),
            str(getattr(obj, "zip", "")).strip(),
        ]
        parts = [p for p in parts if p]
        return ", ".join(parts)

    def get_market_value(self, obj):
        # Map to seller_asis_value if available; otherwise None
        return getattr(obj, "seller_asis_value", None)

    def get_hold_days(self, obj):
        try:
            m: AssetMetrics | None = getattr(obj, "metrics", None)
            return m.time_held_days if m else None
        except Exception:
            return None


class AssetDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single SellerBoardedData asset record.
    Exposes fields used by the loan-level modal tabs (Snapshot, Property, Loan, etc.).

    Docs:
    - DRF ModelSerializer: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    class Meta:
        model = SellerBoardedData
        # Explicitly list fields for stability and to avoid over-exposing internals
        fields = [
            # Identity
            'id', 'sellertape_id', 'seller_name', 'trade_name', 'asset_status', 'as_of_date',
            # Address / property
            'street_address', 'city', 'state', 'zip', 'property_type', 'occupancy', 'year_built',
            'sq_ft', 'lot_size', 'beds', 'baths',
            # Loan core
            'current_balance', 'deferred_balance', 'interest_rate', 'next_due_date', 'last_paid_date',
            'first_pay_date', 'origination_date', 'original_balance', 'original_term', 'original_rate',
            'original_maturity_date', 'default_rate', 'months_dlq', 'current_maturity_date', 'current_term',
            # Balances / fees
            'accrued_note_interest', 'accrued_default_interest', 'escrow_balance', 'escrow_advance',
            'recoverable_corp_advance', 'late_fees', 'other_fees', 'suspense_balance', 'total_debt',
            # Valuation inputs
            'origination_value', 'origination_arv', 'origination_value_date', 'seller_value_date',
            'seller_arv_value', 'seller_asis_value', 'additional_asis_value', 'additional_arv_value',
            'additional_value_date',
            # Flags
            'fc_flag', 'fc_first_legal_date', 'fc_referred_date', 'fc_judgement_date',
            'fc_scheduled_sale_date', 'fc_sale_date', 'fc_starting',
            'bk_flag', 'bk_chapter',
            'mod_flag', 'mod_date', 'mod_maturity_date', 'mod_term', 'mod_rate', 'mod_initial_balance',
            # Provenance
            'boarded_at', 'boarded_by', 'created_at', 'updated_at',
        ]

class AssetInventoryColumnsSerializer(serializers.Serializer):
    """Optional endpoint to drive dynamic columns from the server."""
    field = serializers.CharField()
    headerName = serializers.CharField()
    type = serializers.CharField(required=False)
    width = serializers.IntegerField(required=False)
