"""
Django management command to import StateBridge daily foreclosure data from CSV.

WHAT:
- Reads a CSV (UTF-8 with/without BOM) and loads rows into
  am_module.models.statebridgeservicing.SBDailyForeclosureData.
- Supports both creating new records and updating existing ones (upsert pattern).

WHY:
- StateBridge provides daily foreclosure snapshots via FTP in CSV format.
- Raw data must be loaded exactly as provided to maintain audit trail before
  ETL cleaning into ServicerForeclosureData (internal model).

HOW (high-level):
- For each row, map CSV columns to SBDailyForeclosureData model fields.
- Use bulk_create with update_conflicts for efficient upsert based on
  unique_together constraint (loan_id, investor_id, file_date).
- All fields are stored as strings (raw data landing pattern).
- Each batch is processed in a transaction for atomicity.
"""
from __future__ import annotations

import csv
from typing import Optional, Dict, Any, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from am_module.models.statebridgeservicing import SBDailyForeclosureData


def _clean_string(val: Optional[str]) -> Optional[str]:
    """Clean and return string value, None if blank."""
    if val is None or val.strip() == '':
        return None
    return val.strip()


class Command(BaseCommand):
    help = 'Import StateBridge daily foreclosure data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing foreclosure data'
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
            'FileDate': 'file_date',
            'Loan ID': 'loan_id',
            'Investor ID': 'investor_id',
            'Investor Loan Number': 'investor_loan_number',
            'Prior Servicer Loan Number': 'prior_servicer_loan_number',
            'Prior Servicer Name': 'prior_servicer_name',
            'Prior Servicer Contact': 'prior_servicer_contact',
            'Prior Servicer Contact Phone': 'prior_servicer_contact_phone',
            'Legal Status': 'legal_status',
            'Prim Stat': 'prim_stat',
            'Warning': 'warning',
            'Due Date': 'due_date',
            'Loan Type': 'loan_type',
            'Original Loan Amount': 'original_loan_amount',
            'Current UPB': 'current_upb',
            'Lien Position': 'lien_position',
            'Borrower Name': 'borrower_name',
            'Borrower First Name': 'borrower_first_name',
            'Borrower Last Name': 'borrower_last_name',
            'Borrower Deceased': 'borrower_deceased',
            'Property State': 'property_state',
            'Property Zip': 'property_zip',
            'Mortgage Asgmnt Complete Date': 'mortgage_asgmnt_complete_date',
            'Current Assignee': 'current_assignee',
            'MI Insurance': 'mi_insurance',
            'MI Company Name': 'mi_company_name',
            'MI Claim Filed': 'mi_claim_filed',
            'MI Paid Amount': 'mi_paid_amount',
            'MI Claim Paid Date': 'mi_claim_paid_date',
            'BPO Date': 'bpo_date',
            'BPO As Is Value': 'bpo_as_is_value',
            'BPO Repaired Value': 'bpo_repaired_value',
            'Occupancy Status': 'occupancy_status',
            'Property Condition from Inspection': 'property_condition_from_inspection',
            'Date Inspection Completed': 'date_inspection_completed',
            'FC Attorney': 'fc_attorney',
            'Last Atty Note Date': 'last_atty_note_date',
            'Last Atty Note Topic': 'last_atty_note_topic',
            'Last Atty Note': 'last_atty_note',
            'Delinquent Taxes (Y/N)': 'delinquent_taxes',
            'Title Issue': 'title_issue',
            'Title Received': 'title_received',
            'FC Specialist': 'fc_specialist',
            'Date Breach Letter Sent': 'date_breach_letter_sent',
            'NOI Expiration Date': 'noi_expiration_date',
            'Original FC Referral Date': 'original_fc_referral_date',
            'Date Referred to FC Atty': 'date_referred_to_fc_atty',
            'Reason for Default': 'reason_for_default',
            'Is a Contested FC (Y/N)': 'is_a_contested_fc',
            'Current FC Step': 'current_fc_step',
            'FC Step Completed Date': 'fc_step_completed_date',
            'Next FC Step': 'next_fc_step',
            'Next FC Step Due Date': 'next_fc_step_due_date',
            'Hold Start Date': 'hold_start_date',
            'Hold Reason': 'hold_reason',
            'Hold End Date': 'hold_end_date',
            'Projected FC Sale Date': 'projected_fc_sale_date',
            'Scheduled FC Sale Date': 'scheduled_fc_sale_date',
            'Actual FC Sale Date': 'actual_fc_sale_date',
            'Bid Amount': 'bid_amount',
            'Sale Amount': 'sale_amount',
            'Sale Results': 'sale_results',
            'RRC Expired': 'rrc_expired',
            'FC Completion Date': 'fc_completion_date',
            'Deed Recorded Y/N': 'deed_recorded',
            'First Legal Action Date': 'first_legal_action_date',
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

                        batch.append(SBDailyForeclosureData(**kwargs))

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

    def _process_batch(self, instances: List[SBDailyForeclosureData], dry_run: bool) -> tuple[int, int]:
        """Process a batch of instances."""
        if not instances:
            return 0, 0

        if dry_run:
            self.stdout.write(f"Dry-run batch: would process {len(instances)} rows")
            return len(instances), 0

        try:
            with transaction.atomic():
                result = SBDailyForeclosureData.objects.bulk_create(
                    instances,
                    update_conflicts=True,
                    update_fields=[
                        field for field in [
                            'prior_servicer_loan_number', 'prior_servicer_name', 'prior_servicer_contact',
                            'prior_servicer_contact_phone', 'legal_status', 'prim_stat', 'warning',
                            'due_date', 'loan_type', 'original_loan_amount', 'current_upb', 'lien_position',
                            'borrower_name', 'borrower_first_name', 'borrower_last_name', 'borrower_deceased',
                            'property_state', 'property_zip', 'mortgage_asgmnt_complete_date', 'current_assignee',
                            'mi_insurance', 'mi_company_name', 'mi_claim_filed', 'mi_paid_amount',
                            'mi_claim_paid_date', 'bpo_date', 'bpo_as_is_value', 'bpo_repaired_value',
                            'occupancy_status', 'property_condition_from_inspection', 'date_inspection_completed',
                            'fc_attorney', 'last_atty_note_date', 'last_atty_note_topic', 'last_atty_note',
                            'delinquent_taxes', 'title_issue', 'title_received', 'fc_specialist',
                            'date_breach_letter_sent', 'noi_expiration_date', 'original_fc_referral_date',
                            'date_referred_to_fc_atty', 'reason_for_default', 'is_a_contested_fc',
                            'current_fc_step', 'fc_step_completed_date', 'next_fc_step', 'next_fc_step_due_date',
                            'hold_start_date', 'hold_reason', 'hold_end_date', 'projected_fc_sale_date',
                            'scheduled_fc_sale_date', 'actual_fc_sale_date', 'bid_amount', 'sale_amount',
                            'sale_results', 'rrc_expired', 'fc_completion_date', 'deed_recorded',
                            'first_legal_action_date', 'count'
                        ]
                    ],
                    unique_fields=['loan_id', 'investor_id', 'file_date'],
                )
                
                self.stdout.write(f"Processed batch: {len(instances)} rows")
                return len(result), 0

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Batch insert failed: {e}"))
            return 0, len(instances)
