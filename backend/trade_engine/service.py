# backend/trade_engine/services.py
from django.utils import timezone

# SIMPLE IN-MEMORY STORE FOR THE DEMO (Resets on restart)
# This holds the latest values from Wokwi
METER_STATE = {
    "solar_kw": 0.0,
    "load_kw": 0.0,
    "battery_percent": 85.0,
    "net_kw": 0.0
}

class PricingService:
    @staticmethod
    def get_market_status():
        # ... (Keep your existing Time-of-Use logic here) ...
        # Just ensure you copy the get_market_status code from before
        hour = timezone.localtime().hour
        if 11 <= hour < 15:
            return {"price": 15.00, "status": "SOLAR_GLUT", "color": "green", "message": "Super Off-Peak"}
        elif 18 <= hour < 21:
            return {"price": 35.00, "status": "GRID_STRAIN", "color": "red", "message": "Peak Hours"}
        else:
            return {"price": 22.00, "status": "NORMAL", "color": "blue", "message": "Standard Tariff"}

class MeterService:
    @staticmethod
    def update_readings(solar, load):
        """
        Called by the Wokwi Bridge to update backend state.
        """
        METER_STATE["solar_kw"] = float(solar)
        METER_STATE["load_kw"] = float(load)
        METER_STATE["net_kw"] = float(solar) - float(load)
        
        # Simple Battery Logic: If Solar > Load, Charge. If Load > Solar, Drain.
        if METER_STATE["net_kw"] > 0:
            METER_STATE["battery_percent"] = min(100, METER_STATE["battery_percent"] + 0.5)
        else:
            METER_STATE["battery_percent"] = max(0, METER_STATE["battery_percent"] - 0.2)
            
        return METER_STATE

    @staticmethod
    def get_readings():
        return METER_STATE