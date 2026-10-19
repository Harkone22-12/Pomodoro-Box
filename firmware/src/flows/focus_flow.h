#pragma once
#include <Arduino.h>

// Focus button -> red LED. Local on the ESP32 only, no MQTT.
// Owner: member2

void focusSetup();
void focusLoop();

