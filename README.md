# Study Station (Trạm học tập Pomodoro)

University IoT project. An ESP32 box sits on a study desk. Its sensors send data over
MQTT to **Node-RED**, which processes flows, persists time-series & session data to
**Supabase Cloud PostgreSQL**, and renders the live web interface via **Node-RED Dashboard 2.0**
(`@flowfuse/node-red-dashboard`).

```text
ESP32 ──MQTT──▶ Mosquitto ──MQTT──▶ Node-RED (flows + Dashboard 2.0 UI) ──HTTPS/REST──▶ Supabase PostgreSQL
  ▲                                        │
  └──────────────────MQTT──────────────────┘
```

> Each member implements their own flows on their branch. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Team

Each member works on the git branch named after their handle. The same handle
marks their files (`Owner: <handle>`) and stubs (`TODO(<handle>)`).

| Handle / branch | Member |
|---|---|
| `minh` | Trần Nguyễn Tuấn Minh |
| `duong` | Nguyễn Quốc Dương |
| `hao` | La Anh Hào |

## Repository layout

```text
firmware/   ESP32 DevKit V1, PlatformIO, Arduino framework
nodered/    Node-RED flows (flows_*.json), pure JS logic/tests, Supabase SQL schema
docs/       topics.md: MQTT topic & payload contract, Wireframe/, design/
mosquitto/  local broker config for docker-compose
proposal/   official LaTeX project proposal (main.tex, sections/)
```

*(Note: `backend/` and `frontend/` are legacy Express/React scaffolds kept from an earlier draft and are not used in the Node-RED Dashboard 2.0 architecture.)*

## Flows

Full payload details: [docs/topics.md](docs/topics.md).

| Flow | Owner | Devices | Topic | JSON | Firmware | Node-RED / Dashboard 2.0 |
|---|---|---|---|---|---|---|
| DHT | minh | DHT22 | `study/dht` (ESP32 → Node-RED) | `{"temp": number, "hum": number}` | `src/flows/dht_flow.*` | `nodered/flows_minh.json` (`/minh`) |
| Light | duong | LDR (analog) | `study/light` (ESP32 → Node-RED) | `{"raw": number, "level": string}` | `src/flows/light_flow.*` | Dashboard 2.0 Light gauge/alert |
| RFID sessions | duong | RC522 | `study/rfid` (ESP32 → Node-RED) | `{"uid": string, "action": "start"\|"stop"}` | `src/flows/rfid_flow.*` | Dashboard 2.0 Session panel |
| Focus | duong | button, red LED | `study/focus` (ESP32 → Node-RED) | `{"status": "busy"\|"idle"}` | `src/flows/focus_flow.*` | Dashboard 2.0 Focus indicator |
| Timer | hao | active buzzer | `study/timer` (Node-RED → ESP32) | `{"minutes": number}` | `src/flows/timer_flow.*` | Dashboard 2.0 Timer controls |
| LCD | hao | LCD1602 I2C | `study/lcd` (Node-RED → ESP32) | `{"text": string}` | `src/flows/lcd_flow.*` | Dashboard 2.0 LCD input |

Advanced goals:

- **minh**: Supabase time-series storage (`sensor_data`, `study_sessions`), 24h chart & stats (YC4, YC5), optimal study condition analysis model (YC11).
- **duong**: RFID study sessions, button → red LED (YC1), LDR light alert (YC2), Telegram alert (YC6), weekly email backup (YC7).
- **hao**: LCD1602 I2C Vietnamese text (YC3), account authentication with Supabase `bcrypt` (YC9), ESP32 SoftAP Wi-Fi provisioning server (YC12).

### Shared foundation

| Part | Owner | Files |
|---|---|---|
| WiFi + MQTT connect, auto-reconnect | duong | `firmware/src/net/net.*` |
| Supabase schema (`sensor_data`, `study_sessions`) | minh | `nodered/supabase_schema.sql` |
| Pin map, topics, `main.cpp` | everyone, via PR | `firmware/include/pins.h`, `firmware/include/topics.h`, `firmware/src/main.cpp`, `docs/topics.md` |

## Pin map (ESP32 DevKit V1)

Source of truth: `firmware/include/pins.h`.

| Device | Pin(s) | Notes |
|---|---|---|
| DHT22 | GPIO4 | |
| LDR | GPIO34 | ADC1, so it works with WiFi on. Input-only |
| Active buzzer | GPIO25 | Module is **active-LOW** (LOW = sound) |
| Button | GPIO27 | `INPUT_PULLUP`, pressed = LOW |
| Red LED | GPIO26 | |
| LCD1602 I2C | SDA = GPIO21, SCL = GPIO22 | |
| RC522 (SPI) | SS = 5, SCK = 18, MOSI = 23, MISO = 19, RST = 17 | 3.3 V only |

## Running locally

Requirements: Docker, Node.js ≥ 20.6, Node-RED with `@flowfuse/node-red-dashboard`, PlatformIO (VS Code extension or CLI), and a Supabase project.

### 1. Broker

```bash
docker compose up -d          # Mosquitto on port 1883
```

### 2. Supabase

Run [nodered/supabase_schema.sql](nodered/supabase_schema.sql) in your Supabase SQL Editor.

### 3. Node-RED + Dashboard 2.0

```bash
npm install -g node-red
# Inside ~/.node-red: npm install @flowfuse/node-red-dashboard
# Set environment variables SUPABASE_URL and SUPABASE_KEY, then start Node-RED:
node-red
```

Import `nodered/flows_minh.json` in Node-RED (`http://localhost:1880`) and open Dashboard 2.0 at `http://localhost:1880/dashboard/minh`.

### 4. Firmware

```bash
cd firmware
cp include/secrets.example.h include/secrets.h   # WiFi + broker IP of your PC
pio run -t upload
pio device monitor
```

The ESP32 must reach the broker by your PC's **LAN IP**, not `localhost`. Allow
port 1883 through the Windows firewall if the ESP32 cannot connect.

To watch MQTT traffic while debugging:

```bash
docker exec -it study-station-mosquitto mosquitto_sub -t 'study/#' -v
```
