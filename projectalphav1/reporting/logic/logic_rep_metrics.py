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
