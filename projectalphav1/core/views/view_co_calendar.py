"""
Calendar API Views

What: REST API endpoints for unified calendar event aggregation and custom event CRUD
Why: Frontend calendar widget needs to display dates from multiple models + user-created events
Where: projectalphav1/core/views/view_co_calendar.py
How: Aggregates date fields from various models into standardized format using serial_co_calendar serializers

Handles both:
1. Read-only events from model dates (SellerRawData, ServicerData, TradeLevelAssumption, Trade)
2. CRUD operations for custom calendar events (CalendarEvent model)

Endpoints:
    GET    /api/core/calendar/events/              - List all events (model + custom)
    POST   /api/core/calendar/events/custom/       - Create custom event
    GET    /api/core/calendar/events/custom/<id>/  - Get custom event
    PUT    /api/core/calendar/events/custom/<id>/  - Update custom event
    DELETE /api/core/calendar/events/custom/<id>/  - Delete custom event

Linked Serializers:
- CalendarEventReadSerializer (read-only model events)
- CustomCalendarEventSerializer (CRUD for CalendarEvent model)
- UnifiedCalendarEventSerializer (combined output format)

Location: projectalphav1/core/serializers/serial_co_calendar.py
"""
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.db.models import Q

from rest_framework.exceptions import PermissionDenied

# Import models that contain date fields
from acq_module.models.model_acq_seller import SellerRawData, Seller, Trade
from acq_module.models.model_acq_assumptions import TradeLevelAssumption
from am_module.models.servicers import ServicerLoanData as ServicerData
from core.models import CalendarEvent
from core.serializers.serial_co_calendar import (
    CalendarEventReadSerializer,
    CustomCalendarEventSerializer,
    UnifiedCalendarEventSerializer,
    CALENDAR_DATE_FIELDS,
)

from core.views.view_co_notifications import _resolve_request_user


