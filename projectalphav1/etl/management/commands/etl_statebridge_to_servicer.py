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

from etl.models import (
    SBDailyArmData,
    SBDailyBankruptcyData,
    SBDailyCommentData,
    SBDailyForeclosureData,
    SBDailyLoanData,
    SBDailyPayHistoryData,
    SBDailyTransactionData,
)
from am_module.models.model_am_servicersCleaned import (
    ServicerArmData,
    ServicerBankruptcyData,
    ServicerCommentData,
    ServicerForeclosureData,
    ServicerLoanData,
    ServicerPayHistoryData,
    ServicerTransactionData,
)
from core.models import AssetIdHub

logger = logging.getLogger(__name__)


NULL_LIKE_VALUES = {
    'na',
    'na.',
    'n/a',
    'n/a.',
    'n\\a',
    'null',
    'none',
    'nan',
    '-',
    '--',
    '---',
    '–',
    '—',
    '−',
    '‑',
    '0000-00-00',
    '00/00/0000',
}


class Command(BaseCommand):
    help = 'ETL: Transform SBDailyLoanData -> ServicerLoanData'

    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str, help='Process specific date (YYYY-MM-DD or MM/DD/YYYY)')
        parser.add_argument(
            '--kind',
            action='append',
            choices=[
                'loan',
                'arm',
                'foreclosure',
                'bankruptcy',
                'comment',
                'pay_history',
                'transaction',
            ],
            help='Which dataset(s) to ETL. Repeatable. Defaults to loan only.',
        )
        parser.add_argument('--dry-run', action='store_true', help='Test mode, no DB writes')
        parser.add_argument('--batch-size', type=int, default=100, help='Records per batch (default: 100)')
        parser.add_argument('--max-records', type=int, default=None, help='Limit total records processed (testing)')

    def handle(self, *args, **options):
        """Main ETL execution."""
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        max_records = options.get('max_records')
        date_filter = options.get('date')
        kinds = options.get('kind') or ['loan']
        
        self.stdout.write(
            self.style.SUCCESS(
                f"{'[DRY RUN] ' if dry_run else ''}Starting ETL: StateBridge -> Servicer (kinds={','.join(kinds)})"
            )
        )

        for kind in kinds:
            self._run_kind(
                kind=kind,
                date_filter=date_filter,
                dry_run=dry_run,
                batch_size=batch_size,
                max_records=max_records,
            )

    def _run_kind(
        self,
        *,
        kind: str,
        date_filter: Optional[str],
        dry_run: bool,
        batch_size: int,
        max_records: Optional[int],
    ) -> None:
        if kind == 'loan':
            queryset = SBDailyLoanData.objects.all()
            if date_filter:
                queryset = queryset.filter(date=date_filter)
            processor = lambda raw: self._process_loan_record(raw=raw, dry_run=dry_run)
        else:
            config = self._get_kind_config(kind)
            queryset = config['raw_model'].objects.all()
            if date_filter:
                queryset = queryset.filter(file_date=date_filter)
            processor = lambda raw: self._process_generic_record(raw=raw, dry_run=dry_run, **config)

        if max_records is not None and max_records > 0:
            queryset = queryset.order_by('id')[:max_records]

        total = queryset.count()
        if total == 0:
            self.stdout.write(self.style.WARNING(f"No records to process for kind={kind}"))
            return

        if date_filter:
            self.stdout.write(f"Filtering for date: {date_filter} (kind={kind})")
        self.stdout.write(f"Found {total} raw records (kind={kind})")

        stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'skipped_no_asset': 0,
            'skipped_invalid': 0,
            'errors': 0,
        }

        for i in range(0, total, batch_size):
            batch = queryset[i : i + batch_size]
            self.stdout.write(
                f"Batch {i // batch_size + 1}: records {i + 1}-{min(i + batch_size, total)} (kind={kind})"
            )
            for raw in batch:
                try:
                    result = processor(raw)
                    stats[result] += 1
                    stats['processed'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    logger.error(f"Error processing kind={kind}: {e}")
                    self.stdout.write(self.style.ERROR(f"  ERROR: kind={kind} - {e}"))

        self.stdout.write(self.style.SUCCESS(f"\n=== ETL Complete (kind={kind}) ==="))
        self.stdout.write(f"Processed:          {stats['processed']}")
        self.stdout.write(f"Created:            {stats['created']}")
        self.stdout.write(f"Updated:            {stats['updated']}")
        self.stdout.write(f"Skipped (no asset): {stats['skipped_no_asset']}")
        self.stdout.write(f"Skipped (invalid):  {stats['skipped_invalid']}")
        self.stdout.write(f"Errors:             {stats['errors']}")

    def _get_kind_config(self, kind: str) -> dict:
        if kind == 'arm':
            return {
                'raw_model': SBDailyArmData,
                'target_model': ServicerArmData,
                'key_fields': ['file_date', 'loan_id'],
                'asset_id_fields': ['loan_number', 'loan_id'],
            }
        if kind == 'foreclosure':
            return {
                'raw_model': SBDailyForeclosureData,
                'target_model': ServicerForeclosureData,
                'key_fields': ['file_date', 'loan_id'],
                'asset_id_fields': ['loan_id'],
            }
        if kind == 'bankruptcy':
            return {
                'raw_model': SBDailyBankruptcyData,
                'target_model': ServicerBankruptcyData,
                'key_fields': ['file_date', 'loan_id', 'case_number'],
                'asset_id_fields': ['loan_id'],
            }
        if kind == 'comment':
            return {
                'raw_model': SBDailyCommentData,
                'target_model': ServicerCommentData,
                'key_fields': ['file_date', 'loan_number', 'comment_date', 'department', 'row_hash'],
                'asset_id_fields': ['loan_number'],
            }
        if kind == 'pay_history':
            return {
                'raw_model': SBDailyPayHistoryData,
                'target_model': ServicerPayHistoryData,
                'key_fields': ['file_date', 'loan_number'],
                'asset_id_fields': ['loan_number'],
            }
        if kind == 'transaction':
            return {
                'raw_model': SBDailyTransactionData,
                'target_model': ServicerTransactionData,
                'key_fields': ['file_date', 'loan_transaction_id'],
                'asset_id_fields': ['loan_id'],
            }
        raise ValueError(f"Unknown kind: {kind}")

    def _process_loan_record(self, *, raw: SBDailyLoanData, dry_run: bool) -> str:

        normalized_servicer_id = self._normalize_servicer_id(raw.loan_number)
        if not normalized_servicer_id:
            return 'skipped_invalid'

        rep_year, rep_month, rep_day, as_of = self._parse_date(raw.date)
        if rep_year is None or rep_month is None:
            return 'skipped_invalid'

        asset_hub = AssetIdHub.objects.filter(servicer_id=normalized_servicer_id).first()

        cleaned_data = self._map_fields(
            raw,
            asset_hub,
            normalized_servicer_id,
            rep_year,
            rep_month,
            rep_day,
            as_of,
        )
        cleaned_data['asset_hub'] = asset_hub

        if dry_run:
            return 'created'

        if asset_hub is not None:
            existing = (
                ServicerLoanData.objects.filter(
                    asset_hub=asset_hub,
                    reporting_year=rep_year,
                    reporting_month=rep_month,
                )
                .order_by('id')
                .first()
            )
            if existing is not None:
                for k, v in cleaned_data.items():
                    setattr(existing, k, v)
                existing.save()
                return 'updated'

            orphan = (
                ServicerLoanData.objects.filter(
                    servicer_id=normalized_servicer_id,
                    reporting_year=rep_year,
                    reporting_month=rep_month,
                    asset_hub__isnull=True,
                )
                .order_by('id')
                .first()
            )
            if orphan is not None:
                for k, v in cleaned_data.items():
                    setattr(orphan, k, v)
                orphan.save()
                return 'updated'

            ServicerLoanData.objects.create(
                reporting_year=rep_year,
                reporting_month=rep_month,
                **cleaned_data,
            )
            return 'created'

        try:
            _, created = ServicerLoanData.objects.update_or_create(
                servicer_id=normalized_servicer_id,
                reporting_year=rep_year,
                reporting_month=rep_month,
                defaults=cleaned_data,
            )
        except ServicerLoanData.MultipleObjectsReturned:
            obj = (
                ServicerLoanData.objects.filter(
                    servicer_id=normalized_servicer_id,
                    reporting_year=rep_year,
                    reporting_month=rep_month,
                )
                .order_by('id')
                .first()
            )
            if obj is None:
                raise
            for k, v in cleaned_data.items():
                setattr(obj, k, v)
            obj.save()
            created = False

        return 'created' if created else 'updated'

    def _process_generic_record(
        self,
        *,
        raw,
        dry_run: bool,
        raw_model,
        target_model,
        key_fields: list[str],
        asset_id_fields: list[str],
    ) -> str:
        target_fields_by_name = {f.name: f for f in target_model._meta.fields}

        asset_hub = self._find_asset_hub(raw=raw, asset_id_fields=asset_id_fields)

        defaults: dict = {
            'asset_hub': asset_hub,
            'raw_source_snapshot': raw,
        }

        for f in raw_model._meta.fields:
            if f.name in {'id', 'created_at', 'updated_at'}:
                continue
            target_field = target_fields_by_name.get(f.name)
            if target_field is None:
                continue
            
            raw_value = getattr(raw, f.name, None)
            
            # Clean loan_number fields by stripping leading zeros
            if f.name == 'loan_number' and raw_value is not None:
                raw_value = self._normalize_servicer_id(raw_value)
            
            defaults[f.name] = self._coerce_for_field(
                raw_value,
                target_field=target_field,
                field_name=f.name,
            )

        lookup = {k: defaults.get(k) for k in key_fields}
        if any(v is None or (isinstance(v, str) and v.strip() == '') for v in lookup.values()):
            return 'skipped_invalid'

        if dry_run:
            return 'created'

        try:
            _, created = target_model.objects.update_or_create(**lookup, defaults=defaults)
        except target_model.MultipleObjectsReturned:
            obj = target_model.objects.filter(**lookup).order_by('id').first()
            if obj is None:
                raise
            for k, v in defaults.items():
                setattr(obj, k, v)
            obj.save()
            created = False

        return 'created' if created else 'updated'

    def _find_asset_hub(self, *, raw, asset_id_fields: list[str]) -> Optional[AssetIdHub]:
        for field_name in asset_id_fields:
            raw_val = getattr(raw, field_name, None)
            normalized = self._normalize_servicer_id(raw_val)
            if not normalized:
                continue
            asset_hub = AssetIdHub.objects.filter(servicer_id=normalized).first()
            if asset_hub:
                return asset_hub
        return None

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
        if date_str is None or not isinstance(date_str, str):
            return (None, None, None, None)

        cleaned = self._clean(date_str)
        if cleaned is None:
            return (None, None, None, None)

        date_str = cleaned
        
        # Try multiple date formats
        formats = [
            '%m/%d/%Y',
            '%Y-%m-%d',
            '%m-%d-%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S.%f',
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return (dt.year, dt.month, dt.day, dt.date())
            except ValueError:
                continue

        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return (dt.year, dt.month, dt.day, dt.date())
        except ValueError:
            pass

        if ' ' in date_str:
            maybe_date = date_str.split(' ')[0]
            if maybe_date and maybe_date != date_str:
                return self._parse_date(maybe_date)
        
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
        value = self._clean(value)
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, AttributeError):
            return None

    def _to_dec(self, value: str) -> Optional[Decimal]:
        """Convert string to Decimal, removing $ and commas."""
        value = self._clean(value)
        if value is None:
            return None
        try:
            clean = self._normalize_numeric_string(value)
            return Decimal(clean)
        except (ValueError, InvalidOperation, AttributeError):
            return None

    def _to_bool(self, value: str) -> Optional[bool]:
        """Convert string to boolean."""
        value = self._clean(value)
        if value is None:
            return None
        value = value.lower()
        if value in ('1', 'true', 'yes', 'y', 't'):
            return True
        elif value in ('0', 'false', 'no', 'n', 'f'):
            return False
        return None

    def _clean(self, value: str) -> Optional[str]:
        """Clean string value."""
        if value is None or not isinstance(value, str):
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        lowered = cleaned.lower()
        if lowered in NULL_LIKE_VALUES:
            return None
        return cleaned

    def _normalize_numeric_string(self, value: str) -> str:
        s = value.strip()
        if s.startswith('(') and s.endswith(')'):
            s = '-' + s[1:-1]
        s = s.replace('$', '').replace(',', '')
        if s.endswith('%'):
            s = s[:-1]
        return s.strip()

    def _looks_like_numeric_string(self, value: str) -> bool:
        if value is None:
            return False
        s = value.strip()
        if not s:
            return False
        return re.match(r'^[\d\s\$\,\.\(\)\-\+%]+$', s) is not None

    def _looks_like_date_field(self, field_name: str) -> bool:
        name = field_name.lower()
        return (
            name.endswith('_date')
            or name.endswith('_dt')
            or name in {'file_date', 'date'}
            or 'date' in name
        )

    def _strip_time_from_date_string(self, value: str) -> str:
        s = value.strip()
        if 'T' in s:
            s = s.split('T', 1)[0]
        if ' ' in s:
            s = s.split(' ', 1)[0]
        return s.strip()

    def _coerce_for_field(self, raw_value, *, target_field, field_name: str):
        internal_type = target_field.get_internal_type()

        if raw_value is None:
            return None

        if internal_type in {'DateField', 'DateTimeField'}:
            _, _, _, parsed = self._parse_date(str(raw_value))
            return parsed

        if internal_type in {'IntegerField', 'SmallIntegerField', 'BigIntegerField', 'PositiveIntegerField', 'PositiveSmallIntegerField'}:
            return self._to_int(str(raw_value))

        if internal_type == 'DecimalField':
            return self._to_dec(str(raw_value))

        if internal_type == 'BooleanField':
            return self._to_bool(str(raw_value))

        if internal_type in {'CharField', 'TextField'}:
            cleaned = self._clean(str(raw_value))
            if cleaned is None:
                return None
            if self._looks_like_date_field(field_name):
                return self._strip_time_from_date_string(cleaned)

            if self._looks_like_numeric_string(cleaned):
                numeric_candidate = self._normalize_numeric_string(cleaned)
                cleaned_numeric = self._clean(numeric_candidate)
                return cleaned_numeric

            return cleaned

        cleaned = self._clean(str(raw_value))
        return cleaned

    def _normalize_servicer_id(self, loan_number: Optional[str]) -> Optional[str]:
        if loan_number is None:
            return None
        normalized = self._clean(str(loan_number))
        if normalized is None:
            return None
        trimmed = normalized.lstrip('0')
        return trimmed if trimmed else '0'
