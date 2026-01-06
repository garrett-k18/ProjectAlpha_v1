from django.urls import path, include
from rest_framework.routers import DefaultRouter
from am_module.views.view_am_assetInventory import AssetInventoryViewSet, asset_dashboard_stats, asset_geo_markers, am_pipeline_dashboard
from am_module.views.notes import AMNoteViewSet
from am_module.views.view_am_noteSummary import AMNoteSummaryView
from am_module.views.view_performance_summary import PerformanceSummaryViewSet
from am_module.views.views import cash_flow_series_view, sb_daily_loan_data_raw
from am_module.views.view_am_assetcrmcontact import AssetCRMContactViewSet
from am_module.views.view_am_taskOutcomes import (
    REODataViewSet, REOTaskViewSet,
    FCSaleViewSet, FCTaskViewSet,
    DILViewSet, DILTaskViewSet,
    ShortSaleViewSet, ShortSaleTaskViewSet,
    ModificationViewSet, ModificationTaskViewSet,
    NoteSaleViewSet, NoteSaleTaskViewSet,
    REOScopeViewSet,
    OffersViewSet,
    TaskMetricsView,
    TrackMilestonesView,
    HeirContactViewSet,
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
router.register(r'outcomes/note-sale', NoteSaleViewSet, basename='am-note-sale')
router.register(r'outcomes/note-sale-tasks', NoteSaleTaskViewSet, basename='am-note-sale-tasks')
router.register(r'outcomes/reo-scopes', REOScopeViewSet, basename='am-reo-scopes')
router.register(r'outcomes/offers', OffersViewSet, basename='am-offers')
router.register(r'outcomes/heir-contacts', HeirContactViewSet, basename='am-heir-contacts')

urlpatterns = [
    # WHAT: Note summary endpoint for AI-generated summaries
    # WHY: Provides persisted summaries that only regenerate when notes change
    # WHERE: Called by notes_quickview.vue to display AI summary
    # NOTE: Must be before router include to avoid router matching /am/notes/ first
    path('am/notes/summary/', AMNoteSummaryView.as_view(), name='am-note-summary'),
    # WHAT: Router includes for ViewSet-based endpoints
    # WHY: Provides RESTful CRUD endpoints for various models
    # WHERE: Used by frontend for standard CRUD operations
    path('am/', include(router.urls)),
    path('am/dashboard/stats/', asset_dashboard_stats, name='am-dashboard-stats'),
    path('am/dashboard/markers/', asset_geo_markers, name='am-dashboard-markers'),
    path('am/dashboard/pipeline/', am_pipeline_dashboard, name='am-pipeline-dashboard'),
    # WHAT: Cash flow series endpoint
    # WHY: Retrieve period-by-period cash flow data for time-series grid
    # WHERE: Used by CashFlowSeries.vue component
    path('am/cash-flow-series/<int:asset_id>/', cash_flow_series_view, name='cash-flow-series'),
    path('am/raw/statebridge/daily-loan-data/', sb_daily_loan_data_raw, name='sb-daily-loan-data-raw'),
    # WHAT: Task metrics endpoint for tasking dashboard
    # WHY: Provide active vs completed task counts and badge data
    # WHERE: Called by am_ll_tasking.vue to populate KPI cards
    path('am/outcomes/task-metrics/', TaskMetricsView.as_view(), name='am-task-metrics'),
    # WHAT: Track milestones endpoint for tasking dashboard
    # WHY: Provide current and upcoming tasks organized by track
    # WHERE: Called by milestonesCard.vue to populate milestone data
    path('am/outcomes/track-milestones/', TrackMilestonesView.as_view(), name='am-track-milestones'),
]
