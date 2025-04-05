#include <WiFi.h>
#include <WiFiManager.h>    // For Wi-Fi configuration
#include <PubSubClient.h>   // For MQTT
#include <WiFiClientSecure.h> // For TLS support

// MQTT Broker settings (HiveMQ Cloud)
const char* mqtt_server = "b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud";
const int mqtt_port = 8883; // TLS port
// Generate unique client ID from MAC address
uint64_t chipid;
char mqtt_client_id[50];
const char* mqtt_username = "HUMAN_TRACKING"; // Replace with your HiveMQ username
const char* mqtt_password = "12345678aA";     // Replace with your HiveMQ password

// Pin for an output (e.g., LED)
const int outputPin = 2; // Change this to your hardware pin

// WiFi and MQTT clients
WiFiClientSecure espClient;
PubSubClient client(espClient);

// Variables to track state
bool prevWifiStatus = false;

void setup() {
  Serial.begin(115200);
  pinMode(outputPin, OUTPUT);
  digitalWrite(outputPin, LOW); // Initial state: OFF

  // Create an instance of WiFiManager
  WiFiManager wm;

  // Uncomment the next line to reset WiFi settings for testing
  // wm.resetSettings();

  // Start WiFiManager 
  if (!wm.autoConnect("HUMAN_TRACKING", "12345678")) {
    Serial.println("Failed to connect and hit timeout");
    delay(3000);
    ESP.restart(); // Restart if connection fails
  }

  // If we get here, Wi-Fi is connected
  Serial.println("Connected to Wi-Fi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Generate unique client ID from MAC address
  chipid = ESP.getEfuseMac(); // Get MAC address
  snprintf(mqtt_client_id, 50, "ESP32_Client_%04X%08X", (uint16_t)(chipid >> 32), (uint32_t)chipid);

  Serial.print("Generated Client ID: ");
  Serial.println(mqtt_client_id);

  // Configure TLS (HiveMQ Cloud uses default certificates)
  espClient.setInsecure(); // Use this for default certs (not recommended for production)

  // Set up MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  reconnect();
}

void reconnect() {
  unsigned long startAttempt = millis();
  while (!client.connected() && millis() - startAttempt < 30000) { // 30-second timeout
    Serial.print("Connecting to MQTT... ");
    if (client.connect(mqtt_client_id, mqtt_username, mqtt_password)) {
      Serial.println("Connected to MQTT");
      client.subscribe("esp32/control"); // Subscribe to control topic
      client.publish("esp32/status", "ONLINE"); // Publish online status
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.print(" - Details: ");
      switch (client.state()) {
        case -4: Serial.println("Connection timeout"); break;
        case -3: Serial.println("Connection lost"); break;
        case -2: Serial.println("Connect failed"); break;
        case -1: Serial.println("Disconnected"); break;
        case 1: Serial.println("Incorrect protocol version"); break;
        case 2: Serial.println("Invalid client ID"); break;
        case 3: Serial.println("Broker unavailable"); break;
        case 4: Serial.println("Bad username or password"); break;
        case 5: Serial.println("Not authorized"); break;
        default: Serial.println("Unknown error"); break;
      }
      Serial.println(" - Retrying in 5 seconds...");
      delay(5000);
    }
  }
  if (!client.connected()) {
    Serial.println("MQTT connection timed out after 30 seconds");
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println("Message received: " + message);

  // Control the output based on message
  if (message == "ON") {
    digitalWrite(outputPin, HIGH);
    Serial.println("Output: ON");
  } else if (message == "OFF") {
    digitalWrite(outputPin, LOW);
    Serial.println("Output: OFF");
  }
}

void loop() {
  // Check Wi-Fi status
  bool currentWifiStatus = WiFi.status() == WL_CONNECTED;
  if (currentWifiStatus != prevWifiStatus) {
    prevWifiStatus = currentWifiStatus;
    if (prevWifiStatus) {
      Serial.println("Connected to Wi-Fi");
    } else {
      Serial.println("Disconnected from Wi-Fi");
    }
  }

  // Maintain MQTT connection
  if (prevWifiStatus && !client.connected()) {
    reconnect();
  }
  client.loop();

  // Periodically publish online status
  static unsigned long lastPublish = 0;
  if (millis() - lastPublish > 5000 && client.connected()) { // Every 5 seconds
    client.publish("esp32/status", "ONLINE");
    lastPublish = millis();
  }
}
