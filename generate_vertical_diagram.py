import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

matplotlib.rcParams['font.family'] = 'Times New Roman'
matplotlib.rcParams['mathtext.fontset'] = 'stix'

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proposal", "assets", "diagrams")
os.makedirs(out_dir, exist_ok=True)

# Kích thước khung trang in dọc A4: 10.3 x 15.8 inch (thêm biên phải cho luồng SoftAP)
fig = plt.figure(figsize=(10.3, 15.8), dpi=300)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10.3)
ax.set_ylim(0, 15.8)
ax.axis('off')

DASHDOT = (0, (5, 2, 1.5, 2))


def draw_rbox(x, y, w, h, bg='#ffffff', border='#000000', lw=1.5, rx=0.15):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.01,rounding_size={rx}",
        facecolor=bg, edgecolor=border, linewidth=lw, zorder=2
    )
    ax.add_patch(box)
    return box


def draw_vert_arrow(x, y1, y2, label="", style='solid', is_bidi=False, xshift=0.15, lalign='left'):
    arrowstyle = "<|-|>" if is_bidi else "-|>"
    ax.annotate(
        '', xy=(x, y2), xytext=(x, y1),
        arrowprops=dict(arrowstyle=arrowstyle, color='#000000', lw=2.3, linestyle=style, mutation_scale=17),
        zorder=4
    )
    if label:
        ym = (y1 + y2) / 2
        ax.text(
            x + xshift, ym, label, ha=lalign, va='center',
            fontsize=10.6, fontweight='bold', color='#000000',
            bbox=dict(boxstyle="square,pad=0.15", fc="#ffffff", ec="#888888", lw=0.7),
            zorder=5
        )


def draw_multi_arrows(xs, y1, y2, styles, label):
    for x, st in zip(xs, styles):
        ax.annotate(
            '', xy=(x, y2), xytext=(x, y1),
            arrowprops=dict(arrowstyle="<|-|>", color='#000000', lw=2.0, linestyle=st, mutation_scale=15),
            zorder=4
        )
    xm = sum(xs) / len(xs)
    ym = (y1 + y2) / 2
    ax.text(
        xm, ym, label, ha='center', va='center',
        fontsize=10.4, fontweight='bold', color='#000000',
        bbox=dict(boxstyle="square,pad=0.16", fc="#ffffff", ec="#888888", lw=0.7),
        zorder=5
    )


# --- 1. TẦNG 1: NGOẠI VI & PHẦN CỨNG BÀN HỌC (y = 14.3 -> 15.25) ---
ax.text(4.83, 15.55, "1. LINH KIỆN NGOẠI VI & PHẦN CỨNG BÀN HỌC", ha='center', va='center', fontsize=13.8, fontweight='bold', color='#111827', zorder=3)

hw_nodes = [
    ("DHT22 (ID 1)", "GPIO4 (single-bus)", 0.35, 1.68),
    ("LM393 (ID 4)", "GPIO34 (ADC1)", 2.17, 1.68),
    ("RC522 (ID 2)", "SPI, RF 13.56 MHz", 3.99, 1.68),
    ("Nút & LED (ID 6)", "GPIO27 & 26", 5.81, 1.68),
    ("Còi & LCD (ID 3, 5)", "GPIO25 & I2C", 7.63, 1.68)
]
for t, s, x, w in hw_nodes:
    draw_rbox(x, 14.3, w, 0.95, bg='#f4f4f4', border='#000000', lw=1.3)
    ax.text(x + w / 2, 14.3 + 0.62, t, ha='center', va='center', fontsize=11.3, fontweight='bold', color='#000000', zorder=3)
    ax.text(x + w / 2, 14.3 + 0.28, s, ha='center', va='center', fontsize=9.8, color='#333333', zorder=3)

