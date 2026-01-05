from django.contrib import admin
from django.db.models import Exists, OuterRef
from django.utils.html import format_html
from django.urls import reverse
from urllib.parse import quote
from core.models import (
    DebtFacility,
    CoInvestor,
    InvestorContribution,
    InvestorDistribution,
    # New fund administration models
    Entity,
    FundLegalEntity,
    FundMembership,
    EntityMembership,
    FirmCRM,
    MasterCRM,
    AssetIdHub,
    AssetDetails,
    Servicer,
    StateReference,
    CountyReference,
    MSAReference,
    HUDZIPCBSACrosswalk,
    BrokerMSAAssignment,
    FCStatus,
    FCTimelines,
    CommercialUnits,
    HOAAssumption,
    PropertyTypeAssumption,
    SquareFootageAssumption,
    UnitBasedAssumption,
    LlDataEnrichment,
    Valuation,
    ValuationGradeReference,
    Photo,
    Document,
    LLTransactionSummary,
    LLCashFlowSeries,
    UnitMix,
    RentRoll,
    ComparableProperty,
    SalesComparable,
    LeaseComparable,
    LeaseComparableUnitMix,
    LeaseComparableRentRoll,
    HistoricalPropertyCashFlow,
    CalendarEvent,
    GeneralLedgerEntries,
    ChartOfAccounts,
    Notification,
    NotificationRead,
)

# Cross-app children that reference AssetIdHub
from acq_module.models.model_acq_seller import SellerRawData, Trade


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "title", "asset_hub", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("title", "message", "asset_hub__id")
    readonly_fields = ("created_at",)


@admin.register(NotificationRead)
class NotificationReadAdmin(admin.ModelAdmin):
    list_display = ("id", "notification", "user", "read_at")
    list_filter = ("read_at",)
    search_fields = ("notification__title", "user__username", "user__email")
    readonly_fields = ("read_at",)
# Asset Details admin
@admin.register(AssetDetails)
class AssetDetailsAdmin(admin.ModelAdmin):
    """Admin configuration for AssetDetails model linking assets to fund legal entities."""
    list_display = ("asset", "get_servicer_id", "fund_legal_entity", "trade", "asset_status", "legacy_flag", "created_at", "updated_at")
    list_filter = ("trade", "asset_status", "legacy_flag")
    search_fields = ("asset__id", "asset__servicer_id", "fund_legal_entity__nickname_name", "trade__trade_name")
    autocomplete_fields = ["asset", "fund_legal_entity"]
    readonly_fields = ("get_servicer_id", "created_at", "updated_at")
    # WHAT: Only show fund_legal_entity, not Entity directly
    # WHY: AssetDetails should only link to FundLegalEntity, not Entity
    fieldsets = (
        ("Links", {
            "fields": ("asset", "get_servicer_id", "fund_legal_entity", "trade")
        }),
        ("Status", {
            "fields": ("asset_status", "is_commercial", "legacy_flag")
        }),
        ("Audit", {
            "fields": ("created_at", "updated_at")
        }),
    )
    
    def get_servicer_id(self, obj):
        """Display servicer_id from related AssetIdHub (read-only, no storage)."""
        return obj.asset.servicer_id if obj.asset else None
    get_servicer_id.short_description = "Servicer ID"
    get_servicer_id.admin_order_field = "asset__servicer_id"  # Enable sorting by this field
# DEPRECATED: SellerBoardedData - use SellerRawData instead
# from am_module.models.boarded_data import SellerBoardedData, BlendedOutcomeModel
from am_module.models.boarded_data import BlendedOutcomeModel
from am_module.models.servicers import ServicerLoanData

# Use standard Django admin site

@admin.register(DebtFacility)
class DebtFacilityAdmin(admin.ModelAdmin):
    list_display = (
        "facility_name",  # renamed from partner_name to facility_name to match model field
        "firm_name",
        "commitment_size",
        "rate_index",
        "sofr_rate",
        "spread_bps",
        "start_date",
        "end_date",
        "created_at",
    )
    list_filter = ("rate_index", "start_date", "end_date")
    search_fields = ("facility_name", "firm_name")
    list_per_page = 5

@admin.register(CoInvestor)
class CoInvestorAdmin(admin.ModelAdmin):
    """Admin configuration for CoInvestor model.
    
    What: Parent investor record with commitment and ownership details.
    Why: Central management of investor relationships.
    How: Shows computed totals from child contribution/distribution records.
    """
    list_display = (
        "get_investor_name",
        "get_firm_name",
        "commitment_amount",
        "ownership_percentage",
        "get_total_contributed",
        "get_total_distributed",
        "get_net_position",
        "is_active",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("crm_contact__contact_name", "crm_contact__firm_ref__name", "notes")
    list_per_page = 5
    autocomplete_fields = ['crm_contact']
    readonly_fields = ('created_at', 'updated_at')
    
    def get_investor_name(self, obj):
        """Display investor contact name from CRM"""
        return obj.crm_contact.contact_name if obj.crm_contact else '—'
    get_investor_name.short_description = 'Investor Name'
    
    def get_firm_name(self, obj):
        """Display investor firm name from CRM"""
        return obj.crm_contact.firm if obj.crm_contact else '—'
    get_firm_name.short_description = 'Firm'
    
    def get_total_contributed(self, obj):
        """Display total contributions from child records"""
        return f"${obj.total_contributed():,.2f}"
    get_total_contributed.short_description = 'Total Contributed'
    
    def get_total_distributed(self, obj):
        """Display total distributions from child records"""
        return f"${obj.total_distributed():,.2f}"
    get_total_distributed.short_description = 'Total Distributed'
    
    def get_net_position(self, obj):
        """Display net position (contributions - distributions)"""
        return f"${obj.net_position():,.2f}"
    get_net_position.short_description = 'Net Position'


@admin.register(InvestorContribution)
class InvestorContributionAdmin(admin.ModelAdmin):
    """Admin configuration for InvestorContribution model.
    
    What: Individual contribution transaction records.
    Why: Track all capital contributions with full audit trail.
    How: Links to parent CoInvestor with date, amount, and payment details.
    """
    list_display = (
        "get_investor_name",
        "contribution_date",
        "amount",
        "payment_method",
        "reference_number",
        "created_at",
    )
    list_filter = ("contribution_date", "payment_method")
    search_fields = (
        "co_investor__crm_contact__contact_name",
        "co_investor__crm_contact__firm_ref__name",
        "reference_number",
        "notes"
    )
    list_per_page = 5
    autocomplete_fields = ['co_investor']
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'contribution_date'
    
    def get_investor_name(self, obj):
        """Display investor name from parent CoInvestor"""
        return str(obj.co_investor)
    get_investor_name.short_description = 'Investor'


@admin.register(InvestorDistribution)
class InvestorDistributionAdmin(admin.ModelAdmin):
    """Admin configuration for InvestorDistribution model.
    
    What: Individual distribution transaction records.
    Why: Track all distributions with type categorization for tax reporting.
    How: Links to parent CoInvestor with date, amount, type, and payment details.
    """
    list_display = (
        "get_investor_name",
        "distribution_date",
        "amount",
        "distribution_type",
        "payment_method",
        "reference_number",
        "created_at",
    )
    list_filter = ("distribution_date", "distribution_type", "payment_method")
    search_fields = (
        "co_investor__crm_contact__contact_name",
        "co_investor__crm_contact__firm",
        "reference_number",
        "notes"
    )
    list_per_page = 5
    autocomplete_fields = ['co_investor']
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'distribution_date'
    
    def get_investor_name(self, obj):
        """Display investor name from parent CoInvestor"""
        return str(obj.co_investor)
    get_investor_name.short_description = 'Investor'


# =============================================================================
# NEW FUND ADMINISTRATION ADMIN CLASSES
# =============================================================================


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    """Admin configuration for Entity model.
    
    What: Manage all entities (individuals, LLCs, trusts, etc.)
    Why: Universal entity tracking for fund administration
    How: Display entity details with search and filtering
    """
    list_display = (
        "name",
        "entity_type",
        "tax_id",
        "email",
        "phone",
        "is_active",
        "get_fund_memberships_count",
        "created_at",
    )
    list_filter = ("entity_type", "is_active")
    search_fields = ("name", "tax_id", "email", "phone", "notes")
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'entity_type', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'tax_id')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
    
    def get_fund_memberships_count(self, obj):
        """Count fund memberships"""
        count = obj.fund_memberships.filter(is_active=True).count()
        return count if count > 0 else '—'
    get_fund_memberships_count.short_description = 'Fund Memberships'


