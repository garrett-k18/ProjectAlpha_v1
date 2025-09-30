"""
am_module.models.am_data

Purpose
-------
- Provide a small, flexible model to store auxiliary data used by the Asset Management module
  without bloating core models. Think of this as a light-weight configuration/metadata store
  for per-asset or global records (e.g., notes, tags, computed snapshots, import metadata).

Docs reviewed
-------------
- Django model fields: https://docs.djangoproject.com/en/stable/ref/models/fields/
- Built-in JSONField: https://docs.djangoproject.com/en/stable/ref/models/fields/#jsonfield
- Indexes: https://docs.djangoproject.com/en/stable/ref/models/indexes/

Design
------
- We keep this model intentionally generic and composable.
- `scope` + `key` give you a simple namespacing pattern (e.g., scope="calc", key="npv_run").
- `asset` link is optional; rows can be global (asset=NULL) or tied to a specific asset.
- `payload` stores structured JSON for arbitrary attributes.
"""

from __future__ import annotations

from django.db import models  # Django ORM base class and field types
from datetime import date  # Core date type used to compute delinquency buckets
from django.utils import timezone  # Timezone-aware utilities
from django.conf import settings   # To reference AUTH_USER_MODEL
from django.contrib.contenttypes.models import ContentType  # For generic foreign keys
from django.contrib.contenttypes.fields import GenericForeignKey  # For generic relationships
from django.core.exceptions import ValidationError  # For model-level validation
import json                        # For serializing JSON diffs


