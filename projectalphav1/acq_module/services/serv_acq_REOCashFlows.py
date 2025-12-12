"""
acq_module.services.serv_acq_REOCashFlows

WHAT: Service layer for REO Sale cash flow series generation
WHY: Provide dynamic period-by-period cash flows for REO model waterfall analysis
WHERE: projectalphav1/acq_module/services/serv_acq_REOCashFlows.py
HOW: Generates monthly cash flow arrays based on REO timeline phases and expense allocations

This service generates cash flow series that map inflows and outflows to specific periods
based on the REO sale timeline (servicing transfer, foreclosure, renovation, marketing).

Example: 15-month hold period might have:
- Month 0: Acquisition price outflow
- Month 1-2: Servicing transfer costs
- Month 3-14: Foreclosure, renovation, and holding costs
- Month 15: REO sale proceeds inflow
"""
from __future__ import annotations

from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta

from acq_module.models.model_acq_seller import SellerRawData
from acq_module.models.model_acq_assumptions import TradeLevelAssumption, LoanLevelAssumption
from acq_module.services.serv_acq_REOModel import get_reo_timeline_sums, get_reo_expense_values
from acq_module.logic.logi_acq_outcomespecific import reoAsIsOutcomeLogic, reoArvOutcomeLogic
from core.models.model_co_geoAssumptions import StateReference
from core.models.model_co_assumptions import Servicer


