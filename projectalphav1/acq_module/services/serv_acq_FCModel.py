"""
acq_module.services.serv_acq_FCModel

What: Service layer for foreclosure model calculations and backend sums.
Why: Centralize FC model calculations for frontend display, following service pattern.
Where: projectalphav1/acq_module/services/serv_acq_FCModel.py
How: Uses existing FC timeline logic and calculates servicing transfer duration.
"""
from __future__ import annotations

from typing import Optional, Dict, Any
from datetime import date
from decimal import Decimal

from acq_module.models.model_acq_seller import SellerRawData
from acq_module.models.model_acq_assumptions import TradeLevelAssumption, LoanLevelAssumption
from acq_module.logic.logi_acq_durationAssumptions import get_asset_fc_timeline
from acq_module.logic.logi_acq_expenseAssumptions import monthly_tax_for_asset, monthly_insurance_for_asset, acq_broker_fee, acq_fee_other
from acq_module.logic.logi_acq__proceedAssumptions import fc_sale_proceeds
from acq_module.logic.logi_acq_purchasePrice import purchase_price, purchase_price_metrics
from acq_module.logic.logi_acq_outcomespecific import fcoutcomeLogic
from core.models.model_co_geoAssumptions import StateReference
from core.models.model_co_assumptions import Servicer


