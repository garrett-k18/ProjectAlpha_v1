"""
Import LLTransactionSummary realized P&L backfill from CSV.

CSV is expected to look like backfill_GLTransactions.csv with columns:
    asset_hub_id,purchase_price_realized,...,realized_gross_cost,last_updated,created_at

Only asset_hub_id and the *_realized / *_cost numeric fields are used.
Timestamps (last_updated, created_at) are ignored so Django can manage them.
"""

import csv
import logging
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import AssetIdHub, LLTransactionSummary

logger = logging.getLogger(__name__)


def _read_csv_rows(file_path: Path) -> List[Dict[str, str]]:
    """Read all rows from a CSV using tolerant encoding handling."""
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin-1", "iso-8859-1"]
    last_error: Optional[Exception] = None

    for encoding in encodings:
        try:
            with file_path.open(newline="", encoding=encoding) as handle:
                reader = csv.DictReader(handle)
                return list(reader)
        except UnicodeDecodeError as exc:
            last_error = exc
            continue

    # Fallback: ignore errors to salvage as much data as possible
    try:
        with file_path.open(newline="", encoding="utf-8", errors="ignore") as handle:
            reader = csv.DictReader(handle)
            return list(reader)
    except Exception as exc:  # pragma: no cover - defensive
        raise CommandError(f"Failed to read CSV '{file_path}': {exc or last_error}")


def _parse_decimal(raw: Optional[str]) -> Optional[Decimal]:
    """Convert a CSV cell to Decimal or None.

    Empty strings / quotes become None. Invalid numbers log a warning and return None.
    """
    if raw is None:
        return None
    value = str(raw).strip().strip('"')
    if value == "":
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        logger.warning("Invalid decimal value '%s' - treating as None", raw)
        return None


