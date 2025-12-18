"""
Data Import Module

WHAT: Transforms and imports data into SellerRawData model
WHY: Handles seller/trade management, data transformation, and database operations
HOW: Validates data, creates sellers/trades, and bulk inserts records

USAGE:
    importer = DataImporter(seller_id=1000, trade_id=2000)
    records_imported = importer.import_data(df, column_mapping)
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, InvalidOperation
from datetime import datetime, date

import pandas as pd
import numpy as np
from django.db import transaction
from django.utils.dateparse import parse_date

from acq_module.models.model_acq_seller import SellerRawData, Seller, Trade
from core.models import AssetIdHub, AssetDetails, LlDataEnrichment
from core.services.serv_co_geocoding import batch_geocode_row_ids
from etl.services.services_sellerTapeImport.serv_etl_ai_seller_matcher import AISellerMatcher
from etl.services.services_sellerTapeImport.serv_etl_ai_mapper import validate_choice_value

logger = logging.getLogger(__name__)


class DataImporter:
    """
    WHAT: Handles data transformation and database import
    WHY: Centralizes all database operations and seller/trade management
    HOW: Transforms DataFrame rows into model instances and bulk saves
    """

    def __init__(
        self,
        seller_id: Optional[int] = None,
        trade_id: Optional[int] = None,
        seller_name: Optional[str] = None,
        trade_name: Optional[str] = None,
        auto_create: bool = False,
        update_existing: bool = False,
        use_ai_seller_matching: bool = True,
        email_data: Optional[Dict[str, Any]] = None,
        stdout=None
    ):
        """
        Initialize data importer

        Args:
            seller_id: Existing seller ID (optional)
            trade_id: Existing trade ID (optional)
            seller_name: Seller name for lookup/creation (optional)
            trade_name: Trade name (optional)
            auto_create: Auto-create seller/trade if not found
            update_existing: Update existing records instead of skipping
            use_ai_seller_matching: Use AI to extract and match seller names (default: True)
            email_data: Email metadata for AI seller extraction (optional)
            stdout: Django stdout for progress messages
        """
        self.seller_id = seller_id
        self.trade_id = trade_id
        self.seller_name = seller_name
        self.trade_name = trade_name
        self.auto_create = auto_create
        self.update_existing = update_existing
        self.use_ai_seller_matching = use_ai_seller_matching
        self.email_data = email_data
        self.stdout = stdout

        # Caches for per-row lookups
        self._seller_cache = {}
        self._trade_cache = {}
        self._new_row_ids: List[int] = []
        
        # Initialize AI seller matcher if enabled
        self._ai_matcher = AISellerMatcher(stdout=stdout) if use_ai_seller_matching else None

    def import_data(
        self,
        df: pd.DataFrame,
        column_mapping: Dict[str, str],
        seller: Optional[Seller] = None,
        trade: Optional[Trade] = None,
        batch_size: int = 100,
        file_path: Optional[Path] = None,
        save_mapping: bool = True,
        mapping_name: Optional[str] = None,
        mapping_method: str = 'AI'
    ) -> int:
        """
        WHAT: Main entry point for data import
        WHY: Orchestrates seller/trade resolution, transformation, and saving
        HOW: Gets seller/trade, transforms data, saves to database

        Args:
            df: DataFrame with source data
            column_mapping: Dict mapping source columns to model fields
            seller: Pre-resolved seller (optional)
            trade: Pre-resolved trade (optional)
            batch_size: Records per batch (default: 100)
            file_path: Source file path for seller name generation (optional)
            save_mapping: Whether to save mapping for future use (default: True)
            mapping_name: Name for saved mapping (optional, auto-generated if not provided)
            mapping_method: How mapping was created (AI, MANUAL, EXACT, HYBRID)

        Returns:
            Number of records imported (created + updated)
        """
        # Get or create seller and trade
        if not seller or not trade:
            logger.info('Getting or creating seller and trade...')
            seller, trade = self.get_or_create_seller_trade(file_path)
            logger.info(f'Seller: {seller.name} (ID: {seller.id}), Trade: {trade.trade_name} (ID: {trade.id})')

        # Detect per-row seller/trade columns
        logger.info('Detecting per-row columns...')
        self._detect_per_row_columns(df)

        # Transform and validate data
        logger.info(f'Transforming {len(df)} rows...')
        records, errors = self._transform_data(df, column_mapping, seller, trade)
        logger.info(f'Transformation complete: {len(records)} valid records, {len(errors)} errors')

        if self.stdout:
            self.stdout.write(f'      [OK] Valid records: {len(records)}\n')
            if errors:
                self.stdout.write(f'      [WARNING] Errors: {len(errors)}\n')

        # Save to database
        saved_count, updated_count, skipped_count = self._save_records(records, batch_size)

        # Batch geocode newly created rows using Geocodio official client
        geocode_stats = self._run_batch_geocode_for_new_rows()

        if self.stdout:
            self.stdout.write(
                f'      [OK] Created: {saved_count}, Updated: {updated_count}, Skipped: {skipped_count}\n'
            )
            if geocode_stats:
                self.stdout.write(
                    f"      [GEOCODE] Batch updated {geocode_stats.get('updated_rows', 0)} rows "
                    f"across {geocode_stats.get('api_calls', 0)} call(s)\n"
                )

        # WHAT: Save mapping for future reuse if requested
        # WHY: Users can review and reuse successful mappings
        # HOW: Create ImportMapping record with column mapping and stats
        if save_mapping and seller:
            self._save_import_mapping(
                seller=seller,
                trade=trade,
                column_mapping=column_mapping,
                source_columns=list(df.columns),
                file_path=file_path,
                mapping_name=mapping_name,
                mapping_method=mapping_method,
                import_stats={
                    'records_imported': saved_count + updated_count,
                    'records_created': saved_count,
                    'records_updated': updated_count,
                    'records_skipped': skipped_count,
                    'total_rows': len(df),
                    'errors': len(errors),
                }
            )

        return saved_count + updated_count

    def get_or_create_seller_trade(self, file_path: Optional[Path] = None) -> Tuple[Seller, Trade]:
        """
        WHAT: Get existing or create new Seller and Trade records
        WHY: Simplified flow - always get/create seller, always create NEW trade
        HOW: Seller is reused if exists, Trade is ALWAYS newly created (never overwrites)

        Args:
            file_path: File path for auto-generating seller name (optional)

        Returns:
            Tuple of (Seller, Trade)
        
        LOGIC:
        1. Seller: Get existing or create new (by name)
        2. Trade: ALWAYS create new (with manual name or auto-generated name)
        3. NEVER overwrite existing trade data
        """
        # SCENARIO 1: Both IDs provided - use existing records
        if self.seller_id and self.trade_id:
            try:
                seller = Seller.objects.get(pk=self.seller_id)
                trade = Trade.objects.get(pk=self.trade_id)
                if self.stdout:
                    self.stdout.write(
                        f'[OK] Using existing Seller (ID: {self.seller_id}) and Trade (ID: {self.trade_id})\n'
                    )
                return seller, trade
            except Seller.DoesNotExist:
                raise ValueError(f'Seller with ID {self.seller_id} does not exist')
            except Trade.DoesNotExist:
                raise ValueError(f'Trade with ID {self.trade_id} does not exist')

        # SCENARIO 2: Get or create seller (simplified - no auto_create flag needed)
        if True:  # Always execute this path unless IDs provided
            # Use AI seller matching if enabled
            if self._ai_matcher:
                if self.stdout:
                    self.stdout.write('[AI-SELLER] Using AI seller matching for auto-creation\n')
                
                # AI matcher handles extraction, matching, and creation
                seller = self._ai_matcher.match_or_create_seller(
                    email_data=self.email_data,
                    file_path=file_path,
                    seller_name_hint=self.seller_name
                )
            else:
                # Fallback to original logic when AI is disabled
                # Determine seller name
                if self.seller_name:
                    final_seller_name = self.seller_name
                elif file_path:
                    # Generate from filename: "ABC_Tape_2025.xlsx" -> "ABC Tape 2025"
                    final_seller_name = file_path.stem.replace('_', ' ').replace('-', ' ')
                else:
                    raise ValueError('Cannot auto-create seller: no seller_name or file_path provided')

                # Get or create seller
                seller, seller_created = Seller.objects.get_or_create(
                    name=final_seller_name,
                    defaults={'email': '', 'poc': '', 'broker': ''}
                )

                if self.stdout:
                    if seller_created:
                        self.stdout.write(f'[OK] Created new Seller: {seller.name} (ID: {seller.id})\n')
                    else:
                        self.stdout.write(f'[OK] Using existing Seller: {seller.name} (ID: {seller.id})\n')

            # TRADE CREATION: ALWAYS create NEW trade (NEVER overwrite existing)
            # Determine trade name
            if self.trade_name:
                # User provided manual trade name - use it exactly
                base_trade_name = self.trade_name
                if self.stdout:
                    self.stdout.write(f'[TRADE] Using manual trade name: {base_trade_name}\n')
            else:
                # Auto-generate trade name with timestamp
                from datetime import datetime
                seller_clean = re.sub(r'[^A-Za-z0-9\s]', '', seller.name).replace(' ', '')
                date_str = datetime.now().strftime('%m.%d.%y')
                base_trade_name = f"{seller_clean} - {date_str}"
                if self.stdout:
                    self.stdout.write(f'[TRADE] Auto-generated trade name: {base_trade_name}\n')
            
            # Check if trade name exists and add suffix if needed
            final_trade_name = base_trade_name
            suffix = 2
            while Trade.objects.filter(seller=seller, trade_name=final_trade_name).exists():
                final_trade_name = f"{base_trade_name} -{suffix}"
                suffix += 1
                if self.stdout:
                    self.stdout.write(f'[TRADE] Trade name exists, trying: {final_trade_name}\n')
            
            # ALWAYS create NEW trade (never get existing)
            trade = Trade.objects.create(
                seller=seller,
                trade_name=final_trade_name
            )
            if self.stdout:
                self.stdout.write(f'[OK] Created NEW Trade: {trade.trade_name} (ID: {trade.id})\n')
            
            # WHAT: Auto-create TradeLevelAssumption for new trade
            # WHY: Required for timeline calculations and financial modeling
            # HOW: Create with modeling defaults so UI-controlled settings are applied
            from acq_module.models.model_acq_assumptions import TradeLevelAssumption, ModelingDefaults
            defaults = ModelingDefaults.current_trade_defaults()
            trade_assumption, created = TradeLevelAssumption.objects.get_or_create(
                trade=trade,
                defaults=defaults,
            )
            if created and self.stdout:
                self.stdout.write(f'[OK] Created TradeLevelAssumption for Trade ID: {trade.id}\n')

            return seller, trade

        # Should never reach here
        raise ValueError('Invalid seller/trade configuration')

    def _detect_per_row_columns(self, df: pd.DataFrame):
        """
        WHAT: Detect if DataFrame has per-row seller/trade columns
        WHY: Some files have seller_id/trade_id columns for multi-seller imports
        HOW: Case-insensitive check for specific column names

        Args:
            df: DataFrame to check
        """
        lower_cols = {c.lower().strip(): c for c in df.columns}
        self._col_seller_id = lower_cols.get('seller_id')
        self._col_trade_id = lower_cols.get('trade_id')
        self._col_seller_name = lower_cols.get('seller_name')
        self._col_trade_name = lower_cols.get('trade_name')
        self._per_row_fk = any([
            self._col_seller_id, self._col_trade_id,
            self._col_seller_name, self._col_trade_name
        ])

    def _transform_data(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
        seller: Seller,
        trade: Trade
    ) -> Tuple[List[Dict[str, Any]], List[Tuple[int, str]]]:
        """
        WHAT: Transform and validate DataFrame rows into SellerRawData records
        WHY: Ensures data types, formats, and business rules are correct before saving
        HOW: Iterates rows, applies mapping, validates, and collects errors

        Args:
            df: Source DataFrame
            mapping: Column mapping dict
            seller: Default seller
            trade: Default trade

        Returns:
            Tuple of (valid_records, errors)
        """
        records = []
        errors = []
        
        # Log first error in detail for debugging
        first_error_logged = False

        for idx, row in df.iterrows():
            try:
                record = self._transform_row(row, mapping, seller, trade)
                if record:
                    records.append(record)
            except Exception as e:
                errors.append((idx + 1, str(e)))
                if not first_error_logged:
                    logger.error(f'First row error (row {idx + 1}): {e}')
                    logger.error(f'Mapping used: {mapping}')
                    logger.error(f'Row data sample: {dict(row.head(10))}')
                    first_error_logged = True

        return records, errors

    def _transform_row(
        self,
        row: pd.Series,
        mapping: Dict[str, str],
        seller: Seller,
        trade: Trade
    ) -> Optional[Dict[str, Any]]:
        """
        WHAT: Transform a single DataFrame row into a SellerRawData record dict
        WHY: Applies type conversions, validations, and default values
        HOW: Maps columns, converts types, and validates required fields

        Args:
            row: DataFrame row
            mapping: Column mapping
            seller: Default seller
            trade: Default trade

        Returns:
            Record dict or None if invalid
        """
        # Resolve per-row Seller/Trade if provided
        if getattr(self, '_per_row_fk', False):
            resolved_seller, resolved_trade = self._resolve_seller_trade_from_row(row, seller, trade)
        else:
            resolved_seller, resolved_trade = seller, trade

        record = {
            'seller': resolved_seller,
            'trade': resolved_trade
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
                logger.warning(f'Conversion error for {target_field}: {e}')

        # Auto-generate sellertape_id if missing
        if 'sellertape_id' not in record or not record['sellertape_id']:
            # Generate unique ID: SELLER_{seller_id}_ROW_{row_index}
            import uuid
            record['sellertape_id'] = f"AUTO_{uuid.uuid4().hex[:12].upper()}"
            logger.info(f"Auto-generated sellertape_id: {record['sellertape_id']}")

        return record

    def _resolve_seller_trade_from_row(
        self,
        row: pd.Series,
        default_seller: Seller,
        default_trade: Trade
    ) -> Tuple[Seller, Trade]:
        """Resolve Seller/Trade from row columns (seller_id, trade_id, etc.)"""
        def _to_int(val):
            try:
                if pd.isna(val) or val == '':
                    return None
                return int(str(val).replace(',', '').strip())
            except Exception:
                return None

        seller = default_seller
        trade = default_trade

        # Resolve seller by id or name
        if getattr(self, '_col_seller_id', None) and self._col_seller_id in row:
            sid = _to_int(row[self._col_seller_id])
            if sid:
                seller = self._seller_cache.get(sid) or Seller.objects.filter(pk=sid).first() or seller
                if seller and seller.id == sid:
                    self._seller_cache[sid] = seller
        elif getattr(self, '_col_seller_name', None) and self._col_seller_name in row:
            sname = str(row[self._col_seller_name]).strip() if not pd.isna(row[self._col_seller_name]) else ''
            if sname:
                cache_key = f"name::{sname}"
                seller = self._seller_cache.get(cache_key) or Seller.objects.filter(name=sname).first() or seller
                if seller and seller.name == sname:
                    self._seller_cache[cache_key] = seller

        # Resolve trade by id or name
        if getattr(self, '_col_trade_id', None) and self._col_trade_id in row:
            tid = _to_int(row[self._col_trade_id])
            if tid:
                t_cached = self._trade_cache.get(tid)
                if t_cached is None:
                    t_cached = Trade.objects.filter(pk=tid).select_related('seller').first()
                    if t_cached:
                        self._trade_cache[tid] = t_cached
                if t_cached:
                    if seller and t_cached.seller_id != seller.id:
                        seller = t_cached.seller
                    trade = t_cached
        elif getattr(self, '_col_trade_name', None) and self._col_trade_name in row:
            tname = str(row[self._col_trade_name]).strip() if not pd.isna(row[self._col_trade_name]) else ''
            if tname:
                cache_key = f"t::{seller.id if seller else 0}::{tname}"
                t_cached = self._trade_cache.get(cache_key)
                if t_cached is None and seller:
                    t_cached = Trade.objects.filter(seller=seller, trade_name=tname).first()
                    if t_cached:
                        self._trade_cache[cache_key] = t_cached
                if t_cached:
                    trade = t_cached

        # Final sanity: align seller to trade
        if trade and seller and trade.seller_id != seller.id:
            seller = trade.seller

        return seller or default_seller, trade or default_trade

    def _clean_choice_field(self, value: Any, field_name: str) -> Optional[str]:
        """
        WHAT: Clean and validate choice field values using AI
        WHY: Prevent database constraint violations from invalid ETL data
        HOW: Delegates to AI-powered validation in ai_mapper module
        
        Args:
            value: Raw value from Excel/CSV
            field_name: Name of the model field
            
        Returns:
            Valid choice value or None
        """
        if pd.isna(value) or value == '' or value == '-':
            return None
        
        # Use AI validation from ai_mapper module (respects --no-ai flag)
        return validate_choice_value(field_name, str(value), use_ai=self.use_ai_seller_matching)

    def _convert_value(self, value: Any, field) -> Any:
        """Convert value to appropriate type for Django model field"""
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
            if isinstance(value, str):
                value = value.replace('$', '').replace(',', '').replace('%', '').strip()

            try:
                decimal_value = Decimal(str(value))

                # Normalize rate fields to decimal format (database expects 0.045 for 4.5%)
                field_name = field.name if hasattr(field, 'name') else ''
                if field_name in ['interest_rate', 'default_rate', 'original_rate', 'mod_rate']:
                    # If value looks like a percentage (>1), convert to decimal
                    if decimal_value > 1:
                        decimal_value = decimal_value / 100
                    # Values between 0-1 are already in decimal format, keep as-is

                return decimal_value
            except (InvalidOperation, ValueError):
                return None

        # Integer fields
        elif field_type == 'IntegerField':
            try:
                return int(float(str(value)))
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
                try:
                    return pd.to_datetime(value).date()
                except Exception:
                    return None
            return None

        # Char fields - apply choice validation for fields with choices
        elif field_type in ['CharField', 'TextField', 'EmailField']:
            field_name = field.name if hasattr(field, 'name') else ''
            
            # Apply choice field cleaning for known choice fields
            if field_name in ['property_type', 'product_type', 'occupancy', 'asset_status']:
                cleaned_value = self._clean_choice_field(value, field_name)
                if cleaned_value is None:
                    return None
                value = cleaned_value
            
            return str(value)[:field.max_length] if hasattr(field, 'max_length') else str(value)

        # Default
        return value

    def _save_records(
        self,
        records: List[Dict[str, Any]],
        batch_size: int
    ) -> Tuple[int, int, int]:
        """
        WHAT: Save validated records to database in batches
        WHY: Efficient bulk insertion with transaction safety
        HOW: Creates AssetIdHub first (1:1 requirement), then creates/updates SellerRawData

        Returns:
            Tuple of (saved_count, updated_count, skipped_count)
        """
        saved_count = 0
        updated_count = 0
        skipped_count = 0

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]

            for record_data in batch:
                sellertape_id = record_data.get('sellertape_id')

                try:
                    # Check if record exists
                    existing = SellerRawData.objects.filter(
                        seller=record_data['seller'],
                        trade=record_data['trade'],
                        sellertape_id=sellertape_id
                    ).first()

                    if existing:
                        if self.update_existing:
                            # Update existing record
                            with transaction.atomic():
                                for field, value in record_data.items():
                                    if field not in ['asset_hub', 'seller', 'trade']:
                                        setattr(existing, field, value)
                                existing.save()

                                # Ensure AssetDetails exists and keep trade pointer in sync
                                self._ensure_asset_details(existing.asset_hub, existing.trade)
                            updated_count += 1
                        else:
                            skipped_count += 1
                    else:
                        # Create AssetIdHub first
                        asset_hub = AssetIdHub.objects.create(sellertape_id=sellertape_id)

                        # Create SellerRawData with asset_hub as PK
                        try:
                            with transaction.atomic():
                                record_data['asset_hub'] = asset_hub
                                seller_raw = SellerRawData.objects.create(**record_data)
                                self._new_row_ids.append(seller_raw.asset_hub_id)
                                
                                # WHAT: Auto-create LoanLevelAssumption for each new asset
                                # WHY: Required for duration overrides and loan-specific calculations
                                # HOW: Import and create with default values, link to asset_hub
                                from acq_module.models.model_acq_assumptions import LoanLevelAssumption
                                LoanLevelAssumption.objects.get_or_create(
                                    asset_hub=asset_hub,
                                    defaults={}  # Use model defaults
                                )

                                # Ensure one-to-one AssetDetails row exists for this hub
                                self._ensure_asset_details(asset_hub, seller_raw.trade)

                                # Ensure one-to-one LlDataEnrichment row exists for this hub
                                LlDataEnrichment.objects.get_or_create(
                                    asset_hub=asset_hub,
                                    defaults={},
                                )
                            saved_count += 1
                        except Exception as insert_error:
                            logger.error(f'Error inserting SellerRawData for {sellertape_id}: {insert_error}')
                            skipped_count += 1

                except Exception as e:
                    logger.error(f'Error processing record {sellertape_id}: {e}')
                    skipped_count += 1

        return saved_count, updated_count, skipped_count

    def _ensure_asset_details(self, asset_hub: AssetIdHub, trade: Optional[Trade]):
        """Guarantee the AssetDetails one-to-one row exists and points to current trade."""
        try:
            details, created = AssetDetails.objects.get_or_create(
                asset=asset_hub,
                defaults={
                    "trade": trade,
                    "asset_status": AssetDetails.AssetStatus.ACTIVE,
                },
            )
            if not created:
                updates = []
                if trade and details.trade_id != getattr(trade, "id", None):
                    details.trade = trade
                    updates.append("trade")
                if not details.asset_status:
                    details.asset_status = AssetDetails.AssetStatus.ACTIVE
                    updates.append("asset_status")
                if updates:
                    details.save(update_fields=updates + ["updated_at"])
        except Exception:
            logger.exception("Failed to sync AssetDetails for asset_hub %s", asset_hub_id := getattr(asset_hub, 'id', None))

    def _run_batch_geocode_for_new_rows(self) -> Optional[Dict[str, Any]]:
        """Call Geocodio batch helper for all newly created SellerRawData rows."""
        if not self._new_row_ids:
            return None

        try:
            stats = batch_geocode_row_ids(
                self._new_row_ids,
                chunk_size=1000,
                fields=["census2024", "census", "school"],
            )
            logger.info(
                "Batch geocoded %s new rows (unique=%s, api_calls=%s)",
                stats.get('updated_rows'),
                stats.get('unique_addresses'),
                stats.get('api_calls'),
            )
            return stats
        except Exception as exc:
            logger.warning(f"Batch geocode failed: {exc}")
            return None
        finally:
            self._new_row_ids.clear()

    def _save_import_mapping(
        self,
        seller: Seller,
        trade: Optional[Trade],
        column_mapping: Dict[str, str],
        source_columns: List[str],
        file_path: Optional[Path],
        mapping_name: Optional[str],
        mapping_method: str,
        import_stats: Dict[str, Any]
    ):
        """
        WHAT: Save column mapping for future reuse
        WHY: Enable users to review and reuse successful mappings
        HOW: Create ImportMapping record with mapping details and stats
        
        Args:
            seller: Seller instance
            trade: Trade instance (optional)
            column_mapping: Dict of source -> target mappings
            source_columns: List of source column names
            file_path: Source file path (optional)
            mapping_name: Name for mapping (optional, auto-generated if not provided)
            mapping_method: How mapping was created (AI, MANUAL, EXACT, HYBRID)
            import_stats: Dict with import statistics
        """
        try:
            # WHAT: Import ImportMapping model
            # WHY: Need to create mapping record
            # HOW: Import from etl.models
            from etl.models.model_etl_import_mapping import ImportMapping
            from datetime import datetime
            
            # WHAT: Generate mapping name if not provided
            # WHY: Need unique, descriptive name for mapping
            # HOW: Use seller name, file name, and timestamp
            if not mapping_name:
                if file_path:
                    filename = file_path.stem
                else:
                    filename = "Import"
                date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
                mapping_name = f"{seller.name} - {filename} - {date_str}"
            
            # WHAT: Get original filename
            # WHY: Track which file format this mapping is for
            # HOW: Extract from file_path
            original_filename = file_path.name if file_path else None
            
            # WHAT: Check if similar mapping already exists
            # WHY: Avoid duplicate mappings for same seller/file
            # HOW: Look for recent mapping with same seller and filename
            existing_mapping = None
            if original_filename:
                existing_mapping = ImportMapping.objects.filter(
                    seller=seller,
                    original_filename=original_filename,
                    is_active=True
                ).order_by('-created_at').first()
            
            # WHAT: Update existing or create new mapping
            # WHY: Avoid cluttering with duplicate mappings
            # HOW: Check if existing mapping has same column_mapping
            if existing_mapping and existing_mapping.column_mapping == column_mapping:
                # WHAT: Update existing mapping stats
                # WHY: Track usage and success rate
                # HOW: Increment usage count and update stats
                existing_mapping.usage_count += 1
                existing_mapping.last_used_at = datetime.now()
                existing_mapping.import_stats = import_stats
                existing_mapping.save()
                
                if self.stdout:
                    self.stdout.write(
                        f'      [MAPPING] Updated existing mapping: {existing_mapping.mapping_name}\n'
                    )
                logger.info(f'Updated existing import mapping: {existing_mapping.id}')
            else:
                # WHAT: Create new mapping record
                # WHY: Save mapping for future use
                # HOW: Create ImportMapping instance
                new_mapping = ImportMapping.objects.create(
                    seller=seller,
                    trade=trade,
                    mapping_name=mapping_name,
                    column_mapping=column_mapping,
                    source_columns=source_columns,
                    mapping_method=mapping_method,
                    is_default=False,  # Don't auto-set as default
                    is_active=True,
                    original_filename=original_filename,
                    import_stats=import_stats,
                    notes=f"Auto-saved from import on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    usage_count=1,
                    last_used_at=datetime.now(),
                )
                
                if self.stdout:
                    self.stdout.write(
                        f'      [MAPPING] Saved new mapping: {new_mapping.mapping_name} (ID: {new_mapping.id})\n'
                    )
                logger.info(f'Created new import mapping: {new_mapping.id}')
                
        except Exception as e:
            # WHAT: Log error but don't fail import
            # WHY: Mapping save is optional, shouldn't break import
            # HOW: Log warning and continue
            logger.warning(f'Failed to save import mapping: {e}')
            if self.stdout:
                self.stdout.write(
                    f'      [WARNING] Failed to save mapping: {e}\n'
                )
