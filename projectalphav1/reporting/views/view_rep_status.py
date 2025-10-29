"""
**WHAT**: By Status report endpoints (chart and grid data)
**WHY**: Power By Status report view in dashboard
**WHERE**: Called when user selects By Status view
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from acq_module.models.seller import SellerRawData
from reporting.logic.logic_rep_metrics import calculate_by_status_metrics
from reporting.logic.logic_rep_filters import apply_filters


@api_view(['GET'])
def get_by_status_chart(request):
    """
    **WHAT**: Return chart data for By Status report
    **WHY**: Visualize portfolio breakdown by status in doughnut chart
    **WHERE**: Called when By Status view loads
    
    **QUERY PARAMS**: Same as summary endpoint (trade_ids, statuses, dates)
    
    **RETURNS**: List of {x: status, y: total_upb, meta: {count, percentage}}
    """
    # Start with all seller data
    queryset = SellerRawData.objects.select_related('trade')
    
    # Apply filters
    queryset = apply_filters(request, queryset)
    
    # Group by status and calculate metrics (includes percentage)
    statuses = calculate_by_status_metrics(queryset)
    
    # Format for chart (Chart.js format)
    result = [
        {
            'x': s['trade__status'],
            'y': float(s['total_upb'] or 0),
            'meta': {
                'count': s['asset_count'],
                'percentage': round(s['percentage'], 2)
            }
        }
        for s in statuses
    ]
    
    return Response(result)


@api_view(['GET'])
def get_by_status_grid(request):
    """
    **WHAT**: Return detailed table data for By Status report
    **WHY**: Display granular status-level data in grid
    **WHERE**: Called when By Status view loads (below chart)
    
    **QUERY PARAMS**: Same as summary endpoint
    
    **RETURNS**: List of {status, count, total_upb, avg_upb, percentage, ...}
    """
    # Start with all seller data
    queryset = SellerRawData.objects.select_related('trade')
    
    # Apply filters
    queryset = apply_filters(request, queryset)
    
    # Group by status and calculate metrics (includes percentage)
    statuses = calculate_by_status_metrics(queryset)
    
    # Format for grid table
    result = [
        {
            'status': s['trade__status'],
            'count': s['asset_count'],
            'total_upb': float(s['total_upb'] or 0),
            'avg_upb': float(s['avg_upb'] or 0),
            'percentage': round(s['percentage'], 2),
            'avg_ltv': float(s['avg_ltv'] or 0),
            'total_debt': float(s['total_debt'] or 0)
        }
        for s in statuses
    ]
    
    return Response(result)
