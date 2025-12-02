"""
Acquisition Status Management API
Unified module for managing status at both trade and asset levels.

WHAT: Centralized status management for acquisitions module
WHY: Trade-level and asset-level status serve different purposes but are related
HOW: 
  - Trade status (PASS, INDICATIVE, DD, AWARDED, BOARD) controls lifecycle
  - Asset status (KEEP, DROP) controls individual asset inclusion in active pool

Architecture:
  - Trade-level: Overall deal lifecycle tracking (Trade.status)
  - Asset-level: Individual asset filtering (SellerRawData.acq_status)
  - These are INDEPENDENT but related (trade can have mix of KEEP/DROP assets)

Endpoints:
  Trade-level:
    - GET  /api/acq/trades/<trade_id>/status/ - Get trade status + options
    - POST /api/acq/trades/<trade_id>/status/ - Update trade status
  
  Asset-level:
    - POST /api/acq/assets/<asset_id>/drop/ - Mark asset as dropped (KEEP→DROP)
    - POST /api/acq/assets/<asset_id>/restore/ - Restore asset (DROP→KEEP)

Docs reviewed:
- Django REST Framework views: https://www.django-rest-framework.org/api-guide/views/
- Django transactions: https://docs.djangoproject.com/en/stable/topics/db/transactions/
- Django CSRF: https://docs.djangoproject.com/en/5.1/ref/csrf/
"""

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status

from acq_module.models.model_acq_seller import Trade, SellerRawData


# ============================================================================
# TRADE-LEVEL STATUS MANAGEMENT
# ============================================================================

def _serialize_trade_status_choices():
    """Return Trade.Status choices as value/label dictionaries for UI dropdowns.
    
    WHAT: Convert Django TextChoices to JSON-safe format
    WHY: Frontend needs both value (for storage) and label (for display)
    HOW: Iterate Trade.Status.choices and build dict list
    """
    return [{"value": value, "label": label} for value, label in Trade.Status.choices]


@api_view(["GET"])
@ensure_csrf_cookie  # WHAT: Force CSRF cookie issuance for subsequent POSTs from SPA
def get_trade_status(request, trade_id: int):
    """Fetch the current trade status plus available status options.
    
    WHAT: GET endpoint returning trade's current lifecycle status
    WHY: UI needs both current status and dropdown options for status selector
    HOW: Load trade by PK, return status + choices
    
    Response:
        {
            "trade_id": 123,
            "status": "DD",
            "options": [
                {"value": "PASS", "label": "Pass"},
                {"value": "INDICATIVE", "label": "Indicative"},
                {"value": "DD", "label": "Due Diligence"},
                {"value": "AWARDED", "label": "Awarded"},
                {"value": "BOARD", "label": "Boarded"}
            ]
        }
    """
    try:
        trade = Trade.objects.get(pk=trade_id)
    except Trade.DoesNotExist:
        return JsonResponse(
            {"detail": "Trade not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    return JsonResponse({
        "trade_id": trade.id,
        "status": trade.status,
        "options": _serialize_trade_status_choices(),
    })


