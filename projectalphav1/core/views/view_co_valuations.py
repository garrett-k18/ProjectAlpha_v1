"""
API views for Valuation model operations.

What this does:
- Provides REST API endpoints for creating and updating valuations
- Handles Internal Initial UW valuations from frontend
- Creates/updates Valuation records with proper source tagging

Location: projectalphav1/core/views/view_co_valuations.py
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import logging

from core.models.model_co_valuations import Valuation
from core.models import AssetIdHub

# WHAT: Module-level logger for valuation operations
logger = logging.getLogger(__name__)


@api_view(['POST', 'PUT', 'PATCH'])
def create_or_update_valuation(request, asset_hub_id):
    """
    Create or update a valuation for a specific asset.
    
    What this does:
    - Accepts valuation data for a specific source (e.g., internalInitialUW)
    - Creates new valuation or updates existing one based on source + date
    - Returns the saved valuation data
    
    Args:
        request: Django request object containing valuation data
        asset_hub_id: ID of the AssetIdHub to associate valuation with
        
    Expected payload:
        {
            "source": "internalInitialUW",  # Required: Valuation source
            "asis_value": 250000,           # Optional: As-is value
            "arv_value": 300000,            # Optional: ARV value
            "value_date": "2025-11-03",     # Optional: Date of valuation (defaults to today)
            "rehab_est_total": 50000,       # Optional: Total rehab estimate
            "notes": "..."                   # Optional: Notes
        }
        
    Returns:
        JSON response with saved valuation data
    """
    # WHAT: Validate asset_hub_id exists
    try:
        asset_hub = AssetIdHub.objects.get(pk=asset_hub_id)
    except AssetIdHub.DoesNotExist:
        return Response(
            {"error": f"AssetIdHub with ID {asset_hub_id} does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # WHAT: Extract data from request
    data = request.data
    source = data.get('source')
    
    # WHAT: Validate required fields
    if not source:
        return Response(
            {"error": "source field is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # WHAT: Validate source is a valid choice
    valid_sources = [choice[0] for choice in Valuation.Source.choices]
    if source not in valid_sources:
        return Response(
            {"error": f"Invalid source. Must be one of: {', '.join(valid_sources)}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        with transaction.atomic():
            # WHAT: Get or create valuation for this asset/source/date combination
            # WHY: Unique constraint ensures only one valuation per source per date
            value_date = data.get('value_date')
            if not value_date:
                from datetime import date
                value_date = date.today()
            
            valuation, created = Valuation.objects.get_or_create(
                asset_hub=asset_hub,
                source=source,
                value_date=value_date,
                defaults={
                    'asis_value': data.get('asis_value'),
                    'arv_value': data.get('arv_value'),
                    'rehab_est_total': data.get('rehab_est_total'),
                    'notes': data.get('notes', ''),
                    'created_by': request.user if request.user.is_authenticated else None,
                }
            )
            
            # WHAT: If not created (already exists), update the values
            if not created:
                # WHAT: Update fields that are provided in the request
                if 'asis_value' in data:
                    valuation.asis_value = data.get('asis_value')
                if 'arv_value' in data:
                    valuation.arv_value = data.get('arv_value')
                if 'rehab_est_total' in data:
                    valuation.rehab_est_total = data.get('rehab_est_total')
                if 'notes' in data:
                    valuation.notes = data.get('notes')
                
                valuation.updated_by = request.user if request.user.is_authenticated else None
                valuation.save()
            
            # WHAT: Build response data
            response_data = {
                'id': valuation.id,
                'asset_hub_id': asset_hub_id,
                'source': valuation.source,
                'asis_value': valuation.asis_value,
                'arv_value': valuation.arv_value,
                'rehab_est_total': valuation.rehab_est_total,
                'value_date': valuation.value_date,
                'notes': valuation.notes,
                'created': created,
                'updated_at': valuation.updated_at,
            }
            
            logger.info(
                f"{'Created' if created else 'Updated'} valuation ID {valuation.id} "
                f"for asset {asset_hub_id}, source: {source}"
            )
            
            return Response(response_data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.exception(f"Error saving valuation for asset {asset_hub_id}: {str(e)}")
        return Response(
            {"error": "Failed to save valuation", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_valuations(request, asset_hub_id):
    """
    Get all valuations for a specific asset.
    
    What this does:
    - Retrieves all valuation records for the given asset
    - Filters by source if specified in query params
    - Returns list of valuations ordered by date (most recent first)
    
    Args:
        request: Django request object
        asset_hub_id: ID of the AssetIdHub
        
    Query params:
        source: Optional - filter by valuation source (e.g., 'internalInitialUW')
        
    Returns:
        JSON array of valuation records
    """
    # WHAT: Validate asset_hub_id exists
    try:
        asset_hub = AssetIdHub.objects.get(pk=asset_hub_id)
    except AssetIdHub.DoesNotExist:
        return Response(
            {"error": f"AssetIdHub with ID {asset_hub_id} does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        # WHAT: Get all valuations for this asset
        valuations = Valuation.objects.filter(asset_hub=asset_hub)
        
        # WHAT: Filter by source if provided
        source_filter = request.query_params.get('source')
        if source_filter:
            valuations = valuations.filter(source=source_filter)
        
        # WHAT: Order by date (most recent first)
        valuations = valuations.order_by('-value_date', '-created_at')
        
        # WHAT: Build response data
        response_data = []
        for val in valuations:
            response_data.append({
                'id': val.id,
                'source': val.source,
                'asis_value': val.asis_value,
                'arv_value': val.arv_value,
                'rehab_est_total': val.rehab_est_total,
                'value_date': val.value_date,
                'notes': val.notes,
                'created_at': val.created_at,
                'updated_at': val.updated_at,
            })
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error retrieving valuations for asset {asset_hub_id}: {str(e)}")
        return Response(
            {"error": "Failed to retrieve valuations", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

