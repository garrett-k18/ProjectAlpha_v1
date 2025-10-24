from __future__ import annotations

# DRF docs reviewed:
# - ViewSets & Routers: https://www.django-rest-framework.org/api-guide/viewsets/
# - Mixins: https://www.django-rest-framework.org/api-guide/generic-views/#mixins
# - Filtering via query params: https://www.django-rest-framework.org/api-guide/filtering/

from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import status, mixins
from django.db import transaction
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from am_module.models.am_data import (
    REOData, REOtask,
    FCSale, FCTask,
    DIL, DILTask,
    ShortSale, ShortSaleTask,
    Modification, ModificationTask,
    REOScope,
)
from am_module.serializers.outcomes import (
    REODataSerializer, REOTaskSerializer,
    FCSaleSerializer, FCTaskSerializer,
    DILSerializer, DILTaskSerializer,
    ShortSaleSerializer, ShortSaleTaskSerializer,
    ModificationSerializer, ModificationTaskSerializer,
    REOScopeSerializer,
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
    queryset = REOData.objects.all().select_related('asset_hub', 'crm')
    serializer_class = REODataSerializer


class FCSaleViewSet(_OutcomeBaseViewSet):
    queryset = FCSale.objects.all().select_related('asset_hub', 'crm')
    serializer_class = FCSaleSerializer


class DILViewSet(_OutcomeBaseViewSet):
    queryset = DIL.objects.all().select_related('asset_hub', 'crm')
    serializer_class = DILSerializer


class ShortSaleViewSet(_OutcomeBaseViewSet):
    queryset = ShortSale.objects.all().select_related('asset_hub', 'crm')
    serializer_class = ShortSaleSerializer


class ModificationViewSet(_OutcomeBaseViewSet):
    queryset = Modification.objects.all().select_related('asset_hub', 'crm')
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
    queryset = REOScope.objects.all().select_related('asset_hub', 'crm', 'reo_task')

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
