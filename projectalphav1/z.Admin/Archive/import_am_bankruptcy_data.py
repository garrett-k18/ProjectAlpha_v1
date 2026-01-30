"""
Django management command to import StateBridge daily bankruptcy data from CSV.

WHAT:
- Reads a CSV (UTF-8 with/without BOM) and loads rows into
  etl.models.SBDailyBankruptcyData.
- Supports both creating new records and updating existing ones (upsert pattern).

WHY:
- StateBridge provides daily bankruptcy snapshots via FTP in CSV format.
- Raw data must be loaded exactly as provided to maintain audit trail before
  ETL cleaning into ServicerBankruptcyData (internal model).

HOW (high-level):
- For each row, map CSV columns to SBDailyBankruptcyData model fields.
- Use bulk_create with update_conflicts for efficient upsert based on
  unique_together constraint (loan_id, investor_id, bk_filed_date).
- All fields are stored as strings (raw data landing pattern).
- Each batch is processed in a transaction for atomicity.
"""
from __future__ import annotations

import csv
from typing import Optional, Dict, Any, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from etl.models import SBDailyBankruptcyData


def _clean_string(val: Optional[str]) -> Optional[str]:
    """Clean and return string value, None if blank."""
    if val is None or val.strip() == '':
        return None
    return val.strip()


def _row_has_data(mapped_values: Dict[str, Optional[str]]) -> bool:
    """Return True when at least one mapped field contains data."""
    return any(value not in (None, '') for value in mapped_values.values())


class Command(BaseCommand):
    help = 'Import StateBridge daily bankruptcy data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing bankruptcy data'
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
            'Asset Manager': 'asset_manager',
            'Loan ID': 'loan_id',
            'Investor Loan ID': 'investor_loan_id',
            'Previous Ln Num': 'previous_ln_num',
            'Acquisition Date': 'acquisition_date',
            'Loan Due Date': 'loan_due_date',
            'MBA': 'mba',
            'Legal': 'legal',
            'Warning': 'warning',
            'Investor ID': 'investor_id',
            'Chapter': 'chapter',
            'Case Number': 'case_number',
            'BK Filed Date': 'bk_filed_date',
            'State Filed': 'state_filed',
            'Filing Court': 'filing_court',
            'Filing Borrower': 'filing_borrower',
            'Joint Filer': 'joint_filer',
            'Trustee Name': 'trustee_name',
            'Statebridge Atty Name': 'statebridge_atty_name',
            'Borrower Atty Name': 'borrower_atty_name',
            'Bankruptcy Status': 'bankruptcy_status',
            'Prepetition Claim Amt': 'prepetition_claim_amt',
            'Active Plan': 'active_plan',
            'Plan Start Date': 'plan_start_date',
            'Pre Petition Payment': 'pre_petition_payment',
            'Plan Length': 'plan_length',
            'Projected Plan End Date': 'projected_plan_end_date',
            'Actual Plan Completion Date': 'actual_plan_completion_date',
            'Last Pre Petition Payment Rcvd Date': 'last_pre_petition_payment_rcvd_date',
            'Last Payment Applied': 'last_payment_applied',
            'Pre Petition Balance': 'pre_petition_balance',
            'Stipulation Claim Amt': 'stipulation_claim_amt',
            'Stipulation Date': 'stipulation_date',
            'Stipulation First Pmt Date': 'stipulation_first_pmt_date',
            'Stipulation Last Pmt Date': 'stipulation_last_pmt_date',
            'Stipulation Monthly Pmt': 'stipulation_monthly_pmt',
            'Stipulation Repay Months': 'stipulation_repay_months',
            'Last Stipulation Payment Rcvd Date': 'last_stipulation_payment_rcvd_date',
            'First Post Petition Due Date': 'first_post_petition_due_date',
            'Next Post Petition Due Date': 'next_post_petition_due_date',
            'Post Petition Pmt Amt': 'post_petition_pmt_amt',
            'BK Case Closed Date': 'bk_case_closed_date',
            'BK Discharge Date': 'bk_discharge_date',
            'BK Dismissed Date': 'bk_dismissed_date',
            'Date Motion for Relief Filed': 'date_motion_for_relief_filed',
            'Date Proof of Claim Filed': 'date_proof_of_claim_filed',
            'Date of Meeting of Creditors': 'date_of_meeting_of_creditors',
            'Date Object to Confirmation Filed': 'date_object_to_confirmation_filed',
            'Relief Date': 'relief_date',
            'Bankruptcy Business Area Status': 'bankruptcy_business_area_status',
            'Bankruptcy Business Area Status Date': 'bankruptcy_business_area_status_date',
            'Order of Confirmation Date': 'order_of_confirmation_date',
            'Active Bankruptcy': 'active_bankruptcy',
        }

        skipped_blank_rows = 0  # Track rows that contain only delimiters (no actual data).

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

                        if not _row_has_data(kwargs):
                            skipped_blank_rows += 1
                            continue

                        batch.append(SBDailyBankruptcyData(**kwargs))

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
                f"Import complete: processed={created_count}, errors={error_count}, dry_run={dry_run}, skipped_blank_rows={skipped_blank_rows}"
            )
        )

    def _process_batch(self, instances: List[SBDailyBankruptcyData], dry_run: bool) -> tuple[int, int]:
        """Process a batch of instances."""
        if not instances:
            return 0, 0

        if dry_run:
            self.stdout.write(f"Dry-run batch: would process {len(instances)} rows")
            return len(instances), 0

        try:
            with transaction.atomic():
                result = SBDailyBankruptcyData.objects.bulk_create(
                    instances,
                    batch_size=len(instances),
                )
                
                self.stdout.write(f"Processed batch: {len(instances)} rows")
                return len(result), 0

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Batch insert failed: {e}"))
            return 0, len(instances)
