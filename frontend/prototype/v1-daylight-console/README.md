# Study Station: clickable UI prototype

A static prototype of the web app described in the proposal, built on design D
("Daylight Console", see `docs/Wireframe/`) with square corners. Screenshots are in
[`docs/prototype/v1-daylight-console/`](../../../docs/prototype/v1-daylight-console/README.md).

- **Not the real app.** It is plain HTML, CSS and JavaScript with no build step and
  no npm packages. It is not part of the React app in `frontend/src`, and it does
  not connect to MQTT, Socket.IO or the backend.
- **All data is sample data.** The sensors change a little every few seconds so the
  page looks alive. When you press a button, a toast shows which topic and payload
  from `docs/topics.md` the real app would send.

## Open it

Double-click `index.html`, or open it in any modern browser. Fonts come from Google
Fonts. Without internet the page falls back to system fonts.

| Screen | URL hash |
|---|---|
| Sign in / Create account | `#/signin`, `#/register` |
| Workspace | `#/workspace` (phone tabs: `#/workspace/timer`, `/lcd`, `/room`, `/log`) |
| History | `#/history` |
| Settings | `#/settings` |

## Responsive layout

| Width | Layout |
|---|---|
| > 1180 px | Floating windows you can drag, minimize and close. The icon bar on the right opens and closes them. "Arrange" puts them back. |
| 761–1180 px | Windows in two columns. The icon bar moves to the top. |
| ≤ 760 px | One tab at a time with a bottom tab bar: Timer, LCD, Room, Log, Settings. |

## What you can try

| Window | Feature | What happens |
|---|---|---|
| Timer | CN03 | Pick a preset or a custom length (1–120 min) and press **Send to box**. The page counts down and, at 0, shows the buzzer toast and moves to the next round. |
| LCD 16×2 | YC3 | Type up to 32 characters. Vietnamese accents are removed and the preview wraps the text onto 2 × 16 cells. |
| Climate / Light | CN01, CN02 | Simulated DHT22 and LDR readings. "Enough light" or "Too dim" depends on the threshold. |
| Session | YC2, YC6 | **Simulate card tap** starts and stops a session. A warning shows after 50 min without a break. |
| Session log / History | YC4, YC5, YC11 | Bars per week, month or year; a heatmap; the 24 h chart; the model box; **Export CSV**. |
| Settings | YC9, YC6, YC7 | Validated Pomodoro lengths, Telegram and email switches, and adding or removing RFID cards. |
| Sign in / Register | YC9 | Inline validation. Any email and an 8-character password work. |

## Open questions found while building it

These belong in `docs/topics.md` (via a PR) before the real flows are written:

1. **There is no stop command.** `study/timer` only has `{"minutes": number}`. The **Stop** button
   in the prototype only stops the countdown on the page and says so.
2. **LCD wrapping.** The prototype wraps at a word boundary inside 2 × 16 and removes
   accents. The `text` field notes say this is still undecided.
3. **Light `level` labels.** The prototype uses `du_sang` / `thieu_sang` from the proposal.
   The field notes say the labels are still to be chosen.
