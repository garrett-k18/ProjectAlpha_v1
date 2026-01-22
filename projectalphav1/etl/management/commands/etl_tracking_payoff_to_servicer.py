"""
ETL: Transform raw tracking payoff data (EOMTrackingPayoffData) -> ServicerTrackingPayoffData.

Usage:
    python manage.py etl_tracking_payoff_to_servicer [--file-date YYYY-MM-DD] [--dry-run]
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple
import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from etl.models import EOMTrackingPayoffData
from am_module.models import ServicerTrackingPayoffData
from core.models import AssetIdHub

logger = logging.getLogger(__name__)

NULL_LIKE_VALUES = {
    'na', 'na.', 'n/a', 'n/a.', 'n\\a', 'null', 'none', 'nan', '-', '--', '---', '–', '—', '−', '‑',
    '0000-00-00', '00/00/0000',
}


class Command(BaseCommand):
    help = 'ETL: Transform EOMTrackingPayoffData -> ServicerTrackingPayoffData'

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
                f"{'[DRY RUN] ' if dry_run else ''}Starting ETL: Tracking Payoff -> ServicerTrackingPayoffData"
            )
        )

        queryset = EOMTrackingPayoffData.objects.all()
        if file_date_filter:
            queryset = queryset.filter(file_date=file_date_filter)
        queryset = queryset.order_by('id')

        if max_records is not None and max_records > 0:
            queryset = queryset[:max_records]

        total = queryset.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('No tracking payoff records to process'))
            return

        if file_date_filter:
            self.stdout.write(f"Filtering for file_date: {file_date_filter}")
        self.stdout.write(f"Found {total} raw tracking payoff records")

        stats = {'processed': 0, 'created': 0, 'updated': 0, 'skipped_invalid': 0, 'errors': 0}

        for i in range(0, total, batch_size):
            batch = queryset[i : i + batch_size]
            self.stdout.write(
                f"Batch {i // batch_size + 1}: records {i + 1}-{min(i + batch_size, total)}"
            )
            for raw in batch:
                try:
                    result = self._process_record(raw=raw, dry_run=dry_run)
                    stats[result] += 1
                    stats['processed'] += 1
                except Exception as exc:
                    stats['errors'] += 1
                    logger.error("Error processing tracking payoff id=%s: %s", raw.id, exc)
                    self.stdout.write(self.style.ERROR(f"  ERROR: id={raw.id} - {exc}"))

        self.stdout.write(self.style.SUCCESS("\n=== ETL Complete (tracking payoff) ==="))
        for k in ['processed', 'created', 'updated', 'skipped_invalid', 'errors']:
            self.stdout.write(f"{k.title()}: {stats[k]}")

    def _process_record(self, *, raw: EOMTrackingPayoffData, dry_run: bool) -> str:
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
            'investor_loan_id': self._clean(raw.investor_loan_id),
            'received_date': self._parse_date(raw.received_date)[3],
            'due_date': self._parse_date(raw.due_date)[3],
            'principal_paid_off': self._to_dec(raw.principal_paid_off),
            'interest_collected': self._to_dec(raw.interest_collected),
            'sf_collected': self._to_dec(raw.sf_collected),
            'net_interest': self._to_dec(raw.net_interest),
            'description': self._clean(raw.description),
            'payoff_reason': self._clean(raw.payoff_reason),
        }

        if dry_run:
            return 'created'

        with transaction.atomic():
            obj, created = ServicerTrackingPayoffData.objects.update_or_create(
                file_date=file_date,
                loan_id=normalized_loan_id,
                defaults=cleaned_data,
            )
            return 'created' if created else 'updated'

    def _clean(self, value: str) -> Optional[str]:
        if value is None or not isinstance(value, str):
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        if cleaned.lower() in NULL_LIKE_VALUES:
            return None
        return cleaned

    def _normalize_servicer_id(self, value: str) -> Optional[str]:
        cleaned = self._clean(value)
        if cleaned is None:
            return None
        normalized = cleaned.lstrip('0')
        return normalized or cleaned

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
            return Decimal(self._normalize_numeric_string(value))
        except (ValueError, InvalidOperation, AttributeError):
            return None

    def _parse_date(self, date_str: str) -> Tuple[Optional[int], Optional[int], Optional[int], Optional[datetime]]:
        if date_str is None or not isinstance(date_str, str):
            return (None, None, None, None)
        s = date_str.strip()
        if not s:
            return (None, None, None, None)
        if s.lower() in NULL_LIKE_VALUES:
            return (None, None, None, None)

        formats = [
            '%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f',
            '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S.%f',
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(s, fmt)
                return (dt.year, dt.month, dt.day, dt.date())
            except ValueError:
                continue
        try:
            dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
            return (dt.year, dt.month, dt.day, dt.date())
        except ValueError:
            return (None, None, None, None)
