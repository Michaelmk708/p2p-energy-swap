# P2P Energy Swap ⚡️

A browser‑ready peer‑to‑peer energy trading demo that stitches together IoT, AI, blockchain, and mobile money—built for hackathons and live demos.

Ship the full experience in minutes: simulate a live meter, forecast tomorrow with AI, export surplus energy as tokens (1 kWh → 1 token), and settle via M‑Pesa (demo mode), all from a clean dashboard.

---

## Why this exists

- Solar adoption is rising, but prosumers struggle to monetize surplus energy.
- Existing markets are opaque, slow, or require utility‑level integration.
- Communities need a simple way to “see” energy, price it, and trade it safely.

Our goal: create a pragmatic, friendly P2P trading flow that works today with sensible fallbacks and can evolve into production later.

---

## What we built (high‑level)

- Live Meter: Real‑time power from a device (or simulator) via Azure IoT Central → backend → UI
- AI Prediction: Location‑aware forecast for tomorrow with privacy defaults and strong fallbacks
- Export & Mint: Sell surplus; mint 1 token per 1 kWh on a blockchain PoC
- Marketplace: Basic buy/sell primitives and account balance view
- Payments: M‑Pesa STK Push (demo mode out‑of‑the‑box) with webhook + status endpoints

---

## Architecture (at a glance)

- Frontend: `p2p-energy-swap/` — React + Vite + TypeScript
- Backend: `p2p-energy-backend/` — Django + DRF + SimpleJWT
- AI Service: `p2p-energy-swap-Ai/` — Flask microservice returning forecasts + weather
- Blockchain PoC: `p2p-energy-blockchain-service/` (Flask) and a Solana Anchor PoC under `energy-p2p-bc/` (optional)
- IoT Ingestion: Secure REST ingest from Azure IoT Central into per‑device/component state; simulator for demos

Data flow: Device → (optional) Azure IoT Central → Backend (/api/iotcentral/ingest) → /api/iotcentral/latest → Dashboard Live Meter.

---


## Quickstart (works on any dev machine)

Prerequisites
- Linux/macOS, zsh or bash
- Python 3.10+ (with venv)
- Node 18+ (pnpm or npm)
- Optional: ngrok (for external M‑Pesa callback demos)

1) Clone and enter the project

```bash
git clone <your-fork-or-repo-url> p2p-energy
cd p2p-energy
# if your workspace is already at /home/<you>/Desktop/p2p, keep using that path
```

2) Install the CLI helper (adds a `p2p` command)

```bash
# from the repo root (where this README.md lives)
make install-cli   # or: bash ./scripts/install-cli.sh
# ensure ~/.local/bin is on PATH (Linux)
# macOS: you can symlink to /usr/local/bin instead if preferred
```

3) Run the full stack

```bash
p2p run
# then check status
p2p status
# tail logs (optional)
p2p logs all
```

4) Open the app
- Frontend (Vite): http://localhost:5173
- Backend (Django): http://localhost:8000

To stop everything:
```bash
p2p stop
```

Tip: If `p2p` isn’t recognized, run `make run` or execute `./run_all.sh` directly; or add `~/.local/bin` to your PATH.

---

## Configuration (optional, safe defaults included)

- .env at repo root: load into `run_all.sh` for convenience
	- NGROK_AUTHTOKEN: if set, we auto‑start ngrok on port 8000 and export `PAYMENT_CALLBACK_URL`
	- MPESA_*: Consumer key/secret, passkey, shortcode if you want to test sandbox flows
- IoT Central → Backend ingest security: send header `X-Shared-Secret: <your-secret>` when calling `/api/iotcentral/ingest/`
- IoT Central telemetry push (optional): configure backend env `IOTC_BASE_URL`, `IOTC_API_TOKEN`, `IOTC_EXPORT_FIELD` to reflect “exported today” back to IoT tiles
- Frontend env: you can override device/component via Vite env or UI input; URL also supports `?component=<name>`

---

## Using the Dashboard

- Live Meter
	- Matches Azure IoT Central component values; set component via the small input or URL param
- Export flow
	- Enter kWh to export → executes trade → mints tokens (1:1) → updates Token Balance and Energy Exported immediately
	- Guard rails: cannot export > predicted surplus (if available)
- AI Prediction card
	- Shows tomorrow’s forecast for your city, refreshed every 60s
	- Privacy: backend strips lat/lon from responses by default
	- Fallbacks: even if AI is slow or sparse, Expected Production and Predicted Surplus never show zero during daylight

Power user flags
- Force a positive surplus for demo: add `?testSurplus=1` to the URL
- Align the Live Meter with IoT Central exact tile: `?component=YourComponentName`

---

