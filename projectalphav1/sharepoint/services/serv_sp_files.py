"""
SharePoint Files Service
========================
Retrieve files and folders from SharePoint for specific assets.
Provides data for frontend document viewers.

File Naming Convention: serv_sp_files.py
Module: SharePoint (sp)
Purpose: Fetch files/folders for frontend display
"""

from sharepoint.services.serv_sp_client import SharePointClient
from sharepoint.services.serv_sp_folder_structure import FolderStructure
from typing import Dict, List, Any, Optional
import requests
import logging

logger = logging.getLogger(__name__)


class SharePointFilesService:
    """
    Service for retrieving SharePoint files and folder structure.
    Used by API endpoints to provide data to frontend.
    """
    
    def __init__(self):
        """Initialize service"""
        self.client = SharePointClient()
    
    def get_asset_folders(
        self,
        trade_name: str,
        seller_name: str,
        servicer_id: str,
        asset_hub_id: int
    ) -> Dict[str, Any]:
        """
        Get folder structure and files for a specific asset.
        
        Args:
            trade_name: Trade name (e.g., "FLC-27")
            seller_name: Seller name (e.g., "Archwest")
            servicer_id: Servicer ID (folder name)
            asset_hub_id: Asset hub ID
            
        Returns:
            Dict with folder structure and files
        """
        # Build paths
        combined_trade = f"{trade_name} - {seller_name}" if seller_name else trade_name
        trade_folder = self._sanitize(combined_trade)
        
        # Asset folder name (servicer_id primary, sellertape_id fallback)
        sellertape_id = None  # Will get from asset if needed
        
        if servicer_id:
            asset_folder = str(servicer_id)
        else:
            # Get sellertape_id as fallback
            SellerRawData = apps.get_model('acq_module', 'SellerRawData')
            try:
                asset = SellerRawData.objects.select_related('asset_hub').get(pk=asset_hub_id)
                sellertape_id = asset.asset_hub.sellertape_id if (asset.asset_hub and asset.asset_hub.sellertape_id) else None
                asset_folder = str(sellertape_id) if sellertape_id else f"UNKNOWN_{asset_hub_id}"
            except:
                asset_folder = f"UNKNOWN_{asset_hub_id}"
        
        base_path = FolderStructure.get_asset_base_path(trade_folder, asset_folder)
        
        # Return static folder structure (no API call - instant!)
        folders = []
        base_url = f"https://firstliencapitaldom.sharepoint.com/sites/ProjectAlpha/Shared%20Documents"
        
        # Build folder structure from FolderStructure definition
        for folder_name in FolderStructure.ASSET_FOLDERS:
            folder_path = f"{base_path}/{folder_name}"
            folder_info = {
                'name': folder_name,
                'path': folder_path,
                'web_url': f"{base_url}/{folder_path.replace('/', '%20')}",
                'files': [],
                'subfolders': []
            }
            
            # Add predefined subfolders if any
            if folder_name in FolderStructure.ASSET_SUBFOLDERS:
                for subfolder_name in FolderStructure.ASSET_SUBFOLDERS[folder_name]:
                    folder_info['subfolders'].append({
                        'name': subfolder_name,
                        'path': f"{folder_path}/{subfolder_name}",
                        'web_url': f"{base_url}/{folder_path.replace('/', '%20')}%20{subfolder_name.replace(' ', '%20')}",
                        'file_count': 0
                    })
            
            folders.append(folder_info)
        
        return {
            'success': True,
            'asset_hub_id': asset_hub_id,
            'servicer_id': servicer_id,
            'base_path': base_path,
            'folders': folders,
            'files': []
        }
    
    def _get_folder_contents(self, folder_path: str, recursive: bool = False) -> Dict[str, List]:
        """
        Get contents of a folder (subfolders and files).
        
        Args:
            folder_path: SharePoint folder path
            recursive: If True, fetch all subfolder contents (slow). If False, just list folders (fast).
            
        Returns:
            Dict with 'folders' and 'files' lists
        """
        drive_id = self.client._get_drive_id()
        token = self.client._get_access_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get folder contents
        folder_path = folder_path.strip('/')
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{folder_path}:/children"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get folder contents: {response.text}")
        
        items = response.json().get('value', [])
        
        # Separate folders and files
        folders = []
        files = []
        
        for item in items:
            if 'folder' in item:
                # It's a folder
                folder_name = item['name']
                folder_info = {
                    'name': folder_name,
                    'path': f"{folder_path}/{folder_name}",
                    'web_url': item.get('webUrl'),
                    'file_count': item.get('folder', {}).get('childCount', 0),
                }
                
                # Always fetch immediate children (one level), but don't recurse deeper
                try:
                    # Get immediate children of this folder
                    subfolder_path = f"{folder_path}/{folder_name}"
                    subfolder_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{subfolder_path}:/children"
                    subfolder_response = requests.get(subfolder_url, headers=headers)
                    
                    if subfolder_response.status_code == 200:
                        sub_items = subfolder_response.json().get('value', [])
                        folder_info['subfolders'] = [
                            {
                                'name': sub['name'],
                                'path': f"{subfolder_path}/{sub['name']}",
                                'web_url': sub.get('webUrl'),
                                'file_count': sub.get('folder', {}).get('childCount', 0)
                            }
                            for sub in sub_items if 'folder' in sub
                        ]
                        folder_info['files'] = [
                            {
                                'name': sub['name'],
                                'size': sub.get('size', 0),
                                'web_url': sub.get('webUrl'),
                                'download_url': sub.get('@microsoft.graph.downloadUrl'),
                                'modified': sub.get('lastModifiedDateTime'),
                            }
                            for sub in sub_items if 'file' in sub
                        ]
                    else:
                        folder_info['subfolders'] = []
                        folder_info['files'] = []
                except Exception as e:
                    logger.warning(f"Could not get contents of {folder_name}: {str(e)}")
                    folder_info['subfolders'] = []
                    folder_info['files'] = []
                
                folders.append(folder_info)
            
            elif 'file' in item:
                # It's a file
                files.append({
                    'name': item['name'],
                    'size': item.get('size', 0),
                    'web_url': item.get('webUrl'),
                    'download_url': item.get('@microsoft.graph.downloadUrl'),
                    'modified': item.get('lastModifiedDateTime'),
                    'modified_by': item.get('lastModifiedBy', {}).get('user', {}).get('displayName')
                })
        
        return {
            'folders': folders,
            'files': files
        }
    
    def _sanitize(self, name: str) -> str:
        """Sanitize folder name"""
        for char in ['~', '#', '%', '&', '*', '{', '}', '\\', ':', '<', '>', '?', '/', '|', '"']:
            name = name.replace(char, '_')
        return name.strip(' .')[:100]

