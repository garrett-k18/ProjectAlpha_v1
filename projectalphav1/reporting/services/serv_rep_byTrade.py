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
from django.utils import timezone
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
    WHAT: Get asset-level grid data for By Trade table (AG Grid)
    WHY: Each row represents a single asset, filtered by trade and other sidebar filters
    HOW: Parse filters, build asset-level queryset, project required fields into dicts

    ARGS:
        request: Django request with query params

    RETURNS: List of row objects for AG Grid
        [
            {
                'id': 1001,                      # Asset (SellerRawData) PK
                'trade_id': 1,
                'trade_name': 'NPL Portfolio',
                'street_address': '123 Main St',
                'city': 'Dallas',
                'state': 'TX',
                'total_upb': 125000.00,          # Per-asset current_balance
                'status': 'BOARD',               # Trade status
                'bid_date': '2024-01-15',        # Purchase date from BlendedOutcomeModel
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

    # WHAT: Build filtered queryset (asset-level SellerRawData rows)
    queryset = build_reporting_queryset(**filters)

    grid_rows: List[Dict[str, Any]] = []
    today = timezone.now().date()

    for asset in queryset:
        trade = asset.trade
        purchase_date = getattr(asset, 'purchase_date', None)
        purchase_price = getattr(asset, 'purchase_price', None)
        expected_exit_date = getattr(asset, 'expected_exit_date', None)
        expected_gross_proceeds = getattr(asset, 'expected_gross_proceeds', None)
        expected_net_proceeds = getattr(asset, 'expected_net_proceeds', None)

        purchase_date_value = purchase_date.isoformat() if purchase_date else None
        last_updated_value = asset.updated_at.isoformat() if asset.updated_at else None

        current_duration_months: Optional[int] = None
        if purchase_date:
            current_duration_months = (today.year - purchase_date.year) * 12 + (today.month - purchase_date.month)
            if current_duration_months < 0:
                current_duration_months = 0

        projected_gross_cost: Optional[float] = None
        if expected_gross_proceeds is not None and expected_net_proceeds is not None:
            projected_gross_cost = float(expected_gross_proceeds) - float(expected_net_proceeds)

        grid_rows.append({
            # identifiers / context
            'id': asset.pk,
            'trade_id': asset.trade_id,
            'trade_name': trade.trade_name if trade and trade.trade_name else '',
            'street_address': asset.street_address or '',
            'city': asset.city or '',
            'state': asset.state or '',

            # base financials
            'total_upb': float(asset.current_balance or 0),
            'status': trade.status if trade and trade.status else '',
            'purchase_date': purchase_date_value,
            'last_updated': last_updated_value,

            # servicing view fields
            'servicer_current_balance': float(getattr(asset, 'servicer_current_balance', 0) or 0),
            'servicer_total_debt': float(getattr(asset, 'servicer_total_debt', 0) or 0),
            'servicer_as_of_date': getattr(asset, 'servicer_as_of_date', None),
            'servicer_next_due_date': getattr(asset, 'servicer_next_due_date', None),
            'months_dlq': asset.months_dlq,

            # initial underwriting view fields
            'purchase_price': float(purchase_price or 0) if purchase_price is not None else None,

            # performance view fields
            'current_duration_months': current_duration_months,
            'current_gross_cost': None,

            # re-underwriting / projections view fields
            'expected_exit_date': expected_exit_date,
            'expected_gross_proceeds': float(expected_gross_proceeds or 0) if expected_gross_proceeds is not None else None,
            'expected_net_proceeds': float(expected_net_proceeds or 0) if expected_net_proceeds is not None else None,
            'projected_gross_cost': projected_gross_cost,
        })

    return grid_rows


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

