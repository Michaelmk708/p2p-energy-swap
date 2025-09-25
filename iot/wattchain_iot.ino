#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>


int solarPin = 34;        // Pot 1 = Solar generation
int consumptionPin = 35;  // Pot 2 = Consumption

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* oracle_gateway_url = "YOUR_ORACLE_GATEWAY_URL";
const char* device_id = "YOUR_ORACLE_DEVICE_ID";
const char* shared_secret = "YOUR_ORACLE_SHARED_SECRET";

void setup() {
  Serial.begin(115200);
  // --- Connect to Wi-Fi ---
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
  }
  Serial.println("Connected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}
 
void sendDataToOracle(float solar, float consumption, float surplus, float deficit) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(oracle_gateway_url);
    http.addHeader("Content-Type", "application/json");

    // --- Create JSON payload ---
    StaticJsonDocument<200> doc;
    doc["deviceId"] = device_id;
    doc["solar_generation"] = solar;
    doc["consumption"] = consumption;
    doc["surplus"] = surplus;
    doc["deficit"] = deficit;

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    // --- Send HTTP POST request ---
    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      String payload = http.getString();
      Serial.println(payload);
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi Disconnected. Retrying...");
  }
}

void loop() {
  // --- Read potentiometers ---
  int solarRaw = analogRead(solarPin);
  int consumptionRaw = analogRead(consumptionPin);

  // --- Convert to kW (0–5kW range) ---
  float solarKW = solarRaw * (5.0 / 4095.0);
  float consumptionKW = consumptionRaw * (5.0 / 4095.0);

  // --- Calculations ---
  float surplus = 0;
  float deficit = 0;
  float gridDraw = 0;
  float gridSupply = 0;

  if (solarKW >= consumptionKW) {
    surplus = solarKW - consumptionKW;
    gridSupply = surplus; // send back to grid
  } else {
    deficit = consumptionKW - solarKW;
    gridDraw = deficit;   // draw from grid
  }

  // --- Print results ---
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

  sendDataToOracle(solarKW, consumptionKW, surplus, deficit);


  Serial.println(" kW");
  delay(2000); // update every 2 sec
}
