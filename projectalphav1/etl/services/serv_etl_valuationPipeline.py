"""High-level pipeline that persists valuation extraction results."""

from __future__ import annotations

import datetime
import logging
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from django.db import models as dj_models, transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from core.models import AssetIdHub
from etl.models import (
    ComparablesETL,
    ExtractionFieldResult,
    ExtractionLogEntry,
    ExtractionStatus,
    RepairItem,
    ValuationDocument,
    ValuationETL,
)
from etl.services.serv_etl_valuation_document_extractor import (
    ClaudeFieldAugmenter,
    DocumentExtractionResult,
    DocumentExtractionService,
    FieldExtractionEngine,
    FieldExtractionRecord,
)

logger = logging.getLogger(__name__)


@dataclass
class PipelineSummary:
    """Outcome metadata returned after pipeline execution."""

    document: ValuationDocument
    valuation: Optional[ValuationETL]
    field_results: Sequence[ExtractionFieldResult]
    warnings: Sequence[str] = field(default_factory=list)
    source_used: Optional[str] = None


class ValuationExtractionPipeline:
    """Coordinates document extraction with database persistence."""

    def __init__(
        self,
        extractor: Optional[DocumentExtractionService] = None,
        *,
        claude_client: Optional[ClaudeFieldAugmenter] = None,
        high_confidence_threshold: float = 0.98,
        ai_threshold: float = 0.85,
        review_threshold: float = 0.75,
    ) -> None:
        claude_augmenter = claude_client or ClaudeFieldAugmenter()
        self.extractor = extractor or DocumentExtractionService(
            claude_augmenter=claude_augmenter,
            high_confidence_threshold=high_confidence_threshold,
            ai_threshold=ai_threshold,
            review_threshold=review_threshold,
        )

    # Public API ------------------------------------------------------------------

    @transaction.atomic
    def process_document(
        self,
        file_path: Path,
        *,
        asset_hub: AssetIdHub,
        source: Optional[str] = None,
        created_by=None,
        uploaded_at: Optional[timezone.datetime] = None,
    ) -> PipelineSummary:
        """Extract valuation data from a document and persist results.

        Args:
            file_path: Local path to the source document.
            asset_hub: Asset hub to associate the valuation with.
            source: Choice value from ``Valuation.Source``.
            created_by: Optional user instance for audit metadata.
            uploaded_at: Optional timestamp to backfill original upload time.
        """

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(file_path)

        document = self._create_document_record(
            file_path=file_path,
            created_by=created_by,
            uploaded_at=uploaded_at or timezone.now(),
        )

        try:
            extraction_result = self.extractor.process(file_path)
            logger.info(
                "Extraction produced %d field(s) for %s",
                len(extraction_result.fields),
                file_path,
            )
        except Exception as exc:
            logger.exception("Failed to extract valuation document: %s", file_path)
            document.status = ExtractionStatus.FAILED
            document.status_message = str(exc)
            document.processed_at = timezone.now()
            document.save(update_fields=["status", "status_message", "processed_at"])
            raise

        field_results = self._persist_field_results(document, extraction_result.fields)
        warnings = list(extraction_result.warnings)
        self._log_messages(document, extraction_result)

        inferred_source = extraction_result.inferred_source
        chosen_source = source or inferred_source
        if source and inferred_source and source != inferred_source:
            mismatch_message = (
                f"Provided valuation source '{source}' differs from inferred '{inferred_source}'."
            )
            warnings.append(mismatch_message)
            self._write_log(document, "warning", mismatch_message)
        elif chosen_source:
            origin = "override" if source else "inferred"
            self._write_log(
                document,
                "info",
                f"Using valuation source '{chosen_source}' ({origin}).",
            )
        else:
            no_source_msg = "Unable to determine valuation source from document; skipping ValuationETL creation."
            warnings.append(no_source_msg)
            self._write_log(document, "warning", no_source_msg)

        valuation = None
        if field_results and chosen_source:
            try:
                valuation = self._persist_valuation(
                    asset_hub=asset_hub,
                    source=chosen_source,
                    document=document,
                    field_records=extraction_result.fields,
                )
            except Exception as exc:
                warnings.append(f"Valuation persistence failed: {exc}")
                logger.warning("Valuation persistence failed for %s: %s", file_path, exc)

        document.status = (
            ExtractionStatus.COMPLETE if valuation else ExtractionStatus.PARTIAL
        )
        document.status_message = "; ".join(warnings)[:1000]
        document.processed_at = timezone.now()
        document.save(update_fields=["status", "status_message", "processed_at"])

        return PipelineSummary(
            document=document,
            valuation=valuation,
            field_results=field_results,
            warnings=warnings,
            source_used=chosen_source,
        )

    # Internal helpers -------------------------------------------------------------

    def _create_document_record(
        self,
        *,
        file_path: Path,
        created_by,
        uploaded_at: timezone.datetime,
    ) -> ValuationDocument:
        document = ValuationDocument.objects.create(
            file_name=file_path.name,
            file_path=str(file_path),
            file_mime_type=file_path.suffix.lower(),
            file_size_bytes=file_path.stat().st_size,
            uploaded_at=uploaded_at,
            status=ExtractionStatus.IN_PROGRESS,
            created_by=created_by,
        )
        return document

    def _persist_field_results(
        self,
        document: ValuationDocument,
        records: Sequence[FieldExtractionRecord],
    ) -> List[ExtractionFieldResult]:
        stored: List[ExtractionFieldResult] = []
        for record in records:
            value_text, value_json = self._serialise_value(record.value)
            stored.append(
                ExtractionFieldResult.objects.create(
                    document=document,
                    target_model=record.model_label,
                    target_field=record.field,
                    value_text=value_text,
                    value_json=value_json,
                    confidence=record.confidence,
                    extraction_method=record.method,
                    requires_review=record.requires_review,
                )
            )
        return stored

    def _persist_valuation(
        self,
        *,
        asset_hub: AssetIdHub,
        source: str,
        document: ValuationDocument,
        field_records: Sequence[FieldExtractionRecord],
    ) -> Optional[ValuationETL]:
        if not source:
            return None

        valuation_fields, grouped_records = self._split_by_model(field_records)
        if not valuation_fields:
            return None

        valuation_kwargs = self._filter_model_kwargs(ValuationETL, valuation_fields)
        if not valuation_kwargs:
            return None

        valuation_kwargs.setdefault("inspection_date", timezone.now().date())
        valuation_kwargs.setdefault("loan_number", "UNKNOWN")

        valuation = ValuationETL.objects.create(
            asset_hub=asset_hub,
            source=source,
            **valuation_kwargs,
        )

        ExtractionLogEntry.objects.create(
            document=document,
            level="info",
            message=f"Created ValuationETL {valuation.pk} with fields: {sorted(valuation_kwargs.keys())}",
        )

        comparables_created = self._persist_comparables(
            valuation,
            grouped_records.get("etl.ComparablesETL", []),
            document,
        )
        repairs_created = self._persist_repair_items(
            valuation,
            grouped_records.get("etl.RepairItem", []),
            document,
        )

        if comparables_created:
            self._write_log(
                document,
                "info",
                f"Created {len(comparables_created)} comparable record(s).",
            )
        if repairs_created:
            self._write_log(
                document,
                "info",
                f"Created {len(repairs_created)} repair item(s).",
            )

        return valuation

    @staticmethod
    def _split_by_model(
        records: Sequence[FieldExtractionRecord],
    ) -> Tuple[Dict[str, Dict[str, object]], Dict[str, List[FieldExtractionRecord]]]:
        model_map: Dict[str, Dict[str, object]] = {}
        grouped_records: Dict[str, List[FieldExtractionRecord]] = {}
        for record in records:
            grouped_records.setdefault(record.model_label, []).append(record)
            if record.model_label not in model_map:
                model_map[record.model_label] = {}
            if isinstance(record.value, (dict, list)):
                continue
            model_map[record.model_label][record.field] = record.value
        return model_map.get("etl.ValuationETL", {}), grouped_records

    @staticmethod
    def _filter_model_kwargs(model, values: Dict[str, object]) -> Dict[str, object]:
        valid_fields = {
            field.name
            for field in model._meta.get_fields()
            if hasattr(field, "attname") and not field.many_to_many
        }
        return {
            key: value
            for key, value in values.items()
            if key in valid_fields
        }

    @staticmethod
    def _serialise_value(value) -> Tuple[str, Optional[dict]]:
        if isinstance(value, (dict, list)):
            return "", value
        return str(value), None

    def _persist_comparables(
        self,
        valuation: ValuationETL,
        records: Sequence[FieldExtractionRecord],
        document: ValuationDocument,
    ) -> List[ComparablesETL]:
        created: List[ComparablesETL] = []
        if not records:
            return created

        for idx, record in enumerate(records, start=1):
            payload = record.value
            if not isinstance(payload, dict):
                continue
            enriched_payload = dict(payload)
            enriched_payload.setdefault("comp_number", payload.get("comp_number") or idx)
            kwargs = self._prepare_model_kwargs(ComparablesETL, enriched_payload)

            if "address" not in kwargs or not kwargs["address"]:
                self._write_log(document, "warning", f"Skipped comparable {idx}: missing address.")
                continue
            if "sale_price" not in kwargs or kwargs["sale_price"] is None:
                self._write_log(document, "warning", f"Skipped comparable {idx}: missing sale price.")
                continue
            if "comp_type" not in kwargs or kwargs["comp_type"] is None:
                default_comp_type = self._default_choice(ComparablesETL, "comp_type")
                if default_comp_type:
                    kwargs["comp_type"] = default_comp_type

            try:
                comparable = ComparablesETL.objects.create(valuation=valuation, **kwargs)
            except Exception as exc:  # pragma: no cover - best effort logging
                self._write_log(document, "warning", f"Failed to create comparable {idx}: {exc}")
            else:
                created.append(comparable)

        return created

    def _persist_repair_items(
        self,
        valuation: ValuationETL,
        records: Sequence[FieldExtractionRecord],
        document: ValuationDocument,
    ) -> List[RepairItem]:
        created: List[RepairItem] = []
        if not records:
            return created

        for idx, record in enumerate(records, start=1):
            payload = record.value
            if not isinstance(payload, dict):
                continue
            enriched_payload = dict(payload)
            enriched_payload.setdefault("repair_number", payload.get("repair_number") or idx)
            enriched_payload.setdefault("priority", payload.get("priority") or 3)
            kwargs = self._prepare_model_kwargs(RepairItem, enriched_payload)

            if "repair_type" not in kwargs or kwargs["repair_type"] is None:
                default_type = self._default_choice(RepairItem, "repair_type")
                if default_type:
                    kwargs["repair_type"] = default_type
            if "category" not in kwargs or kwargs["category"] is None:
                default_category = self._default_choice(RepairItem, "category")
                if default_category:
                    kwargs["category"] = default_category
            if "description" not in kwargs:
                kwargs["description"] = payload.get("description", "")
            if "estimated_cost" not in kwargs or kwargs["estimated_cost"] is None:
                kwargs["estimated_cost"] = Decimal("0")
            if "priority" not in kwargs or kwargs["priority"] is None:
                kwargs["priority"] = 3
            if "is_required" not in kwargs or kwargs["is_required"] is None:
                kwargs["is_required"] = False

            try:
                repair = RepairItem.objects.create(valuation=valuation, **kwargs)
            except Exception as exc:  # pragma: no cover - best effort logging
                self._write_log(document, "warning", f"Failed to create repair {idx}: {exc}")
            else:
                created.append(repair)

        return created

    def _prepare_model_kwargs(
        self,
        model: dj_models.Model,
        values: Dict[str, object],
    ) -> Dict[str, object]:
        valid_fields: Dict[str, dj_models.Field] = {
            field.name: field
            for field in model._meta.get_fields()
            if hasattr(field, "attname") and not field.many_to_many and not field.auto_created
        }
        prepared: Dict[str, object] = {}

        for key, value in values.items():
            field = valid_fields.get(key)
            if not field:
                continue
            coerced = self._coerce_field_value(field, value)
            if coerced is None:
                if not getattr(field, "null", False) and not getattr(field, "blank", False):
                    continue
            prepared[key] = coerced

        return prepared

    def _coerce_field_value(self, field: dj_models.Field, value: object) -> Optional[object]:
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None

        if isinstance(field, dj_models.BooleanField):
            if isinstance(value, bool):
                return value
            lowered = str(value).strip().lower()
            if lowered in {"yes", "true", "1", "y"}:
                return True
            if lowered in {"no", "false", "0", "n"}:
                return False
            return None

        if isinstance(field, dj_models.DecimalField):
            try:
                cleaned = re.sub(r"[^0-9\.-]", "", str(value))
                if cleaned in {"", "-", ".", "-."}:
                    return None
                return Decimal(cleaned)
            except (InvalidOperation, ValueError, TypeError):
                return None

        if isinstance(field, dj_models.IntegerField):
            try:
                cleaned = re.sub(r"[^0-9\.-]", "", str(value))
                if cleaned in {"", "-", ".", "-."}:
                    return None
                return int(float(cleaned))
            except (ValueError, TypeError):
                return None

        if isinstance(field, dj_models.FloatField):
            try:
                cleaned = re.sub(r"[^0-9\.-]", "", str(value))
                if cleaned in {"", "-", ".", "-."}:
                    return None
                return float(cleaned)
            except (ValueError, TypeError):
                return None

        if isinstance(field, dj_models.DateField):
            if isinstance(value, datetime.date):
                return value
            parsed = parse_date(str(value))
            return parsed

        if hasattr(field, "choices") and field.choices:
            choice = self._normalize_choice(field, value)
            if choice is not None:
                return choice
            if not getattr(field, "blank", False):
                return None

        if isinstance(field, dj_models.JSONField):
            return value

        return str(value)

    def _normalize_choice(self, field: dj_models.Field, value: object) -> Optional[object]:
        value_str = str(value).strip()
        if not value_str:
            return None
        choice_map: Dict[str, object] = {}
        for key, label in field.flatchoices:
            if key in (None, ""):
                continue
            forms = {
                str(key),
                str(label),
                re.sub(r"\W+", "", str(key)),
                re.sub(r"\W+", "", str(label)),
            }
            for form in forms:
                choice_map[form.lower()] = key

        value_norm = value_str.lower()
        value_slug = re.sub(r"\W+", "", value_norm)
        if value_norm in choice_map:
            return choice_map[value_norm]
        if value_slug in choice_map:
            return choice_map[value_slug]
        return None

    @staticmethod
    def _default_choice(model: dj_models.Model, field_name: str) -> Optional[object]:
        field = model._meta.get_field(field_name)
        try:
            first_choice = next(iter(field.flatchoices))
        except StopIteration:
            return None
        key = first_choice[0]
        return key if key not in (None, "") else None

    def _log_messages(
        self,
        document: ValuationDocument,
        extraction_result: DocumentExtractionResult,
    ) -> None:
        for warning in extraction_result.warnings:
            self._write_log(document, "warning", warning)
        if not extraction_result.warnings:
            self._write_log(document, "info", "Extraction completed without warnings.")

    @staticmethod
    def _write_log(document: ValuationDocument, level: str, message: str) -> None:
        ExtractionLogEntry.objects.create(
            document=document,
            level=level,
            message=message[:1000],
        )


__all__ = [
    "ValuationExtractionPipeline",
    "PipelineSummary",
]
