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
