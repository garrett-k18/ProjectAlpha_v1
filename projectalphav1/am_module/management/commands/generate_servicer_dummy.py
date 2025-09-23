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
        parser.add_argument("--min-hub-id", type=int, default=None, help="Minimum AssetIdHub.id to include (inclusive)")
        parser.add_argument("--max-hub-id", type=int, default=None, help="Maximum AssetIdHub.id to include (inclusive)")
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
        min_hub_id = opts.get("min_hub_id")
        max_hub_id = opts.get("max_hub_id")
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
        if min_hub_id is not None:
            hubs_qs = hubs_qs.filter(id__gte=min_hub_id)
        if max_hub_id is not None:
            hubs_qs = hubs_qs.filter(id__lte=max_hub_id)
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
                            investor_id=random.randint(1000, 9999),
                            servicer_id=random.randint(100, 200),
                            previous_servicer_id=random.choice([None, random.randint(100, 200)]),
                            reporting_year=y,
                            reporting_month=m,
                            as_of_date=as_of_date,
                            address=f"{random.randint(100, 9999)} Main St",
                            city="Anytown",
                            state="CA",
                            zip_code=f"{random.randint(10000, 99999)}",
                            avm_date=as_of_date - dt.timedelta(days=random.randint(5, 30)),
                            avm_value=rand_money(base_bal, 50_000),
                            bpo_asis_value=rand_money(base_bal, 40_000),
                            bpo_asis_date=as_of_date - dt.timedelta(days=random.randint(10, 45)),
                            bpo_arv_value=rand_money(base_bal + 50000, 60_000),
                            occupnacy=random.choice(['Owner Occupied', 'Tenant Occupied', 'Vacant']),
                            borrower_last_name='Smith',
                            borrower_first_name='John',
                            current_fico=random.randint(500, 850),
                            current_fico_date=as_of_date - dt.timedelta(days=random.randint(15, 60)),
                            current_balance=rand_money(base_bal, 75_000),
                            deferred_balance=rand_money(10_000, 10_000),
                            interest_rate=Decimal(base_rate_bp) / Decimal(10000),
                            next_due_date=next_due_date,
                            last_paid_date=as_of_date - dt.timedelta(days=30),
                            current_pi=rand_money(1500, 500),
                            current_ti=rand_money(300, 100),
                            piti=rand_money(1800, 600),
                            term_remaining=random.randint(1, 360),
                            escrow_balance=rand_money(5_000, 5_000),
                            escrow_advance_balance=rand_money(2_500, 2_500),
                            third_party_recov_balance=rand_money(1_000, 1_000),
                            suspense_balance=rand_money(1_000, 1_000),
                            servicer_late_fees=rand_money(2_000, 2_000),
                            other_charges=rand_money(1_500, 1_500),
                            interest_arrears=rand_money(3_000, 3_000),
                            total_debt=None,  # calculated below
                            lien_pos=random.choice([1, 1, 1, 2]),
                            maturity_date=today.replace(year=today.year + random.randint(1, 15)),
                            default_rate=Decimal(base_rate_bp + 200) / Decimal(10000),
                            origination_date=today.replace(year=today.year - random.randint(2, 10)),
                            origination_balance=rand_money(base_bal + 100000, 50000),
                            origination_interest_rate=Decimal(base_rate_bp - 100) / Decimal(10000),
                            original_appraised_value=rand_money(base_bal + 120000, 60000),
                            original_appraised_date=today.replace(year=today.year - random.randint(2, 10)),
                            arm_flag=random.choice([True, False]),
                            escrowed_flag=random.choice([True, False]),
                            loan_warning=random.choice([None, 'High LTV']),
                            mba=random.choice([True, False]),
                            bk_flag=random.choice([True, False, False]),
                            # bk_ch is a BooleanField in the current model; keep to boolean to avoid type issues
                            bk_ch=random.choice([None, True, False]),
                            bk_current_status=random.choice([None, 'Active', 'Discharged']),
                            bk_plan_start_date=random.choice([None, as_of_date - dt.timedelta(days=180)]),
                            bk_plan_end_date=random.choice([None, as_of_date + dt.timedelta(days=180)]),
                            bk_plan_length=random.choice([None, 36, 60]),
                            bk_post_petition_due_date=random.choice([None, as_of_date - dt.timedelta(days=30)]),
                            date_motion_for_relief_filed=random.choice([None, as_of_date - dt.timedelta(days=90)]),
                            date_object_to_confirmation_filed=random.choice([None, as_of_date - dt.timedelta(days=85)]),
                            date_of_meeting_of_creditors=random.choice([None, as_of_date - dt.timedelta(days=75)]),
                            date_proof_of_claim_filed=random.choice([None, as_of_date - dt.timedelta(days=70)]),
                            relief_date=random.choice([None, as_of_date - dt.timedelta(days=45)]),
                            prepetition_unapplied_bal=rand_money(500, 500),
                            stipulation_unapplied_bal=rand_money(500, 500),
                            fc_flag=random.choice([True, False, False]),
                            actual_fc_sale_date=random.choice([None, as_of_date + dt.timedelta(days=60)]),
                            date_referred_to_fc_atty=random.choice([None, as_of_date - dt.timedelta(days=120)]),
                            fc_completion_date=random.choice([None, as_of_date + dt.timedelta(days=120)]),
                            fc_status=random.choice([None, 'Active', 'On Hold', 'Complete']),
                            foreclosure_business_area_status=random.choice([None, 'In Review', 'Approved', 'Completed']),
                            foreclosure_business_area_status_date=random.choice([None, as_of_date - dt.timedelta(days=10)]),
                            days_in_foreclosure=random.randint(0, 720),
                            date_breach_letter_sent=random.choice([None, as_of_date - dt.timedelta(days=150)]),
                            dil_completion_date=random.choice([None, as_of_date + dt.timedelta(days=90)]),
                            loss_mitigation_business_area_status=random.choice([None, 'Offer Sent', 'Active', 'Closed']),
                            loss_mitigation_business_area_status_date=random.choice([None, as_of_date - dt.timedelta(days=20)]),
                            bk_discharge_date=random.choice([None, as_of_date - dt.timedelta(days=random.randint(30, 365))]),
                            bk_dismissed_date=random.choice([None, as_of_date - dt.timedelta(days=random.randint(30, 365))]),
                            bk_filed_date=random.choice([None, as_of_date - dt.timedelta(days=random.randint(60, 730))]),
                            is_a_contested_fc=random.choice([True, False]),
                            reason_for_default=random.choice(['Job Loss', 'Medical', 'Divorce', 'Other']),
                            loan_modification_date=random.choice([None, as_of_date - dt.timedelta(days=random.randint(90, 1000))]),
                            loan_modification_status=random.choice([None, 'Active', 'Complete']),
                            modification_type=random.choice([None, 'Rate', 'Term', 'Forbearance']),
                            workout_option=random.choice([None, 'Forbearance', 'Modification', 'Repayment Plan']),
                            number_of_payments=random.randint(6, 60),
                            repayment_plan_agreement_date=random.choice([None, as_of_date - dt.timedelta(days=120)]),
                            repayment_plan_start_date=random.choice([None, as_of_date - dt.timedelta(days=110)]),
                            repayment_plan_status=random.choice([None, 'Active', 'Complete']),
                            repay_plan_type=random.choice([None, 'Short-term', 'Long-term']),
                            forgive_amount=rand_money(2_000, 1_000),
                            balance_after_forgive=rand_money(base_bal - 5_000, 5_000),
                            # Correct field types
                            mod_extended_maturity=random.choice([None, today + dt.timedelta(days=random.randint(180, 365*5))]),
                            mod_forbearance=rand_money(1_000, 1_000),
                            mod_forgiven=rand_money(1_000, 1_000),
                            modified_first_payment_date=random.choice([None, as_of_date + dt.timedelta(days=30)]),
                            total_capitalized_by_mod=rand_money(3_000, 2_000),
                            post_modification_principal_balance=rand_money(base_bal - 10000, 5000),
                            property_condition_from_inspection=random.choice(['Good', 'Fair', 'Poor']),
                            neighborhood_condition=random.choice(['Good', 'Fair', 'Poor']),
                            date_inspection_completed=random.choice([None, as_of_date - dt.timedelta(days=14)]),
                            first_time_vacant_date=random.choice([None, as_of_date - dt.timedelta(days=200)]),
                            forceplaced_flood_insurance=rand_money(500, 300),
                            forceplaced_hazard_insurance=rand_money(500, 300),
                            is_house_for_sale=random.choice([True, False]),
                            property_county=random.choice(['Los Angeles', 'Cook', 'Harris', 'Maricopa']),
                            borrower_home_phone='555-123-4567',
                            borrower_count=random.choice([1, 2]),
                            co_borrower_fico=random.choice([None, random.randint(500, 850)]),
                            co_borrower_fico_date=random.choice([None, as_of_date - dt.timedelta(days=45)]),
                            follow_up_date=random.choice([None, as_of_date + dt.timedelta(days=14)]),
                            last_contact_outcome=random.choice([None, 'Left VM', 'Spoke', 'No Answer']),
                            last_successful_contact_date=random.choice([None, as_of_date - dt.timedelta(days=7)]),
                            promise_amount=rand_money(1_000, 500),
                            promise_date=random.choice([None, as_of_date + dt.timedelta(days=10)]),
                            right_party_type=random.choice([None, 'Borrower', 'Attorney', 'Agent']),
                            right_party_date=random.choice([None, as_of_date - dt.timedelta(days=5)]),
                            single_point_of_contact=random.choice([True, False]),
                            next_arm_rate_change_date=random.choice([None, as_of_date + dt.timedelta(days=60)]),
                            convert_to_fixed_rate=random.choice([True, False]),
                            max_rate=Decimal(base_rate_bp + 400) / Decimal(10000),
                            min_rate=Decimal(max(base_rate_bp - 400, 100)) / Decimal(10000),
                            first_periodic_rate_cap=Decimal('0.0200'),
                            periodic_rate_cap=Decimal('0.0200'),
                            life_cap=Decimal('0.0600'),
                            arm_audit_status=random.choice([None, 'Passed', 'Failed']),
                            arm_first_rate_change_date=random.choice([None, as_of_date + dt.timedelta(days=90)]),
                            is_pay_option_arm=random.choice([True, False]),
                            pay_option_negative_am_factor=random.choice([None, Decimal('0.10')]),
                            within_pay_option_period=random.choice([True, False]),
                            mi_company_name=random.choice([None, 'MGIC', 'Radian', 'Genworth']),
                            mi_active_policy=random.choice([True, False]),
                            mi_certificate_number=random.choice([None, f'MI-{random.randint(100000, 999999)}']),
                            mi_claim=rand_money(2_500, 1_000),
                            mi_claim_status=random.choice([None, 'Filed', 'Paid', 'Denied']),
                            mi_coverage=random.choice([None, Decimal('0.25')]),
                            mi_date_closed=random.choice([None, as_of_date - dt.timedelta(days=400)]),
                            mi_date_paid=random.choice([None, as_of_date - dt.timedelta(days=200)]),
                            mi_last_review_date=random.choice([None, as_of_date - dt.timedelta(days=60)]),
                            mi_paid_amount=rand_money(5_000, 3_000),
                            mi_rescind_date=random.choice([None, as_of_date - dt.timedelta(days=300)]),
                            mi_rescind_reason=random.choice([None, 'Non-disclosure', 'Ineligible']),
                            mi_claim_filed_date=random.choice([None, as_of_date - dt.timedelta(days=220)]),
                            pif_date=random.choice([None, as_of_date + dt.timedelta(days=365)]),
                            pif_quote_date=random.choice([None, as_of_date + dt.timedelta(days=350)]),
                            res_service_fee_paid=rand_money(500, 300),
                            resolution_corporate_advance_balance=rand_money(2_000, 1_000),
                            resolution_escrow_advance=rand_money(1_000, 500),
                            resolution_fees=rand_money(750, 400),
                            resolution_post_date=random.choice([None, as_of_date + dt.timedelta(days=30)]),
                            resolution_proceeds=rand_money(10_000, 5_000),
                            resolution_type=random.choice([None, 'FC Sale', 'REO', 'Settled']),
                            resolution_balance=rand_money(base_bal - 50_000, 10_000),
                            ss_complete=random.choice([True, False]),
                            ss_proceeds_rcvd=rand_money(15_000, 5_000),
                            deferred_advance_balance=rand_money(2_000, 1_000),
                            acquired_date=today - dt.timedelta(days=random.randint(200, 2000)),
                            inactive_date=random.choice([None, today - dt.timedelta(days=random.randint(10, 300))]),
                            prim_stat=random.choice(['Active', 'Inactive', 'Closed']),
                            noi_expiration_date=random.choice([None, as_of_date + dt.timedelta(days=45)]),
                            total_principal=rand_money(150_000, 30_000),
                            total_interest=rand_money(50_000, 10_000),
                            non_recoverable_principal=rand_money(1_000, 500),
                            non_recoverable_interest=rand_money(800, 400),
                            non_recoverable_escrow=rand_money(600, 300),
                            non_recoverable_fees=rand_money(400, 200),
                            non_recoverable_corporate_advance=rand_money(700, 300),
                            asset_manager=random.choice(['AM1', 'AM2', 'AM3']),
                            collateral_count=random.randint(1, 3),
                            current_loan_term=random.randint(60, 360),
                            current_neg_am_bal=rand_money(0, 1000),
                            deferred_interest=rand_money(0, 2000),
                            deferred_principal=rand_money(0, 2000),
                            first_due_date=today - dt.timedelta(days=random.randint(365, 3650)),
                            interest_method=random.choice(['Simple', 'Daily Accrual']),
                            last_escrow_analysis_date=random.choice([None, as_of_date - dt.timedelta(days=180)]),
                            legal_status=random.choice([None, 'Collection', 'Litigation', 'None']),
                            loan_age=random.randint(1, 360),
                            servicing_specialist=random.choice(['Spec1', 'Spec2', 'Spec3']),
                            mers_num=f'1000111{random.randint(1000000000, 9999999999)}',
                            trust_id=f'TRUST-{random.randint(100, 999)}',
                            original_first_payment_date=today - dt.timedelta(days=random.randint(365, 3650)),
                            original_loan_term=random.randint(120, 360),
                            original_maturity_date=today + dt.timedelta(days=random.randint(365, 3650)),
                            original_amt=rand_money(base_bal + 150_000, 80_000),
                            loan_purpose=random.choice(['Purchase', 'Refinance']),
                            acquisition_or_sale_identifier=random.choice([None, f'SALE-{random.randint(1000,9999)}']),
                            pre_modification_balance=rand_money(base_bal + 20_000, 10_000),
                            pre_modification_coupon=Decimal('0.0850'),
                            pre_modification_payment=rand_money(2_200, 400),
                            property_type=random.choice(['SFR', 'Condo', '2-4 Unit']),
                            balloon_date=random.choice([None, today + dt.timedelta(days=random.randint(365, 2000))]),
                            balloon_payment=rand_money(50_000, 20_000),
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
