import requests
import random
import time

# Use localhost for the pitch so you don't rely on ngrok breaking
TELEMETRY_URL = "http://localhost:8000/api/meter/update/"
TRADE_URL = "http://localhost:8000/api/trade/record/"

def generate_data():
    # Force a "Solar Glut" scenario for the pitch (High PV, Low Load)
    pv = round(random.uniform(3.0, 5.0), 2)      
    load = round(random.uniform(0.5, 2.0), 2)    
    return pv, load

print("🚀 [HARDWARE] ESP32 Oracle Simulator Started...")
print("   Waiting for solar surplus to trigger blockchain settlement...\n")

while True:
    pv, load = generate_data()
    
    try:
        # 1. Send continuous physical telemetry
        requests.post(TELEMETRY_URL, json={"solar": pv, "load": load}, timeout=5)
        print(f"📡 [METER READING] Solar PV: {pv}kW | House Load: {load}kW")
        
        # 2. THE ORACLE LOGIC: If producing more than consuming, sell it!
        if pv > load:
            surplus = round(pv - load, 2)
            price_kes = round(surplus * 15, 2) # Fixed KES 15 P2P Rate
            
            print(f"⚠️  [SURPLUS DETECTED] {surplus}kW excess. Triggering Web3 Oracle...")
            
            trade_payload = {
                "amount": surplus,
                "price": price_kes,
                "seller_id": "Estate_House_A"
            }
            
            # 3. Hit the Web3 Django Endpoint
            resp = requests.post(TRADE_URL, json=trade_payload, timeout=5)
            blockchain_data = resp.json()
            
            print(f"✅  [LEDGER SUCCESS] Hash: {blockchain_data.get('tx_hash')}\n")
        else:
            print("🔋  [GRID] Normal operation. No surplus to trade.\n")
            
    except Exception as e:
        print(f"❌ Connection Error (Is Django running?): {e}\n")
        
    time.sleep(8)  # Fast updates (every 8 seconds) for the live pitch