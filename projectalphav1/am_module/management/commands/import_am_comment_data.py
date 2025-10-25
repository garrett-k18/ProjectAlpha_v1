"""
Django management command to import StateBridge daily comment data from CSV.

WHAT:
- Reads a CSV (UTF-8 with/without BOM) and loads rows into
  am_module.models.statebridgeservicing.SBDailyCommentData.
- Supports both creating new records and updating existing ones (upsert pattern).

WHY:
- StateBridge provides daily comment snapshots via FTP in CSV format.
- Raw data must be loaded exactly as provided to maintain audit trail before
  ETL cleaning into ServicerCommentData (internal model).

HOW (high-level):
- For each row, map CSV columns to SBDailyCommentData model fields.
- Use bulk_create with update_conflicts for efficient upsert based on
  unique_together constraint (loan_number, investor_id, comment_date).
- All fields are stored as strings (raw data landing pattern).
- Each batch is processed in a transaction for atomicity.
"""
from __future__ import annotations

import csv
from typing import Optional, Dict, Any, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from am_module.models.statebridgeservicing import SBDailyCommentData


def _clean_string(val: Optional[str]) -> Optional[str]:
    """Clean and return string value, None if blank."""
    if val is None or val.strip() == '':
        return None
    return val.strip()


class Command(BaseCommand):
    help = 'Import StateBridge daily comment data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing comment data'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to process in each batch (default: 1000)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse CSV and validate without writing to database'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        batch_size = options['batch_size']
        dry_run = options['dry_run']

        # Field mapping from CSV headers to model fields
        FIELD_MAP = {
            'Investor Id': 'investor_id',
            'Loan Number': 'loan_number',
            'Investor Loan Number': 'investor_loan_number',
            'Prior Servicer Loan Number': 'prior_servicer_loan_number',
            'Comment Date': 'comment_date',
            'Department': 'department',
            'Comment': 'comment',
            'Additional Notes': 'additional_notes',
        }

        try:
            with open(csv_file, 'r', encoding='utf-8-sig', newline='') as file:
                reader = csv.DictReader(file)
                
                # Validate CSV headers
                missing_headers = set(FIELD_MAP.keys()) - set(reader.fieldnames or [])
                if missing_headers:
                    self.stderr.write(
                        self.style.WARNING(f"Missing CSV headers: {missing_headers}")
                    )

                created_count = 0
                error_count = 0
                batch = []

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        # Map CSV row to model fields
                        kwargs = {}
                        for csv_col, model_field in FIELD_MAP.items():
                            if csv_col in row:
                                kwargs[model_field] = _clean_string(row[csv_col])

                        batch.append(SBDailyCommentData(**kwargs))

                        # Process batch when it reaches batch_size
                        if len(batch) >= batch_size:
                            created, errors = self._process_batch(batch, dry_run)
                            created_count += created
                            error_count += errors
                            batch = []

                    except Exception as e:
                        error_count += 1
                        self.stderr.write(
                            self.style.ERROR(f"Row {row_num} parse error: {e}")
                        )

                # Process remaining batch
                if batch:
                    created, errors = self._process_batch(batch, dry_run)
                    created_count += created
                    error_count += errors

        except FileNotFoundError:
            raise CommandError(f"CSV file not found: {csv_file}")
        except Exception as e:
            raise CommandError(f"Error processing CSV: {e}")

        # Final summary
        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: processed={created_count}, errors={error_count}, dry_run={dry_run}"
            )
        )

    def _process_batch(self, instances: List[SBDailyCommentData], dry_run: bool) -> tuple[int, int]:
        """Process a batch of instances."""
        if not instances:
            return 0, 0

        if dry_run:
            self.stdout.write(f"Dry-run batch: would process {len(instances)} rows")
            return len(instances), 0

        try:
            with transaction.atomic():
                result = SBDailyCommentData.objects.bulk_create(
                    instances,
                    update_conflicts=True,
                    update_fields=[
                        'investor_loan_number', 'prior_servicer_loan_number', 'department',
                        'comment', 'additional_notes'
                    ],
                    unique_fields=['loan_number', 'investor_id', 'comment_date'],
                )
                
                self.stdout.write(f"Processed batch: {len(instances)} rows")
                return len(result), 0

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Batch insert failed: {e}"))
            return 0, len(instances)
