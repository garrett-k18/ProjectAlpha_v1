from django.db import models
from django.utils import timezone
from acq_module.models.seller import SellerRawData
import re

# The SellerBoardedData model represents boarded seller data transferred from the acq_module. 
# It contains all relevant data points from SellerRawData, along with trade information, 
# including trade name, trade ID, and seller name.

class SellerBoardedData(models.Model):
    """Model for boarded seller data transferred from acq_module.
    Contains all data points from SellerRawData plus trade name, trade_id, seller name.
    """
    # Property Type choices - Inheriting from SellerRawData via import
    # Occupancy choices - Inheriting from SellerRawData via import
    # Asset status choices - Inheriting from SellerRawData via import
    
    # Original seller and trade references (using ID values for future-proofing)
    acq_seller_id = models.IntegerField(help_text="ID reference to the original Seller model in acq_module", null=True)
    acq_trade_id = models.IntegerField(help_text="ID reference to the original Trade model in acq_module", null=True)
    # Stable hub link (1:1) – the boarded record for this hub/asset
    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='am_boarded',
        help_text='One boarded record per hub/asset.',
    )
    
    # String representations for display and reporting
    seller_name = models.CharField(max_length=100, null=True, blank=True)
    trade_name = models.CharField(max_length=100, null=True, blank=True)
    
    # Asset data fields from SellerRawData
    sellertape_id = models.CharField(max_length=64, null=True, blank=True)
    sellertape_altid = models.CharField(max_length=64, null=True, blank=True)
    asset_status = models.CharField(max_length=100, choices=SellerRawData.ASSET_STATUS_CHOICES, null=True, blank=True)
    
    # Property information
    street_address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip = models.CharField(max_length=100, null=True, blank=True)
    class PropertyType(models.TextChoices):
        """Mirror acquisition property types so boarded data stays in sync.

        Using TextChoices ensures Django validation + form rendering constrain values
        without relying on free-form strings. Aligns with SellerRawData.PROPERTY_TYPE_CHOICES.
        Docs: https://docs.djangoproject.com/en/stable/ref/models/fields/#enumeration-types
        """

        SFR = 'SFR', 'SFR'
        MANUFACTURED = 'Manufactured', 'Manufactured'
        CONDO = 'Condo', 'Condo'
        TWO_TO_FOUR_FAMILY = '2-4 Family', '2-4 Family'
        LAND = 'Land', 'Land'
        MULTIFAMILY = 'Multifamily 5+', 'Multifamily 5+'

    property_type = models.CharField(
        max_length=100,
        choices=PropertyType.choices,
        default=PropertyType.SFR,
        null=True,
        blank=True,
        help_text='Categorized property type synced with acquisition import definitions.',
    )
    occupancy = models.CharField(max_length=100, choices=SellerRawData.OCCUPANCY_CHOICES, default=SellerRawData.OCCUPANCY_UNKNOWN, null=True, blank=True)
    year_built = models.IntegerField(null=True, blank=True)
    sq_ft = models.IntegerField(null=True, blank=True)
    lot_size = models.IntegerField(null=True, blank=True)
    beds = models.IntegerField(null=True, blank=True)
    baths = models.IntegerField(null=True, blank=True)
    
    # Loan balance information
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    deferred_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    last_paid_date = models.DateField(null=True, blank=True)
    
    # Loan origination information
    first_pay_date = models.DateField(null=True, blank=True)
    origination_date = models.DateField(null=True, blank=True)
    original_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    original_term = models.IntegerField(null=True, blank=True)
    original_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    original_maturity_date = models.DateField(null=True, blank=True)
    
    # Additional loan information
    default_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    months_dlq = models.IntegerField(null=True, blank=True)
    current_maturity_date = models.DateField(null=True, blank=True)
    current_term = models.IntegerField(null=True, blank=True)
    
    # Balances and fees
    accrued_note_interest = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    accrued_default_interest = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    escrow_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    escrow_advance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    recoverable_corp_advance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    late_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    other_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    suspense_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_debt = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # Valuation information
    origination_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    origination_arv = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    origination_value_date = models.DateField(null=True, blank=True)
    
    seller_value_date = models.DateField(null=True, blank=True)
    seller_arv_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    seller_asis_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    additional_asis_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    additional_arv_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    additional_value_date = models.DateField(null=True, blank=True)

    # Foreclosure information
    fc_flag = models.BooleanField(null=True, blank=True, default=None)
    fc_first_legal_date = models.DateField(null=True, blank=True)
    fc_referred_date = models.DateField(null=True, blank=True)
    fc_judgement_date = models.DateField(null=True, blank=True)
    fc_scheduled_sale_date = models.DateField(null=True, blank=True)
    fc_sale_date = models.DateField(null=True, blank=True)
    fc_starting = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # Bankruptcy information
    bk_flag = models.BooleanField(null=True, blank=True, default=None)
    bk_chapter = models.CharField(max_length=10, null=True, blank=True)
    
    # Modification information
    mod_flag = models.BooleanField(null=True, blank=True, default=None)
    mod_date = models.DateField(null=True, blank=True)
    mod_maturity_date = models.DateField(null=True, blank=True)
    mod_term = models.IntegerField(null=True, blank=True)
    mod_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    mod_initial_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)    

    # Boarding information
    boarded_at = models.DateTimeField(auto_now_add=True, help_text="When this record was boarded into the AM module")
    boarded_by = models.CharField(max_length=100, null=True, blank=True, help_text="User who initiated the boarding process")
    
    # Standard timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Boarded Seller Data"
        verbose_name_plural = "Boarded Seller Data"
        indexes = [
            models.Index(fields=['id']),  # Primary key index
            models.Index(fields=['asset_status']),
            models.Index(fields=['acq_seller_id']),
            models.Index(fields=['acq_trade_id']),
            models.Index(fields=['state']),
            models.Index(fields=['sellertape_id']),
        ]
        ordering = ['-boarded_at']  
    
    def save(self, *args, **kwargs):
        """Override save method without mutating any boarded fields.

        Behavior:
        - Do not normalize or transform any values. Data is assumed to be
          pre-cleaned by the acquisition module before boarding.
        - Persist exactly as provided.
        """
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Boarded Data {self.id} - {self.seller_name} - {self.trade_name}"


