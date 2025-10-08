# Device → Backend payload contract

Send **cumulative energy counters** (survive restarts). Backend computes deltas and mints tokens.

## JSON payload (POST to /)
```json
{
  "device_id": "esp32-abc123",
  "wallet": "YourWalletBase58",
  "ts": 1733164800,
  "gen_kwh_total": 124.728,
  "cons_kwh_total": 121.210,
  "fw_version": "1.2.0",
  "nonce": 4578123,
  "sig": "<base64-of-HMAC(body, device_secret)>"
}
