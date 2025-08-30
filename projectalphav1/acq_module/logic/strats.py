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


def property_type_stratification_categorical(
    seller_id: int,
    trade_id: int,
) -> List[Dict[str, object]]:
    """Return categorical stratification aggregated by `property_type`.

    Behavior:
    - Groups `SellerRawData` records by the categorical field `property_type`.
    - Aggregates counts and sums of `current_balance`, `total_debt`, and `seller_asis_value`.
    - Returns a list of dicts in a consistent order based on model-defined choices.

    Output item shape matches other stratification endpoints:
      {
        key: str,              # property_type code
        index: int,            # 1-based order
        lower: None,           # not applicable for categorical
        upper: None,           # not applicable for categorical
        count: int,
        sum_current_balance: Decimal,
        sum_total_debt: Decimal,
        sum_seller_asis_value: Decimal,
        label: str             # human-friendly label
      }
    """
    # Local import to avoid any potential circular import issues on app load
    from ..models.seller import SellerRawData

    # Base queryset filtered by selection; exclude null/blank property types to be safe
    qs = (
        sellertrade_qs(seller_id, trade_id)
        .exclude(property_type__isnull=True)
        .exclude(property_type__exact="")
    )

    # If empty selection, return no bands
    if not qs.exists():
        return []

    # Typed zero for Decimal sums used by Coalesce so JSON always sees strings
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))

    # Single query to aggregate by property_type
    rows = (
        qs.values("property_type")
        .annotate(
            count=Count("id"),
            sum_current_balance=Coalesce(Sum("current_balance"), zero_dec),
            sum_total_debt=Coalesce(Sum("total_debt"), zero_dec),
            sum_seller_asis_value=Coalesce(Sum("seller_asis_value"), zero_dec),
        )
    )

    # Index aggregated results by code for fast lookup
    by_code: Dict[str, Dict[str, object]] = {r["property_type"]: r for r in rows}

    # Preserve choice order from the model. Include zero-count placeholders for missing categories.
    results: List[Dict[str, object]] = []
    idx = 1
    for code, label in getattr(SellerRawData, "PROPERTY_TYPE_CHOICES", []) or []:
        r = by_code.get(code)
        if r is None:
            # Build a zeroed row to keep UI consistent even if category absent
            results.append({
                "key": str(code),
                "index": idx,
                "lower": None,
                "upper": None,
                "count": 0,
                "sum_current_balance": Decimal("0.00"),
                "sum_total_debt": Decimal("0.00"),
                "sum_seller_asis_value": Decimal("0.00"),
                "label": str(label),
            })
        else:
            results.append({
                "key": str(code),
                "index": idx,
                "lower": None,
                "upper": None,
                "count": int(r.get("count", 0)),
                "sum_current_balance": r.get("sum_current_balance") or Decimal("0.00"),
                "sum_total_debt": r.get("sum_total_debt") or Decimal("0.00"),
                "sum_seller_asis_value": r.get("sum_seller_asis_value") or Decimal("0.00"),
                "label": str(label),
            })
        idx += 1

    # There could be unexpected codes not present in choices (legacy data). Append them at the end.
    known_codes = {code for code, _ in getattr(SellerRawData, "PROPERTY_TYPE_CHOICES", []) or []}
    for code, r in by_code.items():
        if code in known_codes:
            continue
        results.append({
            "key": str(code),
            "index": idx,
            "lower": None,
            "upper": None,
            "count": int(r.get("count", 0)),
            "sum_current_balance": r.get("sum_current_balance") or Decimal("0.00"),
            "sum_total_debt": r.get("sum_total_debt") or Decimal("0.00"),
            "sum_seller_asis_value": r.get("sum_seller_asis_value") or Decimal("0.00"),
            "label": str(code or "Unknown"),
        })
        idx += 1

    return results


