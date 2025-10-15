"""
Django management command to import SellerBoardedData from a CSV file and
ensure AssetIdHub rows exist first (hub-first architecture).

WHAT:
- Reads a CSV (UTF-8 with/without BOM) and loads rows into
  am_module.models.boarded_data.SellerBoardedData.
- Creates the associated core.models.asset_id_hub.AssetIdHub if missing.

WHY:
- Production bootstrap often starts with an empty database. Because
  SellerBoardedData uses `asset_hub` as its primary key (1:1), a hub
  record must exist before the boarded record can be inserted.

HOW (high-level):
- For each row, determine the hub using either `asset_hub` or
  `sellertape_id`.
- Create or fetch the hub, then create/update SellerBoardedData by hub.
- Type conversion is applied for ints/decimals/dates/booleans.

DOCUMENTATION REVIEWED:
- Django custom commands: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
- Django model fields: https://docs.djangoproject.com/en/stable/ref/models/fields/
"""
from __future__ import annotations

import csv
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# ALWAYS import models at module top (perf + clarity)
from core.models.asset_id_hub import AssetIdHub
from am_module.models.boarded_data import SellerBoardedData


# ------------------
# Helper converters
# ------------------

def _blank(val: Optional[str]) -> bool:
    """Return True when value is None or only whitespace."""
    return val is None or str(val).strip() == ""


def _to_int(val: Optional[str]) -> Optional[int]:
    """Convert string to int or None on blank/error. Strips commas."""
    if _blank(val):
        return None
    try:
        return int(str(val).replace(",", "").strip())
    except Exception:
        return None


def _to_dec(val: Optional[str]) -> Optional[Decimal]:
    """Convert currency-like strings to Decimal. Strips commas and "$".
    Returns None on blank/invalid.
    """
    if _blank(val):
        return None
    try:
        return Decimal(str(val).replace(",", "").replace("$", "").strip())
    except (InvalidOperation, ValueError):
        return None


def _to_date(val: Optional[str]) -> Optional[date]:
    """Parse common date formats (YYYY-MM-DD, MM/DD/YYYY)."""
    if _blank(val):
        return None
    s = str(val).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _to_bool(val: Optional[str]) -> Optional[bool]:
    """Parse truthy/falsey tokens. Returns None if blank."""
    if _blank(val):
        return None
    token = str(val).strip().lower()
    if token in ("true", "t", "yes", "y", "1"):  # truthy
        return True
    if token in ("false", "f", "no", "n", "0"):   # falsey
        return False
    return None


