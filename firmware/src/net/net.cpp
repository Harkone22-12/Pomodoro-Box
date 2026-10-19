#include "net.h"
#include "secrets.h"

// TODO(member2): connect to WiFi using WIFI_SSID / WIFI_PASSWORD.
void netSetup() {
}

// TODO(member2): reconnect WiFi and MQTT when lost (non-blocking, with a
// retry interval), re-apply stored subscriptions, and run the MQTT client loop.
void netLoop() {
}

// TODO(member2): report whether the MQTT session is up.
bool netIsConnected() {
  return false;
}

// TODO(member2): publish payload to topic; return false when offline.
bool netPublish(const char* topic, const char* payload) {
  return false;
}

// TODO(member2): store topic + handler, subscribe now if connected, and route
// incoming messages on that topic to the handler.
bool netSubscribe(const char* topic, MqttHandler handler) {
  return false;
}