class AMMetrics(models.Model):
    """Generic auxiliary data store for the Asset Mgmt module.

    Typical uses:
    - Store per-asset modeling snapshots or cached calculations
    - Persist import metadata, user notes, or UI preferences
    - Attach tags or lightweight annotations to assets

    Fields
    ------
    - asset_hub: optional relation to `AssetIdHub`. When NULL, record is global.
    - scope: short namespace (e.g., "calc", "ui", "import").
    - key: identifier within the scope (e.g., "npv_run", "grid_prefs").
    - payload: arbitrary JSON payload (dict/list/primitive) for flexible data.
    - created_at / updated_at: audit timestamps.
    """

    # Optional link to hub (canonical asset key); string path avoids app loading cycles
    asset_hub = models.ForeignKey(
        "core.AssetIdHub",
        on_delete=models.PROTECT,        # Preserve metrics if hub deletion is prevented
        related_name="ammetrics",       # Access via: hub.ammetrics.all()
        null=True,                       # Allow global rows (non-asset specific)
        blank=True,
        help_text="Optional hub this data belongs to (NULL for global entries).",
    )

    DELINQUENCY_STATUS_CHOICES = (
        ("current", "Current"),
        ("30", "30D"),
        ("60", "60D"),
        ("90", "90D"),
        ("120_plus", "120+D"),
    )

    delinquency_status = models.CharField(
        max_length=16,
        choices=DELINQUENCY_STATUS_CHOICES,
        default="current",
        help_text="Bucketed delinquency status derived from ServicerLoanData dates.",
    )

   

    # Audit timestamps (auto-maintained)
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated (any field).",
    )

    # Who last updated this record (optional; depends on caller passing user)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="updated_ammetrics",
        on_delete=models.SET_NULL,
        help_text="User who last updated this record (if known).",
    )

    class Meta:
        """Meta configuration for indexing and uniqueness constraints."""

        verbose_name = "AM Data"
        verbose_name_plural = "AM Data"

        # Common query accelerators (only on existing fields)
        indexes = [
            models.Index(fields=["asset_hub"]),
        ]

        ordering = ["-updated_at"]

    # ------------------------------------------------------------------
    # Helper methods (keep tiny and side-effect free)
    # ------------------------------------------------------------------
    def touch(self) -> None:
        """Lightweight manual bump of `updated_at` without changing payload.

        Use cases:
        - Mark an entry as "visited" or "refreshed" from a background job.
        """
        self.updated_at = timezone.now()
        self.save(update_fields=["updated_at"])  # Only updates this field

    def __str__(self) -> str:  # pragma: no cover - trivial
        """Readable string for admin/debugging."""
        hub_part = f"hub={getattr(self.asset_hub, 'pk', None)}" if self.asset_hub_id else "hub=GLOBAL"
        return f"AMMetrics({hub_part})"

    @staticmethod
    def _compute_delinquency_bucket(as_of: date | None, next_due: date | None) -> str:
        """Derive a delinquency bucket string from two dates.

        The logic follows standard mortgage servicing guidance where the number of
        days between the servicer's reporting `as_of` date and the contractual
        `next_due` payment date determines which delinquency bucket the loan
        currently resides in. Missing dates default to the "current" bucket so that
        the UI does not report a false delinquency.
        """

        # When either date is missing we treat the asset as current to avoid
        # misclassifying incomplete snapshots. This matches the business request to
        # only bucket when both reference dates are available.
        if as_of is None or next_due is None:
            return "current"

        # Calculate the integer day delta between the reporting snapshot and the
        # next due date. Positive values indicate delinquency days past due.
        day_delta = (as_of - next_due).days

        # Loans that are not yet past due (delta <= 0) remain in the current bucket.
        if day_delta <= 0:
            return "current"

        # 1–30 days delinquent map to the 30 day bucket.
        if day_delta <= 30:
            return "30"

        # 31–60 days delinquent map to the 60 day bucket.
        if day_delta <= 60:
            return "60"

        # 61–90 days delinquent map to the 90 day bucket.
        if day_delta <= 90:
            return "90"

        # Anything beyond 90 days is surfaced as 120+ to satisfy the specification.
        return "120_plus"

    def refresh_delinquency_status(self, snapshot: "ServicerLoanData" | None = None) -> str:
        """Update `delinquency_status` using the most recent servicer snapshot.

        Parameters
        ----------
        snapshot:
            Optional explicit `ServicerLoanData` instance. When omitted the latest
            record for the linked `asset_hub` (ordered by `as_of_date` then
            reporting period) is automatically selected. This keeps the helper easy
            to reuse in scheduled jobs or ad-hoc admin actions.

        Returns
        -------
        str
            The freshly derived delinquency status value that also gets persisted on
            this model instance.
        """

        # Import locally to avoid circular dependency at module import time since
        # `.servicers` also references AM modules.
        from .servicers import ServicerLoanData

        # Ensure we have a snapshot to use; if none was supplied, fetch the most
        # recent record for this asset hub. We rely on ordering by `as_of_date`,
        # then reporting period, and finally primary key to get deterministic
        # results.
        if snapshot is None and self.asset_hub_id:
            snapshot = (
                ServicerLoanData.objects
                .filter(asset_hub=self.asset_hub)
                .order_by('-as_of_date', '-reporting_year', '-reporting_month', '-pk')
                .first()
            )

        # Derive the bucket using the helper; fall back to "current" when no
        # snapshot is available.
        bucket = self._compute_delinquency_bucket(
            getattr(snapshot, 'as_of_date', None),
            getattr(snapshot, 'next_due_date', None),
        )

        # Persist the new bucket on the model so downstream consumers can rely on
        # the denormalized value without recomputation.
        self.delinquency_status = bucket
        self.save(update_fields=['delinquency_status', 'updated_at'])

        # Return the bucket to allow calling code to surface it immediately.
        return bucket

    # ---------------------------------------------------------------
    # Field-level change tracking
    # ---------------------------------------------------------------
    # Implementation note:
    # - We override save() to diff current values vs. DB snapshot for a tracked
    #   subset of fields and write a row-per-field change to AssetManagementMetricsChange.
    # - To attribute changes to a user, callers may pass an `actor` kwarg (preferred)
    #   or call `set_actor(user)` before save(). Admin/View code should do this.

    # Private attribute to hold acting user for this save call
    _actor = None  # type: ignore

    # Fields we track at a field-level (extend as needed)
    # Track only existing fields; extend as you add more columns
    TRACKED_FIELDS = ("asset_hub", "delinquency_status")

    def set_actor(self, user) -> None:
        """Attach the acting user to the instance for the next save()."""
        self._actor = user

    def save(self, *args, **kwargs):  # type: ignore[override]
        """Save with field-level audit logging.

        Supported extras:
        - kwargs['actor']: optional user performing the change (preferred)

        Behavior:
        - On create: sets updated_by = actor (if provided)
        - On update: compares tracked fields to prior DB values, logs 1 row per
          changed field to AssetManagementMetricsChange, and sets updated_by.
        """
        actor = kwargs.pop("actor", None) or getattr(self, "_actor", None)

        # Determine original state for diff if this is an update
        original = None
        if self.pk:
            try:
                original = type(self).objects.get(pk=self.pk)
            except type(self).DoesNotExist:
                original = None

        # Set updated_by based on actor
        if actor:
            self.updated_by = actor

        super().save(*args, **kwargs)

        # After save, if we had an original, compute diffs and log changes
        if original is not None:
            changed_at = timezone.now()
            for fname in self.TRACKED_FIELDS:
                # Fetch old/new values
                old_val = getattr(original, fname, None)
                new_val = getattr(self, fname, None)

                # Serialize values as text for consistent comparison/logging
                old_val_ser = str(old_val) if old_val is not None else None
                new_val_ser = str(new_val) if new_val is not None else None

                # Skip if no actual change
                if old_val_ser == new_val_ser:
                    continue

                AMMetricsChange.objects.create(
                    record=self,
                    asset_hub=self.asset_hub,
                    field_name=fname,
                    old_value=old_val_ser,
                    new_value=new_val_ser,
                    changed_at=changed_at,
                    changed_by=actor if actor and getattr(actor, "pk", None) else None,
                )


