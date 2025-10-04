#!/usr/bin/env bash
# Run the full p2p stack (blockchain PoC, AI service, Django backend, frontend) in background.
# Usage:
#   NGROK_AUTHTOKEN="<token>" ./run_all.sh    # will run ngrok and export PAYMENT_CALLBACK_URL
#   Or set PAYMENT_CALLBACK_URL yourself in env before running.
#
# The script stops previously running dev servers, starts each service in its venv,
# redirects logs to /tmp/<service>.log, and prints simple status and tail output.

set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "root: $ROOT_DIR"

# Load optional .env (NGROK_AUTHTOKEN, MPESA_*, etc.)
if [ -f "$ROOT_DIR/.env" ]; then
  echo "Loading env from $ROOT_DIR/.env"
  set -a
  . "$ROOT_DIR/.env"
  set +a
fi

# Helper: safe pkill
safe_kill() {
  pkill -f "$1" || true
}

echo "Stopping previous servers (if any)..."
safe_kill 'manage.py runserver' || true
safe_kill 'main_app.py' || true
safe_kill 'flask_app.py' || true
safe_kill ngrok || true
safe_kill 'vite' || true
safe_kill 'npm' || true
sleep 0.5

# Optional ngrok
NGROK_URL=""
if [ -n "${NGROK_AUTHTOKEN:-}" ]; then
  echo "Configuring ngrok..."
  ngrok authtoken "$NGROK_AUTHTOKEN" >/dev/null 2>&1 || true
  echo "Starting ngrok (http 8000) -> logs /tmp/ngrok.log"
  ngrok http 8000 --log=stdout > /tmp/ngrok.log 2>&1 &
  NGROK_PID=$!
  # wait briefly and attempt to capture url from log
  sleep 1
  NGROK_URL=$(grep -Eo "https://[0-9a-zA-Z._-]+\.ngrok\.[a-z]+" /tmp/ngrok.log | head -1 || true)
  if [ -n "$NGROK_URL" ]; then
    echo "ngrok url: $NGROK_URL"
    export PAYMENT_CALLBACK_URL="$NGROK_URL/api/mpesa/callback/"
  else
    echo "ngrok started but URL not yet available; check /tmp/ngrok.log"
  fi
fi

echo "Starting blockchain PoC (Flask)"
cd "$ROOT_DIR/p2p-energy-blockchain-service"
if [ ! -d .venv ]; then
  python3 -m venv .venv || true
fi
. .venv/bin/activate
pip install -r requirements-min.txt --quiet || true
BLOCKCHAIN_SERVICE_API_KEY=${BLOCKCHAIN_SERVICE_API_KEY:-replace-with-secure-key} .venv/bin/python app/flask_app.py &>/tmp/blockchain.log &
echo "blockchain pid:$! -> /tmp/blockchain.log"

echo "Starting AI service (Flask)"
cd "$ROOT_DIR/p2p-energy-swap-Ai"
if [ ! -d .venv ]; then
  python3 -m venv .venv || true
fi
. .venv/bin/activate
pip install -r requirements.txt --quiet || true
DEMO_MODE=${DEMO_MODE:-1} .venv/bin/python main_app.py &>/tmp/ai.log &
echo "ai pid:$! -> /tmp/ai.log"

echo "Starting Django backend (no autoreload)"
cd "$ROOT_DIR/p2p-energy-backend"
if [ ! -d .venv ]; then
  python3 -m venv .venv || true
fi
. .venv/bin/activate
pip install -r requirements.txt --quiet || true
export DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS:-"localhost,127.0.0.1,0.0.0.0"}
export PAYMENT_CALLBACK_URL=${PAYMENT_CALLBACK_URL:-${PAYMENT_CALLBACK_URL:-}}
export MPESA_CONSUMER_KEY=${MPESA_CONSUMER_KEY:-}
export MPESA_CONSUMER_SECRET=${MPESA_CONSUMER_SECRET:-}
export MPESA_BUSINESS_SHORTCODE=${MPESA_BUSINESS_SHORTCODE:-}
export MPESA_PASSKEY=${MPESA_PASSKEY:-}
echo "DJANGO_ALLOWED_HOSTS=$DJANGO_ALLOWED_HOSTS"
echo "PAYMENT_CALLBACK_URL=${PAYMENT_CALLBACK_URL:-<not-set>}"
echo "MPESA_CONSUMER_KEY=${MPESA_CONSUMER_KEY:+<set>}  MPESA_CONSUMER_SECRET=${MPESA_CONSUMER_SECRET:+<set>}"
echo "MPESA_BUSINESS_SHORTCODE=${MPESA_BUSINESS_SHORTCODE:-<not-set>}  MPESA_PASSKEY=${MPESA_PASSKEY:+<set>}"
PYTHONPATH=.venv/bin/python
PAYMENT_CALLBACK_URL="$PAYMENT_CALLBACK_URL" DJANGO_ALLOWED_HOSTS="$DJANGO_ALLOWED_HOSTS" \
MPESA_CONSUMER_KEY="$MPESA_CONSUMER_KEY" MPESA_CONSUMER_SECRET="$MPESA_CONSUMER_SECRET" \
MPESA_BUSINESS_SHORTCODE="$MPESA_BUSINESS_SHORTCODE" MPESA_PASSKEY="$MPESA_PASSKEY" \
.venv/bin/python manage.py runserver 0.0.0.0:8000 --noreload &>/tmp/django.log &
echo "django pid:$! -> /tmp/django.log"

echo "Starting frontend dev server"
cd "$ROOT_DIR/p2p-energy-swap"
if command -v pnpm >/dev/null 2>&1; then
  pnpm install --silent || true
  pnpm dev &>/tmp/frontend.log &
  echo "frontend pid:$! -> /tmp/frontend.log"
elif command -v npm >/dev/null 2>&1; then
  npm ci --silent || npm install --silent || true
  npm run dev --silent &>/tmp/frontend.log &
  echo "frontend pid:$! -> /tmp/frontend.log"
else
  echo "No pnpm/npm found; frontend not started"
fi

sleep 1
echo
echo "Logs (tail). Use 'tail -f /tmp/<service>.log' to follow." 
echo "--- /tmp/blockchain.log ---"
tail -n 40 /tmp/blockchain.log || true
echo "--- /tmp/ai.log ---"
tail -n 40 /tmp/ai.log || true
echo "--- /tmp/django.log ---"
tail -n 80 /tmp/django.log || true
echo "--- /tmp/frontend.log ---"
tail -n 40 /tmp/frontend.log || true

echo
echo "Done. To stop everything: pkill -f 'manage.py runserver' || pkill -f main_app.py || pkill -f flask_app.py || pkill -f ngrok"