class Command(BaseCommand):
    """Import or backfill LLTransactionSummary from a realized totals CSV."""

    help = (
        "Import or backfill LLTransactionSummary records from a CSV of realized totals "
        "keyed by asset_hub_id."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--file",
            dest="file_path",
            required=True,
            help="Path to the CSV file (e.g. 'z.Admin/DataUploads/Backfill Master/backfill_GLTransactions.csv')",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate CSV without writing any database changes.",
        )

    def handle(self, *args, **options) -> None:
        file_arg = options["file_path"]
        file_path = Path(file_arg)
        if not file_path.exists():
            # Also try relative to current working directory
            alt = Path.cwd() / file_arg
            if alt.exists():
                file_path = alt
            else:
                raise CommandError(f"CSV file '{file_arg}' does not exist.")

        rows = _read_csv_rows(file_path)
        if not rows:
            self.stdout.write(self.style.WARNING("CSV contained no data rows."))
            return

        dry_run: bool = options.get("dry_run", False)

        self.stdout.write(
            self.style.NOTICE(
                "Note: 'last_updated' and 'created_at' columns in CSV are ignored; "
                "timestamps are managed by Django."
            )
        )

        # Collect and normalize asset_hub_ids from CSV
        asset_ids: List[int] = []
        for row in rows:
            raw_id = (row.get("asset_hub_id") or "").strip()
            if not raw_id:
                continue
            try:
                asset_ids.append(int(raw_id))
            except ValueError:
                logger.warning("Skipping row with non-numeric asset_hub_id='%s'", raw_id)

        if not asset_ids:
            self.stdout.write(self.style.WARNING("No valid asset_hub_id values found in CSV."))
            return

        unique_ids = sorted(set(asset_ids))

        # Prefetch AssetIdHub instances and existing summaries
        asset_map: Dict[int, AssetIdHub] = AssetIdHub.objects.in_bulk(unique_ids)
        existing_summaries = set(
            LLTransactionSummary.objects.filter(asset_hub_id__in=unique_ids).values_list(
                "asset_hub_id", flat=True
            )
        )

        stats = {
            "rows": 0,
            "created": 0,
            "updated": 0,
            "missing_asset": 0,
            "skipped_no_asset_id": 0,
            "invalid_asset_id": 0,
            "errors": 0,
        }

        # Helper to build defaults dict for update_or_create
        def build_defaults(row: Dict[str, str]) -> Dict[str, Optional[Decimal]]:
            return {
                "purchase_price_realized": _parse_decimal(row.get("purchase_price_realized")),
                "gross_purchase_price_realized": _parse_decimal(row.get("gross_purchase_price_realized")),
                "acq_due_diligence_realized": _parse_decimal(row.get("acq_due_diligence_realized")),
                "acq_legal_realized": _parse_decimal(row.get("acq_legal_realized")),
                "acq_title_realized": _parse_decimal(row.get("acq_title_realized")),
                "acq_other_realized": _parse_decimal(row.get("acq_other_realized")),
                "income_principal_realized": _parse_decimal(row.get("income_principal_realized")),
                "income_interest_realized": _parse_decimal(row.get("income_interest_realized")),
                "income_rent_realized": _parse_decimal(row.get("income_rent_realized")),
                "income_cam_realized": _parse_decimal(row.get("income_cam_realized")),
                "income_mod_down_payment_realized": _parse_decimal(row.get("income_mod_down_payment_realized")),
                "expense_other_realized": _parse_decimal(row.get("expense_other_realized")),
                "expense_servicing_realized": _parse_decimal(row.get("expense_servicing_realized")),
                "expense_am_fees_realized": _parse_decimal(row.get("expense_am_fees_realized")),
                "expense_property_tax_realized": _parse_decimal(row.get("expense_property_tax_realized")),
                "expense_property_insurance_realized": _parse_decimal(row.get("expense_property_insurance_realized")),
                "legal_foreclosure_realized": _parse_decimal(row.get("legal_foreclosure_realized")),
                "legal_bankruptcy_realized": _parse_decimal(row.get("legal_bankruptcy_realized")),
                "legal_dil_realized": _parse_decimal(row.get("legal_dil_realized")),
                "legal_cash_for_keys_realized": _parse_decimal(row.get("legal_cash_for_keys_realized")),
                "legal_eviction_realized": _parse_decimal(row.get("legal_eviction_realized")),
                "reo_hoa_realized": _parse_decimal(row.get("reo_hoa_realized")),
                "reo_utilities_realized": _parse_decimal(row.get("reo_utilities_realized")),
                "reo_trashout_realized": _parse_decimal(row.get("reo_trashout_realized")),
                "reo_renovation_realized": _parse_decimal(row.get("reo_renovation_realized")),
                "reo_property_preservation_realized": _parse_decimal(row.get("reo_property_preservation_realized")),
                "cre_marketing_realized": _parse_decimal(row.get("cre_marketing_realized")),
                "cre_ga_pool_realized": _parse_decimal(row.get("cre_ga_pool_realized")),
                "cre_maintenance_realized": _parse_decimal(row.get("cre_maintenance_realized")),
                "fund_taxes_realized": _parse_decimal(row.get("fund_taxes_realized")),
                "fund_legal_realized": _parse_decimal(row.get("fund_legal_realized")),
                "fund_consulting_realized": _parse_decimal(row.get("fund_consulting_realized")),
                "fund_audit_realized": _parse_decimal(row.get("fund_audit_realized")),
                "gross_liquidation_proceeds_realized": _parse_decimal(row.get("proceeds_realized")),
                "broker_closing_realized": _parse_decimal(row.get("broker_closing_realized")),
                "other_closing_realized": _parse_decimal(row.get("other_closing_realized")),
                "net_liquidation_proceeds_realized": _parse_decimal(
                    row.get("net_liquidation_proceeds_realized")
                ),
                # Subtotals (can be backfilled directly)
                "acq_total_realized": _parse_decimal(row.get("acq_total_realized")),
                "operating_expenses_total_realized": _parse_decimal(row.get("operating_expenses_total_realized")),
                "legal_total_realized": _parse_decimal(row.get("legal_total_realized")),
                "reo_total_realized": _parse_decimal(row.get("reo_total_realized")),
                "cre_total_realized": _parse_decimal(row.get("cre_total_realized")),
                "fund_total_realized": _parse_decimal(row.get("fund_total_realized")),
                "total_expenses_realized": _parse_decimal(row.get("total_expenses_realized")),
                "realized_gross_cost": _parse_decimal(row.get("realized_gross_cost")),
            }

        if dry_run:
            # Dry run: do not write, just classify rows
            for row in rows:
                stats["rows"] += 1
                raw_id = (row.get("asset_hub_id") or "").strip()
                if not raw_id:
                    stats["skipped_no_asset_id"] += 1
                    continue
                try:
                    asset_id = int(raw_id)
                except ValueError:
                    stats["invalid_asset_id"] += 1
                    continue

                if asset_id not in asset_map:
                    stats["missing_asset"] += 1
                    continue

                if asset_id in existing_summaries:
                    stats["updated"] += 1
                else:
                    stats["created"] += 1

            self._print_summary(stats, dry_run=True)
            return

        # Real run: apply changes inside a transaction
        with transaction.atomic():
            for row in rows:
                stats["rows"] += 1
                raw_id = (row.get("asset_hub_id") or "").strip()
                if not raw_id:
                    stats["skipped_no_asset_id"] += 1
                    continue
                try:
                    asset_id = int(raw_id)
                except ValueError:
                    stats["invalid_asset_id"] += 1
                    continue

                if asset_id not in asset_map:
                    stats["missing_asset"] += 1
                    continue

                defaults = build_defaults(row)
                try:
                    obj, created = LLTransactionSummary.objects.update_or_create(
                        asset_hub_id=asset_id,
                        defaults=defaults,
                    )
                except Exception as exc:  # pragma: no cover - defensive
                    stats["errors"] += 1
                    logger.error(
                        "Error upserting LLTransactionSummary for asset_hub_id=%s: %s",
                        asset_id,
                        exc,
                    )
                    continue

                if created:
                    stats["created"] += 1
                else:
                    stats["updated"] += 1

        self._print_summary(stats, dry_run=False)

    def _print_summary(self, stats: Dict[str, int], dry_run: bool) -> None:
        mode = "DRY RUN" if dry_run else "IMPORT"
        self.stdout.write(self.style.SUCCESS(f"\n=== LLTransactionSummary {mode} COMPLETE ==="))
        self.stdout.write(f"Rows processed:        {stats['rows']}")
        self.stdout.write(f"Created summaries:     {stats['created']}")
        self.stdout.write(f"Updated summaries:     {stats['updated']}")
        self.stdout.write(f"Missing AssetIdHub:    {stats['missing_asset']}")
        self.stdout.write(f"No asset_hub_id:       {stats['skipped_no_asset_id']}")
        self.stdout.write(f"Invalid asset_hub_id:  {stats['invalid_asset_id']}")
        self.stdout.write(f"Errors:                {stats['errors']}")
        if dry_run:
            self.stdout.write(self.style.WARNING("(No database changes were made.)"))
