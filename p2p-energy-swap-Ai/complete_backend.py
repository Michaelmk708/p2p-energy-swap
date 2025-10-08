# AI Energy Trading System - Complete Backend
# File: energy_trading_system.py

import pandas as pd
import numpy as np
import requests
import json
import os
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IoTSimulator:
    """Simulates IoT sensor data for solar generation and consumption"""
    
    def __init__(self):
        self.base_generation = 5.0  # kWh base generation
        self.base_consumption = 3.0  # kWh base consumption
        
    def generate_solar_data(self, temperature, sunlight_hours, cloud_percentage):
        """Generate realistic solar generation data based on weather"""
        try:
            # Solar generation increases with temperature and sunlight, decreases with clouds
            temp_factor = min(temperature / 25, 1.5)  # Optimal around 25°C
            sunlight_factor = sunlight_hours / 12
            cloud_factor = (100 - cloud_percentage) / 100
            
            generation_factor = temp_factor * sunlight_factor * cloud_factor
            generation = max(0, self.base_generation * generation_factor * np.random.uniform(0.8, 1.2))
            
            # Consumption varies throughout the day
            hour = datetime.now().hour
            if 6 <= hour <= 9 or 17 <= hour <= 22:  # Peak consumption times
                consumption = self.base_consumption * np.random.uniform(1.2, 1.8)
            else:
                consumption = self.base_consumption * np.random.uniform(0.6, 1.0)
                
            surplus_deficit = generation - consumption
            
            return {
                'timestamp': datetime.now().isoformat(),
                'solar_generation': round(generation, 2),
                'consumption': round(consumption, 2),
                'surplus_deficit': round(surplus_deficit, 2),
                'temperature': temperature,
                'sunlight_hours': sunlight_hours,
                'cloud_percentage': cloud_percentage
            }
        except Exception as e:
            logger.error(f"Error in generate_solar_data: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'solar_generation': 3.0,
                'consumption': 2.5,
                'surplus_deficit': 0.5,
                'temperature': temperature,
                'sunlight_hours': sunlight_hours,
                'cloud_percentage': cloud_percentage
            }

