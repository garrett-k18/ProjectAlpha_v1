"""
WHAT: API ViewSets for General Ledger Entries
WHY: Provide REST API endpoints for GL entry CRUD and analytics
HOW: DRF ViewSets with filtering, pagination, and custom actions
WHERE: Mounted at /api/gl-entries/ via core.urls
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from datetime import datetime, timedelta
from decimal import Decimal

from core.models import GeneralLedgerEntries, ChartOfAccounts
from core.serializers.serial_co_generalLedger import (
    GeneralLedgerEntriesSerializer,
    GLEntryListSerializer,
    GLEntrySummarySerializer,
    ChartOfAccountsSerializer,
)
from core.services.serv_co_generalLedger import (
    build_gl_entry_queryset,
    get_gl_entry_summary,
    get_entries_by_tag,
    get_entries_by_bucket,
    get_entries_by_account,
    get_monthly_trend,
    get_chart_of_accounts_lookup,
)


class GeneralLedgerEntriesFilter(filters.FilterSet):
    """
    WHAT: FilterSet for GL entries with comprehensive filtering options
    WHY: Enable flexible querying from frontend with URL parameters
    HOW: Define filters for key fields with various lookup types
    """
    
    # WHAT: Date range filters
    # WHY: Enable filtering by date ranges for reporting
    # HOW: Use gte/lte lookups on date fields
    posting_date_start = filters.DateFilter(field_name='posting_date', lookup_expr='gte')
    posting_date_end = filters.DateFilter(field_name='posting_date', lookup_expr='lte')
    entry_date_start = filters.DateFilter(field_name='entry_date', lookup_expr='gte')
    entry_date_end = filters.DateFilter(field_name='entry_date', lookup_expr='lte')
    
    # WHAT: Text search filters
    # WHY: Enable partial matching for flexible searches
    # HOW: Use icontains lookup for case-insensitive partial match
    loan_number = filters.CharFilter(field_name='loan_number', lookup_expr='icontains')
    company_name = filters.CharFilter(field_name='company_name', lookup_expr='icontains')
    account_number = filters.CharFilter(field_name='account_number', lookup_expr='icontains')
    
    # WHAT: Exact match filters
    # WHY: Filter by specific values
    # HOW: Default exact match lookup
    tag = filters.ChoiceFilter(choices=GeneralLedgerEntries.EntryTag.choices)
    bucket = filters.ChoiceFilter(choices=GeneralLedgerEntries.EntryBucket.choices)
    requires_review = filters.BooleanFilter(field_name='requires_review')
    asset_hub = filters.NumberFilter(field_name='asset_hub')
    
    class Meta:
        model = GeneralLedgerEntries
        fields = [
            'posting_date_start',
            'posting_date_end',
            'entry_date_start',
            'entry_date_end',
            'loan_number',
            'company_name',
            'account_number',
            'tag',
            'bucket',
            'requires_review',
            'asset_hub',
        ]


class GeneralLedgerEntriesViewSet(viewsets.ModelViewSet):
    """
    WHAT: ViewSet for GL entries with full CRUD and analytics
    WHY: Provide comprehensive API for GL entry management and reporting
    HOW: ModelViewSet with custom actions for summaries and analytics
    
    ENDPOINTS:
        GET    /api/gl-entries/           - List entries (paginated)
        POST   /api/gl-entries/           - Create new entry
        GET    /api/gl-entries/{id}/      - Retrieve single entry
        PUT    /api/gl-entries/{id}/      - Update entry
        PATCH  /api/gl-entries/{id}/      - Partial update
        DELETE /api/gl-entries/{id}/      - Delete entry
        GET    /api/gl-entries/summary/   - Get summary statistics
        GET    /api/gl-entries/by-tag/    - Get entries grouped by tag
        GET    /api/gl-entries/by-bucket/ - Get entries grouped by bucket
        GET    /api/gl-entries/by-account/- Get entries grouped by account
        GET    /api/gl-entries/monthly-trend/ - Get monthly trend data
    """
    
    # WHAT: Set queryset and serializer
    # WHY: Required by DRF ViewSet
    # HOW: Use all entries with select_related for performance
    queryset = GeneralLedgerEntries.objects.all().select_related(
        'asset_hub', 'created_by', 'updated_by'
    )
    serializer_class = GeneralLedgerEntriesSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = GeneralLedgerEntriesFilter
    
    def get_serializer_class(self):
        """
        WHAT: Return appropriate serializer based on action
        WHY: Use lightweight serializer for list view, full serializer for detail
        HOW: Check self.action and return corresponding serializer
        """
        # WHAT: Use lightweight serializer for list view
        # WHY: Reduce payload size for grid display
        # HOW: Return GLEntryListSerializer for 'list' action
        if self.action == 'list':
            return GLEntryListSerializer
        
        # WHAT: Use full serializer for all other actions
        # WHY: Provide complete data for detail, create, update
        # HOW: Return GeneralLedgerEntriesSerializer
        return GeneralLedgerEntriesSerializer
    
    def get_queryset(self):
        """
        WHAT: Get filtered queryset based on query parameters
        WHY: Enable flexible filtering beyond django-filter capabilities
        HOW: Use service layer filtering function
        """
        # WHAT: Get base queryset from parent
        # WHY: Respect permission filtering if any
        # HOW: Call super().get_queryset()
        queryset = super().get_queryset()
        
        # WHAT: Apply additional search filtering if search param present
        # WHY: Enable full-text search across multiple fields
        # HOW: Pass search query to service layer function
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = build_gl_entry_queryset(
                search_query=search_query,
            )
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        WHAT: Get summary statistics for filtered GL entries
        WHY: Provide aggregate data for dashboard KPIs
        HOW: Use service layer to calculate aggregates
        
        QUERY PARAMS:
            All standard filter params (posting_date_start, tag, bucket, etc.)
        
        RETURNS: Summary statistics including totals, counts, and distributions
        """
        # WHAT: Get filtered queryset based on query params
        # WHY: Calculate summary only for filtered entries
        # HOW: Use filterset to apply filters
        queryset = self.filter_queryset(self.get_queryset())
        
        # WHAT: Calculate summary statistics
        # WHY: Provide aggregate data for frontend
        # HOW: Call service layer function
        summary_data = get_gl_entry_summary(queryset)
        
        # WHAT: Serialize and return summary
        # WHY: Validate data structure and format dates
        # HOW: Use GLEntrySummarySerializer
        serializer = GLEntrySummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-tag')
    def by_tag(self, request):
        """
        WHAT: Get GL entries grouped by tag with aggregates
        WHY: Enable tag-based reporting and charts
        HOW: Use service layer grouping function
        
        QUERY PARAMS:
            All standard filter params (posting_date_start, tag, bucket, etc.)
        
        RETURNS: List of tag groups with counts and amounts
        """
        # WHAT: Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # WHAT: Get tag groupings
        # WHY: Provide data for tag breakdown chart
        # HOW: Call service layer function
        tag_data = get_entries_by_tag(queryset)
        
        return Response(tag_data)
    
    @action(detail=False, methods=['get'], url_path='by-bucket')
    def by_bucket(self, request):
        """
        WHAT: Get GL entries grouped by bucket with aggregates
        WHY: Enable bucket-based strategic reporting and charts
        HOW: Use service layer grouping function
        
        QUERY PARAMS:
            All standard filter params (posting_date_start, tag, bucket, etc.)
        
        RETURNS: List of bucket groups with counts and amounts
        """
        # WHAT: Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # WHAT: Get bucket groupings
        # WHY: Provide data for bucket breakdown chart
        # HOW: Call service layer function
        bucket_data = get_entries_by_bucket(queryset)
        
        return Response(bucket_data)
    
    @action(detail=False, methods=['get'], url_path='by-account')
    def by_account(self, request):
        """
        WHAT: Get GL entries grouped by account with aggregates
        WHY: Show top accounts by activity
        HOW: Use service layer grouping function
        
        QUERY PARAMS:
            All standard filter params (posting_date_start, tag, bucket, etc.)
            limit: Max number of accounts to return (default 20)
        
        RETURNS: List of account groups with counts and amounts
        """
        # WHAT: Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # WHAT: Get limit from query params
        # WHY: Allow customization of top N accounts
        # HOW: Parse 'limit' param with default of 20
        limit = int(request.query_params.get('limit', 20))
        
        # WHAT: Get account groupings
        # WHY: Provide data for top accounts analysis
        # HOW: Call service layer function
        account_data = get_entries_by_account(queryset, limit=limit)
        
        return Response(account_data)
    
    @action(detail=False, methods=['get'], url_path='monthly-trend')
    def monthly_trend(self, request):
        """
        WHAT: Get GL entry volume and amounts by month
        WHY: Show time-series trends for dashboard charts
        HOW: Use service layer trend function
        
        QUERY PARAMS:
            All standard filter params (posting_date_start, tag, bucket, etc.)
            months: Number of months to include (default 12)
        
        RETURNS: List of monthly data points with counts and amounts
        """
        # WHAT: Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # WHAT: Get months from query params
        # WHY: Allow customization of trend period
        # HOW: Parse 'months' param with default of 12
        months = int(request.query_params.get('months', 12))
        
        # WHAT: Get monthly trend data
        # WHY: Provide data for time series chart
        # HOW: Call service layer function
        trend_data = get_monthly_trend(queryset, months=months)
        
        return Response(trend_data)
    
    @action(detail=True, methods=['post'], url_path='flag-for-review')
    def flag_for_review(self, request, pk=None):
        """
        WHAT: Flag a GL entry for review
        WHY: Enable workflow for entries needing attention
        HOW: Set requires_review=True and optional review_notes
        
        BODY:
            review_notes: Optional notes about why entry needs review
        
        RETURNS: Updated entry data
        """
        # WHAT: Get the entry instance
        entry = self.get_object()
        
        # WHAT: Set review flag and notes
        # WHY: Mark entry for attention
        # HOW: Update model fields
        entry.requires_review = True
        entry.review_notes = request.data.get('review_notes', '')
        entry.updated_by = request.user
        entry.save()
        
        # WHAT: Return updated entry
        # WHY: Confirm change to frontend
        # HOW: Serialize and return
        serializer = self.get_serializer(entry)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='clear-review-flag')
    def clear_review_flag(self, request, pk=None):
        """
        WHAT: Clear review flag from a GL entry
        WHY: Mark entry as reviewed and resolved
        HOW: Set requires_review=False
        
        RETURNS: Updated entry data
        """
        # WHAT: Get the entry instance
        entry = self.get_object()
        
        # WHAT: Clear review flag
        # WHY: Mark entry as resolved
        # HOW: Update model fields
        entry.requires_review = False
        entry.updated_by = request.user
        entry.save()
        
        # WHAT: Return updated entry
        # WHY: Confirm change to frontend
        # HOW: Serialize and return
        serializer = self.get_serializer(entry)
        return Response(serializer.data)


class ChartOfAccountsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    WHAT: ViewSet for Chart of Accounts (read-only)
    WHY: Provide account reference data for GL entry forms
    HOW: ReadOnlyModelViewSet for list and retrieve only
    
    ENDPOINTS:
        GET /api/chart-of-accounts/     - List all accounts
        GET /api/chart-of-accounts/{id}/ - Retrieve single account
    """
    
    queryset = ChartOfAccounts.objects.all().order_by('account_number')
    serializer_class = ChartOfAccountsSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='lookup')
    def lookup(self, request):
        """
        WHAT: Get chart of accounts as lookup dictionary
        WHY: Provide efficient account reference for validation and dropdowns
        HOW: Return dict keyed by account_number
        
        RETURNS: Dict mapping account_number to account details
        """
        # WHAT: Get lookup dict from service layer
        # WHY: Efficient reference data structure
        # HOW: Call service layer function
        lookup_data = get_chart_of_accounts_lookup()
        
        return Response(lookup_data)

