"""
SharePoint Client Service
==========================
Handles all Microsoft Graph API interactions for SharePoint.
Manages authentication, folder creation, file uploads.

File Naming Convention: serv_sp_client.py
Module: SharePoint (sp)
Purpose: Microsoft Graph API client for SharePoint operations
"""

import msal
import requests
from django.conf import settings
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SharePointClient:
    """
    Client for Microsoft Graph API SharePoint operations.
    Handles authentication and CRUD operations for folders and files.
    """
    
    def __init__(self):
        """Initialize SharePoint client with credentials from settings"""
        self.client_id = settings.SHAREPOINT_CLIENT_ID
        self.client_secret = settings.SHAREPOINT_CLIENT_SECRET
        self.tenant_id = settings.SHAREPOINT_TENANT_ID
        self.site_hostname = settings.SHAREPOINT_SITE_HOSTNAME
        self.site_path = settings.SHAREPOINT_SITE_PATH
        self._access_token = None
        self._site_id = None
        self._drive_id = None
    
    def _get_access_token(self) -> str:
        """
        Get Microsoft Graph access token using client credentials flow.
        Token is cached for reuse.
        
        Returns:
            Access token string
            
        Raises:
            Exception: If authentication fails
        """
        if self._access_token:
            return self._access_token
        
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret,
        )
        
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        
        if "access_token" not in result:
            error_msg = result.get('error_description', result.get('error', 'Unknown error'))
            logger.error(f"Failed to acquire access token: {error_msg}")
            raise Exception(f"Authentication failed: {error_msg}")
        
        self._access_token = result["access_token"]
        logger.info("Successfully acquired Microsoft Graph access token")
        return self._access_token
    
    def _get_site_id(self) -> str:
        """
        Get SharePoint site ID from Microsoft Graph.
        Site ID is cached for reuse.
        
        Returns:
            Site ID string
        """
        if self._site_id:
            return self._site_id
        
        token = self._get_access_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        site_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_hostname}:{self.site_path}"
        response = requests.get(site_url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to get site ID: {response.status_code} - {response.text}")
            raise Exception(f"Failed to get site ID: {response.text}")
        
        self._site_id = response.json()['id']
        logger.info(f"Retrieved site ID: {self._site_id}")
        return self._site_id
    
    def _get_drive_id(self) -> str:
        """
        Get default drive (Documents library) ID for the site.
        Drive ID is cached for reuse.
        
        Returns:
            Drive ID string
        """
        if self._drive_id:
            return self._drive_id
        
        site_id = self._get_site_id()
        token = self._get_access_token()
        headers = {'Authorization': f'Bearer {token}'}

        # Prefer an explicit library named "Documents" (where custom columns typically live)
        drives_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
        drives_resp = requests.get(drives_url, headers=headers)
        if drives_resp.status_code == 200:
            drives = (drives_resp.json() or {}).get('value', [])
            for d in drives:
                if (d.get('name') or '').strip().lower() == 'documents':
                    self._drive_id = d.get('id')
                    if self._drive_id:
                        logger.info(f"Retrieved drive ID (Documents): {self._drive_id}")
                        return self._drive_id

        # Fallback: Graph default drive for the site
        drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive"
        response = requests.get(drive_url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Failed to get drive ID: {response.status_code} - {response.text}")
            raise Exception(f"Failed to get drive ID: {response.text}")

        self._drive_id = response.json()['id']
        logger.info(f"Retrieved drive ID (default): {self._drive_id}")
        return self._drive_id
    
    def create_folder(self, folder_path: str, skip_parent_check: bool = False) -> Dict[str, Any]:
        """
        Create a folder in SharePoint.
        If folder exists, returns existing folder info.
        
        Args:
            folder_path: Path like "/Trades/TRD-2024-001" or "/Trades/TRD-2024-001/Legal"
            
        Returns:
            Folder metadata from Microsoft Graph
        """
        drive_id = self._get_drive_id()
        token = self._get_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Remove leading/trailing slashes
        folder_path = folder_path.strip('/')
        
        # If skip_parent_check, check if exists first, then create if needed
        if skip_parent_check:
            # Check if folder exists
            check_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{folder_path}"
            check_response = requests.get(check_url, headers=headers)
            
            if check_response.status_code == 200:
                # Folder exists - return it
                return check_response.json()
            
            # Doesn't exist - create it
            parts = folder_path.split('/')
            parent_path = '/'.join(parts[:-1]) if len(parts) > 1 else ''
            folder_name = parts[-1]
            
            if parent_path:
                create_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{parent_path}:/children"
            else:
                create_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
            
            folder_data = {
                "name": folder_name,
                "folder": {}
            }
            
            response = requests.post(create_url, headers=headers, json=folder_data)
            
            if response.status_code in [200, 201]:
                return response.json()
            
            raise Exception(f"Failed to create {folder_path}: {response.text}")
        
        # Original hierarchical creation
        parts = folder_path.split('/')
        current_path = ""
        folder_info = None
        
        for part in parts:
            current_path = f"{current_path}/{part}" if current_path else part
            
            # Try to create folder (will fail if exists, which is OK)
            # Graph API: Create folder in parent
            parent_path = '/'.join(current_path.split('/')[:-1])
            folder_name = current_path.split('/')[-1]
            
            if parent_path:
                create_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{parent_path}:/children"
            else:
                create_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
            
            folder_data = {
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "fail"
            }
            
            response = requests.post(create_url, headers=headers, json=folder_data)
            
            if response.status_code in [200, 201]:
                folder_info = response.json()
                logger.info(f"Created folder: {current_path}")
            elif response.status_code == 409:
                # Folder exists - get its info
                get_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{current_path}"
                get_response = requests.get(get_url, headers=headers)
                if get_response.status_code == 200:
                    folder_info = get_response.json()
                    logger.info(f"Folder already exists: {current_path}")
            else:
                logger.error(f"Failed to create folder {current_path}: {response.status_code} - {response.text}")
                raise Exception(f"Failed to create folder {current_path}: {response.text}")
        
        return folder_info
    
    def folder_exists(self, folder_path: str) -> bool:
        """
        Check if a folder exists in SharePoint.
        
        Args:
            folder_path: Path to check
            
        Returns:
            True if folder exists, False otherwise
        """
        try:
            drive_id = self._get_drive_id()
            token = self._get_access_token()
            headers = {'Authorization': f'Bearer {token}'}
            
            folder_path = folder_path.strip('/')
            check_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{folder_path}"
            response = requests.get(check_url, headers=headers)
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error checking folder existence: {str(e)}")
            return False
    
    def get_site_info(self) -> Dict[str, Any]:
        """
        Get SharePoint site information.
        
        Returns:
            Site metadata including URL, name, etc.
        """
        token = self._get_access_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        site_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_hostname}:{self.site_path}"
        response = requests.get(site_url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get site info: {response.text}")
        
        return response.json()

