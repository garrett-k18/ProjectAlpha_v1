"""
Service: Filter Options

WHAT: Business logic for fetching filter dropdown options
WHY: Populate sidebar filter dropdowns (Trades, Statuses, Funds, Entities)
WHERE: Imported by view_rep_filters.py
HOW: Query Trade, Fund, Entity models for dropdown data

FILE NAMING: serv_rep_filterOptions.py
- serv_ = Services folder
- _rep_ = Reporting module
- filterOptions = Descriptive name

ARCHITECTURE:
View → This Service → Model

Docs reviewed:
- Django QuerySet: https://docs.djangoproject.com/en/stable/ref/models/querysets/
- Django values(): https://docs.djangoproject.com/en/stable/ref/models/querysets/#values
"""

from typing import List, Dict, Any
from django.db.models import Count, Q, F
from acq_module.models.model_acq_seller import Trade, Seller


def get_trade_options_data() -> List[Dict[str, Any]]:
    """
    WHAT: Get all trades for sidebar filter dropdown
    WHY: Populate trade multi-select filter
    HOW: Query Trade model with Seller details
    
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
        return Response(trade_options)
    """
    # WHAT: Query all trades with seller details
    # WHY: Show trade name + seller name in dropdown for context
    # HOW: Use select_related to avoid N+1 queries
    trades = (
        Trade.objects
        .select_related('seller')  # WHAT: Join with Seller to get seller name
        .annotate(
            # WHAT: Count of assets in this trade
            # WHY: Show user how many assets per trade in dropdown
            # HOW: Count SellerRawData rows via reverse FK relationship
            # NOTE: related_name is 'seller_raw_data' on SellerRawData.trade FK
            asset_count=Count('seller_raw_data'),
            # WHAT: Get seller name via FK annotation
            # WHY: Include seller name in results
            # HOW: Use F() expression to reference related field
            seller_name=F('seller__name'),
        )
        .values(
            'id',
            'trade_name',
            'seller_name',  # WHAT: Use annotated field
            'status',
            'asset_count',
        )
        .order_by('trade_name')  # WHAT: Alphabetical order for dropdown
    )
    
    # WHAT: Convert QuerySet to list of dicts
    # WHY: Ready for serialization
    return list(trades)


def get_status_options_data() -> List[Dict[str, Any]]:
    """
    WHAT: Get all unique trade statuses for filter dropdown
    WHY: Populate status multi-select filter
    HOW: Query distinct status values from Trade model
    
    RETURNS: List of status option dicts
        [
            {
                'value': 'DD',
                'label': 'Due Diligence',
                'count': 15,  # Number of trades with this status
            },
            ...
        ]
    
    USAGE in view:
        status_options = get_status_options_data()
        return Response(status_options)
    """
    # WHAT: Get unique statuses with counts
    # WHY: Show user how many trades per status
    # HOW: Use values() + annotate() for GROUP BY
    statuses = (
        Trade.objects
        .values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )
    
    # WHAT: Map status codes to friendly display labels
    # WHY: Show "Due Diligence" not "DD" in dropdown
    # HOW: Dictionary mapping from Trade.Status choices
    status_labels = {
        'DD': 'Due Diligence',
        'AWARDED': 'Awarded',
        'PASS': 'Passed',
        'BOARD': 'Boarded',
        'INDICATIVE': 'Indicative',
        'CLOSED': 'Closed',
    }
    
    # WHAT: Format results
    # WHY: Ready for serialization
    results = [
        {
            'value': status['status'],
            'label': status_labels.get(status['status'], status['status']),
            'count': status['count'],
        }
        for status in statuses
        if status['status']  # WHAT: Filter out null statuses
    ]
    
    return results


def get_fund_options_data() -> List[Dict[str, Any]]:
    """
    WHAT: Get all funds for filter dropdown
    WHY: Populate fund filter
    HOW: Query Fund model (when available)
    
    RETURNS: List of fund option dicts
        [
            {
                'id': 1,
                'name': 'Fund I - Core Real Estate',
                'code': 'FUND-I',
            },
            ...
        ]
    
    TODO: Implement once Fund model is created and FK added to Trade or AssetHub
    
    USAGE in view:
        fund_options = get_fund_options_data()
        return Response(fund_options)
    """
    # TODO: Replace with actual Fund model query
    # from core.models import Fund
    # funds = (
    #     Fund.objects
    #     .values('id', 'name', 'code')
    #     .order_by('name')
    # )
    # return list(funds)
    
    # WHAT: Placeholder data for testing
    # WHY: Allow frontend development while Fund model is being built
    # TODO: Remove once Fund model exists
    return [
        {'id': 1, 'name': 'Fund I - Core Real Estate', 'code': 'FUND-I'},
        {'id': 2, 'name': 'Fund II - Opportunistic', 'code': 'FUND-II'},
        {'id': 3, 'name': 'Fund III - Value-Add', 'code': 'FUND-III'},
    ]


def get_entity_options_data() -> List[Dict[str, Any]]:
    """
    WHAT: Get all legal entities for filter dropdown
    WHY: Populate entity filter
    HOW: Query Entity model (when available)
    
    RETURNS: List of entity option dicts
        [
            {
                'id': 1,
                'name': 'Alpha Capital LLC',
                'entity_type': 'LLC',
            },
            ...
        ]
    
    TODO: Implement once Entity model is created and FK added to Trade or AssetHub
    
    USAGE in view:
        entity_options = get_entity_options_data()
        return Response(entity_options)
    """
    # TODO: Replace with actual Entity model query
    # from core.models import Entity
    # entities = (
    #     Entity.objects
    #     .values('id', 'name', 'entity_type')
    #     .order_by('name')
    # )
    # return list(entities)
    
    # WHAT: Placeholder data for testing
    # WHY: Allow frontend development while Entity model is being built
    # TODO: Remove once Entity model exists
    return [
        {'id': 1, 'name': 'Alpha Capital LLC', 'entity_type': 'LLC'},
        {'id': 2, 'name': 'Beta Properties LP', 'entity_type': 'LP'},
        {'id': 3, 'name': 'Gamma Investments Corp', 'entity_type': 'Corporation'},
    ]

