#!/usr/bin/env python3
"""
Simple bridge server for Wokwi telemetry
Runs on port 9000, receives posts from Wokwi, forwards to Django backend
"""
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

class TelemetryHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/telemetry':
            try:
                # Read the body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                print(f"Received: {data}")
                
                # Forward to Django backend
                response = requests.post(
                    'http://127.0.0.1:8000/api/iotcentral/telemetry_bridge/',
                    json=data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"Django response: {response.status_code}")
                
                # Send 200 OK back to Wokwi
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"ok": true}')
                
            except Exception as e:
                print(f"Error: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'{"error": "server error"}')
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 9000), TelemetryHandler)
    print("Wokwi telemetry bridge running on http://0.0.0.0:9000")
    print("Wokwi should POST to: http://host.docker.internal:9000/telemetry")
    server.serve_forever()