# Mũi tên Tầng 1 <-> Tầng 2 (y = 14.3 <-> 13.35)
draw_vert_arrow(0.35 + 0.84, 14.3, 13.35, "[L1] GPIO4", 'solid', xshift=0.12)
draw_vert_arrow(2.17 + 0.84, 14.3, 13.35, "[L2] ADC1", 'dashed', xshift=0.12)
draw_vert_arrow(3.99 + 0.84, 14.3, 13.35, "[L2] SPI", 'dashed', is_bidi=True, xshift=0.12)
draw_vert_arrow(5.81 + 0.84, 14.3, 13.35, "[L2] Nút/LED", 'dashed', is_bidi=True, xshift=0.12)
draw_vert_arrow(7.63 + 0.84, 13.35, 14.3, "[L3] Còi/LCD", DASHDOT, xshift=0.12)

# --- 2. TẦNG 2: VI ĐIỀU KHIỂN ESP32 TRUNG TÂM (y = 10.95 -> 13.35) ---
draw_rbox(0.35, 10.95, 8.96, 2.4, bg='#ffffff', border='#000000', lw=2.0)
ax.text(4.83, 10.95 + 2.4 - 0.28, "2. TRẠM HỌC TẬP ESP32 (FreeRTOS Dual-Core C/C++)", ha='center', va='center', fontsize=13.8, fontweight='bold', color='#000000', zorder=3)
ax.plot([0.65, 9.0], [12.7, 12.7], color='#888888', lw=0.9, zorder=3)

esp_subs = [
    ("[L1] dht_flow", "Đọc mẫu DHT22 5s\nKhung 40 bit, checksum 8 bit", 0.55, 2.05),
    ("[L2] light, rfid, focus", "ADC1, ngắt nút & LED\nQuét UID RFID (ID 2,4,6)", 2.75, 2.20),
    ("[L3] timer, lcd_flow", "Bộ đếm ngược Pomodoro\nBuzzer & LCD I2C (ID 3,5)", 5.10, 2.15),
    ("SoftAP Wi-Fi (ID 12)", "Web Server tự xây dựng\nAP IP: 192.168.4.1", 7.40, 1.75)
]
for t, s, x, w in esp_subs:
    draw_rbox(x, 11.1, w, 1.45, bg='#fbfbfb', border='#666666', lw=1.0, rx=0.1)
    ax.text(x + w / 2, 11.1 + 1.05, t, ha='center', va='center', fontsize=11.3, fontweight='bold', color='#000000', zorder=3)
    ax.text(x + w / 2, 11.1 + 0.45, s, ha='center', va='center', fontsize=9.6, color='#333333', linespacing=1.2, zorder=3)

# Mũi tên ESP32 <-> MQTT Broker (y = 10.95 <-> 9.95)
draw_vert_arrow(1.58, 10.95, 9.95, "Pub: study/dht", 'solid', xshift=-0.16, lalign='right')
draw_vert_arrow(3.85, 10.95, 9.95, "Pub: light, rfid, focus", 'dashed', xshift=0.14, lalign='left')
draw_vert_arrow(6.25, 9.95, 10.95, "Sub: timer, lcd", DASHDOT, xshift=0.14, lalign='left')

# --- 3. TẦNG 3: MÁY CHỦ MQTT BROKER (y = 8.45 -> 9.95) ---
draw_rbox(0.35, 8.45, 8.96, 1.5, bg='#f9f9f9', border='#000000', lw=1.8)
ax.text(4.83, 8.45 + 1.5 - 0.28, "3. MQTT BROKER (Mosquitto Port :1883 - TCP Central Bus)", ha='center', va='center', fontsize=13.3, fontweight='bold', color='#000000', zorder=3)
ax.plot([0.65, 9.0], [9.4, 9.4], color='#888888', lw=0.9, zorder=3)

