#!/usr/bin/env python3
"""
M-Pesa STK Push Integration Test for Energy Trading Platform
Tests the complete flow: Energy Trade → STK Push → Payment Confirmation → Token Transfer
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Test configuration
API_BASE_URL = 'http://localhost:5000'
TEST_PHONE_NUMBER = '254708374149'  # Safaricom sandbox test number
TEST_SELLER_PHONE = '254700123456'

class STKPushTester:
    """Test class for M-Pesa STK Push integration"""
    
    def __init__(self):
        self.api_url = API_BASE_URL
        self.results = []
    
    def log_result(self, test_name, success, details):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
    
    def test_api_status(self):
        """Test if API is running"""
        try:
            response = requests.get(f"{self.api_url}/api/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                mpesa_status = data.get('integrations', {}).get('mpesa', 'unknown')
                self.log_result(
                    "API Status Check", 
                    True, 
                    f"API running, M-Pesa: {mpesa_status}"
                )
                return data
            else:
                self.log_result("API Status Check", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_result("API Status Check", False, str(e))
            return None
    
    def test_energy_trade_with_stk(self):
        """Test energy trade execution with STK Push"""
        try:
            # Test trade data
            trade_data = {
                'type': 'BUY',
                'amount': 2.5,  # 2.5 kWh
                'price': 12.0,  # 12 KES per kWh
                'phone': TEST_PHONE_NUMBER,
                'seller_phone': TEST_SELLER_PHONE,
                'household': 'HH001_Nairobi_Central'
            }
            
            print(f"\n🔄 Initiating energy trade:")
            print(f"   Energy Amount: {trade_data['amount']} kWh")
            print(f"   Price per kWh: {trade_data['price']} KES")
            print(f"   Total Amount: {trade_data['amount'] * trade_data['price']} KES")
            print(f"   Buyer Phone: {trade_data['phone']}")
            print(f"   Seller Phone: {trade_data['seller_phone']}")
            
            response = requests.post(
                f"{self.api_url}/api/execute_trade", 
                json=trade_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                payment_info = result.get('payment', {})
                
                # Check if STK Push was initiated
                if payment_info.get('payment_method') == 'mpesa_daraja_stk':
                    stk_data = payment_info.get('stk_push_data', {})
                    checkout_request_id = stk_data.get('checkout_request_id')
                    customer_message = stk_data.get('customer_message', '')
                    
                    self.log_result(
                        "Energy Trade with STK Push",
                        True,
                        f"STK Push initiated: {customer_message}"
                    )
                    
                    print(f"   📱 STK Push Details:")
                    print(f"      Checkout Request ID: {checkout_request_id}")
                    print(f"      Customer Message: {customer_message}")
                    print(f"      Status: {payment_info.get('status', 'unknown')}")
                    
                    return {
                        'trade_id': result.get('trade', {}).get('id'),
                        'checkout_request_id': checkout_request_id,
                        'payment_info': payment_info,
                        'total_amount': result.get('total_value')
                    }
                    
                elif payment_info.get('payment_method') == 'mpesa_mock':
                    self.log_result(
                        "Energy Trade with STK Push",
                        False,
                        "Fell back to mock payment (M-Pesa credentials not configured)"
                    )
                    return None
                else:
                    self.log_result(
                        "Energy Trade with STK Push",
                        False,
                        f"Unknown payment method: {payment_info.get('payment_method')}"
                    )
                    return None
            else:
                self.log_result(
                    "Energy Trade with STK Push", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Energy Trade with STK Push", False, str(e))
            return None
    
    def test_stk_status_query(self, checkout_request_id):
        """Test STK Push status query"""
        try:
            print(f"\n🔍 Querying STK Push status...")
            print(f"   Checkout Request ID: {checkout_request_id}")
            
            response = requests.get(
                f"{self.api_url}/api/stk/status/{checkout_request_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    status_info = {
                        'result_code': result.get('result_code'),
                        'result_desc': result.get('result_desc'),
                        'response_code': result.get('response_code')
                    }
                    
                    self.log_result(
                        "STK Status Query",
                        True,
                        f"Status retrieved: {result.get('result_desc', 'N/A')}"
                    )
                    
                    print(f"   📊 Status Details:")
                    print(f"      Result Code: {status_info['result_code']}")
                    print(f"      Result Description: {status_info['result_desc']}")
                    print(f"      Response Code: {status_info['response_code']}")
                    
                    return status_info
                else:
                    self.log_result(
                        "STK Status Query", 
                        False, 
                        result.get('error', 'Unknown error')
                    )
                    return None
            else:
                self.log_result(
                    "STK Status Query", 
                    False, 
                    f"HTTP {response.status_code}"
                )
                return None
                
        except Exception as e:
            self.log_result("STK Status Query", False, str(e))
            return None
    
    def test_payment_callback_simulation(self):
        """Test payment callback processing (simulate success)"""
        try:
            print(f"\n🔗 Testing payment callback simulation...")
            
            # Simulate a successful M-Pesa callback
            callback_data = {
                "Body": {
                    "stkCallback": {
                        "MerchantRequestID": "29115-34620561-1",
                        "CheckoutRequestID": "ws_CO_191220191020363925",
                        "ResultCode": 0,
                        "ResultDesc": "The service request is processed successfully.",
                        "CallbackMetadata": {
                            "Item": [
                                {"Name": "Amount", "Value": 30.0},
                                {"Name": "MpesaReceiptNumber", "Value": "NLJ7RT61SV"},
                                {"Name": "TransactionDate", "Value": 20191219102115},
                                {"Name": "PhoneNumber", "Value": 254708374149}
                            ]
                        }
                    }
                }
            }
            
            response = requests.post(
                f"{self.api_url}/api/payment/callback",
                json=callback_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_result(
                    "Payment Callback Simulation",
                    True,
                    f"Callback processed: {result.get('ResultDesc', 'Success')}"
                )
                return result
            else:
                self.log_result(
                    "Payment Callback Simulation",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Payment Callback Simulation", False, str(e))
            return None
    
    def run_comprehensive_test(self):
        """Run comprehensive STK Push integration test"""
        print("🚀 M-Pesa STK Push Integration Test - Energy Trading Platform")
        print("=" * 80)
        print(f"Test Phone Number: {TEST_PHONE_NUMBER}")
        print(f"API Base URL: {self.api_url}")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Test 1: API Status
        print("\n📋 Test 1: API Status Check")
        status_data = self.test_api_status()
        if not status_data:
            print("❌ Cannot proceed - API not accessible")
            return self.generate_report()
        
        # Test 2: Energy Trade with STK Push
        print("\n📋 Test 2: Energy Trade with STK Push")
        trade_result = self.test_energy_trade_with_stk()
        
        if trade_result and trade_result.get('checkout_request_id'):
            # Wait a moment before querying status
            print("\n⏳ Waiting 3 seconds before status query...")
            time.sleep(3)
            
            # Test 3: STK Status Query
            print("\n📋 Test 3: STK Push Status Query")
            self.test_stk_status_query(trade_result['checkout_request_id'])
        
        # Test 4: Callback Processing
        print("\n📋 Test 4: Payment Callback Processing")
        self.test_payment_callback_simulation()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 80)
        print("📊 TEST REPORT SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['details']}")
        
        print("\n💡 Key Points:")
        print("   - STK Push requires M-Pesa sandbox/production credentials")
        print("   - Real payments need actual phone numbers for testing")
        print("   - Callback URL must be publicly accessible (use ngrok for local testing)")
        print("   - System falls back to mock payments if credentials not configured")
        
        print("\n🔗 Next Steps:")
        print("   1. Configure M-Pesa Daraja API credentials in .env file")
        print("   2. Set up ngrok or public callback URL")
        print("   3. Test with real Safaricom sandbox phone numbers")
        print("   4. Integrate with Solana blockchain for token transfers")
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': passed_tests/total_tests if total_tests > 0 else 0,
            'results': self.results
        }

def main():
    """Main test function"""
    tester = STKPushTester()
    
    print("⚡ Energy Trading Platform - M-Pesa STK Push Test")
    print("This will test the complete energy trading → payment → confirmation flow")
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code != 200:
            raise Exception(f"API returned status {response.status_code}")
    except Exception as e:
        print(f"\n❌ ERROR: Cannot connect to API at {API_BASE_URL}")
        print(f"   Details: {e}")
        print(f"\n💡 Make sure to start the API server first:")
        print(f"   python main_app.py")
        return
    
    # Run comprehensive test
    report = tester.run_comprehensive_test()
    
    # Save report
    report_file = f"stk_push_test_report_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    if report['failed'] == 0:
        print("\n🎉 All tests passed! STK Push integration is working correctly.")
    else:
        print(f"\n⚠️  {report['failed']} test(s) failed. Check the details above.")

if __name__ == '__main__':
    main()