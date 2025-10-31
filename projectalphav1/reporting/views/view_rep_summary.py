"""
**WHAT**: Summary KPI endpoint for reporting dashboard
**WHY**: Display top bar metrics (Total UPB, Asset Count, Avg LTV, Delinquency Rate)
**WHERE**: Called when filters change or view loads
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from acq_module.models.model_acq_seller import SellerRawData
from reporting.logic.logic_rep_metrics import calculate_summary_metrics
from reporting.logic.logic_rep_filters import apply_filters


@api_view(['GET'])
def get_report_summary(request):
    """
    **WHAT**: Calculate summary KPIs based on filters
    **WHY**: Display top bar metrics on reporting dashboard
    **WHERE**: Called when filters change or dashboard loads
    
    **QUERY PARAMS**:
    - trade_ids: Comma-separated trade IDs (e.g., "1,2,3")
    - statuses: Comma-separated statuses (e.g., "DD,AWARDED")
    - start_date: ISO date (e.g., "2024-01-01")
    - end_date: ISO date (e.g., "2024-12-31")
    
    **RETURNS**: Dict with total_upb, asset_count, avg_ltv, delinquency_rate
    """
    # Start with all seller data
    queryset = SellerRawData.objects.select_related('trade', 'trade__seller')
    
    # Apply filters from query params
    queryset = apply_filters(request, queryset)
    
    # Calculate metrics using logic module
    metrics = calculate_summary_metrics(queryset)
    
    return Response(metrics)
