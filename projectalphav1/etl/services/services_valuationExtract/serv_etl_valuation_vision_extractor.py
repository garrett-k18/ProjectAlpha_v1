"""Gemini vision-powered extraction service for valuation documents.

This service uses Google's Gemini 2.5 Flash model to extract structured data
from valuation documents (PDFs, images, etc.). The service:
- Compresses large files before processing
- Uses Gemini's document vision capabilities
- Extracts fields and returns structured JSON
- Writes extracted data to Django models
"""

from __future__ import annotations

import io
import json
import logging
import mimetypes
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from django.db import models as dj_models
from django.utils import timezone

from etl.models import ComparablesETL, RepairItem, ValuationETL
from etl.services.services_valuationExtract.serv_etl_gemini_client import build_valuation_gemini_vision_client

# Import pypdf for PDF processing and compression
try:  # pragma: no cover - optional dependency
    from pypdf import PdfReader, PdfWriter
except Exception:  # pragma: no cover - best effort optional import
    PdfReader = None  # type: ignore
    PdfWriter = None  # type: ignore

# Import PIL for image compression
try:  # pragma: no cover - optional dependency
    from PIL import Image
except Exception:  # pragma: no cover - best effort optional import
    Image = None  # type: ignore

logger = logging.getLogger(__name__)

