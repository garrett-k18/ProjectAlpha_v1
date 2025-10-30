"""Proceeds-related acquisition logic helpers."""

from decimal import Decimal
from typing import Optional

from acq_module.models.seller import SellerRawData
from acq_module.models.assumptions import NoteSaleAssumption
from core.models.valuations import Valuation


def fc_sale_proceeds(asset_hub_id: int) -> Decimal:
    """Calculate foreclosure sale proceeds for an asset.
    
    Returns the minimum of:
    1. Total debt from SellerRawData
    2. Initial UW internal valuation (INTERNAL_INITIAL_UW source) asis_value, or
       seller as-is value if initial UW valuation is not available
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Minimum of total debt and valuation, or Decimal('0.00') if data is missing
    """
    # Get the seller raw data for this asset to find total debt and seller as-is value
    raw = (
        SellerRawData.objects
        .filter(asset_hub_id=asset_hub_id)
        .only('total_debt', 'seller_asis_value')
        .first()
    )
    if not raw or raw.total_debt is None:
        return Decimal('0.00')
    
    # Try to get initial UW valuation first
    initial_uw_valuation = (
        Valuation.objects
        .filter(
            asset_hub_id=asset_hub_id,
            source=Valuation.Source.INTERNAL_INITIAL_UW
        )
        .only('asis_value')
        .first()
    )
    
    # Determine the asset value to use
    asset_value = None
    if initial_uw_valuation and initial_uw_valuation.asis_value:
        asset_value = initial_uw_valuation.asis_value
    elif raw.seller_asis_value:
        asset_value = raw.seller_asis_value
    
    if not asset_value or asset_value <= 0:
        return Decimal('0.00')
    
    # Convert to Decimal if needed
    total_debt = (
        raw.total_debt
        if isinstance(raw.total_debt, Decimal)
        else Decimal(str(raw.total_debt))
    )
    
    asset_val = (
        asset_value
        if isinstance(asset_value, Decimal)
        else Decimal(str(asset_value))
    )
    
    # Return the minimum of the two values
    return min(total_debt, asset_val).quantize(Decimal('0.01'))


def reo_asis_proceeds(asset_hub_id: int) -> Decimal:
    """Calculate REO as-is proceeds for an asset.
    
    Returns the initial UW internal valuation asis_value, or seller as-is value
    if initial UW valuation is not available.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Initial UW asis value or seller asis value, or Decimal('0.00') if data is missing
    """
    # Get the seller raw data for this asset to find seller as-is value
    raw = (
        SellerRawData.objects
        .filter(asset_hub_id=asset_hub_id)
        .only('seller_asis_value')
        .first()
    )
    
    # Try to get initial UW valuation first
    initial_uw_valuation = (
        Valuation.objects
        .filter(
            asset_hub_id=asset_hub_id,
            source=Valuation.Source.INTERNAL_INITIAL_UW
        )
        .only('asis_value')
        .first()
    )
    
    # Determine the asset value to use
    asset_value = None
    if initial_uw_valuation and initial_uw_valuation.asis_value:
        asset_value = initial_uw_valuation.asis_value
    elif raw and raw.seller_asis_value:
        asset_value = raw.seller_asis_value
    
    if not asset_value or asset_value <= 0:
        return Decimal('0.00')
    
    # Convert to Decimal if needed and return
    asset_val = (
        asset_value
        if isinstance(asset_value, Decimal)
        else Decimal(str(asset_value))
    )
    
    return asset_val.quantize(Decimal('0.01'))


def reo_arv_proceeds(asset_hub_id: int) -> Decimal:
    """Calculate REO ARV proceeds for an asset.
    
    Returns the initial UW internal valuation arv_value, or seller ARV value
    if initial UW valuation is not available.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Initial UW arv value or seller arv value, or Decimal('0.00') if data is missing
    """
    # Get the seller raw data for this asset to find seller ARV value
    raw = (
        SellerRawData.objects
        .filter(asset_hub_id=asset_hub_id)
        .only('seller_arv_value')
        .first()
    )
    
    # Try to get initial UW valuation first
    initial_uw_valuation = (
        Valuation.objects
        .filter(
            asset_hub_id=asset_hub_id,
            source=Valuation.Source.INTERNAL_INITIAL_UW
        )
        .only('arv_value')
        .first()
    )
    
    # Determine the asset value to use
    asset_value = None
    if initial_uw_valuation and initial_uw_valuation.arv_value:
        asset_value = initial_uw_valuation.arv_value
    elif raw and raw.seller_arv_value:
        asset_value = raw.seller_arv_value
    
    if not asset_value or asset_value <= 0:
        return Decimal('0.00')
    
    # Convert to Decimal if needed and return
    asset_val = (
        asset_value
        if isinstance(asset_value, Decimal)
        else Decimal(str(asset_value))
    )
    
    return asset_val.quantize(Decimal('0.01'))
