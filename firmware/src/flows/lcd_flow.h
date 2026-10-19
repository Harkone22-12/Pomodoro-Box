#pragma once
#include <Arduino.h>

// MQTT study/lcd {"text": string} -> LCD1602 over I2C
// Owner: member3

void lcdSetup();
void lcdLoop();
void lcdOnMessage(const char* payload, size_t length);
