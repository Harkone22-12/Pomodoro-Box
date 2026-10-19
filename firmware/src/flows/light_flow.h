#pragma once
#include <Arduino.h>

// LDR (analog) -> MQTT study/light {"raw": number, "level": string}
// Owner: member2

void lightSetup();
void lightLoop();

