import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models.model_acq_assumptions import ModelingDefaults
from ..serializers import AssumptionDefaultsSerializer

logger = logging.getLogger(__name__)


@api_view(["GET"])
def get_assumption_defaults(request):
    defaults = ModelingDefaults.get_active()
    serializer = AssumptionDefaultsSerializer(defaults)
    return Response(serializer.data)


@api_view(["PATCH", "PUT"])
def update_assumption_defaults(request):
    defaults = ModelingDefaults.get_active()
    serializer = AssumptionDefaultsSerializer(defaults, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)
