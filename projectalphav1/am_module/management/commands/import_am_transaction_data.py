"""
Django management command to import StateBridge daily transaction data from CSV.

WHAT:
- Reads a CSV (UTF-8 with/without BOM) and loads rows into
  am_module.models.statebridgeservicing.SBDailyTransactionData.
- Supports both creating new records and updating existing ones (upsert pattern).

WHY:
- StateBridge provides daily transaction snapshots via FTP in CSV format.
- Raw data must be loaded exactly as provided to maintain audit trail before
  ETL cleaning into ServicerTransactionData (internal model).

HOW (high-level):
- For each row, map CSV columns to SBDailyTransactionData model fields.
- Use bulk_create with update_conflicts for efficient upsert based on
  unique_together constraint (loan_id, loan_transaction_id, transaction_date).
- All fields are stored as strings (raw data landing pattern).
- Each batch is processed in a transaction for atomicity.
"""
from __future__ import annotations

import csv
from typing import Optional, Dict, Any, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from am_module.models.statebridgeservicing import SBDailyTransactionData


def _clean_string(val: Optional[str]) -> Optional[str]:
    """Clean and return string value, None if blank."""
    if val is None or val.strip() == '':
        return None
    return val.strip()


class Command(BaseCommand):
    help = 'Import StateBridge daily transaction data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing transaction data'
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
            'Investor ID ': 'investor_id',  # Note: CSV header has trailing space
            'Loan ID': 'loan_id',
            'Previous Ln Num': 'previous_ln_num',
            'Loan Transaction ID': 'loan_transaction_id',
            'Transaction Date': 'transaction_date',
            'Transaction Code': 'transaction_code',
            'Transaction Description': 'transaction_description',
            'Effective Date': 'effective_date',
            'Transaction Amt': 'transaction_amt',
            'Due Date': 'due_date',
            'Principal Amount': 'principal_amount',
            'Interest Amount': 'interest_amount',
            'Suspense Paid': 'suspense_paid',
            'Non Recoverable Advance': 'non_recoverable_advance',
            'Recoverable Advance': 'recoverable_advance',
            'Corporate Advance Reason Code': 'corporate_advance_reason_code',
            'Escrow Advance Balance': 'escrow_advance_balance',
            'Escrow Amount': 'escrow_amount',
            'Restricted Escrow': 'restricted_escrow',
            'Fee Code': 'fee_code',
            'Fee Description': 'fee_description',
            'Unapplied Pmt': 'unapplied_pmt',
            'Stipulation Unapplied Pmt': 'stipulation_unapplied_pmt',
            'Pre Petition Unapplied Pmt': 'pre_petition_unapplied_pmt',
            'Asset Manager': 'asset_manager',
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

                        batch.append(SBDailyTransactionData(**kwargs))

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

    def _process_batch(self, instances: List[SBDailyTransactionData], dry_run: bool) -> tuple[int, int]:
        """Process a batch of instances."""
        if not instances:
            return 0, 0

        if dry_run:
            self.stdout.write(f"Dry-run batch: would process {len(instances)} rows")
            return len(instances), 0

        try:
            with transaction.atomic():
                result = SBDailyTransactionData.objects.bulk_create(
                    instances,
                    update_conflicts=True,
                    update_fields=[
                        'previous_ln_num', 'transaction_code', 'transaction_description', 'effective_date',
                        'transaction_amt', 'due_date', 'principal_amount', 'interest_amount', 'suspense_paid',
                        'non_recoverable_advance', 'recoverable_advance', 'corporate_advance_reason_code',
                        'escrow_advance_balance', 'escrow_amount', 'restricted_escrow', 'fee_code',
                        'fee_description', 'unapplied_pmt', 'stipulation_unapplied_pmt',
                        'pre_petition_unapplied_pmt', 'asset_manager'
                    ],
                    unique_fields=['loan_id', 'loan_transaction_id', 'transaction_date'],
                )
                
                self.stdout.write(f"Processed batch: {len(instances)} rows")
                return len(result), 0

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Batch insert failed: {e}"))
            return 0, len(instances)
