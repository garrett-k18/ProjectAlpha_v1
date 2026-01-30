"""
Raw seller tape landing table for acquisition loan tapes.

WHAT: Store seller tape rows exactly as received (raw payload + key metadata).
WHY: Preserve original seller tape data before parsing/typing into domain models.
HOW: Save raw row JSON plus seller/trade linkage and import context.
"""
from __future__ import annotations

from django.db import models


class SellerTapeRawLoan(models.Model):
    """
    RAW DATA LANDING TABLE - store seller tape rows before transformation.

    WHAT: Store each seller tape row with raw payload and import metadata.
    WHY: Enables reprocessing and auditing without re-loading the source file.
    HOW: Persist raw JSON payload + contextual fields (seller, trade, row, file).
    """

    # Seller/trade context (nullable so raw imports can precede entity creation)
    seller = models.ForeignKey(
        "acq_module.Seller",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seller_tape_raw_rows",
        help_text="Optional seller linkage for raw seller tape rows.",
    )
    trade = models.ForeignKey(
        "acq_module.Trade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seller_tape_raw_rows",
        help_text="Optional trade linkage for raw seller tape rows.",
    )

    # Source context
    source_file = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Original file name or path for the seller tape.",
    )
    source_sheet = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Worksheet/tab name if the source is a spreadsheet.",
    )
    row_number = models.IntegerField(
        null=True,
        blank=True,
        help_text="Row number from the original source (1-based if available).",
    )

    # Identifiers (captured raw before standardization)
    sellertape_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text="Primary seller tape loan identifier (raw).",
    )
    sellertape_altid = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Alternate seller tape identifier (raw).",
    )

    # Raw payload and mapping metadata
    raw_payload = models.JSONField(
        null=True,
        blank=True,
        help_text="Raw row payload captured as JSON (all columns, untyped).",
    )
    column_mapping = models.JSONField(
        null=True,
        blank=True,
        help_text="Column mapping used for this import (source -> target).",
    )
    mapping_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Mapping name used for this import (if available).",
    )
    mapping_method = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Mapping method used (AI, MANUAL, EXACT, HYBRID).",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "etl_seller_tape_raw_loan"
        verbose_name = "Seller Tape Raw Loan"
        verbose_name_plural = "Seller Tape Raw Loans"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["seller"]),
            models.Index(fields=["trade"]),
            models.Index(fields=["sellertape_id"]),
            models.Index(fields=["source_file"]),
        ]

    def __str__(self) -> str:
        return f"SellerTapeRawLoan {self.pk} ({self.sellertape_id or 'no-id'})"
