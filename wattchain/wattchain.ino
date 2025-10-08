#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <math.h> // for fabsf

// Match your diagram wiring
const int solarPin = 35;        // pot1: solar panels (PV)
const int consumptionPin = 34;  // pot2: load/consumption

// WiFi (Wokwi or your local WiFi if on real board)
const char* WIFI_SSID = "Wokwi-GUEST"; // change if using real WiFi
const char* WIFI_PASS = "";

// Backend (ngrok tunnel + telemetry endpoint)
const char* DEVICE_ID = "sim-1";
const char* POST_URL  = "https://unbaffled-dwindlingly-lydia.ngrok-free.dev/api/iotcentral/telemetry_bridge/";

// Scale: 0..4095 -> 0..5.00 kW (adjust to what you want to see in UI)
constexpr float SCALE = 5.0f / 4095.0f;

float solarKW = 0, consumptionKW = 0;
unsigned long lastSampleMs = 0;
unsigned long lastPostMs = 0;
float lastSentSolar = -100.0f, lastSentCons = -100.0f;

WiFiClientSecure client;
HTTPClient http;

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("WiFi: connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    Serial.print(".");
  }
  Serial.println("\nWiFi: connected");
}

void setup() {
  Serial.begin(115200);
  analogSetWidth(12);

  connectWiFi();

  // For demo over ngrok: skip cert validation
  client.setInsecure();

  Serial.println("Telemetry POST URL:");
  Serial.println(POST_URL);
  Serial.println("Verify in browser (optional):");
  Serial.println("  Latest PV: https://unbaffled-dwindlingly-lydia.ngrok-free.dev/api/iotcentral/latest/?device=sim-1&component=pv_array");
  Serial.println("  Timeseries: https://unbaffled-dwindlingly-lydia.ngrok-free.dev/api/iotcentral/timeseries/?device=sim-1&components=pv_array,house_load&minutes=60");
}

void sample() {
  const float alpha = 0.25f; // smoothing; set to 1.0f to disable
  int solarRaw = analogRead(solarPin);
  int consRaw  = analogRead(consumptionPin);

  float newSolar = solarRaw * SCALE; // kW
  float newCons  = consRaw  * SCALE; // kW

  solarKW       = (alpha * newSolar) + (1 - alpha) * solarKW;
  consumptionKW = (alpha * newCons)  + (1 - alpha) * consumptionKW;

  // Optional rounding for neat UI numbers
  solarKW       = roundf(solarKW * 100.0f) / 100.0f;
  consumptionKW = roundf(consumptionKW * 100.0f) / 100.0f;
}

bool shouldPost(unsigned long now) {
  bool drift = fabsf(solarKW - lastSentSolar) > 0.05f ||
               fabsf(consumptionKW - lastSentCons) > 0.05f;
  bool stale = (now - lastPostMs) >= 2000; // 2s heartbeat for responsive UI
  return drift || stale;
}

void postTelemetry() {
  if (WiFi.status() != WL_CONNECTED) return;

  // Simple dict JSON your backend accepts:
  // {"device":"sim-1","pv_power":<kW>,"load_power":<kW>}
  char payload[192];
  snprintf(payload, sizeof(payload),
           "{\"device\":\"%s\",\"pv_power\":%.2f,\"load_power\":%.2f}",
           DEVICE_ID, solarKW, consumptionKW);

  if (!http.begin(client, POST_URL)) {
    Serial.println("HTTP begin failed");
    return;
  }

  http.addHeader("Content-Type", "application/json");
  int code = http.POST((uint8_t*)payload, strlen(payload));
  String body = http.getString();

  Serial.printf("POST %d -> pv=%.2f kW, load=%.2f kW\n", code, solarKW, consumptionKW);
  Serial.println(body);
  http.end();
}

void loop() {
  unsigned long now = millis();

  if (now - lastSampleMs >= 200) {
    lastSampleMs = now;
    sample();
  }

  if (shouldPost(now)) {
    lastPostMs = now;
    lastSentSolar = solarKW;
    lastSentCons  = consumptionKW;
    postTelemetry();
  }

  delay(1);
}