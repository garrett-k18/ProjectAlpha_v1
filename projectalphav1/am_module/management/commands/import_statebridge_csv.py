"""
Django management command to import StateBridge daily loan data from CSV.

WHAT:
- Reads a CSV (UTF-8 with/without BOM) and loads rows into
  am_module.models.statebridgeservicing.SBDailyLoanData.
- Supports both creating new records and updating existing ones (upsert pattern).

WHY:
- StateBridge provides daily loan servicing snapshots via FTP in CSV format.
- Raw data must be loaded exactly as provided to maintain audit trail before
  ETL cleaning into ServicerLoanData (internal model).

HOW (high-level):
- For each row, map CSV columns to SBDailyLoanData model fields.
- Use bulk_create with update_conflicts for efficient upsert based on
  unique_together constraint (loan_number, investor_id, date).
- Type conversion is applied for ints/decimals/dates/booleans per field definitions.
- Each batch is processed in a transaction for atomicity.

DOCUMENTATION REVIEWED:
- Django custom commands: https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/
- Django bulk_create: https://docs.djangoproject.com/en/5.0/ref/models/querysets/#bulk-create
- Django update_conflicts: https://docs.djangoproject.com/en/5.0/ref/models/querysets/#django.db.models.query.QuerySet.bulk_create
"""
from __future__ import annotations

import csv
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any, Tuple, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# WHAT: Always import models at module top for performance and clarity.
# WHY: Avoids repeated import overhead and makes dependencies explicit.
from am_module.models.statebridgeservicing import SBDailyLoanData


# ------------------
# Helper converters
# ------------------

def _blank(val: Optional[str]) -> bool:
    """Return True when value is None or only whitespace.
    
    WHAT: Centralized blank-check to avoid repeated None/empty logic.
    WHY: Consistent null handling across all field conversions.
    """
    return val is None or str(val).strip() == ""


def _to_int(val: Optional[str]) -> Optional[int]:
    """Parse integer or return None if blank/invalid.
    
    WHAT: Convert string to integer (FAULT-TOLERANT for raw data).
    WHY: CSV integers may have commas, decimals, or invalid data.
    HOW: Strip non-digits, parse, return None on any error.
    """
    if _blank(val):
        return None
    try:
        # WHAT: Remove commas, whitespace, handle decimals before parsing.
        clean = str(val).strip().replace(",", "").replace("$", "")
        return int(float(clean))  # float() handles "123.0" -> 123
    except (ValueError, TypeError, OverflowError):
        return None  # WHAT: Silently skip bad data in raw imports


def _to_dec(val: Optional[str]) -> Optional[Decimal]:
    """Parse decimal or return None if blank/invalid.
    
    WHAT: Convert string to Decimal for financial values (FAULT-TOLERANT for raw data).
    WHY: Float loses precision; Decimal is required for money.
    HOW: Strip formatting, parse, return None on any error.
    DOCS: https://docs.python.org/3/library/decimal.html
    """
    if _blank(val):
        return None
    try:
        # WHAT: Remove dollar signs, commas, percent signs, parentheses (negative).
        clean = str(val).strip().replace(",", "").replace("$", "").replace("%", "").replace("(", "-").replace(")", "")
        if clean.lower() in ('n/a', 'na', 'null', 'none', ''):
            return None
        return Decimal(clean)
    except (InvalidOperation, ValueError, TypeError, OverflowError):
        return None  # WHAT: Silently skip bad data in raw imports


def _to_date(val: Optional[str]) -> Optional[date]:
    """Parse date string using common formats or return None.
    
    WHAT: Convert string to date object (FAULT-TOLERANT for raw data).
    WHY: Different systems export dates in various formats, may have invalid dates.
    HOW: Try multiple format strings, return None on any error.
    DOCS: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """
    if _blank(val):
        return None
    try:
        s = str(val).strip()
        if s.lower() in ('n/a', 'na', 'null', 'none', '0', '0/0/0000', '00/00/0000'):
            return None
        # WHAT: Try common date formats (MM/DD/YYYY, YYYY-MM-DD, etc.).
        for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%d/%m/%Y", "%Y/%m/%d", "%m/%d/%y", "%Y%m%d"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
    except (ValueError, TypeError, OverflowError):
        pass
    return None  # WHAT: Silently skip bad data in raw imports


