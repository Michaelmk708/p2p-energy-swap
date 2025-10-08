"""
Database Management Module
Handles data storage and retrieval for the energy trading system
"""

import sqlite3
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

from config.settings import settings

logger = logging.getLogger(__name__)

class EnergyTradingDatabase:
    """
    Enhanced database manager for energy trading data
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.connection = None
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with comprehensive schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Energy data table - stores IoT and weather data with AI predictions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS energy_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    household_id TEXT DEFAULT 'default',
                    
                    -- Weather data
                    temperature REAL,
                    humidity REAL,
                    pressure REAL,
                    wind_speed REAL,
                    cloud_percentage REAL,
                    sunlight_hours REAL,
                    weather_desc TEXT,
                    weather_source TEXT DEFAULT 'simulated',
                    
                    -- IoT/Energy data
                    solar_generation REAL,
                    consumption REAL,
                    surplus_deficit REAL,
                    panel_voltage REAL,
                    panel_current REAL,
                    battery_level INTEGER,
                    device_status TEXT DEFAULT 'online',
                    
                    -- AI prediction data
                    ai_decision TEXT,
                    confidence REAL,
                    reasoning TEXT,
                    ai_model TEXT DEFAULT 'unknown',
                    financial_impact TEXT,
                    risk_level TEXT,
                    optimal_timing TEXT,
                    
                    -- Metadata
                    data_quality TEXT DEFAULT 'good',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Trades table - stores executed trades
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    household_id TEXT DEFAULT 'default',
                    trade_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    price REAL NOT NULL,
                    total_value REAL,
                    status TEXT DEFAULT 'pending',
                    tx_hash TEXT,
                    blockchain_network TEXT DEFAULT 'solana',
                    
                    -- Payment integration
                    payment_method TEXT DEFAULT 'mpesa',
                    payment_tx_id TEXT,
                    payment_status TEXT DEFAULT 'pending',
                    
                    -- Market context
                    market_conditions TEXT,
                    execution_time_ms INTEGER,
                    
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Market data table - stores pricing and market information
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    energy_price REAL NOT NULL,
                    grid_demand REAL,
                    supply_available REAL,
                    peak_hours_active BOOLEAN DEFAULT 0,
                    market_sentiment TEXT,
                    price_trend TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # System logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    component TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Weather alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    impact_description TEXT,
                    active BOOLEAN DEFAULT 1,
                    expires_at TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            indexes = [
                'CREATE INDEX IF NOT EXISTS idx_energy_timestamp ON energy_data(timestamp)',
                'CREATE INDEX IF NOT EXISTS idx_energy_household ON energy_data(household_id)',
                'CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)',
                'CREATE INDEX IF NOT EXISTS idx_trades_household ON trades(household_id)',
                'CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)',
                'CREATE INDEX IF NOT EXISTS idx_market_timestamp ON market_data(timestamp)',
                'CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp)',
                'CREATE INDEX IF NOT EXISTS idx_weather_alerts_active ON weather_alerts(active)',
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized successfully at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def store_energy_data(self, weather_data: Dict[str, Any], iot_data: Dict[str, Any], 
                         prediction: Dict[str, Any], household_id: str = 'default'):
        """Store comprehensive energy data including weather, IoT, and AI prediction"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO energy_data 
                (timestamp, household_id, temperature, humidity, pressure, wind_speed,
                 cloud_percentage, sunlight_hours, weather_desc, weather_source,
                 solar_generation, consumption, surplus_deficit, panel_voltage, panel_current,
                 battery_level, device_status, ai_decision, confidence, reasoning,
                 ai_model, financial_impact, risk_level, optimal_timing, data_quality)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction.get('timestamp', datetime.now().isoformat()),
                household_id,
                weather_data.get('temperature'),
                weather_data.get('humidity'),
                weather_data.get('pressure'),
                weather_data.get('wind_speed'),
                weather_data.get('cloud_percentage'),
                weather_data.get('sunlight_hours'),
                weather_data.get('weather_desc'),
                weather_data.get('data_source', 'simulated'),
                iot_data.get('solar_generation_kwh', iot_data.get('solar_generation')),
                iot_data.get('consumption_kwh', iot_data.get('consumption')),
                iot_data.get('surplus_deficit_kwh', iot_data.get('surplus_deficit')),
                iot_data.get('panel_voltage'),
                iot_data.get('panel_current'),
                iot_data.get('battery_level'),
                iot_data.get('device_status', {}).get('online', True),
                prediction.get('decision'),
                prediction.get('confidence'),
                prediction.get('reasoning'),
                prediction.get('ai_model'),
                prediction.get('financial_impact'),
                prediction.get('risk_level'),
                prediction.get('optimal_timing'),
                prediction.get('data_quality', 'good')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing energy data: {e}")
    
    def store_trade(self, trade_data: Dict[str, Any], household_id: str = 'default'):
        """Store trade execution data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trades 
                (timestamp, household_id, trade_type, amount, price, total_value, status, tx_hash,
                 blockchain_network, payment_method, payment_tx_id, payment_status,
                 market_conditions, execution_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data.get('timestamp', datetime.now().isoformat()),
                household_id,
                trade_data['type'],
                trade_data['amount'],
                trade_data['price'],
                trade_data.get('total_value', trade_data['amount'] * trade_data['price']),
                trade_data.get('status', 'pending'),
                trade_data.get('tx_hash', ''),
                trade_data.get('blockchain_network', 'solana'),
                trade_data.get('payment_method', 'mpesa'),
                trade_data.get('payment_tx_id', ''),
                trade_data.get('payment_status', 'pending'),
                json.dumps(trade_data.get('market_conditions', {})),
                trade_data.get('execution_time_ms', 0)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing trade: {e}")
    
    def get_recent_energy_data(self, hours: int = 24, household_id: str = None) -> List[Dict[str, Any]]:
        """Get recent energy data for analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Build query based on whether household_id is specified
            if household_id:
                query = '''
                    SELECT * FROM energy_data 
                    WHERE datetime(timestamp) > datetime('now', '-{} hours')
                    AND household_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1000
                '''.format(hours)
                df = pd.read_sql_query(query, conn, params=[household_id])
            else:
                query = '''
                    SELECT * FROM energy_data 
                    WHERE datetime(timestamp) > datetime('now', '-{} hours')
                    ORDER BY timestamp DESC
                    LIMIT 1000
                '''.format(hours)
                df = pd.read_sql_query(query, conn)
            
            conn.close()
            return df.to_dict('records') if not df.empty else []
            
        except Exception as e:
            logger.error(f"Error retrieving recent energy data: {e}")
            return []
    
    def get_trade_history(self, hours: int = 168, household_id: str = None) -> List[Dict[str, Any]]:
        """Get trade history (default: last week)"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            if household_id:
                query = '''
                    SELECT * FROM trades 
                    WHERE datetime(timestamp) > datetime('now', '-{} hours')
                    AND household_id = ?
                    ORDER BY timestamp DESC
                '''.format(hours)
                df = pd.read_sql_query(query, conn, params=[household_id])
            else:
                query = '''
                    SELECT * FROM trades 
                    WHERE datetime(timestamp) > datetime('now', '-{} hours')
                    ORDER BY timestamp DESC
                '''.format(hours)
                df = pd.read_sql_query(query, conn)
            
            conn.close()
            return df.to_dict('records') if not df.empty else []
            
        except Exception as e:
            logger.error(f"Error retrieving trade history: {e}")
            return []
    
    def get_energy_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive energy analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get energy data for analysis period
            query = '''
                SELECT * FROM energy_data 
                WHERE datetime(timestamp) > datetime('now', '-{} days')
                ORDER BY timestamp DESC
            '''.format(days)
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return {'status': 'no_data', 'message': 'No data available for analysis'}
            
            # Calculate analytics
            analytics = {
                'period_days': days,
                'total_records': len(df),
                'energy_stats': {
                    'avg_solar_generation': df['solar_generation'].mean(),
                    'max_solar_generation': df['solar_generation'].max(),
                    'avg_consumption': df['consumption'].mean(),
                    'max_consumption': df['consumption'].max(),
                    'avg_surplus_deficit': df['surplus_deficit'].mean(),
                    'total_surplus': df[df['surplus_deficit'] > 0]['surplus_deficit'].sum(),
                    'total_deficit': df[df['surplus_deficit'] < 0]['surplus_deficit'].sum()
                },
                'weather_impact': {
                    'avg_temperature': df['temperature'].mean(),
                    'avg_cloud_coverage': df['cloud_percentage'].mean(),
                    'avg_sunlight_hours': df['sunlight_hours'].mean(),
                    'clear_days': len(df[df['cloud_percentage'] < 30]),
                    'cloudy_days': len(df[df['cloud_percentage'] > 70])
                },
                'ai_decisions': {
                    'sell_recommendations': len(df[df['ai_decision'] == 'SELL']),
                    'buy_recommendations': len(df[df['ai_decision'] == 'BUY']),
                    'hold_recommendations': len(df[df['ai_decision'] == 'HOLD']),
                    'avg_confidence': df['confidence'].mean()
                },
                'peak_performance': {
                    'best_generation_day': df.loc[df['solar_generation'].idxmax()]['timestamp'],
                    'best_generation_value': df['solar_generation'].max(),
                    'highest_surplus_day': df.loc[df['surplus_deficit'].idxmax()]['timestamp'],
                    'highest_surplus_value': df['surplus_deficit'].max()
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Round numerical values
            for category in ['energy_stats', 'weather_impact', 'ai_decisions']:
                for key, value in analytics[category].items():
                    if isinstance(value, float):
                        analytics[category][key] = round(value, 2)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error calculating energy analytics: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def store_system_log(self, level: str, component: str, message: str, details: Dict[str, Any] = None):
        """Store system log entry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_logs (timestamp, level, component, message, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                level.upper(),
                component,
                message,
                json.dumps(details) if details else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing system log: {e}")
    
    def store_weather_alert(self, alert_type: str, severity: str, message: str, 
                           impact: str = None, expires_hours: int = 24):
        """Store weather alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            expires_at = (datetime.now() + timedelta(hours=expires_hours)).isoformat()
            
            cursor.execute('''
                INSERT INTO weather_alerts 
                (timestamp, alert_type, severity, message, impact_description, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                alert_type,
                severity.upper(),
                message,
                impact,
                expires_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing weather alert: {e}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active weather alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT * FROM weather_alerts 
                WHERE active = 1 AND datetime(expires_at) > datetime('now')
                ORDER BY severity DESC, timestamp DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df.to_dict('records') if not df.empty else []
            
        except Exception as e:
            logger.error(f"Error retrieving active alerts: {e}")
            return []
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to maintain database performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            # Clean up old records from each table
            tables_to_clean = ['energy_data', 'trades', 'system_logs', 'weather_alerts']
            
            for table in tables_to_clean:
                cursor.execute(f'''
                    DELETE FROM {table} 
                    WHERE datetime(created_at) < datetime(?)
                ''', (cutoff_date,))
                
                deleted_count = cursor.rowcount
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old records from {table}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database cleanup completed, kept data from last {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Error during database cleanup: {e}")

# Initialize database manager
db_manager = EnergyTradingDatabase()