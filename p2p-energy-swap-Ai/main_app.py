"""
Main API Application for AI Energy Trading System
Integrates all modules and provides RESTful endpoints
"""

import logging
import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import json
import hmac
import hashlib

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Environment variables loaded from .env file")
except ImportError:
    print("python-dotenv not installed, using system environment variables")

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import settings
from src.ai_models.gemini_advisor import gemini_advisor
from src.iot.smart_meter import iot_network
from src.weather.weather_api import weather_service
from src.database.db_manager import db_manager
from src.payments.payment_integrator import get_payment_integrator

# IoT device secrets will be loaded after logger initialization
# ...existing code...

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.FileHandler('energy_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load IoT device secrets (simple JSON for PoC)
IOT_DEVICES_PATH = os.path.join(os.path.dirname(__file__), 'config', 'iot_devices.json')
_IOT_DEVICES = {}
try:
    with open(IOT_DEVICES_PATH, 'r') as f:
        _IOT_DEVICES = json.load(f)
        logger.info(f"Loaded IoT devices config from {IOT_DEVICES_PATH}")
except Exception as e:
    logger.warning(f"Could not load IoT devices config: {e}")

# Flask app initialization
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Mock blockchain and payment integrators (same as before for compatibility)
class BlockchainIntegrator:
    """Mock blockchain integration for Solana smart contracts"""
    
    def __init__(self):
        self.trades = []
        self.wallet_balance = settings.INITIAL_WALLET_BALANCE
        self.energy_price = settings.ENERGY_PRICE_KWH
        # If a blockchain microservice is configured, use it for real actions
        self.bc_service_url = os.getenv('BLOCKCHAIN_SERVICE_URL')
        self.bc_service_api_key = os.getenv('BLOCKCHAIN_SERVICE_API_KEY')
    
    def execute_trade(self, trade_type, amount, price):
        """Execute energy trade on blockchain"""
        try:
            trade_id = len(self.trades) + 1

            # If there's a backend microservice, call it to mint tokens / perform trade
            if self.bc_service_url:
                try:
                    import requests
                    payload = {
                        'household_id': f"HH{trade_id}",
                        'amount_kwh': amount,
                        'reason': f"{trade_type} via AI"
                    }
                    headers = {}
                    if self.bc_service_api_key:
                        headers['x-api-key'] = self.bc_service_api_key

                    resp = requests.post(f"{self.bc_service_url.rstrip('/')}/mint_energy", json=payload, headers=headers, timeout=10)
                    if resp.status_code == 200 or resp.status_code == 201:
                        result = resp.json()
                        tx_hash = result.get('tx_hash') or result.get('tx') or f"EXT_{trade_id}"
                    else:
                        logger.warning(f"Blockchain service returned {resp.status_code}: {resp.text}")
                        tx_hash = f"MOCK_FAIL_{trade_id}"
                except Exception as e:
                    logger.error(f"Error calling blockchain service: {e}")
                    tx_hash = f"MOCK_ERR_{trade_id}"
            else:
                tx_hash = f"SOL_{trade_id}_{int(time.time())}"

            trade = {
                'id': trade_id,
                'type': trade_type,
                'amount': amount,
                'price': price,
                'total_value': amount * price,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending',
                'tx_hash': tx_hash
            }

            # Simulate blockchain processing time
            time.sleep(0.1)

            # Update wallet balance
            if trade_type == 'SELL':
                self.wallet_balance += (amount * price)
            else:  # BUY
                self.wallet_balance -= (amount * price)

            trade['status'] = 'confirmed'
            trade['wallet_balance'] = round(self.wallet_balance, 2)
            self.trades.append(trade)

            logger.info(f"Blockchain trade executed: {trade}")
            return trade
            
        except Exception as e:
            logger.error(f"Blockchain execution error: {e}")
            raise

# Enhanced M-Pesa Integrator with Real Daraja API + Mock Fallback
class EnhancedMpesaIntegrator:
    """Enhanced M-Pesa payment integration with real Daraja API and mock fallback"""
    
    def __init__(self):
        self.transactions = []
        self.success_rate = settings.MPESA_SUCCESS_RATE
        # If DEMO_MODE is enabled or credentials are missing, use mock
        self.use_real_api = bool(settings.MPESA_CONSUMER_KEY and settings.MPESA_CONSUMER_SECRET) and not settings.DEMO_MODE
        
        if self.use_real_api:
            try:
                self.payment_integrator = get_payment_integrator(
                    provider='mpesa',
                    environment=settings.MPESA_ENVIRONMENT
                )
                logger.info(f"Real M-Pesa Daraja API initialized ({settings.MPESA_ENVIRONMENT})")
            except Exception as e:
                logger.warning(f"Failed to initialize real M-Pesa API, falling back to mock: {e}")
                self.use_real_api = False
        else:
            logger.info("M-Pesa credentials not configured, using mock integration")
    
    def process_payment(self, phone, amount, trade_id, **kwargs):
        """Process M-Pesa payment using real API or mock fallback"""
        try:
            if self.use_real_api:
                return self._process_real_payment(phone, amount, trade_id, **kwargs)
            else:
                return self._process_mock_payment(phone, amount, trade_id)
                
        except Exception as e:
            logger.error(f"Payment processing error, falling back to mock: {e}")
            return self._process_mock_payment(phone, amount, trade_id)
    
    def _process_real_payment(self, phone, amount, trade_id, **kwargs):
        """Process payment using real M-Pesa Daraja API"""
        try:
            # Extract additional parameters for energy trading
            amount_kwh = kwargs.get('amount_kwh', amount / 10.0)  # Default assumption: 10 KES per kWh
            price_per_kwh = kwargs.get('price_per_kwh', amount / amount_kwh if amount_kwh > 0 else 10.0)
            seller_phone = kwargs.get('seller_phone', '254700000000')  # Default seller
            
            # Initiate STK Push
            stk_result = self.payment_integrator.process_energy_payment(
                trade_id=str(trade_id),
                buyer_phone=phone,
                seller_phone=seller_phone,
                amount_kwh=amount_kwh,
                price_per_kwh=price_per_kwh,
                callback_url=settings.PAYMENT_CALLBACK_URL
            )
            
            if stk_result.get('success'):
                transaction = {
                    'tx_id': stk_result.get('checkout_request_id', f"STK_{int(time.time())}"),
                    'phone': phone,
                    'amount': round(amount, 2),
                    'trade_id': trade_id,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'pending_stk_push',
                    'currency': 'KES',
                    'payment_method': 'mpesa_daraja_stk',
                    'stk_push_data': {
                        'checkout_request_id': stk_result.get('checkout_request_id'),
                        'merchant_request_id': stk_result.get('merchant_request_id'),
                        'customer_message': stk_result.get('customer_message'),
                        'amount_kwh': amount_kwh,
                        'price_per_kwh': price_per_kwh
                    }
                }
                
                self.transactions.append(transaction)
                logger.info(f"STK Push initiated successfully for trade {trade_id}: {stk_result.get('customer_message')}")
                return transaction
            else:
                # STK Push failed, fallback to mock
                logger.warning(f"STK Push failed: {stk_result.get('error')}, falling back to mock")
                return self._process_mock_payment(phone, amount, trade_id)
                
        except Exception as e:
            logger.error(f"Real M-Pesa processing error: {e}")
            raise
    
    def _process_mock_payment(self, phone, amount, trade_id):
        """Process mock payment (original logic)"""
        try:
            # Deterministic mock txn id in demo mode
            if settings.DEMO_MODE:
                tx_id = f"DEMO_MPESA_{trade_id}"
                status = 'completed'
            else:
                tx_id = f"MOCK_MPESA{int(time.time())}{len(self.transactions):03d}"
                # Simulate processing time
                time.sleep(0.2)
                # Simulate occasional failures
                import numpy as np
                success = np.random.random() < self.success_rate
                status = 'completed' if success else 'failed'

            transaction = {
                'tx_id': tx_id,
                'phone': phone,
                'amount': round(amount, 2),
                'trade_id': trade_id,
                'timestamp': datetime.now().isoformat(),
                'status': status,
                'currency': 'KES',
                'payment_method': 'mpesa_mock'
            }
            
            self.transactions.append(transaction)
            logger.info(f"Mock M-Pesa payment processed: {transaction}")
            return transaction
            
        except Exception as e:
            logger.error(f"Mock M-Pesa processing error: {e}")
            raise
    
    def query_payment_status(self, transaction_id):
        """Query payment status for STK Push transactions"""
        if self.use_real_api and hasattr(self.payment_integrator, 'query_transaction_status'):
            try:
                return self.payment_integrator.query_transaction_status(transaction_id)
            except Exception as e:
                logger.error(f"STK status query error: {e}")
                return {'success': False, 'error': str(e)}
        
        # Fallback: search local transactions
        for tx in self.transactions:
            if tx.get('tx_id') == transaction_id:
                return {'success': True, 'transaction': tx}
        
        return {'success': False, 'error': 'Transaction not found'}

# Initialize components
blockchain = BlockchainIntegrator()
mpesa = EnhancedMpesaIntegrator()

# API Routes
@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        'message': 'Enhanced AI Energy Trading System API',
        'version': '2.0.0',
        'status': 'active',
        'features': [
            'Gemini AI-powered trading recommendations',
            'ESP32 smart meter simulation',
            'Real weather API integration',
            'Comprehensive analytics',
            'Multi-household support'
        ],
        'endpoints': [
            'GET / - API information',
            'GET /api/predict - Get AI trading recommendation',
            'GET /api/forecast - Get forecast predictions',  
            'GET /api/history - Get historical data',
            'GET /api/analytics - Get comprehensive analytics',
            'POST /api/execute_trade - Execute energy trade',
            'GET /api/households - Get IoT network status',
            'GET /api/alerts - Get active weather alerts',
            'GET /api/status - System status'
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/predict', methods=['GET'])
def get_prediction():
    """Get current BUY/SELL prediction with Gemini AI analysis"""
    try:
        # Get query parameters
        household_id = request.args.get('household', 'HH001_Nairobi_Central')
        # Optional location hints from client
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        city = request.args.get('city')
        coords = None
        try:
            if lat is not None and lon is not None:
                coords = (float(lat), float(lon))
        except Exception:
            coords = None
        
        # Get current weather (use client-provided coords/city when available)
        weather_data = weather_service.get_current_weather(city=city, coordinates=coords)
        
        # Get live IoT data parameters from request (real-time Wokwi data)
        live_avg_production = request.args.get('live_avg_production')
        live_avg_consumption = request.args.get('live_avg_consumption')
        live_total_surplus = request.args.get('live_total_surplus')
        live_peak_production = request.args.get('live_peak_production')
        
        # Prioritize live real-time data if provided (from Wokwi)
        if live_avg_production is not None and live_avg_consumption is not None:
            try:
                production_kw = float(live_avg_production)
                consumption_kw = float(live_avg_consumption)
                surplus_kw = production_kw - consumption_kw
                
                # Use real-time values for AI prediction
                iot_data = {
                    'solar_generation_kwh': production_kw,  # Current kW production
                    'consumption_kwh': consumption_kw,      # Current kW consumption  
                    'surplus_deficit_kwh': surplus_kw,      # Current kW surplus/deficit
                    'panel_voltage': 240,
                    'panel_current': production_kw * 4.17,  # Estimate current from power
                    'battery_level': 95
                }
                logger.info(f"Using live IoT data: PV={production_kw}kW, Load={consumption_kw}kW, Net={surplus_kw}kW")
            except (ValueError, TypeError):
                logger.warning("Invalid live data parameters, falling back to simulation")
                live_avg_production = None  # Fall through to simulation
        
        # Fallback to simulated data if no live data provided
        if live_avg_production is None:
            if household_id in iot_network.smart_meters:
                meter = iot_network.smart_meters[household_id]
                iot_data = meter.get_sensor_reading(weather_data)['measurements']
            else:
                # Use network average if household not found
                network_data = iot_network.get_network_data(weather_data)
                iot_data = {
                    'solar_generation_kwh': network_data['network_summary']['total_generation'] / max(1, network_data['total_households']),
                    'consumption_kwh': network_data['network_summary']['total_consumption'] / max(1, network_data['total_households']),
                    'surplus_deficit_kwh': network_data['network_summary']['total_surplus_deficit'] / max(1, network_data['total_households']),
                    'panel_voltage': 240,
                    'panel_current': 13.0,
                    'battery_level': 95
                }
        
        # Get historical data for better AI analysis
        historical_data = db_manager.get_recent_energy_data(hours=48, household_id=household_id)
        
        # Get enhanced prediction from Gemini AI
        prediction = gemini_advisor.get_trading_recommendation(
            weather_data, iot_data, historical_data
        )
        
        # Store in database
        db_manager.store_energy_data(weather_data, iot_data, prediction, household_id)
        
        # Prepare enhanced response
        response = {
            'prediction': prediction,
            'weather': weather_data,
            'iot_data': iot_data,
            'household_id': household_id,
            'historical_context': {
                'data_points': len(historical_data),
                'avg_surplus_last_24h': sum([d.get('surplus_deficit', 0) for d in historical_data[-24:]]) / max(1, len(historical_data[-24:]))
            },
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({
            'status': 'error', 
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/forecast', methods=['GET'])
def get_forecast_predictions():
    """Get forecast predictions for next hours with enhanced analysis"""
    try:
        hours = min(int(request.args.get('hours', 24)), 48)
        household_id = request.args.get('household', 'HH001_Nairobi_Central')
        
        # Get weather forecasts
        forecasts = weather_service.get_forecast(hours=hours)
        
        predictions = []
        for forecast in forecasts:
            # Generate IoT data for forecast conditions
            if household_id in iot_network.smart_meters:
                meter = iot_network.smart_meters[household_id]
                iot_data = meter.get_sensor_reading(forecast)['measurements']
            else:
                # Simulate average household data
                iot_data = {
                    'solar_generation_kwh': 3.0,
                    'consumption_kwh': 2.5,
                    'surplus_deficit_kwh': 0.5,
                    'panel_voltage': 240,
                    'panel_current': 13.0,
                    'battery_level': 95
                }
            
            # Get AI prediction for this forecast
            prediction = gemini_advisor.get_trading_recommendation(forecast, iot_data)
            
            predictions.append({
                'timestamp': forecast['timestamp'],
                'weather': forecast,
                'iot_data': iot_data,
                'prediction': prediction
            })
        
        return jsonify({
            'forecasts': predictions,
            'household_id': household_id,
            'count': len(predictions),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get historical data and predictions"""
    try:
        hours = min(int(request.args.get('hours', 24)), 168)  # Max 1 week
        household_id = request.args.get('household')
        
        data = db_manager.get_recent_energy_data(hours, household_id)
        
        return jsonify({
            'history': data,
            'household_id': household_id,
            'count': len(data),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get comprehensive energy analytics"""
    try:
        days = min(int(request.args.get('days', 7)), 30)  # Max 30 days
        
        analytics = db_manager.get_energy_analytics(days)
        
        # Add trade analytics
        trades = db_manager.get_trade_history(days * 24)
        if trades:
            trade_analytics = {
                'total_trades': len(trades),
                'sell_trades': len([t for t in trades if t['trade_type'] == 'SELL']),
                'buy_trades': len([t for t in trades if t['trade_type'] == 'BUY']),
                'total_volume': sum([t['amount'] for t in trades]),
                'total_value': sum([t['total_value'] for t in trades]),
                'avg_trade_size': sum([t['amount'] for t in trades]) / len(trades),
                'successful_trades': len([t for t in trades if t['status'] == 'confirmed'])
            }
            analytics['trade_stats'] = trade_analytics
        
        return jsonify(analytics)
        
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/households', methods=['GET'])
def get_households():
    """Get IoT network status"""
    try:
        # Get current weather for network data
        weather_data = weather_service.get_current_weather()
        
        # Get comprehensive network data
        network_data = iot_network.get_network_data(weather_data)
        
        return jsonify({
            'network_data': network_data,
            'households': list(iot_network.smart_meters.keys()),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Households error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get active weather alerts"""
    try:
        # Get alerts from database
        active_alerts = db_manager.get_active_alerts()
        
        # Get weather alerts from weather service
        weather_alerts = weather_service.get_weather_alerts()
        
        # Store new weather alerts in database
        for alert in weather_alerts:
            db_manager.store_weather_alert(
                alert['type'],
                alert['severity'],
                alert['message'],
                alert.get('impact', ''),
                24  # 24 hour expiry
            )
        
        all_alerts = active_alerts + weather_alerts
        
        return jsonify({
            'alerts': all_alerts,
            'count': len(all_alerts),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Alerts error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/execute_trade', methods=['POST'])
def execute_trade():
    """Execute energy trade with enhanced validation"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['type', 'amount', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing field: {field}'}), 400
        
        trade_type = data['type'].upper()
        amount = float(data['amount'])
        price = float(data['price'])
        phone = data.get('phone', '+254700000000')
        household_id = data.get('household', 'default')
        
        # Validate trade type
        if trade_type not in ['BUY', 'SELL']:
            return jsonify({'status': 'error', 'message': 'Invalid trade type'}), 400
        
        # Validate amounts
        if amount <= 0 or price <= 0:
            return jsonify({'status': 'error', 'message': 'Amount and price must be positive'}), 400
        
        # Execute blockchain trade
        trade = blockchain.execute_trade(trade_type, amount, price)
        
        # Process M-Pesa payment with energy trading details
        payment_kwargs = {
            'amount_kwh': amount,
            'price_per_kwh': price,
            'seller_phone': data.get('seller_phone', '+254700000000'),  # Default seller phone
            'buyer_phone': phone
        }
        
        payment = mpesa.process_payment(phone, amount * price, trade['id'], **payment_kwargs)
        
        # Store trade in database
        trade_data = {
            **trade,
            'payment_method': 'mpesa',
            'payment_tx_id': payment['tx_id'],
            'payment_status': payment['status']
        }
        db_manager.store_trade(trade_data, household_id)
        
        response = {
            'trade': trade,
            'payment': payment,
            'household_id': household_id,
            'total_value': round(amount * price, 2),
            'status': 'success'
        }
        
        return jsonify(response)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'status': 'error', 'message': 'Invalid number format'}), 400
    except Exception as e:
        logger.error(f"Trade execution error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get comprehensive system status"""
    try:
        # Test components
        weather_status = 'active'
        try:
            weather_service.get_current_weather()
        except:
            weather_status = 'error'
        
        db_status = 'active'
        try:
            db_manager.get_recent_energy_data(1)
        except:
            db_status = 'error'
        
        gemini_status = 'active' if gemini_advisor.model else 'backup_only'
        
        # Get API key validation
        api_keys_status = settings.validate_required_keys()
        
        return jsonify({
            'status': 'active',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'components': {
                'weather_api': weather_status,
                'iot_network': 'active',
                'gemini_ai': gemini_status,
                'database': db_status,
                'blockchain': 'active',
                'mpesa': 'active'
            },
            'api_keys': api_keys_status,
            'network_stats': {
                'households': len(iot_network.smart_meters),
                'wallet_balance': blockchain.wallet_balance,
                'total_trades': len(blockchain.trades),
                'total_payments': len(mpesa.transactions)
            }
        })
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

# M-Pesa Callback Endpoints
@app.route('/api/payment/callback', methods=['POST'])
def mpesa_payment_callback():
    """Handle M-Pesa payment confirmation callbacks"""
    try:
        callback_data = request.get_json()
        logger.info(f"Received M-Pesa callback: {callback_data}")
        
        if mpesa.use_real_api:
            # Process real M-Pesa callback
            result = mpesa.payment_integrator.confirm_payment(callback_data)
            
            if result.get('success'):
                trade_id = result.get('trade_id')
                payment_status = result.get('payment_status')
                
                logger.info(f"Payment {payment_status} for trade {trade_id}")
                
                # Update trade status in database if needed
                # db_manager.update_trade_status(trade_id, payment_status)
                
                return jsonify({
                    'ResultCode': 0,
                    'ResultDesc': 'Callback processed successfully',
                    'trade_id': trade_id,
                    'payment_status': payment_status
                })
            else:
                logger.error(f"Callback processing failed: {result.get('error')}")
                return jsonify({
                    'ResultCode': 1,
                    'ResultDesc': 'Callback processing failed'
                }), 400
        else:
            # Mock callback processing
            logger.info("Mock callback processing (real M-Pesa not configured)")
            return jsonify({
                'ResultCode': 0,
                'ResultDesc': 'Mock callback processed'
            })
            
    except Exception as e:
        logger.error(f"Callback processing error: {e}")
        return jsonify({
            'ResultCode': 1,
            'ResultDesc': f'Error processing callback: {str(e)}'
        }), 500

@app.route('/api/payment/status/<transaction_id>', methods=['GET'])
def get_payment_status(transaction_id):
    """Get payment status for a transaction"""
    try:
        status = mpesa.query_payment_status(transaction_id)
        
        if status.get('success'):
            return jsonify({
                'status': 'success',
                'transaction': status.get('transaction', {}),
                'payment_status': status.get('transaction', {}).get('status', 'unknown')
            })
        else:
            return jsonify({
                'status': 'error',
                'message': status.get('error', 'Transaction not found')
            }), 404
            
    except Exception as e:
        logger.error(f"Payment status query error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/stk/status/<checkout_request_id>', methods=['GET'])
def query_stk_status(checkout_request_id):
    """Query STK Push payment status"""
    try:
        if mpesa.use_real_api:
            result = mpesa.payment_integrator.query_transaction_status(checkout_request_id)
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': 'Real M-Pesa API not configured'
            }), 400
            
    except Exception as e:
        logger.error(f"STK status query error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def initialize_system():
    """Initialize the enhanced system on startup"""
    try:
        logger.info("Starting Enhanced AI Energy Trading System v2.0...")
        
        # Test database connection
        logger.info("Testing database connection...")
        db_manager.get_recent_energy_data(1)
        
        # Test weather API
        logger.info("Testing weather API...")
        weather_service.get_current_weather()
        
        # Initialize Gemini AI
        logger.info("Initializing Gemini AI advisor...")
        if gemini_advisor.model:
            logger.info("Gemini AI ready")
        else:
            logger.info("Using backup ML model (Gemini unavailable)")
        
        # Test IoT network
        logger.info("Testing IoT network...")
        weather_data = weather_service.get_current_weather()
        iot_network.get_network_data(weather_data)
        logger.info(f"IoT network ready ({len(iot_network.smart_meters)} households)")
        
        logger.info("System initialization complete!")
        logger.info(f"API server ready at http://localhost:{settings.API_PORT}")
        logger.info("Enhanced analytics and Gemini AI available")
        
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        logger.info("System will continue with limited functionality")


def verify_device_signature(device_id: str, body: bytes, signature: str) -> bool:
    """Verify HMAC-SHA256 signature for device payload"""
    try:
        device = _IOT_DEVICES.get(device_id)
        if not device:
            logger.warning(f"Unknown device id: {device_id}")
            return False

        secret = device.get('shared_secret')
        if not secret:
            logger.warning(f"No shared secret for device {device_id}")
            return False

        computed = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, signature)
    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        return False


@app.route('/api/iot/data', methods=['POST'])
def ingest_iot_data():
    """Secure ingestion endpoint for IoT devices (HMAC-SHA256)"""
    try:
        raw = request.get_data()
        device_id = request.headers.get('X-Device-Id') or request.json.get('deviceId') if request.is_json else None
        signature = request.headers.get('X-Signature')

        if not device_id or not signature:
            return jsonify({'status': 'error', 'message': 'Missing device id or signature'}), 400

        # Verify HMAC signature
        if not verify_device_signature(device_id, raw, signature):
            return jsonify({'status': 'error', 'message': 'Invalid signature or unknown device'}), 401

        payload = request.get_json()
        measurements = payload.get('measurements', {})
        timestamp = payload.get('timestamp', datetime.now().isoformat())

        # Build weather placeholder (can be enriched later)
        weather_data = weather_service.get_current_weather() or {}

        # Build iot_data expected by db_manager
        iot_data = {
            'solar_generation_kwh': measurements.get('solar_generation_kwh') or measurements.get('solar_generation'),
            'consumption_kwh': measurements.get('consumption_kwh') or measurements.get('consumption'),
            'surplus_deficit_kwh': measurements.get('surplus_deficit_kwh') or measurements.get('surplus_deficit'),
            'panel_voltage': measurements.get('panel_voltage'),
            'panel_current': measurements.get('panel_current'),
            'battery_level': measurements.get('battery_level'),
            'device_status': {'online': True}
        }

        # Trigger AI prediction asynchronously to avoid blocking device
        def async_predict_and_store():
            try:
                historical = db_manager.get_recent_energy_data(hours=48, household_id=device_id)
                prediction = gemini_advisor.get_trading_recommendation(weather_data, iot_data, historical)
                db_manager.store_energy_data(weather_data, iot_data, prediction, household_id=device_id)
                logger.info(f"Stored IoT data and prediction for device {device_id}")
            except Exception as e:
                logger.error(f"Async prediction/store error for {device_id}: {e}")

        threading.Thread(target=async_predict_and_store, daemon=True).start()

        return jsonify({'status': 'success', 'message': 'Data ingested'}), 201

    except Exception as e:
        logger.error(f"IoT ingestion error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Initialize system
    initialize_system()
    
    # Start Flask API
    app.run(
        debug=settings.DEBUG_MODE,
        host=settings.API_HOST,
        port=settings.API_PORT,
        threaded=True
    )