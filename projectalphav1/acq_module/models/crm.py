from django.db import models
from django.utils import timezone
from .seller import SellerRawData
import secrets

class Brokercrm(models.Model):
    """Time-bound, optionally single-use invite token for external brokers.

    Links to a specific `SellerRawData` row so an external broker can submit
    a small set of valuation fields without authentication.
    """
    seller_raw_data = models.ForeignKey(
        SellerRawData,
        on_delete=models.CASCADE,
        related_name='broker_invites',
        help_text='SellerRawData row this invite is for.'
    )

    token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text='Opaque invite token used in public URL.'
    )
    broker_firm = models.CharField(max_length=255, blank=True, null=True)
    broker_state = models.CharField(max_length=2, blank=True, null=True)
    broker_msa = models.CharField(max_length=255, blank=True, null=True)
    broker_email = models.EmailField(blank=True, null=True)
    broker_name = models.CharField(max_length=255, blank=True, null=True)

    # Expiration and usage controls
    expires_at = models.DateTimeField(help_text='When this invite token expires.')
    single_use = models.BooleanField(default=True, help_text='If true, lock after first successful submit.')
    used_at = models.DateTimeField(blank=True, null=True, help_text='When the token was first used to submit values.')

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['seller_raw_data']),
            models.Index(fields=['expires_at']),
        ]
        db_table = 'acq_broker_invite_token'
        ordering = ['-created_at']
        verbose_name = 'Broker Invite Token'
        verbose_name_plural = 'Broker Invite Tokens'

    def __str__(self) -> str:
        return f"Invite for SRD {self.seller_raw_data_id} (expires {self.expires_at.isoformat()})"

    @staticmethod
    def generate_token() -> str:
        """Generate a URL-safe opaque token."""
        # 32 bytes -> ~43 char urlsafe string; we cap length to 64 max
        return secrets.token_urlsafe(32)

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    def is_valid(self) -> bool:
        if self.is_expired:
            return False
        if self.single_use and self.is_used:
            return False
        return True
