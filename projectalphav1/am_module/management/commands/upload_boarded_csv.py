"""
Upload SellerBoardedData from a CSV produced using the seller_boarded_headers.csv template.

Usage:
  python manage.py upload_boarded_csv --path Admin/DataUploads/seller_boarded_headers.csv [--update-if-exists]

Notes:
- Requires asset_hub column with valid core.AssetIdHub.id values.
- Handles blank strings as NULLs.
- Safely parses ints/decimals/dates.
- Sets search_path to seller_data, core, public so cross-schema FKs resolve.

Docs reviewed:
- Django custom commands: https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/
- Model field types & parsing: https://docs.djangoproject.com/en/5.2/ref/models/fields/
"""
from __future__ import annotations

import csv
import os
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction, connection
from django.utils.dateparse import parse_date

from am_module.models.boarded_data import SellerBoardedData
from core.models.asset_id_hub import AssetIdHub


# ------------------
# Helper converters
# ------------------

def _blank(val: Optional[str]) -> bool:
    return val is None or str(val).strip() == ""


def _to_int(val: str) -> Optional[int]:
    if _blank(val):
        return None
    try:
        return int(str(val).replace(",", "").strip())
    except Exception:
        return None


def _to_dec(val: str, q: Optional[str] = None) -> Optional[Decimal]:
    if _blank(val):
        return None
    try:
        d = Decimal(str(val).replace(",", "").replace("$", "").strip())
        if q:
            return d.quantize(Decimal(q))
        return d
    except (InvalidOperation, ValueError):
        return None


def _to_date(val: str) -> Optional[date]:
    if _blank(val):
        return None
    return parse_date(str(val).strip())


def _to_bool(val: str) -> Optional[bool]:
    if _blank(val):
        return None
    s = str(val).strip().lower()
    if s in ("true", "t", "yes", "y", "1"): return True
    if s in ("false", "f", "no", "n", "0"): return False
    return None


