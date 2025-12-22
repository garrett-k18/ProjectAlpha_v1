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
        asset_hub_id: int,
        servicer_id: Optional[str] = None,
        sellertape_id: Optional[str] = None,
        full_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get folder structure and files for a specific asset.
        
        Args:
            trade_name: Trade name (e.g., "FLC-27")
            seller_name: Seller name (e.g., "Archwest")
            asset_hub_id: Asset hub ID (used as folder name and metadata identifier)
            
        Returns:
            Dict with folder structure and files
        """
        # Build paths
        combined_trade = f"{trade_name} - {seller_name}" if seller_name else trade_name
        trade_folder = self._sanitize(combined_trade)
        
        # Asset folder naming convention: "{primary_id} - {address}" (sanitized)
        # primary_id: servicer_id -> sellertape_id -> asset_hub_id
        primary_id = servicer_id or sellertape_id or asset_hub_id
        asset_folder_raw = f"{primary_id} - {full_address}" if full_address else str(primary_id)
        asset_folder = self._sanitize(asset_folder_raw)
        
        base_path = FolderStructure.get_asset_base_path(trade_folder, asset_folder)

        # Return static folder structure from FolderStructure definition (no Graph calls)
        folders = []
        base_url = "https://firstliencapitaldom.sharepoint.com/sites/ProjectAlpha/Shared%20Documents"

        for folder_name in FolderStructure.ASSET_FOLDERS:
            folder_path = f"{base_path}/{folder_name}"
            folder_info: Dict[str, Any] = {
                'name': folder_name,
                'path': folder_path,
                'web_url': f"{base_url}/{folder_path.replace('/', '%20')}",
                'files': [],
                'subfolders': [],
            }

            # Add predefined subfolders if any
            if folder_name in FolderStructure.ASSET_SUBFOLDERS:
                for subfolder_name in FolderStructure.ASSET_SUBFOLDERS[folder_name]:
                    folder_info['subfolders'].append({
                        'name': subfolder_name,
                        'path': f"{folder_path}/{subfolder_name}",
                        'web_url': f"{base_url}/{folder_path.replace('/', '%20')}%20{subfolder_name.replace(' ', '%20')}",
                        'file_count': 0,
                    })

            folders.append(folder_info)

        return {
            'success': True,
            'asset_hub_id': asset_hub_id,
            'base_path': base_path,
            'folders': folders,
            'files': [],
        }
    
    def get_trade_folders(
        self,
        trade_name: str,
        seller_name: str,
        trade_id: int
    ) -> Dict[str, Any]:
        """
        Get folder structure for trade-level documents.
        
        Args:
            trade_name: Trade name (e.g., "FLC-27")
            seller_name: Seller name (e.g., "Archwest")
            trade_id: Trade database ID
            
        Returns:
            Dict with trade-level folder structure (Bid, Legal, Post Close - excludes Asset Level)
        """
        # Build paths
        combined_trade = f"{trade_name} - {seller_name}" if seller_name else trade_name
        trade_folder = self._sanitize(combined_trade)
        
        # Get trade base path and Trade Level base path
        base_path = FolderStructure.get_trade_base_path(trade_folder)
        trade_level_base = f"{base_path}/Trade Level"

        # Return static Trade Level folder structure (no Graph calls)
        folders = []
        base_url = "https://firstliencapitaldom.sharepoint.com/sites/ProjectAlpha/Shared%20Documents"

        for folder_name in FolderStructure.TRADE_LEVEL_FOLDERS:
            folder_path = f"{trade_level_base}/{folder_name}"
            folder_info: Dict[str, Any] = {
                'name': folder_name,
                'path': folder_path,
                'web_url': f"{base_url}/{folder_path.replace('/', '%20')}",
                'files': [],
                'subfolders': [],
            }

            # Add nested Trade Level subfolders if defined (e.g., Settlement children)
            if folder_name in FolderStructure.TRADE_LEVEL_SUBFOLDERS:
                for subfolder_name in FolderStructure.TRADE_LEVEL_SUBFOLDERS[folder_name]:
                    folder_info['subfolders'].append({
                        'name': subfolder_name,
                        'path': f"{folder_path}/{subfolder_name}",
                        'web_url': f"{base_url}/{folder_path.replace('/', '%20')}%20{subfolder_name.replace(' ', '%20')}",
                        'file_count': 0,
                    })

            folders.append(folder_info)

        return {
            'success': True,
            'trade_id': trade_id,
            'trade_name': combined_trade,
            'base_path': base_path,
            'folders': folders,
            'files': [],
        }

    def get_folder_contents_by_path(self, folder_path: str) -> Dict[str, Any]:
        """Get folders and files for a specific SharePoint folder path."""
        try:
            contents = self._get_folder_contents(folder_path)
            return {
                'success': True,
                'path': folder_path,
                'folders': contents.get('folders', []),
                'files': contents.get('files', []),
            }
        except Exception as e:
            logger.error(f"Error getting folder contents for {folder_path}: {str(e)}")
            return {
                'success': False,
                'path': folder_path,
                'error': str(e),
                'folders': [],
                'files': [],
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

                # Only fetch each child folder's children when explicitly requested.
                # Default (recursive=False) keeps this to a single Graph call per folder
                # to improve performance when browsing.
                if recursive:
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