# -----------------------------------------------------------------------------------
# Blended Outcome Model (One-to-one with SellerBoardedData)
# -----------------------------------------------------------------------------------
class BlendedOutcomeModel(models.Model):
    """
    BlendedOutcomeModel stores the acquisition modeling snapshot for a boarded asset.

    Relationship:
    - Strict 1:1 with SellerBoardedData so each boarded asset has at most one
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

    # ------------------------------
    # Cost / Proceeds / Timing
    # ------------------------------

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
    property_preservation_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The property preservation cost.")
    month_insurance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total yearly insurance cost.")
    month_property_tax = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total yearly property tax cost.")
    month_hoa = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total yearly HOA costs.")
    month_utility = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total yearly utility costs.")
    month_other = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="The total yearly other costs.")

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

    # ------------------------------
    # Cash flow periods (P1..P30)
    # ------------------------------
    # Stored as currency decimals; can be positive (inflows) or negative (outflows).
    cf_p0 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 0 (currency; can be negative). THis will be bid amount plus any period 0 costs")
    cf_p1 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 1 (currency; can be negative).")
    cf_p2 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 2 (currency; can be negative).")
    cf_p3 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 3 (currency; can be negative).")
    cf_p4 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 4 (currency; can be negative).")
    cf_p5 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 5 (currency; can be negative).")
    cf_p6 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 6 (currency; can be negative).")
    cf_p7 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 7 (currency; can be negative).")
    cf_p8 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 8 (currency; can be negative).")
    cf_p9 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 9 (currency; can be negative).")
    cf_p10 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 10 (currency; can be negative).")
    cf_p11 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 11 (currency; can be negative).")
    cf_p12 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 12 (currency; can be negative).")
    cf_p13 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 13 (currency; can be negative).")
    cf_p14 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 14 (currency; can be negative).")
    cf_p15 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 15 (currency; can be negative).")
    cf_p16 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 16 (currency; can be negative).")
    cf_p17 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 17 (currency; can be negative).")
    cf_p18 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 18 (currency; can be negative).")
    cf_p19 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 19 (currency; can be negative).")
    cf_p20 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 20 (currency; can be negative).")
    cf_p21 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 21 (currency; can be negative).")
    cf_p22 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 22 (currency; can be negative).")
    cf_p23 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 23 (currency; can be negative).")
    cf_p24 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 24 (currency; can be negative).")
    cf_p25 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 25 (currency; can be negative).")
    cf_p26 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 26 (currency; can be negative).")
    cf_p27 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 27 (currency; can be negative).")
    cf_p28 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 28 (currency; can be negative).")
    cf_p29 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 29 (currency; can be negative).")
    cf_p30 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Cash flow period 30 (currency; can be negative).")

    
    
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
