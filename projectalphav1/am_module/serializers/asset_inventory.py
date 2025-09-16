from rest_framework import serializers
from am_module.models.seller_boarded_data import SellerBoardedData
from am_module.models.asset_metrics import AssetMetrics

class AssetInventoryRowSerializer(serializers.Serializer):
    """
    Flat row shape tailored for AG Grid. We keep this serializer
    detached from a specific model to freely compose from multiple sources.
    """
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
    acq_cost = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

    total_hold = serializers.IntegerField(required=False, allow_null=True)
    exit_date = serializers.DateField(required=False, allow_null=True)

    expected_gross_proceeds = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    expected_net_proceeds = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

    expected_pl = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    expected_cf = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    expected_irr = serializers.DecimalField(max_digits=5, decimal_places=4, required=False, allow_null=True)
    expected_moic = serializers.DecimalField(max_digits=6, decimal_places=5, required=False, allow_null=True)
    expected_npv = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

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

class AssetInventoryColumnsSerializer(serializers.Serializer):
    """Optional endpoint to drive dynamic columns from the server."""
    field = serializers.CharField()
    headerName = serializers.CharField()
    type = serializers.CharField(required=False)
    width = serializers.IntegerField(required=False)
