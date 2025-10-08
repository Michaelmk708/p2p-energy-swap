#!/usr/bin/env python3
"""
Simple M-Pesa STK Push Test
Direct test of the M-Pesa integration with your real credentials
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src path for imports
sys.path.append('src')

try:
    from payments.mpesa_daraja import MPesaDarajaAPI
    
    print("Simple M-Pesa STK Push Test")
    print("=" * 50)
    
    # Check if credentials are loaded
    consumer_key = os.getenv('MPESA_CONSUMER_KEY')
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
    
    if not consumer_key or not consumer_secret:
        print("❌ M-Pesa credentials not found in .env file")
        print("Expected: MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET")
        exit(1)
    
    print("M-Pesa credentials loaded")
    print(f"   Consumer Key: {consumer_key[:10]}...{consumer_key[-5:]}")
    
    # Initialize M-Pesa API
    mpesa = MPesaDarajaAPI(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        environment='sandbox'
    )
    
    print("M-Pesa API initialized for sandbox environment")
    
    # Test STK Push
    print("\nTesting STK Push...")
    phone_number = "254715468617"  # Your phone number
    amount = 30  # 30 KES for 2 kWh at 15 KES/kWh
    
    print(f"   Phone: {phone_number}")
    print(f"   Amount: {amount} KES")
    print(f"   Description: Energy Trading Payment")
    
    result = mpesa.initiate_stk_push(
        phone_number=phone_number,
        amount=amount,
        account_reference="ENR001",
        transaction_desc="AI Energy Trading System - Solar energy purchase"
    )
    
    print(f"\nFull Result: {result}")
    
    print("\nSTK Push Result:")
    print(f"   Status: {result.get('response_code', result.get('ResponseCode', 'Unknown'))}")
    print(f"   Message: {result.get('response_description', result.get('ResponseDescription', 'No message'))}")
    
    # Check for success using either format
    success_code = result.get('response_code') == '0' or result.get('ResponseCode') == '0'
    is_success = result.get('success') == True or success_code
    
    if is_success:
        print("   STK Push initiated successfully!")
        print(f"   Transaction ID: {result.get('checkout_request_id', result.get('CheckoutRequestID', 'N/A'))}")
        print(f"   Merchant Request ID: {result.get('merchant_request_id', result.get('MerchantRequestID', 'N/A'))}")
        
        print("\nNext steps:")
        print(f"   1. Check your phone ({phone_number}) for M-Pesa prompt")
        print("   2. Enter your M-Pesa PIN to complete payment")
        print("   3. Payment callback will be sent to your configured URL")
        
    else:
        print("   STK Push failed!")
        print(f"   Error Code: {result.get('ResponseCode', 'Unknown')}")
        print(f"   Error Message: {result.get('ResponseDescription', 'Unknown error')}")
        
        # Additional debugging
        if 'errorCode' in result:
            print(f"   API Error Code: {result['errorCode']}")
        if 'errorMessage' in result:
            print(f"   API Error Message: {result['errorMessage']}")

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure src/payments/mpesa_daraja.py exists")
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Test completed")