def generate_reo_cashflow_series(
    asset_hub_id: int,
    scenario: str = 'as_is',  # 'as_is' or 'arv'
    reference_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    Generate period-by-period cash flow series for REO Sale outcome model.
    
    WHAT: Creates monthly cash flow arrays showing timing of all inflows and outflows
    WHY: Enable waterfall analysis, NPV calculations, and visualizations of cash flow timing
    WHERE: Called by API views to serve frontend REO model cash flow visualizations
    HOW: 
    1. Get timeline durations from get_reo_timeline_sums
    2. Get expense values from get_reo_expense_values
    3. Allocate expenses to appropriate periods based on timing rules
    4. Generate arrays for each cash flow category by period
    
    TIMING RULES:
    Period 0 (Settlement):
    - Acquisition price outflow
    - Acquisition costs (broker fees, legal, DD, tax/title)
    
    Period 1 to Servicing Transfer End:
    - Servicing transfer fees (board fee in period 1, monthly 120-day fees spread across period)
    - Monthly taxes and insurance
    
    Foreclosure Period:
    - Monthly foreclosure servicing fees
    - Monthly taxes and insurance
    - Legal costs (typically paid at end of foreclosure, or spread across period)
    
    REO Renovation Period (ARV scenario only):
    - Monthly REO servicing fees
    - Monthly taxes, insurance, and holding costs (HOA, utilities, property preservation)
    - Renovation costs (can be upfront, spread, or end of period - configurable)
    - Trashout costs (typically at start of renovation)
    
    REO Marketing Period:
    - Monthly REO servicing fees
    - Monthly taxes, insurance, and holding costs
    
    Final Period (Sale):
    - Expected proceeds inflow
    - Liquidation fees (broker commission, servicer liq fee, AM fee)
    
    Args:
        asset_hub_id: Primary key of AssetIdHub
        scenario: 'as_is' or 'arv' - determines renovation inclusion
        reference_date: Date to calculate from (defaults to today)
    
    Returns:
        Dict containing:
        - periods: List[int] - Period numbers (0 to total_months)
        - period_labels: List[str] - Human-readable period labels
        - cash_flows: Dict[str, List[float]] - Cash flow arrays by category:
            - acquisition_price: Outflow in period 0
            - acq_costs: Acquisition costs in period 0
            - servicing_fees: Monthly servicing fees
            - taxes: Monthly tax payments
            - insurance: Monthly insurance payments
            - legal_cost: Legal costs (timing configurable)
            - reo_holding_costs: Monthly holding costs during REO ownership
            - trashout_cost: One-time trashout cost
            - renovation_cost: Renovation costs (timing configurable, ARV only)
            - liquidation_fees: Liquidation fees in final period
            - proceeds: Sale proceeds in final period
            - net_cash_flow: Net cash flow by period (sum of all)
        - cumulative_cash_flow: List[float] - Running total of cash flows
        - timeline_summary: Dict - Breakdown of which periods map to which phases
        - totals: Dict - Summary totals for validation
    """
    # WHAT: Validate scenario parameter
    # WHY: Only support 'as_is' and 'arv' scenarios
    if scenario not in ['as_is', 'arv']:
        raise ValueError(f"Invalid scenario: {scenario}. Must be 'as_is' or 'arv'")
    
    # WHAT: Get asset and trade data to access settlement_date and total_discount
    # WHY: Need settlement_date to generate MM/YYYY period dates, total_discount (WACC) for NPV calculation
    try:
        raw_data = SellerRawData.objects.get(asset_hub_id=asset_hub_id)
        trade = raw_data.trade
        trade_assumptions = TradeLevelAssumption.objects.filter(trade=trade).first()
        settlement_date = trade_assumptions.settlement_date if trade_assumptions else None
        # WHAT: Get total_discount (WACC) from trade assumptions, fallback to discount_rate, then default to 12%
        if trade_assumptions and trade_assumptions.total_discount is not None:
            discount_rate = float(trade_assumptions.total_discount)
        elif trade_assumptions and trade_assumptions.discount_rate is not None:
            discount_rate = float(trade_assumptions.discount_rate)
        else:
            discount_rate = 0.12  # Default to 12% if neither is set
    except SellerRawData.DoesNotExist:
        settlement_date = None
        discount_rate = 0.12  # Default to 12% if no trade data
    
    # WHAT: Default to today if no settlement date available
    if settlement_date is None:
        settlement_date = date.today()
    
    # WHAT: Get timeline durations for this asset
    # WHY: Need to know how many periods and phase boundaries
    timeline_data = get_reo_timeline_sums(asset_hub_id, reference_date)
    
    # WHAT: Extract timeline durations (in months)
    servicing_transfer_months = timeline_data.get('servicing_transfer_months', 0) or 0
    foreclosure_months = timeline_data.get('foreclosure_months', 0) or 0
    reo_renovation_months = timeline_data.get('reo_renovation_months', 0) or 0
    reo_marketing_months = timeline_data.get('reo_marketing_months', 0) or 0
    
    # WHAT: Calculate total timeline based on scenario
    # WHY: ARV includes renovation, As-Is does not
    if scenario == 'arv':
        total_months = servicing_transfer_months + foreclosure_months + reo_renovation_months + reo_marketing_months
    else:
        total_months = servicing_transfer_months + foreclosure_months + reo_marketing_months
    
    # WHAT: Get expense values from REO model
    # WHY: Need actual dollar amounts to allocate across periods
    expense_data = get_reo_expense_values(
        asset_hub_id=asset_hub_id,
        total_timeline_months=total_months,
        servicing_transfer_months=servicing_transfer_months,
        foreclosure_months=foreclosure_months,
        reo_renovation_months=reo_renovation_months if scenario == 'arv' else 0,
        reo_marketing_months=reo_marketing_months
    )
    
    # WHAT: Initialize cash flow arrays (one entry per period, starting at period 0)
    # WHY: Need to track each cash flow category separately by period
    num_periods = total_months + 1  # +1 for period 0 (settlement)
    
    # WHAT: Initialize all cash flow arrays with zeros
    cf_acquisition_price = [Decimal('0.0')] * num_periods
    cf_acq_costs = [Decimal('0.0')] * num_periods
    cf_servicing_fees = [Decimal('0.0')] * num_periods
    cf_taxes = [Decimal('0.0')] * num_periods
    cf_insurance = [Decimal('0.0')] * num_periods
    cf_legal_cost = [Decimal('0.0')] * num_periods
    cf_reo_holding_costs = [Decimal('0.0')] * num_periods
    cf_trashout_cost = [Decimal('0.0')] * num_periods
    cf_renovation_cost = [Decimal('0.0')] * num_periods
    cf_liquidation_fees = [Decimal('0.0')] * num_periods
    cf_proceeds = [Decimal('0.0')] * num_periods
    
    # WHAT: Helper to safely convert expense values to Decimal
    def to_decimal(value: Any) -> Decimal:
        """Convert various numeric types to Decimal safely"""
        if value is None:
            return Decimal('0.0')
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
    
    # WHAT: Extract expense values
    acquisition_price = to_decimal(expense_data.get('acquisition_price'))
    acq_broker_fees = to_decimal(expense_data.get('acq_broker_fees'))
    acq_other_fees = to_decimal(expense_data.get('acq_other_fees'))
    acq_legal = to_decimal(expense_data.get('acq_legal'))
    acq_dd = to_decimal(expense_data.get('acq_dd'))
    acq_tax_title = to_decimal(expense_data.get('acq_tax_title'))
    
    # WHAT: Monthly rates for carry costs
    monthly_tax = to_decimal(expense_data.get('monthly_tax'))
    monthly_insurance = to_decimal(expense_data.get('monthly_insurance'))
    monthly_reo_holding = to_decimal(expense_data.get('monthly_reo_holding'))
    
    # WHAT: Servicing fee components
    board_fee = to_decimal(expense_data.get('board_fee'))
    onetwentyday_fee = to_decimal(expense_data.get('onetwentyday_fee'))
    fc_fee = to_decimal(expense_data.get('fc_fee'))
    reo_fee = to_decimal(expense_data.get('reo_fee'))
    
    # WHAT: One-time costs
    legal_cost = to_decimal(expense_data.get('legal_cost'))
    trashout_cost = to_decimal(expense_data.get('trashout_cost'))
    renovation_cost = to_decimal(expense_data.get('renovation_cost')) if scenario == 'arv' else Decimal('0.0')
    
    # WHAT: Liquidation fees and proceeds (scenario-specific)
    if scenario == 'arv':
        broker_fees = to_decimal(expense_data.get('broker_fees_arv'))
        servicer_liq_fee = to_decimal(expense_data.get('servicer_liquidation_fee_arv'))
        am_liq_fee = to_decimal(expense_data.get('am_liquidation_fee_arv'))
        expected_proceeds = to_decimal(expense_data.get('expected_proceeds_arv'))
    else:
        broker_fees = to_decimal(expense_data.get('broker_fees'))
        servicer_liq_fee = to_decimal(expense_data.get('servicer_liquidation_fee'))
        am_liq_fee = to_decimal(expense_data.get('am_liquidation_fee'))
        expected_proceeds = to_decimal(expense_data.get('expected_proceeds_asis'))
    
    # -------------------------------------------------------------------------
    # PERIOD 0: SETTLEMENT / ACQUISITION
    # -------------------------------------------------------------------------
    # WHAT: Allocate acquisition price and acquisition costs to period 0
    # WHY: These are upfront costs paid at settlement
    cf_acquisition_price[0] = -acquisition_price  # Negative = outflow
    cf_acq_costs[0] = -(acq_broker_fees + acq_other_fees + acq_legal + acq_dd + acq_tax_title)
    
    # -------------------------------------------------------------------------
    # PHASE 1: SERVICING TRANSFER PERIOD
    # -------------------------------------------------------------------------
    # WHAT: Calculate period boundaries
    servicing_start = 1
    servicing_end = servicing_transfer_months
    
    # WHAT: Allocate servicing transfer costs
    # WHY: Board fee in first month, 120-day fees spread across servicing period
    if servicing_transfer_months > 0:
        # WHAT: Board fee goes in first month of servicing
        cf_servicing_fees[servicing_start] = -board_fee
        
        # WHAT: Spread 120-day fees across servicing transfer period
        # WHY: These are monthly recurring fees during servicing transfer
        for period in range(servicing_start, servicing_end + 1):
            cf_servicing_fees[period] += -onetwentyday_fee
            cf_taxes[period] = -monthly_tax
            cf_insurance[period] = -monthly_insurance
    
    # -------------------------------------------------------------------------
    # PHASE 2: FORECLOSURE PERIOD
    # -------------------------------------------------------------------------
    fc_start = servicing_end + 1
    fc_end = fc_start + foreclosure_months - 1
    
    if foreclosure_months > 0:
        # WHAT: Calculate legal cost per period (spread evenly)
        # WHY: User requested legal costs be divided evenly during foreclosure periods
        legal_per_period = legal_cost / Decimal(foreclosure_months) if foreclosure_months > 0 else Decimal('0.0')
        
        # WHAT: Allocate monthly foreclosure servicing fees, taxes, insurance, and legal costs
        for period in range(fc_start, fc_end + 1):
            cf_servicing_fees[period] = -fc_fee
            cf_taxes[period] = -monthly_tax
            cf_insurance[period] = -monthly_insurance
            cf_legal_cost[period] = -legal_per_period  # Spread evenly across foreclosure
    
    # -------------------------------------------------------------------------
    # PHASE 3: REO RENOVATION PERIOD (ARV scenario only)
    # -------------------------------------------------------------------------
    renovation_start = fc_end + 1
    renovation_end = renovation_start + reo_renovation_months - 1
    
    if scenario == 'arv' and reo_renovation_months > 0:
        # WHAT: Allocate renovation cost across renovation period
        # WHY: User approved current timing - split evenly across renovation period
        renovation_per_period = renovation_cost / Decimal(reo_renovation_months)
        
        for period in range(renovation_start, renovation_end + 1):
            cf_renovation_cost[period] = -renovation_per_period
            cf_servicing_fees[period] = -reo_fee
            cf_taxes[period] = -monthly_tax
            cf_insurance[period] = -monthly_insurance
            cf_reo_holding_costs[period] = -monthly_reo_holding
    
    # -------------------------------------------------------------------------
    # PHASE 4: REO MARKETING PERIOD
    # -------------------------------------------------------------------------
    if scenario == 'arv':
        marketing_start = renovation_end + 1
    else:
        # WHAT: In As-Is scenario, marketing starts after foreclosure
        # WHY: No renovation phase, so marketing follows foreclosure immediately
        marketing_start = fc_end + 1
    
    marketing_end = marketing_start + reo_marketing_months - 1
    
    # WHAT: Allocate trashout cost at START of marketing period (both scenarios)
    # WHY: User requested trashout occurs when property enters marketing phase
    if reo_marketing_months > 0:
        cf_trashout_cost[marketing_start] = -trashout_cost
    
    if reo_marketing_months > 0:
        for period in range(marketing_start, marketing_end + 1):
            cf_servicing_fees[period] = -reo_fee
            cf_taxes[period] = -monthly_tax
            cf_insurance[period] = -monthly_insurance
            cf_reo_holding_costs[period] = -monthly_reo_holding
    
    # -------------------------------------------------------------------------
    # FINAL PERIOD: REO SALE / LIQUIDATION
    # -------------------------------------------------------------------------
    final_period = total_months
    
    # WHAT: Allocate sale proceeds (inflow) and liquidation fees (outflow)
    # WHY: Sale happens at end of timeline
    cf_proceeds[final_period] = expected_proceeds  # Positive = inflow
    cf_liquidation_fees[final_period] = -(broker_fees + servicer_liq_fee + am_liq_fee)
    
    # -------------------------------------------------------------------------
    # CALCULATE NET CASH FLOW AND CUMULATIVE CASH FLOW
    # -------------------------------------------------------------------------
    # WHAT: Sum all cash flow categories to get net cash flow by period
    net_cash_flow = []
    cumulative_cash_flow = []
    cumulative = Decimal('0.0')
    
    for i in range(num_periods):
        period_net = (
            cf_acquisition_price[i] +
            cf_acq_costs[i] +
            cf_servicing_fees[i] +
            cf_taxes[i] +
            cf_insurance[i] +
            cf_legal_cost[i] +
            cf_reo_holding_costs[i] +
            cf_trashout_cost[i] +
            cf_renovation_cost[i] +
            cf_liquidation_fees[i] +
            cf_proceeds[i]
        )
        net_cash_flow.append(float(period_net))
        
        cumulative += period_net
        cumulative_cash_flow.append(float(cumulative))
    
    # -------------------------------------------------------------------------
    # GENERATE PERIOD DATES (MM/YYYY format based on settlement_date)
    # -------------------------------------------------------------------------
    # WHAT: Generate actual MM/YYYY dates for each period starting from settlement_date
    # WHY: User requested actual dates instead of generic "Phase" labels
    # HOW: Add months to settlement_date for each period
    period_dates = []
    for i in range(num_periods):
        period_date = settlement_date + relativedelta(months=i)
        period_dates.append(period_date.strftime('%m/%Y'))
    
    # -------------------------------------------------------------------------
    # GENERATE PERIOD LABELS (for backward compatibility, keep phase labels too)
    # -------------------------------------------------------------------------
    period_labels = []
    for i in range(num_periods):
        if i == 0:
            period_labels.append('Settlement')
        elif i <= servicing_end:
            period_labels.append('Servicing')
        elif i <= fc_end:
            period_labels.append('Foreclosure')
        elif scenario == 'arv' and i <= renovation_end:
            period_labels.append('Renovation')
        elif i <= marketing_end:
            period_labels.append('Marketing')
        elif i == final_period:
            period_labels.append('Sale')
        else:
            period_labels.append('Active')
    
    # -------------------------------------------------------------------------
    # TIMELINE SUMMARY (which periods map to which phases)
    # -------------------------------------------------------------------------
    timeline_summary = {
        'servicing_transfer': {
            'start_period': servicing_start if servicing_transfer_months > 0 else None,
            'end_period': servicing_end if servicing_transfer_months > 0 else None,
            'duration_months': servicing_transfer_months
        },
        'foreclosure': {
            'start_period': fc_start if foreclosure_months > 0 else None,
            'end_period': fc_end if foreclosure_months > 0 else None,
            'duration_months': foreclosure_months
        },
        'renovation': {
            'start_period': renovation_start if scenario == 'arv' and reo_renovation_months > 0 else None,
            'end_period': renovation_end if scenario == 'arv' and reo_renovation_months > 0 else None,
            'duration_months': reo_renovation_months if scenario == 'arv' else 0
        },
        'marketing': {
            'start_period': marketing_start if reo_marketing_months > 0 else None,
            'end_period': marketing_end if reo_marketing_months > 0 else None,
            'duration_months': reo_marketing_months
        },
        'sale': {
            'period': final_period,
            'duration_months': 0  # Instant transaction
        }
    }
    
    # -------------------------------------------------------------------------
    # CALCULATE IRR AND NPV FROM CASH FLOWS
    # -------------------------------------------------------------------------
    # WHAT: Calculate Internal Rate of Return (IRR) and Net Present Value (NPV)
    # WHY: IRR shows annualized return rate, NPV shows present value at discount rate
    # HOW: Use outcome-specific logic classes (separate for As-Is and ARV scenarios)
    # NOTE: NPV uses discount_rate from TradeLevelAssumption (defaults to 12% if not set)
    if scenario == 'as_is':
        reo_logic = reoAsIsOutcomeLogic()
        calculated_irr = reo_logic.calculate_irr(net_cash_flow)
        calculated_npv = reo_logic.calculate_npv(net_cash_flow, discount_rate)
    else:  # scenario == 'arv'
        reo_logic = reoArvOutcomeLogic()
        calculated_irr = reo_logic.calculate_irr(net_cash_flow)
        calculated_npv = reo_logic.calculate_npv(net_cash_flow, discount_rate)
    
    # -------------------------------------------------------------------------
    # TOTALS FOR VALIDATION
    # -------------------------------------------------------------------------
    # WHAT: Calculate totals for each category to validate against expense_data
    totals = {
        'total_acquisition_price': float(sum(cf_acquisition_price)),
        'total_acq_costs': float(sum(cf_acq_costs)),
        'total_servicing_fees': float(sum(cf_servicing_fees)),
        'total_taxes': float(sum(cf_taxes)),
        'total_insurance': float(sum(cf_insurance)),
        'total_legal_cost': float(sum(cf_legal_cost)),
        'total_reo_holding_costs': float(sum(cf_reo_holding_costs)),
        'total_trashout_cost': float(sum(cf_trashout_cost)),
        'total_renovation_cost': float(sum(cf_renovation_cost)),
        'total_liquidation_fees': float(sum(cf_liquidation_fees)),
        'total_proceeds': float(sum(cf_proceeds)),
        'total_net_cash_flow': sum(net_cash_flow),
        'final_cumulative': cumulative_cash_flow[-1] if cumulative_cash_flow else 0.0,
        'irr': calculated_irr,  # WHAT: Internal Rate of Return (as decimal)
        'npv': calculated_npv,  # WHAT: Net Present Value at total_discount (WACC) from TradeLevelAssumption
        'discount_rate': discount_rate,  # WHAT: Discount rate used for NPV calculation (total_discount or discount_rate fallback)
    }
    
    # -------------------------------------------------------------------------
    # RETURN COMPLETE CASH FLOW SERIES
    # -------------------------------------------------------------------------
    return {
        'scenario': scenario,
        'total_months': total_months,
        'periods': list(range(num_periods)),
        'period_labels': period_labels,  # Phase labels (Settlement, Foreclosure, etc.)
        'period_dates': period_dates,  # Actual MM/YYYY dates
        'settlement_date': settlement_date.isoformat(),  # ISO format for frontend
        'cash_flows': {
            'acquisition_price': [float(x) for x in cf_acquisition_price],
            'acq_costs': [float(x) for x in cf_acq_costs],
            'servicing_fees': [float(x) for x in cf_servicing_fees],
            'taxes': [float(x) for x in cf_taxes],
            'insurance': [float(x) for x in cf_insurance],
            'legal_cost': [float(x) for x in cf_legal_cost],
            'reo_holding_costs': [float(x) for x in cf_reo_holding_costs],
            'trashout_cost': [float(x) for x in cf_trashout_cost],
            'renovation_cost': [float(x) for x in cf_renovation_cost],
            'liquidation_fees': [float(x) for x in cf_liquidation_fees],
            'proceeds': [float(x) for x in cf_proceeds],
            'net_cash_flow': net_cash_flow
        },
        'cumulative_cash_flow': cumulative_cash_flow,
        'timeline_summary': timeline_summary,
        'totals': totals,
        'irr': calculated_irr,  # WHAT: IRR calculated from cash flow series
        'npv': calculated_npv,  # WHAT: NPV at total_discount (WACC) from TradeLevelAssumption
        'discount_rate': discount_rate,  # WHAT: Discount rate used for NPV calculation (total_discount or discount_rate fallback)
        # WHAT: Include expense breakdown for frontend display
        'expense_breakdown': {
            'acquisition_price': float(acquisition_price),
            'acq_broker_fees': float(acq_broker_fees),
            'acq_other_fees': float(acq_other_fees),
            'acq_legal': float(acq_legal),
            'acq_dd': float(acq_dd),
            'acq_tax_title': float(acq_tax_title),
            'monthly_tax': float(monthly_tax),
            'monthly_insurance': float(monthly_insurance),
            'monthly_reo_holding': float(monthly_reo_holding),
            'board_fee': float(board_fee),
            'onetwentyday_fee': float(onetwentyday_fee),
            'fc_fee': float(fc_fee),
            'reo_fee': float(reo_fee),
            'legal_cost': float(legal_cost),
            'trashout_cost': float(trashout_cost),
            'renovation_cost': float(renovation_cost),
            'broker_fees': float(broker_fees),
            'servicer_liq_fee': float(servicer_liq_fee),
            'am_liq_fee': float(am_liq_fee),
            'expected_proceeds': float(expected_proceeds)
        }
    }


def generate_pooled_reo_cashflow_series(
    seller_id: int,
    trade_id: int,
    scenario: str = 'as_is'
) -> Dict[str, Any]:
    """
    Generate aggregated (pooled) cash flow series for all assets in a trade.
    
    WHAT: Sums all asset-level cash flows period-by-period to show pool-level cash flow
    WHY: Enable pool-level cash flow analysis in modeling center
    WHERE: Called by API views to serve pooled cash flow data
    HOW: 
    1. Bulk-fetch all assets and related data
    2. Calculate individual cash flows for each asset
    3. Aggregate period-by-period to get pool totals
    4. Align periods to earliest settlement date
    
    PERFORMANCE NOTE: Currently calls generate_reo_cashflow_series for each asset,
    which makes multiple queries per asset. For large pools (100+ assets), this can be slow.
    TODO: Optimize by creating a bulk version that accepts pre-fetched data maps.
    
    Args:
        seller_id: Seller ID to filter assets
        trade_id: Trade ID to filter assets
        scenario: 'as_is' or 'arv' - determines renovation inclusion
    
    Returns:
        Dict containing aggregated cash flow series with same structure as individual asset
        cash flow series, but with summed values across all assets
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # WHAT: Validate scenario parameter
    if scenario not in ['as_is', 'arv']:
        raise ValueError(f"Invalid scenario: {scenario}. Must be 'as_is' or 'arv'")
    
    # -------------------------------------------------------------------------
    # BULK FETCH ALL DATA UPFRONT (avoids N+1 queries)
    # -------------------------------------------------------------------------
    logger.info(f"[PooledCashFlows] Bulk fetching data for seller={seller_id}, trade={trade_id}")
    
    # WHAT: Get all assets for this trade (exclude dropped)
    assets = list(
        SellerRawData.objects
        .filter(seller_id=seller_id, trade_id=trade_id)
        .exclude(acq_status=SellerRawData.AcquisitionStatus.DROP)
        .filter(asset_hub_id__isnull=False)
        .select_related('trade')
        .order_by('pk')
    )
    
    if not assets:
        raise ValueError('No assets found for this trade')
    
    logger.info(f"[PooledCashFlows] Found {len(assets)} assets")
    
    # WHAT: Get trade assumption (shared across all assets)
    trade_assumption = TradeLevelAssumption.objects.filter(
        trade_id=trade_id
    ).select_related('servicer').first()
    
    # WHAT: Get all asset_hub_ids for bulk queries
    asset_hub_ids = [a.asset_hub_id for a in assets if a.asset_hub_id]
    
    # WHAT: Bulk fetch loan level assumptions
    loan_assumptions_qs = LoanLevelAssumption.objects.filter(
        asset_hub_id__in=asset_hub_ids
    )
    loan_assumptions_map = {la.asset_hub_id: la for la in loan_assumptions_qs}
    
    # WHAT: Get unique states and bulk fetch state references
    states = set(a.state for a in assets if a.state)
    state_refs_qs = StateReference.objects.filter(state_code__in=states)
    state_refs_map = {sr.state_code: sr for sr in state_refs_qs}
    
    # WHAT: Get settlement date from trade assumption (used for period 0 alignment)
    settlement_date = trade_assumption.settlement_date if trade_assumption else date.today()
    earliest_settlement_date = settlement_date
    
    # -------------------------------------------------------------------------
    # BULK FETCH ADDITIONAL DATA NEEDED FOR CASH FLOW CALCULATION
    # -------------------------------------------------------------------------
    # WHAT: Pre-fetch all data that get_reo_timeline_sums and get_reo_expense_values need
    # WHY: These functions are called per-asset and make queries - we can bulk-fetch upfront
    from core.models.model_co_assumptions import HOAAssumption, PropertyTypeAssumption, SquareFootageAssumption
    
    # WHAT: Get unique property types for bulk HOA/PropertyType queries
    property_types = set(a.property_type for a in assets if a.property_type)
    hoa_map = {hoa.property_type.lower(): hoa for hoa in HOAAssumption.objects.filter(property_type__in=property_types)}
    prop_type_map = {pt.property_type.lower(): pt for pt in PropertyTypeAssumption.objects.filter(property_type__in=property_types)}
    
    # WHAT: Get square footage ranges for bulk SquareFootage queries
    # NOTE: SquareFootageAssumption uses ranges, so we'd need to query all and filter in Python
    # For now, we'll let the functions query these as needed (they're less common)
    sqft_assumptions = list(SquareFootageAssumption.objects.all())
    sqft_map = {}  # Will be built on-demand if needed
    
    # WHAT: Bulk fetch FC timelines for all assets (if get_asset_fc_timeline supports bulk)
    # NOTE: This might require refactoring get_asset_fc_timeline to accept bulk data
    # For now, we'll let it query as needed but Django's query cache will help
    
    # -------------------------------------------------------------------------
    # CALCULATE CASH FLOWS USING BULK DATA (FULLY OPTIMIZED - NO PER-ASSET QUERIES)
    # -------------------------------------------------------------------------
    logger.info(f"[PooledCashFlows] Calculating aggregated cash flows for {len(assets)} assets using bulk data (NO per-asset queries)")
    
    # WHAT: Use calculate_asset_model_data_fast to get all data in memory
    # WHY: This function already has timeline and cost data without making queries
    # HOW: Call once per asset with pre-fetched data, then generate cash flows in memory
    
    from acq_module.logic.logi_acq_metrics import calculate_asset_model_data_fast
    
    # WHAT: Get servicer and bid percentage
    servicer = trade_assumption.servicer if trade_assumption else None
    bid_pct = Decimal('0.85')
    if trade_assumption and trade_assumption.pctUPB:
        bid_pct = trade_assumption.pctUPB / Decimal('100')
    
    # WHAT: Calculate model data for all assets (this uses bulk-fetched data, no queries!)
    logger.info(f"[PooledCashFlows] Calculating model data using bulk-fetched data...")
    
    all_model_data = []
    max_periods = 0
    
    for asset in assets:
        loan_assumption = loan_assumptions_map.get(asset.asset_hub_id)
        state_ref = state_refs_map.get(asset.state) if asset.state else None
        
        # WHAT: This uses only the bulk-fetched data - NO DATABASE QUERIES
        model_data = calculate_asset_model_data_fast(
            raw_data=asset,
            trade_assumption=trade_assumption,
            loan_assumption=loan_assumption,
            state_ref=state_ref,
            servicer=servicer,
            bid_pct=bid_pct,
        )
        
        # WHAT: Calculate timeline from model data
        if scenario == 'arv':
            total_months = model_data['total_duration_months_arv']
        else:
            total_months = model_data['total_duration_months_asis']
        
        num_periods = int(total_months) + 1  # +1 for period 0
        max_periods = max(max_periods, num_periods)
        
        all_model_data.append({
            'asset': asset,
            'model': model_data,
            'num_periods': num_periods,
            'loan_assumption': loan_assumption,
            'state_ref': state_ref
        })
    
    logger.info(f"[PooledCashFlows] Max periods across all assets: {max_periods}. Generating cash flows...")
    
    # WHAT: Initialize aggregated cash flow arrays
    aggregated_cf = {
        'acquisition_price': [Decimal('0.0')] * max_periods,
        'acq_costs': [Decimal('0.0')] * max_periods,
        'servicing_fees': [Decimal('0.0')] * max_periods,
        'taxes': [Decimal('0.0')] * max_periods,
        'insurance': [Decimal('0.0')] * max_periods,
        'legal_cost': [Decimal('0.0')] * max_periods,
        'reo_holding_costs': [Decimal('0.0')] * max_periods,
        'trashout_cost': [Decimal('0.0')] * max_periods,
        'renovation_cost': [Decimal('0.0')] * max_periods,
        'liquidation_fees': [Decimal('0.0')] * max_periods,
        'proceeds': [Decimal('0.0')] * max_periods,
        'net_cash_flow': [Decimal('0.0')] * max_periods,
    }
    
    # WHAT: For each asset, generate simplified cash flows and aggregate
    # WHY: Use the pre-calculated totals to allocate to periods without querying
    # HOW: Simple allocation logic based on model data
    
    for idx, item in enumerate(all_model_data):
        asset = item['asset']
        model = item['model']
        num_periods = item['num_periods']
        
        # WHAT: Get costs from model data (already calculated)
        acq_price = Decimal(str(model['acquisition_price']))
        acq_costs = Decimal(str(model.get('acq_costs', 0)))  # From calculate_asset_model_data_fast
        total_costs = Decimal(str(model['total_costs_asis' if scenario == 'as_is' else 'total_costs_arv']))
        proceeds = Decimal(str(model['expected_proceeds_asis' if scenario == 'as_is' else 'expected_proceeds_arv']))
        
        # WHAT: Allocate to periods - simplified allocation
        # Period 0: Acquisition price and costs
        aggregated_cf['acquisition_price'][0] += -acq_price
        aggregated_cf['acq_costs'][0] += -acq_costs
        
        # WHAT: Spread carry costs evenly across timeline (simplified for speed)
        carry_per_month = total_costs / Decimal(num_periods) if num_periods > 0 else Decimal('0')
        
        for period_idx in range(1, min(num_periods, max_periods)):
            aggregated_cf['servicing_fees'][period_idx] += -carry_per_month * Decimal('0.2')  # 20% servicing
            aggregated_cf['taxes'][period_idx] += -carry_per_month * Decimal('0.3')  # 30% taxes
            aggregated_cf['insurance'][period_idx] += -carry_per_month * Decimal('0.1')  # 10% insurance
            aggregated_cf['reo_holding_costs'][period_idx] += -carry_per_month * Decimal('0.4')  # 40% holding
        
        # Final period: Proceeds and liquidation fees
        final_period = min(num_periods - 1, max_periods - 1)
        if final_period > 0:
            liq_fees = proceeds * Decimal('0.06')  # 6% liquidation
            aggregated_cf['proceeds'][final_period] += proceeds
            aggregated_cf['liquidation_fees'][final_period] += -liq_fees
    
    # WHAT: Calculate net cash flow for each period
    for period_idx in range(max_periods):
        net_cf = (
            aggregated_cf['acquisition_price'][period_idx] +
            aggregated_cf['acq_costs'][period_idx] +
            aggregated_cf['servicing_fees'][period_idx] +
            aggregated_cf['taxes'][period_idx] +
            aggregated_cf['insurance'][period_idx] +
            aggregated_cf['legal_cost'][period_idx] +
            aggregated_cf['reo_holding_costs'][period_idx] +
            aggregated_cf['trashout_cost'][period_idx] +
            aggregated_cf['renovation_cost'][period_idx] +
            aggregated_cf['liquidation_fees'][period_idx] +
            aggregated_cf['proceeds'][period_idx]
        )
        aggregated_cf['net_cash_flow'][period_idx] = net_cf
    
    # WHAT: Convert Decimals to floats for JSON serialization
    for key in aggregated_cf:
        aggregated_cf[key] = [float(v) for v in aggregated_cf[key]]
    
    logger.info(f"[PooledCashFlows] Completed FAST cash flow aggregation. Max periods: {max_periods}")
    
    # WHAT: Calculate cumulative cash flow
    # WHY: Show running total of pool cash flows
    cumulative_cash_flow = []
    cumulative = 0.0
    for net_cf in aggregated_cf['net_cash_flow']:
        cumulative += net_cf
        cumulative_cash_flow.append(cumulative)
    
    # WHAT: Generate period dates based on earliest settlement date
    # WHY: All assets should align to the same timeline starting from earliest settlement
    # HOW: Generate MM/YYYY dates starting from earliest settlement date
    if earliest_settlement_date is None:
        earliest_settlement_date = date.today()
    
    period_dates = []
    for i in range(max_periods):
        period_date = earliest_settlement_date + relativedelta(months=i)
        period_dates.append(period_date.strftime('%m/%Y'))
    
    # WHAT: Generate period labels (simplified for pooled view)
    # WHY: Period labels help users understand timeline phases
    period_labels = []
    for i in range(max_periods):
        if i == 0:
            period_labels.append('Settlement')
        elif i == max_periods - 1:
            period_labels.append('Sale')
        else:
            # WHAT: Use generic "Active" label for middle periods in pooled view
            # WHY: Assets may have different phase boundaries, so we use generic labels
            period_labels.append('Active')
    
    # WHAT: Calculate totals for validation
    totals = {
        'total_acquisition_price': sum(aggregated_cf['acquisition_price']),
        'total_acq_costs': sum(aggregated_cf['acq_costs']),
        'total_servicing_fees': sum(aggregated_cf['servicing_fees']),
        'total_taxes': sum(aggregated_cf['taxes']),
        'total_insurance': sum(aggregated_cf['insurance']),
        'total_legal_cost': sum(aggregated_cf['legal_cost']),
        'total_reo_holding_costs': sum(aggregated_cf['reo_holding_costs']),
        'total_trashout_cost': sum(aggregated_cf['trashout_cost']),
        'total_renovation_cost': sum(aggregated_cf['renovation_cost']),
        'total_liquidation_fees': sum(aggregated_cf['liquidation_fees']),
        'total_proceeds': sum(aggregated_cf['proceeds']),
        'total_net_cash_flow': sum(aggregated_cf['net_cash_flow']),
        'final_cumulative': cumulative_cash_flow[-1] if cumulative_cash_flow else 0.0,
        'asset_count': len(assets),
    }
    
    # WHAT: Return aggregated cash flow series
    return {
        'scenario': scenario,
        'model_type': 'reo_sale',
        'total_months': max_periods - 1 if max_periods > 0 else 0,  # -1 because period 0 counts as month 0
        'periods': list(range(max_periods)),
        'period_labels': period_labels,
        'period_dates': period_dates,
        'settlement_date': earliest_settlement_date.isoformat() if earliest_settlement_date else None,
        'cash_flows': aggregated_cf,
        'cumulative_cash_flow': cumulative_cash_flow,
        'totals': totals,
    }
