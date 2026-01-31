"""
Views for seller/trade dropdowns and summary endpoints.

WHAT: Basic endpoints for seller/trade selection and pool summaries.
WHY: These are needed by the acquisitions dashboard dropdowns and widgets.
"""

import logging
from decimal import Decimal
from django.db.models import Sum, Count, Q, Exists, OuterRef, F, DecimalField, Value
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from acq_module.models.model_acq_seller import Seller, Trade, AcqAsset
from acq_module.logic.common import annotate_seller_valuations
from core.models.model_co_valuations import Valuation
from acq_module.logic import (
    current_balance_stratification_dynamic,
    total_debt_stratification_dynamic,
    seller_asis_value_stratification_dynamic,
    wac_stratification_static,
    default_rate_stratification_static,
    property_type_stratification_categorical,
    occupancy_stratification_categorical,
    delinquency_stratification_categorical,
    judicial_stratification_dynamic,
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Seller/Trade Dropdowns
# -----------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def list_sellers(request):
    """List all sellers for dropdown."""
    sellers = Seller.objects.all().values('id', 'name')
    # Rename 'name' to 'seller_name' for frontend compatibility
    result = [{'id': s['id'], 'seller_name': s['name']} for s in sellers]
    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_trades_by_seller(request, seller_id: int):
    """List trades for a seller (exclude boarded trades)."""
    trades = (
        Trade.objects
        .filter(seller_id=seller_id)
        .exclude(status=Trade.Status.BOARD)
        .values('id', 'trade_name')
    )
    return Response(list(trades))


@api_view(['GET'])
@permission_classes([AllowAny])
def list_active_deals(request):
    """Return all active deals (seller + trade) for the pipeline dropdown.

    Active = trade status is NOT PASS or BOARD.
    """
    active_trades = (
        Trade.objects
        .exclude(status__in=[Trade.Status.PASS, Trade.Status.BOARD])
        .select_related('seller')
        .order_by('seller__name', 'trade_name')
    )

    payload = []
    for t in active_trades:
        if not t.seller:
            continue
        payload.append(
            {
                'seller_id': t.seller_id,
                'seller_name': t.seller.name,
                'trade_id': t.id,
                'trade_name': t.trade_name,
                'status': t.status,
            }
        )

    return Response(payload)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_trades_with_active_assets(request):
    """Return BOARDED trades that have at least one asset with ACTIVE status.
    
    Filters:
    - Trade status must be BOARD (boarded/closed deals)
    - AssetDetails.asset_status == 'ACTIVE' (not LIQUIDATED)
    
    This shows only boarded trades with active assets in the portfolio.
    """
    from core.models.model_co_assetIdHub import AssetDetails
    
    # Get BOARDED trades that have assets with ACTIVE status
    trades_with_active = (
        Trade.objects
        .filter(
            status=Trade.Status.BOARD,
            asset_details__asset_status=AssetDetails.AssetStatus.ACTIVE
        )
        .select_related('seller')
        .distinct()
        .order_by('seller__name', 'trade_name')
    )
    
    payload = []
    for t in trades_with_active:
        if not t.seller:
            continue
        
        # Count active assets for this trade
        active_count = AssetDetails.objects.filter(
            trade=t,
            asset_status=AssetDetails.AssetStatus.ACTIVE
        ).count()
        
        payload.append({
            'seller_id': t.seller_id,
            'seller_name': t.seller.name,
            'trade_id': t.id,
            'trade_name': t.trade_name,
            'status': t.status,
            'active_asset_count': active_count,
        })
    
    return Response(payload)


# -----------------------------------------------------------------------------
# Pool Summary
# -----------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def get_pool_summary(request, seller_id: int, trade_id: int):
    """Get aggregate pool summary for dashboard widgets."""
    qs = annotate_seller_valuations(
        AcqAsset.objects.filter(
            seller_id=seller_id,
            trade_id=trade_id
        )
    ).exclude(acq_status=AcqAsset.AcquisitionStatus.DROP)

    # Use Decimal defaults so we don't mix DecimalField with integer literal 0
    zero_money = Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))

    agg = qs.aggregate(
        # NOTE: SellerRawData primary key is asset_hub, not a plain id column
        assets=Count('asset_hub'),
        # Field names aligned with frontend expectations
        current_balance=Coalesce(Sum('loan__current_balance'), zero_money),
        total_debt=Coalesce(Sum('loan__total_debt'), zero_money),
        seller_asis_value=Coalesce(Sum('seller_asis_value'), zero_money),
    )

    # Derive simple LTV-style percents for widgets (safe even if zeros)
    upb = agg.get('current_balance') or Decimal('0')
    td = agg.get('total_debt') or Decimal('0')
    asis = agg.get('seller_asis_value') or Decimal('0')
    if asis:
        agg['upb_ltv_percent'] = (upb / asis) * Decimal('100')
        agg['td_ltv_percent'] = (td / asis) * Decimal('100')
    else:
        agg['upb_ltv_percent'] = 0
        agg['td_ltv_percent'] = 0

    return Response(agg)


