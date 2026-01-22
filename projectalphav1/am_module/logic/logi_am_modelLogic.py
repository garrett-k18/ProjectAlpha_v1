"""
AM Module Model Logic

WHAT: Business logic for AM module models, particularly for calendar event generation
WHY: Separate business logic from API views to maintain clean separation of concerns
WHERE: Used by calendar views and other AM module services
HOW: Provides reusable functions that can be called from views, services, or other logic modules

Docs reviewed:
- Django QuerySet API: https://docs.djangoproject.com/en/stable/ref/models/querysets/
"""

import math
from decimal import Decimal
from django.db.models import Q
from am_module.models.model_am_modeling import BlendedOutcomeModel, ReUWAMProjections


def resolve_latest_internal_asis_value(
    internal_initial_uw_asis_value,
    internal_asis_value,
):
    """
    Resolve latest as-is value per AM valuation rules.

    WHAT: Prefer Internal Initial UW as-is value, fallback to latest Internal valuation
    WHY: Preserve underwriting baseline while still surfacing updated internal valuations when baseline is blank
    HOW: Return first non-null value in the priority order
    """
    return internal_initial_uw_asis_value or internal_asis_value


def resolve_latest_internal_arv_value(
    internal_initial_uw_arv_value,
    internal_arv_value,
):
    """
    Resolve latest ARV value per AM valuation rules.

    WHAT: Prefer Internal Initial UW ARV value, fallback to latest Internal valuation
    WHY: Preserve underwriting baseline while still surfacing updated internal valuations when baseline is blank
    HOW: Return first non-null value in the priority order
    """
    return internal_initial_uw_arv_value or internal_arv_value


def compute_current_total_debt_from_servicer(
    *,
    current_balance=None,
    deferred_balance=None,
    escrow_advance_balance=None,
    third_party_recov_balance=None,
    suspense_balance=None,
    servicer_late_fees=None,
    other_charges=None,
    interest_arrears=None,
):
    """
    Compute current total debt from servicer-cleaned balances.

    WHAT: Sum key servicer balances into a single debt figure
    WHY: Centralize calculation logic for consistent debt reporting
    HOW:
      - Escrow balance is excluded (cash held, not debt)
      - Escrow advance balance is included (typically negative/owed)
      - Suspense balance is subtracted (funds held, not debt)
    """

    def as_decimal(value):
        if value in (None, ''):
            return Decimal('0')
        try:
            return Decimal(str(value))
        except Exception:
            return Decimal('0')

    total = Decimal('0')
    total += as_decimal(current_balance)
    total += as_decimal(deferred_balance)
    total += as_decimal(escrow_advance_balance)
    total += as_decimal(third_party_recov_balance)
    total += as_decimal(servicer_late_fees)
    total += as_decimal(other_charges)
    total += as_decimal(interest_arrears)
    total -= as_decimal(suspense_balance)

    return total


def resolve_expected_hold_duration(
    expected_hold_duration,
    purchase_date,
    expected_exit_date,
):
    """
    Resolve expected hold duration with fallback to date calculation.

    WHAT: Wrapper for model-level hold duration resolution
    WHY: Centralized logic lives on BlendedOutcomeModel
    HOW: Mirror model-level logic for standalone calls
    """
    if expected_hold_duration is not None:
        try:
            return int(math.ceil(float(expected_hold_duration)))
        except (ValueError, TypeError):
            pass

    if purchase_date and expected_exit_date:
        try:
            months = (expected_exit_date.year - purchase_date.year) * 12 + (expected_exit_date.month - purchase_date.month)
            if expected_exit_date.day > purchase_date.day:
                months += 1
            return max(0, months)
        except Exception:
            pass
    return None


def resolve_gross_purchase_price(
    purchase_price,
    *,
    broker_acq_fees=None,
    other_fee=None,
    taxtitle_fees=None,
    legal_costs=None,
    due_diligence=None,
    fund_acq_fee=None,
):
    """
    Sum of purchase price and acquisition costs.
    """
    if purchase_price is None:
        return None
    
    fees = [broker_acq_fees, other_fee, taxtitle_fees, legal_costs, due_diligence, fund_acq_fee]
    total_fees = sum([Decimal(str(v)) for v in fees if v is not None], Decimal('0'))
    return Decimal(str(purchase_price)) + total_fees


