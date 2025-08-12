from django.urls import path
from .views.view_seller_data import get_seller_trade_data

# This defines the URL patterns for the acq_module app.
urlpatterns = [
    # Get data for a specific seller and trade
    re_path(r'^raw-data/(?P<seller_id>\d+)/(?P<trade_id>\d+)/$', get_seller_trade_data, name='api_get_seller_trade_data'),
    # Get all trades for a specific seller
    path('raw-data/<int:seller_id>/', get_seller_trade_data, name='api_get_seller_data'),
]
