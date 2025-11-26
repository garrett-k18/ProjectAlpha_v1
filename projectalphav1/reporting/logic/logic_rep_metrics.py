"""
**WHAT**: Portfolio metric calculations for reporting dashboard
**WHY**: Centralize all KPI and financial calculations
**WHERE**: Called by view_rep_summary.py and other report views
"""

from django.db.models import Sum, Avg, Count, Q, F
from decimal import Decimal


def calculate_summary_metrics(queryset):
    """
    **WHAT**: Calculate top-level KPIs from filtered queryset
    **WHY**: Provide executive summary metrics for dashboard header
    **HOW**: Aggregate SellerRawData with proper null handling
    
    **PARAMETERS**:
    - queryset: Filtered SellerRawData queryset
    
    **RETURNS**: Dict with total_upb, asset_count, avg_ltv, delinquency_rate
    """
    # Calculate basic aggregates
    summary = queryset.aggregate(
        total_upb=Sum('current_balance'),
        asset_count=Count('id'),
        avg_ltv=Avg('ltv')
    )
    
    # Calculate delinquency rate
    # WHAT: Percentage of assets that are 30+ days delinquent
    # WHY: Key risk indicator for portfolio health
    total_count = summary['asset_count'] or 1
    delinquent_count = queryset.filter(
        Q(days_delinquent__gt=30) | Q(status__icontains='delinquent')
    ).count()
    delinquency_rate = (delinquent_count / total_count) * 100
    
    return {
        'total_upb': float(summary['total_upb'] or Decimal('0.00')),
        'asset_count': summary['asset_count'] or 0,
        'avg_ltv': float(summary['avg_ltv'] or Decimal('0.00')),
        'delinquency_rate': round(delinquency_rate, 2)
    }


def calculate_by_trade_metrics(queryset):
    """
    **WHAT**: Aggregate metrics grouped by trade
    **WHY**: Power By Trade report chart and grid
    **HOW**: Group by trade and calculate sums/averages
    
    **PARAMETERS**:
    - queryset: Filtered SellerRawData queryset
    
    **RETURNS**: QuerySet with trade aggregates
    """
    return queryset.values(
        'trade_id',
        'trade__trade_name',
        'trade__seller__seller_name',
        'trade__status'
    ).annotate(
        total_upb=Sum('current_balance'),
        asset_count=Count('id'),
        avg_upb=Avg('current_balance'),
        avg_ltv=Avg('ltv'),
        total_debt=Sum('total_debt'),
        asis_value=Sum('seller_asis_value')
    ).order_by('-total_upb')


def calculate_by_status_metrics(queryset):
    """
    **WHAT**: Aggregate metrics grouped by status
    **WHY**: Power By Status report chart and grid
    **HOW**: Group by status and calculate sums/averages/percentages
    
    **PARAMETERS**:
    - queryset: Filtered SellerRawData queryset
    
    **RETURNS**: List of dicts with status aggregates including percentage
    """
    # Get total UPB for percentage calculation
    total_upb = queryset.aggregate(total=Sum('current_balance'))['total'] or Decimal('0.00')
    
    # Group by status
    status_data = queryset.values('trade__status').annotate(
        total_upb=Sum('current_balance'),
        asset_count=Count('id'),
        avg_upb=Avg('current_balance'),
        avg_ltv=Avg('ltv'),
        total_debt=Sum('total_debt')
    ).order_by('-total_upb')
    
    # Add percentage to each status
    result = []
    for item in status_data:
        item['percentage'] = (float(item['total_upb'] or 0) / float(total_upb) * 100) if total_upb > 0 else 0
        result.append(item)
    
    return result


def calculate_moic(total_proceeds, total_invested):
    """
    **WHAT**: Calculate Multiple on Invested Capital
    **WHY**: Key return metric for private equity
    **HOW**: Total proceeds / Total invested
    
    **RETURNS**: Float MOIC value
    """
    if not total_invested or total_invested == 0:
        return 0.0
    return float(total_proceeds) / float(total_invested)


def calculate_pl(total_proceeds, gross_cost_basis):
    """
    **WHAT**: Calculate Profit & Loss
    **WHY**: Simple profit calculation
    **HOW**: Total proceeds - Gross cost basis
    
    **RETURNS**: Float P&L value
    """
    return float(total_proceeds or 0) - float(gross_cost_basis or 0)


