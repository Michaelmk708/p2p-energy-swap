"""
M-Pesa Daraja API Integration for Energy Trading Platform
Implements STK Push for secure payment processing in the energy trading ecosystem
"""

import requests
import json
import base64
import time
from datetime import datetime
from typing import Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)

class MPesaDarajaAPI:
    """
    M-Pesa Daraja API client with STK Push integration
    Handles authentication, STK Push requests, and payment confirmations
    """
    
    def __init__(self, consumer_key: str, consumer_secret: str, environment: str = 'sandbox'):
        """
        Initialize M-Pesa Daraja API client
        
        Args:
            consumer_key: M-Pesa consumer key from Safaricom Developer Portal
            consumer_secret: M-Pesa consumer secret from Safaricom Developer Portal  
            environment: 'sandbox' or 'production'
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.environment = environment
        
        # API URLs based on environment
        if environment == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
            
        # API endpoints
        self.auth_url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        self.stk_push_url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
        self.stk_query_url = f'{self.base_url}/mpesa/stkpushquery/v1/query'
        
        # Sandbox test credentials (for testing only)
        if environment == 'sandbox':
            self.business_shortcode = '174379'  # Sandbox shortcode
            self.lipa_na_mpesa_online_passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
            self.test_msisdn = '254708374149'  # Sandbox test number
        else:
            # Production values (to be configured)
            self.business_shortcode = None  # Your production shortcode
            self.lipa_na_mpesa_online_passkey = None  # Your production passkey
            
        self.access_token = None
        self.token_expiry = None
        
        logger.info(f"M-Pesa Daraja API initialized for {environment} environment")
    
    def _get_access_token(self) -> Optional[str]:
        """
        Get access token from M-Pesa API
        Tokens are valid for 1 hour, so we cache and reuse them
        """
        # Check if we have a valid token
        if self.access_token and self.token_expiry and time.time() < self.token_expiry:
            return self.access_token
            
        try:
            # Create basic auth string
            auth_string = f'{self.consumer_key}:{self.consumer_secret}'
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(self.auth_url, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            # Set expiry time (tokens last 1 hour, we refresh 5 minutes early)
            self.token_expiry = time.time() + (int(token_data['expires_in']) - 300)
            
            logger.info("Successfully obtained M-Pesa access token")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get M-Pesa access token: {e}")
            return None
        except KeyError as e:
            logger.error(f"Invalid token response format: {e}")
            return None
    
    def _generate_password(self, shortcode: str, passkey: str, timestamp: str) -> str:
        """Generate the password for STK push"""
        password_str = f'{shortcode}{passkey}{timestamp}'
        password_bytes = password_str.encode('ascii')
        return base64.b64encode(password_bytes).decode('ascii')
    
    def initiate_stk_push(self, 
                         phone_number: str, 
                         amount: float, 
                         account_reference: str,
                         transaction_desc: str = "Energy Trading Payment",
                         callback_url: str = None) -> Dict:
        """
        Initiate STK Push payment
        
        Args:
            phone_number: Customer phone number (254XXXXXXXXX format)
            amount: Amount to be paid (minimum 1 KES)
            account_reference: Reference for the payment (e.g., trade ID)
            transaction_desc: Description of the transaction
            callback_url: URL to receive payment confirmation
            
        Returns:
            Dict containing STK push response
        """
        try:
            # Get access token
            token = self._get_access_token()
            if not token:
                return {
                    'success': False,
                    'error': 'Failed to get access token',
                    'error_code': 'TOKEN_ERROR'
                }
            
            # Format phone number (ensure it starts with 254)
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif phone_number.startswith('+254'):
                phone_number = phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self._generate_password(
                self.business_shortcode,
                self.lipa_na_mpesa_online_passkey,
                timestamp
            )
            
            # Default callback URL if not provided
            if not callback_url:
                callback_url = 'https://mydomain.com/path'  # You'll need to update this
            
            # STK Push payload
            payload = {
                'BusinessShortCode': self.business_shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': int(amount),  # M-Pesa expects integer amount
                'PartyA': phone_number,
                'PartyB': self.business_shortcode,
                'PhoneNumber': phone_number,
                'CallBackURL': callback_url,
                'AccountReference': account_reference,
                'TransactionDesc': transaction_desc
            }
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            logger.info(f"Initiating STK Push for {phone_number}, Amount: {amount} KES")
            
            response = requests.post(self.stk_push_url, json=payload, headers=headers)
            response.raise_for_status()
            
            stk_response = response.json()
            
            if stk_response.get('ResponseCode') == '0':
                logger.info(f"STK Push initiated successfully: {stk_response.get('CheckoutRequestID')}")
                return {
                    'success': True,
                    'checkout_request_id': stk_response.get('CheckoutRequestID'),
                    'merchant_request_id': stk_response.get('MerchantRequestID'),
                    'response_code': stk_response.get('ResponseCode'),
                    'response_description': stk_response.get('ResponseDescription'),
                    'customer_message': stk_response.get('CustomerMessage'),
                    'timestamp': timestamp,
                    'amount': amount,
                    'phone_number': phone_number,
                    'account_reference': account_reference
                }
            else:
                logger.error(f"STK Push failed: {stk_response}")
                return {
                    'success': False,
                    'error': stk_response.get('ResponseDescription', 'Unknown error'),
                    'error_code': stk_response.get('ResponseCode', 'UNKNOWN'),
                    'response': stk_response
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"STK Push request failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'REQUEST_ERROR'
            }
        except Exception as e:
            logger.error(f"STK Push unexpected error: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNEXPECTED_ERROR'
            }
    
    def query_stk_status(self, checkout_request_id: str) -> Dict:
        """
        Query STK Push payment status
        
        Args:
            checkout_request_id: CheckoutRequestID from STK push response
            
        Returns:
            Dict containing payment status
        """
        try:
            token = self._get_access_token()
            if not token:
                return {
                    'success': False,
                    'error': 'Failed to get access token',
                    'error_code': 'TOKEN_ERROR'
                }
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self._generate_password(
                self.business_shortcode,
                self.lipa_na_mpesa_online_passkey,
                timestamp
            )
            
            payload = {
                'BusinessShortCode': self.business_shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': checkout_request_id
            }
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(self.stk_query_url, json=payload, headers=headers)
            response.raise_for_status()
            
            query_response = response.json()
            
            logger.info(f"STK Query response: {query_response}")
            
            return {
                'success': True,
                'response_code': query_response.get('ResponseCode'),
                'response_description': query_response.get('ResponseDescription'),
                'merchant_request_id': query_response.get('MerchantRequestID'),
                'checkout_request_id': query_response.get('CheckoutRequestID'),
                'result_code': query_response.get('ResultCode'),
                'result_desc': query_response.get('ResultDesc'),
                'raw_response': query_response
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"STK Query request failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'REQUEST_ERROR'
            }
        except Exception as e:
            logger.error(f"STK Query unexpected error: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNEXPECTED_ERROR'
            }
    
    def process_callback(self, callback_data: Dict) -> Dict:
        """
        Process M-Pesa payment callback
        
        Args:
            callback_data: Callback data from M-Pesa
            
        Returns:
            Dict containing processed callback information
        """
        try:
            # Extract callback information
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            
            merchant_request_id = stk_callback.get('MerchantRequestID')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            callback_metadata = stk_callback.get('CallbackMetadata', {})
            items = callback_metadata.get('Item', [])
            
            # Parse callback metadata
            metadata = {}
            for item in items:
                name = item.get('Name')
                value = item.get('Value')
                if name:
                    metadata[name] = value
            
            # Determine payment status
            if result_code == 0:
                payment_status = 'completed'
                logger.info(f"Payment successful: {checkout_request_id}")
            else:
                payment_status = 'failed'
                logger.warning(f"Payment failed: {result_desc}")
            
            return {
                'success': True,
                'merchant_request_id': merchant_request_id,
                'checkout_request_id': checkout_request_id,
                'result_code': result_code,
                'result_desc': result_desc,
                'payment_status': payment_status,
                'amount': metadata.get('Amount'),
                'receipt_number': metadata.get('MpesaReceiptNumber'),
                'transaction_date': metadata.get('TransactionDate'),
                'phone_number': metadata.get('PhoneNumber'),
                'metadata': metadata,
                'raw_callback': callback_data
            }
            
        except Exception as e:
            logger.error(f"Callback processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'CALLBACK_ERROR',
                'raw_callback': callback_data
            }

# Energy Trading specific M-Pesa integration
class EnergyTradingMPesa(MPesaDarajaAPI):
    """
    M-Pesa integration specifically designed for the energy trading platform
    Handles energy token payments and blockchain integration
    """
    
    def __init__(self, consumer_key: str, consumer_secret: str, environment: str = 'sandbox'):
        super().__init__(consumer_key, consumer_secret, environment)
        self.pending_payments = {}  # Track pending payments
        self.completed_payments = {}  # Track completed payments
    
    def initiate_energy_payment(self, 
                              trade_id: str,
                              buyer_phone: str, 
                              seller_phone: str,
                              amount_kwh: float,
                              price_per_kwh: float,
                              callback_url: str = None) -> Dict:
        """
        Initiate payment for energy trading
        
        Args:
            trade_id: Unique identifier for the energy trade
            buyer_phone: Buyer's phone number
            seller_phone: Seller's phone number  
            amount_kwh: Amount of energy in kWh
            price_per_kwh: Price per kWh in KES
            callback_url: URL for payment confirmation
            
        Returns:
            Dict containing payment initiation result
        """
        total_amount = amount_kwh * price_per_kwh
        
        # Create account reference for energy trading
        account_ref = f"ENERGY_{trade_id}"
        
        # Create transaction description
        transaction_desc = f"Energy purchase: {amount_kwh} kWh at {price_per_kwh} KES/kWh"
        
        # Initiate STK push
        stk_result = self.initiate_stk_push(
            phone_number=buyer_phone,
            amount=total_amount,
            account_reference=account_ref,
            transaction_desc=transaction_desc,
            callback_url=callback_url
        )
        
        if stk_result.get('success'):
            # Store payment details
            checkout_request_id = stk_result.get('checkout_request_id')
            self.pending_payments[checkout_request_id] = {
                'trade_id': trade_id,
                'buyer_phone': buyer_phone,
                'seller_phone': seller_phone,
                'amount_kwh': amount_kwh,
                'price_per_kwh': price_per_kwh,
                'total_amount': total_amount,
                'initiated_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            logger.info(f"Energy payment initiated for trade {trade_id}: {total_amount} KES")
            
            return {
                **stk_result,
                'trade_id': trade_id,
                'total_amount': total_amount,
                'amount_kwh': amount_kwh,
                'price_per_kwh': price_per_kwh
            }
        
        return stk_result
    
    def complete_energy_payment(self, callback_data: Dict) -> Dict:
        """
        Complete energy payment processing after M-Pesa confirmation
        
        Args:
            callback_data: M-Pesa callback data
            
        Returns:
            Dict containing completion result
        """
        callback_result = self.process_callback(callback_data)
        
        if callback_result.get('success'):
            checkout_request_id = callback_result.get('checkout_request_id')
            
            # Get pending payment details
            pending_payment = self.pending_payments.get(checkout_request_id)
            
            if pending_payment:
                # Update payment status
                if callback_result.get('payment_status') == 'completed':
                    # Move to completed payments
                    self.completed_payments[checkout_request_id] = {
                        **pending_payment,
                        'status': 'completed',
                        'completed_at': datetime.now().isoformat(),
                        'mpesa_receipt': callback_result.get('receipt_number'),
                        'mpesa_transaction_date': callback_result.get('transaction_date')
                    }
                    
                    # Remove from pending
                    del self.pending_payments[checkout_request_id]
                    
                    logger.info(f"Energy payment completed for trade {pending_payment['trade_id']}")
                    
                    return {
                        'success': True,
                        'trade_id': pending_payment['trade_id'],
                        'payment_status': 'completed',
                        'amount': callback_result.get('amount'),
                        'receipt_number': callback_result.get('receipt_number'),
                        'energy_details': {
                            'amount_kwh': pending_payment['amount_kwh'],
                            'price_per_kwh': pending_payment['price_per_kwh'],
                            'buyer_phone': pending_payment['buyer_phone'],
                            'seller_phone': pending_payment['seller_phone']
                        }
                    }
                else:
                    # Payment failed
                    pending_payment['status'] = 'failed'
                    pending_payment['failed_at'] = datetime.now().isoformat()
                    pending_payment['failure_reason'] = callback_result.get('result_desc')
                    
                    logger.warning(f"Energy payment failed for trade {pending_payment['trade_id']}: {callback_result.get('result_desc')}")
                    
                    return {
                        'success': False,
                        'trade_id': pending_payment['trade_id'],
                        'payment_status': 'failed',
                        'error': callback_result.get('result_desc')
                    }
            else:
                logger.error(f"No pending payment found for checkout request: {checkout_request_id}")
                return {
                    'success': False,
                    'error': 'Payment record not found',
                    'checkout_request_id': checkout_request_id
                }
        
        return callback_result
    
    def get_payment_status(self, trade_id: str) -> Optional[Dict]:
        """
        Get payment status for a trade
        
        Args:
            trade_id: Trade identifier
            
        Returns:
            Payment status information
        """
        # Check completed payments
        for payment in self.completed_payments.values():
            if payment['trade_id'] == trade_id:
                return payment
        
        # Check pending payments
        for payment in self.pending_payments.values():
            if payment['trade_id'] == trade_id:
                return payment
        
        return None