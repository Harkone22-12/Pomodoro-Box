#pragma once
#include <Arduino.h>

// LDR (analog) -> MQTT study/light {"raw": number, "level": string}
// Owner: duong

void lightSetup();
void lightLoop();

