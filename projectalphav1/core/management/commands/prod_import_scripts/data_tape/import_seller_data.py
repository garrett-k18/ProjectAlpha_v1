"""
Django management command for intelligent ETL of Excel/CSV files into SellerRawData model.

WHAT: This command imports seller data from Excel (.xlsx, .xls) or CSV files into the SellerRawData model.
WHY: Handles dynamic column mapping using Claude AI to intelligently match source columns to model fields.
WHERE: Run via `python manage.py import_seller_data --file path/to/file.xlsx`
HOW: Uses pandas for reading, Claude AI for intelligent column mapping, and Django ORM for saving.

DOCUMENTATION REVIEWED:
- Pandas read_csv: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
- Pandas read_excel: https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html  
- Anthropic Python SDK: https://docs.anthropic.com/en/api/messages
- Django Management Commands: https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/

USAGE:
    # Auto-create seller and trade (most common workflow)
    python manage.py import_seller_data --file data.xlsx --seller-name "ABC Capital" --auto-create
    
    # Use existing seller and trade IDs
    python manage.py import_seller_data --file data.xlsx --seller-id 1000 --trade-id 2000
    
    # Custom seller name when auto-creating
    python manage.py import_seller_data --file data.xlsx --seller-name "XYZ Lender" --trade-name "Q1 2025" --auto-create
    
    # Dry run to preview without saving
    python manage.py import_seller_data --file data.xlsx --seller-name "Test" --auto-create --dry-run
    
    # Use config file for predefined mappings
    python manage.py import_seller_data --file data.csv --config mapping_config.json --seller-id 1000 --trade-id 2000
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from decimal import Decimal, InvalidOperation
from datetime import datetime, date

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_date

# Pandas for reading Excel/CSV files
# Docs: https://pandas.pydata.org/docs/reference/io.html
import pandas as pd
import numpy as np

# Anthropic AI for intelligent column mapping
# Docs: https://docs.anthropic.com/en/api/messages
import anthropic

# Import our models - ALWAYS import at top level per user preference
# WHAT: Import models from their specific module files (not __init__.py)
# WHY: acq_module.models.__init__.py doesn't export models, so we import directly from files
# HOW: Use dot notation to access the specific model files within the models package
from acq_module.models.seller import SellerRawData, Seller, Trade
from core.models import AssetIdHub


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    WHAT: Django management command for ETL of seller data files.
    WHY: Provides flexible, intelligent data import with AI-powered column mapping.
    HOW: Reads Excel/CSV, maps columns using AI or config, validates, and saves to database.
    """
    
    help = 'Import seller data from Excel or CSV files with AI-powered column mapping'

    def add_arguments(self, parser):
        """
        WHAT: Define command-line arguments for the ETL command.
        WHY: Provides flexibility in how data is imported and processed.
        """
        # REQUIRED ARGUMENTS
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Path to Excel (.xlsx, .xls) or CSV file to import'
        )
        
        # SELLER/TRADE ARGUMENTS (mutually exclusive groups)
        parser.add_argument(
            '--seller-id',
            type=int,
            help='Seller ID (use existing seller)'
        )
        parser.add_argument(
            '--trade-id',
            type=int,
            help='Trade ID (use existing trade)'
        )
        parser.add_argument(
            '--seller-name',
            type=str,
            help='Seller name (for auto-creation or lookup)'
        )
        parser.add_argument(
            '--trade-name',
            type=str,
            help='Trade name (optional, auto-generated if not provided)'
        )
        parser.add_argument(
            '--auto-create',
            action='store_true',
            help='Auto-create seller and trade if they do not exist'
        )
        
        # OPTIONAL ARGUMENTS
        parser.add_argument(
            '--config',
            type=str,
            help='Path to JSON config file with predefined column mappings'
        )
        parser.add_argument(
            '--sheet',
            type=str,
            default=0,
            help='Excel sheet name or index (default: 0 = first sheet)'
        )
        parser.add_argument(
            '--skip-rows',
            type=int,
            default=0,
            help='Number of rows to skip at the beginning of file (default: 0)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview import without saving to database'
        )
        parser.add_argument(
            '--no-ai',
            action='store_true',
            help='Disable AI mapping, use exact column name matching only'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process per batch (default: 100)'
        )
        parser.add_argument(
            '--save-mapping',
            type=str,
            help='Save the generated column mapping to this JSON file path'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing records instead of skipping them (matches on sellertape_id)'
        )

    def handle(self, *args, **options):
        """
        WHAT: Main execution method for the ETL command.
        WHY: Orchestrates the entire ETL process from file reading to database insertion.
        HOW: Validates inputs, reads file, maps columns, validates data, and saves records.
        """
        # Extract options
        file_path = Path(options['file'])
        seller_id = options.get('seller_id')
        trade_id = options.get('trade_id')
        seller_name = options.get('seller_name')
        trade_name = options.get('trade_name')
        auto_create = options.get('auto_create', False)
        config_path = options.get('config')
        sheet = options.get('sheet', 0)
        skip_rows = options.get('skip_rows', 0)
        dry_run = options.get('dry_run', False)
        no_ai = options.get('no_ai', False)
        batch_size = options.get('batch_size', 100)
        save_mapping_path = options.get('save_mapping')
        update_existing = options.get('update_existing', False)

        # Validate file exists
        if not file_path.exists():
            raise CommandError(f'File not found: {file_path}')

        # Get or create Seller and Trade
        seller, trade = self._get_or_create_seller_trade(
            seller_id=seller_id,
            trade_id=trade_id,
            seller_name=seller_name,
            trade_name=trade_name,
            auto_create=auto_create,
            file_path=file_path
        )

        self.stdout.write(self.style.SUCCESS(f'\n=== Starting ETL Process ==='))
        self.stdout.write(f'   File: {file_path}')
        self.stdout.write(f'   Seller: {seller.name} (ID: {seller.id})')
        self.stdout.write(f'   Trade: {trade.trade_name} (ID: {trade.id})')
        self.stdout.write(f'   Mode: {"DRY RUN" if dry_run else "LIVE IMPORT"}\n')

        # STEP 1: Read the file using pandas
        self.stdout.write('Reading file...')
        df = self._read_file(file_path, sheet, skip_rows)
        self.stdout.write(self.style.SUCCESS(f'   [OK] Loaded {len(df)} rows, {len(df.columns)} columns\n'))

        # STEP 2: Get or generate column mapping
        self.stdout.write('Mapping columns...')
        if config_path:
            column_mapping = self._load_mapping_config(config_path)
            self.stdout.write(self.style.SUCCESS(f'   [OK] Loaded mapping from config: {config_path}\n'))
        elif no_ai:
            column_mapping = self._exact_column_mapping(df.columns)
            self.stdout.write(self.style.SUCCESS(f'   [OK] Using exact column name matching\n'))
        else:
            column_mapping = self._ai_column_mapping(df.columns)
            self.stdout.write(self.style.SUCCESS(f'   [OK] AI-generated column mapping\n'))

        # Display mapping
        self._display_mapping(column_mapping)

        # Optionally save mapping for future use
        if save_mapping_path:
            self._save_mapping_config(column_mapping, save_mapping_path)
            self.stdout.write(self.style.SUCCESS(f'   [OK] Saved mapping to: {save_mapping_path}\n'))

        # STEP 3: Transform and validate data
        self.stdout.write('Transforming and validating data...')
        records, errors = self._transform_data(df, column_mapping, seller, trade)
        
        self.stdout.write(self.style.SUCCESS(f'   [OK] Valid records: {len(records)}'))
        if errors:
            self.stdout.write(self.style.WARNING(f'   [WARNING] Errors: {len(errors)}'))
            for idx, error_msg in errors[:5]:  # Show first 5 errors
                self.stdout.write(self.style.ERROR(f'      Row {idx}: {error_msg}'))
            if len(errors) > 5:
                self.stdout.write(self.style.ERROR(f'      ... and {len(errors) - 5} more errors'))
        self.stdout.write('')

        # STEP 4: Save to database (or preview in dry-run mode)
        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN] Previewing first 5 records:\n'))
            for idx, record in enumerate(records[:5], 1):
                self.stdout.write(f'   Record {idx}:')
                self.stdout.write(f'      sellertape_id: {record.get("sellertape_id")}')
                self.stdout.write(f'      street_address: {record.get("street_address")}')
                self.stdout.write(f'      city: {record.get("city")}, state: {record.get("state")}')
                self.stdout.write(f'      current_balance: {record.get("current_balance")}')
                self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(f'[OK] DRY RUN COMPLETE - {len(records)} records ready to import\n'))
        else:
            self.stdout.write('Saving to database...')
            saved_count, updated_count, skipped_count = self._save_records(
                records, batch_size, update_existing
            )
            self.stdout.write(self.style.SUCCESS(f'   [OK] Created: {saved_count}'))
            if update_existing:
                self.stdout.write(self.style.SUCCESS(f'   [OK] Updated: {updated_count}'))
            self.stdout.write(self.style.SUCCESS(f'   [OK] Skipped: {skipped_count}'))
            self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] ETL COMPLETE - Processed {len(records)} records\n'))

    def _get_or_create_seller_trade(
        self,
        seller_id: Optional[int],
        trade_id: Optional[int],
        seller_name: Optional[str],
        trade_name: Optional[str],
        auto_create: bool,
        file_path: Path
    ) -> tuple[Seller, Trade]:
        """
        WHAT: Get existing or create new Seller and Trade records.
        WHY: Common workflow is to upload data before creating seller/trade records.
        HOW: Uses IDs if provided, otherwise creates based on name or intelligent defaults.
        """
        # SCENARIO 1: Both IDs provided - use existing records
        if seller_id and trade_id:
            try:
                seller = Seller.objects.get(pk=seller_id)
                trade = Trade.objects.get(pk=trade_id)
                self.stdout.write(self.style.SUCCESS(f'[OK] Using existing Seller (ID: {seller_id}) and Trade (ID: {trade_id})'))
                return seller, trade
            except Seller.DoesNotExist:
                raise CommandError(f'Seller with ID {seller_id} does not exist')
            except Trade.DoesNotExist:
                raise CommandError(f'Trade with ID {trade_id} does not exist')
        
        # SCENARIO 2: Auto-create mode
        if auto_create:
            # Determine seller name
            if seller_name:
                final_seller_name = seller_name
            else:
                # Generate from filename: "ABC_Tape_2025.xlsx" -> "ABC Tape 2025"
                final_seller_name = file_path.stem.replace('_', ' ').replace('-', ' ')
            
            # Get or create seller
            seller, seller_created = Seller.objects.get_or_create(
                name=final_seller_name,
                defaults={'email': '', 'poc': '', 'broker': ''}
            )
            
            if seller_created:
                self.stdout.write(self.style.SUCCESS(f'[OK] Created new Seller: {seller.name} (ID: {seller.id})'))
            else:
                self.stdout.write(self.style.SUCCESS(f'[OK] Using existing Seller: {seller.name} (ID: {seller.id})'))
            
            # Create trade (always create new trade for each import)
            trade = Trade.objects.create(seller=seller)
            # Trade name is auto-generated by model's save() method
            self.stdout.write(self.style.SUCCESS(f'[OK] Created new Trade: {trade.trade_name} (ID: {trade.id})'))
            
            return seller, trade
        
        # SCENARIO 3: Seller name provided without auto-create - lookup only
        if seller_name:
            try:
                seller = Seller.objects.get(name=seller_name)
                # Get most recent trade for this seller
                trade = seller.trades.latest('created_at')
                self.stdout.write(self.style.SUCCESS(
                    f'[OK] Found Seller: {seller.name} (ID: {seller.id}), using latest Trade: {trade.trade_name}'
                ))
                return seller, trade
            except Seller.DoesNotExist:
                raise CommandError(
                    f'Seller "{seller_name}" not found. Use --auto-create to create it automatically.'
                )
            except Trade.DoesNotExist:
                raise CommandError(
                    f'Seller "{seller_name}" has no trades. Use --auto-create to create a new trade.'
                )
        
        # SCENARIO 4: No seller/trade info provided at all
        raise CommandError(
            'Must provide either:\n'
            '  1. --seller-id and --trade-id (use existing records)\n'
            '  2. --seller-name --auto-create (auto-create new records)\n'
            '  3. --auto-create (auto-create with filename as seller name)'
        )

    def _read_file(self, file_path: Path, sheet: Any, skip_rows: int) -> pd.DataFrame:
        """
        WHAT: Read Excel or CSV file into a pandas DataFrame.
        WHY: Supports multiple file formats commonly used for data sharing.
        HOW: Uses pandas read_excel() or read_csv() based on file extension.
        
        DOCS REVIEWED: https://pandas.pydata.org/docs/reference/io.html
        """
        file_ext = file_path.suffix.lower()
        
        try:
            if file_ext in ['.xlsx', '.xls']:
                # Read Excel file using openpyxl engine (modern, supports .xlsx)
                # Docs: https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
                df = pd.read_excel(
                    file_path,
                    sheet_name=sheet,
                    skiprows=skip_rows,
                    engine='openpyxl' if file_ext == '.xlsx' else 'xlrd',
                    dtype=str,  # Read all as string initially for safer processing
                    na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None']
                )
            elif file_ext == '.csv':
                # Read CSV file
                # Docs: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
                df = pd.read_csv(
                    file_path,
                    skiprows=skip_rows,
                    dtype=str,  # Read all as string initially
                    na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None'],
                    encoding='utf-8-sig'  # Handle BOM in UTF-8 files
                )
            else:
                raise CommandError(f'Unsupported file format: {file_ext}. Use .xlsx, .xls, or .csv')
            
            # Clean column names: strip whitespace, replace special chars
            df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)
            
            return df
            
        except Exception as e:
            raise CommandError(f'Error reading file: {str(e)}')

    def _load_mapping_config(self, config_path: str) -> Dict[str, str]:
        """
        WHAT: Load predefined column mapping from JSON config file.
        WHY: Allows reusing mappings across multiple imports.
        HOW: Reads JSON file with source_column -> model_field mappings.
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('column_mapping', {})
        except Exception as e:
            raise CommandError(f'Error loading config file: {str(e)}')

    def _save_mapping_config(self, mapping: Dict[str, str], save_path: str):
        """
        WHAT: Save column mapping to JSON config file for future reuse.
        WHY: Allows operators to save and share successful mappings.
        HOW: Writes mapping dictionary to JSON file with metadata.
        """
        config = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'description': 'Auto-generated column mapping for SellerRawData import',
            'column_mapping': mapping
        }
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error saving mapping config: {str(e)}'))

    def _exact_column_mapping(self, source_columns: List[str]) -> Dict[str, str]:
        """
        WHAT: Create column mapping using exact field name matching.
        WHY: Fast mapping when source columns already match model field names.
        HOW: Matches source columns to SellerRawData field names (case-insensitive).
        """
        # Get all field names from SellerRawData model
        model_fields = {f.name.lower(): f.name for f in SellerRawData._meta.get_fields() 
                       if not f.auto_created and f.name not in ['asset_hub', 'seller', 'trade']}
        
        mapping = {}
        for col in source_columns:
            col_lower = col.lower().strip()
            if col_lower in model_fields:
                mapping[col] = model_fields[col_lower]
        
        return mapping

    def _ai_column_mapping(self, source_columns: List[str]) -> Dict[str, str]:
        """
        WHAT: Use Claude AI to intelligently map source columns to model fields.
        WHY: Handles variations in column naming, synonyms, and abbreviations.
        HOW: Sends column names + field definitions to Claude for semantic mapping.
        
        DOCS REVIEWED: https://docs.anthropic.com/en/api/messages
        """
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            self.stdout.write(self.style.WARNING(
                '⚠ ANTHROPIC_API_KEY not found. Falling back to exact matching.'
            ))
            return self._exact_column_mapping(source_columns)

        # Build comprehensive field definitions for Claude
        field_definitions = self._get_field_definitions()
        
        # Create AI prompt for intelligent mapping
        prompt = f"""You are a data mapping expert. Map source Excel/CSV columns to database fields.

