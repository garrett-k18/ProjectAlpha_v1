"""
Service: Reporting QuerySet Builder

WHAT: Centralized QuerySet construction with filters, joins, and annotations
WHY: Separate data access logic from views/serializers (single source of truth for queries)
WHERE: Imported by all reporting service files and views
HOW: Build optimized QuerySets with proper select_related, prefetch_related, and filters

FILE NAMING: serv_rep_queryBuilder.py
- serv_ = Services folder
- _rep_ = Reporting module
- queryBuilder = Descriptive name

ARCHITECTURE:
View calls Service → Service calls queryBuilder → Returns optimized QuerySet

Docs reviewed:
- Django QuerySet API: https://docs.djangoproject.com/en/stable/ref/models/querysets/
- QuerySet optimization: https://docs.djangoproject.com/en/stable/topics/db/optimization/
- Django aggregation: https://docs.djangoproject.com/en/stable/topics/db/aggregation/
"""

from typing import Optional, List
from django.db.models import QuerySet, Q, F, Value, CharField
from django.db.models.functions import Coalesce
from acq_module.models.model_acq_seller import SellerRawData, Trade


def build_base_queryset() -> QuerySet[SellerRawData]:
    """
    WHAT: Build base SellerRawData queryset with optimized joins and field annotations
    WHY: Reduce N+1 queries by eagerly loading related data and annotate computed fields
    HOW: Use select_related for ForeignKey joins, annotate for field mapping
    
    RETURNS: Optimized QuerySet ready for filtering
    """
    # WHAT: Select related models to avoid N+1 queries
    # WHY: Trade, Seller, AssetHub, ServicerLoanData are frequently accessed in reporting
    # HOW: Use select_related for ForeignKey, prefetch_related for reverse FKs
    queryset = (
        SellerRawData.objects
        .select_related(
            'trade',                    # WHAT: Trade details (name, status, bid_date)
            'trade__seller',            # WHAT: Seller details (name, POC)
            'asset_hub',                # WHAT: Asset hub for master asset data
            'asset_hub__servicer_data', # WHAT: ServicerLoanData for current servicing info
            'seller',                   # WHAT: Direct seller FK if exists
        )
        .prefetch_related(
            'asset_hub__valuations',    # WHAT: Valuations for AIV/ARV calculations
        )
    )
    
    # ========================================================================
    # 📋 FIELD ANNOTATIONS - MAKE FIELDS FROM RELATED MODELS AVAILABLE
    # ========================================================================
    # WHAT: Annotate fields from related models onto the main queryset
    # WHY: Make fields easily accessible in ALL queries, aggregations, and serializers
    # HOW: Use F() expressions to reference related model fields
    # 
    # IMPORTANT: Fields annotated here are ALWAYS AVAILABLE in every query!
    # This is where you "import" fields from related models.
    # ========================================================================
    
    from django.db.models import F, Value, CharField
    from django.db.models.functions import Concat, Coalesce
    
    queryset = queryset.annotate(
        # ====================================================================
        # ✅ CORE REQUIRED FIELDS - ALWAYS AVAILABLE IN ALL QUERIES
        # ====================================================================
        # WHAT: Essential fields requested for all reporting queries
        # WHY: These fields are used across multiple report types
        # HOW: Annotated once here, available everywhere
        # ====================================================================
        
        # ──────────────────────────────────────────────────────────────────
        # SERVICER ID (from AssetIdHub)
        # ──────────────────────────────────────────────────────────────────
        # WHAT: Servicer loan identifier from AssetIdHub
        # WHY: Primary external identifier used by asset managers
        # SOURCE: asset_hub.servicer_id
        servicer_id=F('asset_hub__servicer_id'),
        
        # ──────────────────────────────────────────────────────────────────
        # ADDRESS FIELDS (from SellerRawData - already on base model)
        # ──────────────────────────────────────────────────────────────────
        # NOTE: These fields are ALREADY on SellerRawData, no annotation needed!
        # - street_address ✅ (directly accessible)
        # - city ✅ (directly accessible)
        # - state ✅ (directly accessible)
        # - zip ✅ (directly accessible)
        # 
        # Just reference them directly in aggregations/serializers:
        # .values('street_address', 'city', 'state')
        # 
        # OPTIONAL: Computed full address field for convenience
        full_address=Concat(
            F('street_address'),
            Value(', '),
            F('city'),
            Value(', '),
            F('state'),
            Value(' '),
            Coalesce(F('zip'), Value('')),
            output_field=CharField()
        ),
        
        # ──────────────────────────────────────────────────────────────────
        # CURRENT BALANCE (from ServicerLoanData)
        # ──────────────────────────────────────────────────────────────────
        # WHAT: Current balance from servicing platform
        # WHY: Most up-to-date balance from servicer (vs. tape balance)
        # SOURCE: asset_hub.servicer_data.current_balance
        servicer_current_balance=F('asset_hub__servicer_data__current_balance'),
        
        # ====================================================================
        # 📊 ADDITIONAL SERVICER FIELDS - Available but not required
        # ====================================================================
        # WHAT: Additional servicer data fields for advanced reporting
        # WHY: Provide comprehensive servicer data access
        # HOW: Add more servicer fields as needed
        # ====================================================================
        
        # WHAT: Interest rate from servicer
        # WHY: Current interest rate from servicing platform
        servicer_interest_rate=F('asset_hub__servicer_data__interest_rate'),
        
        # WHAT: Total debt from servicer (includes fees, advances, escrow)
        # WHY: Complete debt picture from servicing platform
        servicer_total_debt=F('asset_hub__servicer_data__total_debt'),
        
        # WHAT: As of date from servicer data
        # WHY: Know when servicing data was last updated
        servicer_as_of_date=F('asset_hub__servicer_data__as_of_date'),
        
        # WHAT: Next due date from servicer
        # WHY: Track payment schedules
        servicer_next_due_date=F('asset_hub__servicer_data__next_due_date'),
        
        # ====================================================================
        # 🏢 ASSET HUB FIELDS - Master asset data
        # ====================================================================
        # WHAT: Asset master status from AssetIdHub
        # WHY: Lifecycle status (ACTIVE, LIQUIDATED)
        asset_master_status=F('asset_hub__asset_status'),
        
        # ====================================================================
        # 🎯 ADD YOUR OWN FIELDS HERE - Copy patterns above!
        # ====================================================================
        # 
        # PATTERN FOR ASSET HUB FIELDS:
        # your_field_name=F('asset_hub__field_name'),
        #
        # PATTERN FOR SERVICER FIELDS:
        # servicer_your_field=F('asset_hub__servicer_data__field_name'),
        #
        # PATTERN FOR TRADE FIELDS:
        # trade_your_field=F('trade__field_name'),
        #
        # PATTERN FOR SELLER FIELDS:
        # seller_your_field=F('trade__seller__field_name'),
        #
        # EXAMPLES TO ADD:
        # servicer_investor_id=F('asset_hub__servicer_data__investor_id'),
        # servicer_fc_status=F('asset_hub__servicer_data__fc_status'),
        # servicer_bk_status=F('asset_hub__servicer_data__bk_current_status'),
        # servicer_piti=F('asset_hub__servicer_data__piti'),
        # trade_bid_date=F('trade__created_at'),
        # ====================================================================
    )
    
    return queryset


