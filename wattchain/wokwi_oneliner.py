import machine, network, socket, time; import ujson as json; wlan = network.WLAN(network.STA_IF); wlan.active(True); wlan.connect("Wokwi-GUEST", "") if not wlan.isconnected() else None; [time.sleep_ms(100) for _ in range(50) if not wlan.isconnected()]; print("WiFi:", wlan.ifconfig() if wlan.isconnected() else "Failed"); pv_adc = machine.ADC(machine.Pin(35)); pv_adc.atten(machine.ADC.ATTN_11DB); load_adc = machine.ADC(machine.Pin(34)); load_adc.atten(machine.ADC.ATTN_11DB); exec("""
def post_reading(component, watts):
    try:
        payload = {"device": "sim-1", "component": component, "data": {"power": watts/1000.0}}
        json_data = json.dumps(payload)
        s = socket.socket()
        s.settimeout(5)
        s.connect(("host.docker.internal", 9000))
        request = f"POST /telemetry HTTP/1.1\\r\\nHost: host.docker.internal:9000\\r\\nContent-Type: application/json\\r\\nContent-Length: {len(json_data)}\\r\\nConnection: close\\r\\n\\r\\n{json_data}"
        s.send(request.encode())
        resp = s.recv(512).decode()
        s.close()
        return "200 OK" in resp
    except: return False

while True:
    pv = int((pv_adc.read() / 4095) * 5000)
    load = int((load_adc.read() / 4095) * 5000)
    print(f"PV={pv/1000:.3f}kW LOAD={load/1000:.3f}kW", end=" ")
    if post_reading("pv_array", pv): print("PV✓", end=" ")
    else: print("PV✗", end=" ")
    if post_reading("house_load", load): print("LOAD✓")
    else: print("LOAD✗")
    time.sleep(2)
""")