"""
Service: By Trade Report

WHAT: Business logic for By Trade report (chart and grid data)
WHY: Separate aggregation logic from views/serializers
WHERE: Imported by view_rep_trade.py
HOW: Use queryBuilder + aggregations services

FILE NAMING: serv_rep_byTrade.py
- serv_ = Services folder
- _rep_ = Reporting module
- byTrade = Specific report type

ARCHITECTURE:
View → This Service → queryBuilder + aggregations → Model

Docs reviewed:
- Django QuerySet: https://docs.djangoproject.com/en/stable/ref/models/querysets/
- Django aggregation: https://docs.djangoproject.com/en/stable/topics/db/aggregation/
"""

from typing import List, Dict, Any, Optional
from django.db.models import QuerySet
from acq_module.models.model_acq_seller import SellerRawData
from .serv_rep_queryBuilder import build_reporting_queryset, parse_filter_params
from .serv_rep_aggregations import group_by_trade


def get_by_trade_chart_data(request) -> List[Dict[str, Any]]:
    """
    WHAT: Get chart data for By Trade visualization
    WHY: Display bar/line/pie chart showing UPB by trade
    HOW: Parse filters, build queryset, group by trade, format for Chart.js
    
    ARGS:
        request: Django request with query params (trade_ids, statuses, dates)
    
    RETURNS: List of chart data points
        [
            {
                'x': 'NPL Portfolio 2024-Q1',  # Trade name (chart label)
                'y': 12500000.00,              # Total UPB (chart value)
                'meta': {                      # Extra data for tooltips/drill-down
                    'trade_id': 1,
                    'count': 245,
                    'ltv': 78.5,
                    'status': 'DD'
                }
            },
            ...
        ]
    
    EXAMPLE USAGE in view:
        chart_data = get_by_trade_chart_data(request)
        return Response(chart_data)
    """
    # WHAT: Parse filter parameters from query string
    # WHY: Extract trade_ids, statuses, dates, etc.
    filters = parse_filter_params(request)
    
    # WHAT: Build filtered queryset
    # WHY: Apply all user-selected filters
    queryset = build_reporting_queryset(**filters)
    
    # WHAT: Group by trade and calculate metrics
    # WHY: Get per-trade summary stats
    trade_metrics = group_by_trade(queryset)
    
    # WHAT: Format for Chart.js
    # WHY: Frontend expects {x, y, meta} format
    chart_data = [
        {
            'x': trade['trade_name'],
            'y': trade['total_upb'],
            'meta': {
                'trade_id': trade['trade_id'],
                'count': trade['asset_count'],
                'ltv': trade['avg_ltv'],
                'status': trade['status'],
            }
        }
        for trade in trade_metrics
    ]
    
    return chart_data


def get_by_trade_grid_data(request) -> List[Dict[str, Any]]:
    """
    WHAT: Get detailed grid data for By Trade table (AG Grid)
    WHY: Display granular trade-level data with all metrics
    HOW: Parse filters, build queryset, group by trade, return full details
    
    ARGS:
        request: Django request with query params
    
    RETURNS: List of row objects for AG Grid
        [
            {
                'id': 1,
                'trade_id': 1,
                'trade_name': 'NPL Portfolio 2024-Q1',
                'seller_name': 'ABC Bank',
                'asset_count': 245,
                'total_upb': 12500000.00,
                'avg_upb': 51020.41,
                'avg_ltv': 78.5,
                'total_debt': 11200000.00,
                'status': 'DD',
                'bid_date': '2024-01-15',
                'state_count': 12,
                'delinquency_rate': 3.2,
                'last_updated': '2024-11-01T10:30:00Z',
            },
            ...
        ]
    
    EXAMPLE USAGE in view:
        grid_data = get_by_trade_grid_data(request)
        return Response(grid_data)
    """
    # WHAT: Parse filter parameters
    filters = parse_filter_params(request)
    
    # WHAT: Build filtered queryset
    queryset = build_reporting_queryset(**filters)
    
    # WHAT: Group by trade and get full metrics
    # WHY: AG Grid needs all columns available
    trade_metrics = group_by_trade(queryset)
    
    # WHAT: Add additional fields for AG Grid
    # WHY: Grid may display more columns than chart
    for trade in trade_metrics:
        # WHAT: Add last_updated timestamp
        # WHY: Show data freshness in hidden column
        # TODO: Get actual last_updated from Trade or max(asset updated_at)
        trade['last_updated'] = None  # Placeholder
        
        # WHAT: Add seller field (already in trade_metrics from aggregations)
        # Seller name comes from group_by_trade: trade['seller_name']
    
    return trade_metrics


def get_trade_drill_down_data(trade_id: int) -> Dict[str, Any]:
    """
    WHAT: Get detailed data for single trade drill-down modal
    WHY: User clicked a trade in chart/grid, show deep details
    HOW: Query all metrics for specific trade
    
    ARGS:
        trade_id: Trade ID to get details for
    
    RETURNS: Dict with comprehensive trade details
        {
            'trade_id': 1,
            'trade_name': 'NPL Portfolio 2024-Q1',
            'seller_name': 'ABC Bank',
            'status': 'DD',
            'bid_date': '2024-01-15',
            'asset_count': 245,
            'total_upb': 12500000.00,
            'avg_ltv': 78.5,
            'state_breakdown': [...],    # Per-state metrics
            'property_types': [...],     # Per-type metrics
            'delinquency_buckets': [...], # By DLQ bucket
        }
    
    EXAMPLE USAGE in drill-down view:
        details = get_trade_drill_down_data(trade_id=1)
        return Response(details)
    """
    # WHAT: Filter to single trade
    queryset = SellerRawData.objects.filter(trade_id=trade_id).select_related('trade', 'trade__seller')
    
    # WHAT: Calculate metrics for this trade only
    trade_metrics = group_by_trade(queryset)
    
    if not trade_metrics:
        return {}
    
    # WHAT: Return first (and only) result
    # WHY: Single trade, single result
    result = trade_metrics[0]
    
    # TODO: Add additional drill-down metrics:
    # - State breakdown (group by state)
    # - Property type breakdown (group by property_type)
    # - Delinquency buckets (group by months_dlq ranges)
    
    return result

