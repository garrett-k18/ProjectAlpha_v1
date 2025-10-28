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
from ..models.seller import Seller, Trade, SellerRawData
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
    sellertape_id = serializers.IntegerField(read_only=True)
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
            return bool(getattr(hub, 'is_commercial', False)) if hub is not None else False
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

    # Acquisition lifecycle status (Pass/DD/Drop/Awarded/Board) propagated to grid rows
    acq_status = serializers.CharField()
    # Drop/restore tracking
    is_dropped = serializers.SerializerMethodField()
    drop_reason = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    drop_date = serializers.DateTimeField(allow_null=True, required=False)

    # Unified valuation fields (from core.Valuation model)
    # Broker valuations (source='broker')
    broker_asis_value = serializers.SerializerMethodField()
    broker_arv_value = serializers.SerializerMethodField()
    broker_value_date = serializers.SerializerMethodField()
    
    # Internal Initial UW valuations (source='internalInitialUW')
    internal_initial_uw_asis_value = serializers.SerializerMethodField()
    internal_initial_uw_arv_value = serializers.SerializerMethodField()
    internal_initial_uw_value_date = serializers.SerializerMethodField()
    
   
    
    # Helper methods for unified valuations
    def _latest_val_by_source(self, obj, source: str):
        """Return latest Valuation row for the object's asset_hub and given source.
        
        We order by value_date then created_at to get the most recent record.
        """
        hub = getattr(obj, 'asset_hub', None)
        print(f"[Valuation Debug] SellerRawData id={getattr(obj, 'id', None)}, asset_hub={hub}")
        if hub is None:
            print(f"[Valuation Debug] No asset_hub for SellerRawData id={getattr(obj, 'id', None)}")
            return None
        
        valuations = (
            Valuation.objects
            .filter(asset_hub=hub, source=source)
            .order_by('-value_date', '-created_at')
        )
        print(f"[Valuation Debug] Hub {hub.id}, source='{source}', found {valuations.count()} valuations")
        
        result = valuations.first()
        if result:
            print(f"[Valuation Debug] Selected valuation id={result.id}, asis_value={result.asis_value}, arv_value={result.arv_value}")
        else:
            # Log all sources available for this hub to see what we actually have
            all_sources = list(Valuation.objects.filter(asset_hub=hub).values_list('source', flat=True).distinct())
            print(f"[Valuation Debug] No valuation found for source='{source}'. Available sources: {all_sources}")
        
        return result
    
    # Broker valuation getters
    def get_broker_asis_value(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        result = getattr(v, 'asis_value', None) if v else None
        print(f"[Valuation Debug] get_broker_asis_value for SellerRawData id={getattr(obj, 'id', None)}: {result}")
        return result
    
    def get_broker_arv_value(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'arv_value', None) if v else None
    
    def get_broker_value_date(self, obj):
        v = self._latest_val_by_source(obj, 'broker')
        return getattr(v, 'value_date', None) if v else None
    
    # Internal Initial UW valuation getters
    def get_internal_initial_uw_asis_value(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        result = getattr(v, 'asis_value', None) if v else None
        print(f"[Valuation Debug] get_internal_initial_uw_asis_value for SellerRawData id={getattr(obj, 'id', None)}: {result}")
        return result
    
    def get_internal_initial_uw_arv_value(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'arv_value', None) if v else None
    
    def get_internal_initial_uw_value_date(self, obj):
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'value_date', None) if v else None

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
    """
    
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

    def get_is_commercial(self, obj):
        """Return boolean commercial tag from AssetIdHub for detail view."""
        try:
            hub = getattr(obj, 'asset_hub', None)
            return bool(getattr(hub, 'is_commercial', False)) if hub is not None else False
        except Exception:
            return False


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
