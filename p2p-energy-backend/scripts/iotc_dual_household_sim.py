#!/usr/bin/env python3
"""
IoT Central dual-household simulator that connects as two devices and publishes component telemetry
compatible with our backend ingest endpoint (via IoT Central Data Export).

Control entirely from IoT Central UI using device commands:
  - set_pv_on / set_pv_off (no payload)
  - set_targets (payload: { "pv_kw": number, "load_kw": number })

Telemetry components and fields:
  - pv_array.power (kW)
  - house_load.power (kW)
  - grid_export.power (kW)    # derived: max(pv - load, 0)

Env configuration:
  IOTC_CONNSTR_1   : Device connection string for household 1 (sim-1)
  IOTC_CONNSTR_2   : Device connection string for household 2 (sim-2)
  PERIOD_SEC       : Send period per device (default 2.0)

Install dependencies in an isolated venv:
  python3 -m venv .venv && . .venv/bin/activate && pip install azure-iot-device

Run:
  .venv/bin/python scripts/iotc_dual_household_sim.py
"""
import asyncio
import json
import os
import random
from typing import Dict, Any

from azure.iot.device.aio import IoTHubDeviceClient, ProvisioningDeviceClient
from azure.iot.device import Message


def jitter(val: float, pct: float = 0.05) -> float:
    return max(0.0, float(val) * (1.0 + random.uniform(-pct, pct)))


class Household:
    def __init__(self, name: str, *, conn_str: str | None = None,
                 id_scope: str | None = None, registration_id: str | None = None,
                 symmetric_key: str | None = None,
                 pv_kw: float = 0.0, load_kw: float = 0.5):
        self.name = name
        # Connection via full IoT Hub connection string (preferred when available)
        self.conn_str = conn_str
        # Or connect via DPS (IoT Central typical): ID scope + device id + symmetric key
        self.id_scope = id_scope
        self.registration_id = registration_id
        self.symmetric_key = symmetric_key
        self.client: IoTHubDeviceClient | None = None
        self.targets = {"pv_kw": pv_kw, "load_kw": load_kw}

    async def connect(self):
        # Strategy: prefer direct connection string if provided; otherwise use DPS (IoT Central standard)
        if self.conn_str:
            self.client = IoTHubDeviceClient.create_from_connection_string(self.conn_str)
            await self.client.connect()
        else:
            if not (self.id_scope and self.registration_id and self.symmetric_key):
                raise RuntimeError(f"{self.name}: DPS parameters missing (id_scope/registration_id/symmetric_key)")
            provisioning_host = "global.azure-devices-provisioning.net"
            prov = ProvisioningDeviceClient.create_from_symmetric_key(
                provisioning_host=provisioning_host,
                registration_id=self.registration_id,
                id_scope=self.id_scope,
                symmetric_key=self.symmetric_key,
            )
            result = await prov.register()
            if not getattr(result, "registration_state", None) or not getattr(result.registration_state, "assigned_hub", None):
                raise RuntimeError(f"{self.name}: DPS registration failed: {getattr(result, 'registration_state', None)}")
            hostname = result.registration_state.assigned_hub
            self.client = IoTHubDeviceClient.create_from_symmetric_key(
                symmetric_key=self.symmetric_key,
                hostname=hostname,
                device_id=self.registration_id,
            )
            await self.client.connect()

        # Register method handlers for IoT Central commands
        async def on_method_request(request):
            try:
                method = request.name or ""
                payload = request.payload or {}
                if method == "set_pv_on":
                    self.targets["pv_kw"] = max(0.5, float(payload.get("pv_kw", 2.5)))
                    status = 200
                    resp = {"ok": True, "pv_kw": self.targets["pv_kw"]}
                elif method == "set_pv_off":
                    self.targets["pv_kw"] = 0.0
                    status = 200
                    resp = {"ok": True, "pv_kw": 0.0}
                elif method == "set_targets":
                    if "pv_kw" in payload:
                        self.targets["pv_kw"] = max(0.0, float(payload["pv_kw"]))
                    if "load_kw" in payload:
                        self.targets["load_kw"] = max(0.0, float(payload["load_kw"]))
                    status = 200
                    resp = {"ok": True, **self.targets}
                else:
                    status = 404
                    resp = {"error": f"unknown method {method}"}
            except Exception as e:
                status = 500
                resp = {"error": str(e)}
            await self.client.send_method_response({
                "request_id": request.request_id,
                "status": status,
                "payload": resp,
            })

        self.client.on_method_request_received = on_method_request

    async def send_component_telemetry(self, component: str, body: Dict[str, Any]):
        assert self.client is not None
        msg = Message(json.dumps(body))
        # IoT Central uses the $.sub application property for component scoping
        msg.custom_properties["$.sub"] = component
        msg.content_encoding = "utf-8"
        msg.content_type = "application/json"
        await self.client.send_message(msg)

    async def loop(self, period: float = 2.0):
        assert self.client is not None
        disable_export = os.getenv("DISABLE_GRID_EXPORT", "").lower() in ("1","true","yes","on")
        while True:
            # Slight jitter for more realistic values
            pv = jitter(self.targets.get("pv_kw", 0.0))
            ld = jitter(self.targets.get("load_kw", 0.0))
            exp = max(0.0, pv - ld)

            try:
                await self.send_component_telemetry("pv_array", {"power": round(pv, 3)})
                await self.send_component_telemetry("house_load", {"power": round(ld, 3)})
                # Only send export stream if not explicitly disabled
                if not disable_export:
                    await self.send_component_telemetry("grid_export", {"power": round(exp, 3)})
            except Exception as e:
                print(f"{self.name}: telemetry error: {e}")

            await asyncio.sleep(period)