class Command(BaseCommand):
    help = "Upload SellerBoardedData rows from a CSV file"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--path", required=True, help="Path to CSV file")
        parser.add_argument(
            "--update-if-exists",
            action="store_true",
            help="Update existing SellerBoardedData (by asset_hub) instead of skipping",
        )

    def handle(self, *args, **options):
        path = options["path"]
        do_update = options["update_if_exists"]

        if not os.path.exists(path):
            self.stderr.write(self.style.ERROR(f"CSV not found: {path}"))
            return

        # Ensure correct schema order for cross-schema models
        with connection.cursor() as c:
            c.execute("SET search_path TO seller_data, core, public")

        created = 0
        updated = 0
        skipped = 0

        # Field mapping from CSV to model attributes
        # Only include fields we allow to be set via CSV (exclude auto timestamps)
        FIELD_MAP = {
            "acq_seller_id": ("acq_seller_id", _to_int),
            "acq_trade_id": ("acq_trade_id", _to_int),
            "seller_name": ("seller_name", lambda v: (v or "").strip() or None),
            "trade_name": ("trade_name", lambda v: (v or "").strip() or None),
            "sellertape_id": ("sellertape_id", lambda v: (v or "").strip() or None),
            "sellertape_altid": ("sellertape_altid", lambda v: (v or "").strip() or None),
            "asset_status": ("asset_status", lambda v: (v or "").strip() or None),
            "street_address": ("street_address", lambda v: (v or "").strip() or None),
            "city": ("city", lambda v: (v or "").strip() or None),
            "state": ("state", lambda v: (v or "").strip() or None),
            "zip": ("zip", lambda v: (v or "").strip() or None),
            "property_type": ("property_type", lambda v: (v or "").strip() or None),
            "occupancy": ("occupancy", lambda v: (v or "").strip() or None),
            "year_built": ("year_built", _to_int),
            "sq_ft": ("sq_ft", _to_int),
            "lot_size": ("lot_size", _to_int),
            "beds": ("beds", _to_int),
            "baths": ("baths", _to_dec),
            "current_balance": ("current_balance", lambda v: _to_dec(v, "0.01")),
            "deferred_balance": ("deferred_balance", lambda v: _to_dec(v, "0.01")),
            "interest_rate": ("interest_rate", lambda v: _to_dec(v, "0.0001")),
            "next_due_date": ("next_due_date", _to_date),
            "last_paid_date": ("last_paid_date", _to_date),
            "first_pay_date": ("first_pay_date", _to_date),
            "origination_date": ("origination_date", _to_date),
            "original_balance": ("original_balance", lambda v: _to_dec(v, "0.01")),
            "original_term": ("original_term", _to_int),
            "original_rate": ("original_rate", lambda v: _to_dec(v, "0.0001")),
            "original_maturity_date": ("original_maturity_date", _to_date),
            "default_rate": ("default_rate", lambda v: _to_dec(v, "0.0001")),
            "months_dlq": ("months_dlq", _to_int),
            "current_maturity_date": ("current_maturity_date", _to_date),
            "current_term": ("current_term", _to_int),
            "accrued_note_interest": ("accrued_note_interest", lambda v: _to_dec(v, "0.01")),
            "accrued_default_interest": ("accrued_default_interest", lambda v: _to_dec(v, "0.01")),
            "escrow_balance": ("escrow_balance", lambda v: _to_dec(v, "0.01")),
            "escrow_advance": ("escrow_advance", lambda v: _to_dec(v, "0.01")),
            "recoverable_corp_advance": ("recoverable_corp_advance", lambda v: _to_dec(v, "0.01")),
            "late_fees": ("late_fees", lambda v: _to_dec(v, "0.01")),
            "other_fees": ("other_fees", lambda v: _to_dec(v, "0.01")),
            "suspense_balance": ("suspense_balance", lambda v: _to_dec(v, "0.01")),
            "total_debt": ("total_debt", lambda v: _to_dec(v, "0.01")),
            "origination_value": ("origination_value", lambda v: _to_dec(v, "0.01")),
            "origination_arv": ("origination_arv", lambda v: _to_dec(v, "0.01")),
            "origination_value_date": ("origination_value_date", _to_date),
            "seller_value_date": ("seller_value_date", _to_date),
            "seller_arv_value": ("seller_arv_value", lambda v: _to_dec(v, "0.01")),
            "seller_asis_value": ("seller_asis_value", lambda v: _to_dec(v, "0.01")),
            "additional_asis_value": ("additional_asis_value", lambda v: _to_dec(v, "0.01")),
            "additional_arv_value": ("additional_arv_value", lambda v: _to_dec(v, "0.01")),
            "additional_value_date": ("additional_value_date", _to_date),
            "fc_flag": ("fc_flag", _to_bool),
            "fc_first_legal_date": ("fc_first_legal_date", _to_date),
            "fc_referred_date": ("fc_referred_date", _to_date),
            "fc_judgement_date": ("fc_judgement_date", _to_date),
            "fc_scheduled_sale_date": ("fc_scheduled_sale_date", _to_date),
            "fc_sale_date": ("fc_sale_date", _to_date),
            "fc_starting": ("fc_starting", lambda v: _to_dec(v, "0.01")),
            "bk_flag": ("bk_flag", _to_bool),
            "bk_chapter": ("bk_chapter", lambda v: (v or "").strip() or None),
            "mod_flag": ("mod_flag", _to_bool),
            "mod_date": ("mod_date", _to_date),
            "mod_maturity_date": ("mod_maturity_date", _to_date),
            "mod_term": ("mod_term", _to_int),
            "mod_rate": ("mod_rate", lambda v: _to_dec(v, "0.0001")),
            "mod_initial_balance": ("mod_initial_balance", lambda v: _to_dec(v, "0.01")),
            "boarded_by": ("boarded_by", lambda v: (v or "").strip() or None),
        }

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "asset_hub" not in reader.fieldnames:
                raise SystemExit("CSV must include 'asset_hub' column")

            for i, row in enumerate(reader, start=2):
                hub_id = _to_int(row.get("asset_hub"))
                if not hub_id:
                    self.stderr.write(self.style.WARNING(f"Row {i}: missing asset_hub; skipped"))
                    skipped += 1
                    continue

                try:
                    hub = AssetIdHub.objects.get(pk=hub_id)
                except AssetIdHub.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"Row {i}: asset_hub {hub_id} not found; skipped"))
                    skipped += 1
                    continue

                # Create or update by hub
                try:
                    sbd = SellerBoardedData.objects.get(asset_hub=hub)
                    if not do_update:
                        skipped += 1
                        continue
                    mode = "update"
                except SellerBoardedData.DoesNotExist:
                    sbd = SellerBoardedData(asset_hub=hub)
                    mode = "create"

                # Map fields
                for csv_col, (attr, conv) in FIELD_MAP.items():
                    if csv_col in row:
                        setattr(sbd, attr, conv(row[csv_col]))

                sbd.save()
                if mode == "create":
                    created += 1
                else:
                    updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Upload complete: created={created}, updated={updated}, skipped={skipped}"
        ))
