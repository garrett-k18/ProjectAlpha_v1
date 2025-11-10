"""
View: By Trade Report Endpoints

WHAT: API endpoints for By Trade report (chart and grid data)
WHY: Power By Trade report view in reporting dashboard
WHERE: Mounted at /api/reporting/by-trade/
HOW: Delegate to service layer for business logic (thin view principle)

FILE NAMING: view_rep_trade.py
- view_ = Views folder
- _rep_ = Reporting module
- trade = Specific report type

ARCHITECTURE:
Frontend → This View → Service Layer → QuerySet → Model
                ↓
          Serializer (if needed)

Docs reviewed:
- DRF API Views: https://www.django-rest-framework.org/api-guide/views/
- DRF Response: https://www.django-rest-framework.org/api-guide/responses/
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from reporting.services.serv_rep_byTrade import (
    get_by_trade_chart_data,
    get_by_trade_grid_data,
)


@api_view(['GET'])
def by_trade_chart(request):
    """
    WHAT: Return chart data for By Trade visualization
    WHY: Power Chart.js bar/line/pie chart in frontend
    WHERE: Called when user loads By Trade view
    
    ENDPOINT: GET /api/reporting/by-trade/
    
    QUERY PARAMS:
        - trade_ids: Comma-separated trade IDs (e.g., "1,2,3")
        - statuses: Comma-separated statuses (e.g., "DD,AWARDED")
        - fund_id: Single fund ID (e.g., "5")
        - entity_id: Single entity ID (e.g., "2")
        - start_date: ISO date string (e.g., "2024-01-01")
        - end_date: ISO date string (e.g., "2024-12-31")
    
    RETURNS: 200 OK with list of {x, y, meta}
    """
    try:
        # WHAT: Delegate to service layer
        # WHY: Keep view thin, business logic in service
        chart_data = get_by_trade_chart_data(request)
        return Response(chart_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        # WHAT: Log error and return 500
        # WHY: Graceful error handling
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'[ByTradeReport] Chart data error: {str(e)}', exc_info=True)
        return Response(
            {'error': 'Failed to load chart data', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def by_trade_grid(request):
    """
    WHAT: Return detailed grid data for By Trade AG Grid
    WHY: Display granular trade-level metrics in table
    WHERE: Called when user loads By Trade view
    
    ENDPOINT: GET /api/reporting/by-trade/grid/
    
    QUERY PARAMS: Same as chart endpoint
    
    RETURNS: 200 OK with list of row objects
    """
    try:
        # WHAT: Delegate to service layer
        # WHY: Keep view thin, business logic in service
        grid_data = get_by_trade_grid_data(request)
        return Response(grid_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        # WHAT: Log error and return 500
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'[ByTradeReport] Grid data error: {str(e)}', exc_info=True)
        return Response(
            {'error': 'Failed to load grid data', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
