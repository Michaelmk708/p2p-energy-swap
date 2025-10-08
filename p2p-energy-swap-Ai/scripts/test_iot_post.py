import requests
import hmac
import hashlib
import json
from datetime import datetime

API_URL = 'http://localhost:5000/api/iot/data'
DEVICE_ID = 'HH001_Nairobi_Central'
SHARED_SECRET = 'supersecretdevicekey123'

payload = {
    'deviceId': DEVICE_ID,
    'timestamp': datetime.now().isoformat(),
    'measurements': {
        'solar_generation_kwh': 4.2,
        'consumption_kwh': 2.1,
        'surplus_deficit_kwh': 2.1,
        'panel_voltage': 240,
        'panel_current': 12.5,
        'battery_level': 90
    }
}

body = json.dumps(payload, separators=(',', ':'), sort_keys=True)
signature = hmac.new(SHARED_SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()

headers = {
    'Content-Type': 'application/json',
    'X-Device-Id': DEVICE_ID,
    'X-Signature': signature
}

resp = requests.post(API_URL, data=body, headers=headers)
print(resp.status_code)
print(resp.text)
