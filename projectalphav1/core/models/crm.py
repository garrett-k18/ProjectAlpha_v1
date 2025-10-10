from django.db import models
from django.conf import settings

class MasterCRM(models.Model):
    """Unified Master CRM directory entry (broker-first, now generalized).

    Originally a broker directory, this model has been expanded to serve as the
    single Master CRM record by incorporating additional fields used by trading
    partners and legal contacts. External authentication/tokens remain in
    `user_admin` and are linked via optional FKs here.
    Docs: https://docs.djangoproject.com/en/stable/ref/models/fields/
    """
    
    # Contact type tag using Django 3.0+ TextChoices enum
    # This provides better type safety and cleaner code compared to old tuple-based choices
    class ContactTag(models.TextChoices):
        """Enum for contact type categorization in the Master CRM"""
        BROKER = "broker", "Broker"
        TRADING_PARTNER = "trading_partner", "Trading Partner"
        INVESTOR = "investor", "Investor"
        LEGAL = "legal", "Legal"
        VENDOR = "vendor", "Vendor"
    
    firm = models.CharField(max_length=255, blank=True, null=True)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)

    # Contact type tag field using the TextChoices enum
    tag = models.CharField(
        max_length=32,
        choices=ContactTag.choices,
        null=True,
        blank=True,
        db_index=True,
        help_text="Contact type: Broker, Trading Partner, Investor, Legal, or Vendor",
    )
    

    # Unified fields (from TradingPartnerCRM/LegalCRM)
    # Alternate contact (partner-style)
    alt_contact_name = models.CharField(max_length=255, blank=True, null=True)
    alt_contact_email = models.EmailField(blank=True, null=True)
    alt_contact_phone = models.CharField(max_length=255, blank=True, null=True)

    # NDA tracking
    nda_flag = models.BooleanField(default=False)
    nda_signed = models.DateField(blank=True, null=True)

    # Dependencies removed as requested to simplify migrations.

    # Notes and audit
    notes = models.TextField(blank=True, null=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['email']),
            models.Index(fields=['firm']),
            models.Index(fields=['tag']),
        ]
        ordering = ['-created_at']
        verbose_name = 'Master CRM'
        verbose_name_plural = 'Master CRM'
        # Default table name (no legacy table preservation)

    def __str__(self) -> str:
        # Useful admin label
        parts = [p for p in [self.contact_name, self.firm, self.city] if p]
        return " - ".join(parts) or (self.email or f"CRM {self.pk}")

    # No legacy alias properties; API layers should map keys explicitly




