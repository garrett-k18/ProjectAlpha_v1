from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from core.models import AssetIdHub
from core.models.valuations import Valuation
from etl.services import ValuationExtractionPipeline

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Extract valuation data from a document using the ValuationExtractionPipeline "
        "and persist results to the ValuationETL models."
    )

    def add_arguments(self, parser):  # pragma: no cover - argument definitions
        parser.add_argument(
            "--file",
            dest="file_path",
            required=True,
            help="Absolute or relative path to the document to process.",
        )
        parser.add_argument(
            "--asset",
            dest="asset_id",
            required=True,
            type=int,
            help="Primary key of the AssetIdHub record to attach the valuation to.",
        )
        parser.add_argument(
            "--source",
            dest="source",
            choices=list(Valuation.Source.values),
            help=(
                "Optional valuation source override. If omitted, the extractor will attempt to "
                "infer BPO/Appraisal from the document text."
            ),
        )
        parser.add_argument(
            "--created-by",
            dest="created_by",
            type=int,
            help="Optional user ID to attribute the ValuationDocument record to.",
        )
        parser.add_argument(
            "--uploaded-at",
            dest="uploaded_at",
            help="Optional ISO-8601 datetime to record when the document was uploaded.",
        )

    def handle(self, *args, **options):  # pragma: no cover - orchestration
        file_path = Path(options["file_path"]).expanduser().resolve()
        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")

        asset_id = options["asset_id"]
        try:
            asset = AssetIdHub.objects.get(pk=asset_id)
        except AssetIdHub.DoesNotExist as exc:
            raise CommandError(f"AssetIdHub {asset_id} does not exist") from exc

        created_by_user = None
        created_by = options.get("created_by")
        if created_by is not None:
            try:
                created_by_user = User.objects.get(pk=created_by)
            except User.DoesNotExist as exc:
                raise CommandError(f"User {created_by} does not exist") from exc

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

        pipeline = ValuationExtractionPipeline()

        self.stdout.write(self.style.NOTICE("Starting valuation extraction..."))
        summary = pipeline.process_document(
            file_path=file_path,
            asset_hub=asset,
            source=options["source"],
            created_by=created_by_user,
            uploaded_at=uploaded_at,
        )

        self.stdout.write(self.style.SUCCESS(f"Document ID: {summary.document.pk}"))
        if summary.valuation:
            self.stdout.write(
                self.style.SUCCESS(
                    f"ValuationETL ID: {summary.valuation.pk} (asset {asset.pk}, source {summary.valuation.source})"
                )
            )
        else:
            self.stdout.write(self.style.WARNING("ValuationETL not created (check warnings/logs)."))

        if summary.warnings:
            self.stdout.write(self.style.WARNING("Warnings:"))
            for warning in summary.warnings:
                self.stdout.write(f"  - {warning}")

        self.stdout.write(self.style.NOTICE("Persisted fields:"))
        for field_result in summary.field_results:
            value = field_result.value_json if field_result.value_json else field_result.value_text
            value_display = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
            self.stdout.write(
                f"  [{field_result.confidence}] {field_result.target_model}.{field_result.target_field} -> {value_display}"
            )

        self.stdout.write(self.style.SUCCESS("Valuation document processing complete."))
