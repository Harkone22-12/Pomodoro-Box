#pragma once
#include <Arduino.h>

// Proposed pin map for ESP32 DevKit V1.
// It CAN CHANGE - if you move a pin, update this file AND the README pin table
// in the same pull request.

// minh - DHT22 temperature/humidity
constexpr uint8_t PIN_DHT = 4;

// duong - LDR (analog). GPIO34 is on ADC1, which still works while WiFi is on
// (ADC2 pins do not). Input-only pin.
constexpr uint8_t PIN_LDR = 34;

// hao - active buzzer module. The module is active-LOW: LOW = sound on.
constexpr uint8_t PIN_BUZZER = 25;
constexpr uint8_t BUZZER_ON = LOW;
constexpr uint8_t BUZZER_OFF = HIGH;

// duong - focus button (use INPUT_PULLUP: pressed = LOW) and red LED
constexpr uint8_t PIN_BUTTON = 27;
constexpr uint8_t PIN_LED = 26;

// hao - LCD1602 over I2C
constexpr uint8_t PIN_I2C_SDA = 21;
constexpr uint8_t PIN_I2C_SCL = 22;

// duong - RC522 RFID over SPI (VSPI)
constexpr uint8_t PIN_RC522_SS = 5;
constexpr uint8_t PIN_RC522_SCK = 18;
constexpr uint8_t PIN_RC522_MOSI = 23;
constexpr uint8_t PIN_RC522_MISO = 19;
constexpr uint8_t PIN_RC522_RST = 17;
