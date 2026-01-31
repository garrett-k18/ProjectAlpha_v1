"""
Management command to generate test data using Factory Boy.

Usage:
    python manage.py generate_test_data
    python manage.py generate_test_data --sellers=5 --trades-per-seller=1-2 --assets-per-trade=1-25
    python manage.py generate_test_data --seller-val-pct=0.9 --internal-val-pct=0.5 --broker-val-pct=0.9
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
import random

from factories.factory_core import AssetIdHubFactory, AssetDetailsFactory, LlDataEnrichmentFactory
from factories.factory_acq import (
    SellerFactory,
    TradeFactory,
    AcqAssetFactory,
    AcqLoanFactory,
    AcqPropertyFactory,
    AcqForeclosureTimelineFactory,
    AcqBankruptcyFactory,
    AcqModificationFactory,
)
from factories.factory_assumptions import LoanLevelAssumptionFactory, TradeLevelAssumptionFactory
from factories.factory_valuations import ValuationFactory

from core.models.model_co_assumptions import Servicer
from core.models.model_co_valuations import ValuationGradeReference
from acq_module.models.model_acq_seller import AcqAsset


class Command(BaseCommand):
    help = 'Generate interconnected test data using Factory Boy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sellers',
            type=int,
            default=5,
            help='Number of sellers to create (default: 5)'
        )
        parser.add_argument(
            '--trades-per-seller',
            type=str,
            default='1-2',
            help='Trades per seller as range (default: 1-2)'
        )
        parser.add_argument(
            '--assets-per-trade',
            type=str,
            default='1-25',
            help='Assets per trade as range (default: 1-25)'
        )

        parser.add_argument(
            '--database',
            type=str,
            default='default',
            help='Database to use (default, dev, newdev, prod)'
        )

        parser.add_argument(
            '--seller-val-pct',
            type=float,
            default=0.90,
            help='Percent of assets with seller valuations (default: 0.90)'
        )
        parser.add_argument(
            '--internal-val-pct',
            type=float,
            default=0.50,
            help='Percent of assets with internal UW valuations (default: 0.50)'
        )
        parser.add_argument(
            '--broker-val-pct',
            type=float,
            default=0.90,
            help='Percent of assets with broker valuations (default: 0.90)'
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed progress'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating'
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        dry_run = options['dry_run']
        database = options['database']

        num_sellers = options['sellers']
        trades_range = self.parse_range(options['trades_per_seller'])
        assets_range = self.parse_range(options['assets_per_trade'])
        seller_val_pct = options['seller_val_pct']
        internal_val_pct = options['internal_val_pct']
        broker_val_pct = options['broker_val_pct']

        avg_trades = sum(trades_range) / 2
        avg_assets = sum(assets_range) / 2
        estimated_total_assets = int(num_sellers * avg_trades * avg_assets)

        self.stdout.write(
            self.style.SUCCESS(
                f'\n>> Test Data Generation Plan\n'
                f'{"=" * 50}\n'
                f'Sellers: {num_sellers}\n'
                f'Trades per seller: {trades_range[0]}-{trades_range[1]}\n'
                f'Assets per trade: {assets_range[0]}-{assets_range[1]}\n'
                f'Estimated total assets: ~{estimated_total_assets}\n'
                f'Database: {database}\n'
                f'Seller Valuations: {seller_val_pct:.0%}\n'
                f'Internal UW Valuations: {internal_val_pct:.0%}\n'
                f'Broker Valuations: {broker_val_pct:.0%}\n'
                f'{"=" * 50}\n'
            )
        )

        if dry_run:
            self.stdout.write(self.style.WARNING('>> DRY RUN - No data will be created'))
            return

        try:
            using_db = database if database != 'default' else 'default'

            with transaction.atomic(using=using_db):
                self.stdout.write('>> Phase 1: Using existing reference data...')

                servicers = list(Servicer.objects.all())
                if not servicers:
                    self.stdout.write(
                        self.style.WARNING('  ! No servicers found. Creating default servicer...')
                    )
                    servicer = Servicer.objects.create(
                        servicer_name="Default Servicer",
                        is_default_for_trade_assumptions=True
                    )
                    servicers = [servicer]

                if servicers and not any(s.is_default_for_trade_assumptions for s in servicers):
                    servicers[0].is_default_for_trade_assumptions = True
                    servicers[0].save()

                self.stdout.write(f'  [OK] Using {len(servicers)} existing servicers')

                grades = ['A+', 'A', 'B', 'C', 'D', 'F']
                for i, grade in enumerate(grades):
                    ValuationGradeReference.objects.get_or_create(
                        code=grade,
                        defaults={
                            'label': f'Grade {grade}',
                            'description': f'{grade} grade property',
                            'sort_order': i,
                        },
                    )
                if verbose:
                    self.stdout.write(f'  [OK] Created valuation grades')

                self.stdout.write('\n>> Phase 2: Creating sellers and trades...')

                sellers = []
                trades = []

                for _ in range(num_sellers):
                    seller = SellerFactory.create()
                    sellers.append(seller)

                    num_trades = random.randint(*trades_range)
                    for _ in range(num_trades):
                        trade = TradeFactory.create(seller=seller)
                        trades.append(trade)

                        TradeLevelAssumptionFactory.create(
                            trade=trade,
                            servicer=servicers[0] if servicers else None
                        )

                    if verbose:
                        self.stdout.write(
                            f'  [OK] Created seller: {seller.name} with {num_trades} trades'
                        )

                self.stdout.write(
                    f'  [OK] Created {len(sellers)} sellers and {len(trades)} trades'
                )

                self.stdout.write('\n>> Phase 3: Creating assets...')

                total_assets = 0

                for trade in trades:
                    num_assets = random.randint(*assets_range)
                    asset_classes = self.build_asset_classes_for_trade(num_assets)

                    for asset_class in asset_classes:
                        asset_hub = AssetIdHubFactory.create()

                        asset_status = self.pick_asset_status(asset_class)
                        subclass_values = self.pick_subclass_fields(asset_class)

                        asset = AcqAssetFactory.create(
                            asset_hub=asset_hub,
                            seller=trade.seller,
                            trade=trade,
                            asset_class=asset_class,
                            asset_status=asset_status,
                            **subclass_values,
                        )

                        loan = AcqLoanFactory.create(asset=asset)
                        AcqPropertyFactory.create(asset=asset)

                        if asset_hub.sellertape_id != loan.sellertape_id:
                            asset_hub.sellertape_id = loan.sellertape_id
                            asset_hub.save(update_fields=["sellertape_id"])

                        if random.random() < 0.25:
                            AcqForeclosureTimelineFactory.create(asset=asset)

                        if random.random() < 0.15:
                            AcqBankruptcyFactory.create(loan=loan)

                        if random.random() < 0.20:
                            AcqModificationFactory.create(loan=loan)

                        AssetDetailsFactory.create(asset=asset_hub, trade=trade)
                        LlDataEnrichmentFactory.create(asset_hub=asset_hub)
                        LoanLevelAssumptionFactory.create(asset_hub=asset_hub)

                        self.create_valuations_for_asset(
                            asset_hub=asset_hub,
                            seller_val_pct=seller_val_pct,
                            internal_val_pct=internal_val_pct,
                            broker_val_pct=broker_val_pct,
                        )

                        total_assets += 1
                        if total_assets % 50 == 0:
                            self.stdout.write(f'  ... Created {total_assets} assets so far')

                    if verbose:
                        self.stdout.write(
                            f'  [OK] Created {num_assets} assets for trade: {trade.trade_name}'
                        )

                self.stdout.write(f'  [OK] Created {total_assets} total assets')

                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n>> Test data generation complete!\n'
                        f'{"=" * 50}\n'
                        f'Summary:\n'
                        f'  - Sellers: {len(sellers)}\n'
                        f'  - Trades: {len(trades)}\n'
                        f'  - Assets: {total_assets}\n'
                        f'  - Servicers: {len(servicers)}\n'
                        f'  - Database: {database}\n'
                        f'{"=" * 50}\n'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n>> Error during generation: {str(e)}\n')
            )
            import traceback
            traceback.print_exc()
            raise CommandError(f'Data generation failed: {str(e)}')

    def parse_range(self, range_str):
        parts = range_str.split('-')
        if len(parts) == 2:
            return (int(parts[0]), int(parts[1]))
        val = int(parts[0])
        return (val, val)

    def build_asset_classes_for_trade(self, num_assets: int):
        non_note_classes = [
            AcqAsset.AssetClass.REAL_ESTATE_1_4,
            AcqAsset.AssetClass.MULTIFAMILY_5_PLUS,
            AcqAsset.AssetClass.COMMERCIAL,
        ]
        selected_non_note = []
        for cls in non_note_classes:
            if len(selected_non_note) < num_assets and random.random() < 0.5:
                selected_non_note.append(cls)
        remaining = max(0, num_assets - len(selected_non_note))
        note_classes = [AcqAsset.AssetClass.PERFORMING_NOTE, AcqAsset.AssetClass.NPL]
        notes = [random.choice(note_classes) for _ in range(remaining)]
        return selected_non_note + notes

    def pick_asset_status(self, asset_class: str):
        if asset_class == AcqAsset.AssetClass.NPL:
            return AcqAsset.AssetStatus.NPL
        if asset_class == AcqAsset.AssetClass.PERFORMING_NOTE:
            return random.choice([AcqAsset.AssetStatus.PERF, AcqAsset.AssetStatus.RPL])
        return random.choice([c[0] for c in AcqAsset.AssetStatus.choices])

    def pick_subclass_fields(self, asset_class: str):
        if asset_class == AcqAsset.AssetClass.REAL_ESTATE_1_4:
            return {
                "real_estate_subclass_type": random.choice([c[0] for c in AcqAsset.RealEstateSubclass.choices])
            }
        if asset_class == AcqAsset.AssetClass.MULTIFAMILY_5_PLUS:
            return {
                "multifamily_subclass_type": random.choice([c[0] for c in AcqAsset.MultifamilySubclass.choices])
            }
        if asset_class == AcqAsset.AssetClass.COMMERCIAL:
            return {
                "commercial_subclass_type": random.choice([c[0] for c in AcqAsset.CommercialSubclass.choices])
            }
        if asset_class in {AcqAsset.AssetClass.PERFORMING_NOTE, AcqAsset.AssetClass.NPL}:
            if asset_class == AcqAsset.AssetClass.NPL:
                note_value = AcqAsset.NoteSubclass.NPL
            else:
                note_value = random.choice([AcqAsset.NoteSubclass.PERF, AcqAsset.NoteSubclass.RPL])
            return {"note_subclass_type": note_value}
        return {}

    def create_valuations_for_asset(self, asset_hub, seller_val_pct, internal_val_pct, broker_val_pct):
        if random.random() < seller_val_pct:
            ValuationFactory.create(
                asset_hub=asset_hub,
                source="sellerProvided",
            )
        if random.random() < internal_val_pct:
            ValuationFactory.create(
                asset_hub=asset_hub,
                source="internalInitialUW",
            )
        if random.random() < broker_val_pct:
            ValuationFactory.create(
                asset_hub=asset_hub,
                source="broker",
            )