SOURCE COLUMNS (from Excel/CSV file):
{json.dumps(list(source_columns), indent=2)}

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

        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            # Use Claude to generate intelligent mapping
            # Docs: https://docs.anthropic.com/en/api/messages
            # WHAT: Call Claude API for intelligent column mapping
            # WHY: Claude 4.0 (Opus) provides superior reasoning for complex mappings
            # HOW: Send prompt with columns and field definitions, get JSON mapping back
            message = client.messages.create(
                model="claude-opus-4-20250514",  # Claude 4.0 Opus - best reasoning and accuracy
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
            # Handle code blocks if Claude wrapped it in markdown
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
                if target in valid_fields and source in source_columns
            }
            
            return validated_mapping
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f'⚠ AI mapping failed: {str(e)}. Falling back to exact matching.'
            ))
            return self._exact_column_mapping(source_columns)

    def _get_field_definitions(self) -> Dict[str, str]:
        """
        WHAT: Get comprehensive field definitions for AI mapping context.
        WHY: Helps Claude understand the semantic meaning of each field.
        HOW: Extracts field names, types, and help text from Django model.
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

    def _display_mapping(self, mapping: Dict[str, str]):
        """
        WHAT: Display the column mapping to the console.
        WHY: Allows operator to verify mapping before import.
        """
        self.stdout.write('   Column Mapping:')
        for source, target in sorted(mapping.items()):
            self.stdout.write(f'      {source} -> {target}')
        self.stdout.write('')

    def _transform_data(
        self, 
        df: pd.DataFrame, 
        mapping: Dict[str, str],
        seller: Seller,
        trade: Trade
    ) -> tuple[List[Dict[str, Any]], List[tuple[int, str]]]:
        """
        WHAT: Transform and validate DataFrame rows into SellerRawData records.
        WHY: Ensures data types, formats, and business rules are correct before saving.
        HOW: Iterates rows, applies mapping, validates, and collects errors.
        """
        records = []
        errors = []
        
        for idx, row in df.iterrows():
            try:
                record = self._transform_row(row, mapping, seller, trade)
                if record:
                    records.append(record)
            except Exception as e:
                errors.append((idx + 1, str(e)))
        
        return records, errors

    def _transform_row(
        self,
        row: pd.Series,
        mapping: Dict[str, str],
        seller: Seller,
        trade: Trade
    ) -> Optional[Dict[str, Any]]:
        """
        WHAT: Transform a single DataFrame row into a SellerRawData record dict.
        WHY: Applies type conversions, validations, and default values.
        HOW: Maps columns, converts types, and validates required fields.
        """
        record = {
            'seller': seller,
            'trade': trade
        }
        
        # Apply column mapping and type conversion
        for source_col, target_field in mapping.items():
            value = row.get(source_col)
            
            # Skip null/empty values
            if pd.isna(value) or value == '':
                continue
            
            # Get field from model to determine type
            try:
                field = SellerRawData._meta.get_field(target_field)
            except Exception:
                continue  # Skip unmapped fields
            
            # Convert based on field type
            try:
                converted_value = self._convert_value(value, field)
                if converted_value is not None:
                    record[target_field] = converted_value
            except Exception as e:
                # Log conversion error but continue
                logger.warning(f'Conversion error for {target_field}: {e}')
        
        # Validate required field: sellertape_id
        if 'sellertape_id' not in record:
            raise ValueError('Missing required field: sellertape_id')
        
        return record

    def _convert_value(self, value: Any, field) -> Any:
        """
        WHAT: Convert a value to the appropriate type for a Django model field.
        WHY: Ensures type safety and format consistency.
        HOW: Checks field type and applies appropriate conversion logic.
        """
        field_type = field.get_internal_type()
        
        # Handle null/empty
        if pd.isna(value) or value == '':
            return None
        
        # Convert string to appropriate type
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
        
        # Decimal fields (currency, rates, etc.)
        if field_type == 'DecimalField':
            # WHAT: Handle decimal fields with special logic for interest rates
            # WHY: Different sellers format rates differently (5.5 vs 0.055 vs 5.5%)
            # HOW: Detect format and normalize to decimal (e.g., 5.5% -> 5.5)
            
            # Remove common currency formatting: $, commas, %
            if isinstance(value, str):
                value = value.replace('$', '').replace(',', '').replace('%', '').strip()
            
            try:
                decimal_value = Decimal(str(value))
                
                # SMART LOGIC: Detect if interest/default rate needs scaling
                # WHAT: Normalize interest_rate and default_rate fields
                # WHY: Some tapes show "5.5" (percent), others show "0.055" (decimal)
                # HOW: If value > 1, assume it's already a percent. If < 1, scale up by 100
                field_name = field.name if hasattr(field, 'name') else ''
                if field_name in ['interest_rate', 'default_rate', 'original_rate', 'mod_rate']:
                    # If value is between 0 and 1, it's likely decimal format (0.055) -> scale to percent (5.5)
                    if 0 < decimal_value < 1:
                        decimal_value = decimal_value * 100
                    # If value is > 100, it's likely already scaled wrong (550) -> scale down (5.5)
                    elif decimal_value > 100:
                        decimal_value = decimal_value / 100
                    # Otherwise (1-100 range), assume it's correct percent format
                
                return decimal_value
            except (InvalidOperation, ValueError):
                return None
        
        # Integer fields
        elif field_type == 'IntegerField':
            try:
                return int(float(str(value)))  # Handle "123.0" strings
            except (ValueError, TypeError):
                return None
        
        # Boolean fields
        elif field_type == 'BooleanField':
            if isinstance(value, str):
                value_lower = value.lower()
                if value_lower in ['true', 't', 'yes', 'y', '1']:
                    return True
                elif value_lower in ['false', 'f', 'no', 'n', '0']:
                    return False
            return bool(value)
        
        # Date fields
        elif field_type == 'DateField':
            if isinstance(value, date):
                return value
            if isinstance(value, datetime):
                return value.date()
            if isinstance(value, str):
                parsed = parse_date(value)
                if parsed:
                    return parsed
                # Try pandas date parsing for more flexibility
                try:
                    return pd.to_datetime(value).date()
                except Exception:
                    return None
            return None
        
        # Char fields - just return as string
        elif field_type in ['CharField', 'TextField', 'EmailField']:
            return str(value)[:field.max_length] if hasattr(field, 'max_length') else str(value)
        
        # Default: return as-is
        return value

    def _save_records(
        self,
        records: List[Dict[str, Any]],
        batch_size: int,
        update_existing: bool
    ) -> tuple[int, int, int]:
        """
        WHAT: Save validated records to the database in batches.
        WHY: Efficient bulk insertion with transaction safety.
        HOW: Creates AssetIdHub first (1:1 requirement), then creates/updates SellerRawData records.
        
        CRITICAL: SellerRawData uses asset_hub as primary key (OneToOneField with primary_key=True).
        Per MEMORY[92a5018c-e744-47f1-af32-9bfc96affaa8]: Must create hub first, then attach exactly one record.
        """
        saved_count = 0
        updated_count = 0
        skipped_count = 0
        hub_created_count = 0
        
        # Process in batches for better performance
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(records) + batch_size - 1) // batch_size
            
            self.stdout.write(f'   Processing batch {batch_num}/{total_batches} ({len(batch)} records)...')
            
            # CRITICAL FIX: Process each record individually with its own transaction
            # WHY: If we create AssetIdHub inside a batch transaction and SellerRawData fails,
            #      the entire transaction rolls back, deleting the hub but keeping the reference
            for record_data in batch:
                sellertape_id = record_data.get('sellertape_id')
                
                try:
                    # Check if record already exists based on sellertape_id
                    existing = SellerRawData.objects.filter(
                        seller=record_data['seller'],
                        trade=record_data['trade'],
                        sellertape_id=sellertape_id
                    ).first()
                    
                    if existing:
                        if update_existing:
                            # Update existing record (asset_hub already exists)
                            with transaction.atomic():
                                for field, value in record_data.items():
                                    if field not in ['asset_hub', 'seller', 'trade']:
                                        setattr(existing, field, value)
                                existing.save()
                            updated_count += 1
                        else:
                            # Skip existing record
                            skipped_count += 1
                    else:
                        # STEP 1: Create AssetIdHub OUTSIDE transaction (must persist even if insert fails)
                        # WHAT: Master asset identifier used across all asset-related tables
                        # WHY: SellerRawData.asset_hub is primary_key=True (1:1 with hub)
                        # HOW: Create hub first, then insert SellerRawData in separate transaction
                        asset_hub = AssetIdHub.objects.create()
                        hub_created_count += 1
                        
                        # STEP 2: Create SellerRawData record with asset_hub as PK (in transaction)
                        try:
                            with transaction.atomic():
                                record_data['asset_hub'] = asset_hub
                                SellerRawData.objects.create(**record_data)
                            saved_count += 1
                        except Exception as insert_error:
                            # If insert fails, hub is orphaned but that's better than FK constraint error
                            logger.error(f'Error inserting SellerRawData for {sellertape_id}: {insert_error}')
                            self.stdout.write(self.style.ERROR(f'      Failed: {sellertape_id} - {str(insert_error)[:100]}'))
                            skipped_count += 1
                        
                except Exception as e:
                    logger.error(f'Error processing record {sellertape_id}: {e}')
                    self.stdout.write(self.style.ERROR(f'      Failed: {sellertape_id} - {str(e)[:100]}'))
                    skipped_count += 1
        
        # Log AssetIdHub creation summary
        if hub_created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'   [OK] Created {hub_created_count} AssetIdHub records (1:1 with SellerRawData)'))
        
        return saved_count, updated_count, skipped_count
