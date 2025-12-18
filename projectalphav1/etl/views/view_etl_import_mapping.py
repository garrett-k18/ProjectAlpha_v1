"""
Import Mapping Views

WHAT: API endpoints for managing import column mappings
WHY: Provide CRUD operations and mapping management features
HOW: DRF ViewSet with custom actions for mapping workflows

USAGE:
    # List all mappings
    GET /api/etl/import-mappings/
    
    # Get mapping detail
    GET /api/etl/import-mappings/{id}/
    
    # Create new mapping
    POST /api/etl/import-mappings/
    
    # Update mapping
    PUT /api/etl/import-mappings/{id}/
    
    # Delete mapping
    DELETE /api/etl/import-mappings/{id}/
    
    # Get mappings for specific seller
    GET /api/etl/import-mappings/by_seller/{seller_id}/
    
    # Set mapping as default
    POST /api/etl/import-mappings/{id}/set_default/
    
    # Validate mapping
    GET /api/etl/import-mappings/{id}/validate/
    
    # Apply mapping (mark as used)
    POST /api/etl/import-mappings/{id}/apply/

Docs reviewed:
- DRF ViewSets: https://www.django-rest-framework.org/api-guide/viewsets/
- DRF Actions: https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
- DRF Permissions: https://www.django-rest-framework.org/api-guide/permissions/
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

from etl.models.model_etl_import_mapping import ImportMapping
from etl.serializers.serial_etl_import_mapping import (
    ImportMappingListSerializer,
    ImportMappingSerializer,
    ImportMappingDetailSerializer,
    ImportMappingApplySerializer,
)
from acq_module.models.model_acq_seller import Seller


class ImportMappingViewSet(viewsets.ModelViewSet):
    """
    WHAT: ViewSet for ImportMapping CRUD operations
    WHY: Provide REST API for managing column mappings
    HOW: Standard DRF ViewSet with custom actions
    """
    
    queryset = ImportMapping.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """
        WHAT: Return appropriate serializer based on action
        WHY: Use lightweight serializer for list, full for detail
        HOW: Check action and return corresponding serializer
        """
        if self.action == 'list':
            return ImportMappingListSerializer
        elif self.action == 'retrieve':
            return ImportMappingDetailSerializer
        return ImportMappingSerializer
    
    def get_queryset(self):
        """
        WHAT: Filter queryset based on query parameters
        WHY: Support filtering by seller, active status, etc.
        HOW: Apply filters from query params
        """
        queryset = ImportMapping.objects.all()
        
        # WHAT: Filter by seller ID
        # WHY: Users want to see mappings for specific seller
        # HOW: Check seller query param
        seller_id = self.request.query_params.get('seller', None)
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
        
        # WHAT: Filter by active status
        # WHY: Hide archived mappings by default
        # HOW: Check is_active query param
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # WHAT: Filter by default status
        # WHY: Quick lookup of default mappings
        # HOW: Check is_default query param
        is_default = self.request.query_params.get('is_default', None)
        if is_default is not None:
            queryset = queryset.filter(is_default=is_default.lower() == 'true')
        
        # WHAT: Search by mapping name
        # WHY: Users may want to search for specific mapping
        # HOW: Case-insensitive contains search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(mapping_name__icontains=search) |
                Q(notes__icontains=search) |
                Q(original_filename__icontains=search)
            )
        
        # WHAT: Order by most recently used or created
        # WHY: Show most relevant mappings first
        # HOW: Default ordering from model
        return queryset.select_related('seller', 'trade', 'created_by', 'modified_by')
    
    def perform_create(self, serializer):
        """
        WHAT: Override create to set user fields
        WHY: Track who created the mapping
        HOW: Pass request user to serializer
        """
        serializer.save()
    
    def perform_update(self, serializer):
        """
        WHAT: Override update to set modified_by
        WHY: Track who edited the mapping
        HOW: Pass request user to serializer
        """
        serializer.save()
    
    @action(detail=False, methods=['get'], url_path='by_seller/(?P<seller_id>[^/.]+)')
    def by_seller(self, request, seller_id=None):
        """
        WHAT: Get all mappings for a specific seller
        WHY: Convenient endpoint for seller-specific mapping list
        HOW: Filter by seller ID and return serialized results
        
        URL: GET /api/etl/import-mappings/by_seller/{seller_id}/
        """
        # WHAT: Validate seller exists
        # WHY: Return 404 if seller not found
        # HOW: Use get_object_or_404
        seller = get_object_or_404(Seller, pk=seller_id)
        
        # WHAT: Get all active mappings for seller
        # WHY: Show available mappings for this seller
        # HOW: Filter by seller and active status
        mappings = ImportMapping.objects.filter(
            seller=seller,
            is_active=True
        ).select_related('trade', 'created_by', 'modified_by')
        
        # WHAT: Serialize and return
        # WHY: Return JSON response
        # HOW: Use list serializer
        serializer = ImportMappingListSerializer(mappings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        WHAT: Set mapping as default for its seller
        WHY: Users want to mark preferred mapping
        HOW: Update is_default flag and clear others
        
        URL: POST /api/etl/import-mappings/{id}/set_default/
        """
        # WHAT: Get mapping instance
        # WHY: Need to update is_default flag
        # HOW: Use get_object
        mapping = self.get_object()
        
        # WHAT: Validate mapping has a seller
        # WHY: Can't set default without seller association
        # HOW: Check seller field
        if not mapping.seller:
            return Response(
                {'error': 'Cannot set default for mapping without seller'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # WHAT: Set as default
        # WHY: User requested this mapping as default
        # HOW: Update is_default flag (model handles clearing others)
        mapping.is_default = True
        mapping.save()
        
        # WHAT: Return updated mapping
        # WHY: Confirm change to client
        # HOW: Serialize and return
        serializer = ImportMappingSerializer(mapping)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unset_default(self, request, pk=None):
        """
        WHAT: Remove default status from mapping
        WHY: Users may want to clear default
        HOW: Update is_default flag to False
        
        URL: POST /api/etl/import-mappings/{id}/unset_default/
        """
        # WHAT: Get mapping instance
        # WHY: Need to update is_default flag
        # HOW: Use get_object
        mapping = self.get_object()
        
        # WHAT: Clear default status
        # WHY: User requested to unset default
        # HOW: Update is_default flag
        mapping.is_default = False
        mapping.save()
        
        # WHAT: Return updated mapping
        # WHY: Confirm change to client
        # HOW: Serialize and return
        serializer = ImportMappingSerializer(mapping)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def validate(self, request, pk=None):
        """
        WHAT: Validate mapping against current model
        WHY: Check if mapping is still valid after model changes
        HOW: Call model's validate_mapping method
        
        URL: GET /api/etl/import-mappings/{id}/validate/
        """
        # WHAT: Get mapping instance
        # WHY: Need to validate its column_mapping
        # HOW: Use get_object
        mapping = self.get_object()
        
        # WHAT: Run validation
        # WHY: Check if all mapped fields exist in model
        # HOW: Call model method
        validation_results = mapping.validate_mapping()
        
        # WHAT: Return validation results
        # WHY: Show user if mapping is valid
        # HOW: Return dict with validation details
        return Response(validation_results)
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """
        WHAT: Mark mapping as used (increment usage stats)
        WHY: Track mapping usage for analytics
        HOW: Call model's mark_as_used method
        
        URL: POST /api/etl/import-mappings/{id}/apply/
        """
        # WHAT: Get mapping instance
        # WHY: Need to update usage stats
        # HOW: Use get_object
        mapping = self.get_object()
        
        # WHAT: Update usage statistics
        # WHY: Track when and how often mapping is used
        # HOW: Call model method
        mapping.mark_as_used()
        
        # WHAT: Return updated mapping
        # WHY: Show updated usage count and timestamp
        # HOW: Serialize and return
        serializer = ImportMappingSerializer(mapping)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        WHAT: Archive mapping (set is_active to False)
        WHY: Users may want to hide old mappings without deleting
        HOW: Update is_active flag
        
        URL: POST /api/etl/import-mappings/{id}/archive/
        """
        # WHAT: Get mapping instance
        # WHY: Need to update is_active flag
        # HOW: Use get_object
        mapping = self.get_object()
        
        # WHAT: Archive mapping
        # WHY: User requested to hide this mapping
        # HOW: Set is_active to False
        mapping.is_active = False
        mapping.save()
        
        # WHAT: Return updated mapping
        # WHY: Confirm archival to client
        # HOW: Serialize and return
        serializer = ImportMappingSerializer(mapping)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        WHAT: Restore archived mapping (set is_active to True)
        WHY: Users may want to reactivate archived mappings
        HOW: Update is_active flag
        
        URL: POST /api/etl/import-mappings/{id}/restore/
        """
        # WHAT: Get mapping instance
        # WHY: Need to update is_active flag
        # HOW: Use get_object
        mapping = self.get_object()
        
        # WHAT: Restore mapping
        # WHY: User requested to reactivate this mapping
        # HOW: Set is_active to True
        mapping.is_active = True
        mapping.save()
        
        # WHAT: Return updated mapping
        # WHY: Confirm restoration to client
        # HOW: Serialize and return
        serializer = ImportMappingSerializer(mapping)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        WHAT: Create a copy of existing mapping
        WHY: Users may want to create variations of successful mappings
        HOW: Clone mapping with new name
        
        URL: POST /api/etl/import-mappings/{id}/duplicate/
        Body: {"mapping_name": "New Mapping Name"}
        """
        # WHAT: Get original mapping
        # WHY: Need to copy its data
        # HOW: Use get_object
        original = self.get_object()
        
        # WHAT: Get new mapping name from request
        # WHY: Duplicate needs unique name
        # HOW: Extract from request data
        new_name = request.data.get('mapping_name')
        if not new_name:
            return Response(
                {'error': 'mapping_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # WHAT: Create duplicate mapping
        # WHY: User requested a copy
        # HOW: Create new instance with copied data
        duplicate = ImportMapping.objects.create(
            seller=original.seller,
            trade=None,  # Don't copy trade association
            mapping_name=new_name,
            column_mapping=original.column_mapping.copy(),
            source_columns=original.source_columns.copy(),
            mapping_method=original.mapping_method,
            is_default=False,  # Duplicate is not default
            is_active=True,
            original_filename=original.original_filename,
            notes=f"Duplicated from: {original.mapping_name}",
            created_by=request.user,
            modified_by=request.user,
        )
        
        # WHAT: Return new mapping
        # WHY: Show user the created duplicate
        # HOW: Serialize and return
        serializer = ImportMappingSerializer(duplicate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def get_default(self, request):
        """
        WHAT: Get default mapping for a seller
        WHY: Quick lookup of preferred mapping
        HOW: Filter by seller and is_default
        
        URL: GET /api/etl/import-mappings/get_default/?seller={seller_id}
        """
        # WHAT: Get seller ID from query params
        # WHY: Need to know which seller's default to get
        # HOW: Extract from query params
        seller_id = request.query_params.get('seller')
        if not seller_id:
            return Response(
                {'error': 'seller parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # WHAT: Get default mapping for seller
        # WHY: User requested default mapping
        # HOW: Filter by seller and is_default
        try:
            mapping = ImportMapping.objects.get(
                seller_id=seller_id,
                is_default=True,
                is_active=True
            )
        except ImportMapping.DoesNotExist:
            return Response(
                {'error': 'No default mapping found for this seller'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # WHAT: Return default mapping
        # WHY: Show user the default mapping
        # HOW: Serialize and return
        serializer = ImportMappingDetailSerializer(mapping)
        return Response(serializer.data)
