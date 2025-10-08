#!/usr/bin/env python3
"""
Setup script to configure ngrok tunnel for M-Pesa callbacks
This script helps set up ngrok and update the callback URL automatically
"""

import os
import subprocess
import json
import requests
import time

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ngrok_instructions():
    """Provide ngrok installation instructions"""
    print("🔧 Ngrok Installation Required")
    print("=" * 50)
    print("\n📥 To install ngrok:")
    print("1. Go to: https://ngrok.com/download")
    print("2. Download ngrok for Windows")
    print("3. Extract ngrok.exe to a folder in your PATH")
    print("4. Or place ngrok.exe in your current directory")
    print("\n💡 Alternative - Use PowerShell (if you have Chocolatey):")
    print("   choco install ngrok")
    print("\n💡 Alternative - Use PowerShell (if you have Scoop):")
    print("   scoop install ngrok")
    
def configure_ngrok(api_token):
    """Configure ngrok with API token"""
    try:
        print(f"🔑 Configuring ngrok with API token...")
        result = subprocess.run(['ngrok', 'config', 'add-authtoken', api_token], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ngrok configured successfully!")
            return True
        else:
            print(f"❌ Failed to configure ngrok: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error configuring ngrok: {e}")
        return False

def start_ngrok_tunnel(port=5000):
    """Start ngrok tunnel"""
    try:
        print(f"🚀 Starting ngrok tunnel for port {port}...")
        # Start ngrok in background
        process = subprocess.Popen(['ngrok', 'http', str(port), '--log=stdout'], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for ngrok to start
        time.sleep(3)
        
        # Get tunnel info
        tunnel_info = get_ngrok_tunnel_info()
        if tunnel_info:
            return tunnel_info, process
        else:
            print("❌ Failed to get tunnel information")
            return None, process
            
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        return None, None

def get_ngrok_tunnel_info():
    """Get ngrok tunnel information from API"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            for tunnel in tunnels:
                if tunnel.get('proto') == 'https':
                    return tunnel.get('public_url')
        return None
    except Exception as e:
        print(f"❌ Error getting tunnel info: {e}")
        return None

def update_env_callback_url(callback_url):
    """Update .env file with callback URL"""
    try:
        env_file = '.env'
        callback_line = f'PAYMENT_CALLBACK_URL={callback_url}/api/payment/callback\n'
        
        # Read current .env file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update or add callback URL
        found = False
        for i, line in enumerate(lines):
            if line.startswith('PAYMENT_CALLBACK_URL='):
                lines[i] = callback_line
                found = True
                break
        
        if not found:
            lines.append('\n# Ngrok Callback URL\n')
            lines.append(callback_line)
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        print(f"✅ Updated .env with callback URL: {callback_url}/api/payment/callback")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Ngrok Setup for M-Pesa STK Push Testing")
    print("=" * 60)
    
    # Check if ngrok is installed
    if not check_ngrok_installed():
        install_ngrok_instructions()
        print("\n⚠️  Please install ngrok first, then run this script again.")
        return
    
    # Configure ngrok with API token
    api_token = "333FNwRH7Cp4svFWQ2DuC8HrjBf_6qXXv6viYbGFy7P4tvjbr"
    if not configure_ngrok(api_token):
        return
    
    # Start ngrok tunnel
    tunnel_url, process = start_ngrok_tunnel(5000)
    
    if tunnel_url:
        print(f"\n🎉 Ngrok tunnel is running!")
        print(f"📡 Public URL: {tunnel_url}")
        print(f"🔄 Local URL: http://localhost:5000")
        
        # Update .env file
        update_env_callback_url(tunnel_url)
        
        print(f"\n📋 Next Steps:")
        print(f"1. ✅ Ngrok tunnel is running")
        print(f"2. ✅ Callback URL updated in .env")
        print(f"3. 🔄 Start your Flask app: python main_app.py")
        print(f"4. 🔄 Test STK Push: python test_stk_push_integration.py")
        
        print(f"\n🌐 Test URLs:")
        print(f"   Public API: {tunnel_url}/api/status")
        print(f"   Callback: {tunnel_url}/api/payment/callback")
        
        print(f"\n⚠️  Keep this terminal open to maintain the tunnel")
        
        # Keep the script running to monitor ngrok
        try:
            print(f"\n📊 Monitoring ngrok tunnel... (Press Ctrl+C to stop)")
            while True:
                time.sleep(30)
                # Check if tunnel is still active
                current_url = get_ngrok_tunnel_info()
                if not current_url:
                    print("❌ Ngrok tunnel disconnected")
                    break
                elif current_url != tunnel_url:
                    print(f"🔄 Tunnel URL changed: {current_url}")
                    update_env_callback_url(current_url)
                    tunnel_url = current_url
                    
        except KeyboardInterrupt:
            print(f"\n🛑 Stopping ngrok tunnel...")
            if process:
                process.terminate()
            print(f"✅ Ngrok tunnel stopped")
    
    else:
        print("❌ Failed to start ngrok tunnel")

if __name__ == '__main__':
    main()