# 🌞 AI Energy Trading Platform

> **Revolutionizing Solar Energy Trading with Artificial Intelligence and M-Pesa Integration**

An intelligent solar energy trading system powered by AI, designed for households with solar panels in Kenya. The platform provides real-time trading recommendations, IoT device simulation, weather intelligence, M-Pesa payment integration, and comprehensive analytics.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![M-Pesa Daraja API](https://img.shields.io/badge/M--Pesa-Daraja%20API-orange.svg)](https://developer.safaricom.co.ke/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

```bash
# Clone and setup
git clone <your-repo-url>
cd Solarenergyconsumption

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the system
python main_app.py

# Test the API
curl http://localhost:5000/api/predict
```

## ✨ Features

### 🤖 **AI-Powered Trading Intelligence**
- **Google Gemini AI Integration**: Advanced natural language analysis and trading recommendations
- **Backup ML Model**: Random Forest classifier as fallback when Gemini is unavailable
- **Smart Decision Making**: Considers weather, consumption patterns, and market conditions
- **Confidence Scoring**: Provides confidence levels for all recommendations

### � **Real M-Pesa Payment Integration** 
- **Daraja API Integration**: Production-ready M-Pesa STK Push implementation
- **Real-time Payments**: Instant mobile money transactions for energy trades
- **Payment Callbacks**: Automated payment confirmation and status tracking
- **Transaction Management**: Complete payment history and reconciliation

### 📡 **Smart IoT Simulation**
- **ESP32 Smart Meter Simulation**: Realistic solar generation and consumption data
- **Multi-Household Network**: Simulates entire neighborhood energy ecosystem
- **Real-time Sensor Data**: Solar generation, consumption, voltage, current, battery levels
- **Oracle Integration Ready**: Prepared for blockchain data feeds

### 🌤️ **Weather Intelligence**
- **Real Weather Data**: Integration with Open-Meteo API for accurate forecasts  
- **Solar Generation Prediction**: Weather-based energy production forecasting
- **Alert System**: Weather-based warnings and trading recommendations
- **24-Hour Forecasting**: Hourly predictions for optimal trading decisions

### � **Advanced Analytics**
- **Real-time Dashboard**: Comprehensive system monitoring and performance metrics
- **Trading History**: Complete transaction records and analysis
- **Performance Tracking**: ROI analysis and optimization recommendations  
- **Multi-household Analytics**: Network-wide energy flow and efficiency insights

## 📋 Prerequisites

- **Python 3.8+**
- **Internet connection** (for weather data and M-Pesa API)
- **Safaricom M-Pesa account** (for payment testing)

## 🛠️ Installation

### 1. **Clone the Repository**
```bash
git clone <your-repo-url>
cd Solarenergyconsumption
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
```

**Required Environment Variables:**
```env
# Google Gemini AI (Optional)
GEMINI_API_KEY=your_gemini_api_key_here

# M-Pesa Daraja API (Required for payments)
MPESA_CONSUMER_KEY=your_mpesa_consumer_key
MPESA_CONSUMER_SECRET=your_mpesa_consumer_secret

# Payment Callback URL (for production)
PAYMENT_CALLBACK_URL=https://your-domain.com/api/payment/callback

# Database Configuration
DATABASE_PATH=energy_trading.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
DEBUG_MODE=False
```

### 4. **Get API Keys**

#### **M-Pesa Daraja API** (Required for payments):
1. Visit [Safaricom Developer Portal](https://developer.safaricom.co.ke/)
2. Create an account and register your app
3. Get Consumer Key and Consumer Secret from sandbox
4. For production: Apply for Go-Live approval

#### **Google Gemini AI** (Optional):
1. Visit [Google AI Studio](https://ai.google.dev/)
2. Create project and get API key
3. System works with backup ML model if unavailable

## 🏃‍♂️ Running the System

### **Start the API Server**
```bash
python main_app.py
```

The system will initialize and display:
```
2025-09-22 14:04:12 - INFO - Starting Enhanced AI Energy Trading System v2.0...
2025-09-22 14:04:12 - INFO - Real M-Pesa Daraja API initialized (sandbox)
2025-09-22 14:04:12 - INFO - System initialization complete!
2025-09-22 14:04:12 - INFO - API server ready at http://localhost:5000
```

### **Test the System**
```bash
# Test API status
curl http://localhost:5000/api/status

# Get trading recommendation
curl http://localhost:5000/api/predict?household_id=HH_001

# Test M-Pesa STK Push
python simple_mpesa_test.py
```

## 📚 Complete API Documentation & Frontend Integration Guide

### **🔗 API Base Configuration**
```javascript
// Frontend configuration
const API_BASE_URL = 'http://localhost:5000';  // Development
// const API_BASE_URL = 'https://your-domain.com';  // Production

// Headers for all requests
const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
};
```

### **Core API Endpoints**

#### **🏠 System Information & Health**

##### **GET /** - API Information
```bash
curl http://localhost:5000/
```
**Response:**
```json
{
  "message": "Enhanced AI Energy Trading System API",
  "version": "2.0.0",
  "status": "active",
  "features": [
    "Gemini AI-powered trading recommendations",
    "ESP32 smart meter simulation",
    "Real weather API integration",
    "M-Pesa payment integration",
    "Comprehensive analytics"
  ],
  "endpoints": ["GET /", "GET /api/predict", "POST /api/execute_trade", "..."]
}
```

##### **GET /api/status** - System Health Check
```bash
curl http://localhost:5000/api/status
```
**Response:**
```json
{
  "status": "active",
  "timestamp": "2025-09-22T14:04:12.000Z",
  "system_info": {
    "python_version": "3.8.10",
    "flask_version": "2.0.1",
    "uptime_seconds": 3600
  },
  "integrations": {
    "weather": "connected",
    "gemini_ai": "active",
    "mpesa": "connected",
    "database": "healthy"
  },
  "network_stats": {
    "households": 5,
    "total_trades": 15,
    "total_payments": 8,
    "wallet_balance": 1250.75
  }
}
```

#### **🤖 AI Trading Intelligence**

##### **GET /api/predict** - Get Trading Recommendation
```bash
curl "http://localhost:5000/api/predict?household_id=HH_001"
```
**Frontend Integration:**
```javascript
// React/JavaScript example
async function getTradingRecommendation(householdId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/predict?household_id=${householdId}`, {
      method: 'GET',
      headers: DEFAULT_HEADERS
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching trading recommendation:', error);
    throw error;
  }
}

// Usage in React component
const TradingDashboard = () => {
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    const fetchRecommendation = async () => {
      setLoading(true);
      try {
        const data = await getTradingRecommendation('HH_001');
        setRecommendation(data);
      } catch (error) {
        setError('Failed to load trading recommendation');
      } finally {
        setLoading(false);
      }
    };
    
    fetchRecommendation();
  }, []);
  
  return (
    <div className="trading-dashboard">
      {loading && <LoadingSpinner />}
      {recommendation && (
        <RecommendationCard 
          decision={recommendation.prediction.decision}
          confidence={recommendation.prediction.confidence}
          reasoning={recommendation.prediction.reasoning}
        />
      )}
    </div>
  );
};
```

**Response Structure:**
```json
{
  "status": "success",
  "household_id": "HH_001",
  "prediction": {
    "decision": "SELL",
    "confidence": 0.87,
    "reasoning": "High solar production expected, low consumption predicted",
    "expected_production": 8.5,
    "predicted_consumption": 4.2,
    "surplus_deficit": 4.3,
    "optimal_price": 12.5,
    "best_trading_window": "10:00 AM - 2:00 PM"
  },
  "market_conditions": {
    "current_price": 10.8,
    "price_trend": "increasing",
    "demand_level": "high",
    "supply_level": "medium"
  },
  "weather_data": {
    "temperature": 28.5,
    "cloud_coverage": 15,
    "uv_index": 8.2,
    "wind_speed": 12.5,
    "data_source": "open-meteo"
  },
  "gemini_analysis": {
    "market_insight": "Based on weather patterns and historical data...",
    "risk_assessment": "Low risk for selling, high confidence in production",
    "alternative_scenarios": ["Hold until peak hours", "Partial sell now"]
  }
}
```

##### **GET /api/forecast** - 24-Hour Energy Forecast
```bash
curl "http://localhost:5000/api/forecast?household_id=HH_001&hours=24"
```
**Frontend Integration:**
```javascript
// Chart.js integration example
async function loadEnergyForecast(householdId, hours = 24) {
  const response = await fetch(`${API_BASE_URL}/api/forecast?household_id=${householdId}&hours=${hours}`);
  const data = await response.json();
  
  // Transform for Chart.js
  const chartData = {
    labels: data.forecast.map(item => new Date(item.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'Predicted Production (kWh)',
        data: data.forecast.map(item => item.predicted_production),
        borderColor: 'rgb(255, 193, 7)',
        backgroundColor: 'rgba(255, 193, 7, 0.2)',
      },
      {
        label: 'Predicted Consumption (kWh)',
        data: data.forecast.map(item => item.predicted_consumption),
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
      }
    ]
  };
  
  return chartData;
}
```

#### **📊 Analytics & Monitoring**

##### **GET /api/analytics** - Comprehensive Analytics
```bash
curl "http://localhost:5000/api/analytics?household_id=HH_001&days=7"
```
**Frontend Integration:**
```javascript
// Dashboard analytics component
const AnalyticsDashboard = ({ householdId }) => {
  const [analytics, setAnalytics] = useState(null);
  
  useEffect(() => {
    const fetchAnalytics = async () => {
      const response = await fetch(`${API_BASE_URL}/api/analytics?household_id=${householdId}&days=7`);
      const data = await response.json();
      setAnalytics(data);
    };
    
    fetchAnalytics();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchAnalytics, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [householdId]);
  
  if (!analytics) return <LoadingSpinner />;
  
  return (
    <div className="analytics-grid">
      <MetricCard 
        title="Energy Production" 
        value={`${analytics.energy_metrics.total_production} kWh`}
        change={analytics.energy_metrics.production_change}
      />
      <MetricCard 
        title="Energy Consumption" 
        value={`${analytics.energy_metrics.total_consumption} kWh`}
        change={analytics.energy_metrics.consumption_change}
      />
      <MetricCard 
        title="Trading Revenue" 
        value={`KES ${analytics.financial_metrics.total_revenue}`}
        change={analytics.financial_metrics.revenue_change}
      />
      <ChartComponent data={analytics.performance_trends} />
    </div>
  );
};
```

##### **GET /api/households** - IoT Network Status
```bash
curl http://localhost:5000/api/households
```
**Response:**
```json
{
  "status": "success",
  "network_info": {
    "total_households": 5,
    "active_meters": 5,
    "last_update": "2025-09-22T14:04:12.000Z"
  },
  "households": [
    {
      "id": "HH_001",
      "name": "Nairobi Central",
      "location": {"lat": -1.2921, "lng": 36.8219},
      "current_data": {
        "solar_generation": 4.2,
        "consumption": 2.8,
        "battery_level": 85,
        "grid_status": "connected",
        "surplus_deficit": 1.4
      },
      "device_status": {
        "smart_meter": "online",
        "solar_inverter": "active",
        "battery_system": "charging"
      }
    }
  ]
}
```

#### **💰 Energy Trading & Payment Integration**

##### **POST /api/execute_trade** - Execute Energy Trade with M-Pesa
```bash
curl -X POST http://localhost:5000/api/execute_trade \
  -H "Content-Type: application/json" \
  -d '{
    "type": "BUY",
    "amount": 2.0,
    "price": 15.0,
    "phone": "254715468617",
    "household_id": "HH_001"
  }'
