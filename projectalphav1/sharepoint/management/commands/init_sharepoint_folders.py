"""
Initialize SharePoint Folder Structure
=======================================
Management command to create base SharePoint folder structure.
Run once initially or when adding new folder categories.

Usage:
    python manage.py init_sharepoint_folders
    python manage.py init_sharepoint_folders --trade TRD-2024-001
    python manage.py init_sharepoint_folders --dry-run

File Naming Convention: init_sharepoint_folders.py (management command)
Module: SharePoint
Purpose: Initialize folder structure in SharePoint
"""

from django.core.management.base import BaseCommand
from sharepoint.services.serv_sp_client import SharePointClient
from sharepoint.services.serv_sp_folder_structure import FolderStructure


class Command(BaseCommand):
    help = 'Initialize SharePoint folder structure for trades and assets'
    
    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(
            '--trade',
            type=str,
            help='Create folders for specific trade ID only'
        )
        parser.add_argument(
            '--asset',
            type=str,
            help='Create folders for specific asset (requires --trade)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating'
        )
    
    def handle(self, *args, **options):
        """Execute command"""
        dry_run = options.get('dry_run', False)
        trade_id = options.get('trade')
        asset_id = options.get('asset')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No folders will be created'))
        
        client = SharePointClient()
        
        # Verify connection
        try:
            site_info = client.get_site_info()
            self.stdout.write(self.style.SUCCESS(f"✓ Connected to: {site_info['displayName']}"))
            self.stdout.write(f"  URL: {site_info['webUrl']}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Failed to connect: {str(e)}"))
            return
        
        if trade_id:
            # Create folders for specific trade
            self._create_trade_folders(client, trade_id, asset_id, dry_run)
        else:
            # Create base structure only
            self._create_base_structure(client, dry_run)
    
    def _create_base_structure(self, client, dry_run):
        """Create base Trades folder"""
        self.stdout.write(self.style.MIGRATE_HEADING('\n Creating base structure...'))
        
        folders_to_create = [
            f"/{FolderStructure.ROOT_TRADES}"
        ]
        
        for folder_path in folders_to_create:
            if dry_run:
                self.stdout.write(f"  [DRY RUN] Would create: {folder_path}")
            else:
                try:
                    client.create_folder(folder_path)
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Created: {folder_path}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✗ Failed: {folder_path} - {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Base structure complete!'))
        self.stdout.write('\nNext steps:')
        self.stdout.write('  - Run with --trade TRD-ID to create trade folders')
        self.stdout.write('  - Or trades will auto-create folders when created in platform')
    
    def _create_trade_folders(self, client, trade_id, asset_id, dry_run):
        """Create folders for a trade and optionally asset"""
        self.stdout.write(self.style.MIGRATE_HEADING(f'\n Creating folders for Trade: {trade_id}'))
        
        # Get trade folders
        trade_folders = FolderStructure.get_trade_folders(trade_id)
        
        # Create trade base and folders
        for folder_path in trade_folders:
            if dry_run:
                self.stdout.write(f"  [DRY RUN] Would create: {folder_path}")
            else:
                try:
                    client.create_folder(folder_path)
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Created: {folder_path}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✗ Failed: {folder_path} - {str(e)}"))
        
        # If asset specified, create asset folders
        if asset_id:
            self.stdout.write(self.style.MIGRATE_HEADING(f'\n Creating folders for Asset: {asset_id}'))
            asset_folders = FolderStructure.get_asset_folders(trade_id, asset_id)
            
            for folder_path in asset_folders:
                if dry_run:
                    self.stdout.write(f"  [DRY RUN] Would create: {folder_path}")
                else:
                    try:
                        client.create_folder(folder_path)
                        self.stdout.write(self.style.SUCCESS(f"  ✓ Created: {folder_path}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  ✗ Failed: {folder_path} - {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Folders created for {trade_id}'))
        
        # Show structure
        self.stdout.write('\nFolder structure:')
        base_path = FolderStructure.get_trade_base_path(trade_id)
        self.stdout.write(f"  {base_path}/")
        for folder in FolderStructure.TRADE_FOLDERS:
            if folder == "Assets" and asset_id:
                self.stdout.write(f"    {folder}/")
                self.stdout.write(f"      {asset_id}/")
                for asset_folder in FolderStructure.ASSET_FOLDERS:
                    self.stdout.write(f"        {asset_folder}/")
            else:
                self.stdout.write(f"    {folder}/")

