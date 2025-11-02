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
                # NOTE: pctUPB is stored as a whole number percentage (e.g., 85.00 = 85%)
                pct = Decimal(str(trade_assumption.pctUPB)) / Decimal('100')  # Convert percentage to decimal
                current_bal = Decimal(str(raw_data.current_balance)) if raw_data.current_balance else Decimal('0.00')
                price = pct * current_bal
                # print(f"[purchase_price] Calculated from pctUPB: {trade_assumption.pctUPB}% × ${current_bal:,.2f} = ${price:,.2f}")
                return price.quantize(Decimal('0.01'))
    except Exception:
        pass
    
    # WHAT: Return 0.00 if no price available
    # WHY: Fallback when no pricing data exists
    return Decimal('0.00')


def purchase_price_metrics(asset_hub_id: int) -> dict:
    """Calculate purchase price as percentage of various valuation metrics.
    
    What: Calculates purchase price ratios for comparison metrics
    Why: Helps assess the acquisition price relative to key asset values
    Where: Called by FC model service to display alongside acquisition price
    How: Divides purchase price by each metric and returns as percentage
    
    Args:
        asset_hub_id: The AssetIdHub primary key identifying the asset
        
    Returns:
        Dict with keys:
        - purchase_of_currentBalance: Purchase price / current balance (as percentage)
        - purchase_of_totalDebt: Purchase price / total debt (as percentage)
        - purchase_of_sellerAsIs: Purchase price / seller as-is value (as percentage)
        - purchase_of_internalUWAsIs: Purchase price / internal UW as-is value (as percentage)
        All values are Decimal or None if metric not available
    """
    from core.models.valuations import Valuation
    
    # print(f"\n{'='*80}")
    # print(f"PURCHASE PRICE METRICS CALCULATION - Asset Hub ID: {asset_hub_id}")
    # print(f"{'='*80}")
    
    # WHAT: Get the purchase price for this asset
    # WHY: This is the numerator for all ratio calculations
    price = purchase_price(asset_hub_id)
    # print(f"Purchase Price: ${price:,.2f}")
    
    # WHAT: Initialize all metrics as None
    # WHY: Return None for metrics that can't be calculated
    result = {
        'purchase_of_currentBalance': None,
        'purchase_of_totalDebt': None,
        'purchase_of_sellerAsIs': None,
        'purchase_of_internalUWAsIs': None
    }
    
    if price <= 0:
        # WHAT: If no purchase price, can't calculate ratios
        # print(f"⚠ Purchase price is $0 - cannot calculate metrics")
        # print(f"{'='*80}\n")
        return result
    
    # WHAT: Get SellerRawData to access current balance and total debt
    # WHY: These are common metrics for price comparison
    raw_data = SellerRawData.objects.filter(asset_hub_id=asset_hub_id).first()
    
    if not raw_data:
        # print(f"❌ No SellerRawData found")
        # print(f"{'='*80}\n")
        return result
    
    # print(f"\nCalculating metrics:")
    
    # WHAT: Calculate purchase price as % of current balance
    if raw_data.current_balance and raw_data.current_balance > 0:
        current_bal = Decimal(str(raw_data.current_balance))
        result['purchase_of_currentBalance'] = ((price / current_bal) * Decimal('100')).quantize(Decimal('0.01'))
        # print(f"  ✓ Current Balance: ${current_bal:,.2f} → {result['purchase_of_currentBalance']}%")
    else:
        # print(f"  ✗ Current Balance: N/A (value: {raw_data.current_balance})")
        pass
    
    # WHAT: Calculate purchase price as % of total debt
    if raw_data.total_debt and raw_data.total_debt > 0:
        total_debt = Decimal(str(raw_data.total_debt))
        result['purchase_of_totalDebt'] = ((price / total_debt) * Decimal('100')).quantize(Decimal('0.01'))
        # print(f"  ✓ Total Debt: ${total_debt:,.2f} → {result['purchase_of_totalDebt']}%")
    else:
        # print(f"  ✗ Total Debt: N/A (value: {raw_data.total_debt})")
        pass
    
    # WHAT: Get seller as-is value from SellerRawData
    # WHY: Seller valuation is stored directly on the SellerRawData model
    if raw_data.seller_asis_value and raw_data.seller_asis_value > 0:
        seller_asis = Decimal(str(raw_data.seller_asis_value))
        result['purchase_of_sellerAsIs'] = ((price / seller_asis) * Decimal('100')).quantize(Decimal('0.01'))
        # print(f"  ✓ Seller As-Is: ${seller_asis:,.2f} → {result['purchase_of_sellerAsIs']}%")
    else:
        # print(f"  ✗ Seller As-Is: N/A (value: {raw_data.seller_asis_value})")
        pass
    
    # WHAT: Get internal UW as-is value from Valuation
    # WHY: Internal underwriting valuation is another key reference point
    try:
        internal_val = (
            Valuation.objects
            .filter(asset_hub_id=asset_hub_id, source='INTERNAL_INITIAL_UW')
            .only('asis_value')
            .first()
        )
        if internal_val and internal_val.asis_value and internal_val.asis_value > 0:
            internal_asis = Decimal(str(internal_val.asis_value))
            result['purchase_of_internalUWAsIs'] = ((price / internal_asis) * Decimal('100')).quantize(Decimal('0.01'))
            # print(f"  ✓ Internal UW As-Is: ${internal_asis:,.2f} → {result['purchase_of_internalUWAsIs']}%")
        else:
            # print(f"  ✗ Internal UW As-Is: Not found or $0")
            pass
    except Exception as e:
        # print(f"  ✗ Internal UW As-Is: ERROR - {str(e)}")
        pass
    
    # print(f"{'='*80}\n")
    return result