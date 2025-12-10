from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from .serv_co_geocoding import _env_api_key, _geocodio_http_request, _normalize_address_for_dedup


_DEFAULT_CENSUS_FIELDS: Tuple[str, ...] = (
    "census2024",
    "census",
    "census2010",
)


def census_for_addresses(
    addresses: Sequence[str],
    *,
    fields: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    stats: Dict[str, Any] = {
        "requested_addresses": len(addresses or []),
        "unique_addresses": 0,
        "results": [],
    }
    if not addresses:
        return stats

    api_key = _env_api_key()
    if not api_key:
        stats["error"] = "GEOCODIO_API_KEY missing on server"
        return stats

    effective_fields: List[str]
    if fields is not None:
        effective_fields = [f for f in fields if f]
    else:
        effective_fields = list(_DEFAULT_CENSUS_FIELDS)

    if not effective_fields:
        stats["error"] = "No census fields specified"
        return stats

    unique_pairs: List[Tuple[str, str]] = []
    seen: set[str] = set()
    for addr in addresses:
        if not addr:
            continue
        norm = _normalize_address_for_dedup([addr])
        if not norm or norm in seen:
            continue
        seen.add(norm)
        unique_pairs.append((norm, addr))

    stats["unique_addresses"] = len(unique_pairs)
    if not unique_pairs:
        return stats

    results: List[Dict[str, Any]] = []
    for _norm, addr in unique_pairs:
        data = _geocodio_http_request(addr, api_key, fields=effective_fields)
        raw_results = data.get("results") or []
        if not raw_results:
            results.append(
                {
                    "address": addr,
                    "lat": None,
                    "lng": None,
                    "fields": None,
                }
            )
            continue

        entry: Any = raw_results[0]
        if isinstance(entry, dict) and "response" in entry:
            response_obj = entry.get("response") or {}
            inner_results = response_obj.get("results") or []
            if inner_results:
                entry = inner_results[0]

        lat: Optional[float] = None
        lng: Optional[float] = None
        fields_obj: Any = None

        if isinstance(entry, dict):
            coords_obj = entry.get("coords") or entry.get("location") or {}
            if isinstance(coords_obj, dict):
                lat_val = coords_obj.get("lat") or coords_obj.get("latitude")
                lng_val = coords_obj.get("lng") or coords_obj.get("longitude")
            else:
                lat_val = None
                lng_val = None

            try:
                lat = float(lat_val) if lat_val is not None else None
            except (TypeError, ValueError):
                lat = None
            try:
                lng = float(lng_val) if lng_val is not None else None
            except (TypeError, ValueError):
                lng = None

            fields_obj = entry.get("fields")

        results.append(
            {
                "address": addr,
                "lat": lat,
                "lng": lng,
                "fields": fields_obj,
            }
        )

    stats["results"] = results
    return stats
