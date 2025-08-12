from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from ..models.seller import SellerRawData
from django.db.models import Q

def get_seller_trade_data(request, seller_id, trade_id=None):
    """
    A view to fetch raw data for a specific seller and optional trade.
    
    If trade_id is provided, returns data for that specific seller+trade combination.
    If trade_id is None, returns all trades for the given seller.
    
    Args:
        request: The Django request object
        seller_id: The ID of the Seller (required)
        trade_id: The ID of the Trade (optional)
        
    Returns:
        JsonResponse containing:
        - If trade_id provided: List of data entries for that seller+trade
        - If no trade_id: Dictionary with seller's trades and their data
        - Empty list/dict if no data found (instead of 404)
    """
    # Base query - filter by seller
    query = Q(seller_id=seller_id)
    
    # Add trade filter if trade_id is provided
    if trade_id is not None:
        query &= Q(trade_id=trade_id)
    
    # Get all matching entries
    entries = SellerRawData.objects.filter(query).select_related('trade')
    
    if not entries.exists():
        return JsonResponse([], safe=False)
    
    # If trade_id was specified, return just the data list
    if trade_id is not None:
        data_list = [entry.data for entry in entries]
        return JsonResponse(data_list, safe=False, encoder=DjangoJSONEncoder)
    
    # If no trade_id, group by trade
    result = {}
    for entry in entries:
        trade_id = str(entry.trade_id)
        if trade_id not in result:
            result[trade_id] = {
                'trade_name': entry.trade.trade_name,
                'bid_date': entry.trade.bid_date.isoformat(),
                'data_entries': []
            }
        result[trade_id]['data_entries'].append(entry.data)
    
    return JsonResponse(result, encoder=DjangoJSONEncoder)
