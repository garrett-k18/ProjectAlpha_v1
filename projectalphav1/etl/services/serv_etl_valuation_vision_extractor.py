"""Claude vision-powered extraction service for valuation documents."""

from __future__ import annotations

import json
import logging
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.db import models as dj_models
from django.utils import timezone

from etl.models import ComparablesETL, RepairItem, ValuationETL
from etl.services.serv_etl_claude_client import build_valuation_claude_vision_client

logger = logging.getLogger(__name__)

_SKIP_FIELD_NAMES = {
    "id",
    "asset_hub",
    "valuation",
    "document",
    "original_document",
    "created_at",
    "updated_at",
    "created_by",
}

MODEL_REGISTRY: Dict[str, dj_models.Model] = {
    "etl.ValuationETL": ValuationETL,
    "etl.ComparablesETL": ComparablesETL,
    "etl.RepairItem": RepairItem,
}


def _enumerate_model_fields(model: dj_models.Model) -> List[str]:
    fields: List[str] = []
    for field in model._meta.get_fields():
        if getattr(field, "auto_created", False):
            continue
        if not getattr(field, "concrete", False):
            continue
        if field.name in _SKIP_FIELD_NAMES:
            continue
        fields.append(field.name)
    return sorted(fields)


def _choice_summary(field: dj_models.Field) -> str:
    choices = getattr(field, "flatchoices", None)
    if not choices:
        return ""
    values: List[str] = []
    for choice_key, _ in choices:
        if choice_key in (None, ""):
            continue
        values.append(str(choice_key))
        if len(values) >= 12:
            values.append("…")
            break
    if not values:
        return ""
    return f" (choices: {', '.join(values)})"


def _build_schema_guide() -> str:
    lines: List[str] = []
    for label, model in MODEL_REGISTRY.items():
        lines.append(f"{label} fields:")
        for field in model._meta.get_fields():
            if getattr(field, "auto_created", False):
                continue
            if not getattr(field, "concrete", False):
                continue
            if field.name in _SKIP_FIELD_NAMES:
                continue
            summary = _choice_summary(field)
            lines.append(f"  - {field.name}{summary}")
    return "\n".join(lines)


SCHEMA_GUIDE_TEXT = _build_schema_guide()

PROMPT_TEMPLATE = f"""
You are an expert valuation analyst. Extract every available field from the provided
Broker Price Opinion/Appraisal document. Return ONLY strict JSON with the structure:
{{
  "valuation": {{ ... }},
  "comparables": [{{ ... }}, ...],
  "repairs": [{{ ... }}, ...],
  "inferred_source": "",
  "warnings": []
}}

Requirements:
- Populate every field listed in the schema guide. Use null when information is missing.
- Use plain numbers (no currency symbols or commas) for numeric fields.
- Use ISO dates (YYYY-MM-DD) for date fields.
- Use canonical choice codes exactly as specified in the schema guide.
- Always include an array for "comparables" and "repairs" (may be empty).
- Do not add commentary outside the JSON. Do not wrap the JSON in code fences.

Schema guide:
{SCHEMA_GUIDE_TEXT}
"""

DEFAULT_CONFIDENCE = 0.85


@dataclass
class FieldExtractionRecord:
    model_label: str
    field: str
    value: Any
    raw_text: str
    confidence: float = DEFAULT_CONFIDENCE
    method: str = "ai"
    requires_review: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentExtractionResult:
    file_path: Path
    mime_type: str
    extracted_at: timezone.datetime
    fields: List[FieldExtractionRecord]
    valuation_payload: Dict[str, Any] = field(default_factory=dict)
    comparables_payload: List[Dict[str, Any]] = field(default_factory=list)
    repairs_payload: List[Dict[str, Any]] = field(default_factory=list)
    raw_response: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    inferred_source: Optional[str] = None


