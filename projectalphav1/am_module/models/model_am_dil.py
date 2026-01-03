from django.db import models
from django.utils import timezone
from encrypted_fields.fields import EncryptedCharField, EncryptedTextField, EncryptedEmailField


class HeirContact(models.Model):
    """
    WHAT: Stores encrypted contact information for borrowers or heirs linked to DIL tasks
    WHY: Protect sensitive PII (names, phone, email, address) with field-level encryption
    HOW: Many-to-one relationship with DILTask, encrypted fields for all contact data
    
    RELATIONSHIPS:
    - dil_task: ForeignKey to DILTask (many contacts per task)
    
    ENCRYPTED FIELDS (cannot be queried efficiently):
    - contact_name: Full name of borrower or heir
    - contact_phone: Phone number
    - contact_email: Email address
    - contact_address: Mailing address
    
    USAGE:
    >>> task = DILTask.objects.get(pk=123)
    >>> contact = HeirContact.objects.create(
    ...     dil_task=task,
    ...     contact_name='John Doe',
    ...     contact_phone='555-123-4567'
    ... )
    >>> # Data is automatically encrypted in database
    >>> print(contact.contact_name)  # Automatically decrypted: 'John Doe'
    """
    
    # =========================================================================
    # RELATIONSHIP
    # =========================================================================
    
    # WHAT: Link to the DIL task (many contacts per task)
    # WHY: Allows tracking multiple heirs/borrowers per DIL case
    # HOW: ForeignKey with CASCADE delete, related_name for reverse lookup
    dil_task = models.ForeignKey(
        'am_module.DILTask',
        on_delete=models.CASCADE,
        related_name='heir_contacts',
        help_text='The DIL task this contact is associated with.',
    )
    
    # =========================================================================
    # ENCRYPTED CONTACT INFORMATION
    # =========================================================================
    
    # WHAT: Encrypted full name of borrower or heir
    # WHY: Names are PII requiring protection under privacy regulations
    # HOW: EncryptedCharField from django-fernet-encrypted-fields
    contact_name = EncryptedCharField(
        max_length=255,
        help_text="Name of borrower or heir contact (encrypted).",
    )
    
    # WHAT: Encrypted phone number
    # WHY: Phone numbers are PII requiring protection
    # HOW: EncryptedCharField from django-fernet-encrypted-fields
    # FORMAT: Can store various formats (XXX-XXX-XXXX, (XXX) XXX-XXXX, etc.)
    contact_phone = EncryptedCharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Phone number of borrower or heir contact (encrypted).",
    )
    
    # WHAT: Encrypted email address
    # WHY: Email addresses are PII requiring protection
    # HOW: EncryptedEmailField from django-fernet-encrypted-fields
    contact_email = EncryptedEmailField(
        null=True,
        blank=True,
        help_text="Email address of borrower or heir contact (encrypted).",
    )
    
    # WHAT: Encrypted mailing address
    # WHY: Physical addresses are PII requiring protection
    # HOW: EncryptedTextField from django-fernet-encrypted-fields
    contact_address = EncryptedTextField(
        null=True,
        blank=True,
        help_text="Mailing address of borrower or heir contact (encrypted).",
    )
    
    # Audit timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this contact was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this contact was last updated."
    )
    
    class Meta:
        verbose_name = "Heir Contact"
        verbose_name_plural = "Heir Contacts"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.contact_name} - {self.dil_task}"