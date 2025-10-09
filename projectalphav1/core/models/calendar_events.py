"""
CalendarEvent Model
Stores user-created calendar events that don't belong to specific loan/asset models.
This allows users to add custom events (meetings, deadlines, reminders) directly through the calendar.

Model-based dates (maturity, FC dates, etc.) are read-only and pulled from their source models.
Custom events created here can be edited/deleted through the calendar interface.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CalendarEvent(models.Model):
    """
    Custom calendar events created by users.
    
    These are separate from model-based dates (which are read-only in the calendar).
    Users can create, edit, and delete these events directly from the calendar widget.
    
    Fields:
    - title: Event name/description
    - date: Event date
    - time: Display time (e.g., "9:00 AM - 10:00 AM" or "All Day")
    - description: Additional details
    - category: Bootstrap color class for visual categorization
    - created_by: User who created the event
    - seller: Optional link to a seller (for seller-specific events)
    - trade: Optional link to a trade (for trade-specific events)
    - asset_hub: Optional link to a specific asset
    - is_reminder: Flag to indicate if this is a reminder/alert
    """
    
    # Event details
    title = models.CharField(
        max_length=255,
        help_text="Event title/description"
    )
    
    date = models.DateField(
        help_text="Event date"
    )
    
    time = models.CharField(
        max_length=50,
        default="All Day",
        help_text="Event time (e.g., '9:00 AM - 10:00 AM' or 'All Day')"
    )
    
    description = models.TextField(
        blank=True,
        default="",
        help_text="Additional event details"
    )
    
    # Visual category (Bootstrap color class)
    CATEGORY_CHOICES = [
        ('bg-primary', 'Primary (Blue)'),
        ('bg-success', 'Success (Green)'),
        ('bg-info', 'Info (Cyan)'),
        ('bg-warning', 'Warning (Yellow)'),
        ('bg-danger', 'Danger (Red)'),
        ('bg-secondary', 'Secondary (Gray)'),
    ]
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='bg-primary',
        help_text="Event color category"
    )
    
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calendar_events',
        help_text="User who created this event"
    )
    
    # Optional relationships to business entities
    # These allow filtering events by seller, trade, or asset
    seller = models.ForeignKey(
        'acq_module.Seller',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='calendar_events',
        help_text="Link to seller (optional)"
    )
    
    trade = models.ForeignKey(
        'acq_module.Trade',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='calendar_events',
        help_text="Link to trade (optional)"
    )
    
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='calendar_events',
        help_text="Link to specific asset (optional)"
    )
    
    # Event flags
    is_reminder = models.BooleanField(
        default=False,
        help_text="Is this a reminder/alert?"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Calendar Event"
        verbose_name_plural = "Calendar Events"
        ordering = ['date', 'time']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['created_by', 'date']),
            models.Index(fields=['seller', 'date']),
            models.Index(fields=['trade', 'date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.date}"
