"""
**WHAT**: By Status report endpoints (chart and grid data)
**WHY**: Power By Status report view in dashboard
**WHERE**: Called when user selects By Status view
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from reporting.services.serv_rep_byStatus import (
    get_by_status_chart_data,
    get_by_status_grid_data,
)


@api_view(['GET'])
def get_by_status_chart(request):
    """
    **WHAT**: Return chart data for By Status report
    **WHY**: Visualize portfolio breakdown by status in doughnut chart
    **WHERE**: Called when By Status view loads
    
    **QUERY PARAMS**: Same as summary endpoint (trade_ids, statuses, dates)
    
    **RETURNS**: List of {x: status, y: total_upb, meta: {count, percentage}}
    """
    chart_data = get_by_status_chart_data(request)
    return Response(chart_data)


@api_view(['GET'])
def get_by_status_grid(request):
    """
    **WHAT**: Return detailed table data for By Status report
    **WHY**: Display granular status-level data in grid
    **WHERE**: Called when By Status view loads (below chart)
    
    **QUERY PARAMS**: Same as summary endpoint
    
    **RETURNS**: List of {status, count, total_upb, avg_upb, percentage, ...}
    """
    grid_data = get_by_status_grid_data(request)
    return Response(grid_data)