class WeatherAPI:
    """Handles weather data fetching"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY', 'demo_key')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_current_weather(self, city="Nairobi"):
        """Fetch current weather data"""
        if self.api_key == "demo_key":
            # Return simulated weather data for demo
            return self._get_demo_weather()
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'sunlight_hours': max(0, 12 - (data['clouds']['all'] / 100 * 6)),
                'cloud_percentage': data['clouds']['all'],
                'weather_desc': data['weather'][0]['description']
            }
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return self._get_demo_weather()
    
    def _get_demo_weather(self):
        """Generate demo weather data"""
        hour = datetime.now().hour
        # Simulate daily weather patterns
        base_temp = 25 + 5 * np.sin((hour - 6) * np.pi / 12)  # Peak at noon
        temp_variation = np.random.uniform(-3, 3)
        
        return {
            'temperature': max(15, min(40, base_temp + temp_variation)),
            'sunlight_hours': max(0, 12 - abs(hour - 12) / 2) if 6 <= hour <= 18 else 0,
            'cloud_percentage': np.random.uniform(10, 70),
            'weather_desc': 'partly cloudy'
        }

    def get_forecast(self, city="Nairobi", hours=24):
        """Get weather forecast for next few hours"""
        if self.api_key == "demo_key":
            return self._get_demo_forecast(hours)
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': min(hours, 40)  # API limit
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecasts = []
            for item in data['list'][:hours]:
                forecasts.append({
                    'timestamp': datetime.fromtimestamp(item['dt']).isoformat(),
                    'temperature': item['main']['temp'],
                    'sunlight_hours': max(0, 12 - (item['clouds']['all'] / 100 * 6)),
                    'cloud_percentage': item['clouds']['all']
                })
            return forecasts
        except Exception as e:
            logger.error(f"Forecast API error: {e}")
            return self._get_demo_forecast(hours)
    
    def _get_demo_forecast(self, hours):
        """Generate demo forecast data"""
        forecasts = []
        for i in range(hours):
            future_time = datetime.now() + timedelta(hours=i)
            hour = future_time.hour
            
            # Simulate daily temperature cycle
            base_temp = 25 + 5 * np.sin((hour - 6) * np.pi / 12)
            temp_variation = np.random.uniform(-2, 2)
            
            forecasts.append({
                'timestamp': future_time.isoformat(),
                'temperature': max(15, min(40, base_temp + temp_variation)),
                'sunlight_hours': max(0, 12 - abs(hour - 12) / 2) if 6 <= hour <= 18 else 0,
                'cloud_percentage': np.random.uniform(15, 65)
            })
        return forecasts

class EnergyTradingAI:
    """Main AI model for energy trading decisions"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = 'energy_trading_model.pkl'
        self.scaler_path = 'energy_scaler.pkl'
        
    def generate_training_data(self, n_samples=2000):
        """Generate synthetic training data"""
        logger.info(f"Generating {n_samples} training samples...")
        
        data = []
        
        for _ in range(n_samples):
            # Generate random weather conditions with realistic patterns
            temp = np.random.normal(27, 5)  # Nairobi average temp
            temp = max(15, min(40, temp))  # Reasonable bounds
            
            sunlight = max(0, np.random.normal(8, 2))  # Hours
            clouds = max(0, min(100, np.random.normal(40, 20)))  # Percentage
            
            # Simulate IoT data
            surplus_deficit = np.random.uniform(-3, 4)  # kWh
            hour = np.random.randint(0, 24)
            
            # Create intelligent labels
            # SELL conditions: surplus > 1 kWh AND (low clouds OR high sunlight)
            # BUY conditions: deficit OR poor weather
            
            sell_conditions = (
                surplus_deficit > 1.0 and
                (clouds < 50 or sunlight > 7) and
                6 <= hour <= 18  # Daylight hours
            )
            
            buy_conditions = (
                surplus_deficit < -0.5 or
                (clouds > 70 and sunlight < 5) or
                hour < 6 or hour > 20  # Night hours
            )
            
            if sell_conditions:
                label = 1  # SELL
            elif buy_conditions:
                label = 0  # BUY
            else:
                # Neutral conditions - slight preference based on surplus
                label = 1 if surplus_deficit > 0 else 0
                
            data.append({
                'temperature': temp,
                'sunlight_hours': sunlight,
                'cloud_percentage': clouds,
                'surplus_deficit': surplus_deficit,
                'hour_of_day': hour,
                'label': label
            })
            
        df = pd.DataFrame(data)
        logger.info(f"Generated data - SELL: {sum(df['label'])}, BUY: {len(df) - sum(df['label'])}")
        return df
    
    def train_model(self):
        """Train the AI model"""
        logger.info("Training AI model...")
        
        try:
            # Generate training data
            df = self.generate_training_data(3000)
            
            # Prepare features
            features = ['temperature', 'sunlight_hours', 'cloud_percentage', 
                       'surplus_deficit', 'hour_of_day']
            X = df[features]
            y = df['label']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest model with optimized parameters
            self.model = RandomForestClassifier(
                n_estimators=150,
                random_state=42,
                max_depth=12,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight='balanced'
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"Model trained successfully!")
            logger.info(f"Accuracy: {accuracy:.3f}")
            logger.info(f"Classification Report:\n{classification_report(y_test, y_pred, target_names=['BUY', 'SELL'])}")
            
            # Feature importance
            importance = self.model.feature_importances_
            for i, feature in enumerate(features):
                logger.info(f"{feature}: {importance[i]:.3f}")
            
            self.is_trained = True
            
            # Save model
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            logger.info("Model saved successfully")
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            raise
        
    def load_model(self):
        """Load pre-trained model"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.is_trained = True
                logger.info("Pre-trained model loaded successfully")
            else:
                logger.info("No saved model found, training new model...")
                self.train_model()
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.info("Training new model...")
            self.train_model()
    
    def predict(self, weather_data, iot_data):
        """Make BUY/SELL prediction"""
        if not self.is_trained:
            self.load_model()
            
        try:
            # Prepare features
            features = np.array([[
                weather_data['temperature'],
                weather_data['sunlight_hours'],
                weather_data['cloud_percentage'],
                iot_data['surplus_deficit'],
                datetime.now().hour
            ]])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            decision = 'SELL' if prediction == 1 else 'BUY'
            confidence = max(probabilities)
            
            return {
                'decision': decision,
                'confidence': round(confidence, 3),
                'timestamp': datetime.now().isoformat(),
                'reasoning': self._get_reasoning(weather_data, iot_data, decision),
                'sell_probability': round(probabilities[1], 3),
                'buy_probability': round(probabilities[0], 3)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            # Fallback prediction
            decision = 'SELL' if iot_data['surplus_deficit'] > 0 else 'BUY'
            return {
                'decision': decision,
                'confidence': 0.5,
                'timestamp': datetime.now().isoformat(),
                'reasoning': f"Fallback decision based on surplus/deficit",
                'sell_probability': 0.5,
                'buy_probability': 0.5
            }
    
    def _get_reasoning(self, weather_data, iot_data, decision):
        """Provide reasoning for the decision"""
        reasons = []
        
        # Energy surplus/deficit reasoning
        surplus = iot_data['surplus_deficit']
        if surplus > 1.5:
            reasons.append(f"High energy surplus: {surplus:.1f} kWh")
        elif surplus > 0:
            reasons.append(f"Energy surplus: {surplus:.1f} kWh")
        elif surplus < -1:
            reasons.append(f"High energy deficit: {abs(surplus):.1f} kWh")
        elif surplus < 0:
            reasons.append(f"Energy deficit: {abs(surplus):.1f} kWh")
            
        # Weather reasoning
        clouds = weather_data['cloud_percentage']
        sunlight = weather_data['sunlight_hours']
        
        if clouds < 30:
            reasons.append("Clear skies favor solar generation")
        elif clouds > 70:
            reasons.append("Heavy clouds may reduce generation")
            
        if sunlight > 8:
            reasons.append("Excellent sunlight hours expected")
        elif sunlight > 6:
            reasons.append("Good sunlight hours expected")
        elif sunlight < 4:
            reasons.append("Limited sunlight hours")
            
        # Time-based reasoning
        hour = datetime.now().hour
        if 10 <= hour <= 16:
            reasons.append("Peak solar generation hours")
        elif hour < 6 or hour > 20:
            reasons.append("Off-peak solar hours")
            
        return "; ".join(reasons) if reasons else f"Standard {decision} conditions"

class DatabaseManager:
    """Handles data storage and retrieval"""
    
    def __init__(self, db_path='energy_trading.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS energy_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    temperature REAL,
                    sunlight_hours REAL,
                    cloud_percentage REAL,
                    solar_generation REAL,
                    consumption REAL,
                    surplus_deficit REAL,
                    ai_decision TEXT,
                    confidence REAL,
                    reasoning TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    trade_type TEXT,
                    amount REAL,
                    price REAL,
                    total_value REAL,
                    status TEXT,
                    tx_hash TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_energy_timestamp ON energy_data(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def store_prediction(self, weather_data, iot_data, prediction):
        """Store prediction data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO energy_data 
                (timestamp, temperature, sunlight_hours, cloud_percentage,
                 solar_generation, consumption, surplus_deficit,
                 ai_decision, confidence, reasoning)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction['timestamp'],
                weather_data['temperature'],
                weather_data['sunlight_hours'],
                weather_data['cloud_percentage'],
                iot_data['solar_generation'],
                iot_data['consumption'],
                iot_data['surplus_deficit'],
                prediction['decision'],
                prediction['confidence'],
                prediction['reasoning']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing prediction: {e}")
    
    def get_recent_data(self, hours=24):
        """Get recent energy data"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT * FROM energy_data 
                WHERE datetime(timestamp) > datetime('now', '-{} hours')
                ORDER BY timestamp DESC
                LIMIT 100
            '''.format(hours)
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error retrieving recent data: {e}")
            return []
    
    def store_trade(self, trade_data):
        """Store trade execution data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trades (timestamp, trade_type, amount, price, total_value, status, tx_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data['timestamp'],
                trade_data['type'],
                trade_data['amount'],
                trade_data['price'],
                trade_data['amount'] * trade_data['price'],
                trade_data['status'],
                trade_data.get('tx_hash', '')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing trade: {e}")

# Blockchain Integration Mock (Ready for Solana)
class BlockchainIntegrator:
    """Mock blockchain integration for Solana smart contracts"""
    
    def __init__(self):
        self.trades = []
        self.wallet_balance = 100.0  # Mock SOL balance
        self.energy_price = 0.12  # KES per kWh
    
    def execute_trade(self, trade_type, amount, price):
        """Execute energy trade on blockchain"""
        try:
            trade_id = len(self.trades) + 1
            
            trade = {
                'id': trade_id,
                'type': trade_type,
                'amount': amount,
                'price': price,
                'total_value': amount * price,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending',
                'tx_hash': f"SOL_{trade_id}_{int(time.time())}"
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

# M-Pesa Integration Mock
class MpesaIntegrator:
    """Mock M-Pesa payment integration"""
    
    def __init__(self):
        self.transactions = []
        self.success_rate = 0.95  # 95% success rate
    
    def process_payment(self, phone, amount, trade_id):
        """Process M-Pesa payment"""
        try:
            tx_id = f"MPESA{int(time.time())}{len(self.transactions):03d}"
            
            # Simulate processing time
            time.sleep(0.2)
            
            # Simulate occasional failures
            success = np.random.random() < self.success_rate
            
            transaction = {
                'tx_id': tx_id,
                'phone': phone,
                'amount': round(amount, 2),
                'trade_id': trade_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'completed' if success else 'failed',
                'currency': 'KES'
            }
            
            self.transactions.append(transaction)
            logger.info(f"M-Pesa payment processed: {transaction}")
            return transaction
            
        except Exception as e:
            logger.error(f"M-Pesa processing error: {e}")
            raise

# Flask API Setup
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize components
weather_api = WeatherAPI()
iot_simulator = IoTSimulator()
ai_model = EnergyTradingAI()
db_manager = DatabaseManager()
blockchain = BlockchainIntegrator()
mpesa = MpesaIntegrator()

@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        'message': 'AI Energy Trading System API',
        'version': '1.0.0',
        'status': 'active',
        'endpoints': [
            '/api/predict - Get current prediction',
            '/api/forecast - Get forecast predictions',
            '/api/history - Get historical data',
            '/api/execute_trade - Execute trade',
            '/api/status - System status'
        ]
    })

