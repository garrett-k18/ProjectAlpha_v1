"""
WHAT: GeneralLedgerEntries model - Track all general ledger transactions and entries
WHY: Central repository for all financial GL entries to support accounting and reporting
HOW: Stores detailed GL entry information including accounts, amounts, and posting details
WHERE: Used throughout the system for financial transaction tracking and reporting
"""
from django.db import models
from decimal import Decimal
from .model_co_assetIdHub import AssetIdHub


class GeneralLedgerTag(models.Model):
    """
    WHAT: Tag for General Ledger entries
    WHY: Flexible tagging system for GL entries to support ad-hoc reporting and categorization
    HOW: Simple M2M relationship with GeneralLedgerEntries
    """
    name = models.CharField(max_length=50, unique=True, help_text="Tag name")
    description = models.TextField(null=True, blank=True, help_text="Optional description of the tag")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "GL Tag"
        verbose_name_plural = "GL Tags"
        ordering = ['name']

    def __str__(self):
        return self.name


class GeneralLedgerBucket(models.Model):
    """
    WHAT: Bucket for categorizing GL entries
    WHY: High-level categorization (buckets) for aggregating entries, useful for budgeting or specific reporting views
    HOW: Foreign Key relationship with GeneralLedgerEntries
    """
    name = models.CharField(max_length=100, unique=True, help_text="Bucket name")
    code = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Short code for the bucket")
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "GL Bucket"
        verbose_name_plural = "GL Buckets"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name


