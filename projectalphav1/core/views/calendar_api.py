"""
Calendar API Views
Handles both:
1. Read-only events from model dates (SellerRawData, ServicerData, etc.)
2. CRUD operations for custom calendar events (CalendarEvent model)

Endpoints:
    GET    /api/core/calendar/events/              - List all events (model + custom)
    POST   /api/core/calendar/events/custom/       - Create custom event
    GET    /api/core/calendar/events/custom/<id>/  - Get custom event
    PUT    /api/core/calendar/events/custom/<id>/  - Update custom event
    DELETE /api/core/calendar/events/custom/<id>/  - Delete custom event
"""
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.db.models import Q

# Import models that contain date fields
from acq_module.models.seller import SellerRawData, Seller, Trade
from acq_module.models.assumptions import TradeLevelAssumption
from am_module.models.servicers import ServicerLoanData as ServicerData
from core.models import CalendarEvent
from core.serializers.calendar_serializer import (
    CalendarEventReadSerializer,
    CustomCalendarEventSerializer,
    UnifiedCalendarEventSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])  # TODO: Add authentication when ready
def get_calendar_events(request):
    """
    Aggregates calendar events from various models across the application.
    
    Query Parameters:
    - start_date (optional): Filter events on or after this date (YYYY-MM-DD)
    - end_date (optional): Filter events on or before this date (YYYY-MM-DD)
    - seller_id (optional): Filter events for a specific seller
    - trade_id (optional): Filter events for a specific trade
    - categories (optional): Comma-separated list of event categories to include
    
    Returns:
        List of calendar events with standardized format
    """
    
    # Parse query parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    seller_id = request.GET.get('seller_id')
    trade_id = request.GET.get('trade_id')
    categories_param = request.GET.get('categories')
    
    # Convert date strings to date objects
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
    categories_filter = None
    if categories_param:
        categories_filter = [cat.strip() for cat in categories_param.split(',')]
    
    # Collect events from various sources
    events = []
    
    # 1. SellerRawData - Foreclosure dates, maturity dates, modification dates
    events.extend(_get_seller_raw_data_events(start_date, end_date, seller_id, trade_id))
    
    # 2. ServicerData - Payment dates, maturity dates, bankruptcy dates
    events.extend(_get_servicer_data_events(start_date, end_date, seller_id, trade_id))
    
    # 3. Trade-level events (created dates, important milestones)
    events.extend(_get_trade_events(start_date, end_date, seller_id, trade_id))
    
    # 4. TradeLevelAssumption dates (bid_date, settlement_date)
    events.extend(_get_trade_assumption_events(start_date, end_date, seller_id, trade_id))
    
    # 5. Custom CalendarEvent records (user-created events)
    events.extend(_get_custom_calendar_events(start_date, end_date, seller_id, trade_id))
    
    # Filter by categories if specified
    if categories_filter:
        events = [e for e in events if e.get('category') in categories_filter]
    
    # Serialize and return
    serializer = UnifiedCalendarEventSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def _get_seller_raw_data_events(start_date=None, end_date=None, seller_id=None, trade_id=None):
    """
    Extract calendar events from SellerRawData model.
    Includes: maturity dates, foreclosure dates, modification dates, payment dates
    """
    events = []
    
    # Build queryset with filters
    queryset = SellerRawData.objects.select_related('seller', 'trade').all()
    
    if seller_id:
        queryset = queryset.filter(seller_id=seller_id)
    if trade_id:
        queryset = queryset.filter(trade_id=trade_id)
    
    # Define which date fields to extract and their display properties
    # Format: (field_name, title_template, category, description_template)
    # Currently limited to key dates - more can be added later
    date_fields = [
        # Currently no date fields from SellerRawData - will add as needed
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
                    'url': f'/acq/loan/{record.asset_hub_id}/'
                })
    
    return events


def _get_servicer_data_events(start_date=None, end_date=None, seller_id=None, trade_id=None):
    """
    Extract calendar events from ServicerData model.
    Includes: payment dates, maturity dates, bankruptcy dates
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
    
    # Define date fields to extract from ServicerData
    # Format: (field_name, title_template, category, description_template)
    # Currently limited to actual_fc_sale_date - more can be added later
    date_fields = [
        ('actual_fc_sale_date', 'FC Sale: {address}', 'bg-danger', 'Actual foreclosure sale date'),
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
                    'description': desc_template.format(address=address),
                    'category': category,
                    'source_model': 'ServicerData',
                    'source_id': record.id,
                    'url': f'/am/loan/{record.asset_hub_id}/' if record.asset_hub_id else ''
                })
    
    return events


def _get_trade_events(start_date=None, end_date=None, seller_id=None, trade_id=None):
    """
    Extract calendar events from Trade model.
    Includes: trade creation dates, important milestones
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
                'description': f'Trade {trade.trade_name} created for {trade.seller.seller_name if trade.seller else "Unknown Seller"}',
                'category': 'bg-primary',
                'source_model': 'Trade',
                'source_id': trade.id,
                'url': f'/acq/trade/{trade.id}/'
            })
    
    return events


def _get_trade_assumption_events(start_date=None, end_date=None, seller_id=None, trade_id=None):
    """
    Extract calendar events from TradeLevelAssumption model.
    Includes: bid_date, settlement_date
    """
    events = []
    
    # Build queryset with filters
    queryset = TradeLevelAssumption.objects.select_related('trade', 'trade__seller').all()
    
    if seller_id:
        queryset = queryset.filter(trade__seller_id=seller_id)
    if trade_id:
        queryset = queryset.filter(trade_id=trade_id)
    
    # Define date fields to extract from TradeLevelAssumption
    # Format: (field_name, title_template, category, description_template)
    date_fields = [
        ('bid_date', 'Bid Date: {trade_name}', 'bg-primary', 'Bid submitted for {trade_name}'),
        ('settlement_date', 'Settlement: {trade_name}', 'bg-success', 'Settlement date for {trade_name}'),
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


def _get_custom_calendar_events(start_date=None, end_date=None, seller_id=None, trade_id=None):
    """
    Extract calendar events from CalendarEvent model (user-created custom events).
    These events are editable through the calendar interface.
    """
    events = []
    
    # Build queryset with filters
    queryset = CalendarEvent.objects.all()
    
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
            'editable': True,  # Custom events are always editable
            'url': url
        })
    
    return events


class CustomCalendarEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on custom calendar events.
    
    Endpoints:
        GET    /api/core/calendar/events/custom/       - List all custom events
        POST   /api/core/calendar/events/custom/       - Create new custom event
        GET    /api/core/calendar/events/custom/<id>/  - Retrieve custom event
        PUT    /api/core/calendar/events/custom/<id>/  - Update custom event
        PATCH  /api/core/calendar/events/custom/<id>/  - Partial update custom event
        DELETE /api/core/calendar/events/custom/<id>/  - Delete custom event
    
    Query Parameters (for list):
        - start_date: Filter events on or after this date
        - end_date: Filter events on or before this date
        - seller_id: Filter by seller
        - trade_id: Filter by trade
        - asset_hub_id: Filter by asset
    """
    queryset = CalendarEvent.objects.all()
    serializer_class = CustomCalendarEventSerializer
    permission_classes = [AllowAny]  # TODO: Add authentication when ready
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters.
        Allows filtering by date range, seller, trade, or asset.
        """
        queryset = super().get_queryset()
        
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
        
        return queryset.order_by('date', 'time')
    
    def perform_create(self, serializer):
        """
        Save the custom event with the current user as creator.
        """
        if self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()
