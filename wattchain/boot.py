# Auto-start the wattchain script on boot.
# If main.py is present, import it (it contains the main loop).
# If not, run a self-contained fallback so telemetry still starts.
# Added: runtime config support (config.json or host.txt) and a start() function
# you can call manually from the REPL: `import boot; boot.start()`.

try:
    import main  # executes main loop if present
except Exception as e:
    try:
        import sys
        sys.print_exception(e)
    except Exception:
        print("boot error:", e)

    # --- Fallback inline runner (mirrors main.py behavior) ---
    try:
        from machine import Pin, ADC
        import network, time, ujson
        try:
            import ussl
        except Exception:
            try:
                import ssl as ussl
            except Exception:
                ussl = None
        import usocket as socket

        # --- Config helpers ---
        def load_config():
            cfg = {}
            try:
                with open('config.json') as f:
                    cfg = ujson.load(f)
            except Exception:
                # Optional simple override via host.txt
                try:
                    with open('host.txt') as f:
                        host = f.read().strip()
                        if host:
                            cfg['host'] = host
                except Exception:
                    pass
            return cfg

        _cfg = load_config()

        WIFI_SSID = _cfg.get("wifi_ssid", "Wokwi-GUEST")
        WIFI_PASS = _cfg.get("wifi_pass", "")

        HOST = _cfg.get("host", "unbaffled-dwindlingly-lydia.ngrok-free.dev")
        PORT = int(_cfg.get("port", 443))
        PATH = _cfg.get("path", "/api/iotcentral/telemetry_bridge/")

        DEVICE_ID = _cfg.get("device", "sim-1")
        PV_COMPONENT = _cfg.get("pv_component", "pv_array")
        LD_COMPONENT = _cfg.get("load_component", "house_load")

        MAX_WATTS = int(_cfg.get("max_watts", 5000))
        MIN_DELTA_W = int(_cfg.get("min_delta_w", 5))
        HEARTBEAT_MS = int(_cfg.get("heartbeat_ms", 1500))
        DEBUG_BODY_POSTS = int(_cfg.get("debug_body_posts", 3))

        # ADC: PV on GPIO35, Load on GPIO34
        pv = ADC(Pin(35)); pv.atten(ADC.ATTN_11DB)
        ld = ADC(Pin(34)); ld.atten(ADC.ATTN_11DB)

        def wifi_connect(timeout_ms=10000):
            sta = network.WLAN(network.STA_IF)
            sta.active(True)
            if not sta.isconnected():
                print("WiFi: connecting to {}".format(WIFI_SSID))
                sta.connect(WIFI_SSID, WIFI_PASS)
                start = time.ticks_ms()
                while not sta.isconnected():
                    time.sleep_ms(200)
                    if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                        print("WiFi: connect timeout after {} ms".format(timeout_ms))
                        break
                if sta.isconnected():
                    try:
                        print("WiFi: connected {}".format(sta.ifconfig()))
                    except Exception:
                        print("WiFi: connected")
                else:
                    print("WiFi: not connected; will attempt posts anyway")

        def adc_to_watts(adc):
            raw = adc.read()
            return int(raw * MAX_WATTS / 4095)

        def https_post(host, port, path, payload_bytes, read_body=False):
            addr = socket.getaddrinfo(host, port)[0][-1]
            s = socket.socket()
            s.connect(addr)
            if ussl is None:
                s.close()
                raise OSError("TLS not available")
            try:
                try:
                    s = ussl.wrap_socket(s, server_hostname=host)
                except TypeError:
                    s = ussl.wrap_socket(s)
            except Exception:
                s.close()
                raise
            req = (
                "POST {} HTTP/1.1\r\n"
                "Host: {}\r\n"
                "User-Agent: mp-esp32\r\n"
                "Content-Type: application/json\r\n"
                "Connection: close\r\n"
                "Content-Length: {}\r\n"
                "\r\n"
            ).format(path, host, len(payload_bytes))
            s.write(req.encode() + payload_bytes)
            status = s.readline() or b""
            body = b""
            if read_body:
                try:
                    while True:
                        line = s.readline()
                        if not line or line in (b"\r\n", b"\n"):
                            break
                    body = s.read(1024) or b""
                except Exception:
                    pass
            s.close()
            if read_body:
                return status.decode().strip(), body.decode(errors="ignore")
            return status.decode().strip(), None

        def http_post(host, port, path, payload_bytes, read_body=False):
            addr = socket.getaddrinfo(host, port)[0][-1]
            s = socket.socket()
            s.connect(addr)
            req = (
                "POST {} HTTP/1.1\r\n"
                "Host: {}\r\n"
                "User-Agent: mp-esp32\r\n"
                "Content-Type: application/json\r\n"
                "Connection: close\r\n"
                "Content-Length: {}\r\n"
                "\r\n"
            ).format(path, host, len(payload_bytes))
            s.write(req.encode() + payload_bytes)
            status = s.readline() or b""
            body = b""
            if read_body:
                try:
                    while True:
                        line = s.readline()
                        if not line or line in (b"\r\n", b"\n"):
                            break
                    body = s.read(1024) or b""
                except Exception:
                    pass
            s.close()
            if read_body:
                return status.decode().strip(), body.decode(errors="ignore")
            return status.decode().strip(), None

        def start():
            print("Wattchain Fallback runner starting…")
            wifi_connect()
            print("Posting to https://{}{}".format(HOST, PATH))
            print("ADC ready: PV=GPIO35, LOAD=GPIO34; scale=0..5.000 kW")

            last_pv = -10**9
            last_ld = -10**9
            last_post = 0
            debug_posts_left = DEBUG_BODY_POSTS

            while True:
                pv_w = adc_to_watts(pv)
                ld_w = adc_to_watts(ld)
                pv_kw = round(pv_w / 1000.0, 3)
                ld_kw = round(ld_w / 1000.0, 3)
                now = time.ticks_ms()

                should_post = False
                if abs(pv_w - last_pv) > MIN_DELTA_W or abs(ld_w - last_ld) > MIN_DELTA_W:
                    should_post = True
                if time.ticks_diff(now, last_post) >= HEARTBEAT_MS:
                    should_post = True

                print("PV={:.3f} kW, LOAD={:.3f} kW".format(pv_kw, ld_kw))

                if should_post:
                    pv_payload = {"device": DEVICE_ID, "component": PV_COMPONENT, "data": {"power": pv_kw}}
                    ld_payload = {"device": DEVICE_ID, "component": LD_COMPONENT, "data": {"power": ld_kw}}
                    for name, pl in (("PV", pv_payload), ("LOAD", ld_payload)):
                        status = ""
                        body = None
                        try:
                            try:
                                status, body = https_post(HOST, PORT, PATH, ujson.dumps(pl).encode(), read_body=(debug_posts_left > 0))
                            except Exception as tls_err:
                                status, body = http_post(HOST, 80, PATH, ujson.dumps(pl).encode(), read_body=(debug_posts_left > 0))
                        except Exception as e2:
                            status = "ERROR {}".format(e2)
                        print("HTTP:", status, "|", name, pl["data"])
                        if body and debug_posts_left > 0:
                            print("BODY:", body[:200])
                            debug_posts_left -= 1
                        time.sleep_ms(50)
                    last_pv, last_ld = pv_w, ld_w
                    last_post = now
                time.sleep_ms(100)

        # Expose start() to REPL and auto-start fallback now
        globals()['start'] = start
        start()

    except Exception as run_err:
        try:
            import sys
            sys.print_exception(run_err)
        except Exception:
            print("fallback error:", run_err)
