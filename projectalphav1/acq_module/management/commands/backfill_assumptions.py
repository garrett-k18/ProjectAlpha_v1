"""
Django management command to backfill missing TradeLevelAssumption and LoanLevelAssumption records.

WHAT: Creates missing assumption records for existing trades and assets
WHY: Older imports didn't auto-create these, causing timeline calculation failures
HOW: Iterates through all trades/assets and creates missing assumptions with defaults

USAGE:
    python manage.py backfill_assumptions
    python manage.py backfill_assumptions --trade-id 5
    python manage.py backfill_assumptions --seller-name "HUD"
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from acq_module.models.model_acq_seller import Trade, SellerRawData
from acq_module.models.model_acq_assumptions import TradeLevelAssumption, LoanLevelAssumption


class Command(BaseCommand):
    """Backfill missing assumption records for trades and assets."""

    help = 'Create missing TradeLevelAssumption and LoanLevelAssumption records'

    def add_arguments(self, parser):
        """Define command-line arguments."""
        parser.add_argument('--trade-id', type=int, help='Backfill specific trade only')
        parser.add_argument('--seller-name', type=str, help='Backfill specific seller only')
        parser.add_argument('--dry-run', action='store_true', help='Preview without creating records')

    def handle(self, *args, **options):
        """Main execution method."""
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.SUCCESS('\n=== BACKFILL ASSUMPTIONS ===\n'))
        
        # Determine which trades to process
        if options.get('trade_id'):
            trades = Trade.objects.filter(id=options['trade_id'])
        elif options.get('seller_name'):
            trades = Trade.objects.filter(seller__name__icontains=options['seller_name'])
        else:
            trades = Trade.objects.all()
        
        total_trades = trades.count()
        self.stdout.write(f'Found {total_trades} trades to process\n\n')
        
        trade_assumptions_created = 0
        loan_assumptions_created = 0
        
        for trade in trades:
            self.stdout.write(f'Processing Trade: {trade.trade_name} (ID: {trade.id})')
            
            # WHAT: Create TradeLevelAssumption if missing
            # WHY: Required for trade-wide timeline calculations
            if not dry_run:
                trade_assumption, created = TradeLevelAssumption.objects.get_or_create(
                    trade=trade,
                    defaults={}  # Use model defaults
                )
                if created:
                    trade_assumptions_created += 1
                    self.stdout.write(f'   [OK] Created TradeLevelAssumption')
                else:
                    self.stdout.write(f'   [EXISTS] TradeLevelAssumption already exists')
            else:
                exists = TradeLevelAssumption.objects.filter(trade=trade).exists()
                if not exists:
                    self.stdout.write(f'   [DRY RUN] Would create TradeLevelAssumption')
                    trade_assumptions_created += 1
                else:
                    self.stdout.write(f'   - TradeLevelAssumption already exists')
            
            # WHAT: Get all SellerRawData for this trade
            # WHY: Need to create LoanLevelAssumption for each asset
            assets = SellerRawData.objects.filter(trade=trade).select_related('asset_hub')
            asset_count = assets.count()
            
            self.stdout.write(f'   Found {asset_count} assets in trade')
            
            # WHAT: Create LoanLevelAssumption for each asset
            # WHY: Required for loan-specific duration overrides and calculations
            assets_processed = 0
            for asset in assets:
                if not asset.asset_hub:
                    self.stdout.write(f'   [WARNING] Asset {asset.sellertape_id} has no asset_hub, skipping')
                    continue
                
                if not dry_run:
                    loan_assumption, created = LoanLevelAssumption.objects.get_or_create(
                        asset_hub=asset.asset_hub,
                        defaults={}  # Use model defaults
                    )
                    if created:
                        loan_assumptions_created += 1
                        assets_processed += 1
                else:
                    exists = LoanLevelAssumption.objects.filter(asset_hub=asset.asset_hub).exists()
                    if not exists:
                        loan_assumptions_created += 1
                        assets_processed += 1
            
            if assets_processed > 0:
                self.stdout.write(f'   [OK] Created LoanLevelAssumptions for {assets_processed} assets')
            
            self.stdout.write('')  # Blank line
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== SUMMARY ==='))
        self.stdout.write(f'Trades processed: {total_trades}')
        self.stdout.write(f'TradeLevelAssumptions created: {trade_assumptions_created}')
        self.stdout.write(f'LoanLevelAssumptions created: {loan_assumptions_created}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN] No records were actually created\n'))
        else:
            self.stdout.write(self.style.SUCCESS('\n[COMPLETE] Backfill complete!\n'))

