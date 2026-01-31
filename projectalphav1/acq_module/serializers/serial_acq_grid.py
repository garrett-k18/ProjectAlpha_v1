"""
Serializer for AG Grid data.

WHAT: Efficient serializer for main acquisitions grid.
WHY: Previous serializer had N+1 queries for valuations.
HOW: Cache valuations per-object, use prefetched data efficiently.

Usage:
    GET /api/acq/grid/{seller_id}/{trade_id}/
"""

from rest_framework import serializers
from acq_module.models.model_acq_seller import AcqAsset
from core.models.model_co_geoAssumptions import StateReference


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
    sellertape_id = serializers.SerializerMethodField()
    seller_loan_id = serializers.SerializerMethodField()
    trade_id = serializers.IntegerField(read_only=True)
    trade_name = serializers.CharField(source='trade.trade_name', read_only=True, default=None)
    
    # -------------------------------------------------------------------------
    # Location
    # -------------------------------------------------------------------------
    street_address = serializers.CharField(source='property.street_address', read_only=True)
    city = serializers.CharField(source='property.city', read_only=True)
    state = serializers.CharField(source='property.state', read_only=True)
    zip = serializers.CharField(source='property.zip', read_only=True)
    county = serializers.CharField(source='asset_hub.enrichment.geocode_county', read_only=True, default=None)
    
    # -------------------------------------------------------------------------
    # Property Info
    # -------------------------------------------------------------------------
    property_type = serializers.SerializerMethodField()
    occupancy_status = serializers.CharField(source='property.occupancy', read_only=True)
    bedrooms = serializers.IntegerField(source='property.beds', read_only=True)
    bathrooms = serializers.DecimalField(source='property.baths', max_digits=4, decimal_places=1, read_only=True)
    sqft = serializers.IntegerField(source='property.sq_ft', read_only=True)
    year_built = serializers.IntegerField(source='property.year_built', read_only=True)
    lot_size = serializers.DecimalField(source='property.lot_size', max_digits=12, decimal_places=2, read_only=True)
    
    # -------------------------------------------------------------------------
    # Loan Info
    # -------------------------------------------------------------------------
    current_balance = serializers.DecimalField(source='loan.current_balance', max_digits=14, decimal_places=2, read_only=True)
    total_debt = serializers.DecimalField(source='loan.total_debt', max_digits=14, decimal_places=2, read_only=True)
    interest_rate = serializers.DecimalField(source='loan.interest_rate', max_digits=6, decimal_places=4, read_only=True)
    default_rate = serializers.DecimalField(source='loan.default_rate', max_digits=6, decimal_places=4, read_only=True)
    maturity_date = serializers.DateField(source='loan.current_maturity_date', read_only=True)
    origination_date = serializers.DateField(source='loan.origination_date', read_only=True)
    months_delinquent = serializers.IntegerField(source='loan.months_dlq', read_only=True)
    
    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------
    acq_status = serializers.CharField(read_only=True)
    fc_status = serializers.SerializerMethodField()
    judicial = serializers.SerializerMethodField()
    
    # -------------------------------------------------------------------------
    # Seller Values
    # -------------------------------------------------------------------------
    seller_asis_value = serializers.SerializerMethodField()
    seller_arv_value = serializers.SerializerMethodField()
    seller_value_date = serializers.SerializerMethodField()
    
    # -------------------------------------------------------------------------
    # Enrichment (MSA)
    # -------------------------------------------------------------------------
    msa = serializers.SerializerMethodField()
    msa_code = serializers.SerializerMethodField()
    
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

    def _get_field_from_sources(self, obj, sources: list, field: str):
        """
        WHAT: Return first non-null valuation field across multiple sources.
        WHY: Seller valuations can be stored under legacy or new source codes.
        HOW: Iterate sources in priority order and return the first match.
        """
        for source in sources:
            value = self._get_field_from_source(obj, source, field)
            if value is not None:
                return value
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

    def get_msa(self, obj):
        hub = getattr(obj, 'asset_hub', None)
        enrichment = getattr(hub, 'enrichment', None) if hub else None
        return getattr(enrichment, 'geocode_msa', None) if enrichment else None

    def get_msa_code(self, obj):
        hub = getattr(obj, 'asset_hub', None)
        enrichment = getattr(hub, 'enrichment', None) if hub else None
        return getattr(enrichment, 'geocode_msa_code', None) if enrichment else None

    def get_sellertape_id(self, obj):
        """
        WHAT: Return seller tape ID from related loan.
        WHY: Tape identifiers live on AcqLoan after model split.
        HOW: Read from obj.loan with null-safe fallback.
        """
        loan = getattr(obj, 'loan', None)
        return getattr(loan, 'sellertape_id', None) if loan else None

    def get_seller_loan_id(self, obj):
        """
        WHAT: Return seller loan ID for frontend compatibility.
        WHY: Frontend expects seller_loan_id even when sellertape_id exists.
        HOW: Use sellertape_id as the canonical loan identifier.
        """
        loan = getattr(obj, 'loan', None)
        return getattr(loan, 'sellertape_id', None) if loan else None

    def get_property_type(self, obj):
        """
        WHAT: Return unified property type for grid display.
        WHY: Subclass is the single property type source of truth.
        HOW: Use AcqProperty.property_type_merged when available.
        """
        prop = getattr(obj, 'property', None)
        return getattr(prop, 'property_type_merged', None) if prop else None

    def get_fc_status(self, obj):
        """
        WHAT: Return foreclosure status (placeholder).
        WHY: FC status is not yet modeled in AcqForeclosureTimeline.
        HOW: Return None until a status field exists.
        """
        return None

    def get_judicial(self, obj):
        """
        WHAT: Determine if the asset is in a judicial state.
        WHY: Grid needs a judicial/non-judicial flag for filtering.
        HOW: Lookup StateReference by state code with cached map.
        """
        prop = getattr(obj, 'property', None)
        state = getattr(prop, 'state', None) if prop else None
        if not state:
            return None

        if not hasattr(self, '_judicial_cache'):
            self._judicial_cache = {
                sr.state_code: sr.judicialvsnonjudicial
                for sr in StateReference.objects.all()
            }

        return self._judicial_cache.get(state.strip().upper())

    def get_seller_asis_value(self, obj):
        """
        WHAT: Return seller as-is value from valuations.
        WHY: Seller values are stored in Valuation, not on AcqAsset.
        HOW: Use cached valuations prefetched on asset_hub.
        """
        return self._get_field_from_sources(obj, ['sellerProvided', 'seller'], 'asis_value')

    def get_seller_arv_value(self, obj):
        """
        WHAT: Return seller ARV value from valuations.
        WHY: Seller values are stored in Valuation, not on AcqAsset.
        HOW: Use cached valuations prefetched on asset_hub.
        """
        return self._get_field_from_sources(obj, ['sellerProvided', 'seller'], 'arv_value')

    def get_seller_value_date(self, obj):
        """
        WHAT: Return seller valuation date from valuations.
        WHY: Use valuation date for recency indicators.
        HOW: Use cached valuations prefetched on asset_hub.
        """
        return self._get_field_from_sources(obj, ['sellerProvided', 'seller'], 'value_date')
