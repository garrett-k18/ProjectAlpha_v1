"""
WHAT: Import servicer_id mappings to AssetIdHub from CSV.
WHY: Servicers provide mapping files linking their loan IDs to our internal asset IDs.
HOW: Read CSV (sellertape_id → servicer_id), update AssetIdHub records.

CSV Format:
    sellertape_id,servicer_id
    7000139091,2000013861
    7000089233,2000013855

Usage:
    python manage.py import_servicer_id_mapping --file path/to/mapping.csv [--dry-run]
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
import csv
import os
from typing import Dict, List
import logging

from core.models import AssetIdHub

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import servicer_id mappings from CSV to AssetIdHub'

    def add_arguments(self, parser):
        # WHAT: CSV file path (required).
        # WHY: User must specify which mapping file to import.
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Path to CSV file (relative to manage.py or absolute)',
        )
        
        # WHAT: Dry-run mode to test without writing to database.
        # WHY: Safety check before committing changes.
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run import without saving to database (test mode)',
        )

    def handle(self, *args, **options):
        """Main import execution."""
        file_path = options['file']
        dry_run = options['dry_run']
        
        # WHAT: Validate file exists.
        # WHY: Fail fast if file path is wrong.
        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")
        
        self.stdout.write(self.style.SUCCESS(
            f"{'[DRY RUN] ' if dry_run else ''}Starting servicer_id mapping import"
        ))
        self.stdout.write(f"Reading from: {file_path}")
        
        # WHAT: Read and parse CSV file.
        # WHY: Extract mappings from servicer-provided file.
        # HOW: Use csv.DictReader for header-based parsing.
        mappings = self._read_csv(file_path)
        
        if not mappings:
            self.stdout.write(self.style.WARNING("No mappings found in CSV file"))
            return
        
        self.stdout.write(f"Found {len(mappings)} mappings to process")
        
        # WHAT: Track import statistics.
        # WHY: Report success/failure rates for monitoring.
        stats = {
            'processed': 0,
            'updated': 0,
            'not_found': 0,
            'skipped_invalid': 0,
            'errors': 0,
        }
        
        # WHAT: Process each mapping.
        # WHY: Update AssetIdHub records with servicer_id values.
        for mapping in mappings:
            try:
                result = self._process_mapping(mapping, dry_run)
                stats[result] += 1
                stats['processed'] += 1
            except Exception as e:
                stats['errors'] += 1
                sellertape_id = mapping.get('sellertape_id', 'UNKNOWN')
                logger.error(f"Error processing sellertape_id={sellertape_id}: {e}")
                self.stdout.write(self.style.ERROR(f"  ERROR: {sellertape_id} - {str(e)}"))
        
        # WHAT: Report final statistics.
        # WHY: Transparency on import results.
        self.stdout.write(self.style.SUCCESS("\n=== Import Complete ==="))
        self.stdout.write(f"Processed:       {stats['processed']}")
        self.stdout.write(f"Updated:         {stats['updated']}")
        self.stdout.write(f"Not Found:       {stats['not_found']}")
        self.stdout.write(f"Skipped (invalid): {stats['skipped_invalid']}")
        self.stdout.write(f"Errors:          {stats['errors']}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] No changes were saved to database"))

    def _read_csv(self, file_path: str) -> List[Dict[str, str]]:
        """
        WHAT: Read CSV file and extract mappings.
        WHY: Parse servicer-provided mapping file.
        HOW: Use csv.DictReader to handle headers automatically.
        
        Returns: List of dicts with 'sellertape_id' and 'servicer_id' keys.
        """
        mappings = []
        
        # WHAT: Try multiple encodings to handle different file formats.
        # WHY: Servicer files may come in different encodings (UTF-8, cp1252, etc.).
        encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    # WHAT: Validate required columns exist.
                    # WHY: Fail fast if CSV structure is wrong.
                    if 'sellertape_id' not in reader.fieldnames or 'servicer_id' not in reader.fieldnames:
                        raise CommandError(
                            f"CSV must have 'sellertape_id' and 'servicer_id' columns. "
                            f"Found: {reader.fieldnames}"
                        )
                    
                    # WHAT: Read all rows into memory.
                    # WHY: Small file size expected (<10k rows), simplifies processing.
                    for row in reader:
                        sellertape_id = row['sellertape_id'].strip() if row['sellertape_id'] else None
                        servicer_id = row['servicer_id'].strip() if row['servicer_id'] else None
                        
                        if sellertape_id and servicer_id:
                            mappings.append({
                                'sellertape_id': sellertape_id,
                                'servicer_id': servicer_id,
                            })
                    
                    self.stdout.write(self.style.SUCCESS(f"Successfully read CSV using {encoding} encoding"))
                    break
                    
            except UnicodeDecodeError:
                # WHAT: Try next encoding if current one fails.
                # WHY: Automatic encoding detection.
                continue
            except Exception as e:
                if encoding == encodings[-1]:
                    # WHAT: Raise error if all encodings failed.
                    # WHY: File is truly unreadable.
                    raise CommandError(f"Failed to read CSV: {e}")
                continue
        
        return mappings

    def _process_mapping(self, mapping: Dict[str, str], dry_run: bool) -> str:
        """
        WHAT: Process one mapping record - update AssetIdHub.
        WHY: Core import logic for updating servicer_id field.
        HOW: Lookup AssetIdHub by sellertape_id, update servicer_id.
        
        Returns: 'updated', 'not_found', or 'skipped_invalid'
        """
        sellertape_id = mapping['sellertape_id']
        servicer_id = mapping['servicer_id']
        
        # WHAT: Validate inputs.
        # WHY: Skip records with missing data.
        if not sellertape_id or not servicer_id:
            logger.warning(f"Missing data in mapping: {mapping}")
            return 'skipped_invalid'
        
        # WHAT: Lookup AssetIdHub by sellertape_id.
        # WHY: Find the asset record to update.
        try:
            asset_hub = AssetIdHub.objects.get(sellertape_id=sellertape_id)
        except AssetIdHub.DoesNotExist:
            logger.warning(f"AssetIdHub not found for sellertape_id={sellertape_id}")
            return 'not_found'
        except AssetIdHub.MultipleObjectsReturned:
            logger.error(f"Multiple AssetIdHub records found for sellertape_id={sellertape_id}")
            return 'skipped_invalid'
        
        # WHAT: Update servicer_id field.
        # WHY: Store mapping for ETL and admin lookups.
        # HOW: Set field and save (unless dry-run).
        if not dry_run:
            asset_hub.servicer_id = servicer_id
            asset_hub.updated_at = timezone.now()
            asset_hub.save(update_fields=['servicer_id', 'updated_at'])
            logger.info(f"Updated AssetIdHub(id={asset_hub.id}): servicer_id={servicer_id}")
        else:
            logger.info(f"[DRY RUN] Would update AssetIdHub(id={asset_hub.id}): servicer_id={servicer_id}")
        
        return 'updated'
