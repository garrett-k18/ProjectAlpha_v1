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

    # SharePoint listItem field internal names (NOT display names)
    # If your SharePoint library uses different internal names, update these.
    SP_FIELD_MAP = {
        'trade_id': 'TradeID',
        'trade_name': 'Trade',
        'seller_name': 'Seller',
        'asset_hub_id': 'AssetHub',
        'servicer_id': 'Servicer',
        'sellertape_id': 'Tape',
        'address': 'Address',
    }

    _sp_columns_cache = None
    
    def add_arguments(self, parser):
        """Add command arguments"""
        # Subcommands
        parser.add_argument(
            'action',
            type=str,
            choices=['init', 'sync', 'cleanup', 'rename', 'update-metadata', 'migrate-names'],
            help='Action to perform'
        )
        
        # Sync options
        parser.add_argument('--trade-id', type=int, help='Specific trade ID (e.g., 1015)')
        parser.add_argument('--trade-filter', type=int, help='Trades >= this ID (e.g., 1015 for all trades from 1015 onwards)')
        parser.add_argument('--all', action='store_true', help='All trades')
        parser.add_argument('--limit', type=int, help='Limit to N trades')
        parser.add_argument('--keep-only', action='store_true', help='Only assets with acq_status=KEEP')
        
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
        elif action == 'migrate-names':
            self._handle_migrate_names(options)
    
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
        keep_only = options.get('keep_only', False)
        
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
                    # Create trade root folder and stamp metadata for stable linking
                    trade_base_path = FolderStructure.get_trade_base_path(folder_name)
                    trade_metadata = {
                        'trade_id': trade.pk,
                        'trade_name': trade.trade_name,
                        'seller_name': seller_name,
                    }

                    trade_root_info = self._create_with_retry(client, trade_base_path, skip_parent_check=True)
                    if trade_root_info and 'id' in trade_root_info:
                        try:
                            self._set_folder_metadata(client, trade_root_info['id'], trade_metadata)
                        except Exception as e:
                            self.stdout.write(f'  ⚠ Trade folder metadata failed: {str(e)}')

                    for folder_path in FolderStructure.get_trade_folders(folder_name):
                        self._create_with_retry(client, folder_path, skip_parent_check=True)

                    try:
                        self._apply_trade_default_sort_orders(client, trade_base_path)
                    except Exception as e:
                        self.stdout.write(f'  ⚠ DefaultSortOrder failed: {str(e)}')

                    # Stamp metadata on Trade Level folder as well
                    trade_level_path = f"{trade_base_path}/Trade Level"
                    trade_level_info = self._create_with_retry(client, trade_level_path, skip_parent_check=True)
                    if trade_level_info and 'id' in trade_level_info:
                        try:
                            self._set_folder_metadata(client, trade_level_info['id'], trade_metadata)
                        except Exception as e:
                            self.stdout.write(f'  ⚠ Trade Level metadata failed: {str(e)}')

                    # Stamp metadata on all Trade Level subfolders (Seller Data Dump, Due Diligence, Bid, Award, etc.)
                    for tl_folder_name in FolderStructure.TRADE_LEVEL_FOLDERS:
                        tl_folder_path = f"{trade_level_path}/{tl_folder_name}"
                        tl_info = self._create_with_retry(client, tl_folder_path, skip_parent_check=True)
                        if tl_info and 'id' in tl_info:
                            try:
                                self._set_folder_metadata(client, tl_info['id'], trade_metadata)
                            except Exception as e:
                                self.stdout.write(
                                    f"  ⚠ Trade Level subfolder metadata failed ({tl_folder_name}): {str(e)[:80]}"
                                )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Failed trade folders: {str(e)}'))
                    continue
            
            # Get assets for this trade
            assets = Asset.objects.filter(trade=trade).order_by('pk')

            if keep_only:
                assets = assets.filter(acq_status=Asset.AcquisitionStatus.KEEP)
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

                # Build asset folder name: "{primary_id} - {address}" (sanitized)
                # primary_id: servicer_id -> sellertape_id -> asset_hub_id
                primary_id = servicer_id or sellertape_id or asset_hub_id
                asset_folder = self._sanitize(f"{primary_id} - {full_address}" if full_address else str(primary_id))
                
                # Metadata to store on asset folders (parent + all children)
                metadata = {
                    'asset_hub_id': asset_hub_id,
                    'servicer_id': servicer_id,
                    'sellertape_id': sellertape_id,
                    'trade_id': trade.pk,
                    'trade_name': trade.trade_name,
                    'seller_name': seller_name,
                    'address': full_address,
                }
                
                if dry_run:
                    continue
                
                # Create folders IN CORRECT ORDER
                try:
                    # Create base asset folder first with metadata
                    base_path = FolderStructure.get_asset_base_path(folder_name, asset_folder)
                    folder_info = self._create_with_retry(client, base_path, skip_parent_check=True)
                    
                    # Set metadata on base asset folder (parent)
                    if folder_info and 'id' in folder_info:
                        try:
                            self._set_folder_metadata(client, folder_info['id'], metadata)
                        except Exception as e:
                            self.stdout.write(f'      ⚠ Metadata failed (asset base): {str(e)[:80]}')

                    # Then create all category folders and stamp metadata
                    for folder in FolderStructure.ASSET_FOLDERS:
                        cat_path = f"{base_path}/{folder}"
                        cat_info = self._create_with_retry(client, cat_path, skip_parent_check=True)
                        if cat_info and 'id' in cat_info:
                            try:
                                self._set_folder_metadata(client, cat_info['id'], metadata)
                            except Exception as e:
                                self.stdout.write(
                                    f'      ⚠ Metadata failed (asset folder {folder}): {str(e)[:80]}'
                                )
                        
                        # Create subfolders if defined and stamp metadata
                        if folder in FolderStructure.ASSET_SUBFOLDERS:
                            for subfolder in FolderStructure.ASSET_SUBFOLDERS[folder]:
                                sub_path = f"{cat_path}/{subfolder}"
                                sub_info = self._create_with_retry(client, sub_path, skip_parent_check=True)
                                if sub_info and 'id' in sub_info:
                                    try:
                                        self._set_folder_metadata(client, sub_info['id'], metadata)
                                    except Exception as e:
                                        self.stdout.write(
                                            f'      ⚠ Metadata failed (asset subfolder {folder}/{subfolder}): {str(e)[:80]}'
                                        )

                    # Apply DefaultSortOrder to asset-level folders (Valuation, Loan File, etc.)
                    try:
                        self._apply_asset_default_sort_orders(client, base_path)
                    except Exception as e:
                        self.stdout.write(f'      ⚠ DefaultSortOrder (asset folders) failed: {str(e)[:80]}')
                    
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

                # Primary (current) naming convention
                primary_id = servicer_id or sellertape_id or asset_hub_id
                asset_folder = self._sanitize(f"{primary_id} - {full_address}" if full_address else str(primary_id))
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
                    if response.status_code != 200:
                        # Fallback: legacy naming used in older versions
                        legacy_candidates = []
                        if servicer_id:
                            legacy_candidates.append(str(servicer_id))
                        if sellertape_id:
                            legacy_candidates.append(str(sellertape_id))
                        legacy_candidates.append(str(asset_hub_id))
                        legacy_candidates.append(f"NO_SERVICER_{asset_hub_id}")

                        for legacy_asset_folder in legacy_candidates:
                            legacy_base_path = FolderStructure.get_asset_base_path(folder_name, legacy_asset_folder)
                            legacy_folder_path = legacy_base_path.strip('/')
                            legacy_get_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{legacy_folder_path}"
                            response = requests.get(legacy_get_url, headers=headers)
                            if response.status_code == 200:
                                break

                    if response.status_code == 200:
                        folder_id = response.json()['id']
                        self._set_folder_metadata(client, folder_id, metadata)
                        updated += 1
                
                except Exception as e:
                    self.stdout.write(f'  ⚠ Failed {asset_folder}: {str(e)[:50]}')
            
            self.stdout.write(f'  ✓ Updated {assets.count()} assets')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Updated metadata on {updated} folders'))
    
    def _handle_migrate_names(self, options):
        """Rename existing folders to new naming convention (servicer_id or sellertape_id)"""
        dry_run = options.get('dry_run', False)
        trade_filter = options.get('trade_filter')
        trade_id = options.get('trade_id')
        
        self.stdout.write(self.style.MIGRATE_HEADING('Migrating folder names to new convention\n'))
        
        if not dry_run:
            self.stdout.write(self.style.WARNING('This will rename folders in SharePoint'))
            confirm = input('Type "RENAME" to confirm: ')
            if confirm != 'RENAME':
                self.stdout.write('Cancelled')
                return
        
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
        renamed = 0
        
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
                
                # Determine new name
                if servicer_id:
                    new_name = str(servicer_id)
                elif sellertape_id:
                    new_name = str(sellertape_id)
                else:
                    new_name = f"UNKNOWN_{asset_hub_id}"
                
                # Possible old names
                old_names = [
                    f"{asset_hub_id} - {servicer_id}" if servicer_id else None,
                    f"NO_SERVICER_{asset_hub_id}",
                    str(asset_hub_id),
                ]
                old_names = [n for n in old_names if n and n != new_name]
                
                if dry_run:
                    self.stdout.write(f'  Would rename to: {new_name}')
                    continue
                
                # Try to find and rename folder
                try:
                    drive_id = client._get_drive_id()
                    token = client._get_access_token()
                    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
                    
                    # Try each possible old name
                    for old_name in old_names:
                        old_path = FolderStructure.get_asset_base_path(folder_name, old_name).strip('/')
                        get_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{old_path}"
                        
                        response = requests.get(get_url, headers={'Authorization': f'Bearer {token}'})
                        
                        if response.status_code == 200:
                            # Found folder - rename it
                            folder_id = response.json()['id']
                            rename_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}"
                            rename_response = requests.patch(rename_url, headers=headers, json={'name': new_name})
                            
                            if rename_response.status_code == 200:
                                self.stdout.write(self.style.SUCCESS(f'  ✓ {old_name} → {new_name}'))
                                renamed += 1
                                break
                            else:
                                self.stdout.write(f'  ⚠ Rename failed: {rename_response.text[:50]}')
                
                except Exception as e:
                    self.stdout.write(f'  ✗ Error: {str(e)[:50]}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Renamed {renamed} folders'))
    
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
        """Set SharePoint metadata columns on a folder (NOT description)."""
        # Build list of (resolved_field_name, value_as_string)
        resolved_fields = []
        for key, value in (metadata or {}).items():
            if value is None or value == '':
                continue
            sp_field = self.SP_FIELD_MAP.get(key)
            if not sp_field:
                continue
            internal_name = self._resolve_sp_field_name(client, sp_field)
            # Cast to string for safety; SharePoint text columns accept string
            resolved_fields.append((internal_name, str(value)))

        if not resolved_fields:
            return True

        any_success = False
        errors = []

        # Write each field individually so one bad column doesn't block others
        for internal_name, value in resolved_fields:
            try:
                self._set_sharepoint_fields_by_item_id(client, folder_id, {internal_name: value})
                any_success = True
            except Exception as e:
                errors.append((internal_name, str(e)))

        if any_success:
            # At least one field was written; log any failures but do not fall back
            if errors:
                failed_keys = [name for name, _ in errors]
                self.stdout.write(
                    f"  ⚠ Some metadata fields failed (partial success). "
                    f"Failed={failed_keys}. FirstError={errors[0][1][:120]}"
                )
            return True

        # If no fields could be written at all, fall back to description metadata
        try:
            self._debug_print_item_fields(client, folder_id)
        except Exception:
            pass

        failed_field_names = [name for name, _ in resolved_fields]
        first_error = errors[0][1] if errors else 'Unknown error'
        self.stdout.write(
            f"  ⚠ Metadata fields failed (no fields written). "
            f"Fields={failed_field_names}. Error={first_error}"
        )
        # Do not attempt to use the folder description as a metadata store anymore.
        # We only rely on real SharePoint columns; sync remains non-fatal.
        return True

    def _resolve_sp_field_name(self, client, desired_name: str) -> str:
        """Resolve a SharePoint column internal name from a display-ish name.

        SharePoint column display names often differ from internal field names.
        Graph listItem/fields PATCH requires the internal field `name`.
        """
        if not desired_name:
            return desired_name

        columns = self._get_sp_columns(client)
        if not columns:
            return desired_name

        desired_norm = str(desired_name).strip().lower()

        # Best: match column.name (internal) directly
        for col in columns:
            internal = (col.get('name') or '').strip()
            if internal.lower() == desired_norm:
                return internal

        # Next: match displayName
        for col in columns:
            internal = (col.get('name') or '').strip()
            display = (col.get('displayName') or '').strip().lower()
            if display == desired_norm and internal:
                return internal

        return desired_name

    def _get_sp_columns(self, client):
        """Fetch and cache the document library columns for the current drive."""
        if self._sp_columns_cache is not None:
            return self._sp_columns_cache

        try:
            drive_id = client._get_drive_id()
            token = client._get_access_token()
            headers = {'Authorization': f'Bearer {token}'}

            # Get list metadata for the drive (document library)
            list_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/list?$select=id"
            list_resp = requests.get(list_url, headers=headers)
            if list_resp.status_code != 200:
                self._sp_columns_cache = []
                return self._sp_columns_cache

            list_id = (list_resp.json() or {}).get('id')
            if not list_id:
                self._sp_columns_cache = []
                return self._sp_columns_cache

            # Get columns schema
            cols_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/list/columns?$select=name,displayName"
            cols_resp = requests.get(cols_url, headers=headers)
            if cols_resp.status_code != 200:
                self._sp_columns_cache = []
                return self._sp_columns_cache

            self._sp_columns_cache = (cols_resp.json() or {}).get('value', [])
            return self._sp_columns_cache
        except Exception:
            self._sp_columns_cache = []
            return self._sp_columns_cache

    def _debug_print_item_fields(self, client, item_id: str) -> None:
        """Debug helper: prints available listItem/fields keys for a drive item."""
        drive_id = client._get_drive_id()
        token = client._get_access_token()
        headers = {'Authorization': f'Bearer {token}'}

        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/listItem/fields"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return

        data = response.json() or {}
        keys = sorted([k for k in data.keys() if not k.startswith('@')])
        preview = keys[:40]
        self.stdout.write(f"  ℹ Available listItem fields (first {len(preview)}): {preview}")

        # Also print the document library column schema (this is what PATCH expects)
        cols = self._get_sp_columns(client) or []
        wanted = {'tradeid', 'trade', 'seller', 'assethub', 'servicer', 'tape', 'address', 'defaultsortorder'}
        matches = []
        for col in cols:
            display = (col.get('displayName') or '').strip()
            internal = (col.get('name') or '').strip()
            disp_norm = display.lower().replace(' ', '')
            int_norm = internal.lower().replace(' ', '')
            if any(w in disp_norm for w in wanted) or any(w in int_norm for w in wanted):
                matches.append({'displayName': display, 'name': internal})
        if matches:
            self.stdout.write(f"  ℹ Library columns matching expected names: {matches}")
        else:
            self.stdout.write("  ⚠ No matching custom columns found in drive list/columns. Columns may not be added to this library/content type.")

    def _set_folder_description_metadata(self, client, folder_id, metadata):
        """Fallback: store metadata in folder description."""
        drive_id = client._get_drive_id()
        token = client._get_access_token()

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
        if metadata.get('seller_name'):
            desc_parts.append(f"Seller:{metadata['seller_name']}")

        description = " | ".join(desc_parts)

        update_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        payload = {'description': description}
        response = requests.patch(update_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(response.text)

    def _apply_trade_default_sort_orders(self, client, trade_base_path: str) -> None:
        """Apply DefaultSortOrder column values to trade folders for correct SharePoint UI ordering."""
        trade_level_path = f"{trade_base_path}/Trade Level"
        asset_level_path = f"{trade_base_path}/Asset Level"

        # Top-level order under Trade Folder
        for path, order in (
            (trade_level_path, 1),
            (asset_level_path, 2),
        ):
            try:
                self._set_sharepoint_fields_by_path(client, path, {'DefaultSortOrder': order})
            except Exception as e:
                self.stdout.write(
                    f"  ⚠ DefaultSortOrder (top-level '{path.split('/')[-1]}') failed: {str(e)[:80]}"
                )

        # Order inside Trade Level
        trade_level_orders = {
            'Seller Data Dump': 1,
            'Due Diligence': 2,
            'Bid': 3,
            'Award': 4,
            'Settlement': 5,
            'Entity': 6,
            'Legal': 7,
            'Servicing': 8,
            'Asset Management': 9,
        }

        for folder_name, order in trade_level_orders.items():
            folder_path = f"{trade_level_path}/{folder_name}"
            try:
                self._set_sharepoint_fields_by_path(client, folder_path, {'DefaultSortOrder': order})
            except Exception as e:
                self.stdout.write(
                    f"  ⚠ DefaultSortOrder (Trade Level '{folder_name}') failed: {str(e)[:80]}"
                )

        # Order inside Trade Level/Settlement (only remaining child: Transfer Instructions)
        settlement_children_orders = {
            'Transfer Instructions': 7,
        }

        settlement_base = f"{trade_level_path}/Settlement"
        for child_name, order in settlement_children_orders.items():
            child_path = f"{settlement_base}/{child_name}"
            try:
                self._set_sharepoint_fields_by_path(client, child_path, {'DefaultSortOrder': order})
            except Exception as e:
                self.stdout.write(
                    f"  ⚠ DefaultSortOrder (Trade Level 'Settlement/{child_name}') failed: {str(e)[:80]}"
                )

    def _apply_asset_default_sort_orders(self, client, asset_base_path: str) -> None:
        """Apply DefaultSortOrder to all Asset-level folders under a single asset base path."""
        asset_orders = {
            'Valuation': 1,
            'Loan File': 2,
            'Title': 3,
            'Legal': 4,
            'Financials': 5,
            'Tax & Insurance': 6,
            'Servicing': 7,
            'Asset Management': 8,
            'Liquidations': 9,
        }

        for folder_name, order in asset_orders.items():
            folder_path = f"{asset_base_path}/{folder_name}"
            try:
                self._set_sharepoint_fields_by_path(client, folder_path, {'DefaultSortOrder': order})
            except Exception as e:
                self.stdout.write(
                    f"      ⚠ DefaultSortOrder (Asset '{folder_name}') failed: {str(e)[:80]}"
                )

    def _set_sharepoint_fields_by_path(self, client, folder_path: str, fields: dict) -> None:
        """Set SharePoint library column fields (e.g., DefaultSortOrder) on a folder by path."""
        drive_id = client._get_drive_id()
        token = client._get_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        normalized_path = folder_path.strip('/')
        get_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{normalized_path}"

        # Eventual consistency: new folders may not be immediately readable
        response = None
        for attempt in range(5):
            response = requests.get(get_url, headers=headers)
            if response.status_code == 200:
                break
            time.sleep(0.5 + (attempt * 0.5))

        if response is None or response.status_code != 200:
            raise Exception(response.text if response is not None else 'Folder lookup failed')

        item_id = response.json().get('id')
        if not item_id:
            raise Exception('Folder item id not found')

        self._set_sharepoint_fields_by_item_id(client, item_id, fields)

    def _set_sharepoint_fields_by_item_id(self, client, item_id: str, fields: dict) -> None:
        """Set SharePoint library column fields on an item when you already know the drive item_id."""
        drive_id = client._get_drive_id()
        token = client._get_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        patch_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/listItem/fields"
        patch_response = None
        for attempt in range(6):
            patch_response = requests.patch(patch_url, headers=headers, json=fields)
            if patch_response.status_code in [200, 201]:
                return

            # Eventual consistency: listItem/fields can 404 briefly right after folder creation
            if patch_response.status_code == 404 and 'itemNotFound' in (patch_response.text or ''):
                time.sleep(0.5 + (attempt * 0.75))
                continue

            # Throttling
            if patch_response.status_code == 429:
                time.sleep(1 + attempt)
                continue

            break

        # If still failing due to itemNotFound, treat as non-fatal (will be correct on a later run)
        if patch_response is not None and patch_response.status_code == 404 and 'itemNotFound' in (patch_response.text or ''):
            return

        raise Exception(patch_response.text if patch_response is not None else 'PATCH failed')
