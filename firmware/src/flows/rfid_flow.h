#pragma once
#include <Arduino.h>

// RC522 RFID study sessions -> MQTT study/rfid {"uid": string, "action": "start"|"stop"}
// Owner: duong

void rfidSetup();
void rfidLoop();

