from django.db import models

class Brokercrm(models.Model):
    """Canonical Broker directory entry (independent of any loan/token).

    Stores contact and firm/location data used across the app (e.g., dropdowns,
    assignments). Token/authentication for external submissions lives in
    `user_admin.models.BrokerTokenAuth` and is intentionally decoupled.
    """
    broker_firm = models.CharField(max_length=255, blank=True, null=True)
    broker_state = models.CharField(max_length=2, blank=True, null=True)
    broker_city = models.CharField(max_length=255, blank=True, null=True)
    broker_email = models.EmailField(blank=True, null=True)
    broker_phone = models.CharField(max_length=255, blank=True, null=True)
    broker_name = models.CharField(max_length=255, blank=True, null=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['broker_state']),
            models.Index(fields=['broker_email']),
        ]
        # Keeping existing db_table to avoid disruptive renames; can be renamed later via migration if desired
        db_table = 'brokercrm'
        ordering = ['-created_at']
        verbose_name = 'Broker'
        verbose_name_plural = 'Brokers'

    def __str__(self) -> str:
        # Useful admin label
        parts = [p for p in [self.broker_name, self.broker_firm, self.broker_city] if p]
        return " - ".join(parts) or (self.broker_email or f"Broker {self.pk}")


class TradingPartnerCRM(models.Model):
    """Canonical Trading Partner directory entry.

    This model captures core contact details for trading partners (e.g., hedge funds,
    private lenders, institutions) independent of any specific deal/loan. It mirrors
    the lightweight directory style of `Brokercrm` and is intended for global lookups
    and assignments.
    """

    # Primary contact / firm information
    firm = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        help_text="Firm or organization name for the trading partner.",
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Primary contact person's full name.",
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Primary contact email address.",
    )
    phone = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Primary contact phone number (free-form, include country code if applicable).",
    )

    # Alternate contact
    altname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Alternate contact person's full name.",
    )
    altemail = models.EmailField(
        blank=True,
        null=True,
        help_text="Alternate contact email address.",
    )
    alt_phone = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Alternate contact phone number.",
    )

    # NDA tracking
    nda_flag = models.BooleanField(
        default=False,
        help_text="Whether an NDA is required/expected with this partner.",
    )
    nda_signed = models.DateField(
        blank=True,
        null=True,
        help_text="Date the NDA was fully executed (leave blank if not signed).",
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['firm']),
        ]
        db_table = 'tradingpartnercrm'
        ordering = ['-created_at']
        verbose_name = 'Trading Partner'
        verbose_name_plural = 'Trading Partners'

    def __str__(self) -> str:
        """Human-friendly label for admin/change lists."""
        parts = [p for p in [self.name, self.firm] if p]
        return " - ".join(parts) or (self.email or f"Trading Partner {self.pk}")
