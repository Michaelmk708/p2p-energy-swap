Wattchain MicroPython (Wokwi)

Quick tips:

- To change the backend URL (e.g., new ngrok): edit `config.json` and update `host` (and `diagram.json` net.servers if using HTTPS) then restart the sim from the `wattchain` folder.
- Files uploaded to the device are mapped in `wokwi.toml`: `/boot.py`, `/main.py`, and `/config.json`.
- On boot, the device tries to `import main`. If that fails, `boot.py` starts a fallback loop with the same behavior.
- From the REPL, you can manually start the loop:
  - Fallback: `import boot; boot.start()`
  - Main: `import main; main.start()`
- Default pins: PV on GPIO35, Load on GPIO34. Scale is 0–5 kW.

Config fields (config.json):

```
{
  "wifi_ssid": "Wokwi-GUEST",
  "wifi_pass": "",
  "host": "<your-ngrok>.ngrok-free.dev",
  "port": 443,
  "path": "/api/iotcentral/telemetry_bridge/",
  "device": "sim-1",
  "pv_component": "pv_array",
  "load_component": "house_load",
  "max_watts": 5000,
  "min_delta_w": 5,
  "heartbeat_ms": 1500,
  "debug_body_posts": 3
}
```

Troubleshooting:

- If `os.listdir()` only shows `boot.py`, restart the sim from the `wattchain` folder so Wokwi uploads files.
- If HTTPS fails, the code falls back to HTTP on port 80 automatically. Ensure your backend is reachable from the internet (ngrok), and `diagram.json` includes the host under `net.servers` when using HTTPS.