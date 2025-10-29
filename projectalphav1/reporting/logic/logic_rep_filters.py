"""
**WHAT**: Filter query helpers for reporting endpoints
**WHY**: DRY principle - reuse filter logic across all report endpoints
**WHERE**: Imported by all view files to apply consistent filtering
"""

from django.db.models import Q


def apply_filters(request, queryset):
    """
    **WHAT**: Apply common filters from query params to any queryset
    **WHY**: Centralize filter logic to avoid duplication
    **HOW**: Parse query params and build filtered queryset
    
    **PARAMETERS**:
    - request: Django request object with query params
    - queryset: Base queryset to filter
    
    **RETURNS**: Filtered queryset
    """
    # Parse filters from query parameters
    trade_ids = request.GET.get('trade_ids', '').split(',') if request.GET.get('trade_ids') else []
    statuses = request.GET.get('statuses', '').split(',') if request.GET.get('statuses') else []
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Apply trade filter
    if trade_ids and trade_ids[0]:  # Check for non-empty string
        # Convert to integers and filter
        trade_id_ints = [int(tid) for tid in trade_ids if tid]
        queryset = queryset.filter(trade_id__in=trade_id_ints)
    
    # Apply status filter
    if statuses and statuses[0]:
        queryset = queryset.filter(trade__status__in=statuses)
    
    # Apply date range filters
    if start_date:
        queryset = queryset.filter(trade__bid_date__gte=start_date)
    
    if end_date:
        queryset = queryset.filter(trade__bid_date__lte=end_date)
    
    return queryset
