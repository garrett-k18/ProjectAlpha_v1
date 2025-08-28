"""
Stratification utilities for acquisitions analytics (dynamic, data-driven bands).

Design goals:
 - Use product-defined rule-based bins; no DB quantile fallback.
 - Keep helpers modular and reusable for multiple numeric fields.
 - Return concrete Python lists (not lazy QuerySets) for predictable API use.

Docs reviewed (per project standards):
- Django Aggregation: https://docs.djangoproject.com/en/stable/topics/db/aggregation/
- Django Window expressions: https://docs.djangoproject.com/en/stable/ref/models/expressions/#window-expressions
- Django Conditional expressions: https://docs.djangoproject.com/en/stable/ref/models/conditional-expressions/

Notes:
 - Primary path uses rule-based bins keyed off the dataset's max value; we then
   aggregate per band to get count/sum/min/max.
 - All sums are coalesced to Decimal('0.00') to avoid None.
 - Null numeric values are excluded from banding.
"""

from __future__ import annotations

# stdlib
from decimal import Decimal, ROUND_HALF_UP
import logging
from typing import Dict, List, Optional

# Django ORM imports
from django.db.models import (
    Count,
    DecimalField,
    Min,
    Max,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce
# NTILE-based equal-frequency fallback removed per product decision.

# Local selector helper (centralized seller+trade filtering)
from .common import sellertrade_qs

# Module logger
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Formatting utilities
# ---------------------------------------------------------------------------

def _format_compact_currency(value: Decimal) -> str:
    """Return a compact currency string for labels, e.g., $980k or $4.2m.

    - Uses thresholds to decide between 'k' and 'm'.
    - Rounded to one decimal place for millions; no decimals for thousands.
    """
    # Guard: ensure Decimal
    n = Decimal(value or 0)
    if n >= Decimal('1000000'):
        m = (n / Decimal('1000000')).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        # Strip trailing .0 for clean labels
        m_str = ("%s" % m).rstrip('0').rstrip('.')
        return f"${m_str}m"
    # Thousands
    # Use integer formatting without stripping zeros to keep 200k as '200k'.
    k = (n / Decimal('1000')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return f"${int(k)}k"


def _nice_step(max_value: Decimal) -> int:
    """Pick a human-friendly rounding step based on dataset magnitude.

    Examples:
    - < $1m -> $25k
    - < $2.5m -> $50k
    - < $10m -> $100k
    - otherwise -> $250k
    """
    mv = Decimal(max_value or 0)
    if mv < Decimal('1000000'):
        return 25_000
    if mv < Decimal('2500000'):
        return 50_000
    if mv < Decimal('10000000'):
        return 100_000
    return 250_000


def _rounded_range_label(lower: Optional[Decimal], upper: Optional[Decimal]) -> str:
    """Create a friendly label "$X – $Y" using magnitude-aware rounding.

    - If only lower is present: "> $X".
    - If only upper is present: "< $Y".
    - If both are None: "N/A".
    """
    if lower is None and upper is None:
        return "N/A"

    # Choose step from the larger bound for nicer consistency
    max_bound = max([b for b in [lower, upper] if b is not None] or [Decimal('0')])
    step = _nice_step(max_bound)

    def _round_to_step(x: Decimal, up: bool) -> Decimal:
        if x is None:
            return Decimal('0')
        # Convert to integer cents to avoid float
        q = Decimal(step)
        # Compute quotient, then multiply back
        if up:
            # Ceil to nearest multiple of q, Decimal-safe via "negative floor" trick
            # ceil(x / q) * q == (-(-x // q)) * q
            return (-(-x // q)) * q  # type: ignore[operator]
        else:
            # Floor to nearest multiple of q
            return (x // q) * q  # type: ignore[operator]

    lo = _round_to_step(lower, up=False) if lower is not None else None
    hi = _round_to_step(upper, up=True) if upper is not None else None

    if lo is not None and hi is not None:
        return f"{_format_compact_currency(lo)} – {_format_compact_currency(hi)}"
    if lo is not None:
        return f"> {_format_compact_currency(lo)}"
    return f"< {_format_compact_currency(hi or Decimal('0'))}"


def _band_label(lower: Optional[Decimal], upper: Optional[Decimal], index: int, total: int) -> str:
    """Generate a label for a band with UX rules:

    - First band: "< $X" using the upper bound (rounded up to a nice step).
    - Last band:  "> $Y" using the lower bound (rounded down to a nice step).
    - Middle:     "$Y – $X" with floor(lower) and ceil(upper), clamped so hi >= lo.

    This avoids confusing ranges like "$25k – $1k" when rounding steps are coarse.
    """
    # Compute nice step using the larger bound to keep consistency
    max_bound = max([b for b in [lower, upper] if b is not None] or [Decimal('0')])
    step = _nice_step(max_bound)

    def _round_to_step(x: Optional[Decimal], up: bool) -> Optional[Decimal]:
        if x is None:
            return None
        q = Decimal(step)
        return (-(-x // q)) * q if up else (x // q) * q  # type: ignore[operator]

    lo = _round_to_step(lower, up=False) if lower is not None else None
    hi = _round_to_step(upper, up=True) if upper is not None else None

    # Clamp to avoid inverted ranges after rounding
    if lo is not None and hi is not None and hi < lo:
        hi = lo

    # First band: strictly "< $X"
    if index == 1 and hi is not None:
        return f"< {_format_compact_currency(hi)}"
    # Last band: strictly "> $Y"
    if index == total and lo is not None:
        return f"> {_format_compact_currency(lo)}"

    # Middle bands (or missing bound fallbacks)
    if lo is not None and hi is not None:
        return f"{_format_compact_currency(lo)} – {_format_compact_currency(hi)}"
    if lo is not None:
        return f"> {_format_compact_currency(lo)}"
    if hi is not None:
        return f"< {_format_compact_currency(hi)}"
    return "N/A"


 

# ---------------------------------------------------------------------------
# Rule-based thresholds (by max current_balance)
# ---------------------------------------------------------------------------

def _rule_edges_for_max(max_v: Decimal) -> Optional[List[Decimal]]:
    """Return ascending upper-edge breakpoints for rule-based bands.

    The returned list contains the inner edges; bands are defined as:
      [< edge0], [edge0 – edge1], ..., [edge{n-2} – edge{n-1}], [> edge{n-1}]

    Rules provided by product:
    - max < $1,000,000  -> edges: [200k, 400k, 600k, 800k]  (5 bands)
    - 1,000,000 ≤ max < 3,000,000 -> edges: [750k, 1.5m, 2.25m, 3.0m] (5 bands)

    Returns None when no rule matches; callers should fall back to other strategies.
    """
    mv = Decimal(max_v or 0)
    # New rule: very small pools (max <= 500k)
    # Bands: <100k, 100–200k, 200–300k, 300–400k, >400k
    if mv <= Decimal('500000'):
        return [Decimal('100000'), Decimal('200000'), Decimal('300000'), Decimal('400000')]
    if mv < Decimal('1000000'):
        return [Decimal('200000'), Decimal('400000'), Decimal('600000'), Decimal('800000')]
    if mv < Decimal('2000000'):
        return [Decimal('500000'), Decimal('1000000'), Decimal('1500000'), Decimal('2000000')]
    return None

# ---------------------------------------------------------------------------
# Core APIs
# ---------------------------------------------------------------------------


def current_balance_stratification_dynamic(
    seller_id: int,
    trade_id: int,
    bands: int = 6,
) -> List[Dict[str, object]]:
    """Return dynamic bands for `current_balance` with counts and sums.

    Strategy:
    - Rule-based bins chosen by max(current_balance).
    - If no rule matches, returns an empty list (no equal-frequency fallback).

    Output list item shape:
      {
        key: str, index: int,
        lower: Decimal|None, upper: Decimal|None,
        count: int,
        sum_current_balance: Decimal,
        sum_total_debt: Decimal,
        sum_seller_asis_value: Decimal,
        label: str
      }
    """
    # Base queryset: exclude null balances
    qs = sellertrade_qs(seller_id, trade_id).exclude(current_balance__isnull=True)

    # If empty, return no bands
    if not qs.exists():
        return []

    # Typed zero for Decimal
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))

    # Rule-based path, keyed off max(current_balance)
    max_only = qs.aggregate(mx=Max("current_balance"))
    max_v: Decimal = max_only.get("mx") or Decimal("0.00")
    rule_edges = _rule_edges_for_max(max_v)
    if rule_edges:
        total_bands = len(rule_edges) + 1
        results: List[Dict[str, object]] = []
        for i in range(total_bands):
            if i == 0:
                # First band: < edge0
                lo = None
                hi = rule_edges[0]
                bin_qs = qs.filter(current_balance__lt=hi)
            elif i == total_bands - 1:
                # Last band: >= last edge
                lo = rule_edges[-1]
                hi = None
                bin_qs = qs.filter(current_balance__gte=lo)
            else:
                # Middle bands: [edge_{i-1}, edge_i)
                lo = rule_edges[i - 1]
                hi = rule_edges[i]
                bin_qs = qs.filter(current_balance__gte=lo, current_balance__lt=hi)

            cnt = bin_qs.count()
            aggs = bin_qs.aggregate(
                upb=Coalesce(Sum("current_balance"), zero_dec),
                td=Coalesce(Sum("total_debt"), zero_dec),
                asis=Coalesce(Sum("seller_asis_value"), zero_dec),
            )
            label = _band_label(lo, hi, i + 1, total_bands)
            results.append({
                "key": str(i + 1),
                "index": i + 1,
                "lower": lo,
                "upper": hi,
                "count": int(cnt),
                "sum_current_balance": aggs.get("upb") or Decimal("0.00"),
                "sum_total_debt": aggs.get("td") or Decimal("0.00"),
                "sum_seller_asis_value": aggs.get("asis") or Decimal("0.00"),
                "label": label,
            })
        # Keep zero-count bands visible to maintain consistent 5-band layout
        return results

    # Per product decision: no equal-frequency fallback; return empty if no rule match.
    return []

 


def total_debt_stratification_dynamic(
    seller_id: int,
    trade_id: int,
    bands: int = 6,
) -> List[Dict[str, object]]:
    """Return dynamic bands for `total_debt` with counts and sums.

    Strategy mirrors rule-based current balance stratifier:
    - Rule-based bins chosen by max(total_debt).
    - If no rule matches, returns an empty list (no equal-frequency fallback).

    Output list item shape is identical to the current_balance API.
    """
    # Base queryset: exclude null total_debt
    qs = sellertrade_qs(seller_id, trade_id).exclude(total_debt__isnull=True)

    # If empty, return no bands
    if not qs.exists():
        return []

    # Typed zero for Decimal
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))

    # Rule-based path, keyed off max(total_debt)
    max_only = qs.aggregate(mx=Max("total_debt"))
    max_v: Decimal = max_only.get("mx") or Decimal("0.00")
    rule_edges = _rule_edges_for_max(max_v)
    if rule_edges:
        total_bands = len(rule_edges) + 1
        results: List[Dict[str, object]] = []
        for i in range(total_bands):
            if i == 0:
                # First band: < edge0
                lo = None
                hi = rule_edges[0]
                bin_qs = qs.filter(total_debt__lt=hi)
            elif i == total_bands - 1:
                # Last band: >= last edge
                lo = rule_edges[-1]
                hi = None
                bin_qs = qs.filter(total_debt__gte=lo)
            else:
                # Middle bands: [edge_{i-1}, edge_i)
                lo = rule_edges[i - 1]
                hi = rule_edges[i]
                bin_qs = qs.filter(total_debt__gte=lo, total_debt__lt=hi)

            cnt = bin_qs.count()
            aggs = bin_qs.aggregate(
                upb=Coalesce(Sum("current_balance"), zero_dec),
                td=Coalesce(Sum("total_debt"), zero_dec),
                asis=Coalesce(Sum("seller_asis_value"), zero_dec),
            )
            label = _band_label(lo, hi, i + 1, total_bands)
            results.append({
                "key": str(i + 1),
                "index": i + 1,
                "lower": lo,
                "upper": hi,
                "count": int(cnt),
                "sum_current_balance": aggs.get("upb") or Decimal("0.00"),
                "sum_total_debt": aggs.get("td") or Decimal("0.00"),
                "sum_seller_asis_value": aggs.get("asis") or Decimal("0.00"),
                "label": label,
            })
        # Keep zero-count bands visible to maintain consistent 5-band layout
        return results

    # Per product decision: no equal-frequency fallback; return empty if no rule match.
    return []

# Future: generic stratifier for arbitrary numeric field names can be added here,
# following the same rule-based only pattern (no fallbacks).


def seller_asis_value_stratification_dynamic(
    seller_id: int,
    trade_id: int,
    bands: int = 6,
) -> List[Dict[str, object]]:
    """Return dynamic bands for `seller_asis_value` with counts and sums.

    Strategy mirrors other stratifiers:
    - Rule-based bins chosen by max(seller_asis_value).
    - If no rule matches, returns an empty list (no equal-frequency fallback).

    Output list item shape is identical to other stratification APIs.
    """
    # Base queryset: exclude null seller_asis_value
    qs = sellertrade_qs(seller_id, trade_id).exclude(seller_asis_value__isnull=True)

    # If empty, return no bands
    if not qs.exists():
        return []

    # Typed zero for Decimal
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))

    # Rule-based path, keyed off max(seller_asis_value)
    max_only = qs.aggregate(mx=Max("seller_asis_value"))
    max_v: Decimal = max_only.get("mx") or Decimal("0.00")
    rule_edges = _rule_edges_for_max(max_v)
    if rule_edges:
        total_bands = len(rule_edges) + 1
        results: List[Dict[str, object]] = []
        for i in range(total_bands):
            if i == 0:
                # First band: < edge0
                lo = None
                hi = rule_edges[0]
                bin_qs = qs.filter(seller_asis_value__lt=hi)
            elif i == total_bands - 1:
                # Last band: >= last edge
                lo = rule_edges[-1]
                hi = None
                bin_qs = qs.filter(seller_asis_value__gte=lo)
            else:
                # Middle bands: [edge_{i-1}, edge_i)
                lo = rule_edges[i - 1]
                hi = rule_edges[i]
                bin_qs = qs.filter(seller_asis_value__gte=lo, seller_asis_value__lt=hi)

            cnt = bin_qs.count()
            aggs = bin_qs.aggregate(
                upb=Coalesce(Sum("current_balance"), zero_dec),
                td=Coalesce(Sum("total_debt"), zero_dec),
                asis=Coalesce(Sum("seller_asis_value"), zero_dec),
            )
            label = _band_label(lo, hi, i + 1, total_bands)
            results.append({
                "key": str(i + 1),
                "index": i + 1,
                "lower": lo,
                "upper": hi,
                "count": int(cnt),
                "sum_current_balance": aggs.get("upb") or Decimal("0.00"),
                "sum_total_debt": aggs.get("td") or Decimal("0.00"),
                "sum_seller_asis_value": aggs.get("asis") or Decimal("0.00"),
                "label": label,
            })
        # Keep zero-count bands visible to maintain consistent 5-band layout
        return results

    # Per product decision: no equal-frequency fallback; return empty if no rule match.
    return []
