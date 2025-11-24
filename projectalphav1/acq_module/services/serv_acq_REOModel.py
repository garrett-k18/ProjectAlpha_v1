"""
acq_module.services.serv_acq_REOModel

What: Service layer for REO sale model calculations and backend sums.
Why: Centralize REO model calculations for frontend display, following service pattern.
Where: projectalphav1/acq_module/services/serv_acq_REOModel.py
How: Uses existing REO timeline logic and calculates full timelines including foreclosure and REO marketing.
"""
from __future__ import annotations

from typing import Optional, Dict, Any
from datetime import date
from decimal import Decimal

from acq_module.models.model_acq_seller import SellerRawData
from acq_module.models.model_acq_assumptions import TradeLevelAssumption, LoanLevelAssumption
from acq_module.logic.logi_acq_durationAssumptions import get_asset_fc_timeline
from acq_module.logic.logi_acq_expenseAssumptions import monthly_tax_for_asset, monthly_insurance_for_asset, acq_broker_fee, acq_fee_other
from acq_module.logic.logi_acq__proceedAssumptions import reo_asis_proceeds, reo_arv_proceeds
from acq_module.logic.logi_acq_purchasePrice import purchase_price, purchase_price_metrics
from acq_module.logic.logi_acq_outcomespecific import fcoutcomeLogic
from core.models.model_co_geoAssumptions import StateReference
from core.models.model_co_assumptions import Servicer, HOAAssumption, PropertyTypeAssumption, SquareFootageAssumption
from core.models.model_co_valuations import Valuation


