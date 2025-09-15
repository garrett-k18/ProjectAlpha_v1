"""
API views for TradeLevelAssumption model.

This module provides endpoints for retrieving and updating TradeLevelAssumption
data for specific trade.
"""

from django.http import JsonResponse
from rest_framework.decorators import api_view
import logging
from datetime import datetime
import json

from ..models.assumptions import TradeLevelAssumption
from ..models.seller import Trade

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
            data = {
                "id": assumption.id,
                "trade_id": assumption.trade.id,
                "bid_date": assumption.bid_date.isoformat() if assumption.bid_date else None,
                "settlement_date": assumption.settlement_date.isoformat() if assumption.settlement_date else None,
                "pctUPB": str(assumption.pctUPB) if assumption.pctUPB else None,
                "target_irr": str(assumption.target_irr) if assumption.target_irr else None,
                "discount_rate": str(assumption.discount_rate) if assumption.discount_rate else None,
                "perf_rpl_hold_period": assumption.perf_rpl_hold_period,
                "servicing_transfer_date": assumption.servicing_transfer_date.isoformat() if assumption.servicing_transfer_date else None,
                "mod_rate": str(assumption.mod_rate) if assumption.mod_rate else None,
                "mod_term": assumption.mod_term,
                "mod_balance": str(assumption.mod_balance) if assumption.mod_balance else None,
                "mod_date": assumption.mod_date.isoformat() if assumption.mod_date else None,
                "mod_maturity_date": assumption.mod_maturity_date.isoformat() if assumption.mod_maturity_date else None
            }
            return JsonResponse(data)
        else:
            # Return empty object with trade_id
            return JsonResponse({"trade_id": trade_id})
    
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
        
        # Get or create TradeLevelAssumption for the trade
        assumption, created = TradeLevelAssumption.objects.get_or_create(trade=trade)
        
        # Parse the request data
        data = json.loads(request.body)
        
        # Update bid_date and settlement_date if provided
        if 'bid_date' in data and data['bid_date']:
            assumption.bid_date = datetime.fromisoformat(data['bid_date'].replace('Z', '+00:00'))
        
        if 'settlement_date' in data and data['settlement_date']:
            assumption.settlement_date = datetime.fromisoformat(data['settlement_date'].replace('Z', '+00:00'))
        
        # Save the updated assumption
        assumption.save()
        
        # Return the updated data
        return JsonResponse({
            "id": assumption.id,
            "trade_id": assumption.trade.id,
            "bid_date": assumption.bid_date.isoformat() if assumption.bid_date else None,
            "settlement_date": assumption.settlement_date.isoformat() if assumption.settlement_date else None,
            "success": True
        })
    
    except Trade.DoesNotExist:
        return JsonResponse({"error": f"Trade with ID {trade_id} does not exist"}, status=404)
    
    except Exception as e:
        logger.exception(f"Error updating trade level assumptions for trade ID {trade_id}: {str(e)}")
        return JsonResponse({"error": "Failed to update trade level assumptions"}, status=500)