def _to_bool(val: Optional[str]) -> Optional[bool]:
    """Parse truthy/falsey tokens. Returns None if blank.
    
    WHAT: Normalize boolean values from CSV strings (FAULT-TOLERANT for raw data).
    WHY: CSV exports may use "Yes/No", "True/False", "1/0", "0.00", or invalid values.
    HOW: Lowercase and match against known truthy/falsey tokens, return None on errors.
    """
    if _blank(val):
        return None
    try:
        token = str(val).strip().lower()
        if token in ('n/a', 'na', 'null', 'none'):
            return None
        # WHAT: Handle numeric strings like "0.00", "1.00"
        try:
            num_val = float(token.replace(",", ""))
            return num_val != 0.0  # 0 or 0.00 = False, anything else = True
        except ValueError:
            pass
        # WHAT: Handle text boolean values
        if token in ("true", "t", "yes", "y", "1"):
            return True
        if token in ("false", "f", "no", "n", "0"):
            return False
    except (ValueError, TypeError, AttributeError):
        pass
    return None  # WHAT: Silently skip bad data in raw imports


def _to_str(val: Optional[str]) -> Optional[str]:
    """Convert to stripped string or None if blank.
    
    WHAT: Normalize string values (FAULT-TOLERANT for raw data).
    WHY: CSV may have extra whitespace, null markers, or encoding issues.
    HOW: Strip whitespace, convert "N/A" to None, handle any data type.
    """
    if _blank(val):
        return None
    try:
        s = str(val).strip()
        if s.upper() in ("N/A", "NA", "NULL", "NONE", ""):
            return None
        return s
    except (ValueError, TypeError, AttributeError):
        return None  # WHAT: Silently skip bad data in raw imports


