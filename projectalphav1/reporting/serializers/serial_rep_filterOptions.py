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
    WHAT: Field definitions for AM outcome track filter dropdown options
    WHY: Define what track data the sidebar receives (REO, FC, DIL, Short Sale, Modification, Note Sale)
    WHERE: Used by /api/reporting/statuses/ endpoint
    
    FIELDS:
    - value: Track code (reo, fc, dil, short_sale, modification, note_sale)
    - label: Display label (REO, Foreclosure, DIL, etc.)
    - count: Number of assets on this track
    """
    # WHAT: Track code
    # WHY: Used in filter query params (tracks=reo,fc)
    # SOURCE: AssetIdHub outcome relationships
    value = serializers.CharField()
    
    # WHAT: Friendly display label
    # WHY: Show "REO" or "Foreclosure" in dropdown
    # SOURCE: Mapped from outcome model definitions
    label = serializers.CharField()
    
    # WHAT: Count of assets on this track
    # WHY: Show user distribution (e.g., "REO (25 assets)")
    # SOURCE: COUNT(AssetIdHub) with outcome relationship
    count = serializers.IntegerField(required=False)


class TaskStatusOptionSerializer(serializers.Serializer):
    """
    WHAT: Field definitions for task status filter dropdown options
    WHY: Define what task data the sidebar receives (active tasks within outcome tracks)
    WHERE: Used by /api/reporting/task-statuses/ endpoint
    
    FIELDS:
    - value: Task type code (eviction, trashout, nod_noi, etc.)
    - label: Display label (Eviction, Trashout, NOD/NOI, etc.)
    - track: Track this task belongs to (reo, fc, dil, short_sale, modification, note_sale)
    - count: Number of assets with this task
    """
    # WHAT: Task type code
    # WHY: Used in filter query params (tasks=eviction,trashout)
    # SOURCE: Task model task_type field
    value = serializers.CharField()
    
    # WHAT: Friendly display label
    # WHY: Show "Eviction" not "eviction" in dropdown
    # SOURCE: Mapped from TaskType.choices in each task model
    label = serializers.CharField()
    
    # WHAT: Track this task belongs to
    # WHY: Allow grouping and filtering by outcome track
    # SOURCE: Task model association (REOtask->reo, FCTask->fc, etc.)
    track = serializers.CharField()
    
    # WHAT: Count of assets with this task
    # WHY: Show user distribution (e.g., "Eviction (10 assets)")
    # SOURCE: COUNT(Task) GROUP BY task_type
    count = serializers.IntegerField(required=False)


class EntityOptionSerializer(serializers.Serializer):
    """
    WHAT: Field definitions for entity filter dropdown options
    WHY: Define what entity data the sidebar receives (now primary fund/ownership filter)
    WHERE: Used by /api/reporting/entities/ endpoint
    
    FIELDS:
    - id: Entity ID
    - name: Legal entity name
    - entity_type: Raw DB choice (fund, spv, llc, etc.)
    - entity_type_label: Human-readable label ("Fund", "SPV", etc.)
    - is_active: Whether entity is active
    - fund_id/fund_name/fund_status/fund_status_label: Optional Fund metadata if linked
    - owned_asset_count: Number of active assets owned directly
    - owned_entity_count: Number of active downstream entities (SPVs, etc.)
    """
    # WHAT: Unique entity identifier
    # WHY: Used in filter query params (entity_id=2)
    id = serializers.IntegerField()
    
    # WHAT: Entity legal name
    # WHY: Display in dropdown
    # SOURCE: Entity.name
    name = serializers.CharField()
    
    # WHAT: Entity type (LLC, LP, Corporation, etc.)
    # WHY: Show entity structure in dropdown
    # SOURCE: Entity.entity_type
    entity_type = serializers.CharField()
    
    # WHAT: Human-readable label for entity type
    # WHY: Show "Fund" instead of "fund"
    entity_type_label = serializers.CharField()
    
    # WHAT: Active flag
    # WHY: Surface entity availability in UI
    is_active = serializers.BooleanField()
    
    # WHAT: Linked fund metadata (optional)
    fund_id = serializers.IntegerField(required=False, allow_null=True)
    fund_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fund_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fund_status_label = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # WHAT: Ownership counts
    owned_asset_count = serializers.IntegerField(required=False)
    owned_entity_count = serializers.IntegerField(required=False)


class FundOptionSerializer(serializers.Serializer):
    """
    WHAT: Field definitions for fund filter dropdown options
    WHY: Legacy filter contract; still imported by views even while we migrate to entity-only filters
    WHERE: Used by /api/reporting/funds/ endpoint (kept for backward compatibility)

    FIELDS:
    - id: Fund ID
    - fund_name: Name displayed to the user
    - fund_type / fund_status: Raw value codes from Fund model
    - fund_type_label / fund_status_label: Human readable versions
    - entity_id / entity_name: Optional link to new Entity model
    - membership_count: Number of FundMembership rows (GPs + LPs)
    """
    id = serializers.IntegerField()
    fund_name = serializers.CharField()
    fund_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fund_type_label = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fund_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fund_status_label = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    entity_id = serializers.IntegerField(required=False, allow_null=True)
    entity_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    membership_count = serializers.IntegerField(required=False)