@api_view(["POST", "PUT"])
def update_trade_status(request, trade_id: int):
    """Update a trade's lifecycle status.
    
    WHAT: POST/PUT endpoint to change trade status
    WHY: Users need to move trades through lifecycle (INDICATIVE→DD→AWARDED→BOARD)
    HOW: Validate status against choices, update trade in atomic transaction
    
    Request body:
        {
            "status": "AWARDED"
        }
    
    Response:
        {
            "trade_id": 123,
            "status": "AWARDED",
            "options": [...]
        }
    """
    try:
        trade = Trade.objects.get(pk=trade_id)
    except Trade.DoesNotExist:
        return JsonResponse(
            {"detail": "Trade not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # WHAT: Extract status from request body
    # WHY: DRF Request.data handles JSON parsing
    new_status = request.data.get("status") if isinstance(request.data, dict) else None
    
    if not new_status:
        return JsonResponse(
            {"detail": "Status is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # WHAT: Validate status is a valid choice
    # WHY: Prevent corrupting status field with invalid values
    valid_values = {value for value, _ in Trade.Status.choices}
    if new_status not in valid_values:
        return JsonResponse(
            {"detail": f"Invalid status. Must be one of: {', '.join(valid_values)}"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # WHAT: Update trade status if changed
    # WHY: Only persist if status actually changed for efficiency
    # HOW: Atomic transaction ensures consistency
    if trade.status != new_status:
        with transaction.atomic():
            trade.status = new_status
            trade.save(update_fields=["status", "updated_at"])
    
    return JsonResponse({
        "trade_id": trade.id,
        "status": trade.status,
        "options": _serialize_trade_status_choices(),
    })


# ============================================================================
# ASSET-LEVEL STATUS MANAGEMENT
# ============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([TokenAuthentication])  # Token auth only, no session = no CSRF
def drop_asset(request, asset_id):
    """Mark an asset as dropped from active bidding pool.
    
    WHAT: Sets asset acq_status to DROP
    WHY: Exclude specific assets from active pool without deleting them
    HOW: Simple status flag toggle (KEEP→DROP)
    
    Note: Drop metadata (reason, user, date) tracked separately via tags system
    
    POST /api/acq/assets/<asset_id>/drop/
    
    Response:
        {
            "status": "dropped",
            "asset_id": 123
        }
    """
    try:
        # WHAT: Find asset by asset_hub primary key
        # WHY: SellerRawData uses asset_hub as primary key (OneToOne with AssetIdHub)
        asset = SellerRawData.objects.get(asset_hub_id=asset_id)
        
        # WHAT: Mark as dropped
        # WHY: Exclude from active bidding pool
        # HOW: Set acq_status to DROP (binary flag)
        asset.acq_status = SellerRawData.AcquisitionStatus.DROP
        asset.save()
        
        return Response({
            'status': 'dropped',
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


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([TokenAuthentication])  # Token auth only, no session = no CSRF
def bulk_drop_assets(request):
    """Bulk drop many assets in a single transaction.

    Request JSON:
        { "asset_ids": [123, 456, ...] }
    """
    asset_ids = request.data.get("asset_ids") if isinstance(request.data, dict) else None
    if not isinstance(asset_ids, list) or not asset_ids:
        return Response({
            "error": "asset_ids list is required",
        }, status=status.HTTP_400_BAD_REQUEST)

    # Normalize to integers and drop invalid values quietly
    normalized_ids = []
    for raw_id in asset_ids:
        try:
            normalized_ids.append(int(raw_id))
        except (TypeError, ValueError):
            continue

    if not normalized_ids:
        return Response({
            "error": "No valid asset IDs provided",
        }, status=status.HTTP_400_BAD_REQUEST)

    qs = SellerRawData.objects.filter(asset_hub_id__in=normalized_ids)
    trade_ids = list(qs.values_list("trade_id", flat=True).distinct())

    with transaction.atomic():
        updated_count = qs.update(acq_status=SellerRawData.AcquisitionStatus.DROP)

        # Refresh trade-level status for affected trades
        for trade_id in trade_ids:
            if not trade_id:
                continue
            try:
                trade = Trade.objects.get(pk=trade_id)
                trade.refresh_status_from_assets()
            except Trade.DoesNotExist:
                continue

    return Response({
        "status": "dropped",
        "updated_count": updated_count,
        "asset_ids": normalized_ids,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([TokenAuthentication])  # Token auth only, no session = no CSRF
def bulk_restore_assets(request):
    """Bulk restore many assets in a single transaction.

    Request JSON:
        { "asset_ids": [123, 456, ...] }
    """
    asset_ids = request.data.get("asset_ids") if isinstance(request.data, dict) else None
    if not isinstance(asset_ids, list) or not asset_ids:
        return Response({
            "error": "asset_ids list is required",
        }, status=status.HTTP_400_BAD_REQUEST)

    normalized_ids = []
    for raw_id in asset_ids:
        try:
            normalized_ids.append(int(raw_id))
        except (TypeError, ValueError):
            continue

    if not normalized_ids:
        return Response({
            "error": "No valid asset IDs provided",
        }, status=status.HTTP_400_BAD_REQUEST)

    qs = SellerRawData.objects.filter(asset_hub_id__in=normalized_ids)
    trade_ids = list(qs.values_list("trade_id", flat=True).distinct())

    with transaction.atomic():
        updated_count = qs.update(acq_status=SellerRawData.AcquisitionStatus.KEEP)

        for trade_id in trade_ids:
            if not trade_id:
                continue
            try:
                trade = Trade.objects.get(pk=trade_id)
                trade.refresh_status_from_assets()
            except Trade.DoesNotExist:
                continue

    return Response({
        "status": "restored",
        "updated_count": updated_count,
        "asset_ids": normalized_ids,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([TokenAuthentication])  # Token auth only, no session = no CSRF
def restore_asset(request, asset_id):
    """Restore a dropped asset back to active bidding pool.
    
    WHAT: Sets asset acq_status to KEEP
    WHY: Return previously dropped assets to active pool
    HOW: Simple status flag toggle (DROP→KEEP)
    
    POST /api/acq/assets/<asset_id>/restore/
    
    Response:
        {
            "status": "restored",
            "asset_id": 123
        }
    """
    try:
        # WHAT: Find asset by asset_hub primary key
        # WHY: SellerRawData uses asset_hub as primary key (OneToOne with AssetIdHub)
        asset = SellerRawData.objects.get(asset_hub_id=asset_id)
        
        # WHAT: Restore to active pool
        # WHY: Return asset to default KEEP status
        # HOW: Set acq_status to KEEP (default active status)
        asset.acq_status = SellerRawData.AcquisitionStatus.KEEP
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

