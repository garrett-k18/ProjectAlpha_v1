"""Management command to extract trade settlement statements."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from acq_module.models.model_acq_seller import Trade
from etl.services import TradeSettlementStatementPipeline

# WHAT: Resolve the user model for created_by lookups.
# WHY: Support custom user models configured in settings.
User = get_user_model()


class Command(BaseCommand):
    """Run the trade settlement statement extraction workflow."""

    # WHAT: Help text for the command.
    # WHY: Provide CLI guidance for operators.
    help = (
        "Extract trade-level settlement statement data using the ETL pipeline "
        "and persist results to ETL models."
    )

    def add_arguments(self, parser):  # pragma: no cover - argument definitions
        # WHAT: File path argument for the source document.
        # WHY: Required input for extraction.
        parser.add_argument(
            "--file",
            dest="file_path",
            required=True,
            help="Absolute or relative path to the settlement statement document.",
        )
        # WHAT: Optional trade ID for linking the statement.
        # WHY: Associate settlement data with a specific trade.
        parser.add_argument(
            "--trade-id",
            dest="trade_id",
            type=int,
            help="Optional Trade primary key to link the settlement statement.",
        )
        # WHAT: Optional user ID for audit attribution.
        # WHY: Track who initiated the workflow.
        parser.add_argument(
            "--created-by",
            dest="created_by",
            type=int,
            help="Optional user ID to attribute the document record to.",
        )
        # WHAT: Optional uploaded timestamp for the document.
        # WHY: Preserve original ingestion time.
        parser.add_argument(
            "--uploaded-at",
            dest="uploaded_at",
            help="Optional ISO-8601 datetime for original upload time.",
        )

    def handle(self, *args, **options):  # pragma: no cover - orchestration
        # WHAT: Resolve the input file path.
        # WHY: Normalize file handling across platforms.
        file_path = Path(options["file_path"]).expanduser().resolve()
        # WHAT: Validate file existence.
        # WHY: Fail fast with a helpful error.
        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")

        # WHAT: Resolve trade if provided.
        # WHY: Link statement to trade when possible.
        trade = None
        trade_id = options.get("trade_id")
        if trade_id is not None:
            try:
                trade = Trade.objects.get(pk=trade_id)
            except Trade.DoesNotExist as exc:
                raise CommandError(f"Trade {trade_id} does not exist") from exc

        # WHAT: Resolve optional created_by user.
        # WHY: Audit document creation for manual runs.
        created_by_user = None
        created_by = options.get("created_by")
        if created_by is not None:
            try:
                created_by_user = User.objects.get(pk=created_by)
            except User.DoesNotExist as exc:
                raise CommandError(f"User {created_by} does not exist") from exc

        # WHAT: Parse uploaded_at if provided.
        # WHY: Preserve original ingestion timing.
        uploaded_at_value: Optional[str] = options.get("uploaded_at")
        uploaded_at = timezone.now()
        if uploaded_at_value:
            parsed = parse_datetime(uploaded_at_value)
            if parsed is None:
                raise CommandError(
                    "Unable to parse --uploaded-at value. Use ISO-8601 format, e.g. '2024-01-15T13:45:00Z'."
                )
            if timezone.is_naive(parsed):
                parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
            uploaded_at = parsed

        # WHAT: Initialize the pipeline.
        # WHY: Execute extraction and persistence as a single workflow.
        pipeline = TradeSettlementStatementPipeline()

        # WHAT: Run extraction pipeline.
        # WHY: Create document + statement records.
        self.stdout.write(self.style.NOTICE("Starting trade settlement extraction..."))
        statement = pipeline.process_document(
            file_path=file_path,
            trade=trade,
            created_by=created_by_user,
            uploaded_at=uploaded_at,
        )

        # WHAT: Report results for the operator.
        # WHY: Provide immediate feedback in CLI.
        self.stdout.write(self.style.SUCCESS(f"Document ID: {statement.document_id}"))
        self.stdout.write(self.style.SUCCESS(f"Statement ID: {statement.pk}"))
        if statement.trade_id:
            self.stdout.write(self.style.SUCCESS(f"Trade ID: {statement.trade_id}"))
        if statement.statement_date:
            self.stdout.write(self.style.SUCCESS(f"Statement Date: {statement.statement_date}"))
        if statement.settlement_date:
            self.stdout.write(self.style.SUCCESS(f"Settlement Date: {statement.settlement_date}"))

        # WHAT: Display line item count if present.
        # WHY: Confirm adjustments were parsed.
        line_item_count = statement.line_items.count()
        self.stdout.write(self.style.NOTICE(f"Line items: {line_item_count}"))

        self.stdout.write(self.style.SUCCESS("Trade settlement statement processing complete."))