def calculate_pre_reo_duration(blended_outcome):
    """ 
    **WHAT**: Calculate total Pre-REO hold duration in months.
    **WHY**: Roll up underwriting timeline phases before REO into a single metric.
    **HOW**: Sum of servicing_transfer_duration, pre_fc_duration, fc_duration_state_avg, dil_duration.
    **BASIS**: Uses BlendedOutcomeModel timeline fields in
    am_module.models.boarded_data.BlendedOutcomeModel.
    """
    if blended_outcome is None:
        return 0

    servicing_transfer = getattr(blended_outcome, 'servicing_transfer_duration', None) or 0
    pre_fc = getattr(blended_outcome, 'pre_fc_duration', None) or 0
    fc_state_avg = getattr(blended_outcome, 'fc_duration_state_avg', None) or 0
    dil = getattr(blended_outcome, 'dil_duration', None) or 0

    return int(servicing_transfer + pre_fc + fc_state_avg + dil)


def calculate_reo_duration(blended_outcome):
    """
    **WHAT**: Calculate total REO hold duration in months.
    **WHY**: Roll up REO and post-FC phases into a single REO duration metric.
    **HOW**: Sum of eviction_duration, renovation_duration, reo_marketing_duration,
    local_market_ext_duration, rural_ext_duration.
    **BASIS**: Uses BlendedOutcomeModel REO timeline fields in
    am_module.models.boarded_data.BlendedOutcomeModel.
    """
    if blended_outcome is None:
        return 0

    eviction = getattr(blended_outcome, 'eviction_duration', None) or 0
    renovation = getattr(blended_outcome, 'renovation_duration', None) or 0
    reo_marketing = getattr(blended_outcome, 'reo_marketing_duration', None) or 0
    local_market_ext = getattr(blended_outcome, 'local_market_ext_duration', None) or 0
    rural_ext = getattr(blended_outcome, 'rural_ext_duration', None) or 0

    return int(eviction + renovation + reo_marketing + local_market_ext + rural_ext)


def calculate_legal_cost(blended_outcome):
    """
    **WHAT**: Calculate total legal cost for an asset.
    **WHY**: Roll up all boarding/acquisition legal-related fees into a single metric.
    **HOW**: Sum of fc_expenses, fc_legal_fees, outher_fc_fees, dil_fees,
    cfk_fees, bk_legal_fees, eviction_fees.
    **BASIS**: Uses BlendedOutcomeModel legal fee fields in
    am_module.models.boarded_data.BlendedOutcomeModel.
    """
    if blended_outcome is None:
        return 0.0

    fc_expenses = getattr(blended_outcome, 'fc_expenses', None) or 0
    dil_fees = getattr(blended_outcome, 'dil_fees', None) or 0
    cfk_fees = getattr(blended_outcome, 'cfk_fees', None) or 0
    bk_legal_fees = getattr(blended_outcome, 'bk_legal_fees', None) or 0
    eviction_fees = getattr(blended_outcome, 'eviction_fees', None) or 0

    total = (
        fc_expenses
        + dil_fees
        + cfk_fees
        + bk_legal_fees
        + eviction_fees
    )

    return float(total or 0)


def calculate_monthly_servicing_cost(blended_outcome):
    """
    **WHAT**: Calculate total servicing cost for an asset.
    **WHY**: Roll up all servicing-related fees into a single metric.
    **HOW**: Sum of servicing_board_fee, servicing_current, servicing_30d,
    servicing_60d, servicing_90d, servicing_120d, servicing_fc, servicing_bk,
    servicing_liq_fee.
    **BASIS**: Uses BlendedOutcomeModel servicing fee fields in
    am_module.models.boarded_data.BlendedOutcomeModel.
    """
    if blended_outcome is None:
        return 0.0

    servicing_board_fee = getattr(blended_outcome, 'servicing_board_fee', None) or 0
    servicing_current = getattr(blended_outcome, 'servicing_current', None) or 0
    servicing_30d = getattr(blended_outcome, 'servicing_30d', None) or 0
    servicing_60d = getattr(blended_outcome, 'servicing_60d', None) or 0
    servicing_90d = getattr(blended_outcome, 'servicing_90d', None) or 0
    servicing_120d = getattr(blended_outcome, 'servicing_120d', None) or 0
    servicing_fc = getattr(blended_outcome, 'servicing_fc', None) or 0
    servicing_bk = getattr(blended_outcome, 'servicing_bk', None) or 0
    

    total = (
        servicing_board_fee
        + servicing_current
        + servicing_30d
        + servicing_60d
        + servicing_90d
        + servicing_120d
        + servicing_fc
        + servicing_bk
    )

    return float(total or 0)


