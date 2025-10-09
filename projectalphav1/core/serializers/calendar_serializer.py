"""
Calendar Event Serializers
Handles both:
1. Read-only events from model dates (SellerRawData, ServicerData, etc.)
2. Writable custom events (CalendarEvent model)
"""
from rest_framework import serializers
from core.models import CalendarEvent


class CalendarEventReadSerializer(serializers.Serializer):
    """
    Read-only serializer for calendar events aggregated from various models.
    Used for displaying model-based dates (maturity, FC dates, etc.) in the calendar.
    These events cannot be edited through the calendar - they're read from source models.
    
    Fields:
    - id: Unique identifier (format: "model_type:pk:field_name")
    - title: Event title/description
    - date: Event date (YYYY-MM-DD format)
    - time: Display time (optional, defaults to "All Day")
    - description: Additional details about the event
    - category: Bootstrap color class (bg-primary, bg-success, etc.)
    - source_model: Which model this event came from
    - source_id: Primary key of the source record
    - url: Optional link to view the related record
    - editable: Always False for model-based events
    """
    
    # Unique identifier for the event (composite key)
    id = serializers.CharField(read_only=True)
    
    # Event display fields
    title = serializers.CharField(max_length=255)
    date = serializers.DateField()
    time = serializers.CharField(max_length=50, default="All Day")
    description = serializers.CharField(max_length=500, allow_blank=True, default="")
    
    # Visual category (Bootstrap color class)
    category = serializers.CharField(max_length=50, default="bg-primary")
    
    # Metadata for tracking source
    source_model = serializers.CharField(max_length=100)
    source_id = serializers.IntegerField()
    url = serializers.CharField(max_length=500, allow_blank=True, default="")
    
    # Flag to indicate if this event can be edited
    editable = serializers.BooleanField(default=False, read_only=True)


class CustomCalendarEventSerializer(serializers.ModelSerializer):
    """
    Writable serializer for user-created calendar events (CalendarEvent model).
    These events can be created, edited, and deleted through the calendar interface.
    
    Used for custom events like:
    - Meetings
    - Deadlines
    - Reminders
    - Follow-ups
    """
    
    # Add editable flag
    editable = serializers.SerializerMethodField()
    
    # Add source_model for consistency with read-only events
    source_model = serializers.SerializerMethodField()
    
    # Add url field (optional, can link to seller/trade/asset)
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
            'created_by',
            'created_at',
            'updated_at',
            'editable',
            'source_model',
            'url',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_editable(self, obj):
        """Custom events are always editable"""
        return True
    
    def get_source_model(self, obj):
        """Return 'CalendarEvent' as the source model"""
        return 'CalendarEvent'
    
    def get_url(self, obj):
        """Generate URL based on linked entity"""
        if obj.asset_hub_id:
            return f'/acq/loan/{obj.asset_hub_id}/'
        elif obj.trade_id:
            return f'/acq/trade/{obj.trade_id}/'
        elif obj.seller_id:
            return f'/acq/seller/{obj.seller_id}/'
        return ''
    
    def create(self, validated_data):
        """
        Create a new calendar event.
        Automatically set created_by to the current user if available.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class UnifiedCalendarEventSerializer(serializers.Serializer):
    """
    Unified serializer that combines both read-only model events and writable custom events.
    Used for the main calendar GET endpoint that returns all events.
    """
    id = serializers.CharField()
    title = serializers.CharField()
    date = serializers.DateField()
    time = serializers.CharField()
    description = serializers.CharField()
    category = serializers.CharField()
    source_model = serializers.CharField()
    editable = serializers.BooleanField()
    url = serializers.CharField(allow_blank=True)
