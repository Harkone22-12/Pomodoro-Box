#include "dht_flow.h"
#include "pins.h"
#include "topics.h"
#include "../net/net.h"

#include "dht_flow.h"
#include "pins.h"
#include "topics.h"
#include "../net/net.h"
#include <DHT.h>
#include <stdio.h>

namespace {
constexpr unsigned long DHT_INTERVAL_MS = 5000;
DHT dht(PIN_DHT, DHT22);
unsigned long lastReadMs = 0;
}  // namespace

void dhtSetup() {
  dht.begin();
}

void dhtLoop() {
  unsigned long now = millis();
  if (now - lastReadMs < DHT_INTERVAL_MS) return;
  lastReadMs = now;

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  if (isnan(temp) || isnan(hum)) return;

  char payload[64];
  snprintf(payload, sizeof(payload), "{\"temp\":%.1f,\"hum\":%.1f}", temp, hum);
  netPublish(TOPIC_DHT, payload);
}