class AuditLog(models.Model):
    """Generic audit log for tracking changes to any model in the system.

    This model provides comprehensive field-level change tracking across all business
    entities in the Asset Management module. It uses Django's ContentType framework to
    create a single, unified audit table that can track changes to any model.

    ════════════════════════════════════════════════════════════════════════════════
    PURPOSE & BENEFITS:
    ════════════════════════════════════════════════════════════════════════════════

    🔍 COMPLIANCE & AUDITING:
       - Track all data changes for regulatory compliance
       - Maintain complete audit trail for financial transactions
       - Support forensic analysis of data modifications

    🛠️ DEBUGGING & TROUBLESHOOTING:
       - See exactly what changed, when, and by whom
       - Track field-level modifications for issue diagnosis
       - Monitor data integrity and unexpected changes

    📊 BUSINESS INTELLIGENCE:
       - Analyze modification patterns and user behavior
       - Generate reports on data update frequency
       - Track workflow progress and status changes

    🔐 SECURITY MONITORING:
       - Detect unauthorized or suspicious changes
       - Monitor user activity across sensitive data
       - Support incident response investigations

    ════════════════════════════════════════════════════════════════════════════════
    ARCHITECTURE:
    ════════════════════════════════════════════════════════════════════════════════

    Uses Django's GenericForeignKey pattern:
    - One audit table serves all models (REOData, FCSale, DIL, etc.)
    - ContentType + object_id uniquely identifies any model instance
    - Efficient querying across all audit entries

    ════════════════════════════════════════════════════════════════════════════════
    USAGE EXAMPLES:
    ════════════════════════════════════════════════════════════════════════════════

    AUTOMATIC TRACKING (via model save methods):
    ```python
    # In views/forms - set the user making changes
    reo_instance.save(actor=request.user)

    # Alternative - set user first, then save
    task.set_actor(user)
    task.save()
    ```

    MANUAL TRACKING (for custom logic):
    ```python
    # Direct audit logging
    AuditLog.log_change(
        instance=my_model_instance,
        field_name='status',
        old_value='pending',
        new_value='approved',
        changed_by=user,
        asset_hub=asset_hub  # optional
    )
    ```

    QUERYING AUDIT DATA:
    ```python
    # All changes for a specific asset
    AuditLog.objects.filter(asset_hub=hub)

    # All changes to a specific model
    AuditLog.objects.filter(content_type__model='reodata')

    # Changes by a specific user
    AuditLog.objects.filter(changed_by=user)

    # Status changes only
    AuditLog.objects.filter(field_name='task_type')

    # Recent changes (last 24 hours)
    from django.utils import timezone
    yesterday = timezone.now() - timezone.timedelta(days=1)
    AuditLog.objects.filter(changed_at__gte=yesterday)
    ```

    ════════════════════════════════════════════════════════════════════════════════
    INTEGRATION:
    ════════════════════════════════════════════════════════════════════════════════

    All outcome and task models in this file have been enhanced with automatic
    change tracking via custom save() methods. Every field modification is
    automatically logged to this table with:

    - What changed (field name)
    - Previous and new values
    - When it changed (timestamp)
    - Who made the change (user)
    - Which asset it relates to (hub reference)

    The system tracks changes to:
    - REOData, REOtask (property disposition)
    - FCSale, FCTask (foreclosure sales)
    - DIL, DILTask (deed-in-lieu)
    - ShortSale, ShortSaleTask (short sales)
    - Modification, ModificationTask (loan modifications)

    ════════════════════════════════════════════════════════════════════════════════
    ADMIN INTERFACE:
    ════════════════════════════════════════════════════════════════════════════════

    Access via Django Admin > AM Module > Audit Log Entries
    - Filter by model type (Content Type)
    - Filter by field name
    - Search by asset ID or field values
    - View complete change history with user attribution

    ════════════════════════════════════════════════════════════════════════════════
    PERFORMANCE CONSIDERATIONS:
    ════════════════════════════════════════════════════════════════════════════════

    - Optimized with database indexes on frequently queried fields
    - Only logs actual changes (not no-op updates)
    - Minimal performance impact on save operations
    - Efficient bulk queries for audit reporting
    """

    # Generic foreign key to any model instance
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Denormalized direct link to hub for easy filtering/reporting
    asset_hub = models.ForeignKey(
        "core.AssetIdHub",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Denormalized hub reference for direct filtering.",
    )

    # Name of the field that changed
    field_name = models.CharField(max_length=64, help_text="Field name that was updated.")

    # Previous and new values (serialized as text for consistency)
    old_value = models.TextField(null=True, blank=True, help_text="Previous value (as text/JSON).")
    new_value = models.TextField(null=True, blank=True, help_text="New value (as text/JSON).")

    # Who/when
    changed_at = models.DateTimeField(auto_now_add=True, help_text="When the change occurred.")
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="User who made the change (if known).",
    )

    class Meta:
        verbose_name = "Audit Log Entry"
        verbose_name_plural = "Audit Log Entries"
        indexes = [
            models.Index(fields=["content_type", "object_id", "changed_at"]),
            models.Index(fields=["field_name", "changed_at"]),
            models.Index(fields=["asset_hub", "changed_at"]),
            models.Index(fields=["changed_by", "changed_at"]),
        ]
        ordering = ["-changed_at", "-id"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        who = getattr(self.changed_by, "username", None) or "system"
        model_name = self.content_type.model if self.content_type else "Unknown"
        return f"{model_name}.{self.field_name} changed by {who} at {self.changed_at:%Y-%m-%d %H:%M:%S}"

    @classmethod
    def log_change(cls, instance, field_name, old_value, new_value, changed_by=None, asset_hub=None):
        """Helper method to create audit log entries.

        Args:
            instance: The model instance that was changed
            field_name: Name of the field that changed
            old_value: Previous value of the field
            new_value: New value of the field
            changed_by: User who made the change (optional)
            asset_hub: Asset hub reference (auto-detected if not provided)

        Returns:
            AuditLog: The created audit log entry

        Usage:
            AuditLog.log_change(
                instance=my_reo_instance,
                field_name='list_price',
                old_value=150000,
                new_value=160000,
                changed_by=request.user
            )
        """
        # Auto-detect asset_hub if the instance has one
        if not asset_hub and hasattr(instance, 'asset_hub'):
            asset_hub = instance.asset_hub

        return cls.objects.create(
            content_object=instance,
            asset_hub=asset_hub,
            field_name=field_name,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
            changed_by=changed_by,
        )


# DEPRECATED: AMMetricsChange - Use BaseChangeAudit pattern instead
# TODO: Remove this model in next major overhaul after data migration
# This model is kept for backward compatibility and to avoid migration issues
class AMMetricsChange(models.Model):
    """Field-level change audit log for `AMMetrics` records.
    
    DEPRECATED: This model uses the old pattern. New audit models should inherit
    from BaseChangeAudit for consistency. Will be removed in next major overhaul.
    """

    # Link back to the record that changed
    record = models.ForeignKey(
        AMMetrics,
        on_delete=models.CASCADE,
        related_name="changes",
        help_text="The metrics record this change belongs to.",
    )

    # Denormalized direct link to hub for easy filtering/reporting
    asset_hub = models.ForeignKey(
        "core.AssetIdHub",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ammetrics_changes",
        help_text="Denormalized hub reference for direct filtering.",
    )

    # Name of the field that changed
    field_name = models.CharField(max_length=64, help_text="Field name that was updated.")

    # Previous and new values (serialized as text for consistency)
    old_value = models.TextField(null=True, blank=True, help_text="Previous value (as text/JSON).")
    new_value = models.TextField(null=True, blank=True, help_text="New value (as text/JSON).")

    # Who/when
    changed_at = models.DateTimeField(auto_now_add=True, help_text="When the change occurred.")
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ammetrics_changes",
        help_text="User who made the change (if known).",
    )

    class Meta:
        verbose_name = "AM Metrics Change (Deprecated)"
        verbose_name_plural = "AM Metrics Changes (Deprecated)"
        indexes = [
            models.Index(fields=["record", "changed_at"]),
            models.Index(fields=["field_name", "changed_at"]),
            models.Index(fields=["asset_hub", "changed_at"]),
        ]
        ordering = ["-changed_at", "-id"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        who = getattr(self.changed_by, "username", None) or "system"
        return f"Change({self.field_name} by {who} at {self.changed_at:%Y-%m-%d %H:%M:%S})"




class AMNote(models.Model):
    """User-authored note attached to an AssetIdHub (many-to-one).

    Many notes can be attached to a single hub. We key to the hub directly to
    follow the hub-first architecture and avoid coupling to any particular spoke.
    """

    # Many-to-one to the hub (canonical asset key)
    asset_hub = models.ForeignKey(
        "core.AssetIdHub",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="am_notes",  # Access via: hub.am_notes.all()
        help_text="Many notes per AssetIdHub (hub is the canonical asset key).",
    )

    # Predefined single-select tag choices (simple dropdown)
    TAG_URGENT = "urgent"
    TAG_LEGAL = "legal"
    TAG_QC = "qc"
    TAG_OPS = "ops"
    TAG_INFO = "info"

    TAG_CHOICES = (
        (TAG_URGENT, "Urgent"),
        (TAG_LEGAL, "Legal"),
        (TAG_QC, "Quality Control"),
        (TAG_OPS, "Operations"),
        (TAG_INFO, "Info"),
    )

    # Note content
    body = models.TextField(
        help_text="Free-form note text for this asset.",
    )
    tag = models.CharField(
        max_length=32,
        choices=TAG_CHOICES,
        null=True,
        blank=True,
        help_text="Optional single tag for categorizing the note.",
    )

    # --- Context fields for scoping notes to outcome/task while storing centrally ---
    # Scope clarifies what the note is primarily attached to (asset, outcome, or specific task)
    SCOPE_ASSET = "asset"
    SCOPE_OUTCOME = "outcome"
    SCOPE_TASK = "task"
    SCOPE_CHOICES = (
        (SCOPE_ASSET, "Asset"),
        (SCOPE_OUTCOME, "Outcome"),
        (SCOPE_TASK, "Task"),
    )
    scope = models.CharField(
        max_length=16,
        choices=SCOPE_CHOICES,
        default=SCOPE_ASSET,
        help_text="Primary attachment context for this note (asset, outcome, or task).",
    )

    # Outcome context (nullable for pure asset-level notes)
    OUTCOME_DIL = "dil"
    OUTCOME_FC = "fc"
    OUTCOME_REO = "reo"
    OUTCOME_SHORT_SALE = "short_sale"
    OUTCOME_MODIFICATION = "modification"
    OUTCOME_CHOICES = (
        (OUTCOME_DIL, "Deed-in-Lieu"),
        (OUTCOME_FC, "Foreclosure"),
        (OUTCOME_REO, "REO"),
        (OUTCOME_SHORT_SALE, "Short Sale"),
        (OUTCOME_MODIFICATION, "Modification"),
    )
    context_outcome = models.CharField(
        max_length=32,
        choices=OUTCOME_CHOICES,
        null=True,
        blank=True,
        help_text="Outcome context this note relates to (nullable for asset-level notes).",
    )
    # Task context: generic type string and optional task row id for fine-grained linking
    context_task_type = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="Task type key this note relates to (e.g., 'eviction', 'owner_contacted').",
    )
    context_task_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="Optional specific task row id if tying directly to a task instance.",
    )
    
    pinned = models.BooleanField(
        default=False,
        help_text="Pin this note for prominence in UI.",
    )

    # Who/when
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this note was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this note was last updated.")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="created_am_notes",
        on_delete=models.SET_NULL,
        help_text="User who created this note (if known).",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="updated_am_notes",
        on_delete=models.SET_NULL,
        help_text="User who last updated this note (if known).",
    )

    class Meta:
        verbose_name = "AM Note"
        verbose_name_plural = "AM Notes"
        indexes = [
            models.Index(fields=["asset_hub", "pinned", "updated_at"]),
            # Additional indexes to accelerate common filters in unified/filtered views
            models.Index(fields=["asset_hub", "context_outcome", "updated_at"]),
            models.Index(fields=["asset_hub", "context_task_type", "updated_at"]),
            models.Index(fields=["asset_hub", "context_task_id", "updated_at"]),
        ]
        ordering = ["-pinned", "-updated_at", "-id"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        who = getattr(self.created_by, "username", None) or "anon"
        return f"AMNote({who}: {self.body[:32]}...)"


class REOData(models.Model):
    """Data about a REO property."""

    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='reo_data',
        help_text='1:1 with hub; REO data keyed by AssetIdHub.',
    )
    
    # Optional one-to-one link to a CRM directory entry (Broker contact)
    # Using string app label reference to avoid circular imports
    crm = models.OneToOneField(
        "core.MasterCRM",
        on_delete=models.SET_NULL,   # If broker entry is removed, preserve REOData but null the link
        null=True,
        blank=True,
        related_name="reo_record",  # Access from MasterCRM via: mastercrm.reo_record
        help_text="Linked CRM contact for this REO asset (optional).",
    )


    list_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="List price of the REO property (optional).",
    )

    list_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the property was listed (optional).",
    )   

    under_contract_flag = models.BooleanField(
        default=False,
        help_text="Whether the property is under contract (optional).",
    )   

    under_contract_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the property went under contract (optional).",
    )   

    contract_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Contract price of the REO property (optional).",
    )

    estimated_close_date = models.DateField(
        null=True,
        blank=True,
        help_text="Estimated close date of the REO property (optional).",
    )

    actual_close_date = models.DateField(
        null=True,
        blank=True,
        help_text="Actual close date of the REO property (optional).",
    )

    seller_credit_amt = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Seller credit amount (optional).",
    )

    # Enumerated purchase type options for clarity and data integrity
    PURCHASE_TYPE_CASH = "cash"
    PURCHASE_TYPE_FINANCING = "financing"
    PURCHASE_TYPE_SELLER_FINANCING = "seller_financing"

    PURCHASE_TYPE_CHOICES = (
        (PURCHASE_TYPE_CASH, "Cash"),
        (PURCHASE_TYPE_FINANCING, "Financing"),
        (PURCHASE_TYPE_SELLER_FINANCING, "Seller Financing"),
    )

    purchase_type = models.CharField(
        max_length=32,
        choices=PURCHASE_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="How the property was purchased (Cash, Financing, Seller Financing).",
    )

    gross_purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Gross purchase price of the REO property (optional).",
    )
    class Meta:
        verbose_name = "REO Data"
        verbose_name_plural = "REO Data"
        ordering = ["-list_date"]

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor
        
        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)
                
                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub,
                    )

