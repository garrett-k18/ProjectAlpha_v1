"""
Geocoding services for address enrichment.

This service handles external API calls to Geocod.io and persists results 
to the LlDataEnrichment model. No caching layer - coordinates are stored
permanently in the database after successful API calls.

Docs reviewed:
- Geocod.io Python client: https://pygeocodio.readthedocs.io/en/latest/geocode.html
- Geocod.io API reference: https://www.geocod.io/docs/
"""
from __future__ import annotations

import os
import re
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal

from django.db.models import Q
from django.utils import timezone

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
from acq_module.models.seller import SellerRawData
from core.models import LlDataEnrichment

# ---------------------------------------------------------------------------
# Configuration constants (read from environment with safe defaults)
# ---------------------------------------------------------------------------
# Configuration constants
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


def _normalize_address_for_dedup(parts: List[str]) -> str:
    """Normalize address for deduplication purposes.
    
    Simple normalization to group similar addresses together
    to minimize API calls for the same location.
    """
    joined = ", ".join(p.strip() for p in parts if p and str(p).strip())
    return " ".join(joined.split()).lower().strip()


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
    """Compose a concise label for markers using ONLY City and State.

    Street and ZIP are intentionally ignored to keep the vector map approximate
    (US-wide view) and to align with geocoding that targets city centroids
    first, then state centroids as a fallback.
    """
    return ", ".join([
        str(row.get("city", "") or "").strip(),
        str(row.get("state", "") or "").strip(),
    ]).strip(", ")


def _build_address_candidates(row: Dict[str, Optional[str]]) -> List[str]:
    """Build address candidates for geocoding: City+State, then State.

    This intentionally ignores street address and ZIP to reduce geocoding
    precision (acceptable for a US-wide vector map) and improve performance.
    The goal is to geocode to the city centroid first; if that fails, use the
    state centroid.
    """
    city = str(row.get("city", "") or "").strip()
    state = str(row.get("state", "") or "").strip()

    candidates: List[str] = []

    # 1) "City, State" (highest preference for our use case)
    if city and state:
        candidates.append(f"{city}, {state}")

    # 2) "State" (fallback to state centroid)
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


def _call_geocoding_api(address: str, api_key: str) -> Optional[Tuple[float, float]]:
    """Call Geocod.io API directly for an address.
    
    Returns (lat, lng) tuple on success, None on failure.
    """
    return _geocode_geocodio(address, api_key)


def _try_geocoding_candidates(address_candidates: List[str], api_key: str) -> Tuple[Optional[Tuple[float, float]], Optional[str]]:
    """Try multiple address candidates with API calls.

    Args:
        address_candidates: list produced by `_build_address_candidates()`
        api_key: Geocod.io API key

    Returns:
        (coords, used_address)
            - coords: (lat, lng) or None
            - used_address: the address string that produced coords, or None
    """
    for addr in address_candidates:
        coords = _call_geocoding_api(addr, api_key)
        if coords is not None:
            return coords, addr
    return None, None


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
        .values("asset_hub_id", "city", "state", "zip")
    )

    # Deduplicate by the most specific candidate to minimize geocoding calls
    # (and protect quotas)
    addr_to_rows: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        candidates = _build_address_candidates(r)
        if not candidates:
            continue
        primary = candidates[0]
        norm = _normalize_address_for_dedup([primary])
        if not norm:
            continue
        addr_to_rows.setdefault(norm, []).append({
            "id": r["asset_hub_id"],
            "candidates": candidates,
            "display_name": _build_display_address(r),
        })

    unique_addrs = list(addr_to_rows.keys())[:MAX_UNIQUE_ADDRESSES]

    markers: List[Dict[str, Any]] = []
    any_api_calls = False

    for norm in unique_addrs:
        # Use the first representative row for label/name; multiple ids may share address
        representative = addr_to_rows[norm][0]
        candidates = representative["candidates"]
        # 1) Prefer DB-persisted geocode if present on any row for this address
        persisted = None
        used_addr = None
        for r in addr_to_rows[norm]:
            enr = LlDataEnrichment.objects.filter(seller_raw_data_id=r["id"]).only(
                "geocode_lat", "geocode_lng", "geocode_used_address"
            ).first()
            if enr and enr.geocode_lat is not None and enr.geocode_lng is not None:
                try:
                    persisted = (float(enr.geocode_lat), float(enr.geocode_lng))
                    used_addr = enr.geocode_used_address or None
                    break
                except Exception:
                    persisted = None

        if persisted is not None:
            coords, used_addr = persisted, used_addr
            source = "db"
        else:
            # 2) Otherwise call API directly
            coords, used_addr = _try_geocoding_candidates(candidates, api_key)
            source = "api" if coords else "none"

            # If we obtained coordinates, upsert for all rows sharing this address
            if coords is not None:
                lat, lng = coords
                when = timezone.now()
                for r in addr_to_rows[norm]:
                    # safe upsert pattern
                    enr_obj, _created = LlDataEnrichment.objects.get_or_create(
                        seller_raw_data_id=r["id"],
                        defaults={
                            "geocode_lat": lat,
                            "geocode_lng": lng,
                            "geocode_used_address": used_addr or candidates[0],
                            "geocode_full_address": used_addr or candidates[0],
                            "geocode_display_address": representative.get("display_name") or "",
                            "geocoded_at": when,
                        },
                    )
                    # Ensure asset_hub mirrors the raw row's hub
                    if getattr(enr_obj, 'asset_hub_id', None) is None:
                        try:
                            from acq_module.models.seller import SellerRawData as _SRD
                            _raw = _SRD.objects.only('asset_hub_id').get(pk=r["id"])
                            if getattr(_raw, 'asset_hub_id', None) is not None:
                                enr_obj.asset_hub_id = _raw.asset_hub_id
                                enr_obj.save(update_fields=[
                                    'asset_hub',
                                ])
                        except Exception:
                            pass
                    # Update existing if empty or different
                    if not _created:
                        changed = False
                        if not enr_obj.geocode_lat or not enr_obj.geocode_lng:
                            enr_obj.geocode_lat = lat
                            enr_obj.geocode_lng = lng
                            changed = True
                        if not enr_obj.geocode_used_address:
                            enr_obj.geocode_used_address = used_addr or candidates[0]
                            changed = True
                        if not enr_obj.geocode_full_address:
                            enr_obj.geocode_full_address = used_addr or candidates[0]
                            changed = True
                        if not enr_obj.geocode_display_address:
                            enr_obj.geocode_display_address = representative.get("display_name") or ""
                            changed = True
                        if changed:
                            enr_obj.geocoded_at = when
                            enr_obj.save(update_fields=[
                                "geocode_lat", "geocode_lng", "geocode_used_address",
                                "geocode_full_address", "geocode_display_address",
                                "geocoded_at",
                            ])
        if source == "api":
            any_api_calls = True
        if not coords:
            continue
        lat, lng = coords
        markers.append({
            "lat": float(lat),
            "lng": float(lng),
            "name": representative.get("display_name") or used_addr or candidates[0],
            "id": representative["id"],
        })

    # Determine overall source for response
    if any_api_calls:
        source = "api"
    else:
        source = "db"

    return {
        "markers": markers,
        "count": len(markers),
        "source": source,
    }


