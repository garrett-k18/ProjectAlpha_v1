"""
Django management command to seed dummy data for Seller, Trade, and SellerRawData.

- Supports creating multiple assets (SellerRawData rows) per Trade using
  --assets-min/--assets-max to control the range per trade.

References:
- Django custom management commands: https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/
- Faker (data generator) docs: https://faker.readthedocs.io/
"""
from __future__ import annotations

# Standard library imports
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

# Django imports
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from contextlib import nullcontext as _nullctx
from django.utils import timezone

# Local app model imports
from acq_module.models.seller import Seller, Trade, SellerRawData
from core.models.valuations import Valuation
from core.models.asset_id_hub import AssetIdHub
from core.services.geocoding import geocode_markers_for_seller_trade

# List of US state abbreviations (lower 48 states plus Alaska and Hawaii)
US_STATES = [
    # New England
    'ME', 'NH', 'VT', 'MA', 'RI', 'CT',
    # Mid-Atlantic
    'NY', 'NJ', 'PA', 
    # South Atlantic
    'DE', 'MD', 'DC', 'VA', 'WV', 'NC', 'SC', 'GA', 'FL',
    # East North Central
    'OH', 'IN', 'IL', 'MI', 'WI',
    # East South Central
    'KY', 'TN', 'AL', 'MS',
    # West North Central
    'MN', 'IA', 'MO', 'ND', 'SD', 'NE', 'KS',
    # West South Central
    'OK', 'TX', 'AR', 'LA',
    # Mountain
    'MT', 'ID', 'WY', 'CO', 'NM', 'AZ', 'UT', 'NV',
    # Pacific
    'WA', 'OR', 'CA', 'AK', 'HI'
]

try:
    # Faker is an optional dependency for this command; ensure it's installed
    from faker import Faker
except Exception as exc:  # pragma: no cover - import-time guidance for missing dep
    raise SystemExit(
        "Faker is required for this command. Install with: pip install Faker"
    ) from exc


