# Prototype v2: "Teal Desk"

A second, completely different UI prototype for Trạm học tập (Study Station). It is not
the design in the proposal; that one is [`../v1-daylight-console/`](../v1-daylight-console/README.md).
Screenshots: [`docs/prototype/v2-teal-desk/`](../../../docs/prototype/v2-teal-desk/README.md).

- **The UI is in Vietnamese.**
- **No rounded corners** anywhere. The only circles are the status dot and the LED in the box drawing.
- Plain HTML, CSS and JavaScript. There is no build step and there are no npm packages. It is not part of
  `frontend/src` and does not connect to MQTT or the backend. All data is sample data.

Open `index.html` in a browser.

## Design choices

| | v1 Daylight Console (proposal) | v2 Teal Desk |
|---|---|---|
| Layout | Top bar, floating windows, icon dock on the right | Dark teal sidebar on the left, square tile grid |
| Style | Grid background, shadows, amber | Flat: 1 px lines, no shadows, teal + orange |
| Font | Space Grotesk + JetBrains Mono | **Nunito** (200–700) + VT323 for the LCD only |
| Timer | Progress bar | A square frame that fills around the countdown |
| LCD | Blue backlight | Yellow-green backlight, dot-matrix font |
| Phone | 5 tabs | 4 tabs: Tổng quan, Phiên học, Lịch sử, Cài đặt |
| Sign in | Grid background, card | Its own "Cà chua" (tomato) theme, see below |

**Sign-in and register screens:** these use a separate warm theme, because *pomodoro* means
tomato. The page has a cream background `#fbf5ee`, brown text `#2b1a12` and tomato accents
(`#ea580c` for graphics, `#c2410c` for the button and links, 5.2:1 with white). There is a
header bar with a 2 px rule, and the hero is a large thin "25:00" with a blinking colon. A strip
shows one Pomodoro cycle, with each segment as wide as its minutes. The form sits in a card with a
2 px border and a solid tomato offset shadow, and the box status is in the footer.
Corners are still square.

**Why Nunito:** its strokes have rounded ends (less sharp than geometric grotesques), it has
light weights (200 for the big numbers, 300 for headings), and it ships the `vietnamese`
subset, so stacked diacritics such as *ậ, ẩ, ữ, ở* render cleanly. Body text stays at 400 for
contrast. Labels use sentence case, because all-caps Vietnamese looks cramped.

Colors: primary `#0f766e` (5.5:1 with white), accent `#ea580c` (graphics only; orange text
uses `#c2410c`), background `#f3f6f5`, sidebar `#0b3b37`.

## Screens (URL hash)

| Screen | Hash | Features |
|---|---|---|
| Đăng nhập / Tạo tài khoản | `#/signin`, `#/register` | YC9: inline validation, show password, strength meter |
| Tổng quan | `#/home` | CN01, CN02, CN03, YC2, YC3, YC6: timer, room (temperature, humidity, light with tips), card session, LCD, today, 7 days |
| Phiên học | `#/session` | CN03, YC3: mode, custom stepper 1–120, MQTT payload preview, LCD composer with accent removal and per-line counters, command log |
| Lịch sử | `#/history` | YC4, YC5, YC11: KPIs, 30-day calendar, rounds per hour with the best window, 24 h chart, model panel, CSV export |
| Cài đặt | `#/settings/account`, `/pomodoro`, `/alerts`, `/device` | YC9, YC6, YC7: sliders for lengths and thresholds, switches, RFID cards |

## Responsive layout

| Width | Layout |
|---|---|
| > 1100 px | 248 px sidebar with live box status, 12-column grid |
| 761–1100 px | 88 px icon rail |
| ≤ 760 px | Top app bar + bottom tab bar (4 items); Tổng quan covers the room data |

## Open questions (same as v1, for `docs/topics.md`)

1. **There is no stop command** for `study/timer`. **Dừng** only stops the countdown on the page.
2. **LCD text:** the prototype removes accents and cuts the text to 32 characters in the web app, then
   wraps it at a word boundary.
3. **Light `level` labels:** the prototype uses `du_sang` / `thieu_sang` from the proposal.
