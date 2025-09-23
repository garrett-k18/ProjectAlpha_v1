from django.urls import path, include
from rest_framework.routers import DefaultRouter
from am_module.views.asset_inventory import AssetInventoryViewSet
from am_module.views.notes import AMNoteViewSet

router = DefaultRouter()
router.register(r'assets', AssetInventoryViewSet, basename='asset-inventory')
router.register(r'notes', AMNoteViewSet, basename='am-notes')

urlpatterns = [
    path('am/', include(router.urls)),
]