class REOtask(models.Model):
    """Simple REO task tracker using Django's TextChoices.

    We use a nested TextChoices enum to define the allowed task types with
    a single source of truth for value+label. Extend later with hub FK,
    due dates, assignee, status, etc.
    Docs reviewed: https://docs.djangoproject.com/en/stable/ref/models/fields/#enumeration-types
    """

    class TaskType(models.TextChoices):
        """Canonical REO task types and their display labels."""
        EVICTION = "eviction", "Eviction"
        TRASHOUT = "trashout", "Trashout"
        RENOVATION = "renovation", "Renovation"
        MARKETING = "marketing", "Marketing"
        UNDER_CONTRACT = "under_contract", "Under Contract"
        SOLD = "sold", "Sold"

    # Selected task type (single-select). Use TaskType.<NAME> in code.
    task_type = models.CharField(
        max_length=20,                   # fits the longest value 'under_contract'
        choices=TaskType.choices,        # built-in mapping of value->label
        help_text=(
            "Type of REO task (Eviction, Trashout, Renovation, Marketing, Under Contract, Sold)."
        ),
    )

    # Direct link to the asset hub for simplified querying.
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='reo_tasks',
        help_text='The asset hub this REO task belongs to.',
    )

    # Link to the REO outcome record (many tasks per REOData)
    reo_outcome = models.ForeignKey(
        'am_module.REOData',
        on_delete=models.PROTECT,           # prevent deleting outcome while tasks exist
        related_name='tasks',               # access via: reo_data.tasks.all()
        help_text='The REO outcome record this task is associated with (many-to-one).',
    )

    # Minimal audit timestamps (used by serializers)
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this task was last updated.")

    class Meta:
        verbose_name = "REO Task"
        verbose_name_plural = "REO Tasks"
        ordering = ['-created_at', '-id']

    # Change tracking (match pattern used by other task models)
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )

