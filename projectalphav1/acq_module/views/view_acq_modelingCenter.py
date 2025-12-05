"""
Modeling Center API

WHAT: Bulk endpoint for Modeling Center grid data
WHY: Fetching 600+ individual model endpoints is too slow (minutes)
WHERE: /api/acq/modeling-center/{seller_id}/{trade_id}/
HOW: Single query with prefetch, bulk calculations in Python
"""

import logging
import traceback
from decimal import Decimal
from typing import Dict, Any, Optional

from django.conf import settings
from django.db.models import Prefetch
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from acq_module.models.model_acq_seller import SellerRawData
from acq_module.models.model_acq_assumptions import TradeLevelAssumption, LoanLevelAssumption
from core.models.model_co_geoAssumptions import StateReference
from core.models.model_co_assumptions import Servicer

logger = logging.getLogger(__name__)


def get_permission_classes():
    """Return permission classes based on DEBUG setting."""
    return [AllowAny] if getattr(settings, 'DEBUG', False) else [IsAuthenticated]


def calculate_asset_model_data_fast(
    raw_data: SellerRawData,
    trade_assumption: Optional[TradeLevelAssumption],
    loan_assumption: Optional[LoanLevelAssumption],
    state_ref: Optional[StateReference],
    servicer: Optional[Servicer],
    bid_pct: Decimal = Decimal('0.85'),  # Default 85% of UPB
) -> Dict[str, Any]:
    """
    Calculate modeling data for a single asset - FAST version.
    
    Uses simple calculations without expensive per-asset function calls.
    For detailed calculations, use the loan-level modal.
    
    Field names verified from models:
    - TradeLevelAssumption: pctUPB, acq_legal_cost, acq_dd_cost, acq_tax_title_cost, acq_broker_fees, acq_other_costs
    - StateReference: fc_state_months, rehab_duration, reo_marketing_duration, fc_legal_fees_avg
    - SellerRawData: sellertape_id, seller_asis_value, seller_arv_value, current_balance, total_debt
    - Servicer: servicing_transfer_duration, liqfee_pct
    """
    # -------------------------------------------------------------------------
    # Basic Data
    # -------------------------------------------------------------------------
    current_balance = raw_data.current_balance or Decimal('0')
    total_debt = raw_data.total_debt or Decimal('0')
    seller_asis = raw_data.seller_asis_value or Decimal('0')
    
    # -------------------------------------------------------------------------
    # Acquisition Price (simple: bid % of UPB)
    # -------------------------------------------------------------------------
    acq_price = current_balance * bid_pct
    
    # -------------------------------------------------------------------------
    # Timeline Calculations (from state reference, no per-asset queries)
    # -------------------------------------------------------------------------
    servicing_transfer_months = 1  # Default
    if servicer and servicer.servicing_transfer_duration:
        servicing_transfer_months = servicer.servicing_transfer_duration
    
    # Foreclosure from state reference: fc_state_months
    foreclosure_months = 12  # Default
    if state_ref and state_ref.fc_state_months:
        foreclosure_months = state_ref.fc_state_months
    
    # Apply FC duration override if exists
    if loan_assumption and loan_assumption.reo_fc_duration_override_months:
        foreclosure_months = max(0, foreclosure_months + loan_assumption.reo_fc_duration_override_months)
    
    # REO marketing from state reference: reo_marketing_duration
    reo_marketing_months = 6  # Default
    if state_ref and state_ref.reo_marketing_duration:
        reo_marketing_months = state_ref.reo_marketing_duration
    
    # REO renovation (only for ARV scenario): rehab_duration
    reo_renovation_months = 3  # Default
    if state_ref and state_ref.rehab_duration:
        reo_renovation_months = state_ref.rehab_duration
    
    # Total timeline
    total_timeline_asis = servicing_transfer_months + foreclosure_months + reo_marketing_months
    total_timeline_arv = total_timeline_asis + reo_renovation_months
    
    # -------------------------------------------------------------------------
    # Expected Proceeds (use seller values if available)
    # -------------------------------------------------------------------------
    proceeds_asis = raw_data.seller_asis_value or current_balance * Decimal('0.70')  # 70% default
    proceeds_arv = raw_data.seller_arv_value or proceeds_asis * Decimal('1.15')  # 15% above as-is
    
    # -------------------------------------------------------------------------
    # Expense Calculations
    # -------------------------------------------------------------------------
    # Acquisition costs from trade assumption
    acq_costs = Decimal('0')
    if trade_assumption:
        acq_costs += trade_assumption.acq_broker_fees or Decimal('0')
        acq_costs += trade_assumption.acq_other_costs or Decimal('0')
        acq_costs += trade_assumption.acq_legal_cost or Decimal('0')
        acq_costs += trade_assumption.acq_dd_cost or Decimal('0')
        acq_costs += trade_assumption.acq_tax_title_cost or Decimal('0')
    
    # Carry costs (simplified estimates: $200/mo taxes, $100/mo insurance, $150/mo servicing)
    monthly_carry = Decimal('450')
    carry_costs_asis = monthly_carry * Decimal(total_timeline_asis)
    carry_costs_arv = monthly_carry * Decimal(total_timeline_arv)
    
    # Legal costs from state: fc_legal_fees_avg
    legal_cost = Decimal('5000')  # Default
    if state_ref and state_ref.fc_legal_fees_avg:
        legal_cost = state_ref.fc_legal_fees_avg
    
    # Liquidation costs: servicer liqfee_pct + 6% broker
    liq_pct = Decimal('0.06')  # 6% broker default
    if servicer and servicer.liqfee_pct:
        liq_pct += servicer.liqfee_pct
    liq_costs_asis = proceeds_asis * liq_pct
    liq_costs_arv = proceeds_arv * liq_pct
    
    # Total costs
    total_costs_asis = acq_costs + carry_costs_asis + legal_cost + liq_costs_asis
    total_costs_arv = acq_costs + carry_costs_arv + legal_cost + liq_costs_arv
    
    # -------------------------------------------------------------------------
    # Financial Metrics
    # -------------------------------------------------------------------------
    net_pl_asis = proceeds_asis - acq_price - total_costs_asis
    net_pl_arv = proceeds_arv - acq_price - total_costs_arv
    
    moic_asis = Decimal('0')
    moic_arv = Decimal('0')
    if acq_price > 0:
        moic_asis = (proceeds_asis - total_costs_asis) / acq_price
        moic_arv = (proceeds_arv - total_costs_arv) / acq_price
    
    # Bid percentages (match naming used in reporting/blended outcome model)
    bid_pct_upb_val = Decimal('0')
    bid_pct_td_val = Decimal('0')
    bid_pct_sellerasis_val = Decimal('0')
    if current_balance > 0:
        bid_pct_upb_val = (acq_price / current_balance) * 100
    if total_debt > 0:
        bid_pct_td_val = (acq_price / total_debt) * 100
    if seller_asis > 0:
        bid_pct_sellerasis_val = (acq_price / seller_asis) * 100
    
    return {
        'id': raw_data.pk,
        'asset_hub_id': raw_data.asset_hub_id,
        'seller_loan_id': raw_data.sellertape_id,
        'street_address': raw_data.street_address,
        'city': raw_data.city,
        'state': raw_data.state,
        'current_balance': float(current_balance),
        'total_debt': float(total_debt),
        'primary_model': 'reo_sale',
        'total_duration_months_asis': total_timeline_asis,
        'total_duration_months_arv': total_timeline_arv,
        'acquisition_price': float(acq_price),
        'total_costs_asis': float(total_costs_asis),
        'expected_proceeds_asis': float(proceeds_asis),
        'net_pl_asis': float(net_pl_asis),
        'moic_asis': float(moic_asis),
        'total_costs_arv': float(total_costs_arv),
        'expected_proceeds_arv': float(proceeds_arv),
        'net_pl_arv': float(net_pl_arv),
        'moic_arv': float(moic_arv),
        'bid_pct_upb': float(bid_pct_upb_val),
        'bid_pct_td': float(bid_pct_td_val),
        'bid_pct_sellerasis': float(bid_pct_sellerasis_val),
    }


