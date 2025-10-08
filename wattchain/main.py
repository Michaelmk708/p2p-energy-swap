from machine import Pin, ADC, I2C
import network, time, ujson
try:
    import ussl
except Exception:
    try:
        import ssl as ussl
    except Exception:
        ussl = None
import usocket as socket

def load_config():
    cfg = {}
    try:
        with open('config.json') as f:
            cfg = ujson.load(f)
    except Exception:
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

# ADC: PV on GPIO35, Load on GPIO34
pv = ADC(Pin(35)); pv.atten(ADC.ATTN_11DB)
ld = ADC(Pin(34)); ld.atten(ADC.ATTN_11DB)

# I2C LCD1602 Setup
class LCD1602:
    def __init__(self, i2c, addr=0x27):
        self.i2c = i2c
        self.addr = addr
        self.BL = 0x08
        self.E = 0x04
        self.RW = 0x02
        self.RS = 0x01
        self._write_byte(0x33)
        self._write_byte(0x32)
        self._write_byte(0x28)
        self._write_byte(0x0C)
        self._write_byte(0x06)
        self._write_byte(0x01)
        time.sleep_ms(5)

    def _write_byte(self, val):
        temp = val
        if self.BL == 1:
            temp |= 0x08
        else:
            temp &= 0xF7
        self.i2c.writeto(self.addr, bytearray([temp]))
        self._toggle_enable(temp)

    def _toggle_enable(self, val):
        time.sleep_us(20)
        self.i2c.writeto(self.addr, bytearray([val | self.E]))
        time.sleep_us(20)
        self.i2c.writeto(self.addr, bytearray([val & ~self.E]))
        time.sleep_us(20)

    def _write_word(self, val):
        temp = val
        if self.BL == 1:
            temp |= 0x08
        else:
            temp &= 0xF7
        self.i2c.writeto(self.addr, bytearray([temp]))

    def send_command(self, val):
        buf = val & 0xF0
        buf |= self.BL
        self._write_word(buf)
        self._toggle_enable(buf)
        buf = (val & 0x0F) << 4
        buf |= self.BL
        self._write_word(buf)
        self._toggle_enable(buf)

    def send_data(self, val):
        buf = val & 0xF0
        buf |= self.BL | self.RS
        self._write_word(buf)
        self._toggle_enable(buf)
        buf = (val & 0x0F) << 4
        buf |= self.BL | self.RS
        self._write_word(buf)
        self._toggle_enable(buf)

    def clear(self):
        self.send_command(0x01)

    def set_cursor(self, x, y):
        addr = 0x80 + 0x40 * y + x
        self.send_command(addr)

    def putstr(self, text):
        for char in text:
            self.send_data(ord(char))

    def putchar(self, char):
        self.send_data(ord(char))

# Initialize I2C and LCD
try:
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))
    lcd = LCD1602(i2c)
    lcd_available = True
    print("LCD1602 initialized successfully")
except Exception as e:
    print(f"LCD initialization failed: {e}")
    lcd = None
    lcd_available = False

MAX_WATTS = int(_cfg.get("max_watts", 5000))
# Be more sensitive so small pot changes trigger updates
MIN_DELTA_W = int(_cfg.get("min_delta_w", 5))       # post if change > 5W
HEARTBEAT_MS = int(_cfg.get("heartbeat_ms", 1500))   # post at least every 1.5s
DEBUG_BODY_POSTS = int(_cfg.get("debug_body_posts", 3))  # print response body for first N posts to debug backend


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
            print("WiFi: connected {}".format(sta.ifconfig()))
        else:
            print("WiFi: not connected; will attempt posts anyway")


def adc_to_watts(adc):
    raw = adc.read()  # 0..4095
    return int(raw * MAX_WATTS / 4095)


