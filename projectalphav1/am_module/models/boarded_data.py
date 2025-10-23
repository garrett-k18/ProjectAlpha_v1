# ============================================================
# DEPRECATED MODEL - DO NOT USE
# SellerBoardedData is kept only for migration compatibility.
# All code references have been removed.
# Data can be safely deleted.
# REPLACEMENT: Use SellerRawData (acq_module.models.seller) with acq_status=BOARD
# ============================================================

from django.db import models
from django.utils import timezone
from acq_module.models.seller import SellerRawData
import re

# ============================================================
# PHASE 2: MODEL DELETED
# SellerBoardedData model has been removed from the codebase.
# Migration 0033_delete_sellerboardeddata.py successfully deployed.
# REPLACEMENT: Use SellerRawData (acq_module.models.seller) with acq_status=BOARD
# ============================================================

# Blended Outcome Model (One-to-one with AssetIdHub)
# -----------------------------------------------------------------------------------
class BlendedOutcomeModel(models.Model):
    """
    BlendedOutcomeModel stores the acquisition modeling snapshot for a boarded asset.

    Relationship:
    - Strict 1:1 with AssetIdHub so each boarded asset has at most one
      acquisition model row. We use a OneToOneField with primary_key=True so
      this model shares the same PK as the linked asset record.

    Field conventions:
    - Currency-like fields use Decimal(15,2) to match other financial fields across the app.
    - Percentage fields (expected_irr and outcome_*) are stored as 0–100 percent values
      using Decimal with two decimal places.
    - All fields are nullable by default to support partial boarding flows.

    Docs reviewed:
    - Django model fields: https://docs.djangoproject.com/en/stable/ref/models/fields/
    - OneToOneField: https://docs.djangoproject.com/en/stable/topics/db/models/#one-to-one-relationships
    """

    # Hub-owned primary key: strict 1:1 with core.AssetIdHub.
    # This aligns with the hub-first architecture so this model's PK equals the hub ID.
    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='blended_outcome_model',
        help_text='1:1 with hub; this model’s PK equals the hub ID.'
    )
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The purchase price of the asset.")
    purchase_date = models.DateField(null=True, blank=True, help_text="The purchase date of the asset.")
    # ------------------------------
    # Cost / Proceeds / Timing
    # ------------------------------

    outcome_blend = models.CharField(max_length=100, null=True, blank=True, help_text="The blended outcome of the asset.")

    # Timeline Details
    servicing_transfer_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was transferred to servicing.")
    performing_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was performing.")
    pre_mod_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was in pre-mod status.")
    mod_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was in mod status.")
    pre_fc_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was in pre-fc status.")
    fc_progress_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was in fc progress status.")
    fc_left_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was in fc left status.")
    fc_duration_state_avg = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was in fc status.")
    dil_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was in dil status.")
    bk_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was in bk status.")
    eviction_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was in eviction status.")
    renovation_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was in renovation status.")
    reo_marketing_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was in reo marketing status.")
    local_market_ext_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was in local market extension status.")
    rural_ext_duration = models.IntegerField(null=True, blank=True, help_text="The duration in months the loan was in rural status.")

    #Expense Details
        #Legal
    fc_expenses = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total FC expenses.")
    fc_legal_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total FC legal fees.")
    other_fc_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total other FC fees.")
    dil_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total DIL fees.")
    cfk_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total CFK fees.")
    bk_legal_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total BK legal fees.")
    eviction_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total eviction fees.")

        #Property Expenses
    reconciled_rehab_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The reconciled rehab cost.")
    trashout_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The trashout cost.")
    property_preservation_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The property preservation cost.")
    total_insurance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total yearly insurance cost.")
    total_property_tax = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total yearly property tax cost.")
    total_hoa = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total yearly HOA costs.")
    total_utility = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total yearly utility costs.")
    total_other = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total yearly other costs.")

        #Fund Expenses
    acq_costs = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="per asset fees when purchasing such as legal, DD, Title, etc.")
    am_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="total am fee over life of asset hold COuld be a per month calc or liq calc")

            #Closing Costs
    tax_title_transfer_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The tax, title, and transfer costs.")
    broker_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The broker fees at closing of REO.")

        #Servicing Costs
    servicing_board_fee = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total servicing board fee.")
    servicing_current = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total current servicing costs.")
    servicing_30d = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total 30 day servicing costs.")
    servicing_60d = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total 60 day servicing costs.")
    servicing_90d = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total 90 day servicing costs.")
    servicing_120d = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total 180 day servicing costs.")
    servicing_fc = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total FC servicing costs.")
    servicing_bk = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total BK servicing costs.")
    servicing_liq_fee = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total servicing costs.")



    #Income
    principal_collect = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The principal collected.")
    interest_collect = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The interest collected.")
    mod_down_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The modified down payment.")
    rental_income = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The rental income.")
    cam_income = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The CAM income.")
    other_income = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The other income.")

    
    

    expected_exit_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expected exit date (if known)."
    )
    expected_gross_proceeds = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Expected gross proceeds at exit (currency)."
    )
    expected_net_proceeds = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Expected net proceeds at exit (currency)."
    )

    # ------------------------------
    # Performance metrics
    # ------------------------------
    expected_pl = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Expected profit/loss (currency)."
    )
    expected_cf = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Expected cash flow (currency)."
    )
    expected_irr = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Expected IRR stored as percent (0–100)."
    )
    expected_moic = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        null=True,
        blank=True,
        help_text="Expected MOIC stored as decimal (0–100)."
    )
    
    expected_npv = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Expected Net Present Value (currency)."
    )
    expected_pv = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Expected Present Value (currency)."
    )

    # ------------------------------
    # Outcome weights (percent of 100)
    # ------------------------------
    outcome_perf = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight for Performing outcome (percent 0–100)."
    )
    outcome_mod = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight for Modification outcome (percent 0–100)."
    )
    outcome_fcsale = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight for Foreclosure Sale outcome (percent 0–100)."
    )
    outcome_dil_asis = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight for Deed-in-Lieu (As-Is) outcome (percent 0–100)."
    )
    outcome_dil_arv = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight for Deed-in-Lieu (ARV) outcome (percent 0–100)."
    )
    outcome_reo_asis = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight for REO (As-Is) outcome (percent 0–100)."
    )
    outcome_reo_arv = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight for REO (ARV) outcome (percent 0–100)."
    )

    bid_pct_upb = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Bid percentage of UPB (percent 0–100)."
    )
    bid_pct_td = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Bid percentage of TD (percent 0–100)."
    )
    bid_pct_sellerasis = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Bid percentage of Seller asis (percent 0–100)."
    )
   
    bid_pct_pv = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Bid percentage of present value (percent 0–100)."
    )

    # NOTE: Cash flow fields removed - migrated to CashFlowPeriod model below

    
    
    # Audit timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this boarded data record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this acquisition model record was last updated."
    )

    class Meta:
        verbose_name = "Acquisition Model"
        verbose_name_plural = "Acquisition Models"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Readable string for admin/debugging."""
        return f"AcqModel(hub_id={self.pk})"


class UWCashFlows(models.Model):
    """
    WHAT: Stores cash flow data for a single period (month) of an asset
    WHY: Flexible, scalable structure for unlimited periods with underwritten vs realized comparison
    HOW: Many-to-one relationship with AssetIdHub, one record per period
    WHERE: Replaces cf_p0-p30 fields in BlendedOutcomeModel
    
    Architecture:
    - Each asset can have unlimited periods (not limited to 30)
    - Stores both underwritten (from acquisition model) and realized (actual) cash flows
    - Supports detailed line items for both underwritten and realized
    - Enables easy variance calculation and period-level queries
    """
    
    # WHAT: Foreign key to AssetIdHub (many periods per asset)
    # WHY: Allows unlimited periods per asset, easy filtering/querying
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.CASCADE,
        related_name='cash_flow_periods',
        help_text='Asset this period belongs to'
    )
    
    # ------------------------------
    # Period Identification
    # ------------------------------
    period_number = models.IntegerField(
        help_text='Period number: 0 = acquisition, 1+ = monthly periods'
    )
    period_date = models.DateField(
        help_text='Month/year of this period (first day of month)'
    )
    
    # ------------------------------
    # Net Cash Flows (Summary)
    # ------------------------------
    # WHAT: Net cash flow from underwriting model (acquisition projections)
    net_cash_flow_underwritten = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Projected net cash flow from acquisition model (can be negative)'
    )
    
    # WHAT: Net cash flow from realized data (actual performance)
    net_cash_flow_realized = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Actual net cash flow (calculated from realized line items)'
    )
    
    # ------------------------------
    # Underwritten Line Items (Future)
    # ------------------------------
    # TODO: Add underwritten line items when acquisition model is expanded
    # underwritten_income_principal = models.DecimalField(...)
    # underwritten_income_interest = models.DecimalField(...)
    # underwritten_expense_servicing = models.DecimalField(...)
    # etc.
    
    # ------------------------------
    # Realized Line Items (Detailed)
    # ------------------------------
    # WHAT: Actual income collected during this period
    realized_income_principal = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Principal collected'
    )
    realized_income_interest = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Interest collected'
    )
    realized_income_rent = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Rent collected'
    )
    realized_income_cam = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='CAM income'
    )
    realized_income_mod_down_payment = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Modification down payment'
    )
    realized_net_liquidation_proceeds = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Net proceeds from liquidation'
    )
    
    # WHAT: Actual expenses incurred during this period
    realized_purchase_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Purchase price (period 0 only)'
    )
    realized_acq_due_diligence = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Due diligence expenses'
    )
    realized_acq_legal = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Acquisition legal expenses'
    )
    realized_acq_title = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Title expenses'
    )
    realized_expense_servicing = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Servicing fees'
    )
    realized_expense_am_fees = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Asset management fees'
    )
    realized_expense_property_tax = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Property taxes'
    )
    realized_expense_property_insurance = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Property insurance'
    )
    realized_legal_foreclosure = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Foreclosure legal fees'
    )
    realized_legal_bankruptcy = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Bankruptcy legal fees'
    )
    realized_reo_hoa = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='HOA fees'
    )
    realized_reo_utilities = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Utilities'
    )
    realized_reo_renovation = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Renovation costs'
    )
    realized_reo_property_preservation = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Property preservation'
    )
    realized_cre_marketing = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Marketing expenses'
    )
    realized_cre_maintenance = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text='Maintenance expenses'
    )
    
    # ------------------------------
    # Metadata
    # ------------------------------
    is_current_period = models.BooleanField(
        default=False,
        help_text='True if this is the current period (based on today\'s date)'
    )
    notes = models.TextField(
        blank=True,
        help_text='Optional notes for this period'
    )
    
    # Audit timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When this period record was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this period record was last updated'
    )
    
    class Meta:
        verbose_name = 'UW Cash Flows'
        verbose_name_plural = 'UW Cash Flows'
        ordering = ['asset_hub', 'period_number']
        unique_together = ('asset_hub', 'period_number')
        indexes = [
            models.Index(fields=['asset_hub', 'period_number']),
            models.Index(fields=['period_date']),
        ]
    
    def __str__(self) -> str:
        """Readable string for admin/debugging."""
        return f"UWCashFlowPeriod(asset={self.asset_hub_id}, period={self.period_number}, date={self.period_date})"
    
    @property
    def variance(self) -> float:
        """Calculate variance: realized - underwritten."""
        if self.net_cash_flow_realized is None or self.net_cash_flow_underwritten is None:
            return 0
        return float(self.net_cash_flow_realized - self.net_cash_flow_underwritten)
    
    @property
    def total_income(self) -> float:
        """Calculate total realized income for this period."""
        return sum([
            float(self.realized_income_principal or 0),
            float(self.realized_income_interest or 0),
            float(self.realized_income_rent or 0),
            float(self.realized_income_cam or 0),
            float(self.realized_income_mod_down_payment or 0),
            float(self.realized_net_liquidation_proceeds or 0),
        ])
    
    @property
    def total_expenses(self) -> float:
        """Calculate total realized expenses for this period."""
        return sum([
            float(self.realized_purchase_price or 0),
            float(self.realized_acq_due_diligence or 0),
            float(self.realized_acq_legal or 0),
            float(self.realized_acq_title or 0),
            float(self.realized_expense_servicing or 0),
            float(self.realized_expense_am_fees or 0),
            float(self.realized_expense_property_tax or 0),
            float(self.realized_expense_property_insurance or 0),
            float(self.realized_legal_foreclosure or 0),
            float(self.realized_legal_bankruptcy or 0),
            float(self.realized_reo_hoa or 0),
            float(self.realized_reo_utilities or 0),
            float(self.realized_reo_renovation or 0),
            float(self.realized_reo_property_preservation or 0),
            float(self.realized_cre_marketing or 0),
            float(self.realized_cre_maintenance or 0),
        ])
