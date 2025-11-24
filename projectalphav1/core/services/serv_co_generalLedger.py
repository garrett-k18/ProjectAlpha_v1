"""
WHAT: Service layer for General Ledger Entry business logic
WHY: Centralize GL entry operations, filtering, and aggregate calculations
HOW: Reusable service functions for views and background tasks
WHERE: Imported by GL Entry views and management commands
"""
from django.db.models import Q, Sum, Count, Min, Max
from django.db.models.functions import Coalesce
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from core.models import GeneralLedgerEntries, ChartOfAccounts


# ------------------------------
# Filtering and Query Building
# ------------------------------

def build_gl_entry_queryset(
    posting_date_start: Optional[date] = None,
    posting_date_end: Optional[date] = None,
    entry_date_start: Optional[date] = None,
    entry_date_end: Optional[date] = None,
    company_name: Optional[str] = None,
    loan_number: Optional[str] = None,
    asset_hub_id: Optional[int] = None,
    account_number: Optional[str] = None,
    cost_center: Optional[str] = None,
    tag: Optional[str] = None,
    bucket: Optional[str] = None,
    requires_review: Optional[bool] = None,
    search_query: Optional[str] = None,
) -> Any:
    """
    WHAT: Build filtered queryset for GL entries based on multiple criteria
    WHY: Centralize filtering logic for reuse across list, export, and analytics views
    HOW: Apply Q objects and filters progressively based on provided parameters
    
    PARAMETERS:
        - posting_date_start: Filter entries posted on or after this date
        - posting_date_end: Filter entries posted on or before this date
        - entry_date_start: Filter entries created on or after this date
        - entry_date_end: Filter entries created on or before this date
        - company_name: Filter by company name (exact match)
        - loan_number: Filter by loan number (exact match)
        - asset_hub_id: Filter by asset hub ID
        - account_number: Filter by account number
        - cost_center: Filter by cost center code
        - tag: Filter by entry tag
        - bucket: Filter by entry bucket
        - requires_review: Filter by review flag
        - search_query: Full-text search across multiple fields
    
    RETURNS: Filtered QuerySet of GeneralLedgerEntries
    """
    # WHAT: Start with all GL entries, ordered by posting date (most recent first)
    # WHY: Provide a base queryset for progressive filtering
    # HOW: Use model manager with default ordering
    queryset = GeneralLedgerEntries.objects.all()
    
    # ------------------------------
    # Date Range Filters
    # ------------------------------
    # WHAT: Filter by posting date range
    # WHY: Enable date-based reporting and analysis
    # HOW: Apply gte/lte filters on posting_date field
    if posting_date_start:
        queryset = queryset.filter(posting_date__gte=posting_date_start)
    
    if posting_date_end:
        queryset = queryset.filter(posting_date__lte=posting_date_end)
    
    # WHAT: Filter by entry date range
    # WHY: Track when entries were created vs when they were posted
    # HOW: Apply gte/lte filters on entry_date field
    if entry_date_start:
        queryset = queryset.filter(entry_date__gte=entry_date_start)
    
    if entry_date_end:
        queryset = queryset.filter(entry_date__lte=entry_date_end)
    
    # ------------------------------
    # Entity and Loan Filters
    # ------------------------------
    # WHAT: Filter by company name
    # WHY: Isolate entries for specific entities
    # HOW: Exact match on company_name field
    if company_name:
        queryset = queryset.filter(company_name=company_name)
    
    # WHAT: Filter by loan number
    # WHY: Track all GL entries for a specific loan
    # HOW: Exact match on loan_number field
    if loan_number:
        queryset = queryset.filter(loan_number=loan_number)
    
    # WHAT: Filter by asset hub ID
    # WHY: Get all GL entries linked to a specific asset
    # HOW: ForeignKey filter on asset_hub field
    if asset_hub_id:
        queryset = queryset.filter(asset_hub_id=asset_hub_id)
    
    # ------------------------------
    # Account and Cost Center Filters
    # ------------------------------
    # WHAT: Filter by account number
    # WHY: Analyze entries for specific GL accounts
    # HOW: Exact match on account_number field
    if account_number:
        queryset = queryset.filter(account_number=account_number)
    
    # WHAT: Filter by cost center
    # WHY: Enable departmental/cost center reporting
    # HOW: Exact match on cost_center field
    if cost_center:
        queryset = queryset.filter(cost_center=cost_center)
    
    # ------------------------------
    # Tag and Bucket Filters
    # ------------------------------
    # WHAT: Filter by entry tag
    # WHY: Isolate entries by category (e.g., Loan Origination)
    # HOW: Exact match on tag field
    if tag:
        queryset = queryset.filter(tag=tag)
    
    # WHAT: Filter by entry bucket
    # WHY: Group entries by strategic bucket (e.g., Acquisition)
    # HOW: Exact match on bucket field
    if bucket:
        queryset = queryset.filter(bucket=bucket)
    
    # ------------------------------
    # Review Flag Filter
    # ------------------------------
    # WHAT: Filter by review required flag
    # WHY: Isolate entries needing attention
    # HOW: Boolean filter on requires_review field
    if requires_review is not None:
        queryset = queryset.filter(requires_review=requires_review)
    
    # ------------------------------
    # Full-Text Search
    # ------------------------------
    # WHAT: Search across multiple text fields
    # WHY: Enable flexible search in dashboard
    # HOW: Use Q objects with OR logic for multiple fields
    if search_query:
        queryset = queryset.filter(
            Q(entry__icontains=search_query) |
            Q(loan_number__icontains=search_query) |
            Q(borrower_name__icontains=search_query) |
            Q(document_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(comment__icontains=search_query) |
            Q(account_number__icontains=search_query) |
            Q(account_name__icontains=search_query)
        )
    
    return queryset


def get_gl_entry_summary(
    queryset: Any,
) -> Dict[str, Any]:
    """
    WHAT: Calculate summary statistics for a GL entry queryset
    WHY: Provide aggregate data for dashboard KPIs and charts
    HOW: Use Django ORM aggregations and Python calculations
    
    PARAMETERS:
        - queryset: Filtered QuerySet of GeneralLedgerEntries
    
    RETURNS: Dictionary with summary statistics
    """
    # WHAT: Calculate total entries and aggregate amounts
    # WHY: Provide key metrics for dashboard header
    # HOW: Use Django aggregate functions
    aggregates = queryset.aggregate(
        total_entries=Count('id'),
        total_debits=Coalesce(Sum('debit_amount'), Decimal('0.00')),
        total_credits=Coalesce(Sum('credit_amount'), Decimal('0.00')),
        entries_requiring_review=Count('id', filter=Q(requires_review=True)),
        date_range_start=Min('posting_date'),
        date_range_end=Max('posting_date'),
    )
    
    # WHAT: Calculate net total (debits - credits)
    # WHY: Show overall balance impact
    # HOW: Subtract credits from debits
    aggregates['net_total'] = aggregates['total_debits'] - aggregates['total_credits']
    
    # ------------------------------
    # Tag Distribution
    # ------------------------------
    # WHAT: Count entries by tag
    # WHY: Show categorical distribution in charts
    # HOW: Group by tag and count
    tag_counts = queryset.values('tag').annotate(count=Count('id')).order_by('-count')
    aggregates['by_tag'] = {
        item['tag'] or 'untagged': item['count'] 
        for item in tag_counts
    }
    
    # ------------------------------
    # Bucket Distribution
    # ------------------------------
    # WHAT: Count entries by bucket
    # WHY: Show strategic grouping distribution in charts
    # HOW: Group by bucket and count
    bucket_counts = queryset.values('bucket').annotate(count=Count('id')).order_by('-count')
    aggregates['by_bucket'] = {
        item['bucket'] or 'unbucketed': item['count'] 
        for item in bucket_counts
    }
    
    return aggregates


def get_entries_by_tag(queryset: Any) -> List[Dict[str, Any]]:
    """
    WHAT: Get GL entries grouped by tag with aggregate amounts
    WHY: Enable tag-based reporting and charts
    HOW: Group by tag and calculate sums
    
    PARAMETERS:
        - queryset: Filtered QuerySet of GeneralLedgerEntries
    
    RETURNS: List of dicts with tag, count, and amounts
    """
    # WHAT: Group entries by tag and calculate aggregates
    # WHY: Provide data for tag breakdown chart
    # HOW: Use values() with annotate()
    results = queryset.values('tag').annotate(
        count=Count('id'),
        total_debits=Coalesce(Sum('debit_amount'), Decimal('0.00')),
        total_credits=Coalesce(Sum('credit_amount'), Decimal('0.00')),
    ).order_by('-total_debits')
    
    # WHAT: Calculate net amount for each tag
    # WHY: Show net impact per category
    # HOW: Subtract credits from debits
    output = []
    for item in results:
        item['net_amount'] = item['total_debits'] - item['total_credits']
        item['tag_display'] = dict(GeneralLedgerEntries.EntryTag.choices).get(
            item['tag'], 'Untagged'
        )
        output.append(item)
    
    return output


def get_entries_by_bucket(queryset: Any) -> List[Dict[str, Any]]:
    """
    WHAT: Get GL entries grouped by bucket with aggregate amounts
    WHY: Enable bucket-based strategic reporting and charts
    HOW: Group by bucket and calculate sums
    
    PARAMETERS:
        - queryset: Filtered QuerySet of GeneralLedgerEntries
    
    RETURNS: List of dicts with bucket, count, and amounts
    """
    # WHAT: Group entries by bucket and calculate aggregates
    # WHY: Provide data for bucket breakdown chart
    # HOW: Use values() with annotate()
    results = queryset.values('bucket').annotate(
        count=Count('id'),
        total_debits=Coalesce(Sum('debit_amount'), Decimal('0.00')),
        total_credits=Coalesce(Sum('credit_amount'), Decimal('0.00')),
    ).order_by('-total_debits')
    
    # WHAT: Calculate net amount for each bucket
    # WHY: Show net impact per strategic grouping
    # HOW: Subtract credits from debits
    output = []
    for item in results:
        item['net_amount'] = item['total_debits'] - item['total_credits']
        item['bucket_display'] = dict(GeneralLedgerEntries.EntryBucket.choices).get(
            item['bucket'], 'Unbucketed'
        )
        output.append(item)
    
    return output


def get_entries_by_account(queryset: Any, limit: int = 20) -> List[Dict[str, Any]]:
    """
    WHAT: Get GL entries grouped by account with aggregate amounts
    WHY: Show top accounts by activity
    HOW: Group by account and calculate sums, limit to top N
    
    PARAMETERS:
        - queryset: Filtered QuerySet of GeneralLedgerEntries
        - limit: Maximum number of accounts to return (default 20)
    
    RETURNS: List of dicts with account info and amounts
    """
    # WHAT: Group entries by account and calculate aggregates
    # WHY: Provide data for top accounts analysis
    # HOW: Use values() with annotate() and limit
    results = queryset.values('account_number', 'account_name').annotate(
        count=Count('id'),
        total_debits=Coalesce(Sum('debit_amount'), Decimal('0.00')),
        total_credits=Coalesce(Sum('credit_amount'), Decimal('0.00')),
    ).order_by('-total_debits')[:limit]
    
    # WHAT: Calculate net amount for each account
    # WHY: Show net impact per account
    # HOW: Subtract credits from debits
    output = []
    for item in results:
        item['net_amount'] = item['total_debits'] - item['total_credits']
        output.append(item)
    
    return output


def get_monthly_trend(
    queryset: Any,
    months: int = 12,
) -> List[Dict[str, Any]]:
    """
    WHAT: Get GL entry volume and amounts by month
    WHY: Show time-series trends for dashboard charts
    HOW: Group by month and calculate aggregates
    
    PARAMETERS:
        - queryset: Filtered QuerySet of GeneralLedgerEntries
        - months: Number of months to include (default 12)
    
    RETURNS: List of dicts with month and aggregate data
    """
    from django.db.models.functions import TruncMonth
    
    # WHAT: Group entries by month and calculate aggregates
    # WHY: Provide data for monthly trend chart
    # HOW: Use TruncMonth annotation with aggregates
    results = queryset.annotate(
        month=TruncMonth('posting_date')
    ).values('month').annotate(
        count=Count('id'),
        total_debits=Coalesce(Sum('debit_amount'), Decimal('0.00')),
        total_credits=Coalesce(Sum('credit_amount'), Decimal('0.00')),
    ).order_by('-month')[:months]
    
    # WHAT: Calculate net amount and format month for display
    # WHY: Provide complete data for frontend chart
    # HOW: Process query results
    output = []
    for item in results:
        item['net_amount'] = item['total_debits'] - item['total_credits']
        item['month_display'] = item['month'].strftime('%b %Y') if item['month'] else 'Unknown'
        output.append(item)
    
    # WHAT: Reverse list to show chronological order (oldest to newest)
    # WHY: Charts typically display time series left to right
    # HOW: Reverse the list
    return list(reversed(output))


def get_chart_of_accounts_lookup() -> Dict[str, Dict[str, str]]:
    """
    WHAT: Get chart of accounts as a lookup dictionary
    WHY: Provide account reference data for dropdowns and validation
    HOW: Query ChartOfAccounts and build dict keyed by account_number
    
    RETURNS: Dict mapping account_number to account details
    """
    # WHAT: Query all accounts and build lookup dict
    # WHY: Efficient reference for account data
    # HOW: Single query with dict comprehension
    accounts = ChartOfAccounts.objects.all().values(
        'account_number', 'account_name', 'account_type'
    )
    
    return {
        account['account_number']: {
            'name': account['account_name'],
            'type': account['account_type'],
        }
        for account in accounts
    }

