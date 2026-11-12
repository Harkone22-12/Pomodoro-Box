# Prototype v2: "Cà chua" (tomato)

The folder is still called `v2-teal-desk` (the first version used a teal app shell), so links keep working.

A second, completely different UI prototype for Trạm học tập (Study Station). It is not
the design in the proposal; that one is [`../v1-daylight-console/`](../v1-daylight-console/README.md).
Screenshots: [`docs/prototype/v2-teal-desk/`](../../../docs/prototype/v2-teal-desk/README.md).

- **The UI is in Vietnamese.**
- **No rounded corners** anywhere. The only circles are the status dot and the LED in the box drawing.
- Plain HTML, CSS and JavaScript. There is no build step and there are no npm packages. It is not part of
  `frontend/src` and does not connect to MQTT or the backend. All data is sample data.

Open `index.html` in a browser.

## Design choices

| | v1 Daylight Console (proposal) | v2 Cà chua |
|---|---|---|
| Layout | Top bar, floating windows, icon dock on the right | Cream sidebar on the left closed by a 2 px ink rule, square tile grid |
| Style | Grid background, shadows, amber | Flat tiles with warm 1 px lines; 2 px ink rules; one panel per screen with a solid tomato offset shadow |
| Font | Space Grotesk + JetBrains Mono | **Nunito** (200–700) + VT323 for the LCD only |
| Timer | Progress bar | Thin tomato numerals in a square frame that fills around the countdown (teal during a break) |
| LCD | Blue backlight | Yellow-green backlight, dot-matrix font |
| Phone | 5 tabs | 4 tabs: Tổng quan, Phiên học, Lịch sử, Cài đặt |
| Sign in | Grid background, card | Same theme as the rest of the app |

**One theme on every screen: "Cà chua" (tomato),** because *pomodoro* means tomato. The pages
have a cream background `#fbf5ee`, brown ink `#2b1a12` and tomato accents (`#ea580c` for
graphics and very large numbers, `#c2410c` for buttons, links and small text, 5.2:1 with white).
Corners are still square.

- **Sign in / register:** a header bar with a 2 px ink rule, a large thin "25:00" with a blinking
  colon, a strip showing one Pomodoro cycle (each segment as wide as its minutes), and the form
  in a card with a 2 px ink border and a solid tomato offset shadow. The box status is in the footer.
- **App screens use the same pieces:** the sidebar (and the phone app bar and bottom bar) is
  closed by a 2 px ink rule like the sign-in header; each page title sits on a 2 px ink rule; the
  main panel of a screen (the timer on Tổng quan and Phiên học, the form in Cài đặt) is the
  sign-in card with its tomato shadow; the countdown uses the same thin tomato numerals as "25:00".
  Primary and outline buttons have a 2 px ink border and lift onto an ink shadow on hover, like
  the sign-in button. The selected item (sidebar, mode switch, settings tab) is an ink block.
- **Color meaning:** tomato = focus time, brand and the main action. Teal (`#2a9d8f`, `#0f766e`)
  = breaks and "ok" states, the same teal as the break segments in the cycle strip. Amber =
  warning, red = error. The model panel in Lịch sử is the one dark tile, in brand ink.

**Why Nunito:** its strokes have rounded ends (less sharp than geometric grotesques), it has
light weights (200 for the big numbers, 300 for headings), and it ships the `vietnamese`
subset, so stacked diacritics such as *ậ, ẩ, ữ, ở* render cleanly. Body text stays at 400 for
contrast. Labels use sentence case, because all-caps Vietnamese looks cramped.

Colors (tokens at the top of `styles.css`): background `#fbf5ee`, tiles `#ffffff`, ink `#2b1a12`
(15:1 on cream), muted text `#6f5a4d` (6.0:1 on cream), lines `#e6d8ca` / `#d6c5b5`, tomato
`#ea580c` (graphics only) / `#c2410c` (text and buttons) / `#9a3412` (hover), break teal
`#2a9d8f` / `#0f766e`.

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

## One-tap session rating

Ending a session with the simulated card tap shows a three-button rating in the session card. One tap saves it (with Undo in the toast) and it appears in the History table and the CSV export. Open `index.html?demo=rate` to load the page in that state.

The rating lives only in the browser. The real app needs somewhere to send and store it, and `docs/topics.md` has no event or field for that yet, so it needs a contract PR first.
