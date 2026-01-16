"""
model_am_customLists.py
-----------------------
Custom list support for Asset Management (AM) module.

WHAT: Defines CustomAssetList model to store user-created asset lists.
WHY: Users need to group assets into reusable lists from the AM grid.
HOW: Store list metadata (name/description/owner) and a many-to-many
     relationship to AssetIdHub records.
"""

from django.conf import settings
from django.db import models

from core.models.model_co_assetIdHub import AssetIdHub


class CustomAssetList(models.Model):
    """
    CustomAssetList
    --------------
    WHAT: Named list of assets created by a user.
    WHY: Enables "My Lists" functionality for AM workflows.
    HOW: Many-to-many with AssetIdHub plus basic metadata fields.
    """

    # Human-readable list name (required)
    name = models.CharField(max_length=120)

    # Optional description to clarify list purpose
    description = models.TextField(blank=True)

    # Owner of the list (nullable to allow system/global lists)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="am_custom_lists",
    )

    # Assets contained in this list (can be empty at creation time)
    assets = models.ManyToManyField(
        AssetIdHub,
        related_name="am_custom_lists",
        blank=True,
    )

    # Timestamps for audit/history
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure lists are ordered with newest first by default
        ordering = ["-created_at"]
        verbose_name = "Custom Asset List"
        verbose_name_plural = "Custom Asset Lists"

    def __str__(self) -> str:
        # Provide a readable label for admin/debugging
        return f"{self.name}"