class FCSale(models.Model):
    """Data about a foreclosure sale (hub-keyed 1:1)."""

    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='fc_sale',
        help_text='1:1 with hub; foreclosure sale keyed by AssetIdHub.',
    )
    
    # Optional association to a CRM contact/entity managing the FC
    crm = models.ForeignKey(
        "core.MasterCRM",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fc_sales",  # Access from MasterCRM via: crm.fc_sales.all()
        help_text="CRM contact associated with this foreclosure sale (optional).",
    )
    
    fc_sale_sched_date = models.DateField(
        null=True,
        blank=True,
        help_text="Scheduled date of the foreclosure sale (optional).",
    )

    fc_sale_actual_date = models.DateField(
        null=True,
        blank=True,
        help_text="Actual date of the foreclosure sale (optional).",
    )

    fc_bid_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Bid price of the foreclosure sale (optional).",
    )
    fc_sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Sale price of the foreclosure sale (optional).",
    )

    class Meta:
        verbose_name = "Foreclosure Sale"
        verbose_name_plural = "Foreclosure Sales"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor
        
        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)
                
                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )

class FCTask(models.Model):
    """Foreclosure workflow task linked to an `FCSale` record.

    Uses Django's TextChoices for well-defined stage values. Extend later with
    due dates, assignee, notes, etc.
    """

    class TaskType(models.TextChoices):
        NOD_NOI = "nod_noi", "NOD/NOI"
        FC_FILING = "fc_filing", "FC Filing"
        MEDIATION = "mediation", "Mediation"
        JUDGEMENT = "judgement", "Judgement"
        REDEMPTION = "redemption", "Redemption"
        SALE_SCHEDULED = "sale_scheduled", "Sale Scheduled"
        SOLD = "sold", "Sold"

    # Direct link to the asset hub for simplified querying.
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='fc_tasks',
        help_text='The asset hub this foreclosure task belongs to.',
    )

    # Link to the foreclosure sale record (many tasks per FCSale)
    fc_sale = models.ForeignKey(
        'am_module.FCSale',
        on_delete=models.PROTECT,           # prevent deleting sale while tasks exist
        related_name='tasks',               # access via: fc_sale.tasks.all()
        help_text='The FCSale record this task is associated with (many-to-one).',
    )

    # Selected stage
    task_type = models.CharField(
        max_length=32,
        choices=TaskType.choices,
        help_text='Foreclosure workflow stage for this task.',
    )

    # Minimal audit timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this task was last updated.")

    class Meta:
        verbose_name = "Foreclosure Task"
        verbose_name_plural = "Foreclosure Tasks"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor
        
        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)
                
                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )
    
