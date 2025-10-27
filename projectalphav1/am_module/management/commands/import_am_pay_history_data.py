"""
Django management command to import StateBridge daily pay history data from CSV.

WHAT:
- Reads a CSV (UTF-8 with/without BOM) and loads rows into
  am_module.models.statebridgeservicing.SBDailyPayHistoryData.
- Inserts every row exactly as received (no deduping) to preserve audit history.

WHY:
- StateBridge provides daily pay history snapshots via FTP in CSV format.
- Raw data must be loaded exactly as provided to maintain audit trail before
  ETL cleaning into ServicerPayHistoryData (internal model).

HOW (high-level):
- For each row, map CSV columns to SBDailyPayHistoryData model fields.
- Use bulk_create batches with encoding fallbacks so duplicate snapshots land side-by-side.
- All fields are stored as strings (raw data landing pattern).
- Each batch is processed in a transaction for atomicity.
"""
from __future__ import annotations

import csv
import io
from typing import Optional, Dict, Any, List, TextIO, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from am_module.models.statebridgeservicing import SBDailyPayHistoryData


def _clean_string(val: Optional[str]) -> Optional[str]:
    """Clean and return string value, None if blank."""
    if val is None or val.strip() == '':
        return None
    return val.strip()


def _row_has_data(mapped_values: Dict[str, Optional[str]]) -> bool:
    """Return True when at least one mapped field contains data."""
    return any(value not in (None, '') for value in mapped_values.values())


def _open_csv_with_fallback(
    path: str,
    encodings: List[str],
) -> Tuple[TextIO, str]:
    """Open CSV with encoding fallback, returning text handle and detected encoding."""
    # Read file once as bytes so we can retry decoding without extra disk I/O.
    # Reference: Python codec docs https://docs.python.org/3/library/codecs.html#codecs.decode
    with open(path, 'rb') as raw_file:
        data = raw_file.read()

    last_error: Optional[Exception] = None
    for encoding in encodings:
        try:
            text = data.decode(encoding)
            # Wrap decoded text in StringIO so csv module controls newline behavior (newline='').
            # Docs: https://docs.python.org/3/library/csv.html#csv.reader
            handle = io.StringIO(text, newline='')
            return handle, encoding
        except UnicodeDecodeError as decode_error:
            last_error = decode_error
            continue
    if last_error is not None:
        raise last_error
    raise UnicodeDecodeError("", b"", 0, 0, "Unable to detect encoding")


