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