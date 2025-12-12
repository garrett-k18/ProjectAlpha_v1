"""Serializer for trade-level assumptions API."""

from rest_framework import serializers

from ..models.model_acq_assumptions import TradeLevelAssumption
from core.models import Servicer


class TradeLevelAssumptionSerializer(serializers.ModelSerializer):
    """Expose trade-level assumptions for read/write API operations."""

    # WHAT: Map servicer_id to servicer for API convenience
    # WHY: Allow clients to send servicer_id instead of nested servicer object
    servicer_id = serializers.PrimaryKeyRelatedField(
        source="servicer",
        queryset=Servicer.objects.all(),
        allow_null=True,
        required=False,
    )
    trade_id = serializers.IntegerField(source="trade.id", read_only=True)
    servicer_name = serializers.CharField(source="servicer.servicer_name", read_only=True)
    
    # WHAT: Map am_fee_pct to liq_am_fee_pct model field
    # WHY: Model uses liq_am_fee_pct but API clients expect am_fee_pct for simplicity
    # HOW: Use source parameter to map API field name to model field name
    am_fee_pct = serializers.DecimalField(
        source="liq_am_fee_pct",
        max_digits=6,
        decimal_places=4,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = TradeLevelAssumption
        fields = [
            "id",
            "trade_id",
            "servicer_id",
            "servicer_name",
            "bid_method",
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
            "acq_broker_fees",
            "acq_other_costs",
            "am_fee_pct",  # Mapped to liq_am_fee_pct via source parameter above
        ]
        read_only_fields = ["id", "trade_id", "servicer_name"]