def occupancy_stratification_categorical(
    seller_id: int,
    trade_id: int,
) -> List[Dict[str, object]]:
    """Return categorical stratification aggregated by `occupancy`.

    Behavior mirrors `property_type_stratification_categorical()` but groups by
    the `SellerRawData.occupancy` field using model-defined `OCCUPANCY_CHOICES`.

    Output item shape matches other stratification endpoints:
      {
        key: str,              # occupancy code (e.g., 'Vacant')
        index: int,            # 1-based order based on choices
        lower: None,           # not applicable for categorical
        upper: None,           # not applicable for categorical
        count: int,            # asset count
        sum_current_balance: Decimal,
        sum_total_debt: Decimal,
        sum_seller_asis_value: Decimal,
        label: str             # human-friendly label from choices
      }

    Docs reviewed:
    - Django aggregation and values/annotate: https://docs.djangoproject.com/en/stable/topics/db/aggregation/
    - Coalesce to avoid NULL in sums: https://docs.djangoproject.com/en/stable/ref/models/database-functions/#coalesce
    """
    # Local import to avoid circulars at app load time
    from ..models.seller import SellerRawData

    # Base queryset filtered by selection; exclude null/blank occupancy
    qs = (
        sellertrade_qs(seller_id, trade_id)
        .exclude(occupancy__isnull=True)
        .exclude(occupancy__exact="")
    )

    # If no matching rows for selection, return empty list for predictable UI
    if not qs.exists():
        return []

    # Typed zero for Decimal sums so JSON serializer yields strings consistently
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))

    # Aggregate in a single query by occupancy
    rows = (
        qs.values("occupancy")
        .annotate(
            count=Count("id"),
            sum_current_balance=Coalesce(Sum("current_balance"), zero_dec),
            sum_total_debt=Coalesce(Sum("total_debt"), zero_dec),
            sum_seller_asis_value=Coalesce(Sum("seller_asis_value"), zero_dec),
        )
    )

    # Index rows by occupancy code for fast lookup during ordered assembly
    by_code: Dict[str, Dict[str, object]] = {r["occupancy"]: r for r in rows}

    # Walk model choices in order to build the results, inserting zero rows for
    # categories missing from the dataset so the UI always shows a stable table.
    results: List[Dict[str, object]] = []
    idx = 1
    for code, label in getattr(SellerRawData, "OCCUPANCY_CHOICES", []) or []:
        r = by_code.get(code)
        if r is None:
            results.append({
                "key": str(code),
                "index": idx,
                "lower": None,
                "upper": None,
                "count": 0,
                "sum_current_balance": Decimal("0.00"),
                "sum_total_debt": Decimal("0.00"),
                "sum_seller_asis_value": Decimal("0.00"),
                "label": str(label),
            })
        else:
            results.append({
                "key": str(code),
                "index": idx,
                "lower": None,
                "upper": None,
                "count": int(r.get("count", 0)),
                "sum_current_balance": r.get("sum_current_balance") or Decimal("0.00"),
                "sum_total_debt": r.get("sum_total_debt") or Decimal("0.00"),
                "sum_seller_asis_value": r.get("sum_seller_asis_value") or Decimal("0.00"),
                "label": str(label),
            })
        idx += 1

    # Append any unexpected codes not listed in choices (legacy data) at the end
    known_codes = {code for code, _ in getattr(SellerRawData, "OCCUPANCY_CHOICES", []) or []}
    for code, r in by_code.items():
        if code in known_codes:
            continue
        results.append({
            "key": str(code),
            "index": idx,
            "lower": None,
            "upper": None,
            "count": int(r.get("count", 0)),
            "sum_current_balance": r.get("sum_current_balance") or Decimal("0.00"),
            "sum_total_debt": r.get("sum_total_debt") or Decimal("0.00"),
            "sum_seller_asis_value": r.get("sum_seller_asis_value") or Decimal("0.00"),
            "label": str(code or "Unknown"),
        })
        idx += 1

    return results

def wac_stratification_static(
    seller_id: int,
    trade_id: int,
) -> List[Dict[str, object]]:
    """Return static bands for `interest_rate` (fractional) with counts and sums.

    Business-defined static WAC (Weighted Average Coupon) bands using fractional
    interest rates stored on `SellerRawData.interest_rate`:
      - < 0.03   (< 3%)
      - 0.03–0.06 (3% – 6%)
      - 0.06–0.09 (6% – 9%)
      - 0.09–0.12 (9% – 12%)
      - > 0.12   (> 12%)

    Output list item shape mirrors other stratification APIs:
      {
        key: str, index: int,
        lower: Decimal|None, upper: Decimal|None,  # fractional bounds (e.g., 0.03)
        count: int,
        sum_current_balance: Decimal,
        sum_total_debt: Decimal,
        sum_seller_asis_value: Decimal,
        label: str  # e.g., "< 3%", "3% – 6%"
      }

    Docs reviewed:
    - Django ORM filters and aggregation: https://docs.djangoproject.com/en/stable/topics/db/aggregation/
    """
    # Base queryset: exclude null interest rates to avoid skewed bands
    qs = sellertrade_qs(seller_id, trade_id).exclude(interest_rate__isnull=True)

    # If empty, return no bands
    if not qs.exists():
        return []

    # Typed zero for Decimal sums
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))

    # Static fractional edges (upper bounds for inner bands)
    # Bands are defined as: [< e0], [e0 – e1], [e1 – e2], [e2 – e3], [> e3]
    edges = [Decimal("0.03"), Decimal("0.06"), Decimal("0.09"), Decimal("0.12")]
    total_bands = len(edges) + 1

    def pct_label(lo: Optional[Decimal], hi: Optional[Decimal], idx: int, total: int) -> str:
        """Friendly percentage labels from fractional bounds.

        - First band: "< X%" using upper bound
        - Last band:  "> Y%" using lower bound
        - Middle:     "Y% – X%"
        """
        def fmt(x: Optional[Decimal]) -> str:
            if x is None:
                return ""
            # Convert fractional (e.g., 0.03) to integer percent without decimals
            return f"{int((x * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))}%"

        if idx == 1 and hi is not None:
            return f"< {fmt(hi)}"
        if idx == total and lo is not None:
            return f"> {fmt(lo)}"
        if lo is not None and hi is not None:
            return f"{fmt(lo)} – {fmt(hi)}"
        # Fallbacks (should not occur with static edges)
        if lo is not None:
            return f"> {fmt(lo)}"
        if hi is not None:
            return f"< {fmt(hi)}"
        return "N/A"

    results: List[Dict[str, object]] = []
    for i in range(total_bands):
        if i == 0:
            # First band: interest_rate < edges[0]
            lo: Optional[Decimal] = None
            hi: Optional[Decimal] = edges[0]
            bin_qs = qs.filter(interest_rate__lt=hi)
        elif i == total_bands - 1:
            # Last band: interest_rate >= edges[-1]
            lo = edges[-1]
            hi = None
            bin_qs = qs.filter(interest_rate__gte=lo)
        else:
            # Middle bands: [edges[i-1], edges[i])
            lo = edges[i - 1]
            hi = edges[i]
            bin_qs = qs.filter(interest_rate__gte=lo, interest_rate__lt=hi)

        cnt = bin_qs.count()
        aggs = bin_qs.aggregate(
            upb=Coalesce(Sum("current_balance"), zero_dec),
            td=Coalesce(Sum("total_debt"), zero_dec),
            asis=Coalesce(Sum("seller_asis_value"), zero_dec),
        )
        label = pct_label(lo, hi, i + 1, total_bands)
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

    return results

 


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


