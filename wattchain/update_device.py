# Updated Wokwi device code with local bridge endpoint
# Copy and paste this into the Wokwi terminal/REPL

import machine
import network
import socket
try:
    import ussl as ssl
except ImportError:
    import ssl
import ujson as json
import time

# Configuration
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
HOST = "host.docker.internal"
PORT = 9000
PATH = "/telemetry"
DEVICE_ID = "sim-1"
PV_PIN = 35
LOAD_PIN = 34
MAX_WATTS = 5000
MIN_DELTA_W = 5
HEARTBEAT_MS = 1500

# Global state
wlan = None
last_pv = None
last_load = None
last_time = 0

def connect_wifi():
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep_ms(100)
    print("WiFi connected:", wlan.ifconfig())

def read_sensors():
    pv_adc = machine.ADC(machine.Pin(PV_PIN))
    pv_adc.atten(machine.ADC.ATTN_11DB)
    load_adc = machine.ADC(machine.Pin(LOAD_PIN))
    load_adc.atten(machine.ADC.ATTN_11DB)
    
    pv_raw = pv_adc.read()
    load_raw = load_adc.read()
    
    # Convert to watts (0-4095 -> 0-5000W)
    pv_watts = int((pv_raw / 4095) * MAX_WATTS)
    load_watts = int((load_raw / 4095) * MAX_WATTS)
    
    return pv_watts, load_watts

def http_post(host, port, path, data):
    try:
        addr = socket.getaddrinfo(host, port)[0][-1]
        s = socket.socket()
        s.settimeout(10)
        s.connect(addr)
        
        json_data = json.dumps(data)
        request = f"POST {path} HTTP/1.1\r\n"
        request += f"Host: {host}:{port}\r\n"
        request += "Content-Type: application/json\r\n"
        request += f"Content-Length: {len(json_data)}\r\n"
        request += "Connection: close\r\n\r\n"
        request += json_data
        
        s.send(request.encode())
        
        response = s.recv(1024).decode()
        s.close()
        
        if "200 OK" in response:
            print(f"✓ Posted {data['component']} = {data['data']['power']}W")
            return True
        else:
            print(f"✗ POST failed: {response[:100]}")
            return False
            
    except Exception as e:
        print(f"✗ HTTP POST error: {e}")
        return False

def should_post(pv, load):
    global last_pv, last_load, last_time
    current_time = time.ticks_ms()
    
    # Post if significant change
    if last_pv is None or abs(pv - last_pv) >= MIN_DELTA_W or abs(load - last_load) >= MIN_DELTA_W:
        return True
    
    # Post if heartbeat interval passed
    if time.ticks_diff(current_time, last_time) >= HEARTBEAT_MS:
        return True
    
    return False

def telemetry_loop():
    global last_pv, last_load, last_time
    
    connect_wifi()
    
    print(f"Starting telemetry to http://{HOST}:{PORT}{PATH}")
    
    while True:
        try:
            pv_watts, load_watts = read_sensors()
            
            if should_post(pv_watts, load_watts):
                # Post PV reading
                pv_payload = {
                    "device": DEVICE_ID,
                    "component": "pv_array",
                    "data": {"power": pv_watts / 1000.0}  # Convert to kW
                }
                
                # Post Load reading
                load_payload = {
                    "device": DEVICE_ID,
                    "component": "house_load", 
                    "data": {"power": load_watts / 1000.0}  # Convert to kW
                }
                
                http_post(HOST, PORT, PATH, pv_payload)
                http_post(HOST, PORT, PATH, load_payload)
                
                last_pv = pv_watts
                last_load = load_watts
                last_time = time.ticks_ms()
            
            time.sleep_ms(100)
            
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(1)

# Start the telemetry loop
print("Starting Wokwi telemetry with local bridge...")
telemetry_loop()