class Command(BaseCommand):
    """Seed the database with dummy data for development/testing.

    Creates Sellers, Trades, and multiple SellerRawData rows per Trade.
    The number of assets per Trade is randomized between --assets-min and
    --assets-max (inclusive).

    Default behavior creates 8 sellers and 3 trades per seller (24 trades),
    with 1..21 assets per trade.
    """

    help = (
        "Seed Sellers, Trades, and multiple SellerRawData (assets) per Trade with Faker. "
        "Default: 8 sellers, 3 trades/seller, and 1..21 assets/trade."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        """Define CLI arguments for the command.

        Args:
            parser: Argument parser provided by Django.
        """
        parser.add_argument(
            "--sellers",
            type=int,
            default=8,
            help="Number of Seller records to create (default: 8)",
        )
        parser.add_argument(
            "--trades-per-seller",
            type=int,
            default=3,
            help="Number of Trade records per Seller (default: 3)",
        )
        parser.add_argument(
            "--purge",
            action="store_true",
            help="If set, deletes existing data in these models before seeding.",
        )
        parser.add_argument(
            "--locale",
            type=str,
            default="en_US",
            help="Faker locale (default: en_US). See Faker docs for available locales.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Optional RNG seed for reproducible data.",
        )
        parser.add_argument(
            "--assets-min",
            type=int,
            default=1,
            help="Minimum number of assets (SellerRawData rows) per Trade (inclusive). Default: 1",
        )
        parser.add_argument(
            "--assets-max",
            type=int,
            default=21,
            help="Maximum number of assets (SellerRawData rows) per Trade (inclusive). Default: 21",
        )

    def handle(self, *args, **options) -> None:
        """Entrypoint for the command.

        Orchestrates optional purge and then creates Sellers, Trades, and
        SellerRawData under a single DB transaction for consistency.
        """
        sellers_count: int = options["sellers"]
        trades_per_seller: int = options["trades_per_seller"]
        purge: bool = options["purge"]
        locale: str = options["locale"]
        seed_value: int | None = options["seed"]
        assets_min: int = options["assets_min"]
        assets_max: int = options["assets_max"]

        # Initialize Faker with requested locale
        faker = Faker(locale)

        # Seed both Python's random and Faker if requested for reproducibility
        if seed_value is not None:
            random.seed(seed_value)
            Faker.seed(seed_value)

        # IMPORTANT: Ensure writes go to the intended PostgreSQL schemas.
        # Your ACQ app tables (Seller/SellerRawData/Trade) live in schema 'seller_data',
        # while hub and some shared tables live in 'core'. Place seller_data first so
        # acq_module tables resolve there, then core for hub tables.
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO seller_data, core, public")
            cursor.execute("SHOW search_path")
            current_path = cursor.fetchone()[0]
            self.stdout.write(self.style.NOTICE(f"search_path set to: {current_path}"))

        # Optional purge of existing data to avoid unique constraint conflicts
        if purge:
            self.stdout.write(self.style.WARNING("Purging existing data..."))
            # Order matters due to FK constraints: delete children first
            SellerRawData.objects.all().delete()
            Trade.objects.all().delete()
            Seller.objects.all().delete()
            # IMPORTANT: Do not purge AssetIdHub here to avoid ProtectedError from other modules.
            # Hub IDs will continue to increment across seeds, which is acceptable for dev data.

        # Enforce constraints requested for this dummy run pattern
        # - Max 3 sellers
        # - 1-2 trades per seller (randomized per seller)
        # - 1-13 assets per trade
        # - Max 60 total assets/hubs overall
        sellers_count = min(sellers_count, 3)
        ASSETS_TOTAL_MAX = 60

        # Important: avoid a single giant transaction across schemas; commit each insert naturally
        # so FK checks can see parent rows immediately across schemas.
        with _nullctx():
            self.stdout.write(
                f"Creating up to {sellers_count} sellers × 1-2 trades each with 1-13 assets/trade (cap {ASSETS_TOTAL_MAX})..."
            )

            sellers: list[Seller] = []
            trades: list[Trade] = []
            assets_created: int = 0

            # Create Seller records
            for i in range(sellers_count):
                seller = Seller(
                    name=faker.company(),  # e.g., "Acme Corp"
                    broker=faker.name(),   # person name to represent broker
                    email=faker.company_email(),
                    poc=faker.name(),
                )
                sellers.append(seller)
            Seller.objects.bulk_create(sellers)

            # Refresh with PKs
            sellers = list(Seller.objects.order_by("id")[:sellers_count])

            # For each seller, create 1-2 trades (use save() so Trade.save() generates trade_name)
            for seller in sellers:
                num_trades_for_seller = random.randint(1, 2)
                for _ in range(num_trades_for_seller):
                    trade = Trade(seller=seller)
                    trade.save()  # triggers trade_name generation in model.save()
                    trades.append(trade)

            # For each trade, create multiple SellerRawData rows (controlled by --assets-min/--assets-max)
            today = date.today()
            for trade in trades:
                seller = trade.seller
                # Randomize number of assets for this trade within [assets_min, assets_max]
                if assets_created >= ASSETS_TOTAL_MAX:
                    break
                # Respect per-trade 1-13 but never exceed global cap
                remaining = ASSETS_TOTAL_MAX - assets_created
                assets_count = min(random.randint(1, 13), remaining)

                # Create that many assets and number them 1..N per trade
                for sequence_number in range(1, assets_count + 1):
                    # Generate property details
                    beds = random.randint(1, 6)
                    baths = round(random.uniform(1, 4.5) * 2) / 2  # 1, 1.5, 2, 2.5, etc.
                    sq_ft = random.randrange(800, 4000, 100)
                    lot_size = random.randrange(2000, 15000, 500)
                    year_built = random.randint(1920, 2023)
                    
                    # Generate a realistic financial profile
                    original_balance = Decimal(random.randrange(50_000, 800_000))
                    current_balance = original_balance - Decimal(random.randrange(0, 40_000))
                    deferred_balance = Decimal(random.randrange(0, 25_000))
                    
                    # Interest rate rules
                    # Normal note rate between 3-8%
                    interest_rate = Decimal(random.uniform(3.0, 8.0)) / Decimal(100)
                    
                    # Default rate (12-22%) only on 5% of records, otherwise use interest_rate
                    if random.random() <= 0.05:  # 5% chance
                        default_rate = Decimal(random.uniform(12.0, 22.0)) / Decimal(100)
                    else:
                        default_rate = interest_rate  # Use same as interest_rate for non-default cases

                    # Set up date timeline
                    origination_date = today - timedelta(days=random.randrange(365, 365 * 10))
                    first_pay_date = origination_date + timedelta(days=30)
                    original_term_months = random.choice([120, 180, 240, 300, 360])
                    original_maturity_date = origination_date + timedelta(days=30 * original_term_months)
                    current_term = max(1, original_term_months - random.randrange(0, 48))
                    current_maturity_date = today + timedelta(days=30 * current_term)
                    next_due_date = today + timedelta(days=random.randrange(-60, 60))
                    last_paid_date = today - timedelta(days=random.randrange(0, 90))

                    # Property valuation timeline
                    origination_value = Decimal(random.randrange(100_000, 1_200_000))
                    origination_arv = origination_value + Decimal(random.randrange(10_000, 250_000))
                    origination_value_date = origination_date

                    seller_asis_value = Decimal(random.randrange(100_000, 1_200_000))
                    seller_arv_value = seller_asis_value + Decimal(random.randrange(10_000, 250_000))
                    seller_value_date = today - timedelta(days=random.randrange(30, 365))

                    additional_asis_value = seller_asis_value + Decimal(random.randrange(-20_000, 50_000))
                    additional_arv_value = additional_asis_value + Decimal(random.randrange(10_000, 150_000))
                    additional_value_date = today - timedelta(days=random.randrange(0, 180))

                    # Fees and advances
                    accrued_note_interest = Decimal(random.randrange(0, 15_000))
                    accrued_default_interest = Decimal(random.randrange(0, 10_000))
                    escrow_balance = Decimal(random.randrange(0, 20_000))
                    escrow_advance = Decimal(random.randrange(0, 5_000))
                    recoverable_corp_advance = Decimal(random.randrange(0, 8_000))
                    late_fees = Decimal(random.randrange(0, 2_500))
                    other_fees = Decimal(random.randrange(0, 2_500))
                    suspense_balance = Decimal(random.randrange(0, 3_500))

                    # Foreclosure and bankruptcy flags
                    fc_flag = random.random() < 0.15
                    fc_first_legal_date = (
                        today - timedelta(days=random.randrange(30, 240)) if fc_flag else None
                    )
                    fc_referred_date = (
                        fc_first_legal_date + timedelta(days=14) if fc_first_legal_date else None
                    )
                    fc_judgement_date = (
                        fc_first_legal_date + timedelta(days=90) if fc_first_legal_date else None
                    )
                    fc_scheduled_sale_date = (
                        today + timedelta(days=random.randrange(15, 120)) if fc_flag else None
                    )
                    fc_sale_date = None  # not sold by default in dummy data
                    fc_starting = (
                        Decimal(random.randrange(50_000, 400_000)) if fc_flag else None
                    )

                    bk_flag = random.random() < 0.1
                    bk_chapter = random.choice(["7", "11", "13"]) if bk_flag else None

                    # Modifications
                    mod_flag = random.random() < 0.2
                    mod_date = today - timedelta(days=random.randrange(30, 365)) if mod_flag else None
                    mod_maturity_date = (
                        (today + timedelta(days=30 * random.randrange(6, 24))) if mod_flag else None
                    )
                    mod_term = random.randrange(6, 60) if mod_flag else None
                    mod_rate = (
                        Decimal(f"{float(interest_rate) - random.uniform(0.1, 1.0):.4f}") if mod_flag else None
                    )
                    mod_initial_balance = (
                        current_balance + Decimal(random.randrange(-5_000, 10_000)) if mod_flag else None
                    )

                    # Generate property type using the exact codes from the frontend badge system
                    # Map between model choices and frontend badge codes
                    property_type_map = {
                        'SFR': 'SFR',           # Single Family Residence
                        'MFD': 'Manufactured',  # Manufactured Home
                        'CND': 'Condo',         # Condominium
                        'MF2': '2-4 Family',    # 2-4 Family Property
                        'LND': 'Land',          # Vacant Land
                        'MF5': 'Multifamily 5+' # Multifamily 5+ Units
                    }
                    
                    # Generate occupancy status using the exact codes from the frontend badge system
                    # Map between model choices and frontend badge codes
                    occupancy_map = {
                        'VAC': 'Vacant',    # Vacant
                        'OCC': 'Occupied',  # Occupied
                        'UNK': 'Unknown'    # Unknown
                    }
                    
                    # Randomly select property type and occupancy
                    property_type_code = random.choice(['SFR', 'MFD', 'CND', 'MF2', 'LND', 'MF5'])
                    occupancy_code = random.choice(['VAC', 'OCC', 'UNK'])
                    
                    # Get corresponding model values
                    property_type_value = property_type_map[property_type_code]
                    occupancy_value = occupancy_map[occupancy_code]
                    
                    # Generate required fields
                    sellertape_id = sequence_number  # Use sequence_number as sellertape_id
                    asset_status = random.choice(['NPL', 'REO', 'PERF', 'RPL'])
                    as_of_date = today
                    
                    # Generate address
                    street_address = faker.street_address()
                    city = faker.city()
                    state = random.choice(US_STATES)
                    zip_code = faker.zipcode()
                    
                    # Create the AssetIdHub FIRST (canonical hub for this asset)
                    # NOTE: Explicitly insert into core schema to avoid search_path issues
                    from django.db import connection
                    with connection.cursor() as c:
                        c.execute(
                            "INSERT INTO core.core_assetidhub (sellertape_id, created_at, updated_at) "
                            "VALUES (%s, NOW(), NOW()) RETURNING id",
                            [str(sellertape_id)],
                        )
                        hub_id = c.fetchone()[0]
                    hub = AssetIdHub.objects.get(pk=hub_id)
                    # Sanity check: parent exists before FK insert
                    assert AssetIdHub.objects.filter(pk=hub.pk).exists(), "Hub row not persisted"

                    # Create two unified valuation rows in the core Valuation model per hub:
                    # - broker (maps to grid broker fields)
                    # - internalInitialUW (maps to grid underwritten initial fields)
                    # Values must be random within 75,000..700,000 and distinct across all four numbers
                    # for this hub (asis/arv for broker and internal).
                    def _rand_val():
                        return Decimal(random.randrange(75_000, 700_001)).quantize(Decimal("0.01"))

                    b_asis = _rand_val()
                    b_arv = _rand_val()
                    # ensure distinct within broker row
                    if b_arv == b_asis:
                        b_arv = _rand_val()
                    i_asis = _rand_val()
                    # ensure distinct vs broker
                    if i_asis in {b_asis, b_arv}:
                        i_asis = _rand_val()
                    i_arv = _rand_val()
                    if i_arv in {b_asis, b_arv, i_asis}:
                        i_arv = _rand_val()

                    Valuation.objects.get_or_create(
                        asset_hub=hub,
                        source='broker',
                        value_date=seller_value_date,
                        defaults={
                            'asis_value': b_asis,
                            'arv_value': b_arv,
                        },
                    )
                    Valuation.objects.get_or_create(
                        asset_hub=hub,
                        source='internalInitialUW',
                        value_date=seller_value_date,
                        defaults={
                            'asis_value': i_asis,
                            'arv_value': i_arv,
                        },
                    )

                    # Assemble SellerRawData linked to the hub (1:1)
                    raw_data = SellerRawData(
                        seller=seller,
                        trade=trade,
                        asset_hub=hub,
                        sellertape_id=sellertape_id,
                        asset_status=asset_status,
                        as_of_date=as_of_date,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip=zip_code,
                        property_type=property_type_value,
                        occupancy=occupancy_value,
                        beds=beds,
                        baths=baths,
                        sq_ft=sq_ft,
                        lot_size=lot_size,
                        year_built=year_built,
                        next_due_date=next_due_date,
                        last_paid_date=last_paid_date,
                        first_pay_date=first_pay_date,
                        origination_date=origination_date,
                        original_balance=original_balance.quantize(Decimal("0.01")),
                        current_balance=current_balance.quantize(Decimal("0.01")),
                        deferred_balance=deferred_balance.quantize(Decimal("0.01")),
                        interest_rate=interest_rate.quantize(Decimal("0.0000")),
                        original_term=original_term_months,
                        original_rate=Decimal(f"{random.uniform(2.0, 10.0):.4f}"),
                        original_maturity_date=original_maturity_date,
                        default_rate=default_rate.quantize(Decimal("0.0001")),
                        current_maturity_date=current_maturity_date,
                        current_term=current_term,
                        accrued_note_interest=accrued_note_interest.quantize(Decimal("0.01")),
                        accrued_default_interest=accrued_default_interest.quantize(Decimal("0.01")),
                        escrow_balance=escrow_balance.quantize(Decimal("0.01")),
                        escrow_advance=escrow_advance.quantize(Decimal("0.01")),
                        recoverable_corp_advance=recoverable_corp_advance.quantize(Decimal("0.01")),
                        late_fees=late_fees.quantize(Decimal("0.01")),
                        other_fees=other_fees.quantize(Decimal("0.01")),
                        suspense_balance=suspense_balance.quantize(Decimal("0.01")),
                        # total_debt left None (model save() will calculate)
                        origination_value=origination_value.quantize(Decimal("0.01")),
                        origination_arv=origination_arv.quantize(Decimal("0.01")),
                        origination_value_date=origination_value_date,
                        seller_asis_value=seller_asis_value.quantize(Decimal("0.01")),
                        seller_arv_value=seller_arv_value.quantize(Decimal("0.01")),
                        seller_value_date=seller_value_date,
                        additional_asis_value=additional_asis_value.quantize(Decimal("0.01")),
                        additional_arv_value=additional_arv_value.quantize(Decimal("0.01")),
                        additional_value_date=additional_value_date,
                        fc_flag=fc_flag,
                        fc_first_legal_date=fc_first_legal_date,
                        fc_referred_date=fc_referred_date,
                        fc_judgement_date=fc_judgement_date,
                        fc_scheduled_sale_date=fc_scheduled_sale_date,
                        fc_sale_date=fc_sale_date,
                        fc_starting=fc_starting.quantize(Decimal("0.01")) if fc_starting else None,
                        bk_flag=bk_flag,
                        bk_chapter=bk_chapter,
                        mod_flag=mod_flag,
                        mod_date=mod_date,
                        mod_maturity_date=mod_maturity_date,
                        mod_term=mod_term,
                        mod_rate=mod_rate.quantize(Decimal("0.0001")) if mod_rate else None,
                        mod_initial_balance=(
                            mod_initial_balance.quantize(Decimal("0.01")) if mod_initial_balance else None
                        ),
                    )
                    # Save immediately to ensure FK to hub is persisted and model.save() hooks run.
                    # Note: Model.save() will auto-calc total_debt/months_dlq if None, but we've set them anyway.
                    raw_data.save()
                    assets_created += 1
                    if assets_created >= ASSETS_TOTAL_MAX:
                        break

            # No bulk_create: we saved each instance to guarantee FK integrity and run save() logic

        # After commit, geocode per trade to persist coordinates (best-effort)
        # This deduplicates by address internally to minimize API calls.
        for t in trades:
            try:
                geocode_markers_for_seller_trade(t.seller_id, t.id)
            except Exception:
                # Non-fatal for seed routines
                pass

        # Summary output
        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {sellers_count} sellers, {len(trades)} trades, {assets_created} raw rows."
        ))
