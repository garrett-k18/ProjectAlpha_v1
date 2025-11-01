"""
Model Recommendations API

WHAT: REST API endpoint for acquisition model recommendations
WHY: Provide frontend with intelligent model selection based on asset characteristics
WHERE: /api/acq/assets/<asset_id>/model-recommendations/
HOW: Uses ModelRecommendationService to calculate probabilities and reasons
"""

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models.model_acq_seller import SellerRawData
from ..services.serv_acq_modelRecs import ModelRecommendationService
from ..services.serv_acq_FCModel import get_fc_timeline_sums, get_fc_expense_values
from ..models.model_acq_assumptions import LoanLevelAssumption


# WHAT: Helper to get permission classes based on DEBUG setting
# WHY: Allow unauthenticated access in dev for faster iteration, require auth in production
# HOW: Returns AllowAny when DEBUG=True, IsAuthenticated when DEBUG=False (mimics DevAuthBypassMixin pattern)
def get_permission_classes():
    """Return permission classes based on DEBUG setting."""
    return [AllowAny] if getattr(settings, 'DEBUG', False) else [IsAuthenticated]


@api_view(['GET'])
@permission_classes(get_permission_classes())
def get_asset_model_recommendations(request, asset_id):
    """
    Get model recommendations for a specific asset.
    
    GET /api/acq/assets/<asset_id>/model-recommendations/
    
    Returns:
        {
            "asset_id": 12345,
            "asset_status": "NPL",
            "models": [
                {
                    "model_key": "fc_sale",
                    "model_name": "FC Sale",
                    "probability": 50,
                    "reasons": ["High LTV (98.5%) suggests limited short sale viability", ...],
                    "is_recommended": true,
                    "display_order": 1
                },
                ...
            ],
            "metrics": {
                "ltv": 98.5,
                "tdtv": 95.2,
                "has_equity": false,
                "is_delinquent": true,
                "is_foreclosure": true,
                "delinquency_months": 14
            }
        }
    """
    # Get asset or 404
    asset = get_object_or_404(SellerRawData, asset_hub_id=asset_id)
    
    try:
        # Generate recommendations using service
        service = ModelRecommendationService(asset)
        recommendations = service.get_recommendations_dict()
        
        return Response(recommendations, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {
                'error': 'Failed to generate model recommendations',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes(get_permission_classes())
def bulk_model_recommendations(request):
    """
    Get model recommendations for multiple assets at once.
    
    POST /api/acq/model-recommendations/bulk/
    
    Request Body:
        {
            "asset_ids": [12345, 12346, 12347, ...]
        }
    
    Returns:
        {
            "results": [
                {
                    "asset_id": 12345,
                    "asset_status": "NPL",
                    "models": [...],
                    "metrics": {...}
                },
                ...
            ],
            "count": 3
        }
    """
    asset_ids = request.data.get('asset_ids', [])
    
    if not asset_ids:
        return Response(
            {'error': 'asset_ids list is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Limit to reasonable batch size
    if len(asset_ids) > 100:
        return Response(
            {'error': 'Maximum 100 assets per bulk request'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Fetch all assets in one query
        assets = SellerRawData.objects.filter(asset_hub_id__in=asset_ids)
        
        # Generate recommendations for each
        results = []
        for asset in assets:
            service = ModelRecommendationService(asset)
            recommendations = service.get_recommendations_dict()
            results.append(recommendations)
        
        return Response(
            {
                'results': results,
                'count': len(results)
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                'error': 'Failed to generate bulk recommendations',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes(get_permission_classes())
def get_fc_model_timeline_sums(request, asset_id):
    """
    Get foreclosure model timeline sums and expense values for a specific asset.
    
    GET /api/acq/assets/<asset_id>/fc-model-sums/
    
    Returns:
        {
            "servicing_transfer_months": 2.5,
            "foreclosure_days": 180,
            "foreclosure_months": 5.9,
            "foreclosure_months_base": 5.9,
            "fc_duration_override_months": 0,
            "total_timeline_months": 8.4,
            "servicing_fees": 500.00,
            "taxes": 250.00,
            "insurance": 150.00,
            "legal_cost": 2000.00
        }
    """
    # Get asset or 404
    asset = get_object_or_404(SellerRawData, asset_hub_id=asset_id)
    
    try:
        # WHAT: Get timeline sums using service
        # WHY: Fetch timeline duration data
        timeline_sums = get_fc_timeline_sums(asset.asset_hub_id)
        
        # WHAT: Get expense values using service, passing timeline durations
        # WHY: Fetch expense data from models, multiplied by durations
        expense_values = get_fc_expense_values(
            asset.asset_hub_id, 
            total_timeline_months=timeline_sums.get('total_timeline_months'),
            servicing_transfer_months=timeline_sums.get('servicing_transfer_months'),
            foreclosure_months=timeline_sums.get('foreclosure_months')
        )
        
        # WHAT: Merge timeline and expense data into single response
        # WHY: Frontend expects all FC model data in one endpoint
        response_data = {**timeline_sums, **expense_values}
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {
                'error': 'Failed to calculate FC timeline sums and expense values',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST', 'PUT'])
@permission_classes(get_permission_classes())
def update_fc_duration_override(request, asset_id):
    """
    Update FC duration override for a specific asset.
    
    POST/PUT /api/acq/assets/<asset_id>/fc-duration-override/
    
    Request Body:
        {
            "fc_duration_override_months": 3  // Positive adds months, negative subtracts
        }
    
    Returns:
        {
            "success": true,
            "fc_duration_override_months": 3,
            "message": "FC duration override updated successfully"
        }
    """
    # Get asset or 404
    asset = get_object_or_404(SellerRawData, asset_hub_id=asset_id)
    
    override_value = request.data.get('fc_duration_override_months')
    
    if override_value is None:
        return Response(
            {'error': 'fc_duration_override_months is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # WHAT: Get asset hub ID from SellerRawData
        # WHY: LoanLevelAssumption now uses asset_hub FK instead of seller_raw_data
        asset_hub_id = asset.asset_hub_id if asset.asset_hub else None
        
        if not asset_hub_id:
            return Response(
                {'error': 'Asset does not have an associated AssetIdHub'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # WHAT: Get existing LoanLevelAssumption for this asset hub
        # WHY: All fields are now nullable, so we can create if needed
        loan_assumption = LoanLevelAssumption.objects.filter(asset_hub_id=asset_hub_id).first()
        
        if loan_assumption:
            # WHAT: Update the override value on existing record
            # WHY: Record exists, just update the override field
            loan_assumption.fc_duration_override_months = int(override_value)
            loan_assumption.save()
        else:
            # WHAT: Create a new LoanLevelAssumption with only the override value
            # WHY: All fields are nullable now, so we only need to set the override
            loan_assumption = LoanLevelAssumption.objects.create(
                asset_hub_id=asset_hub_id,
                fc_duration_override_months=int(override_value)  # WHAT: Set the override value
            )
        
        return Response(
            {
                'success': True,
                'fc_duration_override_months': loan_assumption.fc_duration_override_months,
                'message': 'FC duration override updated successfully'
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        import traceback
        return Response(
            {
                'error': 'Failed to update FC duration override',
                'detail': str(e),
                'traceback': traceback.format_exc() if settings.DEBUG else None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST', 'PUT'])
@permission_classes(get_permission_classes())
def update_acquisition_price(request, asset_id):
    """
    Update acquisition price for a specific asset.
    
    POST/PUT /api/acq/assets/<asset_id>/acquisition-price/
    
    Request Body:
        {
            "acquisition_price": 50000.00
        }
    
    Returns:
        {
            "success": true,
            "acquisition_price": 50000.00,
            "message": "Acquisition price updated successfully"
        }
    """
    # Get asset or 404
    asset = get_object_or_404(SellerRawData, asset_hub_id=asset_id)
    
    acquisition_price_value = request.data.get('acquisition_price')
    
    if acquisition_price_value is None:
        return Response(
            {'error': 'acquisition_price is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # WHAT: Get asset hub ID from SellerRawData
        # WHY: LoanLevelAssumption uses asset_hub FK
        asset_hub_id = asset.asset_hub_id if asset.asset_hub else None
        
        if not asset_hub_id:
            return Response(
                {'error': 'Asset does not have an associated AssetIdHub'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # WHAT: Get or create LoanLevelAssumption for this asset hub
        # WHY: Store acquisition price at loan level
        loan_assumption = LoanLevelAssumption.objects.filter(asset_hub_id=asset_hub_id).first()
        
        if loan_assumption:
            # WHAT: Update the acquisition price on existing record
            # WHY: Record exists, just update the price field
            loan_assumption.acquisition_price = float(acquisition_price_value)
            loan_assumption.save()
        else:
            # WHAT: Create a new LoanLevelAssumption with the acquisition price
            # WHY: All fields are nullable, so we only need to set the price
            loan_assumption = LoanLevelAssumption.objects.create(
                asset_hub_id=asset_hub_id,
                acquisition_price=float(acquisition_price_value)
            )
        
        return Response(
            {
                'success': True,
                'acquisition_price': loan_assumption.acquisition_price,
                'message': 'Acquisition price updated successfully'
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        import traceback
        return Response(
            {
                'error': 'Failed to update acquisition price',
                'detail': str(e),
                'traceback': traceback.format_exc() if settings.DEBUG else None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


