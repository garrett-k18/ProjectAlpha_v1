"""
AI Column Mapping Module

WHAT: Maps source Excel/CSV columns to SellerRawData model fields
WHY: Different sellers use different column names - need intelligent mapping
HOW: Uses Claude AI for semantic matching, with fallback to exact matching

USAGE:
    mapper = AIColumnMapper(df.columns)
    column_mapping = mapper.map()  # Returns dict: {'Source Col': 'model_field'}

    # Or load from config
    mapper = AIColumnMapper.from_config('mapping.json')
"""

import os
import json
import logging
from typing import Dict, List, Optional

import anthropic

from acq_module.models.seller import SellerRawData

logger = logging.getLogger(__name__)


class AIColumnMapper:
    """
    WHAT: Intelligent column mapping using AI or exact matching
    WHY: Handles variations in column naming across different seller tapes
    HOW: Primary: Claude AI semantic matching, Fallback: Exact name matching
    """

    def __init__(self, source_columns: List[str], stdout=None):
        """
        Initialize AI column mapper

        Args:
            source_columns: List of column names from source file
            stdout: Django stdout for progress messages (optional)
        """
        self.source_columns = source_columns
        self.stdout = stdout

    def map(self, use_ai: bool = True) -> Dict[str, str]:
        """
        WHAT: Map source columns to model fields
        WHY: Main entry point for column mapping
        HOW: Uses AI if enabled and available, otherwise exact matching

        Args:
            use_ai: Use AI mapping (default: True)

        Returns:
            Dict mapping source column names to model field names
        """
        if use_ai:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                try:
                    return self._ai_mapping()
                except Exception as e:
                    if self.stdout:
                        self.stdout.write(f'   [WARNING] AI mapping failed: {e}. Using exact matching.\n')
                    logger.warning(f'AI mapping failed: {e}')
            else:
                if self.stdout:
                    self.stdout.write('   [WARNING] ANTHROPIC_API_KEY not found. Using exact matching.\n')

        return self._exact_matching()

    def _ai_mapping(self) -> Dict[str, str]:
        """
        WHAT: Use Claude AI to intelligently map source columns to model fields
        WHY: Handles variations in column naming, synonyms, and abbreviations
        HOW: Sends column names + field definitions to Claude for semantic mapping

        DOCS: https://docs.anthropic.com/en/api/messages

        Returns:
            Dict mapping source columns to model fields
        """
        api_key = os.getenv('ANTHROPIC_API_KEY')

        # Build comprehensive field definitions for Claude
        field_definitions = self._get_field_definitions()

        # Create AI prompt for intelligent mapping
        prompt = f"""You are a data mapping expert. Map source Excel/CSV columns to database fields.

SOURCE COLUMNS (from Excel/CSV file):
{json.dumps(list(self.source_columns), indent=2)}

TARGET DATABASE FIELDS (SellerRawData model):
{json.dumps(field_definitions, indent=2)}

INSTRUCTIONS:
1. Map each source column to the most appropriate target field
2. Consider synonyms, abbreviations, and semantic meaning
3. If no good match exists, omit that source column
4. Return ONLY valid JSON in this exact format:
{{
  "source_column_name": "target_field_name",
  "another_source": "another_target"
}}

CRITICAL MAPPING RULES (ALWAYS FOLLOW):
- **sellertape_id** (REQUIRED): Map ANY unique loan identifier to this field
  Common names: "Loan Number", "Loan ID", "Loan #", "Account Number", "Asset ID", "ID", "Number"
  This is the PRIMARY identifier - always map the main loan ID column to sellertape_id

- **current_balance**: Unpaid Principal Balance (UPB), Current Balance, Principal Balance
- **original_balance**: Original Balance, Loan Amount, Original UPB, Orig Balance
- **property_type**: Property Type, Prop Type, Type (SFR, Condo, Townhouse, etc.)
- **product_type**: Product Type, Loan Type, Product (FRM, ARM, etc.)
- **street_address**: Property Address, Street Address, Address, Street
- **city**: City
- **state**: State, ST
- **zip**: Zip, Zip Code, Postal Code

EXAMPLES OF GOOD MAPPINGS:
- "Loan Number" -> "sellertape_id" (CRITICAL - unique identifier)
- "Loan ID" -> "sellertape_id" (CRITICAL - unique identifier)
- "Account Number" -> "sellertape_id" (CRITICAL - unique identifier)
- "ID" -> "sellertape_id" (if it's the main loan identifier)
- "Loan Balance" -> "current_balance"
- "UPB" -> "current_balance" (Unpaid Principal Balance)
- "Prop Type" -> "property_type"
- "Addr" -> "street_address"
- "Seller BPO" -> "seller_asis_value"

Return only the JSON mapping, no explanations."""

        client = anthropic.Anthropic(api_key=api_key)

        # Use Claude for intelligent mapping
        message = client.messages.create(
            model="claude-opus-4-20250514",  # Claude 4.0 Opus - best reasoning
            max_tokens=2000,
            temperature=0,  # Deterministic output for consistent mappings
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract text from response
        response_text = ""
        for block in message.content:
            if hasattr(block, 'text'):
                response_text += block.text
            elif isinstance(block, dict) and 'text' in block:
                response_text += block['text']

        # Parse JSON response
        response_text = response_text.strip()
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])  # Remove first and last line
        if response_text.startswith('json'):
            response_text = response_text[4:].strip()

        mapping = json.loads(response_text)

        # Validate that mapped fields actually exist in the model
        valid_fields = {f.name for f in SellerRawData._meta.get_fields()
                       if not f.auto_created and f.name not in ['asset_hub', 'seller', 'trade']}

        validated_mapping = {
            source: target for source, target in mapping.items()
            if target in valid_fields and source in self.source_columns
        }

        return validated_mapping

    def _exact_matching(self) -> Dict[str, str]:
        """
        WHAT: Create column mapping using exact field name matching
        WHY: Fast mapping when source columns already match model field names
        HOW: Matches source columns to SellerRawData field names (case-insensitive)

        Returns:
            Dict mapping source columns to model fields
        """
        # Get all field names from SellerRawData model
        model_fields = {f.name.lower(): f.name for f in SellerRawData._meta.get_fields()
                       if not f.auto_created and f.name not in ['asset_hub', 'seller', 'trade']}

        mapping = {}
        for col in self.source_columns:
            col_lower = col.lower().strip()
            if col_lower in model_fields:
                mapping[col] = model_fields[col_lower]

        return mapping

    def _get_field_definitions(self) -> Dict[str, Dict[str, str]]:
        """
        WHAT: Get comprehensive field definitions for AI mapping context
        WHY: Helps Claude understand the semantic meaning of each field
        HOW: Extracts field names, types, and help text from Django model

        Returns:
            Dict of field definitions: {field_name: {type, description}}
        """
        definitions = {}
        for field in SellerRawData._meta.get_fields():
            if field.auto_created or field.name in ['asset_hub', 'seller', 'trade']:
                continue

            field_type = field.get_internal_type()
            help_text = getattr(field, 'help_text', '')

            definitions[field.name] = {
                'type': field_type,
                'description': help_text or f'{field.name} ({field_type})'
            }

        return definitions

    @classmethod
    def from_config(cls, config_path: str, stdout=None):
        """
        WHAT: Load mapping from JSON config file
        WHY: Reuse saved mappings for consistent imports
        HOW: Reads JSON file with column_mapping dict

        Args:
            config_path: Path to JSON config file
            stdout: Django stdout for messages

        Returns:
            ConfiguredMapper instance with pre-loaded mapping
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        mapping = config.get('column_mapping', {})
        return ConfiguredMapper(mapping, stdout)

    def save_mapping(self, mapping: Dict[str, str], save_path: str):
        """
        WHAT: Save column mapping to JSON config file for future reuse
        WHY: Allows operators to save and share successful mappings
        HOW: Writes mapping dictionary to JSON file with metadata

        Args:
            mapping: Column mapping dict
            save_path: Path to save JSON file
        """
        from datetime import datetime

        config = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'description': 'Auto-generated column mapping for SellerRawData import',
            'column_mapping': mapping
        }

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        if self.stdout:
            self.stdout.write(f'   [OK] Saved mapping to: {save_path}\n')


class ConfiguredMapper:
    """
    WHAT: Pre-configured mapper with saved mapping
    WHY: Skip AI/exact matching when mapping is already known
    HOW: Stores mapping dict and returns it directly
    """

    def __init__(self, mapping: Dict[str, str], stdout=None):
        self.mapping = mapping
        self.stdout = stdout

    def map(self, **kwargs) -> Dict[str, str]:
        """Return pre-configured mapping"""
        return self.mapping
