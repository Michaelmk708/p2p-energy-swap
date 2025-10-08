"""
Enhanced AI Energy Trading System using Google Gemini
Provides intelligent trading recommendations with natural language explanations
"""

import logging
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
import re

# Try to import Gemini - graceful fallback if not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd
import joblib

from config.settings import settings

logger = logging.getLogger(__name__)

class GeminiEnergyAdvisor:
    """
    Google Gemini-powered energy trading advisor
    Provides sophisticated analysis and natural language explanations
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = None
        self.backup_model = None
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini AI model initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI: {e}")
                self.model = None
        else:
            logger.warning("Gemini API not available - using backup model only")
        
        # Initialize backup traditional ML model
        self._init_backup_model()
    
    def _init_backup_model(self):
        """Initialize backup Random Forest model"""
        try:
            self.backup_model = RandomForestClassifier(
                n_estimators=settings.N_ESTIMATORS,
                max_depth=settings.MAX_DEPTH,
                min_samples_split=settings.MIN_SAMPLES_SPLIT,
                min_samples_leaf=settings.MIN_SAMPLES_LEAF,
                random_state=settings.RANDOM_STATE,
                class_weight='balanced'
            )
            self.scaler = StandardScaler()
            self.is_backup_trained = False
            logger.info("Backup ML model initialized")
        except Exception as e:
            logger.error(f"Failed to initialize backup model: {e}")
    
    def get_trading_recommendation(self, weather_data: Dict[str, Any], 
                                 iot_data: Dict[str, Any], 
                                 historical_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get comprehensive trading recommendation using Gemini AI
        
        Args:
            weather_data: Current and forecast weather conditions
            iot_data: IoT sensor data from smart meters
            historical_data: Historical trading and energy data
        """
        try:
            # If configured to run in demo mode (no paid API keys), return a deterministic mock
            if settings.DEMO_MODE and (not self.api_key or not GEMINI_AVAILABLE):
                # Deterministic behavior for hackathon demos
                np.random.seed(settings.DEMO_RANDOM_SEED)
                surplus = iot_data.get('surplus_deficit_kwh', iot_data.get('surplus_deficit', 0))
                if surplus > 1.0:
                    decision = 'SELL'
                    confidence = 90.0
                elif surplus < -0.5:
                    decision = 'BUY'
                    confidence = 85.0
                else:
                    decision = 'HOLD'
                    confidence = 70.0

                return {
                    'decision': decision,
                    'confidence': confidence,
                    'reasoning': 'Demo mode deterministic recommendation based on surplus/deficit',
                    'financial_impact': f"Estimated impact: {round(abs(surplus) * settings.ENERGY_PRICE_KWH, 2)} KES",
                    'risk_level': 'LOW',
                    'optimal_timing': 'Immediate' if decision in ['BUY','SELL'] else 'Monitor',
                    'timestamp': datetime.now().isoformat(),
                    'ai_model': 'demo_fallback',
                    'sell_probability': 0.9 if decision == 'SELL' else 0.05,
                    'buy_probability': 0.9 if decision == 'BUY' else 0.05,
                    'hold_probability': 0.1 if decision == 'HOLD' else 0.05
                }

            if self.model and self.api_key:
                # Use Gemini for intelligent analysis
                return self._get_gemini_recommendation(weather_data, iot_data, historical_data)
            else:
                # Fallback to traditional ML
                logger.warning("Using backup ML model - Gemini unavailable")
                return self._get_backup_recommendation(weather_data, iot_data)
                
        except Exception as e:
            logger.error(f"Error getting trading recommendation: {e}")
            return self._get_emergency_recommendation(iot_data)
    
    def _prepare_analysis_context(self, weather_data: Dict[str, Any], 
                                iot_data: Dict[str, Any], 
                                historical_data: List[Dict[str, Any]] = None) -> str:
        """Prepare comprehensive context for Gemini analysis"""
        
        current_time = datetime.now()
        hour = current_time.hour
        
        # Determine time factor
        if 10 <= hour <= 16:
            time_factor = 'Peak solar hours'
        elif hour < 6 or hour > 20:
            time_factor = 'Off-peak solar'
        else:
            time_factor = 'Standard hours'
        
        # Build context string
        context_parts = [
            "SOLAR ENERGY TRADING ANALYSIS REQUEST",
            "",
            f"CURRENT DATE/TIME: {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"HOUR OF DAY: {hour} (Peak solar: 10-16, Peak consumption: 6-9 & 17-22)",
            "",
            "CURRENT WEATHER CONDITIONS:",
            f"- Temperature: {weather_data.get('temperature', 'N/A')}°C",
            f"- Cloud Coverage: {weather_data.get('cloud_percentage', 'N/A')}%",
            f"- Sunlight Hours Expected: {weather_data.get('sunlight_hours', 'N/A')} hours",
            f"- Weather Description: {weather_data.get('weather_desc', 'N/A')}",
            f"- Wind Speed: {weather_data.get('wind_speed', 'N/A')} m/s",
            f"- Humidity: {weather_data.get('humidity', 'N/A')}%",
            "",
            "CURRENT ENERGY SITUATION:",
            f"- Solar Generation: {iot_data.get('solar_generation_kwh', iot_data.get('solar_generation', 'N/A'))} kWh",
            f"- Household Consumption: {iot_data.get('consumption_kwh', iot_data.get('consumption', 'N/A'))} kWh",
            f"- Surplus/Deficit: {iot_data.get('surplus_deficit_kwh', iot_data.get('surplus_deficit', 'N/A'))} kWh",
            f"- Panel Voltage: {iot_data.get('panel_voltage', 'N/A')} V",
            f"- Panel Current: {iot_data.get('panel_current', 'N/A')} A",
            "",
            "MARKET CONTEXT:",
            f"- Energy Price: {settings.ENERGY_PRICE_KWH} KES per kWh",
            f"- Time of Day Factor: {time_factor}",
            ""
        ]
        
        # Add historical context if available
        if historical_data and len(historical_data) > 0:
            recent_avg_surplus = np.mean([d.get('surplus_deficit', 0) for d in historical_data[-10:]])
            context_parts.extend([
                "RECENT PERFORMANCE (Last 10 readings):",
                f"- Average Surplus/Deficit: {recent_avg_surplus:.2f} kWh",
                f"- Data Points Available: {len(historical_data)}",
                ""
            ])
        
        # Add objectives and requirements
        context_parts.extend([
            "TRADING OBJECTIVES:",
            "1. Maximize revenue from excess solar generation",
            "2. Minimize costs when purchasing energy", 
            "3. Consider weather forecasts for strategic timing",
            "4. Account for typical household consumption patterns",
            "5. Factor in grid demand and pricing patterns",
            "",
            "REQUIRED OUTPUT:",
            "Please provide a trading recommendation with detailed analysis."
        ])
        
        return "\n".join(context_parts)
    
    def _get_gemini_recommendation(self, weather_data: Dict[str, Any], 
                                 iot_data: Dict[str, Any],
                                 historical_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get recommendation from Gemini AI"""
        try:
            context = self._prepare_analysis_context(weather_data, iot_data, historical_data)
            
            prompt = f"""
{context}

Based on the above data, provide a comprehensive solar energy trading recommendation.
Consider all factors: weather conditions, energy surplus/deficit, time of day, and market context.

Please provide your analysis in JSON format with these fields:
- decision: "BUY", "SELL", or "HOLD"
- confidence: confidence percentage (0-100)
- reasoning: detailed explanation
- financial_impact: expected revenue/cost impact
- risk_level: "LOW", "MEDIUM", or "HIGH"
- optimal_timing: when to execute the trade

Focus on practical advice for a Kenyan household with solar panels.
"""
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Try to parse JSON response
                try:
                    # Extract JSON from response
                    json_start = response.text.find('{')
                    json_end = response.text.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_text = response.text[json_start:json_end]
                        gemini_analysis = json.loads(json_text)
                    else:
                        # Fallback: parse structured text response
                        gemini_analysis = self._parse_text_response(response.text)
                    
                    # Enhance with additional metadata
                    recommendation = {
                        'decision': gemini_analysis.get('decision', 'HOLD').upper(),
                        'confidence': min(100, max(0, gemini_analysis.get('confidence', 50))),
                        'reasoning': gemini_analysis.get('reasoning', 'AI analysis based on current conditions'),
                        'financial_impact': gemini_analysis.get('financial_impact', 'Estimated neutral impact'),
                        'risk_level': gemini_analysis.get('risk_level', 'MEDIUM'),
                        'optimal_timing': gemini_analysis.get('optimal_timing', 'Immediate execution recommended'),
                        'timestamp': datetime.now().isoformat(),
                        'ai_model': 'gemini-pro',
                        'data_quality': 'high'
                    }
                    
                    # Calculate probabilities for compatibility
                    if recommendation['decision'] == 'SELL':
                        sell_prob = recommendation['confidence'] / 100
                        buy_prob = (100 - recommendation['confidence']) / 100
                    elif recommendation['decision'] == 'BUY':
                        buy_prob = recommendation['confidence'] / 100
                        sell_prob = (100 - recommendation['confidence']) / 100
                    else:  # HOLD
                        buy_prob = 0.4
                        sell_prob = 0.4
                    
                    recommendation.update({
                        'sell_probability': round(sell_prob, 3),
                        'buy_probability': round(buy_prob, 3),
                        'hold_probability': round(1 - sell_prob - buy_prob, 3)
                    })
                    
                    logger.info(f"Gemini recommendation: {recommendation['decision']} "
                              f"(confidence: {recommendation['confidence']}%)")
                    
                    return recommendation
                    
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Failed to parse Gemini response: {e}")
                    logger.info(f"Raw Gemini response: {response.text[:500]}")
                    
                    # Create structured response from text
                    return self._create_fallback_gemini_response(response.text, weather_data, iot_data)
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
        
        # Fallback to backup model
        return self._get_backup_recommendation(weather_data, iot_data)
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse unstructured Gemini text response"""
        analysis = {}
        
        text_upper = text.upper()
        
        # Extract decision
        if 'SELL' in text_upper:
            analysis['decision'] = 'SELL'
        elif 'BUY' in text_upper:
            analysis['decision'] = 'BUY'
        else:
            analysis['decision'] = 'HOLD'
        
        # Extract confidence (look for percentage)
        confidence_match = re.search(r'(\d+)%', text)
        analysis['confidence'] = int(confidence_match.group(1)) if confidence_match else 70
        
        # Extract reasoning (first substantial paragraph)
        sentences = text.split('. ')
        reasoning_sentences = [s for s in sentences if len(s) > 50][:3]
        analysis['reasoning'] = '. '.join(reasoning_sentences) if reasoning_sentences else text[:200]
        
        return analysis
    
    def _create_fallback_gemini_response(self, raw_text: str, weather_data: Dict[str, Any], 
                                       iot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create structured response when JSON parsing fails"""
        
        # Extract basic decision from text
        text_upper = raw_text.upper()
        if 'SELL' in text_upper:
            decision = 'SELL'
            confidence = 75
        elif 'BUY' in text_upper:
            decision = 'BUY'
            confidence = 75
        else:
            decision = 'HOLD'
            confidence = 60
        
        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': raw_text[:300] + "..." if len(raw_text) > 300 else raw_text,
            'financial_impact': 'Analyze based on current surplus/deficit',
            'risk_level': 'MEDIUM',
            'optimal_timing': 'Consider current market conditions',
            'timestamp': datetime.now().isoformat(),
            'ai_model': 'gemini-pro-fallback',
            'sell_probability': 0.6 if decision == 'SELL' else 0.3,
            'buy_probability': 0.6 if decision == 'BUY' else 0.3,
            'hold_probability': 0.6 if decision == 'HOLD' else 0.1
        }
    
    def _get_backup_recommendation(self, weather_data: Dict[str, Any], 
                                 iot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to traditional ML model"""
        
        if not self.is_backup_trained:
            self._train_backup_model()
        
        try:
            # Prepare features
            features = np.array([[
                weather_data.get('temperature', 25),
                weather_data.get('sunlight_hours', 6),
                weather_data.get('cloud_percentage', 50),
                iot_data.get('surplus_deficit_kwh', iot_data.get('surplus_deficit', 0)),
                datetime.now().hour
            ]])
            
            # Scale and predict
            features_scaled = self.scaler.transform(features)
            prediction = self.backup_model.predict(features_scaled)[0]
            probabilities = self.backup_model.predict_proba(features_scaled)[0]
            
            decision = 'SELL' if prediction == 1 else 'BUY'
            confidence = max(probabilities) * 100
            
            return {
                'decision': decision,
                'confidence': round(confidence, 1),
                'reasoning': self._get_backup_reasoning(weather_data, iot_data, decision),
                'financial_impact': f"Estimated {abs(iot_data.get('surplus_deficit', 0)) * settings.ENERGY_PRICE_KWH:.2f} KES",
                'risk_level': 'LOW',
                'optimal_timing': 'Immediate execution',
                'timestamp': datetime.now().isoformat(),
                'ai_model': 'random_forest_backup',
                'sell_probability': round(probabilities[1], 3),
                'buy_probability': round(probabilities[0], 3),
                'hold_probability': 0.1
            }
            
        except Exception as e:
            logger.error(f"Backup model error: {e}")
            return self._get_emergency_recommendation(iot_data)
    
    def _train_backup_model(self):
        """Train the backup Random Forest model"""
        try:
            logger.info("Training backup ML model...")
            
            # Generate training data
            training_data = []
            for _ in range(settings.TRAINING_SAMPLES):
                temp = np.random.normal(25, 5)
                sunlight = max(0, np.random.normal(8, 2))
                clouds = max(0, min(100, np.random.normal(40, 20)))
                surplus = np.random.uniform(-3, 4)
                hour = np.random.randint(0, 24)
                
                # Label logic
                sell_conditions = (surplus > 1 and (clouds < 50 or sunlight > 7) and 6 <= hour <= 18)
                buy_conditions = (surplus < -0.5 or (clouds > 70 and sunlight < 5) or hour < 6 or hour > 20)
                
                label = 1 if sell_conditions else 0
                
                training_data.append([temp, sunlight, clouds, surplus, hour, label])
            
            df = pd.DataFrame(training_data, columns=['temp', 'sunlight', 'clouds', 'surplus', 'hour', 'label'])
            
            X = df[['temp', 'sunlight', 'clouds', 'surplus', 'hour']]
            y = df['label']
            
            # Scale and train
            X_scaled = self.scaler.fit_transform(X)
            self.backup_model.fit(X_scaled, y)
            
            self.is_backup_trained = True
            logger.info("Backup ML model trained successfully")
            
        except Exception as e:
            logger.error(f"Failed to train backup model: {e}")
    
    def _get_backup_reasoning(self, weather_data: Dict[str, Any], 
                            iot_data: Dict[str, Any], decision: str) -> str:
        """Generate reasoning for backup model decision"""
        reasons = []
        
        surplus = iot_data.get('surplus_deficit_kwh', iot_data.get('surplus_deficit', 0))
        clouds = weather_data.get('cloud_percentage', 50)
        temp = weather_data.get('temperature', 25)
        hour = datetime.now().hour
        
        # Energy balance reasoning
        if surplus > 1.5:
            reasons.append(f"Significant energy surplus ({surplus:.1f} kWh) available for sale")
        elif surplus > 0:
            reasons.append(f"Moderate energy surplus ({surplus:.1f} kWh)")
        elif surplus < -1:
            reasons.append(f"High energy deficit ({abs(surplus):.1f} kWh) - purchasing recommended")
        
        # Weather reasoning
        if clouds < 30:
            reasons.append("Clear weather conditions favor continued solar generation")
        elif clouds > 70:
            reasons.append("Heavy cloud coverage may reduce future generation")
        
        # Time reasoning
        if 10 <= hour <= 16:
            reasons.append("Peak solar generation hours")
        elif hour < 6 or hour > 20:
            reasons.append("Off-peak hours with limited solar generation")
        
        # Temperature reasoning
        if temp > 35:
            reasons.append("High temperature may reduce panel efficiency")
        
        return "; ".join(reasons) if reasons else f"Standard {decision} conditions based on ML analysis"
    
    def _get_emergency_recommendation(self, iot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Emergency fallback recommendation when all else fails"""
        surplus = iot_data.get('surplus_deficit_kwh', iot_data.get('surplus_deficit', 0))
        decision = 'SELL' if surplus > 0 else 'BUY'
        
        return {
            'decision': decision,
            'confidence': 50,
            'reasoning': f"Emergency mode: {decision} based on current surplus/deficit ({surplus:.1f} kWh)",
            'financial_impact': f"Estimated {abs(surplus) * settings.ENERGY_PRICE_KWH:.2f} KES",
            'risk_level': 'HIGH',
            'optimal_timing': 'Immediate - system in emergency mode',
            'timestamp': datetime.now().isoformat(),
            'ai_model': 'emergency_fallback',
            'sell_probability': 0.6 if decision == 'SELL' else 0.4,
            'buy_probability': 0.6 if decision == 'BUY' else 0.4,
            'hold_probability': 0.0
        }

# Initialize the Gemini-powered advisor
gemini_advisor = GeminiEnergyAdvisor()