@api_view(['GET'])
@permission_classes([AllowAny])  # TODO: Add authentication when ready
def get_calendar_events(request):
    """
    Aggregates calendar events from various models across the application.
    
    What: Main calendar endpoint that combines events from multiple data sources
    Why: Frontend FullCalendar widget needs unified event list from all models
    Where: Called by frontend calendar component at /api/core/calendar/events/
    How: Calls helper functions for each model, filters/combines results, serializes with UnifiedCalendarEventSerializer
    
    Query Parameters:
    - start_date (optional): Filter events on or after this date (YYYY-MM-DD)
    - end_date (optional): Filter events on or before this date (YYYY-MM-DD)
    - seller_id (optional): Filter events for a specific seller
    - trade_id (optional): Filter events for a specific trade
    - categories (optional): Comma-separated list of event categories to include
                            Valid: bg-primary, bg-success, bg-info, bg-warning, bg-danger, bg-secondary
    
    Returns:
        JSON array of calendar events with standardized format:
        - id: Unique composite key (e.g., 'servicer_data:123:actual_fc_sale_date')
        - title: Event title displayed on calendar
        - date: Event date (YYYY-MM-DD)
        - time: Event time or 'All Day'
        - description: Additional details
        - category: Bootstrap color class
        - source_model: Origin model name
        - editable: Boolean indicating if event can be edited
        - url: Frontend navigation URL
    
    Example Response:
        [
            {
                "id": "trade_assumption:10:bid_date",
                "title": "Bid Date: Portfolio 2025-Q1",
                "date": "2025-10-15",
                "time": "All Day",
                "description": "Bid submitted for Portfolio 2025-Q1",
                "category": "bg-primary",
                "source_model": "TradeLevelAssumption",
                "editable": false,
                "url": "/acq/trade/5/"
            }
        ]
    """
    
    # Parse query parameters from request
    # What: Extract filter parameters from GET request
    # Why: Allow frontend to filter events by date range, entity, or category
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    seller_id = request.GET.get('seller_id')
    trade_id = request.GET.get('trade_id')
    categories_param = request.GET.get('categories')
    
    # Convert date strings to date objects
    # What: Parse YYYY-MM-DD strings into Python date objects
    # Why: Need date objects for ORM filtering and comparison
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Parse categories filter
    # What: Convert comma-separated category string into list
    # Why: Allow filtering by multiple Bootstrap color classes (e.g., 'bg-danger,bg-warning')
    categories_filter = None
    if categories_param:
        categories_filter = [cat.strip() for cat in categories_param.split(',')]
    
    # Collect events from various sources
    # What: Aggregate events from all models into single list
    # Why: Calendar needs unified view of all date-based events across the system
    # How: Call helper function for each model, each returns list of standardized dicts
    events = []
    
    # 1. SellerRawData - Foreclosure dates, maturity dates, modification dates
    # Currently empty date_fields list - add fields as needed
    events.extend(_get_seller_raw_data_events(start_date, end_date, seller_id, trade_id))
    
    # 2. ServicerData - Payment dates, maturity dates, bankruptcy dates
    # Currently includes: actual_fc_sale_date
    events.extend(_get_servicer_data_events(start_date, end_date, seller_id, trade_id))
    
    # 3. TradeLevelAssumption dates (bid_date, settlement_date)
    # Currently includes: bid_date, settlement_date
    events.extend(_get_trade_assumption_events(start_date, end_date, seller_id, trade_id))
    
    # 4. Custom CalendarEvent records (user-created events)
    # All fields from CalendarEvent model
    events.extend(_get_custom_calendar_events(request, start_date, end_date, seller_id, trade_id))
    
    # Filter by categories if specified
    # What: Remove events that don't match requested categories
    # Why: Allow frontend to show only certain event types (e.g., only deadlines)
    if categories_filter:
        events = [e for e in events if e.get('category') in categories_filter]
    
    # Serialize and return
    # What: Convert list of dicts to JSON using UnifiedCalendarEventSerializer
    # Why: Validates structure and ensures consistent output format
    serializer = UnifiedCalendarEventSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def _get_seller_raw_data_events(start_date=None, end_date=None, seller_id=None, trade_id=None):
    """
    Extract calendar events from SellerRawData model.
    
    What: Converts date fields from SellerRawData records into calendar events
    Why: Seller tape data contains important dates that should appear on calendar
    Where: Called by get_calendar_events() main endpoint
    How: Queries SellerRawData, extracts configured date fields, formats as event dicts
    
    Includes: maturity dates, foreclosure dates, modification dates, payment dates
    
    Args:
        start_date: Filter events on/after this date
        end_date: Filter events on/before this date
        seller_id: Filter to specific seller
        trade_id: Filter to specific trade
    
    Returns:
        List of event dicts with keys: id, title, date, time, description, category, 
        source_model, source_id, url, editable
    
    Note: Currently date_fields list is empty - add date field configs as needed
    """
    events = []
    
    # Build queryset with filters
    queryset = SellerRawData.objects.select_related('seller', 'trade').all()
    
    if seller_id:
        queryset = queryset.filter(seller_id=seller_id)
    if trade_id:
        queryset = queryset.filter(trade_id=trade_id)
    
    # Get date fields from serializer config
    # What: Filter CALENDAR_DATE_FIELDS for SellerRawData model
    # Why: Single list in serial_co_calendar.py controls all calendar fields
    # Where: CALENDAR_DATE_FIELDS in core/serializers/serial_co_calendar.py
    # How: Just add/remove lines in that list - no need to edit this view
    date_fields = [
        (field, f'{title}: {{address}}', event_type, title)
        for model, field, title, event_type in CALENDAR_DATE_FIELDS
        if model == 'SellerRawData'
    ]
    
    for record in queryset:
        # Get display address (use street_address or fallback to city/state)
        address = record.street_address or f"{record.city or 'Unknown'}, {record.state or ''}"
        address = address[:30]  # Truncate for display
        
        # Extract each date field
        for field_name, title_template, category, desc_template in date_fields:
            date_value = getattr(record, field_name, None)
            
            if date_value:
                # Apply date range filter if specified
                if start_date and date_value < start_date:
                    continue
                if end_date and date_value > end_date:
                    continue
                
                events.append({
                    'id': f'seller_raw_data:{record.asset_hub_id}:{field_name}',
                    'title': title_template.format(address=address),
                    'date': date_value,
                    'time': 'All Day',
                    'description': desc_template.format(address=address),
                    'category': category,
                    'source_model': 'SellerRawData',
                    'source_id': record.asset_hub_id,
                    'url': f'/acq/loan/{record.asset_hub_id}/',
                    'editable': False  # Model-based events are read-only
                })
    
    return events


