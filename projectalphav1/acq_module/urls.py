from django.urls import path, re_path
from .views.view_seller_data import (
    get_seller_trade_data,
    get_seller_rawdata_field_names,
    list_sellers,
    list_trades_by_seller,
    get_seller_raw_by_id,
    # State summary endpoints
    get_states_for_selection,
    get_state_count_for_selection,
    get_count_by_state,
    get_sum_current_balance_by_state,
    get_sum_total_debt_by_state,
    get_sum_seller_asis_value_by_state,
    get_pool_summary,
    get_current_balance_stratification,
    get_total_debt_stratification,
    get_seller_asis_value_stratification,
    get_wac_stratification,
    get_judicial_stratification,
    get_property_type_stratification,
    get_occupancy_stratification,
    # LTV scatter chart data
    get_ltv_scatter_data_view,
)
from .views.state_reference_api import get_judicial_states
from .views.photos_api import (
    list_photos_by_raw_id,
)
from .views.ai_summary import generate_quick_summary
from .views.internal_valuation_api import internal_valuation_detail
from .views.brokers.invites import (
    create_broker_invite,
    validate_broker_invite,
    submit_broker_values_with_token,
    list_brokers_by_state_batch,
    upload_broker_photos_with_token,
    upload_broker_documents_with_token,
)
from .views.brokers.portal import (
    assign_broker_batch,
    broker_portal_detail,
)
from .views.geocode import geocode_markers
from .views.brokers.internal import (
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
    path('broker-invites/<str:token>/photos/', upload_broker_photos_with_token, name='api_upload_broker_photos_with_token'),  # POST (public)
    path('broker-invites/<str:token>/documents/', upload_broker_documents_with_token, name='api_upload_broker_documents_with_token'),  # POST (public)
    # Broker portal endpoints
    path('broker-portal/assign/', assign_broker_batch, name='api_assign_broker_batch'),  # POST (internal)
    path('broker-portal/<str:token>/', broker_portal_detail, name='api_broker_portal_detail'),  # GET (public)
    # Broker detail and assigned loans
    path('brokers/<int:broker_id>/', broker_detail, name='api_broker_detail'),  # GET
    path('brokers/<int:broker_id>/assigned-loans/', list_assigned_loans, name='api_broker_assigned_loans'),  # GET
    # Geocoded markers for seller+trade
    path('geocode/markers/<int:seller_id>/<int:trade_id>/', geocode_markers, name='api_geocode_markers'),
    # State summary endpoints (per-seller, per-trade)
    path('summary/state/list/<int:seller_id>/<int:trade_id>/', get_states_for_selection, name='api_states_for_selection'),
    path('summary/state/count/<int:seller_id>/<int:trade_id>/', get_state_count_for_selection, name='api_state_count_for_selection'),
    path('summary/state/count-by/<int:seller_id>/<int:trade_id>/', get_count_by_state, name='api_count_by_state'),
    path('summary/state/sum-current-balance/<int:seller_id>/<int:trade_id>/', get_sum_current_balance_by_state, name='api_sum_current_balance_by_state'),
    path('summary/state/sum-total-debt/<int:seller_id>/<int:trade_id>/', get_sum_total_debt_by_state, name='api_sum_total_debt_by_state'),
    path('summary/state/sum-seller-asis-value/<int:seller_id>/<int:trade_id>/', get_sum_seller_asis_value_by_state, name='api_sum_seller_asis_value_by_state'),
    # Pool summary (single aggregate for top widgets)
    path('summary/pool/<int:seller_id>/<int:trade_id>/', get_pool_summary, name='api_pool_summary'),
    # Dynamic current balance stratification
    path('summary/strat/current-balance/<int:seller_id>/<int:trade_id>/', get_current_balance_stratification, name='api_current_balance_stratification'),
    # Dynamic total debt stratification
    path('summary/strat/total-debt/<int:seller_id>/<int:trade_id>/', get_total_debt_stratification, name='api_total_debt_stratification'),
    # Dynamic seller as-is value stratification
    path('summary/strat/seller-asis-value/<int:seller_id>/<int:trade_id>/', get_seller_asis_value_stratification, name='api_seller_asis_value_stratification'),
    # Static interest rate (WAC) stratification
    path('summary/strat/interest-rate/<int:seller_id>/<int:trade_id>/', get_wac_stratification, name='api_interest_rate_stratification'),
    # Alias path for convenience
    path('summary/strat/wac/<int:seller_id>/<int:trade_id>/', get_wac_stratification, name='api_wac_stratification'),
    # Judicial vs Non-Judicial stratification
    path('summary/strat/judicial/<int:seller_id>/<int:trade_id>/', get_judicial_stratification, name='api_judicial_stratification'),
    # Property Type stratification (categorical)
    path('summary/strat/property-type/<int:seller_id>/<int:trade_id>/', get_property_type_stratification, name='api_property_type_stratification'),
    # Occupancy stratification (categorical)
    path('summary/strat/occupancy/<int:seller_id>/<int:trade_id>/', get_occupancy_stratification, name='api_occupancy_stratification'),
    # LTV scatter chart data
    path('summary/ltv-scatter/<int:seller_id>/<int:trade_id>/', get_ltv_scatter_data_view, name='api_ltv_scatter_data'),
    # State reference endpoints
    path('state-references/judicial/', get_judicial_states, name='api_judicial_states'),
]