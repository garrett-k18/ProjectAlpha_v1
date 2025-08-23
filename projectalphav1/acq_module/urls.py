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
from .views.broker_invite_api import (
    create_broker_invite,
    validate_broker_invite,
    submit_broker_values_with_token,
    list_brokers_by_state_batch,
)
from .views.geocode import geocode_markers
from .views.brokers_api import (
    broker_detail,
    list_assigned_loans,
)

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
    # Broker invite/token endpoints (public)
    path('broker-invites/', create_broker_invite, name='api_create_broker_invite'),  # POST
    # Broker listing for UI (state-based batch) MUST come before the catch-all token path
    path('broker-invites/by-state-batch/', list_brokers_by_state_batch, name='api_list_brokers_by_state_batch'),  # GET
    path('broker-invites/<str:token>/', validate_broker_invite, name='api_validate_broker_invite'),  # GET
    path('broker-invites/<str:token>/submit/', submit_broker_values_with_token, name='api_submit_broker_values_with_token'),  # POST
    # Broker detail and assigned loans
    path('brokers/<int:broker_id>/', broker_detail, name='api_broker_detail'),  # GET
    path('brokers/<int:broker_id>/assigned-loans/', list_assigned_loans, name='api_broker_assigned_loans'),  # GET
    # Geocoded markers for seller+trade
    path('geocode/markers/<int:seller_id>/<int:trade_id>/', geocode_markers, name='api_geocode_markers'),
]