# P2P Energy Swap (Pilot v1)

## Overview
A Peer-to-Peer energy trading platform for gated communities in Nairobi. 
Bypasses the national grid using private wires and internal ledger settlement.

## Architecture
* **Firmware:** ESP32 / Hexing Meter Integration (C++)
* **Backend:** Django + Time-of-Use Pricing Engine (Python)
* **Frontend:** React Dashboard (Vite)

## Pilot Status
* **Location:** Dedan Kimathi University (DeKUT) Solar Plant
* **Hardware:** STS-Compliant Smart Meters
* **Logic:** Time-of-Use (Off-peak: KES 15 | Peak: KES 35)

## Setup
1. `cd backend && python manage.py runserver`
2. `cd frontend && npm run dev`
3. `python scripts/run_demo.py`