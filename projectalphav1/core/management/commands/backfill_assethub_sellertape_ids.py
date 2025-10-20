"""
WHAT: Backfill sellertape_id into existing AssetIdHub records.
WHY: Prod AssetIdHub records were created without sellertape_id populated.
HOW: Read CSV mapping (asset_hub_id → sellertape_id), update records.

CSV Format:
    sellertape_id,asset_hub_id
    7000139091,1
    7000089233,2

Usage:
    python manage.py backfill_assethub_sellertape_ids --file DataUploads/sellertapeid_to_assethub.csv [--dry-run]
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import csv
import os
from typing import Dict, List
import logging

from core.models import AssetIdHub

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Backfill sellertape_id into existing AssetIdHub records from CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Path to CSV file (sellertape_id,asset_hub_id)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Test mode, no DB writes',
        )

    def handle(self, *args, **options):
        """Main backfill execution."""
        file_path = options['file']
        dry_run = options['dry_run']
        
        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")
        
        self.stdout.write(self.style.SUCCESS(
            f"{'[DRY RUN] ' if dry_run else ''}Starting AssetIdHub sellertape_id backfill"
        ))
        self.stdout.write(f"Reading from: {file_path}")
        
        # Read CSV
        mappings = self._read_csv(file_path)
        
        if not mappings:
            self.stdout.write(self.style.WARNING("No mappings found"))
            return
        
        self.stdout.write(f"Found {len(mappings)} mappings to process")
        
        # Statistics
        stats = {
            'processed': 0,
            'updated': 0,
            'not_found': 0,
            'already_set': 0,
            'errors': 0,
        }
        
        # Process each mapping
        for mapping in mappings:
            try:
                result = self._process_mapping(mapping, dry_run)
                stats[result] += 1
                stats['processed'] += 1
            except Exception as e:
                stats['errors'] += 1
                asset_hub_id = mapping.get('asset_hub_id', 'UNKNOWN')
                logger.error(f"Error processing asset_hub_id={asset_hub_id}: {e}")
                self.stdout.write(self.style.ERROR(f"  ERROR: AssetHub #{asset_hub_id} - {e}"))
        
        # Report results
        self.stdout.write(self.style.SUCCESS("\n=== Backfill Complete ==="))
        self.stdout.write(f"Processed:      {stats['processed']}")
        self.stdout.write(f"Updated:        {stats['updated']}")
        self.stdout.write(f"Already Set:    {stats['already_set']}")
        self.stdout.write(f"Not Found:      {stats['not_found']}")
        self.stdout.write(f"Errors:         {stats['errors']}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] No changes saved"))

    def _read_csv(self, file_path: str) -> List[Dict[str, str]]:
        """Read CSV and extract mappings."""
        mappings = []
        
        encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    # Validate columns
                    if 'sellertape_id' not in reader.fieldnames or 'asset_hub_id' not in reader.fieldnames:
                        raise CommandError(
                            f"CSV must have 'sellertape_id' and 'asset_hub_id' columns. "
                            f"Found: {reader.fieldnames}"
                        )
                    
                    for row in reader:
                        sellertape_id = row['sellertape_id'].strip() if row['sellertape_id'] else None
                        asset_hub_id = row['asset_hub_id'].strip() if row['asset_hub_id'] else None
                        
                        if sellertape_id and asset_hub_id:
                            try:
                                mappings.append({
                                    'sellertape_id': sellertape_id,
                                    'asset_hub_id': int(asset_hub_id),
                                })
                            except ValueError:
                                logger.warning(f"Invalid asset_hub_id (not numeric): {asset_hub_id}")
                                continue
                    
                    self.stdout.write(self.style.SUCCESS(f"Read CSV using {encoding} encoding"))
                    break
                    
            except UnicodeDecodeError:
                continue
            except Exception as e:
                if encoding == encodings[-1]:
                    raise CommandError(f"Failed to read CSV: {e}")
                continue
        
        return mappings

    def _process_mapping(self, mapping: Dict, dry_run: bool) -> str:
        """Process one mapping - update AssetIdHub."""
        asset_hub_id = mapping['asset_hub_id']
        sellertape_id = mapping['sellertape_id']
        
        # Lookup AssetIdHub by primary key
        try:
            asset_hub = AssetIdHub.objects.get(pk=asset_hub_id)
        except AssetIdHub.DoesNotExist:
            logger.warning(f"AssetIdHub #{asset_hub_id} not found")
            return 'not_found'
        
        # Check if already set
        if asset_hub.sellertape_id:
            if asset_hub.sellertape_id == sellertape_id:
                logger.info(f"AssetIdHub #{asset_hub_id} already has correct sellertape_id")
                return 'already_set'
            else:
                logger.warning(
                    f"AssetIdHub #{asset_hub_id} has different sellertape_id: "
                    f"existing={asset_hub.sellertape_id}, new={sellertape_id}"
                )
                # Still update it
        
        # Update sellertape_id
        if not dry_run:
            asset_hub.sellertape_id = sellertape_id
            asset_hub.save(update_fields=['sellertape_id', 'updated_at'])
            logger.info(f"Updated AssetIdHub #{asset_hub_id}: sellertape_id={sellertape_id}")
        else:
            logger.info(f"[DRY RUN] Would update AssetIdHub #{asset_hub_id}: sellertape_id={sellertape_id}")
        
        return 'updated'
