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
import logging
import requests
from typing import Dict, List, Optional, Tuple, Any, Sequence
from decimal import Decimal

from django.db.models import Q
from django.utils import timezone

# App model import: `SellerRawData` contains the address fields we need
from acq_module.models.model_acq_seller import SellerRawData
from core.models import LlDataEnrichment

# ---------------------------------------------------------------------------
# Configuration constants (read from environment with safe defaults)
# ---------------------------------------------------------------------------
# Configuration constants
MAX_UNIQUE_ADDRESSES: int = int(os.getenv("GEOCODE_MAX_ADDRESSES", "500"))


logger = logging.getLogger(__name__)


# Function: _env_api_key – fetch the Geocod.io credential from environment variables.
def _env_api_key() -> Optional[str]:
    """Return the Geocod.io API key from env or None when missing.

    Uses a single canonical env variable per deployment (GEOCODIO_API_KEY).
    """
    return os.getenv("GEOCODIO_API_KEY")


# Function: _normalize_address_for_dedup – produce stable lowercase tokens for deduping.
def _normalize_address_for_dedup(parts: List[str]) -> str:
    """Normalize address for deduplication purposes.
    
    Simple normalization to group similar addresses together
    to minimize API calls for the same location.
    """
    joined = ", ".join(p.strip() for p in parts if p and str(p).strip())
    return " ".join(joined.split()).lower().strip()


# Function: _build_full_address – join city/state/zip for storage/logging.
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


# Function: _build_display_address – compact City, State label for markers.
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


# Function: _build_address_candidates – derive ordered geocode attempts.
def _build_address_candidates(row: Dict[str, Optional[str]]) -> List[str]:
    """Build address candidates for geocoding: City+State only.

    WHAT: Return single candidate (City, State) to minimize API calls.
    WHY: Each API call costs money; no fallback to state-only.
    HOW: If city+state fails, we skip that address (no retry).
    """
    city = str(row.get("city", "") or "").strip()
    state = str(row.get("state", "") or "").strip()

    candidates: List[str] = []

    # WHAT: Build single candidate City, State
    if city and state:
        candidates.append(f"{city}, {state}")

    return candidates


_CLIENTS: Dict[str, Any] = {}


# Function: _geocodio_http_request – make direct HTTP request to Geocodio API.
def _geocodio_http_request(addresses, api_key: str, fields=None):
    """Make direct HTTP request to Geocodio API since Python client is broken."""
    url = "https://api.geocod.io/v1.9/geocode"
    
    if isinstance(addresses, str):
        # Single address
        params = {
            'q': addresses,
            'api_key': api_key
        }
        if fields:
            params['fields'] = ','.join(fields)
        response = requests.get(url, params=params)
    else:
        # Batch addresses
        data = {
            'api_key': api_key
        }
        if fields:
            data['fields'] = ','.join(fields)
        response = requests.post(url, json=addresses, params=data)
    
    response.raise_for_status()
    data = response.json()
    
    # WHAT: Log raw response for debugging
    # WHY: User wants to see all fields coming through
    # HOW: Show response structure and normalize to results format
    logger.info("[Geocodio][HTTP] Response top-level keys: %s", list(data.keys()))
    
    # WHAT: Normalize response format - single requests return different structure
    # WHY: Single geocode returns {query, response} vs batch returns {results: []}
    # HOW: Convert single response to batch format for consistent parsing
    if 'response' in data and 'results' not in data:
        # Single geocode response format
        response_data = data['response']
        if 'results' in response_data:
            data['results'] = response_data['results']
        logger.info("[Geocodio][HTTP] Normalized single response to batch format")
    
    if data.get('results'):
        first_result = data['results'][0]
        logger.info("[Geocodio][HTTP] First result keys: %s", list(first_result.keys()))
        
        # WHAT: Handle nested response structure
        # WHY: Geocodio returns results[0]['response']['results'] for actual geocoding data
        # HOW: Extract the inner response and normalize
        if 'response' in first_result:
            inner_response = first_result['response']
            logger.info("[Geocodio][HTTP] Inner response keys: %s", list(inner_response.keys()))
            
            if 'results' in inner_response and inner_response['results']:
                actual_result = inner_response['results'][0]
                logger.info("[Geocodio][HTTP] Actual result keys: %s", list(actual_result.keys()))
                
                # Replace the outer results with the actual geocoding results
                data['results'] = inner_response['results']
                
                if 'fields' in actual_result:
                    fields = actual_result['fields']
                    logger.info("[Geocodio][HTTP] Available fields: %s", list(fields.keys()))
                    
                    # WHAT: Show ALL field data, not just census
                    # WHY: User wants to see everything coming through
                    # HOW: Log each field's content nicely formatted
                    logger.info("[Geocodio][HTTP] ===== AVAILABLE FIELDS =====")
                    for field_name, field_data in fields.items():
                        if field_data:
                            logger.info("[Geocodio][HTTP] %s:", field_name.upper())
                            logger.info("[Geocodio][HTTP]   %s", str(field_data)[:500])
                            logger.info("[Geocodio][HTTP] " + "-" * 50)
                        else:
                            logger.info("[Geocodio][HTTP] %s: None/Empty", field_name.upper())
                    logger.info("[Geocodio][HTTP] ===== END FIELDS =====")
    
    return data


