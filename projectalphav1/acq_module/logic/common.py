"""
acq_module.logic.common

Centralized query/aggregation helpers for SellerRawData selections.

Docs referenced:
- Django ORM aggregation: https://docs.djangoproject.com/en/stable/topics/db/aggregation/
- Query Expressions and database functions (Upper, Substr, Coalesce):
  https://docs.djangoproject.com/en/stable/ref/models/expressions/
  https://docs.djangoproject.com/en/stable/ref/models/database-functions/

These helpers keep selection logic DRY and consistent across views/endpoints.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Dict, Iterable

from django.db.models import (
    QuerySet,
    Sum,
    Count,
    Value,
    DecimalField,
)
from django.db.models.functions import Upper, Substr, Coalesce

from ..models.seller import SellerRawData


def sellertrade_qs(seller_id: int, trade_id: int, view: str = 'snapshot') -> QuerySet[SellerRawData]:
    """Build the base queryset for a specific seller + trade pair.

    Args:
        seller_id: Seller primary key to filter by.
        trade_id: Trade primary key to filter by.
        view: View filter ('snapshot', 'all', 'valuations', 'drops').
              - 'drops': Show only dropped assets (is_dropped=True)
              - All others: Show only active assets (is_dropped=False)

    Returns:
        QuerySet[SellerRawData]: Base queryset for the exact seller+trade pair,
                                 filtered by drop status based on view.

    Notes:
        - Intentionally minimal. Do not exclude/annotate here so this can be
          reused by multiple callsites (raw rows, aggregates, etc.).
    """
    # Filter strictly by the seller and trade foreign keys
    qs = SellerRawData.objects.filter(seller_id=seller_id, trade_id=trade_id)
    
    # Filter by drop status based on view
    if view == 'drops':
        # Drops view: show only dropped assets
        qs = qs.filter(is_dropped=True)
    else:
        # All other views: exclude dropped assets
        qs = qs.filter(is_dropped=False)
    
    return qs


def aggregates_by_state(seller_id: int, trade_id: int) -> QuerySet[Dict[str, object]]:
    """Aggregate per-state counts and financial sums for a selection.

    Groups by normalized 2-letter uppercase state code and computes:
    - count
    - sum_current_balance
    - sum_total_debt
    - sum_seller_asis_value

    Args:
        seller_id: Seller primary key to filter by.
        trade_id: Trade primary key to filter by.

    Returns:
        QuerySet of dictionaries with keys:
            {
              'state': 'CA',
              'count': int,
              'sum_current_balance': Decimal,
              'sum_total_debt': Decimal,
              'sum_seller_asis_value': Decimal,
            }
        Ordered by -count (descending).
    """
    # Start from the shared base queryset
    base_qs: QuerySet[SellerRawData] = sellertrade_qs(seller_id, trade_id)

    # Exclude blank/NULL states to avoid grouping noise
    filtered_qs = (
        base_qs
        .exclude(state__isnull=True)
        .exclude(state__exact='')
    )

    # Normalize to 2-letter uppercase code via DB functions for consistent grouping
    normalized_qs = filtered_qs.annotate(
        state_code=Upper(Substr('state', 1, 2))  # e.g., 'California' -> 'CA'
    )

    # Define a Decimal 0.00 with matching output_field to keep DB adapters happy
    zero_dec = Value(Decimal('0.00'), output_field=DecimalField(max_digits=15, decimal_places=2))

    # Group and aggregate
    aggregated = (
        normalized_qs
        .values('state_code')
        .annotate(
            count=Count('id'),
            sum_current_balance=Coalesce(Sum('current_balance'), zero_dec),
            sum_total_debt=Coalesce(Sum('total_debt'), zero_dec),
            sum_seller_asis_value=Coalesce(Sum('seller_asis_value'), zero_dec),
        )
        .order_by('-count')
    )

    # For a friendlier key name in the output, rename 'state_code' -> 'state'
    # Note: Evaluating here will execute the query once. If the caller prefers
    # a lazy QuerySet, they can work with the annotated version above directly.
    def _row_adapter(row: Dict[str, object]) -> Dict[str, object]:
        # Copy and remap keys for clarity in API responses
        out = dict(row)
        out['state'] = out.pop('state_code')
        return out

    # Return a re-evaluated QuerySet-like iterable by materializing then adapting.
    # If strict laziness is required, callers can adapt themselves.
    adapted_rows = map(_row_adapter, aggregated)

    # Convert back to a list-like iterable; callers can wrap with list() if needed.
    # We keep it as an iterable to avoid immediate materialization by default.
    # Type-wise this is Iterable[Dict[str, object]], but we annotate as QuerySet-like for symmetry.
    return adapted_rows  # type: ignore[return-value]
