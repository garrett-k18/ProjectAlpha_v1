from django.contrib import admin
from django.utils.html import format_html

# All valuation models moved to core
from .models.model_acq_seller import (
    Seller,
    Trade,
    AcqAsset,
    AcqLoan,
    AcqProperty,
    AcqForeclosureTimeline,
    AcqBankruptcy,
    AcqModification,
)
from .models.model_acq_assumptions import LoanLevelAssumption, TradeLevelAssumption, StaticModelAssumptions, NoteSaleAssumption  # StaticModelAssumptions is DEPRECATED
"""
NOTE: Valuation models have been unified.

Deprecated:
- core.models.valuations.InternalValuation
- core.models.valuations.BrokerValues

Use:
- core.models.valuations.Valuation

Admin registrations for Valuation, Photo, and Document now live in core.admin to
avoid duplicate registrations across apps.
"""
from core.models.attachments import Document

# Helper to build list_display with all concrete fields
def all_concrete_field_names(model):
    """Return names of all concrete, non-relation-reverse fields for list_display.
    Includes ForeignKey raw ID fields (e.g., seller_id) automatically via model._meta.
    Excludes many-to-many and reverse relations which are not valid list_display entries.
    """
    names = []
    for f in model._meta.get_fields():
        # Exclude reverse relations and M2M
        if f.auto_created and not f.concrete:
            continue
        if f.many_to_many:
            continue
        if f.concrete:
            names.append(f.name)
    return tuple(names)

# Inline admin classes for related models
class TradeInline(admin.TabularInline):
    """Inline admin for Trade model to display in Seller admin"""
    model = Trade
    extra = 0

class AcqAssetInline(admin.TabularInline):
    """Inline admin for AcqAsset model to display in Trade admin"""
    model = AcqAsset
    extra = 0
    # Do not specify `fields` so Django renders all editable fields by default.
    show_change_link = True
    
## Removed PhotoInline: Photo is hub-first and no longer has FK to SellerRawData


    fk_name = 'seller_raw_data'
    fields = (
        'geocode_lat', 'geocode_lng', 'geocode_used_address',
        'geocode_full_address', 'geocode_display_address',
        'geocode_county', 'geocode_msa_code', 'geocode_msa', 'geocoded_at',
        'created_at', 'updated_at',
    )
    readonly_fields = ('created_at', 'updated_at')


## Photo admin is registered in core.admin; do not register here to avoid duplicates.

# Main admin classes
@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    """Admin configuration for Seller model"""
    # Show all concrete fields including primary key id
    list_display = all_concrete_field_names(Seller)
    search_fields = ('name', 'broker', 'email')
    list_per_page = 5
    inlines = []

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    """Admin configuration for Trade model"""
    # Show all concrete fields including id and FK raw ids (seller_id)
    list_display = all_concrete_field_names(Trade)
    list_filter = ('seller',)
    search_fields = ('trade_name', 'seller__name')
    autocomplete_fields = ['seller']
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_select_related = ('seller',)
    list_per_page = 5
    inlines = []

@admin.register(AcqAsset)
class AcqAssetAdmin(admin.ModelAdmin):
    """Admin configuration for AcqAsset model"""
    list_display = all_concrete_field_names(AcqAsset)
    list_select_related = ('seller', 'trade')
    list_filter = ('asset_status', 'acq_status', 'asset_class', 'seller', 'trade')
    search_fields = (
        'asset_hub__sellertape_id',
        'seller__name',
        'trade__trade_name',
    )
    readonly_fields = ('asset_hub', 'created_at', 'updated_at')
    list_per_page = 5


@admin.register(AcqLoan)
class AcqLoanAdmin(admin.ModelAdmin):
    """Admin configuration for AcqLoan model"""
    list_display = all_concrete_field_names(AcqLoan)
    list_select_related = ('asset',)
    list_filter = ('product_type',)
    search_fields = ('sellertape_id', 'sellertape_altid', 'borrower1_last', 'borrower1_first')
    readonly_fields = ('asset', 'created_at', 'updated_at')
    list_per_page = 5


@admin.register(AcqProperty)
class AcqPropertyAdmin(admin.ModelAdmin):
    """Admin configuration for AcqProperty model"""
    list_display = all_concrete_field_names(AcqProperty)
    list_select_related = ('asset',)
    list_filter = ('state', 'occupancy')
    search_fields = ('street_address', 'city', 'state', 'zip')
    readonly_fields = ('asset', 'created_at', 'updated_at')
    list_per_page = 5


@admin.register(AcqForeclosureTimeline)
class AcqForeclosureTimelineAdmin(admin.ModelAdmin):
    """Admin configuration for AcqForeclosureTimeline model"""
    list_display = all_concrete_field_names(AcqForeclosureTimeline)
    list_select_related = ('asset',)
    list_filter = ('fc_flag',)
    readonly_fields = ('asset', 'created_at', 'updated_at')
    list_per_page = 5


@admin.register(AcqBankruptcy)
class AcqBankruptcyAdmin(admin.ModelAdmin):
    """Admin configuration for AcqBankruptcy model"""
    list_display = all_concrete_field_names(AcqBankruptcy)
    list_select_related = ('loan',)
    list_filter = ('bk_flag',)
    readonly_fields = ('loan', 'created_at', 'updated_at')
    list_per_page = 5


