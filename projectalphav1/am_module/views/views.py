"""
WHAT: API views for AM module
WHY: Provide REST endpoints for asset management data
HOW: Django REST Framework views and viewsets
WHERE: Registered in am_module/urls.py
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from core.models import AssetIdHub, LLCashFlowSeries
from am_module.serializers.serial_am_cashFlows import CashFlowSeriesSerializer


@api_view(['GET'])
def cash_flow_series_view(request, asset_id):
    """
    WHAT: API endpoint to retrieve cash flow series for an asset
    WHY: Frontend needs period-by-period cash flow data for time-series grid
    HOW: Fetch all LLCashFlowSeries records for asset, serialize with purchase date
    
    Args:
        request: HTTP request
        asset_id: AssetIdHub primary key
        
    Returns:
        Response: JSON with purchase_date and periods array
        
    Example Response:
        {
            "purchase_date": "2024-01-15",
            "periods": [
                {
                    "period_number": 0,
                    "period_date": "2024-01-15",
                    "purchase_price": 150000.00,
                    "total_income": 0.00,
                    "total_expenses": 155000.00,
                    "net_cash_flow": -155000.00,
                    ...
                },
                {
                    "period_number": 1,
                    "period_date": "2024-02-15",
                    "income_interest": 1250.00,
                    "servicing_expenses": 350.00,
                    ...
                }
            ]
        }
    """
    # WHAT: Get asset hub with related BlendedOutcomeModel
    # WHY: Need purchase_date from BlendedOutcomeModel
    asset_hub = get_object_or_404(
        AssetIdHub.objects.select_related('blended_outcome_model'),
        pk=asset_id
    )
    print(f"DEBUG: Asset hub found: {asset_hub.id}")
    
    # WHAT: Fetch all cash flow periods for this asset, ordered by period number
    # WHY: Frontend displays periods chronologically
    periods = LLCashFlowSeries.objects.filter(
        asset_hub=asset_hub
    ).order_by('period_number')
    print(f"DEBUG: Periods QuerySet: {periods}")
    print(f"DEBUG: Periods count: {periods.count()}")
    
    # WHAT: Check if asset has purchase date
    # WHY: Purchase date is required to calculate period dates
    if not hasattr(asset_hub, 'blended_outcome_model') or not asset_hub.blended_outcome_model.purchase_date:
        print("DEBUG: No purchase date found")
        return Response(
            {
                'detail': 'Asset does not have a purchase date in BlendedOutcomeModel',
                'purchase_date': None,
                'periods': []
            },
            status=status.HTTP_200_OK
        )
    
    print(f"DEBUG: Purchase date: {asset_hub.blended_outcome_model.purchase_date}")
    
    # WHAT: Manually build response with serialized periods
    # WHY: Simpler than custom serializer, direct control over output
    from am_module.serializers.serial_am_cashFlows import CashFlowPeriodSerializer
    
    serialized_periods = CashFlowPeriodSerializer(periods, many=True).data
    print(f"DEBUG: Serialized periods count: {len(serialized_periods)}")
    
    response_data = {
        'purchase_date': asset_hub.blended_outcome_model.purchase_date,
        'periods': serialized_periods
    }
    
    print(f"DEBUG: Response data keys: {response_data.keys()}")
    print(f"DEBUG: Response periods length: {len(response_data['periods'])}")
    
    return Response(response_data, status=status.HTTP_200_OK)
