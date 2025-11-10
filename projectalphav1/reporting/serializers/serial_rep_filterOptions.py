"""
Serializer: Filter Options

WHAT: Field definitions for filter dropdown options
WHY: Define API contract for sidebar filter endpoints
WHERE: Imported by view_rep_filters.py
HOW: Define fields for each filter type (Trade, Status, Fund, Entity)

FILE NAMING: serial_rep_filterOptions.py
- serial_ = Serializers folder
- _rep_ = Reporting module
- filterOptions = Descriptive name

RULE: All field definitions live in serializers.

Docs reviewed:
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
"""

from rest_framework import serializers


class TradeOptionSerializer(serializers.Serializer):
    """
    WHAT: Field definitions for trade filter dropdown options
    WHY: Define what trade data the sidebar receives
    WHERE: Used by /api/reporting/trades/ endpoint
    
    FIELDS:
    - id: Trade ID (for filtering)
    - trade_name: Trade name (display in dropdown)
    - seller_name: Seller name (context for user)
    - status: Trade status (DD, AWARDED, etc.)
    - asset_count: Number of assets in trade (optional, show in dropdown)
    """
    # WHAT: Unique trade identifier
    # WHY: Used in filter query params (trade_ids=1,2,3)
    id = serializers.IntegerField()
    
    # WHAT: Trade name (from Trade model)
    # WHY: Primary display text in dropdown
    # SOURCE: Trade.trade_name
    trade_name = serializers.CharField()
    
    # WHAT: Seller name (from Seller model via Trade FK)
    # WHY: Context for user - "NPL Portfolio (ABC Bank)"
    # SOURCE: Trade.seller.name
    seller_name = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )
    
    # WHAT: Trade status
    # WHY: Show status badge in dropdown (optional)
    # SOURCE: Trade.status
    status = serializers.CharField(required=False)
    
    # WHAT: Asset count
    # WHY: Show how many assets in this trade
    # SOURCE: COUNT(SellerRawData) for this trade
    asset_count = serializers.IntegerField(required=False)


class StatusOptionSerializer(serializers.Serializer):
    """
    WHAT: Field definitions for status filter dropdown options
    WHY: Define what status data the sidebar receives
    WHERE: Used by /api/reporting/statuses/ endpoint
    
    FIELDS:
    - value: Status code (DD, AWARDED, etc.)
    - label: Display label (Due Diligence, Awarded, etc.)
    - count: Number of trades with this status
    """
    # WHAT: Status code
    # WHY: Used in filter query params (statuses=DD,AWARDED)
    # SOURCE: Trade.status
    value = serializers.CharField()
    
    # WHAT: Friendly display label
    # WHY: Show "Due Diligence" not "DD" in dropdown
    # SOURCE: Mapped from Trade.Status.choices
    label = serializers.CharField()
    
    # WHAT: Count of trades with this status
    # WHY: Show user distribution (e.g., "DD (15 trades)")
    # SOURCE: COUNT(Trade) GROUP BY status
    count = serializers.IntegerField(required=False)


class FundOptionSerializer(serializers.Serializer):
    """
    WHAT: Field definitions for fund filter dropdown options
    WHY: Define what fund data the sidebar receives
    WHERE: Used by /api/reporting/funds/ endpoint
    
    TODO: Update once Fund model is created
    
    FIELDS:
    - id: Fund ID
    - name: Fund name
    - code: Fund code (short identifier)
    """
    # WHAT: Unique fund identifier
    # WHY: Used in filter query params (fund_id=5)
    id = serializers.IntegerField()
    
    # WHAT: Fund name
    # WHY: Display in dropdown
    # SOURCE: Fund.name (TODO: once Fund model exists)
    name = serializers.CharField()
    
    # WHAT: Fund code (short identifier like "FUND-I")
    # WHY: Compact display in UI
    # SOURCE: Fund.code (TODO: once Fund model exists)
    code = serializers.CharField(required=False, allow_blank=True)


class EntityOptionSerializer(serializers.Serializer):
    """
    WHAT: Field definitions for entity filter dropdown options
    WHY: Define what entity data the sidebar receives
    WHERE: Used by /api/reporting/entities/ endpoint
    
    TODO: Update once Entity model is created
    
    FIELDS:
    - id: Entity ID
    - name: Entity name
    - entity_type: Type (LLC, LP, Corporation, etc.)
    """
    # WHAT: Unique entity identifier
    # WHY: Used in filter query params (entity_id=2)
    id = serializers.IntegerField()
    
    # WHAT: Entity legal name
    # WHY: Display in dropdown
    # SOURCE: Entity.name (TODO: once Entity model exists)
    name = serializers.CharField()
    
    # WHAT: Entity type (LLC, LP, Corporation, etc.)
    # WHY: Show entity structure in dropdown
    # SOURCE: Entity.entity_type (TODO: once Entity model exists)
    entity_type = serializers.CharField(required=False, allow_blank=True)