@api_view(['GET'])
@permission_classes(get_permission_classes())
def modeling_center_data(request, seller_id: int, trade_id: int):
    """
    Get bulk modeling data for all assets in a trade.
    
    GET /api/acq/modeling-center/{seller_id}/{trade_id}/
    
    Returns all assets with pre-calculated modeling metrics for the grid.
    Much faster than calling individual model endpoints.
    """
    logger.info(f"[ModelingCenter] GET seller={seller_id} trade={trade_id}")
    
    if not seller_id or not trade_id:
        return Response({'results': [], 'count': 0})
    
    try:
        # -------------------------------------------------------------------------
        # Prefetch all required data in bulk
        # -------------------------------------------------------------------------
        print(f"\n[ModelingCenter] Starting bulk fetch for seller={seller_id}, trade={trade_id}")
        
        # Get trade assumption (shared across all assets)
        trade_assumption = TradeLevelAssumption.objects.filter(
            trade_id=trade_id
        ).select_related('servicer').first()
        print(f"[ModelingCenter] Trade assumption: {trade_assumption}")
        
        servicer = trade_assumption.servicer if trade_assumption else None
        print(f"[ModelingCenter] Servicer: {servicer}")
        
        # Get all assets for this trade (exclude dropped)
        assets = list(
            SellerRawData.objects
            .filter(seller_id=seller_id, trade_id=trade_id)
            .exclude(acq_status=SellerRawData.AcquisitionStatus.DROP)
            .select_related('trade', 'asset_hub')
            .order_by('pk')
        )
        print(f"[ModelingCenter] Found {len(assets)} assets")
        
        if not assets:
            return Response({'results': [], 'count': 0})
        
        # Get all asset_hub_ids
        asset_hub_ids = [a.asset_hub_id for a in assets if a.asset_hub_id]
        
        # Bulk fetch loan level assumptions
        loan_assumptions_qs = LoanLevelAssumption.objects.filter(
            asset_hub_id__in=asset_hub_ids
        )
        loan_assumptions_map = {la.asset_hub_id: la for la in loan_assumptions_qs}
        
        # Get unique states and bulk fetch state references
        states = set(a.state for a in assets if a.state)
        state_refs_qs = StateReference.objects.filter(state_code__in=states)
        state_refs_map = {sr.state_code: sr for sr in state_refs_qs}
        
        # Get bid percentage from trade assumption: pctUPB (stored as 85.00 for 85%)
        bid_pct = Decimal('0.85')  # Default 85%
        if trade_assumption and trade_assumption.pctUPB:
            bid_pct = trade_assumption.pctUPB / Decimal('100')  # Convert from percentage (85.00 -> 0.85)
        
        print(f"[ModelingCenter] Using bid_pct={bid_pct}")
        
        # -------------------------------------------------------------------------
        # Calculate modeling data for each asset (FAST - no per-asset queries)
        # -------------------------------------------------------------------------
        results = []
        for asset in assets:
            try:
                loan_assumption = loan_assumptions_map.get(asset.asset_hub_id)
                state_ref = state_refs_map.get(asset.state) if asset.state else None
                
                model_data = calculate_asset_model_data_fast(
                    raw_data=asset,
                    trade_assumption=trade_assumption,
                    loan_assumption=loan_assumption,
                    state_ref=state_ref,
                    servicer=servicer,
                    bid_pct=bid_pct,
                )
                results.append(model_data)
            except Exception as e:
                logger.warning(f"[ModelingCenter] Error calculating asset {asset.pk}: {e}")
                # Return basic data even if calculation fails
                results.append({
                    'id': asset.pk,
                    'asset_hub_id': asset.asset_hub_id,
                    'seller_loan_id': asset.sellertape_id,  # Use sellertape_id
                    'street_address': asset.street_address,
                    'city': asset.city,
                    'state': asset.state,
                    'current_balance': float(asset.current_balance or 0),
                    'total_debt': float(asset.total_debt or 0),
                    'primary_model': None,
                    'acquisition_price': 0,
                    'total_costs_asis': 0,
                    'expected_proceeds_asis': 0,
                    'net_pl_asis': 0,
                    'moic_asis': 0,
                    'total_costs_arv': 0,
                    'expected_proceeds_arv': 0,
                    'net_pl_arv': 0,
                    'moic_arv': 0,
                    'bid_pct_upb': 0,
                    'total_duration_months_asis': 0,
                    'total_duration_months_arv': 0,
                })
        
        logger.info(f"[ModelingCenter] Returning {len(results)} assets")
        return Response({'results': results, 'count': len(results)})
    
    except Exception as e:
        tb = traceback.format_exc()
        print(f"\n[ModelingCenter] ERROR: {e}\n{tb}")
        logger.exception(f"[ModelingCenter] Error: {e}")
        return Response(
            {'error': 'Failed to fetch modeling center data', 'detail': str(e), 'traceback': tb},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
