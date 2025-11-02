from decimal import Decimal
from typing import Optional

from acq_module.models.model_acq_seller import SellerRawData
from acq_module.models.model_acq_assumptions import TradeLevelAssumption, LoanLevelAssumption
from acq_module.logic.logi_acq_expenseAssumptions import monthly_tax_for_asset, monthly_insurance_for_asset
from acq_module.logic.logi_acq_durationAssumptions import get_asset_fc_timeline
from core.models.model_co_assumptions import StateReference


class fcoutcomeLogic:
    """
    Main logic class for foreclosure outcome calculations.
    
    What: Handles all FC outcome forecasting and calculations.
    Why: Centralize FC outcome logic for API views and other modules.
    Where: projectalphav1/acq_module/logic/logi_acq_outcomespecific.py
    How: Initialize and call specific calculation methods with asset_hub_id.
    """
    
    def __init__(self):
        pass

    def forecasted_total_debt(self, asset_hub_id: int) -> Decimal:
        """
        Return forecasted total debt including accumulated expenses during FC timeline.

        What this calculates:
        - Base total debt from SellerRawData
        - Property taxes accumulated over FC timeline (monthly_tax × total_timeline_months)
        - Insurance accumulated over FC timeline (monthly_insurance × total_timeline_months)
        - Legal costs from state reference table
        
        Why: Provides realistic forecast of total debt at time of foreclosure sale, matching 
             the expense calculations used in the frontend FC model card.
        
        How: 
        - Gets base debt from SellerRawData
        - Gets FC timeline duration (servicing transfer + foreclosure months)
        - Multiplies monthly expenses by timeline duration
        - Adds state-specific legal costs

        Args:
            asset_hub_id: Primary key of the master asset (core.AssetIdHub)

        Returns:
            Decimal: Forecasted total debt including accumulated expenses
        """
        # WHAT: Fetch base debt and state for legal fees
        # WHY: Need current debt baseline and state for cost lookups
        raw: Optional[SellerRawData] = (
            SellerRawData.objects
            .filter(asset_hub_id=asset_hub_id)
            .only('total_debt', 'state')
            .first()
        )

        if not raw:
            return Decimal('0.00')

        base_debt: Decimal = raw.total_debt or Decimal('0.00')
        
        # print(f"\n{'='*80}")
        # print(f"FORECASTED TOTAL DEBT CALCULATION - Asset Hub ID: {asset_hub_id}")
        # print(f"{'='*80}")
        # print(f"1. Base Total Debt: ${base_debt:,.2f}")
        
        # WHAT: Get FC timeline to calculate duration-based expenses (including user overrides)
        # WHY: Taxes and insurance accumulate over the entire timeline
        try:
            fc_timeline = get_asset_fc_timeline(asset_hub_id)
            total_days = fc_timeline.get('totalDurationDays', 0)
            base_months = round(total_days / 30.44) if total_days else 0
            
            # WHAT: Check for user override in LoanLevelAssumption
            # WHY: User may have adjusted FC duration, need to match service file calculation
            loan_assumption = LoanLevelAssumption.objects.filter(asset_hub_id=asset_hub_id).first()
            fc_override = 0
            if loan_assumption and loan_assumption.fc_duration_override_months is not None:
                fc_override = loan_assumption.fc_duration_override_months
            
            # WHAT: Apply override to base months
            # WHY: Match the calculation in serv_acq_FCModel.py
            total_months = base_months + fc_override
            if total_months < 0:
                total_months = 0
                
            # print(f"2. Total Timeline: {total_months} months ({total_days} days, override: {fc_override})")
        except Exception as e:
            # print(f"2. Total Timeline: ERROR - {str(e)}, defaulting to 0 months")
            import traceback
            traceback.print_exc()
            total_months = 0
        
        # WHAT: Calculate accumulated taxes over FC timeline
        # WHY: Property taxes accrue monthly during foreclosure process
        taxes_accumulated = Decimal('0.00')
        try:
            monthly_tax = monthly_tax_for_asset(asset_hub_id)
            if monthly_tax > 0 and total_months > 0:
                taxes_accumulated = monthly_tax * Decimal(str(total_months))
            # print(f"3. Taxes: ${monthly_tax:,.2f}/month × {total_months} months = ${taxes_accumulated:,.2f}")
        except Exception as e:
            # print(f"3. Taxes: ERROR - {str(e)}")
            pass
        
        # WHAT: Calculate accumulated insurance over FC timeline
        # WHY: Insurance premiums accrue monthly during foreclosure process
        insurance_accumulated = Decimal('0.00')
        try:
            monthly_insurance = monthly_insurance_for_asset(asset_hub_id)
            if monthly_insurance > 0 and total_months > 0:
                insurance_accumulated = monthly_insurance * Decimal(str(total_months))
            # print(f"4. Insurance: ${monthly_insurance:,.2f}/month × {total_months} months = ${insurance_accumulated:,.2f}")
        except Exception as e:
            # print(f"4. Insurance: ERROR - {str(e)}")
            pass
        
        # WHAT: Get state-specific legal fees
        # WHY: Legal costs are incurred during foreclosure process
        legal_costs = Decimal('0.00')
        if raw.state:
            try:
                state_ref = StateReference.objects.filter(state_code=raw.state).only('fc_legal_fees_avg').first()
                if state_ref and state_ref.fc_legal_fees_avg:
                    legal_costs = Decimal(str(state_ref.fc_legal_fees_avg))
                # print(f"5. Legal Costs ({raw.state}): ${legal_costs:,.2f}")
            except Exception as e:
                # print(f"5. Legal Costs: ERROR - {str(e)}")
                pass
        else:
            # print(f"5. Legal Costs: $0.00 (no state)")
            pass
        
        # WHAT: Calculate total forecasted debt
        # WHY: Sum all components for complete debt forecast
        total_forecasted_debt = base_debt + taxes_accumulated + insurance_accumulated + legal_costs
        
        # print(f"\n   TOTAL FORECASTED DEBT: ${total_forecasted_debt:,.2f}")
        # print(f"{'='*80}\n")
        
        return total_forecasted_debt

    def fc_am_liq_fee(self, asset_hub_id: int) -> Decimal:
        """
        Calculate FC AM liquidation fee for a specific asset.
        
        What: Calculates the liquidation fee charged by the servicer for FC sale
        Why: Servicers charge a liquidation fee that is either a flat fee or percentage of proceeds
        Where: Used in FC outcome expense calculations
        How: Returns MAX(liq_flat_fee, liq_fee_pct * fc_sale_proceeds)
        
        Business Logic:
        - Get servicer from TradeLevelAssumption (linked via asset's trade)
        - Get FC sale proceeds from logi_acq__proceedAssumptions.fc_sale_proceeds()
        - Calculate: MAX(servicer.liqfee_flat, servicer.liqfee_pct * fc_sale_proceeds)
        - Flat fee acts as a floor/minimum - ensures servicer gets at least that amount
        
        Args:
            asset_hub_id: Primary key of the master asset (core.AssetIdHub)
            
        Returns:
            Decimal: Calculated liquidation fee amount (minimum of flat fee or percentage-based fee)
        """
        # print(f"\n{'='*80}")
        # print(f"FC AM LIQUIDATION FEE CALCULATION - Asset Hub ID: {asset_hub_id}")
        # print(f"{'='*80}")
        
        # WHAT: Import here to avoid circular dependency
        # WHY: logi_acq__proceedAssumptions imports logi_acq_outcomespecific, so we delay import
        from acq_module.logic.logi_acq__proceedAssumptions import fc_sale_proceeds
        
        # WHAT: Get the asset's SellerRawData to access trade
        # WHY: Need trade to find TradeLevelAssumption which has servicer
        # print(f"Step 1: Looking up SellerRawData for asset_hub_id={asset_hub_id}")
        raw_data = (
            SellerRawData.objects
            .filter(asset_hub_id=asset_hub_id)
            .select_related('trade')
            .first()
        )
        
        if not raw_data:
            # print(f"   ❌ ERROR: No SellerRawData found for asset_hub_id={asset_hub_id}")
            # print(f"   Returning: $0.00")
            # print(f"{'='*80}\n")
            return Decimal('0.00')
        
        # print(f"   ✓ Found SellerRawData (asset_hub_id={raw_data.pk})")
        
        if not raw_data.trade:
            # print(f"   ❌ ERROR: SellerRawData has no trade linked")
            # print(f"   Returning: $0.00")
            # print(f"{'='*80}\n")
            return Decimal('0.00')
        
        # print(f"   ✓ Found Trade (id={raw_data.trade.pk}, name={raw_data.trade.trade_name if hasattr(raw_data.trade, 'trade_name') else 'N/A'})")
        
        # WHAT: Get TradeLevelAssumption to access servicer fees
        # WHY: Servicer liquidation fees are stored in the servicer model
        # print(f"\nStep 2: Looking up TradeLevelAssumption for trade_id={raw_data.trade.pk}")
        trade_assumption = (
            TradeLevelAssumption.objects
            .filter(trade=raw_data.trade)
            .select_related('servicer')
            .first()
        )
        
        if not trade_assumption:
            # print(f"   ❌ ERROR: No TradeLevelAssumption found for trade_id={raw_data.trade.pk}")
            # print(f"   Returning: $0.00")
            # print(f"{'='*80}\n")
            return Decimal('0.00')
        
        # print(f"   ✓ Found TradeLevelAssumption (id={trade_assumption.pk})")
        
        if not trade_assumption.servicer:
            # print(f"   ❌ ERROR: TradeLevelAssumption has no servicer linked")
            # print(f"   Returning: $0.00")
            # print(f"{'='*80}\n")
            return Decimal('0.00')
        
        servicer = trade_assumption.servicer
        # print(f"   ✓ Found Servicer (id={servicer.pk}, name={servicer.servicer_name if hasattr(servicer, 'servicer_name') else 'N/A'})")
        
        # WHAT: Get FC sale proceeds for this asset
        # WHY: Percentage-based fee is calculated on proceeds
        # print(f"\nStep 3: Calculating FC sale proceeds")
        try:
            proceeds = fc_sale_proceeds(asset_hub_id)
            # print(f"   ✓ FC Sale Proceeds: ${proceeds:,.2f}")
        except Exception as e:
            # print(f"   ❌ ERROR calculating FC sale proceeds: {str(e)}")
            import traceback
            traceback.print_exc()
            # print(f"   Returning: $0.00")
            # print(f"{'='*80}\n")
            return Decimal('0.00')
        
        if proceeds <= 0:
            # print(f"   ⚠ WARNING: Proceeds is <= 0")
            # print(f"   Returning: $0.00")
            # print(f"{'='*80}\n")
            return Decimal('0.00')
        
        # WHAT: Calculate percentage-based fee
        # WHY: One of the two options for liquidation fee
        # print(f"\nStep 4: Calculating liquidation fees")
        pct_fee = Decimal('0.00')
        if servicer.liqfee_pct:
            pct_fee_pct = Decimal(str(servicer.liqfee_pct))
            pct_fee = (pct_fee_pct * proceeds).quantize(Decimal('0.01'))
            # print(f"   • Percentage Fee: {pct_fee_pct} × ${proceeds:,.2f} = ${pct_fee:,.2f}")
        else:
            # print(f"   • Percentage Fee: N/A (servicer.liqfee_pct is None or 0)")
            pass
        
        # WHAT: Get flat fee option
        # WHY: The other option for liquidation fee
        flat_fee = Decimal('0.00')
        if servicer.liqfee_flat:
            flat_fee = Decimal(str(servicer.liqfee_flat))
            # print(f"   • Flat Fee: ${flat_fee:,.2f}")
        else:
            # print(f"   • Flat Fee: N/A (servicer.liqfee_flat is None or 0)")
            pass
        
        # WHAT: Return the maximum of the two fee options
        # WHY: Servicer charges whichever is higher (flat fee acts as floor/minimum)
        # HOW: MAX(flat_fee, pct_fee) - ensures servicer gets at least the flat fee
        # print(f"\nStep 5: Determining final liquidation fee")
        result = Decimal('0.00')
        if flat_fee > 0 and pct_fee > 0:
            result = max(flat_fee, pct_fee)
            # print(f"   ✓ Result: MAX(${flat_fee:,.2f}, ${pct_fee:,.2f}) = ${result:,.2f}")
        elif flat_fee > 0:
            result = flat_fee
            # print(f"   ✓ Result: ${result:,.2f} (flat fee only)")
        elif pct_fee > 0:
            result = pct_fee
            # print(f"   ✓ Result: ${result:,.2f} (percentage fee only)")
        else:
            # print(f"   ⚠ Result: $0.00 (no fees configured on servicer)")
            pass
        
        # print(f"{'='*80}\n")
        return result