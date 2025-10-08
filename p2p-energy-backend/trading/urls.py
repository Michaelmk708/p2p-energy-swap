from django.urls import path
from .views import predict, execute_trade, mint_energy, marketplace, buy_listing, account_balance, transactions_history, mpesa_stk_push, mpesa_callback, mpesa_status, iotcentral_ingest, iotcentral_latest, iotcentral_simulate, iotcentral_daily_exported, iotcentral_increment_energy, iotcentral_surplus_state, devices_claim, devices_mine, sim_set_targets, sim_get_targets, iotcentral_telemetry_bridge, iotcentral_last_seen, iotcentral_timeseries

urlpatterns = [
    path('predict/', predict, name='predict'),
    path('execute_trade/', execute_trade, name='execute_trade'),
    path('mint_energy/', mint_energy, name='mint_energy'),
    path('marketplace/', marketplace, name='marketplace'),
    path('buy_listing/', buy_listing, name='buy_listing'),
    path('account/balance/', account_balance, name='account_balance'),
    path('transactions/', transactions_history, name='transactions_history'),
    path('mpesa/stk_push/', mpesa_stk_push, name='mpesa_stk_push'),
    path('mpesa/callback/', mpesa_callback, name='mpesa_callback'),
    path('mpesa/status/', mpesa_status, name='mpesa_status'),
    path('iotcentral/ingest/', iotcentral_ingest, name='iotcentral_ingest'),
    path('iotcentral/latest/', iotcentral_latest, name='iotcentral_latest'),
    path('iotcentral/last_seen/', iotcentral_last_seen, name='iotcentral_last_seen'),
    path('iotcentral/simulate/', iotcentral_simulate, name='iotcentral_simulate'),
    path('iotcentral/daily_exported/', iotcentral_daily_exported, name='iotcentral_daily_exported'),
    path('iotcentral/increment_energy/', iotcentral_increment_energy, name='iotcentral_increment_energy'),
    path('iotcentral/surplus_state/', iotcentral_surplus_state, name='iotcentral_surplus_state'),
    path('iotcentral/telemetry_bridge/', iotcentral_telemetry_bridge, name='iotcentral_telemetry_bridge'),
    path('iotcentral/timeseries/', iotcentral_timeseries, name='iotcentral_timeseries'),
    # Simulation controls (DEBUG only)
    path('sim/set_targets/', sim_set_targets, name='sim_set_targets'),
    path('sim/get_targets/', sim_get_targets, name='sim_get_targets'),
    # Device management (authenticated)
    path('devices/claim/', devices_claim, name='devices_claim'),
    path('devices/mine/', devices_mine, name='devices_mine'),
]
