"""
Service layer for composing SellerRawData rows for AG Grid.

This module isolates data-join logic so views remain thin.
Follows the same pattern as am_module.services.asset_inventory.

Docs reviewed:
- Django QuerySet API: https://docs.djangoproject.com/en/stable/ref/models/querysets/
- DRF Filtering & Pagination: https://www.django-rest-framework.org/api-guide/filtering/
"""
from __future__ import annotations

from typing import Optional
from django.db.models import QuerySet, Q
from ..models.seller import SellerRawData

# Fields used by quick filter 'q' - common searchable text fields
QUICK_FILTER_FIELDS = (
    "street_address",
    "city", 
    "state",
    "zip",
    "borrower1_last",
    "borrower1_first",
    "borrower2_last", 
    "borrower2_first",
)


def build_queryset(
    *,
    seller_id: int,
    trade_id: int,
    q: Optional[str] = None,
    filters: Optional[dict] = None,
    ordering: Optional[str] = None,
    view: str = 'snapshot',
) -> QuerySet[SellerRawData]:
    """
    Return a QuerySet of SellerRawData for the given seller and trade.
    
    Data siloing requirement: Only return data when BOTH seller_id and trade_id are provided.
    
    Args:
        seller_id: Required seller ID for data siloing
        trade_id: Required trade ID for data siloing
        q: Optional quick filter text across common fields
        filters: Optional dict of exact-match filters
        ordering: Optional comma-separated ordering fields (supports -prefix for desc)
        view: View filter ('snapshot', 'all', 'valuations', 'drops')
              - 'drops': Show only dropped assets (is_dropped=True)
              - All others: Show only active assets (is_dropped=False)
    
    Returns:
        QuerySet of SellerRawData with proper joins for valuation access
    """
    # Data siloing: enforce both IDs are required
    if not seller_id or not trade_id:
        return SellerRawData.objects.none()
    
    # Base queryset with necessary joins for valuations
    qs = (
        SellerRawData.objects
        .filter(seller_id=seller_id, trade_id=trade_id)
        .select_related('seller', 'trade', 'asset_hub')  # Optimize joins for serializer access
        .prefetch_related('asset_hub__valuations')  # Bring valuations into memory for serializer
    )
    
    # Filter by drop status based on view
    if view == 'drops':
        # Drops view: show only dropped assets
        qs = qs.filter(is_dropped=True)
    else:
        # All other views: exclude dropped assets
        qs = qs.filter(is_dropped=False)
    
    # Apply quick filter across text fields
    if q:
        q_obj = Q()
        for field in QUICK_FILTER_FIELDS:
            q_obj |= Q(**{f"{field}__icontains": q})
        
        # Also try to match numeric sellertape_id if q is digits
        if q.isdigit():
            q_obj |= Q(sellertape_id=int(q))
        
        qs = qs.filter(q_obj)
    
    # Apply exact-match filters
    if filters:
        allowed = {k: v for k, v in filters.items() if v not in (None, "")}
        if allowed:
            qs = qs.filter(**allowed)
    
    # Apply ordering
    if ordering:
        order_fields: list[str] = []
        for part in str(ordering).split(","):
            part = part.strip()
            if not part:
                continue
            
            desc = part.startswith("-")
            key = part[1:] if desc else part
            
            # Translate any friendly aliases to actual ORM paths
            # For now, pass through field names directly
            model_field = key
            
            order_fields.append(f"-{model_field}" if desc else model_field)
        
        if order_fields:
            qs = qs.order_by(*order_fields)
    else:
        # Default ordering by creation time (newest first)
        qs = qs.order_by('-created_at')
    
    return qs


def get_seller_queryset() -> QuerySet:
    """Return queryset for seller dropdown options."""
    return SellerRawData.objects.select_related('seller').values_list(
        'seller_id', 'seller__name'
    ).distinct().order_by('seller__name')


def get_trade_queryset(seller_id: int) -> QuerySet:
    """Return queryset for trade dropdown options for a given seller."""
    if not seller_id:
        return SellerRawData.objects.none()
    
    return SellerRawData.objects.filter(
        seller_id=seller_id
    ).select_related('trade').values_list(
        'trade_id', 'trade__trade_name'  
    ).distinct().order_by('-trade__created_at')  # Most recent trades first
