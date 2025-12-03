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


@receiver(post_save, sender='acq_module.Trade')
def create_trade_folders(sender, instance, created, **kwargs):
    """
    Create SharePoint folders when a trade is created.
    Creates trade-level folders (Bid, Legal, Post Close, Asset Level).
    """
    if not created:
        return  # Only for new trades
    
    try:
        # Build folder name from trade_name and seller
        trade_name = instance.trade_name
        seller_name = instance.seller.name if instance.seller else None
        
        if not trade_name:
            logger.warning(f"Trade {instance.pk} has no trade_name - skipping folder creation")
            return
        
        # Sanitize folder name
        if seller_name:
            combined_name = f"{trade_name} - {seller_name}"
        else:
            combined_name = trade_name
        
        # Simple sanitization
        folder_name = combined_name
        for char in ['~', '#', '%', '&', '*', '{', '}', '\\', ':', '<', '>', '?', '/', '|', '"']:
            folder_name = folder_name.replace(char, '_')
        folder_name = folder_name.strip(' .')[:100]
        
        # Create folders
        client = SharePointClient()
        folders = FolderStructure.get_trade_folders(folder_name)
        for folder_path in folders:
            client.create_folder(folder_path)
        
        logger.info(f"Created SharePoint folders for trade: {combined_name}")
    
    except Exception as e:
        logger.error(f"Failed to create SharePoint folders for trade {instance.pk}: {str(e)}")
        # Don't raise - folder creation failure shouldn't block trade creation


@receiver(post_save, sender='acq_module.SellerRawData')
def create_asset_folders(sender, instance, created, **kwargs):
    """
    Create SharePoint folders when an asset is created.
    Creates all asset-level category folders with subfolders.
    """
    if not created:
        return  # Only for new assets
    
    try:
        # Get trade info
        if not instance.trade or not instance.trade.trade_name:
            logger.warning(f"Asset {instance.pk} has no trade - skipping folder creation")
            return
        
        trade = instance.trade
        trade_name = trade.trade_name
        seller_name = trade.seller.name if trade.seller else None
        
        # Build trade folder name
        if seller_name:
            combined_trade_name = f"{trade_name} - {seller_name}"
        else:
            combined_trade_name = trade_name
        
        # Sanitize
        trade_folder = combined_trade_name
        for char in ['~', '#', '%', '&', '*', '{', '}', '\\', ':', '<', '>', '?', '/', '|', '"']:
            trade_folder = trade_folder.replace(char, '_')
        trade_folder = trade_folder.strip(' .')[:100]
        
        # Get asset info
        asset_hub_id = instance.asset_hub.id if instance.asset_hub else instance.pk
        servicer_id = instance.asset_hub.servicer_id if (instance.asset_hub and instance.asset_hub.servicer_id) else None
        
        # Build asset folder name
        if servicer_id:
            asset_folder = f"{asset_hub_id} - {servicer_id}"
        else:
            asset_folder = str(asset_hub_id)
        
        # Create folders
        client = SharePointClient()
        folders = FolderStructure.get_asset_folders(trade_folder, asset_folder)
        for folder_path in folders:
            client.create_folder(folder_path)
        
        logger.info(f"Created SharePoint folders for asset: {trade_name}/{asset_hub_id}")
    
    except Exception as e:
        logger.error(f"Failed to create SharePoint folders for asset {instance.pk}: {str(e)}")
        # Don't raise - folder creation failure shouldn't block asset creation


logger.info("SharePoint signals active - auto-creating folders for new trades/assets")

