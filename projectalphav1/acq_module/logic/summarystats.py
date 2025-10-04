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

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List
import logging

# Django ORM aggregation and functions
from django.db.models import Count, DecimalField, Sum, Value
from django.db.models.functions import Coalesce

# Centralized base selector for seller+trade
from .common import sellertrade_qs

# Module logger for diagnostics (widgets, summaries)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pool Level Summary Stats
# ---------------------------------------------------------------------------
def total_assets(seller_id: int, trade_id: int) -> int:
    """Return the row count for the selected seller and trade.

    Django docs (Aggregation/Count): https://docs.djangoproject.com/en/stable/topics/db/aggregation/
    """
    # Start from the validated base queryset
    qs = sellertrade_qs(seller_id, trade_id)
    try:
        sample_count = qs.count()
    except Exception as e:
        logger.error("[pool-summary] queryset count failed seller=%s trade=%s: %s", seller_id, trade_id, e)
        sample_count = 0
    # Ask the database for the count (returns int)
    count = qs.count()
    return count
    
def total_current_balance(seller_id: int, trade_id: int) -> Decimal:
    """Return the sum of current_balance for the selected seller and trade.

    Null-safe via Coalesce to keep a Decimal result.
    Django docs (Coalesce): https://docs.djangoproject.com/en/stable/ref/models/database-functions/#coalesce
    """
    qs = sellertrade_qs(seller_id, trade_id)
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    agg = qs.aggregate(total=Coalesce(Sum("current_balance"), zero_dec))
    return agg["total"]

def total_debt(seller_id: int, trade_id: int) -> Decimal:
    """Return the sum of total_debt for the selected seller and trade (null-safe)."""
    qs = sellertrade_qs(seller_id, trade_id)
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    agg = qs.aggregate(total=Coalesce(Sum("total_debt"), zero_dec))
    return agg["total"]

def total_seller_asis_value(seller_id: int, trade_id: int) -> Decimal:
    """Return the sum of seller_asis_value for the selected seller and trade (null-safe)."""
    qs = sellertrade_qs(seller_id, trade_id)
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    agg = qs.aggregate(total=Coalesce(Sum("seller_asis_value"), zero_dec))
    return agg["total"]


def count_upb_td_val_summary(seller_id: int, trade_id: int) -> Dict[str, object]:
    """Return a one-shot aggregate for pool-level tiles (count, UPB, total debt, as-is value).

    This performs a single SQL query using COUNT and SUM with Coalesce to avoid NULLs.

    Output shape:
        {
          'assets': int,                     # row count
          'current_balance': Decimal,         # UPB sum
          'total_debt': Decimal,              # total_debt sum
          'seller_asis_value': Decimal,       # seller_asis_value sum
          'upb_ltv_percent': Decimal,         # (UPB / As-Is) * 100, 2dp
          'td_ltv_percent': Decimal           # (Total Debt / As-Is) * 100, 2dp
        }

    Docs:
      - Aggregation: https://docs.djangoproject.com/en/stable/topics/db/aggregation/
      - Functions (Coalesce): https://docs.djangoproject.com/en/stable/ref/models/database-functions/
    """
    # Build the validated base queryset filtered by seller and trade
    qs = sellertrade_qs(seller_id, trade_id)
    # Define a typed zero Decimal so Coalesce preserves Decimal typing in DB adapters
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    # Execute a single aggregate call to compute all required metrics
    agg = qs.aggregate(
        assets=Count("asset_hub"),
        current_balance=Coalesce(Sum("current_balance"), zero_dec),
        total_debt=Coalesce(Sum("total_debt"), zero_dec),
        seller_asis_value=Coalesce(Sum("seller_asis_value"), zero_dec),
    )
    # Compute simple LTV percentages from the same aggregate to avoid extra queries
    asis: Decimal = agg["seller_asis_value"] or Decimal("0.00")
    upb: Decimal = agg["current_balance"] or Decimal("0.00")
    td: Decimal = agg["total_debt"] or Decimal("0.00")

    def _pct(n: Decimal, d: Decimal) -> Decimal:
        if not d or d == 0:
            return Decimal("0.00")
        return (n * Decimal("100") / d).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    upb_ltv_percent = _pct(upb, asis)
    td_ltv_percent = _pct(td, asis)

    # Normalize and return a predictable dict for API/consumers
    out = {
        "assets": int(agg.get("assets", 0)),
        "current_balance": upb,
        "total_debt": td,
        "seller_asis_value": asis,
        "upb_ltv_percent": upb_ltv_percent,
        "td_ltv_percent": td_ltv_percent,
    }
    # Debug line to help diagnose zeros in widgets (log computed assets)
    try:
        logger.debug(
            "[pool-summary] seller=%s trade=%s assets=%s agg=%s",
            seller_id, trade_id, out.get("assets"), {k: str(v) for k, v in out.items()}
        )
    except Exception:
        # Avoid logging-related failures impacting the response
        pass
    return out
# ---------------------------------------------------------------------------
# Pool LTVs
# ---------------------------------------------------------------------------

def upb_ltv(seller_id: int, trade_id: int) -> Decimal:
    """Return the UPB LTV for the selected seller and trade."""
    qs = sellertrade_qs(seller_id, trade_id)
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    agg = qs.aggregate(upb_ltv=Coalesce(Sum("current_balance"), zero_dec))
    return agg["upb_ltv"]

def td_ltv(seller_id: int, trade_id: int) -> Decimal:
    """Return the Total Debt LTV for the selected seller and trade."""
    qs = sellertrade_qs(seller_id, trade_id)
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    agg = qs.aggregate(td_ltv=Coalesce(Sum("total_debt"), zero_dec))
    return agg["td_ltv"]


# ---------------------------------------------------------------------------
# By State summary helpers (return concrete Python lists)
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
