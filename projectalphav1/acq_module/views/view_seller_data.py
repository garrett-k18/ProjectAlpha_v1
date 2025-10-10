"""
Views for SellerRawData API endpoints.

This module contains several endpoints for fetching SellerRawData rows,
including:

- `get_seller_trade_data`: Fetch raw data specifically for a specific seller
  AND a specific trade. Data siloing requirement: Only return data when BOTH
  identifiers are present.

- `list_sellers`: Fetch all Seller objects.

- `list_trades_by_seller`: Fetch all Trade objects belonging to a specific Seller.

- `get_seller_raw_by_id`: Fetch a single SellerRawData row by its primary key
  `id` and return a flat dict of its concrete fields suitable for direct frontend
  consumption.

- `get_seller_rawdata_field_names`: Fetch concrete field names for SellerRawData
  (for AG Grid columnDefs).

- `list_photos_by_raw_id`: Fetch all photo types (public, document, broker)
  associated with a given SellerRawData id.
"""


from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import logging
from ..models.seller import Seller, Trade, SellerRawData
from ..logic.common import sellertrade_qs
from ..serializers.acq_datatable_serializer import (
    SellerRawDataRowSerializer,
    SellerOptionSerializer,
    TradeOptionSerializer,
    SellerRawDataDetailSerializer,
    SellerRawDataFieldsSerializer,
)
from ..services.seller_data import build_queryset
from ..logic.summarystats import (
    states_for_selection,
    state_count_for_selection,
    count_by_state,
    sum_current_balance_by_state,
    sum_total_debt_by_state,
    sum_seller_asis_value_by_state,
    count_upb_td_val_summary,
)
from ..logic.strats import (
    # Dynamic stratification helpers (NTILE with fallback)
    current_balance_stratification_dynamic,
    total_debt_stratification_dynamic,
    seller_asis_value_stratification_dynamic,
    judicial_stratification_dynamic,
    wac_stratification_static,
    property_type_stratification_categorical,
    occupancy_stratification_categorical,
    delinquency_stratification_categorical,
)
from ..logic.ll_metrics import get_ltv_scatter_data

