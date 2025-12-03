"""
Backfill SharePoint Folders for Existing Trades/Assets
=======================================================
Creates SharePoint folders for all existing trades and assets in database.
Run once after initial setup to sync existing data.

Usage:
    python manage.py backfill_sharepoint_folders
    python manage.py backfill_sharepoint_folders --dry-run
    python manage.py backfill_sharepoint_folders --trades-only

File Naming Convention: backfill_sharepoint_folders.py
Module: SharePoint
Purpose: Backfill folders for existing database records
"""

from django.core.management.base import BaseCommand
from django.apps import apps
from sharepoint.services.serv_sp_client import SharePointClient
from sharepoint.services.serv_sp_folder_structure import FolderStructure


class Command(BaseCommand):
    help = 'Backfill SharePoint folders for all existing trades and assets'
    
    def _sanitize_folder_name(self, name):
        """
        Sanitize folder name for SharePoint.
        Removes forbidden characters and ensures valid format.
        """
        # SharePoint forbidden chars
        forbidden = ['~', '#', '%', '&', '*', '{', '}', '\\', ':', '<', '>', '?', '/', '|', '"']
        
        sanitized = str(name)
        for char in forbidden:
            sanitized = sanitized.replace(char, '_')
        
        # Remove leading/trailing spaces and periods
        sanitized = sanitized.strip(' .')
        
        # Limit length (SharePoint has 400 char URL limit, be conservative)
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized
    
    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating'
        )
        parser.add_argument(
            '--trades-only',
            action='store_true',
            help='Only create trade-level folders, skip assets'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit to first N trades (for testing)'
        )
    
    def handle(self, *args, **options):
        """Execute command"""
        dry_run = options.get('dry_run', False)
        trades_only = options.get('trades_only', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No folders will be created\n'))
        
        # Get your Trade model - adjust import path as needed
        try:
            # Try to import from acq_module
            # Adjust model name if different in your codebase
            Trade = apps.get_model('acq_module', 'Trade')
        except LookupError:
            self.stdout.write(self.style.ERROR('✗ Could not find Trade model'))
            self.stdout.write('  Update model import in backfill_sharepoint_folders.py')
            return
        
        client = SharePointClient() if not dry_run else None
        
        # Get all trades
        trades = Trade.objects.all()
        
        # Apply limit if specified
        limit = options.get('limit')
        if limit:
            trades = trades[:limit]
            self.stdout.write(self.style.WARNING(f'Limited to first {limit} trades'))
        
        total_trades = trades.count()
        
        if total_trades == 0:
            self.stdout.write(self.style.WARNING('No trades found in database'))
            return
        
        self.stdout.write(self.style.MIGRATE_HEADING(f'\nFound {total_trades} trades\n'))
        
        success_count = 0
        error_count = 0
        
        # Process each trade
        for idx, trade in enumerate(trades, 1):
            # Get trade name and seller name for folder
            trade_name = getattr(trade, 'trade_name', None)
            seller_name = trade.seller.name if trade.seller else None
            
            if not trade_name:
                self.stdout.write(self.style.WARNING(f'  Skipping trade {trade.pk} - no trade_name'))
                continue
            
            # Combine: "Trade Name - Seller Name"
            if seller_name:
                combined_name = f"{trade_name} - {seller_name}"
            else:
                combined_name = trade_name
            
            # Sanitize for SharePoint (remove forbidden chars)
            folder_name = self._sanitize_folder_name(combined_name)
            
            self.stdout.write(f'[{idx}/{total_trades}] Processing: {combined_name} → {folder_name}')
            
            try:
                if dry_run:
                    # Show what would be created
                    folders = FolderStructure.get_trade_folders(folder_name)
                    for folder_path in folders:
                        self.stdout.write(f'  [DRY RUN] Would create: {folder_path}')
                else:
                    # Create folders
                    folders = FolderStructure.get_trade_folders(folder_name)
                    for folder_path in folders:
                        client.create_folder(folder_path)
                    
                    # Update trade with folder path (if field exists)
                    if hasattr(trade, 'sharepoint_folder_path'):
                        trade.sharepoint_folder_path = FolderStructure.get_trade_base_path(folder_name)
                        trade.save(update_fields=['sharepoint_folder_path'])
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created folders'))
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Failed: {str(e)}'))
        
        # Process assets if requested
        if not trades_only:
            self.stdout.write(self.style.MIGRATE_HEADING('\nProcessing assets...'))
            
            try:
                Asset = apps.get_model('acq_module', 'Asset')
                assets = Asset.objects.all()
                total_assets = assets.count()
                
                if total_assets > 0:
                    self.stdout.write(f'Found {total_assets} assets\n')
                    
                    asset_success = 0
                    asset_errors = 0
                    
                    for idx, asset in enumerate(assets, 1):
                        # Get trade name and asset ID
                        trade_name = getattr(asset.trade, 'trade_name', None) if hasattr(asset, 'trade') else None
                        asset_id = getattr(asset, 'asset_id', None) or str(asset.pk)
                        
                        if not trade_name:
                            self.stdout.write(self.style.WARNING(f'  Skipping asset {asset_id} - no trade'))
                            continue
                        
                        folder_name = self._sanitize_folder_name(trade_name)
                        asset_folder = self._sanitize_folder_name(asset_id)
                        
                        self.stdout.write(f'[{idx}/{total_assets}] Processing: {trade_name}/{asset_id}')
                        
                        try:
                            if dry_run:
                                folders = FolderStructure.get_asset_folders(folder_name, asset_folder)
                                for folder_path in folders:
                                    self.stdout.write(f'  [DRY RUN] Would create: {folder_path}')
                            else:
                                folders = FolderStructure.get_asset_folders(folder_name, asset_folder)
                                for folder_path in folders:
                                    client.create_folder(folder_path)
                                
                                if hasattr(asset, 'sharepoint_folder_path'):
                                    asset.sharepoint_folder_path = FolderStructure.get_asset_base_path(folder_name, asset_folder)
                                    asset.save(update_fields=['sharepoint_folder_path'])
                                
                                self.stdout.write(self.style.SUCCESS(f'  ✓ Created folders'))
                            
                            asset_success += 1
                            
                        except Exception as e:
                            asset_errors += 1
                            self.stdout.write(self.style.ERROR(f'  ✗ Failed: {str(e)}'))
                    
                    success_count += asset_success
                    error_count += asset_errors
                    
                else:
                    self.stdout.write('No assets found\n')
                    
            except LookupError:
                self.stdout.write(self.style.WARNING('Asset model not found - skipping assets'))
        
        # Summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.MIGRATE_HEADING('SUMMARY'))
        self.stdout.write('=' * 80)
        self.stdout.write(f'\nTrades processed: {total_trades}')
        if not trades_only and 'total_assets' in locals():
            self.stdout.write(f'Assets processed: {total_assets}')
        self.stdout.write(self.style.SUCCESS(f'✓ Success: {success_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'✗ Errors: {error_count}'))
        
        if dry_run:
            self.stdout.write('\n' + self.style.WARNING('DRY RUN - No changes made'))
            self.stdout.write('Run without --dry-run to create folders')
        else:
            self.stdout.write('\n' + self.style.SUCCESS('✓ Backfill complete!'))
            self.stdout.write('\nCheck SharePoint:')
            self.stdout.write('  https://firstliencapitaldom.sharepoint.com/sites/ProjectAlpha')

