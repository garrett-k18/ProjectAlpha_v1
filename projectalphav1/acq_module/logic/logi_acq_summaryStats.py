"""
State Summary helpers for acquisition assets.

Purpose:
- Provide small, single-purpose helpers to compute state-based summaries.
- No normalization here; state normalization is handled upstream.

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
from .common import sellertrade_qs, annotate_seller_valuations

# Module logger for diagnostics (widgets, summaries)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pool Level Summary Stats
# ---------------------------------------------------------------------------
def total_assets(seller_id: int, trade_id: int) -> int:
    """Return the row count for the selected seller and trade.
    
    WHAT: Count active (KEEP) assets in the pool
    WHY: Pool summary should only include assets in active bidding
    HOW: sellertrade_qs() excludes DROP status by default
    
    Note: sellertrade_qs(view='snapshot') filters acq_status != DROP automatically

    Django docs (Aggregation/Count): https://docs.djangoproject.com/en/stable/topics/db/aggregation/
    """
    # WHAT: Get queryset filtered to seller+trade, excluding dropped assets
    # WHY: sellertrade_qs() defaults to view='snapshot' which excludes DROP status
    # HOW: Filter applies acq_status != DROP automatically
    qs = annotate_seller_valuations(
        sellertrade_qs(seller_id, trade_id)
    )
    
    try:
        # WHAT: Ask database for count of matching rows
        # WHY: Efficient COUNT(*) query, returns int
        count = qs.count()
    except Exception as e:
        # WHY: Log error and return 0 if query fails
        logger.error("[pool-summary] queryset count failed seller=%s trade=%s: %s", seller_id, trade_id, e)
        count = 0
    
    return count
    
def total_current_balance(seller_id: int, trade_id: int) -> Decimal:
    """Return the sum of current_balance for the selected seller and trade.

    Null-safe via Coalesce to keep a Decimal result.
    Django docs (Coalesce): https://docs.djangoproject.com/en/stable/ref/models/database-functions/#coalesce
    """
    qs = sellertrade_qs(seller_id, trade_id)
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    agg = qs.aggregate(total=Coalesce(Sum("loan__current_balance"), zero_dec))
    return agg["total"]

def total_debt(seller_id: int, trade_id: int) -> Decimal:
    """Return the sum of total_debt for the selected seller and trade (null-safe)."""
    qs = sellertrade_qs(seller_id, trade_id)
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    agg = qs.aggregate(total=Coalesce(Sum("loan__total_debt"), zero_dec))
    return agg["total"]

def total_seller_asis_value(seller_id: int, trade_id: int) -> Decimal:
    """Return the sum of seller_asis_value for the selected seller and trade (null-safe)."""
    qs = annotate_seller_valuations(sellertrade_qs(seller_id, trade_id))
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
    qs = annotate_seller_valuations(sellertrade_qs(seller_id, trade_id))
    # Define a typed zero Decimal so Coalesce preserves Decimal typing in DB adapters
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    # Execute a single aggregate call to compute all required metrics
    agg = qs.aggregate(
        assets=Count("asset_hub"),
        current_balance=Coalesce(Sum("loan__current_balance"), zero_dec),
        total_debt=Coalesce(Sum("loan__total_debt"), zero_dec),
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
    agg = qs.aggregate(upb_ltv=Coalesce(Sum("loan__current_balance"), zero_dec))
    return agg["upb_ltv"]

def td_ltv(seller_id: int, trade_id: int) -> Decimal:
    """Return the Total Debt LTV for the selected seller and trade."""
    qs = sellertrade_qs(seller_id, trade_id)
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    agg = qs.aggregate(td_ltv=Coalesce(Sum("loan__total_debt"), zero_dec))
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
        .exclude(property__state__isnull=True)
        .exclude(property__state__exact="")
    )
    # Ask the database for distinct state values and sort ascending
    distinct_states = qs.values_list("property__state", flat=True).distinct().order_by("property__state")
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
        .exclude(property__state__isnull=True)
        .exclude(property__state__exact="")
    )
    return qs.values("property__state").distinct().count()


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
        .exclude(property__state__isnull=True)
        .exclude(property__state__exact="")
    )
    # Group by state and compute a row count per group
    aggregated = (
        qs.values("property__state")
        .annotate(
            count=Count("pk"),
        )
        .order_by("-count")
    )
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
        .exclude(property__state__isnull=True)
        .exclude(property__state__exact="")
    )
    # Define a typed zero literal so DB adapters keep Decimal typing consistent
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    # Group by state and compute sums, ordering by the sum descending
    aggregated = (
        qs.values("property__state")
        .annotate(sum_current_balance=Coalesce(Sum("loan__current_balance"), zero_dec))
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
        .exclude(property__state__isnull=True)
        .exclude(property__state__exact="")
    )
    # Typed zero for Coalesce to ensure Decimal type
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    # Group and sum, then order by the sum descending
    aggregated = (
        qs.values("property__state")
        .annotate(sum_total_debt=Coalesce(Sum("loan__total_debt"), zero_dec))
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
        annotate_seller_valuations(
            sellertrade_qs(seller_id, trade_id)
        )
        .exclude(property__state__isnull=True)
        .exclude(property__state__exact="")
    )
    # Typed zero for Coalesce to ensure Decimal type
    zero_dec = Value(Decimal("0.00"), output_field=DecimalField(max_digits=15, decimal_places=2))
    # Group and sum, then order by the sum descending
    aggregated = (
        qs.values("property__state")
        .annotate(sum_seller_asis_value=Coalesce(Sum("seller_asis_value"), zero_dec))
        .order_by("-sum_seller_asis_value")
    )
    # Return list of dicts
    return list(aggregated)


# ---------------------------------------------------------------------------
# Valuation Completion Counts (by source)
# ---------------------------------------------------------------------------

def valuation_completion_summary(seller_id: int, trade_id: int) -> Dict[str, int]:
    """Return counts of assets with valuations by source.
    
    WHAT: Count how many assets have valuations from each source
    WHY: Valuation Center needs completion metrics per source type
    HOW: Query both SellerRawData and Valuation models, count distinct assets
    
    Sources counted:
    - seller: From SellerRawData.seller_asis_value (not null)
    - broker: From Valuation where source='broker'
    - bpo: From Valuation where source in ('BPOI', 'BPOE', 'desktop', 'appraisal') - count only 1 per asset
    - internal_uw: From Valuation where source='internalInitialUW'
    - reconciled: Assets with seller + (broker OR bpo) + internal_uw
    
    Output shape:
        {
          'seller_count': 500,        # Assets with seller_asis_value
          'broker_count': 150,         # Assets with broker valuation
          'bpo_count': 200,            # Assets with any BPO-type valuation
          'internal_uw_count': 100,    # Assets with internal UW valuation
          'reconciled_count': 75,      # Assets with all three sources
        }
    
    Django docs:
        - Aggregation: https://docs.djangoproject.com/en/stable/topics/db/aggregation/
        - Q objects: https://docs.djangoproject.com/en/stable/topics/db/queries/#complex-lookups-with-q-objects
    """
    from django.db.models import Q, Exists, OuterRef
    from core.models.model_co_valuations import Valuation
    
    # WHAT: Get base queryset of active assets (excludes DROP status)
    # WHY: Only count valuations for assets in active bidding pool
    qs = sellertrade_qs(seller_id, trade_id)
    
    # WHAT: Count assets with seller values (from Valuation)
    # WHY: Seller provides initial as-is valuations on their tape
    seller_count = qs.filter(seller_asis_value__isnull=False).count()
    
    # WHAT: Count assets with broker valuations (from Valuation model)
    # WHY: Broker valuations are stored separately in unified Valuation table
    # HOW: Check if asset_hub has related Valuation with source='broker'
    broker_subquery = Valuation.objects.filter(
        asset_hub=OuterRef('asset_hub'),
        source=Valuation.Source.BROKER
    )
    broker_count = qs.filter(Exists(broker_subquery)).count()
    
    # WHAT: Count assets with ANY BPO-type valuation (BPOI, BPOE, desktop, appraisal)
    # WHY: Multiple BPO sources possible, but only count 1 per asset
    # HOW: Use Q objects to OR multiple source types, then check existence
    bpo_sources = [
        Valuation.Source.BPO_INTERIOR,
        Valuation.Source.BPO_EXTERIOR,
        Valuation.Source.DESKTOP,
        Valuation.Source.APPRAISAL,
    ]
    bpo_subquery = Valuation.objects.filter(
        asset_hub=OuterRef('asset_hub'),
        source__in=bpo_sources
    )
    bpo_count = qs.filter(Exists(bpo_subquery)).count()
    
    # WHAT: Count assets with internal initial UW valuations
    # WHY: Internal underwriting team provides initial valuations
    # HOW: Check for Valuation with source='internalInitialUW'
    internal_uw_subquery = Valuation.objects.filter(
        asset_hub=OuterRef('asset_hub'),
        source=Valuation.Source.INTERNAL_INITIAL_UW
    )
    internal_uw_count = qs.filter(Exists(internal_uw_subquery)).count()
    
    # WHAT: Count assets with Internal Initial UW values (reconciled)
    # WHY: Reconciled means assets have an internal UW valuation with asis_value OR arv_value or both
    # HOW: Check for Internal UW valuations where at least one value field is not null
    reconciled_subquery = Valuation.objects.filter(
        asset_hub=OuterRef('asset_hub'),
        source=Valuation.Source.INTERNAL_INITIAL_UW
    ).filter(
        Q(asis_value__isnull=False) | Q(arv_value__isnull=False)
    )
    reconciled_count = qs.filter(Exists(reconciled_subquery)).count()
    
    # WHAT: Count assets with grade assigned to Internal Initial UW valuation
    # WHY: Track completion of valuation grading process
    # HOW: Check for Internal UW valuations with grade FK not null
    graded_subquery = Valuation.objects.filter(
        asset_hub=OuterRef('asset_hub'),
        source=Valuation.Source.INTERNAL_INITIAL_UW,
        grade__isnull=False
    )
    graded_count = qs.filter(Exists(graded_subquery)).count()
    
    return {
        'seller_count': seller_count,
        'broker_count': broker_count,
        'bpo_count': bpo_count,
        'internal_uw_count': internal_uw_count,
        'reconciled_count': reconciled_count,
        'graded_count': graded_count,
    }


# ---------------------------------------------------------------------------
# Collateral & Title Center Metrics (PLACEHOLDER - needs business logic definition)
# ---------------------------------------------------------------------------

def collateral_completion_summary(seller_id: int, trade_id: int) -> Dict[str, int]:
    """Return collateral check completion counts.
    
    WHAT: Count assets with various collateral checks completed
    WHY: Collateral Center needs completion metrics
    HOW: TODO - Define what constitutes each check type
    
    PLACEHOLDER: Currently returns zeros - needs business logic definition:
    - What is "ordered"? (collateral inspections ordered?)
    - What is "photos"? (property photos received?)
    - What is "repairs"? (repair estimates completed?)
    - What is "reviewed"? (collateral reviews completed?)
    
    Output shape:
        {
          'ordered': 0,           # Collateral inspections ordered
          'photos': 0,            # Properties with photos
          'repairs': 0,           # Properties needing repairs
          'repair_cost': 0,       # Total estimated repair cost
          'reviewed': 0,          # Collateral reviews completed
        }
    """
    # TODO: Implement actual business logic
    # For now, return zeros as placeholders
    return {
        'ordered': 0,
        'photos': 0,
        'repairs': 0,
        'repair_cost': 0,
        'reviewed': 0,
    }


def title_completion_summary(seller_id: int, trade_id: int) -> Dict[str, int]:
    """Return title check completion counts.
    
    WHAT: Count assets with various title checks completed
    WHY: Title Center needs completion metrics
    HOW: TODO - Define what constitutes each check type
    
    PLACEHOLDER: Currently returns zeros - needs business logic definition:
    - What is "ordered"? (title searches ordered?)
    - What is "clear"? (titles with no issues?)
    - What is "issues"? (titles with problems?)
    - What is "critical"? (titles with critical issues?)
    - What is "reviewed"? (title reviews completed?)
    
    Output shape:
        {
          'ordered': 0,           # Title searches ordered
          'clear': 0,             # Titles with no issues
          'issues': 0,            # Titles with issues
          'critical': 0,          # Titles with critical issues
          'reviewed': 0,          # Title reviews completed
        }
    """
    # TODO: Implement actual business logic
    # For now, return zeros as placeholders
    return {
        'ordered': 0,
        'clear': 0,
        'issues': 0,
        'critical': 0,
        'reviewed': 0,
    }