broker_subs = [
    ("[L1] Topic: study/dht", "QoS 0, Vi khí hậu bàn học 5s", 0.55, 2.55),
    ("[L2] study/light, rfid, focus", "QoS 0, Ánh sáng, UID thẻ & bận", 3.25, 3.05),
    ("[L3] Topic: study/timer, lcd", "QoS 1, Lệnh đếm Pomodoro & LCD", 6.45, 2.70)
]
for t, s, x, w in broker_subs:
    draw_rbox(x, 8.57, w, 0.72, bg='#ffffff', border='#666666', lw=0.9, rx=0.1)
    ax.text(x + w / 2, 8.57 + 0.46, t, ha='center', va='center', fontsize=10.8, fontweight='bold', color='#000000', zorder=3)
    ax.text(x + w / 2, 8.57 + 0.18, s, ha='center', va='center', fontsize=9.4, color='#333333', zorder=3)

# Mũi tên MQTT Broker <-> Node-RED (y = 8.45 <-> 7.45)
draw_vert_arrow(1.58, 8.45, 7.45, "Sub: study/dht", 'solid', xshift=-0.16, lalign='right')
draw_vert_arrow(3.85, 8.45, 7.45, "Sub: light, rfid, focus", 'dashed', xshift=0.14, lalign='left')
draw_vert_arrow(6.25, 7.45, 8.45, "Pub: timer, lcd", DASHDOT, xshift=0.14, lalign='left')

# --- 4. TẦNG 4: NODE-RED CORE (LUỒNG XỬ LÝ, REST API & WEBSOCKET) (y = 5.05 -> 7.45) ---
draw_rbox(0.35, 5.05, 8.96, 2.4, bg='#f2f2f2', border='#000000', lw=2.0)
ax.text(4.83, 5.05 + 2.4 - 0.28, "4. NODE-RED CORE (Xử lý luồng sự kiện, REST API & WebSocket)", ha='center', va='center', fontsize=13.5, fontweight='bold', color='#000000', zorder=3)
ax.plot([0.65, 9.0], [6.8, 6.8], color='#888888', lw=0.9, zorder=3)

nr_subs = [
    ("[L1] Vi khí hậu & AI", "Lưu sensor_data 60s (ID 7)\nMô hình tối ưu học tập (ID 13)", 0.55, 2.68),
    ("[L2] Phiên học & Cảnh báo", "Đối soát RFID & LED (ID 2, 6)\nTelegram >60p & Gmail (ID 9, 10)", 3.38, 2.90),
    ("[L3] API Điều khiển & Auth", "REST API & WebSocket (ID 3, 5)\nXác thực bcrypt & Token (ID 11)", 6.43, 2.72)
]
for t, s, x, w in nr_subs:
    draw_rbox(x, 5.2, w, 1.45, bg='#ffffff', border='#666666', lw=1.0, rx=0.1)
    ax.text(x + w / 2, 5.2 + 1.05, t, ha='center', va='center', fontsize=11.6, fontweight='bold', color='#000000', zorder=3)
    ax.text(x + w / 2, 5.2 + 0.45, s, ha='center', va='center', fontsize=9.6, color='#333333', linespacing=1.2, zorder=3)

# Mũi tên Tầng 4 <-> Tầng 5 (y = 5.05 <-> 3.70)
draw_multi_arrows([1.50, 1.85, 2.20], 5.05, 3.70, ['solid', 'dashed', DASHDOT], "SQL & Auth (L1, L2, L3)")
draw_multi_arrows([4.48, 4.83, 5.18], 5.05, 3.70, ['solid', 'dashed', DASHDOT], "REST API / WebSocket")
draw_vert_arrow(7.78, 5.05, 3.70, "API / SMTP", 'dashed', xshift=0.15, lalign='left')

# --- 5. TẦNG 5: DỊCH VỤ ĐÁM MÂY, NGOẠI VI & WEB UI TỰ XÂY (y = 2.05 -> 3.70) ---
ax.text(4.83, 3.48, "5. CƠ SỞ DỮ LIỆU ĐÁM MÂY, DỊCH VỤ NGOẠI VI & WEB UI TỰ XÂY DỰNG", ha='center', va='center', fontsize=12.8, fontweight='bold', color='#111827', zorder=3)