@admin.register(FundLegalEntity)
class FundLegalEntityAdmin(admin.ModelAdmin):
    """Admin configuration for FundLegalEntity model.
    
    What: Manage legal entities within fund structures
    Why: Track master funds, feeders, SPVs, GP entities
    How: Display entity role, jurisdiction, and parent fund
    """
    list_display = (
        "get_display_name",
        "get_fund_name",
        "entity_role",
        "jurisdiction",
        "tax_id",
        "is_active",
        "get_members_count",
        "created_at",
    )
    list_filter = ("entity_role", "is_active", "jurisdiction")
    search_fields = ("nickname_name", "tax_id", "fund__name")
    list_per_page = 25
    autocomplete_fields = ['fund']
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Fund Structure', {
            'fields': ('fund', 'entity_role', 'is_active')
        }),
        ('Legal Details', {
            'fields': ('nickname_name', 'jurisdiction', 'tax_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_display_name(self, obj):
        """Display nickname or fallback placeholder for entity"""
        return obj.nickname_name if obj.nickname_name else "Unnamed Entity"
    get_display_name.short_description = 'Entity'

    def get_fund_name(self, obj):
        """Display parent fund name"""
        return obj.fund.name
    get_fund_name.short_description = 'Fund'
    get_fund_name.admin_order_field = 'fund__name'
    
    def get_members_count(self, obj):
        """Count members investing through this entity"""
        count = obj.members.filter(is_active=True).count()
        return count if count > 0 else '—'
    get_members_count.short_description = 'Members'


@admin.register(FundMembership)
class FundMembershipAdmin(admin.ModelAdmin):
    """Admin configuration for FundMembership model.
    
    What: Manage GP/LP memberships in funds
    Why: Track capital commitments, contributions, and ownership
    How: Display entity, fund, member type, and capital details
    """
    list_display = (
        "get_entity_name",
        "get_fund_name",
        "member_type",
        "ownership_percentage",
        "capital_committed",
        "capital_contributed",
        "get_remaining_commitment",
        "admission_date",
        "is_active",
    )
    list_filter = ("member_type", "is_active", "admission_date")
    search_fields = (
        "entity__name",
        "fund__name",
    )
    list_per_page = 25
    autocomplete_fields = ['fund', 'entity', 'investing_through']
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'admission_date'
    
    fieldsets = (
        ('Membership Structure', {
            'fields': ('fund', 'entity', 'member_type', 'admission_date', 'is_active')
        }),
        ('Ownership & Capital', {
            'fields': ('ownership_percentage', 'capital_committed', 'capital_contributed')
        }),
        ('Investment Details', {
            'fields': ('investing_through',),
            'description': 'Optional: specify which fund legal entity they invest through'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_entity_name(self, obj):
        """Display entity name"""
        return obj.entity.name
    get_entity_name.short_description = 'Entity'
    get_entity_name.admin_order_field = 'entity__name'
    
    def get_fund_name(self, obj):
        """Display fund name"""
        return obj.fund.name
    get_fund_name.short_description = 'Fund'
    get_fund_name.admin_order_field = 'fund__name'
    
    def get_remaining_commitment(self, obj):
        """Calculate and display remaining commitment"""
        remaining = obj.remaining_commitment()
        return f"${remaining:,.2f}"
    get_remaining_commitment.short_description = 'Remaining Commitment'


@admin.register(EntityMembership)
class EntityMembershipAdmin(admin.ModelAdmin):
    """Admin configuration for EntityMembership model.
    
    What: Manage nested entity ownership (e.g., who owns the GP entity)
    Why: Track ultimate beneficial ownership and GP member interests
    How: Display ownership relationships, percentages, and capital accounts
    """
    list_display = (
        "get_member_name",
        "get_parent_name",
        "ownership_percentage",
        "get_distribution_pct",
        "capital_account",
        "membership_date",
        "is_active",
    )
    list_filter = ("is_active", "membership_date")
    search_fields = (
        "member_entity__name",
        "parent_entity__name",
        "notes"
    )
    list_per_page = 25
    autocomplete_fields = ['parent_entity', 'member_entity']
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'membership_date'
    
    fieldsets = (
        ('Ownership Structure', {
            'fields': ('parent_entity', 'member_entity', 'membership_date', 'is_active')
        }),
        ('Ownership Details', {
            'fields': ('ownership_percentage', 'distribution_percentage', 'capital_account'),
            'description': 'Distribution % defaults to ownership % if not specified'
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
    
    def get_member_name(self, obj):
        """Display member entity name"""
        return obj.member_entity.name
    get_member_name.short_description = 'Member (Owner)'
    get_member_name.admin_order_field = 'member_entity__name'
    
    def get_parent_name(self, obj):
        """Display parent entity name"""
        return obj.parent_entity.name
    get_parent_name.short_description = 'Parent (Owned)'
    get_parent_name.admin_order_field = 'parent_entity__name'
    
    def get_distribution_pct(self, obj):
        """Display effective distribution percentage"""
        return f"{obj.effective_distribution_percentage()}%"
    get_distribution_pct.short_description = 'Distribution %'


@admin.register(FirmCRM)
class FirmCRMAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'phone', 'email', 'states_list', 'created_at'
    )
    search_fields = ('name', 'email', 'phone')
    list_filter = ('states',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

    def states_list(self, obj):
        return ", ".join(sorted([s.state_code for s in obj.states.all()])) or ''


@admin.register(MasterCRM)
class MasterCRMAdmin(admin.ModelAdmin):
    """Admin configuration for unified Master CRM (Brokercrm) model."""
    list_display = (
        'contact_name', 'firm', 'email', 'states_list', 'city', 'tag',
        'alt_contact_name', 'nda_flag', 'nda_signed', 'created_at'
    )
    list_filter = (
        'states', 'tag', 'nda_flag'
    )
    search_fields = (
        'contact_name', 'email', 'firm_ref__name', 'city',
        'alt_contact_name', 'alt_contact_email'
    )
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50
    # No fieldsets: show all fields by default

    def states_list(self, obj):
        return ", ".join(sorted([s.state_code for s in obj.states.all()])) or '—'
    states_list.short_description = 'States'



@admin.register(Servicer)
class ServicerAdmin(admin.ModelAdmin):
    """Admin configuration for Servicer model."""
    list_display = (
        'servicer_name', 'contact_name', 'contact_email', 'contact_phone',
        'board_fee', 'current_fee', 'fc_fee', 'bk_fee', 'mod_fee', 'dil_fee',
    )
    search_fields = ('servicer_name', 'contact_name', 'contact_email')
    list_filter = ()
    list_per_page = 5




@admin.register(ValuationGradeReference)
class ValuationGradeReferenceAdmin(admin.ModelAdmin):
    """Admin for ValuationGradeReference model.
    
    WHAT: Manage valuation grade reference data (A+, A, B, C, D, F)
    WHY: Allow creating/editing grade definitions used in Valuation FK
    HOW: Simple list/edit interface for reference data
    """
    list_display = (
        'code', 'label', 'sort_order', 'description', 'created_at', 'updated_at'
    )
    list_filter = ('code',)
    search_fields = ('code', 'label', 'description')
    ordering = ('sort_order', 'code')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 10
    
    fieldsets = (
        ('Grade Information', {
            'fields': ('code', 'label', 'sort_order', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Valuation)
class ValuationAdmin(admin.ModelAdmin):
    """Admin for the unified Valuation model.
    
    WHAT: Optimized admin for Valuation with efficient FK loading
    WHY: Prevent N+1 queries when displaying list with ForeignKey fields
    HOW: Use list_select_related to load asset_hub, grade, broker_contact in single query
    """
    list_display = (
        'id', 'asset_hub', 'source', 'grade', 'asis_value', 'arv_value', 'value_date', 'created_at'
    )
    list_filter = (
        'source', 'grade', 'value_date'
    )
    search_fields = (
        'asset_hub__id', 'notes'
    )
    autocomplete_fields = ['grade', 'broker_contact']
    # PERFORMANCE: Load ForeignKeys in single query to avoid N+1 problem
    # For 54 records: reduces ~109 queries down to 1 query
    list_select_related = ('asset_hub', 'grade', 'broker_contact')
    # No fieldsets: show all fields by default
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25  # Increased from 5 to reduce pagination clicks


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    """Admin for the Photo model."""
    list_display = (
        'id', 'asset_hub', 'valuation', 'source_tag', 'caption', 'created_at'
    )
    list_filter = (
        'source_tag',
    )
    search_fields = (
        'asset_hub__id', 'caption'
    )
    list_per_page = 5


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin for the Document model."""
    list_display = (
        'id', 'asset_hub', 'valuation', 'original_name', 'uploaded_at'
    )
    search_fields = (
        'asset_hub__id', 'original_name'
    )
    list_per_page = 5


@admin.register(StateReference)
class StateReferenceAdmin(admin.ModelAdmin):
    """Admin configuration for StateReference model."""
    list_display = (
        'state_code', 'state_name', 'judicialvsnonjudicial', 'fc_state_months'
    )
    search_fields = ('state_code', 'state_name')
    list_filter = ('judicialvsnonjudicial',)
    list_per_page = 50


@admin.register(CountyReference)
class CountyReferenceAdmin(admin.ModelAdmin):
    """
    WHAT: Admin configuration for CountyReference model
    WHY: Allow viewing and managing county reference data
    HOW: Display county FIPS, name, state, population with search and filters
    """
    list_display = (
        'county_fips', 'county_name', 'get_state_code', 'population', 'county_seat'
    )
    search_fields = ('county_fips', 'county_name', 'county_seat')
    list_filter = ('state',)
    ordering = ('state', 'county_name')
    autocomplete_fields = ['state']
    list_per_page = 50
    
    def get_state_code(self, obj):
        """Display state abbreviation"""
        return obj.state.state_code if obj.state else '—'
    get_state_code.short_description = 'State'
    get_state_code.admin_order_field = 'state__state_code'


@admin.register(MSAReference)
class MSAReferenceAdmin(admin.ModelAdmin):
    """
    WHAT: Admin configuration for MSAReference model
    WHY: Allow viewing and managing MSA reference data from Census Bureau
    HOW: Display MSA code, name, state with search and filters
    """
    list_display = (
        'msa_code', 'msa_name', 'get_state_code', 'get_broker_count'
    )
    search_fields = ('msa_code', 'msa_name')
    list_filter = ('state',)
    ordering = ('msa_name',)
    autocomplete_fields = ['state']
    list_per_page = 50
    
    def get_state_code(self, obj):
        """Display state abbreviation"""
        return obj.state.state_code if obj.state else '—'
    get_state_code.short_description = 'State'
    get_state_code.admin_order_field = 'state__state_code'
    
    def get_broker_count(self, obj):
        """Display count of brokers assigned to this MSA"""
        return obj.broker_assignments.filter(is_active=True).count()
    get_broker_count.short_description = 'Brokers'


@admin.register(HUDZIPCBSACrosswalk)
class HUDZIPCBSACrosswalkAdmin(admin.ModelAdmin):
    """
    WHAT: Admin configuration for HUDZIPCBSACrosswalk model that stores the raw HUD
          ZIP-to-CBSA crosswalk file we bulk import each quarter.
    WHY:  Product and ops teams occasionally need to audit the source rows, confirm
          ratios for split ZIP codes, and spot-check CBSA assignments without
          digging through the CSV on disk.
    HOW:  Provide read-only list filters, search, and formatted ratio columns so the
          HUD data is easy to browse directly in Django Admin.
    """

    # WHAT: Columns shown in changelist view
    # WHY: Quickly scan ZIP, CBSA, geography, and weight ratios
    # HOW: Include formatted ratio helpers plus imported_at timestamp for audits
    list_display = (
        'zip_code',
        'cbsa_code',
        'city',
        'state_code',
        'res_ratio_display',
        'bus_ratio_display',
        'oth_ratio_display',
        'tot_ratio_display',
        'imported_at',
    )

    # WHAT: Search configuration
    # WHY: Allow quick lookup by ZIP, CBSA, or city name
    search_fields = ('zip_code', 'cbsa_code', 'city')

    # WHAT: Filters and ordering
    # WHY: Slice records by state and ensure consistent ordering for review
    list_filter = ('state_code',)
    ordering = ('zip_code', '-tot_ratio')

    # WHAT: Make import timestamp read-only (auto-managed)
    readonly_fields = ('imported_at',)

    # WHAT: Paginate helps keep UI responsive when browsing 47k+ rows
    list_per_page = 100

    def _format_ratio(self, value: float) -> str:
        """
        WHAT: Shared helper to convert Decimal ratios (0-1) into percentage strings.
        WHY: HUD publishes ratios as decimals; humans prefer reading percentages.
        HOW: Multiply by 100, format with one decimal place, return '--' if value missing.
        """
        if value is None:
            return '--'
        return f"{value * 100:.1f}%"

    def res_ratio_display(self, obj):
        """
        WHAT: Display residential ratio percentage for changelist.
        WHY: Shows concentration of residential addresses per CBSA.
        HOW: Call helper to format obj.res_ratio.
        """
        return self._format_ratio(obj.res_ratio)

    res_ratio_display.short_description = 'Res %'

    def bus_ratio_display(self, obj):
        """
        WHAT: Display business ratio percentage for changelist.
        WHY: Helps identify commercial-heavy ZIPs.
        HOW: Format obj.bus_ratio via helper.
        """
        return self._format_ratio(obj.bus_ratio)

    bus_ratio_display.short_description = 'Bus %'

    def oth_ratio_display(self, obj):
        """
        WHAT: Display 'other' delivery point ratio percentage.
        WHY: Useful for PO boxes / military ZIP diagnostics.
        HOW: Format obj.oth_ratio via helper.
        """
        return self._format_ratio(obj.oth_ratio)

    oth_ratio_display.short_description = 'Oth %'

    def tot_ratio_display(self, obj):
        """
        WHAT: Display total ratio percentage (dominant CBSA weight).
        WHY: Helps quickly confirm which CBSA dominates the ZIP.
        HOW: Format obj.tot_ratio via helper.
        """
        return self._format_ratio(obj.tot_ratio)

    tot_ratio_display.short_description = 'Tot %'


@admin.register(BrokerMSAAssignment)
class BrokerMSAAssignmentAdmin(admin.ModelAdmin):
    """
    WHAT: Admin configuration for BrokerMSAAssignment junction table
    WHY: Allow creating and managing broker-to-MSA assignments
    HOW: Display broker, MSA, priority, active status with filters
    """
    list_display = (
        'get_broker_name', 'get_msa_name', 'priority', 'is_active', 
        'created_at', 'updated_at'
    )
    search_fields = (
        'broker__contact_name', 'broker__firm_ref__name', 'msa__msa_name', 'msa__msa_code'
    )
    list_filter = ('is_active', 'priority', 'msa__state')
    ordering = ('msa', 'priority', 'broker')
    autocomplete_fields = ['broker']  # Keep broker autocomplete; MSA uses filtered dropdown
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('broker', 'msa', 'priority', 'is_active')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_broker_name(self, obj):
        """Display broker name"""
        return obj.broker.contact_name or obj.broker.firm or f"Broker #{obj.broker.id}"
    get_broker_name.short_description = 'Broker'
    get_broker_name.admin_order_field = 'broker__contact_name'
    
    def get_msa_name(self, obj):
        """Display MSA name (truncated)"""
        if not obj.msa:
            return "No MSA"
        name = obj.msa.msa_name
        return name[:50] + '...' if len(name) > 50 else name
    get_msa_name.short_description = 'MSA'
    get_msa_name.admin_order_field = 'msa__msa_name'

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "msa":
            broker = None

            # When editing an existing assignment, use its broker
            if hasattr(request, "_obj_") and request._obj_:
                broker = request._obj_.broker

            # On add, broker may be preselected via GET/POST (?broker=<id>)
            if broker is None:
                broker_id = request.GET.get("broker") or request.POST.get("broker")
                if broker_id:
                    try:
                        broker = MasterCRM.objects.get(pk=broker_id)
                    except MasterCRM.DoesNotExist:  # noqa: F821
                        broker = None

            if broker:
                broker_states = broker.states.all()
                if broker_states.exists():
                    kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                        state__in=broker_states
                    )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(FCStatus)
class FCStatusAdmin(admin.ModelAdmin):
    """Admin configuration for FCStatus model.
    
    What this does:
    - Manages foreclosure status records with categorical choices
    - Displays status, order, and associated metadata in list view
    - Allows filtering and searching by status category
    """
    list_display = (
        'id', 'status', 'order', 'notes', 'created_at', 'updated_at'
    )
    list_filter = ('status',)
    search_fields = ('notes',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order', 'status')
    list_per_page = 5
    
    # No fieldsets: show all fields by default


@admin.register(FCTimelines)
class FCTimelinesAdmin(admin.ModelAdmin):
    """Admin configuration for FCTimelines model.
    
    What this does:
    - Manages state-specific foreclosure timeline data
    - Links states to foreclosure statuses with duration and cost metrics
    - Enforces unique state/status combinations
    """
    list_display = (
        'state', 'fc_status', 'duration_days', 'cost_avg', 'updated_at'
    )
    list_filter = ('state', 'fc_status__status')
    search_fields = ('state__state_code', 'state__state_name', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['state', 'fc_status']
    list_per_page = 5
    
    # No fieldsets: show all fields by default


@admin.register(CommercialUnits)
class CommercialUnitsAdmin(admin.ModelAdmin):
    """Admin configuration for CommercialUnits model.
    
    What this does:
    - Manages commercial unit scaling factors
    - Displays unit counts and their associated cost/duration multipliers
    - Used for adjusting assumptions based on property unit count
    """
    list_display = (
        'units', 'fc_cost_scale', 'rehab_cost_scale', 'rehab_duration_scale',
        'created_at', 'updated_at'
    )
    search_fields = ('units',)
    ordering = ('units',)
    readonly_fields = ('created_at', 'updated_at')
    
    # No fieldsets: show all fields by default
    list_per_page = 5


@admin.register(HOAAssumption)
class HOAAssumptionAdmin(admin.ModelAdmin):
    """Admin configuration for HOAAssumption model.
    
    What this does:
    - Manages HOA fee assumptions by property type
    - Displays property types and their associated monthly HOA fees
    - Used for estimating ongoing carrying costs in financial calculations
    """
    list_display = (
        'property_type', 'monthly_hoa_fee', 'notes', 'created_at', 'updated_at'
    )
    list_filter = ('property_type',)
    search_fields = ('property_type', 'notes')
    ordering = ('property_type',)
    readonly_fields = ('created_at', 'updated_at')
    
    # No fieldsets: show all fields by default
    list_per_page = 5


@admin.register(LlDataEnrichment)
class LlDataEnrichmentAdmin(admin.ModelAdmin):
    """
    WHAT: Performance-focused admin configuration for LlDataEnrichment.
    WHY:  The default form renders every field from SellerRawData, creating massive
          select widgets that freeze the UI for ~200 seconds.
    HOW:  Use raw ID widgets, select_related, and trimmed fieldsets so the page only
          fetches essential data.
    """

    # WHAT: Columns shown in the changelist for quick scan of geocode status.
    list_display = (
        'asset_hub',                  # Hub link for the underlying loan
        'geocode_lat',                # Latitude from Geocodio
        'geocode_lng',                # Longitude from Geocodio
        'geocode_msa_code',           # CBSA/MSA code returned
        'geocode_msa',                # Human readable MSA label
        'geocoded_at',                # Timestamp of the API call
    )

    # WHAT: Allow searching by hub ID or any stored address string.
    search_fields = (
        'asset_hub__id',
        'geocode_full_address',
        'geocode_used_address',
        'geocode_display_address',
    )

    # WHAT: Slice list view by MSA or county so ops teams can focus on specific geographies.
    list_filter = (
        'geocode_msa_code',
        'geocode_county',
    )

    # WHAT: Keep pagination small because staff uses filters heavily.
    list_per_page = 50

    # WHAT: Eliminate massive select widgets by switching to raw ID inputs.
    raw_id_fields = (
        'asset_hub',                  # Hub records are large; raw ID keeps form fast
    )

    # WHAT: Mark enrichment outputs as read-only to prevent hand edits and avoid validation.
    readonly_fields = (
        'geocode_lat',
        'geocode_lng',
        'geocode_used_address',
        'geocode_full_address',
        'geocode_display_address',
        'geocode_county',
        'geocode_msa',
        'geocode_msa_code',
        'geocoded_at',
        'created_at',
        'updated_at',
    )

    # WHAT: Only render a handful of fields grouped by purpose so templates stay light.
    fieldsets = (
        (
            'Source Links',
            {
                'description': 'Pointer back to the original loan rows via hub.',
                'fields': ('asset_hub',),
            },
        ),
        (
            'Geocode Output',
            {
                'fields': (
                    'geocode_used_address',
                    'geocode_full_address',
                    'geocode_display_address',
                    'geocode_lat',
                    'geocode_lng',
                    'geocode_county',
                    'geocode_msa',
                    'geocode_msa_code',
                ),
                'classes': ('collapse',),  # Collapse to keep form compact
            },
        ),
        (
            'Audit',
            {
                'fields': ('geocoded_at', 'created_at', 'updated_at'),
                'classes': ('collapse',),
            },
        ),
    )

    # WHAT: Ensure queryset pulls related seller/trade rows in one query.
    def get_queryset(self, request):
        """Load heavy foreign keys up front to avoid per-row SQL hits."""
        qs = super().get_queryset(request)
        return qs.select_related(
            'asset_hub',                       # Optional hub link displayed in raw ID widget
            'asset_hub__acq_raw',              # Base loan row (SellerRawData via hub)
            'asset_hub__acq_raw__trade',       # Trade info used in filters/search
            'asset_hub__acq_raw__seller',      # Seller info used in search
        )


@admin.register(PropertyTypeAssumption)
class PropertyTypeAssumptionAdmin(admin.ModelAdmin):
    """Admin for property type-based utility and property management assumptions."""
    list_display = (
        'property_type', 'total_monthly_utilities', 'total_monthly_property_management', 
        'total_one_time_costs', 'is_active', 'updated_at'
    )
    list_filter = ('property_type', 'is_active')
    search_fields = ('property_type', 'notes')
    ordering = ('property_type',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('property_type', 'is_active', 'notes')
        }),
        ('Monthly Utility Costs', {
            'fields': (
                'utility_electric_monthly', 'utility_gas_monthly', 'utility_water_monthly',
                'utility_sewer_monthly', 'utility_trash_monthly', 'utility_other_monthly'
            )
        }),
        ('Monthly Property Management Costs', {
            'fields': (
                'property_management_monthly', 'repairs_maintenance_monthly', 'marketing_monthly',
                'security_cost_monthly', 'landscaping_monthly', 'pool_maintenance_monthly'
            )
        }),
        ('One-Time Costs', {
            'fields': ('trashout_cost', 'renovation_cost')
        }),
    )
    
    def total_monthly_utilities(self, obj):
        """Display total monthly utility costs."""
        return f"${obj.total_monthly_utilities():,.2f}"
    total_monthly_utilities.short_description = "Total Monthly Utilities"
    
    def total_monthly_property_management(self, obj):
        """Display total monthly property management costs."""
        return f"${obj.total_monthly_property_management():,.2f}"
    total_monthly_property_management.short_description = "Total Monthly Prop Mgmt"
    
    def total_one_time_costs(self, obj):
        """Display total one-time costs."""
        return f"${obj.total_one_time_costs():,.2f}"
    total_one_time_costs.short_description = "Total One-Time Costs"


@admin.register(SquareFootageAssumption)
class SquareFootageAssumptionAdmin(admin.ModelAdmin):
    """Admin for square footage-based utility and property management assumptions."""
    list_display = (
        'property_category', 'description', 'is_active', 'updated_at'
    )
    list_filter = ('property_category', 'is_active')
    search_fields = ('description', 'notes')
    ordering = ('property_category', 'description')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('property_category', 'description', 'is_active', 'notes')
        }),
        ('Per Square Foot Monthly Utility Costs', {
            'fields': (
                'utility_electric_per_sqft', 'utility_gas_per_sqft', 'utility_water_per_sqft',
                'utility_sewer_per_sqft', 'utility_trash_per_sqft', 'utility_other_per_sqft'
            )
        }),
        ('Per Square Foot Monthly Property Management Costs', {
            'fields': (
                'property_management_per_sqft', 'repairs_maintenance_per_sqft', 'marketing_per_sqft',
                'security_cost_per_sqft', 'landscaping_per_sqft', 'pool_maintenance_per_sqft'
            )
        }),
        ('Per Square Foot One-Time Costs', {
            'fields': ('trashout_per_sqft', 'renovation_per_sqft')
        }),
    )


@admin.register(UnitBasedAssumption)
class UnitBasedAssumptionAdmin(admin.ModelAdmin):
    """Admin for unit-based utility and property management assumptions."""
    list_display = (
        'unit_range', 'description', 'is_active', 'updated_at'
    )
    list_filter = ('is_active',)
    search_fields = ('description', 'notes')
    ordering = ('units_min',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('units_min', 'units_max', 'description', 'is_active', 'notes')
        }),
        ('Per Unit Monthly Utility Costs', {
            'fields': (
                'utility_electric_per_unit', 'utility_gas_per_unit', 'utility_water_per_unit',
                'utility_sewer_per_unit', 'utility_trash_per_unit', 'utility_other_per_unit'
            )
        }),
        ('Per Unit Monthly Property Management Costs', {
            'fields': (
                'property_management_per_unit', 'repairs_maintenance_per_unit', 'marketing_per_unit',
                'security_cost_per_unit', 'landscaping_per_unit', 'pool_maintenance_per_unit'
            )
        }),
        ('Per Unit One-Time Costs', {
            'fields': ('trashout_per_unit', 'renovation_per_unit')
        }),
    )
    
    def unit_range(self, obj):
        """Display unit count range."""
        max_display = f"{obj.units_max}" if obj.units_max else "∞"
        return f"{obj.units_min} - {max_display} units"
    unit_range.short_description = "Unit Count Range"


@admin.register(UnitMix)
class UnitMixAdmin(admin.ModelAdmin):
    """
    Admin configuration for UnitMix model.
    
    What: Manages unit mix records for commercial/multi-family properties.
    Why: Allow viewing and editing of unit type, count, sqft, and rent data.
    How: Display key metrics including calculated price_sqft field.
    """
    list_display = (
        'id', 'unit_type', 'unit_count', 'unit_avg_sqft', 'unit_avg_rent',
        'price_sqft', 'total_sqft_display', 'total_rent_display', 'created_at'
    )
    list_filter = ('unit_type',)
    search_fields = ('unit_type',)
    readonly_fields = ('price_sqft', 'created_at', 'updated_at')
    ordering = ('unit_type',)
    
    # No fieldsets: show all fields by default
    list_per_page = 5
    
    def total_sqft_display(self, obj):
        """Display total square footage for all units of this type."""
        return f"{obj.get_total_sqft():,} sqft"
    total_sqft_display.short_description = 'Total SqFt'
    
    def total_rent_display(self, obj):
        """Display total monthly rent for all units of this type."""
        return f"${obj.get_total_monthly_rent():,.2f}"
    total_rent_display.short_description = 'Total Monthly Rent'


@admin.register(RentRoll)
class RentRollAdmin(admin.ModelAdmin):
    """
    Admin configuration for RentRoll model.

    What: Manage per-tenant/unit rent roll records.
    Why: Allow full visibility and editing of rent roll details.
    How: Keep default form fields (no fieldsets/fields), expose helpful list columns.
    """
    list_display = (
        'id', 'asset_hub_id', 'tenant_name', 'unit_name', 'sq_feet',
        'rent', 'cam_month', 'lease_start_date', 'lease_end_date',
        'lease_term_months', 'lease_type', 'rent_increase_pct'
    )
    search_fields = ('tenant_name', 'unit_name')
    list_filter = ('lease_type',)
    ordering = ('asset_hub_id', 'tenant_name')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(ComparableProperty)
class ComparablePropertyAdmin(admin.ModelAdmin):
    """
    Admin configuration for ComparableProperty model.

    What: Parent model storing shared property characteristics for sales/lease comps.
    Why: Allow full visibility and editing of comparable property base data.
    How: Default form (all fields visible); list key property info (rating is on child models).
    """
    list_display = (
        'id', 'asset_hub', 'as_of_date', 'street_address', 'city', 'state',
        'property_type', 'beds', 'baths', 'units', 'livable_square_ft_building',
        'created_at'
    )
    search_fields = ('street_address', 'city', 'zip_code')
    list_filter = ('state', 'property_type', 'as_of_date')
    ordering = ('-as_of_date', 'street_address')
    readonly_fields = ('created_at', 'updated_at')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(SalesComparable)
class SalesComparableAdmin(admin.ModelAdmin):
    """
    Admin configuration for SalesComparable model.

    What: Sales-specific data extending ComparableProperty.
    Why: Allow editing of sale prices, dates, and listing info.
    How: Default form (all fields visible); list key sales metrics and comp rating.
    """
    list_display = (
        'id', 'comparable_property', 'last_sales_price', 'last_sales_date',
        'current_listed_price', 'current_listed_date', 'comp_rating', 'created_at'
    )
    search_fields = ('comparable_property__street_address', 'comparable_property__city')
    list_filter = ('last_sales_date', 'current_listed_date', 'comp_rating')
    ordering = ('-last_sales_date',)
    readonly_fields = ('created_at', 'updated_at')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(LeaseComparable)
class LeaseComparableAdmin(admin.ModelAdmin):
    """
    Admin configuration for LeaseComparable model.

    What: Lease-specific data extending ComparableProperty (property-level/SFR leases).
    Why: Allow editing of rent, lease terms, CAM, and property name.
    How: Default form (all fields visible); list key lease metrics and comp rating.
    """
    list_display = (
        'id', 'comparable_property', 'monthly_rent', 'lease_start_date',
        'lease_end_date', 'lease_term_months', 'lease_type', 'cam_monthly', 'comp_rating', 'created_at'
    )
    search_fields = ('comparable_property__street_address', 'comparable_property__city')
    list_filter = ('lease_type', 'lease_start_date', 'comp_rating')
    ordering = ('-lease_start_date',)
    readonly_fields = ('created_at', 'updated_at')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(LeaseComparableUnitMix)
class LeaseComparableUnitMixAdmin(admin.ModelAdmin):
    """
    Admin configuration for LeaseComparableUnitMix model.

    What: Aggregated unit mix data for lease comps (more common scenario).
    Why: Allow editing of unit type summaries (e.g., "20 1BR @ $1200/mo avg").
    How: Default form (all fields visible); list key metrics with auto-calculated price_sqft.
    """
    list_display = (
        'id', 'comparable_property', 'unit_type', 'unit_count', 'unit_avg_sqft',
        'unit_avg_rent', 'price_sqft', 'created_at'
    )
    search_fields = (
        'comparable_property__street_address',
        'comparable_property__city',
        'unit_type'
    )
    list_filter = ('unit_type',)
    ordering = ['comparable_property', 'unit_type']
    readonly_fields = ('price_sqft', 'created_at', 'updated_at')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(LeaseComparableRentRoll)
class LeaseComparableRentRollAdmin(admin.ModelAdmin):
    """
    Admin configuration for LeaseComparableRentRoll model.

    What: Unit-level rent roll data for lease comps (rare scenario).
    Why: Allow editing of per-unit rent, lease terms, and occupancy for multi-family comps.
    How: Default form (all fields visible); list key unit metrics.
    """
    list_display = (
        'id', 'comparable_property', 'unit_number', 'beds', 'baths', 'unit_sqft',
        'monthly_rent', 'lease_start_date', 'lease_end_date', 'is_occupied', 'created_at'
    )
    search_fields = (
        'comparable_property__street_address', 
        'comparable_property__city', 
        'unit_number',
        'tenant_name'
    )
    list_filter = ('is_occupied', 'lease_type', 'lease_start_date', 'beds')
    ordering = ['comparable_property', 'unit_number']
    readonly_fields = ('created_at', 'updated_at')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(HistoricalPropertyCashFlow)
class HistoricalPropertyCashFlowAdmin(admin.ModelAdmin):
    """
    Admin configuration for HistoricalPropertyCashFlow model.

    What: Historical property-level cash flows by year for owned/managed assets.
    Why: Allow editing of annual income and expense data for NOI analysis.
    How: Default form (all fields visible); list key metrics by asset and year.
    """
    list_display = (
        'id', 'asset_hub', 'year', 'gross_potential_rent_revenue', 'vacancy_loss',
        'property_management', 'property_taxes', 'created_at'
    )
    search_fields = ('asset_hub__id', 'year')
    list_filter = ('year',)
    ordering = ['asset_hub', '-year']
    readonly_fields = ('created_at', 'updated_at')
    # No fieldsets/fields/exclude: show all fields by default
    list_per_page = 5


@admin.register(LLTransactionSummary)
class LLTransactionSummaryAdmin(admin.ModelAdmin):
    """
    WHAT: Admin for LLTransactionSummary - realized P&L tracking
    WHY: Allow manual entry/editing of realized transaction data
    HOW: Organized fieldsets matching Performance Summary structure
    """
    list_display = (
        'asset_hub', 'get_asset_status', 'last_updated', 'has_income', 'has_expenses', 'has_proceeds'
    )
    search_fields = ('asset_hub__id', 'asset_hub__servicer_id')
    list_filter = ('asset_hub__details__trade', 'asset_hub__details__asset_status')
    readonly_fields = ('last_updated', 'created_at')
    list_per_page = 5
    
    # No fieldsets: show all fields by default
    
    def has_income(self, obj):
        """Check if any income fields have data"""
        return any([
            obj.income_principal_realized,
            obj.income_interest_realized,
            obj.income_rent_realized,
            obj.income_cam_realized,
            obj.income_mod_down_payment_realized,
        ])
    has_income.boolean = True
    has_income.short_description = 'Income?'
    
    def has_expenses(self, obj):
        """Check if any expense fields have data"""
        return any([
            obj.expense_servicing_realized,
            obj.expense_am_fees_realized,
            obj.legal_foreclosure_realized,
            obj.reo_hoa_realized,
        ])
    has_expenses.boolean = True
    has_expenses.short_description = 'Expenses?'
    
    def has_proceeds(self, obj):
        """Check if proceeds data exists"""
        return obj.gross_liquidation_proceeds_realized is not None
    has_proceeds.boolean = True
    has_proceeds.short_description = 'Proceeds?'

    def get_asset_status(self, obj):
        """Display lifecycle status from AssetDetails."""
        details = getattr(obj.asset_hub, 'details', None)
        return details.asset_status if details else '—'
    get_asset_status.short_description = 'Lifecycle Status'
    get_asset_status.admin_order_field = 'asset_hub__details__asset_status'


@admin.register(LLCashFlowSeries)
class LLCashFlowSeriesAdmin(admin.ModelAdmin):
    """
    WHAT: Admin for LLCashFlowSeries - period-by-period cash flow time series
    WHY: Allow viewing/editing of monthly cash flow data for analytics
    HOW: Organized by period with collapsible fieldsets for each category
    """
    list_display = (
        'asset_hub', 'period_number', 'period_date', 'net_cash_flow',
        'total_income', 'total_expenses', 'has_liquidation'
    )
    list_filter = ('period_number',)
    search_fields = ('asset_hub__id', 'asset_hub__servicer_id')
    readonly_fields = ('period_date', 'total_income', 'total_expenses', 'net_cash_flow', 'purchase_date')
    list_per_page = 5
    ordering = ('asset_hub', 'period_number')
    
    # No fieldsets: show all fields by default
    
    def has_liquidation(self, obj):
        """Check if this period has liquidation proceeds"""
        return obj.proceeds > 0 or obj.net_liquidation_proceeds > 0
    has_liquidation.boolean = True
    has_liquidation.short_description = 'Liquidation?'


# Module-level admin action so it reliably appears in the actions dropdown
@admin.action(description="Delete hub and all children")
def delete_hub_and_children(modeladmin, request, queryset):
    """For each selected hub, delete all child rows then the hub itself.

    Deletion order (to satisfy FK constraints):
    1) Photo, Document
    2) Valuation
    3) SellerRawData (acq)
    4) BlendedOutcomeModel, ServicerLoanData (AM)
    5) Hub
    """
    deleted_hubs = 0
    for hub in queryset:
        # Core attachments first (may reference valuation)
        Photo.objects.filter(asset_hub=hub).delete()
        Document.objects.filter(asset_hub=hub).delete()

        # Valuations (core)
        Valuation.objects.filter(asset_hub=hub).delete()

        # Acquisitions raw
        SellerRawData.objects.filter(asset_hub=hub).delete()

        # AM side
        BlendedOutcomeModel.objects.filter(asset_hub=hub).delete()
        ServicerLoanData.objects.filter(asset_hub=hub).delete()
        # SellerBoardedData.objects.filter(asset_hub=hub).delete()  # DEPRECATED - no longer used

        # Finally, delete the hub itself
        AssetIdHub.objects.filter(pk=hub.pk).delete()
        deleted_hubs += 1

    modeladmin.message_user(request, f"Deleted {deleted_hubs} hub(s) and all children.")
    
# Also register globally to ensure the action appears even if ModelAdmin.actions is overridden by theme/config
admin.site.add_action(delete_hub_and_children, name='delete_hub_and_children')


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    """
    Admin configuration for CalendarEvent model.
    
    Displays user-created calendar events with filtering and search capabilities.
    """
    list_display = (
        'id',
        'title',
        'date',
        'time',
        'category',
        'seller',
        'trade',
        'asset_hub',
        'is_reminder',
        'created_by',
        'created_at',
    )
    
    list_filter = (
        'category',
        'is_reminder',
        'date',
        'created_at',
    )
    
    search_fields = (
        'title',
        'description',
        'seller__seller_name',
        'trade__trade_name',
    )
    
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    date_hierarchy = 'date'
    
    list_per_page = 5
    
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'date', 'time', 'description', 'category', 'is_reminder')
        }),
        ('Relationships', {
            'fields': ('seller', 'trade', 'asset_hub'),
            'description': 'Optional links to business entities'
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Automatically set created_by to the current user if not already set.
        """
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AssetIdHub)
class AssetIdHubAdmin(admin.ModelAdmin):
    """Admin for the central Asset ID Hub."""
    list_display = (
        'id', 'sellertape_id', 'seller_tape_altid', 'servicer_id', 'trade_id_display', 'is_commercial_flag', 'servicer_refs',
        # PK columns showing actual IDs of related records
        'seller_raw_data_id', 'blended_outcome_model_id',  # seller_boarded_data_id removed (deprecated)
        'servicer_loan_data_id', 'valuation_id', 'photo_id', 'document_id',
        'created_at',
    )
    # Show more rows per page (default is 100). Also allow larger "Show all" limit.
    list_per_page = 5
    list_max_show_all = 2000
    search_fields = (
        'id',
        'servicer_id',
    )
    list_filter = ('acq_raw__trade', 'details__is_commercial', 'details__legacy_flag')
    actions_on_top = True
    actions_on_bottom = True
    actions = ['delete_selected', delete_hub_and_children]

    def get_queryset(self, request):
        """
        WHAT: Optimize queryset with select_related for related records
        WHY: Reduce database queries when displaying PKs of related records
        HOW: Use select_related for OneToOne/ForeignKey relationships
        """
        qs = super().get_queryset(request)
        return qs.select_related(
            'acq_raw',  # SellerRawData reverse relation
            # 'am_boarded',  # SellerBoardedData reverse relation - DEPRECATED
            'blended_outcome_model',  # BlendedOutcomeModel reverse relation
        )

    def servicer_refs(self, obj: AssetIdHub):  # type: ignore[name-defined]
        """Link to ServicerLoanData rows that share this hub's servicer_id.

        Allows quick navigation to all imported servicer rows tied to the same
        external servicer identifier.
        """
        sid = getattr(obj, 'servicer_id', None)
        if not sid:
            return '-'
        try:
            servicer_url = f"{reverse('admin:am_module_servicerloandata_changelist')}?servicer_id={quote(str(sid))}"
        except Exception:
            servicer_url = '#'

        count = ServicerLoanData.objects.filter(servicer_id=sid).count()
        return format_html('<a href="{}">Servicer Rows ({})</a>', servicer_url, count)
    servicer_refs.short_description = 'Servicer Data'

    def seller_tape_altid(self, obj: AssetIdHub):  # type: ignore[name-defined]
        srd = getattr(obj, 'acq_raw', None)
        return getattr(srd, 'sellertape_altid', None) or '—'

    seller_tape_altid.short_description = 'Alt ID'
    seller_tape_altid.admin_order_field = 'acq_raw__sellertape_altid'

    def trade_id_display(self, obj: AssetIdHub):  # type: ignore[name-defined]
        srd = getattr(obj, 'acq_raw', None)
        if srd and srd.trade_id:
            return srd.trade_id
        details = getattr(obj, 'details', None)
        if details and details.trade_id:
            return details.trade_id
        return '—'

    trade_id_display.short_description = 'Trade ID'
    trade_id_display.admin_order_field = 'acq_raw__trade_id'

    # Override the built-in delete_selected to delete the hub bundle in the correct order
    @admin.action(description="Delete selected Asset ID Hub (bundle)")
    def delete_selected(self, request, queryset):
        return delete_hub_and_children(self, request, queryset)
    
    # WHAT: Display methods showing PKs of related records
    # WHY: Show actual IDs instead of checkmarks for reference table
    # HOW: Access reverse OneToOne relationships and return PK or dash
    
    def seller_raw_data_id(self, obj: AssetIdHub):
        """Display SellerRawData PK if exists"""
        return obj.acq_raw.pk if hasattr(obj, 'acq_raw') else '—'
    seller_raw_data_id.short_description = 'SellerRawData'

    # def seller_boarded_data_id(self, obj: AssetIdHub):
    #     """DEPRECATED - SellerBoardedData no longer used"""
    #     return obj.am_boarded.pk if hasattr(obj, 'am_boarded') else '—'
    # seller_boarded_data_id.short_description = 'SellerBoardedData'

    def blended_outcome_model_id(self, obj: AssetIdHub):
        """Display BlendedOutcomeModel PK if exists (PK = asset_hub_id)"""
        return obj.blended_outcome_model.pk if hasattr(obj, 'blended_outcome_model') else '—'
    blended_outcome_model_id.short_description = 'BlendedOutcomeModel'
    
    def servicer_loan_data_id(self, obj: AssetIdHub):
        """Display first ServicerLoanData PK if exists (may be multiple)"""
        servicer_data = ServicerLoanData.objects.filter(asset_hub=obj).first()
        return servicer_data.id if servicer_data else '—'
    servicer_loan_data_id.short_description = 'ServicerLoanData'
    
    def valuation_id(self, obj: AssetIdHub):
        """Display first Valuation PK if exists (may be multiple)"""
        valuation = Valuation.objects.filter(asset_hub=obj).first()
        return valuation.id if valuation else '—'
    valuation_id.short_description = 'Valuation'
    
    def photo_id(self, obj: AssetIdHub):
        """Display count of photos"""
        count = Photo.objects.filter(asset_hub=obj).count()
        return f'{count} photos' if count > 0 else '—'
    photo_id.short_description = 'Photos'
    
    def document_id(self, obj: AssetIdHub):
        """Display count of documents"""
        count = Document.objects.filter(asset_hub=obj).count()
        return f'{count} docs' if count > 0 else '—'
    document_id.short_description = 'Documents'


# ------------------------------
# General Ledger Admin
# ------------------------------

@admin.register(GeneralLedgerEntries)
class GeneralLedgerEntriesAdmin(admin.ModelAdmin):
    """
    WHAT: Admin configuration for General Ledger Entries
    WHY: Enable admin users to view, search, and manage GL entries
    HOW: List display with key fields, filters, and search capabilities
    """
    list_display = (
        'entry',
        'posting_date',
        'company_name',
        'loan_number',
        'asset_hub_link',
        'account_number',
        'account_name',
        'debit_amount',
        'credit_amount',
        'net_amount_display',
        'tag',
        'bucket',
        'requires_review_display',
        'created_by',
        'created_at',
    )
    
    list_filter = (
        'posting_date',
        'tag',
        'bucket',
        'requires_review',
        'created_at',
    )
    
    search_fields = (
        'entry',
        'loan_number',
        'company_name',
        'borrower_name',
        'account_number',
        'account_name',
        'description',
        'document_number',
    )
    
    readonly_fields = (
        'net_amount',
        'is_balanced',
        'created_by',
        'updated_by',
        'created_at',
        'updated_at',
    )
    
    autocomplete_fields = ['asset_hub']
    
    date_hierarchy = 'posting_date'
    
    list_per_page = 50
    
    fieldsets = (
        ('Entry Identification', {
            'fields': ('entry', 'document_number', 'external_document_number', 'document_type')
        }),
        ('Company and Loan Information', {
            'fields': ('company_name', 'loan_number', 'asset_hub', 'borrower_name', 'loan_type')
        }),
        ('Date Information', {
            'fields': ('posting_date', 'entry_date', 'date_funded')
        }),
        ('Amounts', {
            'fields': ('debit_amount', 'credit_amount', 'amount', 'net_amount', 'is_balanced')
        }),
        ('Account Information', {
            'fields': ('account_number', 'account_name')
        }),
        ('Description and Comments', {
            'fields': ('description', 'reason_code', 'comment')
        }),
        ('Cost Center', {
            'fields': ('cost_center', 'cost_center_name')
        }),
        ('Classification', {
            'fields': ('tag', 'bucket')
        }),
        ('Review and AI', {
            'fields': ('requires_review', 'review_notes', 'ai_notes')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['flag_for_review', 'clear_review_flag', 'export_to_csv']
    
    def asset_hub_link(self, obj):
        """WHAT: Display clickable link to asset hub"""
        if obj.asset_hub:
            url = reverse('admin:core_assetidhub_change', args=[obj.asset_hub.id])
            return format_html('<a href="{}">{}</a>', url, obj.asset_hub.id)
        return '—'
    asset_hub_link.short_description = 'Asset Hub'
    
    def net_amount_display(self, obj):
        """WHAT: Display net amount with color coding"""
        net = obj.net_amount
        if net > 0:
            color = 'green'
        elif net < 0:
            color = 'red'
        else:
            color = 'gray'
        return format_html('<span style="color: {};">${:,.2f}</span>', color, net)
    net_amount_display.short_description = 'Net Amount'
    net_amount_display.admin_order_field = 'debit_amount'  # Allow sorting
    
    def requires_review_display(self, obj):
        """WHAT: Display review status with icon"""
        if obj.requires_review:
            return format_html('<span style="color: orange;">⚠ Review</span>')
        return format_html('<span style="color: green;">✓ OK</span>')
    requires_review_display.short_description = 'Status'
    requires_review_display.admin_order_field = 'requires_review'
    
    def flag_for_review(self, request, queryset):
        """WHAT: Admin action to flag selected entries for review"""
        count = queryset.update(requires_review=True)
        self.message_user(request, f'{count} entries flagged for review.')
    flag_for_review.short_description = 'Flag selected entries for review'
    
    def clear_review_flag(self, request, queryset):
        """WHAT: Admin action to clear review flag from selected entries"""
        count = queryset.update(requires_review=False, review_notes='')
        self.message_user(request, f'{count} entries marked as reviewed.')
    clear_review_flag.short_description = 'Clear review flag from selected entries'
    
    def export_to_csv(self, request, queryset):
        """WHAT: Admin action to export selected entries to CSV (placeholder)"""
        self.message_user(request, f'CSV export coming soon! ({queryset.count()} entries selected)')
    export_to_csv.short_description = 'Export selected entries to CSV'


@admin.register(ChartOfAccounts)
class ChartOfAccountsAdmin(admin.ModelAdmin):
    """
    WHAT: Admin configuration for Chart of Accounts
    WHY: Enable admin users to manage GL account definitions
    HOW: Simple list display with search and ordering
    """
    list_display = (
        'account_number',
        'account_name',
        'account_type',
        'transaction_table_reference',
    )
    
    search_fields = (
        'account_number',
        'account_name',
        'account_type',
    )
    
    list_filter = ('account_type',)
    
    ordering = ('account_number',)
