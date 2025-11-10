"""
Service: Reporting Aggregations

WHAT: Aggregation and grouping logic for reporting calculations
WHY: Centralize complex aggregation queries (sum, avg, count, group by)
WHERE: Imported by report-specific service files
HOW: Use Django ORM aggregation and annotation functions

FILE NAMING: serv_rep_aggregations.py
- serv_ = Services folder
- _rep_ = Reporting module  
- aggregations = Descriptive name

ARCHITECTURE:
Service calls aggregation functions → Returns aggregated data dicts

Docs reviewed:
- Django aggregation: https://docs.djangoproject.com/en/stable/topics/db/aggregation/
- Django annotations: https://docs.djangoproject.com/en/stable/ref/models/querysets/#annotate
- Django values/values_list: https://docs.djangoproject.com/en/stable/ref/models/querysets/#values
"""

from typing import List, Dict, Any
from django.db.models import QuerySet, Sum, Avg, Count, Max, Min, Q, F, DecimalField
from django.db.models.functions import Coalesce
from acq_module.models.model_acq_seller import SellerRawData


def calculate_summary_metrics(queryset: QuerySet[SellerRawData]) -> Dict[str, Any]:
    """
    WHAT: Calculate high-level summary metrics for top KPI bar
    WHY: Display Total UPB, Asset Count, Avg LTV, Delinquency Rate
    HOW: Use Django aggregate functions on filtered queryset
    
    ARGS:
        queryset: Filtered SellerRawData queryset
    
    RETURNS: Dict with summary metrics
        {
            'total_upb': 123456789.00,
            'asset_count': 1234,
            'avg_ltv': 75.5,
            'delinquency_rate': 3.2,
        }
    """
    # WHAT: Aggregate all metrics in single query
    # WHY: More efficient than multiple queries
    # HOW: Use aggregate() with multiple aggregation functions
    aggregates = queryset.aggregate(
        total_upb=Coalesce(Sum('current_balance'), 0.0, output_field=DecimalField()),
        asset_count=Count('id'),
        avg_ltv=Coalesce(
            Avg(
                F('current_balance') * 100.0 / F('seller_asis_value'),
                output_field=DecimalField()
            ),
            0.0,
            output_field=DecimalField()
        ),
        total_delinquent=Count('id', filter=Q(months_dlq__gt=0)),
    )
    
    # WHAT: Calculate delinquency rate as percentage
    # WHY: Display as percentage (0-100) not decimal
    # HOW: (delinquent_count / total_count) * 100
    asset_count = aggregates['asset_count'] or 0
    delinquency_rate = 0.0
    if asset_count > 0:
        delinquency_rate = (aggregates['total_delinquent'] / asset_count) * 100.0
    
    return {
        'total_upb': float(aggregates['total_upb'] or 0),
        'asset_count': asset_count,
        'avg_ltv': float(aggregates['avg_ltv'] or 0),
        'delinquency_rate': round(delinquency_rate, 2),
    }


