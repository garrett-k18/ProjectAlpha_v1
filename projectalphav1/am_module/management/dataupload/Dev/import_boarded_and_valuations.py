"""
Management command to import two CSVs in one go:
- Valuations into core.models.valuations.Valuation
- SellerBoardedData into am_module.models.boarded_data.SellerBoardedData (delegates to existing upload_boarded_csv)

Usage examples (run from the manage.py directory):
  python manage.py import_boarded_and_valuations --valuations Admin/DataUploads/valuation_headers.csv --boarded Admin/DataUploads/seller_boarded_data_headers.csv --update-boarded
  python manage.py import_boarded_and_valuations --valuations Admin/DataUploads/valuation_headers.csv --dry-run

Key features:
- Normalizes valuation "source" to match Valuation.SOURCE_CHOICES keys (e.g., "Internal" -> "internal", "broker" -> "broker").
- Parses dates in YYYY-MM-DD or MM/DD/YYYY formats.
- Safely parses currency/decimal fields by stripping commas and "$".
- Upserts Valuation on natural key (asset_hub, source, value_date) per model unique constraint.
- Delegates boarded data load to the already-existing "upload_boarded_csv" command.

Docs reviewed:
- Django management commands: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
- Django model fields & parsing: https://docs.djangoproject.com/en/stable/ref/models/fields/
"""
from __future__ import annotations

import csv
import os
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple, Dict, Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# Import the target models
from core.models.valuations import Valuation  # Unified valuation model (core app)
from core.models.model_co_assetIdHub import AssetIdHub  # FK target used by Valuation
from am_module.models.boarded_data import SellerBoardedData  # Boarded data model


# ------------------
# Helper converters
# ------------------

def _blank(val: Optional[str]) -> bool:
    """Return True when value is None or only whitespace."""
    return val is None or str(val).strip() == ""


def _to_int(val: Optional[str]) -> Optional[int]:
    """Convert CSV string to int or return None on blank/error."""
    if _blank(val):
        return None
    try:
        return int(str(val).replace(",", "").strip())
    except Exception:
        return None


def _to_dec(val: Optional[str]) -> Optional[Decimal]:
    """Convert CSV string to Decimal or return None on blank/error.
    Strips commas and "$" symbols first.
    """
    if _blank(val):
        return None
    try:
        return Decimal(str(val).replace(",", "").replace("$", "").strip())
    except (InvalidOperation, ValueError):
        return None


def _to_date(val: Optional[str]) -> Optional[date]:
    """Parse common date formats (YYYY-MM-DD, MM/DD/YYYY). Return None if blank or unparseable."""
    if _blank(val):
        return None
    s = str(val).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _norm_source(val: Optional[str]) -> Optional[str]:
    """Normalize the valuation source to match Valuation.SOURCE_CHOICES keys.
    - Accepts mixed case inputs like "Internal" and maps to "internal".
    - Recognizes known keys; otherwise returns lowercased token.
    """
    if _blank(val):
        return None
    token = str(val).strip()
    # Known keys in model: 'internalInitialUW','internal','broker','desktop','BPOI','BPOE','seller','appraisal'
    # We map some common human inputs to canonical keys.
    lower = token.lower()
    if lower in {"internal", "broker", "desktop", "seller", "appraisal"}:
        return lower
    # Handle initial UW variants
    if lower in {"internalinitialuw", "initial", "initialuw", "uw"}:
        return "internalInitialUW"
    # Preserve exact uppercase keys for BPOI/BPOE if typed that way
    if token in {"BPOI", "BPOE"}:
        return token
    # Fallback to lowercased token (let DB validation handle if not allowed)
    return lower


