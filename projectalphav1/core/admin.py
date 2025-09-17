from django.contrib import admin
from .models.capital import DebtFacility
from .models.crm import Brokercrm, TradingPartnerCRM
from .models.assumptions import Servicer, StateReference
from .models import AssetIdHub

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