def apply_trade_filter(
    queryset: QuerySet[SellerRawData],
    trade_ids: Optional[List[int]] = None
) -> QuerySet[SellerRawData]:
    """
    WHAT: Filter queryset by trade IDs
    WHY: Users select specific trades in sidebar
    HOW: Use __in lookup for multiple IDs
    
    ARGS:
        queryset: Base queryset to filter
        trade_ids: List of trade IDs to include (None = all trades)
    
    RETURNS: Filtered queryset
    """
    if trade_ids and len(trade_ids) > 0:
        # WHAT: Filter to only selected trades
        # WHY: User selected specific trades in sidebar
        queryset = queryset.filter(trade_id__in=trade_ids)
    
    return queryset


def apply_status_filter(
    queryset: QuerySet[SellerRawData],
    statuses: Optional[List[str]] = None
) -> QuerySet[SellerRawData]:
    """
    WHAT: Filter queryset by trade status
    WHY: Users select specific statuses (DD, AWARDED, PASS, BOARD)
    HOW: Use trade__status__in lookup
    
    ARGS:
        queryset: Base queryset to filter
        statuses: List of status values (None = all statuses)
    
    RETURNS: Filtered queryset
    """
    if statuses and len(statuses) > 0:
        # WHAT: Filter to only trades with selected statuses
        # WHY: User selected specific statuses in sidebar
        queryset = queryset.filter(trade__status__in=statuses)
    
    return queryset


