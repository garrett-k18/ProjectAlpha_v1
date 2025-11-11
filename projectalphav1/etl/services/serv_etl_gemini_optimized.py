"""Optimized Gemini extraction with two-pass approach.

Fast pass extracts only critical fields (~10 seconds).
Full pass extracts all fields if needed (~60 seconds).
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

import google.generativeai as genai

from etl.services.serv_etl_gemini_client import build_valuation_gemini_vision_client
from etl.services.serv_etl_valuation_vision_extractor import (
    GeminiVisionExtractionService,
    DocumentExtractionResult,
)

logger = logging.getLogger(__name__)


# FAST PROMPT - Only 15 critical fields (~90% faster)
FAST_EXTRACTION_PROMPT = """
Read this property valuation document and extract these key fields.
Return as JSON:

{
  "property_address": "",
  "city": "",
  "state": "",
  "zip_code": "",
  "living_area": 0,
  "bedrooms": 0,
  "bathrooms": 0,
  "year_built": 0,
  "as_is_value": 0,
  "repaired_value": 0,
  "estimated_monthly_rent": 0,
  "inspection_date": "",
  "condition": "",
  "occupancy_status": "",
  "valuation_type": ""
}

Return only JSON. Use null for missing values. Dates as YYYY-MM-DD.
"""


# OPTIMIZED FULL PROMPT - Minimal, let Gemini infer types
def build_optimized_prompt(fields: list) -> str:
    """Build minimal prompt with just field names."""
    field_list = ", ".join(fields)
    
    return f"""
Extract property valuation data from this document.

Return JSON with these fields:
{field_list}

Rules:
- Use null for missing values
- Dates as YYYY-MM-DD
- Numbers without $ or commas
- Return only JSON

Include arrays for "comparables" and "repairs" if found.
"""


class OptimizedGeminiExtractor:
    """Optimized extractor with fast and full modes."""
    
    def __init__(self):
        """Initialize with Gemini client."""
        self.client = build_valuation_gemini_vision_client()
        if not self.client:
            raise RuntimeError("Gemini client not configured")
    
    def fast_extract(self, file_path: Path) -> Dict[str, Any]:
        """Extract only critical fields (~10 seconds).
        
        Use this for:
        - Quick previews
        - Validation before full extraction
        - Minimum viable data
        
        Args:
            file_path: Path to document
        
        Returns:
            Dict with ~15 key fields
        """
        logger.info(f"FAST extraction: {file_path.name}")
        
        file_bytes = file_path.read_bytes()
        mime_type = "application/pdf"
        
        result = self.client(
            file_bytes=file_bytes,
            mime_type=mime_type,
            prompt=FAST_EXTRACTION_PROMPT
        )
        
        return result.get("valuation", {}) if isinstance(result, dict) else {}
    
    def full_extract(self, file_path: Path, fields: Optional[list] = None) -> DocumentExtractionResult:
        """Extract all fields (~60 seconds).
        
        Use this for:
        - Complete data extraction
        - After fast_extract validation passes
        
        Args:
            file_path: Path to document
            fields: Optional list of specific fields (defaults to all)
        
        Returns:
            DocumentExtractionResult with all data
        """
        logger.info(f"FULL extraction: {file_path.name}")
        
        if fields:
            # Custom field list
            prompt = build_optimized_prompt(fields)
            service = GeminiVisionExtractionService(prompt=prompt)
        else:
            # Use default full extraction
            service = GeminiVisionExtractionService()
        
        return service.process(file_path)
    
    def smart_extract(self, file_path: Path) -> DocumentExtractionResult:
        """Smart extraction: fast first, then full if valid.
        
        Workflow:
        1. Fast extract key fields
        2. Validate (has address and value?)
        3. If valid, do full extraction
        4. If invalid, skip full extraction
        
        Args:
            file_path: Path to document
        
        Returns:
            DocumentExtractionResult
        """
        logger.info(f"SMART extraction: {file_path.name}")
        
        # Step 1: Fast extraction
        fast_result = self.fast_extract(file_path)
        
        # Step 2: Validate
        has_address = bool(fast_result.get("property_address"))
        has_value = bool(fast_result.get("as_is_value") or fast_result.get("repaired_value"))
        
        if not (has_address and has_value):
            logger.warning(f"Fast extraction failed validation: {file_path.name}")
            logger.warning(f"Address: {has_address}, Value: {has_value}")
            # Return empty result with warning
            from django.utils import timezone
            from etl.services.serv_etl_valuation_vision_extractor import DocumentExtractionResult
            return DocumentExtractionResult(
                file_path=file_path,
                mime_type="application/pdf",
                extracted_at=timezone.now(),
                fields=[],
                valuation_payload={},
                comparables_payload=[],
                repairs_payload=[],
                warnings=["Document does not appear to be a valid valuation report"],
            )
        
        # Step 3: Do full extraction
        logger.info("Fast extraction passed, proceeding with full extraction...")
        return self.full_extract(file_path)


# Convenience functions
def quick_extract(file_path: str) -> Dict[str, Any]:
    """Quick extraction of key fields only.
    
    Example:
        data = quick_extract("valuation.pdf")
        print(f"Property: {data['property_address']}")
        print(f"Value: ${data['as_is_value']}")
    """
    extractor = OptimizedGeminiExtractor()
    return extractor.fast_extract(Path(file_path))


def smart_extract(file_path: str) -> DocumentExtractionResult:
    """Smart extraction with validation.
    
    Example:
        result = smart_extract("valuation.pdf")
        if result.warnings:
            print("Not a valid valuation document")
        else:
            print(f"Extracted {len(result.fields)} fields")
    """
    extractor = OptimizedGeminiExtractor()
    return extractor.smart_extract(Path(file_path))


__all__ = [
    "OptimizedGeminiExtractor",
    "quick_extract",
    "smart_extract",
    "FAST_EXTRACTION_PROMPT",
]