@app.route('/api/predict', methods=['GET'])
def get_prediction():
    """Get current BUY/SELL prediction"""
    try:
        # Get current weather
        weather_data = weather_api.get_current_weather()
        
        # Get IoT data
        iot_data = iot_simulator.generate_solar_data(
            weather_data['temperature'],
            weather_data['sunlight_hours'],
            weather_data['cloud_percentage']
        )
        
        # Make prediction
        prediction = ai_model.predict(weather_data, iot_data)
        
        # Store in database
        db_manager.store_prediction(weather_data, iot_data, prediction)
        
        # Prepare response
        response = {
            'prediction': prediction,
            'weather': weather_data,
            'iot_data': iot_data,
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
    """Get forecast predictions for next hours"""
    try:
        hours = min(int(request.args.get('hours', 24)), 48)  # Max 48 hours
        forecasts = weather_api.get_forecast(hours=hours)
        
        predictions = []
        for forecast in forecasts:
            iot_data = iot_simulator.generate_solar_data(
                forecast['temperature'],
                forecast['sunlight_hours'],
                forecast['cloud_percentage']
            )
            
            prediction = ai_model.predict(forecast, iot_data)
            
            predictions.append({
                'timestamp': forecast['timestamp'],
                'weather': forecast,
                'iot_data': iot_data,
                'prediction': prediction
            })
        
        return jsonify({
            'forecasts': predictions,
            'count': len(predictions),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get historical predictions"""
    try:
        hours = min(int(request.args.get('hours', 24)), 168)  # Max 1 week
        data = db_manager.get_recent_data(hours)
        
        return jsonify({
            'history': data,
            'count': len(data),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/execute_trade', methods=['POST'])
def execute_trade():
    """Execute energy trade with blockchain and payment"""
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
        
        # Validate trade type
        if trade_type not in ['BUY', 'SELL']:
            return jsonify({'status': 'error', 'message': 'Invalid trade type'}), 400
        
        # Validate amounts
        if amount <= 0 or price <= 0:
            return jsonify({'status': 'error', 'message': 'Amount and price must be positive'}), 400
        
        # Execute blockchain trade
        trade = blockchain.execute_trade(trade_type, amount, price)
        
        # Process M-Pesa payment
        payment = mpesa.process_payment(phone, amount * price, trade['id'])
        
        # Store trade in database
        db_manager.store_trade(trade)
        
        response = {
            'trade': trade,
            'payment': payment,
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

@app.route('/api/train', methods=['POST'])
def retrain_model():
    """Retrain the AI model"""
    try:
        ai_model.train_model()
        return jsonify({
            'message': 'Model retrained successfully',
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Training error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        # Test components
        weather_status = 'active'
        try:
            weather_api.get_current_weather()
        except:
            weather_status = 'error'
        
        db_status = 'active'
        try:
            db_manager.get_recent_data(1)
        except:
            db_status = 'error'
        
        return jsonify({
            'status': 'active',
            'model_trained': ai_model.is_trained,
            'timestamp': datetime.now().isoformat(),
            'components': {
                'weather_api': weather_status,
                'iot_simulator': 'active',
                'ai_model': 'trained' if ai_model.is_trained else 'not_trained',
                'database': db_status,
                'blockchain': 'active',
                'mpesa': 'active'
            },
            'stats': {
                'wallet_balance': blockchain.wallet_balance,
                'total_trades': len(blockchain.trades),
                'total_payments': len(mpesa.transactions)
            }
        })
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

def initialize_system():
    """Initialize the system on startup"""
    try:
        logger.info("🚀 Starting AI Energy Trading System...")
        
        # Initialize AI model
        logger.info("📊 Loading AI model...")
        ai_model.load_model()
        
        # Test database connection
        logger.info("💾 Testing database connection...")
        db_manager.get_recent_data(1)
        
        # Test weather API
        logger.info("🌤️ Testing weather API...")
        weather_api.get_current_weather()
        
        logger.info("✅ System initialization complete!")
        logger.info("🌐 API server ready at http://localhost:5000")
        logger.info("📈 Dashboard ready for connections")
        
    except Exception as e:
        logger.error(f"❌ System initialization failed: {e}")
        logger.info("⚠️ System will continue with limited functionality")

if __name__ == '__main__':
    # Initialize system
    initialize_system()
    
    # Start Flask API
    app.run(
        debug=False,  # Set to True for development
        host='0.0.0.0',
        port=5000,
        threaded=True
    )