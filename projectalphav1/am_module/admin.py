from django.contrib import admin
from am_module.models.boarded_data import SellerBoardedData, BlendedOutcomeModel
from am_module.models.asset_metrics import AssetMetrics
from am_module.models.servicers import ServicerLoanData


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