def geocode_row(row_id: int) -> Optional[Tuple[float, float]]:
    """Geocode a single SellerRawData row and persist to LlDataEnrichment.

    This is used by post-save signals to populate coordinates automatically
    on creation without requiring a batch call. It follows the same order:
    DB -> cache -> live. Returns (lat, lng) when available.
    """
    try:
        api_key = _env_api_key()
        if not api_key:
            return None

        r = (SellerRawData.objects
             .filter(pk=row_id)
             .values("asset_hub_id", "city", "state", "zip")
             .first())
        if not r:
            return None

        # Check persisted first
        enr = LlDataEnrichment.objects.filter(seller_raw_data_id=row_id).only(
            "geocode_lat", "geocode_lng"
        ).first()
        if enr and enr.geocode_lat is not None and enr.geocode_lng is not None:
            return float(enr.geocode_lat), float(enr.geocode_lng)

        candidates = _build_address_candidates(r)
        if not candidates:
            return None

        coords, used_addr = _try_geocoding_candidates(candidates, api_key)
        if coords is None:
            return None

        lat, lng = coords
        when = timezone.now()
        enr_obj, created = LlDataEnrichment.objects.get_or_create(
            seller_raw_data_id=row_id,
            defaults={
                "geocode_lat": lat,
                "geocode_lng": lng,
                "geocode_used_address": used_addr or candidates[0],
                "geocode_full_address": used_addr or candidates[0],
                "geocode_display_address": _build_display_address(r),
                "geocoded_at": when,
            },
        )
        # Ensure asset_hub mirrors the raw row's hub
        if getattr(enr_obj, 'asset_hub_id', None) is None:
            try:
                from acq_module.models.seller import SellerRawData as _SRD
                _raw = _SRD.objects.only('asset_hub_id').get(pk=row_id)
                if getattr(_raw, 'asset_hub_id', None) is not None:
                    enr_obj.asset_hub_id = _raw.asset_hub_id
                    enr_obj.save(update_fields=[
                        'asset_hub',
                    ])
            except Exception:
                pass
        if not created:
            changed = False
            if not enr_obj.geocode_lat or not enr_obj.geocode_lng:
                enr_obj.geocode_lat = lat
                enr_obj.geocode_lng = lng
                changed = True
            if not enr_obj.geocode_used_address:
                enr_obj.geocode_used_address = used_addr or candidates[0]
                changed = True
            if not enr_obj.geocode_full_address:
                enr_obj.geocode_full_address = used_addr or candidates[0]
                changed = True
            if not enr_obj.geocode_display_address:
                enr_obj.geocode_display_address = _build_display_address(r)
                changed = True
            if changed:
                enr_obj.geocoded_at = when
                enr_obj.save(update_fields=[
                    "geocode_lat", "geocode_lng", "geocode_used_address",
                    "geocode_full_address", "geocode_display_address",
                    "geocoded_at",
                ])
        return lat, lng
    except Exception:
        return None
