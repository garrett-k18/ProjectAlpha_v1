from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request

from am_module.models.am_data import AMNote
from am_module.serializers.am_note import AMNoteSerializer


class AMNoteViewSet(ModelViewSet):
    """CRUD for AMNote items with context-aware filtering.

    - GET requires `asset_hub_id` to avoid full-table scans.
    - Additional optional filters: `context_outcome`, `context_task_type`, `context_task_id`, `tag`, `search`.
    - POST may include `asset_hub_id` via body or query params; view assigns FK and auditing fields.

    Docs reviewed:
    - DRF ViewSets & Routers: https://www.django-rest-framework.org/api-guide/viewsets/
    - Filtering via query params: https://www.django-rest-framework.org/api-guide/filtering/
    """

    serializer_class = AMNoteSerializer
    permission_classes = [AllowAny]
    authentication_classes: list[type[SessionAuthentication]] = []  # avoid CSRF in dev for simplicity

    def get_queryset(self):  # type: ignore[override]
        request: Request = self.request
        qp = request.query_params

        asset_hub_id = qp.get('asset_hub_id')
        if not asset_hub_id:
            # For safety, require explicit filter to avoid accidental full-table fetch
            return AMNote.objects.none()
        try:
            hub_id_int = int(asset_hub_id)
        except Exception:
            return AMNote.objects.none()

        qs = AMNote.objects.filter(asset_hub_id=hub_id_int).order_by('-updated_at')

        # Optional context filters
        context_outcome = qp.get('context_outcome')
        if context_outcome:
            qs = qs.filter(context_outcome=context_outcome)

        context_task_type = qp.get('context_task_type')
        if context_task_type:
            qs = qs.filter(context_task_type=context_task_type)

        context_task_id = qp.get('context_task_id')
        if context_task_id:
            try:
                qs = qs.filter(context_task_id=int(context_task_id))
            except Exception:
                # Ignore invalid task id filter; return current qs
                pass

        tag = qp.get('tag')
        if tag:
            qs = qs.filter(tag=tag)

        search = qp.get('search')
        if search:
            qs = qs.filter(body__icontains=search)

        return qs

    # Assign asset_hub and audit fields on create.
    def perform_create(self, serializer):  # type: ignore[override]
        request: Request = self.request
        qp = request.query_params
        data = request.data

        # Accept asset_hub_id from query params or request body for flexibility
        raw_hub = qp.get('asset_hub_id') or data.get('asset_hub_id') or data.get('asset_hub')
        hub_id_int = None
        try:
            if raw_hub is not None:
                hub_id_int = int(raw_hub)
        except Exception:
            hub_id_int = None

        # Only stamp user fields when authenticated to avoid AnonymousUser assignment errors
        user = getattr(request, 'user', None)
        extra = {}
        if user is not None and getattr(user, 'is_authenticated', False):
            extra = { 'created_by': user, 'updated_by': user }

        if hub_id_int is not None:
            serializer.save(asset_hub_id=hub_id_int, **extra)
        else:
            serializer.save(**extra)

    # Ensure updated_by is stamped on updates
    def perform_update(self, serializer):  # type: ignore[override]
        request: Request = self.request
        user = getattr(request, 'user', None)
        if user is not None and getattr(user, 'is_authenticated', False):
            serializer.save(updated_by=user)
        else:
            serializer.save()
