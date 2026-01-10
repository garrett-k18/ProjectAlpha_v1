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
    Custom tasks created by users.
    
    All CalendarEvent records are tasks. Other event types (liquidations, trades, etc.)
    come from their respective models and are displayed in calendar views but not stored here.
    Users can create, edit, and delete these tasks directly from the calendar widget.
    
    Fields:
    - title: Task name/description (optional, auto-generated from task_type)
    - date: Task due date
    - time: Display time (e.g., "9:00 AM - 10:00 AM" or "All Day")
    - description: Additional task details
    - task_type: Type of task (TaskType enum)
    - priority: Task priority level (Priority enum)
    - created_by: User who created the task
    - assigned_to: User assigned to this task (for notifications)
    - seller: Optional link to a seller (for seller-specific tasks)
    - trade: Optional link to a trade (for trade-specific tasks)
    - asset_hub: Optional link to a specific asset
    - is_reminder: Flag to indicate if this is a reminder/alert
    - completed: Flag to indicate if this task is finished
    """

    class TaskType(models.TextChoices):
        """Task types - all CalendarEvent records are tasks"""
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
    
    # Task type - all CalendarEvents are tasks
    task_type = models.CharField(
        max_length=50,
        choices=TaskType.choices,
        default=TaskType.FOLLOW_UP,
        db_index=True,
        help_text="Type of task"
    )
    
    # Task priority
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
            models.Index(fields=['task_type', 'date']),
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
        
        # All CalendarEvents are tasks, so priority is always valid
        pass
        
    
    def save(self, *args, **kwargs):
        """Override save to run clean validation"""
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if this event is overdue (past date and not completed)"""
        from datetime import date
        return self.date < date.today() and not self.completed
    
    @property
    def display_priority(self):
        """Return priority with fallback for display"""
        return self.get_priority_display() if self.priority else 'Normal'
