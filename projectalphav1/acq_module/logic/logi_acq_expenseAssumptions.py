"""Expense-related acquisition logic helpers."""

from decimal import Decimal
from typing import Optional

from acq_module.models.seller import SellerRawData
from core.models.assumptions import StateReference


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

"""
def monthly_hoa
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
def property_preservation
def security_cost
def landscaping
def pool_maintenance

""" 