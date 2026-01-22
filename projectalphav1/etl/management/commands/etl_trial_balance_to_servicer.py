"""
ETL: Transform raw StateBridge EOM trial balance data (EOMTrialBalanceData)
     -> cleaned ServicerTrialBalanceData (monthly snapshot).

Usage:
    python manage.py etl_trial_balance_to_servicer [--file-date YYYY-MM-DD] [--dry-run]
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple
import logging
import re

from django.core.management.base import BaseCommand
from django.db import transaction

from etl.models import EOMTrialBalanceData
from am_module.models import ServicerTrialBalanceData
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
    help = 'ETL: Transform EOMTrialBalanceData -> ServicerTrialBalanceData'

    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument('--file-date', type=str, help='Process specific file date (YYYY-MM-DD or MM/DD/YYYY)')
        parser.add_argument('--dry-run', action='store_true', help='Test mode, no DB writes')
        parser.add_argument('--batch-size', type=int, default=500, help='Records per batch (default: 500)')
        parser.add_argument('--max-records', type=int, default=None, help='Limit total records processed (testing)')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        max_records = options.get('max_records')
        file_date_filter = options.get('file_date')

        self.stdout.write(
            self.style.SUCCESS(
                f"{'[DRY RUN] ' if dry_run else ''}Starting ETL: Trial Balance -> ServicerTrialBalanceData"
            )
        )

        queryset = EOMTrialBalanceData.objects.all()
        if file_date_filter:
            queryset = queryset.filter(file_date=file_date_filter)

        if max_records is not None and max_records > 0:
            queryset = queryset.order_by('id')[:max_records]

        total = queryset.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No trial balance records to process"))
            return

        if file_date_filter:
            self.stdout.write(f"Filtering for file_date: {file_date_filter}")
        self.stdout.write(f"Found {total} raw trial balance records")

        stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'skipped_invalid': 0,
            'errors': 0,
        }

        for i in range(0, total, batch_size):
            batch = queryset[i : i + batch_size]
            self.stdout.write(
                f"Batch {i // batch_size + 1}: records {i + 1}-{min(i + batch_size, total)}"
            )
            for raw in batch:
                try:
                    result = self._process_trial_balance_record(raw=raw, dry_run=dry_run)
                    stats[result] += 1
                    stats['processed'] += 1
                except Exception as exc:
                    stats['errors'] += 1
                    logger.error("Error processing trial balance record %s: %s", raw.id, exc)
                    self.stdout.write(self.style.ERROR(f"  ERROR: id={raw.id} - {exc}"))

        self.stdout.write(self.style.SUCCESS("\n=== ETL Complete (trial_balance) ==="))
        self.stdout.write(f"Processed:          {stats['processed']}")
        self.stdout.write(f"Created:            {stats['created']}")
        self.stdout.write(f"Updated:            {stats['updated']}")
        self.stdout.write(f"Skipped (invalid):  {stats['skipped_invalid']}")
        self.stdout.write(f"Errors:             {stats['errors']}")

    def _process_trial_balance_record(self, *, raw: EOMTrialBalanceData, dry_run: bool) -> str:
        normalized_loan_id = self._normalize_servicer_id(raw.loan_id)
        file_date = self._parse_date(raw.file_date)[3]

        if not normalized_loan_id or not file_date:
            return 'skipped_invalid'

        asset_hub = AssetIdHub.objects.filter(servicer_id=normalized_loan_id).first()

        cleaned_data = {
            'asset_hub': asset_hub,
            'raw_source_snapshot': raw,
            'file_date': file_date,
            'loan_id': normalized_loan_id,
            'investor_id': self._clean(raw.investor_id),
            'investor_loan_id': self._clean(raw.investor_loan_id),
            'borrower_name': self._clean(raw.borrower_name),
            'principal_bal': self._to_dec(raw.principal_bal),
            'escrow_bal': self._to_dec(raw.escrow_bal),
            'other_funds_bal': self._to_dec(raw.other_funds_bal),
            'late_charge_bal': self._to_dec(raw.late_charge_bal),
            'legal_fee_bal': self._to_dec(raw.legal_fee_bal),
            'deferred_prin': self._to_dec(raw.deferred_prin),
            'unapplied_bal': self._to_dec(raw.unapplied_bal),
            'loss_draft_bal': self._to_dec(raw.loss_draft_bal),
            'asst_bal': self._to_dec(raw.asst_bal),
            'nsf_fee_bal': self._to_dec(raw.nsf_fee_bal),
            'oth_fee_bal': self._to_dec(raw.oth_fee_bal),
            'deferred_int': self._to_dec(raw.deferred_int),
            'primary_status': self._clean(raw.primary_status),
            'loan_type': self._clean(raw.loan_type),
            'legal_status': self._clean(raw.legal_status),
            'warning_status': self._clean(raw.warning_status),
            'due_date': self._parse_date(raw.due_date)[3],
            'date_inactive': self._parse_date(raw.date_inactive)[3],
        }

        if dry_run:
            return 'created'

        with transaction.atomic():
            existing = (
                ServicerTrialBalanceData.objects.filter(
                    file_date=file_date,
                    loan_id=normalized_loan_id,
                )
                .order_by('id')
                .first()
            )
            if existing is not None:
                for k, v in cleaned_data.items():
                    setattr(existing, k, v)
                existing.save()
                return 'updated'

            ServicerTrialBalanceData.objects.create(**cleaned_data)
            return 'created'

    def _clean(self, value: str) -> Optional[str]:
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

    def _to_dec(self, value: str) -> Optional[Decimal]:
        value = self._clean(value)
        if value is None:
            return None
        try:
            clean = self._normalize_numeric_string(value)
            return Decimal(clean)
        except (ValueError, InvalidOperation, AttributeError):
            return None

    def _parse_date(self, date_str: str) -> Tuple[Optional[int], Optional[int], Optional[int], Optional[datetime]]:
        if date_str is None or not isinstance(date_str, str):
            return (None, None, None, None)
        date_str = date_str.strip()
        if not date_str:
            return (None, None, None, None)

        lowered = date_str.lower()
        if lowered in NULL_LIKE_VALUES:
            return (None, None, None, None)

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

        logger.warning("Failed to parse date: %s", date_str)
        return (None, None, None, None)

    def _normalize_servicer_id(self, value: str) -> Optional[str]:
        cleaned = self._clean(value)
        if cleaned is None:
            return None
        normalized = cleaned.lstrip('0')
        return normalized or cleaned
