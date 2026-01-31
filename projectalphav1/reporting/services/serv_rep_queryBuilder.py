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
from functools import lru_cache
from django.db import connection
from django.db.models import QuerySet, Q, F, Value, CharField, DecimalField, IntegerField, ExpressionWrapper, OuterRef, Subquery, DateField
from django.db.models.functions import Coalesce
from acq_module.models.model_acq_seller import AcqAsset, Trade
from am_module.models.model_am_servicersCleaned import ServicerLoanData


@lru_cache(maxsize=1)
def _has_blended_outcome_table() -> bool:
    return 'am_module_blendedoutcomemodel' in connection.introspection.table_names()


def build_base_queryset() -> QuerySet[AcqAsset]:
    """
    WHAT: Build base AcqAsset queryset with optimized joins and field annotations
    WHY: Reduce N+1 queries by eagerly loading related data and annotate computed fields
    HOW: Use select_related for ForeignKey joins, annotate for field mapping
    
    RETURNS: Optimized QuerySet ready for filtering
    
    NOTE: By default, only shows BOARDED trades (status='BOARD')
    """
    # WHAT: Select related models to avoid N+1 queries
    # WHY: Trade, Seller, AssetHub, ServicerLoanData are frequently accessed in reporting
    # HOW: Use select_related for ForeignKey, prefetch_related for reverse FKs
    queryset = (
        AcqAsset.objects
        .select_related(
            'trade',                    # WHAT: Trade details (name, status, bid_date)
            'trade__seller',            # WHAT: Seller details (name, POC)
            'asset_hub',                # WHAT: Asset hub for master asset data
            # NOTE: Removed 'asset_hub__details' from select_related to avoid INNER JOIN
            # WHY: Many assets don't have AssetDetails yet, we want to show them all
            # HOW: Django will do LEFT JOIN automatically when filtering/annotating
            'seller',                   # WHAT: Direct seller FK if exists
            'loan',
            'property',
            'asset_hub__dil',
            'asset_hub__modification',
            'asset_hub__reo_data',
            'asset_hub__fc_sale',
            'asset_hub__short_sale',
            'asset_hub__note_sale',
            'asset_hub__performing_track',
            'asset_hub__delinquent_track',
        )
        .prefetch_related(
            'asset_hub__valuations',    # WHAT: Valuations for AIV/ARV calculations
            'asset_hub__dil_tasks',
            'asset_hub__modification_tasks',
            'asset_hub__reo_tasks',
            'asset_hub__fc_tasks',
            'asset_hub__short_sale_tasks',
            'asset_hub__note_sale_tasks',
            'asset_hub__performing_tasks',
            'asset_hub__delinquent_tasks',
            'asset_hub__ammetrics',
        )
        # WHAT: Filter to only BOARDED trades by default
        # WHY: Reporting should only show closed/boarded loans, not trades in due diligence
        # HOW: Filter by trade status = 'BOARD'
        .filter(trade__status='BOARD')
    )

    # Conditionally add select_related for blended outcome model if table exists
    if _has_blended_outcome_table():
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
    
    latest_servicer = (
        ServicerLoanData.objects
        .filter(asset_hub_id=OuterRef('asset_hub_id'))
        .order_by('-reporting_year', '-reporting_month', '-as_of_date', '-pk')
    )

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
        # ADDRESS FIELDS (from AcqProperty)
        # ──────────────────────────────────────────────────────────────────
        # NOTE: These legacy names are annotated for reporting compatibility.
        # They allow downstream reports to continue referencing street_address/city/state/zip.
        street_address=F('property__street_address'),
        city=F('property__city'),
        state=F('property__state'),
        zip=F('property__zip'),
        sellertape_id=F('loan__sellertape_id'),
        current_balance=F('loan__current_balance'),
        total_debt=F('loan__total_debt'),
        interest_rate=F('loan__interest_rate'),
        default_rate=F('loan__default_rate'),
        maturity_date=Coalesce(F('loan__current_maturity_date'), F('loan__original_maturity_date')),
        full_address=Concat(
            F('property__street_address'),
            Value(', '),
            F('property__city'),
            Value(', '),
            F('property__state'),
            Value(' '),
            Coalesce(F('property__zip'), Value('')),
            output_field=CharField()
        ),
        
        # ──────────────────────────────────────────────────────────────────
        # CURRENT BALANCE (from ServicerLoanData)
        # ──────────────────────────────────────────────────────────────────
        # WHAT: Current balance from latest servicer snapshot
        # WHY: Avoid duplicate rows from multi-row servicer data
        # SOURCE: latest ServicerLoanData snapshot per asset_hub
        servicer_current_balance=Subquery(
            latest_servicer.values('current_balance')[:1],
            output_field=DecimalField(max_digits=15, decimal_places=2),
        ),
        
        # ====================================================================
        # 📊 ADDITIONAL SERVICER FIELDS - Available but not required
        # ====================================================================
        # WHAT: Additional servicer data fields for advanced reporting
        # WHY: Provide comprehensive servicer data access
        # HOW: Add more servicer fields as needed
        # ====================================================================
        
        # WHAT: Interest rate from servicer
        # WHY: Current interest rate from servicing platform
        servicer_interest_rate=Subquery(
            latest_servicer.values('interest_rate')[:1],
            output_field=DecimalField(max_digits=5, decimal_places=3),
        ),
        
        # WHAT: Total debt from servicer (computed using servicer balances)
        # WHY: Align with computed_total_debt rules for servicing dashboards
        servicer_total_debt=ExpressionWrapper(
            Coalesce(F('servicer_current_balance'), Value(0), output_field=DecimalField())
            + Coalesce(Subquery(latest_servicer.values('deferred_balance')[:1], output_field=DecimalField(max_digits=15, decimal_places=2)), Value(0), output_field=DecimalField())
            + Coalesce(Subquery(latest_servicer.values('escrow_advance_balance')[:1], output_field=DecimalField(max_digits=15, decimal_places=2)), Value(0), output_field=DecimalField())
            + Coalesce(Subquery(latest_servicer.values('third_party_recov_balance')[:1], output_field=DecimalField(max_digits=15, decimal_places=2)), Value(0), output_field=DecimalField())
            + Coalesce(Subquery(latest_servicer.values('servicer_late_fees')[:1], output_field=DecimalField(max_digits=15, decimal_places=2)), Value(0), output_field=DecimalField())
            + Coalesce(Subquery(latest_servicer.values('other_charges')[:1], output_field=DecimalField(max_digits=15, decimal_places=2)), Value(0), output_field=DecimalField())
            + Coalesce(Subquery(latest_servicer.values('interest_arrears')[:1], output_field=DecimalField(max_digits=15, decimal_places=2)), Value(0), output_field=DecimalField())
            - Coalesce(Subquery(latest_servicer.values('suspense_balance')[:1], output_field=DecimalField(max_digits=15, decimal_places=2)), Value(0), output_field=DecimalField()),
            output_field=DecimalField(max_digits=15, decimal_places=2),
        ),
        
        # WHAT: Next due date from servicer
        # WHY: Track payment schedules
        servicer_next_due_date=Subquery(
            latest_servicer.values('next_due_date')[:1],
            output_field=DateField(),
        ),
        
        servicer_current_fico=Subquery(
            latest_servicer.values('current_fico')[:1],
            output_field=IntegerField(),
        ),
        servicer_maturity_date=Subquery(
            latest_servicer.values('maturity_date')[:1],
            output_field=DateField(),
        ),
    )

    # Only annotate BlendedOutcomeModel fields if the table exists
    if _has_blended_outcome_table():
        queryset = queryset.annotate(
            purchase_date=F('asset_hub__blended_outcome_model__purchase_date'),
            purchase_price=F('asset_hub__blended_outcome_model__purchase_price'),
            expected_exit_date=F('asset_hub__blended_outcome_model__expected_exit_date'),
            expected_gross_proceeds=F('asset_hub__blended_outcome_model__expected_gross_proceeds'),
            expected_net_proceeds=F('asset_hub__blended_outcome_model__expected_net_proceeds'),
            expected_pl=F('asset_hub__blended_outcome_model__expected_pl'),
            expected_cf=F('asset_hub__blended_outcome_model__expected_cf'),
            realized_total_expenses=F('asset_hub__ll_transaction_summary__total_expenses_realized'),
            realized_operating_expenses=F('asset_hub__ll_transaction_summary__operating_expenses_total_realized'),
            realized_legal_expenses=F('asset_hub__ll_transaction_summary__legal_total_realized'),
            realized_reo_expenses=F('asset_hub__ll_transaction_summary__reo_total_realized'),
            realized_rehab_trashout=F('asset_hub__ll_transaction_summary__rehab_trashout_total_realized'),
            expense_servicing_realized=F('asset_hub__ll_transaction_summary__expense_servicing_realized'),
            realized_reo_closing_cost=F('asset_hub__ll_transaction_summary__reo_closing_cost_realized'),
            realized_gross_cost=F('asset_hub__ll_transaction_summary__realized_gross_cost'),
            realized_gross_purchase_price=F('asset_hub__ll_transaction_summary__gross_purchase_price_realized'),
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
                + Coalesce(F('asset_hub__blended_outcome_model__property_preservation_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            ),
            rehab_trashout_cost=(
                Coalesce(F('asset_hub__blended_outcome_model__reconciled_rehab_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__trashout_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
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
                + Coalesce(F('asset_hub__blended_outcome_model__servicing_liq_fee'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            ),
            reo_closing_cost=(
                Coalesce(F('asset_hub__blended_outcome_model__tax_title_transfer_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__broker_closing_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            ),
            uw_total_expenses=(
                Coalesce(F('legal_expenses'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('servicing_expenses'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('reo_expenses'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('rehab_trashout_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('carry_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('liq_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('reo_closing_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            ),
            gross_purchase_price=(
                Coalesce(F('purchase_price'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__broker_acq_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__other_fee'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__taxtitle_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__legal_costs'), Value(0, output_field=DecimalField()), output_field=DecimalField())
                + Coalesce(F('asset_hub__blended_outcome_model__due_diligence'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            ),
            uw_other_fees=F('asset_hub__blended_outcome_model__total_other'),
        )

    queryset = queryset.annotate(
        # ====================================================================
        # 🏢 ASSET HUB FIELDS - Master asset data & realized P&L
        # ====================================================================
        asset_master_status=F('asset_hub__details__asset_status'),

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
            + Coalesce(F('asset_hub__blended_outcome_model__property_preservation_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
        ),
        rehab_trashout_cost=(
            Coalesce(F('asset_hub__blended_outcome_model__reconciled_rehab_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            + Coalesce(F('asset_hub__blended_outcome_model__trashout_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
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
            + Coalesce(F('asset_hub__blended_outcome_model__servicing_liq_fee'), Value(0, output_field=DecimalField()), output_field=DecimalField())
        ),
        reo_closing_cost=(
            Coalesce(F('asset_hub__blended_outcome_model__tax_title_transfer_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            + Coalesce(F('asset_hub__blended_outcome_model__broker_closing_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
        ),
        uw_total_expenses=(
            Coalesce(F('legal_expenses'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            + Coalesce(F('servicing_expenses'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            + Coalesce(F('reo_expenses'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            + Coalesce(F('rehab_trashout_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            + Coalesce(F('carry_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            + Coalesce(F('liq_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            + Coalesce(F('reo_closing_cost'), Value(0, output_field=DecimalField()), output_field=DecimalField())
        ),
        gross_purchase_price=(
            Coalesce(F('purchase_price'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            + Coalesce(F('asset_hub__blended_outcome_model__broker_acq_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            + Coalesce(F('asset_hub__blended_outcome_model__other_fee'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            + Coalesce(F('asset_hub__blended_outcome_model__taxtitle_fees'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            + Coalesce(F('asset_hub__blended_outcome_model__legal_costs'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            + Coalesce(F('asset_hub__blended_outcome_model__due_diligence'), Value(0, output_field=DecimalField()), output_field=DecimalField())
        ),
        uw_other_fees=F('asset_hub__blended_outcome_model__total_other'),

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
    queryset: QuerySet[AcqAsset],
    trade_ids: Optional[List[int]] = None
) -> QuerySet[AcqAsset]:
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
    queryset: QuerySet[AcqAsset],
    tracks: Optional[List[str]] = None
) -> QuerySet[AcqAsset]:
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
    queryset: QuerySet[AcqAsset],
    task_statuses: Optional[List[str]] = None,
    tracks: Optional[List[str]] = None,
) -> QuerySet[AcqAsset]:
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
        # HOW: Use Q objects with __in to reduce OR explosion
        task_q = Q()
        
        # WHAT: Check each task type across all task models
        # WHY: Task types can exist in any of the 6 task models
        # HOW: Use asset_hub relationship to join task models
        task_related_map = {
            'reo': 'reo_tasks',
            'fc': 'fc_tasks',
            'dil': 'dil_tasks',
            'short_sale': 'short_sale_tasks',
            'modification': 'modification_tasks',
            'note_sale': 'note_sale_tasks',
        }

        task_related_names = list(task_related_map.values())
        if tracks:
            task_related_names = [
                task_related_map[track]
                for track in tracks
                if track in task_related_map
            ]

        if not task_related_names:
            return queryset
        
        # WHAT: Add filter for each task model using __in list
        # WHY: Fewer OR branches and cleaner SQL
        for related_name in task_related_names:
            task_q |= Q(**{f'asset_hub__{related_name}__task_type__in': task_statuses})
        
        # DISTINCT: Multiple task rows can cause duplicates
        queryset = queryset.filter(task_q).distinct()
    
    return queryset


def apply_fund_filter(
    queryset: QuerySet[AcqAsset],
    fund_id: Optional[int] = None,
    partnership_ids: Optional[List[int]] = None
) -> QuerySet[AcqAsset]:
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
    queryset: QuerySet[AcqAsset],
    entity_id: Optional[int] = None
) -> QuerySet[AcqAsset]:
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
    queryset: QuerySet[AcqAsset],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> QuerySet[AcqAsset]:
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
    queryset: QuerySet[AcqAsset],
    q: Optional[str] = None
) -> QuerySet[AcqAsset]:
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
) -> QuerySet[AcqAsset]:
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
    queryset = apply_task_status_filter(queryset, task_statuses, tracks)
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

