"""Purchase price calculation logic for acquisition."""

from decimal import Decimal
from acq_module.models.model_acq_assumptions import LoanLevelAssumption, TradeLevelAssumption
from acq_module.models.model_acq_seller import SellerRawData

def purchase_price(asset_hub_id: int) -> Decimal:
    """Return the acquisition price for the provided asset.
    
    What: Gets the acquisition/purchase price for an asset
    Why: Used across acquisition calculations (broker fees, costs, etc.)
    Where: Called by various acquisition logic functions
    How: Returns user-entered acquisition_price from LoanLevelAssumption if available,
         otherwise calculates from pctUPB * current_balance if pctUPB is set,
         otherwise returns Decimal('0.00')

    Args:
        asset_hub_id: The AssetIdHub primary key identifying the asset

    Returns:
        Decimal: The acquisition price (user-entered > calculated > 0.00)
    """
    # WHAT: Check for user-entered acquisition price first
    # WHY: User-entered value takes priority over calculated values
    loan_assumption = LoanLevelAssumption.objects.filter(asset_hub_id=asset_hub_id).first()
    
    if loan_assumption and loan_assumption.acquisition_price:
        return Decimal(str(loan_assumption.acquisition_price))
    
    # WHAT: Try to calculate from pctUPB if available
    # WHY: Trade-level assumptions may define purchase price as % of UPB
    try:
        raw_data = SellerRawData.objects.filter(asset_hub_id=asset_hub_id).select_related('trade').first()
        
        if raw_data and raw_data.trade:
            trade_assumption = TradeLevelAssumption.objects.filter(trade=raw_data.trade).first()
            
            if trade_assumption and trade_assumption.pctUPB and raw_data.current_balance:
                # WHAT: Calculate purchase price as pctUPB * current_balance
                # WHY: Trade may define pricing as percentage of UPB
                pct = Decimal(str(trade_assumption.pctUPB)) / Decimal('100')  # Convert percentage to decimal
                price = pct * (raw_data.current_balance or Decimal('0.00'))
                return price.quantize(Decimal('0.01'))
    except Exception:
        pass
    
    # WHAT: Return 0.00 if no price available
    # WHY: Fallback when no pricing data exists
    return Decimal('0.00')