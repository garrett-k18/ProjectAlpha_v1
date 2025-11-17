"""
DRF Serializers for Acquisitions Module data structures.

This module defines serializers for:
- SellerRawData AG Grid rows with unified valuation integration
- Seller dropdown options
- Trade dropdown options
- Field metadata for dynamic column generation

Follows the same pattern as am_module.serializers.serial_am_assetInventory for consistency.

Docs reviewed:
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- DRF SerializerMethodField: https://www.django-rest-framework.org/api-guide/fields/#serializermethodfield
"""
from rest_framework import serializers
import logging
from ..models.model_acq_seller import Seller, Trade, SellerRawData
from core.models.valuations import Valuation

logger = logging.getLogger(__name__)


class SellerRawDataRowSerializer(serializers.Serializer):
    """
    Flat row shape tailored for AG Grid. We keep this serializer
    detached from a specific model to freely compose from multiple sources.
    
    This serializer handles SellerRawData with unified valuation integration,
    pulling broker and internal valuation data from the core.Valuation model.
    """
    # Core SellerRawData fields
    # CRITICAL: SellerRawData uses asset_hub as PK (OneToOne primary_key=True), so obj.id doesn't exist.
    # Using SerializerMethodField to expose asset_hub_id as 'id' for frontend consistency.
    # Asset Hub ID is the master identifier across the system.
    # WARNING: Never use `id = serializers.IntegerField(read_only=True)` - it will return undefined!
    id = serializers.SerializerMethodField()
    # WHAT: Loan/Seller tape ID as CharField to handle various formats
    # WHY: Loan IDs come in different formats: numbers, alphanumeric, with hyphens (e.g., '591-126709', 'ABC-123')
    # HOW: CharField allows any format, matching the model definition
    sellertape_id = serializers.CharField(allow_null=True, allow_blank=True)
    # Trade metadata for header/title usage in frontend
    # Expose the FK id directly and a readable trade_name from related Trade model
    trade_id = serializers.IntegerField(read_only=True, required=False)
    trade_name = serializers.SerializerMethodField()
    # Hub-level commercial flag for UI toggles
    is_commercial = serializers.SerializerMethodField()
    
    def get_id(self, obj):
        """Return the Asset Hub ID (SellerRawData PK).
        
        SellerRawData model uses asset_hub OneToOneField as primary_key=True,
        so Django doesn't create a standard 'id' field. Always use asset_hub_id.
        """
        return getattr(obj, 'asset_hub_id', None) or getattr(obj, 'pk', None)
    
    def get_trade_name(self, obj):
        """Return related Trade.trade_name if available; else empty string.
        Keeping this as a method avoids N+1 when views prefetch related trade.
        """
        try:
            # Access already-fetched relation when prefetch/select_related is applied
            t = getattr(obj, 'trade', None)
            return getattr(t, 'trade_name', '') if t else ''
        except Exception:
            return ''
    
    def get_is_commercial(self, obj):
        """Return boolean commercial tag from AssetIdHub.
        Falls back to False if hub/flag not present.
        """
        try:
            hub = getattr(obj, 'asset_hub', None)
            return bool(getattr(hub, 'is_commercial_flag', False)) if hub is not None else False
        except Exception:
            return False
    asset_status = serializers.CharField(allow_null=True)
    
    # Related model fields accessed via foreign keys
    as_of_date = serializers.DateField(allow_null=True)
    
    # Property details
    street_address = serializers.CharField(allow_null=True)
    city = serializers.CharField(allow_null=True)
    state = serializers.CharField(allow_null=True)
    zip = serializers.CharField(allow_null=True)  # Map zip field from model
    zip_normalized = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    msa = serializers.SerializerMethodField()
    msa_code = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    msa_name = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    msa_state = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    county = serializers.SerializerMethodField()
    property_type = serializers.CharField(allow_null=True)
    # New: flow product_type to frontend rows so badges render in snapshots/modals
    product_type = serializers.CharField(allow_null=True, allow_blank=True)
    occupancy = serializers.CharField(allow_null=True)
    year_built = serializers.IntegerField(allow_null=True)
    sq_ft = serializers.IntegerField(allow_null=True)
    lot_size = serializers.IntegerField(allow_null=True)
    beds = serializers.IntegerField(allow_null=True)
    baths = serializers.IntegerField(allow_null=True)
    
    # Financial fields
    current_balance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    original_balance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    interest_rate = serializers.DecimalField(max_digits=6, decimal_places=4, allow_null=True)
    total_debt = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    
    # Date fields
    origination_date = serializers.DateField(allow_null=True)
    next_due_date = serializers.DateField(allow_null=True)
    last_paid_date = serializers.DateField(allow_null=True)
    
    # Delinquency metrics
    months_dlq = serializers.IntegerField(allow_null=True)
    
    # Borrower fields
    borrower1_last = serializers.CharField(allow_null=True, allow_blank=True)
    borrower1_first = serializers.CharField(allow_null=True, allow_blank=True)
    borrower1_full_name = serializers.CharField(allow_null=True, allow_blank=True)
    borrower2_last = serializers.CharField(allow_null=True, allow_blank=True)
    borrower2_first = serializers.CharField(allow_null=True, allow_blank=True)
    borrower2_full_name = serializers.CharField(allow_null=True, allow_blank=True)

    # Direct seller valuation fields (from SellerRawData model)
    seller_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    seller_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    seller_value_date = serializers.DateField(allow_null=True)
    
    # Additional financial and schedule fields
    deferred_balance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    first_pay_date = serializers.DateField(allow_null=True)
    original_term = serializers.IntegerField(allow_null=True)
    original_rate = serializers.DecimalField(max_digits=6, decimal_places=4, allow_null=True)
    original_maturity_date = serializers.DateField(allow_null=True)
    default_rate = serializers.DecimalField(max_digits=6, decimal_places=4, allow_null=True)
    current_maturity_date = serializers.DateField(allow_null=True)
    current_term = serializers.IntegerField(allow_null=True)
    accrued_note_interest = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    accrued_default_interest = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    escrow_balance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    escrow_advance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    recoverable_corp_advance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    late_fees = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    other_fees = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    suspense_balance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)

    origination_value = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    origination_arv = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    origination_value_date = serializers.DateField(allow_null=True)

    additional_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    additional_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    additional_value_date = serializers.DateField(allow_null=True)

    # Foreclosure flags and dates
    fc_flag = serializers.BooleanField(required=False)
    fc_first_legal_date = serializers.DateField(allow_null=True)
    fc_referred_date = serializers.DateField(allow_null=True)
    fc_judgement_date = serializers.DateField(allow_null=True)
    fc_scheduled_sale_date = serializers.DateField(allow_null=True)
    fc_sale_date = serializers.DateField(allow_null=True)
    fc_starting = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)

    # Bankruptcy
    bk_flag = serializers.BooleanField(required=False)
    bk_chapter = serializers.CharField(allow_null=True, allow_blank=True)

    # Modification details
    mod_flag = serializers.BooleanField(required=False)
    mod_date = serializers.DateField(allow_null=True)
    mod_maturity_date = serializers.DateField(allow_null=True)
    mod_term = serializers.IntegerField(allow_null=True)
    mod_rate = serializers.DecimalField(max_digits=6, decimal_places=4, allow_null=True)
    mod_initial_balance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)

    # WHAT: Asset-level acquisition status (KEEP/DROP)
    # WHY: Simple binary flag for active pool filtering
    # HOW: Trade-level status on Trade model controls lifecycle (PASS, DD, AWARDED, BOARD)
    acq_status = serializers.CharField()
    # WHAT: Backward compatibility helper for is_dropped
    # WHY: Grid may still reference is_dropped property
    # HOW: SerializerMethodField computes from acq_status (DROP = True, KEEP = False)
    is_dropped = serializers.SerializerMethodField()

    # Unified valuation fields (from core.Valuation model)
    # Broker valuations (source='broker')
    broker_asis_value = serializers.SerializerMethodField()
    broker_arv_value = serializers.SerializerMethodField()
    broker_value_date = serializers.SerializerMethodField()
    broker_rehab_est = serializers.SerializerMethodField()
    broker_notes = serializers.SerializerMethodField()
    broker_links = serializers.SerializerMethodField()
    broker_recommend_rehab = serializers.SerializerMethodField()
    broker_grade = serializers.SerializerMethodField()
    broker_contact_id = serializers.SerializerMethodField()
    # Detailed broker rehab estimates
    broker_roof_est = serializers.SerializerMethodField()
    broker_kitchen_est = serializers.SerializerMethodField()
    broker_bath_est = serializers.SerializerMethodField()
    broker_flooring_est = serializers.SerializerMethodField()
    broker_windows_est = serializers.SerializerMethodField()
    broker_appliances_est = serializers.SerializerMethodField()
    broker_plumbing_est = serializers.SerializerMethodField()
    broker_electrical_est = serializers.SerializerMethodField()
    broker_landscaping_est = serializers.SerializerMethodField()
    # Detailed broker rehab grades
    broker_roof_grade = serializers.SerializerMethodField()
    broker_kitchen_grade = serializers.SerializerMethodField()
    broker_bath_grade = serializers.SerializerMethodField()
    broker_flooring_grade = serializers.SerializerMethodField()
    broker_windows_grade = serializers.SerializerMethodField()
    broker_appliances_grade = serializers.SerializerMethodField()
    broker_plumbing_grade = serializers.SerializerMethodField()
    broker_electrical_grade = serializers.SerializerMethodField()
    broker_landscaping_grade = serializers.SerializerMethodField()
    
    # Internal Initial UW valuations (source='internalInitialUW')
    internal_initial_uw_asis_value = serializers.SerializerMethodField()
    internal_initial_uw_arv_value = serializers.SerializerMethodField()
    internal_initial_uw_value_date = serializers.SerializerMethodField()
    internal_initial_uw_grade = serializers.SerializerMethodField()
    internal_initial_uw_grade_id = serializers.SerializerMethodField()
    internal_initial_uw_notes = serializers.SerializerMethodField()
    
   
    
    # Helper methods for unified valuations
    def _latest_val_by_source(self, obj, source: str):
        """Return latest Valuation row for the object's asset_hub and given source.
        
        Uses prefetched data from asset_hub.valuations to avoid N+1 queries.
        The queryset uses prefetch_related('asset_hub__valuations') to load
        ALL valuations in ONE database query.
        
        WHAT: Handle NULL value_dates for grade-only valuations
        WHY: Valuations created with only grade have no value_date
        HOW: Sort by created_at (most recent) when value_date is NULL
        """
        hub = getattr(obj, 'asset_hub', None)
        if hub is None:
            return None
        
        # WHAT: Get all valuations for this hub
        # WHY: Debug prefetch issue
        all_vals = list(hub.valuations.all())
        
        # Debug logging for asset 3691
        import logging
        logger = logging.getLogger(__name__)
        if obj.asset_hub_id == 3691:
            logger.info(f"[Serializer] Asset 3691 has {len(all_vals)} total valuations")
            for v in all_vals:
                logger.info(f"[Serializer]   - source={v.source}, grade={v.grade.code if v.grade else None}, created={v.created_at}")
        
        # Use prefetched valuations (already in memory) - NO new query!
        # Filter and sort in Python instead of hitting the database
        valuations = [v for v in all_vals if v.source == source]
        
        if not valuations:
            if obj.asset_hub_id == 3691:
                logger.info(f"[Serializer] Asset 3691 has NO {source} valuations")
            return None
        
        # WHAT: Sort by created_at (most recent first) to handle NULL value_dates
        # WHY: Grade-only valuations have NULL value_date
        # HOW: Use created_at as primary sort key (always present)
        from datetime import datetime
        valuations.sort(
            key=lambda v: v.created_at if v.created_at else datetime.min,
            reverse=True
        )
        
        return valuations[0] if valuations else None
    
    # Broker valuation getters
    def get_broker_asis_value(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'asis_value', None) if v else None
    
    def get_broker_arv_value(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'arv_value', None) if v else None
    
    def get_broker_value_date(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'value_date', None) if v else None
    
    def get_broker_rehab_est(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'rehab_est_total', None) if v else None
    
    def get_broker_notes(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'notes', None) if v else None
    
    def get_broker_links(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'links', None) if v else None
    
    def get_broker_recommend_rehab(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'recommend_rehab', None) if v else None
    
    def get_broker_grade(self, obj):
        """Return grade code for broker valuation."""
        v = self._latest_val_by_source(obj, 'broker')
        if v and v.grade:
            return v.grade.code
        return None
    
    def get_broker_contact_id(self, obj):
        """Return broker_contact (MasterCRM) ID for broker valuation."""
        v = self._latest_val_by_source(obj, 'broker')
        if v and v.broker_contact:
            return v.broker_contact.id
        return None
    
    # Detailed broker rehab estimate getters
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
    
    # Detailed broker rehab grade getters
    def get_broker_roof_grade(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'roof_grade', None) if v else None
    
    def get_broker_kitchen_grade(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'kitchen_grade', None) if v else None
    
    def get_broker_bath_grade(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'bath_grade', None) if v else None
    
    def get_broker_flooring_grade(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'flooring_grade', None) if v else None
    
    def get_broker_windows_grade(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'windows_grade', None) if v else None
    
    def get_broker_appliances_grade(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'appliances_grade', None) if v else None
    
    def get_broker_plumbing_grade(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'plumbing_grade', None) if v else None
    
    def get_broker_electrical_grade(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'electrical_grade', None) if v else None
    
    def get_broker_landscaping_grade(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'landscaping_grade', None) if v else None
    
    # Internal Initial UW valuation getters
    def get_internal_initial_uw_asis_value(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'asis_value', None) if v else None
    
    def get_internal_initial_uw_arv_value(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'arv_value', None) if v else None
    
    def get_internal_initial_uw_value_date(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'value_date', None) if v else None
    
    def get_internal_initial_uw_grade(self, obj):
        """Return grade code for Internal Initial UW valuation.
        
        WHAT: Get grade code (A+, A, B, C, D, F) from related ValuationGradeReference
        WHY: Frontend needs grade for dropdown display
        HOW: Get latest internalInitialUW valuation, then get grade.code if exists
        """
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        if v:
            # WHAT: Check if valuation has grade relationship
            # WHY: Debug why grade isn't showing in frontend
            grade_obj = v.grade
            if grade_obj:
                grade_code = grade_obj.code
                # Debug logging to verify grade is being accessed
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"[Serializer] Asset {obj.asset_hub_id} has grade: {grade_code}")
                return grade_code
        return None
    
    def get_internal_initial_uw_grade_id(self, obj):
        """Return grade ID for Internal Initial UW valuation.
        
        WHAT: Get grade ID for updating grade via API
        WHY: Frontend needs ID to send back when changing grade
        HOW: Get latest internalInitialUW valuation, then get grade_id
        """
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return v.grade_id if v else None
    
    def get_internal_initial_uw_notes(self, obj):
        """Return notes for Internal Initial UW valuation.
        
        WHAT: Get notes from internal valuation
        WHY: ReconciliationTab needs to display internal UW notes, not broker notes
        HOW: Get latest internalInitialUW valuation, then get notes field
        """
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'notes', None) if v else None

    def get_is_dropped(self, obj):
        """Return True when acquisition status indicates a dropped asset."""
        status = getattr(obj, 'acq_status', None)
        return status == getattr(SellerRawData, 'AcquisitionStatus', None).DROP if status else False


