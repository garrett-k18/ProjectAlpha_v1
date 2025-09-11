from django.contrib import admin
from django.utils.html import format_html

# Import all models from the models directory
from .models import (
    Seller, Trade, SellerRawData,
    Servicer, StateReference, LoanLevelAssumption, TradeLevelAssumption,
    InternalValuation, BrokerValues, Photo,
    Brokercrm, LlDataEnrichment,
)

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
    
class PhotoInline(admin.TabularInline):
    """Inline admin for unified Photo model to display in SellerRawData admin."""
    model = Photo
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        """Display a thumbnail preview of the image (if present)."""
        if getattr(obj, 'image', None):
            return format_html('<img src="{}" width="150" height="150" />', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Preview'


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

@admin.register(Brokercrm)
class BrokercrmAdmin(admin.ModelAdmin):
    """Admin configuration for Brokercrm (broker directory) model."""
    list_display = (
        'broker_name', 'broker_firm', 'broker_email', 'broker_state', 'broker_city', 'created_at'
    )
    list_filter = (
        'broker_state',
    )
    search_fields = (
        'broker_name', 'broker_email', 'broker_firm', 'broker_city'
    )


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    """Admin configuration for unified Photo model."""
    list_display = (
        'seller_raw_data', 'source_tag', 'is_primary', 'image', 'created_at',
    )
    list_filter = (
        'source_tag',
        'seller_raw_data__seller',
        'seller_raw_data__trade',
    )
    search_fields = (
        'seller_raw_data__seller__name',
        'seller_raw_data__trade__trade_name',
        'caption',
        'source_url',
        'source_document_name',
        'source_tool',
    )


    # No additional inline classes; use PhotoInline in SellerRawData admin instead.

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
    inlines = [SellerRawDataInline]

@admin.register(SellerRawData)
class SellerRawDataAdmin(admin.ModelAdmin):
    """Admin configuration for SellerRawData model"""
    list_display = ('id', 'seller', 'trade', 'asset_status', 'state', 'current_balance', 'months_dlq')
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
    # Show photos and enrichment inline
    inlines = [PhotoInline, LlDataEnrichmentInline]

@admin.register(Servicer)
class ServicerAdmin(admin.ModelAdmin):
    """Admin configuration for Servicer model"""
    list_display = ('servicer_name', 'contact_name', 'contact_email', 'contact_phone')
    search_fields = ('servicer_name', 'contact_name', 'contact_email')

@admin.register(StateReference)
class StateReferenceAdmin(admin.ModelAdmin):
    """Admin configuration for StateReference model"""
    list_display = ('state_code', 'state_name', 'judicialvsnonjudicial', 'fc_state_months')
    search_fields = ('state_code', 'state_name')
    list_filter = ('judicialvsnonjudicial',)

@admin.register(LoanLevelAssumption)
class LoanLevelAssumptionAdmin(admin.ModelAdmin):
    """Admin configuration for LoanLevelAssumption model"""
    list_display = ('seller_raw_data', 'months_to_resolution', 'probability_of_cure', 'probability_of_foreclosure')
    list_filter = ('seller_raw_data__seller', 'seller_raw_data__trade')

@admin.register(TradeLevelAssumption)
class TradeLevelAssumptionAdmin(admin.ModelAdmin):
    """Admin configuration for TradeLevelAssumption model"""
    list_display = ('trade', 'bid_date', 'settlement_date', 'target_irr')
    list_filter = ('trade__seller',)

@admin.register(InternalValuation)
class InternalValuationAdmin(admin.ModelAdmin):
    """Admin configuration for InternalValuation model"""
    list_display = ('seller_raw_data', 'internal_uw_asis_value', 'internal_uw_arv_value', 'internal_uw_value_date')
    list_filter = ('seller_raw_data__seller', 'seller_raw_data__trade')

@admin.register(BrokerValues)
class BrokerValuesAdmin(admin.ModelAdmin):
    """Admin configuration for BrokerValues model"""
    list_display = ('seller_raw_data', 'broker_asis_value', 'broker_arv_value', 'broker_value_date')
    list_filter = ('seller_raw_data__seller', 'seller_raw_data__trade')
    # Photo is keyed to SellerRawData, so no direct inline here.
    inlines = []
    # Removed old separate photo model admin registrations (BrokerPhoto, PublicPhoto, DocumentPhoto).


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
