
from django.urls import path, re_path
from .views.view_seller_data import (
    get_seller_trade_data,
    get_seller_rawdata_field_names,
    list_sellers,
    list_trades_by_seller,
    get_seller_raw_by_id,
)
from .views.photos_api import (
    list_photos_by_raw_id,
)
from .views.ai_summary import generate_quick_summary
from .views.internal_valuation_api import internal_valuation_detail

# This defines the URL patterns for the acq_module app.
urlpatterns = [
    # Get data for a specific seller and trade
    re_path(r'^raw-data/(?P<seller_id>\d+)/(?P<trade_id>\d+)/$', get_seller_trade_data, name='api_get_seller_trade_data'),
    # Get all trades for a specific seller
    path('raw-data/<int:seller_id>/', get_seller_trade_data, name='api_get_seller_data'),
    # Get a single SellerRawData by id (flat dict of fields)
    path('raw-data/by-id/<int:id>/', get_seller_raw_by_id, name='api_get_seller_raw_by_id'),
    # Get concrete field names for SellerRawData (for AG Grid columnDefs)
    path('raw-data/fields/', get_seller_rawdata_field_names, name='api_get_seller_rawdata_fields'),
    # Dropdown data sources
    path('sellers/', list_sellers, name='api_list_sellers'),
    path('trades/<int:seller_id>/', list_trades_by_seller, name='api_list_trades_by_seller'),
    # Photos endpoint (all photo types) by SellerRawData id
    path('photos/<int:id>/', list_photos_by_raw_id, name='api_list_photos_by_raw_id'),
    # AI summary endpoint
    path('ai/summary/', generate_quick_summary, name='api_ai_quick_summary'),
    # Internal valuation (internal underwriting values) by SellerRawData id
    path('valuations/internal/<int:seller_id>/', internal_valuation_detail, name='api_internal_valuation_detail'),
]