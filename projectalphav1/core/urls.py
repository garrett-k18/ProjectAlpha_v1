"""
URL configuration for core module API endpoints

What this does:
- Registers REST API endpoints for assumptions management
- Uses Django REST Framework's router for automatic URL generation
- Provides endpoints for StateReference, FCTimelines, etc.

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
]
