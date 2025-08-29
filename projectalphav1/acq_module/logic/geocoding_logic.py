"""
Geocoding logic for seller+trade address markers.

This module contains ONLY business logic and helpers. Views should import and call
`geocode_markers_for_seller_trade()` and return its result as JSON.

Docs reviewed:
- Geocod.io Python client: https://pygeocodio.readthedocs.io/en/latest/geocode.html
- Geocod.io API reference: https://www.geocod.io/docs/
- Django cache framework: https://docs.djangoproject.com/en/5.2/topics/cache/
- jVectorMap markers format: https://jvectormap.com/documentation/javascript-api/
"""
from __future__ import annotations

# Standard library imports for environment and typing
import os  # used to read env vars (GEOCODIO_API_KEY, TTLs, etc.)
from typing import Dict, List, Optional, Tuple, Any  # precise typing for clarity

# Django imports for caching and query construction
from django.core.cache import cache  # centralized cache per Django settings
from django.db.models import Q  # used to filter SellerRawData by seller_id/trade_id

# Third-party client for Geocod.io (handle API differences across versions)
try:
    # Newer pygeocodio API
    from geocodio import GeocodioClient as _GeocodioCls  # type: ignore
except Exception:
    try:
        # Some versions expose Geocodio class instead
        from geocodio import Geocodio as _GeocodioCls  # type: ignore
    except Exception as _e:
        # Defer import error until runtime usage to avoid crashing Django import
        _GeocodioCls = None  # type: ignore

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
    """Return the Geocod.io API key from env or None when missing.

    Tries common env var names in order to support different setups:
    - GEOCODIO_API_KEY
    - GEOCODIO_KEY
    - GEOCODIO
    - GEOCODIO_TOKEN
    - GEOCODE
    - geocode
    Also checks legacy GOOGLE_MAPS_API_KEY as a last resort (for backward compat),
    though the Geocod.io client expects a Geocod.io key.
    """
    for name in (
        "GEOCODIO_API_KEY",
        "GEOCODIO_KEY",
        "GEOCODIO",
        "GEOCODIO_TOKEN",
        "GEOCODE",
        "geocode",
        "GOOGLE_MAPS_API_KEY",
    ):  # note: os.getenv is case-sensitive
        val = os.getenv(name)
        if val:
            return val
    return None


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
    """Compose a single-line address from a SellerRawData-like dict using
    ONLY city, state, zip (street address intentionally ignored).

    Expected keys in row: city, state, zip (all optional)
    """
    return ", ".join([
        str(row.get("city", "") or "").strip(),
        str(row.get("state", "") or "").strip(),
        str(row.get("zip", "") or "").strip(),
    ]).strip(", ")


def _build_display_address(row: Dict[str, Optional[str]]) -> str:
    """Compose a human-friendly full address string for marker labels.

    Prefers street, city, state, zip when available; gracefully collapses
    missing parts.
    """
    return ", ".join([
        str(row.get("street_address", "") or "").strip(),
        str(row.get("city", "") or "").strip(),
        str(row.get("state", "") or "").strip(),
        str(row.get("zip", "") or "").strip(),
    ]).strip(", ")


def _build_address_candidates(row: Dict[str, Optional[str]]) -> List[str]:
    """Build fallback address candidates in descending specificity.

    Order tried:
    1) city, state, zip
    2) state, zip
    3) state

    Returns a list of non-empty, de-duplicated candidate strings.
    """
    city = str(row.get("city", "") or "").strip()
    state = str(row.get("state", "") or "").strip()
    zip_code = str(row.get("zip", "") or "").strip()

    candidates: List[str] = []

    # city, state, zip
    parts1 = [p for p in [city, state, zip_code] if p]
    cand1 = ", ".join(parts1).strip(", ")
    if cand1:
        candidates.append(cand1)

    # state, zip
    parts2 = [p for p in [state, zip_code] if p]
    cand2 = ", ".join(parts2).strip(", ")
    if cand2 and cand2 not in candidates:
        candidates.append(cand2)

    # state
    if state and state not in candidates:
        candidates.append(state)

    return candidates


_CLIENTS: Dict[str, Any] = {}


def _get_geocodio_client(api_key: str) -> Any:
    """Return a cached Geocod.io client for the given api_key.

    Supports both `GeocodioClient` and legacy `Geocodio` classes depending on
    installed pygeocodio version.
    """
    client = _CLIENTS.get(api_key)
    if client is None:
        # Set a conservative timeout to avoid hanging requests when supported
        if _GeocodioCls is None:
            raise ImportError(
                "Geocod.io client class not found. Ensure a compatible client is installed (geocodio-library-python)."
            )
        try:
            client = _GeocodioCls(api_key, timeout=10)
        except TypeError:
            # Some client versions may not accept 'timeout'
            client = _GeocodioCls(api_key)
        _CLIENTS[api_key] = client
    return client


