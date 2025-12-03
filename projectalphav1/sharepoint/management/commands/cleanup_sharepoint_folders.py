"""
Cleanup SharePoint Folders
===========================
Delete all folders under /Trades to start fresh.
Use when changing folder naming strategy.

Usage:
    python manage.py cleanup_sharepoint_folders
    python manage.py cleanup_sharepoint_folders --dry-run

File Naming Convention: cleanup_sharepoint_folders.py
Module: SharePoint
Purpose: Delete existing folders for fresh start
"""

from django.core.management.base import BaseCommand
from sharepoint.services.serv_sp_client import SharePointClient
import requests


class Command(BaseCommand):
    help = 'Delete all folders under /Trades in SharePoint'
    
    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        """Execute command"""
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - Nothing will be deleted\n'))
        else:
            self.stdout.write(self.style.ERROR('⚠️  WARNING: This will delete ALL folders under /Trades'))
            confirm = input('Type "DELETE" to confirm: ')
            if confirm != 'DELETE':
                self.stdout.write('Cancelled')
                return
        
        client = SharePointClient()
        
        try:
            # Get drive ID
            drive_id = client._get_drive_id()
            token = client._get_access_token()
            headers = {
                'Authorization': f'Bearer {token}',
            }
            
            # Get all items in /Trades folder
            trades_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/Trades:/children"
            response = requests.get(trades_url, headers=headers)
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Failed to list folders: {response.text}'))
                return
            
            items = response.json().get('value', [])
            
            if not items:
                self.stdout.write('No folders found under /Trades')
                return
            
            self.stdout.write(f'\nFound {len(items)} items to delete:\n')
            
            for item in items:
                name = item['name']
                item_id = item['id']
                
                if dry_run:
                    self.stdout.write(f'  [DRY RUN] Would delete: /Trades/{name}')
                else:
                    # Delete item
                    delete_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}"
                    delete_response = requests.delete(delete_url, headers=headers)
                    
                    if delete_response.status_code in [204, 200]:
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted: /Trades/{name}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'  ✗ Failed to delete {name}: {delete_response.text}'))
            
            if dry_run:
                self.stdout.write('\n' + self.style.WARNING('DRY RUN - Nothing was deleted'))
            else:
                self.stdout.write('\n' + self.style.SUCCESS('✓ Cleanup complete!'))
                self.stdout.write('\nNow run backfill with trade_name:')
                self.stdout.write('  python manage.py backfill_sharepoint_folders --trades-only')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

