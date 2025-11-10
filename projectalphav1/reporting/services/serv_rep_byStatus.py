"""
Service: By Status Report

WHAT: Business logic for By Status report (chart and grid data)
WHY: Separate aggregation logic from views/serializers
WHERE: Imported by view_rep_status.py
HOW: Use queryBuilder + aggregations services

FILE NAMING: serv_rep_byStatus.py
- serv_ = Services folder
- _rep_ = Reporting module
- byStatus = Specific report type

ARCHITECTURE:
View → This Service → queryBuilder + aggregations → Model
"""

from typing import List, Dict, Any
from .serv_rep_queryBuilder import build_reporting_queryset, parse_filter_params
from .serv_rep_aggregations import group_by_status


def get_by_status_chart_data(request) -> List[Dict[str, Any]]:
    """
    WHAT: Get chart data for By Status visualization
    WHY: Display doughnut/pie chart showing portfolio by status
    HOW: Parse filters, build queryset, group by status, format for Chart.js
    
    ARGS:
        request: Django request with query params
    
    RETURNS: List of chart data points
        [
            {
                'x': 'Due Diligence',  # Status label
                'y': 25600000.00,      # Total UPB for this status
                'meta': {
                    'status': 'DD',
                    'count': 487,
                    'percentage': 45.2
                }
            },
            ...
        ]
    """
    # WHAT: Parse filters and build queryset
    filters = parse_filter_params(request)
    queryset = build_reporting_queryset(**filters)
    
    # WHAT: Group by status
    status_metrics = group_by_status(queryset)
    
    # WHAT: Calculate total UPB for percentage calculation
    # WHY: Show "DD: 45.2% of portfolio" in tooltips
    total_upb = sum(s['total_upb'] for s in status_metrics)
    
    # WHAT: Format for Chart.js
    chart_data = []
    for status in status_metrics:
        percentage = 0.0
        if total_upb > 0:
            percentage = (status['total_upb'] / total_upb) * 100.0
        
        # WHAT: Map status codes to friendly labels
        # WHY: Display "Due Diligence" not "DD" in chart
        status_labels = {
            'DD': 'Due Diligence',
            'AWARDED': 'Awarded',
            'PASS': 'Passed',
            'BOARD': 'Boarded',
            'INDICATIVE': 'Indicative',
        }
        
        chart_data.append({
            'x': status_labels.get(status['status'], status['status']),
            'y': status['total_upb'],
            'meta': {
                'status': status['status'],
                'count': status['asset_count'],
                'percentage': round(percentage, 1),
            }
        })
    
    return chart_data


def get_by_status_grid_data(request) -> List[Dict[str, Any]]:
    """
    WHAT: Get detailed grid data for By Status table
    WHY: Display status metrics in AG Grid
    HOW: Same as chart but return full status_metrics directly
    
    ARGS:
        request: Django request with query params
    
    RETURNS: List of row objects for AG Grid
    """
    # WHAT: Parse filters and build queryset
    filters = parse_filter_params(request)
    queryset = build_reporting_queryset(**filters)
    
    # WHAT: Group by status
    status_metrics = group_by_status(queryset)
    
    # WHAT: Calculate percentage of portfolio
    total_upb = sum(s['total_upb'] for s in status_metrics)
    
    for status in status_metrics:
        percentage = 0.0
        if total_upb > 0:
            percentage = (status['total_upb'] / total_upb) * 100.0
        
        status['percentage'] = round(percentage, 1)
    
    return status_metrics

