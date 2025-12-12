# this is for loan level metrics like LTVs, days months delingquent etc

"""
acq_module.logic.logi_acq_metrics

Logic for loan-level metrics calculations such as LTV (Loan-to-Value),
days/months delinquent, and other property-specific metrics.

These functions operate on SellerRawData instances and compute
derived values that aren't directly stored in the database.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, TypedDict, Tuple

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
from core.models.model_co_assumptions import StateReference, Servicer
from acq_module.models.model_acq_assumptions import TradeLevelAssumption, LoanLevelAssumption
from acq_module.models.model_acq_seller import SellerRawData
from core.models.propertycfs import HistoricalPropertyCashFlow
from acq_module.logic.logi_acq_purchasePrice import purchase_price
from acq_module.logic.logi_acq_summaryStats import count_upb_td_val_summary
from acq_module.logic.logi_acq_outcomespecific import reoAsIsOutcomeLogic, reoArvOutcomeLogic


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


def calculate_asset_model_data_fast(
    raw_data: SellerRawData,
    trade_assumption: Optional[TradeLevelAssumption],
    loan_assumption: Optional[LoanLevelAssumption],
    state_ref: Optional[StateReference],
    servicer: Optional[Servicer],
    bid_pct: Decimal = Decimal('0.85'),
) -> Dict[str, Any]:
    """
    Fast modeling calculations shared by the Modeling Center grid.
    """
    current_balance = raw_data.current_balance or Decimal('0')
    total_debt = raw_data.total_debt or Decimal('0')
    seller_asis = raw_data.seller_asis_value or Decimal('0')

    acq_price = current_balance * bid_pct

    servicing_transfer_months = 1
    if servicer and servicer.servicing_transfer_duration:
        servicing_transfer_months = servicer.servicing_transfer_duration

    foreclosure_months = 12
    if state_ref and state_ref.fc_state_months:
        foreclosure_months = state_ref.fc_state_months
    if loan_assumption and loan_assumption.reo_fc_duration_override_months:
        foreclosure_months = max(0, foreclosure_months + loan_assumption.reo_fc_duration_override_months)

    reo_marketing_months = 6
    if state_ref and state_ref.reo_marketing_duration:
        reo_marketing_months = state_ref.reo_marketing_duration

    reo_renovation_months = 3
    if state_ref and state_ref.rehab_duration:
        reo_renovation_months = state_ref.rehab_duration

    total_timeline_asis = servicing_transfer_months + foreclosure_months + reo_marketing_months
    total_timeline_arv = total_timeline_asis + reo_renovation_months

    proceeds_asis = raw_data.seller_asis_value or current_balance * Decimal('0.70')
    proceeds_arv = raw_data.seller_arv_value or proceeds_asis * Decimal('1.15')

    acq_costs = Decimal('0')
    if trade_assumption:
        acq_costs += trade_assumption.acq_broker_fees or Decimal('0')
        acq_costs += trade_assumption.acq_other_costs or Decimal('0')
        acq_costs += trade_assumption.acq_legal_cost or Decimal('0')
        acq_costs += trade_assumption.acq_dd_cost or Decimal('0')
        acq_costs += trade_assumption.acq_tax_title_cost or Decimal('0')

    monthly_carry = Decimal('450')
    carry_costs_asis = monthly_carry * Decimal(total_timeline_asis)
    carry_costs_arv = monthly_carry * Decimal(total_timeline_arv)

    legal_cost = Decimal('5000')
    if state_ref and state_ref.fc_legal_fees_avg:
        legal_cost = state_ref.fc_legal_fees_avg

    liq_pct = Decimal('0.06')
    if servicer and servicer.liqfee_pct:
        liq_pct += servicer.liqfee_pct
    liq_costs_asis = proceeds_asis * liq_pct
    liq_costs_arv = proceeds_arv * liq_pct

    total_costs_asis = acq_costs + carry_costs_asis + legal_cost + liq_costs_asis
    total_costs_arv = acq_costs + carry_costs_arv + legal_cost + liq_costs_arv

    net_pl_asis = proceeds_asis - acq_price - total_costs_asis
    net_pl_arv = proceeds_arv - acq_price - total_costs_arv

    moic_asis = Decimal('0')
    moic_arv = Decimal('0')
    if acq_price > 0:
        moic_asis = (proceeds_asis - total_costs_asis) / acq_price
        moic_arv = (proceeds_arv - total_costs_arv) / acq_price

    # WHAT: Calculate IRR and NPV from simplified cash flow series
    # WHY: Use cash flow timing to get accurate IRR/NPV (not just totals)
    # HOW: Create simplified monthly cash flow array and use outcome-specific logic
    
    def build_simplified_cashflow(
        acq_price: Decimal,
        total_costs: Decimal,
        proceeds: Decimal,
        duration_months: int,
        acq_costs: Decimal
    ) -> List[float]:
        """
        Build simplified monthly cash flow array for fast IRR/NPV calculation.
        
        WHAT: Creates a simplified monthly cash flow: period 0 = acquisition, monthly carry, final = proceeds
        WHY: Fast calculation without generating full detailed cash flow series
        HOW: Spread costs evenly across months, proceeds at end
        """
        if duration_months <= 0:
            return []
        
        # WHAT: Build simplified cash flow array
        # Period 0: Acquisition price + acquisition costs (negative = outflow)
        cash_flows = [float(-(acq_price + acq_costs))]
        
        # WHAT: Monthly periods: spread remaining costs evenly (negative = outflow)
        remaining_costs = float(total_costs - acq_costs)  # Total costs minus acq costs already in period 0
        monthly_carry = remaining_costs / duration_months if duration_months > 0 else 0.0
        
        for _ in range(duration_months):
            cash_flows.append(-monthly_carry)
        
        # WHAT: Final period: add proceeds (positive = inflow)
        cash_flows[-1] += float(proceeds)
        
        return cash_flows
    
    # WHAT: Use outcome-specific logic to calculate IRR and NPV
    # WHY: Each outcome type has its own class for better separation of concerns
    reo_asis_logic = reoAsIsOutcomeLogic()
    reo_arv_logic = reoArvOutcomeLogic()
    
    # WHAT: Build cash flows and calculate metrics for As-Is scenario
    cashflows_asis = build_simplified_cashflow(
        acq_price=acq_price,
        total_costs=total_costs_asis,
        proceeds=proceeds_asis,
        duration_months=total_timeline_asis,
        acq_costs=acq_costs
    )
    irr_asis = reo_asis_logic.calculate_irr(cashflows_asis)
    npv_asis = reo_asis_logic.calculate_npv(cashflows_asis)
    
    # WHAT: Build cash flows and calculate metrics for ARV scenario
    cashflows_arv = build_simplified_cashflow(
        acq_price=acq_price,
        total_costs=total_costs_arv,
        proceeds=proceeds_arv,
        duration_months=total_timeline_arv,
        acq_costs=acq_costs
    )
    irr_arv = reo_arv_logic.calculate_irr(cashflows_arv)
    npv_arv = reo_arv_logic.calculate_npv(cashflows_arv)

    bid_pct_upb_val = Decimal('0')
    bid_pct_td_val = Decimal('0')
    bid_pct_sellerasis_val = Decimal('0')
    if current_balance > 0:
        bid_pct_upb_val = (acq_price / current_balance) * 100
    if total_debt > 0:
        bid_pct_td_val = (acq_price / total_debt) * 100
    if seller_asis > 0:
        bid_pct_sellerasis_val = (acq_price / seller_asis) * 100

    return {
        'id': raw_data.pk,
        'asset_hub_id': raw_data.asset_hub_id,
        'seller_loan_id': raw_data.sellertape_id,
        'street_address': raw_data.street_address,
        'city': raw_data.city,
        'state': raw_data.state,
        'current_balance': float(current_balance),
        'total_debt': float(total_debt),
        'primary_model': 'reo_sale',
        'total_duration_months_asis': total_timeline_asis,
        'total_duration_months_arv': total_timeline_arv,
        'acquisition_price': float(acq_price),
        'total_costs_asis': float(total_costs_asis),
        'expected_proceeds_asis': float(proceeds_asis),
        'net_pl_asis': float(net_pl_asis),
        'moic_asis': float(moic_asis),
        'irr_asis': irr_asis,
        'npv_asis': npv_asis,
        'total_costs_arv': float(total_costs_arv),
        'expected_proceeds_arv': float(proceeds_arv),
        'net_pl_arv': float(net_pl_arv),
        'moic_arv': float(moic_arv),
        'irr_arv': irr_arv,
        'npv_arv': npv_arv,
        'bid_pct_upb': float(bid_pct_upb_val),
        'bid_pct_td': float(bid_pct_td_val),
        'bid_pct_sellerasis': float(bid_pct_sellerasis_val),
    }


def annualized_roi(
    total_return: Decimal,
    total_invested: Decimal,
    weighted_duration_months: Decimal,
) -> float:
    """Calculate an annualized simple return for a pool.

    Definition (simple annualized return):
        (total_return / total_invested) / years

    where years is based on an acquisition-weighted average duration
    derived from ``weighted_duration_months``.
    """
    if not total_invested or total_invested <= 0:
        return 0.0
    if not weighted_duration_months or weighted_duration_months <= 0:
        return 0.0

    try:
        avg_months = float(weighted_duration_months / total_invested)
    except Exception:
        return 0.0
    if avg_months <= 0:
        return 0.0

    years = avg_months / 12.0
    if years <= 0:
        return 0.0

    simple_return = float(total_return) / float(total_invested)
    return simple_return / years


def summarize_modeling_pool(results: List[Dict[str, Any]], seller_id: int, trade_id: int) -> Dict[str, Any]:
    """Aggregate per-asset modeling results into pool-level metrics for Modeling Center.

    The input ``results`` list is expected to contain the dictionaries returned by
    :func:`calculate_asset_model_data_fast`.
    """
    total_acq = Decimal("0")
    total_costs_asis = Decimal("0")
    total_proceeds_asis = Decimal("0")
    total_costs_arv = Decimal("0")
    total_proceeds_arv = Decimal("0")
    modeled_count = 0

    weighted_duration_asis = Decimal("0")
    weighted_duration_arv = Decimal("0")

    for row in results:
        acq = Decimal(str(row.get('acquisition_price') or "0"))
        if acq <= 0:
            continue

        modeled_count += 1
        total_acq += acq

        costs_asis = Decimal(str(row.get('total_costs_asis') or "0"))
        proceeds_asis = Decimal(str(row.get('expected_proceeds_asis') or "0"))
        total_costs_asis += costs_asis
        total_proceeds_asis += proceeds_asis

        costs_arv = Decimal(str(row.get('total_costs_arv') or "0"))
        proceeds_arv = Decimal(str(row.get('expected_proceeds_arv') or "0"))
        total_costs_arv += costs_arv
        total_proceeds_arv += proceeds_arv

        dur_asis = Decimal(str(row.get('total_duration_months_asis') or "0"))
        dur_arv = Decimal(str(row.get('total_duration_months_arv') or "0"))

        if dur_asis > 0:
            weighted_duration_asis += acq * dur_asis
        if dur_arv > 0:
            weighted_duration_arv += acq * dur_arv

    net_pl_asis = total_proceeds_asis - total_acq - total_costs_asis
    net_pl_arv = total_proceeds_arv - total_acq - total_costs_arv

    moic_asis = Decimal("0")
    moic_arv = Decimal("0")
    if total_acq > 0:
        moic_asis = (total_proceeds_asis - total_costs_asis) / total_acq
        moic_arv = (total_proceeds_arv - total_costs_arv) / total_acq

    def _approx_irr(moic: Decimal, weighted_duration_months: Decimal) -> float:
        if moic <= 0 or total_acq <= 0 or weighted_duration_months <= 0:
            return 0.0
        try:
            avg_months = float(weighted_duration_months / total_acq)
        except Exception:
            return 0.0
        if avg_months <= 0:
            return 0.0
        years = avg_months / 12.0
        if years <= 0:
            return 0.0
        moic_f = float(moic)
        if moic_f <= 0:
            return 0.0
        try:
            irr = pow(moic_f, 1.0 / years) - 1.0
        except Exception:
            return 0.0
        if irr != irr or irr in (float('inf'), float('-inf')):
            return 0.0
        return irr

    irr_asis = _approx_irr(moic_asis, weighted_duration_asis)
    irr_arv = _approx_irr(moic_arv, weighted_duration_arv)

    annualized_roi_asis = annualized_roi(net_pl_asis, total_acq, weighted_duration_asis)
    annualized_roi_arv = annualized_roi(net_pl_arv, total_acq, weighted_duration_arv)

    pool_totals = count_upb_td_val_summary(seller_id, trade_id)
    upb_sum: Decimal = pool_totals.get("current_balance") or Decimal("0")
    td_sum: Decimal = pool_totals.get("total_debt") or Decimal("0")
    asis_sum: Decimal = pool_totals.get("seller_asis_value") or Decimal("0")

    bid_pct_upb = Decimal("0")
    bid_pct_td = Decimal("0")
    bid_pct_seller_asis = Decimal("0")
    if upb_sum and upb_sum != 0 and total_acq > 0:
        bid_pct_upb = (total_acq * Decimal("100")) / upb_sum
    if td_sum and td_sum != 0 and total_acq > 0:
        bid_pct_td = (total_acq * Decimal("100")) / td_sum
    if asis_sum and asis_sum != 0 and total_acq > 0:
        bid_pct_seller_asis = (total_acq * Decimal("100")) / asis_sum

    return {
        'total_acquisition_price': float(total_acq),
        'underwritten_asis_total': float(total_proceeds_asis),
        'modeled_count': modeled_count,
        'bid_pct_upb': float(bid_pct_upb),
        'bid_pct_total_debt': float(bid_pct_td),
        'bid_pct_seller_asis': float(bid_pct_seller_asis),
        'as_is': {
            'total_costs': float(total_costs_asis),
            'total_proceeds': float(total_proceeds_asis),
            'net_pl': float(net_pl_asis),
            'moic': float(moic_asis),
            'irr': irr_asis,
            'annualized_roi': annualized_roi_asis,
            'npv': float(net_pl_asis),
        },
        'arv': {
            'total_costs': float(total_costs_arv),
            'total_proceeds': float(total_proceeds_arv),
            'net_pl': float(net_pl_arv),
            'moic': float(moic_arv),
            'irr': irr_arv,
            'annualized_roi': annualized_roi_arv,
            'npv': float(net_pl_arv),
        },
    }


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
        # Get the asset record using asset_hub_id as the primary key
        asset = SellerRawData.objects.get(asset_hub_id=asset_id)
        
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


# -------------------------------------------------------------------------------------------------
# Pool-Level Bid Percentage Calculations
# -------------------------------------------------------------------------------------------------

class PoolBidPercentages(TypedDict):
    """Type definition for pool-level bid percentage metrics."""
    total_acquisition_price: Decimal
    bid_pct_upb: Decimal
    bid_pct_total_debt: Decimal
    bid_pct_seller_asis: Decimal


def get_pool_bid_percentages(seller_id: int, trade_id: int) -> PoolBidPercentages:
    """
    Calculate pool-level bid percentages for a selected seller and trade.
    
    WHAT: Calculates three bid percentage metrics at the pool level:
    - Bid % of UPB: (Total Acquisition Price / Total UPB) * 100
    - Bid % of Total Debt: (Total Acquisition Price / Total Debt) * 100
    - Bid % of Seller As-Is: (Total Acquisition Price / Seller As-Is Value) * 100
    
    WHY: These metrics show the acquisition price as percentages of key pool denominators,
         providing insight into the bid strategy relative to current balance, total debt, and seller valuation.
    
    WHERE: Used by Modeling Center and other pool-level analysis views.
    
    HOW:
    1. Get pool summary (UPB, Total Debt, Seller As-Is Value) from count_upb_td_val_summary()
    2. Calculate total acquisition price by summing purchase_price() for all assets in the pool
    3. Calculate each bid percentage using the total acquisition price and respective denominator
    4. Return all metrics in a typed dictionary
    
    Args:
        seller_id: Seller primary key to filter by.
        trade_id: Trade primary key to filter by.
        
    Returns:
        PoolBidPercentages dict containing:
        - total_acquisition_price: Sum of all asset acquisition prices
        - bid_pct_upb: Bid percentage of UPB (0-100+)
        - bid_pct_total_debt: Bid percentage of Total Debt (0-100+)
        - bid_pct_seller_asis: Bid percentage of Seller As-Is Value (0-100+)
    
    Notes:
        - All percentages are expressed as 0-100+ (e.g., 85.0 for 85%)
        - Returns 0.00 for percentages if denominator is zero or missing
        - Uses purchase_price() logic which prioritizes user-entered values over calculated
        - Calculation is done in Python after database aggregation for flexibility
    """
    # WHAT: Get pool summary data (UPB, Total Debt, Seller As-Is Value)
    # WHY: Need denominators for bid percentage calculations
    # HOW: Use existing pool summary function
    pool_summary = count_upb_td_val_summary(seller_id, trade_id)
    
    # WHAT: Extract pool totals from summary
    # WHY: Use as denominators in bid percentage calculations
    # HOW: Get from pool_summary dict, default to 0 if missing
    total_upb = pool_summary.get('current_balance', Decimal('0.00')) or Decimal('0.00')
    total_debt = pool_summary.get('total_debt', Decimal('0.00')) or Decimal('0.00')
    seller_asis_value = pool_summary.get('seller_asis_value', Decimal('0.00')) or Decimal('0.00')
    
    # WHAT: Get base queryset for selected seller and trade
    # WHY: Need to iterate through all assets to sum acquisition prices
    # HOW: Use common sellertrade_qs function for consistent filtering
    qs = sellertrade_qs(seller_id, trade_id)
    
    # WHAT: Calculate total acquisition price by summing purchase_price for all assets
    # WHY: Need numerator for all three bid percentage calculations
    # HOW: Iterate through queryset and sum purchase_price() for each asset
    total_acquisition_price = Decimal('0.00')
    for asset in qs:
        # WHAT: Get acquisition price for this asset
        # WHY: purchase_price() handles user-entered vs calculated logic
        # HOW: Call purchase_price() with asset_hub_id
        acq_price = purchase_price(asset.asset_hub_id)
        total_acquisition_price += acq_price
    
    # WHAT: Helper function to calculate percentage safely
    # WHY: Avoid division by zero and ensure consistent rounding
    # HOW: Return 0.00 if denominator is zero, otherwise calculate percentage
    def _calculate_pct(numerator: Decimal, denominator: Decimal) -> Decimal:
        """Calculate percentage: (numerator / denominator) * 100, handling division by zero."""
        if not denominator or denominator == 0:
            return Decimal('0.00')
        return ((numerator * Decimal('100')) / denominator).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # WHAT: Calculate Bid % of UPB
    # WHY: Shows acquisition price as percentage of current balance
    # HOW: (Total Acquisition Price / Total UPB) * 100
    bid_pct_upb = _calculate_pct(total_acquisition_price, total_upb)
    
    # WHAT: Calculate Bid % of Total Debt
    # WHY: Shows acquisition price as percentage of total debt
    # HOW: (Total Acquisition Price / Total Debt) * 100
    bid_pct_total_debt = _calculate_pct(total_acquisition_price, total_debt)
    
    # WHAT: Calculate Bid % of Seller As-Is Value
    # WHY: Shows acquisition price as percentage of seller's as-is valuation
    # HOW: (Total Acquisition Price / Seller As-Is Value) * 100
    bid_pct_seller_asis = _calculate_pct(total_acquisition_price, seller_asis_value)
    
    # WHAT: Return all metrics in typed dictionary
    # WHY: Consistent return format for API consumption
    # HOW: Use TypedDict structure
    return {
        'total_acquisition_price': total_acquisition_price,
        'bid_pct_upb': bid_pct_upb,
        'bid_pct_total_debt': bid_pct_total_debt,
        'bid_pct_seller_asis': bid_pct_seller_asis,
    }
