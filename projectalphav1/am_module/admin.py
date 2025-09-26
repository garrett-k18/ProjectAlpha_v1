from django.contrib import admin
from am_module.models.boarded_data import SellerBoardedData, BlendedOutcomeModel
from am_module.models.asset_metrics import AssetMetrics
from am_module.models.servicers import ServicerLoanData
from am_module.models.am_data import (
    AMMetrics, AMMetricsChange, AuditLog,
    AMNote, REOData, FCSale, DIL, ShortSale, Modification,
    REOtask, FCTask, DILTask, ShortSaleTask, ModificationTask
)

class AssetMetricsInline(admin.StackedInline):
    """
    NOTE: AssetMetrics is keyed to core.AssetIdHub (primary key) and does NOT
    have a ForeignKey to SellerBoardedData. Django inlines require a direct FK
    to the parent model, so we cannot inline AssetMetrics under SellerBoardedData.

    Keeping this class as a placeholder for future hub-centric admin, but it is
    not used in SellerBoardedDataAdmin.inlines.
    """
    model = AssetMetrics
    can_delete = False
    extra = 0
    fields = (
        "purchase_date",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
# Inline note: BlendedOutcomeModel is keyed to AssetIdHub, not directly to SellerBoardedData


@admin.register(SellerBoardedData)
class SellerBoardedDataAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sellertape_id",
        "seller_name",
        "trade_name",
        "asset_status",
        "street_address",
        "city",
        "state",
        "property_type",
        "occupancy",
        "seller_asis_value",
    )
    list_filter = (
        "asset_status",
        "state",
        "property_type",
        "occupancy",
    )
    search_fields = (
        "sellertape_id",
        "seller_name",
        "trade_name",
        "street_address",
        "city",
        "state",
        "zip",
    )
    ordering = ("-id",)
    # Cannot inline AssetMetrics here because it is keyed to core.AssetIdHub, not this model.
    inlines = []


@admin.register(AssetMetrics)
class AssetMetricsAdmin(admin.ModelAdmin):
    list_display = (
        "asset_hub",
        "purchase_date",
        "time_held_days_display",
        "created_at",
        "updated_at",
    )
    list_select_related = ("asset_hub",)
    search_fields = (
        # Traverse hub -> boarded record for human fields
        "asset_hub__am_boarded__sellertape_id",
        "asset_hub__am_boarded__street_address",
        "asset_hub__am_boarded__city",
        "asset_hub__am_boarded__state",
    )
    ordering = ("-created_at",)

    def time_held_days_display(self, obj: AssetMetrics) -> int:
        return obj.time_held_days

    time_held_days_display.short_description = "Days Held"


@admin.register(BlendedOutcomeModel)
class BlendedOutcomeModelAdmin(admin.ModelAdmin):
    list_display = (
        "asset_hub",
    )
    search_fields = (
        # Traverse hub -> boarded record for human fields
        "asset_hub__am_boarded__sellertape_id",
        "asset_hub__am_boarded__street_address",
        "asset_hub__am_boarded__city",
        "asset_hub__am_boarded__state",
    )


@admin.register(ServicerLoanData)
class ServicerLoanDataAdmin(admin.ModelAdmin):
    list_display = (
        "asset_hub",
        "reporting_period",
        "current_balance",
        "interest_rate",
        "next_due_date",
        "last_paid_date",
        "term_remaining",
        "lien_pos",
    )
    list_filter = (
        "reporting_year",
        "reporting_month",
        "lien_pos",
    )
    search_fields = (
        # Traverse hub -> boarded record for human fields
        "asset_hub__am_boarded__sellertape_id",
        "asset_hub__am_boarded__street_address",
        "asset_hub__am_boarded__city",
        "asset_hub__am_boarded__state",
    )
    fieldsets = (
        ("Asset Information", {
            "fields": ("asset_hub",)
        }),
        ("Reporting Period", {
            "fields": (
                "reporting_year", "reporting_month", "as_of_date",
            )
        }),
        ("Current Loan Data", {
            "fields": (
                "current_balance", "deferred_balance", "interest_rate",
                "next_due_date", "last_paid_date", "term_remaining", "maturity_date", "lien_pos",
            )
        }),
        ("Balance Information", {
            "fields": (
                "escrow_balance", "escrow_advance_balance", "third_party_recov_balance",
                "suspense_balance", "servicer_late_fees", "other_charges", "interest_arrears", "total_debt",
            )
        }),
        ("BPLS", {
            "fields": ("default_rate",)
        }),
        ("Origination Data", {
            "fields": ("origination_date", "origination_balance", "origination_interest_rate")
        }),
        ("Audit", {
            "fields": ("created_at", "updated_at", "created_by", "updated_by")
        }),
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-reporting_year", "-reporting_month", "-updated_at")
    
    def reporting_period(self, obj):
        """Format the reporting period as MM/YYYY."""
        if obj.reporting_month and obj.reporting_year:
            return f"{obj.reporting_month:02d}/{obj.reporting_year}"
        return "N/A"
    
    reporting_period.short_description = "Period"


@admin.register(REOtask)
class REOtaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset_hub', 'reo_outcome', 'task_type', 'created_at', 'updated_at')
    list_filter = ('task_type',)
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'asset_hub__am_boarded__street_address',
    )
    ordering = ('-updated_at',)
    list_select_related = ('asset_hub', 'reo_outcome')