# -----------------------------------------------------------------------------
# Valuation Completion Summary
# -----------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def get_valuation_completion_summary(request, seller_id: int, trade_id: int):
    """Get valuation completion counts for dashboard."""
    base_qs = annotate_seller_valuations(
        AcqAsset.objects.filter(
            seller_id=seller_id,
            trade_id=trade_id
        )
    ).exclude(acq_status=AcqAsset.AcquisitionStatus.DROP)
    
    total = base_qs.count()
    
    # Count assets with seller values
    seller_count = base_qs.filter(
        Q(seller_asis_value__isnull=False) | Q(seller_arv_value__isnull=False)
    ).count()
    
    # Count assets with internal UW valuations
    internal_uw_count = base_qs.filter(
        Exists(
            Valuation.objects.filter(
                asset_hub_id=OuterRef('asset_hub_id'),
                source='internalInitialUW'
            ).exclude(asis_value__isnull=True, arv_value__isnull=True)
        )
    ).count()
    
    # Count assets with broker valuations
    broker_count = base_qs.filter(
        Exists(
            Valuation.objects.filter(
                asset_hub_id=OuterRef('asset_hub_id'),
                source='broker'
            ).exclude(asis_value__isnull=True, arv_value__isnull=True)
        )
    ).count()
    
    # Count graded assets
    graded_count = base_qs.filter(
        Exists(
            Valuation.objects.filter(
                asset_hub_id=OuterRef('asset_hub_id'),
                grade__isnull=False
            )
        )
    ).count()
    
    return Response({
        'total': total,
        'seller_count': seller_count,
        'internal_uw_count': internal_uw_count,
        'broker_count': broker_count,
        'bpo_count': 0,  # Not implemented yet
        'reconciled_count': internal_uw_count,  # Simplified
        'graded_count': graded_count,
    })


# -----------------------------------------------------------------------------
# Collateral/Title Completion (stubs)
# -----------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def get_collateral_completion_summary(request, seller_id: int, trade_id: int):
    """Stub for collateral completion."""
    return Response({'total': 0, 'complete': 0})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_title_completion_summary(request, seller_id: int, trade_id: int):
    """Stub for title completion."""
    return Response({'total': 0, 'complete': 0})


# -----------------------------------------------------------------------------
# State Summary Endpoints
# -----------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def get_states_for_selection(request, seller_id: int, trade_id: int):
    """Get list of states in the portfolio."""
    states = AcqAsset.objects.filter(
        seller_id=seller_id,
        trade_id=trade_id
    ).exclude(
        acq_status=AcqAsset.AcquisitionStatus.DROP
    ).values_list('property__state', flat=True).distinct()
    return Response(list(states))


