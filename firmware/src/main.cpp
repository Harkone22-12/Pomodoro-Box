// Entry point. Only calls setup/loop functions of the network layer and each
// flow. Do not put flow logic here - it belongs in src/flows/.
#include <Arduino.h>

#include "net/net.h"
#include "flows/dht_flow.h"
#include "flows/light_flow.h"
#include "flows/timer_flow.h"
#include "flows/rfid_flow.h"
#include "flows/focus_flow.h"
#include "flows/lcd_flow.h"

void setup() {
  Serial.begin(115200);

  netSetup();

  dhtSetup();
  lightSetup();
  timerSetup();
  rfidSetup();
  focusSetup();
  lcdSetup();
}

void loop() {
  netLoop();

  dhtLoop();
  lightLoop();
  timerLoop();
  rfidLoop();
  focusLoop();
  lcdLoop();
}
