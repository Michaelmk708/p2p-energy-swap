import serial
import json
import requests
import time
import sys

# CONFIG
WOKWI_PORT = "socket://localhost:4000"  # RFC2217 Port from wokwi.toml
BACKEND_URL = "http://localhost:8000/api/meter/update/"

def run_bridge():
    print(f"🔌 CONNECTING TO WOKWI ON {WOKWI_PORT}...")
    
    try:
        # Connect to the Simulator
        ser = serial.serial_for_url(WOKWI_PORT, baudrate=115200)
        print("✅ CONNECTED! Waiting for knob data...")
        
        buffer = ""
        
        while True:
            if ser.in_waiting > 0:
                # Read data from the "wire"
                char = ser.read().decode('utf-8', errors='ignore')
                
                if char == '\n':
                    # We have a full line! Parse it.
                    try:
                        data = json.loads(buffer)
                        print(f"🎛️  KNOBS: Solar={data['solar']}kW | Load={data['load']}kW")
                        
                        # Forward to Dashboard
                        try:
                            requests.post(BACKEND_URL, json=data, timeout=0.5)
                        except:
                            pass # Ignore backend errors to keep bridge running
                            
                    except json.JSONDecodeError:
                        pass # Ignore garbage data
                        
                    buffer = "" # Reset buffer
                else:
                    buffer += char
            
            time.sleep(0.001)

    except serial.SerialException:
        print("❌ CONNECTION FAILED")
        print("   1. Did you add 'rfc2217ServerPort = 4000' to wokwi.toml?")
        print("   2. Is the simulation RUNNING?")
        print("   3. Restart the Wokwi Simulation and try again.")
    except KeyboardInterrupt:
        print("\n👋 Stopping Bridge")

if __name__ == "__main__":
    run_bridge()