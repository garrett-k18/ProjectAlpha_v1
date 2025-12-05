from django.urls import path, re_path
from .views.view_acq_sellerTrade import (
    list_sellers,
    list_trades_by_seller,
    list_active_deals,
    get_pool_summary,
    get_valuation_completion_summary,
    get_collateral_completion_summary,
    get_title_completion_summary,
    get_states_for_selection,
    get_state_count_for_selection,
    get_count_by_state,
    get_sum_current_balance_by_state,
    get_sum_total_debt_by_state,
    get_sum_seller_asis_value_by_state,
    get_current_balance_stratification,
    get_total_debt_stratification,
    get_seller_asis_value_stratification,
    get_wac_stratification,
    get_default_rate_stratification,
    get_judicial_stratification,
    get_property_type_stratification,
    get_occupancy_stratification,
    get_delinquency_stratification,
    get_ltv_scatter_data_view,
)
from .views.state_reference_api import get_judicial_states
from .views.photos_api import list_photos_by_raw_id
from .views.ai_summary import generate_quick_summary
from .views.view_acq_valuationCenter import valuation_center_list, valuation_center_update
from .views.view_acq_grid import grid_data
from .views.asset_fc_timeline import AssetFCTimelineView
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
from core.views.geocoding import geocode_markers
from .views.brokers.internal import (
    broker_detail,
    list_assigned_loans,
    list_brokers,
)
from .views.view_acq_tradeAssumptions import (
    get_trade_level_assumptions,
    update_trade_level_assumptions,
)
from .views.view_acq_assumptionDefaults import (
    get_assumption_defaults,
    update_assumption_defaults,
)
from .views.view_acq_status import (
    # Trade-level status management
    get_trade_status,
    update_trade_status,
    # Asset-level status management
    drop_asset,
    restore_asset,
    bulk_drop_assets,
    bulk_restore_assets,
)
from .views.view_acq_directImport import import_seller_tape, preview_seller_tape
from .views.view_acq_model import (
    get_asset_model_recommendations,
    bulk_model_recommendations,
    get_fc_model_timeline_sums,
    get_reo_model_timeline_sums,
    update_fc_duration_override,
    update_reo_fc_duration_override,
    update_reo_renovation_override,
    update_reo_marketing_override,
    update_acquisition_price,
)
from .views.view_acq_modelingCenter import modeling_center_data

# Test endpoint to verify Django is responding
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def test_logging(request):
    print('\n\n=== TEST ENDPOINT CALLED ===')
    print('Django is receiving requests!')
    print('=== TEST ENDPOINT END ===\n\n')
    return Response({'status': 'ok', 'message': 'Django is working!'})

