from django.contrib import admin
from django.db.models import Exists, OuterRef
from django.urls import reverse
from django.utils.html import format_html
from urllib.parse import quote
from .models.capital import DebtFacility
from .models.crm import MasterCRM
from .models.assumptions import Servicer, StateReference
from .models.asset_id_hub import AssetIdHub
from .models.valuations import Valuation
from .models.attachments import Photo, Document

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
    fieldsets = (
        ('Primary Contact', {
            'fields': ('contact_name', 'email', 'phone', 'firm', 'state', 'city', 'tag')
        }),
        ('Alternate Contact', {
            'fields': ('alt_contact_name', 'alt_contact_email', 'alt_contact_phone')
        }),
        ('NDA', {
            'fields': ('nda_flag', 'nda_signed')
        }),
        ('Notes & Audit', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
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
        'id', 'servicer_id', 'servicer_refs',
        # Boolean columns indicating presence of child records
        'has_raw', 'has_boarded', 'has_blended', 'has_servicer', 'has_valuation', 'has_photo', 'has_document',
        'created_at',
    )
    # Show more rows per page (default is 100). Also allow larger "Show all" limit.
    list_per_page = 500
    list_max_show_all = 2000
    search_fields = (
        'servicer_id',
    )
    list_filter = ()
    actions_on_top = True
    actions_on_bottom = True
    actions = ['delete_selected', delete_hub_and_children]

    def get_queryset(self, request):
        """Annotate queryset with boolean flags indicating related children exist.

        We keep this read-only and computed at query time using EXISTS subqueries
        to avoid schema changes and synchronization complexity.
        """
        qs = super().get_queryset(request)
        return qs.annotate(
            has_raw=Exists(
                SellerRawData.objects.filter(asset_hub=OuterRef('pk'))
            ),
            has_boarded=Exists(
                SellerBoardedData.objects.filter(asset_hub=OuterRef('pk'))
            ),
            has_blended=Exists(
                BlendedOutcomeModel.objects.filter(asset_hub=OuterRef('pk'))
            ),
            has_servicer=Exists(
                ServicerLoanData.objects.filter(asset_hub=OuterRef('pk'))
            ),
            has_valuation=Exists(
                Valuation.objects.filter(asset_hub=OuterRef('pk'))
            ),
            has_photo=Exists(
                Photo.objects.filter(asset_hub=OuterRef('pk'))
            ),
            has_document=Exists(
                Document.objects.filter(asset_hub=OuterRef('pk'))
            ),
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

    

    # The following accessors simply surface the annotated booleans to the admin list.
    # Django admin uses the attribute name in list_display, so we expose them as methods
    # and mark them as boolean for visual check/times.
    def has_raw(self, obj: AssetIdHub) -> bool:
        return bool(getattr(obj, 'has_raw', False))
    has_raw.boolean = True
    has_raw.short_description = 'Raw?'

    def has_boarded(self, obj: AssetIdHub) -> bool:
        return bool(getattr(obj, 'has_boarded', False))
    has_boarded.boolean = True
    has_boarded.short_description = 'Boarded?'

    def has_blended(self, obj: AssetIdHub) -> bool:
        return bool(getattr(obj, 'has_blended', False))
    has_blended.boolean = True
    has_blended.short_description = 'Blended?'

    def has_servicer(self, obj: AssetIdHub) -> bool:
        return bool(getattr(obj, 'has_servicer', False))
    has_servicer.boolean = True
    has_servicer.short_description = 'Servicer?'

    def has_valuation(self, obj: AssetIdHub) -> bool:
        return bool(getattr(obj, 'has_valuation', False))
    has_valuation.boolean = True
    has_valuation.short_description = 'Valuation?'

    def has_photo(self, obj: AssetIdHub) -> bool:
        return bool(getattr(obj, 'has_photo', False))
    has_photo.boolean = True
    has_photo.short_description = 'Photos?'

    def has_document(self, obj: AssetIdHub) -> bool:
        return bool(getattr(obj, 'has_document', False))
    has_document.boolean = True
    has_document.short_description = 'Docs?'