## IoT: simulate or plug in your device

Option A — Quick simulate (no external IoT)
- Backend exposes `/api/iotcentral/simulate/` for one‑off points the UI can read immediately
- Daily accumulator at `/api/iotcentral/daily_exported/` tracks “Energy Exported (today)”

Option B — Azure IoT Central (dev plan)
- Configure a webhook/call from IoT Central to our backend `/api/iotcentral/ingest/` with header `X-Shared-Secret`
- We store per‑device/component “latest” in `/tmp` and serve it to the UI via `/api/iotcentral/latest/`

---

## Payments (M‑Pesa demo)

- Endpoints: `/api/mpesa/stk_push`, `/api/mpesa/callback/`, `/api/mpesa/status`
- If `NGROK_AUTHTOKEN` is set, `run_all.sh` will expose the backend and set `PAYMENT_CALLBACK_URL` automatically
- If not configured, the system uses safe demo fallbacks so your flow still works

---

## Developer ergonomics

- One‑liner dev: `p2p run`, `p2p status`, `p2p logs`, `p2p stop`
- Makefile targets: `make run|stop|status|logs`
- Logs: `/tmp/ai.log`, `/tmp/django.log`, `/tmp/frontend.log`, `/tmp/blockchain.log`, `/tmp/ngrok.log`
- Hot reload: Vite on the frontend; Django runs without autoreload in this demo for simplicity

---

## Security & privacy (demo defaults)

- Coordinates: backend strips lat/lon from AI responses; city name is shown
- Ingest: require `X-Shared-Secret` for IoT Central → backend
- Auth: DRF + JWT for backend APIs (demo‑friendly, adjust for prod)
- This is a hackathon demo; keep secrets out of git and disable `DEBUG` for production

--

---

## Troubleshooting

- `p2p` not found
	- Run `make install-cli` or `bash ./scripts/install-cli.sh` and ensure `~/.local/bin` is on PATH
- Ports in use
	- Backend: 8000, Frontend (Vite): 5173; stop any other apps or change ports
- Live Meter mismatches IoT Central
	- Specify the correct component via the input or `?component=...` in the URL
- Empty AI fields
	- Fallbacks kick in automatically; you can also set system size and baseline in the AI card settings

--
## Quick start — run everything

The repository includes a helper script `run_all.sh` that starts the blockchain PoC, AI service, Django backend, and the frontend, and logs each service to `/tmp/*.log`.

Run it from the repo root (zsh):

```bash
# from repository root
bash ./run_all.sh
```

The script will:
- create virtualenvs where needed (if not already created)
- install requirements (best-effort)
- start services in the background
- write logs to `/tmp/blockchain_terminal.log`, `/tmp/ai_terminal.log`, `/tmp/django_terminal.log`, and `/tmp/frontend_terminal.log` (when frontend used)

To stop all processes started by the script, find and kill their PIDs or restart your shell/session. The script is intended for local demo convenience.

---

## Run services individually

If you prefer to run services manually (useful for debugging), here are the commands used by the helper script.

1) AI microservice (Flask demo)

```bash
cd p2p-energy-swap-Ai
python3 -m venv .venv          # only once
. .venv/bin/activate
pip install -r requirements.txt
# run in demo mode (recommended for local dev)
DEMO_MODE=1 .venv/bin/python main_app.py
# default: listens on 127.0.0.1:5000
```

Log file (if using run_all.sh): `/tmp/ai_terminal.log`

2) Blockchain PoC (Flask)

```bash
cd p2p-energy-blockchain-service
python3 -m venv .venv          # only once
. .venv/bin/activate
pip install -r requirements.txt
# set the API key expected by the PoC and run
BLOCKCHAIN_SERVICE_API_KEY=replace-with-secure-key .venv/bin/python app/flask_app.py
# default: listens on 127.0.0.1:7000
```

Log file (if using run_all.sh): `/tmp/blockchain_terminal.log`

3) Django backend

```bash
cd p2p-energy-backend
python3 -m venv .venv          # only once
. .venv/bin/activate
pip install -r requirements.txt
# run via manage.py
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

Notes:
- If you modify `trading.models` you'll need to run migrations:

```bash
.venv/bin/python manage.py makemigrations
.venv/bin/python manage.py migrate
```

Log file (if using run_all.sh): `/tmp/django_terminal.log`

4) Frontend (Vite / pnpm or npm)

```bash
cd p2p-energy-swap
# use pnpm if available, otherwise npm
pnpm install      # or: npm install
pnpm run dev      # or: npm run dev
# default: Vite serves on http://localhost:5173 (or similar)
```

Log file (if using run_all.sh): `/tmp/frontend_terminal.log`

---
