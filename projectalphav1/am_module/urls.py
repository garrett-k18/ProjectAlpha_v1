from django.urls import path, include
from rest_framework.routers import DefaultRouter
from am_module.views.asset_inventory import AssetInventoryViewSet

router = DefaultRouter()
router.register(r'assets', AssetInventoryViewSet, basename='asset-inventory')

urlpatterns = [
    path('am/', include(router.urls)),
]