def https_post(host, port, path, payload_bytes, read_body=False):
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    s.connect(addr)
    # Enable SNI for TLS (important for host-name based TLS like ngrok)
    if ussl is None:
        raise OSError("TLS not available")
    try:
        try:
            s = ussl.wrap_socket(s, server_hostname=host)
        except TypeError:
            # Older MicroPython variants may not support server_hostname
            s = ussl.wrap_socket(s)
    except Exception as e:
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
            # Read remainder of headers
            while True:
                line = s.readline()
                if not line or line in (b"\r\n", b"\n"):
                    break
            # Read some of the body (avoid huge reads)
            chunk = s.read(1024) or b""
            body += chunk
        except Exception:
            pass
    # drain/close
    s.close()
    if read_body:
        return status.decode().strip(), body.decode(errors="ignore")
    return status.decode().strip(), None

def http_post(host, port, path, payload_bytes, read_body=False):
    # Plain HTTP fallback (useful if TLS fails)
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
    print("Wattchain MicroPython starting…")
    
    # Initialize LCD with startup message
    if lcd_available:
        try:
            lcd.clear()
            lcd.set_cursor(0, 0)
            lcd.putstr("WattChain Ready")
            lcd.set_cursor(0, 1)
            lcd.putstr("Connecting WiFi...")
            time.sleep(1)
        except Exception as e:
            print(f"LCD startup error: {e}")
    
    wifi_connect()
    print("Posting to https://{}{}".format(HOST, PATH))
    print("ADC ready: PV=GPIO35, LOAD=GPIO34; scale=0..5.000 kW")
    
    # Update LCD after WiFi connection
    if lcd_available:
        try:
            lcd.clear()
            lcd.set_cursor(0, 0)
            lcd.putstr("WattChain Online")
            lcd.set_cursor(0, 1)
            lcd.putstr("Reading sensors...")
            time.sleep(1)
        except Exception as e:
            print(f"LCD post-WiFi error: {e}")

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

        # Always print current values for visibility
        print("PV={:.3f} kW, LOAD={:.3f} kW".format(pv_kw, ld_kw))
        
        # Update LCD display with live readings
        if lcd_available:
            try:
                net_kw = pv_kw - ld_kw
                lcd.clear()
                # Line 1: Solar and Load
                lcd.set_cursor(0, 0)
                lcd.putstr("PV:{:.1f} LD:{:.1f}".format(pv_kw, ld_kw))
                # Line 2: Net power (+ = surplus, - = deficit)
                lcd.set_cursor(0, 1)
                if net_kw >= 0:
                    lcd.putstr("NET: +{:.2f} kW".format(net_kw))
                else:
                    lcd.putstr("NET: {:.2f} kW".format(net_kw))
            except Exception as e:
                print(f"LCD update error: {e}")

        if should_post:
            # Send one POST per component to satisfy bridge expectations
            pv_payload = {"device": DEVICE_ID, "component": PV_COMPONENT, "data": {"power": pv_kw}}
            ld_payload = {"device": DEVICE_ID, "component": LD_COMPONENT, "data": {"power": ld_kw}}

            for name, pl in (("PV", pv_payload), ("LOAD", ld_payload)):
                status = ""
                body = None
                try:
                    try:
                        status, body = https_post(
                            HOST,
                            PORT,
                            PATH,
                            ujson.dumps(pl).encode(),
                            read_body=(debug_posts_left > 0),
                        )
                    except Exception as tls_err:
                        # Fallback: try plain HTTP on port 80 once
                        status, body = http_post(
                            HOST,
                            80,
                            PATH,
                            ujson.dumps(pl).encode(),
                            read_body=(debug_posts_left > 0),
                        )
                except Exception as e:
                    status = f"ERROR {e}"
                # Print first line and values
                print("HTTP:", status, "|", name, pl["data"]) 
                if body:
                    print("BODY:", body[:200])
                if debug_posts_left > 0:
                    debug_posts_left -= 1
                # Tiny gap between posts
                time.sleep_ms(50)
            last_pv, last_ld = pv_w, ld_w
            last_post = now

        time.sleep_ms(100)

# Auto-start when imported (as Wokwi does), but also allow manual start()
try:
    start()
except Exception as e:
    try:
        import sys
        sys.print_exception(e)
    except Exception:
        print("main start error:", e)
