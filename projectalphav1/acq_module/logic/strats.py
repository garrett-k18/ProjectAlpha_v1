"""
Stratification utilities for acquisitions analytics (dynamic, data-driven bands).

Design goals:
- Use equal-frequency (quantile) banding via PostgreSQL NTILE for robust bins.
- Provide safe fallbacks when NTILE is unavailable (equal-width by min/max).
- Keep helpers modular and reusable for multiple numeric fields.
- Return concrete Python lists (not lazy QuerySets) for predictable API use.

Docs reviewed (per project standards):
- Django Aggregation: https://docs.djangoproject.com/en/stable/topics/db/aggregation/
- Django Window expressions: https://docs.djangoproject.com/en/stable/ref/models/expressions/#window-expressions
- Django Conditional expressions: https://docs.djangoproject.com/en/stable/ref/models/conditional-expressions/
- PostgreSQL NTILE: https://www.postgresql.org/docs/current/functions-window.html

Notes:
- Primary path uses NTILE(k) ordered by the numeric field to produce k bands with
  roughly equal counts; then we aggregate per band to get count/sum/min/max.
- Fallback path (non-Postgres or older Django without Ntile) uses equal-width bins
  computed from min/max. This is less robust for skew, but universally available.
- All sums are coalesced to Decimal('0.00') to avoid None.
- Null numeric values are excluded from banding.
"""

from __future__ import annotations

# stdlib
from decimal import Decimal, ROUND_HALF_UP
import logging
from typing import Dict, List, Optional

