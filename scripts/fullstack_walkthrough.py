#!/usr/bin/env python3
"""Simulate frontend interactions with the fullstack app.
Register a user, obtain tokens, call predict, execute_trade and mint_energy via backend.
"""
import os
import requests
import time
import json

BACKEND = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')

def register(username='testuser', email='test@example.com', password='Password123'):
    url = f"{BACKEND.rstrip('/')}/api/register/"
    payload = {'username': username, 'email': email, 'password': password}
    r = requests.post(url, json=payload, timeout=10)
    print('register ->', r.status_code, r.text[:400])
    return r.status_code == 201 or r.status_code == 200

def get_tokens(username='testuser', password='Password123'):
    url = f"{BACKEND.rstrip('/')}/api/token/"
    r = requests.post(url, json={'username': username, 'password': password}, timeout=10)
    print('token ->', r.status_code, r.text[:400])
    if r.status_code == 200:
        return r.json()
    return None

def predict(access_token):
    url = f"{BACKEND.rstrip('/')}/api/predict/"
    headers = {'Authorization': f'Bearer {access_token}'}
    r = requests.get(url, headers=headers, timeout=10)
    print('predict ->', r.status_code)
    print(json.dumps(r.json(), indent=2)[:1000])
    return r

def execute_trade(access_token):
    url = f"{BACKEND.rstrip('/')}/api/execute_trade/"
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    payload = {'type': 'SELL', 'amount': 1.0, 'price': 0.12}
    r = requests.post(url, json=payload, headers=headers, timeout=20)
    print('execute_trade ->', r.status_code)
    print(json.dumps(r.json(), indent=2)[:1000])
    return r

def mint_energy(access_token):
    url = f"{BACKEND.rstrip('/')}/api/mint_energy/"
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    payload = {'household_id': 'HH_UI_001', 'amount_kwh': 1.0, 'reason': 'UI test mint'}
    r = requests.post(url, json=payload, headers=headers, timeout=20)
    print('mint_energy ->', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2)[:1000])
    except Exception:
        print('no json body')
    return r

if __name__ == '__main__':
    print('Starting fullstack walkthrough against', BACKEND)
    ok = register()
    time.sleep(0.2)
    tokens = get_tokens()
    if not tokens:
        print('Could not obtain tokens; abort')
        raise SystemExit(1)
    access = tokens.get('access')
    predict(access)
    execute_trade(access)
    mint_energy(access)
