from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication

from am_module.models.am_data import AMNote
from am_module.serializers.am_note import AMNoteSerializer


class AMNoteViewSet(ModelViewSet):
    """CRUD for AMNote items.

    Dev mode: Allow open access; in prod, tighten to IsAuthenticated.
    """

    queryset = AMNote.objects.all().order_by('-updated_at')
    serializer_class = AMNoteSerializer
    permission_classes = [AllowAny]
    authentication_classes = []  # avoid CSRF in dev for simplicity
