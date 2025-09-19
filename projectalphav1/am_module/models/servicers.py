from __future__ import annotations

from django.db import models
from django.conf import settings
from django.utils import timezone


class ServicerLoanData(models.Model):
    """Model to manage loan data for servicers.
    
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

    # Current Loan Data
    as_of_date = models.DateField(null=True, blank=True, 
                                help_text='Date this loan data was reported/effective.')
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                        help_text='Current principal balance of the loan.')
    deferred_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                        help_text='Portion of balance that has been deferred.')
    interest_rate = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True,
                                      help_text='Current interest rate (%).')
    next_due_date = models.DateField(null=True, blank=True,
                                   help_text='Next payment due date.')
    last_paid_date = models.DateField(null=True, blank=True,
                                    help_text='Date of last payment received.')
    term_remaining = models.IntegerField(null=True, blank=True,
                                       help_text='Remaining term in months.')
    escrow_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                       help_text='Current escrow account balance.')
    escrow_advance_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                              help_text='Escrow advances made by servicer.')
    third_party_recov_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                                 help_text='Third party recoverable balance.')
    suspense_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                         help_text='Funds held in suspense.')
    servicer_late_fees = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                          help_text='Late fees assessed by servicer.')
    other_charges = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                      help_text='Other charges on the loan.')
    interest_arrears = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                         help_text='Interest in arrears.')
    total_debt = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                   help_text='Total debt including all balances and fees.')
    lien_pos = models.IntegerField(null=True, blank=True,
                                 help_text='Lien position (1=first lien, 2=second lien, etc).')
    maturity_date = models.DateField(null=True, blank=True,
                                   help_text='Date when loan matures/is due in full.')

    # BPLS (Business Purpose Loan Servicer)
    default_rate = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True,
                                     help_text='Default interest rate (%).')

    # Origination Data
    origination_date = models.DateField(null=True, blank=True,
                                      help_text='Date when loan was originated.')
    origination_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                           help_text='Original loan balance at origination.')
    origination_interest_rate = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True,
                                                 help_text='Original interest rate at origination (%).')

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
            )
        ]

    def __str__(self):
        """String representation of the loan data."""
        hub_id = self.asset_hub.id if self.asset_hub else 'No Hub'
        period = f"{self.reporting_month}/{self.reporting_year}" if self.reporting_month and self.reporting_year else 'Unknown Period'
        return f"Loan Data for Hub #{hub_id} - {period}"