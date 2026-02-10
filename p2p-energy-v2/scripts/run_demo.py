import requests
import time
import random

# CONFIG
API_URL = "http://localhost:8000/api/trade/record/"
METER_ID = "HEXING_001"

def simulate_teacher_house():
    """
    Simulates 'The Teacher's' house during the presentation.
    """
    print("--- STARTING PILOT SIMULATION ---")
    
    battery = 85.0
    
    while True:
        # 1. Simulate Charging (Sun is out!)
        battery += 0.5
        if battery > 100: battery = 100
        
        print(f"Battery: {battery:.1f}%")

        # 2. TRIGGER: If Battery > 90%, Sell!
        if battery > 90.0:
            print(">>> TRIGGER: Battery Full! Auto-Selling 2kWh...")
            # Fire data to backend
            # requests.post(API_URL, json={"amount": 2, "price": 15.00})
            
            # Drop battery after sale
            battery -= 2.0
            
        time.sleep(2) # Fast forward time for the demo

if __name__ == "__main__":
    simulate_teacher_house()