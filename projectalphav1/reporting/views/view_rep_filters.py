"""
View: Filter Options Endpoints

WHAT: API endpoints for sidebar filter dropdowns
WHY: Populate Trades, Statuses, Funds, Entities multi-select filters
WHERE: Mounted at /api/reporting/trades/, /api/reporting/statuses/, etc.
HOW: Delegate to service layer for business logic (thin view principle)

FILE NAMING: view_rep_filters.py
- view_ = Views folder
- _rep_ = Reporting module
- filters = Filter options

ARCHITECTURE:
Frontend Sidebar → This View → Service Layer → Model
                          ↓
                    Serializer

Docs reviewed:
- DRF API Views: https://www.django-rest-framework.org/api-guide/views/
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from reporting.services.serv_rep_filterOptions import (
    get_trade_options_data,
    get_status_options_data,
    get_task_status_options_data,
    get_fund_options_data,
    get_entity_options_data,
)
from reporting.serializers.serial_rep_filterOptions import (
    TradeOptionSerializer,
    StatusOptionSerializer,
    TaskStatusOptionSerializer,
    FundOptionSerializer,
    EntityOptionSerializer,
)


@api_view(['GET'])
def trade_options(request):
    """
    WHAT: Return all trades for sidebar filter dropdown
    WHY: Populate trade multi-select filter with Trade model data
    WHERE: Called when reporting dashboard loads
    
    ENDPOINT: GET /api/reporting/trades/
    
    RETURNS: 200 OK with list of trade options
        [
            {
                'id': 1,
                'trade_name': 'NPL Portfolio 2024-Q1',
                'seller_name': 'ABC Bank',
                'status': 'DD',
                'asset_count': 245,
            },
            ...
        ]
    
    USAGE in frontend:
        axios.get('/api/reporting/trades/')
        // Populate sidebar dropdown with trade names
    """
    try:
        # WHAT: Delegate to service layer
        # WHY: Keep view thin, business logic in service
        trades = get_trade_options_data()
        
        # WHAT: Serialize data using field definitions
        # WHY: Validate and format response
        serializer = TradeOptionSerializer(trades, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        # WHAT: Log error and return 500
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'[FilterOptions] Trade options error: {str(e)}', exc_info=True)
        return Response(
            {'error': 'Failed to load trade options', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def status_options(request):
    """
    WHAT: Return all unique AM outcome tracks for sidebar filter dropdown
    WHY: Populate track status multi-select filter (REO, FC, DIL, Short Sale, Modification, Note Sale)
    WHERE: Called when reporting dashboard loads
    
    ENDPOINT: GET /api/reporting/statuses/
    
    RETURNS: 200 OK with list of track options
        [
            {
                'value': 'reo',
                'label': 'REO',
                'count': 25,
            },
            ...
        ]
    """
    try:
        # WHAT: Delegate to service layer
        tracks = get_status_options_data()
        
        # WHAT: Serialize data
        serializer = StatusOptionSerializer(tracks, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'[FilterOptions] Track options error: {str(e)}', exc_info=True)
        return Response(
            {'error': 'Failed to load track options', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def task_status_options(request):
    """
    WHAT: Return all active task types for sidebar sub-filter dropdown
    WHY: Populate task status multi-select filter showing active tasks within outcome tracks
    WHERE: Called when reporting dashboard loads or when track filter changes
    
    ENDPOINT: GET /api/reporting/task-statuses/
    QUERY PARAMS: ?track=reo (optional - filter by specific track)
    
    RETURNS: 200 OK with list of task status options
        [
            {
                'value': 'eviction',
                'label': 'Eviction',
                'track': 'reo',
                'count': 10,
            },
            ...
        ]
    """
    try:
        # WHAT: Get optional track filter from query params
        # WHY: Allow filtering tasks by specific outcome track
        track = request.GET.get('track', None)
        
        # WHAT: Delegate to service layer
        # WHY: Keep view thin, business logic in service
        task_statuses = get_task_status_options_data(track=track)
        
        # WHAT: Serialize data using field definitions
        # WHY: Validate and format response
        serializer = TaskStatusOptionSerializer(task_statuses, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'[FilterOptions] Task status options error: {str(e)}', exc_info=True)
        return Response(
            {'error': 'Failed to load task status options', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def fund_options(request):
    """
    WHAT: Return all funds for sidebar filter dropdown
    WHY: Populate fund filter
    WHERE: Called when reporting dashboard loads
    
    ENDPOINT: GET /api/reporting/funds/
    
    TODO: Update once Fund model is created
    
    RETURNS: 200 OK with list of fund options
    """
    try:
        # WHAT: Delegate to service layer
        funds = get_fund_options_data()
        
        # WHAT: Serialize data
        serializer = FundOptionSerializer(funds, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'[FilterOptions] Fund options error: {str(e)}', exc_info=True)
        return Response(
            {'error': 'Failed to load fund options', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def entity_options(request):
    """
    WHAT: Return all legal entities for sidebar filter dropdown
    WHY: Populate entity filter
    WHERE: Called when reporting dashboard loads
    
    ENDPOINT: GET /api/reporting/entities/
    
    TODO: Update once Entity model is created
    
    RETURNS: 200 OK with list of entity options
    """
    try:
        # WHAT: Delegate to service layer
        entities = get_entity_options_data()
        
        # WHAT: Serialize data
        serializer = EntityOptionSerializer(entities, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'[FilterOptions] Entity options error: {str(e)}', exc_info=True)
        return Response(
            {'error': 'Failed to load entity options', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
