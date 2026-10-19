// MQTT topics - must match firmware/include/topics.h and docs/topics.md.
// Change only through a pull request reviewed by all members.

// ESP32 -> web
export const TOPIC_DHT = "study/dht"; // member1 {"temp": number, "hum": number}
export const TOPIC_LIGHT = "study/light"; // member2 {"raw": number, "level": string}
export const TOPIC_RFID = "study/rfid"; // member2 {"uid": string, "action": "start"|"stop"}

// web -> ESP32
export const TOPIC_TIMER = "study/timer"; // member3 {"minutes": number}
export const TOPIC_LCD = "study/lcd"; // member3 {"text": string}
