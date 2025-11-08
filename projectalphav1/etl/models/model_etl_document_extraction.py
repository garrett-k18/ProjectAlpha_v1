"""Models supporting valuation document extraction pipeline."""

from django.conf import settings
from django.db import models


class ExtractionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    IN_PROGRESS = "in_progress", "In Progress"
    PARTIAL = "partial", "Partial"
    COMPLETE = "complete", "Complete"
    FAILED = "failed", "Failed"


class ExtractionMethod(models.TextChoices):
    RULE = "rule", "Rule"
    OCR = "ocr", "OCR"
    AI = "ai", "AI"
    MANUAL = "manual", "Manual"


class ValuationDocument(models.Model):
    """Metadata for a valuation source document processed by the ETL extractor."""

    file_name = models.CharField(max_length=255)
    file_path = models.CharField(
        max_length=1024,
        help_text="Location of the source document in storage (e.g., SharePoint path).",
    )
    file_mime_type = models.CharField(max_length=100, blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)

    uploaded_at = models.DateTimeField(
        help_text="Timestamp when the document became available for processing.",
    )
    processed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=ExtractionStatus.choices,
        default=ExtractionStatus.PENDING,
        db_index=True,
    )
    status_message = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="valuation_documents",
    )

    class Meta:
        db_table = "etl_valuation_document"
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:  # pragma: no cover - human readable display
        return f"{self.file_name} ({self.status})"


class ExtractionFieldResult(models.Model):
    """Per-field extraction metadata with confidence scoring."""

    document = models.ForeignKey(
        ValuationDocument,
        related_name="field_results",
        on_delete=models.CASCADE,
    )
    target_model = models.CharField(
        max_length=100,
        help_text="Django model label receiving the value (e.g., etl.ValuationETL).",
    )
    target_field = models.CharField(max_length=100)

    value_text = models.TextField(blank=True)
    value_json = models.JSONField(blank=True, null=True)

    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        help_text="Confidence score between 0 and 1.",
    )
    extraction_method = models.CharField(
        max_length=20,
        choices=ExtractionMethod.choices,
        default=ExtractionMethod.RULE,
    )
    requires_review = models.BooleanField(
        default=False,
        help_text="True when the value needs human validation.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "etl_valuation_extraction_field"
        unique_together = (
            "document",
            "target_model",
            "target_field",
        )

    def __str__(self) -> str:  # pragma: no cover - human readable display
        return f"{self.target_model}.{self.target_field} ({self.confidence})"


class ExtractionLogEntry(models.Model):
    """Free-form log entries captured during document extraction."""

    document = models.ForeignKey(
        ValuationDocument,
        related_name="logs",
        on_delete=models.CASCADE,
    )
    level = models.CharField(max_length=20, default="info")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "etl_valuation_extraction_log"
        ordering = ["created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"[{self.level}] {self.message[:50]}"
