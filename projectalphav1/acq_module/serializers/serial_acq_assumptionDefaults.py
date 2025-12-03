from rest_framework import serializers

from acq_module.models.model_acq_assumptions import ModelingDefaults


class AssumptionDefaultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelingDefaults
        fields = [
            "id",
            "default_pct_upb",
            "default_discount_rate",
            "default_perf_rpl_hold_period",
            "default_mod_rate",
            "default_mod_legal_term",
            "default_mod_amort_term",
            "default_max_mod_ltv",
            "default_mod_io_flag",
            "default_mod_down_pmt",
            "default_mod_orig_cost",
            "default_mod_setup_duration",
            "default_mod_hold_duration",
            "default_acq_legal_cost",
            "default_acq_dd_cost",
            "default_acq_tax_title_cost",
            "default_am_fee_pct",
        ]
        read_only_fields = ["id"]
