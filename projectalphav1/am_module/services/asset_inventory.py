"""
Service layer for composing Asset Inventory rows for AG Grid.

Docs reviewed:
- Django QuerySet API: https://docs.djangoproject.com/en/stable/ref/models/querysets/
- DRF Filtering & Pagination: https://www.django-rest-framework.org/api-guide/filtering/

This module isolates data-join logic so views remain thin.
"""
from __future__ import annotations

from typing import Iterable, Optional
from django.db.models import QuerySet, Q, F
from acq_module.models.seller import SellerRawData  # WHAT: Post-refactor boarded dataset source per docs (https://docs.djangoproject.com/en/stable/topics/db/models/)

# Fields used by quick filter 'q'
QUICK_FILTER_FIELDS = (
    "street_address",
    "city",
    "state",
    "zip",
    "seller__name",  # WHAT: Map friendly seller_name search to SellerRawData->Seller join
    "trade__trade_name",  # WHAT: Surfaced trade name via ForeignKey per Django join docs
)

# NOTE on ordering:
"""
Frontend may request ordering on any visible column. We expose a permissive
ordering strategy that passes unknown fields through directly to Django ORM so
long as they exist on the base model or related joins. We only translate a
couple of user-friendly aliases to actual DB fields.

Special cases:
- asset_id -> sellertape_id (friendly alias)
- hold_days -> metrics__purchase_date (proxy; monotonic inverse)
"""


def build_queryset(
    *,
    q: Optional[str] = None,
    filters: Optional[dict] = None,
    ordering: Optional[str] = None,
) -> QuerySet[SellerRawData]:
    """
    Return a QuerySet of SellerBoardedData with metrics joined via AssetIdHub.
    - Applies quick filter across common text fields when q is provided
    - Applies simple equality filters from the filters dict
    - Applies ordering when provided (supports -prefix for desc)
    """
    qs = (
        SellerRawData.objects
        .filter(acq_status=SellerRawData.AcquisitionStatus.BOARD)  # WHAT: Limit to assets promoted into AM module
        .select_related("asset_hub")
        .select_related("asset_hub__blended_outcome_model")
        .select_related("seller", "trade")  # HOW: ensure seller/trade names resolve without extra queries
        .annotate(
            seller_name=F("seller__name"),  # WHAT: Expose friendly name aliases to match legacy serializer fields
            trade_name=F("trade__trade_name"),
        )
    )

    if q:
        q_obj = Q()
        for f in QUICK_FILTER_FIELDS:
            q_obj |= Q(**{f"{f}__icontains": q})
        # Also try to match numeric sellertape_id if q is digits per legacy UX contract
        if q.isdigit():
            q_obj |= Q(sellertape_id__icontains=q)
        qs = qs.filter(q_obj)

    if filters:
        # Shallow equality filters; extend as needed
        allowed = {}
        for key, value in filters.items():
            if value in (None, ""):
                continue
            if key == "seller_name":
                allowed["seller__name"] = value
            elif key == "trade_name":
                allowed["trade__trade_name"] = value
            elif key == "lifecycle_status":
                allowed["asset_hub__asset_status"] = value
            else:
                allowed[key] = value
        if allowed:
            qs = qs.filter(**allowed)

    if ordering:
        # Support multiple comma-separated fields
        order_fields: list[str] = []
        for part in str(ordering).split(","):
            part = part.strip()
            if not part:
                continue
            desc = part.startswith("-")
            key = part[1:] if desc else part

            # Translate friendly aliases to actual ORM paths
            if key == "asset_id":
                model_field = "sellertape_id"
            elif key == "hold_days":
                # Fallback to hub created_at when legacy metrics table is unavailable
                model_field = "asset_hub__created_at"
            else:
                model_field = key  # pass-through for any other field

            order_fields.append(f"-{model_field}" if desc else model_field)

        if order_fields:
            qs = qs.order_by(*order_fields)

    return qs
