"""Management command to import FirmCRM (firm-level CRM) records from a CSV.

WHAT: Loads normalized firm records (FirmCRM) including name, phone, email,
      optional tags, and associated states.
WHY:  Centralizes broker/investor firm metadata for use by MasterCRM contacts.
WHERE: Command lives under `core/management/commands/` for Django auto-discovery.
HOW:  Streams a CSV via csv.DictReader and upserts FirmCRM rows with
      transaction safety.

Expected CSV Columns (case-sensitive):
    - firm_name or name  (required)
    - phone              (optional)
    - email              (optional)
    - states             (optional) comma-separated 2-letter state codes, e.g. "CA,AZ,TX"
    - tag                (optional) one of CRMContactTag values (broker, investor, etc.)

You can override the CSV path with --csv.
"""

import csv
import os
from pathlib import Path
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connections
import dj_database_url

from core.models.model_co_crm import FirmCRM
from core.models.model_co_geoAssumptions import StateReference
from core.models.model_co_lookupTables import CRMContactTag


class Command(BaseCommand):
    """Django entry point for importing FirmCRM rows from CSV."""

    help = (
        "Import or update FirmCRM rows from a CSV file. "
        "Upserts on firm name and updates phone/email/tag/states."
    )

    def add_arguments(self, parser):
        """Register CLI flags for CSV path, dry-run, purge, and database alias."""

        default_csv = str((Path(settings.BASE_DIR) / "DataUploads" / "firm_crm.csv").resolve())

        parser.add_argument(
            "--csv",
            dest="csv_path",
            default=default_csv,
            help="Path to the CSV file (defaults to DataUploads/firm_crm.csv)",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate without writing to DB.",
        )

        parser.add_argument(
            "--purge",
            action="store_true",
            help="Delete all existing FirmCRM records before importing.",
        )

        parser.add_argument(
            "--database",
            dest="database",
            default="default",
            help="Database alias to use (e.g., 'default').",
        )

    def handle(self, *args, **options):
        """Main execution flow invoked by Django."""

        csv_path = options["csv_path"]
        dry_run = options["dry_run"]
        purge = options["purge"]
        db_alias = options["database"]

        # Optional dedicated prod DB alias: --database prod
        # This lets you temporarily point imports at a separate Neon prod URL
        # without hardcoding secrets in code. Set DATABASE_URL_PROD in your env.
        if db_alias == "prod":
            prod_url = os.environ.get("DATABASE_URL_PROD")
            if not prod_url:
                raise CommandError("DATABASE_URL_PROD is not set; cannot use 'prod' database alias.")

            prod_cfg = dj_database_url.parse(prod_url, conn_max_age=600, ssl_require=True)

            # Normalize Neon host (drop -pooler) and set search_path like settings.py
            if "neon.tech" in prod_cfg.get("HOST", ""):
                prod_cfg["HOST"] = prod_cfg["HOST"].replace("-pooler", "")

            prod_cfg.setdefault("OPTIONS", {})
            prod_cfg["OPTIONS"]["options"] = "-c search_path=core,seller_data,public"

            connections.databases["prod"] = prod_cfg

        if not os.path.exists(csv_path):
            raise CommandError(f"CSV not found at: {csv_path}")

        if purge and not dry_run:
            existing_count = FirmCRM.objects.using(db_alias).count()
            FirmCRM.objects.using(db_alias).all().delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Purged {existing_count} existing FirmCRM records from '{db_alias}'"
                )
            )

        created = 0
        updated = 0
        errors = 0
        rowno = 1  # include header row

        # Pre-load states into a dict for quick lookups
        states_by_code = {
            s.state_code.upper(): s
            for s in StateReference.objects.using(db_alias).all()
        }
        self.stdout.write(
            f"[FirmCRM Import] Preloaded {len(states_by_code)} StateReference rows from '{db_alias}'."
        )

        with open(csv_path, newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)

            # Minimal required column check (case-insensitive, allows Firm/FIRM/etc.)
            fieldnames = reader.fieldnames or []
            lower_fieldnames = {fn.lower() for fn in fieldnames}

            if not lower_fieldnames:
                raise CommandError("CSV has no header row.")

            # Accept any firm-name style column: firm_name, name, or Firm
            if not ({"firm_name", "name", "firm"} & lower_fieldnames):
                raise CommandError(
                    "CSV must include a firm name column: one of 'firm_name', 'name', or 'Firm'."
                )

            self.stdout.write(
                f"[FirmCRM Import] CSV header columns: {fieldnames}"
            )
            self.stdout.write(
                f"[FirmCRM Import] Starting import: dry_run={dry_run}, purge={purge}, database='{db_alias}'."
            )

            context = transaction.atomic(using=db_alias) if not dry_run else nullcontext()
            try:
                if not dry_run:
                    context.__enter__()

                for row in reader:
                    rowno += 1
                    try:
                        # Normalize row keys to lowercase for case-insensitive access
                        lower_row = { (k or "").lower(): v for k, v in row.items() }

                        name = (
                            lower_row.get("firm_name")
                            or lower_row.get("name")
                            or lower_row.get("firm")
                            or ""
                        ).strip()
                        if not name:
                            raise ValueError("blank firm_name/name/firm")

                        phone = (lower_row.get("phone") or "").strip() or None
                        email = (lower_row.get("email") or "").strip() or None
                        # Support both plural 'states' and singular 'state' column names
                        states_raw = lower_row.get("states") or lower_row.get("state")
                        tag_raw = (lower_row.get("tag") or "").strip().lower() or None

                        # Default all firms to BROKER when tag is missing/blank.
                        # If an invalid tag is supplied, log it and still fall back to BROKER.
                        if tag_raw:
                            if tag_raw in CRMContactTag.values:
                                tag_value = tag_raw
                            else:
                                self.stderr.write(
                                    f"Row {rowno}: invalid tag '{tag_raw}' for firm '{name}', "
                                    "defaulting to 'broker'."
                                )
                                tag_value = CRMContactTag.BROKER
                        else:
                            tag_value = CRMContactTag.BROKER

                        defaults = {
                            "phone": phone,
                            "email": email,
                            "tag": tag_value,
                        }

                        if dry_run:
                            # Instantiate for validation; skip M2M handling.
                            _ = FirmCRM(name=name, **defaults)
                            updated += 1
                            self.stdout.write(
                                f"[FirmCRM Import][DRY-RUN] Row {rowno}: would upsert firm name='{name}', "
                                f"phone='{phone}', email='{email}', tag='{tag_value}', states_raw='{states_raw}'."
                            )
                        else:
                            # Use phone as the primary identity when available, otherwise fall back to name.
                            lookup = {"phone": phone} if phone else {"name": name}
                            firm, created_flag = FirmCRM.objects.using(db_alias).update_or_create(
                                **lookup,
                                defaults=defaults,
                            )

                            # Handle states M2M if column is present
                            if states_raw is not None:
                                codes = [
                                    c.strip().upper()
                                    for c in (states_raw or "").split(",")
                                    if c.strip()
                                ]
                                state_objs = [
                                    states_by_code[code]
                                    for code in codes
                                    if code in states_by_code
                                ]
                                firm.states.set(state_objs)

                            self.stdout.write(
                                f"[FirmCRM Import] Row {rowno}: {'created' if created_flag else 'updated'} "
                                f"firm id={firm.id} name='{firm.name}', tag='{firm.tag}', "
                                f"states_raw='{states_raw}'."
                            )

                            if created_flag:
                                created += 1
                            else:
                                updated += 1

                    except Exception as exc:  # noqa: BLE001
                        errors += 1
                        self.stderr.write(
                            f"Row {rowno}: error processing firm row: {exc}"
                        )

                if not dry_run:
                    context.__exit__(None, None, None)
            except Exception as exc:  # noqa: BLE001
                if not dry_run:
                    context.__exit__(type(exc), exc, exc.__traceback__)
                raise

        self.stdout.write(
            self.style.SUCCESS(
                f"FirmCRM import complete. created={created}, updated={updated}, "
                f"errors={errors}, dry_run={dry_run}, database='{db_alias}'"
            )
        )


# Python 3.7 compatibility shim for `contextlib.nullcontext` -----------------
try:  # pragma: no cover - compatibility branch
    from contextlib import nullcontext
except ImportError:  # pragma: no cover
    class nullcontext:  # type: ignore[override]
        """Fallback context manager that does nothing."""

        def __init__(self, enter_result=None):
            self.enter_result = enter_result

        def __enter__(self):
            return self.enter_result

        def __exit__(self, *excinfo):
            return False


__all__ = ["Command"]