@admin.register(AcqModification)
class AcqModificationAdmin(admin.ModelAdmin):
    """Admin configuration for AcqModification model"""
    list_display = all_concrete_field_names(AcqModification)
    list_select_related = ('loan',)
    list_filter = ('mod_flag',)
    readonly_fields = ('loan', 'created_at', 'updated_at')
    list_per_page = 5

## Servicer and StateReference have been moved to core.models.model_co_assumptions and are registered in core.admin

@admin.register(LoanLevelAssumption)
class LoanLevelAssumptionAdmin(admin.ModelAdmin):
    """Admin configuration for LoanLevelAssumption model"""
    list_display = ('asset_hub', 'acquisition_price', 'months_to_resolution', 'probability_of_cure', 'probability_of_foreclosure', 'fc_duration_override_months')
    list_filter = ('asset_hub__acq_asset__seller', 'asset_hub__acq_asset__trade')
    list_per_page = 5

# ============================================================================
# DEPRECATED - StaticModelAssumptions - TO BE REMOVED IN FUTURE MIGRATION
# Use TradeLevelAssumption with default values instead
# ============================================================================
@admin.register(StaticModelAssumptions)
class StaticModelAssumptionsAdmin(admin.ModelAdmin):
    """DEPRECATED: Admin for StaticModelAssumptions - TO BE REMOVED.
    
    ⚠️ DEPRECATION NOTICE ⚠️
    This admin is DEPRECATED and will be removed in a future update.
    
    DO NOT USE for new trades!
    Use TradeLevelAssumption instead - it has default values for all fields.
    
    This admin remains temporarily for:
    - Viewing legacy data
    - Reference during migration period
    - Will be unregistered once all trades use TradeLevelAssumption
    """
    
    # Hide "Add" button since only one record can exist
    def has_add_permission(self, request):
        """Prevent adding new records - only one singleton record allowed"""
        return False
    
    # Prevent deletion
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of the singleton settings record"""
        return False
    
    list_display = (
        'version_name', 'perf_rpl_hold_period', 'mod_rate', 'mod_legal_term', 
        'mod_amort_term', 'max_mod_ltv', 'mod_io_flag', 'am_fee_pct', 'updated_at'
    )
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_per_page = 5
    
    # No fieldsets: show all fields by default
    
    def changelist_view(self, request, extra_context=None):
        """Override to redirect to the single record's change page"""
        # Load or create the singleton instance
        obj = StaticModelAssumptions.load()
        from django.shortcuts import redirect
        from django.urls import reverse
        # Redirect to the change page for the singleton record
        return redirect(reverse('admin:acq_module_staticmodelassumptions_change', args=[obj.id]))


@admin.register(TradeLevelAssumption)
class TradeLevelAssumptionAdmin(admin.ModelAdmin):
    """Admin configuration for TradeLevelAssumption model.
    
    What this does:
    - Manages trade-specific assumptions with defaults
    - Each trade has its own complete set of assumptions
    - Default values can be overridden per trade
    """
    list_display = (
        'trade', 'bid_date', 'settlement_date', 'target_irr',
        'pctUPB', 'discount_rate', 'perf_rpl_hold_period'
    )
    list_filter = ('trade__seller',)
    search_fields = ('trade__trade_name', 'trade__seller__name')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['trade', 'servicer']
    list_per_page = 5
    
    # No fieldsets: show all fields by default


@admin.register(NoteSaleAssumption)
class NoteSaleAssumptionAdmin(admin.ModelAdmin):
    """Admin configuration for NoteSaleAssumption model.
    
    What this does:
    - Manages individual discount factors for note sale calculations
    - Each record represents one discount factor with factor type dropdown
    - Simple, flexible structure allows unlimited factor combinations
    """
    list_display = (
        'factor_name', 'factor_type', 'index_order', 'discount_factor',
        'range_display', 'priority', 'is_active'
    )
    list_filter = ('factor_type', 'is_active', 'index_order', 'priority')
    search_fields = ('factor_name', 'notes', 'range_value')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 15
    
    # Group fields logically in the form
    fieldsets = (
        ('Basic Information', {
            'fields': ('factor_name', 'factor_type', 'index_order', 'discount_factor', 'priority', 'is_active')
        }),
        ('Range Definition', {
            'fields': ('range_min', 'range_max', 'range_value'),
            'description': 'Define range using min/max for numeric values OR exact value for strings (e.g., property types)'
        }),
        ('Notes & Timestamps', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def range_display(self, obj):
        """Display the range in a readable format"""
        if obj.range_value:
            return f"= {obj.range_value}"
        elif obj.range_min is not None and obj.range_max is not None:
            return f"{obj.range_min} - {obj.range_max}"
        elif obj.range_min is not None:
            return f">= {obj.range_min}"
        elif obj.range_max is not None:
            return f"<= {obj.range_max}"
        else:
            return "All values"
    range_display.short_description = "Range"
    
    def get_queryset(self, request):
        """Order by index order, factor type, then priority"""
        return super().get_queryset(request).order_by('index_order', 'factor_type', '-priority')


## InternalValuation and BrokerValues admin removed (deprecated). Use core.admin Valuation.




# =============================================================================
# UTILITY AND PROPERTY MANAGEMENT ASSUMPTION ADMINS MOVED TO CORE
# =============================================================================
# PropertyTypeAssumption, SquareFootageAssumption, and UnitBasedAssumption 
# admin classes have been moved to core.admin since the models are now in core
