# Models to store StateBridge Raw data

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
    date = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    investor_id = models.CharField(max_length=50, null=True, blank=True)
    loan_number = models.CharField(max_length=50, db_index=True, null=True, blank=True)
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
        # WHAT: Daily snapshots pattern - same loan can appear multiple times but only once per day.
        unique_together = [['loan_number', 'investor_id', 'date']]
        
        indexes = [
            models.Index(fields=['loan_number']),
            models.Index(fields=['investor_loan_number']),
            models.Index(fields=['borrower_last_name', 'borrower_first_name']),
            models.Index(fields=['property_state', 'property_zip']),
            models.Index(fields=['loan_status']),
            models.Index(fields=['date']),
            models.Index(fields=['loan_number', 'date']),  # For time series queries
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
