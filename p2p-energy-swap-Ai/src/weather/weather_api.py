"""
Weather API Integration with Open-Meteo
Handles real weather data fetching and forecasting using Open-Meteo API (free, no API key required)
"""

import requests
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import time

from config.settings import settings

logger = logging.getLogger(__name__)

class WeatherService:
    """
    Enhanced weather service using Open-Meteo API (free, no API key required)
    """
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1"
        self.default_coordinates = settings.DEFAULT_COORDINATES  # Nairobi: (-1.2921, 36.8219)
        self.last_request_time = 0
        self.rate_limit_delay = 0.1  # 100ms between requests (Open-Meteo is more generous)
        
        # Cache for reducing API calls
        self.weather_cache = {}
        self.cache_duration = 600  # 10 minutes cache (longer since it's free)
    
    def _rate_limit(self):
        """Implement rate limiting for API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.weather_cache:
            return False
        
        cache_time = self.weather_cache[cache_key]['timestamp']
        return (time.time() - cache_time) < self.cache_duration
    
    def get_current_weather(self, city: str = None, coordinates: tuple = None) -> Dict[str, Any]:
        """
        Get current weather data using Open-Meteo API
        
        Args:
            city: City name (e.g., "Nairobi") - will be geocoded to coordinates
            coordinates: (latitude, longitude) tuple
        """
        # Get coordinates
        if coordinates:
            lat, lon = coordinates
            cache_key = f"current_{lat}_{lon}"
        elif city:
            coords = self._geocode_city(city)
            if not coords:
                logger.warning(f"Could not geocode city {city}, using default location")
                lat, lon = self.default_coordinates
            else:
                lat, lon = coords
            cache_key = f"current_{city}"
        else:
            lat, lon = self.default_coordinates
            cache_key = "current_default"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached weather data for coordinates ({lat}, {lon})")
            return self.weather_cache[cache_key]['data']
        
        # Get real weather data
        weather_data = self._get_open_meteo_current(lat, lon, city)
        if weather_data:
            # Cache the result
            self.weather_cache[cache_key] = {
                'data': weather_data,
                'timestamp': time.time()
            }
            return weather_data
        
        # Fallback to simulated data
        city_name = city or "Default Location"
        logger.warning(f"Using simulated weather data for {city_name}")
        return self._generate_realistic_weather(city_name)
    
    def _geocode_city(self, city: str) -> Optional[tuple]:
        """Convert city name to coordinates using Open-Meteo geocoding"""
        try:
            self._rate_limit()
            
            params = {
                'name': city,
                'count': 1,
                'language': 'en',
                'format': 'json'
            }
            
            response = requests.get(f"{self.geocoding_url}/search", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                result = data['results'][0]
                return (result['latitude'], result['longitude'])
                
        except Exception as e:
            logger.error(f"Geocoding failed for {city}: {e}")
        
        return None
    
    def _get_open_meteo_current(self, lat: float, lon: float, city_name: str = None) -> Optional[Dict[str, Any]]:
        """Get current weather from Open-Meteo API"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'current': [
                    'temperature_2m',
                    'relative_humidity_2m', 
                    'apparent_temperature',
                    'weather_code',
                    'surface_pressure',
                    'wind_speed_10m',
                    'wind_direction_10m',
                    'cloud_cover',
                    'visibility',
                    'uv_index'
                ],
                'timezone': 'auto',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data['current']
            
            # Transform to our standard format
            weather_data = {
                'temperature': round(current['temperature_2m'], 1),
                'humidity': current['relative_humidity_2m'],
                'pressure': current['surface_pressure'],
                'wind_speed': current['wind_speed_10m'],
                'wind_direction': current['wind_direction_10m'],
                'cloud_percentage': current['cloud_cover'],
                'weather_code': current['weather_code'],
                'weather_desc': self._get_weather_description(current['weather_code']),
                'weather_main': self._get_weather_main(current['weather_code']),
                'visibility': current['visibility'] / 1000 if current['visibility'] else 10,  # Convert to km
                'uv_index': current['uv_index'] or 0,
                'apparent_temperature': round(current['apparent_temperature'], 1),
                'location': {
                    'city': city_name or f"Location ({lat:.2f}, {lon:.2f})",
                    'coordinates': [lat, lon]
                },
                'timestamp': datetime.now().isoformat(),
                'data_source': 'open-meteo'
            }
            
            # Calculate sunlight hours (sunrise/sunset data requires separate API call)
            weather_data.update(self._calculate_sun_times(lat, lon))
            
            # Calculate effective sunlight hours
            weather_data['sunlight_hours'] = self._calculate_effective_sunlight_hours(
                weather_data['sunrise'], weather_data['sunset'], 
                weather_data['cloud_percentage']
            )
            
            logger.info(f"Retrieved real weather data: "
                       f"{weather_data['temperature']}°C, "
                       f"{weather_data['cloud_percentage']}% clouds, "
                       f"UV: {weather_data['uv_index']}")
            
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Open-Meteo API request failed: {e}")
        except KeyError as e:
            logger.error(f"Unexpected API response format: {e}")
        except Exception as e:
            logger.error(f"Weather API error: {e}")
        
        return None
    
    def _get_weather_description(self, weather_code: int) -> str:
        """Convert WMO weather code to description"""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            56: "Light freezing drizzle", 57: "Dense freezing drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            66: "Light freezing rain", 67: "Heavy freezing rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            85: "Slight snow showers", 86: "Heavy snow showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(weather_code, "Unknown")
    
    def _get_weather_main(self, weather_code: int) -> str:
        """Convert WMO weather code to main category"""
        if weather_code == 0:
            return "Clear"
        elif 1 <= weather_code <= 3:
            return "Clouds"
        elif weather_code in [45, 48]:
            return "Mist"
        elif 51 <= weather_code <= 67:
            return "Rain"
        elif 71 <= weather_code <= 86:
            return "Snow"
        elif weather_code >= 95:
            return "Thunderstorm"
        else:
            return "Unknown"
    
    def _calculate_sun_times(self, lat: float, lon: float) -> Dict[str, Any]:
        """Calculate sunrise and sunset times for given coordinates"""
        try:
            # Simple astronomical calculation for sunrise/sunset
            from datetime import date
            import math
            
            today = date.today()
            day_of_year = today.timetuple().tm_yday
            
            # Approximate solar calculations
            solar_declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
            hour_angle = math.degrees(math.acos(-math.tan(math.radians(lat)) * math.tan(math.radians(solar_declination))))
            
            sunrise_hour = 12 - hour_angle / 15
            sunset_hour = 12 + hour_angle / 15
            
            return {
                'sunrise': max(5, min(8, int(sunrise_hour))),  # Clamp between 5-8 AM
                'sunset': max(17, min(20, int(sunset_hour)))   # Clamp between 5-8 PM
            }
            
        except Exception as e:
            logger.warning(f"Sun time calculation failed: {e}, using defaults")
            return {'sunrise': 7, 'sunset': 18}  # Default values
    
    def _calculate_effective_sunlight_hours(self, sunrise_hour: int, sunset_hour: int, 
                                          cloud_percentage: float) -> float:
        """Calculate effective sunlight hours considering cloud coverage"""
        daylight_hours = max(0, sunset_hour - sunrise_hour)
        cloud_reduction = cloud_percentage / 100 * 0.7  # Clouds reduce 70% max
        effective_hours = daylight_hours * (1 - cloud_reduction)
        return max(0, round(effective_hours, 1))
    
    def _estimate_uv_index(self, lat: float, lon: float) -> float:
        """Estimate UV index based on location and time"""
        # Simplified UV index estimation
        # In production, would use UV API or more sophisticated calculation
        hour = datetime.now().hour
        
        if 6 <= hour <= 18:
            # Higher UV near equator, peak at solar noon
            equator_factor = 1 - abs(lat) / 90
            time_factor = 1 - abs(12 - hour) / 6
            uv_index = 8 * equator_factor * time_factor
        else:
            uv_index = 0
        
        return max(0, round(uv_index, 1))
    
    def get_forecast(self, city: str = None, hours: int = 24, coordinates: tuple = None) -> List[Dict[str, Any]]:
        """
        Get weather forecast for specified hours using Open-Meteo API
        
        Args:
            city: City name
            hours: Number of hours to forecast (max 168 for Open-Meteo)
            coordinates: (latitude, longitude) tuple
        """
        # Get coordinates
        if coordinates:
            lat, lon = coordinates
            cache_key = f"forecast_{lat}_{lon}_{hours}"
        elif city:
            coords = self._geocode_city(city)
            if not coords:
                logger.warning(f"Could not geocode city {city}, using default location")
                lat, lon = self.default_coordinates
            else:
                lat, lon = coords
            cache_key = f"forecast_{city}_{hours}"
        else:
            lat, lon = self.default_coordinates
            cache_key = f"forecast_default_{hours}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached forecast data")
            return self.weather_cache[cache_key]['data']
        
        # Get real forecast data
        forecast_data = self._get_open_meteo_forecast(lat, lon, hours)
        if forecast_data:
            # Cache the result
            self.weather_cache[cache_key] = {
                'data': forecast_data,
                'timestamp': time.time()
            }
            return forecast_data
        
        # Fallback to simulated forecast
        city_name = city or "Default Location"
        logger.warning(f"Using simulated forecast data for {city_name}")
        return self._generate_realistic_forecast(city_name, hours)
    
    def _get_open_meteo_forecast(self, lat: float, lon: float, hours: int) -> Optional[List[Dict[str, Any]]]:
        """Get forecast from Open-Meteo API"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'hourly': [
                    'temperature_2m',
                    'relative_humidity_2m',
                    'apparent_temperature',
                    'precipitation',
                    'weather_code',
                    'surface_pressure',
                    'cloud_cover',
                    'visibility',
                    'wind_speed_10m',
                    'wind_direction_10m',
                    'uv_index'
                ],
                'forecast_days': min(7, (hours // 24) + 1),  # Max 7 days
                'timezone': 'auto',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            hourly_data = data['hourly']
            forecasts = []
            
            for i in range(min(hours, len(hourly_data['time']))):
                forecast_time = datetime.fromisoformat(hourly_data['time'][i])
                weather_code = hourly_data['weather_code'][i]
                
                forecast = {
                    'timestamp': forecast_time.isoformat(),
                    'temperature': round(hourly_data['temperature_2m'][i], 1),
                    'humidity': hourly_data['relative_humidity_2m'][i],
                    'pressure': hourly_data['surface_pressure'][i],
                    'wind_speed': hourly_data['wind_speed_10m'][i],
                    'wind_direction': hourly_data['wind_direction_10m'][i],
                    'cloud_percentage': hourly_data['cloud_cover'][i],
                    'weather_code': weather_code,
                    'weather_desc': self._get_weather_description(weather_code),
                    'weather_main': self._get_weather_main(weather_code),
                    'precipitation': hourly_data['precipitation'][i],
                    'visibility': hourly_data['visibility'][i] / 1000 if hourly_data['visibility'][i] else 10,
                    'uv_index': hourly_data['uv_index'][i] or 0,
                    'apparent_temperature': round(hourly_data['apparent_temperature'][i], 1),
                    'data_source': 'open-meteo'
                }
                
                forecasts.append(forecast)
            
            logger.info(f"Retrieved {len(forecasts)} hours of forecast data from Open-Meteo")
            return forecasts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Open-Meteo forecast API request failed: {e}")
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected forecast API response format: {e}")
        except Exception as e:
            logger.error(f"Weather forecast error: {e}")
        
        return None
    
    def _generate_realistic_weather(self, city: str) -> Dict[str, Any]:
        """Generate realistic weather data for fallback"""
        hour = datetime.now().hour
        day_of_year = datetime.now().timetuple().tm_yday
        
        # Base temperature varies by location and season
        if city.lower() in ['nairobi', 'kenya']:
            # Nairobi climate: mild, around equator
            base_temp = 20 + 5 * np.sin((day_of_year - 80) * 2 * np.pi / 365)  # Seasonal variation
            base_temp += 8 * np.sin((hour - 6) * np.pi / 12)  # Daily variation
        else:
            # Generic temperate climate
            base_temp = 15 + 10 * np.sin((day_of_year - 80) * 2 * np.pi / 365)
            base_temp += 10 * np.sin((hour - 6) * np.pi / 12)
        
        # Add random variation
        temperature = base_temp + np.random.uniform(-3, 3)
        temperature = max(-10, min(45, temperature))  # Reasonable bounds
        
        # Cloud percentage with weather patterns
        cloud_base = np.random.uniform(20, 70)
        if np.random.random() < 0.3:  # 30% chance of very cloudy
            cloud_percentage = np.random.uniform(70, 95)
        elif np.random.random() < 0.2:  # 20% chance of clear skies
            cloud_percentage = np.random.uniform(5, 25)
        else:
            cloud_percentage = cloud_base
        
        # Calculate sunrise/sunset (simplified)
        sunrise = 6
        sunset = 18
        sunlight_hours = self._calculate_effective_sunlight_hours(
            sunrise, sunset, cloud_percentage
        )
        
        return {
            'temperature': round(temperature, 1),
            'humidity': int(np.random.uniform(40, 85)),
            'pressure': int(np.random.uniform(1010, 1025)),
            'wind_speed': round(np.random.uniform(0, 15), 1),
            'cloud_percentage': round(cloud_percentage, 1),
            'sunlight_hours': sunlight_hours,
            'weather_desc': self._get_simulated_weather_description(cloud_percentage, temperature),
            'weather_main': self._get_simulated_weather_main(cloud_percentage),
            'visibility': int(np.random.uniform(8000, 12000)),
            'uv_index': self._estimate_uv_index(0, 0),  # Approximate for equator
            'sunrise': sunrise,
            'sunset': sunset,
            'location': {
                'city': city,
                'country': 'Unknown',
                'coordinates': [0, 0]
            },
            'timestamp': datetime.now().isoformat(),
            'data_source': 'simulated'
        }
    
    def _generate_realistic_forecast(self, city: str, hours: int) -> List[Dict[str, Any]]:
        """Generate realistic forecast data"""
        forecasts = []
        current_weather = self._generate_realistic_weather(city)
        
        for i in range(0, hours, 3):  # Generate every 3 hours like real API
            forecast_time = datetime.now() + timedelta(hours=i)
            hour = forecast_time.hour
            
            # Evolve weather gradually
            if i == 0:
                temp = current_weather['temperature']
                clouds = current_weather['cloud_percentage']
            else:
                # Gradual changes
                temp = forecasts[-1]['temperature'] + np.random.uniform(-2, 2)
                clouds = forecasts[-1]['cloud_percentage'] + np.random.uniform(-10, 10)
                clouds = max(0, min(100, clouds))
            
            # Add daily temperature cycle
            daily_temp_variation = 8 * np.sin((hour - 6) * np.pi / 12)
            temp += daily_temp_variation * 0.3  # Reduced impact for forecast
            
            forecast = {
                'timestamp': forecast_time.isoformat(),
                'temperature': round(max(-10, min(45, temp)), 1),
                'humidity': int(np.random.uniform(40, 85)),
                'pressure': int(np.random.uniform(1010, 1025)),
                'wind_speed': round(np.random.uniform(0, 12), 1),
                'cloud_percentage': round(clouds, 1),
                'weather_desc': self._get_simulated_weather_description(clouds, temp),
                'weather_main': self._get_simulated_weather_main(clouds),
                'precipitation': round(max(0, np.random.uniform(-0.5, 2) if clouds > 70 else 0), 1),
                'sunlight_hours': max(0, 3 - (clouds / 100 * 2)) if 6 <= hour <= 18 else 0,
                'data_source': 'simulated'
            }
            
            forecasts.append(forecast)
        
        return forecasts
    
    def _get_simulated_weather_description(self, cloud_percentage: float, temperature: float) -> str:
        """Generate weather description based on conditions"""
        if cloud_percentage < 20:
            return "clear sky"
        elif cloud_percentage < 40:
            return "few clouds"
        elif cloud_percentage < 70:
            return "scattered clouds"
        elif cloud_percentage < 90:
            return "overcast clouds"
        else:
            if temperature > 25:
                return "heavy clouds"
            else:
                return "possible light rain"
    
    def _get_simulated_weather_main(self, cloud_percentage: float) -> str:
        """Get main weather category"""
        if cloud_percentage < 30:
            return "Clear"
        elif cloud_percentage < 70:
            return "Clouds"
        else:
            return "Overcast"
    
    def get_weather_alerts(self, city: str = None) -> List[Dict[str, Any]]:
        """Get weather alerts/warnings (mock implementation)"""
        # This would integrate with weather alert APIs in production
        alerts = []
        
        current_weather = self.get_current_weather(city)
        
        # Temperature alerts
        if current_weather['temperature'] > 35:
            alerts.append({
                'type': 'heat_warning',
                'severity': 'high',
                'message': 'High temperature may reduce solar panel efficiency',
                'impact': 'Potential 5-10% reduction in solar generation',
                'timestamp': datetime.now().isoformat()
            })
        
        # Cloud cover alerts
        if current_weather['cloud_percentage'] > 80:
            alerts.append({
                'type': 'cloud_coverage',
                'severity': 'medium',
                'message': 'Heavy cloud coverage expected',
                'impact': 'Solar generation may be reduced by 30-50%',
                'timestamp': datetime.now().isoformat()
            })
        
        # Wind alerts
        if current_weather.get('wind_speed', 0) > 20:
            alerts.append({
                'type': 'high_wind',
                'severity': 'medium',
                'message': 'High wind speeds detected',
                'impact': 'Monitor solar panel stability',
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts

# Initialize weather service
weather_service = WeatherService()