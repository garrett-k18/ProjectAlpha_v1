"""
WHAT: Borrower Personally Identifiable Information (PII) model with field-level encryption
WHY: Store sensitive borrower data securely with encryption at rest
HOW: Uses django-fernet-encrypted-fields to encrypt SSN, DOB, DOD, and phone numbers
FILE: model_co_borrowerPII.py (Core Module - Borrower PII)

SECURITY NOTES:
- All PII fields are encrypted using django-fernet-encrypted-fields (Fernet symmetric encryption)
- Encrypted fields cannot be indexed or used efficiently in WHERE clauses
- Use asset FK for lookups, not encrypted fields
- NEVER log or display decrypted PII values
- Encryption uses SALT_KEY + Django SECRET_KEY (both required)
- Implement audit logging for all access to this table

COMPLIANCE:
- Designed for GLBA, FCRA, state privacy laws compliance
- Contains regulated consumer financial information
- Access should be restricted and audited

Docs reviewed:
- django-fernet-encrypted-fields: https://github.com/jazzband/django-fernet-encrypted-fields
- Django models: https://docs.djangoproject.com/en/5.2/topics/db/models/
"""

from django.db import models
from encrypted_fields.fields import EncryptedCharField, EncryptedDateField


class BorrowerPII(models.Model):
    """
    WHAT: Stores encrypted personally identifiable information for borrowers
    WHY: Protect sensitive borrower data with field-level encryption
    HOW: One-to-one relationship with AssetIdHub, encrypted fields for all PII
    
    RELATIONSHIPS:
    - asset: OneToOne to AssetIdHub (primary key, lookup field)
    
    ENCRYPTED FIELDS (cannot be queried efficiently):
    - borrower1_ssn: Social Security Number for primary borrower
    - borrower1_dob: Date of birth for primary borrower
    - borrower1_dod: Date of death for primary borrower (if applicable)
    - borrower1_phone: Phone number for primary borrower
    - borrower2_ssn: Social Security Number for co-borrower
    - borrower2_dob: Date of birth for co-borrower
    - borrower2_dod: Date of death for co-borrower (if applicable)
    - borrower2_phone: Phone number for co-borrower
    
    USAGE:
    >>> asset = AssetIdHub.objects.get(pk=123)
    >>> pii = BorrowerPII.objects.create(
    ...     asset=asset,
    ...     borrower1_ssn='123-45-6789',
    ...     borrower1_dob='1980-01-15'
    ... )
    >>> # Data is automatically encrypted in database
    >>> print(pii.borrower1_ssn)  # Automatically decrypted: '123-45-6789'
    """
    
    # =========================================================================
    # PRIMARY KEY AND RELATIONSHIPS
    # =========================================================================
    
    # WHAT: One-to-one relationship with AssetIdHub as primary key
    # WHY: Each asset has at most one set of borrower PII, ensures data integrity
    # HOW: OneToOneField with CASCADE delete, related_name for reverse lookup
    asset = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='borrower_pii',
        help_text='Asset this borrower PII belongs to (primary key)'
    )
    
    # =========================================================================
    # BORROWER 1 - PRIMARY BORROWER ENCRYPTED FIELDS
    # =========================================================================
    
    # WHAT: Encrypted Social Security Number for primary borrower
    # WHY: SSN is highly sensitive PII requiring encryption at rest
    # HOW: EncryptedCharField from django-fernet-encrypted-fields
    # FORMAT: XXX-XX-XXXX or XXXXXXXXX (9 digits with optional dashes)
    borrower1_ssn = EncryptedCharField(
        max_length=11,  # WHAT: 9 digits + 2 dashes = 11 characters
        blank=True,
        null=True,
        help_text='Social Security Number for primary borrower (encrypted)'
    )
    
    # WHAT: Encrypted date of birth for primary borrower
    # WHY: DOB is PII used for identity verification, requires encryption
    # HOW: EncryptedDateField from django-fernet-encrypted-fields
    borrower1_dob = EncryptedDateField(
        blank=True,
        null=True,
        help_text='Date of birth for primary borrower (encrypted)'
    )
    
    # WHAT: Encrypted date of death for primary borrower
    # WHY: Death date is sensitive information for estate/probate cases
    # HOW: EncryptedDateField from django-fernet-encrypted-fields
    # NOTE: NULL indicates borrower is living or status unknown
    borrower1_dod = EncryptedDateField(
        blank=True,
        null=True,
        help_text='Date of death for primary borrower if applicable (encrypted)'
    )
    
    # WHAT: Encrypted phone number for primary borrower
    # WHY: Phone numbers are PII requiring protection under privacy regulations
    # HOW: EncryptedCharField from django-fernet-encrypted-fields
    # FORMAT: Can store various formats (XXX-XXX-XXXX, (XXX) XXX-XXXX, etc.)
    borrower1_phone = EncryptedCharField(
        max_length=20,  # WHAT: Allows for various phone formats and extensions
        blank=True,
        null=True,
        help_text='Phone number for primary borrower (encrypted)'
    )
    
    # =========================================================================
    # BORROWER 2 - CO-BORROWER ENCRYPTED FIELDS
    # =========================================================================
    
    # WHAT: Encrypted Social Security Number for co-borrower
    # WHY: Co-borrower SSN is equally sensitive as primary borrower
    # HOW: EncryptedCharField from django-fernet-encrypted-fields
    # FORMAT: XXX-XX-XXXX or XXXXXXXXX (9 digits with optional dashes)
    # NOTE: NULL indicates no co-borrower on loan
    borrower2_ssn = EncryptedCharField(
        max_length=11,  # WHAT: 9 digits + 2 dashes = 11 characters
        blank=True,
        null=True,
        help_text='Social Security Number for co-borrower (encrypted)'
    )
    
    # WHAT: Encrypted date of birth for co-borrower
    # WHY: Co-borrower DOB is PII requiring encryption
    # HOW: EncryptedDateField from django-fernet-encrypted-fields
    # NOTE: NULL indicates no co-borrower or DOB unknown
    borrower2_dob = EncryptedDateField(
        blank=True,
        null=True,
        help_text='Date of birth for co-borrower (encrypted)'
    )
    
    # WHAT: Encrypted date of death for co-borrower
    # WHY: Death date is sensitive for estate/probate cases
    # HOW: EncryptedDateField from django-fernet-encrypted-fields
    # NOTE: NULL indicates borrower is living, no co-borrower, or status unknown
    borrower2_dod = EncryptedDateField(
        blank=True,
        null=True,
        help_text='Date of death for co-borrower if applicable (encrypted)'
    )
    
    # WHAT: Encrypted phone number for co-borrower
    # WHY: Co-borrower contact information is PII requiring protection
    # HOW: EncryptedCharField from django-fernet-encrypted-fields
    # FORMAT: Can store various formats (XXX-XXX-XXXX, (XXX) XXX-XXXX, etc.)
    # NOTE: NULL indicates no co-borrower or phone unknown
    borrower2_phone = EncryptedCharField(
        max_length=20,  # WHAT: Allows for various phone formats and extensions
        blank=True,
        null=True,
        help_text='Phone number for co-borrower (encrypted)'
    )
    
    # =========================================================================
    # AUDIT TRAIL FIELDS (NOT ENCRYPTED)
    # =========================================================================
    
    # WHAT: Timestamp when PII record was created
    # WHY: Audit trail for compliance and security monitoring
    # HOW: auto_now_add automatically sets on creation
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when this PII record was created'
    )
    
    # WHAT: Timestamp when PII record was last modified
    # WHY: Track when PII was last updated for audit purposes
    # HOW: auto_now automatically updates on every save
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when this PII record was last modified'
    )
    
    # =========================================================================
    # META CONFIGURATION
    # =========================================================================
    
    class Meta:
        # WHAT: Database table name
        # WHY: Follow project naming convention for core models
        db_table = 'core_borrower_pii'
        
        # WHAT: Human-readable model name
        # WHY: Display in Django admin interface
        verbose_name = 'Borrower PII'
        verbose_name_plural = 'Borrower PII Records'
        
        # WHAT: Table-level documentation
        # WHY: Provide context for DBAs and documentation tools
        db_table_comment = 'Encrypted borrower personally identifiable information (SSN, DOB, phone)'
        
        # WHAT: Default ordering for queries
        # WHY: Show most recently updated records first
        ordering = ['-updated_at']
        
        # WHAT: Database indexes for performance
        # WHY: Enable fast lookups by timestamp for audit queries
        # NOTE: Cannot index encrypted fields!
        indexes = [
            models.Index(fields=['created_at'], name='borrower_pii_created_idx'),
            models.Index(fields=['updated_at'], name='borrower_pii_updated_idx'),
        ]
    
    # =========================================================================
    # MODEL METHODS
    # =========================================================================
    
    def __str__(self) -> str:
        """
        WHAT: String representation of BorrowerPII instance
        WHY: Display in Django admin and logs without exposing PII
        HOW: Shows asset ID only, never decrypted sensitive data
        
        SECURITY: Never include encrypted field values in __str__!
        """
        return f"BorrowerPII for Asset {self.asset_id}"
    
    def has_borrower1_data(self) -> bool:
        """
        WHAT: Check if any borrower 1 data exists
        WHY: Determine if primary borrower information is available
        HOW: Returns True if any borrower1 field has data
        
        Returns:
            bool: True if any borrower1 field is populated
        """
        return any([
            self.borrower1_ssn,
            self.borrower1_dob,
            self.borrower1_dod,
            self.borrower1_phone,
        ])
    
    def has_borrower2_data(self) -> bool:
        """
        WHAT: Check if any borrower 2 (co-borrower) data exists
        WHY: Determine if co-borrower information is available
        HOW: Returns True if any borrower2 field has data
        
        Returns:
            bool: True if any borrower2 field is populated
        """
        return any([
            self.borrower2_ssn,
            self.borrower2_dob,
            self.borrower2_dod,
            self.borrower2_phone,
        ])
    
    def has_any_data(self) -> bool:
        """
        WHAT: Check if ANY borrower data exists in record
        WHY: Useful for data quality checks and reporting
        HOW: Returns True if borrower1 or borrower2 has data
        
        Returns:
            bool: True if any PII field is populated
        """
        return self.has_borrower1_data() or self.has_borrower2_data()
    
    def get_borrower1_age(self) -> int | None:
        """
        WHAT: Calculate primary borrower's current age
        WHY: Age calculations needed for various business logic
        HOW: Calculate years between DOB and today (or DOD if deceased)
        
        Returns:
            int | None: Age in years, or None if DOB not available
        """
        # WHAT: Import datetime inside method to avoid circular imports
        # WHY: timezone is from django.utils, may not be loaded at module level
        from django.utils import timezone
        from datetime import date
        
        # WHAT: Return None if no date of birth
        if not self.borrower1_dob:
            return None
        
        # WHAT: Calculate age as of death date if deceased
        # WHY: Accurate age calculation for deceased borrowers
        if self.borrower1_dod:
            end_date = self.borrower1_dod
        else:
            # WHAT: Use current date for living borrowers
            end_date = date.today()
        
        # WHAT: Calculate age in years
        # HOW: Subtract years, adjust if birthday hasn't occurred yet this year
        age = end_date.year - self.borrower1_dob.year
        
        # WHAT: Adjust if birthday hasn't occurred yet this year
        # WHY: Age increments on birthday, not at year start
        if (end_date.month, end_date.day) < (self.borrower1_dob.month, self.borrower1_dob.day):
            age -= 1
        
        return age
    
    def get_borrower2_age(self) -> int | None:
        """
        WHAT: Calculate co-borrower's current age
        WHY: Age calculations needed for various business logic
        HOW: Calculate years between DOB and today (or DOD if deceased)
        
        Returns:
            int | None: Age in years, or None if DOB not available
        """
        from datetime import date
        
        # WHAT: Return None if no date of birth
        if not self.borrower2_dob:
            return None
        
        # WHAT: Calculate age as of death date if deceased
        if self.borrower2_dod:
            end_date = self.borrower2_dod
        else:
            # WHAT: Use current date for living borrowers
            end_date = date.today()
        
        # WHAT: Calculate age in years
        age = end_date.year - self.borrower2_dob.year
        
        # WHAT: Adjust if birthday hasn't occurred yet this year
        if (end_date.month, end_date.day) < (self.borrower2_dob.month, self.borrower2_dob.day):
            age -= 1
        
        return age
