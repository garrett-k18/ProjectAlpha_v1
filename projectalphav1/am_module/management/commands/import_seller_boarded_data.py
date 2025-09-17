from __future__ import annotations
"""
Reusable import command for am_module.SellerBoardedData.

Usage examples:
- Basic insert (headers must match model field names):
    python manage.py import_seller_boarded_data --csv path/to/SellerBoardedData.csv

- Dry run (validate only, no DB writes):
    python manage.py import_seller_boarded_data --csv path/to/file.csv --dry-run

- Truncate table first, then import:
    python manage.py import_seller_boarded_data --csv path/to/file.csv --truncate

- Upsert using a natural key (comma-separated fields):
    python manage.py import_seller_boarded_data --csv path/to/file.csv --update-on sellertape_id,acq_trade_id

Notes:
- Empty strings in CSV are converted to None for nullable fields; otherwise kept as-is.
- Unknown columns are ignored; missing columns will default to None/blank if allowed, else error.
"""

import csv
from typing import Dict, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from am_module.models.boarded_data import SellerBoardedData as SBD


class Command(BaseCommand):
    help = "Import SellerBoardedData rows from a CSV file. Headers must match model field names."

    def add_arguments(self, parser):
        parser.add_argument("--csv", dest="csv_path", required=True, help="Path to CSV file to import")
        parser.add_argument("--dry-run", action="store_true", help="Validate only, do not write to DB")
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Delete all existing rows before import (skipped when --dry-run)",
        )
        parser.add_argument(
            "--allow-partial",
            action="store_true",
            help="Do not enforce required-field presence; let DB/defaults handle it.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="bulk_create batch size (default 1000)",
        )
        parser.add_argument(
            "--update-on",
            dest="update_on",
            default="",
            help="Comma-separated list of field names to use as a natural key for upserts (calls update_or_create). If omitted, inserts only.",
        )

    def handle(self, *args, **opts):
        csv_path: str = opts["csv_path"]
        dry_run: bool = bool(opts["dry_run"])
        truncate: bool = bool(opts["truncate"])
        batch_size: int = int(opts["batch_size"]) or 1000
        update_on_fields: List[str] = [s.strip() for s in (opts.get("update_on") or "").split(",") if s.strip()]
        allow_partial: bool = bool(opts.get("allow_partial"))

        # Introspect model fields
        concrete_fields = [f for f in SBD._meta.concrete_fields]
        field_by_name: Dict[str, object] = {f.name: f for f in concrete_fields}
        allowed_fields = [f.name for f in concrete_fields if f.name != "id"]

        # Read CSV
        try:
            with open(csv_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    raise CommandError("CSV has no header row")
                # Warn about unknown columns
                unknown = [h for h in reader.fieldnames if h not in field_by_name]
                if unknown:
                    self.stdout.write(self.style.WARNING(f"Ignoring unknown columns: {', '.join(unknown)}"))
                rows = list(reader)
        except FileNotFoundError:
            raise CommandError(f"CSV not found at: {csv_path}")

        if not rows:
            self.stdout.write(self.style.WARNING("No rows found in CSV. Nothing to do."))
            return

        def clean_value(name: str, val: str):
            """Coerce CSV strings into appropriate Python types per field.

            Rules:
            - Empty string -> None (even if not nullable; model constraint may error and we report it).
            - IntegerField: strip commas and whitespace, cast to int.
            - DecimalField: strip commas, '$', whitespace, cast to Decimal via str.
            - BooleanField: map case-insensitive 'true'/'false'/'1'/'0'.
            - Else: raw string as-is.
            """
            fld = field_by_name.get(name)
            if fld is None:
                return None  # unknown/ignored
            s = (val or "")
            if s == "":
                return None

            from django.db import models as djm
            # Integer
            if isinstance(fld, djm.IntegerField):
                s2 = s.replace(",", "").strip()
                return int(s2)
            # Decimal
            if isinstance(fld, djm.DecimalField):
                from decimal import Decimal
                s2 = s.replace(",", "").replace("$", "").strip()
                return Decimal(s2)
            # Boolean
            if isinstance(fld, djm.BooleanField):
                sl = s.strip().lower()
                if sl in ("1", "true", "t", "yes", "y"):  # permissive
                    return True
                if sl in ("0", "false", "f", "no", "n"):
                    return False
                # Fallthrough: return original string to let Django raise if invalid
                return s
            # Default: string
            return s

        created = 0
        updated = 0
        errors = 0

        ctx = transaction.atomic() if not dry_run else _NullTx()
        try:
            ctx.__enter__()
            if truncate and not dry_run:
                SBD.objects.all().delete()

            # Upsert path using natural key
            if update_on_fields:
                missing_key_cols = [k for k in update_on_fields if k not in allowed_fields]
                if missing_key_cols:
                    raise CommandError(
                        f"update-on fields not present on model or not importable: {', '.join(missing_key_cols)}"
                    )
                for r in rows:
                    defaults = {}
                    lookup = {}
                    for name in allowed_fields:
                        val = clean_value(name, r.get(name, ""))
                        if name in update_on_fields:
                            lookup[name] = val
                        else:
                            defaults[name] = val
                    try:
                        obj, was_created = SBD.objects.update_or_create(defaults=defaults, **lookup)
                        created += 1 if was_created else 0
                        updated += 0 if was_created else 1
                    except Exception as e:
                        errors += 1
                        self.stderr.write(self.style.ERROR(f"Failed upsert for key={lookup}: {e}"))
            else:
                # Insert-only path using bulk_create
                objs = []
                for idx, r in enumerate(rows, start=2):  # header is line 1
                    data = {name: clean_value(name, r.get(name, "")) for name in allowed_fields}
                    try:
                        # Required field hinting (relaxed): only enforce when field has no default/auto and null=False
                        if not allow_partial:
                            missing_required = []
                            for n in allowed_fields:
                                fld = field_by_name[n]
                                val = data.get(n)
                                # Skip if provided
                                if val is not None:
                                    continue
                                # Determine if field supplies its own value
                                has_default = False
                                try:
                                    has_default = bool(getattr(fld, "has_default", lambda: False)()) or (
                                        getattr(fld, "default", object()) is not getattr(__import__('django.db.models.fields', fromlist=['NOT_PROVIDED']).fields, 'NOT_PROVIDED')
                                    )
                                except Exception:
                                    has_default = False
                                auto_field = bool(getattr(fld, "auto_now", False) or getattr(fld, "auto_now_add", False))
                                # Enforce only if truly required by DB-level null=False and no default/auto
                                if getattr(fld, "null", False) is False and not has_default and not auto_field:
                                    missing_required.append(n)
                            if missing_required:
                                raise ValueError(f"Missing required fields: {', '.join(missing_required)}")
                        objs.append(SBD(**data))
                    except Exception as e:
                        errors += 1
                        self.stderr.write(self.style.ERROR(f"Row {idx} skipped: {e} | data={data}"))
                # Bulk create in batches
                if not dry_run and objs:
                    for i in range(0, len(objs), batch_size):
                        SBD.objects.bulk_create(objs[i : i + batch_size])
                    created += len(objs)

            if dry_run:
                self.stdout.write(self.style.WARNING("Dry run complete (no DB writes)."))
            self.stdout.write(
                self.style.SUCCESS(
                    f"Import complete. created={created}, updated={updated}, errors={errors}, dry_run={dry_run}"
                )
            )
            ctx.__exit__(None, None, None)
        except Exception as e:
            ctx.__exit__(type(e), e, e.__traceback__)
            raise


class _NullTx:
    """No-op context manager to mirror transaction.atomic when --dry-run."""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False
