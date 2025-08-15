from django.http import JsonResponse
from ..models.seller import Seller, Trade, SellerRawData
from django.db.models import Q

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

    # Build a strict query that matches the exact seller+trade combination only.
    # Using Q objects keeps the expression explicit and readable.
    query = Q(seller_id=seller_id) & Q(trade_id=trade_id)

    # Retrieve matching entries. Keep the query efficient with values() to return
    # simple dictionaries consumable by the frontend grid without custom encoders.
    entries_qs = (
        SellerRawData.objects
        .filter(query)
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
