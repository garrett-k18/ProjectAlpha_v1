"""
**WHAT**: By Trade report endpoints (chart and grid data)
**WHY**: Power By Trade report view in dashboard
**WHERE**: Called when user selects By Trade view
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from acq_module.models.seller import SellerRawData
from reporting.logic.logic_rep_metrics import calculate_by_trade_metrics
from reporting.logic.logic_rep_filters import apply_filters


@api_view(['GET'])
def get_by_trade_chart(request):
    """
    **WHAT**: Return chart data for By Trade report
    **WHY**: Visualize performance by trade in chart
    **WHERE**: Called when By Trade view loads
    
    **QUERY PARAMS**: Same as summary endpoint (trade_ids, statuses, dates)
    
    **RETURNS**: List of {x: trade_name, y: total_upb, meta: {...}}
    """
    # Start with all seller data
    queryset = SellerRawData.objects.select_related('trade', 'trade__seller')
    
    # Apply filters
    queryset = apply_filters(request, queryset)
    
    # Group by trade and calculate metrics
    trades = calculate_by_trade_metrics(queryset)
    
    # Format for chart (Chart.js format)
    result = [
        {
            'x': t['trade__trade_name'],
            'y': float(t['total_upb'] or 0),
            'meta': {
                'count': t['asset_count'],
                'ltv': float(t['avg_ltv'] or 0),
                'status': t['trade__status']
            }
        }
        for t in trades
    ]
    
    return Response(result)


@api_view(['GET'])
def get_by_trade_grid(request):
    """
    **WHAT**: Return detailed table data for By Trade report
    **WHY**: Display granular trade-level data in grid
    **WHERE**: Called when By Trade view loads (below chart)
    
    **QUERY PARAMS**: Same as summary endpoint
    
    **RETURNS**: List of {id, trade_name, seller_name, asset_count, total_upb, ...}
    """
    # Start with all seller data
    queryset = SellerRawData.objects.select_related('trade', 'trade__seller')
    
    # Apply filters
    queryset = apply_filters(request, queryset)
    
    # Group by trade and calculate metrics
    trades = calculate_by_trade_metrics(queryset)
    
    # Format for grid table
    result = [
        {
            'id': t['trade_id'],
            'trade_name': t['trade__trade_name'],
            'seller_name': t['trade__seller__seller_name'],
            'asset_count': t['asset_count'],
            'total_upb': float(t['total_upb'] or 0),
            'avg_upb': float(t['avg_upb'] or 0),
            'avg_ltv': float(t['avg_ltv'] or 0),
            'total_debt': float(t['total_debt'] or 0),
            'asis_value': float(t['asis_value'] or 0),
            'status': t['trade__status']
        }
        for t in trades
    ]
    
    return Response(result)
