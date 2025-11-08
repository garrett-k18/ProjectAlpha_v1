from django.db import models
from django.utils import timezone
import secrets


class BrokerTokenAuth(models.Model):
    """Token-based, loginless access for external brokers to submit values.

    This model is intentionally placed in the `user_admin` app to keep
    authentication-like concerns together and separate from the CRM directory
    data stored in `core.MasterCRM`.

    Relations are referenced by app label and model name to avoid import cycles.
    
    WHAT: Links to AssetIdHub (hub-first architecture)
    WHY: All joins happen through the hub table intentionally
    HOW: Direct FK to hub; access ACQ data via asset_hub.acq_raw
    """

    # WHAT: Asset this token provides access to (hub-first)
    # WHY: Hub-first architecture - all cross-module joins go through AssetIdHub
    # HOW: FK to hub; access domain data via reverse relations (asset_hub.acq_raw, asset_hub.am_boarded, etc.)
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.CASCADE,
        related_name='broker_tokens',
        help_text='Asset hub ID this token is for (hub-first architecture).'
    )

    # Optional link to canonical CRM directory entry (Broker contact)
    broker = models.ForeignKey(
        'core.MasterCRM',
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
            models.Index(fields=['asset_hub']),
            models.Index(fields=['expires_at']),
        ]
        db_table = 'user_admin_broker_token_auth'
        ordering = ['-created_at']
        verbose_name = 'Broker Token Auth'
        verbose_name_plural = 'Broker Token Auth'

    def __str__(self) -> str:  # pragma: no cover - simple debug aid
        return f"Token for Asset Hub {self.asset_hub_id} (expires {self.expires_at.isoformat()})"

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


class BrokerPortalToken(models.Model):
    """Multi-use portal token that represents a single public URL per broker.

    Design:
    - This token is used to render a broker's "portal" page listing all currently
      active assigned invites (most recent token per SRD) without requiring the
      broker to switch between multiple links.
    - It is intentionally multi-use and time-bound. When expired, a new portal
      token can be generated and shared again.
    - Per-loan access and submissions are still governed by `BrokerTokenAuth`.
    """

    # Canonical CRM directory entry (Broker contact)
    broker = models.ForeignKey(
        'core.MasterCRM',
        on_delete=models.CASCADE,
        related_name='portal_tokens',
        help_text='Broker this portal token is issued for.'
    )

    # Opaque token used in public URL
    token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text='Opaque portal token used in public URL.'
    )

    # Expiration (multi-use until this time)
    expires_at = models.DateTimeField(help_text='When this portal token expires.')

    # Audit / metadata
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['broker']),
            models.Index(fields=['expires_at']),
        ]
        db_table = 'user_admin_broker_portal_token'
        ordering = ['-created_at']
        verbose_name = 'Broker Portal Token'
        verbose_name_plural = 'Broker Portal Tokens'

    def __str__(self) -> str:  # pragma: no cover - debug aid
        return f"Portal token for broker {self.broker_id} (expires {self.expires_at.isoformat()})"

    @staticmethod
    def generate_token() -> str:
        """Generate a URL-safe opaque token (reusing same strategy as invites)."""
        return secrets.token_urlsafe(32)

    @property
    def is_expired(self) -> bool:
        """Whether the portal token has reached or passed its expiration."""
        return timezone.now() >= self.expires_at

    def is_valid(self) -> bool:
        """Validity check: true when not expired."""
        return not self.is_expired
