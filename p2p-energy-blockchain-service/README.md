P2P Energy Blockchain Microservice (scaffold)

This is a minimal FastAPI scaffold that will become the oracle microservice responsible for submitting Anchor/Solana transactions (minting energy tokens, approving orders, etc.).

Endpoints
- GET /health - health check
- POST /mint_energy - mint energy tokens for a household (API-key protected)

Next steps
- Implement Solana/Anchor client logic (anchorpy or solana-py)
- Securely load and manage the oracle keypair (consider Vault or KMS)
- Add logging, metrics, retries, and idempotency

Quick start (development)
1. Create a virtual environment and install deps:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

2. Run the service:
	# Option A (FastAPI uvicorn - requires pydantic build and may fail on some systems):
	BLOCKCHAIN_SERVICE_API_KEY=replace-with-secure-key .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 7000 --reload

	# Option B (Lightweight Flask PoC - recommended for quick local testing):
	BLOCKCHAIN_SERVICE_API_KEY=replace-with-secure-key .venv/bin/python app/flask_app.py

The AI service can call this microservice by setting:
 - BLOCKCHAIN_SERVICE_URL=http://localhost:7000
 - BLOCKCHAIN_SERVICE_API_KEY=replace-with-secure-key
