from django.contrib import admin
from .models.capital import DebtFacility
from .models.crm import Brokercrm, TradingPartnerCRM
from .models.assumptions import Servicer, StateReference
from .models.asset_id_hub import AssetIdHub
from .models.valuations import Valuation
from .models.attachments import Photo, Document

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


@admin.register(TradingPartnerCRM)
class TradingPartnerCRMAdmin(admin.ModelAdmin):
    """Admin configuration for TradingPartnerCRM (trading partners directory) model.

    Notes:
    - `firm` is required; all other fields are optional per model definition.
    - Provides convenient list columns and search to quickly find partners.
    """
    list_display = (
        'firm', 'name', 'email', 'phone', 'altname', 'altemail', 'alt_phone', 'nda_flag', 'nda_signed', 'created_at'
    )
    list_filter = (
        'nda_flag',
    )
    search_fields = (
        'firm', 'name', 'email', 'phone', 'altname', 'altemail', 'alt_phone'
    )


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
    fieldsets = (
        ('Asset Information', {
            'fields': ('asset_hub', 'source')
        }),
        ('Valuation Data', {
            'fields': ('asis_value', 'arv_value', 'value_date', 'rehab_est_total')
        }),
        ('Rehab Estimates', {
            'fields': ('roof_est', 'kitchen_est', 'bath_est', 'flooring_est', 'windows_est',
                      'appliances_est', 'plumbing_est', 'electrical_est', 'landscaping_est')
        }),
        ('Additional Information', {
            'fields': ('notes', 'links')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by')
        }),
    )
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


@admin.register(AssetIdHub)
class AssetIdHubAdmin(admin.ModelAdmin):
    """Admin for the central Asset ID Hub."""
    list_display = (
        'id', 'sellertape_id', 'created_at'
    )
    search_fields = (
        'sellertape_id',
    )
    list_filter = ()
