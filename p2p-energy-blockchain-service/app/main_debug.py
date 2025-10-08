from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
import os
import secrets
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('BLOCKCHAIN_SERVICE_API_KEY', 'test-blockchain-apikey')

app = FastAPI(title="P2P Energy Blockchain Service")

class MintRequest(BaseModel):
    household_id: str
    amount_kwh: float
    reason: str | None = None

@app.get('/health')
async def health():
    return {'status': 'ok'}

@app.get('/debug/api-key')
async def debug_api_key():
    return {'api_key': API_KEY, 'env_loaded': os.getenv('BLOCKCHAIN_SERVICE_API_KEY') is not None}

@app.post('/mint_energy')
async def mint_energy(req: MintRequest, x_api_key: str = Header(None)):
    # Simple API key protection for now
    if not x_api_key or not secrets.compare_digest(x_api_key, API_KEY):
        return {
            'error': 'Invalid API key',
            'success': False,
            'debug': {
                'received_key': x_api_key,
                'expected_key': API_KEY,
                'keys_match': x_api_key == API_KEY if x_api_key else False
            }
        }

    # TODO: Implement Anchor transaction building and signing with oracle keypair
    # For now, return a mock response mimicking a Solana tx
    tx_hash = f"MOCK_MINT_{req.household_id}_{int(os.times().system)}"
    return {
        'success': True,
        'tx_hash': tx_hash,
        'household_id': req.household_id,
        'amount_kwh': req.amount_kwh
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)