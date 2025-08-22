from django.db import models
from django.utils import timezone
import secrets


class BrokerTokenAuth(models.Model):
    """Token-based, loginless access for external brokers to submit values.

    This model is intentionally placed in the `user_admin` app to keep
    authentication-like concerns together and separate from the broker CRM
    directory data stored in `acq_module.Brokercrm`.

    Relations are referenced by app label and model name to avoid import cycles.
    """

    # Loan this token provides access to
    seller_raw_data = models.ForeignKey(
        'acq_module.SellerRawData',
        on_delete=models.CASCADE,
        related_name='broker_tokens',
        help_text='SellerRawData row this token is for.'
    )

    # Optional link to canonical broker directory entry
    broker = models.ForeignKey(
        'acq_module.Brokercrm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auth_tokens',
        help_text='Directory record of the broker this token is intended for.'
    )

    # Opaque token used in public URL
    token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text='Opaque invite token used in public URL.'
    )

    # Expiration and usage controls
    expires_at = models.DateTimeField(help_text='When this token expires.')
    single_use = models.BooleanField(default=True, help_text='If true, lock after first successful submit.')
    used_at = models.DateTimeField(blank=True, null=True, help_text='When the token was first used to submit values.')

    # Audit / metadata
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['seller_raw_data']),
            models.Index(fields=['expires_at']),
        ]
        db_table = 'user_admin_broker_token_auth'
        ordering = ['-created_at']
        verbose_name = 'Broker Token Auth'
        verbose_name_plural = 'Broker Token Auth'

    def __str__(self) -> str:  # pragma: no cover - simple debug aid
        return f"Token for SRD {self.seller_raw_data_id} (expires {self.expires_at.isoformat()})"

    @staticmethod
    def generate_token() -> str:
        """Generate a URL-safe opaque token.

        32 bytes -> ~43 char urlsafe string; we cap length to 64 max.
        """
        return secrets.token_urlsafe(32)

    @property
    def is_expired(self) -> bool:
        """Whether the token has reached or passed its expiration."""
        return timezone.now() >= self.expires_at

    @property
    def is_used(self) -> bool:
        """Whether the token has been used at least once."""
        return self.used_at is not None

    def is_valid(self) -> bool:
        """Check token validity considering expiry and single-use semantics."""
        if self.is_expired:
            return False
        if self.single_use and self.is_used:
            return False
        return True
