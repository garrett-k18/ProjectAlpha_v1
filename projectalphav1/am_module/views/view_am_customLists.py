"""
view_am_customLists.py
----------------------
API views for CustomAssetList.

WHAT: Exposes CRUD endpoints for AM custom lists.
WHY: Frontend needs to create and manage asset lists from the grid.
HOW: Use DRF ModelViewSet with a service layer for list creation/update.
"""

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from am_module.models.model_am_customLists import CustomAssetList
from am_module.serializers.serial_am_customLists import CustomAssetListSerializer
from am_module.services.serv_am_customLists import create_custom_list, replace_custom_list_assets


class CustomAssetListViewSet(viewsets.ModelViewSet):
    """
    CustomAssetListViewSet
    ----------------------
    WHAT: CRUD API for custom asset lists.
    WHY: Users need to save, update, and retrieve custom lists.
    HOW: Delegate create/update logic to the service layer.
    """

    serializer_class = CustomAssetListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Limit lists to current user (plus global lists with no owner).
        """
        # WHAT: Restrict list visibility to the authenticated user
        # WHY: Prevent users from seeing other users' private lists
        # HOW: Filter by created_by user or include unowned lists
        user = self.request.user
        return CustomAssetList.objects.filter(Q(created_by=user) | Q(created_by__isnull=True))

    def perform_create(self, serializer: CustomAssetListSerializer) -> None:
        """
        Create list using service layer and attach assets.
        """
        # WHAT: Pull asset IDs from validated data
        # WHY: Service layer expects AssetIdHub objects
        # HOW: Pop asset_ids and pass them to create_custom_list
        asset_ids = serializer.validated_data.pop("asset_ids", [])
        custom_list = create_custom_list(
            name=serializer.validated_data.get("name", ""),
            description=serializer.validated_data.get("description", ""),
            created_by=self.request.user,
            asset_ids=asset_ids,
        )
        serializer.instance = custom_list

    def perform_update(self, serializer: CustomAssetListSerializer) -> None:
        """
        Update list metadata and optionally replace assets.
        """
        # WHAT: Replace assets only if asset_ids were supplied
        # WHY: Allow partial updates without clearing assets
        # HOW: Pop asset_ids if present, then set after save
        asset_ids = serializer.validated_data.pop("asset_ids", None)
        custom_list = serializer.save()
        replace_custom_list_assets(custom_list=custom_list, asset_ids=asset_ids)