def judicial_stratification_dynamic(
    seller_id: int,
    trade_id: int,
) -> List[Dict[str, object]]:
    """
    Return stratification data for Judicial vs Non-Judicial foreclosure states.
    
    Uses the StateReference model to determine if each state is judicial or non-judicial,
    then aggregates metrics by these two categories.
    
    Returns a list with two items:
    - One for Judicial states
    - One for Non-Judicial states
    
    Each item includes counts and sums of relevant financial metrics.
    """
    from ..models.assumptions import StateReference
    
    # Get the base queryset for this seller+trade combination
    qs = sellertrade_qs(seller_id, trade_id)
    
    # Early exit if empty
    if not qs.exists():
        return []
        
    # Get all state references for lookups
    state_refs = {sr.state_code: sr.judicialvsnonjudicial 
                  for sr in StateReference.objects.all()}
    
    # Initialize result counters for both categories
    result = {
        "judicial": {
            "count": 0,
            "sum_current_balance": Decimal("0.00"),
            "sum_total_debt": Decimal("0.00"),
            "sum_seller_asis_value": Decimal("0.00"),
        },
        "non_judicial": {
            "count": 0,
            "sum_current_balance": Decimal("0.00"),
            "sum_total_debt": Decimal("0.00"),
            "sum_seller_asis_value": Decimal("0.00"),
        },
    }
    
    # Aggregate by state first
    states_data = qs.values('state').annotate(
        count=Count('id'),
        sum_current_balance=Coalesce(Sum('current_balance'), Value(Decimal("0.00")), output_field=DecimalField()),
        sum_total_debt=Coalesce(Sum('total_debt'), Value(Decimal("0.00")), output_field=DecimalField()),
        sum_seller_asis_value=Coalesce(Sum('seller_asis_value'), Value(Decimal("0.00")), output_field=DecimalField()),
    )
    
    # Sort states into judicial/non-judicial and sum their metrics
    for state_data in states_data:
        state_code = state_data['state']
        if not state_code:  # Skip empty states
            continue
            
        # Normalize state code to match the reference
        state_code = state_code.strip().upper()
        
        # Determine if this is a judicial state
        is_judicial = state_refs.get(state_code, False)  # Default to non-judicial if not found
        
        # Update the appropriate category
        category = "judicial" if is_judicial else "non_judicial"
        
        result[category]["count"] += state_data["count"]
        result[category]["sum_current_balance"] += state_data["sum_current_balance"]
        result[category]["sum_total_debt"] += state_data["sum_total_debt"]
        result[category]["sum_seller_asis_value"] += state_data["sum_seller_asis_value"]
    
    # Format output to match other stratifications
    formatted_result = [
        {
            "key": "judicial",
            "index": 1,
            "label": "Judicial",
            "count": result["judicial"]["count"],
            "sum_current_balance": result["judicial"]["sum_current_balance"],
            "sum_total_debt": result["judicial"]["sum_total_debt"],
            "sum_seller_asis_value": result["judicial"]["sum_seller_asis_value"],
        },
        {
            "key": "non_judicial",
            "index": 2,
            "label": "Non-Judicial",
            "count": result["non_judicial"]["count"],
            "sum_current_balance": result["non_judicial"]["sum_current_balance"],
            "sum_total_debt": result["non_judicial"]["sum_total_debt"],
            "sum_seller_asis_value": result["non_judicial"]["sum_seller_asis_value"],
        },
    ]
    
    return formatted_result


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