def _get_servicer_data_events(start_date=None, end_date=None, seller_id=None, trade_id=None):
    """
    Extract calendar events from ServicerData model.
    
    What: Converts date fields from ServicerLoanData records into calendar events
    Why: Servicer data contains critical dates (FC sales, payments, bankruptcy) for calendar
    Where: Called by get_calendar_events() main endpoint
    How: Queries ServicerLoanData, extracts configured date fields, formats as event dicts
    
    Includes: payment dates, maturity dates, bankruptcy dates, actual_fc_sale_date
    
    Args:
        start_date: Filter events on/after this date
        end_date: Filter events on/before this date
        seller_id: Filter to specific seller (via asset_hub relationship)
        trade_id: Filter to specific trade (via asset_hub relationship)
    
    Returns:
        List of event dicts with keys: id, title, date, time, description, category, 
        source_model, source_id, url, editable
    """
    events = []
    
    # Build queryset with filters
    queryset = ServicerData.objects.select_related('asset_hub').all()
    
    # Filter by seller/trade through asset_hub relationship
    if seller_id or trade_id:
        filters = Q()
        if seller_id:
            filters &= Q(asset_hub__sellerrawdata__seller_id=seller_id)
        if trade_id:
            filters &= Q(asset_hub__sellerrawdata__trade_id=trade_id)
        queryset = queryset.filter(filters)
    
    # Get date fields from serializer config
    # What: Filter CALENDAR_DATE_FIELDS for ServicerLoanData model
    # Why: Single list in serial_co_calendar.py controls all calendar fields
    # Where: CALENDAR_DATE_FIELDS in core/serializers/serial_co_calendar.py
    # How: Just add/remove lines in that list - no need to edit this view
    date_fields = [
        (field, f'{title}: {{address}}', event_type, title)
        for model, field, title, event_type in CALENDAR_DATE_FIELDS
        if model == 'ServicerLoanData'
    ]
    
    for record in queryset:
        address = record.address or f"{record.city or 'Unknown'}, {record.state or ''}"
        address = address[:30]
        
        for field_name, title_template, category, desc_template in date_fields:
            date_value = getattr(record, field_name, None)
            
            if date_value:
                if start_date and date_value < start_date:
                    continue
                if end_date and date_value > end_date:
                    continue
                
                events.append({
                    'id': f'servicer_data:{record.id}:{field_name}',
                    'title': title_template.format(address=address),
                    'date': date_value,
                    'time': 'All Day',
                    'description': desc_template,
                    'category': category,
                    'source_model': 'ServicerData',
                    'source_id': record.id,
                    'url': f'/am/loan/{record.asset_hub_id}/' if record.asset_hub_id else '',
                    'editable': False  # Model-based events are read-only
                })
    
    return events


def _get_trade_events(start_date=None, end_date=None, seller_id=None, trade_id=None):
    """
    Extract calendar events from Trade model.
    
    What: Converts date fields from Trade records into calendar events
    Why: Trade creation dates and milestones should appear on calendar for tracking
    Where: Called by get_calendar_events() main endpoint
    How: Queries Trade model, extracts created_at and other date fields, formats as event dicts
    
    Includes: trade creation dates, important milestones
    
    Args:
        start_date: Filter events on/after this date
        end_date: Filter events on/before this date
        seller_id: Filter to specific seller
        trade_id: Filter to specific trade
    
    Returns:
        List of event dicts with keys: id, title, date, time, description, category, 
        source_model, source_id, url, editable
    """
    events = []
    
    # Build queryset with filters
    queryset = Trade.objects.select_related('seller').all()
    
    if seller_id:
        queryset = queryset.filter(seller_id=seller_id)
    if trade_id:
        queryset = queryset.filter(id=trade_id)
    
    for trade in queryset:
        # Trade created date
        if trade.created_at:
            trade_date = trade.created_at.date()
            
            if start_date and trade_date < start_date:
                continue
            if end_date and trade_date > end_date:
                continue
            
            events.append({
                'id': f'trade:{trade.id}:created',
                'title': f'Trade Created: {trade.trade_name}',
                'date': trade_date,
                'time': 'All Day',
                'description': f'Trade {trade.trade_name} created for {trade.seller.name if trade.seller else "Unknown Seller"}',
                'category': 'bg-primary',
                'source_model': 'Trade',
                'source_id': trade.id,
                'url': f'/acq/trade/{trade.id}/',
                'editable': False  # Model-based events are read-only
            })
    
    return events