# Django ORM imports
from django.db import connection, connections
from django.db.models import (
    Count,
    DecimalField,
    F,
    Min,
    Max,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce
try:
    # Django 4.0+ exposes Ntile as a window function
    from django.db.models.functions import Ntile  # type: ignore
    from django.db.models import Window  # Window expression wrapper
    _HAS_NTILE: bool = True
except Exception:
    # Older Django or unsupported backend
    Ntile = None  # type: ignore
    Window = None  # type: ignore
    _HAS_NTILE = False

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


def _quantile_bands_python(qs, bands: int) -> List[Dict[str, object]]:
    """Python fallback that produces equal-frequency bands when DB NTILE is
    unavailable. It sorts rows by `current_balance` and splits into nearly equal
    segments, then aggregates counts and sums per segment.

    This trades some performance for correctness and portability and is adequate
    for moderate result sizes typically displayed on dashboards.
    """
    # Pull only required fields and sort by the banding key
    rows = list(
        qs.order_by('current_balance').values(
            'id', 'current_balance', 'total_debt', 'seller_asis_value'
        )
    )
    n = len(rows)
    if n == 0:
        return []

    D0 = Decimal('0.00')
    results: List[Dict[str, object]] = []

    for i in range(bands):
        start = (i * n) // bands
        end = ((i + 1) * n) // bands  # exclusive
        if start >= end:
            continue  # empty slice; can happen when bands > n
        segment = rows[start:end]

        lower = segment[0]['current_balance']
        upper = segment[-1]['current_balance']

        # Aggregate within the slice
        cnt = len(segment)
        # Use Decimal start value; parenthesize generator (Pyright af0e57c4, 4b13cf4e, 7f1fa07d)
        sum_upb = sum(((r['current_balance'] or D0) for r in segment), D0)
        sum_td = sum(((r['total_debt'] or D0) for r in segment), D0)
        sum_asis = sum(((r['seller_asis_value'] or D0) for r in segment), D0)

        label = _band_label(lower, upper, i + 1, bands)

        results.append({
            'key': str(i + 1),
            'index': i + 1,
            'lower': lower,
            'upper': upper,
            'count': int(cnt),
            'sum_current_balance': sum_upb,
            'sum_total_debt': sum_td,
            'sum_seller_asis_value': sum_asis,
            'label': label,
        })

    # Remove empty bands just in case and return
    results = [r for r in results if r['count'] > 0]
    return results

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
    if mv < Decimal('1000000'):
        return [Decimal('200000'), Decimal('400000'), Decimal('600000'), Decimal('800000')]
    if mv < Decimal('3000000'):
        return [Decimal('750000'), Decimal('1500000'), Decimal('2250000'), Decimal('3000000')]
    return None

# ---------------------------------------------------------------------------
# Core APIs
# ---------------------------------------------------------------------------

def _is_postgres(db_alias: Optional[str] = None) -> bool:
    """Return True if the given DB backend is PostgreSQL.

    If no alias is provided, falls back to the default connection.
    Uses django.db.connections to respect multi-DB routing.
    """
    try:
        if db_alias:
            return connections[db_alias].vendor == 'postgresql'
        return connection.vendor == 'postgresql'
    except Exception:
        return False


def current_balance_stratification_dynamic(
    seller_id: int,
    trade_id: int,
    bands: int = 6,
) -> List[Dict[str, object]]:
    """Return dynamic bands for `current_balance` with counts and sums.

    Strategy order:
    1) Rule-based bins chosen by max(current_balance) when a rule matches.
    2) PostgreSQL NTILE(k) window-based equal-frequency bands (preferred).
    3) Python equal-frequency fallback (quantiles) when NTILE is unavailable.
    4) Equal-width bands from min/max as the final universal fallback.

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

    # Preferred: NTILE on Postgres if available (check the queryset's DB alias)
    db_alias = getattr(qs, 'db', None)
    if _is_postgres(db_alias) and _HAS_NTILE and Window is not None and Ntile is not None:
        try:
            # Annotate tile 1..k ordered by current_balance ascending (NULLs excluded already)
            annotated = qs.annotate(
                tile=Window(
                    expression=Ntile(bands),
                    # Note: We already exclude NULLs above, so plain asc() is sufficient.
                    # Older Django versions may not support nulls_last kwarg.
                    order_by=F("current_balance").asc(),
                )
            )
            grouped = (
                annotated
                .values("tile")
                .annotate(
                    count=Count("id"),
                    sum_current_balance=Coalesce(Sum("current_balance"), zero_dec),
                    sum_total_debt=Coalesce(Sum("total_debt"), zero_dec),
                    sum_seller_asis_value=Coalesce(Sum("seller_asis_value"), zero_dec),
                    lower=Min("current_balance"),
                    upper=Max("current_balance"),
                )
                .order_by("tile")
            )
            results: List[Dict[str, object]] = []
            for row in grouped:
                idx = int(row["tile"])  # 1-based index
                lower = row.get("lower")
                upper = row.get("upper")
                # First band should be "< $X", last band "> $Y"; middle are ranges
                label = _band_label(lower, upper, idx, bands)
                results.append({
                    "key": str(idx),
                    "index": idx,
                    "lower": lower,
                    "upper": upper,
                    "count": int(row.get("count", 0) or 0),
                    "sum_current_balance": row.get("sum_current_balance") or Decimal("0.00"),
                    "sum_total_debt": row.get("sum_total_debt") or Decimal("0.00"),
                    "sum_seller_asis_value": row.get("sum_seller_asis_value") or Decimal("0.00"),
                    "label": label,
                })
            return results
        except Exception:
            # Graceful degradation: log and continue with equal-width fallback below
            logger.warning(
                "NTILE-based stratification failed for seller_id=%s trade_id=%s; falling back to equal-width bands",
                seller_id,
                trade_id,
                exc_info=True,
            )

    # Secondary fallback: Python equal-frequency (quantile) banding for UX-consistent bands
    try:
        return _quantile_bands_python(qs, bands)
    except Exception:
        logger.warning(
            "Python quantile fallback failed for seller_id=%s trade_id=%s; using equal-width bins",
            seller_id,
            trade_id,
            exc_info=True,
        )

    # Fallback: equal-width bands from min/max
    stats = qs.aggregate(min_v=Min("current_balance"), max_v=Max("current_balance"))
    min_v: Decimal = stats.get("min_v") or Decimal("0.00")
    max_v: Decimal = stats.get("max_v") or Decimal("0.00")

    # Guard: if all values equal, return single band (include all three sums)
    if min_v == max_v:
        count_only = qs.count()
        sums = qs.aggregate(
            upb=Coalesce(Sum("current_balance"), zero_dec),
            td=Coalesce(Sum("total_debt"), zero_dec),
            asis=Coalesce(Sum("seller_asis_value"), zero_dec),
        )
        return [{
            "key": "1",
            "index": 1,
            "lower": min_v,
            "upper": max_v,
            "count": int(count_only),
            "sum_current_balance": sums.get("upb") or Decimal("0.00"),
            "sum_total_debt": sums.get("td") or Decimal("0.00"),
            "sum_seller_asis_value": sums.get("asis") or Decimal("0.00"),
            "label": _rounded_range_label(min_v, max_v),
        }]

    width = (max_v - min_v) / Decimal(bands)

    # Build bin thresholds [min + i*width, min + (i+1)*width)
    thresholds: List[Decimal] = [min_v + (width * Decimal(i)) for i in range(bands + 1)]

    # Aggregate each bin using conditional filters to avoid client-side loops
    # Note: we use inclusive upper bound on the last bin to capture max_v
    results: List[Dict[str, object]] = []
    # Precompute sums and counts per bin via looped queries (kept simple for clarity)
    # If performance becomes a concern, this can be rewritten with a single annotate+Case.
    for i in range(bands):
        lo = thresholds[i]
        hi = thresholds[i + 1]
        if i < bands - 1:
            bin_qs = qs.filter(current_balance__gte=lo, current_balance__lt=hi)
        else:
            bin_qs = qs.filter(current_balance__gte=lo, current_balance__lte=hi)
        cnt = bin_qs.count()
        aggs = bin_qs.aggregate(
            upb=Coalesce(Sum("current_balance"), zero_dec),
            td=Coalesce(Sum("total_debt"), zero_dec),
            asis=Coalesce(Sum("seller_asis_value"), zero_dec),
        )
        results.append({
            "key": str(i + 1),
            "index": i + 1,
            "lower": lo,
            "upper": hi,
            "count": int(cnt),
            "sum_current_balance": aggs.get("upb") or Decimal("0.00"),
            "sum_total_debt": aggs.get("td") or Decimal("0.00"),
            "sum_seller_asis_value": aggs.get("asis") or Decimal("0.00"),
            # First band '< $X', last band '> $Y'
            "label": _band_label(lo, hi, i + 1, bands),
        })

    # Filter out empty bands if any (possible with sparse data)
    results = [r for r in results if r["count"] > 0]
    return results


# Future: generic stratifier for arbitrary numeric field names can be added here,
# following the same NTILE-first, equal-width-fallback pattern.
