from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action, api_view
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from django.db.models import Q

from am_module.services.serv_am_assetInventory import build_queryset, AssetInventoryEnricher
from am_module.serializers.serial_am_assetInventory import (
    AssetInventoryRowSerializer,
    AssetInventoryColumnsSerializer,
)
from am_module.serializers.serial_am_note import AMNoteSerializer
from am_module.serializers.serial_am_servicerData import ServicerLoanDataSerializer
from am_module.models.servicers import ServicerLoanData

# Import acquisitions models to surface photos linked to SellerRawData (via sellertape_id)
from acq_module.models.model_acq_seller import SellerRawData, Trade
from core.models.attachments import Photo
from core.models import AssetIdHub, AssetDetails
from core.models.model_core_notification import Notification
from rest_framework import serializers, status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authentication import SessionAuthentication
from am_module.models.model_am_amData import (
    AMNote,
    FCTask, REOtask, DILTask, ShortSaleTask, ModificationTask, NoteSaleTask,
    PerformingTask, DelinquentTask,
)

import logging

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50  # Match frontend default page size
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
        for k in ['state', 'asset_status', 'seller_name', 'trade_name', 'trade', 'lifecycle_status', 'fund_name', 'active_tracks']:
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
        # NOTE: 'ammetrics' is a ForeignKey reverse relation (one-to-many), not usable with select_related
        # Only select_related for OneToOne and forward FK relations
        asset = get_object_or_404(
            SellerRawData.objects.select_related("asset_hub__blended_outcome_model", "seller", "trade"),
            pk=pk,
            trade__status=Trade.Status.BOARD,
        )

        # WHAT: Enrich single asset with all computed fields
        enricher = AssetInventoryEnricher()
        enriched_asset = enricher.enrich(asset)

        ser = AssetInventoryRowSerializer(enriched_asset)
        return Response(ser.data)

    def partial_update(self, request: Request, pk: int | str | None = None):
        """
        Update asset fields including asset_master_status stored on AssetDetails.

        URL: PATCH /api/am/assets/<id>/
        Body: { "asset_master_status": "ACTIVE" | "LIQUIDATED" }

        WHAT: Allow frontend grid to update the asset lifecycle status via PATCH
        WHY: Asset Master Status needs to be editable from the grid dropdown
        HOW: Fetch asset, update AssetDetails.asset_status, return enriched data

        Docs: https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
        """
        asset = get_object_or_404(
            SellerRawData.objects.select_related("asset_hub"),
            pk=pk,
            trade__status=Trade.Status.BOARD,
        )
        
        # WHAT: Extract asset_master_status from request and validate against AssetDetails.AssetStatus choices
        asset_master_status = request.data.get('asset_master_status')
        if asset_master_status is not None:
            # WHY: Validate that the provided status is one of the allowed choices
            valid_statuses = [choice[0] for choice in AssetDetails.AssetStatus.choices]
            if asset_master_status not in valid_statuses:
                return Response(
                    {"detail": f"Invalid asset_master_status. Must be one of: {', '.join(valid_statuses)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # HOW: Update the AssetDetails.asset_status field and save
            hub = asset.asset_hub
            details, _ = AssetDetails.objects.get_or_create(asset=hub)
            prev_status = details.asset_status
            details.asset_status = asset_master_status
            details.save()

            if (
                asset_master_status == AssetDetails.AssetStatus.LIQUIDATED
                and prev_status != AssetDetails.AssetStatus.LIQUIDATED
            ):
                Notification.objects.create(
                    event_type=Notification.EventType.ASSET_LIQUIDATED,
                    title="Asset Liquidated",
                    message=f"Asset hub {hub.id} marked as LIQUIDATED.",
                    asset_hub=hub,
                    created_by=getattr(request, 'user', None) if getattr(request, 'user', None) and request.user.is_authenticated else None,
                    metadata={"previous_status": prev_status, "new_status": asset_master_status},
                )
        
        # WHAT: Return enriched asset data so frontend can refresh the row
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
            trade__status=Trade.Status.BOARD,
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

    @action(detail=True, methods=['get'])
    def servicer_comments(self, request: Request, pk: int | str | None = None):
        """Return all ServicerCommentData for a boarded asset by AM asset id.

        URL: /api/am/assets/<id>/servicer_comments/
        Response: List of servicer comments ordered by comment_date DESC
        """
        asset = get_object_or_404(
            SellerRawData.objects.select_related("asset_hub"),
            pk=pk,
            trade__status=Trade.Status.BOARD,
        )
        hub = getattr(asset, 'asset_hub', None)
        if hub is None:
            return Response([], status=status.HTTP_200_OK)
        
        from am_module.models.servicers import ServicerCommentData
        
        comments = (
            ServicerCommentData.objects
            .filter(asset_hub=hub)
            .order_by('-comment_date', '-created_at')
            .values(
                'id',
                'comment_date',
                'department',
                'comment',
                'additional_notes',
                'investor_loan_number',
                'file_date',
                'created_at',
            )
        )
        return Response(list(comments), status=status.HTTP_200_OK)

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
            trade__status=Trade.Status.BOARD,
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
    def filter_options(self, request: Request):
        """Return unique filter values for dropdowns across entire dataset.
        
        URL: /api/am/assets/filter_options/
        Response: {
            "trades": ["FLC-36", "FLC-38", ...],
            "sellers": ["HUD", "ABC Bank", ...],
            "funds": ["WFL Homes, LLC", ...]
        }
        
        WHAT: Query all boarded assets to get distinct values for filter dropdowns
        WHY: Dropdowns need to show all available options, not just current page
        HOW: Use Django's distinct() on annotated fields
        """
        from core.models import FundLegalEntity
        
        # Get base queryset of all boarded assets
        qs = (
            SellerRawData.objects
            .filter(trade__status='BOARD')
            .select_related('seller', 'trade', 'asset_hub__details__fund_legal_entity__fund')
        )
        
        # Get unique trade names
        trades = list(
            qs.exclude(trade__trade_name__isnull=True)
            .exclude(trade__trade_name='')
            .values_list('trade__trade_name', flat=True)
            .distinct()
            .order_by('trade__trade_name')
        )
        
        # Get unique seller names
        sellers = list(
            qs.exclude(seller__name__isnull=True)
            .exclude(seller__name='')
            .values_list('seller__name', flat=True)
            .distinct()
            .order_by('seller__name')
        )
        
        # Get unique fund names
        funds = list(
            qs.exclude(asset_hub__details__fund_legal_entity__fund__name__isnull=True)
            .exclude(asset_hub__details__fund_legal_entity__fund__name='')
            .values_list('asset_hub__details__fund_legal_entity__fund__name', flat=True)
            .distinct()
            .order_by('asset_hub__details__fund_legal_entity__fund__name')
        )
        
        # Get unique active track types
        # WHAT: Extract all unique track types from outcome models
        # WHY: Tracks filter needs to show all available track types (DIL, Modification, REO, Short Sale, Performing, Delinquent)
        # HOW: Query outcome models directly since active_tracks is a computed field
        from am_module.models.model_am_tracksTasks import (
            DIL, Modification, ShortSale, REOData,
            PerformingTrack, DelinquentTrack
        )
        
        # Get all asset hubs that have boarded assets
        hub_ids = qs.values_list('asset_hub_id', flat=True).distinct()
        
        # Check which track types exist across all hubs
        tracks_set = set()
        if DIL.objects.filter(asset_hub_id__in=hub_ids).exists():
            tracks_set.add('DIL')
        if Modification.objects.filter(asset_hub_id__in=hub_ids).exists():
            tracks_set.add('Modification')
        if REOData.objects.filter(asset_hub_id__in=hub_ids).exists():
            tracks_set.add('REO')
        if ShortSale.objects.filter(asset_hub_id__in=hub_ids).exists():
            tracks_set.add('Short Sale')
        if PerformingTrack.objects.filter(asset_hub_id__in=hub_ids).exists():
            tracks_set.add('Performing')
        if DelinquentTrack.objects.filter(asset_hub_id__in=hub_ids).exists():
            tracks_set.add('Delinquent')
        
        tracks = sorted(list(tracks_set))
        
        return Response({
            'trades': trades,
            'sellers': sellers,
            'funds': funds,
            'tracks': tracks,
        })

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
            trade__status=Trade.Status.BOARD,
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
    """Return aggregate counts for Asset Management dashboard stats card and pie chart.
    
    WHAT: Count boarded assets by master status (Active vs Liquidated) and Asset Class
    WHY: Dashboard needs high-level metrics for portfolio overview and allocation charts
    HOW: Query SellerRawData with BOARD status, group by AssetDetails fields
    """
    from django.db.models import Count

    # 1. Overall master status counts (for top widgets)
    master_counts = (
        AssetDetails.objects
        .filter(asset__acq_raw__trade__status=Trade.Status.BOARD)
        .values('asset_status')
        .annotate(count=Count('asset_id'))
    )
    
    counts_dict = {row['asset_status']: row['count'] for row in master_counts}
    active_total = counts_dict.get(AssetDetails.AssetStatus.ACTIVE, 0)
    liquidated_total = counts_dict.get(AssetDetails.AssetStatus.LIQUIDATED, 0)

    # 2. Asset Class breakdown for ACTIVE assets (for pie chart)
    # WHAT: NPL, PERFORMING, REO
    class_counts = (
        AssetDetails.objects
        .filter(
            asset__acq_raw__trade__status=Trade.Status.BOARD,
            asset_status=AssetDetails.AssetStatus.ACTIVE
        )
        .values('asset_class')
        .annotate(count=Count('asset_id'))
    )

    allocation = {
        "NPL": 0,
        "Performing": 0,
        "REO": 0,
        "Liquidated": liquidated_total
    }

    for row in class_counts:
        cls = row['asset_class']
        cnt = row['count']
        if cls == AssetDetails.AssetClass.NPL:
            allocation["NPL"] = cnt
        elif cls == AssetDetails.AssetClass.REO:
            allocation["REO"] = cnt
        elif cls == AssetDetails.AssetClass.PERFORMING:
            allocation["Performing"] = cnt

    payload = {
        "active_assets": active_total,
        "liquidated_assets": liquidated_total,
        "allocation": allocation
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
    for key in ['state', 'seller_name', 'trade_name', 'lifecycle_status']:
        value = request.query_params.get(key)
        if value:
            filters[key] = value

    lifecycle_param = request.query_params.get('asset_status') or request.query_params.get('lifecycle_status')
    if lifecycle_param:
        filters['lifecycle_status'] = lifecycle_param
    # HOW: Build the base queryset using shared service function to ensure identical joins
    # and annotations, then apply lifecycle filtering if requested.
    qs = build_queryset(q=q, filters=filters, ordering=None)

    if lifecycle_param == AssetDetails.AssetStatus.ACTIVE:
        qs = qs.filter(
            Q(asset_hub__details__asset_status=AssetDetails.AssetStatus.ACTIVE)
            | Q(asset_hub__details__isnull=True)
        )
    elif lifecycle_param == AssetDetails.AssetStatus.LIQUIDATED:
        qs = qs.filter(asset_hub__details__asset_status=AssetDetails.AssetStatus.LIQUIDATED)
    # WHAT: Pull related enrichment + metadata up front to avoid N+1 lookups while iterating.
    qs = qs.select_related('asset_hub__enrichment', 'asset_hub__details', 'asset_hub', 'seller', 'trade')
    # WHY: Emit one marker per asset record so the frontend renders individual pins rather than clustered aggregates.
    markers = []
    for row in qs:
        hub = getattr(row, 'asset_hub', None)
        enrichment = getattr(hub, 'enrichment', None) if hub is not None else None
        details = getattr(hub, 'details', None) if hub is not None else None
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
            "city": (row.city or "").strip(),
            "street_address": (row.street_address or "").strip(),
            "lifecycle_status": getattr(details, 'asset_status', None) if details is not None else None,
        })
    payload = {
        "markers": markers,
        "count": len(markers),
    }
    return Response(payload)


@api_view(['GET'])
def am_pipeline_dashboard(request):
    """Return pipeline stage counts for Asset Manager dashboard.
    
    WHAT: Count active assets by their current stage across all outcome tracks
    WHY: AM dashboard needs to show pipeline funnel (e.g., "10 in FC Referral, 3 in REO Rehab")
    HOW: Query each task model, group by task_type, filter to ACTIVE assets only
    
    Returns:
        {
            "tracks": {
                "fc": {"nod_noi": 5, "fc_filing": 3, ...},
                "reo": {"eviction": 2, "trashout": 1, ...},
                ...
            },
            "summary": [
                {"stage": "FC: NOD/NOI", "count": 5, "track": "fc", "task_type": "nod_noi"},
                ...
            ],
            "totals": {"fc": 15, "reo": 8, ...}
        }
    """
    from django.db.models import Count

    logger = logging.getLogger(__name__)

    try:
        # WHAT: Get all active asset hub IDs (boarded + ACTIVE status)
        # WHY: Only show pipeline for assets currently being managed
        active_hub_ids = set(
            SellerRawData.objects
            .filter(
                trade__status=Trade.Status.BOARD,
                asset_hub__details__asset_status=AssetDetails.AssetStatus.ACTIVE,
            )
            .values_list('asset_hub_id', flat=True)
        )

        # WHAT: Define track configurations with display labels (excluding 'sold' - terminal state)
        # WHY: Centralize stage ordering and labels for consistent frontend display
        # NOTE: 'sold' is excluded from active pipeline - shown in "Recently Liquidated" section instead
        track_configs = {
            'fc': {
                'model': FCTask,
                'label': 'Foreclosure',
                'stages': [
                    ('nod_noi', 'NOD/NOI'),
                    ('fc_filing', 'FC Filing'),
                    ('mediation', 'Mediation'),
                    ('judgement', 'Judgement'),
                    ('redemption', 'Redemption'),
                    ('sale_scheduled', 'Sale Scheduled'),
                ],
            },
            'reo': {
                'model': REOtask,
                'label': 'REO',
                'stages': [
                    ('eviction', 'Eviction'),
                    ('trashout', 'Trashout'),
                    ('renovation', 'Renovation'),
                    ('marketing', 'Marketing'),
                    ('under_contract', 'Under Contract'),
                ],
            },
            'dil': {
                'model': DILTask,
                'label': 'DIL',
                'stages': [
                    ('pursuing_dil', 'Pursuing DIL'),
                    ('owner_contacted', 'Owner Contacted'),
                    ('dil_drafted', 'Drafted'),
                    ('dil_executed', 'Executed'),
                ],
            },
            'short_sale': {
                'model': ShortSaleTask,
                'label': 'Short Sale',
                'stages': [
                    ('list_price_accepted', 'List Price Accepted'),
                    ('listed', 'Listed'),
                    ('under_contract', 'Under Contract'),
                ],
            },
            'modification': {
                'model': ModificationTask,
                'label': 'Modification',
                'stages': [
                    ('mod_drafted', 'Drafted'),
                    ('mod_executed', 'Executed'),
                    ('mod_rpl', 'Re-Performing'),
                    ('mod_failed', 'Failed'),
                ],
            },
            'note_sale': {
                'model': NoteSaleTask,
                'label': 'Note Sale',
                'stages': [
                    ('potential_note_sale', 'Potential'),
                    ('out_to_market', 'Out to Market'),
                    ('pending_sale', 'Pending Sale'),
                ],
            },
            'performing': {
                'model': PerformingTask,
                'label': 'Performing',
                'stages': [
                    ('perf', 'Performing'),
                    ('rpl', 'Re-Performing (RPL)'),
                ],
            },
            'delinquent': {
                'model': DelinquentTask,
                'label': 'Delinquent',
                'stages': [
                    ('dq_30', '30 Days Delinquent'),
                    ('dq_60', '60 Days Delinquent'),
                    ('dq_90', '90 Days Delinquent'),
                    ('dq_120_plus', '120+ Days Delinquent'),
                ],
            },
        }

        tracks = {}
        summary = []
        totals = {}

        for track_key, config in track_configs.items():
            model = config['model']
            stage_labels = dict(config['stages'])

            # WHAT: Count tasks by task_type for active assets only
            # WHY: Get distribution of assets across pipeline stages
            counts = (
                model.objects
                .filter(asset_hub_id__in=active_hub_ids)
                .exclude(task_type__isnull=True)
                .values('task_type')
                .annotate(count=Count('id'))
            )

            track_counts = {}
            track_total = 0

            for row in counts:
                task_type = row.get('task_type')
                if not task_type:
                    continue
                task_type_s = str(task_type)
                count = int(row.get('count') or 0)
                if count <= 0:
                    continue

                track_counts[task_type_s] = count
                track_total += count

                # Add to summary list with display label
                label = stage_labels.get(task_type_s, task_type_s)
                summary.append({
                    'stage': f"{config['label']}: {label}",
                    'count': count,
                    'track': track_key,
                    'task_type': task_type_s,
                    'order': list(stage_labels.keys()).index(task_type_s) if task_type_s in stage_labels else 99,
                })

            tracks[track_key] = track_counts
            totals[track_key] = track_total

        # WHAT: Sort summary by track then stage order
        # WHY: Frontend displays stages in logical workflow order
        summary.sort(key=lambda x: (x['track'], x['order']))

        # WHAT: Get recently liquidated assets grouped by liquidation type
        # WHY: Show "Recently Liquidated" tab with breakdown by outcome track
        # HOW: Query LIQUIDATED assets and count by which track has a 'sold' task
        liquidated_hub_ids = set(
            SellerRawData.objects
            .filter(
                trade__status=Trade.Status.BOARD,
                asset_hub__details__asset_status=AssetDetails.AssetStatus.LIQUIDATED,
            )
            .values_list('asset_hub_id', flat=True)
        )

        # WHAT: Count liquidated assets by outcome type (which track has 'sold' task)
        # WHY: Show breakdown like "FC Sale: 5, REO: 3, Short Sale: 2"
        recently_liquidated = {
            'fc_sale': FCTask.objects.filter(
                asset_hub_id__in=liquidated_hub_ids,
                task_type='sold'
            ).count(),
            'reo': REOtask.objects.filter(
                asset_hub_id__in=liquidated_hub_ids,
                task_type='sold'
            ).count(),
            'short_sale': ShortSaleTask.objects.filter(
                asset_hub_id__in=liquidated_hub_ids,
                task_type='sold'
            ).count(),
            'note_sale': NoteSaleTask.objects.filter(
                asset_hub_id__in=liquidated_hub_ids,
                task_type='sold'
            ).count(),
            'dil': DILTask.objects.filter(
                asset_hub_id__in=liquidated_hub_ids,
                task_type='dil_executed'
            ).count(),
            'modification': ModificationTask.objects.filter(
                asset_hub_id__in=liquidated_hub_ids,
                task_type__in=['mod_rpl', 'note_sale']
            ).count(),
        }
        recently_liquidated['total'] = sum(int(v or 0) for v in recently_liquidated.values())

        payload = {
            'tracks': tracks,
            'summary': summary,
            'totals': totals,
            'active_asset_count': len(active_hub_ids),
            'recently_liquidated': recently_liquidated,
            'liquidated_asset_count': len(liquidated_hub_ids),
        }
        return Response(payload)
    except Exception:
        logger.exception("am_pipeline_dashboard failed")
        return Response(
            {
                'tracks': {},
                'summary': [],
                'totals': {},
                'active_asset_count': 0,
                'recently_liquidated': {
                    'fc_sale': 0,
                    'reo': 0,
                    'short_sale': 0,
                    'note_sale': 0,
                    'dil': 0,
                    'modification': 0,
                    'total': 0,
                },
                'liquidated_asset_count': 0,
            },
            status=status.HTTP_200_OK,
        )
