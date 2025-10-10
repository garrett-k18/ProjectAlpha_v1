"""
URL configuration for core module API endpoints

What this does:
- Registers REST API endpoints for assumptions management
- Uses Django REST Framework's router for automatic URL generation
- Provides endpoints for StateReference, FCTimelines, etc.
- Provides commercial analysis endpoints for unit mix and rent roll data

Location: projectalphav1/core/urls.py
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views.views_assumptions import (
    StateReferenceViewSet,
    FCTimelinesViewSet,
    FCStatusViewSet,
    CommercialUnitsViewSet,
    ServicerViewSet
)
from core.views.commercial_api import (
    UnitMixListView,
    LeaseComparableUnitMixListView,
    LeaseComparableRentRollListView,
    RentRollListView,
    HistoricalPropertyCashFlowListView
)
from core.views.calendar_api import get_calendar_events, CustomCalendarEventViewSet
from core.views.macro_metrics_api_new import (
    get_mortgage_30_year_api,
    get_10_year_treasury_api,
    get_fed_funds_rate_api,
    get_sofr_api,
    get_cpi_api
)
from core.views.crm_api import (
    InvestorViewSet,
    BrokerViewSet,
    TradingPartnerViewSet,
    LegalViewSet,
)

# Create a router and register our viewsets
router = DefaultRouter()

# Register assumptions-related viewsets
router.register(r'state-assumptions', StateReferenceViewSet, basename='state-assumptions')
router.register(r'fc-timelines', FCTimelinesViewSet, basename='fc-timelines')
router.register(r'fc-statuses', FCStatusViewSet, basename='fc-statuses')
router.register(r'commercial-units', CommercialUnitsViewSet, basename='commercial-units')
router.register(r'servicers', ServicerViewSet, basename='servicers')

# Register calendar viewset for custom events (CRUD operations)
router.register(r'calendar/events/custom', CustomCalendarEventViewSet, basename='calendar-custom-events')

# Register CRM viewsets for Investors, Brokers, Trading Partners, Legal
# These provide tag-filtered views of the MasterCRM model
router.register(r'crm/investors', InvestorViewSet, basename='crm-investors')
router.register(r'crm/brokers', BrokerViewSet, basename='crm-brokers')
router.register(r'crm/trading-partners', TradingPartnerViewSet, basename='crm-trading-partners')
router.register(r'crm/legal', LegalViewSet, basename='crm-legal')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    
    # Calendar events endpoint - aggregates dates from various models
    path('calendar/events/', get_calendar_events, name='calendar-events'),
    
    # Macro Metrics endpoints - FRED API economic indicators
    path('macro/mortgage-rates/30-year/', get_mortgage_30_year_api, name='macro-mortgage-30'),
    path('macro/10-year-treasury/', get_10_year_treasury_api, name='macro-10yr-treasury'),
    path('macro/fed-funds-rate/', get_fed_funds_rate_api, name='macro-fed-funds'),
    path('macro/sofr/', get_sofr_api, name='macro-sofr'),
    path('macro/cpi/', get_cpi_api, name='macro-cpi'),
    
    # Commercial analysis endpoints (match paths expected by frontend CommercialAnalysisTab)
    path('unit-mix/<int:asset_hub_id>/', UnitMixListView.as_view(), name='unit-mix-list'),
    path('lease-comp-unit-mix/<int:asset_hub_id>/', LeaseComparableUnitMixListView.as_view(), name='lease-comp-unit-mix-list'),
    path('lease-comp-rent-roll/<int:asset_hub_id>/', LeaseComparableRentRollListView.as_view(), name='lease-comp-rent-roll-list'),
    path('rent-roll/<int:asset_hub_id>/', RentRollListView.as_view(), name='rent-roll-list'),
    path('historical-cashflow/<int:asset_hub_id>/', HistoricalPropertyCashFlowListView.as_view(), name='historical-cashflow-list'),
]