class DIL(models.Model):
    """Data about a DIL (hub-keyed 1:1)."""
    
    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='dil',
        help_text='1:1 with hub; DIL keyed by AssetIdHub.',
    )
    
    # Optional association to a CRM contact/entity managing the DIL
    crm = models.ForeignKey(
        "core.MasterCRM",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dils",  # Access from MasterCRM via: crm.dils.all()
        help_text="CRM contact associated with this DIL (optional).",
    )
    
    dil_completion_date = models.DateField(
        null=True,
        blank=True,
        help_text="Completion date of the DIL (optional).",
    )
    
    dil_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average cost of the DIL (optional).",
    )
    
    cfk_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="CFK cost of the DIL (optional).",
    )

    class Meta:
        verbose_name = "Deed in Lieu (DIL)"
        verbose_name_plural = "Deeds in Lieu (DILs)"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor
        
        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)
                
                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )

class DILTask(models.Model):
    """DIL workflow task linked to a `DIL` record.

    Uses Django's TextChoices for well-defined stage values.
    """

    class TaskType(models.TextChoices):
        OWNER_CONTACTED = "owner_contacted", "Owner/Heirs contacted"
        # Explicit tag when borrower/heirs are not cooperating
        NO_COOPERATION = "no_cooperation", "No Cooperation"
        DRAFTED = "dil_drafted", "Deed-in-Lieu Drafted"
        SUCCESSFUL = "dil_successful", "Deed-in-Lieu Successful"

    # Direct link to the asset hub for simplified querying.
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='dil_tasks',
        help_text='The asset hub this DIL task belongs to.',
    )

    # Link to the DIL record (many tasks per DIL)
    dil = models.ForeignKey(
        'am_module.DIL',

        on_delete=models.PROTECT,
        related_name='tasks',
        help_text='The DIL record this task is associated with (many-to-one).',
    )

    # Selected stage
    task_type = models.CharField(
        max_length=32,
        choices=TaskType.choices,
        help_text='DIL workflow stage for this task.',
    )

    # Minimal audit timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this task was last updated.")

    class Meta:
        verbose_name = "DIL Task"
        verbose_name_plural = "DIL Tasks"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor
        
        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)
                
                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )

