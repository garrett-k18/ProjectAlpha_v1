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

from django.db.models import (
    F,
    ExpressionWrapper,
    DecimalField,
    Case,
    When,
    Value,
    DurationField,
    IntegerField,
    FloatField,
)
from django.db.models.functions import Coalesce, Cast, Extract

from .common import sellertrade_qs
from core.models.assumptions import StateReference
from acq_module.models.seller import SellerRawData


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


# -------------------------------------------------------------------------------------------------
# Days Delinquent (days_dlq)
# -------------------------------------------------------------------------------------------------

class DlqDataItem(TypedDict):
    """Type definition for Days DLQ items.

    Each item represents a single loan, identified by its primary key string, and the
    number of days delinquent calculated as the difference between the reporting
    date (as_of_date) and the contractual next_due_date.
    """
    id: str
    days_dlq: int


def get_days_dlq_data(seller_id: int, trade_id: int) -> List[DlqDataItem]:
    """Compute days delinquent for every loan in a seller+trade selection.

    Calculation:
    - days_dlq = as_of_date - next_due_date (measured in days)

    Implementation details:
    - We reuse the base queryset from sellertrade_qs(seller_id, trade_id) to ensure strict
      scoping to the selected pool.
    - Date subtraction is performed in the database to produce a Duration/interval. We then
      extract its total seconds (epoch) and divide by 86,400 to convert to days. Finally, we
      cast to an IntegerField to return whole days.
    - Negative values are possible if next_due_date is in the future relative to as_of_date;
      we keep them as-is for transparency.

    Args:
        seller_id: Seller primary key to filter by.
        trade_id: Trade primary key to filter by.

    Returns:
        List[DlqDataItem]: [{ 'id': str(pk), 'days_dlq': int }, ...]
    """
    # Build the base queryset for the selected seller and trade. This ensures we only operate
    # on the intended data slice and keeps logic consistent across call sites.
    qs = sellertrade_qs(seller_id, trade_id)

    # Step 1: Create an interval (duration) by subtracting dates in the database. Using
    # ExpressionWrapper ensures the database performs the calculation efficiently.
    qs = qs.annotate(
        dlq_interval=ExpressionWrapper(
            F('as_of_date') - F('next_due_date'),  # interval: how many days between reporting and next due
            output_field=DurationField(),           # explicit output type so Django knows this is an interval
        )
    )

    # Step 2: Convert the interval to total days. On PostgreSQL, EXTRACT(EPOCH FROM interval)
    # returns seconds. We divide by 86400 to get days, then cast to integer for whole-day count.
    qs = qs.annotate(
        days_dlq=Cast(
            ExpressionWrapper(
                Extract(F('dlq_interval'), 'epoch') / 86400.0,  # seconds -> days (float)
                output_field=FloatField(),
            ),
            output_field=IntegerField(),
        )
    )

    # Step 3: Build the response payload. Ensure types are clean and safe.
    result: List[DlqDataItem] = []
    for item in qs:
        # item.days_dlq is already an int due to the Cast above; coalesce to 0 if missing
        d = int(getattr(item, 'days_dlq', 0) or 0)
        result.append({
            'id': str(item.id),           # normalize PK to string for frontend
            'days_dlq': d,                # whole days delinquent
        })

    return result

