"""
Model Recommendations API

WHAT: REST API endpoint for acquisition model recommendations
WHY: Provide frontend with intelligent model selection based on asset characteristics
WHERE: /api/acq/assets/<asset_id>/model-recommendations/
HOW: Uses ModelRecommendationService to calculate probabilities and reasons
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models.model_acq_seller import SellerRawData
from ..services.model_recommendation_service import ModelRecommendationService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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


