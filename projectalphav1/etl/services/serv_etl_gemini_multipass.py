"""Multi-pass Gemini extraction to avoid 120-second server timeout.

Google's Gemini API has a hard 120-second server-side timeout that cannot be
overridden. For large extractions (150+ fields), we split into multiple passes.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
from django.utils import timezone

from etl.services.serv_etl_gemini_client import build_valuation_gemini_vision_client
from etl.services.serv_etl_valuation_vision_extractor import (
    DocumentExtractionResult,
    _build_schema_guide,
)

logger = logging.getLogger(__name__)


# Pass 1: Core property and valuation data (~50 fields, ~60 seconds)
PASS1_FIELDS = [
    "source", "valuation_type", "bpo_type",
    "property_address", "city", "state", "zip_code", "parcel_number",
    "loan_number", "deal_name",
    "inspection_date", "effective_date", "report_date",
    "occupancy_status", "property_appears_secure",
    "yearly_taxes", "estimated_monthly_rent", "estimated_monthly_rent_repaired",
    "living_area", "total_rooms", "bedrooms", "bathrooms",
    "year_built", "effective_age", "foundation_type", "basement_square_feet",
    "lot_size_acres", "property_type", "style", "number_of_units", "condition",
    "has_pool", "has_deck", "has_fireplace", "has_fencing",
    "garage", "garage_spaces", "parking_spaces", "parking_type",
    "cooling_type", "heating_type", "water_type", "sewer_type",
    "hoa_fees_monthly", "hoa_fees_annual", "subdivision", "school_district",
    "as_is_value", "as_repaired_value", "quick_sale_value", "quick_sale_value_repaired",
    "land_value", "estimated_marketing_time", "typical_marketing_time_days",
    "recommended_sales_strategy", "recommended_list_price", "recommended_list_price_repaired",
]

# Pass 2: Comparables (~60 fields per comp, ~80 seconds for 3-5 comps)
PASS2_PROMPT = """
Extract comparable properties from this valuation document.

Return JSON:
{
  "comparables": [
    {
      "comp_type": "",
      "comp_number": 1,
      "address": "",
      "city": "",
      "state": "",
      "zip_code": "",
      "proximity_miles": 0,
      "sale_price": 0,
      "sale_date": "",
      "original_list_price": 0,
      "original_list_date": "",
      "current_list_price": 0,
      "days_on_market": 0,
      "sales_type": "",
      "seller_concessions": 0,
      "financing_type": "",
      "living_area": 0,
      "bedrooms": 0,
      "bathrooms": 0,
      "year_built": 0,
      "basement_square_feet": 0,
      "lot_size_acres": 0,
      "property_type": "",
      "style": "",
      "condition": "",
      "has_pool": false,
      "has_deck": false,
      "has_fireplace": false,
      "garage": "",
      "parking_spaces": 0,
      "data_source": "",
      "data_source_id": "",
      "total_adjustments": 0,
      "adjusted_sale_price": 0,
      "general_comments": ""
    }
  ]
}

Rules:
- Extract ALL comparable properties (usually 3-6)
- lot_size_acres: convert from sq ft if needed (acres = sq_ft / 43560)
- bathrooms: total count (e.g., 2.5)
- null for missing values
- Return only JSON
"""

# Pass 3: Market analysis and comments (~40 fields, ~50 seconds)
PASS3_FIELDS = [
    "sold_in_last_12_months", "prior_sale_price", "prior_sale_date",
    "currently_listed", "listing_broker", "listing_agent_email", "listing_agent_firm",
    "initial_list_price", "initial_list_date", "current_list_price",
    "days_on_market", "listing_currently_pending", "pending_contract_date",
    "property_rights_appraised", "sales_comparison_approach", "cost_approach", "income_approach",
    "financeable", "market_trend", "neighborhood_trend", "economic_trend",
    "property_values_trend", "subject_appeal_compared_to_avg", "subject_value_compared_to_avg",
    "housing_supply", "crime_vandalism_risk", "reo_driven_market",
    "num_reo_ss_listings", "num_listings_in_area", "num_boarded_properties",
    "new_construction_in_area", "seasonal_market",
    "neighborhood_price_range_low", "neighborhood_price_range_high",
    "neighborhood_median_price", "neighborhood_average_sales_price",
    "marketability_concerns", "property_comments", "neighborhood_comments", "general_comments",
    "data_source", "data_source_id",
]

# Pass 4: Repairs (~8 fields, ~30 seconds)
PASS4_PROMPT = """
Extract repair items from this valuation document.

Return JSON:
{
  "repairs": [
    {
      "repair_type": "",
      "category": "",
      "description": "",
      "estimated_cost": 0,
      "repair_recommended": false
    }
  ],
  "estimated_repair_cost": 0,
  "general_repair_comments": ""
}

