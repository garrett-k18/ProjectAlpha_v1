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
from core.models.propertycfs import HistoricalPropertyCashFlow


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
# TDTV (Total Debt to Value) Calculations
# -------------------------------------------------------------------------------------------------

class TdtvDataItem(TypedDict):
    """Type definition for TDTV data items returned by get_tdtv_data."""
    id: str
    total_debt: Decimal
    seller_arv_value: Decimal
    tdtv: Decimal


def get_tdtv_data(seller_id: int, trade_id: int) -> List[TdtvDataItem]:
    """Calculate TDTV (Total Debt to Value) for each loan in the selected pool.
    
    TDTV is calculated as total_debt / seller_arv_value.
    
    Args:
        seller_id: Seller primary key to filter by.
        trade_id: Trade primary key to filter by.
        
    Returns:
        List of dictionaries containing id, total_debt, seller_arv_value, and tdtv
    
    Notes:
        - TDTV is expressed as a percentage (0-100)
        - If seller_arv_value is zero or null, tdtv will be null to avoid division by zero
        - Calculation is done in the database for efficiency
    """
    # Get the base queryset for the selected seller and trade
    qs = sellertrade_qs(seller_id, trade_id)
    
    # Annotate with TDTV calculation
    # Convert to percentage and round to 1 decimal place
    # Handle division by zero by using Case/When
    qs = qs.annotate(
        tdtv=Case(
            # When denominator exists and is not zero
            When(
                seller_arv_value__gt=0,
                then=ExpressionWrapper(
                    (F('total_debt') * 100) / F('seller_arv_value'),
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
            'total_debt': item.total_debt or Decimal('0.00'),
            'seller_arv_value': item.seller_arv_value or Decimal('0.00'),
            'tdtv': item.tdtv  # Keep as null if calculation wasn't possible
        })
    
    return result


# -------------------------------------------------------------------------------------------------
# Individual Asset Metrics (for single asset analysis)
# -------------------------------------------------------------------------------------------------

def get_single_asset_metrics(asset_id: int) -> Dict[str, Any]:
    """Calculate key metrics for a single asset.
    
    Args:
        asset_id: SellerRawData asset_hub_id (primary key)
        
    Returns:
        Dict containing calculated metrics:
        - ltv: Loan to Value percentage
        - tdtv: Total Debt to Value percentage  
        - days_dlq: Days delinquent
        - months_dlq: Months delinquent (calculated from days)
        - is_delinquent: Boolean if asset is delinquent
        - is_foreclosure: Boolean if FC flag is active
        - has_equity: Boolean if asset has positive equity
    """
    try:
        # Get the asset record using asset_hub as the primary key
        asset = SellerRawData.objects.get(asset_hub=asset_id)
        
        # Calculate LTV (current_balance / seller_asis_value)
        ltv = None
        if asset.seller_asis_value and asset.seller_asis_value > 0:
            ltv = float((asset.current_balance or Decimal('0')) / asset.seller_asis_value * 100)
        
        # Calculate TDTV (total_debt / seller_arv_value)
        tdtv = None
        if asset.seller_arv_value and asset.seller_arv_value > 0:
            tdtv = float((asset.total_debt or Decimal('0')) / asset.seller_arv_value * 100)
        
        # Calculate days delinquent
        days_dlq = 0
        if asset.as_of_date and asset.next_due_date:
            delta = asset.as_of_date - asset.next_due_date
            days_dlq = delta.days
        
        # Calculate months delinquent (approximate: days / 30)
        months_dlq = max(0, days_dlq // 30) if days_dlq > 0 else 0
        
        # Determine status flags
        is_delinquent = days_dlq > 0
        is_foreclosure = bool(asset.fc_flag) if hasattr(asset, 'fc_flag') else False
        
        # Determine if asset has equity (LTV < 100%)
        has_equity = ltv is not None and ltv < 100
        
        return {
            'ltv': ltv,
            'tdtv': tdtv,
            'days_dlq': days_dlq,
            'months_dlq': months_dlq,
            'is_delinquent': is_delinquent,
            'is_foreclosure': is_foreclosure,
            'has_equity': has_equity,
            'delinquency_months': months_dlq,  # Alias for compatibility
        }
        
    except SellerRawData.DoesNotExist:
        # Return null metrics if asset not found
        return {
            'ltv': None,
            'tdtv': None,
            'days_dlq': 0,
            'months_dlq': 0,
            'is_delinquent': False,
            'is_foreclosure': False,
            'has_equity': None,
            'delinquency_months': 0,
        }


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


def acq_seller_orig_cap_rate(seller_id: int, asset_hub_id: int) -> Decimal:
    """
    Calculate Cap Rate for a subject asset using the latest available data.

    What:
        Cap Rate (%) = (NOI / Market Value) * 100

    How:
        - Pull the latest HistoricalPropertyCashFlow row for the given AssetIdHub (by year desc)
        - Compute NOI from the cash flow row
        - Use SellerRawData.origination_value as market value proxy
        - Compute Cap Rate as (NOI / value) * 100

    Safety:
        - Returns Decimal('0.00') if any required value is missing or non-positive

    Args:
        asset_hub_id: Primary key of AssetIdHub

    Returns:
        Decimal: Cap Rate percentage rounded to 2 decimals (e.g., 6.25 for 6.25%)
    """
    # TODO(date-selection): Align NOI year and origination value date
    # - If multiple origination-related values exist, select the value whose date
    #   is closest to the cash flow year (or within a configured tolerance window).
    # - Consider falling back to a valuation snapshot if origination_value missing.
    # - Make date selection rules configurable per asset/product.

    # Get latest historical cash flow for NOI
    hpcf = (
        HistoricalPropertyCashFlow.objects
        .filter(asset_hub_id=asset_hub_id)
        .order_by('-year', '-id')
        .first()
    )
    if not hpcf:
        return Decimal('0.00')

    noi = hpcf.net_operating_income()

    # Get origination value from SellerRawData
    seller = SellerRawData.objects.filter(id=seller_id).only('origination_value').first()
    if not seller or not seller.origination_value:
        return Decimal('0.00')

    value = seller.origination_value if isinstance(seller.origination_value, Decimal) else Decimal(str(seller.origination_value))
    if value <= 0:
        return Decimal('0.00')

    cap = (noi / value) * Decimal('100')
    return cap.quantize(Decimal('0.01'))


def acq_seller_as_is_cap_rate(seller_id: int, asset_hub_id: int) -> Decimal:
    """
    Calculate Cap Rate using the current seller as-is value (SellerRawData.seller_asis_value).

    Args:
        seller_id: SellerRawData primary key
        asset_hub_id: AssetIdHub primary key used to locate NOI from HistoricalPropertyCashFlow

    Returns:
        Decimal percentage (e.g., 7.50 for 7.5%), or 0.00 if unavailable.
    """
    # TODO(date-selection): Align NOI timing with seller as-is value date
    # - Prefer seller_value_date-aligned snapshots; if multiple as-is values exist,
    #   pick the one closest to cash flow year or reporting date.
    # - Consider using latest market valuation as fallback when seller as-is is stale.
    # - Document tie-breaker and tolerance rules.
    # NOI from latest historical cash flow
    hpcf = (
        HistoricalPropertyCashFlow.objects
        .filter(asset_hub_id=asset_hub_id)
        .order_by('-year', '-id')
        .first()
    )
    if not hpcf:
        return Decimal('0.00')
    
    # Compute NOI from latest historical cash flow
    noi = hpcf.net_operating_income()
    
    # Seller as-is value
    seller = SellerRawData.objects.filter(id=seller_id).only('seller_asis_value').first()
    if not seller or not seller.seller_asis_value:
        return Decimal('0.00')

    value = seller.seller_asis_value if isinstance(seller.seller_asis_value, Decimal) else Decimal(str(seller.seller_asis_value))
    if value <= 0:
        return Decimal('0.00')

    cap = (noi / value) * Decimal('100')
    return cap.quantize(Decimal('0.01'))
