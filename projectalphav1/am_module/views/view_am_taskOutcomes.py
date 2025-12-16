from __future__ import annotations

# DRF docs reviewed:
# - ViewSets & Routers: https://www.django-rest-framework.org/api-guide/viewsets/
# - Mixins: https://www.django-rest-framework.org/api-guide/generic-views/#mixins
# - Filtering via query params: https://www.django-rest-framework.org/api-guide/filtering/

from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import status, mixins, viewsets
from django.db import transaction
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from am_module.models.model_am_amData import (
    REOData, REOtask,
    FCSale, FCTask,
    DIL, DILTask,
    ShortSale, ShortSaleTask,
    Modification, ModificationTask,
    NoteSale, NoteSaleTask,
    REOScope,
    Offers,
)
from core.models.model_core_notification import Notification
from am_module.serializers.serial_am_outcomes import (
    REODataSerializer, REOTaskSerializer,
    FCSaleSerializer, FCTaskSerializer,
    DILSerializer, DILTaskSerializer,
    ShortSaleSerializer, ShortSaleTaskSerializer,
    ModificationSerializer, ModificationTaskSerializer,
    NoteSaleSerializer, NoteSaleTaskSerializer,
    REOScopeSerializer,
    OffersSerializer,
)


class _OutcomeBaseViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          GenericViewSet):
    """Base for 1:1 hub-keyed outcome viewsets with idempotent create.

    Behavior:
    - GET /?asset_hub_id=123 returns the outcome if present, else empty list []
    - POST {asset_hub_id} performs idempotent ensure-create via serializer.create()
{{ ... }}
    - PUT/PATCH allowed for field updates (audit handled by model save)
    """

    permission_classes = [AllowAny]
    authentication_classes: list[type[SessionAuthentication]] = []

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        asset_hub_id = request.query_params.get('asset_hub_id')
        if not asset_hub_id:
            # For safety, require explicit filter to avoid accidental full-table fetch
            return Response([], status=status.HTTP_200_OK)
        try:
            asset_hub_id = int(asset_hub_id)
        except Exception:
            return Response({"detail": "asset_hub_id must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        qs = self.get_queryset().filter(asset_hub_id=asset_hub_id)
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Delete an outcome and its child tasks in a single transaction.

        All outcome models in this module expose their child tasks via the
        `related_name='tasks'` reverse relation. Since the FK from task->outcome
        uses PROTECT, we must delete children first to allow outcome deletion.
        """
        instance = self.get_object()
        with transaction.atomic():
            # Delete child tasks if present; ignore when relation is missing
            tasks_rel = getattr(instance, 'tasks', None)
            if tasks_rel is not None:
                tasks_rel.all().delete()
            self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class REODataViewSet(_OutcomeBaseViewSet):
    queryset = REOData.objects.all().select_related('asset_hub')
    serializer_class = REODataSerializer


class FCSaleViewSet(_OutcomeBaseViewSet):
    queryset = FCSale.objects.all().select_related('asset_hub')
    serializer_class = FCSaleSerializer


class DILViewSet(_OutcomeBaseViewSet):
    queryset = DIL.objects.all().select_related('asset_hub')
    serializer_class = DILSerializer


class ShortSaleViewSet(_OutcomeBaseViewSet):
    queryset = ShortSale.objects.all().select_related('asset_hub')
    serializer_class = ShortSaleSerializer


class ModificationViewSet(_OutcomeBaseViewSet):
    queryset = Modification.objects.all().select_related('asset_hub')
    serializer_class = ModificationSerializer


class _TaskBaseViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       GenericViewSet):
    """Base for task viewsets. List supports filtering by asset_hub_id and parent id. Supports DELETE."""

    permission_classes = [AllowAny]
    authentication_classes: list[type[SessionAuthentication]] = []
    pagination_class = None

    parent_field_name: str = ''  # e.g., 'dil', 'fc_sale', etc.

    def perform_create(self, serializer):
        actor = getattr(self.request, 'user', None) if getattr(self.request, 'user', None) and self.request.user.is_authenticated else None
        obj = serializer.save()
        if actor is not None and hasattr(obj, 'set_actor'):
            try:
                obj.set_actor(actor)
            except Exception:
                pass

        try:
            Notification.objects.create(
                event_type=Notification.EventType.TASK_CHANGED,
                title="AM task created",
                message=f"Task {getattr(obj, 'task_type', '')} created for asset hub {getattr(obj, 'asset_hub_id', None)}.",
                asset_hub=getattr(obj, 'asset_hub', None),
                created_by=actor,
                metadata={
                    "model": obj.__class__.__name__,
                    "task_id": getattr(obj, 'id', None),
                    "task_type": getattr(obj, 'task_type', None),
                },
            )
        except Exception:
            pass

    def perform_update(self, serializer):
        instance = self.get_object()
        prev_task_type = getattr(instance, 'task_type', None)

        actor = getattr(self.request, 'user', None) if getattr(self.request, 'user', None) and self.request.user.is_authenticated else None

        if actor is not None and hasattr(instance, 'set_actor'):
            try:
                instance.set_actor(actor)
            except Exception:
                pass

        obj = serializer.save()

        new_task_type = getattr(obj, 'task_type', None)
        if prev_task_type != new_task_type:
            try:
                Notification.objects.create(
                    event_type=Notification.EventType.TASK_CHANGED,
                    title="AM task changed",
                    message=f"Task changed from {prev_task_type} to {new_task_type} for asset hub {getattr(obj, 'asset_hub_id', None)}.",
                    asset_hub=getattr(obj, 'asset_hub', None),
                    created_by=actor,
                    metadata={
                        "model": obj.__class__.__name__,
                        "task_id": getattr(obj, 'id', None),
                        "previous_task_type": prev_task_type,
                        "new_task_type": new_task_type,
                    },
                )
            except Exception:
                pass

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        qs = self.get_queryset()

        asset_hub_id = request.query_params.get('asset_hub_id')
        if asset_hub_id:
            try:
                qs = qs.filter(asset_hub_id=int(asset_hub_id))
            except Exception:
                return Response({"detail": "asset_hub_id must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        parent_id = request.query_params.get(self.parent_field_name)
        if parent_id:
            try:
                filter_kwargs = {f"{self.parent_field_name}_id": int(parent_id)}
            except Exception:
                return Response({"detail": f"{self.parent_field_name} must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
            qs = qs.filter(**filter_kwargs)

        qs = qs.order_by('-created_at', '-id')
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)


class REOTaskViewSet(_TaskBaseViewSet):
    queryset = REOtask.objects.all().select_related('asset_hub', 'reo_outcome')
    serializer_class = REOTaskSerializer
    parent_field_name = 'reo_outcome'


class FCTaskViewSet(_TaskBaseViewSet):
    queryset = FCTask.objects.all().select_related('asset_hub', 'fc_sale')
    serializer_class = FCTaskSerializer
    parent_field_name = 'fc_sale'


class DILTaskViewSet(_TaskBaseViewSet):
    queryset = DILTask.objects.all().select_related('asset_hub', 'dil')
    serializer_class = DILTaskSerializer
    parent_field_name = 'dil'


class ShortSaleTaskViewSet(_TaskBaseViewSet):
    queryset = ShortSaleTask.objects.all().select_related('asset_hub', 'short_sale')
    serializer_class = ShortSaleTaskSerializer
    parent_field_name = 'short_sale'


class ModificationTaskViewSet(_TaskBaseViewSet):
    queryset = ModificationTask.objects.all().select_related('asset_hub', 'modification')
    serializer_class = ModificationTaskSerializer
    parent_field_name = 'modification'


class NoteSaleViewSet(_OutcomeBaseViewSet):
    """
    WHAT: ViewSet for NoteSale outcome (1:1 with AssetIdHub)
    WHY: Provide API endpoints for managing note sale outcomes
    WHERE: Used by Note Sale outcome cards in asset management
    HOW: Extends _OutcomeBaseViewSet with standard CRUD operations
    """
    queryset = NoteSale.objects.all().select_related('asset_hub', 'trading_partner')
    serializer_class = NoteSaleSerializer


class NoteSaleTaskViewSet(_TaskBaseViewSet):
    """
    WHAT: ViewSet for NoteSaleTask workflow tasks (many-to-one with NoteSale)
    WHY: Provide API endpoints for managing note sale workflow tasks
    WHERE: Used by Note Sale task management in asset management
    HOW: Extends _TaskBaseViewSet with filtering and CRUD operations
    """
    queryset = NoteSaleTask.objects.all().select_related('asset_hub', 'note_sale')
    serializer_class = NoteSaleTaskSerializer
    parent_field_name = 'note_sale'


class OffersViewSet(viewsets.ModelViewSet):
    """
    WHAT: ViewSet for managing offers from various sources
    WHY: Handle offers from agent portal, asset manager, manual entry, and AI crawling
    WHERE: Used in Short Sale and REO workflows
    HOW: Standard CRUD operations with asset_hub filtering
    """

    permission_classes = [AllowAny]
    authentication_classes: list[type[SessionAuthentication]] = []
    serializer_class = OffersSerializer
    queryset = Offers.objects.all().select_related('asset_hub')

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        asset_hub_id = request.query_params.get('asset_hub_id')
        offer_source = request.query_params.get('offer_source')
        
        if not asset_hub_id:
            return Response([], status=status.HTTP_200_OK)
        
        try:
            asset_hub_id = int(asset_hub_id)
        except Exception:
            return Response({"detail": "asset_hub_id must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        qs = self.get_queryset().filter(asset_hub_id=asset_hub_id)
        
        # Filter by offer source if specified
        if offer_source in ('short_sale', 'reo'):
            qs = qs.filter(offer_source=offer_source)
            
        qs = qs.order_by('-offer_date', '-created_at')
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)


class REOScopeViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      GenericViewSet):
    """CRUD for REO scopes/bids with query param filters.

    Supported filters via query params:
    - asset_hub_id: required to list; prevents full-table listings by default
    - scope_kind: optional ('trashout' | 'renovation')
    - reo_task: optional (task id)
    """

    permission_classes = [AllowAny]
    authentication_classes: list[type[SessionAuthentication]] = []
    serializer_class = REOScopeSerializer
    queryset = REOScope.objects.all().select_related('asset_hub', 'reo_task')

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        asset_hub_id = request.query_params.get('asset_hub_id')
        if not asset_hub_id:
            return Response([], status=status.HTTP_200_OK)
        try:
            asset_hub_id = int(asset_hub_id)
        except Exception:
            return Response({"detail": "asset_hub_id must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        qs = self.get_queryset().filter(asset_hub_id=asset_hub_id)

        scope_kind = request.query_params.get('scope_kind')
        if scope_kind in ('trashout', 'renovation'):
            qs = qs.filter(scope_kind=scope_kind)

        reo_task = request.query_params.get('reo_task')
        if reo_task:
            try:
                qs = qs.filter(reo_task_id=int(reo_task))
            except Exception:
                return Response({"detail": "reo_task must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        qs = qs.order_by('-created_at', '-id')
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)


# ============================================================
# Task Metrics Endpoint
# ============================================================

from rest_framework.views import APIView
from am_module.services.serv_am_tasking import get_task_metrics, get_active_outcome_tracks, get_track_milestones


class TaskMetricsView(APIView):
    """
    WHAT: Endpoint for task completion metrics by asset hub
    WHY: Provide active vs completed task counts for the tasking dashboard UI
    WHERE: Called by frontend am_ll_tasking.vue to populate KPI cards
    HOW: Delegate to service layer (serv_am_tasking.py) for business logic
    
    URL: GET /api/am/outcomes/task-metrics/?asset_hub_id=<id>
    
    Response:
        {
            'active_count': int,
            'completed_count': int,
            'active_items': [{'key': str, 'label': str, 'tone': str}, ...],
            'completed_items': [{'key': str, 'label': str, 'tone': str}, ...]
        }
    """
    
    permission_classes = [AllowAny]
    authentication_classes: list[type[SessionAuthentication]] = []
    
    def get(self, request: Request) -> Response:
        """
        WHAT: Get task metrics for a specific asset hub
        WHY: Dashboard needs counts and badge data for active/completed tasks
        HOW: Extract hub_id from query params, call service, return metrics
        """
        asset_hub_id = request.query_params.get('asset_hub_id')
        
        if not asset_hub_id:
            return Response(
                {"detail": "asset_hub_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            asset_hub_id = int(asset_hub_id)
        except (ValueError, TypeError):
            return Response(
                {"detail": "asset_hub_id must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # WHAT: Call service layer to compute metrics
        # WHY: Keep business logic in services, not views
        # WHERE: serv_am_tasking.py
        task_metrics = get_task_metrics(asset_hub_id)
        track_metrics = get_active_outcome_tracks(asset_hub_id)
        
        # WHAT: Combine task and track metrics into single response
        # WHY: Frontend needs both task completion and track completion data
        # HOW: Merge dictionaries
        response_data = {
            **task_metrics,
            **track_metrics,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class TrackMilestonesView(APIView):
    """
    WHAT: Endpoint for track milestones (current and upcoming tasks)
    WHY: Provide milestone progression view for tasking dashboard
    WHERE: Called by frontend milestonesCard.vue to populate milestone data
    HOW: Delegate to service layer (serv_am_tasking.py) for business logic
    
    URL: GET /api/am/outcomes/track-milestones/?asset_hub_id=<id>
    
    Response:
        [
            {
                'track_name': 'Foreclosure',
                'current_task': {'id': 1, 'label': 'Mediation', 'due_date': '2025-10-27', 'tone': 'danger'},
                'upcoming_task': {'id': 2, 'label': 'Sheriff Sale', 'due_date': '2025-11-15', 'tone': 'warning'}
            }
        ]
    """
    
    permission_classes = [AllowAny]
    authentication_classes: list[type[SessionAuthentication]] = []
    
    def get(self, request: Request) -> Response:
        """
        WHAT: Get track milestones for a specific asset hub
        WHY: Dashboard needs current and upcoming tasks organized by track
        WHERE: Called by milestonesCard.vue component
        HOW: Extract asset_hub_id, call service layer, return milestone data
        """
        # WHAT: Extract and validate asset_hub_id parameter
        # WHY: Required to identify which asset's milestones to fetch
        # HOW: Get from query params, validate as integer
        asset_hub_id = request.query_params.get('asset_hub_id')
        if not asset_hub_id:
            return Response(
                {'error': 'asset_hub_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            asset_hub_id = int(asset_hub_id)
        except ValueError:
            return Response(
                {'error': 'asset_hub_id must be a valid integer'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # WHAT: Call service layer to get milestone data
        # WHY: Keep business logic in services, not views
        # WHERE: serv_am_tasking.py
        try:
            milestones = get_track_milestones(asset_hub_id)
            return Response(milestones, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch milestones: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
