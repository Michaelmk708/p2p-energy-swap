#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

#define PIN_SOLAR 34
#define PIN_LOAD  35

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(115200); // Must match Python script speed
  lcd.init();
  lcd.backlight();
  
  lcd.setCursor(0, 0);
  lcd.print("P2P System Ready");
  lcd.setCursor(0, 1);
  lcd.print("Serial Mode");
  delay(1000);
}

void loop() {
  // 1. Read Knobs
  float solar_kw = (analogRead(PIN_SOLAR) / 4095.0) * 5.0;
  float load_kw = (analogRead(PIN_LOAD) / 4095.0) * 5.0;
  float net_kw = solar_kw - load_kw;

  // 2. Update LCD
  lcd.setCursor(0, 0);
  lcd.printf("PV:%.1f Ld:%.1fkW", solar_kw, load_kw);
  lcd.setCursor(0, 1);
  lcd.print(net_kw > 0 ? "SELLING >>    " : "BUYING <<     ");

  // 3. Send Pure JSON to Serial (No WiFi overhead)
  Serial.printf("{\"solar\": %.2f, \"load\": %.2f}\n", solar_kw, load_kw);

  delay(200); // Fast updates (5 times per second)
}