class GeneralLedgerEntries(models.Model):
    """
    WHAT: Model for storing general ledger entries and financial transactions
    WHY: Need a comprehensive record of all GL entries for financial reporting and audit trails
    HOW: Captures all relevant GL entry details including debits, credits, and metadata
    """
    
    # ------------------------------
    # Primary Identifier
    # ------------------------------
    # Primary key automatically created by Django as 'id'
    
    entry = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text='General ledger entry identifier or reference number'
    )
    
    # ------------------------------
    # Company and Loan Information
    # ------------------------------
    company_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text='Name of the company associated with this GL entry'
    )
    
    asset_link = models.ForeignKey(
        AssetIdHub,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gl_entries',
        help_text='Link to the canonical Asset/Loan ID Hub for robust tracking'
    )

    loan_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text='Loan number associated with this GL entry (legacy field, prefer asset_link)'
    )
    
    borrower_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Name of the borrower associated with this loan'
    )

    # ------------------------------
    # Categorization
    # ------------------------------
    bucket = models.ForeignKey(
        GeneralLedgerBucket,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entries',
        help_text='Bucket for high-level aggregation and reporting'
    )

    tags = models.ManyToManyField(
        GeneralLedgerTag,
        blank=True,
        related_name='entries',
        help_text='Tags for flexible categorization'
    )
    
    # ------------------------------
    # Document Information
    # ------------------------------
    document_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text='Internal document number for this GL entry'
    )
    
    external_document_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='External document number or reference from third-party systems'
    )
    
    document_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Type of document (e.g., Invoice, Receipt, Journal Entry, etc.)'
    )
    
    # ------------------------------
    # Loan Classification
    # ------------------------------
    loan_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Type of loan (e.g., Commercial, Residential, etc.)'
    )
    
    # ------------------------------
    # Date Fields
    # ------------------------------
    date_funded = models.DateField(
        null=True,
        blank=True,
        help_text='Date when the loan was funded (if applicable)'
    )
    
    posting_date = models.DateField(
        db_index=True,
        help_text='Date when the GL entry was posted to the ledger'
    )
    
    entry_date = models.DateField(
        db_index=True,
        help_text='Date when the GL entry was created or entered into the system'
    )
    
    # ------------------------------
    # Financial Amounts
    # ------------------------------
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Total transaction amount (if using a single amount field)'
    )
    
    credit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Credit amount for this GL entry (increases liability/equity/revenue)'
    )
    
    debit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Debit amount for this GL entry (increases assets/expenses)'
    )
    
    # ------------------------------
    # Account Information
    # ------------------------------
    account_number = models.CharField(
        max_length=50,
        db_index=True,
        help_text='Chart of accounts number for this GL entry'
    )
    
    account_name = models.CharField(
        max_length=255,
        help_text='Name of the account from the chart of accounts'
    )
    
    # ------------------------------
    # Description and Comments
    # ------------------------------
    description = models.TextField(
        null=True,
        blank=True,
        help_text='Detailed description of the GL entry transaction'
    )
    
    reason_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Code indicating the reason or category for this GL entry'
    )
    
    comment = models.TextField(
        null=True,
        blank=True,
        help_text='Additional comments or notes about this GL entry'
    )
    
    # ------------------------------
    # Cost Center Information
    # ------------------------------
    cost_center = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
        help_text='Cost center code for departmental tracking and allocation'
    )
    
    cost_center_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Name of the cost center for easier identification'
    )
    
    # ------------------------------
    # Metadata Fields
    # ------------------------------
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when this record was created in the database'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when this record was last updated'
    )
    
    class Meta:
        """
        WHAT: Meta configuration for GeneralLedgerEntries model
        WHY: Define database table name, ordering, and indexing for optimal performance
        HOW: Uses Django Meta class to specify model behavior and database settings
        """
        db_table = 'general_ledger_entries'
        verbose_name = 'General Ledger Entry'
        verbose_name_plural = 'General Ledger Entries'
        ordering = ['-posting_date', '-entry_date']  # Most recent entries first
        indexes = [
            # Index for fast lookups by posting date
            models.Index(fields=['posting_date']),
            # Index for fast lookups by entry date
            models.Index(fields=['entry_date']),
            # Index for fast lookups by company and posting date
            models.Index(fields=['company_name', 'posting_date']),
            # Index for fast lookups by loan number
            models.Index(fields=['loan_number', 'posting_date']),
            # Index for fast lookups by account number and date
            models.Index(fields=['account_number', 'posting_date']),
            # Index for cost center reporting
            models.Index(fields=['cost_center', 'posting_date']),
        ]
    
    def __str__(self):
        """
        WHAT: String representation of the GeneralLedgerEntries model
        WHY: Provide human-readable representation for admin and debugging
        HOW: Returns GL entry and company name
        """
        return f"GL Entry {self.gl_entry} - {self.company_name}"
    
    def clean(self):
        """
        WHAT: Model validation method
        WHY: Ensure data integrity before saving to database
        HOW: Validates that credit and debit amounts follow accounting rules
        """
        from django.core.exceptions import ValidationError
        
        # Validate that we don't have both credit and debit on the same entry
        # (typically one should be zero in double-entry bookkeeping)
        if self.credit_amount > 0 and self.debit_amount > 0:
            # This is allowed but uncommon - could add a warning in admin
            pass
        
        # Ensure at least one amount is provided
        if self.credit_amount == 0 and self.debit_amount == 0 and not self.amount:
            raise ValidationError(
                'At least one of credit_amount, debit_amount, or amount must be non-zero.'
            )
    
    def save(self, *args, **kwargs):
        """
        WHAT: Override save method to run validation and set defaults
        WHY: Ensure data consistency and run clean method before saving
        HOW: Calls full_clean() and then super().save()
        """
        # Run model validation
        self.full_clean()
        
        # Call parent save method
        super().save(*args, **kwargs)
    
    @property
    def net_amount(self):
        """
        WHAT: Calculate the net amount for this GL entry
        WHY: Provide easy access to the net impact (debit - credit)
        HOW: Returns the difference between debit and credit amounts
        RETURNS: Decimal representing net amount (positive = debit, negative = credit)
        """
        return self.debit_amount - self.credit_amount
    
    @property
    def is_balanced(self):
        """
        WHAT: Check if this entry has both debit and credit amounts equal
        WHY: Useful for validation in double-entry bookkeeping systems
        HOW: Compares debit_amount to credit_amount
        RETURNS: Boolean indicating if the entry is balanced
        """
        return self.debit_amount == self.credit_amount

  # ------------------------------
  # Chart of Accounts
  # ------------------------------

class ChartOfAccounts(models.Model):
    """
    WHAT: Model for storing chart of accounts
    WHY: Need a comprehensive record of all accounts for financial reporting and audit trails
    HOW: Captures all relevant account details including name, number, and type
    """
    account_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text='Chart of accounts number for this account'
    )
    account_name = models.CharField(
        max_length=255,
        help_text='Name of the account from the chart of accounts'
    )
    account_type = models.CharField(
        max_length=50,
        help_text='Type of account (e.g., Asset, Liability, Equity, Revenue, Expense)'
    )
    transaction_table_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Reference to the LLTransactionSummary/LLCashFlowSeries field this account maps to'
    )
 
    class Meta:
        db_table = 'chart_of_accounts'
        verbose_name = 'Chart of Accounts'
        verbose_name_plural = 'Chart of Accounts'
        ordering = ['account_number']
    
    def __str__(self):
        """
        WHAT: String representation of ChartOfAccounts
        WHY: Human-readable display in admin and debugging
        HOW: Returns account number and name
        """
        return f"{self.account_number} - {self.account_name}"