async def main():
    # Prefer full IoT Hub connection strings when available
    conn1 = os.getenv("IOTC_CONNSTR_1")
    conn2 = os.getenv("IOTC_CONNSTR_2")

    # Otherwise fall back to IoT Central DPS parameters
    id_scope = os.getenv("IOTC_ID_SCOPE")
    dev1 = os.getenv("IOTC_DEVICE_ID_1")
    key1 = os.getenv("IOTC_DEVICE_KEY_1")
    dev2 = os.getenv("IOTC_DEVICE_ID_2")
    key2 = os.getenv("IOTC_DEVICE_KEY_2")

    h1: Household
    h2: Household
    if conn1 and conn2:
        h1 = Household("household-1", conn_str=conn1, pv_kw=2.0, load_kw=0.8)
        h2 = Household("household-2", conn_str=conn2, pv_kw=0.0, load_kw=1.0)
    elif id_scope and dev1 and key1 and dev2 and key2:
        h1 = Household("household-1", id_scope=id_scope, registration_id=dev1, symmetric_key=key1, pv_kw=2.0, load_kw=0.8)
        h2 = Household("household-2", id_scope=id_scope, registration_id=dev2, symmetric_key=key2, pv_kw=0.0, load_kw=1.0)
    else:
        print("Provide either:")
        print(" - IOTC_CONNSTR_1 and IOTC_CONNSTR_2 (full IoT Hub connection strings), or")
        print(" - IOTC_ID_SCOPE, IOTC_DEVICE_ID_1, IOTC_DEVICE_KEY_1, IOTC_DEVICE_ID_2, IOTC_DEVICE_KEY_2 (IoT Central DPS)")
        print("In IoT Central: Devices → <device> → Connect: copy ID Scope, Device ID, Primary key for each device.")
        return

    period = float(os.getenv("PERIOD_SEC", "2.0"))

    await asyncio.gather(h1.connect(), h2.connect())
    print("Connected to IoT Central as two devices. Use IoT Central commands set_pv_on/set_pv_off/set_targets to control.")

    await asyncio.gather(h1.loop(period), h2.loop(period))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
