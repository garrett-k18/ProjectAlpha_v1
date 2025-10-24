from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action, api_view
from rest_framework.request import Request
from django.shortcuts import get_object_or_404

from am_module.services.serv_am_assetInventory import build_queryset, AssetInventoryEnricher
from am_module.serializers.serial_am_assetInventory import (
    AssetInventoryRowSerializer,
    AssetInventoryColumnsSerializer,
)
from am_module.serializers.serial_am_note import AMNoteSerializer
from am_module.serializers.serial_am_servicerData import ServicerLoanDataSerializer
from am_module.models.servicers import ServicerLoanData

# Import acquisitions models to surface photos linked to SellerRawData (via sellertape_id)
from acq_module.models.seller import SellerRawData, Trade
from core.models.attachments import Photo
from core.models import AssetIdHub
from rest_framework import serializers, status
from django.db.models import Q
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
        """
        Return paginated list of boarded assets for AG Grid.

        URL: /api/am/assets/
        Response: Paginated AssetInventoryRowSerializer

        WHAT: Build optimized queryset, enrich with computed fields, serialize for grid
        WHY: Separate concerns - query building, business logic, and serialization
        HOW: Use service layer for enrichment, serializer for JSON transformation
        """
        q = request.query_params.get('q')
        ordering = request.query_params.get('sort')
        # Collect simple filters (extend allow-list as needed)
        filters = {}
        for k in ['state', 'asset_status', 'seller_name', 'trade_name', 'lifecycle_status']:
            v = request.query_params.get(k)
            if v:
                filters[k] = v

        qs = build_queryset(q=q, filters=filters, ordering=ordering)

        # WHAT: Support "ALL" page size to mirror frontend view-all option (Docs: https://www.django-rest-framework.org/api-guide/pagination/)
        # WHY: Asset management grid expects a single response containing all rows when the user selects the All option.
        page_size_param = request.query_params.get('page_size')
        if isinstance(page_size_param, str) and page_size_param.strip().upper() == 'ALL':
            # WHAT: Enrich all rows with computed fields before serialization
            enricher = AssetInventoryEnricher()
            enriched_rows = list(enricher.enrich_queryset(qs))
            serialized = AssetInventoryRowSerializer(enriched_rows, many=True).data
            return Response({
                "count": len(serialized),
                "next": None,
                "previous": None,
                "results": serialized,
            })

        # WHAT: Paginate first, then enrich only the current page for efficiency
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)

        # WHAT: Enrich paginated results with computed fields
        # WHY: Avoid enriching entire queryset when only showing one page
        enricher = AssetInventoryEnricher()
        enriched_page = [enricher.enrich(asset) for asset in page]

        ser = AssetInventoryRowSerializer(enriched_page, many=True)
        return paginator.get_paginated_response(ser.data)

    def retrieve(self, request: Request, pk: int | str | None = None):
        """Return detailed boarded asset (now backed by SellerRawData).

        URL: /api/am/assets/<id>/
        Response: AssetInventoryRowSerializer

        WHAT: Use the same serializer as the grid to ensure consistent field availability
        WHY: Loan-level views expect computed fields (purchase_cost, latest_uw_value, servicer_loan_data)
        whether navigating from grid or accessing detail view directly
        HOW: Fetch asset, enrich with computed fields, serialize
        """
        asset = get_object_or_404(
            SellerRawData.objects.select_related("asset_hub__ammetrics", "asset_hub__blended_outcome_model", "seller", "trade"),
            pk=pk,
            acq_status=Trade.Status.BOARD,
        )

        # WHAT: Enrich single asset with all computed fields
        enricher = AssetInventoryEnricher()
        enriched_asset = enricher.enrich(asset)

        ser = AssetInventoryRowSerializer(enriched_asset)
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


@api_view(['GET'])
def asset_dashboard_stats(request):
    active_assets_count = (
        SellerRawData.objects
        .filter(
            acq_status=SellerRawData.AcquisitionStatus.BOARD,
            asset_hub__asset_status=AssetIdHub.AssetStatus.ACTIVE,
        )
        .count()
    )
    liquidated_assets_count = (
        SellerRawData.objects
        .filter(
            acq_status=SellerRawData.AcquisitionStatus.BOARD,
            asset_hub__asset_status=AssetIdHub.AssetStatus.LIQUIDATED,
        )
        .count()
    )
    payload = {
        "active_assets": active_assets_count,
        "liquidated_assets": liquidated_assets_count,
    }
    return Response(payload)


@api_view(['GET'])
def asset_geo_markers(request: Request):
    """Return clustered geocode markers for active Asset Management inventory.

    WHAT: Builds a list of map markers representing active boarded assets.
    WHY: The Asset Dispersion card needs to plot one marker per unique lat/lng,
    bundling multiple assets at identical coordinates so marker size can scale
    with density.
    HOW: Reuse the existing `build_queryset()` helper so filter semantics remain
    identical to the AG Grid, then aggregate over persisted geocode data stored
    on `LlDataEnrichment`.
    Docs reviewed: https://docs.djangoproject.com/en/stable/topics/db/queries/
    """
    # WHAT: Accept optional quick filter search via `q` parameter so the map can mirror
    # the AG Grid quick search results when the user types into the dashboard filter.
    q = request.query_params.get('q')
    # WHY: Mirror AG Grid column filters (state, lifecycle status, etc.) so markers remain
    # perfectly in sync with the grid selection; initialize a typed dict to accumulate them.
    filters: dict[str, str] = {}
    for key in ['state', 'asset_status', 'seller_name', 'trade_name', 'lifecycle_status']:
        value = request.query_params.get(key)
        if value:
            filters[key] = value
    # HOW: Build the base queryset using shared service function to ensure identical joins
    # and annotations, then constrain to assets flagged ACTIVE in the hub lifecycle enum.
    qs = build_queryset(q=q, filters=filters, ordering=None)
    qs = qs.filter(asset_hub__asset_status=AssetIdHub.AssetStatus.ACTIVE)
    # WHAT: Pull related enrichment + metadata up front to avoid N+1 lookups while iterating.
    qs = qs.select_related('enrichment', 'asset_hub', 'seller', 'trade')
    # WHY: Emit one marker per asset record so the frontend renders individual pins rather than clustered aggregates.
    markers = []
    for row in qs:
        enrichment = getattr(row, 'enrichment', None)
        lat = getattr(enrichment, 'geocode_lat', None)
        lng = getattr(enrichment, 'geocode_lng', None)
        if lat is None or lng is None:
            continue  # WHAT: Skip assets without geocode coordinates to avoid invalid map points.
        lat_f = float(lat)
        lng_f = float(lng)
        label = getattr(enrichment, 'geocode_display_address', '') or \
            ", ".join(filter(None, [str(row.city or '').strip(), str(row.state or '').strip()]))
        markers.append({
            "lat": round(lat_f, 6),  # WHAT: Round latitude for consistency while preserving precision.
            "lng": round(lng_f, 6),  # WHAT: Round longitude to align with latitude precision.
            "asset_hub_id": row.pk,  # WHAT: Use row.pk since SellerRawData uses asset_hub as primary key (no .asset_hub_id attribute)
            "label": label,  # WHAT: Provide human-readable location text when available.
            "count": 1,  # WHAT: Maintain count attribute for backwards compatibility with existing UI expectations.
            "state": (row.state or "").strip(),  # WHAT: Include state abbreviation for frontend aggregation (docs reviewed: https://docs.djangoproject.com/en/5.0/ref/models/instances/#field-access for safe field access).
        })
    payload = {
        "markers": markers,
        "count": len(markers),
    }
    return Response(payload)
