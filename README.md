# p2p-energy local dev README

This repository contains multiple services for a local end-to-end demo: a Django backend, a React + Vite frontend, an AI microservice, and a small blockchain PoC service.

This README lists the recommended commands (zsh) to run each service individually and a convenience script that starts everything for you.

All commands below are intended to run from the repository root: `/home/michael/Desktop/p2p`.

---

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

## Optional: ngrok for public callback URLs (M-Pesa webhooks)

If you need a public callback URL (for Daraja / M-Pesa webhook testing), you can run ngrok and set the `PAYMENT_CALLBACK_URL` environment variable before starting the backend. The `run_all.sh` script can start ngrok automatically if `NGROK_AUTHTOKEN` is set in your environment.

Example (manual):

```bash
# start ngrok on port 8000
ngrok http 8000
# copy the https URL (e.g. https://abc123.ngrok.io) and set:
export PAYMENT_CALLBACK_URL=https://abc123.ngrok.io/api/mpesa/callback/
# then start Django so it can receive callbacks
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

Don't forget to update `DJANGO_ALLOWED_HOSTS` if needed for ngrok hostnames.

---

## Logs and troubleshooting

- Check `/tmp/*.log` when using `run_all.sh`.
- If a service fails to start, run it manually in the foreground to see full errors.
- For frontend errors, open the browser devtools and check console/network logs.

---

## Developer notes

- The AI microservice runs in demo fallback mode by default and returns structured predictions.
- The backend uses a demo M-Pesa integrator unless you provide real `MPESA_CONSUMER_KEY` and `MPESA_CONSUMER_SECRET`.
- Token minting currently calls a local blockchain PoC; swapping to Anchor/AnchorPy requires RPC endpoint and keypair.

---

If you want, I can also:
- Add a small systemd/nix/docker-compose recipe to run everything under a single supervisor.
- Add a one-command convenience Makefile target.

Tell me which you'd prefer and I'll create it.