bottom_services = [
    ("Supabase Cloud", "PostgreSQL (ID 7, 11)\nsensor_data, study_sessions, users", 0.35, 2.85),
    ("Web UI tự xây & Người học", "Giao diện Responsive (ID 8, 13)\nGiám sát, Timer, LCD, Auth (ID 1–6, 11)", 3.38, 2.90),
    ("Telegram & Gmail", "Telegram Bot >60p (ID 9)\nGmail SMTP cuối tuần (ID 10)", 6.46, 2.85)
]
for title, sub, x, w in bottom_services:
    draw_rbox(x, 2.05, w, 1.20, bg='#ffffff', border='#000000', lw=1.4)
    ax.text(x + w / 2, 2.05 + 0.82, title, ha='center', va='center', fontsize=11.6, fontweight='bold', color='#000000', zorder=3)
    ax.text(x + w / 2, 2.05 + 0.36, sub, ha='center', va='center', fontsize=9.4, color='#333333', linespacing=1.15, zorder=3)

# Đường kết nối trực tiếp SoftAP Wi-Fi (ID 12) từ ESP32 -> Người học / Điện thoại ở biên phải
ax.plot([9.15, 9.75, 9.75, 4.83, 4.83], [11.82, 11.82, 1.72, 1.72, 2.05], color='#000000', lw=2.0, linestyle=DASHDOT, zorder=3)
ax.annotate('', xy=(4.83, 2.05), xytext=(4.83, 1.76), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.0, mutation_scale=15), zorder=4)
ax.annotate('', xy=(9.15, 11.82), xytext=(9.35, 11.82), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.0, mutation_scale=15), zorder=4)
ax.text(9.75, 6.80, "[L3] Cấu hình Wi-Fi SoftAP 192.168.4.1 (ID 12)", ha='center', va='center', rotation=90,
        fontsize=10.2, fontweight='bold', color='#000000',
        bbox=dict(boxstyle="square,pad=0.18", fc="#ffffff", ec="#888888", lw=0.7), zorder=5)

# --- 6. KHUNG CHÚ GIẢI Ở ĐÁY CÙNG (y = 0.45 -> 1.40) ---
draw_rbox(0.35, 0.45, 9.40, 0.95, bg='#ffffff', border='#000000', lw=1.5)
ax.text(5.05, 1.15, "CHÚ GIẢI CÁC LUỒNG DỮ LIỆU KỸ THUẬT (CHUẨN IN ẤN TRẮNG ĐEN)", ha='center', va='center', fontsize=11.3, fontweight='bold', color='#111827', zorder=3)

# L1: Minh
ax.annotate('', xy=(1.12, 0.72), xytext=(0.52, 0.72),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.4, mutation_scale=15), zorder=4)
ax.text(1.20, 0.72, "[L1] Vi khí hậu & AI (Minh)", ha='left', va='center', fontsize=9.8, fontweight='bold', color='#000000', zorder=3)

# L2: Dương
ax.annotate('', xy=(4.12, 0.72), xytext=(3.52, 0.72),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.4, linestyle='dashed', mutation_scale=15), zorder=4)
ax.text(4.20, 0.72, "[L2] Ánh sáng, RFID, Cảnh báo (Dương)", ha='left', va='center', fontsize=9.8, fontweight='bold', color='#000000', zorder=3)

# L3: Hào
ax.annotate('', xy=(7.62, 0.72), xytext=(7.02, 0.72),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.3, linestyle=DASHDOT, mutation_scale=15), zorder=4)
ax.text(7.70, 0.72, "[L3] Hẹn giờ, LCD, Auth (Hào)", ha='left', va='center', fontsize=9.8, fontweight='bold', color='#000000', zorder=3)

path_vert = os.path.join(out_dir, "so_do_luong_du_lieu_hop_nhat_doc.png")
plt.savefig(path_vert, dpi=300, bbox_inches='tight', pad_inches=0.04)
plt.close()
print("Saved vertical diagram:", path_vert)
