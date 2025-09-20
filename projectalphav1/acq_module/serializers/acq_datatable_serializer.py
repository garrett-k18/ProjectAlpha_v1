"""
DRF Serializers for Acquisitions Module data structures.

This module defines serializers for:
- SellerRawData AG Grid rows with unified valuation integration
- Seller dropdown options
- Trade dropdown options
- Field metadata for dynamic column generation

Follows the same pattern as am_module.serializers.asset_inventory for consistency.

Docs reviewed:
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- DRF SerializerMethodField: https://www.django-rest-framework.org/api-guide/fields/#serializermethodfield
"""
from rest_framework import serializers
from ..models.seller import Seller, Trade, SellerRawData
from core.models.valuations import Valuation


class SellerRawDataRowSerializer(serializers.Serializer):
    """
    Flat row shape tailored for AG Grid. We keep this serializer
    detached from a specific model to freely compose from multiple sources.
    
    This serializer handles SellerRawData with unified valuation integration,
    pulling broker and internal valuation data from the core.Valuation model.
    """
    # Core SellerRawData fields
    id = serializers.IntegerField(read_only=True)
    sellertape_id = serializers.IntegerField(read_only=True)
    asset_status = serializers.CharField(allow_null=True)
    
    # Related model fields accessed via foreign keys
    as_of_date = serializers.DateField(allow_null=True)
    
    # Property details
    street_address = serializers.CharField(allow_null=True)
    city = serializers.CharField(allow_null=True)
    state = serializers.CharField(allow_null=True)
    zip = serializers.CharField(allow_null=True, source='zip')  # Map zip field from model
    property_type = serializers.CharField(allow_null=True)
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
    borrower2_last = serializers.CharField(allow_null=True, allow_blank=True)
    borrower2_first = serializers.CharField(allow_null=True, allow_blank=True)

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
        if hub is None:
            return None
        return (
            Valuation.objects
            .filter(asset_hub=hub, source=source)
            .order_by('-value_date', '-created_at')
            .first()
        )
    
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
    
    class Meta:
        model = SellerRawData
        fields = [
            # Identity
            'id', 'sellertape_id', 'asset_status', 'as_of_date',
            # Address / property
            'street_address', 'city', 'state', 'zip', 'property_type', 'occupancy', 
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
