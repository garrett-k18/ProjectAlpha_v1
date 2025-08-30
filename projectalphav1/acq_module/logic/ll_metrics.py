# this is for loan level metrics like LTVs, days months delingquent etc

"""
acq_module.logic.ll_metrics

Logic for loan-level metrics calculations such as LTV (Loan-to-Value),
days/months delinquent, and other property-specific metrics.

These functions operate on SellerRawData instances and compute
derived values that aren't directly stored in the database.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional, Any, TypedDict

from django.db.models import F, ExpressionWrapper, DecimalField, Case, When, Value
from django.db.models.functions import Coalesce

from .common import sellertrade_qs


class LtvDataItem(TypedDict):
    """Type definition for LTV data items returned by get_ltv_data."""
    id: str
    current_balance: Decimal
    seller_asis_value: Decimal
    ltv: Decimal


def get_ltv_data(seller_id: int, trade_id: int) -> List[LtvDataItem]:
    """Calculate LTV (Loan-to-Value) for each loan in the selected pool.
    
    LTV is calculated as current_balance / seller_asis_value.
    
    Args:
        seller_id: Seller primary key to filter by.
        trade_id: Trade primary key to filter by.
        
    Returns:
        List of dictionaries containing id, current_balance, seller_asis_value, and ltv
    
    Notes:
        - LTV is expressed as a percentage (0-100)
        - If seller_asis_value is zero or null, ltv will be null to avoid division by zero
        - Calculation is done in the database for efficiency
    """
    # Get the base queryset for the selected seller and trade
    qs = sellertrade_qs(seller_id, trade_id)
    
    # Annotate with LTV calculation
    # Convert to percentage and round to 1 decimal place
    # Handle division by zero by using Case/When
    qs = qs.annotate(
        ltv=Case(
            # When denominator exists and is not zero
            When(
                seller_asis_value__gt=0,
                then=ExpressionWrapper(
                    (F('current_balance') * 100) / F('seller_asis_value'),
                    output_field=DecimalField(max_digits=7, decimal_places=1)
                )
            ),
            # Otherwise null
            default=Value(None, output_field=DecimalField(max_digits=7, decimal_places=1))
        )
    )
    
    # Select only the fields we need for the frontend
    # Coalesce null values to zero for numeric fields
    result = []
    for item in qs:
        result.append({
            'id': str(item.id),
            'current_balance': item.current_balance or Decimal('0.00'),
            'seller_asis_value': item.seller_asis_value or Decimal('0.00'),
            'ltv': item.ltv  # Keep as null if calculation wasn't possible
        })
    
    return result


def get_ltv_scatter_data(seller_id: int, trade_id: int) -> List[LtvDataItem]:
    """Get LTV data specifically formatted for the LTV scatter chart.
    
    A wrapper around get_ltv_data that filters out records with null LTV values,
    which would not be useful in the scatter chart visualization.
    
    Args:
        seller_id: Seller primary key to filter by.
        trade_id: Trade primary key to filter by.
        
    Returns:
        Filtered list of LTV data items, excluding null LTV values
    """
    # Get all LTV data
    all_data = get_ltv_data(seller_id, trade_id)
    
    # Filter out items with null LTV values
    return [item for item in all_data if item['ltv'] is not None]
