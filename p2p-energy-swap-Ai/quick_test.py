import requests
import json

try:
    response = requests.get("http://localhost:5000/api/predict?household_id=HH_001", timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("SUCCESS! API is working:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection error: {e}")