@admin.register(FCTask)
class FCTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset_hub', 'fc_sale', 'task_type', 'created_at', 'updated_at')
    list_filter = ('task_type',)
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'asset_hub__am_boarded__street_address',
    )
    ordering = ('-updated_at',)
    list_select_related = ('asset_hub', 'fc_sale')


@admin.register(DILTask)
class DILTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset_hub', 'dil', 'task_type', 'created_at', 'updated_at')
    list_filter = ('task_type',)
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'asset_hub__am_boarded__street_address',
    )
    ordering = ('-updated_at',)
    list_select_related = ('asset_hub', 'dil')


@admin.register(ShortSaleTask)
class ShortSaleTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset_hub', 'short_sale', 'task_type', 'created_at', 'updated_at')
    list_filter = ('task_type',)
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'asset_hub__am_boarded__street_address',
    )
    ordering = ('-updated_at',)
    list_select_related = ('asset_hub', 'short_sale')


@admin.register(ModificationTask)
class ModificationTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset_hub', 'modification', 'task_type', 'created_at', 'updated_at')
    list_filter = ('task_type',)
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'asset_hub__am_boarded__street_address',
    )
    ordering = ('-updated_at',)
    list_select_related = ('asset_hub', 'modification')


@admin.register(AMMetrics)
class AMMetricsAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset_hub', 'updated_at', 'updated_by')
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'asset_hub__am_boarded__street_address',
    )
    ordering = ('-updated_at',)
    list_select_related = ('asset_hub', 'updated_by')
    readonly_fields = ('updated_at',)


@admin.register(AMMetricsChange)
class AMMetricsChangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'record', 'asset_hub', 'field_name', 'changed_at', 'changed_by')
    list_filter = ('field_name', 'changed_at')
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'field_name',
    )
    ordering = ('-changed_at',)
    list_select_related = ('record', 'asset_hub', 'changed_by')
    readonly_fields = ('changed_at',)


@admin.register(AMNote)
class AMNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset_hub', 'tag', 'pinned', 'body_preview', 'created_at', 'created_by')
    list_filter = ('tag', 'pinned', 'created_at')
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'body',
    )
    ordering = ('-pinned', '-updated_at')
    list_select_related = ('asset_hub', 'created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at')
    
    def body_preview(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
    body_preview.short_description = 'Body Preview'


@admin.register(REOData)
class REODataAdmin(admin.ModelAdmin):
    list_display = ('asset_hub', 'list_price', 'list_date', 'under_contract_flag', 'contract_price', 'actual_close_date')
    list_filter = ('under_contract_flag', 'purchase_type')
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'asset_hub__am_boarded__street_address',
    )
    ordering = ('-list_date',)
    list_select_related = ('asset_hub', 'crm')


@admin.register(FCSale)
class FCSaleAdmin(admin.ModelAdmin):
    list_display = ('asset_hub', 'fc_sale_sched_date', 'fc_sale_actual_date', 'fc_bid_price', 'fc_sale_price')
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'asset_hub__am_boarded__street_address',
    )
    ordering = ('-fc_sale_actual_date', '-fc_sale_sched_date')
    list_select_related = ('asset_hub', 'crm')


@admin.register(DIL)
class DILAdmin(admin.ModelAdmin):
    list_display = ('asset_hub', 'dil_completion_date', 'dil_cost', 'cfk_cost')
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'asset_hub__am_boarded__street_address',
    )
    ordering = ('-dil_completion_date',)
    list_select_related = ('asset_hub', 'crm')


@admin.register(ShortSale)
class ShortSaleAdmin(admin.ModelAdmin):
    list_display = ('asset_hub', 'acceptable_min_offer', 'short_sale_date')
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'asset_hub__am_boarded__street_address',
    )
    ordering = ('-short_sale_date',)
    list_select_related = ('asset_hub', 'crm')


@admin.register(Modification)
class ModificationAdmin(admin.ModelAdmin):
    list_display = ('asset_hub', 'modification_date', 'modification_cost', 'modification_upb', 'modification_rate', 'modification_pi')
    list_filter = ('modification_pi',)
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'asset_hub__am_boarded__street_address',
    )
    ordering = ('-modification_date',)
    list_select_related = ('asset_hub', 'crm')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type', 'object_id', 'asset_hub', 'field_name', 'changed_at', 'changed_by')
    list_filter = ('content_type', 'field_name', 'changed_at')
    search_fields = (
        'asset_hub__am_boarded__sellertape_id',
        'field_name',
        'old_value',
        'new_value',
    )
    ordering = ('-changed_at',)
    list_select_related = ('content_type', 'asset_hub', 'changed_by')
    readonly_fields = ('changed_at', 'content_type', 'object_id', 'content_object')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('content_type', 'asset_hub', 'changed_by')
