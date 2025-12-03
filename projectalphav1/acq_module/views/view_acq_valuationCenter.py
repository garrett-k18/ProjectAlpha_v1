"""
Views for Valuation Center.

WHAT: Dedicated API endpoints for the Valuation Center frontend page.
WHY: Clean, efficient data layer without MSA/geo annotation overhead.
HOW: GET for listing assets with valuations, PUT for updating valuations.

Endpoints:
    GET  /api/acq/valuation-center/{seller_id}/{trade_id}/  - List assets with valuations
    PUT  /api/acq/valuation-center/{asset_id}/              - Update valuation
"""

import logging
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from acq_module.models.model_acq_seller import SellerRawData
from core.models.model_co_valuations import Valuation, ValuationGradeReference
from acq_module.serializers.serial_acq_valuationCenter import (
    ValuationCenterRowSerializer,
    ValuationUpdateSerializer,
)

logger = logging.getLogger(__name__)


class ValuationCenterPagination(PageNumberPagination):
    """
    Pagination for valuation center list.
    
    WHAT: Standard DRF pagination with configurable page size
    WHY: Allow frontend to fetch all assets efficiently
    HOW: Default 500, max 5000 to handle large portfolios
    """
    page_size = 500
    page_size_query_param = 'page_size'
    max_page_size = 5000


def build_valuation_center_queryset(seller_id: int, trade_id: int):
    """
    Build optimized queryset for valuation center data.
    
    WHAT: Query SellerRawData with prefetched valuations
    WHY: Single query + prefetch avoids N+1 problem
    HOW: 
        - Filter by seller/trade
        - Exclude dropped assets
        - Prefetch valuations with grade relationship
    
    Args:
        seller_id: Seller ID for data siloing
        trade_id: Trade ID for data siloing
    
    Returns:
        QuerySet of SellerRawData with prefetched valuations
    """
    return (
        SellerRawData.objects
        .filter(seller_id=seller_id, trade_id=trade_id)
        .exclude(acq_status=SellerRawData.AcquisitionStatus.DROP)
        .select_related('asset_hub')
        .prefetch_related(
            Prefetch(
                'asset_hub__valuations',
                queryset=Valuation.objects.select_related('grade').order_by('-created_at')
            )
        )
        .order_by('pk')
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def valuation_center_list(request, seller_id: int, trade_id: int):
    """
    List all assets with valuation data for a seller/trade.
    
    URL: GET /api/acq/valuation-center/{seller_id}/{trade_id}/
    
    Query Params:
        page_size: Number of results per page (default 500, max 5000)
        page: Page number
    
    Returns:
        Paginated list of assets with valuation fields
    """
    logger.info(f"[valuation_center] GET list seller={seller_id} trade={trade_id}")
    
    # Data siloing: require both IDs
    if not seller_id or not trade_id:
        return Response({'results': [], 'count': 0})
    
    # Build optimized queryset
    qs = build_valuation_center_queryset(seller_id, trade_id)
    
    # Log count for debugging
    count = qs.count()
    logger.info(f"[valuation_center] Found {count} assets")
    
    # Paginate
    paginator = ValuationCenterPagination()
    page = paginator.paginate_queryset(qs, request)
    
    # Serialize
    serializer = ValuationCenterRowSerializer(page, many=True)
    
    logger.info(f"[valuation_center] Returning {len(serializer.data)} rows")
    return paginator.get_paginated_response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def valuation_center_update(request, asset_id: int):
    """
    Update valuation for a specific asset.
    
    URL: PUT /api/acq/valuation-center/{asset_id}/
    
    Request Body:
        source: 'internalInitialUW' or 'broker' (required)
        asis_value: As-is value (optional)
        arv_value: ARV value (optional)
        grade_code: Grade code like 'A+', 'B', etc. (optional)
        rehab_est_total: Total rehab estimate (optional)
        recommend_rehab: Boolean flag (optional)
        notes: Text notes (optional)
    
    Returns:
        Updated valuation data
    """
    logger.info(f"[valuation_center] PUT update asset={asset_id} body={request.data}")
    
    # Get the SellerRawData record
    srd = get_object_or_404(SellerRawData, pk=asset_id)
    
    if not srd.asset_hub:
        return Response(
            {'error': 'Asset has no hub record'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate input
    serializer = ValuationUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        logger.error(f"[valuation_center] Validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    source = data.pop('source')
    
    logger.info(f"[valuation_center] Updating source={source} with {data}")
    
    # Find or create valuation for this asset/source
    valuation, created = Valuation.objects.get_or_create(
        asset_hub=srd.asset_hub,
        source=source,
        defaults={}
    )
    
    if created:
        logger.info(f"[valuation_center] Created new valuation id={valuation.id}")
    else:
        logger.info(f"[valuation_center] Updating existing valuation id={valuation.id}")
    
    # Update fields that were provided
    if 'asis_value' in data:
        valuation.asis_value = data['asis_value']
    
    if 'arv_value' in data:
        valuation.arv_value = data['arv_value']
    
    if 'grade_code' in data:
        grade_code = data['grade_code']
        if grade_code:
            valuation.grade = ValuationGradeReference.objects.get(code=grade_code)
        else:
            valuation.grade = None
    
    if 'rehab_est_total' in data:
        valuation.rehab_est_total = data['rehab_est_total']
    
    if 'recommend_rehab' in data:
        valuation.recommend_rehab = data['recommend_rehab']
    
    if 'notes' in data:
        valuation.notes = data['notes']
    
    valuation.save()
    logger.info(f"[valuation_center] Saved valuation id={valuation.id}")
    
    # Return updated data
    return Response({
        'id': valuation.id,
        'asset_id': asset_id,
        'source': source,
        'asis_value': valuation.asis_value,
        'arv_value': valuation.arv_value,
        'grade_code': valuation.grade.code if valuation.grade else None,
        'rehab_est_total': valuation.rehab_est_total,
        'recommend_rehab': valuation.recommend_rehab,
        'notes': valuation.notes,
    })