class ShortSale(models.Model):
    """Data about a short sale (hub-keyed 1:1)."""

    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='short_sale',
        help_text='1:1 with hub; short sale keyed by AssetIdHub.',
    )

    # Optional association to a CRM contact/entity managing the short sale
    crm = models.ForeignKey(
        "core.MasterCRM",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="short_sales",  # Access from MasterCRM via: crm.short_sales.all()
        help_text="CRM contact associated with this short sale (optional).",
    )

    

    acceptable_min_offer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Acceptable minimum offer for the short sale (optional).",
    )
        
    short_sale_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the short sale (optional).",
    )

    class Meta:
        verbose_name = "Short Sale"
        verbose_name_plural = "Short Sales"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor
        
        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)
                
                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )

class ShortSaleTask(models.Model):
    """Short Sale workflow task linked to a `ShortSale` record.

    Uses Django's TextChoices for well-defined stage values.
    """

    class TaskType(models.TextChoices):
        LIST_PRICE_ACCEPTED = "list_price_accepted", "List Price Accepted"
        LISTED = "listed", "Listed"
        UNDER_CONTRACT = "under_contract", "Under-Contract"
        SOLD = "sold", "Sold"

    # Direct link to the asset hub for simplified querying.
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='short_sale_tasks',
        help_text='The asset hub this short sale task belongs to.',
    )

    # Link to the ShortSale record (many tasks per ShortSale)
    short_sale = models.ForeignKey(
        'am_module.ShortSale',
        on_delete=models.PROTECT,
        related_name='tasks',
        help_text='The ShortSale record this task is associated with (many-to-one).',
    )

    # Selected stage
    task_type = models.CharField(
        max_length=32,
        choices=TaskType.choices,
        help_text='Short Sale workflow stage for this task.',
    )

    # Minimal audit timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this task was last updated.")

    class Meta:
        verbose_name = "Short Sale Task"
        verbose_name_plural = "Short Sale Tasks"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor
        
        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)
                
                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )

class Modification(models.Model):
    """Data about a modification (hub-keyed 1:1)."""
    
    # Enumerated payment type options for clarity and data integrity
    MOD_PAYMENT_PI = "pi"
    MOD_PAYMENT_IO = "io"
    MOD_PAYMENT_OTHER = "other"
    MODIFICATION_PAYMENT_CHOICES = (
        (MOD_PAYMENT_PI, "P&I"),
        (MOD_PAYMENT_IO, "Interest Only"),
        (MOD_PAYMENT_OTHER, "Other"),
    )

    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='modification',
        help_text='1:1 with hub; modification keyed by AssetIdHub.',
    )
    
    # Optional association to a CRM contact/entity managing the modification
    crm = models.ForeignKey(
        "core.MasterCRM",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="modifications",  # Access from MasterCRM via: crm.modifications.all()
        help_text="CRM contact associated with this modification (optional).",
    )
    
    modification_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the modification (optional).",
    )
    
    modification_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cost of the modification (optional).",
    )
    
    modification_upb = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="UPB of the modification (optional).",
    )

    modification_term = models.IntegerField(
        null=True,
        blank=True,
        help_text="Term of the modification (optional).",
    )

    modification_rate = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Rate of the modification (optional).",
    )
    
    modification_maturity_date = models.DateField(
        null=True,
        blank=True,
        help_text="Maturity date of the modification (optional).",
    )   

    modification_pi = models.CharField(
        max_length=32,
        choices=MODIFICATION_PAYMENT_CHOICES,
        null=True,
        blank=True,
        help_text="Payment of the modification (optional).",
    )

    modification_down_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Down payment of the modification (optional).",
    )

    class Meta:
        verbose_name = "Loan Modification"
        verbose_name_plural = "Loan Modifications"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor
        
        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)
                
                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )

