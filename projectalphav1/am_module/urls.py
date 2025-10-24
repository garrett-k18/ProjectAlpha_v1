from django.urls import path, include
from rest_framework.routers import DefaultRouter
from am_module.views.view_am_assetInventory import AssetInventoryViewSet, asset_dashboard_stats, asset_geo_markers
from am_module.views.notes import AMNoteViewSet
from am_module.views.view_performance_summary import PerformanceSummaryViewSet
from am_module.views.views import cash_flow_series_view
from am_module.views.view_am_assetcrmcontact import AssetCRMContactViewSet
from am_module.views.outcomes import (
    REODataViewSet, REOTaskViewSet,
    FCSaleViewSet, FCTaskViewSet,
    DILViewSet, DILTaskViewSet,
    ShortSaleViewSet, ShortSaleTaskViewSet,
    ModificationViewSet, ModificationTaskViewSet,
    REOScopeViewSet,
)

router = DefaultRouter()
router.register(r'assets', AssetInventoryViewSet, basename='asset-inventory')
router.register(r'notes', AMNoteViewSet, basename='am-notes')
router.register(r'performance-summary', PerformanceSummaryViewSet, basename='performance-summary')
router.register(r'asset-crm-contacts', AssetCRMContactViewSet, basename='asset-crm-contacts')
router.register(r'outcomes/reo', REODataViewSet, basename='am-reo')
router.register(r'outcomes/reo-tasks', REOTaskViewSet, basename='am-reo-tasks')
router.register(r'outcomes/fc', FCSaleViewSet, basename='am-fc')
router.register(r'outcomes/fc-tasks', FCTaskViewSet, basename='am-fc-tasks')
router.register(r'outcomes/dil', DILViewSet, basename='am-dil')
router.register(r'outcomes/dil-tasks', DILTaskViewSet, basename='am-dil-tasks')
router.register(r'outcomes/short-sale', ShortSaleViewSet, basename='am-short-sale')
router.register(r'outcomes/short-sale-tasks', ShortSaleTaskViewSet, basename='am-short-sale-tasks')
router.register(r'outcomes/modification', ModificationViewSet, basename='am-modification')
router.register(r'outcomes/modification-tasks', ModificationTaskViewSet, basename='am-modification-tasks')
router.register(r'outcomes/reo-scopes', REOScopeViewSet, basename='am-reo-scopes')

urlpatterns = [
    path('am/', include(router.urls)),
    path('am/dashboard/stats/', asset_dashboard_stats, name='am-dashboard-stats'),
    path('am/dashboard/markers/', asset_geo_markers, name='am-dashboard-markers'),
    # WHAT: Cash flow series endpoint
    # WHY: Retrieve period-by-period cash flow data for time-series grid
    # WHERE: Used by CashFlowSeries.vue component
    path('am/cash-flow-series/<int:asset_id>/', cash_flow_series_view, name='cash-flow-series'),
]