```

**Frontend Integration:**
```javascript
// Trading form component
const TradingForm = ({ householdId }) => {
  const [trade, setTrade] = useState({
    type: 'BUY',
    amount: 0,
    price: 0,
    phone: ''
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  
  const executeTrade = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/execute_trade`, {
        method: 'POST',
        headers: DEFAULT_HEADERS,
        body: JSON.stringify({
          ...trade,
          household_id: householdId
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setResult({
          success: true,
          message: 'Trade executed successfully!',
          transactionId: data.payment_details.checkout_request_id,
          totalAmount: data.trade_details.total_amount
        });
        
        // Show M-Pesa prompt notification
        showNotification('Check your phone for M-Pesa payment prompt');
      } else {
        setResult({
          success: false,
          message: data.message || 'Trade execution failed'
        });
      }
    } catch (error) {
      setResult({
        success: false,
        message: 'Network error. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={executeTrade} className="trading-form">
      <select 
        value={trade.type} 
        onChange={(e) => setTrade({...trade, type: e.target.value})}
      >
        <option value="BUY">Buy Energy</option>
        <option value="SELL">Sell Energy</option>
      </select>
      
      <input
        type="number"
        placeholder="Amount (kWh)"
        value={trade.amount}
        onChange={(e) => setTrade({...trade, amount: parseFloat(e.target.value)})}
      />
      
      <input
        type="number"
        placeholder="Price per kWh (KES)"
        value={trade.price}
        onChange={(e) => setTrade({...trade, price: parseFloat(e.target.value)})}
      />
      
      <input
        type="tel"
        placeholder="Phone Number (254XXXXXXXXX)"
        value={trade.phone}
        onChange={(e) => setTrade({...trade, phone: e.target.value})}
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Processing...' : `${trade.type} Energy`}
      </button>
      
      {result && (
        <div className={`result ${result.success ? 'success' : 'error'}`}>
          {result.message}
          {result.success && (
            <div className="transaction-details">
              <p>Transaction ID: {result.transactionId}</p>
              <p>Total: KES {result.totalAmount}</p>
            </div>
          )}
        </div>
      )}
    </form>
  );
};
```

**Response Structure:**
```json
{
  "status": "success",
  "message": "Trade executed and payment initiated successfully",
  "trade_details": {
    "id": "TXN_20250922_001",
    "type": "BUY",
    "amount_kwh": 2.0,
    "price_per_kwh": 15.0,
    "total_amount": 30.0,
    "timestamp": "2025-09-22T14:04:12.000Z",
    "household_id": "HH_001"
  },
  "payment_details": {
    "status": "initiated",
    "method": "mpesa",
    "checkout_request_id": "ws_CO_22092025141046659708374149",
    "merchant_request_id": "dfe1-4cab-a902-17beb3eb42644459",
    "phone_number": "254715468617",
    "amount": 30.0,
    "account_reference": "ENR001"
  },
  "blockchain_details": {
    "transaction_hash": "mock_blockchain_tx_001",
    "smart_contract_address": "mock_solana_contract",
    "gas_fee": 0.001
  }
}
```
GET /api/households

# Weather alerts
GET /api/alerts
```

#### **💰 Energy Trading & Payments**
```bash
# Execute energy trade with M-Pesa payment
POST /api/execute_trade
Content-Type: application/json

{
  "type": "BUY",
  "amount": 2.0,
  "price": 15.0,
  "phone": "254715468617",
  "household_id": "HH_001"
}
```

#### **💳 M-Pesa Payment Callbacks & Webhooks**

The system automatically handles M-Pesa payment confirmations via webhooks. Frontend applications can monitor payment status through polling or WebSocket connections.

##### **POST /api/payment/callback** - Payment Confirmation (Automated)
```json
// Safaricom sends this automatically when payment is completed
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "dfe1-4cab-a902-17beb3eb42644459",
      "CheckoutRequestID": "ws_CO_22092025141046659708374149",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CallbackMetadata": {
        "Item": [
          {"Name": "Amount", "Value": 30.0},
          {"Name": "MpesaReceiptNumber", "Value": "QGR7KLMX61"},
          {"Name": "PhoneNumber", "Value": 254715468617}
        ]
      }
    }
  }
}
```

##### **Frontend Payment Status Monitoring**
```javascript
// Payment status polling
async function monitorPaymentStatus(checkoutRequestId) {
  const maxAttempts = 30; // 5 minutes with 10-second intervals
  let attempts = 0;
  
  return new Promise((resolve, reject) => {
    const pollStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/payment/status/${checkoutRequestId}`);
        const data = await response.json();
        
        if (data.status === 'completed') {
          resolve({
            success: true,
            receiptNumber: data.mpesa_receipt_number,
            amount: data.amount,
            phone: data.phone_number
          });
        } else if (data.status === 'failed' || data.status === 'cancelled') {
          resolve({
            success: false,
            error: data.error_message
          });
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(pollStatus, 10000); // Poll every 10 seconds
        } else {
          reject(new Error('Payment status check timed out'));
        }
      } catch (error) {
        reject(error);
      }
    };
    
    pollStatus();
  });
}

// Usage in React component
const PaymentMonitor = ({ checkoutRequestId, onPaymentComplete }) => {
  const [paymentStatus, setPaymentStatus] = useState('pending');
  const [timeLeft, setTimeLeft] = useState(300); // 5 minutes
  
  useEffect(() => {
    if (!checkoutRequestId) return;
    
    const monitorPayment = async () => {
      try {
        const result = await monitorPaymentStatus(checkoutRequestId);
        
        if (result.success) {
          setPaymentStatus('completed');
          onPaymentComplete(result);
          showSuccessNotification(`Payment of KES ${result.amount} completed! Receipt: ${result.receiptNumber}`);
        } else {
          setPaymentStatus('failed');
          showErrorNotification(result.error);
        }
      } catch (error) {
        setPaymentStatus('timeout');
        showErrorNotification('Payment verification timed out');
      }
    };
    
    monitorPayment();
    
    // Countdown timer
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(timer);
  }, [checkoutRequestId]);
  
  return (
    <div className="payment-monitor">
      <div className="payment-status">
        <StatusIcon status={paymentStatus} />
        <h3>
          {paymentStatus === 'pending' && 'Waiting for payment...'}
          {paymentStatus === 'completed' && 'Payment successful!'}
          {paymentStatus === 'failed' && 'Payment failed'}
          {paymentStatus === 'timeout' && 'Payment timed out'}
        </h3>
      </div>
      
      {paymentStatus === 'pending' && (
        <div className="payment-instructions">
          <p>Please complete the payment on your phone:</p>
          <ol>
            <li>Check your phone for M-Pesa prompt</li>
            <li>Enter your M-Pesa PIN</li>
            <li>Confirm the payment</li>
          </ol>
          <div className="countdown">
            Time remaining: {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, '0')}
          </div>
        </div>
      )}
    </div>
  );
};
```

## 🔧 **Complete Frontend Integration Examples**

### **React.js Integration**
```jsx
// Complete Energy Trading App Component
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EnergyTradingApp = () => {
  const [household] = useState('HH_001');
  const [recommendation, setRecommendation] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState({});
  
  // API client setup
  const api = axios.create({
    baseURL: 'http://localhost:5000',
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 10000,
  });
  
  // Load dashboard data
  useEffect(() => {
    loadDashboardData();
    
    // Auto-refresh every 2 minutes
    const interval = setInterval(loadDashboardData, 2 * 60 * 1000);
    return () => clearInterval(interval);
  }, [household]);
  
  const loadDashboardData = async () => {
    setLoading(prev => ({ ...prev, dashboard: true }));
    
    try {
      const [recResponse, analyticsResponse] = await Promise.all([
        api.get(`/api/predict?household_id=${household}`),
        api.get(`/api/analytics?household_id=${household}&days=7`)
      ]);
      
      setRecommendation(recResponse.data);
      setAnalytics(analyticsResponse.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      showNotification('Failed to load data. Please refresh.', 'error');
    } finally {
      setLoading(prev => ({ ...prev, dashboard: false }));
    }
  };
  
  const executeTrade = async (tradeData) => {
    setLoading(prev => ({ ...prev, trade: true }));
    
    try {
      const response = await api.post('/api/execute_trade', {
        ...tradeData,
        household_id: household
      });
      
      if (response.data.status === 'success') {
        const { checkout_request_id } = response.data.payment_details;
        
        // Start payment monitoring
        const paymentResult = await monitorPaymentStatus(checkout_request_id);
        
        if (paymentResult.success) {
          showNotification('Trade executed successfully!', 'success');
          loadDashboardData(); // Refresh data
        } else {
          showNotification('Payment failed. Please try again.', 'error');
        }
      }
    } catch (error) {
      showNotification('Trade execution failed.', 'error');
    } finally {
      setLoading(prev => ({ ...prev, trade: false }));
    }
  };
  
  return (
    <div className="energy-trading-app">
      <Header household={household} />
      
      <div className="dashboard-grid">
        <RecommendationCard 
          recommendation={recommendation}
          loading={loading.dashboard}
          onTrade={executeTrade}
        />
        
        <AnalyticsPanel 
          analytics={analytics}
          loading={loading.dashboard}
        />
        
        <EnergyChart 
          householdId={household}
        />
        
        <QuickActions 
          onTrade={executeTrade}
          loading={loading.trade}
        />
      </div>
    </div>
  );
};
```

### **Vue.js Integration**
```vue
<template>
  <div id="energy-app">
    <nav-bar />
    
    <!-- Trading Recommendation Card -->
    <div class="recommendation-card" v-if="recommendation">
      <h2>AI Trading Recommendation</h2>
      <div class="decision" :class="recommendation.prediction.decision.toLowerCase()">
        {{ recommendation.prediction.decision }}
      </div>
      <p class="confidence">
        Confidence: {{ Math.round(recommendation.prediction.confidence * 100) }}%
      </p>
      <p class="reasoning">{{ recommendation.prediction.reasoning }}</p>
      
      <button 
        @click="executeTrade" 
        :disabled="trading"
        class="trade-btn"
      >
        {{ trading ? 'Processing...' : `${recommendation.prediction.decision} Energy` }}
      </button>
    </div>
    
    <!-- Energy Forecast Chart -->
    <div class="forecast-section">
      <h2>24-Hour Energy Forecast</h2>
      <canvas ref="forecastChart"></canvas>
    </div>
    
    <!-- Analytics Dashboard -->
    <analytics-dashboard :household-id="householdId" />
  </div>
</template>

<script>
import axios from 'axios';
import Chart from 'chart.js/auto';

export default {
  name: 'EnergyTradingApp',
  data() {
    return {
      householdId: 'HH_001',
      recommendation: null,
      forecast: null,
      trading: false,
      api: axios.create({
        baseURL: 'http://localhost:5000',
        timeout: 10000
      })
    };
  },
  
  mounted() {
    this.loadData();
    this.setupAutoRefresh();
  },
  
  methods: {
    async loadData() {
      try {
        const [recResponse, forecastResponse] = await Promise.all([
          this.api.get(`/api/predict?household_id=${this.householdId}`),
          this.api.get(`/api/forecast?household_id=${this.householdId}&hours=24`)
        ]);
        
        this.recommendation = recResponse.data;
        this.forecast = forecastResponse.data;
        this.updateForecastChart();
      } catch (error) {
        this.$toast.error('Failed to load energy data');
      }
    },
    
    async executeTrade() {
      if (!this.recommendation) return;
      
      this.trading = true;
      
      try {
        const tradeData = {
          type: this.recommendation.prediction.decision,
          amount: this.recommendation.prediction.surplus_deficit || 2.0,
          price: this.recommendation.prediction.optimal_price || 12.0,
          phone: this.userPhone || '254715468617'
        };
        
        const response = await this.api.post('/api/execute_trade', {
          ...tradeData,
          household_id: this.householdId
        });
        
        if (response.data.status === 'success') {
          this.$toast.success('Trade executed! Check your phone for payment.');
          this.monitorPayment(response.data.payment_details.checkout_request_id);
        }
      } catch (error) {
        this.$toast.error('Trade execution failed');
      } finally {
        this.trading = false;
      }
    },
    
    updateForecastChart() {
      const ctx = this.$refs.forecastChart.getContext('2d');
      
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.forecast.forecast.map(item => 
            new Date(item.timestamp).toLocaleTimeString()
          ),
          datasets: [
            {
              label: 'Production (kWh)',
              data: this.forecast.forecast.map(item => item.predicted_production),
              borderColor: '#ffc107',
              backgroundColor: 'rgba(255, 193, 7, 0.1)',
            },
            {
              label: 'Consumption (kWh)',
              data: this.forecast.forecast.map(item => item.predicted_consumption),
              borderColor: '#007bff',
              backgroundColor: 'rgba(0, 123, 255, 0.1)',
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: '24-Hour Energy Forecast'
            }
          }
        }
      });
    },
    
    setupAutoRefresh() {
      setInterval(() => {
        this.loadData();
      }, 2 * 60 * 1000); // Every 2 minutes
    }
  }
};
</script>
```

### **Angular Integration**
```typescript
// energy-trading.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, interval } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class EnergyTradingService {
  private apiUrl = 'http://localhost:5000';
  
  private httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };
  
  constructor(private http: HttpClient) {}
  
  getRecommendation(householdId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/predict?household_id=${householdId}`);
  }
  
  getForecast(householdId: string, hours: number = 24): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/forecast?household_id=${householdId}&hours=${hours}`);
  }
  
  getAnalytics(householdId: string, days: number = 7): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/analytics?household_id=${householdId}&days=${days}`);
  }
  
  executeTrade(tradeData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/execute_trade`, tradeData, this.httpOptions);
  }
  
  // Real-time data stream
  getRealtimeData(householdId: string): Observable<any> {
    return interval(30000).pipe( // Every 30 seconds
      switchMap(() => this.getRecommendation(householdId))
    );
  }
}

// trading-dashboard.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { EnergyTradingService } from './energy-trading.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-trading-dashboard',
  template: `
    <div class="dashboard-container">
      <h1>Energy Trading Dashboard</h1>
      
      <!-- Recommendation Card -->
      <div class="recommendation-card" *ngIf="recommendation">
        <h2>AI Recommendation</h2>
        <div class="decision-badge" [ngClass]="recommendation.prediction.decision.toLowerCase()">
          {{ recommendation.prediction.decision }}
        </div>
        <p>{{ recommendation.prediction.reasoning }}</p>
        <button 
          (click)="executeTrade()" 
          [disabled]="loading"
          class="btn btn-primary"
        >
          {{ loading ? 'Processing...' : 'Execute Trade' }}
        </button>
      </div>
      
      <!-- Analytics Grid -->
      <div class="analytics-grid">
        <div class="metric-card" *ngFor="let metric of analytics?.key_metrics">
          <h3>{{ metric.name }}</h3>
          <span class="value">{{ metric.value }}</span>
          <span class="change" [ngClass]="metric.change > 0 ? 'positive' : 'negative'">
            {{ metric.change > 0 ? '+' : '' }}{{ metric.change }}%
          </span>
        </div>
      </div>
      
      <!-- Forecast Chart -->
      <div class="chart-container">
        <canvas #forecastChart></canvas>
      </div>
    </div>
  `
})
export class TradingDashboardComponent implements OnInit, OnDestroy {
  householdId = 'HH_001';
  recommendation: any;
  analytics: any;
  loading = false;
  
  private subscriptions: Subscription[] = [];
  
  constructor(private energyService: EnergyTradingService) {}
  
  ngOnInit() {
    this.loadDashboard();
    this.setupRealTimeUpdates();
  }
  
  ngOnDestroy() {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }
  
  loadDashboard() {
    // Load recommendation
    const recSub = this.energyService.getRecommendation(this.householdId)
      .subscribe(data => this.recommendation = data);
    
    // Load analytics
    const analyticsSub = this.energyService.getAnalytics(this.householdId)
      .subscribe(data => this.analytics = data);
    
    this.subscriptions.push(recSub, analyticsSub);
  }
  
  executeTrade() {
    if (!this.recommendation) return;
    
    this.loading = true;
    
    const tradeData = {
      type: this.recommendation.prediction.decision,
      amount: this.recommendation.prediction.surplus_deficit || 2.0,
      price: this.recommendation.prediction.optimal_price || 12.0,
      phone: '254715468617',
      household_id: this.householdId
    };
    
    const tradeSub = this.energyService.executeTrade(tradeData)
      .subscribe({
        next: (response) => {
          if (response.status === 'success') {
            alert('Trade executed successfully! Check your phone for payment.');
            this.loadDashboard(); // Refresh data
          }
          this.loading = false;
        },
        error: (error) => {
          alert('Trade execution failed. Please try again.');
          this.loading = false;
        }
      });
    
    this.subscriptions.push(tradeSub);
  }
  
  setupRealTimeUpdates() {
    const realtimeSub = this.energyService.getRealtimeData(this.householdId)
      .subscribe(data => this.recommendation = data);
    
    this.subscriptions.push(realtimeSub);
  }
}
```

### **Mobile App Integration**

#### **React Native Example**
```javascript
// EnergyTradingAPI.js
import AsyncStorage from '@react-native-async-storage/async-storage';

class EnergyTradingAPI {
  constructor(baseURL = 'http://your-api-domain.com') {
    this.baseURL = baseURL;
    this.timeout = 15000; // 15 seconds for mobile
  }
  
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      timeout: this.timeout,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };
    
    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API Request failed: ${endpoint}`, error);
      throw error;
    }
  }
  
  async getRecommendation(householdId) {
    return this.request(`/api/predict?household_id=${householdId}`);
  }
  
  async executeTrade(tradeData) {
    return this.request('/api/execute_trade', {
      method: 'POST',
      body: JSON.stringify(tradeData)
    });
  }
  
  async getAnalytics(householdId, days = 7) {
    return this.request(`/api/analytics?household_id=${householdId}&days=${days}`);
  }
}

