# Study Station (Trạm góc học tập)

University IoT project. An ESP32 box sits on a study desk. Its sensors send data over
MQTT to our own web app (no Node-RED), and the web app sends commands back to the ESP32.

```
ESP32 ──MQTT──▶ Mosquitto ──MQTT──▶ backend (Express + Socket.IO) ──▶ MongoDB Atlas
  ▲                                     │  ▲
  └──────────────MQTT───────────────────┘  └──Socket.IO──▶ frontend (React)
```

> This repository is a **scaffold**. Every flow is a stub marked `TODO(memberN)`.
> Each member implements their own flows. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Repository layout

```
firmware/   ESP32 DevKit V1, PlatformIO, Arduino framework
backend/    Node.js + Express + MQTT.js + Socket.IO + Mongoose
frontend/   React + TypeScript + Vite + Socket.IO client
docs/       topics.md: every MQTT topic and Socket.IO event
mosquitto/  local broker config for docker-compose
```

## Flows

Full payload details: [docs/topics.md](docs/topics.md).

| Flow | Owner | Devices | Topic | JSON | Firmware | Backend | Frontend |
|---|---|---|---|---|---|---|---|
| DHT | member1 | DHT22 | `study/dht` (ESP32 → web) | `{"temp": number, "hum": number}` | `src/flows/dht_flow.*` | `src/flows/dht.flow.ts` | `src/flows/DhtPanel.tsx` |
| Light | member2 | LDR (analog) | `study/light` (ESP32 → web) | `{"raw": number, "level": string}` | `src/flows/light_flow.*` | `src/flows/light.flow.ts` | `src/flows/LightPanel.tsx` |
| RFID sessions | member2 | RC522 | `study/rfid` (ESP32 → web) | `{"uid": string, "action": "start"\|"stop"}` | `src/flows/rfid_flow.*` | `src/flows/rfid.flow.ts` | `src/flows/RfidPanel.tsx` |
| Focus | member2 | button, red LED | none (local on ESP32) | none | `src/flows/focus_flow.*` | none | none |
| Timer | member3 | active buzzer | `study/timer` (web → ESP32) | `{"minutes": number}` | `src/flows/timer_flow.*` | `src/flows/timer.flow.ts` | `src/flows/TimerForm.tsx` |
| LCD | member3 | LCD1602 I2C | `study/lcd` (web → ESP32) | `{"text": string}` | `src/flows/lcd_flow.*` | `src/flows/lcd.flow.ts` | `src/flows/LcdForm.tsx` |

Advanced goals:

- **member1**: time-series storage, chart, own analysis model.
- **member2**: RFID study sessions, button → red LED, Telegram alert
  (`backend/src/notify/telegram.ts`), weekly email (`backend/src/notify/email.ts`).
- **member3**: own website, register/login with the database (`backend/src/auth/`,
  `frontend/src/auth/`), web text → LCD.

### Shared foundation

| Part | Owner | Files |
|---|---|---|
| WiFi + MQTT connect, auto-reconnect | member2 | `firmware/src/net/net.*` |
| Broker connection | member1 | `backend/src/mqtt/client.ts` |
| MongoDB connection | member1 | `backend/src/db/connect.ts` |
| Server, Socket.IO, auth routes | member3 | `backend/src/server.ts`, `backend/src/socket.ts`, `backend/src/auth/` |
| Frontend layout | member3 | `frontend/src/App.tsx`, `frontend/src/layout/`, `frontend/src/socket.ts` |
| Pin map, topics, `main.cpp`, flow registry | everyone, via PR | `firmware/include/pins.h`, `firmware/include/topics.h`, `firmware/src/main.cpp`, `backend/src/topics.ts`, `backend/src/flows/index.ts` |

## Pin map (ESP32 DevKit V1)

This is a **proposed** map and can change. Source of truth: `firmware/include/pins.h`.

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

Requirements: Docker, Node.js ≥ 20.6, PlatformIO (VS Code extension or CLI),
a MongoDB Atlas cluster.

### 1. Broker

```bash
docker compose up -d          # Mosquitto on port 1883
```

### 2. Backend

```bash
cd backend
cp .env.example .env          # fill in MONGODB_URI etc.
npm install
npm run dev                   # http://localhost:3000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173 (proxies /api and Socket.IO to :3000)
```

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

## Pending dependencies

Not added yet. Each needs team approval before it goes into `package.json` /
`platformio.ini`. Candidates:

- Firmware: MQTT client, DHT22 driver, MFRC522 driver, LCD1602 I2C driver, JSON library.
- Backend: password hashing and session/token library (auth), SMTP library (email),
  scheduler (weekly email). Telegram can use plain `fetch` with no library.
- Frontend: chart library, router.
