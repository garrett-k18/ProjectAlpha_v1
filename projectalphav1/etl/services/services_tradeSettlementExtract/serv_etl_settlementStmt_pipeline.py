"""Service workflow for trade-level settlement statement extraction."""

from __future__ import annotations

import logging
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.db import models as dj_models
from django.db import transaction
from django.utils import timezone

from etl.models import (
    ExtractionStatus,
    TradeSettlementStatementDocument,
    TradeSettlementStatementETL,
    TradeSettlementStatementLineItem,
)
from etl.services.services_valuationExtract.serv_etl_gemini_client import (
    build_valuation_gemini_vision_client,
)

# WHAT: Module-level logger for workflow visibility.
# WHY: Capture pipeline diagnostics in Django logs.
logger = logging.getLogger(__name__)

# WHAT: Field names that should not be sent to the extractor prompt.
# WHY: Skip system and relational fields that are not extracted from documents.
_SKIP_FIELD_NAMES = {
    "id",
    "document",
    "trade",
    "extracted_at",
    "created_at",
    "updated_at",
    "created_by",
}


def _enumerate_model_fields(model: dj_models.Model) -> List[str]:
    """Return a sorted list of concrete model fields for prompt guidance."""

    # WHAT: Accumulate fields that are real database columns.
    # WHY: Keep the prompt aligned with stored data.
    fields: List[str] = []
    # WHAT: Iterate all model fields (including relationships).
    # WHY: Filter down to concrete fields only.
    for field in model._meta.get_fields():
        # WHAT: Skip auto-created fields (e.g., reverse relations).
        # WHY: These are not extractable from documents.
        if getattr(field, "auto_created", False):
            continue
        # WHAT: Skip non-concrete fields (e.g., reverse relations).
        # WHY: Only real columns should be extracted.
        if not getattr(field, "concrete", False):
            continue
        # WHAT: Skip explicitly ignored fields.
        # WHY: Avoid sending non-extractable fields to the model.
        if field.name in _SKIP_FIELD_NAMES:
            continue
        # WHAT: Store the field name for prompt schema.
        # WHY: Keep the prompt list human-readable.
        fields.append(field.name)
    # WHAT: Sort for deterministic prompt order.
    # WHY: Stable prompts reduce extraction variability.
    return sorted(fields)


# WHAT: Schema guide for the settlement statement extraction prompt.
# WHY: Tell Gemini which fields to return in the JSON.
SCHEMA_GUIDE_TEXT = "\n".join(
    f"  - {field_name}" for field_name in _enumerate_model_fields(TradeSettlementStatementETL)
)

# WHAT: Prompt template for trade settlement statement extraction.
# WHY: Provide clear instructions and expected JSON structure.
PROMPT_TEMPLATE = f"""
Extract trade-level settlement statement data from this document using vision/OCR.

Return JSON:
{{
  "statement": {{ ... }},
  "line_items": [{{ "description": "", "amount": "", "category": "", "notes": "" }}, ...],
  "warnings": []
}}

Rules:
- Read ALL pages (use OCR if scanned)
- Extract fields listed below
- null for missing values
- Preserve values exactly as shown (do not normalize numbers or dates)
- Return only JSON (no markdown)

Fields:
{SCHEMA_GUIDE_TEXT}
"""


@dataclass
class TradeSettlementExtractionResult:
    """Normalized extraction output for trade settlement statements."""

    # WHAT: Original file path used for extraction.
    # WHY: Useful for auditing and debugging.
    file_path: Path
    # WHAT: MIME type determined for the document.
    # WHY: Helpful for debugging extraction failures.
    mime_type: str
    # WHAT: Timestamp when extraction completed.
    # WHY: Track extractor runtime in logs.
    extracted_at: timezone.datetime
    # WHAT: Parsed statement payload from the extractor.
    # WHY: Source for model persistence.
    statement_payload: Dict[str, Any] = field(default_factory=dict)
    # WHAT: Parsed line items list from the extractor.
    # WHY: Store granular adjustments from the statement.
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    # WHAT: Warning messages returned by the extractor.
    # WHY: Surface extraction caveats to operators.
    warnings: List[str] = field(default_factory=list)


