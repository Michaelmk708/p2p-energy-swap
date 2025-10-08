#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def _send(self, code=200, obj=None):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(obj or {"ok": True}).encode('utf-8'))

    def do_POST(self):
        if self.path.rstrip('/') == '/mint_energy':
            length = int(self.headers.get('Content-Length', '0') or '0')
            body = self.rfile.read(length) if length else b'{}'
            try:
                data = json.loads(body.decode('utf-8') or '{}')
            except Exception:
                data = {}
            resp = {"success": True, "tx_hash": "stub_tx_" + str(abs(hash(json.dumps(data))))}
            return self._send(200, resp)
        return self._send(404, {"error": "not found"})

def main():
    port = 7000
    print(f"Blockchain stub listening on http://127.0.0.1:{port}")
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()

if __name__ == '__main__':
    main()