// TradingScreen.js
import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  Alert, 
  ActivityIndicator,
  TextInput,
  StyleSheet 
} from 'react-native';
import { EnergyTradingAPI } from '../services/EnergyTradingAPI';

const TradingScreen = ({ householdId = 'HH_001' }) => {
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tradeData, setTradeData] = useState({
    phone: '254715468617',
    amount: '2.0',
    price: '15.0'
  });
  
  const api = new EnergyTradingAPI();
  
  useEffect(() => {
    loadRecommendation();
  }, [householdId]);
  
  const loadRecommendation = async () => {
    setLoading(true);
    try {
      const data = await api.getRecommendation(householdId);
      setRecommendation(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load trading recommendation');
    } finally {
      setLoading(false);
    }
  };
  
  const executeTrade = async () => {
    if (!recommendation) return;
    
    setLoading(true);
    
    try {
      const trade = {
        type: recommendation.prediction.decision,
        amount: parseFloat(tradeData.amount),
        price: parseFloat(tradeData.price),
        phone: tradeData.phone,
        household_id: householdId
      };
      
      const response = await api.executeTrade(trade);
      
      if (response.status === 'success') {
        Alert.alert(
          'Trade Executed!',
          `Please check your phone for M-Pesa payment prompt.\n\nAmount: KES ${trade.amount * trade.price}\nTransaction ID: ${response.payment_details.checkout_request_id}`,
          [{ text: 'OK', onPress: loadRecommendation }]
        );
      } else {
        Alert.alert('Trade Failed', response.message || 'Unknown error occurred');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to execute trade. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  if (loading && !recommendation) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007bff" />
        <Text>Loading recommendation...</Text>
      </View>
    );
  }
  
  return (
    <View style={styles.container}>
      {recommendation && (
        <View style={styles.recommendationCard}>
          <Text style={styles.title}>AI Trading Recommendation</Text>
          
          <View style={[
            styles.decisionBadge, 
            { backgroundColor: recommendation.prediction.decision === 'SELL' ? '#28a745' : '#007bff' }
          ]}>
            <Text style={styles.decisionText}>{recommendation.prediction.decision}</Text>
          </View>
          
          <Text style={styles.confidence}>
            Confidence: {Math.round(recommendation.prediction.confidence * 100)}%
          </Text>
          
          <Text style={styles.reasoning}>{recommendation.prediction.reasoning}</Text>
          
          <View style={styles.metrics}>
            <Text>Expected Production: {recommendation.prediction.expected_production} kWh</Text>
            <Text>Predicted Consumption: {recommendation.prediction.predicted_consumption} kWh</Text>
            <Text>Optimal Price: KES {recommendation.prediction.optimal_price}</Text>
          </View>
        </View>
      )}
      
      <View style={styles.tradeForm}>
        <Text style={styles.formTitle}>Execute Trade</Text>
        
        <TextInput
          style={styles.input}
          placeholder="Phone Number (254XXXXXXXXX)"
          value={tradeData.phone}
          onChangeText={(text) => setTradeData({...tradeData, phone: text})}
          keyboardType="phone-pad"
        />
        
        <TextInput
          style={styles.input}
          placeholder="Amount (kWh)"
          value={tradeData.amount}
          onChangeText={(text) => setTradeData({...tradeData, amount: text})}
          keyboardType="decimal-pad"
        />
        
        <TextInput
          style={styles.input}
          placeholder="Price per kWh (KES)"
          value={tradeData.price}
          onChangeText={(text) => setTradeData({...tradeData, price: text})}
          keyboardType="decimal-pad"
        />
        
        <TouchableOpacity 
          style={[styles.button, loading && styles.buttonDisabled]} 
          onPress={executeTrade}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>
              {recommendation ? `${recommendation.prediction.decision} Energy` : 'Execute Trade'}
            </Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#f8f9fa' },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  recommendationCard: { 
    backgroundColor: 'white', 
    padding: 20, 
    borderRadius: 10, 
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3
  },
  title: { fontSize: 18, fontWeight: 'bold', marginBottom: 15 },
  decisionBadge: { 
    padding: 10, 
    borderRadius: 5, 
    alignItems: 'center', 
    marginBottom: 10 
  },
  decisionText: { color: 'white', fontWeight: 'bold', fontSize: 16 },
  confidence: { fontSize: 14, color: '#666', marginBottom: 10 },
  reasoning: { fontSize: 14, marginBottom: 15 },
  metrics: { backgroundColor: '#f8f9fa', padding: 10, borderRadius: 5 },
  tradeForm: { backgroundColor: 'white', padding: 20, borderRadius: 10 },
  formTitle: { fontSize: 16, fontWeight: 'bold', marginBottom: 15 },
  input: { 
    borderWidth: 1, 
    borderColor: '#ddd', 
    padding: 12, 
    borderRadius: 5, 
    marginBottom: 15 
  },
  button: { 
    backgroundColor: '#007bff', 
    padding: 15, 
    borderRadius: 5, 
    alignItems: 'center' 
  },
  buttonDisabled: { backgroundColor: '#ccc' },
  buttonText: { color: 'white', fontWeight: 'bold', fontSize: 16 }
});

