#pragma once

// MQTT topics - must match backend/src/topics.ts and docs/topics.md.
// Change only through a pull request reviewed by all members.

// ESP32 -> web
#define TOPIC_DHT   "study/dht"    // minh {"temp": number, "hum": number}
#define TOPIC_LIGHT "study/light"  // duong {"raw": number, "level": string}
#define TOPIC_RFID  "study/rfid"   // duong {"uid": string, "action": "start"|"stop"}

// web -> ESP32
#define TOPIC_TIMER "study/timer"  // hao {"minutes": number}
#define TOPIC_LCD   "study/lcd"    // hao {"text": string}
