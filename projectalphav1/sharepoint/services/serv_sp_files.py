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
        
        # Asset folder name is servicer_id
        asset_folder = servicer_id if servicer_id else f"NO_SERVICER_{asset_hub_id}"
        
        base_path = FolderStructure.get_asset_base_path(trade_folder, asset_folder)
        
        # Get folder contents (non-recursive for speed - lazy load subfolders)
        try:
            folder_data = self._get_folder_contents(base_path, recursive=False)
            return {
                'success': True,
                'asset_hub_id': asset_hub_id,
                'servicer_id': servicer_id,
                'base_path': base_path,
                'folders': folder_data['folders'],
                'files': folder_data['files']
            }
        except Exception as e:
            logger.error(f"Failed to get folders for asset {asset_hub_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'asset_hub_id': asset_hub_id
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
                
                # Only recurse if requested (for lazy loading)
                if recursive:
                    try:
                        subfolder_contents = self._get_folder_contents(f"{folder_path}/{folder_name}", recursive=True)
                        folder_info['files'] = subfolder_contents['files']
                        folder_info['subfolders'] = subfolder_contents['folders']
                    except Exception as e:
                        logger.warning(f"Could not get contents of {folder_name}: {str(e)}")
                        folder_info['files'] = []
                        folder_info['subfolders'] = []
                else:
                    # Just indicate there might be subfolders
                    folder_info['files'] = []
                    folder_info['subfolders'] = []
                
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

