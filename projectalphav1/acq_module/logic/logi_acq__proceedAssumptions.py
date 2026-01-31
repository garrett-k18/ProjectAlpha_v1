"""Proceeds-related acquisition logic helpers."""

from decimal import Decimal
from typing import Optional

from acq_module.models.model_acq_assumptions import NoteSaleAssumption
from core.models.model_co_valuations import Valuation
from acq_module.logic.logi_acq_outcomespecific import fcoutcomeLogic


def _latest_seller_valuation(asset_hub_id: int) -> Optional[Valuation]:
    """Return most recent seller-provided valuation for an asset."""
    return (
        Valuation.objects
        .filter(
            asset_hub_id=asset_hub_id,
            source__in=[Valuation.Source.SELLER_PROVIDED, Valuation.Source.SELLER],
        )
        .only("asis_value", "arv_value", "value_date", "created_at")
        .order_by("-value_date", "-created_at")
        .first()
    )


def fc_sale_proceeds(asset_hub_id: int) -> Decimal:
    """Calculate foreclosure sale proceeds for an asset.
    
    Returns the minimum of:
    1. Forecasted total debt from fcoutcomeLogic
    2. Initial UW internal valuation (INTERNAL_INITIAL_UW source) asis_value, or
       seller as-is value if initial UW valuation is not available
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Minimum of forecasted total debt and valuation, or Decimal('0.00') if data is missing
    """
    # Get forecasted total debt using outcome logic
    outcome_logic = fcoutcomeLogic()
    total_debt = outcome_logic.forecasted_total_debt(asset_hub_id)
    
    if total_debt <= 0:
        return Decimal('0.00')
    
    # Get seller valuation for fallback values
    seller_val = _latest_seller_valuation(asset_hub_id)
    
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
    elif seller_val and seller_val.asis_value:
        asset_value = seller_val.asis_value
    
    if not asset_value or asset_value <= 0:
        return Decimal('0.00')
    
    # Convert asset value to Decimal if needed
    asset_val = (
        asset_value
        if isinstance(asset_value, Decimal)
        else Decimal(str(asset_value))
    )
    
    # Return the minimum of forecasted total debt and asset valuation
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
    # Get seller valuation for fallback values
    seller_val = _latest_seller_valuation(asset_hub_id)
    
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
    elif seller_val and seller_val.asis_value:
        asset_value = seller_val.asis_value
    
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
    # Get seller valuation for fallback values
    seller_val = _latest_seller_valuation(asset_hub_id)
    
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
    elif seller_val and seller_val.arv_value:
        asset_value = seller_val.arv_value
    
    if not asset_value or asset_value <= 0:
        return Decimal('0.00')
    
    # Convert to Decimal if needed and return
    asset_val = (
        asset_value
        if isinstance(asset_value, Decimal)
        else Decimal(str(asset_value))
    )
    
    return asset_val.quantize(Decimal('0.01'))
