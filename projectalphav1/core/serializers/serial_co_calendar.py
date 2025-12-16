"""
Calendar Event Serializers

What: DRF serializers for calendar events from multiple sources + field configuration classes
Why: Unified calendar view needs to display dates from various models + custom user events
Where: projectalphav1/core/serializers/serial_co_calendar.py
How: Three serializers handle different use cases:
    1. CalendarEventReadSerializer - Read-only events from model date fields
    2. CustomCalendarEventSerializer - CRUD for user-created CalendarEvent records
    3. UnifiedCalendarEventSerializer - Combined output for frontend calendar widget

Handles both:
1. Read-only events from model dates (SellerRawData, ServicerData, TradeLevelAssumption, etc.)
2. Writable custom events (CalendarEvent model)

Date Field Sources:
- SellerRawData: maturity dates, foreclosure dates, modification dates
- ServicerLoanData: payment dates, actual_fc_sale_date, bankruptcy dates
- Trade: created_at, milestone dates
- TradeLevelAssumption: bid_date, settlement_date
- CalendarEvent: user-created custom events

TO ADD/REMOVE CALENDAR DATE FIELDS:
Edit the FIELDS list in the appropriate config class below (SellerRawDataCalendarFields, etc.)
"""
from rest_framework import serializers
from django.utils import timezone
from core.models import CalendarEvent
from core.views.view_co_notifications import _resolve_request_user


# ============================================================================
# CALENDAR FIELD CONFIGURATION - SINGLE PLACE TO ADD/REMOVE DATE FIELDS
# ============================================================================
# What: Simple list of date fields to show on calendar
# Why: One place to add/remove fields - no complex classes or methods
# Where: Used by view_co_calendar.py
# How: Just add lines like: ('SellerRawData', 'maturity_date', 'Maturity', 'deadline')
#
# TO ADD A DATE FIELD TO CALENDAR:
# 1. Add one line below in format: (Model, field_name, title, event_type)
# 2. Done!
#
# TO REMOVE A DATE FIELD:
# 1. Delete or comment out the line
# 2. Done!
#
# Format: (ModelName, field_name, display_title, event_type)
#
# Event Types (semantic - frontend maps to colors):
#   'actual_liquidation'     - Actual foreclosure sales
#   'projected_liquidation'  - Projected/scheduled FC sales
#   'bid_date'              - Bid submission deadlines
#   'settlement_date'       - Settlement dates
#   'milestone'             - Other important milestones
#
# Note: Frontend controls actual colors/styling - backend only sends semantic types
# ============================================================================

CALENDAR_DATE_FIELDS = [
    # Format: (ModelName, field_name, display_title, event_type)
    
    # SellerRawData fields
    # ('SellerRawData', 'fc_sale_date', 'Projected FC Sale', 'projected_liquidation'),
    
    # ServicerLoanData fields - from am_module/models/servicers.py
    ('ServicerLoanData', 'actual_fc_sale_date', 'Liquidation', 'actual_liquidation'),
    
    # TradeLevelAssumption fields - from acq_module/models/assumptions.py
    ('TradeLevelAssumption', 'bid_date', 'Bid Date', 'bid_date'),
    ('TradeLevelAssumption', 'settlement_date', 'Settlement', 'settlement_date'),
    
    # Add more fields here - one line per field
]


# ============================================================================
# CALENDAR EVENT SERIALIZERS
# ============================================================================


