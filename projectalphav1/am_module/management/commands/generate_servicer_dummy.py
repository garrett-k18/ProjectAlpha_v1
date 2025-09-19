from __future__ import annotations
"""
Generate dummy ServicerLoanData rows linked to existing AssetIdHub IDs.

- Links each generated row to an existing hub (no new hubs are created)
- Creates 1 or more monthly snapshots per hub
- Values are randomized but plausible; you can fix a seed for repeatability

Usage examples:
  python manage.py generate_servicer_dummy --per-hub 1 --months 1 --limit 100 --seed 42
  python manage.py generate_servicer_dummy --per-hub 3 --months 6 --start-year 2024 --start-month 7
  python manage.py generate_servicer_dummy --truncate   # deletes existing ServicerLoanData first

Notes:
- The command uses apps.get_model to resolve models dynamically: core.AssetIdHub and am_module.ServicerLoanData
- For each hub, months are generated descending from the start period
"""

import random
from decimal import Decimal
from typing import Iterable, Tuple
import datetime as dt
import calendar

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.apps import apps
from django.utils import timezone


def iter_months(start_year: int, start_month: int, months: int) -> Iterable[Tuple[int, int]]:
    y, m = start_year, start_month
    for _ in range(months):
        yield y, m
        # step back one month
        m -= 1
        if m == 0:
            m = 12
            y -= 1


class Command(BaseCommand):
    help = "Generate dummy ServicerLoanData rows for existing AssetIdHub IDs."

    def add_arguments(self, parser):
        parser.add_argument("--per-hub", type=int, default=1, help="Records to create per hub per month (default 1)")
        parser.add_argument("--months", type=int, default=1, help="How many months of history to generate (default 1)")
        parser.add_argument("--start-year", type=int, default=timezone.now().year, help="Start year (default: current year)")
        parser.add_argument("--start-month", type=int, default=timezone.now().month, help="Start month 1-12 (default: current month)")
        parser.add_argument("--as-of-date", type=str, default=None, help="Optional specific as-of date (YYYY-MM-DD). Overrides start-year/month for first snapshot.")
        parser.add_argument("--limit", type=int, default=0, help="Limit number of hubs processed (0 = all)")
        parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
        parser.add_argument("--truncate", action="store_true", help="Delete all existing ServicerLoanData before generating")
        parser.add_argument("--dry-run", action="store_true", help="Validate only; no writes")

    def handle(self, *args, **opts):
        per_hub: int = opts["per_hub"]
        months: int = opts["months"]
        start_year: int = opts["start_year"]
        start_month: int = opts["start_month"]
        as_of_date_str = opts.get("as_of_date")
        limit: int = opts["limit"]
        seed = opts["seed"]
        truncate: bool = opts["truncate"]
        dry_run: bool = opts["dry_run"]

        if not (1 <= start_month <= 12):
            raise CommandError("start-month must be between 1 and 12")
        if per_hub < 1 or months < 1:
            raise CommandError("per-hub and months must be >= 1")

        if seed is not None:
            random.seed(seed)

        # Parse explicit as_of_date if provided; otherwise use a fixed dummy date (2025-09-19)
        base_as_of_date: dt.date | None = None
        if as_of_date_str:
            try:
                base_as_of_date = dt.datetime.strptime(as_of_date_str, "%Y-%m-%d").date()
            except ValueError:
                raise CommandError("--as-of-date must be in YYYY-MM-DD format")
        else:
            base_as_of_date = dt.date(2025, 9, 19)
        # Force a single snapshot at the selected date
        months = 1
        start_year = base_as_of_date.year
        start_month = base_as_of_date.month

        AssetIdHub = apps.get_model("core", "AssetIdHub")
        ServicerLoanData = apps.get_model("am_module", "ServicerLoanData")

        hubs_qs = AssetIdHub.objects.order_by("id")
        if limit and limit > 0:
            hubs_qs = hubs_qs[:limit]

        created = 0
        ctx = transaction.atomic() if not dry_run else _NullTx()
        try:
            ctx.__enter__()
            if truncate and not dry_run:
                ServicerLoanData.objects.all().delete()

            today = timezone.now().date()

            def rand_money(base: int, spread: int = 100_000) -> Decimal:
                val = base + random.randint(-spread, spread)
                return Decimal(max(val, 0))

            for hub in hubs_qs.iterator():
                # choose a base balance per hub so numbers look coherent across months
                base_bal = random.randint(100_000, 1_000_000)
                base_rate_bp = random.randint(500, 1200)  # 5.00% to 12.00%

                for y, m in iter_months(start_year, start_month, months):
                    # Determine as_of_date and next_due_date
                    if base_as_of_date is not None:
                        day = min(base_as_of_date.day, calendar.monthrange(y, m)[1])
                        as_of_date = dt.date(y, m, day)
                    else:
                        # Default: 15th of the month
                        as_of_date = dt.date(y, m, 15)
                    next_due_date = dt.date(y, m, 1)

                    for _ in range(per_hub):
                        obj = ServicerLoanData(
                            asset_hub=hub,
                            reporting_year=y,
                            reporting_month=m,
                            as_of_date=as_of_date,
                            current_balance=rand_money(base_bal, 75_000),
                            deferred_balance=rand_money(10_000, 10_000),
                            interest_rate=Decimal(base_rate_bp) / Decimal(10000),  # convert bps to rate
                            next_due_date=next_due_date,
                            last_paid_date=as_of_date,
                            term_remaining=random.randint(1, 360),
                            escrow_balance=rand_money(5_000, 5_000),
                            escrow_advance_balance=rand_money(2_500, 2_500),
                            third_party_recov_balance=rand_money(1_000, 1_000),
                            suspense_balance=rand_money(1_000, 1_000),
                            servicer_late_fees=rand_money(2_000, 2_000),
                            other_charges=rand_money(1_500, 1_500),
                            interest_arrears=rand_money(3_000, 3_000),
                            total_debt=None,  # calculate below
                            lien_pos=random.choice([1, 1, 1, 2]),
                            maturity_date=today.replace(year=today.year + random.randint(1, 15)),
                        )
                        # Compute total_debt as a simple sum of balances/fees
                        components = [
                            obj.current_balance or 0,
                            obj.deferred_balance or 0,
                            obj.escrow_balance or 0,
                            obj.escrow_advance_balance or 0,
                            obj.third_party_recov_balance or 0,
                            obj.suspense_balance or 0,
                            obj.servicer_late_fees or 0,
                            obj.other_charges or 0,
                            obj.interest_arrears or 0,
                        ]
                        obj.total_debt = sum(Decimal(c) for c in components)

                        if not dry_run:
                            obj.save()
                        created += 1

            if dry_run:
                raise RuntimeError("DRY_RUN")
        except RuntimeError as ex:
            if str(ex) != "DRY_RUN":
                raise
            self.stdout.write(self.style.WARNING("Dry run complete (no changes saved)"))
            self.stdout.write(self.style.WARNING(f"Would create: {created}"))
            return
        finally:
            ctx.__exit__(None, None, None)

        self.stdout.write(self.style.SUCCESS(f"Created {created} ServicerLoanData records"))


class _NullTx:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False
