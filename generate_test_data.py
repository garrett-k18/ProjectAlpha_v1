"""
Management command to generate test data using Factory Boy.

This command generates realistic, interconnected test data based on
parameters from TEST_DATA_CONFIG.md.

Usage:
    python manage.py generate_test_data --sellers=12 --assets-per-trade=20
    python manage.py generate_test_data --preset=minimal
    python manage.py generate_test_data --database=dev
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connections
from django.conf import settings
from django.db.models.signals import post_save
import random
import sys

# Import factories
sys.path.append(str(settings.BASE_DIR))
from factories.factory_acq import (
    SellerFactory, TradeFactory, AssetIdHubFactory,
    SellerRawDataFactory, AssetDetailsFactory,
    LoanLevelAssumptionFactory, TradeLevelAssumptionFactory,
)
from factories.factory_assumptions import (
    ServicerFactory,
)
from factories.factory_am import (
    AMMetricsFactory, AMNoteFactory,
    REODataFactory, FCSaleFactory, DILFactory,
    ShortSaleFactory, ModificationFactory, NoteSaleFactory,
)

# Import models
from core.models import AssetIdHub, Servicer
from acq_module.models import Seller, Trade
from am_module.models import AMMetrics


class Command(BaseCommand):
    help = 'Generate interconnected test data using Factory Boy'

    def add_arguments(self, parser):
        # Volume parameters (from TEST_DATA_CONFIG.md)
        parser.add_argument(
            '--sellers',
            type=int,
            default=12,
            help='Number of sellers to create (default: 12 from config)'
        )
        parser.add_argument(
            '--trades-per-seller',
            type=str,
            default='1-2',
            help='Trades per seller as range (default: 1-2 from config)'
        )
        parser.add_argument(
            '--assets-per-trade',
            type=str,
            default='1-35',
            help='Assets per trade as range (default: 1-35 from config)'
        )
        
        # Preset configurations
        parser.add_argument(
            '--preset',
            choices=['minimal', 'standard', 'full'],
            help='Use preset configuration (overrides individual parameters)'
        )
        
        # Database selection
        parser.add_argument(
            '--database',
            type=str,
            default='default',
            help='Database to use (default, dev, newdev, prod)'
        )
        
        # Feature flags
        parser.add_argument(
            '--with-outcomes',
            action='store_true',
            help='Generate outcome data (REO, FC, DIL, etc.)'
        )
        parser.add_argument(
            '--with-am-notes',
            action='store_true',
            help='Generate AM notes (1-8 per asset from config)'
        )
        
        # Options
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
        
        # Apply preset if specified
        if options['preset']:
            options = self.apply_preset(options)
        
        # Parse range parameters
        num_sellers = options['sellers']
        trades_range = self.parse_range(options['trades_per_seller'])
        assets_range = self.parse_range(options['assets_per_trade'])
        
        # Calculate totals
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
                f'Outcomes: {"Yes" if options["with_outcomes"] else "No"}\n'
                f'AM Notes: {"Yes" if options["with_am_notes"] else "No"}\n'
                f'{"=" * 50}\n'
            )
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('>> DRY RUN - No data will be created'))
            return
        
        try:
            # Disable SharePoint signals during bulk data generation
            # NOTE: SharePoint integration temporarily disabled
            # from sharepoint.sig_sharepoint_folderTempCreate import create_trade_folders, create_asset_folders
            # post_save.disconnect(create_trade_folders, sender=Trade)
            # post_save.disconnect(create_asset_folders, sender='acq_module.SellerRawData')
            
            if verbose:
                self.stdout.write('  [INFO] SharePoint signals disabled (no SharePoint integration)')
            
            # Use specified database
            using_db = database if database != 'default' else 'default'
            
            with transaction.atomic(using=using_db):
                self.stdout.write('>> Phase 1: Using existing reference data...')
                
                # Use existing servicers (config specifies to keep existing data)
                servicers = list(Servicer.objects.all())
                
                if not servicers:
                    self.stdout.write(
                        self.style.WARNING(
                            '  ! No servicers found. Creating default servicer...'
                        )
                    )
                    servicer = Servicer.objects.create(
                        servicer_name="Default Servicer",
                        is_default_for_trade_assumptions=True
                    )
                    servicers = [servicer]
                
                # Ensure at least one servicer is default
                if servicers and not any(s.is_default_for_trade_assumptions for s in servicers):
                    servicers[0].is_default_for_trade_assumptions = True
                    servicers[0].save()
                
                self.stdout.write(f'  [OK] Using {len(servicers)} existing servicers')
                
                # Create valuation grades (if not exist) - using direct model creation
                from core.models import ValuationGradeReference
                grades = ['A+', 'A', 'B', 'C', 'D', 'F']
                for i, grade in enumerate(grades):
                    ValuationGradeReference.objects.get_or_create(
                        code=grade,
                        defaults={
                            'label': f'Grade {grade}',
                            'description': f'{grade} grade property',
                            'sort_order': i
                        }
                    )
                if verbose:
                    self.stdout.write(f'  [OK] Created valuation grades')
                
                self.stdout.write('\n>> Phase 2: Creating sellers and trades...')
                
                sellers = []
                trades = []
                
                for i in range(num_sellers):
                    # Create seller
                    seller = SellerFactory.create()
                    sellers.append(seller)
                    
                    # Create trades for this seller
                    num_trades = random.randint(*trades_range)
                    for j in range(num_trades):
                        trade = TradeFactory.create(seller=seller)
                        trades.append(trade)
                        
                        # Create trade-level assumption
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
                
                asset_hubs = []
                total_assets = 0
                
                for trade in trades:
                    # Create assets for this trade
                    num_assets = random.randint(*assets_range)
                    
                    for k in range(num_assets):
                        # Create AssetIdHub (central hub)
                        asset_hub = AssetIdHubFactory.create()
                        asset_hubs.append(asset_hub)
                        
                        # Create SellerRawData (1:1 with AssetIdHub)
                        SellerRawDataFactory.create(
                            asset_hub=asset_hub,
                            seller=trade.seller,
                            trade=trade
                        )
                        
                        # Create AssetDetails (1:1 with AssetIdHub)
                        AssetDetailsFactory.create(
                            asset=asset_hub,
                            trade=trade
                        )
                        
                        # Create LoanLevelAssumption
                        LoanLevelAssumptionFactory.create(
                            asset_hub=asset_hub
                        )
                        
                        # Create AMMetrics (includes delinquency_status)
                        AMMetricsFactory.create(
                            asset_hub=asset_hub
                        )
                        
                        total_assets += 1
                        
                        # Progress indicator
                        if total_assets % 50 == 0:
                            self.stdout.write(f'  ... Created {total_assets} assets so far')
                    
                    if verbose:
                        self.stdout.write(
                            f'  [OK] Created {num_assets} assets for trade: {trade.trade_name}'
                        )
                
                self.stdout.write(f'  [OK] Created {total_assets} total assets')
                
                # Phase 4: Create outcomes (if enabled)
                if options['with_outcomes']:
                    self.stdout.write('\n>> Phase 4: Creating outcomes...')
                    
                    # Outcome distribution from config:
                    # REO 20%, FC 30%, DIL 15%, ShortSale 3%, Mod 5%, NoteSale 2%, No outcome 25%
                    outcome_counts = {
                        'reo': 0,
                        'fc': 0,
                        'dil': 0,
                        'short_sale': 0,
                        'modification': 0,
                        'note_sale': 0,
                        'none': 0,
                    }
                    
                    for asset_hub in asset_hubs:
                        # Determine outcome based on distribution
                        rand = random.random()
                        
                        if rand < 0.20:  # 20% REO
                            REODataFactory.create(asset_hub=asset_hub)
                            outcome_counts['reo'] += 1
                        elif rand < 0.50:  # 30% FC (20% + 30%)
                            FCSaleFactory.create(asset_hub=asset_hub)
                            outcome_counts['fc'] += 1
                        elif rand < 0.65:  # 15% DIL (50% + 15%)
                            DILFactory.create(asset_hub=asset_hub)
                            outcome_counts['dil'] += 1
                        elif rand < 0.68:  # 3% ShortSale (65% + 3%)
                            ShortSaleFactory.create(asset_hub=asset_hub)
                            outcome_counts['short_sale'] += 1
                        elif rand < 0.73:  # 5% Modification (68% + 5%)
                            ModificationFactory.create(asset_hub=asset_hub)
                            outcome_counts['modification'] += 1
                        elif rand < 0.75:  # 2% NoteSale (73% + 2%)
                            NoteSaleFactory.create(asset_hub=asset_hub)
                            outcome_counts['note_sale'] += 1
                        else:  # 25% No outcome
                            outcome_counts['none'] += 1
                    
                    self.stdout.write(f'  [OK] Created outcomes:')
                    for outcome, count in outcome_counts.items():
                        if count > 0:
                            pct = (count / total_assets) * 100
                            self.stdout.write(f'    - {outcome}: {count} ({pct:.1f}%)')
                
                # Phase 5: Create AM notes (if enabled)
                if options['with_am_notes']:
                    self.stdout.write('\n>> Phase 5: Creating AM notes...')
                    
                    total_notes = 0
                    for asset_hub in asset_hubs:
                        # Create 1-8 notes per asset (from config)
                        num_notes = random.randint(1, 8)
                        for _ in range(num_notes):
                            AMNoteFactory.create(asset_hub=asset_hub)
                            total_notes += 1
                    
                    self.stdout.write(f'  [OK] Created {total_notes} AM notes')
                
                # Summary
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
            
            # Re-enable SharePoint signals
            # NOTE: SharePoint integration temporarily disabled
            # from sharepoint.sig_sharepoint_folderTempCreate import create_trade_folders, create_asset_folders
            # post_save.connect(create_trade_folders, sender=Trade)
            # post_save.connect(create_asset_folders, sender='acq_module.SellerRawData')
            
            if verbose:
                self.stdout.write('  [INFO] Data generation complete (SharePoint disabled)')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n>> Error during generation: {str(e)}\n')
            )
            import traceback
            traceback.print_exc()
            raise CommandError(f'Data generation failed: {str(e)}')

    def apply_preset(self, options):
        """Apply preset configuration."""
        preset = options['preset']
        
        if preset == 'minimal':
            options['sellers'] = 2
            options['trades_per_seller'] = '2-2'
            options['assets_per_trade'] = '25-25'
        elif preset == 'standard':
            options['sellers'] = 5
            options['trades_per_seller'] = '3-3'
            options['assets_per_trade'] = '50-50'
            options['with_outcomes'] = True
        elif preset == 'full':
            options['sellers'] = 10
            options['trades_per_seller'] = '5-5'
            options['assets_per_trade'] = '100-100'
            options['with_outcomes'] = True
            options['with_am_notes'] = True
        
        return options

    def parse_range(self, range_str):
        """Parse range string like '1-2' into tuple (1, 2)."""
        parts = range_str.split('-')
        if len(parts) == 2:
            return (int(parts[0]), int(parts[1]))
        else:
            val = int(parts[0])
            return (val, val)
