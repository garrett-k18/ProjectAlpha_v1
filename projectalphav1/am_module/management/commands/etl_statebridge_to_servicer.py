"""
ETL: Transform raw StateBridge data (SBDailyLoanData) → clean ServicerLoanData.

Data Flow: SBDailyLoanData (raw strings) → ETL → ServicerLoanData (typed fields)

Usage:
    python manage.py etl_statebridge_to_servicer [--date YYYY-MM-DD] [--dry-run]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Optional, Tuple
import inspect
import logging
import re

from etl.models import SBDailyLoanData
from am_module.models.servicers import ServicerLoanData
from core.models import AssetIdHub

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'ETL: Transform SBDailyLoanData → ServicerLoanData'

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str, help='Process specific date (YYYY-MM-DD or MM/DD/YYYY)')
        parser.add_argument('--dry-run', action='store_true', help='Test mode, no DB writes')
        parser.add_argument('--batch-size', type=int, default=100, help='Records per batch (default: 100)')

    def handle(self, *args, **options):
        """Main ETL execution."""
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        date_filter = options.get('date')
        
        self.stdout.write(self.style.SUCCESS(
            f"{'[DRY RUN] ' if dry_run else ''}Starting ETL: StateBridge → ServicerLoanData"
        ))
        
        # Build queryset
        queryset = SBDailyLoanData.objects.all()
        if date_filter:
            queryset = queryset.filter(date=date_filter)
            self.stdout.write(f"Filtering for date: {date_filter}")
        
        total = queryset.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No records to process"))
            return
        
        self.stdout.write(f"Found {total} raw records")
        
        # Statistics tracking
        stats = {'processed': 0, 'created': 0, 'updated': 0, 
                'skipped_no_asset': 0, 'skipped_invalid': 0, 'errors': 0}
        
        # Process in batches
        for i in range(0, total, batch_size):
            batch = queryset[i:i + batch_size]
            self.stdout.write(f"Batch {i // batch_size + 1}: records {i + 1}-{min(i + batch_size, total)}")
            
            for raw in batch:
                try:
                    result = self._process_record(raw, dry_run)
                    stats[result] += 1
                    stats['processed'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    logger.error(f"Error processing loan {raw.loan_number}: {e}")
                    self.stdout.write(self.style.ERROR(f"  ERROR: {raw.loan_number} - {e}"))
        
        # Report results
        self.stdout.write(self.style.SUCCESS("\n=== ETL Complete ==="))
        self.stdout.write(f"Processed:          {stats['processed']}")
        self.stdout.write(f"Created:            {stats['created']}")
        self.stdout.write(f"Updated:            {stats['updated']}")
        self.stdout.write(f"Skipped (no asset): {stats['skipped_no_asset']}")
        self.stdout.write(f"Skipped (invalid):  {stats['skipped_invalid']}")
        self.stdout.write(f"Errors:             {stats['errors']}")

    def _process_record(self, raw: SBDailyLoanData, dry_run: bool) -> str:
        """Transform one raw record into ServicerLoanData."""
        
        # Normalize servicer identifier to align with AssetIdHub while preserving long IDs as text
        normalized_servicer_id = self._normalize_servicer_id(raw.loan_number)
        if not normalized_servicer_id:
            return 'skipped_invalid'

        # Lookup AssetIdHub by servicer_id
        asset_hub = AssetIdHub.objects.filter(servicer_id=normalized_servicer_id).first()
        if not asset_hub:
            logger.warning(f"No AssetIdHub for servicer_id={normalized_servicer_id}")
            return 'skipped_no_asset'
        
        # Parse reporting period
        rep_year, rep_month, rep_day, as_of = self._parse_date(raw.date)
        
        # Build cleaned data dictionary
        cleaned_data = self._map_fields(raw, asset_hub, normalized_servicer_id, 
                                        rep_year, rep_month, rep_day, as_of)
        
        if dry_run:
            return 'created'  # Simulated
        
        # Upsert: update if exists, create if new
        servicer_record, created = ServicerLoanData.objects.update_or_create(
            asset_hub=asset_hub,
            reporting_year=rep_year,
            reporting_month=rep_month,
            defaults=cleaned_data
        )
        
        return 'created' if created else 'updated'

    def _map_fields(self, raw, asset_hub, servicer_id_value, rep_year, rep_month, rep_day, as_of):
        """Map all fields from raw to clean model."""
        return {
            # Core relationships
            'raw_source_snapshot': raw,
            'reporting_day': rep_day,
            'as_of_date': as_of,
            
            # IDs
            'investor_id': self._clean(raw.investor_id),
            'servicer_id': servicer_id_value,
            'previous_servicer_id': self._clean(raw.prior_servicer_loan_number),  # TODO: Verify mapping
            
            # Property
            'address': self._clean(raw.property_address),
            'city': self._clean(raw.property_city),
            'state': self._clean(raw.property_state),
            'zip_code': self._clean(raw.property_zip),
            'property_type': self._clean(raw.property_type),
            
            # Valuation
            'avm_date': self._parse_date(raw.avm_appraisal_date)[3],
            'avm_value': self._to_dec(raw.avm_appraisal_value),
            'bpo_asis_value': self._to_dec(raw.bpo_as_is_value),
            'bpo_asis_date': self._parse_date(raw.bpo_date)[3],
            'bpo_arv_value': self._to_dec(raw.bpo_repaired_value),
            'original_appraised_value': self._to_dec(raw.original_appraisal_value),
            
            # Borrower
            'occupnacy': self._clean(raw.occupancy_status),
            'borrower_last_name': self._clean(raw.borrower_last_name),
            'borrower_first_name': self._clean(raw.borrower_first_name),
            'current_fico': self._to_int(raw.current_fico),
            'current_fico_date': self._parse_date(raw.current_fico_date)[3],
            
            # Balance
            'current_balance': self._to_dec(raw.current_upb),
            'current_pi': self._to_dec(raw.current_principal_and_interest_payment),
            'current_ti': self._to_dec(raw.current_taxes_and_insurance_payment),
            'piti': self._to_dec(raw.current_principal_and_interest_payment),
            'term_remaining': self._to_int(raw.remaining_term),
            'maturity_date': self._parse_date(raw.maturity_date)[3],
            
            # Escrow
            'escrow_balance': self._to_dec(raw.escrow_balance),
            'escrow_advance_balance': self._to_dec(raw.escrow_advance_balance),
            'escrowed_flag': self._to_bool(raw.is_escrowed),
            'last_escrow_analysis_date': self._parse_date(raw.last_escrow_analysis_date)[3],
            
            # Other balances - TODO: Verify these mappings
            'third_party_recov_balance': self._to_dec(raw.corporate_advance_balance),
            'suspense_balance': self._to_dec(raw.unapplied_balance),
            'servicer_late_fees': self._to_dec(raw.accrued_late_fees),
            'other_charges': self._to_dec(raw.other_fees),
            'interest_arrears': self._to_dec(raw.interest_due),
            
            # Loan characteristics
            'lien_pos': self._to_int(raw.lien_position),
            'arm_flag': self._to_bool(raw.is_arm),
            'loan_type': self._clean(raw.loan_type),
            'loan_warning': self._clean(raw.loan_warning),
            'mba': self._to_bool(raw.mba),
            'loan_purpose': self._clean(raw.loan_purpose),
            
            # Origination
            'origination_date': self._parse_date(raw.origination_date)[3],
            'origination_balance': self._to_dec(raw.original_amt),
            'original_first_payment_date': self._parse_date(raw.original_first_payment_date)[3],
            'original_loan_term': self._to_int(raw.original_loan_term),
            'original_maturity_date': self._parse_date(raw.original_maturity_date)[3],
            
            # Bankruptcy
            'bk_flag': self._to_bool(raw.active_bk_plan),
            'bk_current_status': self._clean(raw.bankruptcy_business_area_status),
            'bk_discharge_date': self._parse_date(raw.bk_discharge_date)[3],
            'bk_dismissed_date': self._parse_date(raw.bk_dismissed_date)[3],
            'bk_filed_date': self._parse_date(raw.bk_filed_date)[3],
            
            # Foreclosure
            'actual_fc_sale_date': self._parse_date(raw.actual_fc_sale_date)[3],
            'date_referred_to_fc_atty': self._parse_date(raw.date_referred_to_fc_atty)[3],
            'fc_completion_date': self._parse_date(raw.fc_completion_date)[3],
            'fc_status': self._clean(raw.fc_status),
            
            # Loss mitigation
            
            # Modification
            
            # Repayment
            
            # Property & inspection
            
            # Contact
            
            # ARM
            
            # MI
            
            # Resolution
            'pif_date': self._parse_date(raw.pif_date)[3],
            
            # Additional status
            'acquired_date': self._parse_date(raw.acquired_date)[3],
            'inactive_date': self._parse_date(raw.inactive_date)[3],
            'prim_stat': self._clean(raw.prim_stat),
            'noi_expiration_date': self._parse_date(raw.noi_expiration_date)[3],
            'total_principal': self._to_dec(raw.total_principal),
            'total_interest': self._to_dec(raw.total_interest),
            'non_recoverable_principal': self._to_dec(raw.non_recoverable_principal),
            'non_recoverable_interest': self._to_dec(raw.non_recoverable_interest),
            'non_recoverable_escrow': self._to_dec(raw.non_recoverable_escrow),
            'non_recoverable_fees': self._to_dec(raw.non_recoverable_fees),
            'non_recoverable_corporate_advance': self._to_dec(raw.non_recoverable_corporate_advance),
            'asset_manager': self._clean(raw.asset_manager),
            'collateral_count': self._to_int(raw.collateral_count),
            'current_loan_term': self._to_int(raw.current_loan_term),
            'current_neg_am_bal': self._to_dec(raw.current_neg_am_bal),
            'deferred_interest': self._to_dec(raw.deferred_interest),
            'interest_method': self._clean(raw.interest_method),
            'loan_age': self._to_int(raw.loan_age),
            'mers_num': self._clean(raw.mers_num),
            'servicing_specialist': self._clean(raw.servicing_specialist),
            'trust_id': self._clean(raw.trust_id),
            'balloon_date': self._parse_date(raw.balloon_date)[3],
            'balloon_payment': self._to_dec(raw.balloon_payment),
            'acquisition_or_sale_identifier': self._clean(raw.acquisition_or_sale_identifier),
        }

    # Helper functions for type conversion
    def _parse_date(self, date_str: str) -> Tuple[Optional[int], Optional[int], Optional[int], Optional[datetime]]:
        """Parse date string into (year, month, day, date_object). Returns (None, None, None, None) if invalid."""
        if not date_str or not isinstance(date_str, str):
            return (None, None, None, None)
        
        date_str = date_str.strip()
        if not date_str:
            return (None, None, None, None)
        
        # Try multiple date formats
        formats = ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d/%m/%Y']
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return (dt.year, dt.month, dt.day, dt.date())
            except ValueError:
                continue
        
        field_label = None
        frame = inspect.currentframe()
        caller = frame.f_back if frame else None
        try:
            if caller:
                info = inspect.getframeinfo(caller)
                context_line = info.code_context[0].strip() if info.code_context else None
                if context_line:
                    match = re.search(r"raw\.([a-zA-Z0-9_]+)", context_line)
                    if match:
                        field_label = match.group(1)
        finally:
            del frame
            del caller

        if field_label:
            logger.warning(f"Failed to parse date for {field_label}: {date_str}")
        else:
            logger.warning(f"Failed to parse date: {date_str}")
        return (None, None, None, None)

    def _to_int(self, value: str) -> Optional[int]:
        """Convert string to integer."""
        if not value or not isinstance(value, str):
            return None
        try:
            return int(value.strip())
        except (ValueError, AttributeError):
            return None

    def _to_dec(self, value: str) -> Optional[Decimal]:
        """Convert string to Decimal, removing $ and commas."""
        if not value or not isinstance(value, str):
            return None
        try:
            clean = value.strip().replace('$', '').replace(',', '')
            return Decimal(clean)
        except (ValueError, InvalidOperation, AttributeError):
            return None

    def _to_bool(self, value: str) -> Optional[bool]:
        """Convert string to boolean."""
        if not value or not isinstance(value, str):
            return None
        value = value.strip().lower()
        if value in ('1', 'true', 'yes', 'y', 't'):
            return True
        elif value in ('0', 'false', 'no', 'n', 'f'):
            return False
        return None

    def _clean(self, value: str) -> Optional[str]:
        """Clean string value."""
        if not value or not isinstance(value, str):
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None

    def _normalize_servicer_id(self, loan_number: Optional[str]) -> Optional[str]:
        if loan_number is None:
            return None
        normalized = str(loan_number).strip()
        if not normalized:
            return None
        trimmed = normalized.lstrip('0')
        return trimmed if trimmed else '0'
