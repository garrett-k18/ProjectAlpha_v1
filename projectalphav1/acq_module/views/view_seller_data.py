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
from ..models.seller import Seller, Trade, SellerRawData
from ..logic.common import sellertrade_qs
from ..logic.summarystats import (
    states_for_selection,
    state_count_for_selection,
    count_by_state,
    sum_current_balance_by_state,
    sum_total_debt_by_state,
    sum_seller_asis_value_by_state,
)

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
    entries_qs = (
        sellertrade_qs(seller_id, trade_id)
        .values()  # returns a dict per row with concrete field names
    )

    # If there are no matches, return an empty list to avoid 404s or cross-trade leakage.
    if not entries_qs.exists():
        return JsonResponse([], safe=False)

    # Return list of dicts (field: value) suitable for AG Grid rowData.
    data_list = list(entries_qs)
    return JsonResponse(data_list, safe=False)


def get_seller_rawdata_field_names(request):
    """
    Return a JSON response containing the concrete field names for the
    `SellerRawData` model, intended for use as AG Grid `field` keys in
    `columnDefs`.
    
    TEMPORARY IMPLEMENTATION:
    Instead of using Django's Model Meta API which requires database connection,
    this function now returns a hardcoded list of field names based on the
    SellerRawData model structure. This allows the frontend to work without
    a functioning database connection.
    
    Original implementation details:
    - Uses Django's Model Meta API to enumerate fields.
    - Excludes reverse relations and many-to-many fields (not concrete columns).
    - Maps ForeignKey fields to their underlying DB column names via `attname`
      (e.g., `seller` -> `seller_id`, `trade` -> `trade_id`) so they align
      with ORM `.values()` keys and remain unambiguous in the grid.
    """
    # Hardcoded field names based on the SellerRawData model
    # These are the most common fields that would be returned by the model introspection
    field_names = [
        # Primary key and foreign keys
        'id',
        'street_address',
        'city',
        'state',
        'zip',
        'current_balance',
        'deferred_balance',
        'interest_rate',
        'next_due_date',
        'last_paid_date',
        'first_pay_date',
        'origination_date',
        'original_balance',
        'original_term',
        'original_rate',
        'original_maturity_date',
        'default_rate',
        'months_dlq',
        'current_maturity_date',
        'current_term',
        'accrued_note_interest',
        'accrued_default_interest',
        'escrow_balance',
        'fc_flag',
        'fc_first_legal_date',
        'fc_referred_date',
        'fc_judgement_date',
        'fc_scheduled_sale_date',
        'fc_sale_date',
        'fc_starting',
        'bk_flag',
        'bk_chapter',
        'mod_flag',
        'mod_date',
        'mod_maturity_date',
        'mod_term',
        'mod_rate',
        'mod_initial_balance',
    ]
    # Fields to exclude: "id", "created_at", "updated_at", "data", "is_active", "is_verified"
    return JsonResponse({"fields": field_names})


def list_sellers(request):
    """
    List all Sellers with minimal fields for dropdown population.

    Returns:
        JsonResponse: list of { id, name }
    """
    sellers = Seller.objects.all().order_by('name').values('id', 'name')
    return JsonResponse(list(sellers), safe=False)


def list_trades_by_seller(request, seller_id: int):
    """
    List Trades belonging to a specific Seller for dependent dropdowns.

    Args:
        seller_id (int): The Seller ID to filter trades by.

    Returns:
        JsonResponse: list of { id, trade_name }
    """
    trades = (
        Trade.objects
        .filter(seller_id=seller_id)
        .order_by('trade_name')
        .values('id', 'trade_name')
    )
    return JsonResponse(list(trades), safe=False)


def get_seller_raw_by_id(request, id: int):
    """
    Fetch a single SellerRawData row by its primary key `id` and return a flat dict
    of its concrete fields suitable for direct frontend consumption.

    Args:
        request: Django request object (unused)
        id (int): Primary key of SellerRawData

    Returns:
        JsonResponse: {} when not found, or a dict of field: value when found
    """
    # Use values() to avoid custom encoders; returns a plain dict per row
    entry = (
        SellerRawData.objects
        .filter(id=id)
        .values()
        .first()
    )
    # Return empty object if not found for predictable client handling
    return JsonResponse(entry or {}, safe=False)


# ---------------------------------------------------------------------------
# State Summary Endpoints (per-seller, per-trade)
# ---------------------------------------------------------------------------

def get_states_for_selection(request, seller_id: int, trade_id: int):
    """Return a list of distinct states for the given seller+trade selection.

    Uses: logic.summarystats.states_for_selection()

    Returns:
        JsonResponse (list[str]): e.g., ["AZ", "CA", "TX"]
    """
    # Enforce the data siloing pattern used elsewhere in this module
    if not seller_id or not trade_id:
        return JsonResponse([], safe=False)

    result = states_for_selection(seller_id, trade_id)
    return JsonResponse(result, safe=False)


def get_state_count_for_selection(request, seller_id: int, trade_id: int):
    """Return the count of distinct states for the seller+trade selection.

    Uses: logic.summarystats.state_count_for_selection()

    Returns:
        JsonResponse (object): { "count": <int> }
    """
    if not seller_id or not trade_id:
        return JsonResponse({"count": 0})

    count = state_count_for_selection(seller_id, trade_id)
    return JsonResponse({"count": count})


def get_count_by_state(request, seller_id: int, trade_id: int):
    """Return counts per state for the seller+trade selection.

    Uses: logic.summarystats.count_by_state()

    Returns:
        JsonResponse (list[object]): [ { "state": "CA", "count": 42 }, ... ]
    """
    if not seller_id or not trade_id:
        return JsonResponse([], safe=False)

    rows = count_by_state(seller_id, trade_id)
    return JsonResponse(list(rows), safe=False)


def get_sum_current_balance_by_state(request, seller_id: int, trade_id: int):
    """Return sum(current_balance) per state for the seller+trade selection.

    Uses: logic.summarystats.sum_current_balance_by_state()

    Returns:
        JsonResponse (list[object]): [ { "state": "CA", "sum_current_balance": "123.45" }, ... ]
    """
    if not seller_id or not trade_id:
        return JsonResponse([], safe=False)

    rows = sum_current_balance_by_state(seller_id, trade_id)
    return JsonResponse(list(rows), safe=False)


def get_sum_total_debt_by_state(request, seller_id: int, trade_id: int):
    """Return sum(total_debt) per state for the seller+trade selection.

    Uses: logic.summarystats.sum_total_debt_by_state()

    Returns:
        JsonResponse (list[object]): [ { "state": "CA", "sum_total_debt": "123.45" }, ... ]
    """
    if not seller_id or not trade_id:
        return JsonResponse([], safe=False)

    rows = sum_total_debt_by_state(seller_id, trade_id)
    return JsonResponse(list(rows), safe=False)


def get_sum_seller_asis_value_by_state(request, seller_id: int, trade_id: int):
    """Return sum(seller_asis_value) per state for the seller+trade selection.

    Uses: logic.summarystats.sum_seller_asis_value_by_state()

    Returns:
        JsonResponse (list[object]): [ { "state": "CA", "sum_seller_asis_value": "123.45" }, ... ]
    """
    if not seller_id or not trade_id:
        return JsonResponse([], safe=False)

    rows = sum_seller_asis_value_by_state(seller_id, trade_id)
    return JsonResponse(list(rows), safe=False)
