from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.request import Request
from django.shortcuts import get_object_or_404

from am_module.services.asset_inventory import build_queryset
from am_module.serializers.asset_inventory import (
    AssetInventoryRowSerializer,
    AssetInventoryColumnsSerializer,
    AssetDetailSerializer,
)
from am_module.models.boarded_data import SellerBoardedData

# Import acquisitions models to surface photos linked to SellerRawData (via sellertape_id)
from acq_module.models.seller import SellerRawData
from core.models.valuations import Photo
from rest_framework import serializers, status

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

    def retrieve(self, request: Request, pk: int | str | None = None):
        """Return detailed SellerBoardedData by AM asset id.

        URL: /api/am/assets/<id>/
        Response: AssetDetailSerializer
        """
        asset = get_object_or_404(SellerBoardedData.objects.select_related("metrics"), pk=pk)
        ser = AssetDetailSerializer(asset)
        return Response(ser.data)

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

    @action(detail=True, methods=['get'])
    def photos(self, request: Request, pk: int | str | None = None):
        """Return normalized photo items for a boarded asset.

        We link SellerBoardedData -> SellerRawData via `sellertape_id` and reuse
        acquisitions Photo store. Output matches the acquisitions photos API.

        URL: /api/am/assets/<id>/photos/
        Response: [ { src, alt, thumb, type } ]

        Docs reviewed:
        - DRF ViewSet actions: https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
        - DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
        - Django File storage: https://docs.djangoproject.com/en/stable/topics/files/
        """

        class OutputPhotoSerializer(serializers.Serializer):
            src = serializers.CharField()
            alt = serializers.CharField(required=False, allow_blank=True)
            thumb = serializers.CharField(required=False, allow_blank=True)
            type = serializers.CharField(required=False, allow_blank=True)

        asset = get_object_or_404(SellerBoardedData, pk=pk)
        raw_id = getattr(asset, 'sellertape_id', None)
        if raw_id is None:
            return Response([], status=status.HTTP_200_OK)

        # 404 if raw row missing to signal potential data integrity issue
        raw = get_object_or_404(SellerRawData, pk=raw_id)

        def abs_url(rel_url: str) -> str:
            return request.build_absolute_uri(rel_url)

        items: list[dict] = []
        for p in Photo.objects.filter(seller_raw_data=raw).iterator():
            try:
                src = abs_url(p.image.url)
            except Exception:
                continue

            if p.source_tag == 'public':
                alt = p.caption or "Public photo"
            elif p.source_tag == 'document':
                page = f" p{p.page_number}" if p.page_number is not None else ""
                alt = p.caption or f"Document photo{page}"
            elif p.source_tag == 'broker':
                alt = p.caption or "Broker photo"
            else:
                alt = p.caption or "Photo"

            items.append({
                "src": src,
                "alt": alt,
                "thumb": src,
                "type": p.source_tag,
            })

        data = OutputPhotoSerializer(items, many=True).data
        return Response(data)
