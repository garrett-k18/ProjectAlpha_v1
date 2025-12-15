"""
am_module.views.view_am_assetcrmcontact

Purpose
-------
API endpoints for managing AssetCRMContact relationships.

What: CRUD operations for asset-to-CRM contact links
Why: Allows frontend to assign/manage multiple contacts per asset
Where: Mounted at /api/am/asset-crm-contacts/
How: Standard DRF ViewSet with filtering by asset_hub and role

Docs Reviewed
-------------
- DRF ViewSets: https://www.django-rest-framework.org/api-guide/viewsets/
- Filtering: https://www.django-rest-framework.org/api-guide/filtering/
"""

from rest_framework import viewsets, filters, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from am_module.models.model_am_amData import AssetCRMContact
from am_module.serializers.serial_am_crm import AssetCRMContactSerializer


class AssetCRMContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing asset-to-CRM contact relationships.
    
    What: CRUD API for AssetCRMContact junction model
    Why: Allows assigning multiple contacts (legal, servicer, broker) to assets
    Where: /api/am/asset-crm-contacts/
    How: Supports filtering by asset_hub_id and role via query params
    
    Examples:
    - GET /api/am/asset-crm-contacts/?asset_hub=123 - All contacts for asset
    - GET /api/am/asset-crm-contacts/?asset_hub=123&role=legal - Legal contact only
    - POST /api/am/asset-crm-contacts/ - Create new contact link
    - DELETE /api/am/asset-crm-contacts/{id}/ - Remove contact link
    """
    
    queryset = AssetCRMContact.objects.all()
    serializer_class = AssetCRMContactSerializer
    permission_classes = [AllowAny]
    
    # Enable search and ordering
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['role', 'notes']
    ordering_fields = ['created_at', 'role']
    ordering = ['role', 'created_at']
    
    def get_queryset(self):
        """
        Filter queryset by query parameters.
        
        What: Manual filtering by asset_hub and role
        Why: django-filter not installed, use simple query param filtering
        How: Check for asset_hub and role in request.query_params
        """
        queryset = super().get_queryset()
        
        # Filter by asset_hub if provided
        asset_hub = self.request.query_params.get('asset_hub')
        if asset_hub:
            queryset = queryset.filter(asset_hub_id=asset_hub)
        
        # Filter by role if provided
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by crm if provided
        crm = self.request.query_params.get('crm')
        if crm:
            queryset = queryset.filter(crm_id=crm)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        WHAT: Create or update AssetCRMContact with idempotent behavior
        WHY: Bypass DRF's unique validation to allow reassigning same contact
        WHERE: POST /api/am/asset-crm-contacts/
        HOW: Manually get_or_create, then serialize and return
        """
        asset_hub_id = request.data.get('asset_hub_id')
        crm_id = request.data.get('crm_id')
        role = request.data.get('role')
        notes = request.data.get('notes', '')
        
        if not all([asset_hub_id, crm_id, role]):
            return Response(
                {'detail': 'asset_hub_id, crm_id, and role are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # WHAT: Get or create contact link (idempotent)
        # WHY: Allow reassigning same contact without error
        # HOW: Use get_or_create with unique fields
        obj, created = AssetCRMContact.objects.get_or_create(
            asset_hub_id=asset_hub_id,
            crm_id=crm_id,
            role=role,
            defaults={'notes': notes}
        )
        
        # Update notes if already exists
        if not created and notes:
            obj.notes = notes
            obj.save()
        
        serializer = self.get_serializer(obj)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