# Function: _get_attr_or_key – uniform access for dict-like or object responses.
def _get_attr_or_key(obj: Any, key: str) -> Any:
    """Return attribute or dict key value for mixed response objects."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


# Function: _get_nested_value – drill down through nested dict/attr safely.
def _get_nested_value(obj: Any, *keys: str) -> Any:
    """Safely traverse nested attributes/keys from Geocod.io responses."""
    current = obj
    for key in keys:
        current = _get_attr_or_key(current, key)
        if current is None:
            break
    return current


# Function: _extract_msa_fields – pull metro/combined statistical areas from census payload.
def _extract_msa_fields(census_obj: Any) -> Dict[str, Optional[str]]:
    """Extract MSA/CBSA metadata from Geocodio census object.
    
    Handles both metro/micro statistical areas and combined statistical areas
    returned when requesting the `census` field.
    """
    extras: Dict[str, Optional[str]] = {}
    
    if not census_obj:
        return extras
    
    # WHAT: Log the structure of the incoming census object
    # WHY: Need to see if it's year-bucketed or direct payload
    # HOW: Check if it's a dict and show its top-level keys
    if isinstance(census_obj, dict):
        logger.info("[Geocode][MSA] Census object keys: %s", list(census_obj.keys()))
    else:
        logger.info("[Geocode][MSA] Census object type: %s", type(census_obj))

    def _is_year_key(key: Any) -> bool:
        if isinstance(key, int):
            return True
        if isinstance(key, str):
            return key.isdigit()
        return False

    def _select_year_payload(candidate: Any) -> Any:
        """Return the preferred census year payload when responses are bucketed by year."""
        if isinstance(candidate, dict):
            year_keys = [k for k in candidate.keys() if _is_year_key(k)]
            if year_keys:
                preferred_order = ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012", "2011", "2010"]
                for key in preferred_order:
                    if key in candidate:
                        return candidate[key]
                    try:
                        key_int = int(key)
                    except ValueError:
                        continue
                    if key_int in candidate:
                        return candidate[key_int]
                chosen = max(year_keys, key=lambda x: int(x) if isinstance(x, (int, str)) and str(x).isdigit() else -1)
                return candidate[chosen]
        return candidate

    payload = _select_year_payload(census_obj)
    
    # WHAT: Log what payload was selected after year extraction
    # WHY: Verify we correctly extracted the year-specific data
    # HOW: Show payload keys if it's a dict
    payload_year = None
    payload_keys: Optional[List[str]] = None
    if isinstance(payload, dict):
        payload_year = payload.get("census_year") or next(
            (k for k in ("year", "censusYear") if k in payload),
            None,
        )
        try:
            payload_keys = sorted(payload.keys())
        except Exception:
            payload_keys = list(payload.keys())
        logger.info("[Geocode][MSA] Extracted payload for year=%s with keys=%s", payload_year, payload_keys)
    else:
        logger.info("[Geocode][MSA] Payload after year selection is not a dict: %s", type(payload))

    def _as_str(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, (int, float, Decimal)):
            return str(value)
        value = str(value).strip()
        return value or None

    msa_sources = [
        _get_attr_or_key(payload, "metro_micro_statistical_area"),
        _get_attr_or_key(payload, "metropolitan_statistical_area"),
    ]

    msa_obj = next((obj for obj in msa_sources if obj), None)
    if msa_obj:
        msa_name = _as_str(_get_attr_or_key(msa_obj, "name"))
        msa_code = _as_str(
            _get_attr_or_key(msa_obj, "area_code") or _get_attr_or_key(msa_obj, "code")
        )
        if msa_name:
            extras["msa_name"] = msa_name
        if msa_code:
            extras["msa_code"] = msa_code
    else:
        logger.info(
            "[Geocode][MSA] Missing metro/micro area in census payload (year=%s keys=%s)",
            payload_year,
            payload_keys,
        )

    # Capture combined statistical area metadata for future use/debugging
    csa_obj = _get_attr_or_key(payload, "combined_statistical_area")
    if csa_obj:
        extras.setdefault("csa_name", _as_str(_get_attr_or_key(csa_obj, "name")))
        extras.setdefault(
            "csa_code",
            _as_str(_get_attr_or_key(csa_obj, "area_code") or _get_attr_or_key(csa_obj, "code")),
        )

    return {k: v for k, v in extras.items() if v}


# Function: _extract_all_census_fields – extract all requested census fields including MSA/CSA data.
def _extract_all_census_fields(census_obj: Any) -> Dict[str, Optional[str]]:
    """Extract comprehensive census data including MSA, CSA, FIPS codes, and county info."""
    extras: Dict[str, Optional[str]] = {}
    
    if not census_obj:
        return extras

    def _is_year_key(key: Any) -> bool:
        if isinstance(key, int):
            return True
        if isinstance(key, str):
            return key.isdigit()
        return False

    def _select_year_payload(candidate: Any) -> Any:
        """Return the preferred census year payload when responses are bucketed by year."""
        if isinstance(candidate, dict):
            year_keys = [k for k in candidate.keys() if _is_year_key(k)]
            if year_keys:
                preferred_order = ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012", "2011", "2010"]
                for key in preferred_order:
                    if key in candidate:
                        return candidate[key]
                    try:
                        key_int = int(key)
                    except ValueError:
                        continue
                    if key_int in candidate:
                        return candidate[key_int]
                chosen = max(year_keys, key=lambda x: int(x) if isinstance(x, (int, str)) and str(x).isdigit() else -1)
                return candidate[chosen]
        return candidate

    payload = _select_year_payload(census_obj)
    
    if not isinstance(payload, dict):
        return extras

    def _as_str(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, (int, float, Decimal)):
            return str(value)
        value = str(value).strip()
        return value or None

    # ONLY extract MSA/CSA data - NO FIPS codes or other census data
    
    # Extract MSA data
    msa_sources = [
        payload.get("metro_micro_statistical_area"),
        payload.get("metropolitan_statistical_area"),
    ]
    
    msa_obj = next((obj for obj in msa_sources if obj), None)
    if msa_obj and isinstance(msa_obj, dict):
        extras["msa_name"] = _as_str(msa_obj.get("name"))
        extras["msa_code"] = _as_str(msa_obj.get("area_code") or msa_obj.get("code"))
        extras["msa_type"] = _as_str(msa_obj.get("type"))
    
    # Extract CSA data
    csa_obj = payload.get("combined_statistical_area")
    if csa_obj and isinstance(csa_obj, dict):
        extras["csa_name"] = _as_str(csa_obj.get("name"))
        extras["csa_code"] = _as_str(csa_obj.get("area_code") or csa_obj.get("code"))
    
    return {k: v for k, v in extras.items() if v}


# Function: _extract_school_fields – extract school district name from Geocodio school data.
def _extract_school_fields(school_obj: Any) -> Dict[str, Optional[str]]:
    """Extract school district name from Geocodio school field."""
    extras: Dict[str, Optional[str]] = {}
    
    if not school_obj or not isinstance(school_obj, dict):
        return extras
    
    def _as_str(value: Any) -> Optional[str]:
        if value is None:
            return None
        value = str(value).strip()
        return value or None
    
    # School data can have different structures - check for unified, elementary, secondary
    for school_type in ["unified", "elementary", "secondary"]:
        schools = school_obj.get(school_type)
        if schools and isinstance(schools, list) and len(schools) > 0:
            first_school = schools[0]
            if isinstance(first_school, dict):
                school_name = _as_str(first_school.get("name"))
                if school_name:
                    extras["school_district"] = school_name
                    break
    
    return {k: v for k, v in extras.items() if v}


# Function: _extract_primary_geocodio_result – normalize to the first result entry.
def _extract_primary_geocodio_result(container: Any) -> Any:
    """Return the first result object from a Geocodio response container."""
    if container is None:
        return None

    response_obj = _get_attr_or_key(container, "response")
    if response_obj not in (None, container):
        primary = _extract_primary_geocodio_result(response_obj)
        if primary is not None:
            return primary

    results = _get_attr_or_key(container, "results")
    if isinstance(results, list) and results:
        return results[0]

    return container


# Function: _coerce_lat_lng – convert coords into float tuple regardless of structure.
def _coerce_lat_lng(obj: Any) -> Tuple[Optional[float], Optional[float]]:
    """Extract latitude/longitude from various Geocodio response shapes."""
    if obj is None:
        return None, None

    if isinstance(obj, (list, tuple)) and len(obj) >= 2:
        return obj[0], obj[1]

    lat = _get_attr_or_key(obj, "lat")
    lng = _get_attr_or_key(obj, "lng")

    if lat is None:
        lat = _get_attr_or_key(obj, "latitude")
    if lng is None:
        lng = _get_attr_or_key(obj, "longitude")

    return lat, lng


# Function: _parse_geocodio_result_entry – turn a Geocodio entry into coords + extras.
def _parse_geocodio_result_entry(entry: Any) -> Tuple[Optional[Tuple[float, float]], Dict[str, Optional[str]]]:
    extras: Dict[str, Optional[str]] = {}
    if entry is None:
        return None, extras

    lat, lng = _coerce_lat_lng(_get_attr_or_key(entry, "coords"))
    if lat is None or lng is None:
        lat, lng = _coerce_lat_lng(_get_attr_or_key(entry, "location"))

    if lat is None or lng is None:
        return None, extras

    fields_obj = _get_attr_or_key(entry, "fields")
    
    # WHAT: Log raw fields for debugging
    # WHY: Need to see exactly what Geocodio returns to fix MSA extraction
    # HOW: Dump fields object keys when present
    if fields_obj:
        if isinstance(fields_obj, dict):
            logger.info("[Geocode][Fields] Available field keys: %s", list(fields_obj.keys()))
        else:
            logger.info("[Geocode][Fields] Fields object type: %s", type(fields_obj))
    
    # WHAT: Try census2024, census, census2010 fields from HTTP JSON response
    # WHY: Direct HTTP API returns dict with census data
    # HOW: Use dict access to get census data
    census_obj = None
    if fields_obj and isinstance(fields_obj, dict):
        for field_name in ("census2024", "census", "census2010"):
            census_obj = fields_obj.get(field_name)
            logger.info("[Geocode][Census] Checking %s field: %s", field_name, type(census_obj) if census_obj else None)
            if census_obj:
                logger.info("[Geocode][Census] Using %s field", field_name)
                break
    
    if census_obj:
        logger.info("[Geocode][Census] Raw census data: %s", str(census_obj)[:500])
        extras.update(_extract_all_census_fields(census_obj))
    else:
        logger.warning("[Geocode][Census] No census data found in fields object")
    
    # WHAT: Extract school district data
    # WHY: User wants school district name
    # HOW: Parse school field from Geocodio response
    school_obj = fields_obj.get('school') if fields_obj and isinstance(fields_obj, dict) else None
    if school_obj:
        logger.info("[Geocode][School] Raw school data: %s", str(school_obj)[:300])
        extras.update(_extract_school_fields(school_obj))
    else:
        logger.info("[Geocode][School] No school data found")
    
    # WHAT: Log all extracted data for debugging
    # WHY: User wants to see what fields are actually coming through
    # HOW: Show coordinates and all extras
    logger.info("[Geocode][Result] Coordinates: lat=%s, lng=%s", lat, lng)
    logger.info("[Geocode][Result] All extracted fields: %s", extras)

    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except (TypeError, ValueError):
        return None, extras

    return (lat_f, lng_f), extras


# Function: _persist_enrichment_rows – upsert LlDataEnrichment rows for shared addresses.
def _persist_enrichment_rows(
    rows_info: List[Dict[str, Any]],
    coords: Tuple[float, float],
    extras: Dict[str, Optional[str]],
    used_address: Optional[str],
) -> int:
    """Persist geocode results for a set of SellerRawData rows."""
    if not rows_info or coords is None:
        return 0

    lat, lng = coords
    when = timezone.now()
    msa_name = extras.get("msa_name")
    msa_code = extras.get("msa_code")
    updated_rows = 0
    
    # WHAT: Log what we're about to persist
    # WHY: User wants to see what's being processed to avoid wasting API calls
    # HOW: Show coordinates and MSA data (or lack thereof)
    logger.info("[Persist] Coordinates: lat=%s, lng=%s, MSA: %s (%s), Address: %s", 
                lat, lng, msa_name or "None", msa_code or "None", used_address or "Unknown")

    for row_meta in rows_info:
        row_id = row_meta.get("id")
        if not row_id:
            continue

        candidates = row_meta.get("candidates") or []
        fallback_addr = used_address or row_meta.get("used_address") or (candidates[0] if candidates else None)
        display_name = row_meta.get("display_name") or fallback_addr or ""

        defaults = {
            "geocode_lat": lat,
            "geocode_lng": lng,
            "geocode_used_address": fallback_addr or "",
            "geocode_full_address": fallback_addr or "",
            "geocode_display_address": display_name,
            "geocoded_at": when,
            "geocode_msa": msa_name or "",  # Store empty string instead of None
            "geocode_msa_code": msa_code or "",  # Store empty string instead of None
        }
        
        # WHAT: Log what we're saving for this specific row
        # WHY: User wants detailed tracking of what gets persisted
        # HOW: Show row ID and whether it has MSA data
        logger.info("[Persist] Row %s: %s -> MSA: %s", row_id, fallback_addr or "No address", 
                    msa_name or "NO MSA DATA")

        try:
            # WHAT: Use asset_hub_id as the primary key since seller_raw_data was removed
            # WHY: LlDataEnrichment now only has OneToOneField to AssetIdHub
            # HOW: Direct relationship to asset_hub_id
            enr_obj, created = LlDataEnrichment.objects.get_or_create(
                asset_hub_id=row_id,
                defaults=defaults,
            )
            logger.info("[Persist] Row %s: %s (created=%s)", row_id, "SUCCESS", created)
        except Exception as e:
            logger.error("[Persist] Row %s: FAILED - %s (address: %s)", row_id, str(e), fallback_addr or "Unknown")
            continue

        if getattr(enr_obj, 'asset_hub_id', None) is None:
            try:
                _raw = SellerRawData.objects.only('asset_hub_id').get(pk=row_id)
                if getattr(_raw, 'asset_hub_id', None) is not None:
                    enr_obj.asset_hub_id = _raw.asset_hub_id
                    enr_obj.save(update_fields=['asset_hub'])
            except Exception:
                pass

        if not created:
            changed = False
            if not enr_obj.geocode_lat or not enr_obj.geocode_lng:
                enr_obj.geocode_lat = lat
                enr_obj.geocode_lng = lng
                changed = True
            if not enr_obj.geocode_used_address and fallback_addr:
                enr_obj.geocode_used_address = fallback_addr
                changed = True
            if not enr_obj.geocode_full_address and fallback_addr:
                enr_obj.geocode_full_address = fallback_addr
                changed = True
            if not enr_obj.geocode_display_address and display_name:
                enr_obj.geocode_display_address = display_name
                changed = True
            # WHAT: Always update MSA fields, even if empty
            # WHY: User wants to track which addresses were processed but have no MSA
            # HOW: Store empty string to indicate "processed but no MSA data"
            if not enr_obj.geocode_msa or (msa_name and enr_obj.geocode_msa != msa_name):
                enr_obj.geocode_msa = msa_name or ""
                changed = True
            if not getattr(enr_obj, "geocode_msa_code", None) or (msa_code and getattr(enr_obj, "geocode_msa_code", None) != msa_code):
                enr_obj.geocode_msa_code = msa_code or ""
                changed = True
            if changed:
                enr_obj.geocoded_at = when
                enr_obj.save(update_fields=[
                    "geocode_lat",
                    "geocode_lng",
                    "geocode_used_address",
                    "geocode_full_address",
                    "geocode_display_address",
                    "geocode_msa",
                    "geocode_msa_code",
                    "geocoded_at",
                ])

        updated_rows += 1

    return updated_rows


# Function: _geocode_geocodio – single-address call to official client with census append.
def _geocode_geocodio(
    address: str,
    api_key: str,
    *,
    fields: Optional[Sequence[str]] = None,
) -> Tuple[Optional[Tuple[float, float]], Dict[str, Optional[str]]]:
    """Call Geocod.io API using official geocodio-library-python.
    
    DOCS: https://github.com/Geocodio/geocodio-library-python
    """
    extras: Dict[str, Optional[str]] = {}
    
    try:
        # WHAT: Call Geocodio HTTP API directly since Python client is broken
        # WHY: Python client doesn't expose census data properly
        # HOW: Use direct HTTP request and parse JSON response
        response_data = _geocodio_http_request(address, api_key, fields or [
            'census2024', 'census', 'census2010'
        ])
        
        if not response_data.get('results'):
            return None, extras
        
        first = response_data['results'][0]
        coords, extras = _parse_geocodio_result_entry(first)
        
        return coords, extras
        
    except Exception as e:
        print(f"[GEOCODIO_ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None, extras


# Function: _call_geocoding_api – thin wrapper to keep signature consistent.
def _call_geocoding_api(
    address: str,
    api_key: str,
    *,
    fields: Optional[Sequence[str]] = None,
) -> Tuple[Optional[Tuple[float, float]], Dict[str, Optional[str]]]:
    """Call Geocod.io API directly for an address."""
    return _geocode_geocodio(address, api_key, fields=fields)


# Function: _try_geocoding_candidates – iterate candidate strings until success.
def _try_geocoding_candidates(
    address_candidates: List[str],
    api_key: str,
    *,
    fields: Optional[Sequence[str]] = None,
) -> Tuple[Optional[Tuple[float, float]], Optional[str], Dict[str, Optional[str]]]:
    """Try multiple address candidates with API calls.

    Args:
        address_candidates: list produced by `_build_address_candidates()`
        api_key: Geocod.io API key

    Returns:
        (coords, used_address, extras)
            - coords: (lat, lng) or None
            - used_address: the address string that produced coords, or None
    """
    for addr in address_candidates:
        coords, extras = _call_geocoding_api(addr, api_key, fields=fields)
        if coords is not None:
            return coords, addr, extras
    return None, None, {}


# Function: _batch_geocode_geocodio – perform Geocodio batch lookup and map responses.
def _batch_geocode_geocodio(
    addresses: Sequence[str],
    api_key: str,
    *,
    fields: Optional[Sequence[str]] = None,
) -> Dict[str, Tuple[Tuple[float, float], Dict[str, Optional[str]], str]]:
    """Batch geocode a list of addresses using the official client."""
    resolved: Dict[str, Tuple[Tuple[float, float], Dict[str, Optional[str]], str]] = {}
    if not addresses:
        return resolved

    try:
        response_data = _geocodio_http_request(list(addresses), api_key, fields or [
            'census2024', 'census', 'census2010'
        ])
        raw_results = response_data.get('results', [])

        for idx, addr in enumerate(addresses):
            entry = raw_results[idx] if idx < len(raw_results) else None
            coords, extras = _parse_geocodio_result_entry(entry)
            if coords:
                norm = _normalize_address_for_dedup([addr])
                resolved[norm] = (coords, extras, addr)

    except Exception as exc:
        print(f"[GEOCODIO_BATCH_ERROR] {exc}")
        import traceback
        traceback.print_exc()

    return resolved


# Function: batch_geocode_row_ids – persist coordinates/MSA data for specific assets.
def batch_geocode_row_ids(
    row_ids: Sequence[int],
    *,
    chunk_size: int = 1000,
    fields: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Batch geocode SellerRawData rows by primary key."""
    stats = {
        "requested_rows": len(row_ids or []),
        "unique_addresses": 0,
        "updated_rows": 0,
        "api_calls": 0,
        "raw_responses": [],  # Store raw responses for CSV export
    }

    if not row_ids:
        return stats

    api_key = _env_api_key()
    if not api_key:
        stats["error"] = "GEOCODIO_API_KEY missing on server"
        return stats

    clean_ids = [rid for rid in row_ids if rid]
    rows = list(
        SellerRawData.objects.filter(pk__in=clean_ids)
        .values("pk", "asset_hub_id", "city", "state", "zip")
    )

    addr_to_rows: Dict[str, List[Dict[str, Any]]] = {}
    unique_addresses: List[Tuple[str, str]] = []

    for row in rows:
        candidates = _build_address_candidates(row)
        if not candidates:
            continue
        primary = candidates[0]
        norm = _normalize_address_for_dedup([primary])
        if not norm:
            continue
        if norm not in addr_to_rows:
            addr_to_rows[norm] = []
            unique_addresses.append((norm, primary))
        addr_to_rows[norm].append({
            "id": row["asset_hub_id"],  # Use asset_hub_id for persistence
            "candidates": candidates,
            "display_name": _build_display_address(row),
        })

    stats["unique_addresses"] = len(unique_addresses)
    logger.info("[Batch] Found %d unique addresses from %d rows", len(unique_addresses), len(rows))
    for i, (norm, addr) in enumerate(unique_addresses[:5]):  # Log first 5
        logger.info("[Batch] Address %d: %s -> %s", i+1, addr, norm)
    
    if not unique_addresses:
        logger.warning("[Batch] No unique addresses found!")
        return stats

    effective_chunk = max(1, min(chunk_size, 1000))
    for i in range(0, len(unique_addresses), effective_chunk):
        chunk_pairs = unique_addresses[i:i + effective_chunk]
        payload = [addr for _norm, addr in chunk_pairs]
        chunk_results = _batch_geocode_geocodio(payload, api_key, fields=fields)
        stats["api_calls"] += 1

        for norm, addr in chunk_pairs:
            # WHAT: Use the original norm key that was used to create the batch
            # WHY: Re-normalizing creates different key and causes lookup failures
            # HOW: Use the norm from chunk_pairs directly
            result = chunk_results.get(norm)
            if not result:
                continue
            coords, extras, used_addr = result
            
            # WHAT: Capture raw response data for CSV export
            # WHY: User wants to save all responses to avoid wasting API calls
            # HOW: Store all extracted data plus raw response
            rows_for_addr = addr_to_rows.get(norm, [])
            for row_info in rows_for_addr:
                asset_hub_id = row_info.get("id")
                raw_response_data = {
                    'asset_hub_id': asset_hub_id,
                    'address': used_addr,
                    'lat': coords[0] if coords else '',
                    'lng': coords[1] if coords else '',
                    'msa_name': extras.get('msa_name', ''),
                    'msa_code': extras.get('msa_code', ''),
                    'csa_name': extras.get('csa_name', ''),
                    'csa_code': extras.get('csa_code', '')
                }
                stats["raw_responses"].append(raw_response_data)
            
            updated = _persist_enrichment_rows(
                rows_for_addr,
                coords,
                extras,
                used_addr,
            )
            stats["updated_rows"] += updated

    return stats