class TradeSettlementExtractionService:
    """Extract trade settlement statement data using Gemini Vision."""

    # WHAT: Default model name for Gemini extraction.
    # WHY: Keep parity with the valuation extraction workflow.
    default_model_name: str = "gemini-2.5-flash"
    # WHAT: Default prompt for trade settlement extraction.
    # WHY: Ensure consistent response structure.
    prompt: str = PROMPT_TEMPLATE

    def __init__(
        self,
        *,
        client=None,
        prompt: Optional[str] = None,
        model_name: str = default_model_name,
        max_document_bytes: int = 50 * 1024 * 1024,
    ) -> None:
        """Initialize the extraction service.

        Args:
            client: Optional Gemini client callable.
            prompt: Optional custom prompt override.
            model_name: Gemini model to use.
            max_document_bytes: Soft limit for file size warnings.
        """

        # WHAT: Use the provided client or build a shared Gemini client.
        # WHY: Share the same Gemini upload client across workflows.
        self.client = client or build_valuation_gemini_vision_client(default_model=model_name)
        # WHAT: Prompt used for extraction.
        # WHY: Allow override for customization/testing.
        self.prompt = prompt or self.prompt
        # WHAT: Gemini model name used by the client.
        # WHY: Keep diagnostics clear in logs.
        self.model_name = model_name
        # WHAT: Soft file size cap for warning purposes.
        # WHY: Large files can exceed Gemini limits or slow processing.
        self.max_document_bytes = max_document_bytes

    def process(self, file_path: Path) -> TradeSettlementExtractionResult:
        """Process a settlement statement document and return normalized output."""

        # WHAT: Normalize to Path object.
        # WHY: Ensure consistent path handling.
        file_path = Path(file_path)
        # WHAT: Confirm file exists before processing.
        # WHY: Fail fast with a clear error.
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        # WHAT: Ensure Gemini client is configured.
        # WHY: Avoid silent failures when API key is missing.
        if self.client is None:
            raise RuntimeError("Gemini vision client is not configured")

        # WHAT: Determine MIME type for the input file.
        # WHY: Gemini needs accurate MIME type for processing.
        mime_type = mimetypes.guess_type(str(file_path))[0] or "application/pdf"
        # WHAT: Read file bytes into memory for upload.
        # WHY: Gemini upload API expects raw bytes.
        file_bytes = file_path.read_bytes()
        # WHAT: Compute file size for logging and warnings.
        # WHY: Large files can trigger Gemini limits.
        file_size_bytes = len(file_bytes)

        # WHAT: Warn when file size exceeds soft limit.
        # WHY: Make it obvious when Gemini may reject or truncate.
        warnings: List[str] = []
        if file_size_bytes > self.max_document_bytes:
            warnings.append(
                f"File size {file_size_bytes} bytes exceeds soft limit {self.max_document_bytes} bytes."
            )

        # WHAT: Call Gemini vision client with document bytes and prompt.
        # WHY: Receive structured JSON extraction payload.
        response = self.client(file_bytes=file_bytes, mime_type=mime_type, prompt=self.prompt)
        # WHAT: Guard against invalid response payloads.
        # WHY: Ensure extraction output is always a dict.
        if not isinstance(response, dict):
            response = {}

        # WHAT: Pull the statement object from the response.
        # WHY: Keep payload aligned with prompt structure.
        statement_payload = response.get("statement") or {}
        # WHAT: Pull line items list from the response.
        # WHY: Preserve granular adjustments and fees.
        line_items = response.get("line_items") or []
        # WHAT: Pull warnings from the response.
        # WHY: Surface extraction issues to operators.
        response_warnings = response.get("warnings") or []

        # WHAT: Normalize warnings to a list of strings.
        # WHY: Ensure we can join warnings safely.
        if not isinstance(response_warnings, list):
            response_warnings = [str(response_warnings)]
        # WHAT: Append response warnings to local list.
        # WHY: Combine extractor warnings with size warnings.
        warnings.extend([str(item) for item in response_warnings])

        # WHAT: Normalize statement payload to dict.
        # WHY: Avoid errors on unexpected response formats.
        if not isinstance(statement_payload, dict):
            statement_payload = {}
            warnings.append("Extractor returned non-dict statement payload.")
        # WHAT: Normalize line items to list of dicts.
        # WHY: Ensure JSON is stored consistently.
        if not isinstance(line_items, list):
            line_items = []
            warnings.append("Extractor returned non-list line_items payload.")

        return TradeSettlementExtractionResult(
            file_path=file_path,
            mime_type=mime_type,
            extracted_at=timezone.now(),
            statement_payload=statement_payload,
            line_items=[item for item in line_items if isinstance(item, dict)],
            warnings=warnings,
        )


