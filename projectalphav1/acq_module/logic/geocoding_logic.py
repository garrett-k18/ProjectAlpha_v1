"""
Geocoding logic for seller+trade address markers.

This module contains ONLY business logic and helpers. Views should import and call
`geocode_markers_for_seller_trade()` and return its result as JSON.

Docs reviewed:
- Google Geocoding API: https://developers.google.com/maps/documentation/geocoding/requests-geocoding
- Django cache framework: https://docs.djangoproject.com/en/5.2/topics/cache/
- jVectorMap markers format: https://jvectormap.com/documentation/javascript-api/
"""
from __future__ import annotations

# Standard library imports for environment, HTTP requests, and JSON handling
import os  # used to read env vars like GOOGLE_MAPS_API_KEY and TTLs
import json  # used to parse Google Geocoding API responses
import urllib.parse  # used to safely encode query parameters
import urllib.request  # used to perform a simple HTTP GET request to Google API
from typing import Dict, List, Optional, Tuple, Any  # precise typing for clarity

# Django imports for caching and query construction
from django.core.cache import cache  # centralized cache per Django settings
from django.db.models import Q  # used to filter SellerRawData by seller_id/trade_id

# App model import: `SellerRawData` contains the address fields we need
from ..models.seller import SellerRawData

# ---------------------------------------------------------------------------
# Configuration constants (read from environment with safe defaults)
# ---------------------------------------------------------------------------
# Cache TTL (seconds). Default 7 days to minimize repeat lookups without persisting.
CACHE_TTL_SECONDS: int = int(os.getenv("GEOCODE_CACHE_TTL", str(7 * 24 * 60 * 60)))

# Soft cap on number of unique addresses geocoded for a single request
MAX_UNIQUE_ADDRESSES: int = int(os.getenv("GEOCODE_MAX_ADDRESSES", "500"))


def _env_api_key() -> Optional[str]:
    """Return the Google Maps Geocoding API key from env or None when missing.

    Env var: GOOGLE_MAPS_API_KEY
    Keeping key server-side prevents exposing it to the frontend.
    """
    return os.getenv("GOOGLE_MAPS_API_KEY")


def _normalize_address(parts: List[str]) -> str:
    """Normalize address components for use as a stable cache key.

    Steps:
    - Trim whitespace on each part
    - Drop empty parts
    - Join with ", "
    - Collapse internal multiple spaces
    - Lowercase for case-insensitive equality
    """
    joined = ", ".join(p.strip() for p in parts if p and str(p).strip())
    return " ".join(joined.split()).lower()


def _build_full_address(row: Dict[str, Optional[str]]) -> str:
    """Compose a single-line address from a SellerRawData-like dict.

    Expected keys in row: street_address, city, state, zip (all optional)
    """
    return ", ".join([
        str(row.get("street_address", "") or "").strip(),
        str(row.get("city", "") or "").strip(),
        str(row.get("state", "") or "").strip(),
        str(row.get("zip", "") or "").strip(),
    ]).strip(", ")


def _geocode_google(address: str, api_key: str) -> Optional[Tuple[float, float]]:
    """Call Google Geocoding API for a single address.

    Returns:
        (lat, lng) tuple on success, or None on failure.

    Reference: Google Geocoding API response structure
    https://developers.google.com/maps/documentation/geocoding/requests-geocoding
    """
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    q = urllib.parse.urlencode({"address": address, "key": api_key})
    url = f"{base_url}?{q}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None

    status = data.get("status")
    if status != "OK":
        # Common statuses: ZERO_RESULTS, OVER_QUERY_LIMIT, REQUEST_DENIED, INVALID_REQUEST
        return None

    results = data.get("results") or []
    if not results:
        return None

    loc = results[0].get("geometry", {}).get("location", {})
    lat = loc.get("lat")
    lng = loc.get("lng")
    if lat is None or lng is None:
        return None

    return float(lat), float(lng)


def _geocode_with_cache(full_address: str, api_key: str) -> Tuple[Optional[Tuple[float, float]], str]:
    """Resolve an address using cache first, then Google if needed.

    Returns:
        (coords, source)
            - coords: (lat, lng) or None
            - source: one of {"cache", "live", "none"}
    """
    key = f"geocode:{_normalize_address([full_address])}"

    cached = cache.get(key)
    if cached:
        return cached, "cache"

    coords = _geocode_google(full_address, api_key)
    if coords is not None:
        cache.set(key, coords, timeout=CACHE_TTL_SECONDS)
        return coords, "live"

    return None, "none"


def geocode_markers_for_seller_trade(seller_id: int, trade_id: int) -> Dict[str, Any]:
    """Business logic: build geocoded markers for all addresses under seller+trade.

    Args:
        seller_id: The seller identifier to filter rows by
        trade_id:  The trade identifier to filter rows by

    Returns:
        A dict payload ready to be returned by a Django view as JSON, with keys:
        - markers: list of { lat: float, lng: float, name: str, id: int }
        - count:   number of markers
        - source:  "cache" | "live" | "mixed" | "none"
        - error:   optional error string (e.g., missing API key)
    """
    api_key = _env_api_key()
    if not api_key:
        return {
            "markers": [],
            "count": 0,
            "source": "none",
            "error": "GOOGLE_MAPS_API_KEY missing on server",
        }

    # Query only the fields needed to compose addresses and labels for markers
    rows = list(
        SellerRawData.objects
        .filter(Q(seller_id=seller_id) & Q(trade_id=trade_id))
        .values("id", "street_address", "city", "state", "zip")
    )

    # Deduplicate addresses to minimize geocoding calls (and protect quotas)
    addr_to_rows: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        full_addr = _build_full_address(r)
        norm = _normalize_address([full_addr])
        if not norm:
            continue
        addr_to_rows.setdefault(norm, []).append({"id": r["id"], "full": full_addr})

    unique_addrs = list(addr_to_rows.keys())[:MAX_UNIQUE_ADDRESSES]

    markers: List[Dict[str, Any]] = []
    any_live = False
    any_cache = False

    for norm in unique_addrs:
        # Use the first representative row for label/name; multiple ids may share address
        representative = addr_to_rows[norm][0]
        full_addr = representative["full"]
        coords, source = _geocode_with_cache(full_addr, api_key)
        if source == "live":
            any_live = True
        elif source == "cache":
            any_cache = True
        if not coords:
            continue
        lat, lng = coords
        markers.append({
            "lat": float(lat),
            "lng": float(lng),
            "name": full_addr,
            "id": representative["id"],
        })

    source = "none"
    if any_live and any_cache:
        source = "mixed"
    elif any_live:
        source = "live"
    elif any_cache:
        source = "cache"

    return {
        "markers": markers,
        "count": len(markers),
        "source": source,
    }
