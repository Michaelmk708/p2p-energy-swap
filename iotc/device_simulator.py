#!/usr/bin/env python3
"""
Azure IoT Central device simulator for HouseholdMeter

This script connects to your IoT Central device using the device connection string
and sends Plug and Play component telemetry:
  - pv_array.power (kW)
  - house_load.power (kW)
Optionally, it can send grid_export.energy_kwh_total (kWh) as a slowly increasing counter.

Requirements:
  pip install azure-iot-device

Environment variables expected:
  IOTC_DEVICE_CONNECTION_STRING  # From IoT Central: Devices -> sim-1 -> Connect
  IOTC_MODEL_ID=dtmi:org:wattchain:HouseholdMeter;1  # optional; defaults to this DTMI
  IOTC_SEND_EXPORT_TOTAL=0/1  # optional; when 1 sends grid_export.energy_kwh_total

Usage:
  export IOTC_DEVICE_CONNECTION_STRING="HostName=...;DeviceId=sim-1;SharedAccessKey=..."
  python iotc/device_simulator.py

To simulate multiple devices, run multiple processes each with its own device connection string.
"""
import os
import sys
import time
import math
import json
from datetime import datetime

try:
    from azure.iot.device import IoTHubDeviceClient, Message
except Exception as e:
    print("Missing dependency: azure-iot-device. Install it with: pip install azure-iot-device")
    sys.exit(1)


CONN_STR = os.getenv("IOTC_DEVICE_CONNECTION_STRING")
MODEL_ID = os.getenv("IOTC_MODEL_ID", "dtmi:org:wattchain:HouseholdMeter;1")
SEND_EXPORT = os.getenv("IOTC_SEND_EXPORT_TOTAL", "0") == "1"

if not CONN_STR:
    print("IOTC_DEVICE_CONNECTION_STRING is required. Get it from IoT Central -> Devices -> <your device> -> Connect.")
    sys.exit(2)


def make_client():
    # Newer azure-iot-device supports model_id argument; if not available, fallback without it.
    try:
        client = IoTHubDeviceClient.create_from_connection_string(CONN_STR, websockets=True, product_info="pnp", model_id=MODEL_ID)
    except TypeError:
        client = IoTHubDeviceClient.create_from_connection_string(CONN_STR, websockets=True)
    return client


def send_component_telemetry(client: IoTHubDeviceClient, component: str, payload: dict):
    msg = Message(json.dumps(payload))
    msg.content_type = "application/json"
    msg.content_encoding = "utf-8"
    # IoT Plug and Play convention for component telemetry
    msg.custom_properties["$.sub"] = component
    client.send_message(msg)


def main():
    print(f"Connecting to IoT Central with model {MODEL_ID}...")
    client = make_client()
    client.connect()
    print("Connected. Streaming pv_array.power and house_load.power every 2s.")
    if SEND_EXPORT:
        print("Also sending grid_export.energy_kwh_total every 30s.")

    i = 0
    export_total = 0.0
    last_export_ts = time.time()
    try:
        while True:
            # Generate PV and Load
            pv_kw = max(0.0, min(5.0, 2.5 + 2.0 * math.sin(i / 20.0) + 0.3 * math.sin(i / 5.0)))
            load_kw = max(0.2, min(3.0, 1.2 + 0.6 * math.sin(i / 30.0 + 0.7) + 0.3 * math.sin(i / 6.0)))

            send_component_telemetry(client, "pv_array", {"power": round(pv_kw, 3)})
            send_component_telemetry(client, "house_load", {"power": round(load_kw, 3)})

            # Optional export total every ~30s
            now = time.time()
            if SEND_EXPORT and now - last_export_ts >= 30:
                # Increase by approximate net surplus over period (very rough)
                # In a real device this would be a measured cumulative counter.
                net_kw = max(0.0, pv_kw - load_kw)
                export_total = round(export_total + net_kw * (now - last_export_ts) / 3600.0, 4)
                send_component_telemetry(client, "grid_export", {"energy_kwh_total": export_total})
                last_export_ts = now

            i += 1
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        client.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    main()
