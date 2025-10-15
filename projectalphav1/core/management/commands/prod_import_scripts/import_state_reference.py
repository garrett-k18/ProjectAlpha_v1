from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from decimal import Decimal, InvalidOperation
import csv
import os
from pathlib import Path
from django.conf import settings

from core.models.assumptions import StateReference


class Command(BaseCommand):
    help = (
        "Import or update StateReference rows from DataUploads/state_ref.csv. "
        "Upserts on state_code (State Abbr)."
    )

    def add_arguments(self, parser):
        # Default CSV at project-level DataUploads/state_ref.csv
        default_csv = str((Path(settings.BASE_DIR) / "DataUploads" / "state_ref.csv").resolve())
        parser.add_argument(
            "--csv",
            dest="csv_path",
            default=default_csv,
            help="Path to the CSV file (defaults to DataUploads/state_ref.csv)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate without writing to DB.",
        )
        parser.add_argument(
            "--purge",
            action="store_true",
            help="Delete all existing StateReference records before importing.",
        )
        parser.add_argument(
            "--database",
            dest="database",
            default="default",
            help="Database alias to use (e.g., 'default').",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        dry_run = options["dry_run"]
        purge = options["purge"]
        db_alias = options["database"]

        if not os.path.exists(csv_path):
            raise CommandError(f"CSV not found at: {csv_path}")

        # Purge existing data if requested
        if purge and not dry_run:
            count = StateReference.objects.using(db_alias).count()
            StateReference.objects.using(db_alias).all().delete()
            self.stdout.write(
                self.style.WARNING(f"Purged {count} existing StateReference records")
            )

        created = 0
        updated = 0
        errors = 0
        rowno = 1

        def to_int(val, default=0):
            try:
                s = str(val).strip()
                if s == "" or s.lower() == "none":
                    return default
                return int(Decimal(s))
            except Exception:
                return default

        def to_decimal(val, default=Decimal("0")):
            try:
                s = str(val).strip()
                if s == "" or s.lower() == "none":
                    return default
                return Decimal(s)
            except (InvalidOperation, ValueError):
                return default

        def to_bool_from_judicial(val):
            # Judicial column contains "Judicial" or "Non-Judicial"
            s = str(val).strip().lower()
            if s.startswith("judicial"):
                return True
            return False

        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            missing_cols = [
                c
                for c in [
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
                if c not in reader.fieldnames
            ]
            if missing_cols:
                raise CommandError(
                    f"CSV is missing required columns: {', '.join(missing_cols)}"
                )

            # Use a transaction so either all rows apply or none if not dry-run
            ctx = transaction.atomic(using=db_alias) if not dry_run else nullcontext()
            try:
                if not dry_run:
                    ctx.__enter__()
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

                        # Pick one: map DIL_CFK Cost to cfk_cost_avg and leave dil_cost_avg 0.00
                        cfk_cost_avg = to_decimal(row.get("DIL_CFK Cost"))
                        dil_cost_avg = Decimal("0.00")

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
                            # Validate by constructing but not saving
                            _ = StateReference(state_code=state_code, **defaults)
                            updated += 1  # count as processed
                        else:
                            obj, created_flag = StateReference.objects.using(db_alias).update_or_create(
                                state_code=state_code, defaults=defaults
                            )
                            if created_flag:
                                created += 1
                            else:
                                updated += 1
                    except Exception as e:
                        errors += 1
                        self.stderr.write(
                            f"Row {rowno}: error processing state_code='{row.get('State Abbr', '')}': {e}"
                        )
                if not dry_run:
                    ctx.__exit__(None, None, None)
            except Exception as e:
                if not dry_run:
                    ctx.__exit__(type(e), e, e.__traceback__)
                raise

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. created={created}, updated={updated}, errors={errors}, dry_run={dry_run}"
            )
        )


# Python 3.7+ compatibility: contextlib.nullcontext
try:
    from contextlib import nullcontext
except ImportError:  # pragma: no cover
    class nullcontext:
        def __init__(self, enter_result=None):
            self.enter_result = enter_result
        def __enter__(self):
            return self.enter_result
        def __exit__(self, *excinfo):
            return False
