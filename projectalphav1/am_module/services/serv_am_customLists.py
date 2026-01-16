"""
serv_am_customLists.py
----------------------
Service layer for CustomAssetList operations.

WHAT: Encapsulates list creation and asset assignment logic.
WHY: Keeps serializers thin and avoids business logic in views.
HOW: Provide helper functions used by the ViewSet.
"""

from typing import Iterable

from am_module.models.model_am_customLists import CustomAssetList
from core.models.model_co_assetIdHub import AssetIdHub


def create_custom_list(
    *,
    name: str,
    description: str = "",
    created_by=None,
    asset_ids: Iterable[AssetIdHub] | None = None,
) -> CustomAssetList:
    """
    Create a new CustomAssetList and optionally attach assets.
    """
    # WHAT: Build the list record
    # WHY: Users need a persisted list entity before assets are attached
    # HOW: Create the list and then add M2M relationships
    custom_list = CustomAssetList.objects.create(
        name=name,
        description=description or "",
        created_by=created_by,
    )

    # WHAT: Attach assets if provided
    # WHY: Create list with selected assets in one operation
    # HOW: Use add() with an iterable of AssetIdHub objects
    if asset_ids:
        custom_list.assets.add(*list(asset_ids))

    return custom_list


def replace_custom_list_assets(
    *,
    custom_list: CustomAssetList,
    asset_ids: Iterable[AssetIdHub] | None = None,
) -> CustomAssetList:
    """
    Replace the assets in a list with a new set.
    """
    # WHAT: Replace the list membership
    # WHY: Support updates that overwrite list contents
    # HOW: Use set() to replace M2M relationships
    if asset_ids is not None:
        custom_list.assets.set(list(asset_ids))
    return custom_list
