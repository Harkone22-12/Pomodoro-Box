# Wireframe v3: "Focus Grid"

A mid-fidelity wireframe of the Study Station website. It covers every page described in
`proposal/sections/02_thiet_ke.tex` (section 2.2): Đăng nhập, Tạo tài khoản, Tổng quan, Phiên học,
Lịch sử and Cài đặt (all four tabs), on desktop, tablet and phone.

Unlike v1 and v2, the source lives in this folder: [`wireframe.html`](wireframe.html) is one static
file with no dependencies. Open it in a browser and use the menu, or jump to a screen with
`wireframe.html?screen=<name>` (`dang-nhap`, `dang-ky`, `tong-quan`, `phien-hoc`, `lich-su`,
`cai-dat`). Cài đặt also takes `&tab=` (`tai-khoan`, `pomodoro`, `canh-bao`, `thiet-bi`).

All numbers are sample data. Buttons do nothing: this is a layout document, not flow code.

## Design decisions

The design tokens come from the UI/UX Pro Max skill data:

| Token | Choice | Source in the skill data |
|---|---|---|
| Style | Minimalism & Swiss + Data-Dense Dashboard, 12-column grid, 10 px radius | `styles.csv` |
| Colour | Neutral slate, focus red `#DC2626` for the one main action per card, break green `#047857` for "connected" | `colors.csv`, "Timer & Pomodoro" |
| Type | Fira Sans (text) and Fira Code (numbers, UIDs, MQTT payloads) | `typography.csv`, "Dashboard Data" |
| Charts | Line chart for 24 h trend, calendar heatmap for 30 days, bars for rounds per hour | `charts.csv` |

Rules applied on every screen:

- Touch targets are at least 44 px high; phone navigation is a bottom bar with 4 items.
- State is never shown by colour alone: the status dot always has a text label, and the humidity
  line is dashed while the temperature line is solid.
- Each card carries dashed tags with its Node-RED group (`grp_*`) and function ID from the proposal,
  so a screen can be checked against the tables in section 2.2.
- Breakpoints match the proposal: sidebar 248 px above 1100 px, icon rail 88 px from 761 to 1100 px,
  one column with top bar and bottom tabs at 760 px or less.

## Screens

### Desktop (1440 px)

| File | Screen | Function IDs |
|---|---|---|
| `01-dang-nhap-desktop.png` | Đăng nhập: Pomodoro cycle strip, 3 steps, form, box status footer | 11 |
| `02-dang-ky-desktop.png` | Tạo tài khoản, with the password strength meter | 11 |
| `03-tong-quan-desktop.png` | Tổng quan: quick timer, room now, card session, LCD preview, today and 7 days | 1, 2, 3, 4, 5, 6, 9 |
| `04-phien-hoc-desktop.png` | Phiên học: timer modes, MQTT payload preview, LCD composer, command log | 3, 5, 7 |
| `05-lich-su-desktop.png` | Lịch sử: KPIs, 30-day calendar, rounds per hour, 24 h chart, best conditions, sessions | 7, 8, 13 |
| `06-cai-dat-pomodoro-desktop.png` | Cài đặt, Pomodoro tab: sliders and cycle preview | 3 |
| `07-cai-dat-canh-bao-desktop.png` | Cài đặt, Cảnh báo tab: Telegram, weekly email, room thresholds | 9, 10 |
| `08-cai-dat-thiet-bi-desktop.png` | Cài đặt, Thiết bị và thẻ tab: box status, Wi-Fi setup note, card whitelist | 2, 12 |
| `09-cai-dat-tai-khoan-desktop.png` | Cài đặt, Tài khoản tab: profile, change password, sign out | 11 |

### Tablet (1024 px)

| File | Screen |
|---|---|
| `10-tong-quan-tablet.png` | Tổng quan with the icon rail |

### Phone (390 px, 2× pixel density)

| File | Screen |
|---|---|
| `11-dang-nhap-mobile.png` | Đăng nhập, form first |
| `12-tong-quan-mobile.png` | Tổng quan |
| `13-phien-hoc-mobile.png` | Phiên học, with the command log as a list |
| `14-lich-su-mobile.png` | Lịch sử, with the sessions table as a list |
| `15-cai-dat-mobile.png` | Cài đặt, Cảnh báo tab |

### One-tap session rating

When a card tap ends a session, the "Phiên quẹt thẻ" card asks "Phiên vừa rồi thế nào?" with three
buttons (Mất tập trung, Tạm ổn, Tập trung tốt). One tap saves the answer, with no submit button;
"Bỏ qua" dismisses it. Lịch sử shows the answer in the "Đánh giá" column. Open this state with
`wireframe.html?screen=tong-quan&state=danh-gia`.

| File | Screen |
|---|---|
| `16-danh-gia-desktop.png` | Tổng quan right after the session ends (1440 px) |
| `17-danh-gia-mobile.png` | The same state on a phone (390 px) |

The rating is not in the proposal's function list and `docs/topics.md` has no event or field for
it, so the real app needs a contract PR before it can store one.

## Regenerating the screenshots

```powershell
powershell -ExecutionPolicy Bypass -File docs\prototype\v3-focus-grid\capture.ps1
```

The script uses headless Microsoft Edge and takes full-page captures. It needs internet access once
to load the two Google Fonts; without it the page falls back to Segoe UI and Consolas.
