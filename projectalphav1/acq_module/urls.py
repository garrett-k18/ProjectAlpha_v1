
from django.urls import path, re_path
from .views.view_seller_data import get_seller_trade_data, get_seller_rawdata_field_names

# This defines the URL patterns for the acq_module app.
urlpatterns = [
    # Get data for a specific seller and trade
    re_path(r'^raw-data/(?P<seller_id>\d+)/(?P<trade_id>\d+)/$', get_seller_trade_data, name='api_get_seller_trade_data'),
    # Get all trades for a specific seller
    path('raw-data/<int:seller_id>/', get_seller_trade_data, name='api_get_seller_data'),
    # Get concrete field names for SellerRawData (for AG Grid columnDefs)
    path('raw-data/fields/', get_seller_rawdata_field_names, name='api_get_seller_rawdata_fields'),
]