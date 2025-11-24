"""
WHAT: Serializers for General Ledger Entries
WHY: Transform GL Entry model data to/from JSON for API endpoints
HOW: DRF serializers with field definitions and validation logic
WHERE: Used by GL Entry ViewSets for API responses
"""
from rest_framework import serializers
from core.models import GeneralLedgerEntries, ChartOfAccounts


class ChartOfAccountsSerializer(serializers.ModelSerializer):
    """
    WHAT: Serializer for Chart of Accounts model
    WHY: Provide account lookup data for GL entry forms and dropdowns
    HOW: Simple ModelSerializer exposing all relevant fields
    """
    class Meta:
        model = ChartOfAccounts
        fields = [
            'id',
            'account_number',
            'account_name',
            'account_type',
            'transaction_table_reference',
        ]


class GeneralLedgerEntriesSerializer(serializers.ModelSerializer):
    """
    WHAT: Serializer for General Ledger Entries model
    WHY: Transform GL entries to/from JSON with validation and computed fields
    HOW: ModelSerializer with read-only computed fields and user tracking
    """
    
    # ------------------------------
    # Computed/Read-Only Fields
    # ------------------------------
    # WHAT: Include computed properties from model as read-only fields
    # WHY: Provide calculated values like net_amount and is_balanced to frontend
    # HOW: Use SerializerMethodField for custom computed values
    net_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True,
        help_text='Computed: debit_amount - credit_amount'
    )
    
    is_balanced = serializers.BooleanField(
        read_only=True,
        help_text='Computed: True if debit_amount equals credit_amount'
    )
    
    # ------------------------------
    # User Information Display
    # ------------------------------
    # WHAT: Display username instead of just user ID for audit fields
    # WHY: Make audit trail human-readable in UI without extra lookups
    # HOW: SerializerMethodField to extract username from user object
    created_by_username = serializers.SerializerMethodField()
    updated_by_username = serializers.SerializerMethodField()
    
    # ------------------------------
    # Asset Hub Display
    # ------------------------------
    # WHAT: Include asset hub details for easier frontend display
    # WHY: Avoid extra API calls to fetch asset hub information
    # HOW: SerializerMethodField to include relevant hub data
    asset_hub_display = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneralLedgerEntries
        fields = [
            # Primary identifiers
            'id',
            'entry',
            
            # Company and loan information
            'company_name',
            'loan_number',
            'asset_hub',
            'asset_hub_display',
            'borrower_name',
            
            # Document information
            'document_number',
            'external_document_number',
            'document_type',
            
            # Loan classification
            'loan_type',
            
            # Date fields
            'date_funded',
            'posting_date',
            'entry_date',
            
            # Financial amounts
            'amount',
            'credit_amount',
            'debit_amount',
            'net_amount',
            'is_balanced',
            
            # Account information
            'account_number',
            'account_name',
            
            # Description and comments
            'description',
            'reason_code',
            'comment',
            
            # Cost center
            'cost_center',
            'cost_center_name',
            
            # Tagging and buckets
            'tag',
            'bucket',
            
            # AI and review fields
            'ai_notes',
            'requires_review',
            'review_notes',
            
            # Audit fields
            'created_by',
            'created_by_username',
            'updated_by',
            'updated_by_username',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'net_amount',
            'is_balanced',
            'created_by_username',
            'updated_by_username',
            'asset_hub_display',
        ]
    
    def get_created_by_username(self, obj):
        """
        WHAT: Extract username from created_by user object
        WHY: Provide human-readable creator info for audit trail
        HOW: Safe access to user.username with None fallback
        """
        return obj.created_by.username if obj.created_by else None
    
    def get_updated_by_username(self, obj):
        """
        WHAT: Extract username from updated_by user object
        WHY: Provide human-readable updater info for audit trail
        HOW: Safe access to user.username with None fallback
        """
        return obj.updated_by.username if obj.updated_by else None
    
    def get_asset_hub_display(self, obj):
        """
        WHAT: Get asset hub display information
        WHY: Provide quick asset context without extra API calls
        HOW: Return dict with hub ID and key identifiers
        """
        if not obj.asset_hub:
            return None
        
        return {
            'id': obj.asset_hub.id,
            'sellertape_id': obj.asset_hub.sellertape_id,
            'servicer_id': obj.asset_hub.servicer_id,
        }
    
    def create(self, validated_data):
        """
        WHAT: Override create to automatically set created_by from request user
        WHY: Ensure audit trail captures who created each entry
        HOW: Extract user from context and set created_by field
        """
        # WHAT: Get the current user from the serializer context
        # WHY: Need to set created_by field for audit trail
        # HOW: Access request object passed in serializer context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        WHAT: Override update to automatically set updated_by from request user
        WHY: Ensure audit trail captures who updated each entry
        HOW: Extract user from context and set updated_by field
        """
        # WHAT: Get the current user from the serializer context
        # WHY: Need to set updated_by field for audit trail
        # HOW: Access request object passed in serializer context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)


class GLEntryListSerializer(serializers.ModelSerializer):
    """
    WHAT: Lightweight serializer for GL entry list views
    WHY: Reduce payload size for grid/table displays with many entries
    HOW: Include only essential fields for list display
    """
    
    # WHAT: Include computed net amount for quick display
    net_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    
    # WHAT: Include username for display
    created_by_username = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneralLedgerEntries
        fields = [
            'id',
            'entry',
            'posting_date',
            'entry_date',
            'company_name',
            'loan_number',
            'asset_hub',
            'account_number',
            'account_name',
            'debit_amount',
            'credit_amount',
            'net_amount',
            'tag',
            'bucket',
            'requires_review',
            'created_by_username',
            'created_at',
        ]
    
    def get_created_by_username(self, obj):
        """Get username for display"""
        return obj.created_by.username if obj.created_by else None


class GLEntrySummarySerializer(serializers.Serializer):
    """
    WHAT: Serializer for GL entry summary statistics
    WHY: Provide aggregate data for dashboard KPIs and charts
    HOW: Plain Serializer with computed aggregate fields
    """
    
    # WHAT: Summary statistics fields
    # WHY: Display key metrics on dashboard header/cards
    # HOW: Fields populated by service layer aggregations
    total_entries = serializers.IntegerField()
    total_debits = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_credits = serializers.DecimalField(max_digits=20, decimal_places=2)
    net_total = serializers.DecimalField(max_digits=20, decimal_places=2)
    entries_requiring_review = serializers.IntegerField()
    date_range_start = serializers.DateField(required=False, allow_null=True)
    date_range_end = serializers.DateField(required=False, allow_null=True)
    
    # WHAT: Breakdown by tag
    # WHY: Show distribution of entries by category
    # HOW: Dict field with tag counts
    by_tag = serializers.DictField(child=serializers.IntegerField(), required=False)
    
    # WHAT: Breakdown by bucket
    # WHY: Show distribution of entries by strategic bucket
    # HOW: Dict field with bucket counts
    by_bucket = serializers.DictField(child=serializers.IntegerField(), required=False)

