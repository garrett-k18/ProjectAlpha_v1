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
from am_module.serializers.am_note import AMNoteSerializer
from am_module.serializers.servicer_loan_data import ServicerLoanDataSerializer
from am_module.models.servicers import ServicerLoanData

# Import acquisitions models to surface photos linked to SellerRawData (via sellertape_id)
from acq_module.models.seller import SellerRawData, Trade
from core.models.attachments import Photo
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authentication import SessionAuthentication
from am_module.models.am_data import AMNote

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

        # WHAT: Support "ALL" page size to mirror frontend view-all option (Docs: https://www.django-rest-framework.org/api-guide/pagination/)
        # WHY: Asset management grid expects a single response containing all rows when the user selects the All option.
        page_size_param = request.query_params.get('page_size')
        if isinstance(page_size_param, str) and page_size_param.strip().upper() == 'ALL':
            rows = list(qs)
            serialized = AssetInventoryRowSerializer(rows, many=True).data
            return Response({
                "count": len(serialized),
                "next": None,
                "previous": None,
                "results": serialized,
            })

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)
        ser = AssetInventoryRowSerializer(page, many=True)
        return paginator.get_paginated_response(ser.data)

    def retrieve(self, request: Request, pk: int | str | None = None):
        """Return detailed boarded asset (now backed by SellerRawData).

        URL: /api/am/assets/<id>/
        Response: AssetDetailSerializer
        """
        asset = get_object_or_404(
            SellerRawData.objects.select_related("asset_hub__am_metrics", "seller", "trade"),
            pk=pk,
            acq_status=Trade.Status.BOARD,
        )
        ser = AssetDetailSerializer(asset)
        return Response(ser.data)

    @action(detail=True, methods=['get'])
    def servicing(self, request: Request, pk: int | str | None = None):
        """Return the latest ServicerLoanData for a boarded asset by AM asset id.

        URL: /api/am/assets/<id>/servicing/
        Response: ServicerLoanDataSerializer
        """
        asset = get_object_or_404(
            SellerRawData.objects.select_related("asset_hub"),
            pk=pk,
            acq_status=Trade.Status.BOARD,
        )
        hub = getattr(asset, 'asset_hub', None)
        if hub is None:
            return Response({}, status=status.HTTP_200_OK)
        latest = (
            ServicerLoanData.objects
            .filter(asset_hub=hub)
            .order_by('-reporting_year', '-reporting_month', '-as_of_date')
            .first()
        )
        if not latest:
            return Response({}, status=status.HTTP_200_OK)
        return Response(ServicerLoanDataSerializer(latest).data)

    # DEV: Allow unauthenticated POST and avoid CSRF by not using SessionAuthentication here
    @action(detail=True, methods=['get', 'post'], permission_classes=[AllowAny], authentication_classes=[])
    def notes(self, request: Request, pk: int | str | None = None):
        """List or create AM notes for a boarded asset by AM asset id.

        GET: Return notes (most recent first) keyed by the asset's hub.
        POST: Create a new note with HTML body and optional tag.

        URL: /api/am/assets/<id>/notes/
        """
        # WHAT: Resolve boarded asset via SellerRawData rows flagged BOARD (legacy SellerBoardedData deprecated)
        asset = get_object_or_404(
            SellerRawData.objects.select_related("asset_hub"),
            pk=pk,
            acq_status=Trade.Status.BOARD,
        )
        hub = getattr(asset, 'asset_hub', None)
        if hub is None:
            return Response({"detail": "Asset has no hub assigned."}, status=status.HTTP_400_BAD_REQUEST)

        if request.method.lower() == 'get':
            # List notes for this hub (ordering handled by model Meta)
            qs = AMNote.objects.filter(asset_hub=hub)
            data = AMNoteSerializer(qs, many=True).data
            return Response(data)

        # POST create
        body = request.data.get('body')
        tag = request.data.get('tag')
        if not body or not str(body).strip():
            return Response({"detail": "'body' is required."}, status=status.HTTP_400_BAD_REQUEST)

        note = AMNote.objects.create(
            asset_hub=hub,
            body=str(body),
            tag=str(tag) if tag else None,
            created_by=getattr(request, 'user', None) if getattr(request, 'user', None) and request.user.is_authenticated else None,
            updated_by=getattr(request, 'user', None) if getattr(request, 'user', None) and request.user.is_authenticated else None,
        )
        return Response(AMNoteSerializer(note).data, status=status.HTTP_201_CREATED)

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

        asset = get_object_or_404(
            SellerRawData.objects.select_related("asset_hub"),
            pk=pk,
            acq_status=Trade.Status.BOARD,
        )
        raw = asset  # WHAT: SellerRawData already contains the acquisition row; no extra lookup needed

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
