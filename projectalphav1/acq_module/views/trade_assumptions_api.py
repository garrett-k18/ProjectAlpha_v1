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
from core.models import Servicer

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
                "servicer_id": assumption.servicer_id,
                "servicer_name": getattr(assumption.servicer, 'servicer_name', None),
                "bid_date": assumption.bid_date.isoformat() if assumption.bid_date else None,
                "settlement_date": assumption.settlement_date.isoformat() if assumption.settlement_date else None,
                "servicing_transfer_date": assumption.servicing_transfer_date.isoformat() if assumption.servicing_transfer_date else None,
                "pctUPB": str(assumption.pctUPB) if assumption.pctUPB is not None else None,
                "target_irr": str(assumption.target_irr) if assumption.target_irr is not None else None,
                "discount_rate": str(assumption.discount_rate) if assumption.discount_rate is not None else None,
                "perf_rpl_hold_period": assumption.perf_rpl_hold_period,
                # Modification assumptions
                "mod_rate": str(assumption.mod_rate) if assumption.mod_rate is not None else None,
                "mod_legal_term": assumption.mod_legal_term,
                "mod_amort_term": assumption.mod_amort_term,
                "max_mod_ltv": str(assumption.max_mod_ltv) if assumption.max_mod_ltv is not None else None,
                "mod_io_flag": assumption.mod_io_flag,
                "mod_down_pmt": str(assumption.mod_down_pmt) if assumption.mod_down_pmt is not None else None,
                "mod_orig_cost": str(assumption.mod_orig_cost) if assumption.mod_orig_cost is not None else None,
                "mod_setup_duration": assumption.mod_setup_duration,
                "mod_hold_duration": assumption.mod_hold_duration,
                # Acquisition costs and AM fees
                "acq_legal_cost": str(assumption.acq_legal_cost) if assumption.acq_legal_cost is not None else None,
                "acq_dd_cost": str(assumption.acq_dd_cost) if assumption.acq_dd_cost is not None else None,
                "acq_tax_title_cost": str(assumption.acq_tax_title_cost) if assumption.acq_tax_title_cost is not None else None,
                "am_fee_pct": str(assumption.am_fee_pct) if assumption.am_fee_pct is not None else None,
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
        
        # Optional: servicing transfer date
        if 'servicing_transfer_date' in data and data['servicing_transfer_date']:
            assumption.servicing_transfer_date = datetime.fromisoformat(data['servicing_transfer_date'].replace('Z', '+00:00'))

        # Update servicer if provided (accepts servicer_id or servicerId)
        servicer_id = data.get('servicer_id') or data.get('servicerId')
        if servicer_id is not None:
            try:
                assumption.servicer = Servicer.objects.get(pk=int(servicer_id))
            except (Servicer.DoesNotExist, ValueError, TypeError):
                assumption.servicer = None

        # Save the updated assumption
        assumption.save()
        
        # Return the updated data
        return JsonResponse({
            "id": assumption.id,
            "trade_id": assumption.trade.id,
            "servicer_id": assumption.servicer_id,
            "servicer_name": getattr(assumption.servicer, 'servicer_name', None),
            "bid_date": assumption.bid_date.isoformat() if assumption.bid_date else None,
            "settlement_date": assumption.settlement_date.isoformat() if assumption.settlement_date else None,
            "servicing_transfer_date": assumption.servicing_transfer_date.isoformat() if assumption.servicing_transfer_date else None,
            "success": True
        })
    
    except Trade.DoesNotExist:
        return JsonResponse({"error": f"Trade with ID {trade_id} does not exist"}, status=404)
    
    except Exception as e:
        logger.exception(f"Error updating trade level assumptions for trade ID {trade_id}: {str(e)}")
        return JsonResponse({"error": "Failed to update trade level assumptions"}, status=500)
