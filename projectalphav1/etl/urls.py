"""
ETL Module URL Configuration

WHAT: URL routing for ETL module API endpoints
WHY: Expose import mapping management endpoints
HOW: DRF router for ViewSet registration

Docs reviewed:
- Django URL dispatcher: https://docs.djangoproject.com/en/stable/topics/http/urls/
- DRF Routers: https://www.django-rest-framework.org/api-guide/routers/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from etl.views.view_etl_import_mapping import ImportMappingViewSet

# WHAT: DRF router for automatic URL generation
# WHY: Provides standard REST endpoints for ViewSets
# HOW: Register ViewSets with router
router = DefaultRouter()

# WHAT: Register ImportMapping ViewSet
# WHY: Expose CRUD endpoints for import mappings
# HOW: Router generates standard REST URLs
router.register(r'import-mappings', ImportMappingViewSet, basename='import-mapping')

# WHAT: URL patterns for ETL module
# WHY: Include router URLs in Django URL configuration
# HOW: Include router.urls
urlpatterns = [
    path('', include(router.urls)),
]
