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
    - category: Semantic event type (EventCategory enum)
    - reason: Sub-category for follow-up tasks (TaskReason enum)
    - priority: Task priority level (Priority enum)
    - created_by: User who created the event
    - assigned_to: User assigned to this task (for notifications)
    - seller: Optional link to a seller (for seller-specific events)
    - trade: Optional link to a trade (for trade-specific events)
    - asset_hub: Optional link to a specific asset
    - is_reminder: Flag to indicate if this is a reminder/alert
    - completed: Flag to indicate if this task/event is finished
    """

    class EventCategory(models.TextChoices):
        """Semantic event categories - frontend maps these to colors"""
        REALIZED_LIQUIDATION = "realized_liquidation", "Realized Liquidation"
        PROJECTED_LIQUIDATION = "projected_liquidation", "Projected Liquidation"
        TRADE = "trade", "Trade"
        FOLLOW_UP = "follow_up", "Task"
        MILESTONE = "milestone", "Milestone"
    
    class TaskReason(models.TextChoices):
        """Sub-categories for follow-up tasks"""
        FOLLOW_UP = "follow_up", "Follow-up"
        NOD_NOI = "nod_noi", "NOD/NOI"
        FC_COUNSEL = "fc_counsel", "FC Counsel"
        ESCROW = "escrow", "Escrow"
        REO = "reo", "REO"
        DOCUMENT_REVIEW = "document_review", "Document Review"
        CONTACT_BORROWER = "contact_borrower", "Contact Borrower"
        LEGAL = "legal", "Legal"
        INSPECTION = "inspection", "Inspection"
        OTHER = "other", "Other"
    
    class Priority(models.TextChoices):
        """Task priority levels"""
        URGENT = "urgent", "Urgent"
        ROUTINE = "routine", "Routine"
        LOW = "low", "Low"
    
    # Event details
    title = models.CharField(
        max_length=255,
        db_index=True,
        blank=True,
        default="",
        help_text="Event title/description (optional - events tagged by category)"
    )
    
    date = models.DateField(
        db_index=True,
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
    
    # Semantic event category
    category = models.CharField(
        max_length=50,
        choices=EventCategory.choices,
        default=EventCategory.MILESTONE,
        db_index=True,
        help_text="Event category (frontend determines visual styling)"
    )
    
    # Task priority (for follow-up events)
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.ROUTINE,
        blank=True,
        null=True,
        help_text="Priority level for tasks"
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
    
    # User assignment/notification
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_calendar_events',
        help_text="User assigned to this task (for notifications)"
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

    completed = models.BooleanField(
        default=False,
        help_text="Has the task/event been completed?"
    )

    is_public = models.BooleanField(
        default=False,
        help_text="Visible to all users when true; otherwise private to creator",
    )

    reason = models.CharField(
        max_length=32,
        choices=TaskReason.choices,
        null=True,
        blank=True,
        help_text="Standardized task reason",
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Calendar Event"
        verbose_name_plural = "Calendar Events"
        ordering = ['date', 'time']
        constraints = [
            models.CheckConstraint(
                check=models.Q(date__gte='2020-01-01'),
                name='calendar_event_date_not_too_old'
            ),
        ]
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['created_by', 'date']),
            models.Index(fields=['assigned_to', 'date']),
            models.Index(fields=['seller', 'date']),
            models.Index(fields=['trade', 'date']),
            models.Index(fields=['asset_hub', 'date']),
            models.Index(fields=['category', 'date']),
            models.Index(fields=['priority', 'date']),
            models.Index(fields=['is_reminder', 'date']),
            models.Index(fields=['completed', 'date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.date}"
    
    def clean(self):
        """Custom validation for CalendarEvent"""
        from django.core.exceptions import ValidationError
        from datetime import date
        
        # Validate date is not too far in the past (more than 5 years)
        if self.date and self.date < date(2020, 1, 1):
            raise ValidationError({'date': 'Event date cannot be before 2020.'})
        
        # Validate priority is only set for follow-up tasks
        if self.priority and self.category != self.EventCategory.FOLLOW_UP:
            # Allow priority for any category - users might want to prioritize any event type
            pass
        
        # Validate reason is only set for follow-up tasks
        if self.reason and self.category != self.EventCategory.FOLLOW_UP:
            raise ValidationError({
                'reason': 'Task reason can only be set for follow-up tasks.'
            })
    
    def save(self, *args, **kwargs):
        """Override save to run clean validation"""
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if this event is overdue (past date and not completed)"""
        from datetime import date
        return self.date < date.today() and self.category == self.EventCategory.FOLLOW_UP
    
    @property
    def display_priority(self):
        """Return priority with fallback for display"""
        return self.get_priority_display() if self.priority else 'Normal'
