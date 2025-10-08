Demo / Hackathon Guide

This project supports a full demo mode that does not require paid API keys (Gemini, M-Pesa, or an external blockchain service).

How it works
- Set DEMO_MODE=1 (default) to run using deterministic mock data and fallback models.
- The AI advisor will return deterministic recommendations based on the device surplus/deficit.
- M-Pesa and blockchain interactions are mocked/deterministic so judges can reproduce results quickly.

Run locally (recommended)
1. Create venv and install dependencies:
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt

2. Start the AI service (demo mode enabled by default):
   DEMO_MODE=1 .venv/bin/python main_app.py

3. Test ingestion with the provided script:
   .venv/bin/python scripts/test_iot_post.py

Notes
- For production or integration testing, set GEMINI_API_KEY, MPESA_* keys, and BLOCKCHAIN_SERVICE_URL as needed. The service will automatically use real integrations when keys/URLs are present and DEMO_MODE is not enabled.
- For security, rotate device secrets and use a proper secrets manager in real deployments.