# Module-level logger
logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    """Pagination class matching AM module for consistency."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


@api_view(["GET"])
def get_seller_trade_data(request, seller_id, trade_id=None):
    """
    Fetch raw data strictly for a specific seller AND a specific trade.
    Now uses DRF serializers following the AM module pattern.

    Data siloing requirement: Only return data when BOTH identifiers are present.
    If either `seller_id` or `trade_id` is missing, return an empty list.

    Args:
        request: The Django request object
        seller_id: The ID of the Seller (required by route)
        trade_id: The ID of the Trade (must be provided; otherwise no data is returned)

    Returns:
        Response containing:
        - Paginated list of serialized SellerRawData entries for the seller+trade pair
        - Empty results if either identifier is missing or no data matches
    """
    # Guard clause: enforce data siloing by requiring BOTH IDs
    if not seller_id or not trade_id:
        return Response({'results': [], 'count': 0, 'next': None, 'previous': None})

    try:
        # Get view parameter from query string (default to 'snapshot')
        # Used to filter by drop status: 'drops' shows dropped assets, others show active
        view = request.GET.get('view', 'snapshot')
        
        # Build queryset using service layer with NO server-side filters/sorting.
        # All filtering will be handled client-side by AG Grid.
        qs = build_queryset(
            seller_id=seller_id,
            trade_id=trade_id,
            q=None,
            filters=None,
            ordering=None,
            view=view,
        )

        # Apply pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
    except Exception as e:
        logger.error(f"Query build/pagination failed for seller_id={seller_id}, trade_id={trade_id}: {e}")
        # Attempt a minimal fallback using raw values() without service layer
        try:
            raw_qs = SellerRawData.objects.filter(seller_id=seller_id, trade_id=trade_id).values()
            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(list(raw_qs), request)
            return paginator.get_paginated_response(page)
        except Exception as e2:
            logger.error(f"Fallback raw values pagination failed: {e2}")
            return Response({'results': [], 'count': 0, 'next': None, 'previous': None})
    
    # Serialize each row individually to avoid losing method fields for all rows
    # if a single row raises during serialization (e.g., bad data in one record).
    results = []
    errors = 0
    for obj in page:
        try:
            data = SellerRawDataRowSerializer(obj).data
        except Exception as e:
            errors += 1
            logger.error(
                f"Row serialization failed for SellerRawData id={getattr(obj, 'id', None)}: {e}"
            )
            # Minimal fallback for this row only; omit method fields but keep core data
            try:
                data = model_to_dict(obj)
            except Exception:
                data = {}
        results.append(data)

    # Return the paginated response with our per-row serialized results
    # This preserves count/next/previous metadata.
    return paginator.get_paginated_response(results)


@api_view(["GET"])
def get_seller_rawdata_field_names(request):
    """
    Return field names from SellerRawDataRowSerializer for AG Grid columnDefs.
    Now uses DRF serializer fields for consistency and accuracy.
    """
    try:
        fields = SellerRawDataFieldsSerializer.get_fields_list()
        # Contract: Frontend expects { "fields": [...] }
        return Response({"fields": fields})
    except Exception as e:
        # Log and return a safe minimal default to keep the UI working
        logger.error(f"Failed to build SellerRawData fields list: {e}")
        # IMPORTANT: Do not include seller_id or trade_id in fallback (not part of grid contract)
        fallback = [
            "id",
            # Address parts (the UI will condense these into a single Address column)
            "street_address", "city", "state", "zip",
            # Core fields commonly used in snapshots
            "asset_status", "property_type", "occupancy",
            "current_balance", "total_debt",
            # Seller valuation
            "seller_asis_value", "seller_arv_value", "seller_value_date",
        ]
        return Response({"fields": fallback})


# ------------------------------------------------------------
# Minimal wrappers expected by urls.py
# These return JSON using existing logic helpers, or safe defaults.
# ------------------------------------------------------------

@api_view(["GET"])
def list_sellers(request):
    """Return a minimal list of sellers (id, name) using DRF serializers."""
    try:
        sellers = Seller.objects.all().order_by('name')
        serializer = SellerOptionSerializer(sellers, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Failed to fetch sellers: {e}")
        return Response([])


@api_view(["GET"])
def list_trades_by_seller(request, seller_id: int):
    """Return trades for a given seller using DRF serializers.

    Important: The Trade model uses the field name 'trade_name'. The frontend
    expects each trade option to have keys { id, trade_name }.
    """
    try:
        if not seller_id:
            return Response([])
        
        trades = Trade.objects.filter(seller_id=seller_id).order_by('-created_at')
        serializer = TradeOptionSerializer(trades, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Failed to fetch trades for seller {seller_id}: {e}")
        return Response([])


@api_view(["GET"])
def get_seller_raw_by_id(request, id: int):
    """Return a single SellerRawData row using DRF serializer; {} if not found."""
    try:
        raw_data = SellerRawData.objects.select_related('seller', 'trade', 'asset_hub').get(id=id)
        serializer = SellerRawDataDetailSerializer(raw_data)
        return Response(serializer.data)
    except SellerRawData.DoesNotExist:
        return Response({}, status=404)
    except Exception as e:
        logger.error(f"Failed to fetch SellerRawData {id}: {e}")
        return Response({}, status=500)


@api_view(["GET"])  # State selection options
def get_states_for_selection(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(states_for_selection(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse([], safe=False)


@api_view(["GET"])  # State counts
def get_state_count_for_selection(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(state_count_for_selection(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse({}, safe=False)


@api_view(["GET"])  # Count by state
def get_count_by_state(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(count_by_state(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse({}, safe=False)


@api_view(["GET"])  # Sums by state
def get_sum_current_balance_by_state(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(sum_current_balance_by_state(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse({}, safe=False)


@api_view(["GET"])  # Sums by state
def get_sum_total_debt_by_state(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(sum_total_debt_by_state(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse({}, safe=False)


@api_view(["GET"])  # Sums by state
def get_sum_seller_asis_value_by_state(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(sum_seller_asis_value_by_state(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse({}, safe=False)


@api_view(["GET"])  # Pool summary (UPB/TD/Val)
def get_pool_summary(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(count_upb_td_val_summary(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse({}, safe=False)


@api_view(["GET"])  # Current balance stratification
def get_current_balance_stratification(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(current_balance_stratification_dynamic(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse([], safe=False)


@api_view(["GET"])  # Total debt stratification
def get_total_debt_stratification(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(total_debt_stratification_dynamic(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse([], safe=False)


@api_view(["GET"])  # Seller as-is value strat
def get_seller_asis_value_stratification(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(seller_asis_value_stratification_dynamic(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse([], safe=False)


@api_view(["GET"])  # WAC strat (static)
def get_wac_stratification(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(wac_stratification_static(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse([], safe=False)


@api_view(["GET"])  # Judicial strat
def get_judicial_stratification(request, seller_id: int, trade_id: int):
    try:
        data = judicial_stratification_dynamic(seller_id, trade_id)
        # Frontend expects an object with a 'bands' array
        return JsonResponse({"bands": data}, safe=False)
    except Exception:
        return JsonResponse({"bands": []}, safe=False)


@api_view(["GET"])  # Property type strat
def get_property_type_stratification(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(property_type_stratification_categorical(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse([], safe=False)


@api_view(["GET"])  # Occupancy strat
def get_occupancy_stratification(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(occupancy_stratification_categorical(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse([], safe=False)


@api_view(["GET"])  # Delinquency strat
def get_delinquency_stratification(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(delinquency_stratification_categorical(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse([], safe=False)


@api_view(["GET"])  # LTV scatter
def get_ltv_scatter_data_view(request, seller_id: int, trade_id: int):
    try:
        return JsonResponse(get_ltv_scatter_data(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse([], safe=False)