def apply_fund_filter(
    queryset: QuerySet[SellerRawData],
    fund_id: Optional[int] = None
) -> QuerySet[SellerRawData]:
    """
    WHAT: Filter queryset by fund
    WHY: Users want to see data for specific investment fund
    HOW: Filter by fund FK on Trade or AssetHub
    
    ARGS:
        queryset: Base queryset to filter
        fund_id: Fund ID to filter by (None = all funds)
    
    RETURNS: Filtered queryset
    
    TODO: Add fund FK to Trade or AssetHub model when fund structure is finalized
    """
    if fund_id:
        # WHAT: Filter by fund (once fund FK is added to model)
        # WHY: Users want fund-specific reporting
        # TODO: Uncomment once fund FK exists
        # queryset = queryset.filter(trade__fund_id=fund_id)
        pass
    
    return queryset


def apply_entity_filter(
    queryset: QuerySet[SellerRawData],
    entity_id: Optional[int] = None
) -> QuerySet[SellerRawData]:
    """
    WHAT: Filter queryset by legal entity
    WHY: Users need entity-level reporting for accounting/compliance
    HOW: Filter by entity FK on Trade or AssetHub
    
    ARGS:
        queryset: Base queryset to filter
        entity_id: Entity ID to filter by (None = all entities)
    
    RETURNS: Filtered queryset
    
    TODO: Add entity FK to Trade or AssetHub model when entity structure is finalized
    """
    if entity_id:
        # WHAT: Filter by legal entity (once entity FK is added to model)
        # WHY: Users want entity-specific reporting
        # TODO: Uncomment once entity FK exists
        # queryset = queryset.filter(trade__entity_id=entity_id)
        pass
    
    return queryset


