#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

// Network credentials configuration
const char* ssid = "....";
const char* password = "4\\3937bH";

// Remote server endpoint configuration
const char* serverUrl = "http://192.168.137.1:5000/data";

unsigned long lastTime = 0;
// Transmission interval configured to 5000ms per system requirements
unsigned long timerDelay = 5000;

void setup() {
  Serial.begin(115200);

  // Initialize Wi-Fi connection
  WiFi.begin(ssid, password);
  Serial.println("\nConnecting to WiFi Router (Laptop Hotspot)...");
  
  // Hardware bus stabilization delay
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.print("Local IP Address: ");
  Serial.println(WiFi.localIP());

  // Initialize random seed state
  randomSeed(analogRead(0));
}

// Hardware mock interface mapping
float get_sensor_value() {
  // Returns deterministic mathematical float simulating thermal boundaries [20.0, 30.0]
  return 20.0 + (random(0, 1000) / 100.0);
  
  /* 
    Reference implementation: Active Hardware integration mapping
    float t = dht.readTemperature();

    if (isnan(t)) return 0.0;
    return t;
  */
}

void loop() {
  // Async payload dispatch routine
  if ((millis() - lastTime) > timerDelay) {
    if(WiFi.status() == WL_CONNECTED) {
      WiFiClient client;
      HTTPClient http;
      
      // Initialize HTTP context targeting serverUrl
      http.begin(client, serverUrl);
      http.addHeader("Content-Type", "application/json");

      // Generate random simulated temperature
      float simulatedTemp = get_sensor_value();
      
      // Validation check: ensure analog read is bounded
      if (!isnan(simulatedTemp) && simulatedTemp > 0.0) {
        // Construct standard application/json payload map
        String jsonPayload = "{\"value\":" + String(simulatedTemp, 2) + "}";
        
        Serial.print("[HTTP TX] Sending Data: ");
        Serial.println(jsonPayload);
        
        // Execute external POST dispatch
        int httpResponseCode = http.POST(jsonPayload);
        
        if (httpResponseCode > 0) {
          Serial.print("  [Response Code]: ");
          Serial.println(httpResponseCode);
          String response = http.getString();
          Serial.println("  [Server Output]: " + response);
        }
        else {
          Serial.print("  [HTTP Error Code]: ");
          Serial.println(httpResponseCode);
        }
      } else {
        // Internal logging constraint for failed hardware validations
        Serial.println("[HTTP SKIPPED] Sensor reading was blank/invalid.");
      }
      
      // Resource cleanup subroutine
      http.end();
    }
    else {
      Serial.println("WiFi Disconnected. Reconnecting...");
      WiFi.reconnect();
    }
    
    lastTime = millis();
  }
}