# Function: preview_msa_for_row_ids – fetch MSA/CSA preview data without DB writes.
def preview_msa_for_row_ids(
    row_ids: Sequence[int],
    *,
    chunk_size: int = 1000,
    fields: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Fetch Geocodio MSA data for SellerRawData rows without persisting."""
    stats = {
        "requested_rows": len(row_ids or []),
        "unique_addresses": 0,
        "api_calls": 0,
        "results": [],
    }

    if not row_ids:
        return stats

    api_key = _env_api_key()
    if not api_key:
        stats["error"] = "GEOCODIO_API_KEY missing on server"
        return stats

    clean_ids = [rid for rid in row_ids if rid]
    rows = list(
        SellerRawData.objects.filter(pk__in=clean_ids)
        .values("pk", "asset_hub_id", "city", "state", "zip")
    )

    addr_to_rows: Dict[str, List[Dict[str, Any]]] = {}
    unique_addresses: List[Tuple[str, str]] = []

    for row in rows:
        candidates = _build_address_candidates(row)
        if not candidates:
            continue
        primary = candidates[0]
        norm = _normalize_address_for_dedup([primary])
        if not norm:
            continue
        if norm not in addr_to_rows:
            addr_to_rows[norm] = []
            unique_addresses.append((norm, primary))
        addr_to_rows[norm].append({
            "id": row["asset_hub_id"],  # Use asset_hub_id for persistence
            "candidates": candidates,
            "display_name": _build_display_address(row),
        })

    stats["unique_addresses"] = len(unique_addresses)
    if not unique_addresses:
        return stats

    previews: List[Dict[str, Any]] = []
    effective_chunk = max(1, min(chunk_size, 1000))
    for i in range(0, len(unique_addresses), effective_chunk):
        chunk_pairs = unique_addresses[i:i + effective_chunk]
        payload = [addr for _norm, addr in chunk_pairs]
        chunk_results = _batch_geocode_geocodio(payload, api_key, fields=fields)
        stats["api_calls"] += 1

        for norm, addr in chunk_pairs:
            norm_key = _normalize_address_for_dedup([addr])
            result = chunk_results.get(norm_key)
            if not result:
                continue
            coords, extras, used_addr = result
            for row_meta in addr_to_rows.get(norm, []):
                previews.append({
                    "seller_raw_data_id": row_meta["id"],
                    "address": used_addr or row_meta["candidates"][0],
                    "lat": coords[0] if coords else None,
                    "lng": coords[1] if coords else None,
                    "msa_name": extras.get("msa_name"),
                    "msa_code": extras.get("msa_code"),
                    "csa_name": extras.get("csa_name"),
                    "csa_code": extras.get("csa_code"),
                })

    stats["results"] = previews
    return stats


# Function: preview_msa_for_addresses – fetch MSA data for raw address strings (no DB lookup).
def preview_msa_for_addresses(
    addresses: Sequence[str],
    *,
    chunk_size: int = 1000,
    fields: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Fetch Geocodio MSA/CSA metadata for arbitrary address strings."""
    stats = {
        "requested_addresses": len(addresses or []),
        "unique_addresses": 0,
        "api_calls": 0,
        "results": [],
    }

    if not addresses:
        return stats

    api_key = _env_api_key()
    if not api_key:
        stats["error"] = "GEOCODIO_API_KEY missing on server"
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

    previews: List[Dict[str, Any]] = []
    effective_chunk = max(1, min(chunk_size, 1000))
    for i in range(0, len(unique_pairs), effective_chunk):
        chunk_pairs = unique_pairs[i:i + effective_chunk]
        payload = [addr for _norm, addr in chunk_pairs]
        chunk_results = _batch_geocode_geocodio(payload, api_key, fields=fields)
        stats["api_calls"] += 1

        for norm, addr in chunk_pairs:
            result = chunk_results.get(norm)
            if not result:
                previews.append({
                    "address": addr,
                    "lat": None,
                    "lng": None,
                    "msa_name": None,
                    "msa_code": None,
                    "csa_name": None,
                    "csa_code": None,
                })
                continue
            coords, extras, used_addr = result
            previews.append({
                "address": used_addr or addr,
                "lat": coords[0] if coords else None,
                "lng": coords[1] if coords else None,
                "msa_name": extras.get("msa_name"),
                "msa_code": extras.get("msa_code"),
                "csa_name": extras.get("csa_name"),
                "csa_code": extras.get("csa_code"),
            })

    stats["results"] = previews
    return stats


# Function: geocode_markers_for_seller_trade – drive seller/trade map marker enrichment.
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
    import logging
    import time
    logger = logging.getLogger(__name__)
    
    start_time = time.time()
    print(f'[GEOCODE SERVICE] Starting for seller={seller_id}, trade={trade_id}')
    
    api_key = _env_api_key()
    if not api_key:
        return {
            "markers": [],
            "count": 0,
            "source": "none",
            "error": "GEOCODIO_API_KEY missing on server",
        }

    # Query only the fields needed to compose addresses and labels for markers
    query_start = time.time()
    rows = list(
        SellerRawData.objects
        .filter(Q(seller_id=seller_id) & Q(trade_id=trade_id))
        .values("pk", "asset_hub_id", "city", "state", "zip")
    )
    query_time = time.time() - query_start
    print(f'[GEOCODE SERVICE] Found {len(rows)} rows in {query_time:.2f}s')

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

    # WHAT: Process all unique addresses
    unique_addrs = list(addr_to_rows.keys())
    
    dedup_time = time.time() - query_start
    print(f'[GEOCODE SERVICE] Deduplicated to {len(unique_addrs)} unique addresses in {dedup_time:.2f}s')

    # WHAT: Bulk-fetch ALL enrichment records for this seller/trade to avoid N+1 queries
    # WHY: Querying in a loop causes 658+ individual queries (extremely slow)
    # HOW: Single query with filter, build lookup dict by seller_raw_data_id
    all_asset_ids = [r["id"] for row_list in addr_to_rows.values() for r in row_list]
    enrichment_prefetch_start = time.time()
    print(f'[GEOCODE SERVICE] Prefetching enrichments for {len(all_asset_ids)} asset IDs')
    
    try:
        enrichments = LlDataEnrichment.objects.filter(
            seller_raw_data_id__in=all_asset_ids
        ).only("seller_raw_data_id", "geocode_lat", "geocode_lng", "geocode_used_address")
        
        # Build lookup dict: seller_raw_data_id -> enrichment object
        enrichment_lookup = {e.seller_raw_data_id: e for e in enrichments}
        enrichment_prefetch_time = time.time() - enrichment_prefetch_start
        print(f'[GEOCODE SERVICE] Prefetched {len(enrichment_lookup)} enrichment records in {enrichment_prefetch_time:.2f}s')
    except Exception as e:
        print(f'[GEOCODE SERVICE ERROR] Failed to prefetch enrichments: {e}')
        import traceback
        traceback.print_exc()
        # Fallback to empty lookup (will trigger API calls if needed)
        enrichment_lookup = {}

    markers: List[Dict[str, Any]] = []
    any_api_calls = False
    
    enrichment_start = time.time()
    for norm in unique_addrs:
        # Use the first representative row for label/name; multiple ids may share address
        representative = addr_to_rows[norm][0]
        candidates = representative["candidates"]
        # 1) Prefer DB-persisted geocode if present on any row for this address
        persisted = None
        used_addr = None
        extras: Dict[str, Optional[str]] = {}
        for r in addr_to_rows[norm]:
            # Use lookup dict instead of database query
            enr = enrichment_lookup.get(r["id"])
            if enr and enr.geocode_lat is not None and enr.geocode_lng is not None:
                try:
                    persisted = (float(enr.geocode_lat), float(enr.geocode_lng))
                    used_addr = enr.geocode_used_address or None
                    extras = {
                        "msa_name": getattr(enr, "geocode_msa", None),
                        "msa_code": getattr(enr, "geocode_msa_code", None),
                    }
                    break
                except Exception:
                    persisted = None

        # WHAT: Always call API to get MSA fields (census data).
        # WHY: MSA enrichment is critical; don't skip API just because coords exist.
        # HOW: Call API fresh for every address to extract msa_name and msa_code.
        coords, used_addr, extras = _try_geocoding_candidates(candidates, api_key)
        source = "api" if coords else "none"

        # If we obtained coordinates, upsert for all rows sharing this address
        if coords is not None:
                lat, lng = coords
                when = timezone.now()
                msa_name = extras.get("msa_name")
                msa_code = extras.get("msa_code")
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
                            "geocode_msa": msa_name,
                            "geocode_msa_code": msa_code,
                        },
                    )
                    # Ensure asset_hub mirrors the raw row's hub
                    if getattr(enr_obj, 'asset_hub_id', None) is None:
                        try:
                            from acq_module.models.model_acq_seller import SellerRawData as _SRD
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
                        if msa_name and not enr_obj.geocode_msa:
                            enr_obj.geocode_msa = msa_name
                            changed = True
                        if msa_code and not getattr(enr_obj, "geocode_msa_code", None):
                            enr_obj.geocode_msa_code = msa_code
                            changed = True
                        if changed:
                            enr_obj.geocoded_at = when
                            enr_obj.save(update_fields=[
                                "geocode_lat", "geocode_lng", "geocode_used_address",
                                "geocode_full_address", "geocode_display_address",
                                "geocode_msa", "geocode_msa_code",
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
    
    enrichment_time = time.time() - enrichment_start
    total_time = time.time() - start_time
    print(f'[GEOCODE SERVICE] Enrichment loop: {enrichment_time:.2f}s')
    print(f'[GEOCODE SERVICE] TOTAL TIME: {total_time:.2f}s for {len(markers)} markers')

    return {
        "markers": markers,
        "count": len(markers),
        "source": source,
    }


# Function: geocode_row – single-row enrichment used by signals/import hooks.
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
             .values("pk", "asset_hub_id", "city", "state", "zip")
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

        coords, used_addr, extras = _try_geocoding_candidates(candidates, api_key)
        if coords is None:
            return None

        lat, lng = coords
        when = timezone.now()
        msa_name = extras.get("msa_name")
        msa_code = extras.get("msa_code")
        enr_obj, created = LlDataEnrichment.objects.get_or_create(
            seller_raw_data_id=row_id,
            defaults={
                "geocode_lat": lat,
                "geocode_lng": lng,
                "geocode_used_address": used_addr or candidates[0],
                "geocode_full_address": used_addr or candidates[0],
                "geocode_display_address": _build_display_address(r),
                "geocoded_at": when,
                "geocode_msa": msa_name,
                "geocode_msa_code": msa_code,
            },
        )
        # Ensure asset_hub mirrors the raw row's hub
        if getattr(enr_obj, 'asset_hub_id', None) is None:
            try:
                from acq_module.models.model_acq_seller import SellerRawData as _SRD
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
            if msa_name and not enr_obj.geocode_msa:
                enr_obj.geocode_msa = msa_name
                changed = True
            if msa_code and not getattr(enr_obj, "geocode_msa_code", None):
                enr_obj.geocode_msa_code = msa_code
                changed = True
            if changed:
                enr_obj.geocoded_at = when
                enr_obj.save(update_fields=[
                    "geocode_lat", "geocode_lng", "geocode_used_address",
                    "geocode_full_address", "geocode_display_address",
                    "geocode_msa", "geocode_msa_code",
                    "geocoded_at",
                ])
        return lat, lng
    except Exception:
        return None
