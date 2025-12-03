"""
SharePoint Batch Operations Service
====================================
High-performance batch operations for creating folders.
Uses Microsoft Graph batch API and caching for 10-20x speedup.

File Naming Convention: serv_sp_batch.py
Module: SharePoint (sp)
Purpose: Batch folder creation for performance
"""

import requests
from typing import List, Dict, Any
from django.conf import settings
from sharepoint.services.serv_sp_client import SharePointClient
import logging

logger = logging.getLogger(__name__)


class SharePointBatchService(SharePointClient):
    """
    Optimized SharePoint operations using batching and caching.
    Much faster than creating folders one-by-one.
    """
    
    def __init__(self):
        """Initialize batch service with folder cache"""
        super().__init__()
        self._folder_cache = set()  # Track created folders to skip redundant checks
    
    def create_folders_batch(self, folder_paths: List[str]) -> Dict[str, Any]:
        """
        Create multiple folders in batch with optimization.
        
        Args:
            folder_paths: List of folder paths to create
            
        Returns:
            Dict with success/failure counts
        """
        drive_id = self._get_drive_id()
        token = self._get_access_token()
        
        results = {
            'created': 0,
            'existed': 0,
            'failed': 0,
            'errors': []
        }
        
        # Process in chunks to avoid overwhelming API
        chunk_size = 20  # Graph API batch limit
        
        for i in range(0, len(folder_paths), chunk_size):
            chunk = folder_paths[i:i + chunk_size]
            
            # Build batch requests
            batch_requests = []
            for idx, folder_path in enumerate(chunk):
                # Skip if already in cache
                if folder_path in self._folder_cache:
                    results['existed'] += 1
                    continue
                
                # Split path into parts
                folder_path = folder_path.strip('/')
                parts = folder_path.split('/')
                
                # Only create leaf folder (parents should exist or be cached)
                parent_path = '/'.join(parts[:-1]) if len(parts) > 1 else ''
                folder_name = parts[-1]
                
                # Build request
                if parent_path:
                    url = f"/drives/{drive_id}/root:/{parent_path}:/children"
                else:
                    url = f"/drives/{drive_id}/root/children"
                
                batch_requests.append({
                    "id": str(idx),
                    "method": "POST",
                    "url": url,
                    "body": {
                        "name": folder_name,
                        "folder": {},
                        "@microsoft.graph.conflictBehavior": "rename"  # Auto-rename if exists
                    },
                    "headers": {"Content-Type": "application/json"}
                })
            
            # Execute batch if we have requests
            if batch_requests:
                batch_result = self._execute_batch(batch_requests, token)
                
                # Process results
                for response in batch_result.get('responses', []):
                    status = response.get('status')
                    if status in [200, 201]:
                        results['created'] += 1
                        # Add to cache
                        req_idx = int(response['id'])
                        if req_idx < len(chunk):
                            self._folder_cache.add(chunk[req_idx])
                    elif status == 409:  # Conflict - already exists
                        results['existed'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(response.get('body', {}))
        
        return results
    
    def _execute_batch(self, requests_list: List[Dict], token: str) -> Dict:
        """
        Execute batch request to Microsoft Graph.
        
        Args:
            requests_list: List of batch request objects
            token: Access token
            
        Returns:
            Batch response
        """
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        batch_data = {"requests": requests_list}
        batch_url = "https://graph.microsoft.com/v1.0/$batch"
        
        response = requests.post(batch_url, headers=headers, json=batch_data)
        
        if response.status_code != 200:
            logger.error(f"Batch request failed: {response.status_code} - {response.text}")
            raise Exception(f"Batch request failed: {response.text}")
        
        return response.json()
    
    def create_asset_folders_optimized(self, trade_name: str, asset_folders: List[tuple]) -> Dict[str, Any]:
        """
        Optimized creation of all folders for assets in a trade.
        
        Args:
            trade_name: Sanitized trade folder name
            asset_folders: List of (asset_id, servicer_id) tuples
            
        Returns:
            Results dict
        """
        from sharepoint.services.serv_sp_folder_structure import FolderStructure
        
        all_paths = []
        
        # Add trade path to cache (we know it exists)
        trade_path = FolderStructure.get_trade_base_path(trade_name)
        self._folder_cache.add(f"{trade_path}/Asset Level")
        
        # Generate all folder paths
        for asset_id, servicer_id in asset_folders:
            # Build asset folder name
            if servicer_id:
                asset_name = f"{asset_id} - {servicer_id}"
            else:
                asset_name = str(asset_id)
            
            # Get all folders for this asset
            folders = FolderStructure.get_asset_folders(trade_name, asset_name)
            all_paths.extend(folders)
        
        # Create in batch
        return self.create_folders_batch(all_paths)

