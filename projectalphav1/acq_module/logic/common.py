"""
acq_module.logic.common

Centralized query helpers for acquisition asset selections.

These helpers keep selection logic DRY and consistent across views/endpoints.
"""
from __future__ import annotations

from django.db.models import QuerySet, OuterRef, Subquery

from core.models.model_co_valuations import Valuation

from ..models.model_acq_seller import AcqAsset


def sellertrade_qs(seller_id: int, trade_id: int, view: str = 'snapshot') -> QuerySet[AcqAsset]:
    """Build the base queryset for a specific seller + trade pair.

    Args:
        seller_id: Seller primary key to filter by.
        trade_id: Trade primary key to filter by.
        view: View filter ('snapshot', 'all', 'valuations', 'drops').
              - 'drops': Show only dropped assets (is_dropped=True)
              - All others: Show only active assets (is_dropped=False)

    Returns:
        QuerySet[AcqAsset]: Base queryset for the exact seller+trade pair,
                            filtered by drop status based on view.

    Notes:
        - Intentionally minimal. Do not exclude/annotate here so this can be
          reused by multiple callsites (raw rows, aggregates, etc.).
    """
    # Filter strictly by the seller and trade foreign keys
    qs = (
        AcqAsset.objects
        .filter(seller_id=seller_id, trade_id=trade_id)
        .select_related(
            'asset_hub',
            'seller',
            'trade',
            'loan',
            'property',
            'foreclosure_timeline',
        )
    )
    
    # Filter by acquisition status based on view
    if view == 'drops':
        qs = qs.filter(acq_status=AcqAsset.AcquisitionStatus.DROP)
    else:
        qs = qs.exclude(acq_status=AcqAsset.AcquisitionStatus.DROP)
    
    return qs


def annotate_seller_valuations(qs: QuerySet[AcqAsset]) -> QuerySet[AcqAsset]:
    """
    WHAT: Annotate a queryset with latest seller-provided valuation fields.
    WHY: Seller values now live in Valuation, not on AcqAsset/AcqLoan.
    HOW: Use correlated subqueries for seller-provided valuations.
    """
    # WHAT: Base queryset for seller valuations ordered by value_date/created_at
    # WHY: We want the most recent seller valuation per asset
    # HOW: Filter by asset_hub and seller-provided sources
    seller_vals = (
        Valuation.objects
        .filter(
            asset_hub_id=OuterRef('asset_hub_id'),
            source__in=[Valuation.Source.SELLER_PROVIDED, Valuation.Source.SELLER],
        )
        .order_by('-value_date', '-created_at')
    )

    # WHAT: Annotate seller as-is value
    # WHY: LTV and pool summaries need seller as-is values
    # HOW: Subquery grabs the first matching row
    qs = qs.annotate(
        seller_asis_value=Subquery(seller_vals.values('asis_value')[:1]),
        seller_arv_value=Subquery(seller_vals.values('arv_value')[:1]),
        seller_value_date=Subquery(seller_vals.values('value_date')[:1]),
    )

    return qs


