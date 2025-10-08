#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WiFiClientSecure.h>

// ===== Configure these =====
const char* WIFI_SSID     = "Wokwi-GUEST";   // Wokwi web default network
const char* WIFI_PASS     = "";              // empty password
const char* TELEMETRY_URL = "https://unbaffled-dwindlingly-lydia.ngrok-free.dev/api/iotcentral/telemetry_bridge/";
const char* DEVICE_ID     = "household-1";   // must match the UI device

// Pin mapping per diagram.json:
// pot1 ("solar panels") -> ESP32 GPIO35
// pot2 ("load/consumption") -> ESP32 GPIO34
int solarPin = 35;        // Solar generation (pot1)
int consumptionPin = 34;  // Load/consumption (pot2)

// Send JSON to backend bridge: { device, pv_power, load_power }
void sendTelemetry(float solarKW, float consumptionKW) {
  if (WiFi.status() != WL_CONNECTED) return;

  WiFiClientSecure secure;
  secure.setInsecure();  // demo: skip TLS cert validation
  HTTPClient http;

  if (!http.begin(secure, TELEMETRY_URL)) {
    Serial.println("HTTP begin() failed");
    return;
  }

  http.addHeader("Content-Type", "application/json");

  JsonDocument doc;
  doc["device"]     = DEVICE_ID;
  doc["pv_power"]   = solarKW;
  doc["load_power"] = consumptionKW;

  String body;
  serializeJson(doc, body);
  int code = http.POST(body);

  Serial.print("POST telemetry -> HTTP ");
  Serial.println(code);

  http.end();
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to WiFi");
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - start) < 15000) {
    delay(200);
    Serial.print(".");
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
  } else {
    Serial.println("\nWiFi connect timeout, continuing without network");
  }
}

void loop() {
  int solarRaw = analogRead(solarPin);
  int consumptionRaw = analogRead(consumptionPin);

  float solarKW = solarRaw * (5.0 / 4095.0);
  float consumptionKW = consumptionRaw * (5.0 / 4095.0);

  float surplus = 0;
  float deficit = 0;
  float gridDraw = 0;
  float gridSupply = 0;

  if (solarKW >= consumptionKW) {
    surplus = solarKW - consumptionKW;
    gridSupply = surplus;
  } else {
    deficit = consumptionKW - solarKW;
    gridDraw = deficit;
  }

  Serial.print("Solar: ");
  Serial.print(solarKW, 2);
  Serial.print(" kW | Consumption: ");
  Serial.print(consumptionKW, 2);
  Serial.print(" kW | ");

  if (surplus > 0) {
    Serial.print("Surplus: ");
    Serial.print(surplus, 2);
    Serial.print(" kW | Grid Supply: ");
    Serial.print(gridSupply, 2);
  } else {
    Serial.print("Deficit: ");
    Serial.print(deficit, 2);
    Serial.print(" kW | Grid Draw: ");
    Serial.print(gridDraw, 2);
  }
  Serial.println(" kW");

  sendTelemetry(solarKW, consumptionKW);

  delay(3000);
}
