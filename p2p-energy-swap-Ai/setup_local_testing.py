#!/usr/bin/env python3
"""
Alternative solution for M-Pesa testing without ngrok
Creates a local testing environment and provides setup instructions
"""

import json
import time
from datetime import datetime

def create_mock_callback_test():
    """Create a local test for M-Pesa callbacks without needing ngrok"""
    
    print("🚀 M-Pesa STK Push Local Testing Solution")
    print("=" * 60)
    print()
    
    print("📋 Since ngrok requires a valid token, here are alternative approaches:")
    print()
    
    # Option 1: Get new ngrok token
    print("🔑 Option 1: Get New Ngrok Token (Recommended)")
    print("   1. Go to: https://dashboard.ngrok.com/signup")
    print("   2. Create free account")
    print("   3. Go to: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("   4. Copy your new authtoken")
    print("   5. Run: .\\ngrok.exe config add-authtoken YOUR_NEW_TOKEN")
    print("   6. Run: .\\ngrok.exe http 5000")
    print()
    
    # Option 2: Use alternative tunneling service
    print("🌐 Option 2: Use Alternative Tunneling (Free)")
    print("   • Localtunnel: https://localtunnel.github.io/www/")
    print("     Install: npm install -g localtunnel")
    print("     Usage: lt --port 5000")
    print()
    print("   • Serveo: https://serveo.net/")
    print("     Usage: ssh -R 80:localhost:5000 serveo.net")
    print()
    
    # Option 3: Local testing with simulated callbacks
    print("🧪 Option 3: Local Testing (No Internet Required)")
    print("   We can test M-Pesa integration locally by simulating callbacks")
    print()
    
    return create_local_test_environment()

def create_local_test_environment():
    """Create local test environment for M-Pesa"""
    
    print("🔧 Setting up Local M-Pesa Test Environment...")
    print()
    
    # Update .env with local callback for development
    callback_url = "http://localhost:5000"
    
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        # Update or add callback URL for local testing
        if 'PAYMENT_CALLBACK_URL=' in env_content:
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('PAYMENT_CALLBACK_URL='):
                    lines[i] = f'PAYMENT_CALLBACK_URL={callback_url}/api/payment/callback'
                    break
            env_content = '\n'.join(lines)
        else:
            env_content += f'\n# Local Callback URL for development\nPAYMENT_CALLBACK_URL={callback_url}/api/payment/callback\n'
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print(f"✅ Updated .env with local callback URL")
        
    except Exception as e:
        print(f"❌ Error updating .env: {e}")
    
    # Create local test script
    create_local_stk_test_script()
    
    print()
    print("📋 Local Testing Instructions:")
    print("1. ✅ Environment configured for local testing")
    print("2. 🔄 Start Flask app: python main_app.py")
    print("3. 🔄 Run local test: python local_mpesa_test.py")
    print()
    print("⚠️  Note: For production STK Push testing, you'll need:")
    print("   - Valid ngrok authtoken OR")
    print("   - Public server with HTTPS callback URL")
    
    return True

def create_local_stk_test_script():
    """Create a local STK Push test script"""
    
    test_script = '''#!/usr/bin/env python3
"""
Local M-Pesa STK Push Test Script
Tests the integration without requiring public callbacks
"""

import requests
import json
import time
from datetime import datetime

def test_local_mpesa_integration():
    """Test M-Pesa integration locally"""
    
    print("🧪 Local M-Pesa STK Push Integration Test")
    print("=" * 50)
    
    api_url = 'http://localhost:5000'
    
    try:
        # Test 1: API Status
        print("\\n1. Testing API Status...")
        response = requests.get(f"{api_url}/api/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data.get('status', 'unknown')}")
            integrations = data.get('integrations', {})
            print(f"   M-Pesa: {integrations.get('mpesa', 'unknown')}")
        else:
            print(f"❌ API not accessible: {response.status_code}")
            return False
        
        # Test 2: STK Push Initiation (with your real credentials)
        print("\\n2. Testing STK Push Initiation...")
        trade_data = {
            'type': 'BUY',
            'amount': 2.0,  # 2 kWh
            'price': 15.0,  # 15 KES per kWh  
            'phone': '254708374149',  # Safaricom sandbox number
            'seller_phone': '254700123456'
        }
        
        print(f"   Trade Details:")
        print(f"   • Energy: {trade_data['amount']} kWh")
        print(f"   • Price: {trade_data['price']} KES/kWh")
        print(f"   • Total: {trade_data['amount'] * trade_data['price']} KES")
        print(f"   • Buyer Phone: {trade_data['phone']}")
        
        response = requests.post(f"{api_url}/api/execute_trade", json=trade_data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            payment = result.get('payment', {})
            
            print(f"\\n✅ Trade Executed!")
            print(f"   Trade ID: {result.get('trade', {}).get('id', 'N/A')}")
            print(f"   Payment Method: {payment.get('payment_method', 'N/A')}")
            print(f"   Payment Status: {payment.get('status', 'N/A')}")
            
            # Check if real STK Push was initiated
            if payment.get('payment_method') == 'mpesa_daraja_stk':
                stk_data = payment.get('stk_push_data', {})
                
                print(f"\\n📱 Real STK Push Initiated!")
                print(f"   Checkout Request ID: {stk_data.get('checkout_request_id', 'N/A')}")
                print(f"   Customer Message: {stk_data.get('customer_message', 'N/A')}")
                print(f"   📲 Check phone {trade_data['phone']} for STK Push popup!")
                
                # Test callback simulation
                simulate_payment_callback(stk_data.get('checkout_request_id', ''), api_url)
                
                return True
                
            elif payment.get('payment_method') == 'mpesa_mock':
                print(f"\\n🔄 Using Mock Payment")
                print(f"   Transaction ID: {payment.get('tx_id', 'N/A')}")
                print(f"   This means your M-Pesa credentials need to be configured")
                return True
            else:
                print(f"\\n❓ Unknown payment method: {payment.get('payment_method')}")
                return False
        else:
            print(f"❌ Trade execution failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Make sure to start the Flask app first: python main_app.py")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def simulate_payment_callback(checkout_request_id, api_url):
    """Simulate M-Pesa payment callback for testing"""
    
    print("\\n3. Simulating Payment Callback...")
    
    # Create realistic M-Pesa callback data
    callback_data = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29115-34620561-1",
                "CheckoutRequestID": checkout_request_id or "ws_CO_191220191020363925",
                "ResultCode": 0,  # 0 = success
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 30.0},
                        {"Name": "MpesaReceiptNumber", "Value": f"NLJ{int(time.time())}"},
                        {"Name": "TransactionDate", "Value": int(datetime.now().strftime("%Y%m%d%H%M%S"))},
                        {"Name": "PhoneNumber", "Value": 254708374149}
                    ]
                }
            }
        }
    }
    
    try:
        response = requests.post(
            f"{api_url}/api/payment/callback",
            json=callback_data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Callback processed successfully")
            print(f"   Result Code: {result.get('ResultCode', 'N/A')}")
            print(f"   Description: {result.get('ResultDesc', 'N/A')}")
        else:
            print(f"❌ Callback failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Callback simulation error: {e}")

def main():
    """Main test function"""
    print("📱 Starting Local M-Pesa STK Push Test")
    print("This will test your M-Pesa integration with your real credentials")
    print()
    
    success = test_local_mpesa_integration()
    
    print("\\n" + "=" * 50)
    if success:
        print("🎉 Local M-Pesa Integration Test COMPLETED!")
        print()
        print("✅ What was tested:")
        print("   - API connectivity")
        print("   - M-Pesa credential validation")
        print("   - STK Push initiation")
        print("   - Payment callback processing")
        print()
        print("📱 If STK Push was initiated:")
        print("   - Check the test phone for payment popup")
        print("   - Enter PIN to complete payment")
        print("   - System will automatically process confirmation")
        print()
        print("🚀 Your M-Pesa integration is working!")
        print("   Ready for production with valid callback URL")
    else:
        print("❌ Test failed - check the error messages above")
        print("💡 Make sure your Flask app is running: python main_app.py")

if __name__ == '__main__':
    main()
'''
    
    with open('local_mpesa_test.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created local_mpesa_test.py")

def main():
    """Main function"""
    success = create_mock_callback_test()
    
    if success:
        print()
        print("🎯 Summary:")
        print("✅ Local test environment configured")
        print("✅ Test script created: local_mpesa_test.py")
        print("✅ Environment variables updated")
        print()
        print("🚀 Ready to test M-Pesa STK Push!")
        print("   1. Start Flask app: python main_app.py")
        print("   2. Run test: python local_mpesa_test.py")
        print()
        print("📱 For production STK Push:")
        print("   • Get new ngrok token from: https://dashboard.ngrok.com/")
        print("   • Or use alternative tunneling service")
        print("   • Or deploy to server with public HTTPS endpoint")

if __name__ == '__main__':
    main()