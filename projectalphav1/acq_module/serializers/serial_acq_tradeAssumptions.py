"""Serializer for trade-level assumptions API."""

from rest_framework import serializers

from ..models.model_acq_assumptions import TradeLevelAssumption
from core.models import Servicer


class TradeLevelAssumptionSerializer(serializers.ModelSerializer):
    """Expose trade-level assumptions for read/write API operations."""

    servicer_id = serializers.PrimaryKeyRelatedField(
        source="servicer",
        queryset=Servicer.objects.all(),
        allow_null=True,
        required=False,
    )
    trade_id = serializers.IntegerField(source="trade.id", read_only=True)
    servicer_name = serializers.CharField(source="servicer.servicer_name", read_only=True)

    class Meta:
        model = TradeLevelAssumption
        fields = [
            "id",
            "trade_id",
            "servicer_id",
            "servicer_name",
            "bid_date",
            "settlement_date",
            "servicing_transfer_date",
            "pctUPB",
            "target_irr",
            "discount_rate",
            "perf_rpl_hold_period",
            "mod_rate",
            "mod_legal_term",
            "mod_amort_term",
            "max_mod_ltv",
            "mod_io_flag",
            "mod_down_pmt",
            "mod_orig_cost",
            "mod_setup_duration",
            "mod_hold_duration",
            "acq_legal_cost",
            "acq_dd_cost",
            "acq_tax_title_cost",
            "am_fee_pct",
        ]
        read_only_fields = ["id", "trade_id", "servicer_name"]
