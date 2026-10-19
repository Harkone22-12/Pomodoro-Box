#pragma once
#include <Arduino.h>

// Shared network layer: WiFi + MQTT connection with auto-reconnect.
// Owner: member2
//
// Contract used by every flow:
// - netLoop() must never block for long; flows keep running while offline.
// - netSubscribe() must remember the topic/handler and re-subscribe after
//   every reconnect, so flows can call it once from their setup function.

using MqttHandler = void (*)(const char* payload, size_t length);

void netSetup();
void netLoop();
bool netIsConnected();
bool netPublish(const char* topic, const char* payload);
bool netSubscribe(const char* topic, MqttHandler handler);
