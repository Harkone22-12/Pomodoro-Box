# MQTT topics

Single source of truth for topics and payloads. Firmware constants live in
`firmware/include/topics.h`, and Node-RED flows subscribe/publish to these exact topics
(e.g., `nodered/flows_minh.json`). If you change a topic, update `docs/topics.md`,
`firmware/include/topics.h`, and the corresponding Node-RED flow in the same pull request.

All payloads are JSON objects encoded as UTF-8.

| Topic | Direction | Publisher | Subscriber | Payload | Owner |
|---|---|---|---|---|---|
| `study/dht` | ESP32 → Node-RED | ESP32 `dht_flow` | Node-RED (`flows_minh.json`) | `{"temp": number, "hum": number}` | minh |
| `study/light` | ESP32 → Node-RED | ESP32 `light_flow` | Node-RED (light flow) | `{"raw": number, "level": string}` | duong |
| `study/rfid` | ESP32 → Node-RED | ESP32 `rfid_flow` | Node-RED (rfid flow) | `{"uid": string, "action": "start" \| "stop"}` | duong |
| `study/focus` | ESP32 → Node-RED | ESP32 `focus_flow` | Node-RED (focus flow) | `{"status": "busy" \| "idle"}` | duong |
| `study/timer` | Node-RED → ESP32 | Node-RED (timer flow) | ESP32 `timer_flow` | `{"minutes": number}` | hao |
| `study/lcd` | Node-RED → ESP32 | Node-RED (lcd flow) | ESP32 `lcd_flow` | `{"text": string}` | hao |

The focus flow (button → red LED) runs on the ESP32 and publishes `study/focus` to sync status with Node-RED Dashboard 2.0.

## Field notes

- `temp`: °C, `hum`: % relative humidity.
- `raw`: ADC reading 0–4095 (12-bit). `level`: label values to be chosen by duong. Write them here once decided.
- `uid`: card UID as a hex string. Agree on the format (upper/lower case, separators) and write it here.
- `minutes`: a positive number. Valid range to be chosen by hao.
- `text`: the LCD1602 shows 2 × 16 characters. Decide how longer text is handled.

## Suggested conventions (team to confirm)

- Sensor topics: QoS 0, not retained.
- Command topics (`study/timer`, `study/lcd`): QoS 1, **not retained**. A retained
  timer command would fire again every time the ESP32 reconnects.

## Node-RED Dashboard 2.0 UI sync

Node-RED Dashboard 2.0 (`@flowfuse/node-red-dashboard`) pushes state updates directly
from Node-RED flows to the browser over its built-in Socket.IO channel on `/dashboard`.
No custom backend REST API or manual Socket.IO event contract is required.
