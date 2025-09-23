#!/usr/bin/env python3
"""
Setup ngrok tunnel for M-Pesa callback URL
Configures public callback URL for production M-Pesa testing
"""

import subprocess
import time
import json
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_ngrok_tunnel(port=5000):
    """Start ngrok tunnel and return public URL"""
    print("🚀 Starting ngrok tunnel...")
    print(f"   Exposing port {port} to public internet")
    
    try:
        # Start ngrok tunnel in background
        process = subprocess.Popen(
            ['ngrok', 'http', str(port), '--log=stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for tunnel to establish
        print("   ⏳ Waiting for tunnel to establish...")
        time.sleep(5)
        
        # Get tunnel information from ngrok API
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=10)
            tunnels = response.json()
            
            if tunnels['tunnels']:
                public_url = tunnels['tunnels'][0]['public_url']
                if public_url.startswith('http://'):
                    # Get HTTPS URL if available
                    for tunnel in tunnels['tunnels']:
                        if tunnel['public_url'].startswith('https://'):
                            public_url = tunnel['public_url']
                            break
                
                print(f"   ✅ Tunnel established successfully!")
                print(f"   🌐 Public URL: {public_url}")
                print(f"   🔗 Local URL: http://localhost:{port}")
                
                return public_url, process
            else:
                print("   ❌ No tunnels found")
                return None, process
                
        except requests.exceptions.RequestException:
            print("   ⚠️  Could not fetch tunnel info from ngrok API")
            print("   📝 Please check ngrok status manually at http://localhost:4040")
            return None, process
            
    except FileNotFoundError:
        print("   ❌ ngrok not found in PATH")
        print("   💡 Make sure ngrok is installed and accessible from command line")
        return None, None
    except Exception as e:
        print(f"   ❌ Error starting ngrok: {e}")
        return None, None

def update_env_callback_url(public_url):
    """Update .env file with new callback URL"""
    if not public_url:
        return False
    
    callback_url = f"{public_url}/api/payment/callback"
    validation_url = f"{public_url}/api/payment/validation"
    
    print(f"\n📝 Updating environment configuration...")
    print(f"   Callback URL: {callback_url}")
    print(f"   Validation URL: {validation_url}")
    
    # Read current .env file
    env_path = '.env'
    env_lines = []
    
    try:
        with open(env_path, 'r') as f:
            env_lines = f.readlines()
    except FileNotFoundError:
        print("   ⚠️  .env file not found, creating new one...")
    
    # Update or add callback URLs
    callback_updated = False
    validation_updated = False
    
    for i, line in enumerate(env_lines):
        if line.startswith('PAYMENT_CALLBACK_URL='):
            env_lines[i] = f'PAYMENT_CALLBACK_URL={callback_url}\n'
            callback_updated = True
        elif line.startswith('PAYMENT_VALIDATION_URL='):
            env_lines[i] = f'PAYMENT_VALIDATION_URL={validation_url}\n'
            validation_updated = True
    
    # Add new lines if not found
    if not callback_updated:
        env_lines.append(f'PAYMENT_CALLBACK_URL={callback_url}\n')
    if not validation_updated:
        env_lines.append(f'PAYMENT_VALIDATION_URL={validation_url}\n')
    
    # Write back to .env file
    try:
        with open(env_path, 'w') as f:
            f.writelines(env_lines)
        print("   ✅ Environment file updated successfully!")
        return True
    except Exception as e:
        print(f"   ❌ Failed to update .env file: {e}")
        return False

def test_callback_endpoint(public_url):
    """Test if callback endpoint is accessible"""
    if not public_url:
        return False
    
    callback_url = f"{public_url}/api/payment/callback"
    
    print(f"\n🧪 Testing callback endpoint...")
    print(f"   Testing: {callback_url}")
    
    try:
        # Test with a dummy POST request
        test_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "test_request_id",
                    "CheckoutRequestID": "test_checkout_id",
                    "ResultCode": 0,
                    "ResultDesc": "Test callback"
                }
            }
        }
        
        response = requests.post(
            callback_url,
            json=test_data,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("   ✅ Callback endpoint is accessible!")
            print(f"   📊 Response: {response.status_code}")
            return True
        else:
            print(f"   ⚠️  Callback endpoint returned: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            return True  # Still accessible, just different response
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Callback endpoint not accessible: {e}")
        print("   💡 Make sure your Flask app is running on the specified port")
        return False

def display_integration_info(public_url):
    """Display integration information for M-Pesa configuration"""
    if not public_url:
        return
    
    callback_url = f"{public_url}/api/payment/callback"
    validation_url = f"{public_url}/api/payment/validation"
    
    print(f"\n🔧 M-Pesa Daraja API Configuration")
    print("=" * 60)
    print(f"📍 Use these URLs in your M-Pesa app configuration:")
    print(f"   Callback URL:    {callback_url}")
    print(f"   Validation URL:  {validation_url}")
    print()
    print(f"🌐 ngrok Web Interface: http://localhost:4040")
    print(f"   - View request logs")
    print(f"   - Monitor callback traffic") 
    print(f"   - Inspect HTTP requests")
    print()
    print(f"📋 Next Steps:")
    print(f"   1. Keep this terminal open to maintain the tunnel")
    print(f"   2. Update your M-Pesa app with the callback URLs above")
    print(f"   3. Test M-Pesa STK Push with: python simple_mpesa_test.py")
    print(f"   4. Monitor callbacks at http://localhost:4040")
    print()
    print(f"⚠️  Important:")
    print(f"   - This tunnel is temporary and will close when you stop this script")
    print(f"   - For production, use a permanent domain")
    print(f"   - Keep your ngrok session active during testing")

def main():
    """Main setup function"""
    print("🌞 AI Energy Trading Platform - ngrok Callback Setup")
    print("=" * 60)
    print()
    
    # Check if Flask app is running
    print("🔍 Checking if Flask app is running...")
    try:
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        if response.status_code == 200:
            print("   ✅ Flask app is running!")
        else:
            print("   ⚠️  Flask app is not responding properly")
    except requests.exceptions.RequestException:
        print("   ❌ Flask app is not running!")
        print("   💡 Start your Flask app first: python main_app.py")
        print("   🔄 Then run this script again")
        return
    
    # Start ngrok tunnel
    public_url, process = start_ngrok_tunnel(5000)
    
    if public_url:
        # Update environment file
        update_env_callback_url(public_url)
        
        # Test callback endpoint
        test_callback_endpoint(public_url)
        
        # Display configuration info
        display_integration_info(public_url)
        
        # Keep tunnel alive
        print("\n🔄 Tunnel is active! Press Ctrl+C to stop...")
        try:
            # Keep the script running
            while True:
                time.sleep(60)
                # Periodically check if tunnel is still active
                try:
                    requests.get('http://localhost:4040/api/tunnels', timeout=5)
                except:
                    print("⚠️  ngrok tunnel may have disconnected!")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping ngrok tunnel...")
            if process:
                process.terminate()
            print("✅ Tunnel stopped successfully!")
    else:
        print("\n❌ Failed to establish ngrok tunnel")
        print("💡 Troubleshooting:")
        print("   1. Check if ngrok is installed: ngrok version")
        print("   2. Verify auth token: ngrok config check")
        print("   3. Ensure port 5000 is not in use")
        print("   4. Try manually: ngrok http 5000")

if __name__ == "__main__":
    main()