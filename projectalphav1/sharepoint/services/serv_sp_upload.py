"""
SharePoint Upload Service
==========================
Handles file uploads to SharePoint with validation.

File Naming Convention: serv_sp_upload.py
Module: SharePoint (sp)
Purpose: Upload files to SharePoint
"""

from sharepoint.services.serv_sp_client import SharePointClient
from sharepoint.services.serv_sp_folder_structure import FolderStructure
from sharepoint.models import SharePointDocument
from django.apps import apps
import requests
import os
import logging

logger = logging.getLogger(__name__)


class SharePointUploadService:
    """Upload files to SharePoint and track in database"""
    
    def __init__(self):
        self.client = SharePointClient()
    
    def upload_file(
        self,
        file_obj,
        asset_hub_id: int,
        category: str,
        subcategory: str = None,
        tags: list = None,
        uploaded_by=None
    ) -> dict:
        """
        Upload file to SharePoint.
        
        Args:
            file_obj: Django UploadedFile object
            asset_hub_id: Asset hub ID
            category: Category folder (valuation, legal, etc.)
            subcategory: Optional subfolder (bpo, appraisal, etc.)
            uploaded_by: User who uploaded
            
        Returns:
            Dict with upload result
        """
        try:
            # Get asset
            SellerRawData = apps.get_model('acq_module', 'SellerRawData')
            asset = SellerRawData.objects.select_related(
                'asset_hub', 'trade', 'trade__seller'
            ).get(pk=asset_hub_id)
            
            # Build folder path
            trade = asset.trade
            trade_name = trade.trade_name
            seller_name = trade.seller.name if trade.seller else None
            combined_trade = f"{trade_name} - {seller_name}" if seller_name else trade_name
            trade_folder = self._sanitize(combined_trade)
            
            # Get servicer_id for folder name (or fallback to sellertape_id)
            servicer_id = asset.asset_hub.servicer_id if (asset.asset_hub and asset.asset_hub.servicer_id) else None
            sellertape_id = asset.asset_hub.sellertape_id if (asset.asset_hub and asset.asset_hub.sellertape_id) else None
            
            if servicer_id:
                asset_folder = str(servicer_id)
            elif sellertape_id:
                asset_folder = str(sellertape_id)
            else:
                asset_folder = f"UNKNOWN_{asset_hub_id}"
            
            # Build file path
            base_path = FolderStructure.get_asset_base_path(trade_folder, asset_folder)
            file_path = f"{base_path}/{category}"
            if subcategory:
                file_path = f"{file_path}/{subcategory}"
            file_path = f"{file_path}/{file_obj.name}"
            
            # Upload to SharePoint
            drive_id = self.client._get_drive_id()
            token = self.client._get_access_token()
            
            # Remove leading slash for API
            upload_path = file_path.strip('/')
            upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{upload_path}:/content"
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/octet-stream'
            }
            
            response = requests.put(upload_url, headers=headers, data=file_obj.read())
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Upload failed: {response.text}")
            
            file_data = response.json()
            
            # Set tags on file in SharePoint (as description)
            if tags:
                try:
                    tags_str = ', '.join(tags)
                    update_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_data['id']}"
                    update_response = requests.patch(
                        update_url,
                        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
                        json={'description': f"Tags: {tags_str}"}
                    )
                except Exception as e:
                    logger.warning(f"Could not set tags on file: {str(e)}")
            
            # Create database record
            SharePointDocument.objects.create(
                trade_id=str(trade.pk),
                asset_id=str(asset_hub_id),
                category=category,
                file_name=file_obj.name,
                file_type=os.path.splitext(file_obj.name)[1].lstrip('.'),
                file_size_bytes=file_obj.size,
                sharepoint_path=file_path,
                sharepoint_item_id=file_data['id'],
                sharepoint_drive_id=drive_id,
                sharepoint_web_url=file_data.get('webUrl', ''),
                uploaded_by=uploaded_by,
                tags=tags or [],
                is_validated=True,
            )
            
            logger.info(f"Uploaded {file_obj.name} to {file_path}")
            
            return {
                'success': True,
                'file_name': file_obj.name,
                'path': file_path,
                'web_url': file_data.get('webUrl')
            }
            
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_name': file_obj.name
            }
    
    def _sanitize(self, name: str) -> str:
        """Sanitize folder name"""
        for char in ['~', '#', '%', '&', '*', '{', '}', '\\', ':', '<', '>', '?', '/', '|', '"']:
            name = name.replace(char, '_')
        return name.strip(' .')[:100]

