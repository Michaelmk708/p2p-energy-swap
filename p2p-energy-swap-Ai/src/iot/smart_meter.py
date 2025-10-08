"""
IoT Simulator for ESP32 Smart Meters
Simulates real-time solar generation and consumption data
"""

import numpy as np
import logging
from datetime import datetime
from typing import Dict, Any
import json

from config.settings import settings

logger = logging.getLogger(__name__)

class ESP32SmartMeter:
    """
    Simulates ESP32 smart meter behavior for solar energy monitoring
    Mimics the actual IoT devices that will be deployed in households
    """
    
    def __init__(self, household_id: str, location: str = "Nairobi"):
        self.household_id = household_id
        self.location = location
        self.base_generation = settings.BASE_SOLAR_GENERATION
        self.base_consumption = settings.BASE_CONSUMPTION
        
        # Household characteristics (randomized for diversity)
        self.household_size = np.random.randint(2, 6)  # 2-5 people
        self.solar_panel_capacity = np.random.uniform(3.0, 8.0)  # kW
        self.energy_efficiency = np.random.uniform(0.8, 1.2)  # Efficiency factor
        
        logger.info(f"Initialized ESP32 Smart Meter for household {household_id}")
        logger.info(f"Panel capacity: {self.solar_panel_capacity:.1f}kW, "
                   f"Household size: {self.household_size}")
    
    def read_solar_generation(self, temperature: float, sunlight_hours: float, 
                            cloud_percentage: float) -> float:
        """
        Simulate solar panel generation based on weather conditions
        Mimics actual ESP32 sensor readings
        """
        try:
            # Base generation adjusted for panel capacity
            base_gen = self.base_generation * (self.solar_panel_capacity / 5.0)
            
            # Temperature efficiency curve (panels work best around 25°C)
            if temperature <= 25:
                temp_factor = 0.8 + (temperature - 15) * 0.02  # Increases to 1.0 at 25°C
            else:
                temp_factor = 1.0 - (temperature - 25) * 0.005  # Decreases after 25°C
            
            temp_factor = max(0.5, min(1.2, temp_factor))
            
            # Sunlight hours factor
            sunlight_factor = min(sunlight_hours / 8.0, 1.0)  # Peak at 8 hours
            
            # Cloud coverage impact
            cloud_factor = (100 - cloud_percentage) / 100
            
            # Time of day factor (solar generation follows sun curve)
            hour = datetime.now().hour
            if 6 <= hour <= 18:
                time_factor = 1.0 - abs(12 - hour) / 6.0  # Peak at noon
            else:
                time_factor = 0.0  # No generation at night
            
            # Calculate generation with random variation
            generation_factor = temp_factor * sunlight_factor * cloud_factor * time_factor
            generation = base_gen * generation_factor * np.random.uniform(0.85, 1.15)
            
            return max(0, generation)
            
        except Exception as e:
            logger.error(f"Error in solar generation calculation: {e}")
            return 0.0
    
    def read_energy_consumption(self) -> float:
        """
        Simulate household energy consumption
        Based on typical usage patterns and household size
        """
        try:
            # Base consumption adjusted for household size
            base_consumption = self.base_consumption * (self.household_size / 3.0)
            
            # Time-based consumption patterns
            hour = datetime.now().hour
            
            # Peak consumption periods
            if 6 <= hour <= 9:  # Morning peak
                time_factor = np.random.uniform(1.4, 1.8)
            elif 17 <= hour <= 22:  # Evening peak
                time_factor = np.random.uniform(1.5, 2.0)
            elif 22 <= hour <= 6:  # Night time
                time_factor = np.random.uniform(0.4, 0.7)
            else:  # Day time
                time_factor = np.random.uniform(0.8, 1.2)
            
            # Add efficiency factor
            consumption = base_consumption * time_factor / self.energy_efficiency
            
            # Add random variation
            consumption *= np.random.uniform(0.9, 1.1)
            
            return max(0.1, consumption)
            
        except Exception as e:
            logger.error(f"Error in consumption calculation: {e}")
            return self.base_consumption
    
    def get_sensor_reading(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get complete sensor reading like actual ESP32 would provide
        Returns data in format that Oracle gateway expects
        """
        try:
            generation = self.read_solar_generation(
                weather_data['temperature'],
                weather_data['sunlight_hours'],
                weather_data['cloud_percentage']
            )
            
            consumption = self.read_energy_consumption()
            surplus_deficit = generation - consumption
            
            # Format data like ESP32 JSON output
            sensor_data = {
                'device_id': self.household_id,
                'timestamp': datetime.now().isoformat(),
                'location': self.location,
                'measurements': {
                    'solar_generation_kwh': round(generation, 3),
                    'consumption_kwh': round(consumption, 3),
                    'surplus_deficit_kwh': round(surplus_deficit, 3),
                    'panel_voltage': round(np.random.uniform(230, 250), 1),  # Simulated voltage
                    'panel_current': round(generation * 4.35, 2),  # Simulated current (V=230)
                    'temperature_c': weather_data['temperature'],
                    'battery_level': np.random.randint(85, 100)  # ESP32 battery level
                },
                'weather_conditions': {
                    'temperature': weather_data['temperature'],
                    'sunlight_hours': weather_data['sunlight_hours'],
                    'cloud_percentage': weather_data['cloud_percentage'],
                    'weather_desc': weather_data.get('weather_desc', 'clear')
                },
                'device_status': {
                    'online': True,
                    'signal_strength': np.random.randint(-70, -30),  # dBm
                    'last_maintenance': '2024-09-15',
                    'firmware_version': '1.2.3'
                }
            }
            
            return sensor_data
            
        except Exception as e:
            logger.error(f"Error generating sensor reading: {e}")
            return self._get_fallback_data(weather_data)
    
    def _get_fallback_data(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback sensor data in case of errors"""
        return {
            'device_id': self.household_id,
            'timestamp': datetime.now().isoformat(),
            'location': self.location,
            'measurements': {
                'solar_generation_kwh': 3.0,
                'consumption_kwh': 2.5,
                'surplus_deficit_kwh': 0.5,
                'panel_voltage': 240.0,
                'panel_current': 13.04,
                'temperature_c': weather_data.get('temperature', 25),
                'battery_level': 95
            },
            'weather_conditions': weather_data,
            'device_status': {
                'online': True,
                'signal_strength': -50,
                'last_maintenance': '2024-09-15',
                'firmware_version': '1.2.3'
            }
        }

class IoTNetwork:
    """
    Manages multiple ESP32 smart meters in a network
    Simulates the IoT infrastructure for multiple households
    """
    
    def __init__(self):
        self.smart_meters: Dict[str, ESP32SmartMeter] = {}
        self.oracle_gateway_url = "http://localhost:8080/iot-data"  # Mock Oracle gateway
        
    def add_household(self, household_id: str, location: str = "Nairobi") -> ESP32SmartMeter:
        """Add a new smart meter to the network"""
        meter = ESP32SmartMeter(household_id, location)
        self.smart_meters[household_id] = meter
        logger.info(f"Added smart meter for household {household_id}")
        return meter
    
    def get_network_data(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect data from all smart meters in the network
        Aggregates data like the Oracle gateway would
        """
        network_data = {
            'timestamp': datetime.now().isoformat(),
            'total_households': len(self.smart_meters),
            'households': {},
            'network_summary': {
                'total_generation': 0,
                'total_consumption': 0,
                'total_surplus_deficit': 0,
                'online_devices': 0
            }
        }
        
        for household_id, meter in self.smart_meters.items():
            try:
                sensor_data = meter.get_sensor_reading(weather_data)
                network_data['households'][household_id] = sensor_data
                
                # Update network summary
                measurements = sensor_data['measurements']
                network_data['network_summary']['total_generation'] += measurements['solar_generation_kwh']
                network_data['network_summary']['total_consumption'] += measurements['consumption_kwh']
                network_data['network_summary']['total_surplus_deficit'] += measurements['surplus_deficit_kwh']
                
                if sensor_data['device_status']['online']:
                    network_data['network_summary']['online_devices'] += 1
                    
            except Exception as e:
                logger.error(f"Error collecting data from {household_id}: {e}")
        
        # Round summary values
        summary = network_data['network_summary']
        for key in ['total_generation', 'total_consumption', 'total_surplus_deficit']:
            summary[key] = round(summary[key], 2)
        
        return network_data
    
    def send_to_oracle_gateway(self, network_data: Dict[str, Any]) -> bool:
        """
        Send aggregated data to Oracle gateway (simulated)
        In production, this would connect to actual Oracle blockchain gateway
        """
        try:
            # Simulate sending to Oracle gateway
            logger.info(f"Sending network data to Oracle gateway: {self.oracle_gateway_url}")
            logger.info(f"Data summary: {network_data['network_summary']}")
            
            # In production, this would be:
            # response = requests.post(self.oracle_gateway_url, json=network_data)
            # return response.status_code == 200
            
            return True  # Simulated success
            
        except Exception as e:
            logger.error(f"Error sending to Oracle gateway: {e}")
            return False

# Initialize default IoT network
iot_network = IoTNetwork()

# Add some default households for testing
default_households = [
    "HH001_Nairobi_Central",
    "HH002_Nairobi_East", 
    "HH003_Nairobi_West",
    "HH004_Nairobi_South",
    "HH005_Nairobi_North"
]

for household in default_households:
    iot_network.add_household(household)