def _get_trade_assumption_events(start_date=None, end_date=None, seller_id=None, trade_id=None):
    """
    Extract calendar events from TradeLevelAssumption model.
    
    What: Converts date fields from TradeLevelAssumption records into calendar events
    Why: Bid dates and settlement dates are critical milestones that should appear on calendar
    Where: Called by get_calendar_events() main endpoint
    How: Queries TradeLevelAssumption, extracts configured date fields, formats as event dicts
    
    Includes: bid_date, settlement_date
    
    Args:
        start_date: Filter events on/after this date
        end_date: Filter events on/before this date
        seller_id: Filter to specific seller (via trade relationship)
        trade_id: Filter to specific trade
    
    Returns:
        List of event dicts with keys: id, title, date, time, description, category, 
        source_model, source_id, url, editable
    """
    events = []
    
    # Build queryset with filters
    queryset = TradeLevelAssumption.objects.select_related('trade', 'trade__seller').all()
    
    if seller_id:
        queryset = queryset.filter(trade__seller_id=seller_id)
    if trade_id:
        queryset = queryset.filter(trade_id=trade_id)
    
    # Get date fields from serializer config
    # What: Filter CALENDAR_DATE_FIELDS for TradeLevelAssumption model
    # Why: Single list in serial_co_calendar.py controls all calendar fields
    # Where: CALENDAR_DATE_FIELDS in core/serializers/serial_co_calendar.py
    # How: Just add/remove lines in that list - no need to edit this view
    date_fields = [
        (field, f'{title}: {{trade_name}}', event_type, title)
        for model, field, title, event_type in CALENDAR_DATE_FIELDS
        if model == 'TradeLevelAssumption'
    ]
    
    for record in queryset:
        trade_name = record.trade.trade_name if record.trade else 'Unknown Trade'
        
        for field_name, title_template, category, desc_template in date_fields:
            date_value = getattr(record, field_name, None)
            
            if date_value:
                if start_date and date_value < start_date:
                    continue
                if end_date and date_value > end_date:
                    continue
                
                events.append({
                    'id': f'trade_assumption:{record.id}:{field_name}',
                    'title': title_template.format(trade_name=trade_name),
                    'date': date_value,
                    'time': 'All Day',
                    'description': desc_template.format(trade_name=trade_name),
                    'category': category,
                    'source_model': 'TradeLevelAssumption',
                    'source_id': record.id,
                    'editable': False,
                    'url': f'/acq/trade/{record.trade_id}/' if record.trade_id else ''
                })
    
    return events


def _get_custom_calendar_events(request, start_date=None, end_date=None, seller_id=None, trade_id=None):
    """
    Extract calendar events from CalendarEvent model (user-created custom events).
    
    What: Retrieves user-created CalendarEvent records and formats as calendar events
    Why: Users need to add custom events (meetings, deadlines, reminders) to calendar
    Where: Called by get_calendar_events() main endpoint
    How: Queries CalendarEvent model, formats all fields as event dicts
    
    These events are editable through the calendar interface.
    
    Args:
        start_date: Filter events on/after this date
        end_date: Filter events on/before this date
        seller_id: Filter to specific seller
        trade_id: Filter to specific trade
    
    Returns:
        List of event dicts with keys: id, title, date, time, description, category, 
        source_model, editable (True), url
    
    Note: Unlike model-based events, these have editable=True and can be modified via API
    """
    events = []

    user = _resolve_request_user(request)

    queryset = CalendarEvent.objects.all()
    if user is None:
        queryset = queryset.filter(is_public=True)
    else:
        queryset = queryset.filter(Q(is_public=True) | Q(created_by=user))
    
    if seller_id:
        queryset = queryset.filter(seller_id=seller_id)
    if trade_id:
        queryset = queryset.filter(trade_id=trade_id)
    if start_date:
        queryset = queryset.filter(date__gte=start_date)
    if end_date:
        queryset = queryset.filter(date__lte=end_date)
    
    for event in queryset:
        # Generate URL based on linked entity
        url = ''
        if event.asset_hub_id:
            url = f'/acq/loan/{event.asset_hub_id}/'
        elif event.trade_id:
            url = f'/acq/trade/{event.trade_id}/'
        elif event.seller_id:
            url = f'/acq/seller/{event.seller_id}/'
        
        events.append({
            'id': f'custom:{event.id}',
            'title': event.title,
            'date': event.date,
            'time': event.time,
            'description': event.description,
            'category': event.category,
            'source_model': 'CalendarEvent',
            'editable': bool(user is not None and event.created_by_id and event.created_by_id == user.id),
            'url': url
        })
    
    return events


class CustomCalendarEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on custom calendar events.
    
    What: DRF ModelViewSet providing full CRUD for CalendarEvent model
    Why: Users need to create/edit/delete custom calendar events through the UI
    Where: Registered at /api/core/calendar/events/custom/ in core/urls.py
    How: Uses CustomCalendarEventSerializer from serial_co_calendar.py
    
    Endpoints:
        GET    /api/core/calendar/events/custom/       - List all custom events
        POST   /api/core/calendar/events/custom/       - Create new custom event
        GET    /api/core/calendar/events/custom/<id>/  - Retrieve custom event
        PUT    /api/core/calendar/events/custom/<id>/  - Update custom event
        PATCH  /api/core/calendar/events/custom/<id>/  - Partial update custom event
        DELETE /api/core/calendar/events/custom/<id>/  - Delete custom event
    
    Query Parameters (for list):
        - start_date: Filter events on or after this date (YYYY-MM-DD)
        - end_date: Filter events on or before this date (YYYY-MM-DD)
        - seller_id: Filter by seller ID
        - trade_id: Filter by trade ID
        - asset_hub_id: Filter by asset hub ID
    
    Serializer: CustomCalendarEventSerializer (projectalphav1/core/serializers/serial_co_calendar.py)
    """
    queryset = CalendarEvent.objects.all()
    serializer_class = CustomCalendarEventSerializer
    permission_classes = [AllowAny]  # TODO: Add authentication when ready
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters.
        
        What: Applies filters to CalendarEvent queryset based on GET parameters
        Why: Frontend needs to filter events by date range or entity
        Where: Called automatically by DRF for list/retrieve operations
        How: Parses query params and applies Django ORM filters
        
        Allows filtering by date range, seller, trade, or asset.
        """
        queryset = super().get_queryset()

        user = _resolve_request_user(self.request)
        if user is None:
            queryset = queryset.filter(is_public=True)
        else:
            queryset = queryset.filter(Q(is_public=True) | Q(created_by=user))
        
        # Date range filters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass
        
        # Entity filters
        seller_id = self.request.query_params.get('seller_id')
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
        
        trade_id = self.request.query_params.get('trade_id')
        if trade_id:
            queryset = queryset.filter(trade_id=trade_id)
        
        asset_hub_id = self.request.query_params.get('asset_hub_id')
        if asset_hub_id:
            queryset = queryset.filter(asset_hub_id=asset_hub_id)

        is_reminder = self.request.query_params.get('is_reminder')
        if is_reminder is not None:
            is_reminder_bool = str(is_reminder).strip().lower() in {'1', 'true', 't', 'yes', 'y'}
            queryset = queryset.filter(is_reminder=is_reminder_bool)

        reason = self.request.query_params.get('reason')
        if reason:
            queryset = queryset.filter(reason=reason)

        mine = self.request.query_params.get('mine')
        if mine is not None and str(mine).strip().lower() in {'1', 'true', 't', 'yes', 'y'}:
            if user is None:
                queryset = queryset.none()
            else:
                queryset = queryset.filter(created_by=user)
        
        return queryset.order_by('date', 'time')
    
    def perform_create(self, serializer):
        """
        Save the custom event with the current user as creator.
        
        What: Intercepts save operation to set created_by field
        Why: Track which user created each calendar event for audit trail
        Where: Called automatically by DRF during POST operations
        How: Checks if user is authenticated and sets created_by before save
        """
        user = _resolve_request_user(self.request)
        if user is not None:
            serializer.save(created_by=user)
        else:
            serializer.save(is_public=True)

    def perform_update(self, serializer):  # type: ignore[override]
        user = _resolve_request_user(self.request)
        if user is None:
            raise PermissionDenied('Authentication required')
        if serializer.instance.created_by_id != user.id:
            raise PermissionDenied('Only the creator can edit this event')
        serializer.save()

    def perform_destroy(self, instance):  # type: ignore[override]
        user = _resolve_request_user(self.request)
        if user is None:
            raise PermissionDenied('Authentication required')
        if instance.created_by_id != user.id:
            raise PermissionDenied('Only the creator can delete this event')
        instance.delete()