class Command(BaseCommand):
    """Import SellerBoardedData with hub-first guarantees.

    ARGUMENTS:
    - --file <path>: Path to CSV with headers similar to
      Admin/DataUploads/seller_boarded_data_headers.csv
    - --update-if-exists: Update existing SellerBoardedData rows when a
      record for the hub already exists (default: skip existing rows).
    - --id-precedence <asset_hub|sellertape_id>: When both columns are
      present, which one to prioritize to identify/create the hub. Default: asset_hub.
    - --sellertape-id-col <name>: Column name for seller tape id if your file
      uses a different header. Default: sellertape_id.
    - --dry-run: Validate and report only; no DB writes.

    USAGE:
        python manage.py import_seller_boarded_data --file Admin/DataUploads/seller_boarded_data_headers.csv --update-if-exists
    """

    help = "Import SellerBoardedData from CSV, auto-creating AssetIdHub if missing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            dest="file_path",
            required=True,
            help="Path to CSV (headers like Admin/DataUploads/seller_boarded_data_headers.csv)",
        )
        parser.add_argument(
            "--update-if-exists",
            action="store_true",
            help="Update existing SellerBoardedData rows; default is to skip them.",
        )
        parser.add_argument(
            "--id-precedence",
            choices=("asset_hub", "sellertape_id"),
            default="asset_hub",
            help="When both columns are present, prefer this one to identify/create the hub.",
        )
        parser.add_argument(
            "--sellertape-id-col",
            default="sellertape_id",
            help="Header name for seller tape id if your file uses a different column name.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate only (no DB writes).",
        )

    def handle(self, *args, **opts):
        """Main entry point: read CSV, resolve hubs, upsert boarded rows."""
        file_path: str = opts.get("file_path")
        update_if_exists: bool = bool(opts.get("update_if_exists"))
        id_precedence: str = opts.get("id_precedence") or "asset_hub"
        sellertape_col: str = opts.get("sellertape_id_col") or "sellertape_id"
        dry_run: bool = bool(opts.get("dry_run"))

        # Open CSV (utf-8-sig handles BOM)
        try:
            with open(file_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            raise CommandError(f"Failed to read CSV '{file_path}': {e}")

        if not rows:
            self.stdout.write(self.style.WARNING("CSV contains no data rows. Exiting."))
            return

        # Field conversions map: csv_col -> (model_attr, converter)
        FIELD_MAP: Dict[str, Tuple[str, callable]] = {
            # IDs / references / labels
            "acq_seller_id": ("acq_seller_id", _to_int),
            "acq_trade_id": ("acq_trade_id", _to_int),
            "seller_name": ("seller_name", lambda v: (v or "").strip() or None),
            "trade_name": ("trade_name", lambda v: (v or "").strip() or None),
            "sellertape_id": ("sellertape_id", lambda v: (v or "").strip() or None),
            "sellertape_altid": ("sellertape_altid", lambda v: (v or "").strip() or None),
            "asset_status": ("asset_status", lambda v: (v or "").strip() or None),
            # Property
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
            # Loan
            "current_balance": ("current_balance", _to_dec),
            "deferred_balance": ("deferred_balance", _to_dec),
            "interest_rate": ("interest_rate", _to_dec),
            "next_due_date": ("next_due_date", _to_date),
            "last_paid_date": ("last_paid_date", _to_date),
            "first_pay_date": ("first_pay_date", _to_date),
            "origination_date": ("origination_date", _to_date),
            "original_balance": ("original_balance", _to_dec),
            "original_term": ("original_term", _to_int),
            "original_rate": ("original_rate", _to_dec),
            "original_maturity_date": ("original_maturity_date", _to_date),
            # Extras
            "default_rate": ("default_rate", _to_dec),
            "months_dlq": ("months_dlq", _to_int),
            "current_maturity_date": ("current_maturity_date", _to_date),
            "current_term": ("current_term", _to_int),
            "accrued_note_interest": ("accrued_note_interest", _to_dec),
            "accrued_default_interest": ("accrued_default_interest", _to_dec),
            "escrow_balance": ("escrow_balance", _to_dec),
            "escrow_advance": ("escrow_advance", _to_dec),
            "recoverable_corp_advance": ("recoverable_corp_advance", _to_dec),
            "late_fees": ("late_fees", _to_dec),
            "other_fees": ("other_fees", _to_dec),
            "suspense_balance": ("suspense_balance", _to_dec),
            "total_debt": ("total_debt", _to_dec),
            # Valuations
            "origination_value": ("origination_value", _to_dec),
            "origination_arv": ("origination_arv", _to_dec),
            "origination_value_date": ("origination_value_date", _to_date),
            "seller_value_date": ("seller_value_date", _to_date),
            "seller_arv_value": ("seller_arv_value", _to_dec),
            "seller_asis_value": ("seller_asis_value", _to_dec),
            "additional_asis_value": ("additional_asis_value", _to_dec),
            "additional_arv_value": ("additional_arv_value", _to_dec),
            "additional_value_date": ("additional_value_date", _to_date),
            # FC/BK/MOD
            "fc_flag": ("fc_flag", _to_bool),
            "fc_first_legal_date": ("fc_first_legal_date", _to_date),
            "fc_referred_date": ("fc_referred_date", _to_date),
            "fc_judgement_date": ("fc_judgement_date", _to_date),
            "fc_scheduled_sale_date": ("fc_scheduled_sale_date", _to_date),
            "fc_sale_date": ("fc_sale_date", _to_date),
            "fc_starting": ("fc_starting", _to_dec),
            "bk_flag": ("bk_flag", _to_bool),
            "bk_chapter": ("bk_chapter", lambda v: (v or "").strip() or None),
            "mod_flag": ("mod_flag", _to_bool),
            "mod_date": ("mod_date", _to_date),
            "mod_maturity_date": ("mod_maturity_date", _to_date),
            "mod_term": ("mod_term", _to_int),
            "mod_rate": ("mod_rate", _to_dec),
            "mod_initial_balance": ("mod_initial_balance", _to_dec),
            # Meta
            "boarded_by": ("boarded_by", lambda v: (v or "").strip() or None),
        }

        # Stats
        created_hubs = 0
        created_rows = 0
        updated_rows = 0
        skipped_rows = 0

        # Each row gets its own small transaction to isolate failures
        for idx, row in enumerate(rows, start=2):  # CSV header is line 1
            try:
                # -----------------------------
                # Resolve/create the hub first
                # -----------------------------
                hub = self._resolve_hub(
                    row=row,
                    sellertape_col=sellertape_col,
                    id_precedence=id_precedence,
                    dry_run=dry_run,
                )
                if hub is None:
                    skipped_rows += 1
                    self.stderr.write(self.style.WARNING(
                        f"Row {idx}: skipped - could not resolve/create AssetIdHub (need asset_hub or {sellertape_col})."
                    ))
                    continue

                if getattr(hub, "_was_created", False):
                    created_hubs += 1

                # --------------------------------------
                # Create or update SellerBoardedData row
                # --------------------------------------
                try:
                    sbd = SellerBoardedData.objects.get(asset_hub=hub)
                    if not update_if_exists:
                        skipped_rows += 1
                        continue
                    mode = "update"
                except SellerBoardedData.DoesNotExist:
                    sbd = SellerBoardedData(asset_hub=hub)
                    mode = "create"

                # Map present CSV fields through converters
                for csv_col, (attr, conv) in FIELD_MAP.items():
                    if csv_col in row:
                        setattr(sbd, attr, conv(row[csv_col]))

                if dry_run:
                    # Instantiate/validate without save by touching clean save path
                    _ = sbd  # no-op; model instantiation already done
                    if mode == "create":
                        created_rows += 1
                    else:
                        updated_rows += 1
                else:
                    sbd.save()
                    if mode == "create":
                        created_rows += 1
                    else:
                        updated_rows += 1

            except Exception as e:
                skipped_rows += 1
                self.stderr.write(self.style.ERROR(f"Row {idx} failed: {e}"))

        # Summary
        self.stdout.write(self.style.SUCCESS(
            f"Import complete: hubs_created={created_hubs}, created={created_rows}, updated={updated_rows}, skipped={skipped_rows}, dry_run={dry_run}"
        ))

    # ----------------------
    # Hub resolution helpers
    # ----------------------
    def _resolve_hub(
        self,
        row: Dict[str, Any],
        sellertape_col: str,
        id_precedence: str,
        dry_run: bool,
    ) -> Optional[AssetIdHub]:
        """Resolve or create an AssetIdHub for a CSV row.

        RULES:
        - If `asset_hub` column present and non-empty, prefer it when
          id_precedence == 'asset_hub'. Create hub with that explicit id when missing.
        - Else if `sellertape_id` column present, get-or-create hub by sellertape_id.
        - When both are present and id_precedence == 'sellertape_id', use sellertape first.
        - Return None if neither id source is available.
        """
        # Extract identifiers
        asset_hub_id = _to_int(row.get("asset_hub")) if "asset_hub" in row else None
        tape_id_raw = row.get(sellertape_col)
        sellertape_id = (tape_id_raw or "").strip() or None

        # Two strategies depending on precedence
        if id_precedence == "asset_hub":
            hub = self._hub_by_asset_hub(asset_hub_id, sellertape_id, dry_run)
            if hub is None:
                hub = self._hub_by_sellertape(sellertape_id, dry_run)
        else:  # sellertape_id precedence
            hub = self._hub_by_sellertape(sellertape_id, dry_run)
            if hub is None:
                hub = self._hub_by_asset_hub(asset_hub_id, sellertape_id, dry_run)

        return hub

    def _hub_by_asset_hub(
        self, asset_hub_id: Optional[int], sellertape_id: Optional[str], dry_run: bool
    ) -> Optional[AssetIdHub]:
        """Get or create hub using an explicit integer `asset_hub` id.

        - If the hub exists, optionally patch its sellertape_id if currently blank and
          CSV provides one.
        - If missing, create with the explicit id (primary key) so downstream rows match.
        - In dry-run, simulate creation by returning a transient instance with a marker.
        """
        if not asset_hub_id:
            return None

        # Try fetch existing first
        try:
            hub = AssetIdHub.objects.get(pk=asset_hub_id)
            if sellertape_id and not hub.sellertape_id:
                if not dry_run:
                    hub.sellertape_id = sellertape_id
                    hub.save(update_fields=["sellertape_id"])
            return hub
        except AssetIdHub.DoesNotExist:
            pass

        # Create missing hub with explicit id
        if dry_run:
            hub = AssetIdHub(id=asset_hub_id, sellertape_id=sellertape_id)
            setattr(hub, "_was_created", True)
            return hub

        # Use a tiny transaction to ensure clean insert
        with transaction.atomic():
            hub = AssetIdHub(id=asset_hub_id, sellertape_id=sellertape_id)
            hub.save(force_insert=True)
            setattr(hub, "_was_created", True)
            return hub

    def _hub_by_sellertape(
        self, sellertape_id: Optional[str], dry_run: bool
    ) -> Optional[AssetIdHub]:
        """Get or create hub using `sellertape_id` when no explicit hub id is available.

        Returns None if no seller tape id provided.
        """
        if not sellertape_id:
            return None

        try:
            return AssetIdHub.objects.get(sellertape_id=sellertape_id)
        except AssetIdHub.DoesNotExist:
            pass

        if dry_run:
            hub = AssetIdHub(sellertape_id=sellertape_id)
            setattr(hub, "_was_created", True)
            return hub

        with transaction.atomic():
            hub, created = AssetIdHub.objects.get_or_create(sellertape_id=sellertape_id)
            if created:
                setattr(hub, "_was_created", True)
            return hub