def calculate_carry_cost(blended_outcome):
    """
    **WHAT**: Calculate total carry cost for an asset (servicing + insurance + property tax).
    **WHY**: Provide a single holding-cost metric that combines servicing and core
    property-level costs.
    **HOW**: calculate_servicing_cost(blended_outcome) + total_insurance + total_property_tax.
    **BASIS**: Uses BlendedOutcomeModel fields servicing_* plus total_insurance and
    total_property_tax in am_module.models.boarded_data.BlendedOutcomeModel.
    """
    if blended_outcome is None:
        return 0.0

    servicing_total = calculate_monthly_servicing_cost(blended_outcome)
    total_insurance = getattr(blended_outcome, 'total_insurance', None) or 0
    total_property_tax = getattr(blended_outcome, 'total_property_tax', None) or 0

    total = (
        servicing_total
        + float(total_insurance)
        + float(total_property_tax)
    )

    return float(total or 0)


def calculate_reo_cost(blended_outcome):
    """
    **WHAT**: Calculate REO-specific property carrying costs.
    **WHY**: Group HOA, utilities, and other REO property expenses into one metric.
    **HOW**: Sum of total_hoa, total_utility, total_other.
    **BASIS**: Uses BlendedOutcomeModel property expense fields (total_hoa,
    total_utility, total_other) in
    am_module.models.boarded_data.BlendedOutcomeModel.
    """
    if blended_outcome is None:
        return 0.0

    total_hoa = getattr(blended_outcome, 'total_hoa', None) or 0
    total_utility = getattr(blended_outcome, 'total_utility', None) or 0
    total_other = getattr(blended_outcome, 'total_other', None) or 0

    total = total_hoa + total_utility + total_other

    return float(total or 0)


def calculate_liq_fees(blended_outcome):
    """
    **WHAT**: Calculate liquidation management fees (AM + servicing).
    **WHY**: Separate people/process fees from property-level closing costs.
    **HOW**: Sum of am_liq_fees and servicing_liq_fee.
    **BASIS**: Uses BlendedOutcomeModel fields am_liq_fees and servicing_liq_fee.
    """
    if blended_outcome is None:
        return 0.0

    am_liq_fees = getattr(blended_outcome, 'am_liq_fees', None) or 0
    servicing_liq_fee = getattr(blended_outcome, 'servicing_liq_fee', None) or 0

    total = am_liq_fees + servicing_liq_fee

    return float(total or 0)


def calculate_reo_closing_cost(blended_outcome):
    """
    **WHAT**: Calculate REO closing costs tied to tax/title transfer and brokers.
    **WHY**: Track property disposition closing costs separately from liquidation fees.
    **HOW**: Sum of tax_title_transfer_cost and broker_fees.
    **BASIS**: Uses BlendedOutcomeModel fields tax_title_transfer_cost and broker_fees.
    """
    if blended_outcome is None:
        return 0.0

    tax_title_transfer_cost = getattr(blended_outcome, 'tax_title_transfer_cost', None) or 0
    broker_fees = getattr(blended_outcome, 'broker_fees', None) or 0

    total = tax_title_transfer_cost + broker_fees

    return float(total or 0)


# Placeholder for IRR calculation (requires numpy/scipy for accurate calculation)
def calculate_irr(cash_flows, dates):
    """
    **WHAT**: Calculate Internal Rate of Return
    **WHY**: Time-weighted return metric
    **HOW**: Solve for rate where NPV = 0 (requires numpy.irr or scipy.optimize)
    
    **NOTE**: Placeholder - implement with numpy_financial.irr() when needed
    
    **RETURNS**: Float IRR percentage
    """
    # TODO: Implement with numpy_financial.irr(cash_flows)
    return 0.0


# Placeholder for NPV calculation
def calculate_npv(cash_flows, discount_rate):
    """
    **WHAT**: Calculate Net Present Value
    **WHY**: Present value of future cash flows
    **HOW**: Sum of discounted cash flows
    
    **NOTE**: Placeholder - implement with numpy_financial.npv() when needed
    
    **RETURNS**: Float NPV value
    """
    # TODO: Implement with numpy_financial.npv(discount_rate, cash_flows)
    return 0.0
