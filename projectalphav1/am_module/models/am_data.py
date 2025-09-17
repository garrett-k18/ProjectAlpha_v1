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
from django.utils import timezone  # Timezone-aware utilities
from django.conf import settings   # To reference AUTH_USER_MODEL
import json                        # For serializing JSON diffs


class AMMetrics(models.Model):
    """Generic auxiliary data store for the Asset Mgmt module.

    Typical uses:
    - Store per-asset modeling snapshots or cached calculations
    - Persist import metadata, user notes, or UI preferences
    - Attach tags or lightweight annotations to assets

    Fields
    ------
    - asset: optional relation to `SellerBoardedData`. When NULL, record is global.
    - scope: short namespace (e.g., "calc", "ui", "import").
    - key: identifier within the scope (e.g., "npv_run", "grid_prefs").
    - payload: arbitrary JSON payload (dict/list/primitive) for flexible data.
    - created_at / updated_at: audit timestamps.
    """

    # Optional link to a boarded asset; string path avoids app loading cycles
    asset = models.ForeignKey(
        "am_module.SellerBoardedData",  # Target model in same Django app
        on_delete=models.CASCADE,         # Delete AMData rows if the asset is deleted
        related_name="ammetrics",           # Reverse accessor: asset.ammetrics (QuerySet)
        null=True,                        # Allow global rows (non-asset specific)
        blank=True,
        help_text="Optional asset this data belongs to (NULL for global entries).",
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
            models.Index(fields=["asset"]),
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
        asset_part = f"asset={getattr(self.asset, 'pk', None)}" if self.asset_id else "asset=GLOBAL"
        return f"AMMetrics({asset_part})"

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
    TRACKED_FIELDS = ("asset", )

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
                    field_name=fname,
                    old_value=old_val_ser,
                    new_value=new_val_ser,
                    changed_at=changed_at,
                    changed_by=actor if actor and getattr(actor, "pk", None) else None,
                )


class AMMetricsChange(models.Model):
    """Field-level change audit log for `AMMetrics` records.

    One row per change, per field, capturing who changed it and when.
    """

    # Link back to the record that changed
    record = models.ForeignKey(
        AMMetrics,
        on_delete=models.CASCADE,
        related_name="changes",
        help_text="The metrics record this change belongs to.",
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
        indexes = [
            models.Index(fields=["record", "changed_at"]),
            models.Index(fields=["field_name", "changed_at"]),
        ]
        ordering = ["-changed_at", "-id"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        who = getattr(self.changed_by, "username", None) or "system"
        return f"Change({self.field_name} by {who} at {self.changed_at:%Y-%m-%d %H:%M:%S})"


class AMNote(models.Model):
    """User-authored note attached to a SellerBoardedData record (many-to-one).

    This is a simple note model to capture free-form annotations, with optional
    author and audit timestamps. Multiple notes can be attached to the same asset.
    """

    # Many-to-one to the boarded asset
    seller_boarded_data = models.ForeignKey(
        "am_module.SellerBoardedData",
        on_delete=models.CASCADE,
        related_name="am_notes",  # Access via: asset.am_notes.all()
        help_text="The SellerBoardedData this note belongs to.",
    )

    # Note content
    body = models.TextField(
        help_text="Free-form note text for this asset.",
    )

    # Optional pinned flag for UI surfaces
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
        indexes = [
            models.Index(fields=["seller_boarded_data", "pinned", "updated_at"]),
        ]
        ordering = ["-pinned", "-updated_at", "-id"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        who = getattr(self.created_by, "username", None) or "anon"
        return f"AMNote({who}: {self.body[:32]}...)"


class REOData(models.Model):
    """Data about a REO property."""

    asset = models.OneToOneField(
        "am_module.SellerBoardedData",
        on_delete=models.CASCADE,
        related_name="reo_data",
        help_text="The boarded asset this REO data belongs to.",
    )
    
    # Optional one-to-one link to a Broker CRM directory entry
    # Using string app label reference to avoid circular imports
    broker_crm = models.OneToOneField(
        "core.Brokercrm",
        on_delete=models.SET_NULL,   # If broker entry is removed, preserve REOData but null the link
        null=True,
        blank=True,
        related_name="reo_record",  # Access from Brokercrm via: brokercrm.reo_record
        help_text="Linked Broker CRM contact for this REO asset (optional).",
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
    # Note: No Meta ordering here because there is no `as_of_date` field on REOData.
    # If you want ordering, consider one of the existing date fields, e.g.,
    # ordering by most recent list_date or estimated_close_date.
    # class Meta:
    #     ordering = ["-list_date"]

class FCSale(models.Model):
    """Data about a foreclosure sale."""

    asset = models.OneToOneField(
        "am_module.SellerBoardedData",
        on_delete=models.CASCADE,
        related_name="fc_sale",
        help_text="The boarded asset this foreclosure sale belongs to.",
    )
    
    # Optional association to a Legal CRM contact/entity managing the FC
    legal_crm = models.ForeignKey(
        "core.LegalCRM",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fc_sales",  # Access from LegalCRM via: legalcrm.fc_sales.all()
        help_text="Legal entity/contact from CRM associated with this foreclosure sale (optional).",
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
    
        