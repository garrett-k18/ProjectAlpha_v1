from rest_framework import serializers
from am_module.models.boarded_data import SellerBoardedData
from am_module.models.asset_metrics import AssetMetrics
from am_module.models.am_data import AMMetrics
from am_module.models.servicers import ServicerLoanData
from core.models.valuations import Valuation
from .servicer_loan_data import ServicerLoanDataSerializer

class AssetInventoryRowSerializer(serializers.Serializer):
    """
    Flat row shape tailored for AG Grid. We keep this serializer
    detached from a specific model to freely compose from multiple sources.
    """
    id = serializers.IntegerField(read_only=True)
    # Expose the hub id explicitly so the frontend can validate nested records
    asset_hub_id = serializers.IntegerField(read_only=True)
    asset_id = serializers.SerializerMethodField()
    asset_status = serializers.CharField(allow_null=True)
    delinquency_status = serializers.SerializerMethodField()
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

    # --- Latest Servicer Loan Data ---
    servicer_loan_data = serializers.SerializerMethodField()

    # --- Unified Valuation (latest per source) ---
    # Internal (source='internal')
    internal_asis_value = serializers.SerializerMethodField()
    internal_arv_value = serializers.SerializerMethodField()
    internal_value_date = serializers.SerializerMethodField()
    internal_rehab_est_total = serializers.SerializerMethodField()
    internal_roof_est = serializers.SerializerMethodField()
    internal_kitchen_est = serializers.SerializerMethodField()
    internal_bath_est = serializers.SerializerMethodField()
    internal_flooring_est = serializers.SerializerMethodField()
    internal_windows_est = serializers.SerializerMethodField()
    internal_appliances_est = serializers.SerializerMethodField()
    internal_plumbing_est = serializers.SerializerMethodField()
    internal_electrical_est = serializers.SerializerMethodField()
    internal_landscaping_est = serializers.SerializerMethodField()

    # Broker (source='broker')
    broker_asis_value = serializers.SerializerMethodField()
    broker_arv_value = serializers.SerializerMethodField()
    broker_value_date = serializers.SerializerMethodField()
    broker_rehab_est_total = serializers.SerializerMethodField()
    broker_roof_est = serializers.SerializerMethodField()
    broker_kitchen_est = serializers.SerializerMethodField()
    broker_bath_est = serializers.SerializerMethodField()
    broker_flooring_est = serializers.SerializerMethodField()
    broker_windows_est = serializers.SerializerMethodField()
    broker_appliances_est = serializers.SerializerMethodField()
    broker_plumbing_est = serializers.SerializerMethodField()
    broker_electrical_est = serializers.SerializerMethodField()
    broker_landscaping_est = serializers.SerializerMethodField()
    broker_notes = serializers.SerializerMethodField()
    broker_links = serializers.SerializerMethodField()

    # Internal Initial UW (source='internalInitialUW')
    internal_initial_uw_asis_value = serializers.SerializerMethodField()
    internal_initial_uw_arv_value = serializers.SerializerMethodField()
    internal_initial_uw_value_date = serializers.SerializerMethodField()
    internal_initial_uw_rehab_est_total = serializers.SerializerMethodField()
    internal_initial_uw_roof_est = serializers.SerializerMethodField()
    internal_initial_uw_kitchen_est = serializers.SerializerMethodField()
    internal_initial_uw_bath_est = serializers.SerializerMethodField()
    internal_initial_uw_flooring_est = serializers.SerializerMethodField()
    internal_initial_uw_windows_est = serializers.SerializerMethodField()
    internal_initial_uw_appliances_est = serializers.SerializerMethodField()
    internal_initial_uw_plumbing_est = serializers.SerializerMethodField()
    internal_initial_uw_electrical_est = serializers.SerializerMethodField()
    internal_initial_uw_landscaping_est = serializers.SerializerMethodField()

    # Seller (source='seller')
    seller_asis_value = serializers.SerializerMethodField()
    seller_arv_value = serializers.SerializerMethodField()
    seller_value_date = serializers.SerializerMethodField()
    seller_rehab_est_total = serializers.SerializerMethodField()
    seller_roof_est = serializers.SerializerMethodField()
    seller_kitchen_est = serializers.SerializerMethodField()
    seller_bath_est = serializers.SerializerMethodField()
    seller_flooring_est = serializers.SerializerMethodField()
    seller_windows_est = serializers.SerializerMethodField()
    seller_appliances_est = serializers.SerializerMethodField()
    seller_plumbing_est = serializers.SerializerMethodField()
    seller_electrical_est = serializers.SerializerMethodField()
    seller_landscaping_est = serializers.SerializerMethodField()

    expected_pl = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_pl')
    expected_cf = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_cf')
    expected_irr = serializers.DecimalField(max_digits=5, decimal_places=4, required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_irr')
    expected_moic = serializers.DecimalField(max_digits=6, decimal_places=5, required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_moic')
    expected_npv = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True, source='asset_hub.blended_outcome_model.expected_npv')

    def get_asset_id(self, obj):
        stid = getattr(obj, "sellertape_id", None)
        return stid if stid is not None else getattr(obj, "pk", None)

    def get_delinquency_status(self, obj):
        """Return the cached delinquency bucket from `AMMetrics` for this asset.

        We intentionally expose the denormalized field to avoid recomputing the
        bucket on every serializer call. Upstream nightly jobs (or manual refreshes)
        should call `AMMetrics.refresh_delinquency_status()` whenever new servicer
        data arrives so that this field stays in sync.
        """

        # Resolve hub from the row; this serializer is usually fed a
        # `SellerBoardedData` instance so we can jump through `asset_hub`.
        hub = getattr(obj, 'asset_hub', None)
        if not hub:
            return None

        metrics_manager = getattr(hub, 'ammetrics', None)
        if metrics_manager is None:
            return None

        # Related manager can return multiple rows; grab the most recently
        # updated metric to keep the UI consistent with backend refresh jobs.
        metrics: AMMetrics | None
        if isinstance(metrics_manager, AMMetrics):
            metrics = metrics_manager
        else:
            metrics = metrics_manager.order_by('-updated_at').first()

        return getattr(metrics, 'delinquency_status', None)

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


    # ----------------- Helpers -----------------
    def _latest_val_by_source(self, obj, source: str):
        """Return latest Valuation row for the object's asset_hub and given source.

        We order by value_date then created_at to get the most recent record.
        """
        hub = getattr(obj, 'asset_hub', None)
        if hub is None:
            return None
        return (
            Valuation.objects
            .filter(asset_hub=hub, source=source)
            .order_by('-value_date', '-created_at')
            .first()
        )

    # ----------------- Servicer getters -----------------
    def get_servicer_loan_data(self, obj):
        """Fetch and serialize the most recent ServicerLoanData record by asset_hub."""
        # Resolve asset_hub consistently (obj may be an AssetIdHub or any model with asset_hub FK)
        hub = getattr(obj, 'asset_hub', None) or obj
        latest_servicer_record = (
            ServicerLoanData.objects
            .filter(asset_hub=hub)
            .order_by('-reporting_year', '-reporting_month', '-as_of_date')
            .first()
        )
        if latest_servicer_record:
            return ServicerLoanDataSerializer(latest_servicer_record).data
        return None

    # ----------------- Internal getters -----------------
    def get_internal_asis_value(self, obj):
        v = self._latest_val_by_source(obj, 'internal')
        return getattr(v, 'asis_value', None) if v else None

    def get_internal_arv_value(self, obj):
        v = self._latest_val_by_source(obj, 'internal')
        return getattr(v, 'arv_value', None) if v else None

    def get_internal_value_date(self, obj):
        v = self._latest_val_by_source(obj, 'internal')
        return getattr(v, 'value_date', None) if v else None

    def get_internal_rehab_est_total(self, obj):
        v = self._latest_val_by_source(obj, 'internal')
        return getattr(v, 'rehab_est_total', None) if v else None

    def get_internal_roof_est(self, obj):
        v = self._latest_val_by_source(obj, 'internal')
        return getattr(v, 'roof_est', None) if v else None

    def get_internal_kitchen_est(self, obj):
        v = self._latest_val_by_source(obj, 'internal')
        return getattr(v, 'kitchen_est', None) if v else None

    def get_internal_bath_est(self, obj):
        v = self._latest_val_by_source(obj, 'internal')
        return getattr(v, 'bath_est', None) if v else None

    def get_internal_flooring_est(self, obj):
        v = self._latest_val_by_source(obj, 'internal')
        return getattr(v, 'flooring_est', None) if v else None

    def get_internal_windows_est(self, obj):
        v = self._latest_val_by_source(obj, 'internal')
        return getattr(v, 'windows_est', None) if v else None

    def get_internal_appliances_est(self, obj):
        v = self._latest_val_by_source(obj, 'internal')
        return getattr(v, 'appliances_est', None) if v else None

    def get_internal_plumbing_est(self, obj):
        v = self._latest_val_by_source(obj, 'internal')
        return getattr(v, 'plumbing_est', None) if v else None

    def get_internal_electrical_est(self, obj):
        v = self._latest_val_by_source(obj, 'internal')
        return getattr(v, 'electrical_est', None) if v else None

    def get_internal_landscaping_est(self, obj):
        v = self._latest_val_by_source(obj, 'internal')
        return getattr(v, 'landscaping_est', None) if v else None

    # ----------------- Broker getters -----------------
    def get_broker_asis_value(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'asis_value', None) if v else None

    def get_broker_arv_value(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'arv_value', None) if v else None

    def get_broker_value_date(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'value_date', None) if v else None

    def get_broker_rehab_est_total(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'rehab_est_total', None) if v else None

    def get_broker_roof_est(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'roof_est', None) if v else None

    def get_broker_kitchen_est(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'kitchen_est', None) if v else None

    def get_broker_bath_est(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'bath_est', None) if v else None

    def get_broker_flooring_est(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'flooring_est', None) if v else None

    def get_broker_windows_est(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'windows_est', None) if v else None

    def get_broker_appliances_est(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'appliances_est', None) if v else None

    def get_broker_plumbing_est(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'plumbing_est', None) if v else None

    def get_broker_electrical_est(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'electrical_est', None) if v else None

    def get_broker_landscaping_est(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'landscaping_est', None) if v else None

    def get_broker_notes(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'notes', None) if v else None

    def get_broker_links(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'links', None) if v else None

    # ----------------- Internal Initial UW getters -----------------
    def get_internal_initial_uw_asis_value(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'asis_value', None) if v else None

    def get_internal_initial_uw_arv_value(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'arv_value', None) if v else None

    def get_internal_initial_uw_value_date(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'value_date', None) if v else None

    def get_internal_initial_uw_rehab_est_total(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'rehab_est_total', None) if v else None

    def get_internal_initial_uw_roof_est(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'roof_est', None) if v else None

    def get_internal_initial_uw_kitchen_est(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'kitchen_est', None) if v else None

    def get_internal_initial_uw_bath_est(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'bath_est', None) if v else None

    def get_internal_initial_uw_flooring_est(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'flooring_est', None) if v else None

    def get_internal_initial_uw_windows_est(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'windows_est', None) if v else None

    def get_internal_initial_uw_appliances_est(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'appliances_est', None) if v else None

    def get_internal_initial_uw_plumbing_est(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'plumbing_est', None) if v else None

    def get_internal_initial_uw_electrical_est(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'electrical_est', None) if v else None

    def get_internal_initial_uw_landscaping_est(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'landscaping_est', None) if v else None

    # ----------------- Seller getters -----------------
    def get_seller_asis_value(self, obj):
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'asis_value', None) if v else None

    def get_seller_arv_value(self, obj):
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'arv_value', None) if v else None

    def get_seller_value_date(self, obj):
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'value_date', None) if v else None

    def get_seller_rehab_est_total(self, obj):
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'rehab_est_total', None) if v else None

    def get_seller_roof_est(self, obj):
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'roof_est', None) if v else None

    def get_seller_kitchen_est(self, obj):
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'kitchen_est', None) if v else None

    def get_seller_bath_est(self, obj):
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'bath_est', None) if v else None

    def get_seller_flooring_est(self, obj):
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'flooring_est', None) if v else None

    def get_seller_windows_est(self, obj):
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'windows_est', None) if v else None

    def get_seller_appliances_est(self, obj):
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'appliances_est', None) if v else None

    def get_seller_plumbing_est(self, obj):
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'plumbing_est', None) if v else None

    def get_seller_electrical_est(self, obj):
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'electrical_est', None) if v else None

    def get_seller_landscaping_est(self, obj):
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'landscaping_est', None) if v else None


class AssetDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single SellerBoardedData asset record.
    Exposes fields used by the loan-level modal tabs (Snapshot, Property, Loan, etc.).

    Docs:
    - DRF ModelSerializer: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    # Expose hub id explicitly for downstream API calls (e.g., outcomes ensure-create)
    asset_hub_id = serializers.SerializerMethodField()

    def get_asset_hub_id(self, obj):
        hub = getattr(obj, 'asset_hub', None)
        return getattr(hub, 'id', None)

    class Meta:
        model = SellerBoardedData
        # Explicitly list fields for stability and to avoid over-exposing internals
        fields = [
            # Identity
            'id', 'asset_hub_id', 'sellertape_id', 'seller_name', 'trade_name', 'asset_status', 'as_of_date',
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
