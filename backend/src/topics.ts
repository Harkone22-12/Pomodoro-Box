// MQTT topics - must match firmware/include/topics.h and docs/topics.md.
// Change only through a pull request reviewed by all members.

// ESP32 -> web
export const TOPIC_DHT = "study/dht"; // minh {"temp": number, "hum": number}
export const TOPIC_LIGHT = "study/light"; // duong {"raw": number, "level": string}
export const TOPIC_RFID = "study/rfid"; // duong {"uid": string, "action": "start"|"stop"}
export const TOPIC_FOCUS = "study/focus"; // duong {"status": "busy"|"idle"}

// web -> ESP32
export const TOPIC_TIMER = "study/timer"; // hao {"minutes": number}
export const TOPIC_LCD = "study/lcd"; // hao {"text": string}
