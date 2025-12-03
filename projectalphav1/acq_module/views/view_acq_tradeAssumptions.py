"""
API views for TradeLevelAssumption model.

This module provides endpoints for retrieving and updating TradeLevelAssumption
data for specific trade.
"""

from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

from ..models.model_acq_assumptions import TradeLevelAssumption, ModelingDefaults
from ..models.model_acq_seller import Trade
from ..serializers import TradeLevelAssumptionSerializer

# Module-level logger
logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_trade_level_assumptions(request, trade_id):
    """
    Get trade level assumptions for a specific trade.

    Args:
        request: The Django request object
        trade_id: The ID of the Trade

    Returns:
        JsonResponse containing the TradeLevelAssumption data, or an empty dict if not found
    """
    if not trade_id:
        return JsonResponse({}, safe=False)

    try:
        # Get or initialize TradeLevelAssumption for the trade
        assumption = TradeLevelAssumption.objects.filter(trade_id=trade_id).first()
        
        if assumption:
            serializer = TradeLevelAssumptionSerializer(assumption)
            return Response(serializer.data)

        # Return empty skeleton so UI knows the trade id even without an assumption row yet
        return Response({"trade_id": trade_id})
    
    except Exception as e:
        logger.exception(f"Error fetching trade level assumptions for trade ID {trade_id}: {str(e)}")
        return JsonResponse({"error": "Failed to retrieve trade level assumptions"}, status=500)

@api_view(['POST', 'PUT'])
def update_trade_level_assumptions(request, trade_id):
    """
    Update or create trade level assumptions for a specific trade.

    Args:
        request: The Django request object
        trade_id: The ID of the Trade

    Returns:
        JsonResponse containing the updated TradeLevelAssumption data
    """
    if not trade_id:
        return JsonResponse({"error": "Trade ID is required"}, status=400)

    try:
        # Get the trade object
        trade = Trade.objects.get(pk=trade_id)
        
        # WHAT: Get or create TradeLevelAssumption for the trade
        # WHY: Handle cases where duplicates exist (use first record, log warning)
        # HOW: Try get_or_create first, fall back to filter().first() if multiple exist
        try:
            defaults = ModelingDefaults.current_trade_defaults()
            assumption, _ = TradeLevelAssumption.objects.get_or_create(trade=trade, defaults=defaults)
        except TradeLevelAssumption.MultipleObjectsReturned:
            # WHAT: Handle duplicate TradeLevelAssumption records
            # WHY: Database has duplicate records for this trade (data integrity issue)
            # HOW: Use first record and log warning
            logger.warning(f"Multiple TradeLevelAssumption records found for trade ID {trade_id}. Using first record. Consider cleaning up duplicates.")
            assumption = TradeLevelAssumption.objects.filter(trade=trade).first()

        serializer = TradeLevelAssumptionSerializer(
            instance=assumption,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_payload = dict(serializer.data)
        response_payload["success"] = True
        return Response(response_payload)
    
    except Trade.DoesNotExist:
        return Response({"error": f"Trade with ID {trade_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.exception(f"Error updating trade level assumptions for trade ID {trade_id}: {str(e)}")
        return Response({"error": "Failed to update trade level assumptions"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
