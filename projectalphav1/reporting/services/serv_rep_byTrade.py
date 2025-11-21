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
from am_module.services.serv_am_assetInventory import AssetInventoryEnricher
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
                'purchase_date': '2024-01-15',   # From BlendedOutcomeModel
                # Servicing fields when available
                'servicer_current_balance': 125000.00,
                'servicer_total_debt': 135000.00,
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

    enricher = AssetInventoryEnricher()
    grid_rows: List[Dict[str, Any]] = []
    today = timezone.now().date()

    for asset in queryset:
        trade = asset.trade
        purchase_date = getattr(asset, 'purchase_date', None)
        purchase_price = getattr(asset, 'purchase_price', None)
        expected_exit_date = getattr(asset, 'expected_exit_date', None)
        expected_gross_proceeds = getattr(asset, 'expected_gross_proceeds', None)
        expected_net_proceeds = getattr(asset, 'expected_net_proceeds', None)
        expected_pl = getattr(asset, 'expected_pl', None)
        expected_cf = getattr(asset, 'expected_cf', None)
        expected_irr = getattr(asset, 'expected_irr', None)
        expected_moic = getattr(asset, 'expected_moic', None)
        expected_hold_duration = getattr(asset, 'expected_hold_duration', None)

        active_tracks = enricher.get_active_tracks(asset)
        active_tasks = enricher.get_active_tasks(asset)

        purchase_date_value = purchase_date.isoformat() if purchase_date else None
        expected_exit_date_value = expected_exit_date.isoformat() if expected_exit_date else None
        servicer_next_due_date = getattr(asset, 'servicer_next_due_date', None)
        servicer_next_due_date_value = servicer_next_due_date.isoformat() if servicer_next_due_date else None

        current_duration_months: Optional[int] = None
        if purchase_date:
            current_duration_months = (today.year - purchase_date.year) * 12 + (today.month - purchase_date.month)
            if current_duration_months < 0:
                current_duration_months = 0

        projected_gross_cost: Optional[float] = None
        if purchase_price is not None:
            purchase_price_val = float(purchase_price or 0)
            legal_expenses_val = float(getattr(asset, 'legal_expenses', 0) or 0)
            servicing_expenses_val = float(getattr(asset, 'servicing_expenses', 0) or 0)
            reo_expenses_val = float(getattr(asset, 'reo_expenses', 0) or 0)
            carry_cost_val = float(getattr(asset, 'carry_cost', 0) or 0)
            liq_fees_val = float(getattr(asset, 'liq_fees', 0) or 0)
            projected_gross_cost = (
                purchase_price_val
                + legal_expenses_val
                + servicing_expenses_val
                + reo_expenses_val
                + carry_cost_val
                + liq_fees_val
            )

        # UW Exit Duration (months between purchase_date and expected_exit_date)
        uw_exit_duration_months: Optional[int] = None
        if expected_hold_duration is not None:
            uw_exit_duration_months = int(expected_hold_duration)
        elif purchase_date and expected_exit_date:
            uw_exit_duration_months = (expected_exit_date.year - purchase_date.year) * 12 + (expected_exit_date.month - purchase_date.month)
            if uw_exit_duration_months < 0:
                uw_exit_duration_months = 0

        grid_rows.append({
            # identifiers / context
            'id': asset.pk,
            'trade_id': asset.trade_id,
            'trade_name': trade.trade_name if trade and trade.trade_name else '',

            # core asset fields expected by grid
            'servicer_id': getattr(asset, 'servicer_id', None),
            'street_address': asset.street_address or '',
            'city': asset.city or '',
            'state': asset.state or '',

            # initial underwriting snapshot (from BlendedOutcomeModel)
            'purchase_price': float(purchase_price or 0) if purchase_price is not None else None,
            'purchase_date': purchase_date_value,
            'exit_strategy': getattr(asset, 'exit_strategy', None),
            'bid_pct_upb': float(getattr(asset, 'bid_pct_upb', 0)) if getattr(asset, 'bid_pct_upb', None) is not None else None,
            'bid_pct_td': float(getattr(asset, 'bid_pct_td', 0)) if getattr(asset, 'bid_pct_td', None) is not None else None,
            'bid_pct_sellerasis': float(getattr(asset, 'bid_pct_sellerasis', 0)) if getattr(asset, 'bid_pct_sellerasis', None) is not None else None,
            'bid_pct_pv': float(getattr(asset, 'bid_pct_pv', 0)) if getattr(asset, 'bid_pct_pv', None) is not None else None,
            'uw_exit_duration_months': uw_exit_duration_months,

            # servicing fields (these were fine to keep)
            'servicer_current_balance': float(getattr(asset, 'servicer_current_balance', 0) or 0),
            'servicer_total_debt': float(getattr(asset, 'servicer_total_debt', 0) or 0),
            'servicer_next_due_date': servicer_next_due_date_value,
            'months_dlq': asset.months_dlq,

            # hold durations and performance metrics
            'pre_reo_hold_duration': getattr(asset, 'pre_reo_hold_duration', None),
            'reo_hold_duration': getattr(asset, 'reo_hold_duration', None),
            'current_duration_months': current_duration_months,
            'current_gross_cost': float(getattr(asset, 'current_gross_cost', 0) or 0),
            'projected_gross_cost': projected_gross_cost,
            'expected_exit_date': expected_exit_date_value,
            'expected_gross_proceeds': float(expected_gross_proceeds or 0) if expected_gross_proceeds is not None else None,
            'expected_net_proceeds': float(expected_net_proceeds or 0) if expected_net_proceeds is not None else None,
            'expected_pl': float(expected_pl or 0) if expected_pl is not None else None,
            'expected_cf': float(expected_cf or 0) if expected_cf is not None else None,
            'expected_irr': float(expected_irr or 0) if expected_irr is not None else None,
            'expected_moic': float(expected_moic or 0) if expected_moic is not None else None,

            # monthly servicing cost (matches calculate_monthly_servicing_cost helper)
            'legal_expenses': float(getattr(asset, 'legal_expenses', 0) or 0),
            'servicing_expenses': float(getattr(asset, 'servicing_expenses', 0) or 0),
            'reo_expenses': float(getattr(asset, 'reo_expenses', 0) or 0),
            'carry_cost': float(getattr(asset, 'carry_cost', 0) or 0),
            'liq_fees': float(getattr(asset, 'liq_fees', 0) or 0),
            'active_tracks': active_tracks,
            'active_tasks': active_tasks,
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

