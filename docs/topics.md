# MQTT topics

Single source of truth for topics and payloads. Code copies live in
`firmware/include/topics.h` and `backend/src/topics.ts`. If you change a topic,
change all three in the same pull request, and get it reviewed by all members.

All payloads are JSON objects encoded as UTF-8.

| Topic | Direction | Publisher | Subscriber | Payload | Owner |
|---|---|---|---|---|---|
| `study/dht` | ESP32 → web | ESP32 `dht_flow` | backend `dht.flow.ts` | `{"temp": number, "hum": number}` | member1 |
| `study/light` | ESP32 → web | ESP32 `light_flow` | backend `light.flow.ts` | `{"raw": number, "level": string}` | member2 |
| `study/rfid` | ESP32 → web | ESP32 `rfid_flow` | backend `rfid.flow.ts` | `{"uid": string, "action": "start" \| "stop"}` | member2 |
| `study/timer` | web → ESP32 | backend `timer.flow.ts` | ESP32 `timer_flow` | `{"minutes": number}` | member3 |
| `study/lcd` | web → ESP32 | backend `lcd.flow.ts` | ESP32 `lcd_flow` | `{"text": string}` | member3 |

The focus flow (button → red LED) runs only on the ESP32 and has no topic.

## Field notes

- `temp`: °C, `hum`: % relative humidity.
- `raw`: ADC reading 0–4095 (12-bit). `level`: label values to be chosen by member2. Write them here once decided.
- `uid`: card UID as a hex string. Agree on the format (upper/lower case, separators) and write it here.
- `minutes`: a positive number. Valid range to be chosen by member3.
- `text`: the LCD1602 shows 2 × 16 characters. Decide how longer text is handled.

## Suggested conventions (team to confirm)

- Sensor topics: QoS 0, not retained.
- Command topics (`study/timer`, `study/lcd`): QoS 1, **not retained**. A retained
  timer command would fire again every time the ESP32 reconnects.

## Socket.IO events (backend ↔ browser)

These names are a proposal; the owner of each flow can rename theirs, but must update this table.

| Event | Direction | Payload | Owner |
|---|---|---|---|
| `dht` | server → client | same as `study/dht` (+ timestamp) | member1 |
| `light` | server → client | same as `study/light` (+ timestamp) | member2 |
| `rfid` | server → client | same as `study/rfid` (+ timestamp) | member2 |
| `timer:set` | client → server | `{"minutes": number}` | member3 |
| `lcd:set` | client → server | `{"text": string}` | member3 |
