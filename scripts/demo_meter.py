import requests
import random
import time

BRIDGE_URL = "http://unbaffled-dwindlingly-lydia.ngrok-free.dev/telemetry"  # Update if your ngrok URL changes

def generate_data():
    pv = round(random.uniform(0.5, 5.0), 2)      # PV: 0.5 to 5.0 kW
    load = round(random.uniform(0.3, 4.0), 2)    # Load: 0.3 to 4.0 kW
    return {"PV": pv, "Load": load}

while True:
    data = generate_data()
    try:
        resp = requests.post(BRIDGE_URL, json=data, timeout=5)
        print(f"Sent: {data} | Response: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Error sending data: {e}")
    time.sleep(120)  # 2 minutes
