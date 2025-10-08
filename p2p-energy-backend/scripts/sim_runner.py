#!/usr/bin/env python3
import os, json, time, requests, random

BACKEND = os.getenv('BACKEND_BASE', 'http://127.0.0.1:8000')
INGEST = f"{BACKEND.rstrip('/')}/api/iotcentral/ingest/"
SECRET = os.getenv('IOTCENTRAL_WEBHOOK_SECRET') or os.getenv('IOTCENTRAL_SHARED_SECRET') or 'dev'
HEADERS = {'X-Webhook-Secret': SECRET, 'Content-Type': 'application/json'}
TARGETS_URL = f"{BACKEND.rstrip('/')}/api/sim/get_targets/"

# default devices
DEVICES = [
    {'device': os.getenv('SIM1_ID','sim-1'), 'pv_comp': 'pv_array', 'load_comp': 'house_load'},
    {'device': os.getenv('SIM2_ID','sim-2'), 'pv_comp': 'pv_array', 'load_comp': 'house_load'},
]


def get_targets():
    try:
        r = requests.get(TARGETS_URL, timeout=5)
        if r.ok:
            return r.json().get('targets', {})
    except Exception:
        pass
    return {}


def jitter(val, pct=0.05):
    return max(0.0, float(val) * (1.0 + random.uniform(-pct, pct)))


def make_sample(dev, comp, power_kw):
    return {
        'device': dev,
        'component': comp,
        'measurements': {
            'power': round(power_kw, 3)
        },
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }


def loop():
    print("sim_runner: posting telemetry to", INGEST)
    while True:
        targets = get_targets()
        batch = []
        for d in DEVICES:
            dev = d['device']
            pv_t = float(targets.get(dev, {}).get('pv_kw', 0.0))
            load_t = float(targets.get(dev, {}).get('load_kw', 0.0))
            # add small jitter to simulate fluctuation
            if pv_t > 0:
                batch.append(make_sample(dev, d['pv_comp'], jitter(pv_t)))
            if load_t > 0:
                batch.append(make_sample(dev, d['load_comp'], jitter(load_t)))
        if batch:
            try:
                resp = requests.post(INGEST, headers=HEADERS, data=json.dumps(batch), timeout=8)
                if not resp.ok:
                    print('ingest error', resp.status_code, resp.text[:200])
            except Exception as e:
                print('ingest exception', e)
        time.sleep(float(os.getenv('SIM_PERIOD_SEC','2.0')))


if __name__ == '__main__':
    loop()