export default TradingScreen;
```

#### **Flutter Example**
```dart
// energy_trading_service.dart
import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;

class EnergyTradingService {
  final String baseUrl;
  final Duration timeout;
  
  EnergyTradingService({
    this.baseUrl = 'http://your-api-domain.com',
    this.timeout = const Duration(seconds: 15)
  });
  
  Future<Map<String, dynamic>> _request(String endpoint, {
    String method = 'GET',
    Map<String, dynamic>? body,
    Map<String, String>? headers,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');
    final defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    http.Response response;
    
    try {
      switch (method.toUpperCase()) {
        case 'POST':
          response = await http.post(
            uri,
            headers: {...defaultHeaders, ...?headers},
            body: body != null ? json.encode(body) : null,
          ).timeout(timeout);
          break;
        case 'GET':
        default:
          response = await http.get(
            uri,
            headers: {...defaultHeaders, ...?headers},
          ).timeout(timeout);
          break;
      }
      
      if (response.statusCode >= 200 && response.statusCode < 300) {
        return json.decode(response.body);
      } else {
        throw Exception('HTTP ${response.statusCode}: ${response.reasonPhrase}');
      }
    } catch (e) {
      print('API Request failed: $endpoint - $e');
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>> getRecommendation(String householdId) async {
    return _request('/api/predict?household_id=$householdId');
  }
  
  Future<Map<String, dynamic>> executeTrade(Map<String, dynamic> tradeData) async {
    return _request('/api/execute_trade', method: 'POST', body: tradeData);
  }
  
  Future<Map<String, dynamic>> getAnalytics(String householdId, {int days = 7}) async {
    return _request('/api/analytics?household_id=$householdId&days=$days');
  }
}

// trading_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/energy_trading_service.dart';

class TradingScreen extends StatefulWidget {
  final String householdId;
  
  const TradingScreen({Key? key, this.householdId = 'HH_001'}) : super(key: key);
  
  @override
  State<TradingScreen> createState() => _TradingScreenState();
}

class _TradingScreenState extends State<TradingScreen> {
  final EnergyTradingService _api = EnergyTradingService();
  final _phoneController = TextEditingController(text: '254715468617');
  final _amountController = TextEditingController(text: '2.0');
  final _priceController = TextEditingController(text: '15.0');
  
  Map<String, dynamic>? recommendation;
  bool loading = false;
  
  @override
  void initState() {
    super.initState();
    _loadRecommendation();
  }
  
  Future<void> _loadRecommendation() async {
    setState(() => loading = true);
    
    try {
      final data = await _api.getRecommendation(widget.householdId);
      setState(() => recommendation = data);
    } catch (e) {
      _showErrorDialog('Failed to load trading recommendation');
    } finally {
      setState(() => loading = false);
    }
  }
  
  Future<void> _executeTrade() async {
    if (recommendation == null) return;
    
    setState(() => loading = true);
    
    try {
      final tradeData = {
        'type': recommendation!['prediction']['decision'],
        'amount': double.parse(_amountController.text),
        'price': double.parse(_priceController.text),
        'phone': _phoneController.text,
        'household_id': widget.householdId,
      };
      
      final response = await _api.executeTrade(tradeData);
      
      if (response['status'] == 'success') {
        final paymentDetails = response['payment_details'];
        final totalAmount = tradeData['amount']! * tradeData['price']!;
        
        _showSuccessDialog(
          'Trade Executed!',
          'Please check your phone for M-Pesa payment prompt.\n\n'
          'Amount: KES ${totalAmount.toStringAsFixed(2)}\n'
          'Transaction ID: ${paymentDetails['checkout_request_id']}'
        );
        
        _loadRecommendation(); // Refresh data
      } else {
        _showErrorDialog(response['message'] ?? 'Unknown error occurred');
      }
    } catch (e) {
      _showErrorDialog('Failed to execute trade. Please try again.');
    } finally {
      setState(() => loading = false);
    }
  }
  
  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Error'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
  
  void _showSuccessDialog(String title, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Energy Trading'),
        backgroundColor: Colors.blue,
      ),
      body: loading && recommendation == null
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Loading recommendation...'),
                ],
              ),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  if (recommendation != null) ...[
                    _buildRecommendationCard(),
                    const SizedBox(height: 20),
                  ],
                  _buildTradeForm(),
                ],
              ),
            ),
    );
  }
  
  Widget _buildRecommendationCard() {
    final prediction = recommendation!['prediction'];
    final decision = prediction['decision'];
    final confidence = (prediction['confidence'] * 100).round();
    
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'AI Trading Recommendation',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 15),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: decision == 'SELL' ? Colors.green : Colors.blue,
                borderRadius: BorderRadius.circular(5),
              ),
              child: Text(
                decision,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ),
            const SizedBox(height: 10),
            Text(
              'Confidence: $confidence%',
              style: const TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 10),
            Text(prediction['reasoning']),
            const SizedBox(height: 15),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(5),
              ),
              child: Column(
                children: [
                  _buildMetricRow('Expected Production', '${prediction['expected_production']} kWh'),
                  _buildMetricRow('Predicted Consumption', '${prediction['predicted_consumption']} kWh'),
                  _buildMetricRow('Optimal Price', 'KES ${prediction['optimal_price']}'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildMetricRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
  
  Widget _buildTradeForm() {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Execute Trade',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 15),
            TextField(
              controller: _phoneController,
              decoration: const InputDecoration(
                labelText: 'Phone Number',
                hintText: '254XXXXXXXXX',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: 15),
            TextField(
              controller: _amountController,
              decoration: const InputDecoration(
                labelText: 'Amount (kWh)',
                border: OutlineInputBorder(),
              ),
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
            ),
            const SizedBox(height: 15),
            TextField(
              controller: _priceController,
              decoration: const InputDecoration(
                labelText: 'Price per kWh (KES)',
                border: OutlineInputBorder(),
              ),
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: loading ? null : _executeTrade,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                ),
                child: loading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : Text(
                        recommendation != null 
                            ? '${recommendation!['prediction']['decision']} Energy'
                            : 'Execute Trade',
                        style: const TextStyle(fontSize: 16, color: Colors.white),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  @override
  void dispose() {
    _phoneController.dispose();
    _amountController.dispose();
    _priceController.dispose();
    super.dispose();
  }
}
```

## 📱 **API Integration Best Practices**

### **Error Handling**
```javascript
// Comprehensive error handling
class APIClient {
  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        timeout: 15000,
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      });
      
      // Handle different HTTP status codes
      if (response.status === 401) {
        throw new Error('Authentication failed. Please login again.');
      } else if (response.status === 403) {
        throw new Error('Access denied. Insufficient permissions.');
      } else if (response.status === 429) {
        throw new Error('Too many requests. Please try again later.');
      } else if (response.status >= 500) {
        throw new Error('Server error. Please try again later.');
      } else if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      // Log error for debugging
      console.error(`API Error [${endpoint}]:`, error);
      
      // Re-throw with user-friendly message
      if (error.name === 'TimeoutError') {
        throw new Error('Request timed out. Please check your internet connection.');
      } else if (error.name === 'NetworkError') {
        throw new Error('Network error. Please check your connection.');
      }
      
      throw error;
    }
  }
}
```

### **Caching Strategy**
```javascript
// Frontend caching for better performance
class CachedAPIClient {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
  }
  
  async getWithCache(endpoint, options = {}) {
    const cacheKey = `${endpoint}${JSON.stringify(options)}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }
    
    const data = await this.request(endpoint, options);
    this.cache.set(cacheKey, { data, timestamp: Date.now() });
    
    return data;
  }
  
  clearCache(pattern) {
    if (pattern) {
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) {
          this.cache.delete(key);
        }
      }
    } else {
      this.cache.clear();
    }
  }
}
```

### **Real-time Data Updates**
```javascript
// WebSocket-like polling for real-time updates
class RealTimeDataManager {
  constructor(apiClient) {
    this.apiClient = apiClient;
    this.subscribers = new Map();
    this.intervals = new Map();
  }
  
  subscribe(endpoint, callback, interval = 30000) {
    const id = Math.random().toString(36).substr(2, 9);
    
    this.subscribers.set(id, { endpoint, callback, interval });
    
    // Initial fetch
    this.fetchAndNotify(endpoint, callback);
    
    // Set up polling
    const intervalId = setInterval(() => {
      this.fetchAndNotify(endpoint, callback);
    }, interval);
    
    this.intervals.set(id, intervalId);
    
    return id; // Return subscription ID for unsubscribing
  }
  
  unsubscribe(subscriptionId) {
    const intervalId = this.intervals.get(subscriptionId);
    if (intervalId) {
      clearInterval(intervalId);
      this.intervals.delete(subscriptionId);
    }
    this.subscribers.delete(subscriptionId);
  }
  
  async fetchAndNotify(endpoint, callback) {
    try {
      const data = await this.apiClient.request(endpoint);
      callback(data);
    } catch (error) {
      callback(null, error);
    }
  }
}

// Usage
const realTimeManager = new RealTimeDataManager(apiClient);

const subscriptionId = realTimeManager.subscribe(
  '/api/predict?household_id=HH_001',
  (data, error) => {
    if (error) {
      console.error('Real-time update failed:', error);
    } else {
      updateRecommendationUI(data);
    }
  },
  30000 // Update every 30 seconds
);
```

### **Loading States & UX**
```javascript
// Loading state management
const useAPICall = (apiFunction, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const execute = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiFunction(...args);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, dependencies);
  
  return { data, loading, error, execute };
};

// Usage in React component
const TradingComponent = () => {
  const { 
    data: recommendation, 
    loading: recommendationLoading, 
    error: recommendationError, 
    execute: getRecommendation 
  } = useAPICall(api.getRecommendation);
  
  const { 
    loading: tradeLoading, 
    execute: executeTrade 
  } = useAPICall(api.executeTrade);
  
  useEffect(() => {
    getRecommendation('HH_001');
  }, []);
  
  return (
    <div>
      {recommendationLoading && <LoadingSpinner />}
      {recommendationError && <ErrorAlert message={recommendationError} />}
      {recommendation && (
        <RecommendationCard 
          data={recommendation} 
          onTrade={executeTrade}
          tradeLoading={tradeLoading}
        />
      )}
    </div>
  );
};
```
```
### **Example API Responses**

#### **Trading Recommendation Response:**
```json
{
  "status": "success",
  "household_id": "HH_001",
  "prediction": {
    "decision": "SELL",
    "confidence": 0.87,
    "reasoning": "High solar production expected, low consumption predicted",
    "expected_production": 8.5,
    "predicted_consumption": 4.2,
    "surplus_deficit": 4.3,
    "optimal_price": 12.5
  },
  "market_conditions": {
    "current_price": 10.8,
    "price_trend": "increasing",
    "demand_level": "high"
  },
  "weather_data": {
    "temperature": 28.5,
    "cloud_coverage": 15,
    "uv_index": 8.2,
    "data_source": "open-meteo"
  }
}
```

#### **M-Pesa STK Push Response:**
```json
{
  "status": "success",
  "message": "STK Push initiated successfully",
  "transaction_details": {
    "checkout_request_id": "ws_CO_22092025150142941715468617",
    "merchant_request_id": "dfe1-4cab-a902-17beb3eb42645131",
    "amount": 30.0,
    "phone_number": "254715468617",
    "account_reference": "ENR001"
  }
}
```

## 🏗️ Project Architecture

```
📁 AI Energy Trading Platform
├── 🚀 main_app.py              # Main Flask application & API routes
├── 📊 complete_backend.py      # Original monolithic version (reference)
├── ⚙️  requirements.txt        # Python dependencies
├── 🔧 .env.example            # Environment configuration template
├── � README.md               # This documentation
├── 
├── 📂 config/
│   └── ⚙️  settings.py         # System configuration management
│
├── 📂 src/                     # Core application modules
│   ├── 📂 ai_models/
│   │   └── 🤖 gemini_advisor.py   # Google Gemini AI integration
│   │
│   ├── 📂 database/
│   │   └── 🗄️  db_manager.py      # SQLite database operations
│   │
│   ├── 📂 iot/
│   │   └── 📡 smart_meter.py      # ESP32 IoT device simulation
│   │
│   ├── 📂 payments/
│   │   ├── 💰 mpesa_daraja.py     # M-Pesa Daraja API client
│   │   ├── 🔗 payment_integrator.py # Unified payment interface
│   │   └── 📦 __init__.py         # Payment module exports
│   │
│   └── 📂 weather/
│       └── 🌤️  weather_api.py      # Open-Meteo weather service
│
├── 📂 tests/                   # Testing scripts
│   ├── 🧪 test_api.py          # Comprehensive API testing
│   ├── 💳 simple_mpesa_test.py  # M-Pesa STK Push testing
│   └── 📊 test_trading_functions.py # Trading logic testing
│
└── 📂 docs/                    # Documentation
    ├── 📋 DEPLOYMENT_SUCCESS.md    # Deployment guide
    ├── 💰 MPESA_INTEGRATION_SUCCESS.md # M-Pesa setup guide
    └── 🔧 TRADING_FUNCTIONS_TEST_COMPLETE.md # Testing results
```
## 🧪 Testing the System

### **1. Quick API Test**
```bash
python test_api.py
```

### **2. M-Pesa Payment Test**
```bash
# Edit phone number in simple_mpesa_test.py
python simple_mpesa_test.py
```

### **3. Trading Functions Test**
```bash
python test_trading_functions.py
```

### **4. System Status Check**
```bash
curl http://localhost:5000/api/status
```

**Expected Test Results:**
```
🔋 AI Energy Trading System API Test
==================================================
Testing API at: http://localhost:5000/api

✅ 1. Energy Predictions - SUCCESS
✅ 2. Forecast Analysis - SUCCESS  
✅ 3. System Analytics - SUCCESS
✅ 4. Trade Execution - SUCCESS

TEST SUMMARY: 4/4 tests passed
🎉 All API endpoints are working correctly!
```

## 🔧 Configuration Options

### **API Configuration**
```python
# config/settings.py
API_HOST = '0.0.0.0'        # Listen on all interfaces
API_PORT = 5000             # Default port
DEBUG_MODE = False          # Production mode
LOG_LEVEL = 'INFO'          # Logging level
```

### **Payment Configuration**
```python
# M-Pesa Settings
MPESA_ENVIRONMENT = 'sandbox'    # 'sandbox' or 'production'
MPESA_BUSINESS_SHORTCODE = '174379'  # Your business shortcode
PAYMENT_CALLBACK_URL = 'http://localhost:5000/api/payment/callback'
```

### **IoT Network Configuration**
```python
# Smart Meter Simulation
HOUSEHOLD_COUNT = 5          # Number of simulated households
DATA_UPDATE_INTERVAL = 60    # Seconds between updates
SOLAR_PANEL_CAPACITY = 5.0   # kW capacity per household
```

## 🎯 Production Deployment

### **1. Environment Setup**
```bash
# Production environment variables
export MPESA_ENVIRONMENT=production
export API_HOST=0.0.0.0
export DEBUG_MODE=False
export PAYMENT_CALLBACK_URL=https://yourdomain.com/api/payment/callback
```

### **2. Public Callback URL Setup**
For M-Pesa payments to work in production, you need a public callback URL:

#### **Option A: ngrok (for testing)**
```bash
# Install ngrok
npm install -g ngrok

# Get auth token from https://dashboard.ngrok.com/
ngrok config add-authtoken YOUR_AUTH_TOKEN

# Start tunnel
ngrok http 5000

# Update PAYMENT_CALLBACK_URL in .env with ngrok URL
```

#### **Option B: Production Deployment**
```bash
# Deploy to cloud provider (AWS, Google Cloud, Heroku, etc.)
# Update DNS and SSL certificates
# Update M-Pesa app with production callback URL
```

### **3. Database Configuration**
```python
# For production, consider PostgreSQL or MySQL
DATABASE_URL = 'postgresql://user:pass@localhost/energy_trading'
```

## 🐛 Troubleshooting

### **Common Issues**

#### **M-Pesa STK Push Not Working**
```bash
# Check credentials
python simple_mpesa_test.py

# Verify callback URL is accessible
curl -X POST http://your-callback-url/api/payment/callback

# Check M-Pesa API status
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest
```

#### **API Not Responding**
```bash
# Check if Flask is running
ps aux | grep python

# Check port availability
netstat -an | grep 5000

# Check logs
tail -f energy_trading.log
```

#### **Weather Data Issues**
```bash
# Test weather API directly
curl "https://api.open-meteo.com/v1/forecast?latitude=-1.292&longitude=36.822&current_weather=true"

# Check internet connectivity
ping open-meteo.com
```

## 📞 Support & Documentation

### **Getting Help**
- 📧 **Email**: your-email@domain.com
- 📱 **WhatsApp**: +254-XXX-XXXXX
- 💬 **Telegram**: @yourusername
- 🐛 **Issues**: GitHub Issues page

### **Additional Resources**
- 📖 [M-Pesa Daraja API Documentation](https://developer.safaricom.co.ke/docs)
- 🤖 [Google Gemini AI Documentation](https://ai.google.dev/docs)
- 🌤️ [Open-Meteo Weather API](https://open-meteo.com/en/docs)
- 📊 [Flask Documentation](https://flask.palletsprojects.com/)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- **Safaricom** for M-Pesa Daraja API
- **Google** for Gemini AI platform  
- **Open-Meteo** for weather data API
- **Flask** and **Python** communities
- **ESP32** and **IoT** community resources

---

### 🚀 **Ready to Transform Energy Trading?**

```bash
# Get started in 3 commands
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
python main_app.py    # Launch the system!
```

**Your AI-powered solar energy trading platform is ready to revolutionize how households buy and sell solar energy! ⚡🌞**

---

*Made with ❤️ for sustainable energy trading in Kenya and beyond.*# wattchain
# wattchain
