"""
Views for AG Grid data.

WHAT: Dedicated API endpoint for acquisitions grid.
WHY: Clean, efficient data layer with proper prefetch.
HOW: Single endpoint serves all grid views (snapshot, all, valuations, drops).

Endpoints:
    GET /api/acq/grid/{seller_id}/{trade_id}/
"""

import logging
from django.db.models import Prefetch
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from acq_module.models.model_acq_seller import AcqAsset
from core.models.model_co_valuations import Valuation
from acq_module.serializers.serial_acq_grid import GridRowSerializer

logger = logging.getLogger(__name__)


class GridPagination(PageNumberPagination):
    """
    Pagination for grid data.
    
    Large page size to minimize requests for typical portfolios.
    """
    page_size = 2000
    page_size_query_param = 'page_size'
    max_page_size = 10000


def build_grid_queryset(seller_id: int, trade_id: int, view: str = 'snapshot'):
    """
    Build optimized queryset for grid data.
    
    WHAT: Query AcqAsset with efficient prefetch
    WHY: Single query + prefetch, no N+1
    HOW: 
        - Filter by seller/trade/view
        - Prefetch valuations with grade
        - Select related trade for trade_name
    
    Args:
        seller_id: Seller ID
        trade_id: Trade ID
        view: 'snapshot' (exclude drops), 'all', 'drops', 'valuations'
    
    Returns:
        QuerySet
    """
    qs = (
        AcqAsset.objects
        .filter(seller_id=seller_id, trade_id=trade_id)
        .select_related(
            'trade',
            'asset_hub',
            'asset_hub__enrichment',
            'loan',
            'property',
            'foreclosure_timeline',
        )
        .prefetch_related(
            Prefetch(
                'asset_hub__valuations',
                queryset=Valuation.objects.select_related('grade').order_by('-created_at')
            )
        )
        .order_by('pk')
    )
    
    # Apply view filter
    if view == 'snapshot':
        # Exclude dropped assets
        qs = qs.exclude(acq_status=AcqAsset.AcquisitionStatus.DROP)
    elif view == 'drops':
        # Only dropped assets
        qs = qs.filter(acq_status=AcqAsset.AcquisitionStatus.DROP)
    elif view == 'valuations':
        # Assets with any valuation (for valuation-focused views)
        qs = qs.exclude(acq_status=AcqAsset.AcquisitionStatus.DROP)
    # 'all' = no additional filter
    
    return qs


@api_view(['GET'])
@permission_classes([AllowAny])
def grid_data(request, seller_id: int, trade_id: int):
    """
    Get grid data for a seller/trade.
    
    URL: GET /api/acq/grid/{seller_id}/{trade_id}/
    
    Query Params:
        view: 'snapshot' (default), 'all', 'drops', 'valuations'
        page_size: Results per page (default 2000, max 10000)
        page: Page number
    
    Returns:
        Paginated list of grid rows
    """
    view = request.query_params.get('view', 'snapshot')
    
    logger.info(f"[grid] GET seller={seller_id} trade={trade_id} view={view}")
    
    if not seller_id or not trade_id:
        return Response({'results': [], 'count': 0})
    
    # Build queryset
    qs = build_grid_queryset(seller_id, trade_id, view)
    
    # Paginate
    paginator = GridPagination()
    page = paginator.paginate_queryset(qs, request)
    
    # Serialize
    serializer = GridRowSerializer(page, many=True)
    
    logger.info(f"[grid] Returning {len(serializer.data)} rows")
    return paginator.get_paginated_response(serializer.data)
