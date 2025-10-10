"""
Asset Actions API
Handles drop/restore actions for assets in the acquisitions module.

Endpoints:
- POST /api/acq/assets/<asset_id>/drop/ - Mark asset as dropped
- POST /api/acq/assets/<asset_id>/restore/ - Restore dropped asset

Docs reviewed:
- Django REST Framework APIView: https://www.django-rest-framework.org/api-guide/views/
- Django timezone: https://docs.djangoproject.com/en/stable/topics/i18n/timezones/
"""

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status

from acq_module.models.seller import SellerRawData


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([TokenAuthentication])  # Use only token auth, no session auth = no CSRF
def drop_asset(request, asset_id):
    """
    Mark an asset as dropped from active bidding.
    
    POST /api/acq/assets/<asset_id>/drop/
    
    Request body:
        {
            "reason": "Optional reason for dropping" 
        }
    
    Response:
        {
            "status": "dropped",
            "asset_id": 123,
            "drop_date": "2025-10-10T10:42:00Z"
        }
    """
    try:
        # Find asset by asset_hub primary key
        asset = SellerRawData.objects.get(asset_hub_id=asset_id)
        
        # Mark as dropped with metadata
        asset.is_dropped = True
        asset.drop_reason = request.data.get('reason', 'Dropped from grid')
        asset.drop_date = timezone.now()
        asset.dropped_by = request.user if request.user.is_authenticated else None
        asset.save()
        
        return Response({
            'status': 'dropped',
            'asset_id': asset_id,
            'drop_date': asset.drop_date.isoformat(),
            'reason': asset.drop_reason
        }, status=status.HTTP_200_OK)
        
    except SellerRawData.DoesNotExist:
        return Response({
            'error': 'Asset not found',
            'asset_id': asset_id
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([TokenAuthentication])  # Use only token auth, no session auth = no CSRF
def restore_asset(request, asset_id):
    """
    Restore a dropped asset back to active bidding.
    
    POST /api/acq/assets/<asset_id>/restore/
    
    Response:
        {
            "status": "restored",
            "asset_id": 123
        }
    """
    try:
        # Find asset by asset_hub primary key
        asset = SellerRawData.objects.get(asset_hub_id=asset_id)
        
        # Clear drop metadata
        asset.is_dropped = False
        asset.drop_reason = None
        asset.drop_date = None
        asset.dropped_by = None
        asset.save()
        
        return Response({
            'status': 'restored',
            'asset_id': asset_id
        }, status=status.HTTP_200_OK)
        
    except SellerRawData.DoesNotExist:
        return Response({
            'error': 'Asset not found',
            'asset_id': asset_id
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
