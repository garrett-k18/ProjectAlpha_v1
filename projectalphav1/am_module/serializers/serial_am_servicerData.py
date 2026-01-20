from __future__ import annotations

from rest_framework import serializers
from am_module.models.model_am_servicersCleaned import ServicerLoanData
from am_module.logic.logi_am_modelLogic import compute_current_total_debt_from_servicer


class ServicerLoanDataSerializer(serializers.Serializer):
    """Serializer for the ServicerLoanData model.

    PERFORMANCE: Converted from ModelSerializer to plain Serializer to avoid
    automatic FK serialization (created_by, updated_by, raw_source_snapshot)
    which causes N+1 queries. We only serialize the fields the frontend needs.
    """

    # Frontend-friendly aliases
    as_of = serializers.DateField(source='as_of_date', read_only=True)
    asset_hub_id = serializers.IntegerField(read_only=True)
    
    # Reporting period
    reporting_year = serializers.IntegerField(allow_null=True)
    reporting_month = serializers.IntegerField(allow_null=True)
    reporting_day = serializers.IntegerField(allow_null=True)
    
    # Core loan data
    investor_id = serializers.CharField(allow_null=True, allow_blank=True)
    servicer_id = serializers.CharField(allow_null=True, allow_blank=True)
    previous_servicer_id = serializers.CharField(allow_null=True, allow_blank=True)
    as_of_date = serializers.DateField(allow_null=True)
    
    # Property info
    address = serializers.CharField(allow_null=True, allow_blank=True)
    city = serializers.CharField(allow_null=True, allow_blank=True)
    state = serializers.CharField(allow_null=True, allow_blank=True)
    zip_code = serializers.CharField(allow_null=True, allow_blank=True)
    occupnacy = serializers.CharField(allow_null=True, allow_blank=True)
    property_type = serializers.CharField(allow_null=True, allow_blank=True)
    
    # Borrower info
    borrower_last_name = serializers.CharField(allow_null=True, allow_blank=True)
    borrower_first_name = serializers.CharField(allow_null=True, allow_blank=True)
    current_fico = serializers.IntegerField(allow_null=True)
    current_fico_date = serializers.DateField(allow_null=True)
    
    # Financial data
    current_balance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    deferred_balance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=3, allow_null=True)
    next_due_date = serializers.DateField(allow_null=True)
    last_paid_date = serializers.DateField(allow_null=True)
    current_pi = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    current_ti = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    piti = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    term_remaining = serializers.IntegerField(allow_null=True)
    
    # Balances
    escrow_balance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    escrow_advance_balance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    third_party_recov_balance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    suspense_balance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    servicer_late_fees = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    other_charges = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    interest_arrears = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    total_debt = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    computed_total_debt = serializers.SerializerMethodField()
    lien_pos = serializers.IntegerField(allow_null=True)
    maturity_date = serializers.DateField(allow_null=True)
    default_rate = serializers.DecimalField(max_digits=5, decimal_places=3, allow_null=True)
    
    # Origination data
    origination_date = serializers.DateField(allow_null=True)
    origination_balance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    origination_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=3, allow_null=True)
    original_appraised_value = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    original_appraised_date = serializers.DateField(allow_null=True)
    
    # Valuations
    avm_date = serializers.DateField(allow_null=True)
    avm_value = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    bpo_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    bpo_asis_date = serializers.DateField(allow_null=True)
    bpo_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    
    # Flags
    arm_flag = serializers.BooleanField(allow_null=True)
    escrowed_flag = serializers.BooleanField(allow_null=True)
    bk_flag = serializers.BooleanField(allow_null=True)
    bk_ch = serializers.BooleanField(allow_null=True)
    fc_flag = serializers.BooleanField(allow_null=True)
    mba = serializers.BooleanField(allow_null=True)
    
    # Legal/workflow fields
    loan_type = serializers.CharField(allow_null=True, allow_blank=True)
    loan_warning = serializers.CharField(allow_null=True, allow_blank=True)
    bk_current_status = serializers.CharField(allow_null=True, allow_blank=True)
    bk_discharge_date = serializers.DateField(allow_null=True)
    bk_dismissed_date = serializers.DateField(allow_null=True)
    bk_filed_date = serializers.DateField(allow_null=True)
    actual_fc_sale_date = serializers.DateField(allow_null=True)
    date_referred_to_fc_atty = serializers.DateField(allow_null=True)
    fc_completion_date = serializers.DateField(allow_null=True)
    fc_status = serializers.CharField(allow_null=True, allow_blank=True)
    pif_date = serializers.DateField(allow_null=True)
    acquired_date = serializers.DateField(allow_null=True)
    inactive_date = serializers.DateField(allow_null=True)
    prim_stat = serializers.CharField(allow_null=True, allow_blank=True)
    
    # Additional fields
    noi_expiration_date = serializers.DateField(allow_null=True)
    total_principal = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    total_interest = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    non_recoverable_principal = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    non_recoverable_interest = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    non_recoverable_escrow = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    non_recoverable_fees = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    non_recoverable_corporate_advance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    asset_manager = serializers.CharField(allow_null=True, allow_blank=True)
    collateral_count = serializers.IntegerField(allow_null=True)
    current_loan_term = serializers.IntegerField(allow_null=True)
    current_neg_am_bal = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    deferred_interest = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    deferred_principal = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)

    def get_computed_total_debt(self, obj: ServicerLoanData):
        return compute_current_total_debt_from_servicer(
            current_balance=getattr(obj, 'current_balance', None),
            deferred_balance=getattr(obj, 'deferred_balance', None),
            escrow_advance_balance=getattr(obj, 'escrow_advance_balance', None),
            third_party_recov_balance=getattr(obj, 'third_party_recov_balance', None),
            suspense_balance=getattr(obj, 'suspense_balance', None),
            servicer_late_fees=getattr(obj, 'servicer_late_fees', None),
            other_charges=getattr(obj, 'other_charges', None),
            interest_arrears=getattr(obj, 'interest_arrears', None),
        )
    first_due_date = serializers.DateField(allow_null=True)
    interest_method = serializers.CharField(allow_null=True, allow_blank=True)
    last_escrow_analysis_date = serializers.DateField(allow_null=True)
    legal_status = serializers.CharField(allow_null=True, allow_blank=True)
    loan_age = serializers.IntegerField(allow_null=True)
    mers_num = serializers.CharField(allow_null=True, allow_blank=True)
    original_first_payment_date = serializers.DateField(allow_null=True)
    original_loan_term = serializers.IntegerField(allow_null=True)
    original_maturity_date = serializers.DateField(allow_null=True)
    original_amt = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    servicing_specialist = serializers.CharField(allow_null=True, allow_blank=True)
    trust_id = serializers.CharField(allow_null=True, allow_blank=True)
    balloon_date = serializers.DateField(allow_null=True)
    balloon_payment = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    loan_purpose = serializers.CharField(allow_null=True, allow_blank=True)
    acquisition_or_sale_identifier = serializers.CharField(allow_null=True, allow_blank=True)
    
    # Timestamps (exclude FK fields created_by/updated_by to avoid queries)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    # NOTE: Deliberately excluding created_by, updated_by, and raw_source_snapshot
    # to avoid N+1 queries. Frontend doesn't need these fields for grid display.
