"""
API wrapper for geocoding seller+trade address markers.

All business logic is implemented in `core.services.geocoding`.
This view simply calls the service layer and returns the JSON response.
"""
from __future__ import annotations

from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_GET

from core.services.geocoding import geocode_markers_for_seller_trade


@require_GET
def geocode_markers(request: HttpRequest, seller_id: int, trade_id: int):
    """Thin API wrapper: delegates to geocoding service and returns JSON."""
    payload = geocode_markers_for_seller_trade(seller_id=seller_id, trade_id=trade_id)
    return JsonResponse(payload)
