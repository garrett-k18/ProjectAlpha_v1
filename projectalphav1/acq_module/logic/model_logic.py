"""
acq_module.logic.model_logic

What: Backend logic helpers for ACQ workflows.
Why: Keep reusable model/business logic out of views; import from DRF views and other modules.
Where: projectalphav1/acq_module/logic/model_logic.py
How: Plain functions that query models and shape dictionaries for serializers.
"""

from typing import Dict, Any, List

from django.db.models import Prefetch

from acq_module.models.seller import SellerRawData
from core.models.assumptions import FCTimelines, FCStatus, StateReference


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

    return {"state": state_code, "statuses": results, "totalDurationDays": total}

