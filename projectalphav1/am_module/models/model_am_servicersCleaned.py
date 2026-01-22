from __future__ import annotations

from django.db import models
from django.conf import settings
from django.utils import timezone


class ServicerLoanData(models.Model):
    """Model to manage loan data for servicers.
    This is a merged DB of all different servicers
    This model stores loan data, balance information, and origination details
    for assets managed by loan servicers. Each record is linked to an AssetIdHub via
    a ForeignKey relationship, allowing multiple records per asset over time (monthly snapshots).
    """

    # Core relationship
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='servicer_loan_data',
        help_text='Link to hub; multiple loan data records per asset over time.',
    )
    raw_source_snapshot = models.ForeignKey(  # WHAT: Audit trail linking cleaned record to the specific raw daily snapshot it was derived from (docs reviewed: https://docs.djangoproject.com/en/5.0/ref/models/fields/#foreignkey).
        'etl.SBDailyLoanData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cleaned_records',
        help_text='Links to the specific SBDailyLoanData snapshot this cleaned record was derived from for provenance tracking.',
    )
    
    # Reporting period
    reporting_year = models.PositiveSmallIntegerField(
        help_text='Year of this loan data snapshot (e.g., 2025).',
        null=True,
        blank=True,
    )
    reporting_month = models.PositiveSmallIntegerField(
        help_text='Month of this loan data snapshot (1-12).',
        null=True,
        blank=True,
        choices=[
            (1, 'January'),
            (2, 'February'),
            (3, 'March'),
            (4, 'April'),
            (5, 'May'),
            (6, 'June'),
            (7, 'July'),
            (8, 'August'),
            (9, 'September'),
            (10, 'October'),
            (11, 'November'),
            (12, 'December'),
        ],
    )
    reporting_day = models.PositiveSmallIntegerField(
        help_text='Day of this loan data snapshot (1-31).',
        null=True,
        blank=True,
    )

    # Current Loan Data
    investor_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text='Investor ID associated with the loan (stored as text to preserve long identifiers).',
    )
    servicer_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text='Servicer ID associated with the loan (stored as text to preserve long identifiers).',
    )
    previous_servicer_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text='Previous servicer ID associated with the loan (stored as text to preserve long identifiers).',
    )
    as_of_date = models.DateField(null=True, blank=True, help_text='Date this loan data was reported/effective.')
    address = models.CharField(max_length=255, null=True, blank=True, help_text='Address of the property.')
    city = models.CharField(max_length=100, null=True, blank=True, help_text='City of the property.')
    state = models.CharField(max_length=50, null=True, blank=True, help_text='State of the property.')
    zip_code = models.CharField(max_length=20, null=True, blank=True, help_text='Zip code of the property.')
    avm_date = models.DateField(null=True, blank=True, help_text='Date this loan data was reported/effective.')
    avm_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Current principal balance of the loan.')
    bpo_asis_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Current principal balance of the loan.')
    bpo_asis_date = models.DateField(null=True, blank=True, help_text='Date this loan data was reported/effective.')
    bpo_arv_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Current principal balance of the loan.')
    occupnacy = models.CharField(max_length=50, null=True, blank=True, help_text='Occupancy status.')
    borrower_last_name = models.CharField(max_length=100, null=True, blank=True, help_text='Last name of the borrower.')
    borrower_first_name = models.CharField(max_length=100, null=True, blank=True, help_text='First name of the borrower.')
    current_fico = models.IntegerField(null=True, blank=True, help_text='Current FICO score of the borrower.')
    current_fico_date = models.DateField(null=True, blank=True, help_text='Date this loan data was reported/effective.')
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Current principal balance of the loan.')
    deferred_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Portion of balance that has been deferred.')
    interest_rate = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text='Current interest rate (%).')
    next_due_date = models.DateField(null=True, blank=True, help_text='Next payment due date.')
    last_paid_date = models.DateField(null=True, blank=True, help_text='Date of last payment received.')
    current_pi = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Current principal balance of the loan.')
    current_ti = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Current interest balance of the loan.')
    piti = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Current principal balance of the loan.')
    term_remaining = models.IntegerField(null=True, blank=True, help_text='Remaining term in months.')
    escrow_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Current escrow account balance.')
    escrow_advance_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Escrow advances made by servicer.')
    third_party_recov_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Third party recoverable balance.')
    suspense_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Funds held in suspense.')
    servicer_late_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Late fees assessed by servicer.')
    other_charges = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Other charges on the loan.')
    interest_arrears = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Interest in arrears.')
    total_debt = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Total debt including all balances and fees.')
    lien_pos = models.IntegerField(null=True, blank=True, help_text='Lien position (1=first lien, 2=second lien, etc).')
    maturity_date = models.DateField(null=True, blank=True, help_text='Date when loan matures/is due in full.')

    # BPLS (Business Purpose Loan Servicer)
    default_rate = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text='Default interest rate (%).')

    # Origination Data
    origination_date = models.DateField(null=True, blank=True, help_text='Date when loan was originated.')
    origination_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Original loan balance at origination.')
    origination_interest_rate = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text='Original interest rate at origination (%).')
    original_appraised_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Original appraised value of the property.')
    original_appraised_date = models.DateField(null=True, blank=True, help_text='Date when loan was originated.')

    arm_flag = models.BooleanField(null=True, blank=True, help_text='ARM flag.')
    escrowed_flag = models.BooleanField(null=True, blank=True, help_text='Escrowed flag.')
    loan_type = models.CharField(max_length=50, null=True, blank=True, help_text='Loan type.')
    loan_warning = models.CharField(max_length=50, null=True, blank=True, help_text='Loan warning.')
    mba = models.BooleanField(null=True, blank=True, help_text='MBA flag.')
    
    bk_flag = models.BooleanField(null=True, blank=True, help_text='BK flag.')
    bk_ch = models.BooleanField(null=True, blank=True, help_text='BK change flag.')
    bk_current_status = models.CharField(max_length=50, null=True, blank=True, help_text='BK current status.')
    # Bankruptcy (BK) Fields
    bk_discharge_date = models.DateField(null=True, blank=True, help_text='Date of bankruptcy discharge.')
    bk_dismissed_date = models.DateField(null=True, blank=True, help_text='Date of bankruptcy dismissal.')
    bk_filed_date = models.DateField(null=True, blank=True, help_text='Date bankruptcy was filed.')
   
    # Foreclosure (FC) Fields
    fc_flag = models.BooleanField(null=True, blank=True, help_text='FC flag.')
    actual_fc_sale_date = models.DateField(null=True, blank=True, help_text='Actual date of the foreclosure sale.')
    date_referred_to_fc_atty = models.DateField(null=True, blank=True, help_text='Date referred to foreclosure attorney.')
    fc_completion_date = models.DateField(null=True, blank=True, help_text='Date foreclosure was completed.')
    fc_status = models.CharField(max_length=100, null=True, blank=True, help_text='Current status of the foreclosure.')
   
       # Property & Inspection Fields
    property_type = models.CharField(max_length=100, null=True, blank=True, help_text='Type of property.')

    
    # Resolution & Payoff Fields
    pif_date = models.DateField(null=True, blank=True, help_text='Paid-in-full date.')
   
    # Additional Loan & Status Fields
    acquired_date = models.DateField(null=True, blank=True, help_text='Date the loan was acquired.')
    inactive_date = models.DateField(null=True, blank=True, help_text='Date the loan became inactive.')
    prim_stat = models.CharField(max_length=100, null=True, blank=True, help_text='Primary status.')
    noi_expiration_date = models.DateField(null=True, blank=True, help_text='Notice of Intent expiration date.')
    total_principal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Total principal amount.')
    total_interest = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Total interest amount.')
    non_recoverable_principal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Non-recoverable principal.')
    non_recoverable_interest = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Non-recoverable interest.')
    non_recoverable_escrow = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Non-recoverable escrow.')
    non_recoverable_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Non-recoverable fees.')
    non_recoverable_corporate_advance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Non-recoverable corporate advance.')
    asset_manager = models.CharField(max_length=100, null=True, blank=True, help_text='Name of the asset manager.')
    collateral_count = models.IntegerField(null=True, blank=True, help_text='Number of collateral items.')
    current_loan_term = models.IntegerField(null=True, blank=True, help_text='Current term of the loan in months.')
    current_neg_am_bal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Current negative amortization balance.')
    deferred_interest = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Deferred interest amount.')
    deferred_principal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Deferred principal amount.')
    first_due_date = models.DateField(null=True, blank=True, help_text='First payment due date.')
    interest_method = models.CharField(max_length=100, null=True, blank=True, help_text='Method used for interest calculation.')
    last_escrow_analysis_date = models.DateField(null=True, blank=True, help_text='Date of the last escrow analysis.')
    legal_status = models.CharField(max_length=100, null=True, blank=True, help_text='Legal status of the loan.')
    loan_age = models.IntegerField(null=True, blank=True, help_text='Age of the loan in months.')
    mers_num = models.CharField(max_length=18, null=True, blank=True, help_text='MERS MIN number.')
    original_first_payment_date = models.DateField(null=True, blank=True, help_text='Original first payment date.')
    original_loan_term = models.IntegerField(null=True, blank=True, help_text='Original term of the loan in months.')
    original_maturity_date = models.DateField(null=True, blank=True, help_text='Original maturity date.')
    original_amt = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Original loan amount.')
    servicing_specialist = models.CharField(max_length=100, null=True, blank=True, help_text='Name of the servicing specialist.')
    trust_id = models.CharField(max_length=100, null=True, blank=True, help_text='ID of the trust.')
    balloon_date = models.DateField(null=True, blank=True, help_text='Date of the balloon payment.')
    balloon_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Amount of the balloon payment.')
    loan_purpose = models.CharField(max_length=100, null=True, blank=True, help_text='Purpose of the loan.')
    acquisition_or_sale_identifier = models.CharField(max_length=100, null=True, blank=True, help_text='Identifier for acquisition or sale.')

    
    # Audit fields
    created_at = models.DateTimeField(default=timezone.now, editable=False,
                                    help_text='Timestamp when record was created.')
    updated_at = models.DateTimeField(auto_now=True,
                                    help_text='Timestamp when record was last updated.')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_servicer_loan_data',
        help_text='User who created this record.',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_servicer_loan_data',
        help_text='User who last updated this record.',
    )

    class Meta:
        db_table = 'am_servicer_loan_data'
        verbose_name = 'Servicer Loan Data'
        verbose_name_plural = 'Servicer Loan Data'
        ordering = ['-reporting_year', '-reporting_month', '-as_of_date']
        indexes = [
            models.Index(fields=['asset_hub']),
            models.Index(fields=['reporting_year', 'reporting_month']),
            models.Index(fields=['as_of_date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['asset_hub', 'reporting_year', 'reporting_month'],
                name='unique_asset_reporting_period'
            ),
        ]

    def __str__(self):
        """String representation of the loan data."""
        hub_id = self.asset_hub.id if self.asset_hub else 'No Hub'
        period = f"{self.reporting_month}/{self.reporting_year}" if self.reporting_month and self.reporting_year else 'Unknown Period'
        return f"Loan Data for Hub #{hub_id} - {period}"

    def save(self, *args, **kwargs) -> None:  
        super().save(*args, **kwargs)


class _ServicerBase(models.Model):
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_%(class)s_records',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_%(class)s_records',
    )

    class Meta:
        abstract = True


