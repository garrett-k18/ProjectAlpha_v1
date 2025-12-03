"""
SharePoint Signals
==================
Auto-create SharePoint folders when Django entities are created.
Maintains sync between platform and SharePoint structure.

Implementation: Option 1 (Eager Creation)
- Folders created immediately when trade/asset created
- SharePoint mirrors full database structure
- Users see organized structure before uploading files
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from sharepoint.services.serv_sp_client import SharePointClient
from sharepoint.services.serv_sp_folder_structure import FolderStructure
import logging

logger = logging.getLogger(__name__)


# TODO: Uncomment and update these when you're ready to connect to your Trade/Asset models
# Example implementation:
#
# @receiver(post_save, sender='acq_module.Trade')
# def create_trade_folders(sender, instance, created, **kwargs):
#     """
#     Create SharePoint folders when a trade is created.
#     
#     Args:
#         sender: Model class
#         instance: Actual trade instance created
#         created: True if this is a new record
#         **kwargs: Additional arguments
#     """
#     if not created:
#         return  # Only create folders for new trades
#     
#     try:
#         client = SharePointClient()
#         trade_id = instance.trade_id  # Adjust to match your model field
#         
#         # Create all trade-level folders
#         folders = FolderStructure.get_trade_folders(trade_id)
#         for folder_path in folders:
#             client.create_folder(folder_path)
#         
#         # Store base path in trade model (add this field to your Trade model)
#         instance.sharepoint_folder_path = FolderStructure.get_trade_base_path(trade_id)
#         instance.save(update_fields=['sharepoint_folder_path'])
#         
#         logger.info(f"Created SharePoint folders for trade: {trade_id}")
#     
#     except Exception as e:
#         logger.error(f"Failed to create SharePoint folders for trade {instance.trade_id}: {str(e)}")
#         # Don't raise - folder creation failure shouldn't block trade creation
#
#
# @receiver(post_save, sender='acq_module.Asset')
# def create_asset_folders(sender, instance, created, **kwargs):
#     """
#     Create SharePoint folders when an asset is created.
#     
#     Args:
#         sender: Model class
#         instance: Actual asset instance created
#         created: True if this is a new record
#         **kwargs: Additional arguments
#     """
#     if not created:
#         return  # Only create folders for new assets
#     
#     try:
#         client = SharePointClient()
#         trade_id = instance.trade.trade_id  # Adjust to match your model relationships
#         asset_id = instance.asset_id  # Adjust to match your model field
#         
#         # Create all asset-level folders
#         folders = FolderStructure.get_asset_folders(trade_id, asset_id)
#         for folder_path in folders:
#             client.create_folder(folder_path)
#         
#         # Store base path in asset model (add this field to your Asset model)
#         instance.sharepoint_folder_path = FolderStructure.get_asset_base_path(trade_id, asset_id)
#         instance.save(update_fields=['sharepoint_folder_path'])
#         
#         logger.info(f"Created SharePoint folders for asset: {trade_id}/{asset_id}")
#     
#     except Exception as e:
#         logger.error(f"Failed to create SharePoint folders for asset {instance.asset_id}: {str(e)}")
#         # Don't raise - folder creation failure shouldn't block asset creation


# Placeholder - signals will be activated once you configure your models
logger.info("SharePoint signals module loaded (signals commented out until models configured)")

