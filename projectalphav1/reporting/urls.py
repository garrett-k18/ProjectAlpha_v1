"""
URL Routing: Reporting Module

WHAT: URL routing for reporting app endpoints
WHY: Map URLs to view functions for reporting dashboard
WHERE: Included in main projectalphav1/urls.py under /api/reporting/
HOW: Import view functions and map to URL patterns

ENDPOINTS:
- /api/reporting/summary/ - Top bar KPIs
- /api/reporting/by-trade/ - By Trade chart data
- /api/reporting/by-trade/grid/ - By Trade grid data
- /api/reporting/trades/ - Trade filter options
- etc.

Docs reviewed:
- Django URL dispatcher: https://docs.djangoproject.com/en/stable/topics/http/urls/
"""

from django.urls import path
from reporting.views import (
    view_rep_filters,
    view_rep_summary,
    view_rep_trade,
    view_rep_status
)

urlpatterns = [
    # ========================================================================
    # FILTER OPTIONS - Populate sidebar dropdowns
    # ========================================================================
    # WHAT: Trade filter options from Trade model
    # ENDPOINT: GET /api/reporting/trades/
    # RETURNS: List of {id, trade_name, seller_name, status, asset_count}
    path('trades/', view_rep_filters.trade_options, name='reporting-trades'),
    
    # WHAT: Status filter options
    # ENDPOINT: GET /api/reporting/statuses/
    # RETURNS: List of {value, label, count}
    path('statuses/', view_rep_filters.status_options, name='reporting-statuses'),
    
    # WHAT: Fund filter options (TODO: implement once Fund model exists)
    # ENDPOINT: GET /api/reporting/funds/
    path('funds/', view_rep_filters.fund_options, name='reporting-funds'),
    
    # WHAT: Entity filter options (TODO: implement once Entity model exists)
    # ENDPOINT: GET /api/reporting/entities/
    path('entities/', view_rep_filters.entity_options, name='reporting-entities'),
    
    # ========================================================================
    # SUMMARY KPIs - Top bar metrics (Total UPB, Count, Avg LTV, DLQ Rate)
    # ========================================================================
    path('summary/', view_rep_summary.report_summary, name='reporting-summary'),
    
    # ========================================================================
    # BY TRADE REPORT - Chart and grid data
    # ========================================================================
    path('by-trade/', view_rep_trade.by_trade_chart, name='reporting-by-trade-chart'),
    path('by-trade/grid/', view_rep_trade.by_trade_grid, name='reporting-by-trade-grid'),
    
    # ========================================================================
    # BY STATUS REPORT - Chart and grid data
    # ========================================================================
    path('by-status/', view_rep_status.get_by_status_chart, name='reporting-by-status-chart'),
    path('by-status/grid/', view_rep_status.get_by_status_grid, name='reporting-by-status-grid'),
    
    # TODO: Add remaining report endpoints:
    # - by-fund/
    # - by-entity/
    # - geographic/
    # - collateral/
    # - timeseries/
]
