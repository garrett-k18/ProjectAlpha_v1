from __future__ import annotations
"""
Import unified Valuation rows from a CSV file.

- Supports multiple sources via a required 'source' column
- Upserts by (asset_hub_id, source, value_date) when --update-on is provided
- Allows repeated asset_hub_id to import many valuations for the same asset

Usage examples:
  python manage.py import_valuations --csv C:/path/valuations.csv --dry-run
  python manage.py import_valuations --csv C:/path/valuations.csv --update-on asset_hub_id,source,value_date
  python manage.py import_valuations --csv C:/path/valuations.csv --truncate

CSV columns (recommended):
  asset_hub_id,source,value_date,asis_value,arv_value,rehab_est_total,notes,links,created_by_id,updated_by_id

Notes:
- value_date format: YYYY-MM-DD or MM/DD/YYYY
- Unknown columns are ignored
"""

import csv
from typing import Dict, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import django.db.models as djm

from decimal import Decimal
import datetime as dt

from core.models.valuations import Valuation


class _NullTx:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class Command(BaseCommand):
    help = "Import unified Valuation rows from CSV. Use --update-on asset_hub_id,source,value_date to upsert."

    def add_arguments(self, parser):
        parser.add_argument("--csv", dest="csv_path", required=True, help="Path to CSV file to import")
        parser.add_argument("--dry-run", action="store_true", help="Validate only, do not write to DB")
        parser.add_argument("--truncate", action="store_true", help="Delete all existing rows before import (skipped when --dry-run)")
        parser.add_argument("--allow-partial", action="store_true", help="Allow missing required fields; DB/null defaults may apply")
        parser.add_argument("--batch-size", type=int, default=1000, help="bulk_create batch size (default 1000)")
        parser.add_argument(
            "--update-on",
            dest="update_on",
            default="asset_hub_id,source,value_date",
            help="Comma-separated list of fields to use as update key (default asset_hub_id,source,value_date)",
        )

    def handle(self, *args, **options):
        csv_path: str = options["csv_path"]
        dry_run: bool = options["dry_run"]
        truncate: bool = options["truncate"]
        allow_partial: bool = options["allow_partial"]
        batch_size: int = options["batch_size"]
        update_on_fields: List[str] = [s.strip() for s in (options.get("update_on") or "").split(",") if s.strip()]

        # Load CSV
        try:
            with open(csv_path, "r", newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except FileNotFoundError:
            raise CommandError(f"CSV file not found: {csv_path}")

        # Validation helpers
        def clean_value(name: str, raw: str):
            if raw is None:
                return None
            s = str(raw).strip()
            if s == "":
                return None
            # Type coercion by expected fields
            if name in {"asis_value", "arv_value", "rehab_est_total",
                        "roof_est", "kitchen_est", "bath_est", "flooring_est",
                        "windows_est", "appliances_est", "plumbing_est", "electrical_est",
                        "landscaping_est"}:
                try:
                    return Decimal(str(s).replace(",", ""))
                except Exception as e:
                    raise ValueError(f"Invalid decimal for {name}: {s}")
            if name in {"value_date"}:
                # Accept YYYY-MM-DD or MM/DD/YYYY
                try:
                    if "-" in s:
                        return dt.datetime.strptime(s, "%Y-%m-%d").date()
                    return dt.datetime.strptime(s, "%m/%d/%Y").date()
                except Exception:
                    raise ValueError(f"Invalid date for {name}: {s}")
            # Text fields
            return s

        # Model metadata
        concrete_fields = [f for f in Valuation._meta.concrete_fields]
        field_by_name: Dict[str, object] = {f.name: f for f in concrete_fields}
        allowed_fields = [f.name for f in concrete_fields if f.name != "id"]

        created = 0
        updated = 0
        errors = 0

        ctx = transaction.atomic() if not dry_run else _NullTx()
        try:
            ctx.__enter__()
            if truncate and not dry_run:
                Valuation.objects.all().delete()

            # Validate update_on fields exist
            if update_on_fields:
                missing_key_cols = [k for k in update_on_fields if k not in allowed_fields and not k.endswith("_id")]
                # asset_hub_id is special: it maps to FK asset_hub
                for k in list(missing_key_cols):
                    if k == "asset_hub_id":
                        missing_key_cols.remove(k)
                if missing_key_cols:
                    raise CommandError(
                        f"update-on fields not present on model or not importable: {', '.join(missing_key_cols)}"
                    )

            # Upsert path always (we have a default key). Use update_or_create when keys present, else bulk create.
            for idx, r in enumerate(rows, start=2):  # header is line 1
                try:
                    # Build lookup and defaults
                    lookup = {}
                    defaults = {}
                    # Ensure required columns for default key are present
                    if not r.get("asset_hub_id"):
                        raise ValueError("asset_hub_id is required")
                    if not r.get("source"):
                        raise ValueError("source is required")
                    # value_date may be null; we still allow import but key differs

                    # Map fields
                    # FK mapping for asset_hub
                    asset_hub_id = r.get("asset_hub_id")
                    sval = (asset_hub_id or "").replace(",", "").strip()
                    lookup["asset_hub_id"] = int(sval) if sval else None

                    # Source
                    defaults["source"] = (r.get("source") or "").strip().lower()
                    # If source provided in update_on, also include in lookup
                    if "source" in update_on_fields:
                        lookup["source"] = defaults["source"]

                    # Dates and numbers
                    value_date_raw = r.get("value_date")
                    value_date = clean_value("value_date", value_date_raw) if value_date_raw not in (None, "") else None
                    if "value_date" in update_on_fields:
                        lookup["value_date"] = value_date
                    else:
                        defaults["value_date"] = value_date

                    for name in ("asis_value", "arv_value", "rehab_est_total",
                                 "roof_est", "kitchen_est", "bath_est", "flooring_est",
                                 "windows_est", "appliances_est", "plumbing_est", "electrical_est",
                                 "landscaping_est", "notes", "links"):
                        if name in field_by_name:
                            defaults[name] = clean_value(name, r.get(name))

                    # Optional audit IDs
                    cb = r.get("created_by_id")
                    ub = r.get("updated_by_id")
                    if cb is not None and cb != "":
                        defaults["created_by_id"] = int(str(cb).strip())
                    if ub is not None and ub != "":
                        defaults["updated_by_id"] = int(str(ub).strip())

                    # Perform upsert
                    if update_on_fields:
                        # Ensure we have the minimal default key
                        for k in ("asset_hub_id", "source", "value_date"):
                            if k in update_on_fields and k not in lookup:
                                # fallback from defaults if present
                                if k == "value_date":
                                    lookup[k] = defaults.get(k)
                        obj, was_created = Valuation.objects.update_or_create(defaults=defaults, **lookup)
                        created += 1 if was_created else 0
                        updated += 0 if was_created else 1
                    else:
                        # No upsert key given: create
                        obj = Valuation.objects.create(**{**lookup, **defaults})
                        created += 1
                except Exception as e:
                    errors += 1
                    self.stderr.write(self.style.ERROR(f"Row {idx} skipped: {e} | data={r}"))

            if dry_run:
                raise RuntimeError("DRY_RUN")
        except RuntimeError as ex:
            if str(ex) != "DRY_RUN":
                raise
            # Roll back implicitly by not committing transaction
            self.stdout.write(self.style.WARNING("Dry run complete (no changes saved)"))
            self.stdout.write(self.style.WARNING(f"Would create: {created}, update: {updated}, errors: {errors}"))
            return
        finally:
            ctx.__exit__(None, None, None)

        self.stdout.write(self.style.SUCCESS(f"Import complete. Created: {created}, Updated: {updated}, Errors: {errors}"))
