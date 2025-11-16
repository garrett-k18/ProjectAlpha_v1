"""
API wrapper for geocoding seller+trade address markers.

All business logic is implemented in `core.services.geocoding`.
This view simply calls the service layer and returns the JSON response.
"""
from __future__ import annotations

from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_GET

from core.services.serv_co_geocoding import geocode_markers_for_seller_trade


@require_GET
def geocode_markers(request: HttpRequest, seller_id: int, trade_id: int):
    """Thin API wrapper: delegates to geocoding service and returns JSON."""
    import logging
    logger = logging.getLogger(__name__)
    
    print(f'\n\n=== GEOCODE MARKERS CALLED: seller_id={seller_id}, trade_id={trade_id} ===\n')
    logger.info(f'[GEOCODE MARKERS] Starting for seller_id={seller_id}, trade_id={trade_id}')
    
    payload = geocode_markers_for_seller_trade(seller_id=seller_id, trade_id=trade_id)
    
    print(f'=== GEOCODE MARKERS COMPLETE: {payload.get("count")} markers, source={payload.get("source")} ===\n\n')
    logger.info(f'[GEOCODE MARKERS] Returning {payload.get("count")} markers, source={payload.get("source")}')
    
    return JsonResponse(payload)
