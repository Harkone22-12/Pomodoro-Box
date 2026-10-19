#pragma once

// MQTT topics - must match backend/src/topics.ts and docs/topics.md.
// Change only through a pull request reviewed by all members.

// ESP32 -> web
#define TOPIC_DHT   "study/dht"    // member1 {"temp": number, "hum": number}
#define TOPIC_LIGHT "study/light"  // member2 {"raw": number, "level": string}
#define TOPIC_RFID  "study/rfid"   // member2 {"uid": string, "action": "start"|"stop"}

// web -> ESP32
#define TOPIC_TIMER "study/timer"  // member3 {"minutes": number}
#define TOPIC_LCD   "study/lcd"    // member3 {"text": string}
