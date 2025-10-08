#!/usr/bin/env python3
"""
Local simulator that mimics IoT Central Data Export payloads and sends them to the backend ingest endpoint.
Use this when IoT Central export isn’t wired yet, or for quick multi-household testing.
"""
import os
import sys
import time
import json
import math
from datetime import datetime, timezone

try:
    import requests
except Exception as e:
    print("Missing 'requests' library. Install with: pip install requests")
    sys.exit(1)

BACKEND_URL = os.getenv("BACKEND_INGEST_URL", "http://localhost:8000/api/iotcentral/ingest/")
SHARED_SECRET = os.getenv("IOTCENTRAL_SHARED_SECRET", "change-this-32char-secret")

HOUSEHOLDS = [
    {"device": "sim-1", "pv_component": "pv_array", "load_component": "house_load"},
    {"device": "sim-2", "pv_component": "pv_array", "load_component": "house_load"},
]

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def main():
    print(f"Streaming to {BACKEND_URL} (header X-Shared-Secret set)")
    t0 = time.time()
    i = 0
    while True:
        ts = now_iso()
        batch = []
        for idx, hh in enumerate(HOUSEHOLDS):
            # Simple daily curve: PV ~ sine peak at midday; Load ~ base + small noise
            # i advances ~every 2s
            pv_base = 2.5 + 2.0 * math.sin((i/30.0) + idx)  # slow sine
            pv_noise = 0.3 * math.sin(i/7.0 + idx)
            pv_kw = clamp(pv_base + pv_noise, 0.0, 5.0)

            load_base = 1.2 + 0.6 * math.sin((i/40.0) + idx/2)
            load_noise = 0.3 * math.sin(i/5.0 + 0.7*idx)
            load_kw = clamp(load_base + load_noise, 0.2, 3.0)

            batch.append({
                "device": hh["device"],
                "component": hh["pv_component"],
                "timestamp": ts,
                "measurements": {"power": round(pv_kw, 3)}
            })
            batch.append({
                "device": hh["device"],
                "component": hh["load_component"],
                "timestamp": ts,
                "measurements": {"power": round(load_kw, 3)}
            })

        headers = {"Content-Type": "application/json", "X-Shared-Secret": SHARED_SECRET}
        try:
            r = requests.post(BACKEND_URL, data=json.dumps(batch), headers=headers, timeout=5)
            if r.status_code >= 300:
                print(f"POST {r.status_code}: {r.text[:200]}")
            else:
                # print a tiny dot to show progress
                print(".", end="", flush=True)
        except Exception as e:
            print(f"Error posting telemetry: {e}")

        i += 1
        time.sleep(2)

if __name__ == "__main__":
    main()
"""
Multi-household IoT Central simulator

Generates PV and Load telemetry per household using the existing IoT smart meter
models from p2p-energy-swap-Ai, and posts them to the Django backend's secure
IoT Central ingest endpoint.

Usage:
  - Ensure backend is running on http://localhost:8000
  - Ensure IOTCENTRAL_WEBHOOK_SECRET is set in backend .env
  - Optionally, ensure AUTO_MINT_ENABLED=true in backend .env and restart backend
  - Run this script with the backend venv:
      source ../.venv/bin/activate
      python scripts/simulate_iotcentral_households.py

This will stream readings every ~2 seconds for multiple households.
"""

from __future__ import annotations

import os
import sys
import time
import json
from datetime import datetime, timezone
from typing import Dict, Any, List

try:
    import requests
except Exception:
    print("The 'requests' package is required. Install it in the backend venv: pip install requests")
    raise

# --- Config ---
BACKEND_BASE = os.getenv("BACKEND_BASE", "http://localhost:8000")
INGEST_URL = f"{BACKEND_BASE.rstrip('/')}/api/iotcentral/ingest/"
SECRET = os.getenv("IOTCENTRAL_WEBHOOK_SECRET", "")

if not SECRET:
    # try load from backend .env if present
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        try:
            for line in open(env_path, "r", encoding="utf-8"):
                if line.strip().startswith("IOTCENTRAL_WEBHOOK_SECRET="):
                    SECRET = line.strip().split("=", 1)[1]
                    break
        except Exception:
            pass

if not SECRET:
    print("WARNING: IOTCENTRAL_WEBHOOK_SECRET not set. Set it in environment or backend .env.")

# --- Import IoT simulation code from AI project ---
AI_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "p2p-energy-swap-Ai"))
AI_SRC = os.path.join(AI_ROOT, "src")
# Ensure both the AI project's src (for packages like weather, iot, etc.) and
# the project root (for top-level packages like config) are on sys.path.
if AI_SRC not in sys.path:
    sys.path.append(AI_SRC)
if AI_ROOT not in sys.path:
    sys.path.append(AI_ROOT)

try:
    from iot.smart_meter import iot_network
    from weather.weather_api import weather_service
except Exception as e:
    print("Could not import IoT simulation modules from p2p-energy-swap-Ai.")
    print("Ensure the workspace contains p2p-energy-swap-Ai with both 'src' and 'config' folders.")
    print(f"Import error: {e}")
    raise


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_payload_for_household(household_id: str, weather: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build two telemetry records for a single household: PV power and Load power.
    We map the smart meter's per-hour kWh estimate to an instantaneous kW value
    for this PoC (1 kWh over 1 hour ~ 1 kW instantaneous).
    """
    meter = iot_network.smart_meters.get(household_id)
    if meter is None:
        meter = iot_network.add_household(household_id)

    reading = meter.get_sensor_reading(weather)
    meas = reading.get("measurements", {})
    gen_kwh = float(meas.get("solar_generation_kwh", 0.0))
    cons_kwh = float(meas.get("consumption_kwh", 0.0))

    ts = _now_iso()
    return [
        {
            "device": household_id,
            "component": "pv-array",
            "timestamp": ts,
            "measurements": {"power": round(gen_kwh, 3)},
        },
        {
            "device": household_id,
            "component": "house-load",
            "timestamp": ts,
            "measurements": {"power": round(cons_kwh, 3)},
        },
    ]


def post_batch(items: List[Dict[str, Any]]) -> None:
    headers = {
        "Content-Type": "application/json",
        "X-Shared-Secret": SECRET,
    }
    try:
        resp = requests.post(INGEST_URL, headers=headers, data=json.dumps(items), timeout=10)
        if resp.status_code != 200:
            print(f"Ingest error {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"Ingest exception: {e}")


def main() -> None:
    # get current weather for simulation
    weather = weather_service.get_current_weather(city="Nairobi") or {
        "temperature": 26.0,
        "sunlight_hours": 7.0,
        "cloud_percentage": 20.0,
        "weather_desc": "clear",
    }

    # choose households: use any preloaded in iot_network or defaults
    households = list(iot_network.smart_meters.keys())
    if not households:
        households = [
            "HH001_Nairobi_Central",
            "HH002_Nairobi_East",
            "HH003_Nairobi_West",
            "HH004_Nairobi_South",
            "HH005_Nairobi_North",
        ]

    print(f"Streaming IoT telemetry for {len(households)} households → {INGEST_URL}")
    print("Ctrl+C to stop.")

    # stream loop
    tick = 0
    try:
        while True:
            batch: List[Dict[str, Any]] = []
            for hh in households:
                batch.extend(make_payload_for_household(hh, weather))
            post_batch(batch)
            tick += 1
            if tick % 10 == 0:
                print(f"Tick {tick}: sent {len(batch)} records")
            time.sleep(2.0)
    except KeyboardInterrupt:
        print("\nStopped streaming.")


if __name__ == "__main__":
    main()
