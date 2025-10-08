#!/usr/bin/env python3
"""
Manual energy data updater
Use this to simulate Wokwi potentiometer changes until the Wokwi connection is fixed
"""
import requests
import time

def update_energy_data(pv_kw, load_kw):
    """Update both PV and Load data"""
    base_url = "http://127.0.0.1:8000/api/iotcentral/telemetry_bridge/"
    
    # Post PV data
    pv_data = {"device": "sim-1", "component": "pv_array", "data": {"power": pv_kw}}
    pv_response = requests.post(base_url, json=pv_data)
    
    # Post Load data  
    load_data = {"device": "sim-1", "component": "house_load", "data": {"power": load_kw}}
    load_response = requests.post(base_url, json=load_data)
    
    print(f"PV={pv_kw}kW Load={load_kw}kW Net={(pv_kw-load_kw):+.2f}kW")
    return pv_response.ok and load_response.ok

if __name__ == "__main__":
    print("Energy Data Updater")
    print("Enter PV and Load values to update the dashboard")
    print("Example: 2.5 1.2  (PV=2.5kW Load=1.2kW)")
    print("Type 'quit' to exit")
    
    while True:
        try:
            user_input = input("\nEnter PV Load (kW): ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            parts = user_input.split()
            if len(parts) == 2:
                pv_kw = float(parts[0])
                load_kw = float(parts[1])
                
                if update_energy_data(pv_kw, load_kw):
                    print("✓ Updated successfully - check dashboard!")
                else:
                    print("✗ Update failed")
            else:
                print("Please enter two numbers: PV_kW Load_kW")
                
        except ValueError:
            print("Please enter valid numbers")
        except KeyboardInterrupt:
            break
    
    print("\nGoodbye!")