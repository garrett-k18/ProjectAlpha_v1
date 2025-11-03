"""
Egnyte Integration Service
This service handles all interactions with Egnyte REST API for document management.
"""

import requests
from django.conf import settings
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class EgnyteService:
    """
    Service class for interacting with Egnyte Public API.
    
    Documentation: https://developers.egnyte.com/docs
    """
    
    def __init__(self):
        """
        Initialize Egnyte service with credentials from Django settings.
        
        Add these to your settings.py:
        EGNYTE_DOMAIN = 'your-domain.egnyte.com'
        EGNYTE_API_TOKEN = 'your-api-token'
        """
        self.domain = getattr(settings, 'EGNYTE_DOMAIN', None)
        self.api_token = getattr(settings, 'EGNYTE_API_TOKEN', None)
        self.base_url = f"https://{self.domain}"
        
        if not self.domain or not self.api_token:
            logger.warning("Egnyte credentials not configured in settings")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def upload_file(self, file_path: str, file_content: bytes, folder_path: str = '/Shared/Documents') -> Dict[str, Any]:
        """
        Upload a file to Egnyte.
        
        Args:
            file_path: Name of the file (e.g., 'document.pdf')
            file_content: Binary content of the file
            folder_path: Destination folder in Egnyte (default: /Shared/Documents)
        
        Returns:
            dict: Response from Egnyte API containing file metadata
            
        REST API Endpoint: POST /pubapi/v1/fs-content/{path}
        """
        try:
            full_path = f"{folder_path}/{file_path}".replace('//', '/')
            url = f"{self.base_url}/pubapi/v1/fs-content{full_path}"
            
            headers = {
                'Authorization': f'Bearer {self.api_token}',
            }
            
            response = requests.post(url, data=file_content, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Successfully uploaded file: {file_path}")
            return {
                'success': True,
                'path': full_path,
                'message': 'File uploaded successfully'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error uploading file to Egnyte: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """
        Download a file from Egnyte.
        
        Args:
            file_path: Path to the file in Egnyte (e.g., '/Shared/Documents/file.pdf')
        
        Returns:
            bytes: File content if successful, None otherwise
            
        REST API Endpoint: GET /pubapi/v1/fs-content/{path}
        """
        try:
            url = f"{self.base_url}/pubapi/v1/fs-content{file_path}"
            headers = self._get_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Successfully downloaded file: {file_path}")
            return response.content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading file from Egnyte: {str(e)}")
            return None
    
    def list_folder(self, folder_path: str = '/Shared') -> Dict[str, Any]:
        """
        List contents of a folder in Egnyte.
        
        Args:
            folder_path: Path to the folder (default: /Shared)
        
        Returns:
            dict: Folder contents including files and subfolders
            
        REST API Endpoint: GET /pubapi/v1/fs/{path}
        """
        try:
            url = f"{self.base_url}/pubapi/v1/fs{folder_path}"
            headers = self._get_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully listed folder: {folder_path}")
            return {
                'success': True,
                'data': data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error listing folder in Egnyte: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_folder(self, folder_path: str) -> Dict[str, Any]:
        """
        Create a new folder in Egnyte.
        
        Args:
            folder_path: Path for the new folder (e.g., '/Shared/NewFolder')
        
        Returns:
            dict: Response indicating success or failure
            
        REST API Endpoint: POST /pubapi/v1/fs/{path}
        """
        try:
            url = f"{self.base_url}/pubapi/v1/fs{folder_path}"
            headers = self._get_headers()
            
            payload = {
                'action': 'add_folder'
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Successfully created folder: {folder_path}")
            return {
                'success': True,
                'path': folder_path,
                'message': 'Folder created successfully'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating folder in Egnyte: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Delete a file from Egnyte.
        
        Args:
            file_path: Path to the file to delete
        
        Returns:
            dict: Response indicating success or failure
            
        REST API Endpoint: DELETE /pubapi/v1/fs/{path}
        """
        try:
            url = f"{self.base_url}/pubapi/v1/fs{file_path}"
            headers = self._get_headers()
            
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Successfully deleted file: {file_path}")
            return {
                'success': True,
                'message': 'File deleted successfully'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting file from Egnyte: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_files(self, query: str, folder_path: str = '/Shared') -> Dict[str, Any]:
        """
        Search for files in Egnyte.
        
        Args:
            query: Search query string
            folder_path: Folder to search in (default: /Shared)
        
        Returns:
            dict: Search results
            
        REST API Endpoint: GET /pubapi/v1/search
        """
        try:
            url = f"{self.base_url}/pubapi/v1/search"
            headers = self._get_headers()
            
            params = {
                'query': query,
                'folder': folder_path
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Search completed for query: {query}")
            return {
                'success': True,
                'results': data.get('results', [])
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching files in Egnyte: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get metadata for a specific file.
        
        Args:
            file_path: Path to the file
        
        Returns:
            dict: File metadata including size, modified date, etc.
            
        REST API Endpoint: GET /pubapi/v1/fs/{path}
        """
        try:
            url = f"{self.base_url}/pubapi/v1/fs{file_path}"
            headers = self._get_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved file info for: {file_path}")
            return {
                'success': True,
                'data': data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting file info from Egnyte: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_link(self, file_path: str, link_type: str = 'file', 
                   expiry_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a shareable link for a file or folder.
        
        Args:
            file_path: Path to the file/folder
            link_type: 'file' or 'folder'
            expiry_date: Optional expiry date (format: 'YYYY-MM-DD')
        
        Returns:
            dict: Link information including URL
            
        REST API Endpoint: POST /pubapi/v1/links
        """
        try:
            url = f"{self.base_url}/pubapi/v1/links"
            headers = self._get_headers()
            
            payload = {
                'path': file_path,
                'type': link_type,
                'accessibility': 'anyone'
            }
            
            if expiry_date:
                payload['expiry_date'] = expiry_date
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Created link for: {file_path}")
            return {
                'success': True,
                'link': data.get('links', [{}])[0].get('url'),
                'data': data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating link in Egnyte: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
egnyte_service = EgnyteService()

