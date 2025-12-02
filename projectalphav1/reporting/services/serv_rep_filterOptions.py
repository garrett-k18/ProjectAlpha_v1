"""
Service: Filter Options

WHAT: Business logic for fetching filter dropdown options
WHY: Populate sidebar filter dropdowns (Trades, Statuses, Partnerships)
WHERE: Imported by view_rep_filters.py
HOW: Query Trade + FundLegalEntity models for dropdown data

FILE NAMING: serv_rep_filterOptions.py
- serv_ = Services folder
- _rep_ = Reporting module
- filterOptions = Descriptive name

ARCHITECTURE:
View → This Service → Model

Docs reviewed:
- Django QuerySet: https://docs.djangoproject.com/en/stable/ref/models/querysets/
- Django values(): https://docs.djangoproject.com/en/stable/ref/models/querysets/#values
- Django aggregation docs for Count annotations:
  https://docs.djangoproject.com/en/stable/topics/db/aggregation/
"""

from typing import List, Dict, Any, Optional
from django.db.models import Count, Q, F
from acq_module.models.model_acq_seller import Trade
from core.models import FundLegalEntity


def get_trade_options_data(partnership_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
    """
    WHAT: Get all trades for sidebar filter dropdown (optionally filtered by partnership)
    WHY: Populate trade multi-select filter
    HOW: Query Trade model with Seller details, filter by partnership if provided
    
    ARGS:
        partnership_ids: Optional list of FundLegalEntity IDs to filter trades by
    
    RETURNS: List of trade option dicts
        [
            {
                'id': 1,
                'trade_name': 'NPL Portfolio 2024-Q1',
                'seller_name': 'ABC Bank',
                'status': 'DD',
                'asset_count': 245,  # Optional: show count in dropdown
            },
            ...
        ]
    
    USAGE in view:
        trade_options = get_trade_options_data()
        # OR filter by partnership:
        trade_options = get_trade_options_data(partnership_ids=[1, 2])
        return Response(trade_options)
    """
    from acq_module.models.model_acq_seller import SellerRawData
    
    # WHAT: Query all trades with seller details
    # WHY: Show trade name + seller name in dropdown for context
    # HOW: Use select_related to avoid N+1 queries
    trades = (
        Trade.objects
        .select_related('seller')  # WHAT: Join with Seller to get seller name
        # WHAT: Filter to only BOARDED trades
        # WHY: Reporting module only shows boarded loans, not trades in due diligence
        # HOW: Filter by status = 'BOARD'
        .filter(status='BOARD')
    )
    
    # WHAT: Filter trades by partnership if provided
    # WHY: When user selects a partnership, only show trades that have assets in that partnership
    # HOW: Find trades that have at least one asset linked to the selected partnership(s)
    if partnership_ids and len(partnership_ids) > 0:
        # WHAT: Get trade IDs that have assets in the selected partnership(s)
        # WHY: Filter trades based on AssetDetails.fund_legal_entity relationship
        # HOW: Query SellerRawData → asset_hub → details → fund_legal_entity
        trade_ids_with_partnership = (
            SellerRawData.objects
            .filter(
                trade__status='BOARD',
                asset_hub__details__fund_legal_entity_id__in=partnership_ids
            )
            .values_list('trade_id', flat=True)
            .distinct()
        )
        trades = trades.filter(id__in=trade_ids_with_partnership)
    
    trades = trades.annotate(
        # WHAT: Count of assets in this trade
        # WHY: Show user how many assets per trade in dropdown
        # HOW: Count SellerRawData rows via reverse FK relationship
        # NOTE: related_name is 'seller_raw_data' on SellerRawData.trade FK
        asset_count=Count('seller_raw_data'),
        # WHAT: Get seller name via FK annotation
        # WHY: Include seller name in results
        # HOW: Use F() expression to reference related field
        seller_name=F('seller__name'),
    ).values(
        'id',
        'trade_name',
        'seller_name',  # WHAT: Use annotated field
        'status',
        'asset_count',
    ).order_by('trade_name')  # WHAT: Alphabetical order for dropdown
    
    # WHAT: Convert QuerySet to list of dicts
    # WHY: Ready for serialization
    return list(trades)


def get_status_options_data() -> List[Dict[str, Any]]:
    """
    WHAT: Get all unique AM outcome tracks for filter dropdown
    WHY: Populate track status multi-select filter showing which outcome track assets are on
    HOW: Query AssetIdHub for assets with each outcome type (REO, FC, DIL, Short Sale, Modification, Note Sale)
    
    RETURNS: List of track option dicts
        [
            {
                'value': 'reo',
                'label': 'REO',
                'count': 25,  # Number of assets on this track
            },
            ...
        ]
    
    USAGE in view:
        track_options = get_status_options_data()
        return Response(track_options)
    """
    # WHAT: Import AssetIdHub to query outcome tracks
    # WHY: Need to check which assets have which outcome records
    from core.models.model_co_assetIdHub import AssetIdHub
    from acq_module.models.model_acq_seller import SellerRawData
    
    # WHAT: Get all boarded assets
    # WHY: Only show tracks for boarded assets in reporting
    boarded_assets = (
        SellerRawData.objects
        .filter(trade__status='BOARD')
        .values_list('asset_hub_id', flat=True)
    )
    
    # WHAT: Define track mappings with their related names and labels
    # WHY: Map from related_name on AssetIdHub to friendly display labels
    # HOW: Dictionary with value, label, and related_name for query
    track_definitions = [
        {'value': 'reo', 'label': 'REO', 'related_name': 'reo_data'},
        {'value': 'fc', 'label': 'Foreclosure', 'related_name': 'fc_sale'},
        {'value': 'dil', 'label': 'DIL', 'related_name': 'dil'},
        {'value': 'short_sale', 'label': 'Short Sale', 'related_name': 'short_sale'},
        {'value': 'modification', 'label': 'Modification', 'related_name': 'modification'},
        {'value': 'note_sale', 'label': 'Note Sale', 'related_name': 'note_sale'},
    ]
    
    # WHAT: Count assets for each track
    # WHY: Show user how many assets are on each track
    # HOW: Query AssetIdHub with filter for each related outcome model
    results = []
    for track in track_definitions:
        # WHAT: Count assets that have this outcome record
        # WHY: Each outcome is a 1:1 relationship, so existence means asset is on that track
        # HOW: Use __isnull=False to check if related record exists
        count = (
            AssetIdHub.objects
            .filter(id__in=boarded_assets)
            .filter(**{f"{track['related_name']}__isnull": False})
            .count()
        )
        
        # WHAT: Only include tracks that have at least one asset
        # WHY: Keep dropdown clean and relevant
        if count > 0:
            results.append({
                'value': track['value'],
                'label': track['label'],
                'count': count,
            })
    
    return results


def get_task_status_options_data(track: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    WHAT: Get all active task types for filter dropdown (optionally filtered by track)
    WHY: Populate task status sub-filter showing active tasks within outcome tracks
    HOW: Query task models for each outcome track and return unique task types
    
    ARGS:
        track: Optional track value to filter tasks by (reo, fc, dil, short_sale, modification, note_sale)
    
    RETURNS: List of task status option dicts
        [
            {
                'value': 'eviction',
                'label': 'Eviction',
                'track': 'reo',
                'count': 10,  # Number of assets with this task
            },
            ...
        ]
    
    USAGE in view:
        task_options = get_task_status_options_data()
        # OR filter by specific track:
        reo_tasks = get_task_status_options_data(track='reo')
        return Response(task_options)
    """
    # WHAT: Import task models from AM module
    # WHY: Need to query each task type table
    from am_module.models.am_data import REOtask, FCTask, DILTask, ShortSaleTask, ModificationTask, NoteSaleTask
    from acq_module.models.model_acq_seller import SellerRawData
    
    # WHAT: Get all boarded asset IDs
    # WHY: Only show tasks for boarded assets in reporting
    boarded_asset_ids = list(
        SellerRawData.objects
        .filter(trade__status='BOARD')
        .values_list('asset_hub_id', flat=True)
    )
    
    # WHAT: Define task model mappings with their track associations
    # WHY: Map each task model to its track and extract task types
    # HOW: Dictionary with track value, task model, and label prefix
    task_model_map = [
        {'track': 'reo', 'model': REOtask, 'tasks_related': 'reo_tasks'},
        {'track': 'fc', 'model': FCTask, 'tasks_related': 'fc_tasks'},
        {'track': 'dil', 'model': DILTask, 'tasks_related': 'dil_tasks'},
        {'track': 'short_sale', 'model': ShortSaleTask, 'tasks_related': 'short_sale_tasks'},
        {'track': 'modification', 'model': ModificationTask, 'tasks_related': 'modification_tasks'},
        {'track': 'note_sale', 'model': NoteSaleTask, 'tasks_related': 'note_sale_tasks'},
    ]
    
    # WHAT: Filter task models if track is specified
    # WHY: Allow filtering by specific outcome track
    if track:
        task_model_map = [tm for tm in task_model_map if tm['track'] == track]
    
    results = []
    
    # WHAT: Iterate through each task model and extract task types
    # WHY: Get unique task types with counts across all tracks
    for task_info in task_model_map:
        task_model = task_info['model']
        track_value = task_info['track']
        
        # WHAT: Query for unique task types in this model
        # WHY: Get all active task types with counts
        # HOW: Use values() + annotate() for GROUP BY on task_type
        task_types = (
            task_model.objects
            .filter(asset_hub_id__in=boarded_asset_ids)
            .values('task_type')
            .annotate(count=Count('id'))
            .order_by('task_type')
        )
        
        # WHAT: Get TaskType choices from the model
        # WHY: Use the model's own label mappings for display
        task_type_choices = dict(task_model.TaskType.choices)
        
        # WHAT: Format each task type as a result
        # WHY: Provide value, label, track, and count for each task
        for task_data in task_types:
            task_type = task_data['task_type']
            count = task_data['count']
            
            # WHAT: Get friendly label from TaskType choices
            # WHY: Display human-readable labels in dropdown
            label = task_type_choices.get(task_type, task_type.replace('_', ' ').title())
            
            results.append({
                'value': task_type,
                'label': label,
                'track': track_value,
                'count': count,
            })
    
    return results


def get_partnership_options_data() -> List[Dict[str, Any]]:
    """
    WHAT: Get all FundLegalEntity records for the Partnerships filter dropdown
    WHY: Partnership filter represents fund/SPV wrappers instead of the general Entity model
    HOW: Query FundLegalEntity with fund metadata
    
    RETURNS: List of partnership option dicts
        [
            {
                'id': 1,
                'nickname': 'Alpha Fund LP',
                'entity_role': 'fund',
                'entity_role_label': 'Fund',
                'is_active': True,
                'fund_id': 42,
                'fund_name': 'Fund I - Core',
            },
            ...
        ]
    """
    partnerships = (
        FundLegalEntity.objects
        .select_related('fund')
        .order_by('nickname_name', 'id')
    )
    
    results: List[Dict[str, Any]] = []
    for partnership in partnerships:
        fund = partnership.fund
        nickname = partnership.nickname_name or (fund.name if fund else "Unnamed Partnership")
        results.append({
            'id': partnership.id,
            'nickname': nickname,
            'entity_role': partnership.entity_role,
            'entity_role_label': partnership.get_entity_role_display() if partnership.entity_role else None,
            'is_active': partnership.is_active,
            'fund_id': fund.id if fund else None,
            'fund_name': fund.name if fund else None,
        })
    
    return results

