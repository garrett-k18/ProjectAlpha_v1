"""Management command to import state reference rows from a CSV into PostgreSQL.

WHAT: Loads the canonical `StateReference` data that powers judicial/non-judicial
      stratifications, foreclosure timelines, and cost assumptions.
WHY:  Keeps production data current by upserting the authoritative spreadsheet.
WHERE: Command lives directly under `core/management/commands/` so Django can
       auto-discover it when `manage.py` runs.
HOW:  Stream a CSV via Python's `csv.DictReader`, validate, and perform
      `update_or_create` calls with transaction safety and multi-database support.

"""

from decimal import Decimal, InvalidOperation
import csv
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models.model_co_geoAssumptions import StateReference


class Command(BaseCommand):
    """Django entry point that orchestrates the CSV import logic."""

    help = (
        "Import or update StateReference rows from DataUploads/state_ref.csv. "
        "Upserts on state_code (State Abbr)."
    )

    def add_arguments(self, parser):
        """Register CLI flags with plenty of guard rails for operators."""

        # WHAT: Pre-compute the default CSV path.
        # WHY: Avoid duplicating string literals in multiple places.
        # HOW: Use BASE_DIR/DataUploads/state_ref.csv to support local + prod.
        default_csv = str((Path(settings.BASE_DIR) / "DataUploads" / "state_ref.csv").resolve())

        # WHAT: Allow overriding the CSV location.
        # WHY: Operators may stage new files elsewhere before promoting to Git.
        # HOW: default provided above; accepts absolute or relative paths.
        parser.add_argument(
            "--csv",
            dest="csv_path",
            default=default_csv,
            help="Path to the CSV file (defaults to DataUploads/state_ref.csv)",
        )

        # WHAT: Toggle dry-run mode.
        # WHY: Lets analysts validate parsing without mutating the database.
        # HOW: Short opt-in flag, zero arguments.
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate without writing to DB.",
        )

        # WHAT: Optional purge of existing rows prior to import.
        # WHY: Enables total refreshes when the source of truth radically changes.
        # HOW: Guarded by `--dry-run` to ensure no writes occur during validation.
        parser.add_argument(
            "--purge",
            action="store_true",
            help="Delete all existing StateReference records before importing.",
        )

        # WHAT: Support Django's multi-database routing.
        # WHY: Production Railway deploy uses named aliases; we need explicit control.
        # HOW: Mirror Django's `--database` convention from built-in commands.
        parser.add_argument(
            "--database",
            dest="database",
            default="default",
            help="Database alias to use (e.g., 'default').",
        )

    def handle(self, *args, **options):
        """Main execution flow invoked by Django."""

        # Extract runtime options with clear naming.
        csv_path = options["csv_path"]
        dry_run = options["dry_run"]
        purge = options["purge"]
        db_alias = options["database"]

        # Fail fast if the CSV does not exist to avoid silent misconfigurations.
        if not os.path.exists(csv_path):
            raise CommandError(f"CSV not found at: {csv_path}")

        # Optionally remove existing data (no transaction yet so that purge stands alone).
        if purge and not dry_run:
            existing_count = StateReference.objects.using(db_alias).count()
            StateReference.objects.using(db_alias).all().delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Purged {existing_count} existing StateReference records from '{db_alias}'"
                )
            )

        # Counters used for final telemetry.
        created = 0
        updated = 0
        errors = 0
        rowno = 1  # include header row for easier debugging

        # Helper utilities -------------------------------------------------

        def to_int(value, default=0):
            """Convert arbitrary CSV strings to integers with graceful fallback."""

            try:
                cleaned = str(value).strip()
                if cleaned == "" or cleaned.lower() == "none":
                    return default
                return int(Decimal(cleaned))
            except Exception:
                return default

        def to_decimal(value, default=Decimal("0")):
            """Convert CSV input into Decimal instances for financial accuracy."""

            try:
                cleaned = str(value).strip()
                if cleaned == "" or cleaned.lower() == "none":
                    return default
                return Decimal(cleaned)
            except (InvalidOperation, ValueError):
                return default

        def to_bool_from_judicial(value):
            """Interpret the Judicial/Non-Judicial string into a boolean flag."""

            text = str(value).strip().lower()
            if text.startswith("judicial"):
                return True
            return False

        # CSV ingestion ----------------------------------------------------

        with open(csv_path, newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)

            # Validate required headers to catch human editing mistakes early.
            required_columns = [
                "State Abbr",
                "State",
                "Judicial",
                "Tax Rate",
                "Insurance %",
                "FC Fees",
                "Eviction Duration",
                "FC Duration",
                "DIL Duration",
                "REO Market Duration (Months)",
                "REO Ext",
                "Rehab Duration",
                "Transfer Tax",
                "Annual Value Adjustment",
                "DIL_CFK Cost",
            ]
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            if missing_columns:
                raise CommandError(
                    f"CSV is missing required columns: {', '.join(missing_columns)}"
                )

            # Create a transaction when writing, skip when dry-running to avoid locks.
            context = transaction.atomic(using=db_alias) if not dry_run else nullcontext()
            try:
                if not dry_run:
                    context.__enter__()

                for row in reader:
                    rowno += 1
                    try:
                        state_code = str(row.get("State Abbr", "")).strip().upper()
                        if not state_code:
                            raise ValueError("blank State Abbr")

                        state_name = str(row.get("State", "")).strip()
                        judicial = to_bool_from_judicial(row.get("Judicial", ""))

                        property_tax_rate = to_decimal(row.get("Tax Rate"))
                        insurance_rate_avg = to_decimal(row.get("Insurance %"))
                        fc_legal_fees_avg = to_decimal(row.get("FC Fees"))

                        fc_state_months = to_int(row.get("FC Duration"))
                        eviction_duration = to_int(row.get("Eviction Duration"))
                        rehab_duration = to_int(row.get("Rehab Duration"))
                        reo_marketing_duration = to_int(row.get("REO Market Duration (Months)"))
                        reo_local_market_ext_duration = to_int(row.get("REO Ext"))
                        dil_duration_avg = to_int(row.get("DIL Duration"))

                        transfer_tax_rate = to_decimal(row.get("Transfer Tax"))
                        value_adjustment_annual = to_decimal(row.get("Annual Value Adjustment"))

                        # Map CFK/DIL columns to current schema semantics.
                        cfk_cost_avg = to_decimal(row.get("DIL_CFK Cost"))
                        dil_cost_avg = Decimal("0.00")

                        # Compose defaults dictionary for update_or_create.
                        defaults = {
                            "state_name": state_name,
                            "judicialvsnonjudicial": judicial,
                            "fc_state_months": fc_state_months,
                            "eviction_duration": eviction_duration,
                            "rehab_duration": rehab_duration,
                            "reo_marketing_duration": reo_marketing_duration,
                            "reo_local_market_ext_duration": reo_local_market_ext_duration,
                            "dil_duration_avg": dil_duration_avg,
                            "property_tax_rate": property_tax_rate,
                            "transfer_tax_rate": transfer_tax_rate,
                            "insurance_rate_avg": insurance_rate_avg,
                            "fc_legal_fees_avg": fc_legal_fees_avg,
                            "dil_cost_avg": dil_cost_avg,
                            "cfk_cost_avg": cfk_cost_avg,
                            "value_adjustment_annual": value_adjustment_annual,
                        }

                        if dry_run:
                            # Construct model instance to trigger Django validators.
                            _ = StateReference(state_code=state_code, **defaults)
                            updated += 1  # Count as processed during dry-run.
                        else:
                            _, created_flag = StateReference.objects.using(db_alias).update_or_create(
                                state_code=state_code,
                                defaults=defaults,
                            )
                            if created_flag:
                                created += 1
                            else:
                                updated += 1
                    except Exception as exc:
                        errors += 1
                        self.stderr.write(
                            f"Row {rowno}: error processing state_code='{row.get('State Abbr', '')}': {exc}"
                        )

                if not dry_run:
                    context.__exit__(None, None, None)
            except Exception as exc:
                if not dry_run:
                    context.__exit__(type(exc), exc, exc.__traceback__)
                raise

        # Emit summary stats for operator awareness.
        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. created={created}, updated={updated}, errors={errors}, dry_run={dry_run}, database='{db_alias}'"
            )
        )


# Python 3.7 compatibility shim for `contextlib.nullcontext` -----------------
try:  # pragma: no cover - compatibility branch
    from contextlib import nullcontext
except ImportError:  # pragma: no cover
    class nullcontext:  # type: ignore
        """Fallback context manager that does nothing."""

        def __init__(self, enter_result=None):
            self.enter_result = enter_result

        def __enter__(self):
            return self.enter_result

        def __exit__(self, *excinfo):
            return False


__all__ = ["Command"]
