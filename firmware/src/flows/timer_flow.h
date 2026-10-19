#pragma once
#include <Arduino.h>

// MQTT study/timer {"minutes": number} -> active buzzer (active-LOW)
// Owner: member3

void timerSetup();
void timerLoop();
void timerOnMessage(const char* payload, size_t length);
