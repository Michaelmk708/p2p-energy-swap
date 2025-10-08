#!/usr/bin/env python3
"""
Simple HTTP bridge server for Wokwi device telemetry.
Receives plain HTTP requests from Wokwi and forwards to Django backend.
"""
import http.server
import socketserver
import json
import urllib.request
import urllib.parse
from urllib.error import HTTPError, URLError

class WokwiBridgeHandler(http.server.BaseHTTPRequestHandler):
    
    def do_POST(self):
        if self.path == '/telemetry':
            try:
                # Read the request body
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length == 0:
                    self.send_error(400, "No content")
                    return
                
                post_data = self.rfile.read(content_length)
                
                # Parse JSON data
                raw_data = json.loads(post_data.decode('utf-8'))
                print(f"📥 Received: {raw_data}")
                
                # Handle Wokwi format: {'PV': X, 'Load': Y} -> separate messages
                if 'PV' in raw_data or 'Load' in raw_data:
                    responses = []
                    if 'PV' in raw_data:
                        pv_data = {"device": "sim-1", "component": "pv_array", "data": {"power": raw_data['PV']}}
                        responses.append(self.forward_to_django(pv_data))
                    if 'Load' in raw_data:
                        load_data = {"device": "sim-1", "component": "house_load", "data": {"power": raw_data['Load']}}
                        responses.append(self.forward_to_django(load_data))
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": True, "processed": len(responses)}).encode('utf-8'))
                    return
                
                # Standard format - forward directly
                data = raw_data
                response = self.forward_to_django(data)
                
                # Send success response back to Wokwi
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))
                
            except json.JSONDecodeError as e:
                print(f"✗ JSON decode error: {e}")
                self.send_error(400, f"Invalid JSON: {e}")
                
            except Exception as e:
                print(f"✗ Unexpected error: {e}")
                self.send_error(500, f"Server error: {e}")
        else:
            self.send_error(405, "Method not allowed")
    
    def forward_to_django(self, data):
        """Helper method to forward data to Django"""
        try:
            django_url = 'http://localhost:8000/api/iotcentral/telemetry_bridge/'
            req = urllib.request.Request(
                django_url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                django_response = response.read().decode('utf-8')
            print(f"✓ Forwarded: {data['device']}/{data['component']} = {data['data']['power']}kW -> {django_response}")
            return django_response
        except Exception as e:
            print(f"❌ Forward error: {e}")
            return f'{{"error": "{e}"}}'
    
    def log_message(self, format, *args):
        # Suppress default logging to reduce noise
        pass

def start_bridge_server():
    PORT = 9000
    handler = WokwiBridgeHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"🌉 Wokwi HTTP Bridge starting on port {PORT}")
        print(f"📡 Forwarding telemetry to Django at http://localhost:8000")
        print("🔗 Ready to receive data from Wokwi at http://localhost:9000/telemetry")
        httpd.serve_forever()

if __name__ == "__main__":
    start_bridge_server()