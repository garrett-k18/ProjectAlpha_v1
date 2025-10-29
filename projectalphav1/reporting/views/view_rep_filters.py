"""
**WHAT**: Filter dropdown endpoints for reporting dashboard
**WHY**: Populate multi-select filters in sidebar
**WHERE**: Called on dashboard mount and when filters change
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, F
from acq_module.models.seller import Trade


@api_view(['GET'])
def get_trade_options(request):
    """
    **WHAT**: Return all trades for filter dropdown
    **WHY**: Populate multi-select trade filter
    **WHERE**: Called on dashboard mount
    
    **RETURNS**: List of {id, trade_name, seller_name}
    """
    trades = Trade.objects.select_related('seller').values(
        'id', 
        'trade_name',
        seller_name=F('seller__seller_name')
    ).order_by('trade_name')
    
    return Response(list(trades))


@api_view(['GET'])
def get_status_options(request):
    """
    **WHAT**: Return all statuses with counts
    **WHY**: Populate multi-select status filter
    **WHERE**: Called on dashboard mount
    
    **RETURNS**: List of {value, label, count}
    """
    # Get unique statuses from trades
    statuses = Trade.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Map status codes to display labels
    status_map = {
        'DD': 'Due Diligence',
        'AWARDED': 'Awarded',
        'PASS': 'Passed',
        'BOARD': 'Boarded',
        'CLOSED': 'Closed',
        'ACTIVE': 'Active'
    }
    
    result = [
        {
            'value': s['status'],
            'label': status_map.get(s['status'], s['status']),
            'count': s['count']
        }
        for s in statuses if s['status']  # Filter out null statuses
    ]
    
    return Response(result)


@api_view(['GET'])
def get_fund_options(request):
    """
    **WHAT**: Return fund options for filter dropdown
    **WHY**: Populate multi-select fund filter
    **WHERE**: Called on dashboard mount
    
    **NOTE**: Placeholder - replace with actual Fund model query when available
    
    **RETURNS**: List of {id, name, code}
    """
    # TODO: Replace with actual Fund model query
    # from core.models import Fund
    # funds = Fund.objects.values('id', 'name', 'code').order_by('name')
    # return Response(list(funds))
    
    # Placeholder data
    return Response([
        {'id': 1, 'name': 'Fund I', 'code': 'FUND-I'},
        {'id': 2, 'name': 'Fund II', 'code': 'FUND-II'}
    ])


@api_view(['GET'])
def get_entity_options(request):
    """
    **WHAT**: Return entity options for filter dropdown
    **WHY**: Populate multi-select entity filter
    **WHERE**: Called on dashboard mount
    
    **NOTE**: Placeholder - replace with actual Entity model query when available
    
    **RETURNS**: List of {id, name, entity_type}
    """
    # TODO: Replace with actual Entity model query
    # from core.models import Entity
    # entities = Entity.objects.values('id', 'name', 'entity_type').order_by('name')
    # return Response(list(entities))
    
    # Placeholder data
    return Response([
        {'id': 1, 'name': 'Alpha Capital LLC', 'entity_type': 'LLC'},
        {'id': 2, 'name': 'Beta Properties LP', 'entity_type': 'LP'}
    ])
