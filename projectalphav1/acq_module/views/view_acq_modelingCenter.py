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

from acq_module.models.model_acq_seller import AcqAsset
from acq_module.logic.common import annotate_seller_valuations
from acq_module.models.model_acq_assumptions import TradeLevelAssumption, LoanLevelAssumption
from core.models.model_co_geoAssumptions import StateReference
from core.models.model_co_assumptions import Servicer
from acq_module.logic.logi_acq_metrics import calculate_asset_model_data_fast, summarize_modeling_pool
from acq_module.services.serv_acq_REOCashFlows import generate_pooled_reo_cashflow_series

logger = logging.getLogger(__name__)


def get_permission_classes():
    """Return permission classes based on DEBUG setting."""
    return [AllowAny] if getattr(settings, 'DEBUG', False) else [IsAuthenticated]




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
            annotate_seller_valuations(
                AcqAsset.objects
                .filter(seller_id=seller_id, trade_id=trade_id)
                .exclude(acq_status=AcqAsset.AcquisitionStatus.DROP)
                .select_related('trade', 'asset_hub', 'loan', 'property')
                .order_by('pk')
            )
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
        states = set(a.property.state for a in assets if a.property and a.property.state)
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
                state_ref = state_refs_map.get(asset.property.state) if asset.property and asset.property.state else None
                
                model_data = calculate_asset_model_data_fast(
                    asset=asset,
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
                    'seller_loan_id': asset.loan.sellertape_id if asset.loan else None,  # Use sellertape_id
                    'street_address': asset.property.street_address if asset.property else None,
                    'city': asset.property.city if asset.property else None,
                    'state': asset.property.state if asset.property else None,
                    'current_balance': float(asset.loan.current_balance or 0) if asset.loan else 0,
                    'total_debt': float(asset.loan.total_debt or 0) if asset.loan else 0,
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

        # Pool-level summary metrics for tiles (as-is and ARV)
        summary = summarize_modeling_pool(results, seller_id=seller_id, trade_id=trade_id)

        logger.info(f"[ModelingCenter] Returning {len(results)} assets")
        return Response({'results': results, 'count': len(results), 'summary': summary})
    
    except Exception as e:
        tb = traceback.format_exc()
        print(f"\n[ModelingCenter] ERROR: {e}\n{tb}")
        logger.exception(f"[ModelingCenter] Error: {e}")
        return Response(
            {'error': 'Failed to fetch modeling center data', 'detail': str(e), 'traceback': tb},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes(get_permission_classes())
def pooled_cashflow_series(request, seller_id: int, trade_id: int):
    """
    Get aggregated (pooled) cash flow series for all assets in a trade.
    
    WHAT: API endpoint that returns pool-level aggregated cash flows
    WHY: Enable pool-level cash flow analysis in modeling center
    WHERE: /api/acq/modeling-center/{seller_id}/{trade_id}/pooled-cashflows/
    HOW: Thin view wrapper that delegates to service layer (generate_pooled_reo_cashflow_series)
    
    GET /api/acq/modeling-center/{seller_id}/{trade_id}/pooled-cashflows/?scenario=as_is&model_type=reo_sale
    
    Query Parameters:
        scenario (optional): 'as_is' or 'arv' - defaults to 'as_is'
        model_type (optional): 'reo_sale' or 'fc_sale' - defaults to 'reo_sale'
    
    Returns:
        Same structure as individual asset cash flow series, but with summed values
    """
    logger.info(f"[PooledCashFlows] GET seller={seller_id} trade={trade_id}")
    
    scenario = request.query_params.get('scenario', 'as_is')
    model_type = request.query_params.get('model_type', 'reo_sale')
    
    if scenario not in ['as_is', 'arv']:
        return Response({'error': 'Invalid scenario. Must be "as_is" or "arv"'}, status=status.HTTP_400_BAD_REQUEST)
    
    if model_type not in ['reo_sale', 'fc_sale']:
        return Response({'error': 'Invalid model_type. Must be "reo_sale" or "fc_sale"'}, status=status.HTTP_400_BAD_REQUEST)
    
    # WHAT: Only support REO Sale for now (FC Sale cash flows can be added later)
    if model_type != 'reo_sale':
        return Response({'error': 'Only reo_sale model type supported currently'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # WHAT: Call service function to generate pooled cash flow series
        # WHY: All business logic lives in service layer, view is thin wrapper
        result = generate_pooled_reo_cashflow_series(
            seller_id=seller_id,
            trade_id=trade_id,
            scenario=scenario
        )
        
        return Response(result)
    
    except ValueError as e:
        # WHAT: Handle business logic errors (no assets, no data, etc.)
        # WHY: These are expected errors, return 404 not 500
        logger.warning(f"[PooledCashFlows] Business logic error: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        # WHAT: Handle unexpected errors
        # WHY: These are system errors, return 500
        tb = traceback.format_exc()
        logger.exception(f"[PooledCashFlows] Error: {e}")
        return Response(
            {'error': 'Failed to fetch pooled cash flow data', 'detail': str(e), 'traceback': tb},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
