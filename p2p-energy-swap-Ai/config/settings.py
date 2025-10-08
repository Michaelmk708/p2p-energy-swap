"""
Configuration settings for AI Energy Trading System
"""
import os
from typing import Dict, Any

class Settings:
    """Main settings class"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'energy_trading.db')
    
    # Weather API (Open-Meteo - free, no API key required)
    WEATHER_API_BASE_URL = "https://api.open-meteo.com/v1"
    GEOCODING_API_BASE_URL = "https://geocoding-api.open-meteo.com/v1"
    DEFAULT_COORDINATES = (-1.2921, 36.8219)  # Nairobi, Kenya
    DEFAULT_CITY = "Nairobi"
    
    # AI Model Settings
    MODEL_PATH = 'models/energy_trading_model.pkl'
    SCALER_PATH = 'models/energy_scaler.pkl'
    
    # Training Parameters
    TRAINING_SAMPLES = 3000
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    
    # Random Forest Parameters
    N_ESTIMATORS = 150
    MAX_DEPTH = 12
    MIN_SAMPLES_SPLIT = 5
    MIN_SAMPLES_LEAF = 2
    
    # IoT Simulation
    BASE_SOLAR_GENERATION = 5.0  # kWh
    BASE_CONSUMPTION = 3.0  # kWh
    
    # Energy Trading
    ENERGY_PRICE_KWH = 0.12  # KES per kWh
    INITIAL_WALLET_BALANCE = 100.0  # SOL
    
    # API Server
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    DEBUG_MODE = False
    # Demo / hackathon mode - if true, use deterministic mock data and fallbacks
    DEMO_MODE = bool(os.getenv('DEMO_MODE', '1') == '1')
    DEMO_RANDOM_SEED = int(os.getenv('DEMO_RANDOM_SEED', '42'))
    
    # M-Pesa Daraja API Settings
    MPESA_SUCCESS_RATE = 0.95  # For mock fallback
    MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', '')
    MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', '')
    MPESA_ENVIRONMENT = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
    MPESA_BUSINESS_SHORTCODE = os.getenv('MPESA_BUSINESS_SHORTCODE', '174379')
    MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')
    
    # Payment callback URL (update with your actual domain)
    PAYMENT_CALLBACK_URL = os.getenv('PAYMENT_CALLBACK_URL', 'http://localhost:5000/api/payment/callback')
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """Return all settings as dictionary"""
        return {
            key: getattr(cls, key) 
            for key in dir(cls) 
            if not key.startswith('_') and not callable(getattr(cls, key))
        }
    
    @classmethod
    def validate_required_keys(cls) -> Dict[str, bool]:
        """Validate that required API keys are set"""
        return {
            'weather_api': True,  # Using Open-Meteo (free, no key required)
            'gemini_api': bool(cls.GEMINI_API_KEY),
            'mpesa_keys': bool(cls.MPESA_CONSUMER_KEY and cls.MPESA_CONSUMER_SECRET)
        }

    @classmethod
    def get_demo_status(cls) -> Dict[str, bool]:
        """Return which external services will run in demo mode"""
        return {
            'gemini': not bool(cls.GEMINI_API_KEY),
            'mpesa': not bool(cls.MPESA_CONSUMER_KEY and cls.MPESA_CONSUMER_SECRET),
            'blockchain_service': not bool(os.getenv('BLOCKCHAIN_SERVICE_URL'))
        }

# Create settings instance
settings = Settings()