def apply_date_range_filter(
    queryset: QuerySet[SellerRawData],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> QuerySet[SellerRawData]:
    """
    WHAT: Filter queryset by date range
    WHY: Users want to see data for specific time periods
    HOW: Filter by trade bid_date or other relevant date fields
    
    ARGS:
        queryset: Base queryset to filter
        start_date: ISO date string (YYYY-MM-DD)
        end_date: ISO date string (YYYY-MM-DD)
    
    RETURNS: Filtered queryset
    """
    # WHAT: Filter by trade bid date range
    # WHY: Most common date filter for reporting
    # TODO: Make date field configurable per report type
    if start_date:
        queryset = queryset.filter(trade__created_at__gte=start_date)
    
    if end_date:
        queryset = queryset.filter(trade__created_at__lte=end_date)
    
    return queryset


def apply_quick_filter(
    queryset: QuerySet[SellerRawData],
    q: Optional[str] = None
) -> QuerySet[SellerRawData]:
    """
    WHAT: Apply quick search filter across multiple fields
    WHY: Users type in search box to find specific assets/trades
    HOW: Use Q objects with OR logic across text fields
    
    ARGS:
        queryset: Base queryset to filter
        q: Search text
    
    RETURNS: Filtered queryset
    """
    if not q or q.strip() == '':
        return queryset
    
    # WHAT: Fields to search (matches acquisitions grid pattern)
    # WHY: Search across common identifying fields
    search_q = Q()
    search_q |= Q(street_address__icontains=q)
    search_q |= Q(city__icontains=q)
    search_q |= Q(state__icontains=q)
    search_q |= Q(trade__trade_name__icontains=q)
    search_q |= Q(trade__seller__name__icontains=q)
    search_q |= Q(sellertape_id__icontains=q)
    
    return queryset.filter(search_q)


def build_reporting_queryset(
    *,
    trade_ids: Optional[List[int]] = None,
    statuses: Optional[List[str]] = None,
    fund_id: Optional[int] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    q: Optional[str] = None,
    ordering: Optional[str] = None,
) -> QuerySet[SellerRawData]:
    """
    WHAT: Build complete reporting queryset with all filters applied
    WHY: Single function to handle all reporting filter combinations
    HOW: Chain all filter functions together
    
    ARGS:
        trade_ids: List of trade IDs to filter by
        statuses: List of trade statuses (DD, AWARDED, PASS, BOARD)
        fund_id: Fund ID to filter by
        entity_id: Entity ID to filter by
        start_date: Start of date range (ISO string)
        end_date: End of date range (ISO string)
        q: Quick search text
        ordering: Comma-separated field names (supports - prefix for desc)
    
    RETURNS: Fully filtered and ordered QuerySet
    
    EXAMPLE:
        # Filter by trades 1,2,3 with status DD or AWARDED
        qs = build_reporting_queryset(
            trade_ids=[1, 2, 3],
            statuses=['DD', 'AWARDED'],
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
    """
    # WHAT: Start with optimized base queryset
    queryset = build_base_queryset()
    
    # WHAT: Apply filters in sequence
    # WHY: Each filter narrows down the dataset
    queryset = apply_trade_filter(queryset, trade_ids)
    queryset = apply_status_filter(queryset, statuses)
    queryset = apply_fund_filter(queryset, fund_id)
    queryset = apply_entity_filter(queryset, entity_id)
    queryset = apply_date_range_filter(queryset, start_date, end_date)
    queryset = apply_quick_filter(queryset, q)
    
    # WHAT: Apply ordering if specified
    # WHY: Users can sort by any column in AG Grid
    if ordering:
        # WHAT: Parse comma-separated ordering fields
        # WHY: Support multi-column ordering (e.g., "trade_name,-total_upb")
        # HOW: Split by comma, strip whitespace, pass to order_by
        order_fields = [f.strip() for f in ordering.split(',') if f.strip()]
        if order_fields:
            queryset = queryset.order_by(*order_fields)
    
    return queryset


def parse_filter_params(request) -> dict:
    """
    WHAT: Parse filter parameters from request query params
    WHY: Centralize parameter parsing logic
    HOW: Extract and convert query params to proper types
    
    ARGS:
        request: Django request object
    
    RETURNS: Dict with parsed filter parameters
    
    EXAMPLE:
        # Request: ?trade_ids=1,2,3&statuses=DD,AWARDED
        params = parse_filter_params(request)
        # Returns: {'trade_ids': [1, 2, 3], 'statuses': ['DD', 'AWARDED'], ...}
    """
    params = {}
    
    # WHAT: Parse trade IDs (comma-separated integers)
    # WHY: Users can select multiple trades
    trade_ids_str = request.GET.get('trade_ids', '').strip()
    if trade_ids_str:
        try:
            params['trade_ids'] = [int(tid) for tid in trade_ids_str.split(',') if tid.strip()]
        except ValueError:
            params['trade_ids'] = []
    
    # WHAT: Parse statuses (comma-separated strings)
    # WHY: Users can select multiple statuses
    statuses_str = request.GET.get('statuses', '').strip()
    if statuses_str:
        params['statuses'] = [s.strip().upper() for s in statuses_str.split(',') if s.strip()]
    
    # WHAT: Parse fund ID (single integer)
    # WHY: Users select one fund at a time
    fund_id_str = request.GET.get('fund_id', '').strip()
    if fund_id_str:
        try:
            params['fund_id'] = int(fund_id_str)
        except ValueError:
            params['fund_id'] = None
    
    # WHAT: Parse entity ID (single integer)
    # WHY: Users select one entity at a time
    entity_id_str = request.GET.get('entity_id', '').strip()
    if entity_id_str:
        try:
            params['entity_id'] = int(entity_id_str)
        except ValueError:
            params['entity_id'] = None
    
    # WHAT: Parse date range (ISO date strings)
    # WHY: Users set start/end dates for time-based filtering
    if request.GET.get('start_date'):
        params['start_date'] = request.GET.get('start_date').strip()
    
    if request.GET.get('end_date'):
        params['end_date'] = request.GET.get('end_date').strip()
    
    # WHAT: Parse quick search text
    # WHY: Users type in search box for instant filtering
    if request.GET.get('q'):
        params['q'] = request.GET.get('q').strip()
    
    # WHAT: Parse ordering (comma-separated field names)
    # WHY: AG Grid sends sort fields when user clicks column headers
    if request.GET.get('sort'):
        params['ordering'] = request.GET.get('sort').strip()
    
    return params