def group_by_trade(queryset: QuerySet[SellerRawData]) -> List[Dict[str, Any]]:
    """
    WHAT: Group assets by trade and calculate per-trade metrics
    WHY: Power "By Trade" report view
    HOW: Use values() + annotate() for GROUP BY query
    
    ARGS:
        queryset: Filtered SellerRawData queryset (with annotated fields from queryBuilder)
    
    RETURNS: List of dicts with per-trade metrics
        [
            {
                'trade_id': 1,
                'trade_name': 'NPL Portfolio 2024-Q1',
                'seller_name': 'ABC Bank',
                'asset_count': 245,
                'total_upb': 12500000.00,
                'avg_upb': 51020.41,
                'avg_ltv': 78.5,
                'status': 'DD',
                'bid_date': '2024-01-15',
                'state_count': 12,
                'delinquency_rate': 3.2,
            },
            ...
        ]
    """
    # ========================================================================
    # 📋 GROUP BY FIELDS - Fields to group by (one row per unique combination)
    # ========================================================================
    # WHAT: Group by trade and calculate aggregates
    # WHY: Each row represents one trade with summary stats
    # HOW: Use values() for GROUP BY, annotate() for aggregates
    #
    # NOTE: Any field in values() becomes a GROUP BY column in SQL
    # Add fields here that define unique rows (trade_id, trade_name, etc.)
    # ========================================================================
    trades = (
        queryset
        .values(
            'trade_id',
            'trade__trade_name',
            'trade__seller__name',
            'trade__status',
            'trade__created_at',
            # ================================================================
            # 🎯 ADD MORE GROUP BY FIELDS HERE IF NEEDED
            # ================================================================
            # Examples:
            # 'trade__fund__name',        # If grouping by fund too
            # 'trade__entity__name',      # If grouping by entity too
            # ================================================================
        )
        .annotate(
            # ================================================================
            # 📊 AGGREGATION FIELDS - Calculated metrics (sum, avg, count, max, min)
            # ================================================================
            # WHAT: Count of assets in this trade
            # WHY: How many assets in this trade
            asset_count=Count('id'),
            
            # ================================================================
            # CURRENT BALANCE METRICS (from SellerRawData)
            # ================================================================
            # WHAT: Sum of current balances (SellerRawData.current_balance)
            # WHY: Total UPB for this trade
            total_upb=Coalesce(Sum('current_balance'), 0.0, output_field=DecimalField()),
            
            # WHAT: Average current balance per asset
            # WHY: Average loan size in trade
            avg_upb=Coalesce(Avg('current_balance'), 0.0, output_field=DecimalField()),
            
            # ================================================================
            # SERVICER BALANCE METRICS (from ServicerLoanData)
            # ================================================================
            # WHAT: Sum of servicer current balances (annotated field)
            # WHY: Most up-to-date balance from servicing platform
            # HOW: Use annotated field servicer_current_balance from queryBuilder
            servicer_total_upb=Coalesce(Sum('servicer_current_balance'), 0.0, output_field=DecimalField()),
            
            # WHAT: Average servicer balance
            # WHY: Average loan size from servicer data
            servicer_avg_balance=Coalesce(Avg('servicer_current_balance'), 0.0, output_field=DecimalField()),
            
            # ================================================================
            # LTV CALCULATIONS
            # ================================================================
            # WHAT: Average LTV ratio (Current Balance / AIV)
            # WHY: Risk metric - higher LTV = higher risk
            avg_ltv=Coalesce(
                Avg(
                    F('current_balance') * 100.0 / F('seller_asis_value'),
                    output_field=DecimalField()
                ),
                0.0,
                output_field=DecimalField()
            ),
            
            # ================================================================
            # DEBT METRICS
            # ================================================================
            # WHAT: Sum of total debt across all assets in trade
            # WHY: Total exposure including fees, advances
            total_debt=Coalesce(Sum('total_debt'), 0.0, output_field=DecimalField()),
            
            # WHAT: Sum of servicer total debt (from ServicerLoanData)
            # WHY: Most current debt figures from servicer
            servicer_total_debt_sum=Coalesce(Sum('servicer_total_debt'), 0.0, output_field=DecimalField()),
            
            # ================================================================
            # GEOGRAPHIC METRICS
            # ================================================================
            # WHAT: Count of unique states in this trade
            # WHY: Geographic diversification metric
            state_count=Count('state', distinct=True),
            
            # ================================================================
            # DELINQUENCY METRICS
            # ================================================================
            # WHAT: Count of delinquent assets (months_dlq > 0)
            # WHY: Calculate delinquency rate percentage
            delinquent_count=Count('id', filter=Q(months_dlq__gt=0)),
            
            # ================================================================
            # 🎯 ADD YOUR OWN AGGREGATIONS HERE - Copy patterns above!
            # ================================================================
            # 
            # AGGREGATION FUNCTIONS:
            # - Count('field') - Count rows
            # - Sum('field') - Sum values
            # - Avg('field') - Average values
            # - Max('field') - Maximum value
            # - Min('field') - Minimum value
            # - Count('field', distinct=True) - Count unique values
            # - Count('id', filter=Q(condition)) - Conditional count
            #
            # EXAMPLES:
            # avg_interest_rate=Avg('servicer_interest_rate'),
            # max_balance=Max('servicer_current_balance'),
            # min_balance=Min('servicer_current_balance'),
            # fc_count=Count('id', filter=Q(fc_flag=True)),
            # occupied_count=Count('id', filter=Q(occupancy='O')),
            # ================================================================
        )
        .order_by('-total_upb')  # WHAT: Default sort by largest trades first
    )
    
    # ========================================================================
    # 📦 FORMAT RESULTS - Convert QuerySet to clean dicts
    # ========================================================================
    # WHAT: Calculate delinquency rate and format results
    # WHY: Return clean dicts ready for serialization
    # HOW: Loop through QuerySet results and build dict for each row
    # ========================================================================
    results = []
    for trade in trades:
        asset_count = trade['asset_count'] or 0
        delinquent_count = trade['delinquent_count'] or 0
        delinquency_rate = 0.0
        if asset_count > 0:
            delinquency_rate = (delinquent_count / asset_count) * 100.0
        
        results.append({
            # ================================================================
            # CORE FIELDS (always include these)
            # ================================================================
            'id': trade['trade_id'],
            'trade_id': trade['trade_id'],
            'trade_name': trade['trade__trade_name'],
            'seller_name': trade['trade__seller__name'] or '',
            'asset_count': asset_count,
            'status': trade['trade__status'],
            'bid_date': trade['trade__created_at'].isoformat() if trade['trade__created_at'] else None,
            
            # ================================================================
            # BALANCE FIELDS (from SellerRawData)
            # ================================================================
            'total_upb': float(trade['total_upb'] or 0),
            'avg_upb': float(trade['avg_upb'] or 0),
            'total_debt': float(trade['total_debt'] or 0),
            
            # ================================================================
            # SERVICER BALANCE FIELDS (from ServicerLoanData via annotations)
            # ================================================================
            'servicer_total_upb': float(trade['servicer_total_upb'] or 0),
            'servicer_avg_balance': float(trade['servicer_avg_balance'] or 0),
            'servicer_total_debt_sum': float(trade['servicer_total_debt_sum'] or 0),
            
            # ================================================================
            # CALCULATED METRICS
            # ================================================================
            'avg_ltv': float(trade['avg_ltv'] or 0),
            'state_count': trade['state_count'] or 0,
            'delinquency_rate': round(delinquency_rate, 2),
            
            # ================================================================
            # 🎯 ADD MORE FIELDS HERE - Copy pattern above!
            # ================================================================
            # 
            # PATTERN: 'field_name': value_from_trade_dict,
            #
            # For aggregated fields (from .annotate() above):
            # 'avg_interest_rate': float(trade['avg_interest_rate'] or 0),
            #
            # For group by fields (from .values() above):
            # 'fund_name': trade['trade__fund__name'] or '',
            #
            # EXAMPLES:
            # 'avg_interest_rate': float(trade.get('avg_interest_rate', 0)),
            # 'max_balance': float(trade.get('max_balance', 0)),
            # 'fc_count': trade.get('fc_count', 0),
            # ================================================================
        })
    
    return results


