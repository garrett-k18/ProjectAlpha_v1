"""
State Summary helpers for SellerRawData.

Purpose:
- Provide small, single-purpose helpers to compute state-based summaries.
- No normalization here; state normalization is done in SellerRawData.save().

Docs (Django ORM):
- Aggregation: https://docs.djangoproject.com/en/stable/topics/db/aggregation/
- Functions (Coalesce): https://docs.djangoproject.com/en/stable/ref/models/database-functions/

Design:
- Return concrete Python lists (not lazy QuerySets) for predictable API consumption.
- Exclude null/blank states to avoid noisy groups.
- Coalesce numeric sums to Decimal('0.00') to avoid None in results.
- Reuse sellertrade_qs() from logic/common.py for DRY filtering.

Used by view endpoints (acq_module/views/view_seller_data.py):
- get_states_for_selection -> URL name 'api_states_for_selection'
- get_state_count_for_selection -> URL name 'api_state_count_for_selection'
- get_count_by_state -> URL name 'api_count_by_state'
- get_sum_current_balance_by_state -> URL name 'api_sum_current_balance_by_state'
- get_sum_total_debt_by_state -> URL name 'api_sum_total_debt_by_state'
- get_sum_seller_asis_value_by_state -> URL name 'api_sum_seller_asis_value_by_state'
"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

# Django ORM aggregation and functions
from django.db.models import Count, DecimalField, Sum, Value
from django.db.models.functions import Coalesce

# Centralized base selector for seller+trade
from .common import sellertrade_qs





# ---------------------------------------------------------------------------
# Public state summary helpers (return concrete Python lists)
# ---------------------------------------------------------------------------

def states_for_selection(seller_id: int, trade_id: int) -> List[str]:
    """Return a sorted list of distinct state values present in the selection.

    Example output:
        ['AZ', 'CA', 'TX']
    
    Used by view:
        acq_module.views.view_seller_data.get_states_for_selection
        (URL name: 'api_states_for_selection')
    """
    # Start from the validated base queryset
    qs = (
        sellertrade_qs(seller_id, trade_id)
        .exclude(state__isnull=True)
        .exclude(state__exact="")
    )
    # Ask the database for distinct state values and sort ascending
    distinct_states = qs.values_list("state", flat=True).distinct().order_by("state")
    # Materialize to a Python list for predictable consumption
    return list(distinct_states)


def state_count_for_selection(seller_id: int, trade_id: int) -> int:
    """Return the number of distinct states in the selection.

    This issues a COUNT DISTINCT at the database for efficiency.
    
    Used by view:
        acq_module.views.view_seller_data.get_state_count_for_selection
        (URL name: 'api_state_count_for_selection')
    """
    # Build the base queryset and count distinct states
    qs = (
        sellertrade_qs(seller_id, trade_id)
        .exclude(state__isnull=True)
        .exclude(state__exact="")
    )
    return qs.values("state").distinct().count()


def count_by_state(seller_id: int, trade_id: int) -> List[Dict[str, object]]:
    """Return counts per state for the selection.

    Output shape:
        [
          {'state': 'CA', 'count': 42},
          {'state': 'TX', 'count': 18},
          ...
        ]
    
    Used by view:
        acq_module.views.view_seller_data.get_count_by_state
        (URL name: 'api_count_by_state')
    """
    # Base queryset with valid states only
    qs = (
        sellertrade_qs(seller_id, trade_id)
        .exclude(state__isnull=True)
        .exclude(state__exact="")
    )
    # Group by state and compute a row count per group
    aggregated = qs.values("state").annotate(count=Count("id")).order_by("-count")
    # Return as a list of dicts, ready for JSON serialization
    return list(aggregated)


def sum_current_balance_by_state(seller_id: int, trade_id: int) -> List[Dict[str, object]]:
    """Return sum(current_balance) per state for the selection.

    Uses Coalesce to default to Decimal('0.00') when the sum is NULL.
    
    Used by view:
        acq_module.views.view_seller_data.get_sum_current_balance_by_state
        (URL name: 'api_sum_current_balance_by_state')
    """
    # Build the base queryset with valid states only
    qs = (
        sellertrade_qs(seller_id, trade_id)
        .exclude(state__isnull=True)
        .exclude(state__exact="")
    )
    # Define a typed zero literal so DB adapters keep Decimal typing consistent
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    # Group by state and compute sums, ordering by the sum descending
    aggregated = (
        qs.values("state")
        .annotate(sum_current_balance=Coalesce(Sum("current_balance"), zero_dec))
        .order_by("-sum_current_balance")
    )
    # Return as a list of dicts
    return list(aggregated)


def sum_total_debt_by_state(seller_id: int, trade_id: int) -> List[Dict[str, object]]:
    """Return sum(total_debt) per state for the selection.

    Uses Coalesce to default to Decimal('0.00') when the sum is NULL.
    
    Used by view:
        acq_module.views.view_seller_data.get_sum_total_debt_by_state
        (URL name: 'api_sum_total_debt_by_state')
    """
    # Base queryset with valid states only
    qs = (
        sellertrade_qs(seller_id, trade_id)
        .exclude(state__isnull=True)
        .exclude(state__exact="")
    )
    # Typed zero for Coalesce to ensure Decimal type
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    # Group and sum, then order by the sum descending
    aggregated = (
        qs.values("state")
        .annotate(sum_total_debt=Coalesce(Sum("total_debt"), zero_dec))
        .order_by("-sum_total_debt")
    )
    # Materialize to list
    return list(aggregated)


def sum_seller_asis_value_by_state(seller_id: int, trade_id: int) -> List[Dict[str, object]]:
    """Return sum(seller_asis_value) per state for the selection.

    Uses Coalesce to default to Decimal('0.00') when the sum is NULL.
    
    Used by view:
        acq_module.views.view_seller_data.get_sum_seller_asis_value_by_state
        (URL name: 'api_sum_seller_asis_value_by_state')
    """
    # Base queryset with valid states only
    qs = (
        sellertrade_qs(seller_id, trade_id)
        .exclude(state__isnull=True)
        .exclude(state__exact="")
    )
    # Typed zero for Coalesce to ensure Decimal type
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    # Group and sum, then order by the sum descending
    aggregated = (
        qs.values("state")
        .annotate(sum_seller_asis_value=Coalesce(Sum("seller_asis_value"), zero_dec))
        .order_by("-sum_seller_asis_value")
    )
    # Return list of dicts
    return list(aggregated)
