#pragma once

// Copy this file to secrets.h (same folder) and fill in your own values.
// secrets.h is gitignored - never commit real credentials.

#define WIFI_SSID     "your-wifi-name"
#define WIFI_PASSWORD "your-wifi-password"

// Local Mosquitto from docker-compose: use the LAN IP of the PC running Docker,
// not "localhost" (localhost on the ESP32 is the ESP32 itself).
#define MQTT_HOST      "192.168.1.100"
#define MQTT_PORT      1883
#define MQTT_USERNAME  ""
#define MQTT_PASSWORD  ""
#define MQTT_CLIENT_ID "study-station-esp32"