class Command(BaseCommand):
    """Import StateBridge daily loan data from CSV with upsert support.

    ARGUMENTS:
    - --file <path>: Path to CSV with StateBridge daily export format.
    - --batch-size <int>: Number of rows to process per bulk insert (default: 1000).
    - --dry-run: Validate and report only; no DB writes.

    USAGE:
        python manage.py import_statebridge_csv --file data/statebridge_2025_01_15.csv
        python manage.py import_statebridge_csv --file data/statebridge_2025_01_15.csv --batch-size 500 --dry-run
    
    WHAT: Upsert daily StateBridge loan snapshots into SBDailyLoanData raw table.
    WHY: Preserve complete audit trail before ETL into cleaned ServicerLoanData model.
    HOW: Use Django bulk_create with update_conflicts on unique_together (loan_number, investor_id, date).
    """

    help = "Import StateBridge daily loan data from CSV (upsert on loan_number+investor_id+date)."

    def add_arguments(self, parser):
        """Define command-line arguments.
        
        WHAT: Register --file, --batch-size, --dry-run flags.
        WHY: Provide flexible import control for different scenarios.
        """
        parser.add_argument(
            "--file",
            dest="file_path",
            required=True,
            help="Path to StateBridge CSV file",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of rows per bulk insert (default: 1000)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate only (no DB writes).",
        )
        parser.add_argument(
            "--purge",
            action="store_true",
            help="Delete all existing records before import.",
        )

    def handle(self, *args, **opts):
        """Main entry point: read CSV, map fields, bulk upsert.
        
        WHAT: Orchestrate CSV parsing and database upsert.
        WHY: Single command interface for daily data loads.
        HOW: Read CSV → map to model fields → batch upsert with conflict handling.
        """
        file_path: str = opts.get("file_path")
        batch_size: int = opts.get("batch_size", 1000)
        dry_run: bool = bool(opts.get("dry_run"))
        purge: bool = bool(opts.get("purge"))
        
        # WHAT: Optionally purge existing data before import.
        # WHY: Useful for full refresh imports or testing.
        if purge and not dry_run:
            count = SBDailyLoanData.objects.count()
            SBDailyLoanData.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Purged {count} existing records"))

        # WHAT: Try multiple encodings to handle various CSV export formats.
        # WHY: Different systems use different encodings (UTF-8, Windows-1252, Latin-1).
        # HOW: Try encodings in order of likelihood, fallback gracefully.
        # DOCS: https://docs.python.org/3/library/codecs.html#encodings-and-unicode
        rows = None
        last_error = None
        encodings_to_try = ['utf-8-sig', 'utf-8', 'cp1252', 'latin-1', 'iso-8859-1']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, newline="", encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                self.stdout.write(self.style.SUCCESS(f"Successfully read CSV using {encoding} encoding"))
                break
            except UnicodeDecodeError as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                break
        
        if rows is None:
            raise CommandError(f"Failed to read CSV '{file_path}' with any encoding. Last error: {last_error}")

        if not rows:
            self.stdout.write(self.style.WARNING("CSV contains no data rows. Exiting."))
            return

        # WHAT: CSV headers mapped to model fields (RAW DATA - all stored as strings)
        # WHY: SBDailyLoanData is a raw landing table with CharField for all fields.
        # HOW: Use _to_str for everything, defer type validation to ETL → ServicerLoanData.
        FIELD_MAP: Dict[str, Tuple[str, callable]] = {
            "Date": ("date", _to_str),
            "Investor ID": ("investor_id", _to_str),
            "Loan Number": ("loan_number", _to_str),
            "AVM Appraisal Date": ("avm_appraisal_date", _to_str),
            "AVM Appraisal Type": ("avm_appraisal_type", _to_str),
            "AVM Appraisal Value": ("avm_appraisal_value", _to_str),
            "Borrower First Name": ("borrower_first_name", _to_str),
            "Borrower Last Name": ("borrower_last_name", _to_str),
            "BPO As Is Value": ("bpo_as_is_value", _to_str),
            "BPO Date": ("bpo_date", _to_str),
            "BPO Repaired Value": ("bpo_repaired_value", _to_str),
            "Corporate Advance Balance": ("corporate_advance_balance", _to_str),
            "Current FICO Date": ("current_fico_date", _to_str),
            "Current FICO": ("current_fico", _to_str),
            "Current Interest Rate": ("current_interest_rate", _to_str),
            "Current Principal and Interest Payment": ("current_principal_and_interest_payment", _to_str),
            "Current Taxes and Insurance Payment": ("current_taxes_and_insurance_payment", _to_str),
            "Current UPB": ("current_upb", _to_str),
            "Date Last Payment Received": ("date_last_payment_received", _to_str),
            "Due Date": ("due_date", _to_str),
            "Escrow Advance Balance": ("escrow_advance_balance", _to_str),
            "Escrow Balance": ("escrow_balance", _to_str),
            "Investor Loan Number": ("investor_loan_number", _to_str),
            "Is ARM": ("is_arm", _to_str),
            "Is Escrowed": ("is_escrowed", _to_str),
            "Lien Position": ("lien_position", _to_str),
            "Loan Status": ("loan_status", _to_str),
            "Loan Type": ("loan_type", _to_str),
            "Loan Warning": ("loan_warning", _to_str),
            "MBA": ("mba", _to_str),
            "Occupancy Status": ("occupancy_status", _to_str),
            "Original Appraisal Date": ("original_appraisal_date", _to_str),
            "Original Appraisal Value": ("original_appraisal_value", _to_str),
            "Prior Servicer Loan Number": ("prior_servicer_loan_number", _to_str),
            "Property State": ("property_state", _to_str),
            "Property Zip": ("property_zip", _to_str),
            "Restricted Escrow": ("restricted_escrow", _to_str),
            "Active BK Plan": ("active_bk_plan", _to_str),
            "Bankruptcy Business Area Status Date": ("bankruptcy_business_area_status_date", _to_str),
            "Bankruptcy Business Area Status": ("bankruptcy_business_area_status", _to_str),
            "BK Case Number": ("bk_case_number", _to_str),
            "BK Chapter": ("bk_chapter", _to_str),
            "BK Court District": ("bk_court_district", _to_str),
            "BK Discharge Date": ("bk_discharge_date", _to_str),
            "BK Dismissed Date": ("bk_dismissed_date", _to_str),
            "BK Filed Date": ("bk_filed_date", _to_str),
            "BK Plan End Date": ("bk_plan_end_date", _to_str),
            "BK Plan Length": ("bk_plan_length", _to_str),
            "BK Plan Start Date": ("bk_plan_start_date", _to_str),
            "BK Post Petition Due Date": ("bk_post_petition_due_date", _to_str),
            "Date Motion for Relief Filed": ("date_motion_for_relief_filed", _to_str),
            "Date Object to Confirmation Filed": ("date_object_to_confirmation_filed", _to_str),
            "Date of Meeting of Creditors": ("date_of_meeting_of_creditors", _to_str),
            "Date Proof of Claim Filed": ("date_proof_of_claim_filed", _to_str),
            "Relief Date": ("relief_date", _to_str),
            "Actual FC Sale Date": ("actual_fc_sale_date", _to_str),
            "Date Referred to FC Atty": ("date_referred_to_fc_atty", _to_str),
            "FC Completion Date": ("fc_completion_date", _to_str),
            "FC Status": ("fc_status", _to_str),
            "Foreclosure Business Area Status Date": ("foreclosure_business_area_status_date", _to_str),
            "Foreclosure Business Area Status": ("foreclosure_business_area_status", _to_str),
            "Is a Contested FC": ("is_a_contested_fc", _to_str),
            "Reason for Default": ("reason_for_default", _to_str),
            "Scheduled FC Sale Date": ("scheduled_fc_sale_date", _to_str),
            "Date Breach Letter Sent": ("date_breach_letter_sent", _to_str),
            "DIL Completion Date": ("dil_completion_date", _to_str),
            "Loss Mitigation Business Area Status Date": ("loss_mitigation_business_area_status_date", _to_str),
            "Loss Mitigation Business Area Status": ("loss_mitigation_business_area_status", _to_str),
            "Loss Mitigation Start Date": ("loss_mitigation_start_date", _to_str),
            "Loss Mitigation Status": ("loss_mitigation_status", _to_str),
            "Workout Option": ("workout_option", _to_str),
            "Convert to Fixed Rate": ("convert_to_fixed_rate", _to_str),
            "Loan Modification Date": ("loan_modification_date", _to_str),
            "Loan Modification Status": ("loan_modification_status", _to_str),
            "Number of Payments": ("number_of_payments", _to_str),
            "Post Modification Principal Balance": ("post_modification_principal_balance", _to_str),
            "Repayment Plan Agreement Date": ("repayment_plan_agreement_date", _to_str),
            "Repayment Plan Start Date": ("repayment_plan_start_date", _to_str),
            "Repayment Plan Status": ("repayment_plan_status", _to_str),
            "Date Inspection Completed": ("date_inspection_completed", _to_str),
            "Deferred Advance Balance": ("deferred_advance_balance", _to_str),
            "First Time Vacant Date": ("first_time_vacant_date", _to_str),
            "Follow Up Date": ("follow_up_date", _to_str),
            "Forceplaced Flood Insurance": ("forceplaced_flood_insurance", _to_str),
            "Forceplaced Hazard Insurance": ("forceplaced_hazard_insurance", _to_str),
            "Is House for Sale": ("is_house_for_sale", _to_str),
            "Last Contact Outcome": ("last_contact_outcome", _to_str),
            "Last Successful Contact Date": ("last_successful_contact_date", _to_str),
            "MI company name": ("mi_company_name", _to_str),
            "Neighborhood Condition": ("neighborhood_condition", _to_str),
            "Next ARM Rate Change Date": ("next_arm_rate_change_date", _to_str),
            "PIF Date": ("pif_date", _to_str),
            "PIF Quote Date": ("pif_quote_date", _to_str),
            "Post Modification Coupon": ("post_modification_coupon", _to_str),
            "Post Modification Payment": ("post_modification_payment", _to_str),
            "Pre Modification Balance": ("pre_modification_balance", _to_str),
            "Pre Modification Coupon": ("pre_modification_coupon", _to_str),
            "Pre Modification Payment": ("pre_modification_payment", _to_str),
            "Promise Amount": ("promise_amount", _to_str),
            "Promise Date": ("promise_date", _to_str),
            "Property Condition from Inspection": ("property_condition_from_inspection", _to_str),
            "Res Service Fee Paid": ("res_service_fee_paid", _to_str),
            "Resolution Corporate Advance Balance": ("resolution_corporate_advance_balance", _to_str),
            "Resolution Escrow Advance": ("resolution_escrow_advance", _to_str),
            "Resolution Fees": ("resolution_fees", _to_str),
            "Resolution Post Date": ("resolution_post_date", _to_str),
            "Resolution Proceeds": ("resolution_proceeds", _to_str),
            "Resolution Type": ("resolution_type", _to_str),
            "Resolution Balance": ("resolution_balance", _to_str),
            "ss complete": ("ss_complete", _to_str),
            "ss proceeds rcvd": ("ss_proceeds_rcvd", _to_str),
            "Acquired Date": ("acquired_date", _to_str),
            "Inactive Date": ("inactive_date", _to_str),
            "Prim Stat": ("prim_stat", _to_str),
            "NOIExpiration Date": ("noi_expiration_date", _to_str),
            "Forgive Amount": ("forgive_amount", _to_str),
            "Balance After Forgive": ("balance_after_forgive", _to_str),
            "BK Case Closed Date": ("bk_case_closed_date", _to_str),
            "Max Rate": ("max_rate", _to_str),
            "Min Rate": ("min_rate", _to_str),
            "First Periodic Rate Cap": ("first_periodic_rate_cap", _to_str),
            "Periodic Rate Cap": ("periodic_rate_cap", _to_str),
            "Life Cap": ("life_cap", _to_str),
            "Acquisition Or Sale Identifier": ("acquisition_or_sale_identifier", _to_str),
            "Total Principal": ("total_principal", _to_str),
            "Total Interest": ("total_interest", _to_str),
            "Borrower Home Phone": ("borrower_home_phone", _to_str),
            "Days in Foreclosure": ("days_in_foreclosure", _to_str),
            "Non Recoverable Principal": ("non_recoverable_principal", _to_str),
            "Non Recoverable Interest": ("non_recoverable_interest", _to_str),
            "Non Recoverable Escrow": ("non_recoverable_escrow", _to_str),
            "Non Recoverable Fees": ("non_recoverable_fees", _to_str),
            "Non Recoverable Corporate Advance": ("non_recoverable_corporate_advance", _to_str),
            "Property Address": ("property_address", _to_str),
            "Property City": ("property_city", _to_str),
            "Arm Audit Status": ("arm_audit_status", _to_str),
            "Arm First Rate Change Date": ("arm_first_rate_change_date", _to_str),
            "Borrower Count": ("borrower_count", _to_str),
            "Asset Manager": ("asset_manager", _to_str),
            "Co Borrower FICO": ("co_borrower_fico", _to_str),
            "Co Borrower FICO Date": ("co_borrower_fico_date", _to_str),
            "Collateral Count": ("collateral_count", _to_str),
            "Current Loan Term": ("current_loan_term", _to_str),
            "Current Neg Am Bal": ("current_neg_am_bal", _to_str),
            "Deferred Interest": ("deferred_interest", _to_str),
            "Deferred Principal": ("deferred_principal", _to_str),
            "First Due Date": ("first_due_date", _to_str),
            "Interest Method": ("interest_method", _to_str),
            "IsPayOptionARM": ("is_pay_option_arm", _to_str),
            "Last Escrow Analysis Date": ("last_escrow_analysis_date", _to_str),
            "Legal Status": ("legal_status", _to_str),
            "Loan Age": ("loan_age", _to_str),
            "Maturity Date": ("maturity_date", _to_str),
            "MERSNum": ("mers_num", _to_str),
            "MI Active Policy": ("mi_active_policy", _to_str),
            "MI Certificate Number": ("mi_certificate_number", _to_str),
            "MI Claim": ("mi_claim", _to_str),
            "MI Claim Status": ("mi_claim_status", _to_str),
            "MI Coverage": ("mi_coverage", _to_str),
            "MI Date Closed": ("mi_date_closed", _to_str),
            "MI Date Paid": ("mi_date_paid", _to_str),
            "MI Last Review Date": ("mi_last_review_date", _to_str),
            "MI Paid Amount": ("mi_paid_amount", _to_str),
            "MI Rescind Date": ("mi_rescind_date", _to_str),
            "MI Rescind Reason": ("mi_rescind_reason", _to_str),
            "Mod Extended Maturity": ("mod_extended_maturity", _to_str),
            "Mod Forbearance": ("mod_forbearance", _to_str),
            "Mod Forgiven": ("mod_forgiven", _to_str),
            "Modification Type": ("modification_type", _to_str),
            "Modified First Payment Date": ("modified_first_payment_date", _to_str),
            "Original First Payment Date": ("original_first_payment_date", _to_str),
            "Original Loan Term": ("original_loan_term", _to_str),
            "Original Maturity Date": ("original_maturity_date", _to_str),
            "Original Amt": ("original_amt", _to_str),
            "Origination Date": ("origination_date", _to_str),
            "Pay Option Negative Amort Factor": ("pay_option_negative_amort_factor", _to_str),
            "Prepetition Unapplied Bal": ("prepetition_unapplied_bal", _to_str),
            "Prior Deferred Principal": ("prior_deferred_principal", _to_str),
            "Property County": ("property_county", _to_str),
            "Remaining Term": ("remaining_term", _to_str),
            "Repay Plan Type": ("repay_plan_type", _to_str),
            "Servicing Specialist": ("servicing_specialist", _to_str),
            "Stipulation Unapplied Bal": ("stipulation_unapplied_bal", _to_str),
            "Total Capitalized By Mod": ("total_capitalized_by_mod", _to_str),
            "Trust ID": ("trust_id", _to_str),
            "Within Pay Option Period": ("within_pay_option_period", _to_str),
            "Balloon Date": ("balloon_date", _to_str),
            "Balloon Payment": ("balloon_payment", _to_str),
            "MI Claim Filed Date": ("mi_claim_filed_date", _to_str),
            "Loan Purpose": ("loan_purpose", _to_str),
            "Property Type": ("property_type", _to_str),
            "Single Point of Contact": ("single_point_of_contact", _to_str),
            "Right Party Type": ("right_party_type", _to_str),
            "Right Party Date": ("right_party_date", _to_str),
            "Non Recoverable Corp Adv Balance": ("non_recoverable_corp_adv_balance", _to_str),
            "Total Due": ("total_due", _to_str),
            "Principal Due": ("principal_due", _to_str),
            "Interest Due": ("interest_due", _to_str),
            "Escrow Due": ("escrow_due", _to_str),
            "Legal Fees": ("legal_fees", _to_str),
            "Other Fees": ("other_fees", _to_str),
            "NSF Fees": ("nsf_fees", _to_str),
            "Accrued Late Fees": ("accrued_late_fees", _to_str),
            "Unapplied Balance": ("unapplied_balance", _to_str),
        }


        # WHAT: Process CSV in batches for memory efficiency.
        # WHY: Large CSVs (100k+ rows) can overwhelm memory if processed at once.
        # HOW: Chunk rows into batch_size groups, upsert each batch separately.
        created_count = 0
        updated_count = 0
        error_count = 0

        for batch_start in range(0, len(rows), batch_size):
            batch = rows[batch_start:batch_start + batch_size]
            
            # WHAT: Build list of SBDailyLoanData instances from CSV batch.
            # WHY: bulk_create requires materialized model instances.
            # HOW: Map each CSV row through FIELD_MAP converters.
            instances: List[SBDailyLoanData] = []
            
            for idx, row in enumerate(batch, start=batch_start + 2):  # CSV header is line 1
                try:
                    # WHAT: Create instance with mapped field values.
                    # WHY: Each row becomes one SBDailyLoanData object.
                    kwargs = {}
                    for csv_col, (attr, conv) in FIELD_MAP.items():
                        if csv_col in row:
                            kwargs[attr] = conv(row[csv_col])
                    
                    instances.append(SBDailyLoanData(**kwargs))
                    
                except Exception as e:
                    error_count += 1
                    self.stderr.write(self.style.ERROR(f"Row {idx} parse error: {e}"))
            
            if not instances:
                continue
            
            if dry_run:
                # WHAT: Count what would be created without DB writes.
                # WHY: Validate CSV structure before committing.
                created_count += len(instances)
                self.stdout.write(f"Dry-run batch: would process {len(instances)} rows")
                continue
            
            # WHAT: Bulk upsert using Django's bulk_create with update_conflicts.
            # WHY: Efficient upsert pattern for large datasets (reviewed: https://docs.djangoproject.com/en/5.0/ref/models/querysets/#bulk-create).
            # HOW: unique_together (loan_number, investor_id, date) triggers update on conflict.
            try:
                with transaction.atomic():
                    result = SBDailyLoanData.objects.bulk_create(
                        instances,
                        update_conflicts=True,
                        update_fields=[attr for csv_col, (attr, conv) in FIELD_MAP.items() if attr not in ('loan_number', 'investor_id', 'date')],  # All fields except unique constraint
                        unique_fields=['loan_number', 'investor_id', 'date'],
                    )
                    # WHAT: Django doesn't return created vs updated counts, so estimate.
                    # WHY: Provide user feedback on operation results.
                    created_count += len(result)
                    
                    self.stdout.write(f"Processed batch: {len(instances)} rows")
                    
            except Exception as e:
                error_count += len(instances)
                self.stderr.write(self.style.ERROR(f"Batch insert failed: {e}"))

        # WHAT: Final summary of import operation.
        # WHY: Clear feedback on what was accomplished.
        self.stdout.write(self.style.SUCCESS(
            f"Import complete: processed={created_count}, errors={error_count}, dry_run={dry_run}"
        ))
