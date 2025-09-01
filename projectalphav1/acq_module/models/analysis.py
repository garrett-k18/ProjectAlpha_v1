#Definition for the modeling

# Centralized analysis utilities for acquisition module.
# These helpers centralize mapping from SellerRawData.state -> StateReference.state_code
# to fetch state-level assumption fields (e.g., fc_state_months) without repeating query logic.

from django.db.models import OuterRef, Subquery
from .seller import SellerRawData
from .assumptions import StateReference

# ---------------------------
# Utility helpers
# ---------------------------
# These helpers centralize the logic of mapping a SellerRawData's `state`
# (e.g., "CA", "TX") to the [StateReference](cci:2://file:///Users/garrettknobf/ProjectAlpha_v1/projectalphav1/acq_module/models/assumptions.py:50:0-92:30) table's `state_code` so we can
# retrieve state-specific fields like `fc_state_months` without duplicating
# query logic across the codebase (views, services, analysis, admin, etc.).
#
# Benefits:
# - Single source of truth for the lookup. If we change how we normalize or
#   join on state, we only change it here.
# - Efficient: implemented with Subquery/annotation for bulk operations.
#
# Quick examples:
#   from projectalphav1.acq_module.models.analysis import (
#       get_fc_state_months_for_seller_qs, get_fc_state_months_for_id
#   )
#   
#   # Batch usage (recommended for many rows):
#   mapping = get_fc_state_months_for_seller_qs(SellerRawData.objects.filter(...))
#   # mapping => {seller_raw_data_id: fc_state_months}
#   
#   # Single-id usage:
#   months = get_fc_state_months_for_id(123)  # -> int or None
# ---------------------------

def get_fc_state_months_for_seller_qs(qs_or_ids):
    """Return a dict mapping SellerRawData.id -> fc_state_months via StateReference.

    Accepts either:
    - a SellerRawData QuerySet (recommended), or
    - an iterable of SellerRawData IDs

    Notes:
    - This matches `SellerRawData.state` to `StateReference.state_code`.
    - If a state's code does not exist in [StateReference](cci:2://file:///Users/garrettknobf/ProjectAlpha_v1/projectalphav1/acq_module/models/assumptions.py:50:0-92:30), the value will be None.
    """
    # Normalize to a queryset of SellerRawData
    if hasattr(qs_or_ids, "model") and qs_or_ids.model is SellerRawData:
        qs = qs_or_ids
    else:
        qs = SellerRawData.objects.filter(id__in=list(qs_or_ids))

    # Annotate each row with the fc_state_months from StateReference
    sr_sub = (
        StateReference.objects
        .filter(state_code=OuterRef("state"))
        .values("fc_state_months")[:1]
    )

    annotated = qs.annotate(fc_state_months=Subquery(sr_sub))

    # Build and return mapping {id: fc_state_months}
    return dict(annotated.values_list("id", "fc_state_months"))


def get_fc_state_months_for_id(seller_raw_data_id):
    """Single-ID convenience wrapper around get_fc_state_months_for_seller_qs.

    Returns the integer fc_state_months for the given SellerRawData id, or None
    if the state is not found in StateReference (or the id does not exist).
    """
    mapping = get_fc_state_months_for_seller_qs([seller_raw_data_id])
    return mapping.get(seller_raw_data_id)