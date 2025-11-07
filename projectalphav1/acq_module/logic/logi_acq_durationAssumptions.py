"""
acq_module.logic.logi_acq_durationAssumptions
General logic used for all outcomes...not specific to any one outcome
What: Backend logic helpers for ACQ workflows.
Why: Keep reusable model/business logic out of views; import from DRF views and other modules.
Where: projectalphav1/acq_module/logic/logi_acq_durationAssumptions.py
How: Plain functions that query models and shape dictionaries for serializers.
"""

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.db.models import Prefetch, Sum

from acq_module.models.model_acq_seller import SellerRawData
from core.models.model_co_assumptions import FCStatus, FCTimelines, StateReference
from .logi_acq_expenseAssumptions import (
    monthly_insurance_for_asset,
    monthly_tax_for_asset,
)

# Logger for foreclosure timeline calculations
logger = logging.getLogger(__name__)


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
    - Timelines from `core.models.model_co_assumptions.FCTimelines` filtered by state
    - Status order/display from `core.models.model_co_assumptions.FCStatus`
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

    # Compute total duration across statuses (sum non-null values). If none present, fallback to StateReference.
    non_null = [d for d in duration_by_status.values() if d is not None]
    total = sum(non_null) if non_null else None

    # WHAT: Get StateReference for REO marketing AND foreclosure fallback
    # WHY: If FCTimelines not configured for this state, use StateReference.fc_state_months as default
    # HOW: Query StateReference by state_code and use fc_state_months converted to days
    reo_marketing_months = None
    try:
        state_ref = StateReference.objects.filter(state_code=state_code).first()
        if state_ref:
            reo_marketing_months = state_ref.reo_marketing_duration
            
            # WHAT: If FCTimelines has no data (total is None), fallback to StateReference
            # WHY: Newly imported assets don't have FCTimelines configured yet
            # HOW: Use fc_state_months from StateReference, convert to days (months * 30.44)
            if total is None and state_ref.fc_state_months:
                total = round(state_ref.fc_state_months * 30.44)  # Convert months to days
                logger.info(
                    f'[FC TIMELINE] No FCTimelines for state {state_code}, '
                    f'using StateReference default: {state_ref.fc_state_months} months ({total} days)'
                )
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
        state_ref = (
            StateReference.objects
            .filter(state_code=state_code)
            .only('reo_marketing_duration')
            .first()
        )
        if state_ref:
            reo_months = state_ref.reo_marketing_duration
    except StateReference.DoesNotExist:
        pass
    return {'totalDurationDays': total, 'reoMarketingMonths': reo_months}