class Command(BaseCommand):
    help = 'Import StateBridge daily pay history data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing pay history data'
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
            'Investor': 'investor',
            'Loan Number': 'loan_number',
            'Previous Ln Num': 'previous_ln_num',
            'Borrower Name': 'borrower_name',
            'Property Address': 'property_address',
            'City': 'city',
            'State': 'state',
            'Zip': 'zip',
            'Property Type': 'property_type',
            '# of Units': 'number_of_units',
            'Occupancy Status': 'occupancy_status',
            'Original UPB': 'original_upb',
            '2nd UPB': 'second_upb',
            'Current UPB': 'current_upb',
            'Account Type': 'account_type',
            'Lien': 'lien',
            'Loan Term': 'loan_term',
            'Remaining Term': 'remaining_term',
            'Maturity Date': 'maturity_date',
            'Rate Type': 'rate_type',
            'ARM': 'arm',
            'Balloon': 'balloon',
            'Piggyback': 'piggyback',
            'Current IR': 'current_ir',
            'Current PI': 'current_pi',
            'Current TI': 'current_ti',
            'Current PITI': 'current_piti',
            'Last Full Payment Dt': 'last_full_payment_dt',
            'Next Payment Due Dt': 'next_payment_due_dt',
            'Escrow Indicator': 'escrow_indicator',
            'Restricted Escrow': 'restricted_escrow',
            'Escrow Advance': 'escrow_advance',
            'REC CORP Advance Balance': 'rec_corp_advance_balance',
            'Third Party REC Balance': 'third_party_rec_balance',
            'Accrued Interest': 'accrued_interest',
            'Accrued Late Fees': 'accrued_late_fees',
            'FCStatus': 'fc_status',
            'FCType': 'fc_type',
            'FC 1st Legal Filed Dt': 'fc_first_legal_filed_dt',
            'FC Judgement Entered Dt': 'fc_judgement_entered_dt',
            'FC Sale Scheduled Dt': 'fc_sale_scheduled_dt',
            'FC Suspended Dt': 'fc_suspended_dt',
            'FC Removal Dt': 'fc_removal_dt',
            'FCRemoval Description': 'fc_removal_description',
            'BK Status': 'bk_status',
            'BK Code': 'bk_code',
            'BK Filing Date': 'bk_filing_date',
            'BK Case #': 'bk_case_number',
            'BKRemoval Dt': 'bk_removal_dt',
            'Original Appraised Value': 'original_appraised_value',
            'AS ISBPO': 'as_is_bpo',
            'BPODate': 'bpo_date',
            'FICOOriginal': 'fico_original',
            'FICO': 'fico',
            'FICODate': 'fico_date',
            'Loan Mod Dt': 'loan_mod_dt',
            'Mod UPB': 'mod_upb',
            'Mod IR': 'mod_ir',
            'Mod PI': 'mod_pi',
            'Mod First Payment Dt': 'mod_first_payment_dt',
            'Mod Maturity': 'mod_maturity',
            'Origination Date': 'origination_date',
            'Original Principal': 'original_principal',
            'Orig Rate': 'orig_rate',
            'FPDate': 'fp_date',
            'Mt Date': 'mt_date',
            'Interest Only Indicator': 'interest_only_indicator',
            'Interest Only Expiration Dt': 'interest_only_expiration_dt',
            'HOI Expiration Dt': 'hoi_expiration_dt',
            'M0': 'm0',
            'M1': 'm1',
            'M2': 'm2',
            'M3': 'm3',
            'M4': 'm4',
            'M5': 'm5',
            'M6': 'm6',
            'M7': 'm7',
            'M8': 'm8',
            'M9': 'm9',
            'M10': 'm10',
            'M11': 'm11',
            'M12': 'm12',
            'ID0 0 - $': 'id0_0',
            'ID0 1 - $': 'id0_1',
            'ID0 2 - $': 'id0_2',
            'ID0 3 - $': 'id0_3',
            'ID0 4 - $': 'id0_4',
            'ID0 5 - $': 'id0_5',
            'ID0 6 - $': 'id0_6',
            'ID0 7 - $': 'id0_7',
            'ID0 8 - $': 'id0_8',
            'ID0 9 - $': 'id0_9',
            'ID0 10 - $': 'id0_10',
            'ID0 11 - $': 'id0_11',
            'ID0 12 - $': 'id0_12',
        }

        skipped_blank_rows = 0  # Track rows containing only delimiters with no actual data.

        try:
            csv_handle, active_encoding = _open_csv_with_fallback(
                csv_file,
                ['utf-8-sig', 'utf-8', 'cp1252', 'latin-1'],
            )
            with csv_handle as file:
                if active_encoding not in {'utf-8', 'utf-8-sig'}:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Detected non-UTF8 encoding '{active_encoding}' for file: {csv_file}. "
                            "Continuing with fallback decoding."
                        )
                    )
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

                        batch.append(SBDailyPayHistoryData(**kwargs))

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

    def _process_batch(self, instances: List[SBDailyPayHistoryData], dry_run: bool) -> tuple[int, int]:
        """Process a batch of instances."""
        if not instances:
            return 0, 0

        if dry_run:
            self.stdout.write(f"Dry-run batch: would process {len(instances)} rows")
            return len(instances), 0

        try:
            with transaction.atomic():
                result = SBDailyPayHistoryData.objects.bulk_create(
                    instances,
                    batch_size=len(instances),
                )
                
                self.stdout.write(f"Processed batch: {len(instances)} rows")
                return len(result), 0

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Batch insert failed: {e}"))
            return 0, len(instances)
