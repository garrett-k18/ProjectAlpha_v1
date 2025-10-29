"""
**WHAT**: URL routing for reporting app endpoints
**WHY**: Map URLs to view functions
**WHERE**: Included in main projectalphav1/urls.py
"""

from django.urls import path
from reporting.views import (
    view_rep_filters,
    view_rep_summary,
    view_rep_trade,
    view_rep_status
)

urlpatterns = [
    # Filter options - populate dropdowns
    path('trades/', view_rep_filters.get_trade_options, name='reporting-trades'),
    path('statuses/', view_rep_filters.get_status_options, name='reporting-statuses'),
    path('funds/', view_rep_filters.get_fund_options, name='reporting-funds'),
    path('entities/', view_rep_filters.get_entity_options, name='reporting-entities'),
    
    # Summary KPIs - top bar metrics
    path('summary/', view_rep_summary.get_report_summary, name='reporting-summary'),
    
    # By Trade report - chart and grid data
    path('by-trade/', view_rep_trade.get_by_trade_chart, name='reporting-by-trade-chart'),
    path('by-trade/grid/', view_rep_trade.get_by_trade_grid, name='reporting-by-trade-grid'),
    
    # By Status report - chart and grid data
    path('by-status/', view_rep_status.get_by_status_chart, name='reporting-by-status-chart'),
    path('by-status/grid/', view_rep_status.get_by_status_grid, name='reporting-by-status-grid'),
]