class TradeSettlementStatementPipeline:
    """Persist trade settlement extraction results to ETL models."""

    def __init__(self, extractor: Optional[TradeSettlementExtractionService] = None) -> None:
        """Initialize the pipeline with an optional custom extractor."""

        # WHAT: Use provided extractor or default extractor.
        # WHY: Allow dependency injection for testing.
        self.extractor = extractor or TradeSettlementExtractionService()

    @transaction.atomic
    def process_document(
        self,
        file_path: Path,
        *,
        trade=None,
        created_by=None,
        uploaded_at: Optional[timezone.datetime] = None,
    ) -> TradeSettlementStatementETL:
        """Extract and persist a trade settlement statement document."""

        # WHAT: Normalize file path to Path.
        # WHY: Standardize file operations.
        file_path = Path(file_path)
        # WHAT: Ensure the file exists before proceeding.
        # WHY: Avoid creating document records for missing files.
        if not file_path.exists():
            raise FileNotFoundError(file_path)

        # WHAT: Create the document metadata record.
        # WHY: Capture lineage and status before extraction runs.
        # WHAT: Detect MIME type for the document.
        # WHY: Store accurate file metadata for auditing.
        mime_type = mimetypes.guess_type(str(file_path))[0] or file_path.suffix.lower()
        document = TradeSettlementStatementDocument.objects.create(
            file_name=file_path.name,
            file_path=str(file_path),
            file_mime_type=mime_type,
            file_size_bytes=file_path.stat().st_size,
            uploaded_at=uploaded_at or timezone.now(),
            status=ExtractionStatus.IN_PROGRESS,
            created_by=created_by,
        )

        # WHAT: Attempt extraction with error handling.
        # WHY: Ensure document status is updated on failure.
        try:
            extraction_result = self.extractor.process(file_path)
        except Exception as exc:
            # WHAT: Mark document as failed with message.
            # WHY: Persist failure state for audit.
            document.status = ExtractionStatus.FAILED
            document.status_message = str(exc)
            document.processed_at = timezone.now()
            document.save(update_fields=["status", "status_message", "processed_at"])
            raise

        # WHAT: Persist statement record using extracted payload.
        # WHY: Store structured settlement data for downstream use.
        statement = self._persist_statement(
            document=document,
            payload=extraction_result.statement_payload,
            line_items=extraction_result.line_items,
            trade=trade,
            created_by=created_by,
        )

        # WHAT: Update document status based on persistence success.
        # WHY: Track pipeline outcomes with consistent states.
        document.status = ExtractionStatus.COMPLETE if statement else ExtractionStatus.PARTIAL
        # WHAT: Store warnings in the status message (trimmed).
        # WHY: Make warnings visible without extra queries.
        document.status_message = "; ".join(extraction_result.warnings)[:1000]
        document.processed_at = timezone.now()
        document.save(update_fields=["status", "status_message", "processed_at"])

        return statement

    def _persist_statement(
        self,
        *,
        document: TradeSettlementStatementDocument,
        payload: Dict[str, Any],
        line_items: List[Dict[str, Any]],
        trade=None,
        created_by=None,
    ) -> TradeSettlementStatementETL:
        """Persist the settlement statement payload to the ETL model."""

        # WHAT: Prepare model kwargs from payload.
        # WHY: Filter and coerce values based on model fields.
        statement_kwargs = self._prepare_model_kwargs(TradeSettlementStatementETL, payload)
        # WHAT: Attach required foreign keys and metadata.
        # WHY: Preserve lineage to the document and user.
        statement_kwargs["document"] = document
        statement_kwargs["trade"] = trade
        statement_kwargs["created_by"] = created_by

        # WHAT: Create the ETL record.
        # WHY: Persist normalized extraction data.
        statement = TradeSettlementStatementETL.objects.create(**statement_kwargs)

        # WHAT: Persist line items as separate raw records.
        # WHY: Keep line items normalized and queryable.
        self._persist_line_items(statement=statement, line_items=line_items)

        return statement

    def _persist_line_items(
        self,
        *,
        statement: TradeSettlementStatementETL,
        line_items: List[Dict[str, Any]],
    ) -> None:
        """Persist line items in the raw line item model."""

        # WHAT: Exit early if no line items were extracted.
        # WHY: Avoid unnecessary database work.
        if not line_items:
            return

        # WHAT: Build line item records with ordered line numbers.
        # WHY: Preserve original ordering from the statement.
        items_to_create: List[TradeSettlementStatementLineItem] = []
        for index, item in enumerate(line_items, start=1):
            # WHAT: Normalize each field to string for raw storage.
            # WHY: Preserve source formatting without coercion.
            description = "" if item.get("description") is None else str(item.get("description"))
            amount = "" if item.get("amount") is None else str(item.get("amount"))
            category = "" if item.get("category") is None else str(item.get("category"))
            notes = "" if item.get("notes") is None else str(item.get("notes"))

            items_to_create.append(
                TradeSettlementStatementLineItem(
                    statement=statement,
                    line_number=index,
                    description=description,
                    amount=amount,
                    category=category,
                    notes=notes,
                )
            )

        # WHAT: Bulk create all line items.
        # WHY: Improve performance for statements with many items.
        TradeSettlementStatementLineItem.objects.bulk_create(items_to_create)

    def _prepare_model_kwargs(
        self,
        model: dj_models.Model,
        values: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Coerce payload values into model-compatible kwargs."""

        # WHAT: Build a map of valid fields on the model.
        # WHY: Filter payload keys to actual model fields.
        valid_fields: Dict[str, dj_models.Field] = {
            field.name: field
            for field in model._meta.get_fields()
            if hasattr(field, "attname") and not field.many_to_many and not field.auto_created
        }

        # WHAT: Prepare output dictionary for model creation.
        # WHY: Separate clean data from raw payload.
        prepared: Dict[str, Any] = {}

        # WHAT: Iterate over payload key/value pairs.
        # WHY: Coerce and validate each potential field.
        for key, value in values.items():
            # WHAT: Resolve the model field for the payload key.
            # WHY: Skip unknown fields gracefully.
            field = valid_fields.get(key)
            if not field:
                continue
            # WHAT: Coerce value to the field's expected type.
            # WHY: Prevent database errors on invalid types.
            coerced = self._coerce_field_value(field, value)
            # WHAT: Skip empty values for non-nullable fields.
            # WHY: Avoid integrity issues when data is missing.
            if coerced is None:
                if getattr(field, "null", False):
                    prepared[key] = None
                else:
                    continue
            prepared[key] = coerced

        return prepared

    def _coerce_field_value(self, field: dj_models.Field, value: Any) -> Optional[Any]:
        """Normalize a value for a given Django model field."""

        # WHAT: Short-circuit null values.
        # WHY: Preserve missing data in the payload.
        if value is None:
            return None

        # WHAT: Normalize string values.
        # WHY: Avoid empty strings from breaking coercion.
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None

        # WHAT: Default to string conversion.
        # WHY: Preserve values for CharField/TextField.
        return str(value)


__all__ = [
    "TradeSettlementExtractionService",
    "TradeSettlementStatementPipeline",
    "TradeSettlementExtractionResult",
]
