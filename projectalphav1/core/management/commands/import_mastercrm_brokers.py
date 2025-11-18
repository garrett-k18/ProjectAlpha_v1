"""Management command to import broker MasterCRM contacts from a CSV.

WHAT: Loads broker-level contacts into MasterCRM, linking them to FirmCRM and
      StateReference (M2M) using the normalized schema.
WHY:  Seeds/updates the broker CRM directory from a flat file export.
WHERE: Command lives under `core/management/commands/` for Django auto-discovery.
HOW:  Streams a CSV via csv.DictReader, upserts MasterCRM rows, and uses the
      MasterCRM.firm property and states M2M for associations.

Expected CSV Columns (case-sensitive):
    - name or contact_name   (required)
    - email                  (recommended, used as primary upsert key when present)
    - phone                  (optional)
    - firm                   (optional firm name; creates/links FirmCRM via property)
    - city                   (optional)
    - states                 (optional) comma-separated 2-letter state codes, e.g. "CA,AZ,TX"
    - tag                    (optional) one of CRMContactTag / MasterCRM.ContactTag values;
                              defaults to 'broker' when blank/invalid.

Upsert Strategy:
    - If email is provided: update_or_create on email.
    - If email is blank:   update_or_create on contact_name only (best-effort).
"""

import csv
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connections
import dj_database_url

from core.models.model_co_crm import MasterCRM
from core.models.model_co_geoAssumptions import StateReference
from core.models.model_co_lookupTables import YesNo


