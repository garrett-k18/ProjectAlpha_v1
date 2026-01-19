"""ETL models for trade-level settlement statement extraction."""

from django.conf import settings
from django.db import models

from .model_etl_document_extraction import ExtractionStatus


class TradeSettlementStatementDocument(models.Model):
    """Metadata for a trade-level settlement statement document."""

    # WHAT: Original file name as provided by the source system.
    # WHY: Keep a human-readable identifier for the document.
    file_name = models.CharField(max_length=255)
    # WHAT: Full path or URI to the document.
    # WHY: Provide a stable reference for reprocessing or audit.
    file_path = models.CharField(max_length=1024)
    # WHAT: MIME type detected for the document.
    # WHY: Helpful for downstream OCR/extraction tooling.
    file_mime_type = models.CharField(max_length=100, blank=True)
    # WHAT: File size in bytes.
    # WHY: Useful for diagnostics and size-limiting logic.
    file_size_bytes = models.BigIntegerField(null=True, blank=True)

    # WHAT: Timestamp when the document became available to the ETL.
    # WHY: Retain original ingestion timing for reporting.
    uploaded_at = models.DateTimeField()
    # WHAT: Timestamp when extraction completed (success or failure).
    # WHY: Track processing latency and finalization.
    processed_at = models.DateTimeField(null=True, blank=True)

    # WHAT: Extraction status aligned with the shared ETL status enum.
    # WHY: Consistent status tracking across document workflows.
    status = models.CharField(
        max_length=20,
        choices=ExtractionStatus.choices,
        default=ExtractionStatus.PENDING,
        db_index=True,
    )
    # WHAT: Human-readable status summary or error message.
    # WHY: Quick inspection without digging into logs.
    status_message = models.TextField(blank=True)

    # WHAT: Optional user who triggered the extraction.
    # WHY: Audit and attribution for manual workflows.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="trade_settlement_documents",
    )

    # WHAT: Created/updated timestamps for the document record.
    # WHY: Standard audit fields for ETL metadata.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "etl_trade_settlement_document"
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:  # pragma: no cover - human readable display
        return f"{self.file_name} ({self.status})"


class TradeSettlementStatementETL(models.Model):
    """Structured trade-level settlement statement data captured by ETL."""

    # WHAT: Document that produced this settlement statement.
    # WHY: Preserve lineage to the original file.
    document = models.ForeignKey(
        TradeSettlementStatementDocument,
        on_delete=models.CASCADE,
        related_name="statements",
    )

    # WHAT: Trade reference from the acquisition module.
    # WHY: Link settlement data to the trade lifecycle.
    trade = models.ForeignKey(
        "acq_module.Trade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trade_settlement_statements",
    )

    # WHAT: Statement date as shown on the statement (raw text).
    # WHY: Preserve the source value before any downstream normalization.
    statement_date = models.CharField(max_length=20, blank=True, db_index=True)
    # WHAT: Settlement date (closing date) as shown on the statement (raw text).
    # WHY: Keep the original source formatting for audit.
    settlement_date = models.CharField(max_length=20, blank=True, db_index=True)

    # WHAT: Seller name shown on the statement.
    # WHY: Match settlement counterparties to internal records.
    seller_name = models.CharField(max_length=255, blank=True)
    # WHAT: Buyer name shown on the statement.
    # WHY: Capture buying entity (Project Alpha or affiliate).
    buyer_name = models.CharField(max_length=255, blank=True)
    # WHAT: Accepted bid amount printed on the settlement sheet (raw text).
    # WHY: Capture the final negotiated bid as provided.
    accepted_bid_amount = models.CharField(max_length=50, blank=True)
    # WHAT: Deposit amount listed on the document (raw text).
    # WHY: Track funds posted prior to closing.
    deposit_amount = models.CharField(max_length=50, blank=True)
    # WHAT: Pool or bucket name from the settlement statement.
    # WHY: Preserve grouping labels from the source document.
    pool_name = models.CharField(max_length=100, blank=True)





    # WHAT: Free-form notes extracted or added during processing.
    # WHY: Capture any additional commentary from the statement.
    notes = models.TextField(blank=True)

    # WHAT: Timestamp when the extraction service ran.
    # WHY: Track data freshness separate from document timestamps.
    extracted_at = models.DateTimeField(auto_now_add=True)

    # WHAT: Created/updated timestamps for the settlement record.
    # WHY: Standard audit fields for ETL data.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # WHAT: Optional user who initiated the extraction.
    # WHY: Audit and attribution for manual workflows.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="trade_settlement_statements_created",
    )

    class Meta:
        db_table = "etl_trade_settlement_statement"
        ordering = ["-statement_date", "-created_at"]
        indexes = [
            models.Index(fields=["trade"], name="etl_stst_trade_idx"),
            models.Index(fields=["settlement_date"], name="etl_stst_sett_dt_idx"),
            models.Index(fields=["statement_date"], name="etl_stst_stmt_dt_idx"),
        ]

    def __str__(self) -> str:  # pragma: no cover - human readable display
        trade_label = self.trade_name or (self.trade.trade_name if self.trade else "Unlinked Trade")
        return f"{trade_label} - {self.statement_date or 'Unknown Statement Date'}"


class TradeSettlementStatementLineItem(models.Model):
    """Raw line items extracted from trade settlement statements."""

    # WHAT: Parent settlement statement record.
    # WHY: Maintain lineage for each line item.
    statement = models.ForeignKey(
        TradeSettlementStatementETL,
        on_delete=models.CASCADE,
        related_name="line_items",
    )

    # WHAT: Line item order as extracted.
    # WHY: Preserve original ordering from the statement.
    line_number = models.IntegerField()

    # WHAT: Line item description text (raw).
    # WHY: Preserve exact label for audit.
    description = models.CharField(max_length=255, blank=True)
    # WHAT: Line item amount (raw).
    # WHY: Keep original formatting before normalization.
    amount = models.CharField(max_length=50, blank=True)
    # WHAT: Optional category for grouping (raw).
    # WHY: Preserve any section headers or categories present.
    category = models.CharField(max_length=100, blank=True)
    # WHAT: Additional notes from the line item (raw).
    # WHY: Capture any extra context text.
    notes = models.TextField(blank=True)

    # WHAT: Created/updated timestamps for the line item record.
    # WHY: Standard audit fields for ETL line items.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "etl_trade_settlement_statement_line_item"
        ordering = ["statement_id", "line_number"]
        indexes = [
            models.Index(fields=["statement"], name="etl_stst_line_stmt_idx"),
            models.Index(fields=["line_number"], name="etl_stst_line_num_idx"),
        ]

    def __str__(self) -> str:  # pragma: no cover - human readable display
        return f"{self.statement_id} - Line {self.line_number}"
