from django.db import models


class SBDailyLoanData(models.Model):
    """
    RAW DATA LANDING TABLE - All fields are CharField to accept data as-is.

    WHAT: Store StateBridge daily loan snapshots exactly as received.
    WHY: Raw data may have formatting issues, invalid values, encoding problems.
    HOW: Accept everything as strings, defer validation to ETL → ServicerLoanData.

    PATTERN:
    1. SBDailyLoanData (this table) = Raw strings, no validation
    2. ETL cleaning process = Parse, validate, transform
    3. ServicerLoanData = Typed fields with constraints
    """

    # Basic Loan Information
    date = models.CharField(max_length=20, null=True, blank=True)
    investor_id = models.CharField(max_length=50, null=True, blank=True)
    loan_number = models.CharField(max_length=50, null=True, blank=True)
    investor_loan_number = models.CharField(max_length=50, null=True, blank=True)
    prior_servicer_loan_number = models.CharField(max_length=50, null=True, blank=True)

    # Appraisal Information
    avm_appraisal_date = models.CharField(max_length=20, null=True, blank=True)
    avm_appraisal_type = models.CharField(max_length=50, null=True, blank=True)
    avm_appraisal_value = models.CharField(max_length=50, null=True, blank=True)
    original_appraisal_date = models.CharField(max_length=20, null=True, blank=True)
    original_appraisal_value = models.CharField(max_length=50, null=True, blank=True)

    # BPO Information
    bpo_as_is_value = models.CharField(max_length=50, null=True, blank=True)
    bpo_date = models.CharField(max_length=20, null=True, blank=True)
    bpo_repaired_value = models.CharField(max_length=50, null=True, blank=True)

    # Borrower Information
    borrower_first_name = models.CharField(max_length=100, null=True, blank=True)
    borrower_last_name = models.CharField(max_length=100, null=True, blank=True)
    borrower_home_phone = models.CharField(max_length=20, null=True, blank=True)
    borrower_count = models.CharField(max_length=20, null=True, blank=True)

    # Financial Information
    corporate_advance_balance = models.CharField(max_length=50, null=True, blank=True)
    current_upb = models.CharField(max_length=50, null=True, blank=True)
    current_interest_rate = models.CharField(max_length=50, null=True, blank=True)
    current_principal_and_interest_payment = models.CharField(max_length=50, null=True, blank=True)
    current_taxes_and_insurance_payment = models.CharField(max_length=50, null=True, blank=True)

    # FICO Information
    current_fico_date = models.CharField(max_length=20, null=True, blank=True)
    current_fico = models.CharField(max_length=20, null=True, blank=True)
    co_borrower_fico = models.CharField(max_length=20, null=True, blank=True)
    co_borrower_fico_date = models.CharField(max_length=20, null=True, blank=True)

    # Payment Information
    date_last_payment_received = models.CharField(max_length=20, null=True, blank=True)
    due_date = models.CharField(max_length=20, null=True, blank=True)
    first_due_date = models.CharField(max_length=20, null=True, blank=True)

    # Escrow Information
    escrow_advance_balance = models.CharField(max_length=50, null=True, blank=True)
    escrow_balance = models.CharField(max_length=50, null=True, blank=True)
    is_escrowed = models.CharField(max_length=10, null=True, blank=True)
    restricted_escrow = models.CharField(max_length=10, null=True, blank=True)
    last_escrow_analysis_date = models.CharField(max_length=20, null=True, blank=True)

    # Loan Characteristics
    is_arm = models.CharField(max_length=10, null=True, blank=True)
    lien_position = models.CharField(max_length=10, null=True, blank=True)
    loan_status = models.CharField(max_length=50, null=True, blank=True)
    loan_type = models.CharField(max_length=50, null=True, blank=True)
    loan_purpose = models.CharField(max_length=50, null=True, blank=True)
    loan_warning = models.CharField(max_length=255, null=True, blank=True)
    mba = models.CharField(max_length=50, null=True, blank=True)
    occupancy_status = models.CharField(max_length=50, null=True, blank=True)
    legal_status = models.CharField(max_length=50, null=True, blank=True)

    # Property Information
    property_state = models.CharField(max_length=2, null=True, blank=True)
    property_zip = models.CharField(max_length=10, null=True, blank=True)
    property_address = models.CharField(max_length=255, null=True, blank=True)
    property_city = models.CharField(max_length=100, null=True, blank=True)
    property_county = models.CharField(max_length=100, null=True, blank=True)
    property_type = models.CharField(max_length=50, null=True, blank=True)

    # Bankruptcy Information
    active_bk_plan = models.CharField(max_length=10, null=True, blank=True)
    bankruptcy_business_area_status_date = models.CharField(max_length=20, null=True, blank=True)
    bankruptcy_business_area_status = models.CharField(max_length=50, null=True, blank=True)
    bk_case_number = models.CharField(max_length=50, null=True, blank=True)
    bk_chapter = models.CharField(max_length=10, null=True, blank=True)
    bk_court_district = models.CharField(max_length=100, null=True, blank=True)
    bk_discharge_date = models.CharField(max_length=20, null=True, blank=True)
    bk_dismissed_date = models.CharField(max_length=20, null=True, blank=True)
    bk_filed_date = models.CharField(max_length=20, null=True, blank=True)
    bk_plan_end_date = models.CharField(max_length=20, null=True, blank=True)
    bk_plan_length = models.CharField(max_length=20, null=True, blank=True)
    bk_plan_start_date = models.CharField(max_length=20, null=True, blank=True)
    bk_post_petition_due_date = models.CharField(max_length=20, null=True, blank=True)
    bk_case_closed_date = models.CharField(max_length=20, null=True, blank=True)

    # Bankruptcy Process Dates
    date_motion_for_relief_filed = models.CharField(max_length=20, null=True, blank=True)
    date_object_to_confirmation_filed = models.CharField(max_length=20, null=True, blank=True)
    date_of_meeting_of_creditors = models.CharField(max_length=20, null=True, blank=True)
    date_proof_of_claim_filed = models.CharField(max_length=20, null=True, blank=True)
    relief_date = models.CharField(max_length=20, null=True, blank=True)

    # Foreclosure Information
    actual_fc_sale_date = models.CharField(max_length=20, null=True, blank=True)
    date_referred_to_fc_atty = models.CharField(max_length=20, null=True, blank=True)
    fc_completion_date = models.CharField(max_length=20, null=True, blank=True)
    fc_status = models.CharField(max_length=50, null=True, blank=True)
    foreclosure_business_area_status_date = models.CharField(max_length=20, null=True, blank=True)
    foreclosure_business_area_status = models.CharField(max_length=50, null=True, blank=True)
    is_a_contested_fc = models.CharField(max_length=10, null=True, blank=True)
    reason_for_default = models.CharField(max_length=255, null=True, blank=True)
    scheduled_fc_sale_date = models.CharField(max_length=20, null=True, blank=True)
    days_in_foreclosure = models.CharField(max_length=20, null=True, blank=True)

    # Loss Mitigation
    date_breach_letter_sent = models.CharField(max_length=20, null=True, blank=True)
    dil_completion_date = models.CharField(max_length=20, null=True, blank=True)
    loss_mitigation_business_area_status_date = models.CharField(max_length=20, null=True, blank=True)
    loss_mitigation_business_area_status = models.CharField(max_length=50, null=True, blank=True)
    loss_mitigation_start_date = models.CharField(max_length=20, null=True, blank=True)
    loss_mitigation_status = models.CharField(max_length=50, null=True, blank=True)
    workout_option = models.CharField(max_length=50, null=True, blank=True)

    # Loan Modification
    convert_to_fixed_rate = models.CharField(max_length=10, null=True, blank=True)
    loan_modification_date = models.CharField(max_length=20, null=True, blank=True)
    loan_modification_status = models.CharField(max_length=50, null=True, blank=True)
    number_of_payments = models.CharField(max_length=20, null=True, blank=True)
    post_modification_principal_balance = models.CharField(max_length=50, null=True, blank=True)
    pre_modification_balance = models.CharField(max_length=50, null=True, blank=True)
    post_modification_coupon = models.CharField(max_length=50, null=True, blank=True)
    post_modification_payment = models.CharField(max_length=50, null=True, blank=True)
    pre_modification_coupon = models.CharField(max_length=50, null=True, blank=True)
    pre_modification_payment = models.CharField(max_length=50, null=True, blank=True)
    total_capitalized_by_mod = models.CharField(max_length=50, null=True, blank=True)
    modification_type = models.CharField(max_length=50, null=True, blank=True)
    modified_first_payment_date = models.CharField(max_length=20, null=True, blank=True)
    mod_extended_maturity = models.CharField(max_length=20, null=True, blank=True)
    mod_forbearance = models.CharField(max_length=50, null=True, blank=True)
    mod_forgiven = models.CharField(max_length=50, null=True, blank=True)

    # Repayment Plans
    repayment_plan_agreement_date = models.CharField(max_length=20, null=True, blank=True)
    repayment_plan_start_date = models.CharField(max_length=20, null=True, blank=True)
    repayment_plan_status = models.CharField(max_length=50, null=True, blank=True)
    repay_plan_type = models.CharField(max_length=50, null=True, blank=True)

    # Property Condition & Inspection
    date_inspection_completed = models.CharField(max_length=20, null=True, blank=True)
    deferred_advance_balance = models.CharField(max_length=50, null=True, blank=True)
    first_time_vacant_date = models.CharField(max_length=20, null=True, blank=True)
    follow_up_date = models.CharField(max_length=20, null=True, blank=True)
    is_house_for_sale = models.CharField(max_length=10, null=True, blank=True)
    neighborhood_condition = models.CharField(max_length=50, null=True, blank=True)
    property_condition_from_inspection = models.CharField(max_length=255, null=True, blank=True)

    # Insurance
    forceplaced_flood_insurance = models.CharField(max_length=50, null=True, blank=True)
    forceplaced_hazard_insurance = models.CharField(max_length=50, null=True, blank=True)

    # Contact Information
    last_contact_outcome = models.CharField(max_length=255, null=True, blank=True)
    last_successful_contact_date = models.CharField(max_length=20, null=True, blank=True)

    # ARM Information
    next_arm_rate_change_date = models.CharField(max_length=20, null=True, blank=True)
    arm_audit_status = models.CharField(max_length=50, null=True, blank=True)
    arm_first_rate_change_date = models.CharField(max_length=20, null=True, blank=True)
    max_rate = models.CharField(max_length=50, null=True, blank=True)
    min_rate = models.CharField(max_length=50, null=True, blank=True)
    first_periodic_rate_cap = models.CharField(max_length=50, null=True, blank=True)
    periodic_rate_cap = models.CharField(max_length=50, null=True, blank=True)
    life_cap = models.CharField(max_length=50, null=True, blank=True)
    is_pay_option_arm = models.CharField(max_length=10, null=True, blank=True)
    pay_option_negative_amort_factor = models.CharField(max_length=50, null=True, blank=True)
    within_pay_option_period = models.CharField(max_length=10, null=True, blank=True)
    current_neg_am_bal = models.CharField(max_length=50, null=True, blank=True)

    # Payoff Information
    pif_date = models.CharField(max_length=20, null=True, blank=True)
    pif_quote_date = models.CharField(max_length=20, null=True, blank=True)

    # Promise Information
    promise_amount = models.CharField(max_length=50, null=True, blank=True)
    promise_date = models.CharField(max_length=20, null=True, blank=True)

    # Resolution Information
    res_service_fee_paid = models.CharField(max_length=50, null=True, blank=True)
    resolution_corporate_advance_balance = models.CharField(max_length=50, null=True, blank=True)
    resolution_escrow_advance = models.CharField(max_length=50, null=True, blank=True)
    resolution_fees = models.CharField(max_length=50, null=True, blank=True)
    resolution_post_date = models.CharField(max_length=20, null=True, blank=True)
    resolution_proceeds = models.CharField(max_length=50, null=True, blank=True)
    resolution_type = models.CharField(max_length=50, null=True, blank=True)
    resolution_balance = models.CharField(max_length=50, null=True, blank=True)

    # Status Fields
    ss_complete = models.CharField(max_length=10, null=True, blank=True)
    ss_proceeds_rcvd = models.CharField(max_length=10, null=True, blank=True)
    acquired_date = models.CharField(max_length=20, null=True, blank=True)
    inactive_date = models.CharField(max_length=20, null=True, blank=True)
    prim_stat = models.CharField(max_length=50, null=True, blank=True)
    noi_expiration_date = models.CharField(max_length=20, null=True, blank=True)

    # Forgiveness
    forgive_amount = models.CharField(max_length=50, null=True, blank=True)
    balance_after_forgive = models.CharField(max_length=50, null=True, blank=True)

    # Additional Financial Fields
    acquisition_or_sale_identifier = models.CharField(max_length=10, null=True, blank=True)
    total_principal = models.CharField(max_length=50, null=True, blank=True)
    total_interest = models.CharField(max_length=50, null=True, blank=True)

    # Non-Recoverable Amounts
    non_recoverable_principal = models.CharField(max_length=50, null=True, blank=True)
    non_recoverable_interest = models.CharField(max_length=50, null=True, blank=True)
    non_recoverable_escrow = models.CharField(max_length=50, null=True, blank=True)
    non_recoverable_fees = models.CharField(max_length=50, null=True, blank=True)
    non_recoverable_corporate_advance = models.CharField(max_length=50, null=True, blank=True)
    non_recoverable_corp_adv_balance = models.CharField(max_length=50, null=True, blank=True)

    # Loan Terms
    collateral_count = models.CharField(max_length=20, null=True, blank=True)
    current_loan_term = models.CharField(max_length=20, null=True, blank=True)
    deferred_interest = models.CharField(max_length=50, null=True, blank=True)
    deferred_principal = models.CharField(max_length=50, null=True, blank=True)
    prior_deferred_principal = models.CharField(max_length=50, null=True, blank=True)
    interest_method = models.CharField(max_length=50, null=True, blank=True)
    loan_age = models.CharField(max_length=20, null=True, blank=True)
    maturity_date = models.CharField(max_length=20, null=True, blank=True)
    original_maturity_date = models.CharField(max_length=20, null=True, blank=True)
    original_loan_term = models.CharField(max_length=20, null=True, blank=True)
    original_amt = models.CharField(max_length=50, null=True, blank=True)
    original_first_payment_date = models.CharField(max_length=20, null=True, blank=True)
    origination_date = models.CharField(max_length=20, null=True, blank=True)
    remaining_term = models.CharField(max_length=20, null=True, blank=True)

    # MERS and Trust Information
    mers_num = models.CharField(max_length=50, null=True, blank=True, help_text="MERS Number")
    trust_id = models.CharField(max_length=50, null=True, blank=True)

    # Mortgage Insurance
    mi_company_name = models.CharField(max_length=100, null=True, blank=True)
    mi_active_policy = models.CharField(max_length=10, null=True, blank=True)
    mi_certificate_number = models.CharField(max_length=50, null=True, blank=True)
    mi_claim = models.CharField(max_length=50, null=True, blank=True)
    mi_claim_status = models.CharField(max_length=50, null=True, blank=True)
    mi_claim_filed_date = models.CharField(max_length=20, null=True, blank=True)
    mi_coverage = models.CharField(max_length=50, null=True, blank=True)
    mi_date_closed = models.CharField(max_length=20, null=True, blank=True)
    mi_date_paid = models.CharField(max_length=20, null=True, blank=True)
    mi_last_review_date = models.CharField(max_length=20, null=True, blank=True)
    mi_paid_amount = models.CharField(max_length=50, null=True, blank=True)
    mi_rescind_date = models.CharField(max_length=20, null=True, blank=True)
    mi_rescind_reason = models.CharField(max_length=255, null=True, blank=True)

    # Balloon Information
    balloon_date = models.CharField(max_length=20, null=True, blank=True)
    balloon_payment = models.CharField(max_length=50, null=True, blank=True)

    # Contact and Service Information
    asset_manager = models.CharField(max_length=100, null=True, blank=True)
    servicing_specialist = models.CharField(max_length=100, null=True, blank=True)
    single_point_of_contact = models.CharField(max_length=100, null=True, blank=True)
    right_party_type = models.CharField(max_length=50, null=True, blank=True)
    right_party_date = models.CharField(max_length=20, null=True, blank=True)

    # Balance Information
    prepetition_unapplied_bal = models.CharField(max_length=50, null=True, blank=True)
    stipulation_unapplied_bal = models.CharField(max_length=50, null=True, blank=True)
    unapplied_balance = models.CharField(max_length=50, null=True, blank=True)

    # Due Amounts
    total_due = models.CharField(max_length=50, null=True, blank=True)
    principal_due = models.CharField(max_length=50, null=True, blank=True)
    interest_due = models.CharField(max_length=50, null=True, blank=True)
    escrow_due = models.CharField(max_length=50, null=True, blank=True)
    legal_fees = models.CharField(max_length=50, null=True, blank=True)
    other_fees = models.CharField(max_length=50, null=True, blank=True)
    nsf_fees = models.CharField(max_length=50, null=True, blank=True)
    accrued_late_fees = models.CharField(max_length=50, null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loan_records'
        verbose_name = 'StateBridge Daily Loan Data'
        verbose_name_plural = 'StateBridge Daily Loan Data'

        indexes = [
            models.Index(fields=['loan_number'], name='loan_record_loan_nu_a822c9_idx'),
            models.Index(fields=['investor_loan_number'], name='loan_record_investo_ffcd41_idx'),
            models.Index(fields=['borrower_last_name', 'borrower_first_name'], name='loan_record_borrowe_073caf_idx'),
            models.Index(fields=['property_state', 'property_zip'], name='loan_record_propert_164947_idx'),
            models.Index(fields=['loan_status'], name='loan_record_loan_st_08b3b3_idx'),
            models.Index(fields=['date'], name='loan_record_date_f4c38c_idx'),
            models.Index(fields=['loan_number', 'date'], name='loan_record_loan_nu_c13584_idx'),
        ]

    def __str__(self):
        return f"Loan {self.loan_number} - {self.borrower_last_name}, {self.borrower_first_name}"

    @property
    def full_borrower_name(self):
        """Returns full borrower name"""
        if self.borrower_first_name and self.borrower_last_name:
            return f"{self.borrower_first_name} {self.borrower_last_name}"
        return self.borrower_last_name or self.borrower_first_name or "Unknown"

    @property
    def full_property_address(self):
        """Returns formatted property address"""
        parts = [self.property_address, self.property_city, self.property_state, self.property_zip]
        return ", ".join([part for part in parts if part])


class SBDailyArmData(models.Model):
    file_date = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    loan_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    loan_number = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    investor_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    row_data = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "arm_records"
        verbose_name = "StateBridge Daily ARM Data"
        verbose_name_plural = "StateBridge Daily ARM Data"

        indexes = [
            models.Index(fields=["loan_number"], name="arm_record_loan_nu_3e7fdc_idx"),
            models.Index(fields=["loan_id"], name="arm_record_loan_id_1e6f7e_idx"),
            models.Index(fields=["investor_id"], name="arm_record_investo_8fbe0c_idx"),
            models.Index(fields=["file_date"], name="arm_record_file_d_24dd7b_idx"),
        ]


class SBDailyForeclosureData(models.Model):

    # Basic File and Loan Information
    file_date = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    loan_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    investor_id = models.CharField(max_length=50, null=True, blank=True)
    investor_loan_number = models.CharField(max_length=50, null=True, blank=True)
    prior_servicer_loan_number = models.CharField(max_length=50, null=True, blank=True)
    prior_servicer_name = models.CharField(max_length=100, null=True, blank=True)
    prior_servicer_contact = models.CharField(max_length=100, null=True, blank=True)
    prior_servicer_contact_phone = models.CharField(max_length=20, null=True, blank=True)

    # Loan Status Information
    legal_status = models.CharField(max_length=50, null=True, blank=True)
    prim_stat = models.CharField(max_length=50, null=True, blank=True)
    warning = models.CharField(max_length=255, null=True, blank=True)
    due_date = models.CharField(max_length=20, null=True, blank=True)
    loan_type = models.CharField(max_length=50, null=True, blank=True)
    original_loan_amount = models.CharField(max_length=50, null=True, blank=True)
    current_upb = models.CharField(max_length=50, null=True, blank=True)
    lien_position = models.CharField(max_length=10, null=True, blank=True)

    # Borrower Information
    borrower_name = models.CharField(max_length=200, null=True, blank=True)
    borrower_first_name = models.CharField(max_length=100, null=True, blank=True)
    borrower_last_name = models.CharField(max_length=100, null=True, blank=True)
    borrower_deceased = models.CharField(max_length=10, null=True, blank=True)

    # Property Information
    property_state = models.CharField(max_length=2, null=True, blank=True)
    property_zip = models.CharField(max_length=10, null=True, blank=True)

    # Assignment Information
    mortgage_asgmnt_complete_date = models.CharField(max_length=20, null=True, blank=True)
    current_assignee = models.CharField(max_length=100, null=True, blank=True)

    # Mortgage Insurance Information
    mi_insurance = models.CharField(max_length=10, null=True, blank=True)
    mi_company_name = models.CharField(max_length=100, null=True, blank=True)
    mi_claim_filed = models.CharField(max_length=10, null=True, blank=True)
    mi_paid_amount = models.CharField(max_length=50, null=True, blank=True)
    mi_claim_paid_date = models.CharField(max_length=20, null=True, blank=True)

    # Property Valuation Information
    bpo_date = models.CharField(max_length=20, null=True, blank=True)
    bpo_as_is_value = models.CharField(max_length=50, null=True, blank=True)
    bpo_repaired_value = models.CharField(max_length=50, null=True, blank=True)
    occupancy_status = models.CharField(max_length=50, null=True, blank=True)
    property_condition_from_inspection = models.CharField(max_length=255, null=True, blank=True)
    date_inspection_completed = models.CharField(max_length=20, null=True, blank=True)

    # Foreclosure Information
    fc_attorney = models.CharField(max_length=100, null=True, blank=True)
    last_atty_note_date = models.CharField(max_length=20, null=True, blank=True)
    last_atty_note_topic = models.CharField(max_length=255, null=True, blank=True)
    last_atty_note = models.CharField(max_length=1000, null=True, blank=True)
    delinquent_taxes = models.CharField(max_length=10, null=True, blank=True)
    title_issue = models.CharField(max_length=255, null=True, blank=True)
    title_received = models.CharField(max_length=10, null=True, blank=True)
    fc_specialist = models.CharField(max_length=100, null=True, blank=True)

    # Foreclosure Process Dates
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

    # Hold Information
    hold_start_date = models.CharField(max_length=20, null=True, blank=True)
    hold_reason = models.CharField(max_length=255, null=True, blank=True)
    hold_end_date = models.CharField(max_length=20, null=True, blank=True)

    # Sale Information
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

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "foreclosure_records"
        verbose_name = "StateBridge Daily Foreclosure Data"
        verbose_name_plural = "StateBridge Daily Foreclosure Data"

        indexes = [
            models.Index(fields=["loan_id"], name="foreclosure_loan_id_0679d9_idx"),
            models.Index(fields=["investor_loan_number"], name="foreclosure_investo_cb2199_idx"),
            models.Index(
                fields=["borrower_last_name", "borrower_first_name"],
                name="foreclosure_borrowe_ddceb2_idx",
            ),
            models.Index(
                fields=["property_state", "property_zip"],
                name="foreclosure_propert_977e84_idx",
            ),
            models.Index(fields=["legal_status"], name="foreclosure_legal_s_309be1_idx"),
            models.Index(fields=["file_date"], name="foreclosure_file_da_c4958f_idx"),
            models.Index(
                fields=["loan_id", "file_date"],
                name="foreclosure_loan_id_59c89d_idx",
            ),
        ]

    def __str__(self):
        return f"Foreclosure {self.loan_id} - {self.borrower_last_name}, {self.borrower_first_name}"


class SBDailyBankruptcyData(models.Model):

    # Basic Loan Information
    asset_manager = models.CharField(max_length=100, null=True, blank=True)
    loan_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    investor_loan_id = models.CharField(max_length=50, null=True, blank=True)
    previous_ln_num = models.CharField(max_length=50, null=True, blank=True)
    acquisition_date = models.CharField(max_length=20, null=True, blank=True)
    loan_due_date = models.CharField(max_length=20, null=True, blank=True)
    mba = models.CharField(max_length=50, null=True, blank=True)
    legal = models.CharField(max_length=50, null=True, blank=True)
    warning = models.CharField(max_length=255, null=True, blank=True)
    investor_id = models.CharField(max_length=50, null=True, blank=True)

    # Bankruptcy Case Information
    chapter = models.CharField(max_length=20, null=True, blank=True)
    case_number = models.CharField(max_length=50, null=True, blank=True)
    bk_filed_date = models.CharField(max_length=20, null=True, blank=True)
    state_filed = models.CharField(max_length=2, null=True, blank=True)
    filing_court = models.CharField(max_length=255, null=True, blank=True)
    filing_borrower = models.CharField(max_length=200, null=True, blank=True)
    joint_filer = models.CharField(max_length=200, null=True, blank=True)

    # Contact Information
    trustee_name = models.CharField(max_length=200, null=True, blank=True)
    statebridge_atty_name = models.CharField(max_length=200, null=True, blank=True)
    borrower_atty_name = models.CharField(max_length=200, null=True, blank=True)

    # Status Information
    bankruptcy_status = models.CharField(max_length=50, null=True, blank=True)
    prepetition_claim_amt = models.CharField(max_length=50, null=True, blank=True)
    active_plan = models.CharField(max_length=10, null=True, blank=True)

    # Plan Information
    plan_start_date = models.CharField(max_length=20, null=True, blank=True)
    pre_petition_payment = models.CharField(max_length=50, null=True, blank=True)
    plan_length = models.CharField(max_length=20, null=True, blank=True)
    projected_plan_end_date = models.CharField(max_length=20, null=True, blank=True)
    actual_plan_completion_date = models.CharField(max_length=20, null=True, blank=True)

    # Payment Information
    last_pre_petition_payment_rcvd_date = models.CharField(max_length=20, null=True, blank=True)
    last_payment_applied = models.CharField(max_length=20, null=True, blank=True)
    pre_petition_balance = models.CharField(max_length=50, null=True, blank=True)

    # Stipulation Information
    stipulation_claim_amt = models.CharField(max_length=50, null=True, blank=True)
    stipulation_date = models.CharField(max_length=20, null=True, blank=True)
    stipulation_first_pmt_date = models.CharField(max_length=20, null=True, blank=True)
    stipulation_last_pmt_date = models.CharField(max_length=20, null=True, blank=True)
    stipulation_monthly_pmt = models.CharField(max_length=50, null=True, blank=True)
    stipulation_repay_months = models.CharField(max_length=20, null=True, blank=True)
    last_stipulation_payment_rcvd_date = models.CharField(max_length=20, null=True, blank=True)

    # Post Petition Information
    first_post_petition_due_date = models.CharField(max_length=20, null=True, blank=True)
    next_post_petition_due_date = models.CharField(max_length=20, null=True, blank=True)
    post_petition_pmt_amt = models.CharField(max_length=50, null=True, blank=True)

    # Case Status Dates
    bk_case_closed_date = models.CharField(max_length=20, null=True, blank=True)
    bk_discharge_date = models.CharField(max_length=20, null=True, blank=True)
    bk_dismissed_date = models.CharField(max_length=20, null=True, blank=True)

    # Legal Process Dates
    date_motion_for_relief_filed = models.CharField(max_length=20, null=True, blank=True)
    date_proof_of_claim_filed = models.CharField(max_length=20, null=True, blank=True)
    date_of_meeting_of_creditors = models.CharField(max_length=20, null=True, blank=True)
    date_object_to_confirmation_filed = models.CharField(max_length=20, null=True, blank=True)
    relief_date = models.CharField(max_length=20, null=True, blank=True)

    # Business Area Status
    bankruptcy_business_area_status = models.CharField(max_length=50, null=True, blank=True)
    bankruptcy_business_area_status_date = models.CharField(max_length=20, null=True, blank=True)
    order_of_confirmation_date = models.CharField(max_length=20, null=True, blank=True)
    active_bankruptcy = models.CharField(max_length=10, null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bankruptcy_records"
        verbose_name = "StateBridge Daily Bankruptcy Data"
        verbose_name_plural = "StateBridge Daily Bankruptcy Data"

        indexes = [
            models.Index(fields=["loan_id"], name="bankruptcy__loan_id_0b2105_idx"),
            models.Index(fields=["investor_loan_id"], name="bankruptcy__investo_55480c_idx"),
            models.Index(fields=["case_number"], name="bankruptcy__case_nu_8d6298_idx"),
            models.Index(fields=["filing_borrower"], name="bankruptcy__filing__a7e889_idx"),
            models.Index(fields=["bankruptcy_status"], name="bankruptcy__bankrup_dc4437_idx"),
            models.Index(fields=["bk_filed_date"], name="bankruptcy__bk_file_3512a6_idx"),
            models.Index(
                fields=["loan_id", "bk_filed_date"],
                name="bankruptcy__loan_id_d2e610_idx",
            ),
        ]

    def __str__(self):
        return f"Bankruptcy {self.loan_id} - Case {self.case_number}"


class SBDailyCommentData(models.Model):

    # Basic Loan Information
    investor_id = models.CharField(max_length=50, null=True, blank=True)
    loan_number = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    investor_loan_number = models.CharField(max_length=50, null=True, blank=True)
    prior_servicer_loan_number = models.CharField(max_length=50, null=True, blank=True)

    # Comment Information
    comment_date = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    department = models.CharField(max_length=50, null=True, blank=True)
    comment = models.CharField(max_length=4000, null=True, blank=True)
    additional_notes = models.CharField(max_length=4000, null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comment_records"
        verbose_name = "StateBridge Daily Comment Data"
        verbose_name_plural = "StateBridge Daily Comment Data"

        indexes = [
            models.Index(fields=["loan_number"], name="comment_rec_loan_nu_ad6a2d_idx"),
            models.Index(fields=["investor_loan_number"], name="comment_rec_investo_7cae45_idx"),
            models.Index(fields=["comment_date"], name="comment_rec_comment_a4d9b1_idx"),
            models.Index(fields=["department"], name="comment_rec_departm_f7e086_idx"),
            models.Index(
                fields=["loan_number", "comment_date"],
                name="comment_rec_loan_nu_e9e187_idx",
            ),
        ]

    def __str__(self):
        return f"Comment {self.loan_number} - {self.comment_date}"


class SBDailyPayHistoryData(models.Model):

    # Basic Loan Information
    investor = models.CharField(max_length=50, null=True, blank=True)
    loan_number = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    previous_ln_num = models.CharField(max_length=50, null=True, blank=True)

    # Borrower and Property Information
    borrower_name = models.CharField(max_length=200, null=True, blank=True)
    property_address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    zip = models.CharField(max_length=10, null=True, blank=True)
    property_type = models.CharField(max_length=50, null=True, blank=True)
    number_of_units = models.CharField(max_length=10, null=True, blank=True)
    occupancy_status = models.CharField(max_length=50, null=True, blank=True)

    # Loan Balance Information
    original_upb = models.CharField(max_length=50, null=True, blank=True)
    second_upb = models.CharField(max_length=50, null=True, blank=True)
    current_upb = models.CharField(max_length=50, null=True, blank=True)

    # Loan Characteristics
    account_type = models.CharField(max_length=50, null=True, blank=True)
    lien = models.CharField(max_length=10, null=True, blank=True)
    loan_term = models.CharField(max_length=20, null=True, blank=True)
    remaining_term = models.CharField(max_length=20, null=True, blank=True)
    maturity_date = models.CharField(max_length=20, null=True, blank=True)
    rate_type = models.CharField(max_length=50, null=True, blank=True)
    arm = models.CharField(max_length=10, null=True, blank=True)
    balloon = models.CharField(max_length=10, null=True, blank=True)
    piggyback = models.CharField(max_length=10, null=True, blank=True)

    # Payment Information
    current_ir = models.CharField(max_length=50, null=True, blank=True)
    current_pi = models.CharField(max_length=50, null=True, blank=True)
    current_ti = models.CharField(max_length=50, null=True, blank=True)
    current_piti = models.CharField(max_length=50, null=True, blank=True)
    last_full_payment_dt = models.CharField(max_length=20, null=True, blank=True)
    next_payment_due_dt = models.CharField(max_length=20, null=True, blank=True)

    # Escrow Information
    escrow_indicator = models.CharField(max_length=10, null=True, blank=True)
    restricted_escrow = models.CharField(max_length=10, null=True, blank=True)
    escrow_advance = models.CharField(max_length=50, null=True, blank=True)

    # Advance Balances
    rec_corp_advance_balance = models.CharField(max_length=50, null=True, blank=True)
    third_party_rec_balance = models.CharField(max_length=50, null=True, blank=True)
    accrued_interest = models.CharField(max_length=50, null=True, blank=True)
    accrued_late_fees = models.CharField(max_length=50, null=True, blank=True)

    # Foreclosure Information
    fc_status = models.CharField(max_length=50, null=True, blank=True)
    fc_type = models.CharField(max_length=50, null=True, blank=True)
    fc_first_legal_filed_dt = models.CharField(max_length=20, null=True, blank=True)
    fc_judgement_entered_dt = models.CharField(max_length=20, null=True, blank=True)
    fc_sale_scheduled_dt = models.CharField(max_length=20, null=True, blank=True)
    fc_suspended_dt = models.CharField(max_length=20, null=True, blank=True)
    fc_removal_dt = models.CharField(max_length=20, null=True, blank=True)
    fc_removal_description = models.CharField(max_length=255, null=True, blank=True)

    # Bankruptcy Information
    bk_status = models.CharField(max_length=50, null=True, blank=True)
    bk_code = models.CharField(max_length=20, null=True, blank=True)
    bk_filing_date = models.CharField(max_length=20, null=True, blank=True)
    bk_case_number = models.CharField(max_length=50, null=True, blank=True)
    bk_removal_dt = models.CharField(max_length=20, null=True, blank=True)

    # Valuation Information
    original_appraised_value = models.CharField(max_length=50, null=True, blank=True)
    as_is_bpo = models.CharField(max_length=50, null=True, blank=True)
    bpo_date = models.CharField(max_length=20, null=True, blank=True)

    # Credit Score Information
    fico_original = models.CharField(max_length=20, null=True, blank=True)
    fico = models.CharField(max_length=20, null=True, blank=True)
    fico_date = models.CharField(max_length=20, null=True, blank=True)

    # Modification Information
    loan_mod_dt = models.CharField(max_length=20, null=True, blank=True)
    mod_upb = models.CharField(max_length=50, null=True, blank=True)
    mod_ir = models.CharField(max_length=50, null=True, blank=True)
    mod_pi = models.CharField(max_length=50, null=True, blank=True)
    mod_first_payment_dt = models.CharField(max_length=20, null=True, blank=True)
    mod_maturity = models.CharField(max_length=20, null=True, blank=True)

    # Original Loan Information
    origination_date = models.CharField(max_length=20, null=True, blank=True)
    original_principal = models.CharField(max_length=50, null=True, blank=True)
    orig_rate = models.CharField(max_length=50, null=True, blank=True)
    fp_date = models.CharField(max_length=20, null=True, blank=True)
    mt_date = models.CharField(max_length=20, null=True, blank=True)

    # Interest Only Information
    interest_only_indicator = models.CharField(max_length=10, null=True, blank=True)
    interest_only_expiration_dt = models.CharField(max_length=20, null=True, blank=True)
    hoi_expiration_dt = models.CharField(max_length=20, null=True, blank=True)

    # Payment History (Last 13 Months)
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

    # Payment History Amounts (Last 13 Months)
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

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pay_history_records"
        verbose_name = "StateBridge Daily Pay History Data"
        verbose_name_plural = "StateBridge Daily Pay History Data"

        indexes = [
            models.Index(fields=["loan_number"], name="pay_history_loan_nu_4d1dfe_idx"),
            models.Index(fields=["previous_ln_num"], name="pay_history_previou_59bbbd_idx"),
            models.Index(fields=["borrower_name"], name="pay_history_borrowe_19e60f_idx"),
            models.Index(fields=["state", "zip"], name="pay_history_state_f88917_idx"),
            models.Index(fields=["fc_status"], name="pay_history_fc_stat_c65467_idx"),
            models.Index(fields=["bk_status"], name="pay_history_bk_stat_f92c65_idx"),
            models.Index(fields=["next_payment_due_dt"], name="pay_history_next_pa_db51a2_idx"),
            models.Index(
                fields=["loan_number", "next_payment_due_dt"],
                name="pay_history_loan_nu_366299_idx",
            ),
        ]

    def __str__(self):
        return f"PayHistory {self.loan_number} - Due {self.next_payment_due_dt}"


class SBDailyTransactionData(models.Model):

    # Basic Loan Information
    investor_id = models.CharField(max_length=50, null=True, blank=True)
    loan_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    previous_ln_num = models.CharField(max_length=50, null=True, blank=True)

    # Transaction Information
    loan_transaction_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    transaction_date = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    transaction_code = models.CharField(max_length=50, null=True, blank=True)
    transaction_description = models.CharField(max_length=255, null=True, blank=True)
    effective_date = models.CharField(max_length=20, null=True, blank=True)
    transaction_amt = models.CharField(max_length=50, null=True, blank=True)
    due_date = models.CharField(max_length=20, null=True, blank=True)

    # Payment Breakdown
    principal_amount = models.CharField(max_length=50, null=True, blank=True)
    interest_amount = models.CharField(max_length=50, null=True, blank=True)
    suspense_paid = models.CharField(max_length=50, null=True, blank=True)

    # Advance Information
    non_recoverable_advance = models.CharField(max_length=50, null=True, blank=True)
    recoverable_advance = models.CharField(max_length=50, null=True, blank=True)
    corporate_advance_reason_code = models.CharField(max_length=50, null=True, blank=True)

    # Escrow Information
    escrow_advance_balance = models.CharField(max_length=50, null=True, blank=True)
    escrow_amount = models.CharField(max_length=50, null=True, blank=True)
    restricted_escrow = models.CharField(max_length=10, null=True, blank=True)

    # Fee Information
    fee_code = models.CharField(max_length=50, null=True, blank=True)
    fee_description = models.CharField(max_length=255, null=True, blank=True)

    # Unapplied Payment Information
    unapplied_pmt = models.CharField(max_length=50, null=True, blank=True)
    stipulation_unapplied_pmt = models.CharField(max_length=50, null=True, blank=True)
    pre_petition_unapplied_pmt = models.CharField(max_length=50, null=True, blank=True)

    # Management Information
    asset_manager = models.CharField(max_length=100, null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transaction_records"
        verbose_name = "StateBridge Daily Transaction Data"
        verbose_name_plural = "StateBridge Daily Transaction Data"

        indexes = [
            models.Index(fields=["loan_id"], name="transaction_loan_id_a1ee8f_idx"),
            models.Index(fields=["previous_ln_num"], name="transaction_previou_ab528a_idx"),
            models.Index(fields=["loan_transaction_id"], name="transaction_loan_tr_9256e6_idx"),
            models.Index(fields=["transaction_date"], name="transaction_transac_75c4f7_idx"),
            models.Index(fields=["transaction_code"], name="transaction_transac_c919df_idx"),
            models.Index(fields=["effective_date"], name="transaction_effecti_56902d_idx"),
            models.Index(fields=["due_date"], name="transaction_due_dat_ac2d63_idx"),
            models.Index(
                fields=["loan_id", "transaction_date"],
                name="transaction_loan_id_cf33b5_idx",
            ),
        ]

    def __str__(self):
        return f"Transaction {self.loan_id} - {self.transaction_date} ({self.transaction_code})"
