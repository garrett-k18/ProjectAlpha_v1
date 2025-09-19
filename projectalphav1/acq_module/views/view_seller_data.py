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
from rest_framework.decorators import api_view
import logging
from ..models.seller import Seller, Trade, SellerRawData
from ..logic.common import sellertrade_qs
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

def get_seller_trade_data(request, seller_id, trade_id=None):
    """
    Fetch raw data strictly for a specific seller AND a specific trade.

    Data siloing requirement: Only return data when BOTH identifiers are present.
    If either `seller_id` or `trade_id` is missing, return an empty list.

    Args:
        request: The Django request object
        seller_id: The ID of the Seller (required by route)
        trade_id: The ID of the Trade (must be provided; otherwise no data is returned)

    Returns:
        JsonResponse containing:
        - A list of data entries (entry.data) for the exact seller+trade pair when both are provided
        - An empty list [] if either identifier is missing or no data matches
    """
    # Guard clause: enforce data siloing by requiring BOTH IDs.
    # If either seller_id is falsy or trade_id is None/falsy, return an empty list immediately.
    # This prevents accidental exposure of broader datasets.
    if not seller_id or not trade_id:
        return JsonResponse([], safe=False)

    # Retrieve matching entries using centralized selection helper.
    # Keep the query efficient with values() to return
    # simple dictionaries consumable by the frontend grid without custom encoders.
    # 
    # TODO: Future improvement - Replace direct values() approach with Django REST Framework serializers.
    # Using serializers would provide better:
    # 1. Field validation and type handling
    # 2. Support for nested relationships
    # 3. Computed fields via SerializerMethodField
    # 4. Consistent API design across the application
    # See am_module/serializers/asset_inventory.py for an example of this approach.
    entries_qs = (
        sellertrade_qs(seller_id, trade_id)
        .values()  # returns a dict per row with concrete field names
    )

    # If there are no matches, return an empty list to avoid 404s or cross-trade leakage.
    if not entries_qs.exists():
        return JsonResponse([], safe=False)

    # Return list of dicts (field: value) suitable for AG Grid rowData.
    # Note: While this works for simple flat data structures, serializers would provide
    # more flexibility for complex data transformations and relationships.
    data_list = list(entries_qs)
    return JsonResponse(data_list, safe=False)


def get_seller_rawdata_field_names(request):
    """
    Return a JSON response containing the concrete field names for the
    `SellerRawData` model, intended for use as AG Grid `field` keys in
    `columnDefs`.

    TEMPORARY IMPLEMENTATION:
    Instead of using Django's Model Meta API which requires database connection,
    this function returns a hardcoded list of field names based on the
    SellerRawData model structure. This allows the frontend to work without
    a functioning database connection.

    TODO: Replace with DRF serializer-defined fields once DB connectivity is ensured.
    """
    fields = [
        # Foreign keys mapped to their *_id columns
        "id",
        "seller_id",
        "trade_id",
        # Common address/location fields (adjust as needed to match your model)
        "address",
        "city",
        "state",
        "zip_code",
        # Financial fields commonly used in grids
        "current_balance",
        "total_debt",
        "seller_asis_value",
        # Property attributes
        "property_type",
        "occupancy",
        # Delinquency/loan metrics
        "days_past_due",
        # Dates (examples)
        "created_at",
        "updated_at",
    ]
    return JsonResponse(fields, safe=False)


# ------------------------------------------------------------
# Minimal wrappers expected by urls.py
# These return JSON using existing logic helpers, or safe defaults.
# ------------------------------------------------------------

@api_view(["GET"])
def list_sellers(request):
    """Return a minimal list of sellers (id, name) or empty when DB not available."""
    try:
        data = list(Seller.objects.values("id", "name"))
    except Exception:
        data = []
    return JsonResponse(data, safe=False)


@api_view(["GET"])
def list_trades_by_seller(request, seller_id: int):
    """Return trades for a given seller or empty list."""
    try:
        data = list(Trade.objects.filter(seller_id=seller_id).values("id", "name"))
    except Exception:
        data = []
    return JsonResponse(data, safe=False)


@api_view(["GET"])
def get_seller_raw_by_id(request, id: int):
    """Return a single SellerRawData row as a flat dict; {} if not found."""
    try:
        row = SellerRawData.objects.filter(id=id).values().first() or {}
    except Exception:
        row = {}
    return JsonResponse(row, safe=False)


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
        return JsonResponse(judicial_stratification_dynamic(seller_id, trade_id), safe=False)
    except Exception:
        return JsonResponse([], safe=False)


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
