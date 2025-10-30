"""Expense-related acquisition logic helpers."""

from decimal import Decimal
from typing import Optional

from acq_module.models.seller import SellerRawData
from acq_module.models.assumptions import LoanLevelAssumption
from core.models.assumptions import StateReference, HOAAssumption
from core.models.valuations import Valuation


def monthly_tax_for_asset(asset_hub_id: int) -> Decimal:
    """Convenience wrapper: compute monthly property tax for an asset ID.

    Pulls `state` and `seller_asis_value` from `SellerRawData` using the given
    AssetIdHub primary key, then delegates to state tax rates.
    Returns Decimal('0.00') if the asset or required fields are missing.
    """
    raw = (
        SellerRawData.objects
        .filter(asset_hub_id=asset_hub_id)
        .only('state', 'seller_asis_value')
        .first()
    )
    if not raw or not raw.state or not raw.seller_asis_value:
        return Decimal('0.00')

    state = (
        StateReference.objects
        .filter(state_code=raw.state)
        .only('property_tax_rate')
        .first()
    )
    if not state or state.property_tax_rate is None:
        return Decimal('0.00')

    base = (
        raw.seller_asis_value
        if isinstance(raw.seller_asis_value, Decimal)
        else Decimal(str(raw.seller_asis_value))
    )
    if base <= 0:
        return Decimal('0.00')

    return (base * state.property_tax_rate / Decimal('12')).quantize(Decimal('0.01'))


def monthly_insurance_for_asset(asset_hub_id: int) -> Decimal:
    """Convenience wrapper: compute monthly insurance for an asset ID.

    Pulls `state` and `seller_asis_value` from `SellerRawData` using the given
    AssetIdHub primary key, then delegates to state insurance rates.
    Returns Decimal('0.00') if the asset or required fields are missing.
    """
    raw = (
        SellerRawData.objects
        .filter(asset_hub_id=asset_hub_id)
        .only('state', 'seller_asis_value')
        .first()
    )
    if not raw or not raw.state or not raw.seller_asis_value:
        return Decimal('0.00')

    state = (
        StateReference.objects
        .filter(state_code=raw.state)
        .only('insurance_rate_avg')
        .first()
    )
    if not state or state.insurance_rate_avg is None:
        return Decimal('0.00')

    base = (
        raw.seller_asis_value
        if isinstance(raw.seller_asis_value, Decimal)
        else Decimal(str(raw.seller_asis_value))
    )
    if base <= 0:
        return Decimal('0.00')

    return (base * state.insurance_rate_avg / Decimal('12')).quantize(Decimal('0.01'))

def property_preservation(asset_hub_id: int) -> Decimal:
    """Calculate property preservation cost for an asset.
    
    Uses percentage from LoanLevelAssumption.property_preservation_cost multiplied by:
    1. Initial UW valuation (INTERNAL_INITIAL_UW source) asis_value, or
    2. Seller as-is value if initial UW valuation is not available
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Calculated property preservation cost, or Decimal('0.00') if data is missing
    """
    # Get the seller raw data for this asset
    raw = (
        SellerRawData.objects
        .filter(asset_hub_id=asset_hub_id)
        .only('seller_asis_value')
        .first()
    )
    if not raw:
        return Decimal('0.00')
    
    # Get the loan level assumption for this asset
    assumption = (
        LoanLevelAssumption.objects
        .filter(seller_raw_data__asset_hub_id=asset_hub_id)
        .only('property_preservation_cost')
        .first()
    )
    if not assumption or assumption.property_preservation_cost is None:
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
    
    # Determine the base value to use
    base_value = None
    if initial_uw_valuation and initial_uw_valuation.asis_value:
        base_value = initial_uw_valuation.asis_value
    elif raw.seller_asis_value:
        base_value = raw.seller_asis_value
    
    if not base_value or base_value <= 0:
        return Decimal('0.00')
    
    # Convert to Decimal if needed
    base = (
        base_value
        if isinstance(base_value, Decimal)
        else Decimal(str(base_value))
    )
    
    preservation_pct = (
        assumption.property_preservation_cost
        if isinstance(assumption.property_preservation_cost, Decimal)
        else Decimal(str(assumption.property_preservation_cost))
    )
    
    # Calculate property preservation cost as percentage of base value
    return (base * preservation_pct).quantize(Decimal('0.01'))


def monthly_hoa(asset_hub_id: int) -> Decimal:
    """Calculate monthly HOA fee for an asset.
    
    Uses the property type from SellerRawData to cross-reference with the
    HOAAssumption table and return the monthly HOA fee for that property type.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Monthly HOA fee, or Decimal('0.00') if no HOA assumption exists
    """
    # Get the seller raw data for this asset to find property type
    raw = (
        SellerRawData.objects
        .filter(asset_hub_id=asset_hub_id)
        .only('property_type')
        .first()
    )
    if not raw or not raw.property_type:
        return Decimal('0.00')
    
    # Look up HOA assumption for this property type
    hoa_assumption = (
        HOAAssumption.objects
        .filter(property_type=raw.property_type)
        .only('monthly_hoa_fee')
        .first()
    )
    if not hoa_assumption or hoa_assumption.monthly_hoa_fee is None:
        return Decimal('0.00')
    
    # Convert to Decimal if needed and return
    hoa_fee = (
        hoa_assumption.monthly_hoa_fee
        if isinstance(hoa_assumption.monthly_hoa_fee, Decimal)
        else Decimal(str(hoa_assumption.monthly_hoa_fee))
    )
    
    return hoa_fee.quantize(Decimal('0.01'))


"""

def acq_broker_fee
def acq_fee_other
def acq_dd_cost
def acq_legal_cost
def acq_tax_title_cost
def liq_tax_transfer
def liq_title_expense
def liq_broker_fees
def liq_am_fees
def utiliy_electric
def utiliy_gas
def utiliy_water
def utiliy_sewer
def utiliy_trash
def utiliy_other
def property_management
def repairs_maintenance
def marketing
def trashout
def renovation
def security_cost
def landscaping
def pool_maintenance

""" 