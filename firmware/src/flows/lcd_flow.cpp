#include "lcd_flow.h"
#include "pins.h"
#include "topics.h"
#include "../net/net.h"

// TODO(member3): Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL), init the LCD, netSubscribe(TOPIC_LCD, lcdOnMessage).
void lcdSetup() {
}

// TODO(member3): scroll or refresh the display if needed.
void lcdLoop() {
}

// TODO(member3): parse {"text": string} and show it on the 16x2 display.
void lcdOnMessage(const char* payload, size_t length) {
}
