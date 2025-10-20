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
        'am_module.SBDailyLoanData',
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
    investor_id = models.IntegerField(null=True, blank=True, help_text='Investor ID associated with the loan.')
    servicer_id = models.IntegerField(null=True, blank=True, help_text='Servicer ID associated with the loan.')
    previous_servicer_id = models.IntegerField(null=True, blank=True, help_text='Previous servicer ID associated with the loan.')
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
    bk_plan_end_date = models.DateField(null=True, blank=True, help_text='End date of the BK plan.')
    bk_plan_length = models.IntegerField(null=True, blank=True, help_text='Length of the BK plan in months.')
    bk_plan_start_date = models.DateField(null=True, blank=True, help_text='Start date of the BK plan.')
    bk_post_petition_due_date = models.DateField(null=True, blank=True, help_text='Post-petition due date.')
    bk_case_closed_date = models.DateField(null=True, blank=True, help_text='Date the BK case was closed.')
    date_motion_for_relief_filed = models.DateField(null=True, blank=True, help_text='Date Motion for Relief was filed.')
    date_object_to_confirmation_filed = models.DateField(null=True, blank=True, help_text='Date Objection to Confirmation was filed.')
    date_of_meeting_of_creditors = models.DateField(null=True, blank=True, help_text='Date of the Meeting of Creditors.')
    date_proof_of_claim_filed = models.DateField(null=True, blank=True, help_text='Date Proof of Claim was filed.')
    relief_date = models.DateField(null=True, blank=True, help_text='Date relief was granted.')
    prepetition_unapplied_bal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Pre-petition unapplied balance.')
    stipulation_unapplied_bal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Stipulation unapplied balance.')

    # Foreclosure (FC) Fields
    fc_flag = models.BooleanField(null=True, blank=True, help_text='FC flag.')
    actual_fc_sale_date = models.DateField(null=True, blank=True, help_text='Actual date of the foreclosure sale.')
    date_referred_to_fc_atty = models.DateField(null=True, blank=True, help_text='Date referred to foreclosure attorney.')
    fc_completion_date = models.DateField(null=True, blank=True, help_text='Date foreclosure was completed.')
    fc_status = models.CharField(max_length=100, null=True, blank=True, help_text='Current status of the foreclosure.')
    foreclosure_business_area_status_date = models.DateField(null=True, blank=True, help_text='Date of the foreclosure business area status.')
    foreclosure_business_area_status = models.CharField(max_length=100, null=True, blank=True, help_text='Status from the foreclosure business area.')
    is_a_contested_fc = models.BooleanField(null=True, blank=True, help_text='Is the foreclosure contested?')
    reason_for_default = models.CharField(max_length=255, null=True, blank=True, help_text='Reason for the loan default.')
    scheduled_fc_sale_date = models.DateField(null=True, blank=True, help_text='Scheduled date for the foreclosure sale.')
    days_in_foreclosure = models.IntegerField(null=True, blank=True, help_text='Number of days in foreclosure.')

    # Loss Mitigation & Workout Fields
    date_breach_letter_sent = models.DateField(null=True, blank=True, help_text='Date the breach letter was sent.')
    dil_completion_date = models.DateField(null=True, blank=True, help_text='Deed-in-Lieu completion date.')
    loss_mitigation_business_area_status_date = models.DateField(null=True, blank=True, help_text='Date of the loss mitigation business area status.')
    loss_mitigation_business_area_status = models.CharField(max_length=100, null=True, blank=True, help_text='Status from the loss mitigation business area.')
    loss_mitigation_start_date = models.DateField(null=True, blank=True, help_text='Date loss mitigation started.')
    loss_mitigation_status = models.CharField(max_length=100, null=True, blank=True, help_text='Current status of loss mitigation.')
    workout_option = models.CharField(max_length=100, null=True, blank=True, help_text='Selected workout option.')
    loan_modification_date = models.DateField(null=True, blank=True, help_text='Date of loan modification.')
    loan_modification_status = models.CharField(max_length=100, null=True, blank=True, help_text='Status of the loan modification.')
    modification_type = models.CharField(max_length=100, null=True, blank=True, help_text='Type of loan modification.')
    number_of_payments = models.IntegerField(null=True, blank=True, help_text='Number of payments in the plan.')
    post_modification_principal_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Principal balance after modification.')
    repayment_plan_agreement_date = models.DateField(null=True, blank=True, help_text='Date of the repayment plan agreement.')
    repayment_plan_start_date = models.DateField(null=True, blank=True, help_text='Start date of the repayment plan.')
    repayment_plan_status = models.CharField(max_length=100, null=True, blank=True, help_text='Status of the repayment plan.')
    repay_plan_type = models.CharField(max_length=100, null=True, blank=True, help_text='Type of repayment plan.')
    forgive_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Amount of principal forgiven.')
    balance_after_forgive = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Balance after forgiveness.')
    mod_extended_maturity = models.DateField(null=True, blank=True, help_text='Extended maturity date after modification.')
    mod_forbearance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Forbearance amount in modification.')
    mod_forgiven = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Amount forgiven in modification.')
    modified_first_payment_date = models.DateField(null=True, blank=True, help_text='First payment date after modification.')
    total_capitalized_by_mod = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Total amount capitalized by modification.')

    # Property & Inspection Fields
    date_inspection_completed = models.DateField(null=True, blank=True, help_text='Date of the last inspection.')
    first_time_vacant_date = models.DateField(null=True, blank=True, help_text='Date the property was first found to be vacant.')
    forceplaced_flood_insurance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Cost of force-placed flood insurance.')
    forceplaced_hazard_insurance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Cost of force-placed hazard insurance.')
    is_house_for_sale = models.BooleanField(null=True, blank=True, help_text='Is the house currently for sale?')
    neighborhood_condition = models.CharField(max_length=100, null=True, blank=True, help_text='Condition of the neighborhood.')
    property_condition_from_inspection = models.CharField(max_length=100, null=True, blank=True, help_text='Property condition from inspection.')
    property_county = models.CharField(max_length=100, null=True, blank=True, help_text='County of the property.')
    property_type = models.CharField(max_length=100, null=True, blank=True, help_text='Type of property.')

    # Borrower & Contact Fields
    borrower_home_phone = models.CharField(max_length=20, null=True, blank=True, help_text='Home phone number of the borrower.')
    borrower_count = models.IntegerField(null=True, blank=True, help_text='Number of borrowers on the loan.')
    co_borrower_fico = models.IntegerField(null=True, blank=True, help_text='FICO score of the co-borrower.')
    co_borrower_fico_date = models.DateField(null=True, blank=True, help_text='Date of the co-borrower FICO score.')
    follow_up_date = models.DateField(null=True, blank=True, help_text='Date for next follow-up.')
    last_contact_outcome = models.CharField(max_length=255, null=True, blank=True, help_text='Outcome of the last contact.')
    last_successful_contact_date = models.DateField(null=True, blank=True, help_text='Date of the last successful contact.')
    promise_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Promised payment amount.')
    promise_date = models.DateField(null=True, blank=True, help_text='Date of the promised payment.')
    right_party_type = models.CharField(max_length=100, null=True, blank=True, help_text='Type of right party contacted.')
    right_party_date = models.DateField(null=True, blank=True, help_text='Date of right party contact.')
    single_point_of_contact = models.CharField(max_length=100, null=True, blank=True, help_text='Single point of contact for the loan.')

    # ARM Fields
    next_arm_rate_change_date = models.DateField(null=True, blank=True, help_text='Next ARM rate change date.')
    convert_to_fixed_rate = models.BooleanField(null=True, blank=True, help_text='Was the loan converted to a fixed rate?')
    max_rate = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text='Maximum interest rate for an ARM loan.')
    min_rate = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text='Minimum interest rate for an ARM loan.')
    first_periodic_rate_cap = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text='First periodic rate cap for an ARM.')
    periodic_rate_cap = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text='Periodic rate cap for an ARM.')
    life_cap = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text='Lifetime rate cap for an ARM.')
    arm_audit_status = models.CharField(max_length=100, null=True, blank=True, help_text='Status of the ARM audit.')
    arm_first_rate_change_date = models.DateField(null=True, blank=True, help_text='First rate change date for the ARM.')
    is_pay_option_arm = models.BooleanField(null=True, blank=True, help_text='Is this a pay-option ARM?')
    pay_option_negative_am_factor = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text='Negative amortization factor for pay-option ARM.')
    within_pay_option_period = models.BooleanField(null=True, blank=True, help_text='Is the loan within the pay-option period?')

    # MI (Mortgage Insurance) Fields
    mi_company_name = models.CharField(max_length=100, null=True, blank=True, help_text='Mortgage insurance company name.')
    mi_active_policy = models.BooleanField(null=True, blank=True, help_text='Is the MI policy active?')
    mi_certificate_number = models.CharField(max_length=100, null=True, blank=True, help_text='MI certificate number.')
    mi_claim = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='MI claim amount.')
    mi_claim_status = models.CharField(max_length=100, null=True, blank=True, help_text='Status of the MI claim.')
    mi_coverage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='MI coverage percentage.')
    mi_date_closed = models.DateField(null=True, blank=True, help_text='Date the MI claim was closed.')
    mi_date_paid = models.DateField(null=True, blank=True, help_text='Date the MI claim was paid.')
    mi_last_review_date = models.DateField(null=True, blank=True, help_text='Last review date for the MI policy.')
    mi_paid_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Amount paid by MI.')
    mi_rescind_date = models.DateField(null=True, blank=True, help_text='Date the MI policy was rescinded.')
    mi_rescind_reason = models.CharField(max_length=255, null=True, blank=True, help_text='Reason for MI policy rescission.')
    mi_claim_filed_date = models.DateField(null=True, blank=True, help_text='Date the MI claim was filed.')

    # Resolution & Payoff Fields
    pif_date = models.DateField(null=True, blank=True, help_text='Paid-in-full date.')
    pif_quote_date = models.DateField(null=True, blank=True, help_text='Date the PIF quote was generated.')
    res_service_fee_paid = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Resolution service fee paid.')
    resolution_corporate_advance_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Resolution corporate advance balance.')
    resolution_escrow_advance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Resolution escrow advance.')
    resolution_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Resolution fees.')
    resolution_post_date = models.DateField(null=True, blank=True, help_text='Date the resolution was posted.')
    resolution_proceeds = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Proceeds from the resolution.')
    resolution_type = models.CharField(max_length=100, null=True, blank=True, help_text='Type of resolution.')
    resolution_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Balance at resolution.')
    ss_complete = models.BooleanField(null=True, blank=True, help_text='Short sale complete flag.')
    ss_proceeds_rcvd = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Short sale proceeds received.')
    deferred_advance_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Deferred advance balance.')

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

    # Pre-Modification Fields
    pre_modification_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Balance before modification.')
    pre_modification_coupon = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text='Coupon rate before modification.')
    pre_modification_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Payment amount before modification.')

    # Post-Modification Fields
    post_modification_coupon = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text='Coupon rate after modification.')
    post_modification_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Payment amount after modification.')

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
            # Ensure we don't have duplicate entries for the same asset in the same month/year
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