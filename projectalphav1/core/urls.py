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

# Create a router and register our viewsets
router = DefaultRouter()

# Register assumptions-related viewsets
router.register(r'state-assumptions', StateReferenceViewSet, basename='state-assumptions')
router.register(r'fc-timelines', FCTimelinesViewSet, basename='fc-timelines')
router.register(r'fc-statuses', FCStatusViewSet, basename='fc-statuses')
router.register(r'commercial-units', CommercialUnitsViewSet, basename='commercial-units')
router.register(r'servicers', ServicerViewSet, basename='servicers')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    
    # Commercial analysis endpoints (match paths expected by frontend CommercialAnalysisTab)
    path('unit-mix/<int:asset_hub_id>/', UnitMixListView.as_view(), name='unit-mix-list'),
    path('lease-comp-unit-mix/<int:asset_hub_id>/', LeaseComparableUnitMixListView.as_view(), name='lease-comp-unit-mix-list'),
    path('lease-comp-rent-roll/<int:asset_hub_id>/', LeaseComparableRentRollListView.as_view(), name='lease-comp-rent-roll-list'),
    path('rent-roll/<int:asset_hub_id>/', RentRollListView.as_view(), name='rent-roll-list'),
    path('historical-cashflow/<int:asset_hub_id>/', HistoricalPropertyCashFlowListView.as_view(), name='historical-cashflow-list'),
]
