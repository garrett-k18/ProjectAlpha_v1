"""
Django Admin configuration for CalendarEvent model.
Allows viewing and managing user-created calendar events through the admin interface.
"""
from django.contrib import admin
from core.models import CalendarEvent


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    """
    Admin configuration for CalendarEvent model.
    
    Displays user-created calendar events with filtering and search capabilities.
    """
    list_display = (
        'id',
        'title',
        'date',
        'time',
        'category',
        'seller',
        'trade',
        'asset_hub',
        'is_reminder',
        'created_by',
        'created_at',
    )
    
    list_filter = (
        'category',
        'is_reminder',
        'date',
        'created_at',
    )
    
    search_fields = (
        'title',
        'description',
        'seller__seller_name',
        'trade__trade_name',
    )
    
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    date_hierarchy = 'date'
    
    list_per_page = 5
    
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'date', 'time', 'description', 'category', 'is_reminder')
        }),
        ('Relationships', {
            'fields': ('seller', 'trade', 'asset_hub'),
            'description': 'Optional links to business entities'
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Automatically set created_by to the current user if not already set.
        """
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
