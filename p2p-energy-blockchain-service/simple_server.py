from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
import secrets
import time

app = FastAPI()

class MintRequest(BaseModel):
    household_id: str
    amount_kwh: float
    reason: str = None

@app.get('/health')
async def health():
    return {'status': 'ok'}

@app.post('/mint_energy')
async def mint_energy(req: MintRequest, x_api_key: str = Header(None)):
    # Simple API key check
    if not x_api_key or x_api_key != "test-blockchain-apikey":
        raise HTTPException(status_code=401, detail='Invalid API key')
    
    # Mock blockchain transaction
    tx_hash = f"MOCK_TX_{req.household_id}_{int(time.time())}"
    return {
        'success': True,
        'tx_hash': tx_hash,
        'household_id': req.household_id,
        'amount_kwh': req.amount_kwh
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)