"""
Performance Summary ViewSet

WHAT: API endpoint for Performance Summary grid (P&L metrics)
WHY: Provides data for PLMetrics.vue component in loan-level tabs
HOW: Returns BlendedOutcomeModel data via PerformanceSummarySerializer
WHERE: Accessed from frontend at /api/am/performance-summary/<asset_hub_id>/

Docs reviewed:
- DRF ViewSets: https://www.django-rest-framework.org/api-guide/viewsets/
- DRF Response: https://www.django-rest-framework.org/api-guide/responses/
"""

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from am_module.models.boarded_data import BlendedOutcomeModel
from am_module.serializers.serial_performance_summary import PerformanceSummarySerializer


class PerformanceSummaryViewSet(ViewSet):
    """
    ViewSet for Performance Summary data.
    
    Endpoints:
    - GET /api/am/performance-summary/<asset_hub_id>/ - Get P&L metrics for an asset
    """
    
    def retrieve(self, request, pk=None):
        """
        WHAT: Get performance summary data for a specific asset
        WHY: Frontend PLMetrics.vue needs underwritten/realized values
        HOW: Fetch BlendedOutcomeModel by asset_hub_id, serialize and return
        
        Args:
            pk: asset_hub_id (primary key of BlendedOutcomeModel)
            
        Returns:
            PerformanceSummarySerializer data with all P&L metrics
        """
        # BlendedOutcomeModel uses asset_hub as primary key (1:1 relationship)
        outcome_model = get_object_or_404(
            BlendedOutcomeModel.objects.select_related('asset_hub'),
            asset_hub_id=pk
        )
        
        serializer = PerformanceSummarySerializer(outcome_model)
        return Response(serializer.data, status=status.HTTP_200_OK)