Rules:
- Extract ALL repair items listed
- Numbers without $ or commas
- null for missing values
- Return only JSON
"""


class MultiPassGeminiExtractor:
    """Multi-pass extractor to work within 120-second server timeout."""
    
    def __init__(self):
        """Initialize with Gemini client."""
        self.client = build_valuation_gemini_vision_client()
        if not self.client:
            raise RuntimeError("Gemini client not configured")
    
    def extract(self, file_path: Path) -> DocumentExtractionResult:
        """Extract using multiple passes to avoid timeout.
        
        COST-OPTIMIZED: Uploads file ONCE, makes 4 generation calls on same file.
        
        Args:
            file_path: Path to document
        
        Returns:
            DocumentExtractionResult with all data
        """
        import google.generativeai as genai
        import tempfile
        import os
        import time
        
        logger.info("Starting multi-pass extraction: %s", file_path.name)
        logger.info("This will upload ONCE and make 4 separate generation calls")
        
        # Upload file ONCE
        logger.info("Uploading file to Gemini...")
        upload_start = time.time()
        uploaded_file = genai.upload_file(path=str(file_path), mime_type="application/pdf")
        upload_time = time.time() - upload_start
        logger.info("File uploaded in %.1f seconds: %s", upload_time, uploaded_file.name)
        
        try:
            # Create model
            model = genai.GenerativeModel(model_name="gemini-2.5-flash")
            
            # Pass 1: Core valuation data
            logger.info("PASS 1/4: Core valuation data (~60 fields)...")
            pass1_prompt = self._build_field_prompt(PASS1_FIELDS, "valuation")
            start = time.time()
            response1 = model.generate_content([uploaded_file, pass1_prompt])
            logger.info("  Pass 1 complete in %.1f seconds", time.time() - start)
            pass1_result = self._parse_response(response1)
            valuation_data = pass1_result.get("valuation", {}) if pass1_result else {}
            
            # Pass 2: Comparables
            logger.info("PASS 2/4: Comparables (~35 fields × 5 comps)...")
            start = time.time()
            response2 = model.generate_content([uploaded_file, PASS2_PROMPT])
            logger.info("  Pass 2 complete in %.1f seconds", time.time() - start)
            pass2_result = self._parse_response(response2)
            comparables_data = pass2_result.get("comparables", []) if pass2_result else []
            
            # Pass 3: Market data and comments
            logger.info("PASS 3/4: Market data (~40 fields)...")
            pass3_prompt = self._build_field_prompt(PASS3_FIELDS, "valuation")
            start = time.time()
            response3 = model.generate_content([uploaded_file, pass3_prompt])
            logger.info("  Pass 3 complete in %.1f seconds", time.time() - start)
            pass3_result = self._parse_response(response3)
            market_data = pass3_result.get("valuation", {}) if pass3_result else {}
            
            # Pass 4: Repairs
            logger.info("PASS 4/4: Repairs (~5 fields × 20 repairs)...")
            start = time.time()
            response4 = model.generate_content([uploaded_file, PASS4_PROMPT])
            logger.info("  Pass 4 complete in %.1f seconds", time.time() - start)
            pass4_result = self._parse_response(response4)
            repairs_data = pass4_result.get("repairs", []) if pass4_result else []
            repair_cost = pass4_result.get("estimated_repair_cost") if pass4_result else None
            repair_comments = pass4_result.get("general_repair_comments", "") if pass4_result else ""
            
        finally:
            # Clean up uploaded file
            try:
                genai.delete_file(uploaded_file.name)
                logger.info("Cleaned up uploaded file: %s", uploaded_file.name)
            except Exception:
                pass
        
        # Merge valuation data
        valuation_payload = {**valuation_data, **market_data}
        if repair_cost:
            valuation_payload["estimated_repair_cost"] = repair_cost
        if repair_comments:
            valuation_payload["general_repair_comments"] = repair_comments
        
        logger.info("Multi-pass extraction complete!")
        logger.info("  Valuation fields: %d", len(valuation_payload))
        logger.info("  Comparables: %d", len(comparables_data))
        logger.info("  Repairs: %d", len(repairs_data))
        
        # Return in standard format
        return DocumentExtractionResult(
            file_path=file_path,
            mime_type="application/pdf",
            extracted_at=timezone.now(),
            fields=[],
            valuation_payload=valuation_payload,
            comparables_payload=comparables_data,
            repairs_payload=repairs_data,
            raw_response={"pass1": pass1_result, "pass2": pass2_result, "pass3": pass3_result, "pass4": pass4_result},
            warnings=[],
            inferred_source=valuation_data.get("valuation_type"),
        )
    
    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse Gemini response into JSON."""
        import json
        try:
            response_text = response.text.strip()
            
            # Remove markdown if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                if len(lines) > 2:
                    response_text = "\n".join(lines[1:-1])
            
            return json.loads(response_text)
        except Exception as e:
            logger.error("Failed to parse response: %s", e)
            return {}
    
    def _build_field_prompt(self, fields: List[str], section_name: str) -> str:
        """Build a prompt for specific fields."""
        field_list = "\n".join(f"  - {f}" for f in fields)
        
        return f"""
Extract property valuation data from this document.

Return JSON:
{{
  "{section_name}": {{
    ... fields below ...
  }}
}}

Rules:
- Extract fields listed below
- null for missing values
- Numbers without $ or commas
- Dates as YYYY-MM-DD
- lot_size_acres: convert from sq ft (acres = sq_ft / 43560)
- bathrooms: total count (e.g., 2.5)
- Return only JSON

Fields:
{field_list}
"""


def multipass_extract(file_path: str) -> DocumentExtractionResult:
    """Multi-pass extraction that works within 120-second timeout.
    
    Usage:
        result = multipass_extract("valuation.pdf")
        print(f"Extracted {len(result.valuation_payload)} valuation fields")
        print(f"Extracted {len(result.comparables_payload)} comparables")
        print(f"Extracted {len(result.repairs_payload)} repairs")
    """
    extractor = MultiPassGeminiExtractor()
    return extractor.extract(Path(file_path))


__all__ = [
    "MultiPassGeminiExtractor",
    "multipass_extract",
]

