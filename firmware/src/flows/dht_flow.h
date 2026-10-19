#pragma once
#include <Arduino.h>

// DHT22 -> MQTT study/dht {"temp": number, "hum": number}
// Owner: minh

void dhtSetup();
void dhtLoop();

