"""
Service layer for composing Asset Inventory rows for AG Grid.

Docs reviewed:
- Django QuerySet API: https://docs.djangoproject.com/en/stable/ref/models/querysets/
- DRF Filtering & Pagination: https://www.django-rest-framework.org/api-guide/filtering/

This module isolates data-join logic so views remain thin.
"""
from __future__ import annotations

from typing import Iterable, Optional
from django.db.models import QuerySet, Q
from am_module.models.boarded_data import SellerBoardedData

# Fields used by quick filter 'q'
QUICK_FILTER_FIELDS = (
    "street_address",
    "city",
    "state",
    "zip",
    "seller_name",
    "trade_name",
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
) -> QuerySet[SellerBoardedData]:
    """
    Return a QuerySet of SellerBoardedData with metrics joined.
    - Applies quick filter across common text fields when q is provided
    - Applies simple equality filters from the filters dict
    - Applies ordering when provided (supports -prefix for desc)
    """
    qs = (
        SellerBoardedData.objects
        .select_related("metrics")  # OneToOne relation to AssetMetrics
        .select_related("asset_hub__blended_outcome_model")  # hub-keyed BlendedOutcomeModel
    )

    if q:
        q_obj = Q()
        for f in QUICK_FILTER_FIELDS:
            q_obj |= Q(**{f"{f}__icontains": q})
        # Also try to match numeric sellertape_id if q is digits
        if q.isdigit():
            q_obj |= Q(sellertape_id=int(q))
        qs = qs.filter(q_obj)

    if filters:
        # Shallow equality filters; extend as needed
        allowed = {k: v for k, v in filters.items() if v not in (None, "")}
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
                # Sort by purchase_date as a proxy for hold length
                # Note: this is inversely correlated to hold_days; the client can
                # choose asc/desc to match desired behavior.
                model_field = "metrics__purchase_date"
            else:
                model_field = key  # pass-through for any other field

            order_fields.append(f"-{model_field}" if desc else model_field)

        if order_fields:
            qs = qs.order_by(*order_fields)

    return qs