class CalendarEventReadSerializer(serializers.Serializer):
    """
    Read-only serializer for calendar events aggregated from various models.
    
    What: Serializes date fields from any model into standardized calendar events
    Why: Calendar needs unified format regardless of source model
    Where: Used by view_co_calendar.py view functions (_get_seller_raw_data_events, etc.)
    How: Accepts dict with standardized keys, validates, and returns JSON for frontend
    
    Used for displaying model-based dates (maturity, FC dates, etc.) in the calendar.
    These events cannot be edited through the calendar - they're read from source models.
    
    Fields:
    - id: Unique identifier (format: "model_type:pk:field_name") - prevents duplicates
    - title: Event title/description - displayed on calendar tile
    - date: Event date (YYYY-MM-DD format) - required for calendar positioning
    - time: Display time (optional, defaults to "All Day") - shown in event details
    - description: Additional details about the event - tooltip/modal content
    - category: Bootstrap color class (bg-primary, bg-success, etc.) - visual categorization
    - source_model: Which model this event came from - for debugging/filtering
    - source_id: Primary key of the source record - enables drill-down navigation
    - url: Optional link to view the related record - click-through navigation
    - editable: Always False for model-based events - prevents accidental edits
    
    Example Input:
    {
        'id': 'servicer_data:123:actual_fc_sale_date',
        'title': 'FC Sale: 123 Main St',
        'date': datetime.date(2025, 10, 15),
        'time': 'All Day',
        'description': 'Actual foreclosure sale date',
        'category': 'bg-danger',
        'source_model': 'ServicerData',
        'source_id': 123,
        'url': '/am/loan/456/',
        'editable': False
    }
    """
    
    # Unique identifier for the event (composite key)
    # Format: "model_name:record_id:field_name" ensures uniqueness across all sources
    id = serializers.CharField(read_only=True)
    
    # Event display fields
    # Title is shown on the calendar tile - keep concise
    title = serializers.CharField(max_length=255)
    
    # Date is required - this is what positions the event on the calendar
    date = serializers.DateField()
    
    # Time is optional - defaults to "All Day" for date-only events
    time = serializers.CharField(max_length=50, default="All Day")
    
    # Description provides additional context in tooltips/modals
    description = serializers.CharField(max_length=500, allow_blank=True, default="")
    
    # Visual category (Bootstrap color class)
    # Options: bg-primary (blue), bg-success (green), bg-info (cyan), 
    #          bg-warning (yellow), bg-danger (red), bg-secondary (gray)
    category = serializers.CharField(max_length=50, default="bg-primary")
    
    # Metadata for tracking source
    # source_model: Name of the Django model this event came from
    source_model = serializers.CharField(max_length=100)
    
    # source_id: Primary key of the source record (enables navigation back to source)
    source_id = serializers.IntegerField()
    
    # url: Frontend route to view the related record (e.g., '/acq/loan/123/')
    url = serializers.CharField(max_length=500, allow_blank=True, default="")
    
    # Flag to indicate if this event can be edited
    # Always False for model-based events - they must be edited at the source
    editable = serializers.BooleanField(default=False, read_only=True)
    
    def validate_date(self, value):
        """
        Validate that the date is not None and is a valid date object.
        
        What: Ensures date field is valid before serialization
        Why: Prevents null dates from breaking the calendar widget
        Where: Called automatically during serialization
        How: Checks for None and validates date type
        """
        if value is None:
            raise serializers.ValidationError("Date cannot be null for calendar events.")
        return value
    
    def validate_category(self, value):
        """
        Validate that the category is a valid Bootstrap color class.
        
        What: Ensures category is a recognized Bootstrap class
        Why: Invalid classes break frontend styling
        Where: Called automatically during serialization
        How: Checks against allowed Bootstrap color classes
        """
        valid_categories = [
            'bg-primary', 'bg-success', 'bg-info', 
            'bg-warning', 'bg-danger', 'bg-secondary'
        ]
        if value not in valid_categories:
            # Default to bg-primary if invalid category provided
            return 'bg-primary'
        return value