def get_reo_timeline_sums(asset_hub_id: int, reference_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Get REO sale timeline sums for an asset.
    
    What: Calculates duration fields for REO sale scenario:
    - Servicing Transfer: Duration from settlement_date to servicing_transfer_date (in months)
    - Foreclosure: Sum of all FCStatus durations from FCTimelines (in days, converted to months)
    - REO Marketing: Duration to market and sell the REO property (in months, from StateReference)
    
    Why: Provide simplified timeline data for REO model card display.
    Where: Called by API views to serve frontend REOSaleModelCard component.
    How: 
    - Gets servicing transfer duration from TradeLevelAssumption
    - Gets FC timeline totals from existing get_asset_fc_timeline function
    - Gets REO marketing duration from StateReference for the asset's state
    - Converts days to months and rounds to nearest whole integer
    
    Args:
        asset_hub_id: Primary key of AssetIdHub
        reference_date: Date to calculate servicing transfer duration to (defaults to today)
    
    Returns:
        Dict with keys:
        - servicing_transfer_months: Optional[int] - Months from settlement to servicing transfer
        - foreclosure_months: Optional[int] - Total FC duration converted to months
        - reo_marketing_months: Optional[int] - REO marketing duration from state assumptions
        - total_timeline_months: Optional[int] - Sum of all timeline phases
    """
    if reference_date is None:
        reference_date = date.today()
    
    # WHAT: Get asset's SellerRawData to access trade and state
    # WHY: Need trade for servicing transfer date, state for REO marketing duration
    raw_data = SellerRawData.objects.filter(asset_hub_id=asset_hub_id).select_related('trade').first()
    
    # WHAT: PERFORMANCE - Fetch LoanLevelAssumption ONCE to avoid N+1 queries
    # WHY: This function was querying it 3 separate times (FC, renovation, marketing overrides)
    loan_assumption = LoanLevelAssumption.objects.filter(asset_hub_id=asset_hub_id).first()
    
    # WHAT: PERFORMANCE - Fetch StateReference ONCE to avoid duplicate queries
    # WHY: This function was querying it 2 separate times (rehab duration, marketing duration)
    state_ref = None
    if raw_data and raw_data.state:
        state_ref = StateReference.objects.filter(state_code=raw_data.state).first()
    
    # WHAT: Default to 0 instead of None so calculations still work
    # WHY: Returning None breaks frontend calculations; 0 is a valid "no duration" value
    servicing_transfer_months = 0
    
    if raw_data and raw_data.trade:
        # WHAT: Get TradeLevelAssumption for this trade
        # WHY: Contains servicing_transfer_date field with fallback logic
        trade_assumption = TradeLevelAssumption.objects.filter(trade=raw_data.trade).select_related('servicer').first()
        
        if trade_assumption:
            # WHAT: Use effective_servicing_transfer_date property
            transfer_date = trade_assumption.effective_servicing_transfer_date
            
            if transfer_date and trade_assumption.settlement_date:
                # WHAT: Calculate months between settlement_date and servicing_transfer_date
                days_diff = (transfer_date - trade_assumption.settlement_date).days
                
                if days_diff >= 0:
                    servicing_transfer_months = round(days_diff / 30.44)
                else:
                    servicing_transfer_months = 1
            elif not trade_assumption.settlement_date and trade_assumption.servicer:
                # WHAT: If no settlement date but servicer exists, use servicer's default duration
                # WHY: Still provide a value for calculations
                if trade_assumption.servicer.servicing_transfer_duration:
                    servicing_transfer_months = trade_assumption.servicer.servicing_transfer_duration
    
    # WHAT: Get FC timeline data using existing function
    # WHY: REO scenario includes full foreclosure process
    fc_timeline_data = get_asset_fc_timeline(asset_hub_id)
    
    foreclosure_days = fc_timeline_data.get('totalDurationDays')
    foreclosure_months = None
    foreclosure_months_base = None
    reo_fc_override_months = 0
    
    if foreclosure_days is not None and foreclosure_days > 0:
        # WHAT: Convert FC days to months, round to nearest integer
        base_foreclosure_months = round(foreclosure_days / 30.44)
        foreclosure_months_base = base_foreclosure_months
        
        # WHAT: Check for user override in LoanLevelAssumption (REO-specific FC override)
        # WHY: Allow users to adjust FC duration for REO model independently
        if loan_assumption and loan_assumption.reo_fc_duration_override_months is not None:
            reo_fc_override_months = loan_assumption.reo_fc_duration_override_months
        
        # WHAT: Apply override to base foreclosure months
        foreclosure_months = base_foreclosure_months + reo_fc_override_months
        if foreclosure_months < 0:
            foreclosure_months = 0
    
    # WHAT: Get REO renovation duration from state assumptions
    # WHY: REO assets may need renovation/rehab before marketing
    reo_renovation_months = None
    reo_renovation_months_base = None
    reo_renovation_override_months = 0
    
    if state_ref:
        try:
            if state_ref.rehab_duration is not None:
                base_renovation_months = state_ref.rehab_duration
                reo_renovation_months_base = base_renovation_months
                
                # WHAT: Check for user override for renovation duration (using cached loan_assumption)
                if loan_assumption and loan_assumption.reo_renovation_override_months is not None:
                    reo_renovation_override_months = loan_assumption.reo_renovation_override_months
                
                # WHAT: Apply override to base renovation months
                reo_renovation_months = base_renovation_months + reo_renovation_override_months
                if reo_renovation_months < 0:
                    reo_renovation_months = 0
        except Exception as e:
            print(f"ERROR getting REO renovation duration for state {raw_data.state}: {str(e)}")
    
    # WHAT: If no state reference, default to 0 renovation months
    if reo_renovation_months is None:
        reo_renovation_months_base = 0
        reo_renovation_months = 0
    
    # WHAT: Get REO marketing duration from state assumptions
    # WHY: Each state has different typical REO marketing durations
    reo_marketing_months = None
    reo_marketing_months_base = None
    reo_marketing_override_months = 0
    
    if state_ref:
        try:
            if state_ref.reo_marketing_duration:
                base_marketing_months = state_ref.reo_marketing_duration
                reo_marketing_months_base = base_marketing_months
                
                # WHAT: Check for user override for marketing duration (using cached loan_assumption)
                if loan_assumption and loan_assumption.reo_marketing_override_months is not None:
                    reo_marketing_override_months = loan_assumption.reo_marketing_override_months
                
                # WHAT: Apply override to base marketing months
                reo_marketing_months = base_marketing_months + reo_marketing_override_months
                if reo_marketing_months < 0:
                    reo_marketing_months = 0
        except Exception as e:
            print(f"ERROR getting REO marketing duration for state {raw_data.state}: {str(e)}")
    
    # WHAT: Calculate total timeline
    # WHY: Need to show complete duration from acquisition to sale
    total_timeline_months = None
    if all(x is not None for x in [servicing_transfer_months, foreclosure_months, reo_renovation_months, reo_marketing_months]):
        total_timeline_months = servicing_transfer_months + foreclosure_months + reo_renovation_months + reo_marketing_months
    
    # WHAT: Get expected recovery (REO sale proceeds)
    # WHY: Display estimated proceeds from REO sale
    expected_recovery = None
    try:
        proceeds = reo_asis_proceeds(asset_hub_id)
        if proceeds is not None:
            expected_recovery = float(proceeds)
    except Exception as e:
        print(f"ERROR calculating REO proceeds: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # WHAT: Get acquisition price for this asset
    # WHY: Need to display and allow editing in frontend
    acq_price = None
    try:
        price = purchase_price(asset_hub_id)
        if price is not None:
            acq_price = float(price)
    except Exception as e:
        print(f"ERROR calculating acquisition price: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return {
        'servicing_transfer_months': servicing_transfer_months,
        'foreclosure_months': foreclosure_months,
        'foreclosure_months_base': foreclosure_months_base,
        'reo_fc_duration_override_months': reo_fc_override_months if foreclosure_months_base is not None else None,
        'reo_renovation_months': reo_renovation_months,
        'reo_renovation_months_base': reo_renovation_months_base,
        'reo_renovation_override_months': reo_renovation_override_months if reo_renovation_months_base is not None else None,
        'reo_marketing_months': reo_marketing_months,
        'reo_marketing_months_base': reo_marketing_months_base,
        'reo_marketing_override_months': reo_marketing_override_months if reo_marketing_months_base is not None else None,
        'total_timeline_months': total_timeline_months,
        'expected_recovery': expected_recovery,
        'acquisition_price': acq_price
    }


# HYBRID CALCULATION ARCHITECTURE - REO Expense Values
# 
# PURPOSE: Provides both authoritative backend calculations AND monthly rates for instant frontend recalculation
# PATTERN: Industry standard used by Bloomberg Terminal, Salesforce, Banking platforms
# 
# BACKEND RESPONSIBILITIES:
# - Complex business logic and validation
# - Authoritative calculations for audit/compliance  
# - Database queries and data aggregation
# - Monthly rate calculations from property data
# 
# FRONTEND RESPONSIBILITIES:
# - Instant UI feedback on duration changes (+/- buttons)
# - Real-time recalculation using monthly rates
# - User experience optimization
# 
# BENEFITS:
# - Instant UX: No 3-second waits for simple interactions
# - Backend Authority: All permanent calculations server-side
# - Reduced Load: Avoid unnecessary API calls
# - Data Consistency: Single source of truth + calculation components
# - Fallback Safety: Frontend failures don't break backend values
def get_reo_expense_values(
    asset_hub_id: int, 
    total_timeline_months: Optional[int] = None,
    servicing_transfer_months: Optional[int] = None,
    foreclosure_months: Optional[int] = None,
    reo_renovation_months: Optional[int] = None,
    reo_marketing_months: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get REO sale expense values for an asset from models.
    
    What: Fetches expense values from backend models/logic for REO sale scenario:
    - Servicing Fees: Calculated during servicing transfer and foreclosure phases
    - Taxes: Monthly tax multiplied by total timeline months
    - Insurance: Monthly insurance multiplied by total timeline months
    - Legal Cost: From StateReference.fc_legal_fees_avg
    - REO Holding Costs: Monthly costs (HOA + Utilities + Property Preservation) during REO period (eviction + renovation + marketing)
    - Listing Commission: Realtor commission on REO sale (typically 6% of proceeds)
    - Closing Costs: Transaction costs for REO sale (typically 2-3% of proceeds)
    
    Why: Provide expense values from models for REO scenario.
    Where: Called by API views to serve frontend REOSaleModelCard component.
    How:
    - Gets asset's state from SellerRawData
    - Gets servicer from TradeLevelAssumption
    - Calculates expenses using existing functions
    - Adds REO-specific costs (holding costs, commission, closing costs)
    
    Args:
        asset_hub_id: Primary key of AssetIdHub
        total_timeline_months: Total duration in months (servicing + FC + REO marketing)
        servicing_transfer_months: Servicing transfer duration in months
        foreclosure_months: Foreclosure duration in months
        reo_marketing_months: REO marketing duration in months
    
    Returns:
        Dict with raw expense data for frontend KPI calculations:
        - Acquisition costs (broker fees, legal, due diligence, tax/title)
        - Carry costs (servicing fees, taxes, insurance, legal, REO holding, trashout, renovation)
        - Liquidation expenses (broker fees, servicer fee, AM fee)
        - Monthly rates for instant recalculation (monthly_tax, monthly_insurance, etc.)
        - Expected proceeds (As-Is and ARV)
        - Acquisition price
        
        NOTE: Total Costs, Net PL, MOIC, and Annualized ROI are NOT calculated here.
        These KPIs are calculated exclusively in the FRONTEND using instant recalculated values.
    """
    # WHAT: Initialize all expense variables
    servicing_fees = Decimal('0.0')
    taxes = Decimal('0.0')
    insurance = Decimal('0.0')
    legal_cost = Decimal('0.0')
    reo_holding_costs = Decimal('0.0')
    trashout_cost = Decimal('0.0')
    renovation_cost = Decimal('0.0')
    broker_fees = Decimal('0.0')
    servicer_liquidation_fee = Decimal('0.0')
    
    # WHAT: Get asset data with optimized queries
    # WHY: Use select_related to fetch trade and servicer in a single query to avoid N+1
    raw_data = SellerRawData.objects.filter(asset_hub_id=asset_hub_id).select_related('trade').first()
    
    if not raw_data:
        print(f"No SellerRawData found for asset_hub_id {asset_hub_id}")
        return {}
    
    # WHAT: Fetch TradeLevelAssumption ONCE and reuse throughout function
    # WHY: PERFORMANCE - Avoid querying the same data 9+ times (N+1 query problem)
    trade_assumption = None
    servicer = None
    if raw_data.trade:
        trade_assumption = TradeLevelAssumption.objects.filter(trade=raw_data.trade).select_related('servicer').first()
        if trade_assumption:
            servicer = trade_assumption.servicer
    
    # WHAT: Calculate servicing fees
    # WHY: Fees apply during servicing transfer, foreclosure, and REO phases
    if trade_assumption and servicer:
        # WHAT: Calculate servicing fees components
        # WHY: Different fees apply at different stages
        board_fee = servicer.board_fee or Decimal('0.0')
        onetwentyday_fee = servicer.onetwentyday_fee or Decimal('0.0')
        fc_fee = servicer.fc_fee or Decimal('0.0')
        reo_fee = servicer.reo_fee or Decimal('0.0')
        
        # WHAT: Calculate total REO duration (renovation + marketing)
        # WHY: REO fee applies during the entire REO period
        reo_duration_months = (reo_renovation_months or 0) + (reo_marketing_months or 0)
        
        # WHAT: Sum up servicing fees based on timeline phases
        servicing_fees = board_fee
        if servicing_transfer_months:
            servicing_fees += onetwentyday_fee * Decimal(servicing_transfer_months)
        if foreclosure_months:
            servicing_fees += fc_fee * Decimal(foreclosure_months)
        if reo_duration_months:
            servicing_fees += reo_fee * Decimal(reo_duration_months)
        
        print(f"\nServicing Fees Calculation:")
        print(f"  Board Fee: ${board_fee:,.2f}")
        print(f"  120-Day Fee ({servicing_transfer_months} months): ${onetwentyday_fee * Decimal(servicing_transfer_months if servicing_transfer_months else 0):,.2f}")
        print(f"  FC Fee ({foreclosure_months} months): ${fc_fee * Decimal(foreclosure_months if foreclosure_months else 0):,.2f}")
        print(f"  REO Fee ({reo_duration_months} months): ${reo_fee * Decimal(reo_duration_months):,.2f}")
        print(f"  Total Servicing Fees: ${servicing_fees:,.2f}")
    
    # WHAT: Calculate taxes and insurance
    # WHY: These carry costs apply throughout entire timeline
    if total_timeline_months:
        try:
            monthly_tax = monthly_tax_for_asset(asset_hub_id)
            if monthly_tax is not None:
                taxes = monthly_tax * Decimal(total_timeline_months)
                print(f"Taxes: ${monthly_tax:,.2f}/month * {total_timeline_months} months = ${taxes:,.2f}")
        except Exception as e:
            print(f"ERROR calculating taxes: {str(e)}")
        
        try:
            monthly_ins = monthly_insurance_for_asset(asset_hub_id)
            if monthly_ins is not None:
                insurance = monthly_ins * Decimal(total_timeline_months)
                print(f"Insurance: ${monthly_ins:,.2f}/month * {total_timeline_months} months = ${insurance:,.2f}")
        except Exception as e:
            print(f"ERROR calculating insurance: {str(e)}")
    
    # WHAT: Get legal costs from state reference
    if raw_data.state:
        try:
            state_ref = StateReference.objects.filter(state_code=raw_data.state).first()
            if state_ref and state_ref.fc_legal_fees_avg:
                legal_cost = state_ref.fc_legal_fees_avg
                print(f"Legal Cost (State {raw_data.state}): ${legal_cost:,.2f}")
        except Exception as e:
            print(f"ERROR getting legal costs: {str(e)}")
    
    # WHAT: Calculate REO holding costs (HOA + Utilities + Property Preservation)
    # WHY: Costs incurred during REO period while property is owned (eviction + renovation + marketing)
    # HOW: Sum of monthly HOA, utilities, and property preservation costs multiplied by REO-specific duration
    if reo_renovation_months or reo_marketing_months:
        try:
            monthly_hoa = Decimal('0.0')
            monthly_utilities = Decimal('0.0')
            monthly_property_pres = Decimal('0.0')
            
            # WHAT: Get property type and square footage from SellerRawData
            property_type = raw_data.property_type if raw_data else None
            square_feet = raw_data.sq_ft if raw_data else None
            
            print(f"\n=== REO HOLDING COSTS CALCULATION ===")
            print(f"Property Type: {property_type}, Square Feet: {square_feet}, REO Marketing Months: {reo_marketing_months}")
            
            # WHAT: Calculate monthly HOA fee
            # HOW: Lookup by property type in HOAAssumption table
            if property_type:
                try:
                    hoa_record = HOAAssumption.objects.filter(property_type__iexact=property_type).first()
                    if hoa_record:
                        monthly_hoa = hoa_record.monthly_hoa_fee
                        print(f"HOA Fee: ${monthly_hoa:,.2f}/month (from HOAAssumption table)")
                    else:
                        print(f"No HOA assumption found for property type: {property_type}")
                except Exception as e:
                    print(f"ERROR getting HOA fee: {str(e)}")
            
            # WHAT: Calculate monthly utilities and property preservation
            # HOW: Priority 1 - Use SquareFootageAssumption if square feet available (more precise)
            #      Priority 2 - Fall back to PropertyTypeAssumption
            
            # WHAT: Try square footage model first if square feet is available
            if square_feet and square_feet > 0:
                try:
                    # WHAT: Get RESIDENTIAL square footage assumptions
                    sqft_record = SquareFootageAssumption.objects.filter(
                        property_category='RESIDENTIAL',
                        is_active=True
                    ).first()
                    if sqft_record:
                        # WHAT: Calculate utilities from per-sqft rates
                        monthly_utilities = (
                            ((sqft_record.utility_electric_per_sqft or Decimal('0.0')) * Decimal(str(square_feet))) +
                            ((sqft_record.utility_gas_per_sqft or Decimal('0.0')) * Decimal(str(square_feet))) +
                            ((sqft_record.utility_water_per_sqft or Decimal('0.0')) * Decimal(str(square_feet))) +
                            ((sqft_record.utility_sewer_per_sqft or Decimal('0.0')) * Decimal(str(square_feet))) +
                            ((sqft_record.utility_trash_per_sqft or Decimal('0.0')) * Decimal(str(square_feet))) +
                            ((sqft_record.utility_other_per_sqft or Decimal('0.0')) * Decimal(str(square_feet)))
                        )
                        print(f"Utilities: ${monthly_utilities:,.2f}/month (from SquareFootageAssumption - {square_feet} sqft)")
                        
                        # WHAT: Calculate property preservation from per-sqft rates
                        monthly_property_pres = (
                            ((sqft_record.security_cost_per_sqft or Decimal('0.0')) * Decimal(str(square_feet))) +
                            ((sqft_record.landscaping_per_sqft or Decimal('0.0')) * Decimal(str(square_feet)))
                        )
                        print(f"Property Preservation: ${monthly_property_pres:,.2f}/month (from SquareFootageAssumption - {square_feet} sqft)")
                    else:
                        print(f"No active RESIDENTIAL SquareFootageAssumption found - will try PropertyTypeAssumption")
                except Exception as e:
                    print(f"ERROR using square footage model: {str(e)}")
            
            # WHAT: Fall back to property type model if no square feet or sqft model didn't work
            if (monthly_utilities == 0 or monthly_property_pres == 0) and property_type:
                try:
                    prop_type_record = PropertyTypeAssumption.objects.filter(property_type__iexact=property_type).first()
                    if prop_type_record:
                        # WHAT: Only use property type values if sqft model didn't provide them
                        if monthly_utilities == 0:
                            monthly_utilities = (
                                (prop_type_record.utility_electric_monthly or Decimal('0.0')) +
                                (prop_type_record.utility_gas_monthly or Decimal('0.0')) +
                                (prop_type_record.utility_water_monthly or Decimal('0.0')) +
                                (prop_type_record.utility_sewer_monthly or Decimal('0.0')) +
                                (prop_type_record.utility_trash_monthly or Decimal('0.0')) +
                                (prop_type_record.utility_other_monthly or Decimal('0.0'))
                            )
                            print(f"Utilities: ${monthly_utilities:,.2f}/month (from PropertyTypeAssumption table)")
                        
                        # WHAT: Only use property type values if sqft model didn't provide them
                        if monthly_property_pres == 0:
                            monthly_property_pres = (
                                (prop_type_record.security_cost_monthly or Decimal('0.0')) +
                                (prop_type_record.landscaping_monthly or Decimal('0.0'))
                            )
                            print(f"Property Preservation: ${monthly_property_pres:,.2f}/month (from PropertyTypeAssumption table)")
                    else:
                        print(f"No PropertyTypeAssumption found for property type: {property_type}")
                except Exception as e:
                    print(f"ERROR getting property type assumptions: {str(e)}")
            
            # WHAT: Calculate total monthly holding cost
            monthly_holding = monthly_hoa + monthly_utilities + monthly_property_pres
            print(f"Total Monthly Holding Cost: ${monthly_holding:,.2f} (HOA: ${monthly_hoa:,.2f} + Utilities: ${monthly_utilities:,.2f} + Prop Pres: ${monthly_property_pres:,.2f})")
            
            # TODO: Add eviction duration to REO holding period calculation
            # WHAT: Calculate REO holding duration (BOTH renovation + marketing)
            # WHY: Holding costs (HOA, utilities, property preservation) accrue during entire REO ownership
            # NOTE: Whether renovating or marketing, property still incurs HOA, utilities, maintenance costs
            reo_holding_duration = (reo_renovation_months or 0) + (reo_marketing_months or 0)
            print(f"REO Holding Duration: {reo_holding_duration} months (Renovation: {reo_renovation_months or 0} + Marketing: {reo_marketing_months or 0})")
            
            # WHAT: Multiply monthly holding cost by total REO duration (renovation + marketing)
            reo_holding_costs = monthly_holding * Decimal(reo_holding_duration)
            print(f"REO Holding Costs: ${monthly_holding:,.2f}/month * {reo_holding_duration} months = ${reo_holding_costs:,.2f}")
            print(f"=== END REO HOLDING COSTS ===\n")
            
            # WHAT: Store monthly rates for frontend recalculation (individual components)
            monthly_reo_holding = monthly_holding
            monthly_hoa_rate = monthly_hoa
            monthly_utilities_rate = monthly_utilities  
            monthly_property_pres_rate = monthly_property_pres
            
        except Exception as e:
            print(f"ERROR calculating REO holding costs: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # WHAT: Calculate trashout cost (one-time cost)
    # WHY: Cost to clear out property after foreclosure/eviction
    # HOW: Use SquareFootageAssumption if square feet available, otherwise PropertyTypeAssumption
    try:
        print(f"\n=== TRASHOUT COST CALCULATION ===")
        property_type = raw_data.property_type if raw_data else None
        square_feet = raw_data.sq_ft if raw_data else None
        
        print(f"Property Type: {property_type}, Square Feet: {square_feet}")
        
        # WHAT: Try square footage model first if square feet is available
        # HOW: Use RESIDENTIAL category for SquareFootageAssumption (independent of property_type)
        if square_feet and square_feet > 0:
            try:
                # WHAT: Get RESIDENTIAL square footage assumptions (most common)
                sqft_record = SquareFootageAssumption.objects.filter(
                    property_category='RESIDENTIAL',
                    is_active=True
                ).first()
                if sqft_record and sqft_record.trashout_per_sqft:
                    trashout_cost = Decimal(str(square_feet)) * sqft_record.trashout_per_sqft
                    print(f"Trashout Cost (Square Foot Model - RESIDENTIAL): {square_feet} sqft * ${sqft_record.trashout_per_sqft:.4f}/sqft = ${trashout_cost:,.2f}")
                else:
                    print(f"No active RESIDENTIAL SquareFootageAssumption with trashout_per_sqft found")
            except Exception as e:
                print(f"ERROR using square footage model: {str(e)}")
        
        # WHAT: Fall back to property type assumption if no square feet or sqft model didn't work
        if trashout_cost == 0 and property_type:
            try:
                prop_type_record = PropertyTypeAssumption.objects.filter(property_type__iexact=property_type).first()
                if prop_type_record and prop_type_record.trashout_cost:
                    trashout_cost = prop_type_record.trashout_cost
                    print(f"Trashout Cost (Property Type Model): ${trashout_cost:,.2f}")
                else:
                    print(f"No PropertyTypeAssumption with trashout_cost found for property type: {property_type}")
            except Exception as e:
                print(f"ERROR using property type model: {str(e)}")
        
        print(f"Final Trashout Cost: ${trashout_cost:,.2f}")
        print(f"=== END TRASHOUT COST ===\n")
        
    except Exception as e:
        print(f"ERROR calculating trashout cost: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # WHAT: Calculate renovation cost (for Rehab scenario)
    # WHY: Cost to renovate property before REO sale
    # HOW: Priority 1 - Internal UW rehab estimate, 2 - Square footage model, 3 - Property type model
    try:
        print(f"\n=== RENOVATION COST CALCULATION ===")
        property_type = raw_data.property_type if raw_data else None
        square_feet = raw_data.sq_ft if raw_data else None
        
        print(f"Property Type: {property_type}, Square Feet: {square_feet}")
        
        # WHAT: Priority 1 - Check for Internal Initial UW valuation rehab estimate
        # WHY: Most accurate if underwriter provided specific rehab estimate
        try:
            internal_uw_val = Valuation.objects.filter(
                asset_hub_id=asset_hub_id,
                source='internalInitialUW'
            ).only('rehab_est_total').first()
            
            print(f"Internal UW Valuation found: {internal_uw_val is not None}")
            if internal_uw_val:
                print(f"rehab_est_total value: {internal_uw_val.rehab_est_total}")
            
            if internal_uw_val and internal_uw_val.rehab_est_total:
                renovation_cost = Decimal(str(internal_uw_val.rehab_est_total))
                print(f"✓ Renovation Cost (Internal UW Estimate): ${renovation_cost:,.2f}")
            else:
                print(f"No Internal UW rehab estimate found - will try square footage model")
        except Exception as e:
            print(f"ERROR getting Internal UW rehab estimate: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # WHAT: Priority 2 - Try square footage model if no UW estimate and square feet available
        if renovation_cost == 0 and square_feet and square_feet > 0:
            try:
                sqft_record = SquareFootageAssumption.objects.filter(
                    property_category='RESIDENTIAL',
                    is_active=True
                ).first()
                if sqft_record and sqft_record.renovation_per_sqft:
                    renovation_cost = Decimal(str(square_feet)) * sqft_record.renovation_per_sqft
                    print(f"Renovation Cost (Square Foot Model - RESIDENTIAL): {square_feet} sqft * ${sqft_record.renovation_per_sqft:.4f}/sqft = ${renovation_cost:,.2f}")
                else:
                    print(f"No active RESIDENTIAL SquareFootageAssumption with renovation_per_sqft found")
            except Exception as e:
                print(f"ERROR using square footage model: {str(e)}")
        
        # WHAT: Priority 3 - Fall back to property type assumption
        if renovation_cost == 0 and property_type:
            try:
                prop_type_record = PropertyTypeAssumption.objects.filter(property_type__iexact=property_type).first()
                if prop_type_record and prop_type_record.renovation_cost:
                    renovation_cost = prop_type_record.renovation_cost
                    print(f"Renovation Cost (Property Type Model): ${renovation_cost:,.2f}")
                else:
                    print(f"No PropertyTypeAssumption with renovation_cost found for property type: {property_type}")
            except Exception as e:
                print(f"ERROR using property type model: {str(e)}")
        
        print(f"Final Renovation Cost: ${renovation_cost:,.2f}")
        print(f"=== END RENOVATION COST ===\n")
        
    except Exception as e:
        print(f"ERROR calculating renovation cost: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # WHAT: Get REO sale proceeds (As-Is)
    # WHY: Expected proceeds = Internal UW As-Is value (priority 1) or Seller As-Is value (priority 2)
    expected_proceeds_asis = Decimal('0.0')
    try:
        proceeds = reo_asis_proceeds(asset_hub_id)
        if proceeds is not None:
            expected_proceeds_asis = proceeds
            print(f"Expected Proceeds (REO As-Is): ${expected_proceeds_asis:,.2f}")
    except Exception as e:
        print(f"ERROR calculating REO As-Is proceeds: {str(e)}")
    
    # WHAT: Get REO sale proceeds (ARV - After Repair Value)
    # WHY: Expected proceeds for Rehab scenario = Internal UW ARV (priority 1) or Seller ARV (priority 2)
    expected_proceeds_arv = Decimal('0.0')
    try:
        proceeds_arv = reo_arv_proceeds(asset_hub_id)
        if proceeds_arv is not None:
            expected_proceeds_arv = proceeds_arv
            print(f"Expected Proceeds (REO ARV): ${expected_proceeds_arv:,.2f}")
    except Exception as e:
        print(f"ERROR calculating REO ARV proceeds: {str(e)}")
    
    # WHAT: Use As-Is proceeds as default (frontend will toggle between As-Is and ARV)
    expected_proceeds = expected_proceeds_asis
    
    # WHAT: Calculate broker fees for As-Is scenario
    # WHY: Broker fees for REO sale calculated as liq_broker_cc_pct from trade assumptions × expected proceeds
    # HOW: Use liq_broker_cc_pct from TradeLevelAssumption (already fetched), multiply by As-Is proceeds
    broker_fees = Decimal('0.0')
    if trade_assumption and expected_proceeds > 0:
        try:
            if trade_assumption.liq_broker_cc_pct:
                broker_fee_pct = trade_assumption.liq_broker_cc_pct
                broker_fees = (broker_fee_pct * expected_proceeds).quantize(Decimal('0.01'))
                print(f"Broker Fees (As-Is): {broker_fee_pct} × ${expected_proceeds:,.2f} = ${broker_fees:,.2f}")
        except Exception as e:
            print(f"ERROR calculating broker fees: {str(e)}")
    
    # WHAT: Calculate servicer liquidation fee
    # WHY: Servicer fee for completing the REO sale
    # HOW: Use MAX(flat fee, percentage fee × proceeds) - same logic as FC model
    servicer_liquidation_fee = Decimal('0.0')
    if trade_assumption and servicer:
        try:
                
                # WHAT: Get flat fee option
                flat_fee = servicer.liqfee_flat or Decimal('0.0')
                
                # WHAT: Get percentage fee option
                pct_fee = Decimal('0.0')
                if servicer.liqfee_pct and expected_proceeds > 0:
                    pct_fee = (servicer.liqfee_pct * expected_proceeds).quantize(Decimal('0.01'))
                
                # WHAT: Take the maximum of the two options
                servicer_liquidation_fee = max(flat_fee, pct_fee)
                print(f"Servicer Liquidation Fee: MAX(${flat_fee:,.2f}, ${pct_fee:,.2f}) = ${servicer_liquidation_fee:,.2f}")
        except Exception as e:
            print(f"ERROR calculating servicer liquidation fee: {str(e)}")
    
    # WHAT: Calculate acquisition costs
    # WHY: One-time costs when acquiring the asset
    acq_broker_fees = Decimal('0.0')
    acq_other_fees = Decimal('0.0')
    acq_legal = Decimal('0.0')
    acq_dd = Decimal('0.0')
    acq_tax_title = Decimal('0.0')
    
    # WHAT: Get acquisition price for fee calculations
    acquisition_price = None
    try:
        acq_price = purchase_price(asset_hub_id)
        if acq_price is not None:
            acquisition_price = acq_price
            
            # WHAT: Calculate acquisition broker and other fees as % of purchase price
            acq_broker_fees = acq_broker_fee(asset_hub_id)
            acq_other_fees = acq_fee_other(asset_hub_id)
    except Exception as e:
        print(f"ERROR calculating acquisition price: {str(e)}")
    
    # WHAT: Get flat acquisition costs and percentages from trade
    # WHY: Frontend needs percentages to recalculate fees when acquisition price changes
    # HOW: Use liq_broker_cc_pct (percentage) and acq_other_costs (percentage) from trade assumptions
    acq_broker_fee_pct = Decimal('0.0')
    acq_other_fee_pct = Decimal('0.0')
    if trade_assumption:
        acq_legal = trade_assumption.acq_legal_cost or Decimal('0.0')
        acq_dd = trade_assumption.acq_dd_cost or Decimal('0.0')
        acq_tax_title = trade_assumption.acq_tax_title_cost or Decimal('0.0')
        # WHAT: Store percentages for frontend display
        # WHY: Frontend may need to show the percentage
        acq_broker_fee_pct = trade_assumption.acq_broker_fees or Decimal('0.0')
        acq_other_fee_pct = trade_assumption.acq_other_costs or Decimal('0.0')
    
    # WHAT: Calculate AM liquidation fee for As-Is scenario
    # WHY: Asset manager's fee at REO liquidation
    # HOW: Straight percentage calculation using liq_am_fee_pct from trade assumptions × expected proceeds
    am_liquidation_fee = Decimal('0.0')
    if trade_assumption and expected_proceeds > 0:
        try:
            if trade_assumption.liq_am_fee_pct:
                # WHAT: Simple percentage calculation (no MAX, no flat fee)
                # WHY: AM fee is always a percentage of exit proceeds
                am_fee_pct = trade_assumption.liq_am_fee_pct
                am_liquidation_fee = (am_fee_pct * expected_proceeds).quantize(Decimal('0.01'))
                print(f"AM Liquidation Fee (As-Is): {am_fee_pct} × ${expected_proceeds:,.2f} = ${am_liquidation_fee:,.2f}")
        except Exception as e:
            print(f"ERROR calculating AM liquidation fee: {str(e)}")
    
    # WHAT: Calculate fees for Rehab scenario (based on ARV proceeds)
    # WHY: Liquidation fees in Rehab are based on higher ARV proceeds, not As-Is
    # HOW: Use same liq_broker_cc_pct but multiply by ARV proceeds instead
    broker_fees_arv = Decimal('0.0')
    servicer_liquidation_fee_arv = Decimal('0.0')
    am_liquidation_fee_arv = Decimal('0.0')
    
    if expected_proceeds_arv > 0:
        # WHAT: Recalculate broker fees for ARV
        # WHY: Same liq_broker_cc_pct percentage but applied to higher ARV proceeds
        # HOW: Use liq_broker_cc_pct from TradeLevelAssumption (already fetched) × ARV proceeds
        if trade_assumption:
            try:
                if trade_assumption.liq_broker_cc_pct:
                    broker_fee_pct = trade_assumption.liq_broker_cc_pct
                    broker_fees_arv = (broker_fee_pct * expected_proceeds_arv).quantize(Decimal('0.01'))
                    print(f"Broker Fees (ARV): {broker_fee_pct} × ${expected_proceeds_arv:,.2f} = ${broker_fees_arv:,.2f}")
            except Exception as e:
                print(f"ERROR calculating ARV broker fees: {str(e)}")
        
        # WHAT: Recalculate servicer liquidation fee for ARV
        if trade_assumption and servicer:
            try:
                flat_fee = servicer.liqfee_flat or Decimal('0.0')
                pct_fee = (servicer.liqfee_pct * expected_proceeds_arv).quantize(Decimal('0.01')) if servicer.liqfee_pct else Decimal('0.0')
                servicer_liquidation_fee_arv = max(flat_fee, pct_fee)
                print(f"Servicer Liquidation Fee ARV: MAX(${flat_fee:,.2f}, ${pct_fee:,.2f}) = ${servicer_liquidation_fee_arv:,.2f}")
            except Exception as e:
                print(f"ERROR calculating ARV servicer liquidation fee: {str(e)}")
        
        # WHAT: Recalculate AM liquidation fee for ARV
        # WHY: Same liq_am_fee_pct percentage but applied to higher ARV proceeds
        # HOW: Simple percentage calculation using liq_am_fee_pct (already fetched) × ARV proceeds
        if trade_assumption:
            try:
                if trade_assumption.liq_am_fee_pct:
                    # WHAT: Simple percentage calculation (no MAX, no flat fee)
                    am_fee_pct = trade_assumption.liq_am_fee_pct
                    am_liquidation_fee_arv = (am_fee_pct * expected_proceeds_arv).quantize(Decimal('0.01'))
                    print(f"AM Liquidation Fee (ARV): {am_fee_pct} × ${expected_proceeds_arv:,.2f} = ${am_liquidation_fee_arv:,.2f}")
            except Exception as e:
                print(f"ERROR calculating ARV AM liquidation fee: {str(e)}")
    
    # WHAT: Backend does NOT calculate Total Costs, Net PL, MOIC, or Annualized ROI
    # WHY: These KPIs are calculated exclusively in FRONTEND using instant recalculated values
    # NOTE: Frontend has real-time carry costs (taxes, insurance, servicing, REO holding) that backend doesn't have
    # RESULT: Backend only provides raw expense data, frontend calculates all KPIs
    print(f"\n=== BACKEND DOES NOT CALCULATE KPIs ===")
    print(f"Total Costs, Net PL, MOIC, and Annualized ROI are calculated in frontend only")
    print(f"Backend provides raw data: acquisition costs, carry costs, liquidation expenses")
    print(f"Frontend recalculates carry costs instantly and computes all KPIs")
    print(f"=== END BACKEND NOTE ===")
    
    # WHAT: Get purchase price metrics (ratios as percentages)
    price_metrics = {}
    base_values = {
        'base_currentBalance': None,
        'base_totalDebt': None,
        'base_sellerAsIs': None,
        'base_internalUWAsIs': None
    }
    try:
        price_metrics = purchase_price_metrics(asset_hub_id)
        
        if raw_data:
            base_values['base_currentBalance'] = float(raw_data.current_balance) if raw_data.current_balance else None
            base_values['base_totalDebt'] = float(raw_data.total_debt) if raw_data.total_debt else None
            base_values['base_sellerAsIs'] = float(raw_data.seller_asis_value) if raw_data.seller_asis_value else None
            
            # WHAT: Valuation is already imported at top of file
            try:
                internal_val = Valuation.objects.filter(
                    asset_hub_id=asset_hub_id, 
                    source='INTERNAL_INITIAL_UW'
                ).only('asis_value').first()
                if internal_val and internal_val.asis_value:
                    base_values['base_internalUWAsIs'] = float(internal_val.asis_value)
            except Exception:
                pass
    except Exception as e:
        print(f"ERROR calculating purchase price metrics: {str(e)}")
    
    # WHAT: Return raw expense data for frontend calculations
    # WHY: Frontend calculates ALL KPIs using instant recalculated carry costs
    # BACKEND PROVIDES: Raw expense data, monthly rates for recalculation, static costs
    # FRONTEND CALCULATES: Total Costs, Net PL, MOIC, Annualized ROI, Total Duration
    # PATTERN: Hybrid calculation architecture - backend authority + frontend responsiveness
    return {
        # WHAT: Acquisition Costs (one-time costs when acquiring asset)
        'acq_broker_fees': float(acq_broker_fees) if acq_broker_fees is not None else None,
        'acq_other_fees': float(acq_other_fees) if acq_other_fees is not None else None,
        'acq_legal': float(acq_legal) if acq_legal is not None else None,
        'acq_dd': float(acq_dd) if acq_dd is not None else None,
        'acq_tax_title': float(acq_tax_title) if acq_tax_title is not None else None,
        # WHAT: Acquisition fee percentages for frontend live calculation
        'acq_broker_fee_pct': float(acq_broker_fee_pct) if acq_broker_fee_pct is not None else None,
        'acq_other_fee_pct': float(acq_other_fee_pct) if acq_other_fee_pct is not None else None,
        # WHAT: Carry Costs (ongoing expenses during entire timeline)
        'servicing_fees': float(servicing_fees) if servicing_fees is not None else None,
        'taxes': float(taxes) if taxes is not None else None,
        'insurance': float(insurance) if insurance is not None else None,
        'legal_cost': float(legal_cost) if legal_cost is not None else None,
        'reo_holding_costs': float(reo_holding_costs) if reo_holding_costs is not None else None,
        'trashout_cost': float(trashout_cost) if trashout_cost is not None else None,
        'renovation_cost': float(renovation_cost) if renovation_cost is not None else None,
        # WHAT: Hybrid Calculation Architecture - Monthly rates and fee components for frontend recalculation
        # WHY: Industry best practice - Backend provides authoritative calculations + components for instant frontend updates
        # HOW: When user changes duration via +/- buttons, frontend recalculates instantly using these rates
        # PATTERN: Similar to Bloomberg Terminal, Salesforce calculators, banking platforms
        # BENEFITS: Instant UX + Backend authority + Audit compliance + Reduced server load
        'board_fee': float(board_fee) if 'board_fee' in locals() and board_fee is not None else None,
        'onetwentyday_fee': float(onetwentyday_fee) if 'onetwentyday_fee' in locals() and onetwentyday_fee is not None else None,
        'fc_fee': float(fc_fee) if 'fc_fee' in locals() and fc_fee is not None else None,
        'reo_fee': float(reo_fee) if 'reo_fee' in locals() and reo_fee is not None else None,
        # WHAT: Monthly tax and insurance rates for instant frontend recalculation
        'monthly_tax': float(monthly_tax) if 'monthly_tax' in locals() and monthly_tax is not None else None,
        'monthly_insurance': float(monthly_ins) if 'monthly_ins' in locals() and monthly_ins is not None else None,
        # WHAT: Monthly REO holding cost rates for REO Marketing duration recalculation (individual components)
        'monthly_reo_holding': float(monthly_reo_holding) if 'monthly_reo_holding' in locals() and monthly_reo_holding is not None else None,
        'monthly_hoa': float(monthly_hoa_rate) if 'monthly_hoa_rate' in locals() and monthly_hoa_rate is not None else None,
        'monthly_utilities': float(monthly_utilities_rate) if 'monthly_utilities_rate' in locals() and monthly_utilities_rate is not None else None,
        'monthly_property_preservation': float(monthly_property_pres_rate) if 'monthly_property_pres_rate' in locals() and monthly_property_pres_rate is not None else None,
        # WHAT: Liquidation Expenses (costs incurred at REO sale) - As-Is values
        'broker_fees': float(broker_fees) if broker_fees is not None else None,
        'servicer_liquidation_fee': float(servicer_liquidation_fee) if servicer_liquidation_fee is not None else None,
        'am_liquidation_fee': float(am_liquidation_fee) if am_liquidation_fee is not None else None,
        # WHAT: Liquidation Expenses - Rehab/ARV values
        'broker_fees_arv': float(broker_fees_arv) if broker_fees_arv is not None else None,
        'servicer_liquidation_fee_arv': float(servicer_liquidation_fee_arv) if servicer_liquidation_fee_arv is not None else None,
        'am_liquidation_fee_arv': float(am_liquidation_fee_arv) if am_liquidation_fee_arv is not None else None,
        # WHAT: KPIs NOT calculated in backend - all frontend-only using instant values
        # NOTE: Total Costs, Net PL, MOIC, Annualized ROI calculated in frontend with real-time carry costs
        'total_costs': None,  # Frontend-only - calculated using instant recalculated carry costs
        'total_costs_asis': None,  # Frontend-only - calculated using instant recalculated carry costs
        'total_costs_rehab': None,  # Frontend-only - calculated using instant recalculated carry costs
        'net_pl_asis': None,  # Frontend-only - calculated using instant total costs
        'net_pl_rehab': None,  # Frontend-only - calculated using instant total costs
        'moic_asis': None,  # Frontend-only - calculated using instant total costs
        'moic_rehab': None,  # Frontend-only - calculated using instant total costs
        'annualized_roi_asis': None,  # Frontend-only - calculated using instant total costs
        'annualized_roi_rehab': None,  # Frontend-only - calculated using instant total costs
        # WHAT: Expected proceeds for both scenarios
        'expected_recovery': float(expected_proceeds) if expected_proceeds is not None else None,
        'expected_proceeds_asis': float(expected_proceeds_asis) if expected_proceeds_asis is not None else None,
        'expected_proceeds_arv': float(expected_proceeds_arv) if expected_proceeds_arv is not None else None,
        'acquisition_price': float(acquisition_price) if acquisition_price is not None else None,
        # WHAT: Legacy fields for backward compatibility - all frontend-only now
        'net_pl': None,  # Frontend-only - calculated using instant total costs
        'moic': None,  # Frontend-only - calculated using instant total costs
        'annualized_roi': None,  # Frontend-only - calculated using instant total costs
        # WHAT: Purchase price metrics (ratios as percentages)
        'purchase_of_currentBalance': float(price_metrics.get('purchase_of_currentBalance')) if price_metrics.get('purchase_of_currentBalance') is not None else None,
        'purchase_of_totalDebt': float(price_metrics.get('purchase_of_totalDebt')) if price_metrics.get('purchase_of_totalDebt') is not None else None,
        'purchase_of_sellerAsIs': float(price_metrics.get('purchase_of_sellerAsIs')) if price_metrics.get('purchase_of_sellerAsIs') is not None else None,
        'purchase_of_internalUWAsIs': float(price_metrics.get('purchase_of_internalUWAsIs')) if price_metrics.get('purchase_of_internalUWAsIs') is not None else None,
        # WHAT: Base values for live metric calculation on frontend
        'base_currentBalance': base_values['base_currentBalance'],
        'base_totalDebt': base_values['base_totalDebt'],
        'base_sellerAsIs': base_values['base_sellerAsIs'],
        'base_internalUWAsIs': base_values['base_internalUWAsIs']
    }

