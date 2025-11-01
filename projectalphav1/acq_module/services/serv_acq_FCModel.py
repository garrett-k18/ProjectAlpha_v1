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
from acq_module.logic.logi_acq_expenseAssumptions import monthly_tax_for_asset, monthly_insurance_for_asset
from acq_module.logic.logi_acq__proceedAssumptions import fc_sale_proceeds
from acq_module.logic.logi_acq_purchasePrice import purchase_price
from acq_module.logic.outcome_logic import fcoutcomeLogic
from core.models.model_co_assumptions import StateReference, Servicer


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
    
    servicing_transfer_months = None
    
    if raw_data and raw_data.trade:
        # WHAT: Get TradeLevelAssumption for this trade
        # WHY: Contains servicing_transfer_date field with fallback logic
        trade_assumption = TradeLevelAssumption.objects.filter(trade=raw_data.trade).first()
        
        if trade_assumption:
            # WHAT: Use effective_servicing_transfer_date property which has fallback logic
            # WHY: Returns explicit date if set, otherwise calculates as settlement_date + 30 days
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
            elif transfer_date:
                # WHAT: If no settlement_date but transfer_date exists, use reference_date as fallback
                # WHY: Still calculate duration for display
                days_diff = (reference_date - transfer_date).days
                if days_diff >= 0:
                    servicing_transfer_months = round(days_diff / 30.44)
                else:
                    servicing_transfer_months = 0
    
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
    except Exception:
        # WHAT: If calculation fails, leave as None
        # WHY: Don't break the API if proceeds calculation fails
        pass
    
    # WHAT: Get acquisition price for this asset
    # WHY: Need to display and allow editing in frontend
    acq_price = None
    try:
        price = purchase_price(asset_hub_id)
        if price is not None:
            acq_price = float(price)
    except Exception:
        pass
    
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
        - servicing_fees: Optional[float] - Total servicing fees (board + 120day*servicing_months + fc*fc_months + liquidation_fee)
        - taxes: Optional[float] - Total property tax amount (monthly * total_timeline_months if provided)
        - insurance: Optional[float] - Total insurance amount (monthly * total_timeline_months if provided)
        - legal_cost: Optional[float] - FC legal fees from state reference table
    """
    # WHAT: Get asset's SellerRawData to access state and trade
    # WHY: Need state for legal fees and trade for servicer
    raw_data = SellerRawData.objects.filter(asset_hub_id=asset_hub_id).select_related('trade').first()
    
    # WHAT: Initialize expense values with None
    # WHY: Return None if data not available
    servicing_fees = None
    taxes = None
    insurance = None
    legal_cost = None
    
    # WHAT: Get servicing fees from Servicer model
    # WHY: Calculate based on servicer's board fee, 120-day fee, FC fee, and liquidation fee
    # HOW: servicing_fees = board_fee + (onetwentyday_fee * servicing_transfer_months) + (fc_fee * foreclosure_months) + liquidation_fee
    if raw_data and raw_data.trade:
        try:
            # WHAT: Get TradeLevelAssumption to access servicer
            # WHY: Servicer is linked to the trade
            trade_assumption = TradeLevelAssumption.objects.filter(trade=raw_data.trade).select_related('servicer').first()
            
            if trade_assumption and trade_assumption.servicer:
                servicer = trade_assumption.servicer
                
                print(f"\n{'='*80}")
                print(f"SERVICING FEES CALCULATION DEBUG - Asset Hub ID: {asset_hub_id}")
                print(f"{'='*80}")
                
                # WHAT: Start with board fee (one-time cost)
                # WHY: Board fee is charged once when loan is boarded
                total_servicing_fees = Decimal('0.00')
                board_fee_value = Decimal('0.00')
                if servicer.board_fee:
                    board_fee_value = Decimal(str(servicer.board_fee))
                    total_servicing_fees += board_fee_value
                print(f"1. Board Fee (one-time): ${board_fee_value:,.2f}")
                
                # WHAT: Add 120-day fee multiplied by servicing transfer duration
                # WHY: 120-day fee applies during servicing transfer period
                onetwentyday_total = Decimal('0.00')
                if servicer.onetwentyday_fee and servicing_transfer_months:
                    onetwentyday_fee_value = Decimal(str(servicer.onetwentyday_fee))
                    onetwentyday_total = onetwentyday_fee_value * Decimal(str(servicing_transfer_months))
                    total_servicing_fees += onetwentyday_total
                    print(f"2. 120-Day Fee: ${onetwentyday_fee_value:,.2f} × {servicing_transfer_months} months = ${onetwentyday_total:,.2f}")
                else:
                    print(f"2. 120-Day Fee: $0.00 (fee: {servicer.onetwentyday_fee}, months: {servicing_transfer_months})")
                
                # WHAT: Add FC fee multiplied by foreclosure duration
                # WHY: FC fee applies during foreclosure period
                fc_total = Decimal('0.00')
                if servicer.fc_fee and foreclosure_months:
                    fc_fee_value = Decimal(str(servicer.fc_fee))
                    fc_total = fc_fee_value * Decimal(str(foreclosure_months))
                    total_servicing_fees += fc_total
                    print(f"3. FC Fee: ${fc_fee_value:,.2f} × {foreclosure_months} months = ${fc_total:,.2f}")
                else:
                    print(f"3. FC Fee: $0.00 (fee: {servicer.fc_fee}, months: {foreclosure_months})")
                
                print(f"\n   Subtotal (before liquidation fee): ${total_servicing_fees:,.2f}")
                
                # WHAT: Add liquidation fee (charged at sale)
                # WHY: Servicer charges liquidation fee = MAX(flat_fee, pct_fee * proceeds)
                # HOW: Use fcoutcomeLogic to calculate liquidation fee
                liq_fee = Decimal('0.00')
                try:
                    outcome_logic = fcoutcomeLogic()
                    liq_fee = outcome_logic.fc_am_liq_fee(asset_hub_id)
                    if liq_fee > 0:
                        print(f"4. Liquidation Fee: ${liq_fee:,.2f}")
                        print(f"   (Servicer liqfee_flat: ${servicer.liqfee_flat or 0:,.2f}, liqfee_pct: {servicer.liqfee_pct or 0})")
                        total_servicing_fees += liq_fee
                    else:
                        print(f"4. Liquidation Fee: $0.00")
                except Exception as e:
                    # WHAT: If liquidation fee calc fails, continue without it
                    # WHY: Don't break entire servicing fee calculation
                    print(f"4. Liquidation Fee: ERROR - {str(e)}")
                
                print(f"\n   TOTAL SERVICING FEES: ${total_servicing_fees:,.2f}")
                print(f"{'='*80}\n")
                
                servicing_fees = total_servicing_fees
        except Exception as e:
            # WHAT: If calculation fails, leave as None
            # WHY: Don't break the API if one calculation fails
            print(f"ERROR calculating servicing fees: {str(e)}")
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
    
    return {
        'servicing_fees': float(servicing_fees) if servicing_fees is not None else None,
        'taxes': float(taxes) if taxes is not None else None,
        'insurance': float(insurance) if insurance is not None else None,
        'legal_cost': float(legal_cost) if legal_cost is not None else None
    }