@api_view(['GET'])
@permission_classes([AllowAny])
def get_state_count_for_selection(request, seller_id: int, trade_id: int):
    """Get count of unique states."""
    count = AcqAsset.objects.filter(
        seller_id=seller_id,
        trade_id=trade_id
    ).exclude(
        acq_status=AcqAsset.AcquisitionStatus.DROP
    ).values('property__state').distinct().count()
    return Response({'count': count})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_count_by_state(request, seller_id: int, trade_id: int):
    """Get asset count by state."""
    data = AcqAsset.objects.filter(
        seller_id=seller_id,
        trade_id=trade_id
    ).exclude(
        acq_status=AcqAsset.AcquisitionStatus.DROP
    ).values('property__state').annotate(count=Count('asset_hub')).order_by('-count')
    return Response(list(data))


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sum_current_balance_by_state(request, seller_id: int, trade_id: int):
    """Get sum of current balance by state."""
    data = AcqAsset.objects.filter(
        seller_id=seller_id,
        trade_id=trade_id
    ).exclude(
        acq_status=AcqAsset.AcquisitionStatus.DROP
    ).values('property__state').annotate(sum_current_balance=Sum('loan__current_balance')).order_by('-sum_current_balance')
    return Response(list(data))


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sum_total_debt_by_state(request, seller_id: int, trade_id: int):
    """Get sum of total debt by state."""
    data = AcqAsset.objects.filter(
        seller_id=seller_id,
        trade_id=trade_id
    ).exclude(
        acq_status=AcqAsset.AcquisitionStatus.DROP
    ).values('property__state').annotate(sum_total_debt=Sum('loan__total_debt')).order_by('-sum_total_debt')
    return Response(list(data))


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sum_seller_asis_value_by_state(request, seller_id: int, trade_id: int):
    """Get sum of seller as-is value by state."""
    data = annotate_seller_valuations(
        AcqAsset.objects.filter(
            seller_id=seller_id,
            trade_id=trade_id
        )
    ).exclude(
        acq_status=AcqAsset.AcquisitionStatus.DROP
    ).values('property__state').annotate(sum_seller_asis_value=Sum('seller_asis_value')).order_by('-sum_seller_asis_value')
    return Response(list(data))


# -----------------------------------------------------------------------------
# Stratification Endpoints (simplified)
# -----------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def get_current_balance_stratification(request, seller_id: int, trade_id: int):
    """Current balance stratification bands for current_balance field."""
    data = current_balance_stratification_dynamic(seller_id, trade_id)
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_total_debt_stratification(request, seller_id: int, trade_id: int):
    """Total debt stratification bands for total_debt field."""
    data = total_debt_stratification_dynamic(seller_id, trade_id)
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_seller_asis_value_stratification(request, seller_id: int, trade_id: int):
    """Seller as-is value stratification bands for seller_asis_value field."""
    data = seller_asis_value_stratification_dynamic(seller_id, trade_id)
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_wac_stratification(request, seller_id: int, trade_id: int):
    """Coupon (interest_rate) WAC stratification bands."""
    data = wac_stratification_static(seller_id, trade_id)
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_default_rate_stratification(request, seller_id: int, trade_id: int):
    """Default rate stratification bands."""
    data = default_rate_stratification_static(seller_id, trade_id)
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_judicial_stratification(request, seller_id: int, trade_id: int):
    """Judicial vs Non-Judicial stratification (wrapped in bands key for Vue)."""
    bands = judicial_stratification_dynamic(seller_id, trade_id)
    return Response({"bands": bands})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_property_type_stratification(request, seller_id: int, trade_id: int):
    """Property type stratification bands (categorical)."""
    data = property_type_stratification_categorical(seller_id, trade_id)
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_occupancy_stratification(request, seller_id: int, trade_id: int):
    """Occupancy stratification bands (categorical)."""
    data = occupancy_stratification_categorical(seller_id, trade_id)
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_delinquency_stratification(request, seller_id: int, trade_id: int):
    """Delinquency stratification bands (categorical by days delinquent)."""
    data = delinquency_stratification_categorical(seller_id, trade_id)
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_ltv_scatter_data_view(request, seller_id: int, trade_id: int):
    """LTV scatter data."""
    return Response([])
