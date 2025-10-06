"""
acq_module.logic.model_logic
General logic used for all outcomes...not specific to any one outcome
What: Backend logic helpers for ACQ workflows.
Why: Keep reusable model/business logic out of views; import from DRF views and other modules.
Where: projectalphav1/acq_module/logic/model_logic.py
How: Plain functions that query models and shape dictionaries for serializers.
"""

from decimal import Decimal
from typing import Dict, Any, List, Optional

from django.db.models import Prefetch, Sum

from acq_module.models.seller import SellerRawData
from core.models.assumptions import FCStatus, FCTimelines, StateReference


def get_asset_fc_timeline(asset_id: int) -> Dict[str, Any]:
    """
    Return an asset-scoped foreclosure timeline payload.
    Shape:
    {
        "state": "CA",
        "statuses": [
            {"id": 1, "status": "pre_fc", "statusDisplay": "Pre-Foreclosure", "durationDays": 45},
            ...
        ],
        "totalDurationDays": 123
    }

    Source of truth:
    - Asset state from `acq_module.models.seller.SellerRawData.state` (PK is hub/asset id)
    - Timelines from `core.models.assumptions.FCTimelines` filtered by state
    - Status order/display from `core.models.assumptions.FCStatus`
    - totalDurationDays: sum of non-null duration_days across all statuses
    """

    # Resolve asset state (already normalized upstream by ETL/model layer)
    # SellerRawData has a OneToOneField primary key to core.AssetIdHub via `asset_hub`.
    # Query explicitly by asset_hub_id to avoid any ambiguity with PKs in data imports.
    raw = SellerRawData.objects.filter(asset_hub_id=asset_id).only("state").first()
    if not raw or not raw.state:
        return {"state": None, "statuses": []}
    state_code = raw.state

    # Preload all statuses in defined order for consistent rows
    statuses: List[FCStatus] = list(FCStatus.objects.all().order_by("order", "status"))

    # Build a map of fc_status_id -> duration_days for the given state
    # Use select_related to avoid extra queries
    timelines = (
        FCTimelines.objects.select_related("fc_status", "state")
        .filter(state__state_code=state_code)
    )
    duration_by_status: Dict[int, int] = {t.fc_status_id: t.duration_days for t in timelines}

    results = []
    for s in statuses:
        results.append({
            "id": s.id,
            "status": s.status,
            "statusDisplay": s.get_status_display(),
            "durationDays": duration_by_status.get(s.id),
        })

    # Compute total duration across statuses (sum non-null values). If none present, return None.
    non_null = [d for d in duration_by_status.values() if d is not None]
    total = sum(non_null) if non_null else None

    # Get REO marketing duration from StateReference
    reo_marketing_months = None
    try:
        state_ref = StateReference.objects.filter(state_code=state_code).first()
        if state_ref:
            reo_marketing_months = state_ref.reo_marketing_duration
    except StateReference.DoesNotExist:
        pass

    return {
        "state": state_code,
        "statuses": results,
        "totalDurationDays": total,
        "reoMarketingMonths": reo_marketing_months
    }

def get_state_fc_total_duration_days(state_code: str) -> Optional[int]:
    """Return the sum of `duration_days` across all foreclosure statuses for a state.

    Args:
        state_code: Two-letter state code (e.g., 'CA').

    Returns:
        Integer total of days across statuses, or None if no durations exist for the state.
    """
    # Aggregate over all timeline rows for the given state.
    agg = (
        FCTimelines.objects
        .filter(state__state_code=state_code)
        .aggregate(total=Sum('duration_days'))
    )
    return agg.get('total')


def get_asset_fc_total_duration_days(asset_id: int) -> Optional[int]:
    """Resolve the asset's state from `SellerRawData` and return that state's total duration days.

    Args:
        asset_id: The AssetIdHub primary key.

    Returns:
        Integer total of days across statuses for the asset's state, or None if unknown.
    """
    raw = SellerRawData.objects.filter(asset_hub_id=asset_id).only('state').first()
    if not raw or not raw.state:
        return None
    return get_state_fc_total_duration_days(raw.state)


def get_state_fc_metrics(state_code: str) -> Dict[str, Optional[int]]:
    """Convenience: return both total FC duration (days) and REO marketing (months) for a state.

    Returns a dict with keys: { 'totalDurationDays', 'reoMarketingMonths' }.
    """
    total = get_state_fc_total_duration_days(state_code)
    reo_months = None
    try:
        state_ref = StateReference.objects.filter(state_code=state_code).only('reo_marketing_duration').first()
        if state_ref:
            reo_months = state_ref.reo_marketing_duration
    except StateReference.DoesNotExist:
        pass
    return { 'totalDurationDays': total, 'reoMarketingMonths': reo_months }


def monthly_tax_for_asset(asset_hub_id: int) -> Decimal:
    """Convenience wrapper: compute monthly property tax for an asset ID.

    Pulls `state` and `seller_asis_value` from `SellerRawData` using the given
    AssetIdHub primary key, then delegates to `monthly_tax()`.
    Returns Decimal('0.00') if the asset or required fields are missing.
    """
    raw = SellerRawData.objects.filter(asset_hub_id=asset_hub_id).only('state', 'seller_asis_value').first()
    if not raw or not raw.state or not raw.seller_asis_value:
        return Decimal('0.00')
    state = StateReference.objects.filter(state_code=raw.state).only('property_tax_rate').first()
    if not state or state.property_tax_rate is None:
        return Decimal('0.00')
    base = raw.seller_asis_value if isinstance(raw.seller_asis_value, Decimal) else Decimal(str(raw.seller_asis_value))
    if base <= 0:
        return Decimal('0.00')
    return (base * state.property_tax_rate / Decimal('12')).quantize(Decimal('0.01'))


def monthly_insurance_for_asset(asset_hub_id: int) -> Decimal:
    """Convenience wrapper: compute monthly insurance for an asset ID.

    Pulls `state` and `seller_asis_value` from `SellerRawData` using the given
    AssetIdHub primary key, then delegates to `monthly_insurance()`.
    Returns Decimal('0.00') if the asset or required fields are missing.
    """
    raw = SellerRawData.objects.filter(asset_hub_id=asset_hub_id).only('state', 'seller_asis_value').first()
    if not raw or not raw.state or not raw.seller_asis_value:
        return Decimal('0.00')
    state = StateReference.objects.filter(state_code=raw.state).only('insurance_rate_avg').first()
    if not state or state.insurance_rate_avg is None:
        return Decimal('0.00')
    base = raw.seller_asis_value if isinstance(raw.seller_asis_value, Decimal) else Decimal(str(raw.seller_asis_value))
    if base <= 0:
        return Decimal('0.00')
    return (base * state.insurance_rate_avg / Decimal('12')).quantize(Decimal('0.01'))