class Command(BaseCommand):
    """Django entry point for importing broker MasterCRM rows from CSV."""

    help = (
        "Import or update broker MasterCRM records from a CSV file. "
        "Upserts on email when available and associates firms and states."
    )

    def add_arguments(self, parser):
        """Register CLI flags for CSV path, dry-run, purge, and database alias."""

        default_csv = str((Path(settings.BASE_DIR) / "DataUploads" / "broker_crm.csv").resolve())

        parser.add_argument(
            "--csv",
            dest="csv_path",
            default=default_csv,
            help="Path to the CSV file (defaults to DataUploads/broker_crm.csv)",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate without writing to DB.",
        )

        parser.add_argument(
            "--purge",
            action="store_true",
            help=(
                "Delete existing broker MasterCRM records (tag='broker') before importing. "
                "Does not touch other contact types."
            ),
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

        if db_alias == "proddb":
            # NOTE: env var name intentionally matches user's .env key: 'proddb'
            prod_url = os.environ.get("proddb")
            if not prod_url:
                raise CommandError("proddb is not set; cannot use 'proddb' database alias.")

            prod_cfg = dj_database_url.parse(prod_url, conn_max_age=600, ssl_require=True)

            # Ensure required Django DB config keys are present
            # TIME_ZONE and AUTOCOMMIT/ATOMIC_REQUESTS are accessed by Django's
            # database wrapper, so we mirror the global defaults here.
            prod_cfg.setdefault("TIME_ZONE", settings.TIME_ZONE)
            prod_cfg.setdefault("AUTOCOMMIT", True)
            prod_cfg.setdefault("ATOMIC_REQUESTS", False)

            if "neon.tech" in prod_cfg.get("HOST", ""):
                prod_cfg["HOST"] = prod_cfg["HOST"].replace("-pooler", "")

            prod_cfg.setdefault("OPTIONS", {})
            prod_cfg["OPTIONS"]["options"] = "-c search_path=core,seller_data,public"

            # Register the dynamic proddb config
            connections.databases["proddb"] = prod_cfg

        if not os.path.exists(csv_path):
            raise CommandError(f"CSV not found at: {csv_path}")

        broker_tag = MasterCRM.ContactTag.BROKER

        if purge and not dry_run:
            qs = MasterCRM.objects.using(db_alias).filter(tag=broker_tag)
            existing_count = qs.count()
            qs.delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Purged {existing_count} existing broker MasterCRM records from '{db_alias}'"
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

        # Use utf-8-sig with errors='replace' so that non-UTF-8 characters from
        # Excel/Windows-1252 exports (e.g., curly quotes, en dashes) don't crash
        # the import. They will be replaced with the Unicode replacement char.
        with open(csv_path, newline="", encoding="utf-8-sig", errors="replace") as csv_file:
            reader = csv.DictReader(csv_file)

            if not reader.fieldnames:
                raise CommandError("CSV has no header row.")

            # Header validation: accept 'name', 'contact_name', or 'Contact Name' (case-insensitive)
            lower_fieldnames = {fn.lower() for fn in reader.fieldnames}
            if not ({"name", "contact_name", "contact name"} & lower_fieldnames):
                raise CommandError("CSV must include a 'name' or 'contact_name' column.")

            context = transaction.atomic(using=db_alias) if not dry_run else nullcontext()
            try:
                if not dry_run:
                    context.__enter__()

                for row in reader:
                    rowno += 1
                    try:
                        # Normalize keys to lowercase for case-insensitive access
                        lower_row = {(k or "").lower(): v for k, v in row.items()}

                        # Skip completely blank lines (no meaningful data in any column)
                        if not any((v or "").strip() for v in lower_row.values()):
                            continue

                        # Accept both snake_case and space-separated contact name headers
                        # e.g., "Contact Name" -> "contact name" when lowercased.
                        name = (
                            lower_row.get("name")
                            or lower_row.get("contact_name")
                            or lower_row.get("contact name")
                            or ""
                        ).strip()
                        if not name:
                            raise ValueError("blank name/contact_name")

                        email = (lower_row.get("email") or "").strip() or None
                        phone = (lower_row.get("phone") or "").strip() or None
                        firm_name = (lower_row.get("firm") or "").strip() or None
                        city = (lower_row.get("city") or "").strip() or None
                        # Support both plural 'states' and singular 'state' column names
                        states_raw = lower_row.get("states") or lower_row.get("state")
                        tag_raw = (lower_row.get("tag") or "").strip().lower() or None
                        preferred_raw = (lower_row.get("preferred") or "").strip().lower()

                        # Normalize tag; default to broker when invalid/blank
                        if tag_raw and tag_raw in MasterCRM.ContactTag.values:
                            tag_value = tag_raw
                        else:
                            tag_value = broker_tag

                        # Map preferred flag to Yes/No choices when present
                        if preferred_raw in ("yes", "y", "true", "1"):  # type: ignore[comparison-overlap]
                            preferred_value = YesNo.YES
                        elif preferred_raw in ("no", "n", "false", "0"):
                            preferred_value = YesNo.NO
                        else:
                            preferred_value = None

                        # Build defaults for update_or_create
                        defaults = {
                            "contact_name": name,
                            "phone": phone,
                            "city": city,
                            "tag": tag_value,
                            "preferred": preferred_value,
                        }
                        if email:
                            defaults["email"] = email

                        if dry_run:
                            # Validate fields; skip relationships
                            _ = MasterCRM(**defaults)
                            updated += 1
                        else:
                            lookup = {}
                            if email:
                                lookup["email"] = email
                            else:
                                # Fallback: best-effort upsert on name+tag
                                lookup["contact_name"] = name
                                lookup["tag"] = broker_tag

                            instance, created_flag = (
                                MasterCRM.objects.using(db_alias).update_or_create(
                                    **lookup,
                                    defaults=defaults,
                                )
                            )

                            # Associate firm via property if provided
                            if firm_name:
                                instance.firm = firm_name
                                instance.save(update_fields=["firm_ref"])

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
                                instance.states.set(state_objs)

                            if created_flag:
                                created += 1
                            else:
                                updated += 1

                    except Exception as exc:  # noqa: BLE001
                        errors += 1
                        self.stderr.write(
                            f"Row {rowno}: error processing broker row: {exc}"
                        )

                if not dry_run:
                    context.__exit__(None, None, None)
            except Exception as exc:  # noqa: BLE001
                if not dry_run:
                    context.__exit__(type(exc), exc, exc.__traceback__)
                raise

        self.stdout.write(
            self.style.SUCCESS(
                f"MasterCRM broker import complete. created={created}, updated={updated}, "
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