class Command(BaseCommand):
    """Composite import command for valuations and boarded seller data.

    Arguments:
    - --valuations <path>: path to valuations CSV (headers must match Admin/DataUploads/valuation_headers.csv)
    - --boarded <path>: path to seller boarded data CSV (delegated to upload_boarded_csv)
    - --dry-run: validate only for valuations (no DB writes). Boarded import is skipped in dry-run.
    - --update-boarded: pass --update-if-exists to upload_boarded_csv when importing boarded data.
    """

    help = "Import valuations and/or boarded seller data from CSV files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--valuations",
            dest="valuations_path",
            help="Path to valuations CSV (Admin/DataUploads/valuation_headers.csv)",
        )
        parser.add_argument(
            "--boarded",
            dest="boarded_path",
            help="Path to boarded data CSV (Admin/DataUploads/seller_boarded_data_headers.csv)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate valuations CSV only; do not write to DB and skip boarded import.",
        )
        parser.add_argument(
            "--update-boarded",
            action="store_true",
            help="When importing boarded data, update existing rows if hub already has a record.",
        )

    def handle(self, *args, **opts):
        valuations_path: Optional[str] = opts.get("valuations_path")
        boarded_path: Optional[str] = opts.get("boarded_path")
        dry_run: bool = bool(opts.get("dry_run"))
        update_boarded: bool = bool(opts.get("update_boarded"))

        if not valuations_path and not boarded_path:
            raise CommandError("Provide at least one of --valuations or --boarded")

        # ----------------------------
        # Part 1: Import Valuations
        # ----------------------------
        created_v = 0
        updated_v = 0
        errors_v = 0

        if valuations_path:
            if not os.path.exists(valuations_path):
                raise CommandError(f"Valuations CSV not found: {valuations_path}")

            # Open CSV with utf-8-sig to handle BOM if present
            with open(valuations_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if not rows:
                self.stdout.write(self.style.WARNING("Valuations CSV contains no rows."))
            else:
                # Transactionally insert/update unless dry-run
                ctx = transaction.atomic() if not dry_run else _NullTx()
                try:
                    ctx.__enter__()
                    for idx, r in enumerate(rows, start=2):  # enumerate starts at 2 since header is line 1
                        try:
                            # Extract foreign key to hub (expects 'asset_hub_id' column by name)
                            hub_id = _to_int(r.get("asset_hub_id"))
                            if not hub_id:
                                raise ValueError("asset_hub_id is required")

                            # Validate hub exists
                            if not AssetIdHub.objects.filter(id=hub_id).exists():
                                raise ValueError(f"AssetIdHub id {hub_id} does not exist")

                            # Normalize and parse fields
                            source = _norm_source(r.get("source"))
                            value_date = _to_date(r.get("value_date"))

                            # Build defaults payload for update_or_create
                            defaults: Dict[str, Any] = {
                                "asis_value": _to_dec(r.get("asis_value")),
                                "arv_value": _to_dec(r.get("arv_value")),
                                "rehab_est_total": _to_dec(r.get("rehab_est_total")),
                                "roof_est": _to_dec(r.get("roof_est")),
                                "kitchen_est": _to_dec(r.get("kitchen_est")),
                                "bath_est": _to_dec(r.get("bath_est")),
                                "flooring_est": _to_dec(r.get("flooring_est")),
                                "windows_est": _to_dec(r.get("windows_est")),
                                "appliances_est": _to_dec(r.get("appliances_est")),
                                "plumbing_est": _to_dec(r.get("plumbing_est")),
                                "electrical_est": _to_dec(r.get("electrical_est")),
                                "landscaping_est": _to_dec(r.get("landscaping_est")),
                                "notes": (r.get("notes") or None),
                                "links": (r.get("links") or None),
                                # created_by / updated_by can be set by *_id too; DB will accept unknown user as None
                                "created_by_id": _to_int(r.get("created_by_id")),
                                "updated_by_id": _to_int(r.get("updated_by_id")),
                            }

                            # Natural key matches model unique constraint
                            lookup = {
                                "asset_hub_id": hub_id,
                                "source": source,
                                "value_date": value_date,
                            }

                            if dry_run:
                                # Only validate by instantiating (no save)
                                _ = Valuation(**lookup, **defaults)
                                created_v += 1  # count as would-create
                                continue

                            # Perform upsert
                            obj, was_created = Valuation.objects.update_or_create(defaults=defaults, **lookup)
                            if was_created:
                                created_v += 1
                            else:
                                updated_v += 1
                        except Exception as e:
                            errors_v += 1
                            self.stderr.write(self.style.ERROR(f"Valuation row {idx} failed: {e}"))
                    if dry_run:
                        self.stdout.write(self.style.WARNING("Valuations dry run complete (no DB writes)."))
                    ctx.__exit__(None, None, None)
                except Exception as e:
                    ctx.__exit__(type(e), e, e.__traceback__)
                    raise

        # ----------------------------
        # Part 2: Import Boarded Data
        # ----------------------------
        if boarded_path:
            if dry_run:
                self.stdout.write(self.style.WARNING("Skipping boarded import due to --dry-run."))
            else:
                if not os.path.exists(boarded_path):
                    raise CommandError(f"Boarded CSV not found: {boarded_path}")

                # Field map mirrors the standalone uploader
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
                    "origination_value": ("origination_value", _to_dec),
                    "origination_arv": ("origination_arv", _to_dec),
                    "origination_value_date": ("origination_value_date", _to_date),
                    "seller_value_date": ("seller_value_date", _to_date),
                    "seller_arv_value": ("seller_arv_value", _to_dec),
                    "seller_asis_value": ("seller_asis_value", _to_dec),
                    "additional_asis_value": ("additional_asis_value", _to_dec),
                    "additional_arv_value": ("additional_arv_value", _to_dec),
                    "additional_value_date": ("additional_value_date", _to_date),
                    "fc_flag": ("fc_flag", lambda v: None if _blank(v) else str(v).strip().lower() in ("true","t","yes","y","1")),
                    "fc_first_legal_date": ("fc_first_legal_date", _to_date),
                    "fc_referred_date": ("fc_referred_date", _to_date),
                    "fc_judgement_date": ("fc_judgement_date", _to_date),
                    "fc_scheduled_sale_date": ("fc_scheduled_sale_date", _to_date),
                    "fc_sale_date": ("fc_sale_date", _to_date),
                    "fc_starting": ("fc_starting", _to_dec),
                    "bk_flag": ("bk_flag", lambda v: None if _blank(v) else str(v).strip().lower() in ("true","t","yes","y","1")),
                    "bk_chapter": ("bk_chapter", lambda v: (v or "").strip() or None),
                    "mod_flag": ("mod_flag", lambda v: None if _blank(v) else str(v).strip().lower() in ("true","t","yes","y","1")),
                    "mod_date": ("mod_date", _to_date),
                    "mod_maturity_date": ("mod_maturity_date", _to_date),
                    "mod_term": ("mod_term", _to_int),
                    "mod_rate": ("mod_rate", _to_dec),
                    "mod_initial_balance": ("mod_initial_balance", _to_dec),
                    "boarded_by": ("boarded_by", lambda v: (v or "").strip() or None),
                }

                created_b = 0
                updated_b = 0
                skipped_b = 0

                with open(boarded_path, newline="", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    if "asset_hub" not in (reader.fieldnames or []):
                        raise CommandError("Boarded CSV must include 'asset_hub' column")
                    for i, row in enumerate(reader, start=2):
                        hub_id = _to_int(row.get("asset_hub"))
                        if not hub_id:
                            skipped_b += 1
                            continue
                        # Validate hub exists
                        try:
                            hub = AssetIdHub.objects.get(pk=hub_id)
                        except AssetIdHub.DoesNotExist:
                            skipped_b += 1
                            continue

                        # Create or update existing boarded row by hub
                        try:
                            sbd = SellerBoardedData.objects.get(asset_hub=hub)
                            if not update_boarded:
                                skipped_b += 1
                                continue
                            mode = "update"
                        except SellerBoardedData.DoesNotExist:
                            sbd = SellerBoardedData(asset_hub=hub)
                            mode = "create"

                        # Map fields if present
                        for csv_col, (attr, conv) in FIELD_MAP.items():
                            if csv_col in row:
                                setattr(sbd, attr, conv(row[csv_col]))

                        sbd.save()
                        if mode == "create":
                            created_b += 1
                        else:
                            updated_b += 1

                self.stdout.write(self.style.SUCCESS(
                    f"Boarded import complete: created={created_b}, updated={updated_b}, skipped={skipped_b}"
                ))

        # Final summary (valuations portion)
        if valuations_path:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Valuations import complete: created={created_v}, updated={updated_v}, errors={errors_v}, dry_run={dry_run}"
                )
            )


class _NullTx:
    """No-op context manager to mirror transaction.atomic when --dry-run.
    This allows a unified code path without opening a real transaction.
    """

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False