class ModificationTask(models.Model):
    """Modification workflow task linked to a `Modification` record.

    Uses Django's TextChoices for well-defined stage values.
    """

    class TaskType(models.TextChoices):
        NEGOTIATIONS = "mod_negotiations", "Mod negotiations"
        ACCEPTED = "mod_accepted", "Mod Accepted"
        STARTED = "mod_started", "Mod Started"
        FAILED = "mod_failed", "Mod Failed"

    # Direct link to the asset hub for simplified querying.
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='modification_tasks',
        help_text='The asset hub this modification task belongs to.',
    )

    # Link to the Modification record (many tasks per Modification)
    modification = models.ForeignKey(
        'am_module.Modification',
        on_delete=models.PROTECT,
        related_name='tasks',
        help_text='The Modification record this task is associated with (many-to-one).',
    )

    # Selected stage
    task_type = models.CharField(
        max_length=32,
        choices=TaskType.choices,
        help_text='Modification workflow stage for this task.',
    )

    # Minimal audit timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this task was last updated.")

    class Meta:
        verbose_name = "Modification Task"
        verbose_name_plural = "Modification Tasks"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor
        
        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)
        
        # Log changes for all fields
        if original_values:
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)
                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )

class REOScope(models.Model):
    """Work orders / scopes / bids associated with a property (many-to-one).

    Stores vendor/contact information, scope dates, estimated totals, and notes.
    Each row ties to a single `AssetIdHub` and can optionally reference a
    `MasterCRM` vendor/contact record.
    """

    # Canonical asset key (many scopes per asset)
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='reo_scopes',
        help_text='The asset hub this scope/bid belongs to (many-to-one).',
    )

    # Optional link to CRM vendor/contact
    crm = models.ForeignKey(
        'core.MasterCRM',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reo_scopes',
        help_text='Optional CRM contact/vendor associated with this scope/bid.',
    )

    # Scope classification and optional link to a specific REO task (Trashout/Renovation)
    class ScopeKind(models.TextChoices):
        """Permitted scope categories for REO Scopes."""
        TRASHOUT = 'trashout', 'Trashout'
        RENOVATION = 'renovation', 'Renovation'

    scope_kind = models.CharField(
        max_length=16,
        choices=ScopeKind.choices,
        null=True,
        blank=True,
        help_text='Scope classification (Trashout or Renovation). Optional but recommended.',
    )

    reo_task = models.ForeignKey(
        'am_module.REOtask',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scopes',
        help_text='Optional link to the related REO task (Trashout/Renovation).',
    )

    # Vendor/contact snapshot fields
    vendor_name = models.CharField(
        max_length=255,
        help_text='Vendor/company name providing the scope/bid.',
    )
    contact_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Primary contact name (optional).',
    )
    contact_phone = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text='Primary contact phone (optional).',
    )
    contact_email = models.EmailField(
        null=True,
        blank=True,
        help_text='Primary contact email (optional).',
    )

    # Scope timing and totals
    scope_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date of the scope/bid (optional).',
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Total cost quoted or expected (optional).',
    )
    expected_completion = models.DateField(
        null=True,
        blank=True,
        help_text='Expected completion date (optional).',
    )

    # Free-form details
    notes = models.TextField(
        null=True,
        blank=True,
        help_text='Additional notes or itemization (optional).',
    )

    # Minimal audit timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text='When this scope record was created.')
    updated_at = models.DateTimeField(auto_now=True, help_text='When this scope record was last updated.')

    class Meta:
        verbose_name = 'REO Scope / Bid'
        verbose_name_plural = 'REO Scopes / Bids'
        indexes = [
            models.Index(fields=['asset_hub', 'created_at']),
            models.Index(fields=['asset_hub', 'scope_date']),
            models.Index(fields=['asset_hub', 'expected_completion']),
            models.Index(fields=['asset_hub', 'scope_kind']),
            models.Index(fields=['crm']),
            models.Index(fields=['reo_task']),
        ]
        ordering = ['-created_at', '-id']

    # Change tracking (pattern used across this module)
    _actor = None

    def set_actor(self, user):
        """Set the acting user for audit logging."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic field-level audit logging via `AuditLog`.
        Accepts optional kwarg `actor` to attribute the change to a user.
        """
        actor = kwargs.pop('actor', None) or self._actor

        # If a related REO task is provided and scope_kind is empty, infer from task_type.
        # We only infer for the allowed kinds to keep data clean.
        if getattr(self, 'reo_task_id', None) and not self.scope_kind:
            try:
                tt = getattr(self.reo_task, 'task_type', None)
                if tt in ('trashout', 'renovation'):
                    self.scope_kind = tt  # safe defaulting based on task type
            except Exception:
                pass  # Do not block save; validation below will catch inconsistencies

        # Run model validation before persisting to enforce integrity rules.
        self.full_clean()

        # Snapshot original values on update to compute diffs after save
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        super().save(*args, **kwargs)

        # Log changes for all fields that actually changed
        if original_values:
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub,
                    )