from django.contrib import admin
from django.db.models import Exists, OuterRef
from django.urls import reverse
from django.utils.html import format_html
from urllib.parse import quote
from .models.capital import DebtFacility
from .models.crm import MasterCRM
from .models.assumptions import Servicer, StateReference, FCStatus, FCTimelines, CommercialUnits
from .models.asset_id_hub import AssetIdHub
from .models.valuations import Valuation
from .models.attachments import Photo, Document
from .models.transactions import LLTransactionSummary, LLCashFlowSeries
from .models.commercial import UnitMix, RentRoll
from .models.valuations import ComparableProperty, SalesComparable, LeaseComparable, LeaseComparableUnitMix, LeaseComparableRentRoll, HistoricalPropertyCashFlow

# Cross-app children that reference AssetIdHub
from acq_module.models.seller import SellerRawData
from am_module.models.boarded_data import SellerBoardedData, BlendedOutcomeModel
from am_module.models.servicers import ServicerLoanData

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

@admin.register(MasterCRM)
class MasterCRMAdmin(admin.ModelAdmin):
    """Admin configuration for unified Master CRM (Brokercrm) model."""
    list_display = (
        'contact_name', 'firm', 'email', 'state', 'city', 'tag',
        'alt_contact_name', 'nda_flag', 'nda_signed', 'created_at'
    )
    list_filter = (
        'state', 'tag', 'nda_flag'
    )
    search_fields = (
        'contact_name', 'email', 'firm', 'city',
        'alt_contact_name', 'alt_contact_email'
    )
    readonly_fields = ('created_at', 'updated_at')
    # No fieldsets: show all fields by default





@admin.register(Servicer)
class ServicerAdmin(admin.ModelAdmin):
    """Admin configuration for Servicer model."""
    list_display = (
        'servicer_name', 'contact_name', 'contact_email', 'contact_phone',
        'board_fee', 'current_fee', 'fc_fee', 'bk_fee', 'mod_fee', 'dil_fee',
    )
    search_fields = ('servicer_name', 'contact_name', 'contact_email')
    list_filter = ()


@admin.register(Valuation)
class ValuationAdmin(admin.ModelAdmin):
    """Admin for the unified Valuation model."""
    list_display = (
        'id', 'asset_hub', 'source', 'asis_value', 'arv_value', 'value_date', 'created_at'
    )
    list_filter = (
        'source', 'value_date'
    )
    search_fields = (
        'asset_hub__id', 'notes'
    )
    # No fieldsets: show all fields by default
    readonly_fields = ('created_at', 'updated_at')


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


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin for the Document model."""
    list_display = (
        'id', 'asset_hub', 'valuation', 'original_name', 'uploaded_at'
    )
    search_fields = (
        'asset_hub__id', 'original_name'
    )


@admin.register(StateReference)
class StateReferenceAdmin(admin.ModelAdmin):
    """Admin configuration for StateReference model."""
    list_display = (
        'state_code', 'state_name', 'judicialvsnonjudicial', 'fc_state_months'
    )
    search_fields = ('state_code', 'state_name')
    list_filter = ('judicialvsnonjudicial',)


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


@admin.register(HistoricalPropertyCashFlow)
class HistoricalPropertyCashFlowAdmin(admin.ModelAdmin):
    """
    Admin configuration for HistoricalPropertyCashFlow model.

    What: Historical property-level cash flows by year for owned/managed assets.
    Why: Allow editing of annual income and expense data for NOI analysis.
    How: Default form (all fields visible); list key metrics by asset and year.
    """
    list_display = (
        'id', 'asset_hub', 'year', 'gross_rent_revenue', 'vacancy_loss',
        'property_management', 'property_taxes', 'created_at'
    )
    search_fields = ('asset_hub__id', 'year')
    list_filter = ('year',)
    ordering = ['asset_hub', '-year']
    readonly_fields = ('created_at', 'updated_at')
    # No fieldsets/fields/exclude: show all fields by default


@admin.register(LLTransactionSummary)
class LLTransactionSummaryAdmin(admin.ModelAdmin):
    """
    WHAT: Admin for LLTransactionSummary - realized P&L tracking
    WHY: Allow manual entry/editing of realized transaction data
    HOW: Organized fieldsets matching Performance Summary structure
    """
    list_display = (
        'asset_hub', 'last_updated', 'has_income', 'has_expenses', 'has_proceeds'
    )
    search_fields = ('asset_hub__id', 'asset_hub__servicer_id')
    readonly_fields = ('last_updated', 'created_at')
    list_per_page = 100
    
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
        return obj.proceeds_realized is not None
    has_proceeds.boolean = True
    has_proceeds.short_description = 'Proceeds?'


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
    list_per_page = 100
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
    4) BlendedOutcomeModel, ServicerLoanData, SellerBoardedData (AM)
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
        SellerBoardedData.objects.filter(asset_hub=hub).delete()

        # Finally, delete the hub itself
        AssetIdHub.objects.filter(pk=hub.pk).delete()
        deleted_hubs += 1

    modeladmin.message_user(request, f"Deleted {deleted_hubs} hub(s) and all children.")
    
# Also register globally to ensure the action appears even if ModelAdmin.actions is overridden by theme/config
admin.site.add_action(delete_hub_and_children, name='delete_hub_and_children')


@admin.register(AssetIdHub)
class AssetIdHubAdmin(admin.ModelAdmin):
    """Admin for the central Asset ID Hub."""
    list_display = (
        'id', 'servicer_id', 'is_commercial', 'servicer_refs',
        # PK columns showing actual IDs of related records
        'seller_raw_data_id', 'seller_boarded_data_id', 'blended_outcome_model_id', 
        'servicer_loan_data_id', 'valuation_id', 'photo_id', 'document_id',
        'created_at',
    )
    # Show more rows per page (default is 100). Also allow larger "Show all" limit.
    list_per_page = 500
    list_max_show_all = 2000
    search_fields = (
        'servicer_id',
    )
    list_filter = ('is_commercial',)
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
            'am_boarded',  # SellerBoardedData reverse relation
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
    
    def seller_boarded_data_id(self, obj: AssetIdHub):
        """Display SellerBoardedData PK if exists"""
        return obj.am_boarded.pk if hasattr(obj, 'am_boarded') else '—'
    seller_boarded_data_id.short_description = 'SellerBoardedData'
    
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