class CustomCalendarEventSerializer(serializers.ModelSerializer):
    """
    Writable serializer for user-created calendar events (CalendarEvent model).
    
    What: Full CRUD serializer for CalendarEvent model records
    Why: Users need to create custom events (meetings, deadlines, reminders) in the calendar
    Where: Used by CustomCalendarEventViewSet in view_co_calendar.py
    How: ModelSerializer provides automatic validation and save logic
    
    These events can be created, edited, and deleted through the calendar interface.
    
    Used for custom events like:
    - Meetings with brokers/sellers
    - Bid submission deadlines
    - Follow-up reminders
    - Settlement dates
    - Court dates
    - Inspection appointments
    
    Key Differences from CalendarEventReadSerializer:
    - Writable (POST/PUT/PATCH/DELETE supported)
    - Backed by CalendarEvent model (persisted to database)
    - Can be linked to seller/trade/asset for context
    - Supports is_reminder flag for alerts
    - Tracks created_by user for audit trail
    """
    
    # Add editable flag - always True for custom events
    # What: Indicates this event can be modified through the calendar UI
    # Why: Frontend needs to know which events show edit/delete buttons
    editable = serializers.SerializerMethodField()
    
    # Add source_model for consistency with read-only events
    # What: Returns 'CalendarEvent' as the source model name
    # Why: Unified calendar view needs consistent source_model field
    source_model = serializers.SerializerMethodField()
    
    # Add url field (optional, can link to seller/trade/asset)
    # What: Generates navigation URL based on linked entity
    # Why: Clicking event should navigate to related seller/trade/asset
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = CalendarEvent
        fields = [
            'id',
            'title',
            'date',
            'time',
            'description',
            'category',
            'seller',
            'trade',
            'asset_hub',
            'is_reminder',
            'is_public',
            'reason',
            'created_by',
            'created_at',
            'updated_at',
            'editable',
            'source_model',
            'url',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_editable(self, obj):
        """
        Custom events are always editable.
        
        What: Returns True to indicate this event can be modified
        Why: Frontend uses this flag to show/hide edit/delete buttons
        Where: Called during serialization for each CalendarEvent instance
        How: Always returns True since custom events are user-created
        """
        request = self.context.get('request')
        if request is None:
            return False
        user = _resolve_request_user(request)
        if user is None:
            return False
        return bool(obj.created_by_id) and obj.created_by_id == user.id
    
    def get_source_model(self, obj):
        """
        Return 'CalendarEvent' as the source model.
        
        What: Returns the model name for this event
        Why: Unified calendar view needs consistent source_model field
        Where: Called during serialization for each CalendarEvent instance
        How: Returns static string 'CalendarEvent'
        """
        return 'CalendarEvent'
    
    def get_url(self, obj):
        """
        Generate URL based on linked entity.
        
        What: Builds frontend navigation URL from related entity
        Why: Clicking event should navigate to related seller/trade/asset
        Where: Called during serialization for each CalendarEvent instance
        How: Checks asset_hub, trade, seller in priority order and builds URL
        
        Priority:
        1. Asset-level URL (most specific)
        2. Trade-level URL
        3. Seller-level URL
        4. Empty string if no entity linked
        """
        # Asset-level link (most specific)
        if obj.asset_hub_id:
            return f'/acq/loan/{obj.asset_hub_id}/'
        # Trade-level link
        elif obj.trade_id:
            return f'/acq/trade/{obj.trade_id}/'
        # Seller-level link
        elif obj.seller_id:
            return f'/acq/seller/{obj.seller_id}/'
        # No entity linked - standalone event
        return ''
    
    def validate_date(self, value):
        """
        Validate that the date is not in the distant past.
        
        What: Ensures date is reasonable (not more than 5 years in past)
        Why: Prevents accidental entry of very old dates
        Where: Called automatically during validation
        How: Compares date to current date minus 5 years
        """
        from datetime import timedelta
        five_years_ago = timezone.now().date() - timedelta(days=365*5)
        if value < five_years_ago:
            raise serializers.ValidationError(
                f"Date cannot be more than 5 years in the past. Got: {value}"
            )
        return value
    
    def validate(self, attrs):
        """
        Cross-field validation.
        
        What: Validates that at most one entity (seller/trade/asset) is linked
        Why: Event should be linked to one entity or none, not multiple
        Where: Called automatically during validation
        How: Counts non-null entity fields and raises error if > 1
        """
        # Count how many entities are linked
        entity_count = sum([
            1 if attrs.get('seller') else 0,
            1 if attrs.get('trade') else 0,
            1 if attrs.get('asset_hub') else 0,
        ])
        
        # Allow 0 (standalone event) or 1 (linked to one entity)
        if entity_count > 1:
            raise serializers.ValidationError(
                "Event can only be linked to one entity (seller, trade, or asset)."
            )
        
        return attrs
    
    def create(self, validated_data):
        """
        Create a new calendar event.
        
        What: Creates new CalendarEvent record in database
        Why: Users need to add custom events through the calendar UI
        Where: Called by ViewSet when POST request is made
        How: Automatically sets created_by to current user if authenticated
        """
        # Get the current user from request context
        request = self.context.get('request')
        
        # Set created_by if user is authenticated
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        
        # Call parent create method to save to database
        return super().create(validated_data)


class UnifiedCalendarEventSerializer(serializers.Serializer):
    """
    Unified serializer that combines both read-only model events and writable custom events.
    
    What: Output-only serializer for combined calendar event list
    Why: Frontend calendar needs single unified format for all event types
    Where: Used by get_calendar_events() view in view_co_calendar.py
    How: Accepts list of dicts from various sources, validates, returns JSON array
    
    Used for the main calendar GET endpoint that returns all events.
    
    This serializer handles events from:
    1. Model date fields (SellerRawData, ServicerLoanData, etc.) - read-only
    2. Custom CalendarEvent records - editable
    
    All events are normalized to this common format regardless of source.
    
    Frontend Usage:
    - FullCalendar widget expects this exact structure
    - 'editable' field controls whether edit/delete buttons show
    - 'category' field determines event color on calendar
    - 'url' field enables click-through navigation
    
    Example Output:
    [
        {
            "id": "servicer_data:123:actual_fc_sale_date",
            "title": "FC Sale: 123 Main St",
            "date": "2025-10-15",
            "time": "All Day",
            "description": "Actual foreclosure sale date",
            "category": "bg-danger",
            "source_model": "ServicerData",
            "editable": false,
            "url": "/am/loan/456/"
        },
        {
            "id": "custom:789",
            "title": "Meeting with Broker",
            "date": "2025-10-20",
            "time": "2:00 PM - 3:00 PM",
            "description": "Discuss new portfolio",
            "category": "bg-primary",
            "source_model": "CalendarEvent",
            "editable": true,
            "url": "/acq/seller/10/"
        }
    ]
    """
    # Unique identifier - composite key for model events, 'custom:id' for CalendarEvents
    id = serializers.CharField()
    
    # Event title - displayed on calendar tile
    title = serializers.CharField()
    
    # Event date - required for calendar positioning (YYYY-MM-DD)
    date = serializers.DateField()
    
    # Event time - "All Day" or specific time range
    time = serializers.CharField()
    
    # Event description - shown in tooltip/modal
    description = serializers.CharField()
    
    # Bootstrap color class - determines event color on calendar
    category = serializers.CharField()
    
    # Source model name - for debugging and filtering
    source_model = serializers.CharField()
    
    # Editable flag - controls whether edit/delete buttons show
    editable = serializers.BooleanField()
    
    # Navigation URL - click-through to related record
    url = serializers.CharField(allow_blank=True)
