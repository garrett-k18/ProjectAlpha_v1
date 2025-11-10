"""
View: Summary KPI Endpoint

WHAT: Summary KPI endpoint for reporting dashboard top bar
WHY: Display Total UPB, Asset Count, Avg LTV, Delinquency Rate
WHERE: Called when filters change or view loads
HOW: Delegate to service layer for metric calculations

FILE NAMING: view_rep_summary.py
- view_ = Views folder
- _rep_ = Reporting module
- summary = Summary KPIs

ARCHITECTURE:
Frontend → This View → Service Layer → QuerySet → Model

Docs reviewed:
- DRF API Views: https://www.django-rest-framework.org/api-guide/views/
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from reporting.services.serv_rep_queryBuilder import build_reporting_queryset, parse_filter_params
from reporting.services.serv_rep_aggregations import calculate_summary_metrics


@api_view(['GET'])
def report_summary(request):
    """
    WHAT: Calculate summary KPIs based on filters
    WHY: Display top bar metrics on reporting dashboard
    WHERE: Called when filters change or dashboard loads
    
    ENDPOINT: GET /api/reporting/summary/
    
    QUERY PARAMS:
        - trade_ids: Comma-separated trade IDs (e.g., "1,2,3")
        - statuses: Comma-separated statuses (e.g., "DD,AWARDED")
        - fund_id: Single fund ID (e.g., "5")
        - entity_id: Single entity ID (e.g., "2")
        - start_date: ISO date (e.g., "2024-01-01")
        - end_date: ISO date (e.g., "2024-12-31")
    
    RETURNS: 200 OK with Dict
        {
            'total_upb': 123456789.00,
            'asset_count': 1234,
            'avg_ltv': 75.5,
            'delinquency_rate': 3.2,
        }
    """
    try:
        # WHAT: Parse filter parameters from query string
        # WHY: Extract user-selected filters
        filters = parse_filter_params(request)
        
        # WHAT: Build filtered queryset using service layer
        # WHY: Centralized query building logic
        queryset = build_reporting_queryset(**filters)
        
        # WHAT: Calculate summary metrics using service layer
        # WHY: Business logic stays in service, not view
        metrics = calculate_summary_metrics(queryset)
        
        return Response(metrics, status=status.HTTP_200_OK)
    
    except Exception as e:
        # WHAT: Log error and return 500
        # WHY: Graceful error handling with details
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'[ReportSummary] Error calculating metrics: {str(e)}', exc_info=True)
        return Response(
            {'error': 'Failed to calculate summary metrics', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
