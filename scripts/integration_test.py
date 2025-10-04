#!/usr/bin/env python3
"""Simple integration test: try backend proxy endpoints, fall back to AI + blockchain direct calls
"""
import os
import requests
import json

BACKEND = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')
AI = os.getenv('AI_URL', 'http://127.0.0.1:5000')
BC = os.getenv('BC_URL', 'http://127.0.0.1:7000')
API_KEY = os.getenv('BLOCKCHAIN_SERVICE_API_KEY', 'replace-with-secure-key')

def try_backend_predict():
    try:
        r = requests.get(f"{BACKEND.rstrip('/')}/api/predict/", timeout=10)
        print('backend /api/predict ->', r.status_code)
        print(json.dumps(r.json(), indent=2)[:1000])
        return True
    except Exception as e:
        print('backend predict failed:', e)
        return False

def try_backend_execute_trade():
    try:
        payload = { 'type': 'SELL', 'amount': 1.5, 'price': 0.12 }
        r = requests.post(f"{BACKEND.rstrip('/')}/api/execute_trade/", json=payload, timeout=20)
        print('backend /api/execute_trade ->', r.status_code)
        print(json.dumps(r.json(), indent=2)[:1000])
        return True
    except Exception as e:
        print('backend execute_trade failed:', e)
        return False

def try_backend_mint():
    try:
        payload = { 'household_id': 'HH_TEST_01', 'amount_kwh': 2.0, 'reason': 'integration test' }
        r = requests.post(f"{BACKEND.rstrip('/')}/api/mint_energy/", json=payload, timeout=20)
        print('backend /api/mint_energy ->', r.status_code)
        print(json.dumps(r.json(), indent=2)[:1000])
        return True
    except Exception as e:
        print('backend mint failed:', e)
        return False

def direct_ai_predict():
    try:
        r = requests.get(f"{AI.rstrip('/')}/api/predict", timeout=10)
        print('AI /api/predict ->', r.status_code)
        print(json.dumps(r.json(), indent=2)[:1000])
    except Exception as e:
        print('AI predict failed:', e)

def direct_bc_mint():
    try:
        payload = { 'household_id': 'HH_TEST_01', 'amount_kwh': 2.0, 'reason': 'integration test' }
        headers = { 'x-api-key': API_KEY }
        r = requests.post(f"{BC.rstrip('/')}/mint_energy", json=payload, headers=headers, timeout=10)
        print('BC /mint_energy ->', r.status_code)
        print(json.dumps(r.json(), indent=2)[:1000])
    except Exception as e:
        print('BC mint failed:', e)

if __name__ == '__main__':
    ok = try_backend_predict()
    if not ok:
        direct_ai_predict()

    ok = try_backend_execute_trade()
    if not ok:
        print('Skipping direct AI execute_trade fallback in this script')

    ok = try_backend_mint()
    if not ok:
        direct_bc_mint()
