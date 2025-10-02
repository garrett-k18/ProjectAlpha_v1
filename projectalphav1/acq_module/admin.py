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

# Inline admin classes for related models
class TradeInline(admin.TabularInline):
    """Inline admin for Trade model to display in Seller admin"""
    model = Trade
    extra = 0

class SellerRawDataInline(admin.TabularInline):
    """Inline admin for SellerRawData model to display in Trade admin"""
    model = SellerRawData
    extra = 0
    fields = ('asset_status', 'as_of_date', 'state', 'current_balance', 'months_dlq')
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
    list_display = ('name', 'broker', 'email', 'poc')
    search_fields = ('name', 'broker', 'email')
    inlines = [TradeInline]

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    """Admin configuration for Trade model"""
    list_display = ('trade_name', 'seller')
    list_filter = ('seller',)
    search_fields = ('trade_name', 'seller__name')
    autocomplete_fields = ['seller']
    inlines = [SellerRawDataInline]

@admin.register(SellerRawData)
class SellerRawDataAdmin(admin.ModelAdmin):
    """Admin configuration for SellerRawData model"""
    # Include the Asset Hub ID for quick reference (asset_hub is now the PK)
    list_display = ('asset_hub', 'seller', 'trade', 'asset_status', 'state', 'current_balance', 'months_dlq')
    # Optimize FK lookups for list view performance
    list_select_related = ('seller', 'trade')
    list_filter = ('asset_status', 'state', 'seller', 'trade')
    search_fields = ('street_address', 'city', 'state', 'zip')
    fieldsets = (
        ('Identification', {
            'fields': ('seller', 'trade', 'sellertape_id', 'asset_status', 'as_of_date')
        }),
        ('Property Information', {
            'fields': ('street_address', 'city', 'state', 'zip')
        }),
        ('Loan Details', {
            'fields': ('current_balance', 'deferred_balance', 'interest_rate', 'next_due_date', 'last_paid_date')
        }),
        ('Origination Information', {
            'fields': ('first_pay_date', 'origination_date', 'original_balance', 'original_term', 'original_rate', 'original_maturity_date')
        }),
        ('Current Loan Status', {
            'fields': ('default_rate', 'months_dlq', 'current_maturity_date', 'current_term')
        }),
        ('Financial Details', {
            'fields': ('accrued_note_interest', 'accrued_default_interest', 'escrow_balance', 'escrow_advance', 
                     'recoverable_corp_advance', 'late_fees', 'other_fees', 'suspense_balance', 'total_debt')
        }),
        ('Valuation Information', {
            'fields': ('origination_value', 'origination_arv', 'origination_value_date',
                     'seller_asis_value', 'seller_arv_value', 'seller_value_date',
                     'additional_asis_value', 'additional_arv_value', 'additional_value_date')
        }),
        ('Foreclosure Information', {
            'fields': ('fc_flag', 'fc_first_legal_date', 'fc_referred_date', 'fc_judgement_date',
                     'fc_scheduled_sale_date', 'fc_sale_date', 'fc_starting')
        }),
        ('Bankruptcy Information', {
            'fields': ('bk_flag', 'bk_chapter')
        }),
        ('Modification Information', {
            'fields': ('mod_flag', 'mod_date', 'mod_maturity_date', 'mod_term', 'mod_rate', 'mod_initial_balance')
        }),
    )
    # Show enrichment inline
    inlines = [LlDataEnrichmentInline]

## Servicer and StateReference have been moved to core.models.assumptions and are registered in core.admin

@admin.register(LoanLevelAssumption)
class LoanLevelAssumptionAdmin(admin.ModelAdmin):
    """Admin configuration for LoanLevelAssumption model"""
    list_display = ('seller_raw_data', 'months_to_resolution', 'probability_of_cure', 'probability_of_foreclosure')
    list_filter = ('seller_raw_data__seller', 'seller_raw_data__trade')

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
    
    fieldsets = (
        ('Version Info', {
            'fields': ('id', 'version_name'),
            'description': 'This is a singleton settings record. Only one record exists. Edit values below to change global defaults.'
        }),
        ('Performance/RPL Defaults', {
            'fields': ('perf_rpl_hold_period',),
            'description': 'Default assumptions for performing/re-performing loans'
        }),
        ('Modification Defaults', {
            'fields': ('mod_rate', 'mod_legal_term', 'mod_amort_term', 'max_mod_ltv', 'mod_io_flag', 
                      'mod_down_pmt', 'mod_orig_cost', 'mod_setup', 'mod_hold'),
            'description': 'Default modification parameters used across all trades'
        }),
        ('Acquisition Cost Defaults', {
            'fields': ('acq_legal_cost', 'acq_dd_cost', 'acq_tax_title_cost'),
            'description': 'Default acquisition cost percentages'
        }),
        ('Asset Management Fees', {
            'fields': ('am_fee_pct',),
            'description': 'Default AM fee percentage'
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
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
    autocomplete_fields = ['trade']
    
    fieldsets = (
        ('Trade Link', {
            'fields': ('trade',),
            'description': 'Link to trade'
        }),
        ('Trade Dates', {
            'fields': ('bid_date', 'settlement_date', 'servicing_transfer_date')
        }),
        ('Financial Assumptions', {
            'fields': ('pctUPB', 'target_irr', 'discount_rate'),
            'description': 'Trade-specific financial parameters'
        }),
        ('Performance/RPL Assumptions', {
            'fields': ('perf_rpl_hold_period',),
            'description': 'Performing/re-performing loan assumptions'
        }),
        ('Modification Assumptions', {
            'fields': ('mod_rate', 'mod_legal_term', 'mod_amort_term', 'max_mod_ltv', 'mod_io_flag',
                      'mod_down_pmt', 'mod_orig_cost', 'mod_setup', 'mod_hold'),
            'description': 'Modification parameters (defaults can be overridden)',
            'classes': ('collapse',)
        }),
        ('Acquisition Costs', {
            'fields': ('acq_legal_cost', 'acq_dd_cost', 'acq_tax_title_cost'),
            'description': 'Acquisition cost percentages',
            'classes': ('collapse',)
        }),
        ('Asset Management', {
            'fields': ('am_fee_pct',),
            'description': 'AM fee percentage',
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

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
