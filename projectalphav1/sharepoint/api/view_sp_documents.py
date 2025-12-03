"""
SharePoint Documents API
========================
API endpoints for fetching SharePoint folders and files.
Links backend assets to SharePoint structure.

File Naming Convention: view_sp_documents.py
Module: SharePoint
Purpose: API for frontend to access SharePoint documents
"""

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.apps import apps
from sharepoint.services.serv_sp_files import SharePointFilesService
from sharepoint.services.serv_sp_upload import SharePointUploadService
from sharepoint.services.serv_sp_folder_structure import FolderStructure
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def get_asset_documents(request, asset_hub_id):
    """
    Get SharePoint folders and files for a specific asset.
    
    Args:
        asset_hub_id: Asset hub ID
        
    Returns:
        JSON with folder structure and files
        
    Example:
        GET /api/sharepoint/assets/1068/documents/
        
        Response:
        {
            "success": true,
            "asset_hub_id": 1068,
            "servicer_id": "880507",
            "trade_name": "FLC-27 - Archwest",
            "folders": [
                {
                    "name": "Valuation",
                    "subfolders": ["BPO", "Appraisal", "Property Inspection"],
                    "files": [...]
                },
                ...
            ]
        }
    """
    try:
        # Get asset from database
        SellerRawData = apps.get_model('acq_module', 'SellerRawData')
        
        try:
            # SellerRawData PK = asset_hub, so query by pk
            asset = SellerRawData.objects.select_related(
                'asset_hub', 'trade', 'trade__seller'
            ).get(pk=asset_hub_id)
        except SellerRawData.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Asset {asset_hub_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get trade info
        if not asset.trade:
            return Response({
                'success': False,
                'error': 'Asset has no associated trade'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        trade = asset.trade
        trade_name = trade.trade_name
        seller_name = trade.seller.name if trade.seller else None
        
        # Get asset info
        servicer_id = asset.asset_hub.servicer_id if (asset.asset_hub and asset.asset_hub.servicer_id) else None
        
        if not servicer_id:
            return Response({
                'success': False,
                'error': 'Asset has no servicer ID - folder not created',
                'note': f'Using fallback: NO_SERVICER_{asset_hub_id}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Fetch SharePoint data
        service = SharePointFilesService()
        result = service.get_asset_folders(
            trade_name=trade_name,
            seller_name=seller_name,
            servicer_id=servicer_id,
            asset_hub_id=asset_hub_id
        )
        
        # Add trade context to response
        if result['success']:
            result['trade_name'] = f"{trade_name} - {seller_name}" if seller_name else trade_name
            result['trade_id'] = trade.pk
        
        return Response(result)
    
    except Exception as e:
        logger.error(f"Error fetching documents for asset {asset_hub_id}: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_trade_documents(request, trade_id):
    """
    Get SharePoint folders for trade-level documents.
    
    Args:
        trade_id: Trade database ID
        
    Returns:
        JSON with trade-level folder structure
    """
    try:
        Trade = apps.get_model('acq_module', 'Trade')
        
        try:
            trade = Trade.objects.select_related('seller').get(pk=trade_id)
        except Trade.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Trade {trade_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Build folder path
        trade_name = trade.trade_name
        seller_name = trade.seller.name if trade.seller else None
        combined = f"{trade_name} - {seller_name}" if seller_name else trade_name
        
        # Return folder URLs
        base_url = f"https://firstliencapitaldom.sharepoint.com/sites/ProjectAlpha/Shared%20Documents/Trades/{combined}"
        
        return Response({
            'success': True,
            'trade_id': trade_id,
            'trade_name': combined,
            'folders': {
                'bid': f"{base_url}/Bid",
                'legal': f"{base_url}/Legal",
                'post_close': f"{base_url}/Post%20Close",
                'asset_level': f"{base_url}/Asset%20Level"
            }
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    """
    Upload file to SharePoint.
    
    POST /api/sharepoint/upload/
    Form data:
        - file: File object
        - asset_hub_id: Asset ID
        - category: Category folder name
        - subcategory: Optional subfolder
        
    Returns:
        Upload result with SharePoint URL
    """
    try:
        file_obj = request.FILES.get('file')
        asset_hub_id = request.data.get('asset_hub_id')
        category = request.data.get('category')
        subcategory = request.data.get('subcategory')
        
        if not file_obj:
            return Response({
                'success': False,
                'error': 'No file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not asset_hub_id or not category:
            return Response({
                'success': False,
                'error': 'asset_hub_id and category required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Upload to SharePoint
        service = SharePointUploadService()
        result = service.upload_file(
            file_obj=file_obj,
            asset_hub_id=int(asset_hub_id),
            category=category,
            subcategory=subcategory,
            uploaded_by=request.user if request.user.is_authenticated else None
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_available_tags(request):
    """
    Get available tags for categorizing files.
    
    GET /api/sharepoint/tags/
    
    Returns:
        Dict of category -> available tags
    """
    return Response({
        'valuation': FolderStructure.VALUATION_TAGS,
    })
