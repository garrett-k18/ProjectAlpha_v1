from django.contrib import admin
from django.utils.html import format_html

# All valuation models moved to core
from .models.seller import Seller, Trade, SellerRawData
from .models.assumptions import LoanLevelAssumption, TradeLevelAssumption, StaticModelAssumptions  # StaticModelAssumptions is DEPRECATED
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
from core.models.enrichment import LlDataEnrichment

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

class SellerRawDataInline(admin.TabularInline):
    """Inline admin for SellerRawData model to display in Trade admin"""
    model = SellerRawData
    extra = 0
    # Do not specify `fields` so Django renders all editable fields by default.
    show_change_link = True
    
## Removed PhotoInline: Photo is hub-first and no longer has FK to SellerRawData


class LlDataEnrichmentInline(admin.StackedInline):
    """Inline admin to view/edit one-to-one enrichment on SellerRawData."""
    model = LlDataEnrichment
    extra = 0
    can_delete = True
    fk_name = 'seller_raw_data'
    fields = (
        'geocode_lat', 'geocode_lng', 'geocode_used_address',
        'geocode_full_address', 'geocode_display_address',
        'geocode_county', 'geocode_msa', 'geocoded_at',
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

@admin.register(SellerRawData)
class SellerRawDataAdmin(admin.ModelAdmin):
    """Admin configuration for SellerRawData model"""
    # Show all concrete fields (this is a wide list view)
    list_display = all_concrete_field_names(SellerRawData)
    # Optimize FK lookups for list view performance
    list_select_related = ('seller', 'trade')
    list_filter = ('asset_status', 'state', 'seller', 'trade', 'property_type', 'product_type', 'occupancy')
    search_fields = (
        'street_address', 'city', 'state', 'zip',
        'sellertape_id', 'sellertape_altid',
        'borrower1_last', 'borrower1_first', 'borrower2_last', 'borrower2_first'
    )
    # Expose read-only identifiers and audit fields on the form
    readonly_fields = ('asset_hub', 'created_at', 'updated_at')
    # Use Django's default add/change form, which renders ALL model fields by default.
    list_per_page = 5

## Servicer and StateReference have been moved to core.models.assumptions and are registered in core.admin

@admin.register(LoanLevelAssumption)
class LoanLevelAssumptionAdmin(admin.ModelAdmin):
    """Admin configuration for LoanLevelAssumption model"""
    list_display = ('seller_raw_data', 'months_to_resolution', 'probability_of_cure', 'probability_of_foreclosure')
    list_filter = ('seller_raw_data__seller', 'seller_raw_data__trade')
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

## InternalValuation and BrokerValues admin removed (deprecated). Use core.admin Valuation.


@admin.register(LlDataEnrichment)
class LlDataEnrichmentAdmin(admin.ModelAdmin):
    """Admin for loan-level enrichment records."""
    list_display = (
        'seller_raw_data', 'geocode_lat', 'geocode_lng', 'geocoded_at',
    )
    search_fields = (
        'seller_raw_data__seller__name',
        'seller_raw_data__trade__trade_name',
        'geocode_full_address', 'geocode_used_address', 'geocode_display_address',
    )
    list_filter = (
        'seller_raw_data__seller', 'seller_raw_data__trade',
    )
    list_per_page = 5
