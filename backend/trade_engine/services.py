from django.utils import timezone

# SIMPLE IN-MEMORY STORE FOR THE DEMO (Resets on restart)
METER_STATE = {
    "solar_kw": 0.0,
    "load_kw": 0.0,
    "battery_percent": 85.0,
    "net_kw": 0.0
}

class PricingService:
    @staticmethod
    def get_market_status():
        """
        The 'Investor-Approved' Logic. 
        Reliable, Deterministic, Demo-Safe.
        """
        try:
            hour = timezone.localtime().hour
        except:
            hour = timezone.now().hour
        
        # 11 AM - 3 PM: Solar Glut (Cheap)
        if 11 <= hour < 15:
            return {
                "price": 15.00, 
                "status": "SOLAR_GLUT", 
                "message": "Super Off-Peak! Solar is abundant.",
                "color": "green"
            }
        # 6 PM - 9 PM: Peak (Expensive)
        elif 18 <= hour < 21:
            return {
                "price": 35.00, 
                "status": "GRID_STRAIN", 
                "message": "Peak Hours. Conservation active.",
                "color": "red"
            }
        # Normal Time
        else:
            return {
                "price": 22.00, 
                "status": "NORMAL", 
                "message": "Standard Grid Tariff.",
                "color": "blue"
            }

class MeterService:
    @staticmethod
    def update_readings(solar, load):
        """
        Called by the Wokwi Bridge to update backend state.
        """
        # Update the global state
        METER_STATE["solar_kw"] = float(solar)
        METER_STATE["load_kw"] = float(load)
        METER_STATE["net_kw"] = float(solar) - float(load)
        
        # Simple Battery Logic simulation
        if METER_STATE["net_kw"] > 0:
            METER_STATE["battery_percent"] = min(100, METER_STATE["battery_percent"] + 0.5)
        else:
            METER_STATE["battery_percent"] = max(0, METER_STATE["battery_percent"] - 0.2)
            
        return METER_STATE

    @staticmethod
    def get_readings():
        return METER_STATE