def _geocode_geocodio(address: str, api_key: str) -> Optional[Tuple[float, float]]:
    """Call Geocod.io API for a single address via pygeocodio.

    Returns:
        (lat, lng) tuple on success, or None on failure.

    Notes:
        - pygeocodio's `coords` returns (lng, lat), so we reorder to (lat, lng).
        - Service coverage: US and Canada.
    """
    try:
        client = _get_geocodio_client(api_key)
        result = client.geocode(address)
        if not result:
            return None

        # pygeocodio path: result.coords returns (lng, lat)
        coords = getattr(result, "coords", None)
        if coords:
            try:
                lng, lat = coords
                if lat is None or lng is None:
                    return None
                return float(lat), float(lng)
            except Exception:
                pass

        # Official geocodio-library-python path:
        # result.results[0].location with lat/lng as attributes or dict keys
        results_list = getattr(result, "results", None)
        if results_list:
            try:
                first = results_list[0]
                loc = getattr(first, "location", None)
                if loc is not None:
                    lat = getattr(loc, "lat", None)
                    lng = getattr(loc, "lng", None)
                    if lat is None or lng is None:
                        # Handle dict-like location
                        try:
                            lat = lat or (loc.get("lat") if hasattr(loc, "get") else None)
                            lng = lng or (loc.get("lng") if hasattr(loc, "get") else None)
                        except Exception:
                            pass
                    if lat is not None and lng is not None:
                        return float(lat), float(lng)
            except Exception:
                pass

        return None
    except Exception:
        # Swallow exceptions and return None; callers handle None as failure
        return None


def _geocode_with_cache(full_address: str, api_key: str) -> Tuple[Optional[Tuple[float, float]], str]:
    """Resolve an address using cache first, then Geocod.io if needed.

    Returns:
        (coords, source)
            - coords: (lat, lng) or None
            - source: one of {"cache", "live", "none"}
    """
    key = f"geocode:{_normalize_address([full_address])}"

    cached = cache.get(key)
    if cached:
        return cached, "cache"

    coords = _geocode_geocodio(full_address, api_key)
    if coords is not None:
        cache.set(key, coords, timeout=CACHE_TTL_SECONDS)
        return coords, "live"

    return None, "none"


def _geocode_with_cache_any(address_candidates: List[str], api_key: str) -> Tuple[Optional[Tuple[float, float]], str, Optional[str]]:
    """Try multiple address candidates with cache+live fallback.

    Args:
        address_candidates: list produced by `_build_address_candidates()`
        api_key: Geocod.io API key

    Returns:
        (coords, source, used_address)
            - coords: (lat, lng) or None
            - source: "cache" | "live" | "none" (for the attempt that succeeded)
            - used_address: the address string that produced coords, or None
    """
    for addr in address_candidates:
        coords, source = _geocode_with_cache(addr, api_key)
        if coords is not None:
            return coords, source, addr
    return None, "none", None


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
            "error": "GEOCODIO_API_KEY missing on server",
        }

    # Query only the fields needed to compose addresses and labels for markers
    rows = list(
        SellerRawData.objects
        .filter(Q(seller_id=seller_id) & Q(trade_id=trade_id))
        .values("id", "street_address", "city", "state", "zip")
    )

    # Deduplicate by the most specific candidate to minimize geocoding calls
    # (and protect quotas)
    addr_to_rows: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        candidates = _build_address_candidates(r)
        if not candidates:
            continue
        primary = candidates[0]
        norm = _normalize_address([primary])
        if not norm:
            continue
        addr_to_rows.setdefault(norm, []).append({
            "id": r["id"],
            "candidates": candidates,
            "display_name": _build_display_address(r),
        })

    unique_addrs = list(addr_to_rows.keys())[:MAX_UNIQUE_ADDRESSES]

    markers: List[Dict[str, Any]] = []
    any_live = False
    any_cache = False

    for norm in unique_addrs:
        # Use the first representative row for label/name; multiple ids may share address
        representative = addr_to_rows[norm][0]
        candidates = representative["candidates"]
        coords, source, used_addr = _geocode_with_cache_any(candidates, api_key)
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
            "name": representative.get("display_name") or used_addr or candidates[0],
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
