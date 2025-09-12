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
