"""
acq_module.logic.common

Centralized query helpers for SellerRawData selections.

These helpers keep selection logic DRY and consistent across views/endpoints.
"""
from __future__ import annotations

from django.db.models import QuerySet

from ..models.model_acq_seller import SellerRawData


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
    
    # Filter by acquisition status based on view
    if view == 'drops':
        qs = qs.filter(acq_status=SellerRawData.AcquisitionStatus.DROP)
    else:
        qs = qs.exclude(acq_status=SellerRawData.AcquisitionStatus.DROP)
    
    return qs