class ClaudeVisionExtractionService:
    """Uploads full documents to Claude Vision and normalises the JSON output."""

    prompt: str = PROMPT_TEMPLATE
    default_confidence: float = DEFAULT_CONFIDENCE

    def __init__(
        self,
        *,
        client=None,
        prompt: str = PROMPT_TEMPLATE,
        model_name: str = "claude-3-5-haiku-20241022",
    ) -> None:
        self.client = client or build_valuation_claude_vision_client(default_model=model_name)
        self.prompt = prompt
        self.model_name = model_name

    def process(self, file_path: Path) -> DocumentExtractionResult:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        if self.client is None:
            raise RuntimeError("Claude vision client is not configured")

        mime_type = mimetypes.guess_type(str(file_path))[0] or "application/pdf"
        file_bytes = file_path.read_bytes()

        logger.info("Sending %s to Claude vision model %s", file_path.name, self.model_name)
        response = self.client(file_bytes=file_bytes, mime_type=mime_type, prompt=self.prompt)
        if not isinstance(response, dict):
            raise ValueError("Claude vision returned an unexpected response payload")

        valuation_data = self._safe_dict(response.get("valuation"))
        comparables_data = self._safe_list_of_dicts(response.get("comparables"))
        repairs_data = self._safe_list_of_dicts(response.get("repairs"))
        inferred_source = response.get("inferred_source")
        warnings = response.get("warnings") or []
        if not isinstance(warnings, list):
            warnings = [str(warnings)]

        fields: List[FieldExtractionRecord] = []
        fields.extend(self._build_field_records("etl.ValuationETL", valuation_data))
        fields.extend(self._build_table_records("etl.ComparablesETL", comparables_data))
        fields.extend(self._build_table_records("etl.RepairItem", repairs_data))

        if inferred_source and not valuation_data.get("valuation_type"):
            valuation_record = FieldExtractionRecord(
                model_label="etl.ValuationETL",
                field="valuation_type",
                value=inferred_source,
                raw_text=inferred_source,
                confidence=DEFAULT_CONFIDENCE,
                method="ai",
                requires_review=False,
                metadata={"source": "vision_inferred"},
            )
            fields.append(valuation_record)

        return DocumentExtractionResult(
            file_path=file_path,
            mime_type=mime_type,
            extracted_at=timezone.now(),
            fields=fields,
            valuation_payload=valuation_data,
            comparables_payload=comparables_data,
            repairs_payload=repairs_data,
            raw_response=response,
            warnings=warnings,
            inferred_source=inferred_source or valuation_data.get("valuation_type"),
        )

    @staticmethod
    def _safe_dict(value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            return value
        return {}

    @staticmethod
    def _safe_list_of_dicts(value: Any) -> List[Dict[str, Any]]:
        if not isinstance(value, list):
            return []
        results: List[Dict[str, Any]] = []
        for item in value:
            if isinstance(item, dict):
                results.append(item)
        return results

    def _build_field_records(self, model_label: str, payload: Dict[str, Any]) -> List[FieldExtractionRecord]:
        records: List[FieldExtractionRecord] = []
        for field_name, value in payload.items():
            record = FieldExtractionRecord(
                model_label=model_label,
                field=field_name,
                value=value,
                raw_text=json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else ("" if value is None else str(value)),
                confidence=DEFAULT_CONFIDENCE,
                method="ai",
                requires_review=False,
                metadata={"source": "vision"},
            )
            records.append(record)
        return records

    def _build_table_records(self, model_label: str, rows: List[Dict[str, Any]]) -> List[FieldExtractionRecord]:
        records: List[FieldExtractionRecord] = []
        for index, payload in enumerate(rows, start=1):
            record = FieldExtractionRecord(
                model_label=model_label,
                field=f"row_{index}",
                value=payload,
                raw_text=json.dumps(payload, ensure_ascii=False),
                confidence=DEFAULT_CONFIDENCE,
                method="ai",
                requires_review=False,
                metadata={"source": "vision", "row_index": index},
            )
            records.append(record)
        return records


__all__ = [
    "ClaudeVisionExtractionService",
    "DocumentExtractionResult",
    "FieldExtractionRecord",
]