def resolve_expected_gross_cost(
    expected_gross_cost,
    purchase_price,
    *,
    total_expenses=None, # Sum of everything else
    **acq_fee_kwargs
):
    """
    Resolve expected gross cost: Gross Purchase Price + Holding/Operating Expenses.
    """
    if expected_gross_cost is not None:
        return expected_gross_cost

    gpp = resolve_gross_purchase_price(purchase_price, **acq_fee_kwargs)
    if gpp is None:
        return None
    
    # If total_expenses is passed, it should be the holding/operating part 
    # to match the model logic of GPP + HOLDING.
    holding_costs = Decimal(str(total_expenses)) if total_expenses is not None else Decimal('0')
    return gpp + holding_costs


def resolve_total_expenses(model):
    """
    Sum up all major expense categories from a modeling record.

    WHAT: Aggregate individual modeled expense line items
    WHY: Modeling records store fine-grained expenses but UI often needs a grand total
    HOW: Call .total_expenses property on the model
    """
    if not model:
        return None
    return getattr(model, 'total_expenses', None)


def get_projected_liquidation_events(start_date=None, end_date=None, seller_id=None, trade_id=None):
    """
    Extract projected liquidation dates from ReUWAMProjections (with fallback to BlendedOutcomeModel).
    
    WHAT: Gets projected liquidation dates using re-underwritten AM projections if available, otherwise initial UW projections
    WHY: Calendar needs to show projected liquidation dates, prioritizing re-underwritten values over initial UW
    WHERE: Called by calendar views and other services that need projected liquidation dates
    HOW: Queries BlendedOutcomeModel (all boarded assets), checks ReUWAMProjections for re-underwritten values, falls back to initial UW
    
    Logic:
    - Queries all BlendedOutcomeModel records (initial UW projections)
    - For each, checks if ReUWAMProjections.reuw_projected_liq_date exists (re-underwritten projection)
    - If ReUWAMProjections.reuw_projected_liq_date is blank, uses BlendedOutcomeModel.expected_exit_date (initial UW)
    - Only creates event if a date exists from either source
    
    Args:
        start_date: Filter events on/after this date (optional)
        end_date: Filter events on/before this date (optional)
        seller_id: Filter to specific seller (via asset_hub relationship, optional)
        trade_id: Filter to specific trade (via asset_hub relationship, optional)
    
    Returns:
        List of event dicts with keys: id, title, date, time, description, category, 
        source_model, source_id, url, editable, event_type='projected_liquidation'
    """
    events = []
    
    # Build queryset with filters
    # WHAT: Query BlendedOutcomeModel (all boarded assets) with select_related to ReUWAMProjections
    # WHY: Need to check both models - most assets will have BlendedOutcomeModel, some will have ReUWAMProjections
    # HOW: Use select_related to avoid N+1 queries (ReUWAMProjections is OneToOne, so use select_related)
    queryset = BlendedOutcomeModel.objects.select_related(
        'asset_hub',
        'asset_hub__reuw_am_projections'
    ).all()
    
    # Filter by seller/trade through asset_hub relationship
    # WHAT: Apply optional filters for seller_id and/or trade_id
    # WHY: Allow filtering projected liquidation events by seller or trade
    # HOW: Use Q objects to build dynamic filters
    if seller_id or trade_id:
        filters = Q()
        if seller_id:
            filters &= Q(asset_hub__sellerrawdata__seller_id=seller_id)
        if trade_id:
            filters &= Q(asset_hub__sellerrawdata__trade_id=trade_id)
        queryset = queryset.filter(filters)
    
    # WHAT: Iterate through each blended outcome model to extract projected liquidation dates
    # WHY: Need to check each asset for re-underwritten vs initial UW projections
    # HOW: Check ReUWAMProjections first, then fall back to BlendedOutcomeModel
    for blended_model in queryset:
        # WHAT: Get projected liquidation date with fallback logic
        # WHY: Use re-underwritten AM projection if available, otherwise use initial UW projection
        # HOW: Check ReUWAMProjections.reuw_projected_liq_date first, then BlendedOutcomeModel.expected_exit_date
        projected_date = None
        source_model = None
        
        # Priority 1: Use re-underwritten AM projection if available
        # WHAT: Check if ReUWAMProjections exists and has reuw_projected_liq_date
        # WHY: Re-underwritten projections take priority over initial UW projections
        # HOW: Access via OneToOne relationship (select_related already loaded it)
        if blended_model.asset_hub:
            try:
                reuw_projection = getattr(blended_model.asset_hub, 'reuw_am_projections', None)
                if reuw_projection and reuw_projection.reuw_projected_liq_date:
                    projected_date = reuw_projection.reuw_projected_liq_date
                    source_model = 'ReUWAMProjections'
            except AttributeError:
                pass
        
        # Priority 2: Fall back to initial UW projection
        # WHAT: Use BlendedOutcomeModel.expected_exit_date if ReUWAMProjections doesn't have a date
        # WHY: Initial UW projections are better than no projection at all
        # HOW: Check if expected_exit_date exists and projected_date is still None
        if not projected_date and blended_model.expected_exit_date:
            projected_date = blended_model.expected_exit_date
            source_model = 'BlendedOutcomeModel'
        
        # Only create event if we have a date from either source
        # WHAT: Skip assets that don't have any projected liquidation date
        # WHY: Don't create calendar events for assets without projections
        # HOW: Continue to next iteration if projected_date is None
        if not projected_date:
            continue
        
        # Apply date range filter if specified
        # WHAT: Filter out events outside the requested date range
        # WHY: Calendar views may only need events for a specific time period
        # HOW: Compare projected_date to start_date and end_date
        if start_date and projected_date < start_date:
            continue
        if end_date and projected_date > end_date:
            continue
        
        # Get servicer_id, address, city, and state for display
        # WHAT: Extract servicer_id and property location from related models for event display
        # WHY: Calendar events need readable titles showing servicer_id and property (same format as follow-up)
        # HOW: Get servicer_id from AssetIdHub, address/city/state from SellerRawData or ServicerLoanData
        servicer_id = ''
        address = 'Unknown Address'
        city = ''
        state = ''
        if blended_model.asset_hub:
            # WHAT: Get servicer_id directly from AssetIdHub
            # WHY: AssetIdHub has servicer_id field for cross-referencing
            # HOW: Access servicer_id field directly
            servicer_id = blended_model.asset_hub.servicer_id or ''
            
            # WHAT: Get address, city, and state from SellerRawData first, then ServicerLoanData as fallback
            # WHY: Address and location needed for event display
            # HOW: Try SellerRawData first, then ServicerLoanData
            srd = getattr(blended_model.asset_hub, 'acq_raw', None)
            if srd:
                address = srd.street_address or f"{srd.city or 'Unknown'}, {srd.state or ''}"
                city = srd.city or ''
                state = srd.state or ''
            else:
                servicer_data = getattr(blended_model.asset_hub, 'servicer_loan_data', None)
                if servicer_data:
                    latest_servicer = servicer_data.order_by('-as_of_date').first()
                    if latest_servicer:
                        address = latest_servicer.address or f"{latest_servicer.city or 'Unknown'}, {latest_servicer.state or ''}"
                        city = latest_servicer.city or ''
                        state = latest_servicer.state or ''
        
        # WHAT: Truncate address to reasonable length for calendar display
        # WHY: Long addresses break calendar layout
        # HOW: Take first 30 characters
        address_display = address[:30] if address else 'Unknown Address'
        
        # WHAT: Format title same as follow-up events: "servicer_id - address"
        # WHY: Consistent format across event types
        # HOW: Use servicer_id and address if both available, otherwise just address
        if servicer_id and address_display:
            title = f'{servicer_id} - {address_display}'
        elif servicer_id:
            title = servicer_id
        else:
            title = address_display
        
        # WHAT: Create calendar event dict with all required fields
        # WHY: Calendar views expect standardized event format
        # HOW: Build dict with id, title, date, category, event_type, servicer_id, address, city, state, etc.
        events.append({
            'id': f'projected_liquidation:{blended_model.asset_hub_id}',
            'title': title,
            'date': projected_date,
            'time': 'All Day',
            'description': f'Projected liquidation date for {address_display}',
            'category': 'projected_liquidation',
            'event_type': 'projected_liquidation',  # WHAT: Set event_type for frontend filtering
            'source_model': source_model,
            'source_id': blended_model.asset_hub_id,
            'url': f'/am/loan/{blended_model.asset_hub_id}/' if blended_model.asset_hub_id else '',
            'editable': False,  # Model-based events are read-only
            'asset_hub_id': blended_model.asset_hub_id,
            'servicer_id': servicer_id,  # WHAT: Include servicer_id for frontend display
            'address': address_display,  # WHAT: Include address for frontend display
            'city': city,  # WHAT: Include city for event card display
            'state': state,  # WHAT: Include state for event card display
        })
    
    return events

