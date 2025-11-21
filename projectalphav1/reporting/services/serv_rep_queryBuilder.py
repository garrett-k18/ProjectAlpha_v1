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
from django.db import connection
from django.db.models import QuerySet, Q, F, Value, CharField, DecimalField, IntegerField
from django.db.models.functions import Coalesce
from acq_module.models.model_acq_seller import SellerRawData, Trade


def build_base_queryset() -> QuerySet[SellerRawData]:
    """
    WHAT: Build base SellerRawData queryset with optimized joins and field annotations
    WHY: Reduce N+1 queries by eagerly loading related data and annotate computed fields
    HOW: Use select_related for ForeignKey joins, annotate for field mapping
    
    RETURNS: Optimized QuerySet ready for filtering
    
    NOTE: By default, only shows BOARDED trades (status='BOARD')
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
            # NOTE: Removed 'asset_hub__details' from select_related to avoid INNER JOIN
            # WHY: Many assets don't have AssetDetails yet, we want to show them all
            # HOW: Django will do LEFT JOIN automatically when filtering/annotating
            'seller',                   # WHAT: Direct seller FK if exists
            'asset_hub__dil',
            'asset_hub__modification',
            'asset_hub__reo_data',
            'asset_hub__fc_sale',
            'asset_hub__short_sale',
        )
        .prefetch_related(
            'asset_hub__valuations',    # WHAT: Valuations for AIV/ARV calculations
            'asset_hub__dil_tasks',
            'asset_hub__modification_tasks',
            'asset_hub__reo_tasks',
            'asset_hub__fc_tasks',
            'asset_hub__short_sale_tasks',
        )
        # WHAT: Filter to only BOARDED trades by default
        # WHY: Reporting should only show closed/boarded loans, not trades in due diligence
        # HOW: Filter by trade status = 'BOARD'
        .filter(trade__status='BOARD')
    )

    # Conditionally add select_related for blended outcome model if table exists
    if 'am_module_blendedoutcomemodel' in connection.introspection.table_names():
        queryset = queryset.select_related('asset_hub__blended_outcome_model')
    
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
        # SOURCE: asset_hub.servicer_loan_data.current_balance
        servicer_current_balance=F('asset_hub__servicer_loan_data__current_balance'),
        
        # ====================================================================
        # 📊 ADDITIONAL SERVICER FIELDS - Available but not required
        # ====================================================================
        # WHAT: Additional servicer data fields for advanced reporting
        # WHY: Provide comprehensive servicer data access
        # HOW: Add more servicer fields as needed
        # ====================================================================
        
        # WHAT: Interest rate from servicer
        # WHY: Current interest rate from servicing platform
        servicer_interest_rate=F('asset_hub__servicer_loan_data__interest_rate'),
        
        # WHAT: Total debt from servicer (includes fees, advances, escrow)
        # WHY: Complete debt picture from servicing platform
        servicer_total_debt=F('asset_hub__servicer_loan_data__total_debt'),
        
        # WHAT: Next due date from servicer
        # WHY: Track payment schedules
        servicer_next_due_date=F('asset_hub__servicer_loan_data__next_due_date'),
    )

    # Only annotate BlendedOutcomeModel fields if the table exists
    has_blended = 'am_module_blendedoutcomemodel' in connection.introspection.table_names()
    if has_blended:
        queryset = queryset.annotate(
            purchase_date=F('asset_hub__blended_outcome_model__purchase_date'),
            purchase_price=F('asset_hub__blended_outcome_model__purchase_price'),
            expected_exit_date=F('asset_hub__blended_outcome_model__expected_exit_date'),
            expected_gross_proceeds=F('asset_hub__blended_outcome_model__expected_gross_proceeds'),
            expected_net_proceeds=F('asset_hub__blended_outcome_model__expected_net_proceeds'),
            expected_pl=F('asset_hub__blended_outcome_model__expected_pl'),
            expected_cf=F('asset_hub__blended_outcome_model__expected_cf'),
            expected_irr=F('asset_hub__blended_outcome_model__expected_irr'),
            expected_moic=F('asset_hub__blended_outcome_model__expected_moic'),
            expected_hold_duration=F('asset_hub__blended_outcome_model__expected_hold_duration'),

            # Initial underwriting percentage bids
            bid_pct_upb=F('asset_hub__blended_outcome_model__bid_pct_upb'),
            bid_pct_td=F('asset_hub__blended_outcome_model__bid_pct_td'),
            bid_pct_sellerasis=F('asset_hub__blended_outcome_model__bid_pct_sellerasis'),
            bid_pct_pv=F('asset_hub__blended_outcome_model__bid_pct_pv'),

            # Exit strategy label
            exit_strategy=F('asset_hub__blended_outcome_model__outcome_blend'),

            # Hold durations
            pre_reo_hold_duration=(
                Coalesce(
                    F('asset_hub__blended_outcome_model__servicing_transfer_duration'),
                    Value(0, output_field=IntegerField()),
                    output_field=IntegerField(),
                )
                + Coalesce(
                    F('asset_hub__blended_outcome_model__pre_fc_duration'),
                    Value(0, output_field=IntegerField()),
                    output_field=IntegerField(),
                )
                + Coalesce(
                    F('asset_hub__blended_outcome_model__fc_duration_state_avg'),
                    Value(0, output_field=IntegerField()),
                    output_field=IntegerField(),
                )
                + Coalesce(
                    F('asset_hub__blended_outcome_model__dil_duration'),
                    Value(0, output_field=IntegerField()),
                    output_field=IntegerField(),
                )
            ),
            reo_hold_duration=(
                Coalesce(
                    F('asset_hub__blended_outcome_model__eviction_duration'),
                    Value(0, output_field=IntegerField()),
                    output_field=IntegerField(),
                )
                + Coalesce(
                    F('asset_hub__blended_outcome_model__renovation_duration'),
                    Value(0, output_field=IntegerField()),
                    output_field=IntegerField(),
                )
                + Coalesce(
                    F('asset_hub__blended_outcome_model__reo_marketing_duration'),
                    Value(0, output_field=IntegerField()),
                    output_field=IntegerField(),
                )
                + Coalesce(
                    F('asset_hub__blended_outcome_model__local_market_ext_duration'),
                    Value(0, output_field=IntegerField()),
                    output_field=IntegerField(),
                )
                + Coalesce(
                    F('asset_hub__blended_outcome_model__rural_ext_duration'),
                    Value(0, output_field=IntegerField()),
                    output_field=IntegerField(),
                )
            ),

            # Aggregated expense buckets
            legal_expenses=(
                Coalesce(F('asset_hub__blended_outcome_model__fc_expenses'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__bk_legal_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__eviction_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__dil_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__cfk_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            ),
            servicing_expenses=(
                Coalesce(F('asset_hub__blended_outcome_model__servicing_board_fee'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_current'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_30d'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_60d'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_90d'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_120d'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_fc'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_bk'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_liq_fee'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            ),
            reo_expenses=(
                Coalesce(F('asset_hub__blended_outcome_model__total_hoa'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__total_utility'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__total_other'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            ),
            carry_cost=(
                Coalesce(F('asset_hub__blended_outcome_model__servicing_board_fee'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_current'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_30d'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_60d'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_90d'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_120d'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_fc'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_bk'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_liq_fee'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__total_insurance'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__total_property_tax'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            ),
            liq_fees=(
                Coalesce(F('asset_hub__blended_outcome_model__am_liq_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__tax_title_transfer_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__broker_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_liq_fee'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            ),
            uw_other_fees=F('asset_hub__blended_outcome_model__total_other'),
        )

    queryset = queryset.annotate(
        # ====================================================================
        # 🏢 ASSET HUB FIELDS - Master asset data
        # ====================================================================
        # WHAT: Asset master status from AssetDetails
        # WHY: Lifecycle status (ACTIVE, LIQUIDATED)
        asset_master_status=F('asset_hub__details__asset_status'),

        # WHAT: Realized gross cost from LLTransactionSummary (loan-level P&L)
        # WHY: Back current_gross_cost column in By Trade asset grid
        current_gross_cost=F('asset_hub__ll_transaction_summary__realized_gross_cost'),

        # ====================================================================
        # 🎯 ADD YOUR OWN FIELDS HERE - Copy patterns above!
        # ====================================================================
        # 
        # PATTERN FOR ASSET HUB FIELDS:
        # your_field_name=F('asset_hub__field_name'),
        #
        # PATTERN FOR SERVICER FIELDS:
        # servicer_your_field=F('asset_hub__servicer_loan_data__field_name'),
        #
        # PATTERN FOR TRADE FIELDS:
        # trade_your_field=F('trade__field_name'),
        #
        # PATTERN FOR SELLER FIELDS:
        # seller_your_field=F('trade__seller__field_name'),
        #
        # EXAMPLES TO ADD:
        # servicer_investor_id=F('asset_hub__servicer_loan_data__investor_id'),
        # servicer_fc_status=F('asset_hub__servicer_loan_data__fc_status'),
        # servicer_bk_status=F('asset_hub__servicer_loan_data__bk_current_status'),
        # servicer_piti=F('asset_hub__servicer_loan_data__piti'),
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


def apply_track_filter(
    queryset: QuerySet[SellerRawData],
    tracks: Optional[List[str]] = None
) -> QuerySet[SellerRawData]:
    """
    WHAT: Filter queryset by AM outcome tracks (REO, FC, DIL, Short Sale, Modification, Note Sale)
    WHY: Users select specific outcome tracks to view in reporting
    HOW: Use asset_hub relationship checks for each track type
    
    ARGS:
        queryset: Base queryset to filter
        tracks: List of track values (reo, fc, dil, short_sale, modification, note_sale) (None = all tracks)
    
    RETURNS: Filtered queryset
    """
    if tracks and len(tracks) > 0:
        # WHAT: Build OR filter for multiple tracks
        # WHY: User can select multiple outcome tracks simultaneously
        # HOW: Use Q objects to combine multiple track checks
        track_q = Q()
        
        # WHAT: Map track values to their related names on AssetIdHub
        # WHY: Each track corresponds to a 1:1 outcome model relationship
        track_map = {
            'reo': 'reo_data',
            'fc': 'fc_sale',
            'dil': 'dil',
            'short_sale': 'short_sale',
            'modification': 'modification',
            'note_sale': 'note_sale',
        }
        
        # WHAT: Add filter for each selected track
        # WHY: Include assets that have any of the selected outcome records
        for track in tracks:
            related_name = track_map.get(track)
            if related_name:
                # WHAT: Check if related outcome model exists
                # WHY: Existence of 1:1 outcome record means asset is on that track
                track_q |= Q(**{f'asset_hub__{related_name}__isnull': False})
        
        queryset = queryset.filter(track_q)
    
    return queryset


def apply_task_status_filter(
    queryset: QuerySet[SellerRawData],
    task_statuses: Optional[List[str]] = None
) -> QuerySet[SellerRawData]:
    """
    WHAT: Filter queryset by active task statuses (eviction, trashout, nod_noi, etc.)
    WHY: Users select specific tasks to view in reporting
    HOW: Query task models for assets with specified task types
    
    ARGS:
        queryset: Base queryset to filter
        task_statuses: List of task type values (eviction, trashout, etc.) (None = no task filtering)
    
    RETURNS: Filtered queryset
    """
    if task_statuses and len(task_statuses) > 0:
        # WHAT: Build OR filter for multiple task types
        # WHY: User can select multiple task types simultaneously
        # HOW: Use Q objects to combine multiple task checks across all task models
        task_q = Q()
        
        # WHAT: Check each task type across all task models
        # WHY: Task types can exist in any of the 6 task models
        # HOW: Use asset_hub relationship to join task models
        task_related_names = [
            'reo_tasks',
            'fc_tasks',
            'dil_tasks',
            'short_sale_tasks',
            'modification_tasks',
            'note_sale_tasks',
        ]
        
        # WHAT: Add filter for each task type across all task models
        # WHY: Find assets that have any of the selected task types active
        for related_name in task_related_names:
            for task_type in task_statuses:
                # WHAT: Check if asset has this task type in this task model
                # WHY: Task can exist in any of the 6 outcome track task models
                task_q |= Q(**{f'asset_hub__{related_name}__task_type': task_type})
        
        queryset = queryset.filter(task_q)
    
    return queryset


def apply_fund_filter(
    queryset: QuerySet[SellerRawData],
    fund_id: Optional[int] = None,
    partnership_ids: Optional[List[int]] = None
) -> QuerySet[SellerRawData]:
    """
    WHAT: Filter queryset by fund/partnership (FundLegalEntity)
    WHY: Users want to see data for specific investment funds or partnerships
    HOW: Filter by fund_legal_entity FK on AssetDetails
    
    ARGS:
        queryset: Base queryset to filter
        fund_id: Single fund ID to filter by (deprecated, use partnership_ids)
        partnership_ids: List of FundLegalEntity IDs to filter by (None = all funds)
    
    RETURNS: Filtered queryset
    """
    # WHAT: Support both single fund_id (legacy) and partnership_ids (new multi-select)
    # WHY: Backward compatibility during transition
    if partnership_ids and len(partnership_ids) > 0:
        # WHAT: Filter by fund_legal_entity on AssetDetails
        # WHY: AssetDetails.fund_legal_entity links assets to funds/partnerships
        # HOW: Use asset_hub__details__fund_legal_entity relationship
        queryset = queryset.filter(asset_hub__details__fund_legal_entity_id__in=partnership_ids)
    elif fund_id:
        # WHAT: Legacy single fund filter
        # WHY: Backward compatibility
        queryset = queryset.filter(asset_hub__details__fund_legal_entity_id=fund_id)
    
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
    tracks: Optional[List[str]] = None,
    task_statuses: Optional[List[str]] = None,
    fund_id: Optional[int] = None,
    partnership_ids: Optional[List[int]] = None,
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
        tracks: List of AM outcome tracks (reo, fc, dil, short_sale, modification, note_sale)
        task_statuses: List of task types (eviction, trashout, nod_noi, etc.)
        fund_id: Single fund ID to filter by (deprecated, use partnership_ids)
        partnership_ids: List of FundLegalEntity IDs to filter by
        entity_id: Entity ID to filter by
        start_date: Start of date range (ISO string)
        end_date: End of date range (ISO string)
        q: Quick search text
        ordering: Comma-separated field names (supports - prefix for desc)
    
    RETURNS: Fully filtered and ordered QuerySet
    
    EXAMPLE:
        # Filter by REO and FC tracks with eviction tasks
        qs = build_reporting_queryset(
            trade_ids=[1, 2, 3],
            tracks=['reo', 'fc'],
            task_statuses=['eviction'],
            partnership_ids=[1, 2],
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
    """
    # WHAT: Start with optimized base queryset
    queryset = build_base_queryset()
    
    # WHAT: Apply filters in sequence
    # WHY: Each filter narrows down the dataset
    queryset = apply_trade_filter(queryset, trade_ids)
    queryset = apply_track_filter(queryset, tracks)
    queryset = apply_task_status_filter(queryset, task_statuses)
    queryset = apply_fund_filter(queryset, fund_id, partnership_ids)
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
        # Request: ?trade_ids=1,2,3&tracks=reo,fc&task_statuses=eviction
        params = parse_filter_params(request)
        # Returns: {'trade_ids': [1, 2, 3], 'tracks': ['reo', 'fc'], 'task_statuses': ['eviction'], ...}
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
    
    # WHAT: Parse tracks (comma-separated strings)
    # WHY: Users can select multiple AM outcome tracks (REO, FC, DIL, Short Sale, Modification, Note Sale)
    tracks_str = request.GET.get('tracks', '').strip()
    if tracks_str:
        params['tracks'] = [s.strip().lower() for s in tracks_str.split(',') if s.strip()]
    
    # WHAT: Parse task statuses (comma-separated strings)
    # WHY: Users can select multiple task types (eviction, trashout, nod_noi, etc.)
    task_statuses_str = request.GET.get('task_statuses', '').strip()
    if task_statuses_str:
        params['task_statuses'] = [s.strip().lower() for s in task_statuses_str.split(',') if s.strip()]
    
    # WHAT: Parse partnership IDs (comma-separated integers)
    # WHY: Users can select multiple funds/partnerships (FundLegalEntity)
    partnership_ids_str = request.GET.get('partnership_ids', '').strip()
    if partnership_ids_str:
        try:
            params['partnership_ids'] = [int(pid) for pid in partnership_ids_str.split(',') if pid.strip()]
        except ValueError:
            params['partnership_ids'] = []
    
    # WHAT: Parse fund ID (single integer) - DEPRECATED, use partnership_ids
    # WHY: Backward compatibility during transition
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

