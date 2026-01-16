"""
serial_am_customLists.py
------------------------
Serializer for CustomAssetList.

WHAT: Defines API fields for custom asset lists.
WHY: Ensures list creation and retrieval follow a consistent schema.
HOW: Use ModelSerializer with explicit asset_ids field for write operations.
"""

from rest_framework import serializers

from am_module.models.model_am_customLists import CustomAssetList
from core.models.model_co_assetIdHub import AssetIdHub


class CustomAssetListSerializer(serializers.ModelSerializer):
    """
    CustomAssetListSerializer
    -------------------------
    WHAT: Serializes list metadata + asset IDs.
    WHY: Frontend needs to create lists and attach assets via IDs.
    HOW: Expose asset_ids as write-only list, assets as read-only list.
    """

    # Write-only list of asset IDs to attach to the list
    asset_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=AssetIdHub.objects.all(),
        required=False,
    )

    # Read-only list of asset IDs already attached to the list
    assets = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )

    class Meta:
        model = CustomAssetList
        fields = [
            "id",
            "name",
            "description",
            "assets",
            "asset_ids",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_by",
            "created_at",
            "updated_at",
        ]
