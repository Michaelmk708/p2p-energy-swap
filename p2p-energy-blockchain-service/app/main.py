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

@app.post('/mint_energy')
async def mint_energy(req: MintRequest, x_api_key: str = Header(None)):
    # Simple API key protection for now
    if not x_api_key or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail='Invalid API key')

    # TODO: Implement Anchor transaction building and signing with oracle keypair
    # For now, return a mock response mimicking a Solana tx
    tx_hash = f"MOCK_MINT_{req.household_id}_{int(os.times().system)}"
    return {
        'success': True,
        'tx_hash': tx_hash,
        'household_id': req.household_id,
        'amount_kwh': req.amount_kwh
    }
