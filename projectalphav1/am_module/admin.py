from django.contrib import admin
from am_module.models.boarded_data import SellerBoardedData, BlendedOutcomeModel
from am_module.models.asset_metrics import AssetMetrics


class AssetMetricsInline(admin.StackedInline):
    model = AssetMetrics
    can_delete = False
    extra = 0
    fields = (
        "purchase_date",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")

# Inline removed: BlendedOutcomeModel is keyed to AssetIdHub, not directly to SellerBoardedData


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
    inlines = [AssetMetricsInline]


@admin.register(AssetMetrics)
class AssetMetricsAdmin(admin.ModelAdmin):
    list_display = (
        "asset",
        "purchase_date",
        "time_held_days_display",
        "created_at",
        "updated_at",
    )
    list_select_related = ("asset",)
    search_fields = (
        "asset__sellertape_id",
        "asset__street_address",
        "asset__city",
        "asset__state",
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
