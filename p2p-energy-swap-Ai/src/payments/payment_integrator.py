"""
Payment Integration Factory for Energy Trading Platform
Provides unified interface for different payment providers
"""

from typing import Optional, Dict, Any
from .mpesa_daraja import EnergyTradingMPesa
import os
import logging

logger = logging.getLogger(__name__)

class PaymentIntegrator:
    """
    Unified payment interface for the energy trading platform
    Supports M-Pesa Daraja API and can be extended for other providers
    """
    
    def __init__(self, provider: str = 'mpesa', environment: str = 'sandbox'):
        """
        Initialize payment integrator
        
        Args:
            provider: Payment provider ('mpesa', 'stripe', etc.)
            environment: 'sandbox' or 'production'
        """
        self.provider = provider
        self.environment = environment
        self.client = None
        
        if provider == 'mpesa':
            self._initialize_mpesa()
        else:
            raise ValueError(f"Unsupported payment provider: {provider}")
    
    def _initialize_mpesa(self):
        """Initialize M-Pesa Daraja API client"""
        consumer_key = os.getenv('MPESA_CONSUMER_KEY')
        consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
        
        if not consumer_key or not consumer_secret:
            logger.warning("M-Pesa credentials not found in environment variables")
            # For development/testing, we can still initialize with empty credentials
            consumer_key = consumer_key or 'test_key'
            consumer_secret = consumer_secret or 'test_secret'
        
        self.client = EnergyTradingMPesa(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            environment=self.environment
        )
        
        logger.info(f"Payment integrator initialized with M-Pesa {self.environment}")
    
    def process_energy_payment(self, 
                             trade_id: str,
                             buyer_phone: str,
                             seller_phone: str, 
                             amount_kwh: float,
                             price_per_kwh: float,
                             callback_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Process payment for energy trading
        
        Args:
            trade_id: Unique trade identifier
            buyer_phone: Buyer's phone number
            seller_phone: Seller's phone number
            amount_kwh: Energy amount in kWh
            price_per_kwh: Price per kWh in KES
            callback_url: Payment confirmation callback URL
            
        Returns:
            Dict containing payment processing result
        """
        if self.provider == 'mpesa':
            return self.client.initiate_energy_payment(
                trade_id=trade_id,
                buyer_phone=buyer_phone,
                seller_phone=seller_phone,
                amount_kwh=amount_kwh,
                price_per_kwh=price_per_kwh,
                callback_url=callback_url
            )
        
        raise NotImplementedError(f"Payment processing not implemented for {self.provider}")
    
    def confirm_payment(self, callback_data: Dict) -> Dict[str, Any]:
        """
        Confirm payment from provider callback
        
        Args:
            callback_data: Payment confirmation data from provider
            
        Returns:
            Dict containing confirmation result
        """
        if self.provider == 'mpesa':
            return self.client.complete_energy_payment(callback_data)
        
        raise NotImplementedError(f"Payment confirmation not implemented for {self.provider}")
    
    def get_payment_status(self, trade_id: str) -> Optional[Dict]:
        """
        Get payment status for a trade
        
        Args:
            trade_id: Trade identifier
            
        Returns:
            Payment status information
        """
        if self.provider == 'mpesa':
            return self.client.get_payment_status(trade_id)
        
        raise NotImplementedError(f"Payment status check not implemented for {self.provider}")
    
    def query_transaction_status(self, transaction_ref: str) -> Dict[str, Any]:
        """
        Query transaction status by reference
        
        Args:
            transaction_ref: Transaction reference (e.g., CheckoutRequestID)
            
        Returns:
            Dict containing transaction status
        """
        if self.provider == 'mpesa':
            return self.client.query_stk_status(transaction_ref)
        
        raise NotImplementedError(f"Transaction query not implemented for {self.provider}")

# Global payment integrator instance
payment_integrator = None

def get_payment_integrator(provider: str = 'mpesa', environment: str = 'sandbox') -> PaymentIntegrator:
    """
    Get or create payment integrator instance
    
    Args:
        provider: Payment provider name
        environment: Environment ('sandbox' or 'production')
        
    Returns:
        PaymentIntegrator instance
    """
    global payment_integrator
    
    if payment_integrator is None:
        payment_integrator = PaymentIntegrator(provider=provider, environment=environment)
    
    return payment_integrator