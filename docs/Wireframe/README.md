# UI wireframes: Study Station (design D, "Daylight Console")

These images show the web UI the team chose (design D). Each screen has two versions:

- `color/`: the full design with colors and real fonts.
- `lowfi/`: the same screen in grey with a hand-drawn font. Use it in the report when you want to talk about layout, not colors.

All numbers on the screens are sample data for the mockup (for example 29.5 °C, 26 rounds per week, card `A1B2C3D4`). The real values come from the ESP32 over MQTT.

## Desktop (1440 px wide)

| File | Screen | What it shows |
|---|---|---|
| `01-sign-in-desktop.png` | Sign in | Email and password form, plus a small status list of the box sensors. |
| `02-workspace-desktop.png` | Workspace | Each function is its own window: Climate (DHT22), Light (LDR), Session (RC522), Timer (buzzer), LCD 16×2 and Session log. The bar on the right opens and closes each window. Windows can be dragged, minimized and closed. |
| `03-history-desktop.png` | History | Totals for 30 days, a heatmap of when rounds are finished, temperature and humidity for 24 h, the "best conditions" box for the analysis model, and the session table. |
| `04-settings-desktop.png` | Settings | Account, Pomodoro lengths, Telegram and weekly email, device status and RFID cards. |

## Mobile (390 px wide)

On a phone the windows do not float. The user switches between them with the tab bar at the bottom.

| File | Screen | What it shows |
|---|---|---|
| `05-sign-in-mobile.png` | Sign in | Same form, one column. |
| `06-workspace-mobile-timer.png` | Workspace, Timer tab | Countdown, Send to box / Stop, today / streak / week, timer settings. |
| `07-workspace-mobile-lcd.png` | Workspace, LCD tab | LCD preview, message input (max 2 × 16 characters, no accents), quick messages. |
| `08-workspace-mobile-room.png` | Workspace, Room tab | Temperature and humidity, light level, active RFID session and the Telegram break warning. |
| `09-workspace-mobile-log.png` | Workspace, Log tab | Rounds per day this week and recent sessions. |
| `10-history-mobile.png` | History | Totals, a smaller heatmap, best conditions and the session list. |
| `11-settings-mobile.png` | Settings | Settings as grouped lists, with Sign out at the bottom. |

## Responsive rules

- Wider than 1180 px: floating windows and the icon bar on the right.
- 761 to 1180 px (tablet): windows sit in a grid; the icon bar moves to the top.
- 760 px or less (phone): one tab at a time with a bottom tab bar (Timer, LCD, Room, Log, Settings).

## Which flow each window belongs to

| Window | MQTT topic | Owner |
|---|---|---|
| Climate | `study/dht` | minh |
| Light | `study/light` | duong |
| Session | `study/rfid` | duong |
| Timer | `study/timer` | hao |
| LCD | `study/lcd` | hao |
| Session log / History | data saved in MongoDB | minh |

The focus button and red LED run only on the ESP32 and have no topic, so the web does not show the LED state.
