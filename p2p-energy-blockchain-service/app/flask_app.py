"""
Lightweight Flask scaffold for the Blockchain microservice (PoC)
Provides simple API-key protected endpoints without pydantic dependency.
"""
import os
import secrets
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('BLOCKCHAIN_SERVICE_API_KEY', 'test-blockchain-apikey')
SHARED_SECRET = os.getenv('BLOCKCHAIN_SHARED_SECRET', 'replace-with-shared-secret')
USE_ONCHAIN = os.getenv('USE_ONCHAIN', '0') == '1'
ONCHAIN_RPC = os.getenv('ONCHAIN_RPC')
ONCHAIN_KEYPAIR = os.getenv('ONCHAIN_KEYPAIR')

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/mint_energy', methods=['POST'])
def mint_energy():
    x_api_key = request.headers.get('x-api-key') or request.headers.get('X-API-KEY')
    if not x_api_key or not secrets.compare_digest(x_api_key, API_KEY):
        return jsonify({'success': False, 'error': 'Invalid API key'}), 401

    # Verify HMAC signature if provided
    signature = request.headers.get('X-Signature') or request.headers.get('x-signature')
    if SHARED_SECRET:
        raw = request.get_data() or b''
        import hmac as _hmac
        import hashlib as _hashlib
        expected = _hmac.new(SHARED_SECRET.encode(), raw, _hashlib.sha256).hexdigest()
        if not signature or not secrets.compare_digest(signature, expected):
            return jsonify({'success': False, 'error': 'Invalid or missing signature'}), 401

    data = request.get_json() or {}
    household_id = data.get('household_id')
    amount_kwh = data.get('amount_kwh')
    reason = data.get('reason')

    if not household_id or amount_kwh is None:
        return jsonify({'success': False, 'error': 'Missing household_id or amount_kwh'}), 400

    # TODO: Hook into Anchor/Solana client to submit a real transaction
    tx_hash = None
    if USE_ONCHAIN:
        # Attempt on-chain mint using AnchorPy or solana-py if available
        try:
            # Lazy import to avoid hard dependency
            try:
                from anchorpy import Provider, Wallet, Program
                from solana.rpc.async_api import AsyncClient
            except Exception:
                raise RuntimeError('anchorpy/solana not installed in environment')

            if not ONCHAIN_RPC or not ONCHAIN_KEYPAIR:
                raise RuntimeError('ONCHAIN_RPC and ONCHAIN_KEYPAIR must be set for on-chain mode')

            # NOTE: This code is a stub and requires proper program ID, IDL and keypair management.
            # For the PoC we will not perform a real transaction here. Log the intent and return a placeholder.
            app.logger.info('On-chain mint requested but full Anchor integration is not configured in PoC')
            tx_hash = f'ONCHAIN_PLACEHOLDER_{household_id}_{int(os.times().system)}'
        except Exception as e:
            app.logger.warning(f'On-chain mint failed or not available: {e}')
            # fallback to mock if on-chain isn't possible
            tx_hash = f"MOCK_MINT_{household_id}_{int(os.times().system)}"
    else:
        tx_hash = f"MOCK_MINT_{household_id}_{int(os.times().system)}"

    return jsonify({
        'success': True,
        'tx_hash': tx_hash,
        'household_id': household_id,
        'amount_kwh': amount_kwh,
        'reason': reason
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 7000)))