def get_fc_timeline_sums(asset_hub_id: int, reference_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Get foreclosure timeline sums for an asset.
    
    What: Calculates two main duration fields:
    - Servicing Transfer: Duration from settlement_date to servicing_transfer_date (in months, rounded to whole integer)
    - Foreclosure: Sum of all FCStatus durations from FCTimelines (in days, converted to months, rounded to whole integer)
    
    Why: Provide simplified timeline data for FC model card display.
    Where: Called by API views to serve frontend ForeclosureModelCard component.
    How: 
    - Gets settlement_date and servicing_transfer_date from TradeLevelAssumption linked via SellerRawData.trade
    - Calculates servicing_transfer_months as difference between settlement_date and servicing_transfer_date
    - Uses effective_servicing_transfer_date property which defaults to settlement_date + 30 days if not set
    - Gets FC timeline totals from existing get_asset_fc_timeline function
    - Converts days to months and rounds to nearest whole integer for both values
    
    Args:
        asset_hub_id: Primary key of AssetIdHub
        reference_date: Date to calculate servicing transfer duration to (defaults to today, used as fallback if settlement_date missing)
    
    Returns:
        Dict with keys:
        - servicing_transfer_months: Optional[int] - Months from settlement_date to servicing_transfer_date (rounded to nearest integer, typically 1)
        - foreclosure_days: Optional[int] - Total FC duration in days
        - foreclosure_months: Optional[int] - Total FC duration converted to months (rounded to nearest integer)
        - total_timeline_months: Optional[int] - Sum of servicing + foreclosure months (whole integer)
    """
    if reference_date is None:
        reference_date = date.today()
    
    # WHAT: Get asset's SellerRawData to access trade
    # WHY: Need trade to find TradeLevelAssumption for servicing_transfer_date
    raw_data = SellerRawData.objects.filter(asset_hub_id=asset_hub_id).select_related('trade').first()
    
    # WHAT: Default to 0 instead of None so calculations still work
    # WHY: Returning None breaks frontend calculations; 0 is a valid "no duration" value
    servicing_transfer_months = 0
    
    if raw_data and raw_data.trade:
        # WHAT: Get TradeLevelAssumption for this trade
        # WHY: Contains servicing_transfer_date field with fallback logic
        trade_assumption = TradeLevelAssumption.objects.filter(trade=raw_data.trade).first()
        
        if trade_assumption:
            # WHAT: Use effective_servicing_transfer_date property which has fallback logic
            # WHY: Returns explicit date if set, otherwise calculates using servicer duration
            transfer_date = trade_assumption.effective_servicing_transfer_date
            
            if transfer_date and trade_assumption.settlement_date:
                # WHAT: Calculate months between settlement_date and servicing_transfer_date
                # WHY: Need duration in months from settlement to transfer (typically ~1 month)
                # HOW: Calculate difference in days, convert to months, round to nearest integer
                days_diff = (transfer_date - trade_assumption.settlement_date).days
                
                if days_diff >= 0:
                    # WHAT: Convert days to months and round to nearest whole integer
                    # WHY: Work with whole integers for display consistency
                    servicing_transfer_months = round(days_diff / 30.44)
                else:
                    # WHAT: If transfer date is before settlement, default to 1 month
                    # WHY: Minimum reasonable transfer period
                    servicing_transfer_months = 1
            elif not trade_assumption.settlement_date and trade_assumption.servicer:
                # WHAT: If no settlement date but servicer exists, use servicer's default duration
                # WHY: Still provide a value for calculations
                if trade_assumption.servicer.servicing_transfer_duration:
                    servicing_transfer_months = trade_assumption.servicer.servicing_transfer_duration
    
    # WHAT: Get FC timeline data using existing function
    # WHY: Reuse existing logic that sums all FCStatus durations
    fc_timeline_data = get_asset_fc_timeline(asset_hub_id)
    
    foreclosure_days = fc_timeline_data.get('totalDurationDays')
    foreclosure_months = None
    foreclosure_months_base = None
    fc_duration_override_months = 0
    
    if foreclosure_days is not None:
        # WHAT: Convert days to months and round to nearest whole integer
        # WHY: Work with whole integers for display consistency
        base_foreclosure_months = round(foreclosure_days / 30.44)
        foreclosure_months_base = base_foreclosure_months
        
        # WHAT: Check for user override in LoanLevelAssumption
        # WHY: Allow users to adjust FC duration if needed
        loan_assumption = LoanLevelAssumption.objects.filter(
            asset_hub_id=asset_hub_id
        ).first()
        
        if loan_assumption and loan_assumption.fc_duration_override_months is not None:
            fc_duration_override_months = loan_assumption.fc_duration_override_months
        
        # WHAT: Apply override to base foreclosure months
        # WHY: User-specified adjustment takes precedence
        foreclosure_months = base_foreclosure_months + fc_duration_override_months
        # WHAT: Ensure non-negative result
        # WHY: Negative months don't make sense
        if foreclosure_months < 0:
            foreclosure_months = 0
    
    # WHAT: Calculate total timeline months (sum of servicing + foreclosure)
    # WHY: Sum for display in Financial Summary
    # HOW: Already integers, so simple addition
    total_timeline_months = None
    if servicing_transfer_months is not None and foreclosure_months is not None:
        total_timeline_months = servicing_transfer_months + foreclosure_months
    elif servicing_transfer_months is not None:
        total_timeline_months = servicing_transfer_months
    elif foreclosure_months is not None:
        total_timeline_months = foreclosure_months
    
    # WHAT: Get FC sale proceeds for this asset
    # WHY: Need to display expected recovery in frontend Financial Summary
    expected_recovery = None
    try:
        proceeds = fc_sale_proceeds(asset_hub_id)
        if proceeds is not None:
            expected_recovery = float(proceeds)
    except Exception as e:
        # WHAT: If calculation fails, leave as None
        # WHY: Don't break the API if proceeds calculation fails
        # print(f"ERROR calculating FC sale proceeds: {str(e)}")
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
        # print(f"ERROR calculating acquisition price: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return {
        'servicing_transfer_months': servicing_transfer_months,
        'foreclosure_days': foreclosure_days,
        'foreclosure_months': foreclosure_months,
        'foreclosure_months_base': foreclosure_months_base,
        'fc_duration_override_months': fc_duration_override_months if foreclosure_months_base is not None else None,
        'total_timeline_months': total_timeline_months,
        'expected_recovery': expected_recovery,
        'acquisition_price': acq_price
    }


def get_fc_expense_values(
    asset_hub_id: int, 
    total_timeline_months: Optional[int] = None,
    servicing_transfer_months: Optional[int] = None,
    foreclosure_months: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get foreclosure expense values for an asset from models.
    
    What: Fetches expense values from backend models/logic:
    - Servicing Fees: board_fee + (onetwentyday_fee * servicing_transfer_months) + (fc_fee * foreclosure_months) + liquidation_fee
    - Taxes: Monthly tax from logi_acq_expenseAssumptions.monthly_tax_for_asset multiplied by total_timeline_months
    - Insurance: Monthly insurance from logi_acq_expenseAssumptions.monthly_insurance_for_asset multiplied by total_timeline_months
    - Legal Cost: From StateReference.fc_legal_fees_avg by matching asset's state
    
    Why: Provide expense values from models instead of free-form input.
    Where: Called by API views to serve frontend ForeclosureModelCard component.
    How:
    - Gets asset's state from SellerRawData
    - Gets servicer from TradeLevelAssumption
    - Calculates servicing fees from Servicer model fees
    - Looks up StateReference by state_code for legal fees
    - Uses existing expense calculation functions for taxes and insurance
    - Multiplies monthly taxes and insurance by total_timeline_months to get total expense
    
    Args:
        asset_hub_id: Primary key of AssetIdHub
        total_timeline_months: Total FC duration in months (servicing + foreclosure). If None, taxes/insurance remain monthly.
        servicing_transfer_months: Duration of servicing transfer in months
        foreclosure_months: Duration of foreclosure in months
    
    Returns:
        Dict with keys:
        Acquisition Costs:
        - acq_broker_fees: Optional[float] - Broker fees (percentage of purchase price from acq_broker_fee)
        - acq_other_fees: Optional[float] - Other fees (percentage of purchase price from acq_fee_other)
        - acq_legal: Optional[float] - Legal cost (flat fee per asset from TradeLevelAssumption.acq_legal_cost)
        - acq_dd: Optional[float] - Due diligence cost (flat fee per asset from TradeLevelAssumption.acq_dd_cost)
        - acq_tax_title: Optional[float] - Tax/title cost (flat fee per asset from TradeLevelAssumption.acq_tax_title_cost)
        Carry Costs:
        - servicing_fees: Optional[float] - Servicing fees (board + 120day*servicing_months + fc*fc_months)
        - taxes: Optional[float] - Total property tax amount (monthly * total_timeline_months if provided)
        - insurance: Optional[float] - Total insurance amount (monthly * total_timeline_months if provided)
        - legal_cost: Optional[float] - FC legal fees from state reference table
        Liquidation Expenses:
        - servicer_liquidation_fee: Optional[float] - Servicer liquidation fee = MAX(flat_fee, pct_fee * proceeds)
        - am_liquidation_fee: Optional[float] - Asset Manager liquidation fee (from logi_acq_outcomespecific.fc_am_liq_fee)
        Calculated Totals:
        - total_costs: float - Sum of all expenses (acquisition costs + carry costs + liquidation expenses)
        - expected_recovery: Optional[float] - FC sale proceeds (from logi_acq__proceedAssumptions.fc_sale_proceeds)
        - acquisition_price: Optional[float] - Purchase price (from logi_acq_purchasePrice.purchase_price)
        - net_pl: Optional[float] - Net P&L (Expected Recovery - Total Costs - Acquisition Price)
        - moic: Optional[float] - Multiple on Invested Capital (Expected Proceeds / (Acquisition Price + Total Costs))
        - annualized_roi: Optional[float] - Annualized ROI (((NetPL / Total Costs) + 1) ^ (12 / duration) - 1)
        - purchase_of_currentBalance: Optional[float] - Purchase price as % of current balance
        - purchase_of_totalDebt: Optional[float] - Purchase price as % of total debt
        - purchase_of_sellerAsIs: Optional[float] - Purchase price as % of seller as-is value
        - purchase_of_internalUWAsIs: Optional[float] - Purchase price as % of internal UW as-is value
        Base Values (for live frontend calculations):
        - base_currentBalance: Optional[float] - Current balance amount
        - base_totalDebt: Optional[float] - Total debt amount
        - base_sellerAsIs: Optional[float] - Seller as-is value amount
        - base_internalUWAsIs: Optional[float] - Internal UW as-is value amount
    """
    # WHAT: Get asset's SellerRawData to access state and trade
    # WHY: Need state for legal fees and trade for servicer
    raw_data = SellerRawData.objects.filter(asset_hub_id=asset_hub_id).select_related('trade').first()
    
    # WHAT: Initialize expense values with None
    # WHY: Return None if data not available
    # Acquisition Costs
    acq_broker_fees = None
    acq_other_fees = None
    acq_legal = None
    acq_dd = None
    acq_tax_title = None
    # WHAT: Acquisition fee percentages for frontend live calculation
    acq_broker_fee_pct = None
    acq_other_fee_pct = None
    # Carry Costs
    servicing_fees = None
    taxes = None
    insurance = None
    legal_cost = None
    # Liquidation Expenses
    servicer_liquidation_fee = None
    am_liquidation_fee = None
    
    # WHAT: Calculate Acquisition Costs
    # WHY: These are one-time costs incurred when acquiring the asset
    # HOW: Broker fee and other fees are percentages of purchase price; legal, DD, and tax/title are flat fees per asset
    # print(f"\n{'='*80}")
    # print(f"ACQUISITION COSTS CALCULATION - Asset Hub ID: {asset_hub_id}")
    # print(f"{'='*80}")
    
    # WHAT: Get broker fee and percentage (for live frontend calculation)
    try:
        broker_fee = acq_broker_fee(asset_hub_id)
        if broker_fee > 0:
            acq_broker_fees = broker_fee
            # print(f"1. Broker Fee: ${acq_broker_fees:,.2f}")
            pass
        # WHAT: Also fetch the percentage for frontend display
        # WHY: Frontend may need to show the percentage
        # HOW: Use acq_broker_fees (acquisition broker fee percentage) from trade assumptions
        if raw_data and raw_data.trade:
            trade_assumptions = TradeLevelAssumption.objects.filter(trade=raw_data.trade).only('acq_broker_fees').first()
            if trade_assumptions and trade_assumptions.acq_broker_fees is not None:
                acq_broker_fee_pct = float(trade_assumptions.acq_broker_fees)
        # else:
            # print(f"1. Broker Fee: $0.00")
    except Exception as e:
        # print(f"1. Broker Fee: ERROR - {str(e)}")
        pass
    
    # WHAT: Get other fees and percentage (for live frontend calculation)
    try:
        other_fee = acq_fee_other(asset_hub_id)
        if other_fee > 0:
            acq_other_fees = other_fee
            # print(f"2. Other Fees: ${acq_other_fees:,.2f}")
            pass
        # WHAT: Also fetch the percentage for frontend live calculation
        if raw_data and raw_data.trade:
            trade_assumptions = TradeLevelAssumption.objects.filter(trade=raw_data.trade).only('acq_other_costs').first()
            if trade_assumptions and trade_assumptions.acq_other_costs is not None:
                acq_other_fee_pct = float(trade_assumptions.acq_other_costs)
        # else:
            # print(f"2. Other Fees: $0.00")
    except Exception as e:
        # print(f"2. Other Fees: ERROR - {str(e)}")
        pass
    
    # WHAT: Get flat per-asset fees from TradeLevelAssumption
    # WHY: Legal, DD, and tax/title costs are applied to all assets in the trade
    if raw_data and raw_data.trade:
        try:
            trade_assumption = TradeLevelAssumption.objects.filter(trade=raw_data.trade).first()
            if trade_assumption:
                if trade_assumption.acq_legal_cost:
                    acq_legal = Decimal(str(trade_assumption.acq_legal_cost))
                    # print(f"3. Legal Cost: ${acq_legal:,.2f}")
                else:
                    # print(f"3. Legal Cost: $0.00 (not set)")
                    pass
                
                if trade_assumption.acq_dd_cost:
                    acq_dd = Decimal(str(trade_assumption.acq_dd_cost))
                    # print(f"4. Due Diligence Cost: ${acq_dd:,.2f}")
                else:
                    # print(f"4. Due Diligence Cost: $0.00 (not set)")
                    pass
                
                if trade_assumption.acq_tax_title_cost:
                    acq_tax_title = Decimal(str(trade_assumption.acq_tax_title_cost))
                    # print(f"5. Tax/Title Cost: ${acq_tax_title:,.2f}")
                else:
                    # print(f"5. Tax/Title Cost: $0.00 (not set)")
                    pass
            else:
                # print(f"3-5. Legal, DD, Tax/Title: $0.00 (no TradeLevelAssumption found)")
                pass
        except Exception as e:
            # print(f"3-5. Legal, DD, Tax/Title: ERROR - {str(e)}")
            pass
    else:
        # print(f"3-5. Legal, DD, Tax/Title: $0.00 (no trade linked)")
        pass
    
    # print(f"{'='*80}\n")
    
    # WHAT: Get servicing fees from Servicer model (Carry Costs only)
    # WHY: Calculate based on servicer's board fee, 120-day fee, and FC fee
    # HOW: servicing_fees = board_fee + (onetwentyday_fee * servicing_transfer_months) + (fc_fee * foreclosure_months)
    # NOTE: Liquidation fee is calculated separately and returned as servicer_liquidation_fee
    if raw_data and raw_data.trade:
        try:
            # WHAT: Get TradeLevelAssumption to access servicer
            # WHY: Servicer is linked to the trade
            trade_assumption = TradeLevelAssumption.objects.filter(trade=raw_data.trade).select_related('servicer').first()
            
            if trade_assumption and trade_assumption.servicer:
                servicer = trade_assumption.servicer
                
                # print(f"\n{'='*80}")
                # print(f"SERVICING FEES CALCULATION DEBUG - Asset Hub ID: {asset_hub_id}")
                # print(f"{'='*80}")
                
                # WHAT: Start with board fee (one-time cost)
                # WHY: Board fee is charged once when loan is boarded
                total_servicing_fees = Decimal('0.00')
                board_fee_value = Decimal('0.00')
                if servicer.board_fee:
                    board_fee_value = Decimal(str(servicer.board_fee))
                    total_servicing_fees += board_fee_value
                # print(f"1. Board Fee (one-time): ${board_fee_value:,.2f}")
                
                # WHAT: Add 120-day fee multiplied by servicing transfer duration
                # WHY: 120-day fee applies during servicing transfer period
                onetwentyday_total = Decimal('0.00')
                if servicer.onetwentyday_fee and servicing_transfer_months:
                    onetwentyday_fee_value = Decimal(str(servicer.onetwentyday_fee))
                    onetwentyday_total = onetwentyday_fee_value * Decimal(str(servicing_transfer_months))
                    total_servicing_fees += onetwentyday_total
                    # print(f"2. 120-Day Fee: ${onetwentyday_fee_value:,.2f} × {servicing_transfer_months} months = ${onetwentyday_total:,.2f}")
                else:
                    # print(f"2. 120-Day Fee: $0.00 (fee: {servicer.onetwentyday_fee}, months: {servicing_transfer_months})")
                    pass
                
                # WHAT: Add FC fee multiplied by foreclosure duration
                # WHY: FC fee applies during foreclosure period
                fc_total = Decimal('0.00')
                if servicer.fc_fee and foreclosure_months:
                    fc_fee_value = Decimal(str(servicer.fc_fee))
                    fc_total = fc_fee_value * Decimal(str(foreclosure_months))
                    total_servicing_fees += fc_total
                    # print(f"3. FC Fee: ${fc_fee_value:,.2f} × {foreclosure_months} months = ${fc_total:,.2f}")
                else:
                    # print(f"3. FC Fee: $0.00 (fee: {servicer.fc_fee}, months: {foreclosure_months})")
                    pass
                
                # print(f"\n   TOTAL SERVICING FEES (Carry Costs): ${total_servicing_fees:,.2f}")
                # print(f"{'='*80}\n")
                
                servicing_fees = total_servicing_fees
        except Exception as e:
            # WHAT: If calculation fails, leave as None
            # WHY: Don't break the API if one calculation fails
            # print(f"ERROR calculating servicing fees: {str(e)}")
            import traceback
            traceback.print_exc()
            pass
    
    # WHAT: Get monthly tax for asset
    # WHY: Use existing tax calculation logic
    try:
        monthly_taxes = monthly_tax_for_asset(asset_hub_id)
        # WHAT: Multiply by total_timeline_months if provided
        # WHY: Convert monthly tax to total tax expense over FC duration
        if monthly_taxes is not None and total_timeline_months is not None and total_timeline_months > 0:
            taxes = monthly_taxes * Decimal(str(total_timeline_months))
        else:
            taxes = monthly_taxes
    except Exception:
        pass
    
    # WHAT: Get monthly insurance for asset
    # WHY: Use existing insurance calculation logic
    try:
        monthly_insurance = monthly_insurance_for_asset(asset_hub_id)
        # WHAT: Multiply by total_timeline_months if provided
        # WHY: Convert monthly insurance to total insurance expense over FC duration
        if monthly_insurance is not None and total_timeline_months is not None and total_timeline_months > 0:
            insurance = monthly_insurance * Decimal(str(total_timeline_months))
        else:
            insurance = monthly_insurance
    except Exception:
        pass
    
    # WHAT: Get legal fees from StateReference table
    # WHY: Legal fees are state-specific and stored in reference table
    if raw_data and raw_data.state:
        try:
            state_ref = StateReference.objects.filter(state_code=raw_data.state).only('fc_legal_fees_avg').first()
            if state_ref and state_ref.fc_legal_fees_avg is not None:
                legal_cost = state_ref.fc_legal_fees_avg
                # WHAT: Convert to Decimal if not already
                # WHY: Ensure consistent type
                if not isinstance(legal_cost, Decimal):
                    legal_cost = Decimal(str(legal_cost))
        except Exception:
            pass
    
    # WHAT: Calculate Servicer Liquidation Fee separately
    # WHY: This is a liquidation expense, not a carry cost
    # HOW: Use fcoutcomeLogic to calculate liquidation fee = MAX(flat_fee, pct_fee * proceeds)
    if raw_data and raw_data.trade:
        try:
            trade_assumption = TradeLevelAssumption.objects.filter(trade=raw_data.trade).select_related('servicer').first()
            if trade_assumption and trade_assumption.servicer:
                # print(f"\n{'='*80}")
                # print(f"SERVICER LIQUIDATION FEE CALCULATION - Asset Hub ID: {asset_hub_id}")
                # print(f"{'='*80}")
                
                try:
                    outcome_logic = fcoutcomeLogic()
                    liq_fee = outcome_logic.fc_am_liq_fee(asset_hub_id)
                    if liq_fee > 0:
                        servicer_liquidation_fee = liq_fee
                        servicer = trade_assumption.servicer
                        # print(f"Liquidation Fee: ${liq_fee:,.2f}")
                        # print(f"(Servicer liqfee_flat: ${servicer.liqfee_flat or 0:,.2f}, liqfee_pct: {servicer.liqfee_pct or 0})")
                    else:
                        # print(f"Liquidation Fee: $0.00")
                        pass
                except Exception as e:
                    # print(f"Liquidation Fee: ERROR - {str(e)}")
                    pass
                
                # print(f"{'='*80}\n")
        except Exception:
            pass
    
    # WHAT: Calculate AM Liquidation Fee
    # WHY: Asset Manager charges a liquidation fee for managing the sale
    # HOW: Use fcoutcomeLogic.fc_am_liq_fee() to calculate
    # print(f"\n{'='*80}")
    # print(f"CALLING fc_am_liq_fee() for asset_hub_id={asset_hub_id}")
    # print(f"{'='*80}")
    am_liquidation_fee = Decimal('0.00')
    try:
        outcome_logic = fcoutcomeLogic()
        am_liq_fee = outcome_logic.fc_am_liq_fee(asset_hub_id)
        am_liquidation_fee = am_liq_fee
        # print(f"\n✓ AM Liquidation Fee returned: ${am_liquidation_fee:,.2f}")
        if am_liquidation_fee == 0:
            # print(f"⚠ WARNING: AM liquidation fee is $0.00 - check if servicer fees are configured")
            pass
        # print(f"{'='*80}\n")
    except Exception as e:
        # print(f"\n❌ ERROR calculating AM liquidation fee: {str(e)}")
        import traceback
        traceback.print_exc()
        # print(f"{'='*80}\n")
    
    # WHAT: Calculate total costs (sum of acquisition costs + carry costs + liquidation expenses)
    # WHY: Centralize calculation in backend instead of frontend
    total_costs = Decimal('0.00')
    # Acquisition Costs
    if acq_broker_fees is not None:
        total_costs += acq_broker_fees
    if acq_other_fees is not None:
        total_costs += acq_other_fees
    if acq_legal is not None:
        total_costs += acq_legal
    if acq_dd is not None:
        total_costs += acq_dd
    if acq_tax_title is not None:
        total_costs += acq_tax_title
    # Carry Costs
    if servicing_fees is not None:
        total_costs += servicing_fees
    if taxes is not None:
        total_costs += taxes
    if insurance is not None:
        total_costs += insurance
    if legal_cost is not None:
        total_costs += legal_cost
    # Liquidation Expenses
    if servicer_liquidation_fee is not None:
        total_costs += servicer_liquidation_fee
    if am_liquidation_fee is not None:
        total_costs += am_liquidation_fee
    
    # WHAT: Get expected recovery (FC sale proceeds)
    # WHY: Need this for Net PL calculation
    expected_recovery = None
    try:
        proceeds = fc_sale_proceeds(asset_hub_id)
        if proceeds is not None:
            expected_recovery = proceeds
    except Exception as e:
        # print(f"ERROR calculating expected recovery for Net PL: {str(e)}")
        pass
    
    # WHAT: Get acquisition price
    # WHY: Need this for Net PL calculation
    acquisition_price = None
    try:
        acq_price = purchase_price(asset_hub_id)
        if acq_price is not None:
            acquisition_price = acq_price
    except Exception as e:
        # print(f"ERROR getting acquisition price for Net PL: {str(e)}")
        pass
    
    # WHAT: Get purchase price metrics (ratios) and base values
    # WHY: Display acquisition price as % of key metrics for context, and provide base values for live updates
    price_metrics = {}
    base_values = {
        'base_currentBalance': None,
        'base_totalDebt': None,
        'base_sellerAsIs': None,
        'base_internalUWAsIs': None
    }
    try:
        price_metrics = purchase_price_metrics(asset_hub_id)
        # print(f"\nPurchase Price Metrics:")
        # print(f"  - % of Current Balance: {price_metrics.get('purchase_of_currentBalance')}%")
        # print(f"  - % of Total Debt: {price_metrics.get('purchase_of_totalDebt')}%")
        # print(f"  - % of Seller As-Is: {price_metrics.get('purchase_of_sellerAsIs')}%")
        # print(f"  - % of Internal UW As-Is: {price_metrics.get('purchase_of_internalUWAsIs')}%")
        
        # WHAT: Also get base values for frontend live calculations
        # WHY: Frontend needs these to recalculate percentages as user types
        if raw_data:
            base_values['base_currentBalance'] = float(raw_data.current_balance) if raw_data.current_balance else None
            base_values['base_totalDebt'] = float(raw_data.total_debt) if raw_data.total_debt else None
            base_values['base_sellerAsIs'] = float(raw_data.seller_asis_value) if raw_data.seller_asis_value else None
            
            # WHAT: Get internal UW as-is value from Valuation for base
            from core.models.valuations import Valuation
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
        # print(f"ERROR calculating purchase price metrics: {str(e)}")
        pass
    
    # WHAT: Calculate Net PL
    # WHY: Net PL = Expected Recovery - Total Costs - Acquisition Price
    # HOW: Centralize this calculation in backend for consistency
    net_pl = None
    if expected_recovery is not None and acquisition_price is not None:
        net_pl = expected_recovery - total_costs - acquisition_price
    
    # WHAT: Calculate MOIC (Multiple on Invested Capital)
    # WHY: MOIC = Total Inflows / Total Outflows = Expected Proceeds / (Acquisition Price + Total Costs)
    # HOW: Shows how many times the investment is returned
    moic = None
    if expected_recovery is not None and acquisition_price is not None:
        total_outflows = acquisition_price + total_costs
        if total_outflows > 0:
            moic = expected_recovery / total_outflows
            # print(f"\nMOIC: ${expected_recovery:,.2f} / (${acquisition_price:,.2f} + ${total_costs:,.2f}) = {moic:.2f}x")
    
    # WHAT: Calculate Annualized ROI
    # WHY: Annualized ROI = ((NetPL / Gross Cost) + 1) ^ (12 / total_duration) - 1
    #      where Gross Cost = Acquisition Price + Total Expenses
    # HOW: Annualizes the return to show yearly percentage return
    annualized_roi = None
    if net_pl is not None and acquisition_price is not None and total_timeline_months and total_timeline_months > 0:
        # WHAT: Calculate Gross Cost (total invested capital)
        # WHY: This is acquisition price + all expenses
        gross_cost = acquisition_price + total_costs
        if gross_cost > 0:
            # WHAT: Calculate base return ratio (Net PL / Gross Cost)
            return_ratio = net_pl / gross_cost
            # WHAT: Add 1 to convert from percentage to growth multiplier
            growth_factor = float(return_ratio) + 1.0
            # WHAT: Calculate exponent as 12 / duration (for full year annualization)
            # WHY: Converts the return to an annual basis
            exponent = 12.0 / float(total_timeline_months)
            # WHAT: Apply exponent and subtract 1 to get annualized percentage
            annualized_roi = (growth_factor ** exponent) - 1.0
            # print(f"Annualized ROI: ((${net_pl:,.2f} / (${acquisition_price:,.2f} + ${total_costs:,.2f})) + 1) ^ (12 / {total_timeline_months}) - 1 = {annualized_roi:.4f} ({annualized_roi * 100:.2f}%)")
    
    return {
        # WHAT: Acquisition Costs (one-time costs when acquiring asset)
        'acq_broker_fees': float(acq_broker_fees) if acq_broker_fees is not None else None,
        'acq_other_fees': float(acq_other_fees) if acq_other_fees is not None else None,
        'acq_legal': float(acq_legal) if acq_legal is not None else None,
        'acq_dd': float(acq_dd) if acq_dd is not None else None,
        'acq_tax_title': float(acq_tax_title) if acq_tax_title is not None else None,
        # WHAT: Return percentages for frontend live calculation
        'acq_broker_fee_pct': acq_broker_fee_pct,
        'acq_other_fee_pct': acq_other_fee_pct,
        # WHAT: Carry Costs (ongoing expenses during FC process)
        'servicing_fees': float(servicing_fees) if servicing_fees is not None else None,
        'taxes': float(taxes) if taxes is not None else None,
        'insurance': float(insurance) if insurance is not None else None,
        'legal_cost': float(legal_cost) if legal_cost is not None else None,
        # WHAT: Liquidation Expenses (costs incurred at sale)
        'servicer_liquidation_fee': float(servicer_liquidation_fee) if servicer_liquidation_fee is not None else None,
        'am_liquidation_fee': float(am_liquidation_fee) if am_liquidation_fee is not None else None,
        # WHAT: Calculated totals
        'total_costs': float(total_costs),
        'expected_recovery': float(expected_recovery) if expected_recovery is not None else None,
        'acquisition_price': float(acquisition_price) if acquisition_price is not None else None,
        'net_pl': float(net_pl) if net_pl is not None else None,
        'moic': float(moic) if moic is not None else None,
        'annualized_roi': float(annualized_roi) if annualized_roi is not None else None,
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

