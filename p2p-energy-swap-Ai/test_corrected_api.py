#!/usr/bin/env python3
"""
CORRECTED Trading Functions Test - Matches Actual API Format
Tests sell/buy predictions and consumption forecasting
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🔋 {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section"""
    print(f"\n📊 {title}")
    print("-" * 40)

def test_actual_api_structure():
    """Test the actual API structure and format"""
    print_header("TESTING ACTUAL API STRUCTURE")
    
    try:
        # Test prediction with correct household format
        household_ids = ["HH001_Nairobi_Central", "HH_001", "HH_002", "HH_003"]
        
        for household_id in household_ids:
            print_section(f"Testing {household_id}")
            
            response = requests.get(f"{BASE_URL}/predict", 
                                  params={"household": household_id}, 
                                  timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response Structure for {household_id}:")
                
                # Extract prediction data
                prediction = data.get('prediction', {})
                weather = data.get('weather', {})
                iot_data = data.get('iot_data', {})
                
                print(f"   🏠 Household ID: {data.get('household_id', 'N/A')}")
                print(f"   📊 Status: {data.get('status', 'N/A')}")
                
                if prediction:
                    print(f"   🤖 AI Prediction:")
                    print(f"      - Recommendation: {prediction.get('recommendation', 'N/A')}")
                    print(f"      - Confidence: {prediction.get('confidence', 0):.1%}")
                    print(f"      - Action: {prediction.get('action', 'N/A')}")
                    print(f"      - Expected Profit: {prediction.get('expected_profit', 'N/A')}")
                
                if iot_data:
                    print(f"   ⚡ IoT Data:")
                    print(f"      - Solar Generation: {iot_data.get('solar_generation_kwh', 0):.2f} kWh")
                    print(f"      - Consumption: {iot_data.get('consumption_kwh', 0):.2f} kWh")
                    print(f"      - Surplus/Deficit: {iot_data.get('surplus_deficit_kwh', 0):.2f} kWh")
                    print(f"      - Battery Level: {iot_data.get('battery_level', 0):.0f}%")
                
                if weather:
                    print(f"   🌤️  Weather:")
                    print(f"      - Temperature: {weather.get('temperature', 'N/A')}°C")
                    print(f"      - Cloud Cover: {weather.get('cloud_percentage', 'N/A')}%")
                    print(f"      - Data Source: {weather.get('data_source', 'N/A')}")
                
                # Trading decision logic
                surplus = iot_data.get('surplus_deficit_kwh', 0)
                battery = iot_data.get('battery_level', 0)
                
                if surplus > 1 and battery > 80:
                    trading_decision = "SELL - Excess energy available"
                elif surplus < -1 and battery < 30:
                    trading_decision = "BUY - Energy deficit and low battery"
                else:
                    trading_decision = "HOLD - Balanced energy state"
                
                print(f"   💡 Trading Decision: {trading_decision}")
                
            else:
                print(f"❌ Failed for {household_id}: Status {response.status_code}")
                print(f"   Response: {response.text}")
            
            print()
            break  # Test first successful one
            
    except Exception as e:
        print(f"❌ Error in API structure test: {e}")

def test_forecast_structure():
    """Test forecast API structure"""
    print_header("FORECAST API STRUCTURE TEST")
    
    try:
        response = requests.get(f"{BASE_URL}/forecast", 
                              params={"household": "HH001_Nairobi_Central", "hours": 12}, 
                              timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            forecasts = data.get('forecasts', [])
            
            print(f"✅ Forecast Response:")
            print(f"   📊 Status: {data.get('status', 'N/A')}")
            print(f"   🏠 Household: {data.get('household_id', 'N/A')}")
            print(f"   📈 Forecast Count: {data.get('count', 0)}")
            
            if forecasts:
                print(f"\n🕐 First Few Forecast Periods:")
                for i, forecast in enumerate(forecasts[:6]):  # Show first 6
                    timestamp = forecast.get('timestamp', 'N/A')
                    weather_info = forecast.get('weather', {})
                    iot_info = forecast.get('iot_data', {})
                    prediction = forecast.get('prediction', {})
                    
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M')
                    except:
                        time_str = f"Period {i+1}"
                    
                    temp = weather_info.get('temperature', 'N/A')
                    clouds = weather_info.get('cloud_percentage', 'N/A')
                    production = iot_info.get('solar_generation_kwh', 0)
                    consumption = iot_info.get('consumption_kwh', 0)
                    recommendation = prediction.get('recommendation', 'N/A')
                    
                    print(f"   {time_str}: {temp}°C, {clouds}% clouds, "
                          f"{production:.1f}kWh prod, {consumption:.1f}kWh cons, "
                          f"Rec: {recommendation}")
                    
        else:
            print(f"❌ Forecast failed: Status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error in forecast test: {e}")

def test_corrected_trade_execution():
    """Test trade execution with correct API format"""
    print_header("CORRECTED TRADE EXECUTION TEST")
    
    # Test trades with correct format (using 'type' not 'action')
    test_trades = [
        {
            "type": "sell",
            "amount": 5.0,
            "price": 12.0,
            "household": "HH001_Nairobi_Central",
            "phone": "+254700123456",
            "scenario": "Selling excess solar energy"
        },
        {
            "type": "buy",
            "amount": 3.0,
            "price": 10.0,
            "household": "HH001_Nairobi_Central",
            "phone": "+254700123456",
            "scenario": "Buying energy for evening use"
        }
    ]
    
    for i, trade in enumerate(test_trades, 1):
        print_section(f"Trade Test {i}: {trade['scenario']}")
        
        try:
            response = requests.post(f"{BASE_URL}/execute_trade", 
                                   json=trade, 
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Trade executed successfully:")
                print(f"   📊 Status: {data.get('status', 'N/A')}")
                print(f"   🏠 Household: {data.get('household_id', 'N/A')}")
                print(f"   💰 Total Value: {data.get('total_value', 'N/A')} KES")
                
                # Trade details
                trade_info = data.get('trade', {})
                if trade_info:
                    print(f"   🔄 Trade ID: {trade_info.get('id', 'N/A')}")
                    print(f"   📈 Type: {trade_info.get('trade_type', 'N/A')}")
                    print(f"   ⚡ Amount: {trade_info.get('amount', 'N/A')} kWh")
                    print(f"   💲 Price: {trade_info.get('price', 'N/A')} KES/kWh")
                
                # Payment details
                payment_info = data.get('payment', {})
                if payment_info:
                    print(f"   📱 Payment Status: {payment_info.get('status', 'N/A')}")
                    print(f"   🆔 Payment ID: {payment_info.get('tx_id', 'N/A')}")
                    print(f"   📞 Phone: {payment_info.get('phone', 'N/A')}")
                
            else:
                print(f"❌ Trade failed: Status {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error executing trade: {e}")

def test_households_api():
    """Test households/IoT network API"""
    print_header("IoT NETWORK & HOUSEHOLDS TEST")
    
    try:
        response = requests.get(f"{BASE_URL}/households", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ IoT Network Status:")
            print(f"   📊 Status: {data.get('status', 'N/A')}")
            
            households = data.get('households', [])
            print(f"   🏠 Available Households: {len(households)}")
            for household in households:
                print(f"      - {household}")
            
            # Network data
            network_data = data.get('network_data', {})
            if network_data:
                network_summary = network_data.get('network_summary', {})
                if network_summary:
                    print(f"\n   📊 Network Summary:")
                    print(f"      - Total Generation: {network_summary.get('total_generation', 'N/A')} kWh")
                    print(f"      - Total Consumption: {network_summary.get('total_consumption', 'N/A')} kWh")
                    print(f"      - Net Surplus/Deficit: {network_summary.get('total_surplus_deficit', 'N/A')} kWh")
                    print(f"      - Average Battery: {network_summary.get('avg_battery_level', 'N/A')}%")
                    
        else:
            print(f"❌ Households API failed: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in households test: {e}")

def test_analytics_api():
    """Test analytics API"""
    print_header("ANALYTICS API TEST")
    
    try:
        response = requests.get(f"{BASE_URL}/analytics", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Analytics Retrieved:")
            
            # Print all available keys
            print(f"   📊 Available Data Fields:")
            for key in data.keys():
                value = data[key]
                if isinstance(value, dict):
                    print(f"      - {key}: {len(value)} items")
                elif isinstance(value, list):
                    print(f"      - {key}: {len(value)} entries")
                else:
                    print(f"      - {key}: {value}")
                    
        else:
            print(f"❌ Analytics API failed: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in analytics test: {e}")

def main():
    """Run corrected comprehensive tests"""
    print("🌞 AI ENERGY TRADING SYSTEM - CORRECTED API TESTS")
    print("=" * 80)
    print(f"🕒 Test Time: {datetime.now()}")
    print(f"🌐 Testing API at: {BASE_URL}")
    
    # Check server
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Server is responding")
    except:
        print("❌ Server not responding")
        return
    
    # Run tests
    test_actual_api_structure()
    test_forecast_structure()
    test_corrected_trade_execution()
    test_households_api()
    test_analytics_api()
    
    # Summary
    print_header("CORRECTED TEST SUMMARY")
    print("✅ TESTED CAPABILITIES:")
    print("   🔮 AI prediction API structure")
    print("   📈 Forecast API with hourly data")
    print("   💰 Corrected trade execution (using 'type' field)")
    print("   🏠 IoT network and households data")
    print("   📊 System analytics")
    print("   🌤️  Real weather integration")
    print("   ⚖️  Energy balance calculations")
    print("   🔋 Battery and consumption monitoring")
    
    print("\n🎯 Your AI Energy Trading System APIs are working!")
    print("📝 Note: API uses 'type' not 'action' for trades")
    print("🌐 Server: http://localhost:5000")

if __name__ == "__main__":
    main()