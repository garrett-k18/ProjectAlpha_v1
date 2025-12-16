from django.conf import settings
from django.db import models


class UserAssetAccess(models.Model):
    class AccessRole(models.TextChoices):
        AM_MANAGER = 'am_manager', 'AM Manager'
        REO_MANAGER = 'reo_manager', 'REO Manager'

    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.CASCADE,
        related_name='user_access_assignments',
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='asset_access_assignments',
    )

    role = models.CharField(
        max_length=32,
        choices=AccessRole.choices,
        db_index=True,
    )

    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_admin_user_asset_access'
        ordering = ['-created_at']
        unique_together = [['asset_hub', 'user', 'role']]
        indexes = [
            models.Index(fields=['asset_hub', 'role']),
            models.Index(fields=['user', 'role']),
            models.Index(fields=['role', 'is_active']),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user_id} -> {self.asset_hub_id} ({self.role})"
