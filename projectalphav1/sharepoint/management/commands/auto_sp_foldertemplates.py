"""
SharePoint Folder Management - Unified Command
===============================================
All SharePoint folder operations in one command.

Usage:
    python manage.py auto_sp_foldertemplates init                              # Create base structure
    python manage.py auto_sp_foldertemplates sync --trade-id 1015              # Sync one trade
    python manage.py auto_sp_foldertemplates sync --trade-filter FLC-25        # Sync trades FLC-25+
    python manage.py auto_sp_foldertemplates sync --all                        # Sync all trades
    python manage.py auto_sp_foldertemplates cleanup                           # Delete all
    python manage.py auto_sp_foldertemplates rename --old "Assets" --new "Asset Level"

File Naming Convention: auto_sp_foldertemplates.py
Module: SharePoint
Purpose: Unified folder management command
"""

from django.core.management.base import BaseCommand
from django.apps import apps
from sharepoint.services.serv_sp_client import SharePointClient
from sharepoint.services.serv_sp_folder_structure import FolderStructure
import requests
import re
import time


class Command(BaseCommand):
    help = 'Unified SharePoint folder management'
    
    def add_arguments(self, parser):
        """Add command arguments"""
        # Subcommands
        parser.add_argument(
            'action',
            type=str,
            choices=['init', 'sync', 'cleanup', 'rename', 'update-metadata'],
            help='Action to perform'
        )
        
        # Sync options
        parser.add_argument('--trade-id', type=int, help='Specific trade ID (e.g., 1015)')
        parser.add_argument('--trade-filter', type=int, help='Trades >= this ID (e.g., 1015 for all trades from 1015 onwards)')
        parser.add_argument('--all', action='store_true', help='All trades')
        parser.add_argument('--limit', type=int, help='Limit to N trades')
        
        # Rename options
        parser.add_argument('--old', type=str, help='Old folder name')
        parser.add_argument('--new', type=str, help='New folder name')
        
        # Global options
        parser.add_argument('--dry-run', action='store_true', help='Preview only')
        parser.add_argument('--batch', action='store_true', help='Use batch mode (faster but less feedback)')
    
    def handle(self, *args, **options):
        """Route to appropriate handler"""
        action = options['action']
        
        if action == 'init':
            self._handle_init(options)
        elif action == 'sync':
            self._handle_sync(options)
        elif action == 'cleanup':
            self._handle_cleanup(options)
        elif action == 'rename':
            self._handle_rename(options)
        elif action == 'update-metadata':
            self._handle_update_metadata(options)
    
    def _sanitize(self, name):
        """Sanitize folder name for SharePoint"""
        for char in ['~', '#', '%', '&', '*', '{', '}', '\\', ':', '<', '>', '?', '/', '|', '"']:
            name = name.replace(char, '_')
        return name.strip(' .')[:100]
    
    def _handle_init(self, options):
        """Initialize base /Trades folder structure"""
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.MIGRATE_HEADING('Initialize SharePoint Base Structure'))
        
        if dry_run:
            self.stdout.write('[DRY RUN] Would create: /Trades')
            return
        
        client = SharePointClient()
        try:
            site_info = client.get_site_info()
            self.stdout.write(self.style.SUCCESS(f"✓ Connected: {site_info['displayName']}"))
            
            client.create_folder(f"/{FolderStructure.ROOT_TRADES}")
            self.stdout.write(self.style.SUCCESS(f"✓ Created: /{FolderStructure.ROOT_TRADES}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed: {str(e)}"))
    
    def _handle_sync(self, options):
        """Sync trades and assets to SharePoint"""
        dry_run = options.get('dry_run', False)
        use_batch = options.get('batch', False)
        
        # Get models
        Trade = apps.get_model('acq_module', 'Trade')
        Asset = apps.get_model('acq_module', 'SellerRawData')
        
        # Query trades
        trades = Trade.objects.all()
        
        # Apply filters
        if options.get('trade_id'):
            trades = trades.filter(pk=options['trade_id'])
        elif options.get('trade_filter'):
            min_id = options['trade_filter']
            trades = trades.filter(pk__gte=min_id)
            self.stdout.write(self.style.WARNING(f'Filtered to trade IDs >= {min_id}'))
        
        if options.get('limit'):
            trades = trades[:options['limit']]
        
        if not trades.exists():
            self.stdout.write('No trades found')
            return
        
        self.stdout.write(f'\nSyncing {trades.count()} trades\n')
        
        client = SharePointClient() if not dry_run else None
        total_assets = 0
        
        # Process each trade
        for t_idx, trade in enumerate(trades, 1):
            trade_name = trade.trade_name
            seller_name = trade.seller.name if trade.seller else None
            
            if not trade_name:
                continue
            
            # Build folder name
            combined = f"{trade_name} - {seller_name}" if seller_name else trade_name
            folder_name = self._sanitize(combined)
            
            self.stdout.write(f'[{t_idx}/{trades.count()}] {combined}')
            
            # Create trade folders first
            if not dry_run:
                try:
                    for folder_path in FolderStructure.get_trade_folders(folder_name):
                        self._create_with_retry(client, folder_path, skip_parent_check=True)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Failed trade folders: {str(e)}'))
                    continue
            
            # Get assets for this trade
            assets = Asset.objects.filter(trade=trade).order_by('pk')
            asset_count = assets.count()
            
            if not asset_count:
                self.stdout.write('  No assets')
                continue
            
            self.stdout.write(f'  Creating folders for {asset_count} assets...')
            
            # Process each asset sequentially (reliable)
            for a_idx, asset in enumerate(assets, 1):
                # Get asset info
                asset_hub_id = asset.asset_hub.id if asset.asset_hub else asset.pk
                servicer_id = asset.asset_hub.servicer_id if (asset.asset_hub and asset.asset_hub.servicer_id) else None
                sellertape_id = asset.asset_hub.sellertape_id if (asset.asset_hub and asset.asset_hub.sellertape_id) else None
                
                # Get address
                street = asset.street_address or ''
                city = asset.city or ''
                state = asset.state or ''
                zip_code = asset.zip or ''
                full_address = f"{street}, {city}, {state} {zip_code}".strip(', ')
                
                # Build asset folder name (servicer_id as primary)
                if servicer_id:
                    asset_folder = str(servicer_id)
                else:
                    asset_folder = f"NO_SERVICER_{asset_hub_id}"
                
                # Metadata to store on folder
                metadata = {
                    'asset_hub_id': asset_hub_id,
                    'servicer_id': servicer_id,
                    'sellertape_id': sellertape_id,
                    'trade_id': trade.pk,
                    'trade_name': trade.trade_name,
                    'address': full_address
                }
                
                if dry_run:
                    continue
                
                # Create folders IN CORRECT ORDER
                try:
                    # Create base asset folder first with metadata
                    base_path = FolderStructure.get_asset_base_path(folder_name, asset_folder)
                    folder_info = self._create_with_retry(client, base_path, skip_parent_check=True)
                    
                    # Set metadata on base folder
                    if folder_info and 'id' in folder_info:
                        try:
                            self._set_folder_metadata(client, folder_info['id'], metadata)
                        except Exception as e:
                            self.stdout.write(f'      ⚠ Metadata failed: {str(e)}')
                    
                    # Then create all category folders
                    for folder in FolderStructure.ASSET_FOLDERS:
                        cat_path = f"{base_path}/{folder}"
                        self._create_with_retry(client, cat_path, skip_parent_check=True)
                        
                        # Create subfolders if defined
                        if folder in FolderStructure.ASSET_SUBFOLDERS:
                            for subfolder in FolderStructure.ASSET_SUBFOLDERS[folder]:
                                sub_path = f"{cat_path}/{subfolder}"
                                self._create_with_retry(client, sub_path, skip_parent_check=True)
                    
                    total_assets += 1
                    
                    # Progress + small delay every 5 assets to avoid throttling
                    if a_idx % 5 == 0:
                        time.sleep(0.5)  # Half second pause
                    
                    if a_idx % 10 == 0 or a_idx == asset_count:
                        self.stdout.write(f'    [{a_idx}/{asset_count}] Complete')
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    [{a_idx}] Failed {asset_folder}: {str(e)}'))
        
        # Summary
        self.stdout.write('\n' + '=' * 80)
        if dry_run:
            self.stdout.write('[DRY RUN]')
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Synced {total_assets} assets'))
    
    def _handle_cleanup(self, options):
        """Delete all folders under /Trades"""
        dry_run = options.get('dry_run', False)
        
        if not dry_run:
            self.stdout.write(self.style.ERROR('⚠️  WARNING: Delete ALL folders under /Trades'))
            confirm = input('Type "DELETE" to confirm: ')
            if confirm != 'DELETE':
                self.stdout.write('Cancelled')
                return
        
        client = SharePointClient()
        drive_id = client._get_drive_id()
        token = client._get_access_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get all trade folders
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/Trades:/children"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f'Failed to list: {response.text}'))
            return
        
        items = response.json().get('value', [])
        self.stdout.write(f'\nFound {len(items)} items\n')
        
        for item in items:
            name = item['name']
            if dry_run:
                self.stdout.write(f'[DRY RUN] Would delete: /Trades/{name}')
            else:
                delete_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item['id']}"
                delete_response = requests.delete(delete_url, headers=headers)
                if delete_response.status_code in [204, 200]:
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted: {name}'))
                else:
                    self.stdout.write(self.style.ERROR(f'✗ Failed: {name}'))
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS('\n✓ Cleanup complete'))
    
    def _handle_rename(self, options):
        """Rename folders"""
        old_name = options.get('old')
        new_name = options.get('new')
        dry_run = options.get('dry_run', False)
        
        if not old_name or not new_name:
            self.stdout.write(self.style.ERROR('Both --old and --new required'))
            return
        
        self.stdout.write(f'Renaming: "{old_name}" → "{new_name}"')
        
        client = SharePointClient()
        drive_id = client._get_drive_id()
        token = client._get_access_token()
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Get all trades
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/Trades:/children"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f'Failed: {response.text}'))
            return
        
        trades = response.json().get('value', [])
        renamed = 0
        
        for trade in trades:
            # Get children
            children_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{trade['id']}/children"
            children_response = requests.get(children_url, headers=headers)
            
            if children_response.status_code != 200:
                continue
            
            for child in children_response.json().get('value', []):
                if child.get('name') == old_name and 'folder' in child:
                    if dry_run:
                        self.stdout.write(f'[DRY RUN] Would rename in: {trade["name"]}')
                    else:
                        rename_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{child['id']}"
                        rename_response = requests.patch(rename_url, headers=headers, json={'name': new_name})
                        if rename_response.status_code == 200:
                            self.stdout.write(self.style.SUCCESS(f'✓ {trade["name"]}'))
                            renamed += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Renamed {renamed} folders'))
    
    def _handle_update_metadata(self, options):
        """Update metadata on existing folders without recreating them"""
        dry_run = options.get('dry_run', False)
        trade_filter = options.get('trade_filter')
        trade_id = options.get('trade_id')
        
        self.stdout.write(self.style.MIGRATE_HEADING('Updating folder metadata\n'))
        
        # Get models
        Trade = apps.get_model('acq_module', 'Trade')
        Asset = apps.get_model('acq_module', 'SellerRawData')
        
        # Query trades
        trades = Trade.objects.all()
        
        if trade_id:
            trades = trades.filter(pk=trade_id)
        elif trade_filter:
            trades = trades.filter(pk__gte=trade_filter)
        
        client = SharePointClient() if not dry_run else None
        drive_id = client._get_drive_id() if client else None
        updated = 0
        
        # Process each trade
        for trade in trades:
            trade_name = trade.trade_name
            seller_name = trade.seller.name if trade.seller else None
            
            if not trade_name:
                continue
            
            combined = f"{trade_name} - {seller_name}" if seller_name else trade_name
            folder_name = self._sanitize(combined)
            
            self.stdout.write(f'\n{combined}')
            
            # Get assets
            assets = Asset.objects.filter(trade=trade)
            
            for asset in assets:
                asset_hub_id = asset.asset_hub.id if asset.asset_hub else asset.pk
                servicer_id = asset.asset_hub.servicer_id if (asset.asset_hub and asset.asset_hub.servicer_id) else None
                sellertape_id = asset.asset_hub.sellertape_id if (asset.asset_hub and asset.asset_hub.sellertape_id) else None
                
                # Get address
                street = asset.street_address or ''
                city = asset.city or ''
                state = asset.state or ''
                zip_code = asset.zip or ''
                full_address = f"{street}, {city}, {state} {zip_code}".strip(', ')
                
                asset_folder = str(servicer_id) if servicer_id else f"NO_SERVICER_{asset_hub_id}"
                base_path = FolderStructure.get_asset_base_path(folder_name, asset_folder)
                
                # Build metadata
                metadata = {
                    'asset_hub_id': asset_hub_id,
                    'servicer_id': servicer_id,
                    'sellertape_id': sellertape_id,
                    'address': full_address,
                    'trade_id': trade.pk,
                    'trade_name': trade.trade_name
                }
                
                if dry_run:
                    continue
                
                # Find folder in SharePoint and update metadata
                try:
                    # Get folder ID
                    folder_path = base_path.strip('/')
                    get_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{folder_path}"
                    token = client._get_access_token()
                    headers = {'Authorization': f'Bearer {token}'}
                    
                    response = requests.get(get_url, headers=headers)
                    if response.status_code == 200:
                        folder_id = response.json()['id']
                        self._set_folder_metadata(client, folder_id, metadata)
                        updated += 1
                
                except Exception as e:
                    self.stdout.write(f'  ⚠ Failed {asset_folder}: {str(e)[:50]}')
            
            self.stdout.write(f'  ✓ Updated {assets.count()} assets')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Updated metadata on {updated} folders'))
    
    def _make_folder_request(self, folder_path, request_id):
        """Build batch request for folder creation"""
        parts = folder_path.strip('/').split('/')
        parent = '/'.join(parts[:-1]) if len(parts) > 1 else ''
        name = parts[-1]
        
        if parent:
            url = f"/drives/{{drive_id}}/root:/{parent}:/children"
        else:
            url = f"/drives/{{drive_id}}/root/children"
        
        return {
            "id": str(request_id),
            "method": "POST",
            "url": url,
            "headers": {"Content-Type": "application/json"},
            "body": {
                "name": name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename"
            }
        }
    
    def _execute_batches(self, client, requests_list):
        """Execute batch requests in chunks of 20"""
        drive_id = client._get_drive_id()
        token = client._get_access_token()
        
        # Replace drive_id placeholder
        for req in requests_list:
            req['url'] = req['url'].replace('{drive_id}', drive_id)
        
        # Process in chunks of 20
        chunk_size = 20
        for i in range(0, len(requests_list), chunk_size):
            chunk = requests_list[i:i + chunk_size]
            
            batch_data = {"requests": chunk}
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                'https://graph.microsoft.com/v1.0/$batch',
                headers=headers,
                json=batch_data
            )
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Batch failed: {response.text}'))
                continue
            
            # Progress indicator
            self.stdout.write(f'      Batch {i//chunk_size + 1}/{(len(requests_list)-1)//chunk_size + 1} complete')
            
            # Delay between batches to avoid throttling
            if i + chunk_size < len(requests_list):
                time.sleep(1)  # 1 second delay between batches
    
    def _create_with_retry(self, client, folder_path, skip_parent_check=False, max_retries=3):
        """Create folder with retry on throttling and token expiration"""
        for attempt in range(max_retries):
            try:
                return client.create_folder(folder_path, skip_parent_check=skip_parent_check)
            except Exception as e:
                error_str = str(e).lower()
                
                # Handle token expiration
                if 'invalidauthenticationtoken' in error_str or 'expired' in error_str:
                    if attempt < max_retries - 1:
                        self.stdout.write(f'    Token expired - refreshing...')
                        client._access_token = None  # Force token refresh
                        time.sleep(2)
                        continue
                
                # Handle throttling
                if 'throttled' in error_str or 'activitylimitreached' in error_str:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                        self.stdout.write(f'    Throttled - waiting {wait_time}s...')
                        time.sleep(wait_time)
                        continue
                
                raise
    
    def _set_folder_metadata(self, client, folder_id, metadata):
        """Set metadata on folder using description field"""
        drive_id = client._get_drive_id()
        token = client._get_access_token()
        
        # Build description from metadata
        desc_parts = []
        if metadata.get('asset_hub_id'):
            desc_parts.append(f"AssetHub:{metadata['asset_hub_id']}")
        if metadata.get('servicer_id'):
            desc_parts.append(f"Servicer:{metadata['servicer_id']}")
        if metadata.get('sellertape_id'):
            desc_parts.append(f"Tape:{metadata['sellertape_id']}")
        if metadata.get('address'):
            desc_parts.append(f"Address:{metadata['address']}")
        if metadata.get('trade_id'):
            desc_parts.append(f"TradeID:{metadata['trade_id']}")
        if metadata.get('trade_name'):
            desc_parts.append(f"Trade:{metadata['trade_name']}")
        
        description = " | ".join(desc_parts)
        
        # Update folder
        update_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.patch(update_url, headers=headers, json={'description': description})
        
        if response.status_code != 200:
            raise Exception(f"Failed to set metadata: {response.text}")
        
        return True

