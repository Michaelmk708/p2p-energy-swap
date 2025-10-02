# Oracle backend (dev)

- `POST /v0` — accepts your current device JSON:
  `{ deviceId, solar_generation, consumption, surplus, deficit, wallet }`
- `POST /v1` — future cumulative counters.

Set RPC/PROGRAM_ID/PORT in `.env`. Run:

```bash
export ANCHOR_WALLET="$HOME/.config/solana/id.json"
npx ts-node backend/index.ts
