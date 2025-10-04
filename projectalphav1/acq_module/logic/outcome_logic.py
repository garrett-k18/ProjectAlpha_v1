from decimal import Decimal
from typing import Optional

from acq_module.models.seller import SellerRawData

class fcoutcomeLogic:
    def __init__(self):
        pass

    def forecasted_total_debt(self, asset_hub_id: int) -> Decimal:
        """
        Return a base forecast of total debt for a single asset identified by AssetIdHub.

        What this does (now):
        - Loads `SellerRawData` by `asset_hub_id` and returns its `total_debt` value
          (defaults to Decimal('0.00') when missing).

        What we'll add next (future components to be summed into the forecast):
        - estimated monthly property taxes using state assumptions
          e.g., see helpers in `acq_module.logic.model_logic`:
              monthly_tax_for_asset(asset_hub_id)
        - estimated monthly insurance using state assumptions
              monthly_insurance_for_asset(asset_hub_id)
        - Advances (escrow advances, recoverable corporate advances)
        - Legal costs (FC, BK, DIL, CFK, eviction)
        - REO holding/marketing costs

        Ultimately the forecast could be:
            total = base_debt \
                    + est_monthly_tax \
                    + est_monthly_insurance \
                    + est_advances \
                    + est_legal \
                    + est_reo_holding

        Args:
            asset_hub_id: Primary key of the master asset (core.AssetIdHub)

        Returns:
            Decimal: Current total debt for the asset (baseline for the forecast).
        """
        # Fetch just what we need: current consolidated debt on the asset row
        raw: Optional[SellerRawData] = (
            SellerRawData.objects
            .filter(asset_hub_id=asset_hub_id)
            .only('total_debt', 'state', 'seller_asis_value')  # state/value may be needed for future components
            .first()
        )

        if not raw:
            return Decimal('0.00')

        base_debt: Decimal = raw.total_debt or Decimal('0.00')

        # NOTE: Future extension point (intentionally commented for clarity):
        # from acq_module.logic.model_logic import monthly_tax_for_asset, monthly_insurance_for_asset
        # est_monthly_tax = monthly_tax_for_asset(asset_hub_id)
        # est_monthly_ins = monthly_insurance_for_asset(asset_hub_id)
        # advances = Decimal('0.00')  # TODO: source from servicer data or assumptions
        # legal   = Decimal('0.00')  # TODO: sum FC/BK/DIL/CFK/Eviction assumptions
        # total = base_debt + est_monthly_tax + est_monthly_ins + advances + legal
        # return total

        # For now, return the baseline only.
        return base_debt

    def fc_am_liq_fee(self, asset_hub_id: int) -> Decimal:
        

   