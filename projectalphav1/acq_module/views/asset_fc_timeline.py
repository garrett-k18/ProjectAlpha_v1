"""
acq_module.views.asset_fc_timeline

What: API view to return an asset-scoped foreclosure timeline (state + durations by status).
Why: Provide consistent, reusable timeline payload for platform-wide use (ACQ/AM/reporting).
Where: projectalphav1/acq_module/views/asset_fc_timeline.py
How: Calls service function in logic.model_logic and serializes response.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from acq_module.logic.model_logic import get_asset_fc_timeline
from acq_module.serializers.asset_fc_timeline import AssetFCTimelineSerializer


class AssetFCTimelineView(APIView):
    """GET /api/acq/assets/{id}/fc-timeline/

    Returns asset state and foreclosure timeline durations by status.
    """
    def get(self, request: Request, id: int, *args, **kwargs) -> Response:
        data = get_asset_fc_timeline(id)
        ser = AssetFCTimelineSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data, status=status.HTTP_200_OK)