# This defines the URL patterns for the acq_module app.
urlpatterns = [
    # Asset actions (drop/restore)
    path('assets/<int:asset_id>/drop/', drop_asset, name='api_drop_asset'),
    path('assets/<int:asset_id>/restore/', restore_asset, name='api_restore_asset'),
    path('assets/bulk-drop/', bulk_drop_assets, name='api_bulk_drop_assets'),
    path('assets/bulk-restore/', bulk_restore_assets, name='api_bulk_restore_assets'),
    # Model recommendations
    path('assets/<int:asset_id>/model-recommendations/', get_asset_model_recommendations, name='api_asset_model_recommendations'),
    path('model-recommendations/bulk/', bulk_model_recommendations, name='api_bulk_model_recommendations'),
    # FC model timeline sums
    path('assets/<int:asset_id>/fc-model-sums/', get_fc_model_timeline_sums, name='api_fc_model_timeline_sums'),
    path('assets/<int:asset_id>/fc-duration-override/', update_fc_duration_override, name='api_fc_duration_override'),
    # REO model timeline sums
    path('assets/<int:asset_id>/reo-model-sums/', get_reo_model_timeline_sums, name='api_reo_model_timeline_sums'),
    path('assets/<int:asset_id>/reo-fc-duration-override/', update_reo_fc_duration_override, name='api_reo_fc_duration_override'),
    path('assets/<int:asset_id>/reo-renovation-override/', update_reo_renovation_override, name='api_reo_renovation_override'),
    path('assets/<int:asset_id>/reo-marketing-override/', update_reo_marketing_override, name='api_reo_marketing_override'),
    # Shared acquisition price endpoint
    path('assets/<int:asset_id>/acquisition-price/', update_acquisition_price, name='api_update_acquisition_price'),
    # Dropdown data sources
    path('sellers/', list_sellers, name='api_list_sellers'),
    path('trades/active-deals/', list_active_deals, name='api_list_active_deals'),
    path('trades/<int:seller_id>/', list_trades_by_seller, name='api_list_trades_by_seller'),
    # Photos endpoint (all photo types) by SellerRawData id
    path('photos/<int:id>/', list_photos_by_raw_id, name='api_list_photos_by_raw_id'),
    # AI summary endpoint
    path('ai/summary/', generate_quick_summary, name='api_ai_quick_summary'),
    # Valuation Center dedicated endpoints (clean, efficient)
    path('valuation-center/<int:seller_id>/<int:trade_id>/', valuation_center_list, name='api_valuation_center_list'),
    path('valuation-center/<int:asset_id>/', valuation_center_update, name='api_valuation_center_update'),
    # AG Grid dedicated endpoint (clean, efficient - replaces raw-data for grid)
    path('grid/<int:seller_id>/<int:trade_id>/', grid_data, name='api_grid_data'),
    # Modeling Center bulk endpoint (efficient - single query for all assets)
    path('modeling-center/<int:seller_id>/<int:trade_id>/', modeling_center_data, name='api_modeling_center_data'),
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
    path('brokers/', list_brokers, name='api_brokers_list'),  # GET (public)
    path('brokers/<int:broker_id>/', broker_detail, name='api_broker_detail'),  # GET
    path('brokers/<int:broker_id>/assigned-loans/', list_assigned_loans, name='api_broker_assigned_loans'),  # GET
    # Geocoded markers for seller+trade
    path('geocode/markers/<int:seller_id>/<int:trade_id>/', geocode_markers, name='api_geocode_markers'),
    # Trade level assumptions endpoints
    path('trade-assumptions/<int:trade_id>/', get_trade_level_assumptions, name='api_get_trade_assumptions'),  # GET
    path('trade-assumptions/<int:trade_id>/update/', update_trade_level_assumptions, name='api_update_trade_assumptions'),  # POST, PUT
    # Assumption defaults endpoints
    path('assumption-defaults/', get_assumption_defaults, name='api_get_assumption_defaults'),  # GET
    path('assumption-defaults/update/', update_assumption_defaults, name='api_update_assumption_defaults'),  # PATCH, PUT
    # Trade status endpoints
    path('trades/<int:trade_id>/status/', get_trade_status, name='api_get_trade_status'),  # GET
    path('trades/<int:trade_id>/status/update/', update_trade_status, name='api_update_trade_status'),  # POST, PUT
    # State summary endpoints (per-seller, per-trade)
    path('summary/state/list/<int:seller_id>/<int:trade_id>/', get_states_for_selection, name='api_states_for_selection'),
    path('summary/state/count/<int:seller_id>/<int:trade_id>/', get_state_count_for_selection, name='api_state_count_for_selection'),
    path('summary/state/count-by/<int:seller_id>/<int:trade_id>/', get_count_by_state, name='api_count_by_state'),
    path('summary/state/sum-current-balance/<int:seller_id>/<int:trade_id>/', get_sum_current_balance_by_state, name='api_sum_current_balance_by_state'),
    path('summary/state/sum-total-debt/<int:seller_id>/<int:trade_id>/', get_sum_total_debt_by_state, name='api_sum_total_debt_by_state'),
    path('summary/state/sum-seller-asis-value/<int:seller_id>/<int:trade_id>/', get_sum_seller_asis_value_by_state, name='api_sum_seller_asis_value_by_state'),
    # Pool summary (single aggregate for top widgets)
    path('summary/pool/<int:seller_id>/<int:trade_id>/', get_pool_summary, name='api_pool_summary'),
    # Center-specific completion summaries (counts by type)
    path('summary/valuations/<int:seller_id>/<int:trade_id>/', get_valuation_completion_summary, name='api_valuation_completion_summary'),
    path('summary/collateral/<int:seller_id>/<int:trade_id>/', get_collateral_completion_summary, name='api_collateral_completion_summary'),
    path('summary/title/<int:seller_id>/<int:trade_id>/', get_title_completion_summary, name='api_title_completion_summary'),
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
    # Static default rate stratification
    path('summary/strat/default-rate/<int:seller_id>/<int:trade_id>/', get_default_rate_stratification, name='api_default_rate_stratification'),
    # Judicial vs Non-Judicial stratification
    path('summary/strat/judicial/<int:seller_id>/<int:trade_id>/', get_judicial_stratification, name='api_judicial_stratification'),
    # Property Type stratification (categorical)
    path('summary/strat/property-type/<int:seller_id>/<int:trade_id>/', get_property_type_stratification, name='api_property_type_stratification'),
    # Occupancy stratification (categorical)
    path('summary/strat/occupancy/<int:seller_id>/<int:trade_id>/', get_occupancy_stratification, name='api_occupancy_stratification'),
    path('summary/strat/delinquency/<int:seller_id>/<int:trade_id>/', get_delinquency_stratification, name='api_delinquency_stratification'),
    # LTV scatter chart data
    path('summary/ltv-scatter/<int:seller_id>/<int:trade_id>/', get_ltv_scatter_data_view, name='api_ltv_scatter_data'),
    # State reference endpoints
    path('state-references/judicial/', get_judicial_states, name='api_judicial_states'),
    # Asset-scoped foreclosure timeline
    path('assets/<int:id>/fc-timeline/', AssetFCTimelineView.as_view(), name='api_asset_fc_timeline'),
    # Import seller tape endpoints
    path('import-seller-tape/', import_seller_tape, name='api_import_seller_tape'),
    path('preview-seller-tape/', preview_seller_tape, name='api_preview_seller_tape'),
    # Test endpoint to verify logging
    path('test-logging/', test_logging, name='api_test_logging'),
]