#pragma once
#include <Arduino.h>

// RC522 RFID study sessions -> MQTT study/rfid {"uid": string, "action": "start"|"stop"}
// Owner: member2

void rfidSetup();
void rfidLoop();

