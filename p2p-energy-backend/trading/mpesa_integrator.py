"""Daraja (M-Pesa) integration helper.

This module provides a small wrapper to request OAuth tokens and initiate STK Push
requests to the Daraja API. It uses environment variables for credentials and is
designed to be safe in demo mode (it will not attempt real API calls if credentials
are missing). Do NOT commit credentials to the repository.
"""
import os
import time
import base64
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)


MPESA_ENV = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET')
CALLBACK_URL = os.getenv('PAYMENT_CALLBACK_URL')
BUSINESS_SHORTCODE = os.getenv('MPESA_BUSINESS_SHORTCODE', '')
PASSKEY = os.getenv('MPESA_PASSKEY', '')


def _daraja_base() -> str:
    return 'https://sandbox.safaricom.co.ke' if MPESA_ENV == 'sandbox' else 'https://api.safaricom.co.ke'


def get_oauth_token(timeout: int = 5) -> Optional[str]:
    """Fetch an OAuth token from Daraja. Returns token or None on failure.

    Requires CONSUMER_KEY and CONSUMER_SECRET to be set.
    """
    if not (CONSUMER_KEY and CONSUMER_SECRET):
        logger.debug('Daraja credentials not configured; skipping real OAuth')
        return None

    try:
        auth = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()
        url = f"{_daraja_base()}/oauth/v1/generate?grant_type=client_credentials"
        headers = {'Authorization': f'Basic {auth}'}
        r = requests.get(url, headers=headers, timeout=timeout)
        if r.status_code == 200:
            token = r.json().get('access_token')
            logger.debug('Retrieved Daraja OAuth token')
            return token
        else:
            logger.warning(f'Daraja token request failed: {r.status_code} {r.text}')
    except Exception as e:
        logger.exception('Error getting Daraja OAuth token')
    return None


def _timestamp() -> str:
    return time.strftime('%Y%m%d%H%M%S')


def _password(shortcode: str, passkey: str, timestamp: str) -> str:
    # Daraja STK password = Base64(BusinessShortCode + Passkey + Timestamp)
    raw = f"{shortcode}{passkey}{timestamp}".encode()
    return base64.b64encode(raw).decode()


def initiate_stk_push(amount_kes: float, phone: str, trade_id: str, description: str = '', timeout: int = 10) -> Dict[str, Any]:
    """Initiate an STK Push against Daraja (if configured).

    Returns a dict with at least keys: success (bool), checkout_request_id (if available), message.
    Falls back to a deterministic demo response when credentials are missing or in demo mode.
    """
    # Demo fallback if configuration not present
    # Decide demo vs real:
    # - If MPESA_DEMO_MODE is explicitly set, honor it.
    # - Otherwise, require core env vars to attempt real calls.
    explicit_demo = os.getenv('MPESA_DEMO_MODE')
    if explicit_demo is not None:
        demo_mode = explicit_demo == '1'
    else:
        demo_mode = not (CONSUMER_KEY and CONSUMER_SECRET and CALLBACK_URL and BUSINESS_SHORTCODE and PASSKEY)

    if demo_mode:
        checkout_request_id = f"DEMO_STK_{trade_id}"
        return {
            'success': True,
            'checkout_request_id': checkout_request_id,
            'merchant_request_id': f"DEMO_MR_{trade_id}",
            'customer_message': 'STK Push simulated (demo mode)',
            'trade_id': trade_id,
            'amount_kes': amount_kes,
        }

    token = get_oauth_token()
    if not token:
        return {'success': False, 'error': 'Unable to obtain Daraja OAuth token'}

    try:
        url = f"{_daraja_base()}/mpesa/stkpush/v1/processrequest"
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

        ts = _timestamp()
        shortcode = BUSINESS_SHORTCODE or os.getenv('MPESA_BUSINESS_SHORTCODE', '')
        passkey = PASSKEY or os.getenv('MPESA_PASSKEY', '')
        password = _password(shortcode, passkey, ts)
        partyb = os.getenv('MPESA_PARTYB') or shortcode

        payload = {
            'BusinessShortCode': shortcode,
            'Password': password,
            'Timestamp': ts,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(round(float(amount_kes))),
            'PartyA': phone,
            'PartyB': partyb,
            'PhoneNumber': phone,
            'CallBackURL': CALLBACK_URL,
            'AccountReference': trade_id,
            'TransactionDesc': description or f'Trade {trade_id}'
        }

        r = requests.post(url, json=payload, headers=headers, timeout=timeout)
        if r.status_code in (200, 201):
            data = r.json()
            return {'success': True, **data}
        else:
            # Try to surface Daraja error details
            try:
                edata = r.json()
            except Exception:
                edata = {'error': r.text}
            msg = edata.get('errorMessage') or edata.get('error') or 'Daraja STK request failed'
            return {'success': False, 'status_code': r.status_code, 'error': msg, 'raw': edata}
    except Exception as e:
        logger.exception('Error initiating STK Push')
        return {'success': False, 'error': str(e)}
