#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
WOKWI_DIR="$ROOT_DIR/wattchain"

if [ ! -d "$WOKWI_DIR" ]; then
  echo "wattchain folder not found at $WOKWI_DIR" >&2
  exit 1
fi

# Usage: ./scripts/update_wokwi_host.sh [HOST_OR_URL]
# If argument omitted, tries ngrok admin API on 127.0.0.1:4040
ARG_HOST="${1:-}"

normalize_host() {
  local in="$1"
  # Accept full URL or host:port; strip scheme/path and port
  in="${in#http://}"
  in="${in#https://}"
  in="${in%%/*}"
  in="${in%%:*}"
  echo "$in"
}

HOST=""
if [ -n "$ARG_HOST" ]; then
  HOST="$(normalize_host "$ARG_HOST")"
else
  # Try ngrok admin API
  if curl -sS http://127.0.0.1:4040/api/tunnels >/dev/null 2>&1; then
    HOST=$(curl -sS http://127.0.0.1:4040/api/tunnels | sed -n 's/.*\("public_url":"https:\/\/[^"]*\).*/\1/p' | head -n1 | cut -d '"' -f4)
    HOST="$(normalize_host "$HOST")"
  fi
fi

if [ -z "$HOST" ]; then
  echo "Usage: $0 <ngrok-host-or-url>  (example: $0 https://abcd-123.ngrok-free.dev)" >&2
  echo "Or ensure ngrok is running (admin at 127.0.0.1:4040) and re-run without args." >&2
  exit 2
fi

MAIN_PY="$WOKWI_DIR/main.py"
DIAG_JSON="$WOKWI_DIR/diagram.json"

if [ ! -f "$MAIN_PY" ]; then
  echo "main.py not found at $MAIN_PY" >&2
  exit 3
fi
if [ ! -f "$DIAG_JSON" ]; then
  echo "diagram.json not found at $DIAG_JSON" >&2
  exit 4
fi

echo "Updating Wokwi files to host: $HOST"

# Update HOST in main.py
sed -i.bak -E "s/^(HOST\s*=\s*").*("\s*)$/\\1$HOST\\2/" "$MAIN_PY"

# Update net.servers in diagram.json to ["<host>:443"]
tmpfile="$(mktemp)"
python3 - "$DIAG_JSON" "$HOST" >"$tmpfile" <<'PY'
import json, sys
path, host = sys.argv[1], sys.argv[2]
with open(path) as f:
    d = json.load(f)
d.setdefault('net', {})['servers'] = [f"{host}:443"]
print(json.dumps(d, indent=2))
PY
mv "$tmpfile" "$DIAG_JSON"

echo "Done. Open the 'wattchain' project in Wokwi and run the simulator."