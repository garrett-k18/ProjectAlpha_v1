from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    class EventType(models.TextChoices):
        TRADE_IMPORT = "trade_import", "Trade Import"
        TASK_CHANGED = "task_changed", "Task Changed"
        ASSET_LIQUIDATED = "asset_liquidated", "Asset Liquidated"

    event_type = models.CharField(max_length=64, choices=EventType.choices, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    asset_hub = models.ForeignKey(
        "core.AssetIdHub",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notifications",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_notifications",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["asset_hub", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type}: {self.title}"


class NotificationRead(models.Model):
    notification = models.ForeignKey(
        "core.Notification",
        on_delete=models.CASCADE,
        related_name="reads",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_reads",
    )
    read_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["notification", "user"], name="uniq_notification_user"),
        ]
        indexes = [
            models.Index(fields=["user", "read_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} read {self.notification_id}"
