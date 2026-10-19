#pragma once
#include <Arduino.h>

// DHT22 -> MQTT study/dht {"temp": number, "hum": number}
// Owner: member1

void dhtSetup();
void dhtLoop();

