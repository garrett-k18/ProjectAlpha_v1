"""
Borrower Personally Identifiable Information (PII) and related servicer contact extract models
for the Acquisitions module.

NOTE: Database table name for BorrowerPII remains 'core_borrower_pii' to preserve existing data.
"""

from django.db import models
from encrypted_fields.fields import EncryptedCharField, EncryptedDateField


class BorrowerPII(models.Model):
    """Borrower PII with field-level encryption (rehomed to acq_module)."""

    asset = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='borrower_pii',
        help_text='Asset this borrower PII belongs to (primary key)',
    )

    borrower1_ssn = EncryptedCharField(
        max_length=11,
        blank=True,
        null=True,
        help_text='Social Security Number for primary borrower (encrypted)',
    )

    borrower1_dob = EncryptedDateField(
        blank=True,
        null=True,
        help_text='Date of birth for primary borrower (encrypted)',
    )

    borrower1_dod = EncryptedDateField(
        blank=True,
        null=True,
        help_text='Date of death for primary borrower if applicable (encrypted)',
    )

    borrower1_phone = EncryptedCharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Phone number for primary borrower (encrypted)',
    )

    borrower2_ssn = EncryptedCharField(
        max_length=11,
        blank=True,
        null=True,
        help_text='Social Security Number for co-borrower (encrypted)',
    )

    borrower2_dob = EncryptedDateField(
        blank=True,
        null=True,
        help_text='Date of birth for co-borrower (encrypted)',
    )

    borrower2_dod = EncryptedDateField(
        blank=True,
        null=True,
        help_text='Date of death for co-borrower if applicable (encrypted)',
    )

    borrower2_phone = EncryptedCharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Phone number for co-borrower (encrypted)',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when this PII record was created',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when this PII record was last modified',
    )

    class Meta:
        db_table = 'core_borrower_pii'
        verbose_name = 'Borrower PII'
        verbose_name_plural = 'Borrower PII Records'
        db_table_comment = 'Encrypted borrower personally identifiable information (SSN, DOB, phone)'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['created_at'], name='borrower_pii_created_idx'),
            models.Index(fields=['updated_at'], name='borrower_pii_updated_idx'),
        ]

    def __str__(self) -> str:
        return f"BorrowerPII for Asset {self.asset_id}"

    def has_borrower1_data(self) -> bool:
        return any([
            self.borrower1_ssn,
            self.borrower1_dob,
            self.borrower1_dod,
            self.borrower1_phone,
        ])

    def has_borrower2_data(self) -> bool:
        return any([
            self.borrower2_ssn,
            self.borrower2_dob,
            self.borrower2_dod,
            self.borrower2_phone,
        ])

    def has_any_data(self) -> bool:
        return self.has_borrower1_data() or self.has_borrower2_data()

    def get_borrower1_age(self) -> int | None:
        from django.utils import timezone  # noqa: F401  # kept for parity with original
        from datetime import date

        if not self.borrower1_dob:
            return None

        if self.borrower1_dod:
            end_date = self.borrower1_dod
        else:
            end_date = date.today()

        age = end_date.year - self.borrower1_dob.year
        if (end_date.month, end_date.day) < (self.borrower1_dob.month, self.borrower1_dob.day):
            age -= 1
        return age

    def get_borrower2_age(self) -> int | None:
        from datetime import date

        if not self.borrower2_dob:
            return None

        if self.borrower2_dod:
            end_date = self.borrower2_dod
        else:
            end_date = date.today()

        age = end_date.year - self.borrower2_dob.year
        if (end_date.month, end_date.day) < (self.borrower2_dob.month, self.borrower2_dob.day):
            age -= 1
        return age


class ServicerContactsExtract(models.Model):
    asset = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.CASCADE,
        related_name='servicer_contacts_extracts',
    )

    borrower_pii = models.ForeignKey(
        'acq_module.BorrowerPII',
        on_delete=models.CASCADE,
        related_name='servicer_contacts_extracts',
    )

    contact_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Contact type from servicer extract",
    )

    hecm_date_of_death = models.DateField(
        blank=True,
        null=True,
        help_text="HECM date of death",
    )

    def __str__(self) -> str:
        return f"ServicerContactsExtract for Asset {self.asset_id} ({self.contact_type})"


class ServicerLoanExtract(models.Model):
    asset = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.CASCADE,
        related_name='servicer_loan_extracts',
    )

    def __str__(self) -> str:
        return f"ServicerLoanExtract for Asset {self.asset_id}"


class ServicerTransactionExtract(models.Model):
    asset = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.CASCADE,
        related_name='servicer_transaction_extracts',
    )

    def __str__(self) -> str:
        return f"ServicerTransactionExtract for Asset {self.asset_id}"
