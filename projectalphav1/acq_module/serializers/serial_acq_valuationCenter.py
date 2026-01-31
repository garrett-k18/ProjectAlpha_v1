"""
Serializer for Valuation Center data.

WHAT: Combines basic asset info from AcqAsset/Loan/Property with valuation data from Valuation model.
WHY: Valuation Center needs a focused, efficient data layer without MSA/geo overhead.
HOW: Single serializer serves all tabs (Overview, Reconciliation, Brokers).

Usage:
    GET /api/acq/valuation-center/{seller_id}/{trade_id}/
    PUT /api/acq/valuation-center/{asset_id}/
"""

from rest_framework import serializers
from acq_module.models.model_acq_seller import AcqAsset
from core.models.model_co_valuations import Valuation, ValuationGradeReference


class ValuationCenterRowSerializer(serializers.Serializer):
    """
    Read-only serializer for valuation center list view.
    
    Combines:
    - Basic asset identifiers and location from AcqAsset/Loan/Property
    - Seller-provided values from Valuation model
    - Internal Initial UW valuation data from Valuation model
    - Broker valuation data from Valuation model
    """
    
    # -------------------------------------------------------------------------
    # Asset Identifiers (from AcqAsset/Loan)
    # -------------------------------------------------------------------------
    id = serializers.IntegerField(source='pk', read_only=True)
    asset_hub_id = serializers.IntegerField(read_only=True)
    sellertape_id = serializers.CharField(source='loan.sellertape_id', read_only=True)
    
    # -------------------------------------------------------------------------
    # Location (from AcqProperty)
    # -------------------------------------------------------------------------
    street_address = serializers.CharField(source='property.street_address', read_only=True)
    city = serializers.CharField(source='property.city', read_only=True)
    state = serializers.CharField(source='property.state', read_only=True)
    zip = serializers.CharField(source='property.zip', read_only=True)
    
    # -------------------------------------------------------------------------
    # Loan Info (from AcqLoan)
    # -------------------------------------------------------------------------
    current_balance = serializers.DecimalField(source='loan.current_balance', max_digits=14, decimal_places=2, read_only=True)
    total_debt = serializers.DecimalField(source='loan.total_debt', max_digits=14, decimal_places=2, read_only=True)
    
    # -------------------------------------------------------------------------
    # Seller Values (from Valuation model)
    # -------------------------------------------------------------------------
    seller_asis_value = serializers.SerializerMethodField()
    seller_arv_value = serializers.SerializerMethodField()
    
    # -------------------------------------------------------------------------
    # Internal Initial UW Valuation (from Valuation model, source='internalInitialUW')
    # -------------------------------------------------------------------------
    internal_initial_uw_asis_value = serializers.SerializerMethodField()
    internal_initial_uw_arv_value = serializers.SerializerMethodField()
    internal_initial_uw_grade = serializers.SerializerMethodField()
    internal_initial_uw_notes = serializers.SerializerMethodField()
    internal_initial_uw_trashout_est = serializers.SerializerMethodField()
    
    # -------------------------------------------------------------------------
    # Broker Valuation (from Valuation model, source='broker')
    # -------------------------------------------------------------------------
    broker_asis_value = serializers.SerializerMethodField()
    broker_arv_value = serializers.SerializerMethodField()
    broker_rehab_est = serializers.SerializerMethodField()
    broker_recommend_rehab = serializers.SerializerMethodField()
    broker_notes = serializers.SerializerMethodField()
    
    # -------------------------------------------------------------------------
    # Internal Cache for Valuations
    # -------------------------------------------------------------------------
    
    def _get_valuations_by_source(self, obj):
        """
        Get all valuations for this asset, organized by source.
        
        WHAT: Build a dict of source -> best Valuation object
        WHY: Avoid repeated iteration through prefetched valuations
        HOW: Cache on the serializer instance per object
        
        Priority: Prefer valuations with grade set, then most recent
        """
        # Use object ID as cache key
        cache_attr = '_valuation_cache'
        if not hasattr(self, cache_attr):
            setattr(self, cache_attr, {})
        
        cache = getattr(self, cache_attr)
        obj_id = obj.pk
        
        if obj_id in cache:
            return cache[obj_id]
        
        # Build source -> valuation map from prefetched data
        result = {}
        hub = getattr(obj, 'asset_hub', None)
        if hub is None:
            cache[obj_id] = result
            return result
        
        # Group valuations by source
        by_source = {}
        for val in hub.valuations.all():
            source = val.source
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(val)
        
        # For each source, pick the best valuation:
        # 1. Prefer one with a grade set
        # 2. Otherwise take the most recent (first in list since ordered by -created_at)
        for source, vals in by_source.items():
            with_grade = [v for v in vals if v.grade_id is not None]
            result[source] = with_grade[0] if with_grade else vals[0]
        
        cache[obj_id] = result
        return result
    
    def _get_all_valuations_for_source(self, obj, source: str):
        """Get all valuations for a specific source."""
        hub = getattr(obj, 'asset_hub', None)
        if hub is None:
            return []
        return [v for v in hub.valuations.all() if v.source == source]
    
    def _get_field_from_valuations(self, valuations, field: str):
        """Get first non-null value for a field from a list of valuations."""
        for val in valuations:
            value = getattr(val, field, None)
            if value is not None:
                return value
        return None
    
    # -------------------------------------------------------------------------
    # Internal Initial UW Getters
    # -------------------------------------------------------------------------
    
    def get_internal_initial_uw_asis_value(self, obj):
        vals = self._get_all_valuations_for_source(obj, 'internalInitialUW')
        return self._get_field_from_valuations(vals, 'asis_value')
    
    def get_internal_initial_uw_arv_value(self, obj):
        vals = self._get_all_valuations_for_source(obj, 'internalInitialUW')
        return self._get_field_from_valuations(vals, 'arv_value')
    
    def get_internal_initial_uw_grade(self, obj):
        """Return grade code (A+, A, B, C, D, F) from ValuationGradeReference."""
        vals = self._get_all_valuations_for_source(obj, 'internalInitialUW')
        for val in vals:
            if val.grade:
                return val.grade.code
        return None
    
    def get_internal_initial_uw_notes(self, obj):
        vals = self._get_all_valuations_for_source(obj, 'internalInitialUW')
        return self._get_field_from_valuations(vals, 'notes')
    
    def get_internal_initial_uw_trashout_est(self, obj):
        vals = self._get_all_valuations_for_source(obj, 'internalInitialUW')
        return self._get_field_from_valuations(vals, 'trashout_est_total')
    
    # -------------------------------------------------------------------------
    # Broker Getters
    # -------------------------------------------------------------------------
    
    def get_broker_asis_value(self, obj):
        vals = self._get_all_valuations_for_source(obj, 'broker')
        return self._get_field_from_valuations(vals, 'asis_value')
    
    def get_broker_arv_value(self, obj):
        vals = self._get_all_valuations_for_source(obj, 'broker')
        return self._get_field_from_valuations(vals, 'arv_value')
    
    def get_broker_rehab_est(self, obj):
        vals = self._get_all_valuations_for_source(obj, 'broker')
        return self._get_field_from_valuations(vals, 'rehab_est_total')
    
    def get_broker_recommend_rehab(self, obj):
        vals = self._get_all_valuations_for_source(obj, 'broker')
        return self._get_field_from_valuations(vals, 'recommend_rehab')
    
    def get_broker_notes(self, obj):
        vals = self._get_all_valuations_for_source(obj, 'broker')
        return self._get_field_from_valuations(vals, 'notes')

    # -------------------------------------------------------------------------
    # Seller Values Getters
    # -------------------------------------------------------------------------

    def _get_seller_valuations(self, obj):
        """Return seller-provided valuations from any seller source tag."""
        seller_vals = self._get_all_valuations_for_source(obj, 'seller')
        seller_provided_vals = self._get_all_valuations_for_source(obj, 'sellerProvided')
        return seller_vals + seller_provided_vals

    def get_seller_asis_value(self, obj):
        vals = self._get_seller_valuations(obj)
        return self._get_field_from_valuations(vals, 'asis_value')

    def get_seller_arv_value(self, obj):
        vals = self._get_seller_valuations(obj)
        return self._get_field_from_valuations(vals, 'arv_value')


class ValuationUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating valuation data.
    
    WHAT: Accept and validate valuation updates
    WHY: Single update endpoint for grades, values, and rehab estimates
    HOW: Validate incoming fields and return cleaned data
    """
    
    # Source determines which valuation record to update
    source = serializers.ChoiceField(
        choices=['internalInitialUW', 'broker'],
        required=True,
    )
    
    # Value fields (all optional - only update what's provided)
    asis_value = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, allow_null=True)
    arv_value = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, allow_null=True)
    grade_code = serializers.CharField(max_length=10, required=False, allow_null=True, allow_blank=True)
    rehab_est_total = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, allow_null=True)
    trashout_est_total = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, allow_null=True)
    recommend_rehab = serializers.BooleanField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    
    def validate_grade_code(self, value):
        """Validate grade code exists in ValuationGradeReference."""
        if value:
            if not ValuationGradeReference.objects.filter(code=value).exists():
                raise serializers.ValidationError(f"Invalid grade code: {value}")
        return value
