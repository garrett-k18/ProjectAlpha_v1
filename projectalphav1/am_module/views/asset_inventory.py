from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.request import Request

from am_module.services.asset_inventory import build_queryset
from am_module.serializers.asset_inventory import AssetInventoryRowSerializer, AssetInventoryColumnsSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500

class AssetInventoryViewSet(ViewSet):
    """Unified endpoint for the Asset Mgmt AG Grid."""
    pagination_class = StandardResultsSetPagination

    def list(self, request: Request):
        q = request.query_params.get('q')
        ordering = request.query_params.get('sort')
        # Collect simple filters (extend allow-list as needed)
        filters = {}
        for k in ['state', 'asset_status', 'seller_name', 'trade_name']:
            v = request.query_params.get(k)
            if v:
                filters[k] = v

        qs = build_queryset(q=q, filters=filters, ordering=ordering)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)
        ser = AssetInventoryRowSerializer(page, many=True)
        return paginator.get_paginated_response(ser.data)

    @action(detail=False, methods=['get'])
    def columns(self, request: Request):
        """Optional: column metadata for the grid UI."""
        cols = [
            {"field": "asset_id", "headerName": "Asset ID", "width": 140},
            {"field": "address", "headerName": "Address", "width": 240},
            {"field": "state", "headerName": "State", "width": 100},
            {"field": "asset_status", "headerName": "Status", "width": 140},
            {"field": "market_value", "headerName": "Market Value", "type": "currency", "width": 150},
            {"field": "hold_days", "headerName": "Hold (days)", "width": 130},
        ]
        ser = AssetInventoryColumnsSerializer(cols, many=True)
        return Response(ser.data)