class ServicerTrialBalanceData(_ServicerBase):
    """Cleaned EOM trial balance data (monthly snapshot)."""

    raw_source_snapshot = models.ForeignKey(
        'etl.EOMTrialBalanceData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cleaned_records',
    )

    file_date = models.DateField(null=True, blank=True, db_index=True)

    # Loan identification
    loan_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    investor_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    investor_loan_id = models.CharField(max_length=50, null=True, blank=True)

    # Borrower
    borrower_name = models.CharField(max_length=150, null=True, blank=True)

    # Balances
    principal_bal = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    escrow_bal = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    other_funds_bal = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    late_charge_bal = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    legal_fee_bal = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    deferred_prin = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    unapplied_bal = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    loss_draft_bal = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    asst_bal = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    nsf_fee_bal = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    oth_fee_bal = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    deferred_int = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    # Status and type
    primary_status = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    loan_type = models.CharField(max_length=50, null=True, blank=True)
    legal_status = models.CharField(max_length=50, null=True, blank=True)
    warning_status = models.CharField(max_length=50, null=True, blank=True)

    # Dates
    due_date = models.DateField(null=True, blank=True)
    date_inactive = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'am_servicer_trial_balance_data'
        verbose_name = 'Servicer Trial Balance Data'
        verbose_name_plural = 'Servicer Trial Balance Data'
        indexes = [
            models.Index(fields=['asset_hub']),
            models.Index(fields=['file_date']),
            models.Index(fields=['loan_id']),
            models.Index(fields=['investor_id']),
            models.Index(fields=['primary_status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['file_date', 'loan_id'],
                name='uniq_am_trial_fdate_loanid',
            ),
        ]


class ServicerForeclosureData(_ServicerBase):
    raw_source_snapshot = models.ForeignKey(
        'etl.SBDailyForeclosureData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cleaned_records',
    )

    file_date = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    loan_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    investor_id = models.CharField(max_length=50, null=True, blank=True)
    investor_loan_number = models.CharField(max_length=50, null=True, blank=True)
    prior_servicer_loan_number = models.CharField(max_length=50, null=True, blank=True)
    prior_servicer_name = models.CharField(max_length=100, null=True, blank=True)
    prior_servicer_contact = models.CharField(max_length=100, null=True, blank=True)
    prior_servicer_contact_phone = models.CharField(max_length=20, null=True, blank=True)
    legal_status = models.CharField(max_length=50, null=True, blank=True)
    prim_stat = models.CharField(max_length=50, null=True, blank=True)
    warning = models.CharField(max_length=255, null=True, blank=True)
    due_date = models.CharField(max_length=20, null=True, blank=True)
    loan_type = models.CharField(max_length=50, null=True, blank=True)
    original_loan_amount = models.CharField(max_length=50, null=True, blank=True)
    current_upb = models.CharField(max_length=50, null=True, blank=True)
    lien_position = models.CharField(max_length=10, null=True, blank=True)
    borrower_name = models.CharField(max_length=200, null=True, blank=True)
    borrower_first_name = models.CharField(max_length=100, null=True, blank=True)
    borrower_last_name = models.CharField(max_length=100, null=True, blank=True)
    borrower_deceased = models.CharField(max_length=10, null=True, blank=True)
    property_state = models.CharField(max_length=2, null=True, blank=True)
    property_zip = models.CharField(max_length=10, null=True, blank=True)
    mortgage_asgmnt_complete_date = models.CharField(max_length=20, null=True, blank=True)
    current_assignee = models.CharField(max_length=100, null=True, blank=True)
    mi_insurance = models.CharField(max_length=10, null=True, blank=True)
    mi_company_name = models.CharField(max_length=100, null=True, blank=True)
    mi_claim_filed = models.CharField(max_length=10, null=True, blank=True)
    mi_paid_amount = models.CharField(max_length=50, null=True, blank=True)
    mi_claim_paid_date = models.CharField(max_length=20, null=True, blank=True)
    bpo_date = models.CharField(max_length=20, null=True, blank=True)
    bpo_as_is_value = models.CharField(max_length=50, null=True, blank=True)
    bpo_repaired_value = models.CharField(max_length=50, null=True, blank=True)
    occupancy_status = models.CharField(max_length=50, null=True, blank=True)
    property_condition_from_inspection = models.CharField(max_length=255, null=True, blank=True)
    date_inspection_completed = models.CharField(max_length=20, null=True, blank=True)
    fc_attorney = models.CharField(max_length=100, null=True, blank=True)
    last_atty_note_date = models.CharField(max_length=20, null=True, blank=True)
    last_atty_note_topic = models.CharField(max_length=255, null=True, blank=True)
    last_atty_note = models.CharField(max_length=1000, null=True, blank=True)
    delinquent_taxes = models.CharField(max_length=10, null=True, blank=True)
    title_issue = models.CharField(max_length=255, null=True, blank=True)
    title_received = models.CharField(max_length=10, null=True, blank=True)
    fc_specialist = models.CharField(max_length=100, null=True, blank=True)
    date_breach_letter_sent = models.CharField(max_length=20, null=True, blank=True)
    noi_expiration_date = models.CharField(max_length=20, null=True, blank=True)
    original_fc_referral_date = models.CharField(max_length=20, null=True, blank=True)
    date_referred_to_fc_atty = models.CharField(max_length=20, null=True, blank=True)
    reason_for_default = models.CharField(max_length=255, null=True, blank=True)
    is_a_contested_fc = models.CharField(max_length=10, null=True, blank=True)
    current_fc_step = models.CharField(max_length=255, null=True, blank=True)
    fc_step_completed_date = models.CharField(max_length=20, null=True, blank=True)
    next_fc_step = models.CharField(max_length=255, null=True, blank=True)
    next_fc_step_due_date = models.CharField(max_length=20, null=True, blank=True)
    hold_start_date = models.CharField(max_length=20, null=True, blank=True)
    hold_reason = models.CharField(max_length=255, null=True, blank=True)
    hold_end_date = models.CharField(max_length=20, null=True, blank=True)
    projected_fc_sale_date = models.CharField(max_length=20, null=True, blank=True)
    scheduled_fc_sale_date = models.CharField(max_length=20, null=True, blank=True)
    actual_fc_sale_date = models.CharField(max_length=20, null=True, blank=True)
    bid_amount = models.CharField(max_length=50, null=True, blank=True)
    sale_amount = models.CharField(max_length=50, null=True, blank=True)
    sale_results = models.CharField(max_length=255, null=True, blank=True)
    rrc_expired = models.CharField(max_length=10, null=True, blank=True)
    fc_completion_date = models.CharField(max_length=20, null=True, blank=True)
    deed_recorded = models.CharField(max_length=10, null=True, blank=True)
    first_legal_action_date = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'am_servicer_foreclosure_data'
        verbose_name = 'Servicer Foreclosure Data'
        verbose_name_plural = 'Servicer Foreclosure Data'
        indexes = [
            models.Index(fields=['asset_hub']),
            models.Index(fields=['file_date']),
            models.Index(fields=['loan_id']),
        ]


class ServicerBankruptcyData(_ServicerBase):
    raw_source_snapshot = models.ForeignKey(
        'etl.SBDailyBankruptcyData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cleaned_records',
    )

    asset_manager = models.CharField(max_length=100, null=True, blank=True)
    file_date = models.CharField(max_length=20, null=True, blank=True)
    loan_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    investor_loan_id = models.CharField(max_length=50, null=True, blank=True)
    previous_ln_num = models.CharField(max_length=50, null=True, blank=True)
    acquisition_date = models.CharField(max_length=20, null=True, blank=True)
    loan_due_date = models.CharField(max_length=20, null=True, blank=True)
    mba = models.CharField(max_length=50, null=True, blank=True)
    legal = models.CharField(max_length=50, null=True, blank=True)
    warning = models.CharField(max_length=255, null=True, blank=True)
    investor_id = models.CharField(max_length=50, null=True, blank=True)
    chapter = models.CharField(max_length=20, null=True, blank=True)
    case_number = models.CharField(max_length=50, null=True, blank=True)
    bk_filed_date = models.CharField(max_length=20, null=True, blank=True)
    state_filed = models.CharField(max_length=2, null=True, blank=True)
    filing_court = models.CharField(max_length=255, null=True, blank=True)
    filing_borrower = models.CharField(max_length=200, null=True, blank=True)
    joint_filer = models.CharField(max_length=200, null=True, blank=True)
    trustee_name = models.CharField(max_length=200, null=True, blank=True)
    statebridge_atty_name = models.CharField(max_length=200, null=True, blank=True)
    borrower_atty_name = models.CharField(max_length=200, null=True, blank=True)
    bankruptcy_status = models.CharField(max_length=50, null=True, blank=True)
    prepetition_claim_amt = models.CharField(max_length=50, null=True, blank=True)
    active_plan = models.CharField(max_length=10, null=True, blank=True)
    plan_start_date = models.CharField(max_length=20, null=True, blank=True)
    pre_petition_payment = models.CharField(max_length=50, null=True, blank=True)
    plan_length = models.CharField(max_length=20, null=True, blank=True)
    projected_plan_end_date = models.CharField(max_length=20, null=True, blank=True)
    actual_plan_completion_date = models.CharField(max_length=20, null=True, blank=True)
    last_pre_petition_payment_rcvd_date = models.CharField(max_length=20, null=True, blank=True)
    last_payment_applied = models.CharField(max_length=20, null=True, blank=True)
    pre_petition_balance = models.CharField(max_length=50, null=True, blank=True)
    stipulation_claim_amt = models.CharField(max_length=50, null=True, blank=True)
    stipulation_date = models.CharField(max_length=20, null=True, blank=True)
    stipulation_first_pmt_date = models.CharField(max_length=20, null=True, blank=True)
    stipulation_last_pmt_date = models.CharField(max_length=20, null=True, blank=True)
    stipulation_monthly_pmt = models.CharField(max_length=50, null=True, blank=True)
    stipulation_repay_months = models.CharField(max_length=20, null=True, blank=True)
    last_stipulation_payment_rcvd_date = models.CharField(max_length=20, null=True, blank=True)
    first_post_petition_due_date = models.CharField(max_length=20, null=True, blank=True)
    next_post_petition_due_date = models.CharField(max_length=20, null=True, blank=True)
    post_petition_pmt_amt = models.CharField(max_length=50, null=True, blank=True)
    bk_case_closed_date = models.CharField(max_length=20, null=True, blank=True)
    bk_discharge_date = models.CharField(max_length=20, null=True, blank=True)
    bk_dismissed_date = models.CharField(max_length=20, null=True, blank=True)
    date_motion_for_relief_filed = models.CharField(max_length=20, null=True, blank=True)
    date_proof_of_claim_filed = models.CharField(max_length=20, null=True, blank=True)
    date_of_meeting_of_creditors = models.CharField(max_length=20, null=True, blank=True)
    date_object_to_confirmation_filed = models.CharField(max_length=20, null=True, blank=True)
    relief_date = models.CharField(max_length=20, null=True, blank=True)
    bankruptcy_business_area_status = models.CharField(max_length=50, null=True, blank=True)
    bankruptcy_business_area_status_date = models.CharField(max_length=20, null=True, blank=True)
    order_of_confirmation_date = models.CharField(max_length=20, null=True, blank=True)
    active_bankruptcy = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = 'am_servicer_bankruptcy_data'
        verbose_name = 'Servicer Bankruptcy Data'
        verbose_name_plural = 'Servicer Bankruptcy Data'
        indexes = [
            models.Index(fields=['asset_hub']),
            models.Index(fields=['file_date']),
            models.Index(fields=['loan_id']),
            models.Index(fields=['case_number']),
        ]


class ServicerCommentData(_ServicerBase):
    raw_source_snapshot = models.ForeignKey(
        'etl.SBDailyCommentData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cleaned_records',
    )

    investor_id = models.CharField(max_length=50, null=True, blank=True)
    file_date = models.CharField(max_length=20, null=True, blank=True)
    loan_number = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    investor_loan_number = models.CharField(max_length=50, null=True, blank=True)
    prior_servicer_loan_number = models.CharField(max_length=50, null=True, blank=True)
    comment_date = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    department = models.CharField(max_length=50, null=True, blank=True)
    comment = models.CharField(max_length=4000, null=True, blank=True)
    additional_notes = models.CharField(max_length=4000, null=True, blank=True)
    row_hash = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        db_table = 'am_servicer_comment_data'
        verbose_name = 'Servicer Comment Data'
        verbose_name_plural = 'Servicer Comment Data'
        indexes = [
            models.Index(fields=['asset_hub']),
            models.Index(fields=['file_date']),
            models.Index(fields=['loan_number']),
            models.Index(fields=['comment_date']),
        ]


class ServicerPayHistoryData(_ServicerBase):
    raw_source_snapshot = models.ForeignKey(
        'etl.SBDailyPayHistoryData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cleaned_records',
    )

    investor = models.CharField(max_length=50, null=True, blank=True)
    file_date = models.CharField(max_length=20, null=True, blank=True)
    loan_number = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    previous_ln_num = models.CharField(max_length=50, null=True, blank=True)
    borrower_name = models.CharField(max_length=200, null=True, blank=True)
    property_address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    zip = models.CharField(max_length=10, null=True, blank=True)
    property_type = models.CharField(max_length=50, null=True, blank=True)
    number_of_units = models.CharField(max_length=10, null=True, blank=True)
    occupancy_status = models.CharField(max_length=50, null=True, blank=True)
    original_upb = models.CharField(max_length=50, null=True, blank=True)
    second_upb = models.CharField(max_length=50, null=True, blank=True)
    current_upb = models.CharField(max_length=50, null=True, blank=True)
    account_type = models.CharField(max_length=50, null=True, blank=True)
    lien = models.CharField(max_length=10, null=True, blank=True)
    loan_term = models.CharField(max_length=20, null=True, blank=True)
    remaining_term = models.CharField(max_length=20, null=True, blank=True)
    maturity_date = models.CharField(max_length=20, null=True, blank=True)
    rate_type = models.CharField(max_length=50, null=True, blank=True)
    arm = models.CharField(max_length=10, null=True, blank=True)
    balloon = models.CharField(max_length=10, null=True, blank=True)
    piggyback = models.CharField(max_length=10, null=True, blank=True)
    current_ir = models.CharField(max_length=50, null=True, blank=True)
    current_pi = models.CharField(max_length=50, null=True, blank=True)
    current_ti = models.CharField(max_length=50, null=True, blank=True)
    current_piti = models.CharField(max_length=50, null=True, blank=True)
    last_full_payment_dt = models.CharField(max_length=20, null=True, blank=True)
    next_payment_due_dt = models.CharField(max_length=20, null=True, blank=True)
    escrow_indicator = models.CharField(max_length=10, null=True, blank=True)
    restricted_escrow = models.CharField(max_length=10, null=True, blank=True)
    escrow_advance = models.CharField(max_length=50, null=True, blank=True)
    rec_corp_advance_balance = models.CharField(max_length=50, null=True, blank=True)
    third_party_rec_balance = models.CharField(max_length=50, null=True, blank=True)
    accrued_interest = models.CharField(max_length=50, null=True, blank=True)
    accrued_late_fees = models.CharField(max_length=50, null=True, blank=True)
    fc_status = models.CharField(max_length=50, null=True, blank=True)
    fc_type = models.CharField(max_length=50, null=True, blank=True)
    fc_first_legal_filed_dt = models.CharField(max_length=20, null=True, blank=True)
    fc_judgement_entered_dt = models.CharField(max_length=20, null=True, blank=True)
    fc_sale_scheduled_dt = models.CharField(max_length=20, null=True, blank=True)
    fc_suspended_dt = models.CharField(max_length=20, null=True, blank=True)
    fc_removal_dt = models.CharField(max_length=20, null=True, blank=True)
    fc_removal_description = models.CharField(max_length=255, null=True, blank=True)
    bk_status = models.CharField(max_length=50, null=True, blank=True)
    bk_code = models.CharField(max_length=20, null=True, blank=True)
    bk_filing_date = models.CharField(max_length=20, null=True, blank=True)
    bk_case_number = models.CharField(max_length=50, null=True, blank=True)
    bk_removal_dt = models.CharField(max_length=20, null=True, blank=True)
    original_appraised_value = models.CharField(max_length=50, null=True, blank=True)
    as_is_bpo = models.CharField(max_length=50, null=True, blank=True)
    bpo_date = models.CharField(max_length=20, null=True, blank=True)
    fico_original = models.CharField(max_length=20, null=True, blank=True)
    fico = models.CharField(max_length=20, null=True, blank=True)
    fico_date = models.CharField(max_length=20, null=True, blank=True)
    loan_mod_dt = models.CharField(max_length=20, null=True, blank=True)
    mod_upb = models.CharField(max_length=50, null=True, blank=True)
    mod_ir = models.CharField(max_length=50, null=True, blank=True)
    mod_pi = models.CharField(max_length=50, null=True, blank=True)
    mod_first_payment_dt = models.CharField(max_length=20, null=True, blank=True)
    mod_maturity = models.CharField(max_length=20, null=True, blank=True)
    origination_date = models.CharField(max_length=20, null=True, blank=True)
    original_principal = models.CharField(max_length=50, null=True, blank=True)
    orig_rate = models.CharField(max_length=50, null=True, blank=True)
    fp_date = models.CharField(max_length=20, null=True, blank=True)
    mt_date = models.CharField(max_length=20, null=True, blank=True)
    interest_only_indicator = models.CharField(max_length=10, null=True, blank=True)
    interest_only_expiration_dt = models.CharField(max_length=20, null=True, blank=True)
    hoi_expiration_dt = models.CharField(max_length=20, null=True, blank=True)
    m0 = models.CharField(max_length=20, null=True, blank=True)
    m1 = models.CharField(max_length=20, null=True, blank=True)
    m2 = models.CharField(max_length=20, null=True, blank=True)
    m3 = models.CharField(max_length=20, null=True, blank=True)
    m4 = models.CharField(max_length=20, null=True, blank=True)
    m5 = models.CharField(max_length=20, null=True, blank=True)
    m6 = models.CharField(max_length=20, null=True, blank=True)
    m7 = models.CharField(max_length=20, null=True, blank=True)
    m8 = models.CharField(max_length=20, null=True, blank=True)
    m9 = models.CharField(max_length=20, null=True, blank=True)
    m10 = models.CharField(max_length=20, null=True, blank=True)
    m11 = models.CharField(max_length=20, null=True, blank=True)
    m12 = models.CharField(max_length=20, null=True, blank=True)
    id0_0 = models.CharField(max_length=50, null=True, blank=True, db_column="ID0 0 - $")
    id0_1 = models.CharField(max_length=50, null=True, blank=True, db_column="ID0 1 - $")
    id0_2 = models.CharField(max_length=50, null=True, blank=True, db_column="ID0 2 - $")
    id0_3 = models.CharField(max_length=50, null=True, blank=True, db_column="ID0 3 - $")
    id0_4 = models.CharField(max_length=50, null=True, blank=True, db_column="ID0 4 - $")
    id0_5 = models.CharField(max_length=50, null=True, blank=True, db_column="ID0 5 - $")
    id0_6 = models.CharField(max_length=50, null=True, blank=True, db_column="ID0 6 - $")
    id0_7 = models.CharField(max_length=50, null=True, blank=True, db_column="ID0 7 - $")
    id0_8 = models.CharField(max_length=50, null=True, blank=True, db_column="ID0 8 - $")
    id0_9 = models.CharField(max_length=50, null=True, blank=True, db_column="ID0 9 - $")
    id0_10 = models.CharField(max_length=50, null=True, blank=True, db_column="ID0 10 - $")
    id0_11 = models.CharField(max_length=50, null=True, blank=True, db_column="ID0 11 - $")
    id0_12 = models.CharField(max_length=50, null=True, blank=True, db_column="ID0 12 - $")

    class Meta:
        db_table = 'am_servicer_pay_history_data'
        verbose_name = 'Servicer Pay History Data'
        verbose_name_plural = 'Servicer Pay History Data'
        indexes = [
            models.Index(fields=['asset_hub']),
            models.Index(fields=['file_date']),
            models.Index(fields=['loan_number']),
        ]


class ServicerTransactionData(_ServicerBase):
    raw_source_snapshot = models.ForeignKey(
        'etl.SBDailyTransactionData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cleaned_records',
    )

    investor_id = models.CharField(max_length=50, null=True, blank=True)
    file_date = models.CharField(max_length=20, null=True, blank=True)
    loan_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    previous_ln_num = models.CharField(max_length=50, null=True, blank=True)
    loan_transaction_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    transaction_date = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    transaction_code = models.CharField(max_length=50, null=True, blank=True)
    transaction_description = models.CharField(max_length=255, null=True, blank=True)
    effective_date = models.CharField(max_length=20, null=True, blank=True)
    transaction_amt = models.CharField(max_length=50, null=True, blank=True)
    due_date = models.CharField(max_length=20, null=True, blank=True)
    principal_amount = models.CharField(max_length=50, null=True, blank=True)
    interest_amount = models.CharField(max_length=50, null=True, blank=True)
    suspense_paid = models.CharField(max_length=50, null=True, blank=True)
    non_recoverable_advance = models.CharField(max_length=50, null=True, blank=True)
    recoverable_advance = models.CharField(max_length=50, null=True, blank=True)
    corporate_advance_reason_code = models.CharField(max_length=50, null=True, blank=True)
    escrow_advance_balance = models.CharField(max_length=50, null=True, blank=True)
    escrow_amount = models.CharField(max_length=50, null=True, blank=True)
    restricted_escrow = models.CharField(max_length=10, null=True, blank=True)
    fee_code = models.CharField(max_length=50, null=True, blank=True)
    fee_description = models.CharField(max_length=255, null=True, blank=True)
    unapplied_pmt = models.CharField(max_length=50, null=True, blank=True)
    stipulation_unapplied_pmt = models.CharField(max_length=50, null=True, blank=True)
    pre_petition_unapplied_pmt = models.CharField(max_length=50, null=True, blank=True)
    asset_manager = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'am_servicer_transaction_data'
        verbose_name = 'Servicer Transaction Data'
        verbose_name_plural = 'Servicer Transaction Data'
        indexes = [
            models.Index(fields=['asset_hub']),
            models.Index(fields=['file_date']),
            models.Index(fields=['loan_id']),
            models.Index(fields=['loan_transaction_id']),
            models.Index(fields=['transaction_date']),
        ]


class ServicerArmData(_ServicerBase):
    raw_source_snapshot = models.ForeignKey(
        'etl.SBDailyArmData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cleaned_records',
    )

    file_date = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    loan_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    loan_number = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    investor_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    previous_ln_num = models.CharField(max_length=255, null=True, blank=True)
    manual_adjustment = models.CharField(max_length=255, null=True, blank=True)
    audit_flag = models.CharField(max_length=255, null=True, blank=True)
    carry_over_flag = models.CharField(max_length=255, null=True, blank=True)
    convertible_flag = models.CharField(max_length=255, null=True, blank=True)
    current_index = models.CharField(max_length=255, null=True, blank=True)
    floor_rate = models.CharField(max_length=255, null=True, blank=True)
    frst_chg_period_dec = models.CharField(max_length=255, null=True, blank=True)
    frst_chg_period_inc = models.CharField(max_length=255, null=True, blank=True)
    frst_pichg_date = models.CharField(max_length=255, null=True, blank=True)
    frst_rate_chg_date = models.CharField(max_length=255, null=True, blank=True)
    index = models.CharField(max_length=255, null=True, blank=True)
    letter_lead_days = models.CharField(max_length=255, null=True, blank=True)
    lookback_period = models.CharField(max_length=255, null=True, blank=True)
    margin = models.CharField(max_length=255, null=True, blank=True)
    life_rate_decrease = models.CharField(max_length=255, null=True, blank=True)
    life_rate_increase = models.CharField(max_length=255, null=True, blank=True)
    min_rate_chg = models.CharField(max_length=255, null=True, blank=True)
    period_rate_dec = models.CharField(max_length=255, null=True, blank=True)
    period_rate_inc = models.CharField(max_length=255, null=True, blank=True)
    neg_am_cap_flag = models.CharField(max_length=255, null=True, blank=True)
    neg_am_cap = models.CharField(max_length=255, null=True, blank=True)
    next_pichg_date = models.CharField(max_length=255, null=True, blank=True)
    next_rate_chg_date = models.CharField(max_length=255, null=True, blank=True)
    original_index = models.CharField(max_length=255, null=True, blank=True)
    original_int_rate = models.CharField(max_length=255, null=True, blank=True)
    original_pipmt = models.CharField(max_length=255, null=True, blank=True)
    pichg_frequency = models.CharField(max_length=255, null=True, blank=True)
    pipmt_cap_flag = models.CharField(max_length=255, null=True, blank=True)
    pipmt_cap = models.CharField(max_length=255, null=True, blank=True)
    rate_calc = models.CharField(max_length=255, null=True, blank=True)
    rate_chg_frequency = models.CharField(max_length=255, null=True, blank=True)
    rounding = models.CharField(max_length=255, null=True, blank=True)
    rounding_factor = models.CharField(max_length=255, null=True, blank=True)
    teaser_rate = models.CharField(max_length=255, null=True, blank=True)
    tot_carry_over_percent = models.CharField(max_length=255, null=True, blank=True)
    investor_margin = models.CharField(max_length=255, null=True, blank=True)
    recast_year = models.CharField(max_length=255, null=True, blank=True)
    pipmt_down_cap = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'am_servicer_arm_data'
        verbose_name = 'Servicer ARM Data'
        verbose_name_plural = 'Servicer ARM Data'
        indexes = [
            models.Index(fields=['asset_hub']),
            models.Index(fields=['file_date']),
            models.Index(fields=['loan_id']),
            models.Index(fields=['loan_number']),
        ]