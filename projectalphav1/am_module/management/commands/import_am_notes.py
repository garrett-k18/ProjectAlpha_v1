"""
Django management command to import AM notes from CSV.

WHAT:
- Reads a CSV with columns: loanNumberSeller, createdTimestamp, value
- Creates AMNote records linked to AssetIdHub via loan number lookup

WHY:
- Bulk import historical notes from external systems
- Preserve original creation timestamps

HOW:
- Maps loan numbers to AssetIdHub records
- Creates AMNote instances with body=value and created_at=createdTimestamp
- Processes in batches for efficiency
"""
from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Optional, List, TextIO, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from am_module.models import AMNote
from core.models import AssetIdHub


def _clean_string(val: Optional[str]) -> Optional[str]:
    """Clean and return string value, None if blank."""
    if val is None or val.strip() == '':
        return None
    return val.strip()


def _parse_timestamp(timestamp_str: Optional[str]) -> Optional[datetime]:
    """Parse timestamp string to datetime object.
    
    Supports common formats:
    - ISO format: 2024-01-15T10:30:00
    - US format: 01/15/2024 10:30:00 or 1/15/2024 10:30
    - Date only: 2024-01-15 or 01/15/2024
    """
    if not timestamp_str:
        return None
    
    timestamp_str = timestamp_str.strip()
    
    # Try common timestamp formats (order matters - try most specific first)
    formats = [
        '%Y-%m-%dT%H:%M:%S',      # ISO format
        '%Y-%m-%d %H:%M:%S.%f',    # With microseconds
        '%Y-%m-%d %H:%M:%S',       # Standard datetime
        '%m/%d/%Y %I:%M:%S %p',    # US with AM/PM and seconds
        '%m/%d/%Y %H:%M:%S',       # US datetime with seconds
        '%m/%d/%Y %H:%M',          # US datetime without seconds (common in CSV)
        '%Y-%m-%d',                # Date only ISO
        '%m/%d/%Y',                # Date only US
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            # Make timezone-aware
            return timezone.make_aware(dt, timezone.get_current_timezone())
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse timestamp: {timestamp_str}")


def _open_csv_with_fallback(
    path: str,
    encodings: List[str],
) -> Tuple[TextIO, str]:
    """Open CSV with encoding fallback, returning handle and detected encoding."""
    with open(path, 'rb') as raw_file:
        data = raw_file.read()

    last_error: Optional[Exception] = None
    for encoding in encodings:
        try:
            text = data.decode(encoding)
            handle = io.StringIO(text, newline='')
            return handle, encoding
        except UnicodeDecodeError as decode_error:
            last_error = decode_error
            continue
    
    if last_error is not None:
        raise last_error
    raise UnicodeDecodeError("", b"", 0, 0, "Unable to detect encoding")


class Command(BaseCommand):
    help = 'Import AM notes from CSV file (loanNumberSeller, createdTimestamp, value)'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing note data'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Number of records to process in each batch (default: 500)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse CSV and validate without writing to database'
        )
        parser.add_argument(
            '--skip-missing-assets',
            action='store_true',
            help='Skip notes for loan numbers not found in AssetIdHub (default: error on missing)'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        skip_missing = options['skip_missing_assets']

        # Expected CSV columns
        REQUIRED_COLUMNS = ['loanNumberSeller', 'createdTimestamp', 'value']

        # Statistics
        stats = {
            'processed': 0,
            'created': 0,
            'skipped_blank': 0,
            'skipped_missing_asset': 0,
            'errors': 0,
        }

        try:
            csv_handle, active_encoding = _open_csv_with_fallback(
                csv_file,
                ['utf-8-sig', 'utf-8', 'cp1252', 'latin-1'],
            )
            
            with csv_handle as file:
                if active_encoding not in {'utf-8', 'utf-8-sig'}:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Detected non-UTF8 encoding '{active_encoding}' for file: {csv_file}"
                        )
                    )
                
                reader = csv.DictReader(file)
                
                # Validate CSV headers
                if not reader.fieldnames:
                    raise CommandError("CSV file has no headers")
                
                missing_headers = set(REQUIRED_COLUMNS) - set(reader.fieldnames)
                if missing_headers:
                    raise CommandError(f"Missing required CSV columns: {missing_headers}")

                # Pre-load all asset hubs for efficient lookup using servicer_id
                self.stdout.write("Loading AssetIdHub records for servicer ID lookup...")
                asset_hub_map = {}
                for hub in AssetIdHub.objects.all():
                    if hub.servicer_id:
                        asset_hub_map[hub.servicer_id] = hub
                
                self.stdout.write(f"Loaded {len(asset_hub_map)} asset hub records with servicer IDs")

                batch = []

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        # Extract and clean values
                        loan_number = _clean_string(row.get('loanNumberSeller'))
                        timestamp_str = _clean_string(row.get('createdTimestamp'))
                        note_body = _clean_string(row.get('value'))

                        # Skip blank rows
                        if not loan_number or not note_body:
                            stats['skipped_blank'] += 1
                            continue

                        # Parse timestamp
                        try:
                            created_at = _parse_timestamp(timestamp_str)
                        except ValueError as e:
                            self.stderr.write(
                                self.style.ERROR(f"Row {row_num}: {e}")
                            )
                            stats['errors'] += 1
                            continue

                        # Lookup asset hub
                        asset_hub = asset_hub_map.get(loan_number)
                        if not asset_hub:
                            if skip_missing:
                                stats['skipped_missing_asset'] += 1
                                if row_num % 100 == 0:  # Log occasionally
                                    self.stdout.write(
                                        f"Row {row_num}: Skipping loan {loan_number} (not found)"
                                    )
                                continue
                            else:
                                raise CommandError(
                                    f"Row {row_num}: Loan number '{loan_number}' not found in AssetIdHub. "
                                    "Use --skip-missing-assets to skip these rows."
                                )

                        # Create note instance
                        note = AMNote(
                            asset_hub=asset_hub,
                            body=note_body,
                            created_at=created_at,
                        )
                        batch.append(note)
                        stats['processed'] += 1

                        # Process batch when it reaches batch_size
                        if len(batch) >= batch_size:
                            created = self._process_batch(batch, dry_run)
                            stats['created'] += created
                            batch = []
                            
                            # Progress update
                            self.stdout.write(
                                f"Progress: {stats['processed']} rows processed, "
                                f"{stats['created']} notes created"
                            )

                    except CommandError:
                        raise
                    except Exception as e:
                        stats['errors'] += 1
                        self.stderr.write(
                            self.style.ERROR(f"Row {row_num} error: {e}")
                        )

                # Process remaining batch
                if batch:
                    created = self._process_batch(batch, dry_run)
                    stats['created'] += created

        except FileNotFoundError:
            raise CommandError(f"CSV file not found: {csv_file}")
        except Exception as e:
            raise CommandError(f"Error processing CSV: {e}")

        # Final summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("Import Complete"))
        self.stdout.write("="*60)
        self.stdout.write(f"Rows processed:        {stats['processed']}")
        self.stdout.write(f"Notes created:         {stats['created']}")
        self.stdout.write(f"Blank rows skipped:    {stats['skipped_blank']}")
        self.stdout.write(f"Missing assets:        {stats['skipped_missing_asset']}")
        self.stdout.write(f"Errors:                {stats['errors']}")
        self.stdout.write(f"Dry run mode:          {dry_run}")
        self.stdout.write("="*60)

    def _process_batch(
        self,
        instances: List[AMNote],
        dry_run: bool,
    ) -> int:
        """Process a batch of note instances."""
        if not instances:
            return 0

        if dry_run:
            self.stdout.write(f"[DRY RUN] Would create {len(instances)} notes")
            return len(instances)

        try:
            with transaction.atomic():
                AMNote.objects.bulk_create(instances, batch_size=len(instances))
                return len(instances)

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Batch insert failed: {e}"))
            return 0
