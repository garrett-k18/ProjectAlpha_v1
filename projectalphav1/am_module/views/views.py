"""
WHAT: API views for AM module
WHY: Provide REST endpoints for asset management data
HOW: Django REST Framework views and viewsets
WHERE: Registered in am_module/urls.py
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Q
from datetime import datetime

from core.models import AssetIdHub, LLCashFlowSeries
from am_module.serializers.serial_am_cashFlows import CashFlowSeriesSerializer
from etl.models import SBDailyLoanData


@api_view(['GET'])
def cash_flow_series_view(request, asset_id):
    """
    WHAT: API endpoint to retrieve cash flow series for an asset
    WHY: Frontend needs period-by-period cash flow data for time-series grid
    HOW: Fetch all LLCashFlowSeries records for asset, serialize with purchase date
    
    Args:
        request: HTTP request
        asset_id: AssetIdHub primary key
        
    Returns:
        Response: JSON with purchase_date and periods array
        
    Example Response:
        {
            "purchase_date": "2024-01-15",
            "periods": [
                {
                    "period_number": 0,
                    "period_date": "2024-01-15",
                    "purchase_price": 150000.00,
                    "total_income": 0.00,
                    "total_expenses": 155000.00,
                    "net_cash_flow": -155000.00,
                    ...
                },
                {
                    "period_number": 1,
                    "period_date": "2024-02-15",
                    "income_interest": 1250.00,
                    "servicing_expenses": 350.00,
                    ...
                }
            ]
        }
    """
    # WHAT: Get asset hub with related BlendedOutcomeModel
    # WHY: Need purchase_date from BlendedOutcomeModel
    asset_hub = get_object_or_404(
        AssetIdHub.objects.select_related('blended_outcome_model'),
        pk=asset_id
    )
    print(f"DEBUG: Asset hub found: {asset_hub.id}")
    
    # WHAT: Fetch all cash flow periods for this asset, ordered by period number
    # WHY: Frontend displays periods chronologically
    periods = LLCashFlowSeries.objects.filter(
        asset_hub=asset_hub
    ).order_by('period_number')
    print(f"DEBUG: Periods QuerySet: {periods}")
    print(f"DEBUG: Periods count: {periods.count()}")
    
    # WHAT: Check if asset has purchase date
    # WHY: Purchase date is required to calculate period dates
    if not hasattr(asset_hub, 'blended_outcome_model') or not asset_hub.blended_outcome_model.purchase_date:
        print("DEBUG: No purchase date found")
        return Response(
            {
                'detail': 'Asset does not have a purchase date in BlendedOutcomeModel',
                'purchase_date': None,
                'periods': []
            },
            status=status.HTTP_200_OK
        )
    
    print(f"DEBUG: Purchase date: {asset_hub.blended_outcome_model.purchase_date}")
    
    # WHAT: Manually build response with serialized periods
    # WHY: Simpler than custom serializer, direct control over output
    from am_module.serializers.serial_am_cashFlows import CashFlowPeriodSerializer
    
    serialized_periods = CashFlowPeriodSerializer(periods, many=True).data
    print(f"DEBUG: Serialized periods count: {len(serialized_periods)}")
    
    response_data = {
        'purchase_date': asset_hub.blended_outcome_model.purchase_date,
        'periods': serialized_periods
    }
    
    print(f"DEBUG: Response data keys: {response_data.keys()}")
    print(f"DEBUG: Response periods length: {len(response_data['periods'])}")
    
    return Response(response_data, status=status.HTTP_200_OK)


def _raw_permission_classes():
    return [AllowAny] if getattr(settings, 'DEBUG', False) else [IsAuthenticated]


def _date_variants_and_iso(date_str: str | None):
    """Return (variants, iso) for a raw date string.

    The SBDailyLoanData.date field is stored as a raw string from vendor CSVs,
    and can be either YYYY-MM-DD or M/D/YYYY (or MM/DD/YYYY).
    """
    if not date_str:
        return [], None

    s = str(date_str).strip()
    if not s:
        return [], None

    # If already ISO, generate slash variants.
    if '-' in s and len(s) >= 10:
        try:
            dt = datetime.strptime(s[:10], '%Y-%m-%d')
            iso = dt.strftime('%Y-%m-%d')
            mdyyyy = f"{dt.month}/{dt.day}/{dt.year}"
            mmddyyyy = dt.strftime('%m/%d/%Y')
            return [s, iso, mdyyyy, mmddyyyy], iso
        except Exception:
            return [s], None

    # Slash variants.
    if '/' in s:
        parts = [p.strip() for p in s.split('/') if p.strip()]
        if len(parts) == 3:
            try:
                m = int(parts[0])
                d = int(parts[1])
                y = int(parts[2])
                if y < 100:
                    y = 2000 + y
                iso = f"{y:04d}-{m:02d}-{d:02d}"
                mdyyyy = f"{m}/{d}/{y}"
                mmddyyyy = f"{m:02d}/{d:02d}/{y:04d}"
                return [s, iso, mdyyyy, mmddyyyy], iso
            except Exception:
                return [s], None

    return [s], None


def _date_q(date_str: str | None):
    variants, iso = _date_variants_and_iso(date_str)
    q = Q()
    for v in variants:
        if v:
            q |= Q(date=v)
    return q, iso


@api_view(['GET'])
@permission_classes(_raw_permission_classes())
def sb_daily_loan_data_raw(request):
    requested_date = request.query_params.get('date')

    try:
        limit = int(request.query_params.get('limit', '500'))
    except (TypeError, ValueError):
        limit = 500

    try:
        offset = int(request.query_params.get('offset', '0'))
    except (TypeError, ValueError):
        offset = 0

    limit = max(1, min(limit, 5000))
    offset = max(0, offset)

    qs = SBDailyLoanData.objects.all()

    # Default to the most recently ingested date if none specified.
    applied_date = None
    applied_date_iso = None
    if requested_date:
        applied_date = requested_date
        date_q, applied_date_iso = _date_q(requested_date)
        qs = qs.filter(date_q)
    else:
        latest_date = (
            SBDailyLoanData.objects
            .exclude(date__isnull=True)
            .exclude(date='')
            .order_by('-id')
            .values_list('date', flat=True)
            .first()
        )
        if latest_date:
            applied_date = str(latest_date)
            date_q, applied_date_iso = _date_q(applied_date)
            if date_q:
                qs = qs.filter(date_q)

    qs = qs.order_by('-id')

    total = qs.count()
    field_names = [f.name for f in SBDailyLoanData._meta.fields]
    rows = list(qs.values(*field_names)[offset:offset + limit])

    return Response(
        {
            'count': total,
            'applied_date': applied_date,
            'applied_date_iso': applied_date_iso,
            'results': rows,
        },
        status=status.HTTP_200_OK,
    )
