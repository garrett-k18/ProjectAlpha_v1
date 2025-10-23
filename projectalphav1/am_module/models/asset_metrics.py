# ============================================================
# PHASE 2: MODEL REMOVED
# This model class has been commented out to generate deletion migration.
# All code references were removed in Phase 1.
# REPLACEMENT: Use AMMetrics model instead (am_module.models.am_data)
# ============================================================

from django.db import models  # Django ORM base class and field types
from django.utils import timezone  # Timezone-aware date utilities (localdate)

# class AssetMetrics(models.Model): #deprecated delete in PRod
#     """
#     AssetMetrics tracks performance-related attributes for a single boarded asset.
#     It is a strict 1:1 with AssetIdHub (asset hub id as primary key).
#     """
#
#     # One-to-one link to the Asset Hub record (hub-first architecture).
#     # We share the same PK as the hub to enforce strict 1:1 by hub id.
#     asset_hub = models.OneToOneField(
#         'core.AssetIdHub',              # Stable hub id source of truth
#         on_delete=models.PROTECT,       # Protect hub integrity; do not cascade delete
#         related_name='am_metrics',      # Reverse accessor: hub.am_metrics
#         primary_key=True,               # PK equals hub id
#         help_text='The AssetIdHub this metrics record belongs to.'
#     )
#
#     # Required purchase date (cannot be null or blank) as requested.
#     purchase_date = models.DateField(
#         null=False,
#         blank=False,
#         help_text="The date the asset was purchased (required)."
#     )
#
#     # Audit timestamps (common best practice)
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         help_text="When this metrics record was created."
#     )
#     updated_at = models.DateTimeField(
#         auto_now=True,
#         help_text="When this metrics record was last updated."
#     )
#
#     class Meta:
#         verbose_name = "Asset Metrics"
#         verbose_name_plural = "Asset Metrics"
#         ordering = ["-created_at"]  # Newest first for convenience
#         indexes = [
#             models.Index(fields=["purchase_date"]),  # Efficient date range queries
#         ]
#
#     @property
#     def time_held_days(self) -> int:
#         """
#         Computed property (not stored in DB):
#         Returns the number of days held = today - purchase_date, clamped to 0.
#         Uses timezone.localdate() to respect Django's timezone configuration.
#         """
#         today = timezone.localdate()  # current local date per Django settings
#         delta_days = (today - self.purchase_date).days  # difference in days (int)
#         return max(0, delta_days)  # never return negative values
#
#     def __str__(self) -> str:
#         """Readable string for admin/debugging."""
#         return f"AssetMetrics(asset_id={self.pk}, time_held_days={self.time_held_days})"