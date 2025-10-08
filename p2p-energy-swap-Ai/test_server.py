#!/usr/bin/env python3
"""
Quick test server to verify if the basic Flask setup works
"""

from flask import Flask, jsonify
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Test server is running', 'status': 'success'})

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'success',
        'message': 'Basic test server',
        'integrations': {
            'test': 'working'
        }
    })

if __name__ == '__main__':
    print("🔧 Starting basic test server...")
    app.run(host='0.0.0.0', port=5001, debug=False)  # Use port 5001 to avoid conflicts