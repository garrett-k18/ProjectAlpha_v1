from django.db import models
from django.conf import settings
from .model_co_geoAssumptions import StateReference, MSAReference

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
        SERVICER = "servicer", "Servicer"
        TITLE_COMPANY = "title_company", "Title Company"
    
    firm = models.CharField(max_length=255, blank=True, null=True)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    states = models.ManyToManyField(
        StateReference,
        blank=True,
        related_name='crm_contacts',
    )
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
        help_text="Contact type: Broker, Trading Partner, Investor, Legal, Servicer, or Vendor",
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


class BrokerMSAAssignment(models.Model):
    """
    WHAT: Junction table for many-to-many relationship between brokers and MSAs
    WHY: One broker can cover multiple MSAs, one MSA can have multiple brokers
    HOW: Links MasterCRM (brokers) to MSAReference with priority and active status
    
    Example Use Cases:
    - Broker "John Smith" covers "Los Angeles" and "San Diego" MSAs
    - "Phoenix MSA" has "Jane Doe" (priority 1) and "Bob Wilson" (priority 2) as backups
    
    Business Logic:
    - Priority 1 = Primary broker for auto-assignment
    - Priority 2+ = Backup brokers if primary is unavailable
    - is_active flag allows temporary disabling without deletion
    """
    
    # WHAT: Foreign key to MasterCRM (the broker)
    # WHY: Link to broker record in CRM
    broker = models.ForeignKey(
        MasterCRM,
        on_delete=models.CASCADE,
        related_name='msa_assignments',
        help_text="Broker assigned to this MSA"
    )
    
    # WHAT: Foreign key to MSAReference (the market)
    # WHY: Link to MSA market
    msa = models.ForeignKey(
        MSAReference,
        on_delete=models.CASCADE,
        related_name='broker_assignments',
        help_text="MSA market assigned to this broker"
    )
    
    # WHAT: Priority for multiple brokers in same MSA
    # WHY: Determine primary vs backup brokers
    # HOW: Lower number = higher priority (1 = primary, 2 = backup, etc.)
    priority = models.IntegerField(
        default=1,
        help_text="Assignment priority (1 = primary, 2 = backup, etc.)"
    )
    
    # WHAT: Active status flag
    # WHY: Enable/disable assignments without deleting them
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this assignment is currently active"
    )
    
    # Optional notes
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this broker-MSA assignment"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Broker MSA Assignment"
        verbose_name_plural = "Broker MSA Assignments"
        ordering = ['msa', 'priority', 'broker']
        # WHAT: Ensure unique combination of broker + MSA
        # WHY: Prevent duplicate assignments (can't assign same broker to same MSA twice)
        unique_together = [['broker', 'msa']]
        indexes = [
            models.Index(fields=['msa', 'priority']),
            models.Index(fields=['broker']),
            models.Index(fields=['is_active']),
            models.Index(fields=['msa', 'is_active', 'priority']),  # Composite for queries
        ]
        db_table = 'broker_msa_assignments'
    
    def __str__(self):
        broker_name = self.broker.contact_name or self.broker.firm or f"Broker #{self.broker.id}"
        return f"{broker_name} → {self.msa.msa_name} (Priority: {self.priority})"
