"""
API wrapper for geocoding seller+trade address markers.

All business logic is implemented in `acq_module/logic/geocoding_logic.py`.
This view simply calls the logic layer and returns the JSON response.
"""
from __future__ import annotations

from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_GET

from ..logic.geocoding_logic import geocode_markers_for_seller_trade


# moved: _env_api_key -> logic/geocoding_logic.py


# moved: _normalize_address -> logic/geocoding_logic.py


# moved: _build_full_address -> logic/geocoding_logic.py


# moved: _geocode_google -> logic/geocoding_logic.py


# moved: _geocode_with_cache -> logic/geocoding_logic.py


@require_GET
def geocode_markers(request: HttpRequest, seller_id: int, trade_id: int):
    """Thin API wrapper: delegates to logic layer and returns JSON."""
    payload = geocode_markers_for_seller_trade(seller_id=seller_id, trade_id=trade_id)
    return JsonResponse(payload)