_SKIP_FIELD_NAMES = {
    # System/Django fields (always skip)
    "id",
    "asset_hub",
    "valuation",
    "document",
    "original_document",
    "created_at",
    "updated_at",
    "created_by",
    
    # Fields marked as "Remove" - excluded from extraction
    "hoa_name",
    "hoa_phone",
    "neighborhood_pride_of_ownership",
    "internal_notes",
    "partner_comments",
    "vendor_comments",
    "owner_name",               # Not needed - property owner info
    "listing_broker_contact",   # Not needed - have listing_broker
    "basement_percent_finished", # Not needed - have basement_square_feet
    "basement_rooms",            # Not needed - have basement_square_feet
    "quality_rating",            # Not needed - have condition field
    # Feature consolidation - removed detailed fields
    "has_spa",
    "pool_type",
    "view",
    "has_porch",
    "has_patio",
    "patio_deck_description",
    "number_of_fireplaces",
    "fencing_type",
    "other_features",
    "proximity_to_amenities",
    # Appraisal-specific (not needed for BPOs)
    "appraisal_purpose",
    "location_type",
    "location_view",
    # Market analysis fields removed
    "avg_neighborhood_age",
    "predominant_ownership",
    "percentage_owner_occupancy",
    "neighborhood_predominate_value",
    # Marketability
    "most_likely_buyer_type",
    "financing_issues",
    # Comparable proximity consolidation (keep proximity_miles only)
    "proximity_direction",
    "proximity_to_subject",
    "calculated_distance_miles",
    # Comparable adjustment details (keep total_adjustments & adjusted_sale_price only)
    "agent_adjustments",
    "adjustment_location",
    "adjustment_site_view",
    "adjustment_design_appeal",
    "adjustment_quality",
    "adjustment_age",
    "adjustment_condition",
    "adjustment_above_grade_rooms",
    "adjustment_gross_living_area",
    "adjustment_basement",
    "adjustment_functional_utility",
    "adjustment_heating_cooling",
    "adjustment_garage_carport",
    "adjustment_porch_patio_deck",
    "adjustment_other",
    "adjustments_description",
    # Comparable features already removed (matching ValuationETL)
    "effective_age",  # from comparables
    # Repair item fields removed (simplified)
    "severity",
    "repair_number",
    "priority",
    "is_required",  # Renamed to repair_recommended
    # Consolidated fields (removed duplicates)
    "full_bathrooms",
    "half_bathrooms",
    "lot_size_square_feet",
    "cumulative_days_on_market",
    "list_price_at_sale",
    "active_days_on_market",
    "total_days_on_market",
    "repairs_to_bring_to_market",
    "deferred_maintenance_cost",
    # Calculated fields (computed on-demand)
    "price_per_sqft",  # Computed: sale_price / living_area
    # Market fields removed (not consistently in BPOs)
    "housing_supply",
    "reo_driven_market",
    "num_reo_ss_listings",
    "num_boarded_properties",
    "new_construction_in_area",
    "seasonal_market",
    # Note: subdivision, school_district, parking_type, data_source, data_source_id - KEEPING these
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


def _build_schema_guide(minimal: bool = True) -> str:
    """Build schema guide for extraction prompt.
    
    Args:
        minimal: If True, only list field names (faster, smaller prompt)
                 If False, include choice values (slower, more accurate)
    """
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
            
            if minimal:
                # Just list field name (much smaller prompt)
                lines.append(f"  - {field.name}")
            else:
                # Include choice values (larger prompt, more accurate)
                summary = _choice_summary(field)
                lines.append(f"  - {field.name}{summary}")
    
    return "\n".join(lines)


# Use minimal=True for faster extraction (50%+ smaller prompt)
# Set minimal=False if you need more accuracy with choice fields
SCHEMA_GUIDE_TEXT = _build_schema_guide(minimal=True)

# Gemini File API supports up to 50MB files, but we'll use 20MB for safety
DEFAULT_MAX_DOCUMENT_BYTES = 20 * 1024 * 1024  # ~20 MB Gemini File API limit
# Target compression size - compress files larger than this
COMPRESSION_THRESHOLD_BYTES = 10 * 1024 * 1024  # ~10 MB

PROMPT_TEMPLATE = f"""
Extract property valuation data from this document using vision/OCR.

Return JSON:
{{
  "valuation": {{ ... }},
  "comparables": [{{ ... }}, ...],
  "repairs": [{{ ... }}, ...],
  "inferred_source": "",
  "warnings": []
}}

Rules:
- Read ALL pages (use OCR if scanned)
- Extract fields listed below
- null for missing values
- Numbers without $ or commas
- Dates as YYYY-MM-DD
- lot_size_acres: convert square feet to acres (acres = sq_ft / 43560)
- bathrooms: use total count (e.g., 2.5 for 2 full + 1 half)
- Return only JSON (no markdown)

Fields:
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


class GeminiVisionExtractionService:
    """Uploads full documents to Gemini Vision and normalizes the JSON output.
    
    This service handles:
    - File compression for large documents
    - PDF chunking for documents exceeding size limits
    - Image compression for image files
    - Document vision processing via Gemini 2.5 Flash
    - Field extraction and normalization
    """

    prompt: str = PROMPT_TEMPLATE
    default_confidence: float = DEFAULT_CONFIDENCE

    def __init__(
        self,
        *,
        client=None,
        prompt: str = PROMPT_TEMPLATE,
        model_name: str = "gemini-2.5-flash",
        max_document_bytes: int = DEFAULT_MAX_DOCUMENT_BYTES,
        compression_threshold: int = COMPRESSION_THRESHOLD_BYTES,
    ) -> None:
        """Initialize the Gemini Vision Extraction Service.
        
        Args:
            client: Optional custom Gemini client (default: builds new client)
            prompt: The extraction prompt template
            model_name: Gemini model to use (default: gemini-2.5-flash)
            max_document_bytes: Maximum document size in bytes
            compression_threshold: Compress files larger than this threshold
        """
        self.client = client or build_valuation_gemini_vision_client(default_model=model_name)
        self.prompt = prompt
        self.model_name = model_name
        self.max_document_bytes = max_document_bytes
        self.compression_threshold = compression_threshold

    def process(self, file_path: Path) -> DocumentExtractionResult:
        """Process a document file and extract valuation data.
        
        Args:
            file_path: Path to the document file to process
        
        Returns:
            DocumentExtractionResult containing extracted fields and metadata
        
        Raises:
            FileNotFoundError: If the file doesn't exist
            RuntimeError: If the Gemini client is not configured
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        if self.client is None:
            raise RuntimeError("Gemini vision client is not configured")

        # Determine MIME type of the file
        mime_type = mimetypes.guess_type(str(file_path))[0] or "application/pdf"
        file_size = file_path.stat().st_size
        
        logger.info("Processing file: %s (size: %d bytes, type: %s)", file_path.name, file_size, mime_type)

        # Compress the file if it exceeds the compression threshold
        processed_file_path = file_path
        compressed = False
        if file_size > self.compression_threshold:
            logger.info("File exceeds compression threshold, attempting compression...")
            compressed_path = self._compress_file(file_path, mime_type)
            if compressed_path:
                processed_file_path = compressed_path
                compressed = True
                file_size = processed_file_path.stat().st_size
                logger.info("Compression successful. New size: %d bytes", file_size)

        responses: List[Dict[str, Any]] = []
        
        try:
            # Process the file based on size and type
            if file_size <= self.max_document_bytes:
                # File is small enough to process in one call
                responses.append(self._call_vision(file_bytes=processed_file_path.read_bytes(), mime_type=mime_type))
            elif mime_type == "application/pdf":
                # PDF is too large, split into chunks
                logger.info("PDF exceeds size limit, splitting into chunks...")
                responses = self._process_pdf_in_chunks(processed_file_path)
            else:
                # Non-PDF file is too large even after compression
                warning = (
                    f"File {file_path.name} exceeds Gemini vision size limit ({self.max_document_bytes} bytes) "
                    f"even after compression; please split or reduce quality before processing."
                )
                logger.warning(warning)
                return DocumentExtractionResult(
                    file_path=file_path,
                    mime_type=mime_type,
                    extracted_at=timezone.now(),
                    fields=[],
                    valuation_payload={},
                    comparables_payload=[],
                    repairs_payload=[],
                    raw_response={},
                    warnings=[warning],
                    inferred_source=None,
                )

            # Aggregate all responses into a single result
            aggregate_result = self._aggregate_responses(responses, file_path, mime_type)
            return aggregate_result
            
        finally:
            # Clean up compressed temporary file if created
            if compressed and processed_file_path != file_path:
                try:
                    processed_file_path.unlink()
                    logger.info("Cleaned up temporary compressed file: %s", processed_file_path)
                except Exception as cleanup_exc:
                    logger.warning("Failed to clean up temp file %s: %s", processed_file_path, cleanup_exc)

    def _call_vision(self, *, file_bytes: bytes, mime_type: str) -> Dict[str, Any]:
        """Call Gemini vision API to extract data from document bytes.
        
        Args:
            file_bytes: The document bytes to process
            mime_type: The MIME type of the document
        
        Returns:
            Dictionary containing extracted data
        
        Raises:
            ValueError: If Gemini returns an unexpected response format
        """
        logger.info("Sending %d bytes to Gemini vision model %s", len(file_bytes), self.model_name)
        response = self.client(file_bytes=file_bytes, mime_type=mime_type, prompt=self.prompt)
        if not isinstance(response, dict):
            raise ValueError("Gemini vision returned an unexpected response payload")
        return response
    
    def _compress_file(self, file_path: Path, mime_type: str) -> Optional[Path]:
        """Compress a file to reduce its size before processing.
        
        Args:
            file_path: Path to the file to compress
            mime_type: MIME type of the file
        
        Returns:
            Path to the compressed file, or None if compression failed
        """
        try:
            if mime_type == "application/pdf":
                return self._compress_pdf(file_path)
            elif mime_type.startswith("image/"):
                return self._compress_image(file_path, mime_type)
            else:
                logger.warning("No compression available for MIME type: %s", mime_type)
                return None
        except Exception as exc:
            logger.warning("Compression failed for %s: %s", file_path.name, exc)
            return None
    
    def _compress_pdf(self, file_path: Path) -> Optional[Path]:
        """Compress a PDF file by removing unnecessary elements.
        
        Args:
            file_path: Path to the PDF file
        
        Returns:
            Path to the compressed PDF, or None if compression failed
        """
        if PdfReader is None or PdfWriter is None:
            logger.warning("pypdf is not available for PDF compression")
            return None
        
        try:
            reader = PdfReader(str(file_path))
            writer = PdfWriter()
            
            # Copy all pages to writer (writer automatically compresses)
            for page in reader.pages:
                writer.add_page(page)
            
            # Compress images in the PDF
            for page in writer.pages:
                if hasattr(page, "compress_content_streams"):
                    page.compress_content_streams()
            
            # Write to a temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix=".pdf", prefix="compressed_")
            try:
                with open(temp_path, "wb") as output_file:
                    writer.write(output_file)
                
                # Close the file descriptor
                import os
                os.close(temp_fd)
                
                # Check if compression was successful
                original_size = file_path.stat().st_size
                compressed_size = Path(temp_path).stat().st_size
                
                if compressed_size < original_size:
                    logger.info(
                        "PDF compression reduced size from %d to %d bytes (%.1f%% reduction)",
                        original_size,
                        compressed_size,
                        100 * (1 - compressed_size / original_size)
                    )
                    return Path(temp_path)
                else:
                    # Compression didn't help, remove temp file
                    Path(temp_path).unlink()
                    logger.info("PDF compression did not reduce size")
                    return None
                    
            except Exception:
                # Clean up on error
                import os
                try:
                    os.close(temp_fd)
                except Exception:
                    pass
                if Path(temp_path).exists():
                    Path(temp_path).unlink()
                raise
                
        except Exception as exc:
            logger.warning("PDF compression failed: %s", exc)
            return None
    
    def _compress_image(self, file_path: Path, mime_type: str) -> Optional[Path]:
        """Compress an image file by reducing quality.
        
        Args:
            file_path: Path to the image file
            mime_type: MIME type of the image
        
        Returns:
            Path to the compressed image, or None if compression failed
        """
        if Image is None:
            logger.warning("PIL is not available for image compression")
            return None
        
        try:
            # Open the image
            img = Image.open(file_path)
            
            # Convert RGBA to RGB if necessary (for JPEG)
            if img.mode == "RGBA" and mime_type == "image/jpeg":
                # Create a white background
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = rgb_img
            
            # Determine output format and quality
            output_format = "JPEG" if mime_type == "image/jpeg" else "PNG"
            quality = 85 if output_format == "JPEG" else None
            
            # Create a temporary file
            temp_fd, temp_path = tempfile.mkstemp(
                suffix=".jpg" if output_format == "JPEG" else ".png",
                prefix="compressed_"
            )
            
            try:
                # Save the compressed image
                save_kwargs = {"format": output_format, "optimize": True}
                if quality:
                    save_kwargs["quality"] = quality
                
                img.save(temp_path, **save_kwargs)
                
                # Close the file descriptor
                import os
                os.close(temp_fd)
                
                # Check compression results
                original_size = file_path.stat().st_size
                compressed_size = Path(temp_path).stat().st_size
                
                if compressed_size < original_size:
                    logger.info(
                        "Image compression reduced size from %d to %d bytes (%.1f%% reduction)",
                        original_size,
                        compressed_size,
                        100 * (1 - compressed_size / original_size)
                    )
                    return Path(temp_path)
                else:
                    # Compression didn't help
                    Path(temp_path).unlink()
                    logger.info("Image compression did not reduce size")
                    return None
                    
            except Exception:
                # Clean up on error
                import os
                try:
                    os.close(temp_fd)
                except Exception:
                    pass
                if Path(temp_path).exists():
                    Path(temp_path).unlink()
                raise
                
        except Exception as exc:
            logger.warning("Image compression failed: %s", exc)
            return None

    def _process_pdf_in_chunks(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a large PDF by splitting it into chunks.
        
        Args:
            file_path: Path to the PDF file
        
        Returns:
            List of response dictionaries, one per chunk
        
        Raises:
            RuntimeError: If pypdf is not available
        """
        if PdfReader is None or PdfWriter is None:
            raise RuntimeError("pypdf is required to split large PDFs for Gemini vision processing")

        reader = PdfReader(str(file_path))
        total_pages = len(reader.pages)
        if total_pages == 0:
            return []

        responses: List[Dict[str, Any]] = []
        current_pages: List[Any] = []
        current_bytes: Optional[bytes] = None

        def flush_chunk(pages: Sequence[Any], chunk_bytes: Optional[bytes]) -> None:
            if not pages:
                return
            chunk = chunk_bytes if chunk_bytes is not None else self._write_pdf_pages(pages)
            responses.append(self._call_vision(file_bytes=chunk, mime_type="application/pdf"))

        for page_index, page in enumerate(reader.pages, start=1):
            tentative_pages = current_pages + [page]
            tentative_bytes = self._write_pdf_pages(tentative_pages)
            if len(tentative_bytes) <= self.max_document_bytes:
                current_pages = tentative_pages
                current_bytes = tentative_bytes
                continue

            if not current_pages:
                message = (
                    f"Single page from {file_path.name} exceeds Claude vision size limit "
                    f"({self.max_document_bytes} bytes)."
                )
                logger.error(message)
                raise ValueError(message)

            flush_chunk(current_pages, current_bytes)
            current_pages = [page]
            current_bytes = self._write_pdf_pages(current_pages)

        flush_chunk(current_pages, current_bytes)
        logger.info(
            "Split %s into %d chunk(s) (pages: %d) for Gemini vision.",
            file_path.name,
            len(responses),
            total_pages,
        )
        return responses

    @staticmethod
    def _write_pdf_pages(pages: Sequence[Any]) -> bytes:
        buffer = io.BytesIO()
        writer = PdfWriter()
        for page in pages:
            writer.add_page(page)
        writer.write(buffer)
        return buffer.getvalue()

    def _aggregate_responses(
        self,
        responses: Sequence[Dict[str, Any]],
        file_path: Path,
        mime_type: str,
    ) -> DocumentExtractionResult:
        combined_valuation: Dict[str, Any] = {}
        combined_comparables: List[Dict[str, Any]] = []
        combined_repairs: List[Dict[str, Any]] = []
        combined_fields: List[FieldExtractionRecord] = []
        combined_warnings: List[str] = []
        inferred_source: Optional[str] = None
        raw_chunks: List[Dict[str, Any]] = []

        for chunk_index, response in enumerate(responses, start=1):
            if not response:
                warning = f"Gemini vision chunk {chunk_index} returned an empty response."
                combined_warnings.append(warning)
                logger.warning(warning)
                continue

            (
                valuation_data,
                comparables_data,
                repairs_data,
                chunk_source,
                chunk_warnings,
                field_records,
            ) = self._normalise_response(response, chunk_index=chunk_index)

            self._merge_valuation_payload(combined_valuation, valuation_data)
            combined_comparables.extend(comparables_data)
            combined_repairs.extend(repairs_data)
            combined_fields.extend(field_records)
            raw_chunks.append(response)

            if chunk_source and not inferred_source:
                inferred_source = chunk_source
            combined_warnings.extend(chunk_warnings)

        return DocumentExtractionResult(
            file_path=file_path,
            mime_type=mime_type,
            extracted_at=timezone.now(),
            fields=combined_fields,
            valuation_payload=combined_valuation,
            comparables_payload=combined_comparables,
            repairs_payload=combined_repairs,
            raw_response={"chunks": raw_chunks},
            warnings=combined_warnings,
            inferred_source=inferred_source,
        )

    def _normalise_response(
        self,
        response: Dict[str, Any],
        *,
        chunk_index: int,
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]], Optional[str], List[str], List[FieldExtractionRecord]]:
        valuation_data = self._safe_dict(response.get("valuation"))
        comparables_data = self._safe_list_of_dicts(response.get("comparables"))
        repairs_data = self._safe_list_of_dicts(response.get("repairs"))
        inferred_source = response.get("inferred_source")
        warnings = response.get("warnings") or []
        if not isinstance(warnings, list):
            warnings = [str(warnings)]

        fields: List[FieldExtractionRecord] = []
        fields.extend(self._build_field_records("etl.ValuationETL", valuation_data, chunk_index=chunk_index))
        fields.extend(self._build_table_records("etl.ComparablesETL", comparables_data, chunk_index=chunk_index))
        fields.extend(self._build_table_records("etl.RepairItem", repairs_data, chunk_index=chunk_index))

        if inferred_source and not valuation_data.get("valuation_type"):
            valuation_record = FieldExtractionRecord(
                model_label="etl.ValuationETL",
                field="valuation_type",
                value=inferred_source,
                raw_text=inferred_source,
                confidence=DEFAULT_CONFIDENCE,
                method="ai",
                requires_review=False,
                metadata={"source": "vision_inferred", "chunk_index": chunk_index},
            )
            fields.append(valuation_record)

        return (
            valuation_data,
            comparables_data,
            repairs_data,
            inferred_source or valuation_data.get("valuation_type"),
            warnings,
            fields,
        )

    @staticmethod
    def _merge_valuation_payload(destination: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Merge valuation data from source into destination.
        
        Only overwrites destination values if they are empty or missing.
        
        Args:
            destination: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key not in destination or GeminiVisionExtractionService._is_empty_value(destination[key]):
                destination[key] = value

    @staticmethod
    def _is_empty_value(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False

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

    def _build_field_records(
        self,
        model_label: str,
        payload: Dict[str, Any],
        *,
        chunk_index: int,
    ) -> List[FieldExtractionRecord]:
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
                metadata={"source": "vision", "chunk_index": chunk_index},
            )
            records.append(record)
        return records

    def _build_table_records(
        self,
        model_label: str,
        rows: List[Dict[str, Any]],
        *,
        chunk_index: int,
    ) -> List[FieldExtractionRecord]:
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
                metadata={"source": "vision", "row_index": index, "chunk_index": chunk_index},
            )
            records.append(record)
        return records


__all__ = [
    "GeminiVisionExtractionService",
    "DocumentExtractionResult",
    "FieldExtractionRecord",
]

# Backward compatibility alias (deprecated)
ClaudeVisionExtractionService = GeminiVisionExtractionService
