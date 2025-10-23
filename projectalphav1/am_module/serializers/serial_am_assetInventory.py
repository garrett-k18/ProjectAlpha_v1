"""
Asset Inventory Serializers

WHAT: Serialization layer for asset inventory data
WHY: Transform enriched SellerRawData objects into JSON for frontend consumption
HOW: Pure field definitions - all business logic delegated to service layer

Docs: https://www.django-rest-framework.org/api-guide/serializers/
"""
from rest_framework import serializers
from .servicer_loan_data import ServicerLoanDataSerializer


class AssetInventoryRowSerializer(serializers.Serializer):
    """
    Flat row serializer for AG Grid and loan-level detail views.

    WHAT: Maps SellerRawData (enriched by AssetInventoryEnricher) to JSON
    WHY: Provides consistent data structure for both grid and detail endpoints
    HOW: Pure field definitions - business logic lives in am_module.services.serv_am_assetInventory

    NOTE: Objects passed to this serializer MUST be enriched first using
    AssetInventoryEnricher.enrich() to populate _computed_* attributes.

    Usage:
        from am_module.services.serv_am_assetInventory import AssetInventoryEnricher

        enricher = AssetInventoryEnricher()
        enriched_assets = [enricher.enrich(asset) for asset in queryset]
        serializer = AssetInventoryRowSerializer(enriched_assets, many=True)
        return Response(serializer.data)
    """

    # ========== Identity Fields ==========
    # CRITICAL: SellerRawData uses asset_hub as primary key (OneToOneField with primary_key=True)
    # so obj.id and obj.asset_hub_id don't exist. Must use obj.pk or SerializerMethodField.
    id = serializers.SerializerMethodField(
        help_text='Asset Hub ID (SellerRawData.pk)'
    )
    asset_hub_id = serializers.SerializerMethodField(
        help_text='Asset Hub ID (same as id, exposed explicitly for frontend validation)'
    )

    def get_id(self, obj):
        """
        Return the primary key value.
        
        WHAT: Access SellerRawData primary key
        WHY: Model uses asset_hub as PK (not standard 'id' field)
        HOW: Use obj.pk which works regardless of PK field name
        """
        return obj.pk

    def get_asset_hub_id(self, obj):
        """
        Return the asset hub ID for frontend validation.
        
        WHAT: Provide asset hub ID explicitly
        WHY: Frontend expects this field name for consistency
        HOW: Same as get_id since asset_hub IS the primary key
        """
        return obj.pk
    asset_id = serializers.CharField(
        source='_computed_asset_id',
        read_only=True,
        allow_null=True,
        help_text='Display ID (sellertape_id or pk fallback)'
    )
    servicer_id = serializers.CharField(
        source='asset_hub.servicer_id',
        read_only=True,
        allow_null=True,
        help_text='External servicer ID from AssetIdHub'
    )

    # ========== Status Fields ==========
    asset_status = serializers.CharField(
        allow_null=True,
        help_text='Legacy asset status field'
    )
    lifecycle_status = serializers.CharField(
        source='_computed_lifecycle_status',
        read_only=True,
        allow_null=True,
        help_text='Canonical lifecycle status from AssetIdHub'
    )
    delinquency_status = serializers.CharField(
        source='_computed_delinquency_status',
        read_only=True,
        allow_null=True,
        help_text='Cached delinquency bucket from AMMetrics'
    )

    # ========== Property Address Fields ==========
    street_address = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    property_type = serializers.CharField(allow_null=True)
    occupancy = serializers.CharField(allow_null=True)

    # ========== Seller/Trade Fields ==========
    seller_name = serializers.CharField(
        source='_computed_seller_name',
        read_only=True,
        allow_null=True,
        help_text='Seller display name (from annotation or FK)'
    )
    trade_name = serializers.CharField(
        source='_computed_trade_name',
        read_only=True,
        allow_null=True,
        help_text='Trade display name (from annotation or FK)'
    )

    # ========== Blended Outcome Model Fields ==========
    # All these fields come directly from asset_hub.blended_outcome_model via DRF source paths
    acq_cost = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        allow_null=True,
        source='asset_hub.blended_outcome_model.acq_cost'
    )
    purchase_cost = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        allow_null=True,
        source='asset_hub.blended_outcome_model.purchase_price',
        help_text='Purchase price - frontend AssetSummary expects this field'
    )
    purchase_date = serializers.DateField(
        required=False,
        allow_null=True,
        source='asset_hub.blended_outcome_model.purchase_date',
        help_text='Purchase date - frontend AssetSummary expects this field'
    )
    total_expenses = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        allow_null=True,
        source='asset_hub.blended_outcome_model.expected_total_expenses'
    )
    total_hold = serializers.IntegerField(
        required=False,
        allow_null=True,
        source='asset_hub.blended_outcome_model.expected_total_hold'
    )
    exit_date = serializers.DateField(
        required=False,
        allow_null=True,
        source='asset_hub.blended_outcome_model.expected_exit_date'
    )
    expected_gross_proceeds = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        allow_null=True,
        source='asset_hub.blended_outcome_model.expected_gross_proceeds'
    )
    expected_net_proceeds = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        allow_null=True,
        source='asset_hub.blended_outcome_model.expected_net_proceeds'
    )
    expected_pl = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        allow_null=True,
        source='asset_hub.blended_outcome_model.expected_pl'
    )
    expected_cf = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        allow_null=True,
        source='asset_hub.blended_outcome_model.expected_cf'
    )
    expected_irr = serializers.DecimalField(
        max_digits=5,
        decimal_places=4,
        required=False,
        allow_null=True,
        source='asset_hub.blended_outcome_model.expected_irr'
    )
    expected_moic = serializers.DecimalField(
        max_digits=6,
        decimal_places=5,
        required=False,
        allow_null=True,
        source='asset_hub.blended_outcome_model.expected_moic'
    )
    expected_npv = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        allow_null=True,
        source='asset_hub.blended_outcome_model.expected_npv'
    )

    # ========== Servicer Loan Data (Nested) ==========
    servicer_loan_data = serializers.SerializerMethodField(
        help_text='Latest ServicerLoanData record (nested serialized object)'
    )

    def get_servicer_loan_data(self, obj):
        """
        Serialize the enriched servicer loan data.

        WHAT: Convert ServicerLoanData object (from enricher) to JSON
        WHY: Frontend expects nested servicer data with all loan details
        HOW: Use ServicerLoanDataSerializer on pre-fetched object
        """
        servicer_data = getattr(obj, '_computed_servicer_loan_data', None)
        if servicer_data:
            return ServicerLoanDataSerializer(servicer_data).data
        return None

    # ========== Valuation Fields (Latest by Source) ==========
    # Internal Initial UW
    internal_initial_uw_asis_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        source='_computed_internal_initial_uw_asis_value',
        read_only=True,
        allow_null=True,
        help_text='Latest as-is value from Internal Initial UW valuation'
    )
    internal_initial_uw_arv_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        source='_computed_internal_initial_uw_arv_value',
        read_only=True,
        allow_null=True,
        help_text='Latest ARV from Internal Initial UW valuation'
    )

    # Seller
    seller_asis_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        source='_computed_seller_asis_value',
        read_only=True,
        allow_null=True,
        help_text='Latest as-is value from Seller valuation'
    )
    seller_arv_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        source='_computed_seller_arv_value',
        read_only=True,
        allow_null=True,
        help_text='Latest ARV from Seller valuation'
    )

    # Latest UW Value (Prioritized)
    latest_uw_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        source='_computed_latest_uw_value',
        read_only=True,
        allow_null=True,
        help_text='Most recent as-is valuation (priority: Internal Initial UW > Seller)'
    )


class AssetInventoryColumnsSerializer(serializers.Serializer):
    """
    Optional endpoint to drive dynamic column definitions from server.

    WHAT: Metadata serializer for AG Grid column configuration
    WHY: Allows server to control grid column structure
    HOW: Simple field-to-header mapping for frontend consumption
    """
    field = serializers.CharField()
    headerName = serializers.CharField()
    type = serializers.CharField(required=False)
    width = serializers.IntegerField(required=False)
