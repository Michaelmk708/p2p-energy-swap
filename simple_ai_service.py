#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['GET'])
def predict():
    """Simple AI prediction service"""
    try:
        household = request.args.get('household', 'sim-1')
        live_production = float(request.args.get('live_avg_production', 0))
        live_consumption = float(request.args.get('live_avg_consumption', 0))
        
        # Simple realistic prediction logic
        current_surplus = live_production - live_consumption
        
        # Predict next hour trend with some randomness
        trend_factor = random.uniform(0.8, 1.2)
        predicted_surplus = current_surplus * trend_factor
        
        # Keep deficit reasonable (-12kWh max)
        if predicted_surplus < -12:
            predicted_surplus = -12
        
        # Generate clear reasoning
        if predicted_surplus > 1.0:
            reason = f"Strong solar production ({live_production:.1f}kW) exceeds consumption ({live_consumption:.1f}kW). Expected surplus of {predicted_surplus:.1f}kWh - good time to export to grid."
            recommendation = "export"
        elif predicted_surplus > 0.2:
            reason = f"Moderate surplus expected ({predicted_surplus:.1f}kWh). Solar slightly exceeds usage - consider holding or small export."
            recommendation = "hold"
        elif predicted_surplus > -2.0:
            reason = f"Balanced usage. Consumption ({live_consumption:.1f}kW) nearly matches production ({live_production:.1f}kW) - hold tokens for better opportunities."
            recommendation = "hold"
        else:
            reason = f"High consumption period. Using {live_consumption:.1f}kW vs producing {live_production:.1f}kW. Deficit expected - consider buying tokens if available."
            recommendation = "buy"
            
        return jsonify({
            "household": household,
            "predicted_surplus_kwh": round(predicted_surplus, 2),
            "confidence": random.uniform(0.75, 0.95),
            "recommendation": recommendation,
            "reason": reason,
            "market_suggestion": "export" if predicted_surplus > 0.5 else "buy",
            "timestamp": int(time.time())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "AI Prediction"})

if __name__ == '__main__':
    print("🤖 AI Service starting on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False)