class SellerOptionSerializer(serializers.ModelSerializer):
    """Serializer for seller dropdown options."""
    
    class Meta:
        model = Seller
        fields = ['id', 'name']


class TradeOptionSerializer(serializers.ModelSerializer):
    """Serializer for trade dropdown options."""
    
    class Meta:
        model = Trade
        fields = ['id', 'trade_name']


class SellerRawDataDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single SellerRawData record.
    Used by loan-level detail views and modals.
    
    IMPORTANT: SellerRawData uses asset_hub as primary_key=True (OneToOne with AssetIdHub).
    This means there is NO 'id' field - we must use SerializerMethodField to expose asset_hub_id as 'id'.
    """
    
    # WHAT: Expose asset_hub_id as 'id' for frontend consistency
    # WHY: SellerRawData uses asset_hub OneToOneField as primary key, so Django doesn't create 'id' field
    id = serializers.SerializerMethodField()
    
    # Include hub-level commercial flag for loan-level UI
    is_commercial = serializers.SerializerMethodField()

    class Meta:
        model = SellerRawData
        fields = [
            # Identity
            'id', 'sellertape_id', 'asset_status', 'as_of_date', 'is_commercial',
            'acq_status',
            # Address / property
            'street_address', 'city', 'state', 'zip', 'property_type', 'product_type', 'occupancy', 
            'year_built', 'sq_ft', 'lot_size', 'beds', 'baths',
            # Borrower info
            'borrower1_last', 'borrower1_first', 'borrower2_last', 'borrower2_first',
            # Financial core
            'current_balance', 'deferred_balance', 'interest_rate', 'next_due_date', 
            'last_paid_date', 'first_pay_date', 'origination_date', 'original_balance',
            'original_term', 'original_rate', 'original_maturity_date', 'default_rate',
            'months_dlq', 'current_maturity_date', 'current_term',
            # Balances and fees
            'accrued_note_interest', 'accrued_default_interest', 'escrow_balance',
            'escrow_advance', 'recoverable_corp_advance', 'late_fees', 'other_fees',
            'suspense_balance', 'total_debt',
            # Valuations
            'origination_value', 'origination_arv', 'origination_value_date',
            'seller_value_date', 'seller_arv_value', 'seller_asis_value',
            'additional_asis_value', 'additional_arv_value', 'additional_value_date',
            # Flags and legal
            'fc_flag', 'fc_first_legal_date', 'fc_referred_date', 'fc_judgement_date',
            'fc_scheduled_sale_date', 'fc_sale_date', 'fc_starting',
            'bk_flag', 'bk_chapter',
            'mod_flag', 'mod_date', 'mod_maturity_date', 'mod_term', 'mod_rate', 'mod_initial_balance',
            # Timestamps
            'created_at', 'updated_at',
        ]

    def get_id(self, obj):
        """
        Return the Asset Hub ID (SellerRawData PK).
        
        SellerRawData model uses asset_hub OneToOneField as primary_key=True,
        so Django doesn't create a standard 'id' field. Always use asset_hub_id.
        """
        return getattr(obj, 'asset_hub_id', None) or getattr(obj, 'pk', None)
    
    def get_is_commercial(self, obj):
        """Return boolean commercial tag from AssetIdHub for detail view."""
        try:
            hub = getattr(obj, 'asset_hub', None)
            return bool(getattr(hub, 'is_commercial_flag', False)) if hub is not None else False
        except Exception:
            return False
    
    def get_msa(self, obj):
        """Return friendly MSA display name (fall back to code)."""
        try:
            name = getattr(obj, 'msa_name', None)
            code = getattr(obj, 'msa_code', None)
            if name:
                return name
            if code:
                return code
            return None
        except Exception:
            return None
    
    def get_county(self, obj):
        """Return county derived from ZIP reference lookup (if available)."""
        try:
            county_name = getattr(obj, 'msa_county', None)
            return county_name or None
        except Exception:
            return None


class SellerRawDataFieldsSerializer(serializers.Serializer):
    """
    Serializer for field metadata used by AG Grid dynamic column generation.
    Returns the field names available in SellerRawDataRowSerializer.
    """
    fields = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )
    
    @classmethod
    def get_fields_list(cls):
        """Return list of field names from SellerRawDataRowSerializer."""
        serializer = SellerRawDataRowSerializer()
        return list(serializer.fields.keys())
