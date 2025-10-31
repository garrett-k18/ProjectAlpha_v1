"""Purchase price calculation logic for acquisition."""

from decimal import Decimal

from acq_module.models.model_acq_seller import SellerRawData
from am_module.models.boarded_data import BlendedOutcomeModel


def purchase_price(asset_hub_id: int) -> Decimal:
    """Calculate the purchase price for an asset.
    
    For boarded assets, returns the purchase price from BlendedOutcomeModel.
    For non-boarded assets, returns seller as-is value as a fallback approximation.
    Returns Decimal('0.00') if no purchase price data is available.
    
    Args:
        asset_hub_id: The AssetIdHub primary key identifying the asset
        
    Returns:
        Decimal: The purchase price, or Decimal('0.00') if unavailable
    """
    # First try to get the purchase price from boarded data (most accurate for acquired assets)
    boarded_data = (
        BlendedOutcomeModel.objects
        .filter(asset_hub_id=asset_hub_id)
        .only('purchase_price')
        .first()
    )
    if boarded_data and boarded_data.purchase_price is not None:
        # Convert to Decimal if needed for consistency
        return (
            boarded_data.purchase_price
            if isinstance(boarded_data.purchase_price, Decimal)
            else Decimal(str(boarded_data.purchase_price))
        )
    
    # Fallback to seller as-is value for assets not yet boarded
    seller_data = (
        SellerRawData.objects
        .filter(asset_hub_id=asset_hub_id)
        .only('seller_asis_value')
        .first()
    )
    if seller_data and seller_data.seller_asis_value is not None:
        # Use seller as-is value as approximation of purchase price
        return (
            seller_data.seller_asis_value
            if isinstance(seller_data.seller_asis_value, Decimal)
            else Decimal(str(seller_data.seller_asis_value))
        )
    
    # Return zero if no price data available
    return Decimal('0.00')