def group_by_status(queryset: QuerySet[SellerRawData]) -> List[Dict[str, Any]]:
    """
    WHAT: Group assets by trade status
    WHY: Power "By Status" report view
    HOW: Use values() + annotate() grouped by trade__status
    
    ARGS:
        queryset: Filtered SellerRawData queryset
    
    RETURNS: List of dicts with per-status metrics
    """
    statuses = (
        queryset
        .values('trade__status')
        .annotate(
            asset_count=Count('id'),
            total_upb=Coalesce(Sum('current_balance'), 0.0, output_field=DecimalField()),
            avg_upb=Coalesce(Avg('current_balance'), 0.0, output_field=DecimalField()),
            avg_ltv=Coalesce(
                Avg(
                    F('current_balance') * 100.0 / F('seller_asis_value'),
                    output_field=DecimalField()
                ),
                0.0,
                output_field=DecimalField()
            ),
        )
        .order_by('-total_upb')
    )
    
    results = []
    for status in statuses:
        results.append({
            'id': status['trade__status'],
            'status': status['trade__status'],
            'asset_count': status['asset_count'] or 0,
            'total_upb': float(status['total_upb'] or 0),
            'avg_upb': float(status['avg_upb'] or 0),
            'avg_ltv': float(status['avg_ltv'] or 0),
        })
    
    return results


def group_by_fund(queryset: QuerySet[SellerRawData]) -> List[Dict[str, Any]]:
    """
    WHAT: Group assets by fund
    WHY: Power "By Fund" report view
    HOW: Use values() + annotate() grouped by fund
    
    ARGS:
        queryset: Filtered SellerRawData queryset
    
    RETURNS: List of dicts with per-fund metrics
    
    TODO: Implement once fund FK is added to Trade or AssetHub model
    """
    # TODO: Group by fund once fund FK exists on model
    # For now, return empty list
    return []


def group_by_entity(queryset: QuerySet[SellerRawData]) -> List[Dict[str, Any]]:
    """
    WHAT: Group assets by legal entity
    WHY: Power "By Entity" report view
    HOW: Use values() + annotate() grouped by entity
    
    ARGS:
        queryset: Filtered SellerRawData queryset
    
    RETURNS: List of dicts with per-entity metrics
    
    TODO: Implement once entity FK is added to Trade or AssetHub model
    """
    # TODO: Group by entity once entity FK exists on model
    # For now, return empty list
    return []

