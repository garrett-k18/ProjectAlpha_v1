"""
Serializer for AG Grid data.

WHAT: Efficient serializer for main acquisitions grid.
WHY: Previous serializer had N+1 queries for valuations.
HOW: Cache valuations per-object, use prefetched data efficiently.

Usage:
    GET /api/acq/grid/{seller_id}/{trade_id}/
"""

from rest_framework import serializers
from acq_module.models.model_acq_seller import SellerRawData


class GridRowSerializer(serializers.Serializer):
    """
    Efficient serializer for AG Grid rows.
    
    Caches valuation lookups per-object to avoid N+1 queries.
    All valuation data comes from prefetched asset_hub__valuations.
    """
    
    # -------------------------------------------------------------------------
    # Core Identifiers
    # -------------------------------------------------------------------------
    id = serializers.IntegerField(source='pk', read_only=True)
    asset_hub_id = serializers.IntegerField(read_only=True)
    sellertape_id = serializers.CharField(read_only=True)
    seller_loan_id = serializers.CharField(read_only=True)
    trade_id = serializers.IntegerField(read_only=True)
    trade_name = serializers.CharField(source='trade.trade_name', read_only=True, default=None)
    
    # -------------------------------------------------------------------------
    # Location
    # -------------------------------------------------------------------------
    street_address = serializers.CharField(read_only=True)
    city = serializers.CharField(read_only=True)
    state = serializers.CharField(read_only=True)
    zip = serializers.CharField(read_only=True)
    county = serializers.CharField(read_only=True)
    
    # -------------------------------------------------------------------------
    # Property Info
    # -------------------------------------------------------------------------
    property_type = serializers.CharField(read_only=True)
    occupancy_status = serializers.CharField(read_only=True)
    bedrooms = serializers.IntegerField(read_only=True)
    bathrooms = serializers.DecimalField(max_digits=4, decimal_places=1, read_only=True)
    sqft = serializers.IntegerField(read_only=True)
    year_built = serializers.IntegerField(read_only=True)
    lot_size = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    # -------------------------------------------------------------------------
    # Loan Info
    # -------------------------------------------------------------------------
    current_balance = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total_debt = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    interest_rate = serializers.DecimalField(max_digits=6, decimal_places=4, read_only=True)
    default_rate = serializers.DecimalField(max_digits=6, decimal_places=4, read_only=True)
    maturity_date = serializers.DateField(read_only=True)
    origination_date = serializers.DateField(read_only=True)
    months_delinquent = serializers.IntegerField(read_only=True)
    
    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------
    acq_status = serializers.CharField(read_only=True)
    fc_status = serializers.CharField(read_only=True)
    judicial = serializers.BooleanField(read_only=True)
    
    # -------------------------------------------------------------------------
    # Seller Values
    # -------------------------------------------------------------------------
    seller_asis_value = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    seller_arv_value = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    seller_value_date = serializers.DateField(read_only=True)
    
    # -------------------------------------------------------------------------
    # Internal Initial UW Valuation (computed from prefetched data)
    # -------------------------------------------------------------------------
    internal_initial_uw_asis_value = serializers.SerializerMethodField()
    internal_initial_uw_arv_value = serializers.SerializerMethodField()
    internal_initial_uw_grade = serializers.SerializerMethodField()
    
    # -------------------------------------------------------------------------
    # Broker Valuation (computed from prefetched data)
    # -------------------------------------------------------------------------
    broker_asis_value = serializers.SerializerMethodField()
    broker_arv_value = serializers.SerializerMethodField()
    broker_rehab_est = serializers.SerializerMethodField()
    broker_recommend_rehab = serializers.SerializerMethodField()
    
    # -------------------------------------------------------------------------
    # Valuation Cache - avoids N+1 queries
    # -------------------------------------------------------------------------
    
    def _get_valuations_cache(self, obj):
        """
        Build and cache valuation lookup for this object.
        
        Returns dict: { source: [list of valuations sorted by -created_at] }
        """
        cache_key = '_val_cache'
        if not hasattr(obj, cache_key):
            by_source = {}
            hub = getattr(obj, 'asset_hub', None)
            if hub:
                for val in hub.valuations.all():  # Uses prefetched data
                    src = val.source
                    if src not in by_source:
                        by_source[src] = []
                    by_source[src].append(val)
            setattr(obj, cache_key, by_source)
        return getattr(obj, cache_key)
    
    def _get_field_from_source(self, obj, source: str, field: str):
        """Get first non-null value for field from valuations of given source."""
        cache = self._get_valuations_cache(obj)
        vals = cache.get(source, [])
        for val in vals:
            value = getattr(val, field, None)
            if value is not None:
                return value
        return None
    
    def _get_grade_from_source(self, obj, source: str):
        """Get grade code from valuations of given source."""
        cache = self._get_valuations_cache(obj)
        vals = cache.get(source, [])
        for val in vals:
            if val.grade:
                return val.grade.code
        return None
    
    # -------------------------------------------------------------------------
    # Internal Initial UW Getters
    # -------------------------------------------------------------------------
    
    def get_internal_initial_uw_asis_value(self, obj):
        return self._get_field_from_source(obj, 'internalInitialUW', 'asis_value')
    
    def get_internal_initial_uw_arv_value(self, obj):
        return self._get_field_from_source(obj, 'internalInitialUW', 'arv_value')
    
    def get_internal_initial_uw_grade(self, obj):
        return self._get_grade_from_source(obj, 'internalInitialUW')
    
    # -------------------------------------------------------------------------
    # Broker Getters
    # -------------------------------------------------------------------------
    
    def get_broker_asis_value(self, obj):
        return self._get_field_from_source(obj, 'broker', 'asis_value')
    
    def get_broker_arv_value(self, obj):
        return self._get_field_from_source(obj, 'broker', 'arv_value')
    
    def get_broker_rehab_est(self, obj):
        return self._get_field_from_source(obj, 'broker', 'rehab_est_total')
    
    def get_broker_recommend_rehab(self, obj):
        return self._get_field_from_source(obj, 'broker', 'recommend_rehab')
