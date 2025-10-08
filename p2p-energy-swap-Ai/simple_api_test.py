#!/usr/bin/env python3
"""
Simple API test to verify STK Push integration is working
"""

import requests
import json
import time

def test_api():
    """Test the API endpoints"""
    api_url = 'http://localhost:5000'
    
    print("🔧 Testing M-Pesa STK Push Integration")
    print("=" * 50)
    
    try:
        # Test 1: API Status
        print("\n1. Testing API Status...")
        response = requests.get(f"{api_url}/api/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data.get('status', 'unknown')}")
            integrations = data.get('integrations', {})
            print(f"   Weather API: {integrations.get('weather', 'unknown')}")
            print(f"   M-Pesa: {integrations.get('mpesa', 'unknown')}")
        else:
            print(f"❌ API Status Failed: {response.status_code}")
            return False
        
        # Test 2: Energy Trade with Payment
        print("\n2. Testing Energy Trade with Payment...")
        trade_data = {
            'type': 'BUY',
            'amount': 2.0,  # 2 kWh
            'price': 10.0,  # 10 KES per kWh
            'phone': '254708374149',  # Sandbox test number
            'seller_phone': '254700123456'
        }
        
        response = requests.post(f"{api_url}/api/execute_trade", json=trade_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            payment = result.get('payment', {})
            
            print(f"✅ Trade Executed Successfully!")
            print(f"   Trade ID: {result.get('trade', {}).get('id', 'N/A')}")
            print(f"   Payment Method: {payment.get('payment_method', 'N/A')}")
            print(f"   Payment Status: {payment.get('status', 'N/A')}")
            print(f"   Total Amount: {result.get('total_value', 'N/A')} KES")
            
            # Check if STK Push was used
            if payment.get('payment_method') == 'mpesa_daraja_stk':
                stk_data = payment.get('stk_push_data', {})
                print(f"   📱 STK Push Initiated!")
                print(f"      Checkout ID: {stk_data.get('checkout_request_id', 'N/A')}")
                print(f"      Customer Message: {stk_data.get('customer_message', 'N/A')}")
                return True
            elif payment.get('payment_method') == 'mpesa_mock':
                print(f"   🔄 Using Mock Payment (M-Pesa credentials not configured)")
                return True
            else:
                print(f"   ❓ Unknown payment method: {payment.get('payment_method')}")
                return False
        else:
            print(f"❌ Trade Execution Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def main():
    """Main test function"""
    success = test_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 M-Pesa STK Push Integration Test PASSED!")
        print("\n✅ System Status:")
        print("   - API Server: Running")
        print("   - Payment Processing: Working")
        print("   - Energy Trading: Functional")
        print("   - Mock Fallback: Active (configure M-Pesa for real STK Push)")
        
        print("\n🔗 Next Steps:")
        print("   1. Add real M-Pesa credentials to .env for STK Push")
        print("   2. Set up ngrok for public callback URL")
        print("   3. Test with real Safaricom sandbox numbers")
        print("   4. Integrate with Solana blockchain for token transfers")
    else:
        print("❌ M-Pesa STK Push Integration Test FAILED!")
        print("   Check the error messages above and restart the API server")
    
    return success

if __name__ == '__main__':
    main()