import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

# Set high DPI and font
matplotlib.rcParams['font.family'] = 'Times New Roman'
matplotlib.rcParams['mathtext.fontset'] = 'stix'

fig = plt.figure(figsize=(16.8, 8.0), dpi=300)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 16.8)
ax.set_ylim(0, 8.0)
ax.axis('off')

# Box drawing utility
def draw_rounded_box(x, y, w, h, bg='#ffffff', border='#000000', lw=1.5, rx=0.15):
    box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.01,rounding_size={rx}",
                         facecolor=bg, edgecolor=border, linewidth=lw, zorder=2)
    ax.add_patch(box)
    return box

def draw_header_box(x, y, w, h, title, subtitle="", bg='#ffffff', border='#000000', lw=1.5):
    draw_rounded_box(x, y, w, h, bg=bg, border=border, lw=lw)
    # Title
    ax.text(x + w/2, y + h - 0.28, title, ha='center', va='center', fontsize=13, fontweight='bold', color='#000000', zorder=3)
    if subtitle:
        ax.text(x + w/2, y + h - 0.54, subtitle, ha='center', va='center', fontsize=10, fontstyle='italic', color='#333333', zorder=3)
        # Separator line
        ax.plot([x + 0.12, x + w - 0.12], [y + h - 0.70, y + h - 0.70], color='#aaaaaa', lw=0.8, zorder=3)

# 1. COLUMN 1: PERIPHERAL HARDWARE (x=0.4, w=2.4)
hw_list = [
    ("DHT22 (ID 1)", "GPIO4 (1-Wire)", 6.55, 1.05),
    ("LM393 (ID 4)", "GPIO34 (ADC1)", 5.15, 1.05),
    ("RC522 (ID 2)", "Bus SPI (13.56MHz)", 3.75, 1.05),
    ("Nút & LED (ID 6)", "GPIO27 & GPIO26", 2.35, 1.05),
    ("Còi & LCD (ID 3, 5)", "GPIO25 & Bus I2C", 0.95, 1.05)
]

for title, sub, y, h in hw_list:
    draw_rounded_box(0.4, y, 2.4, h, bg='#f4f4f4', border='#000000', lw=1.5)
    ax.text(0.4 + 1.2, y + 0.66, title, ha='center', va='center', fontsize=12, fontweight='bold', color='#000000', zorder=3)
    ax.text(0.4 + 1.2, y + 0.30, sub, ha='center', va='center', fontsize=10.5, color='#444444', zorder=3)

# 2. COLUMN 2: ESP32 STATION (x=3.8, w=2.8, y=0.85, h=6.75)
draw_header_box(3.8, 0.85, 2.8, 6.75, "TRẠM HỌC TẬP ESP32", "FreeRTOS Dual-Core (C/C++)", bg='#ffffff', border='#000000', lw=2.0)
esp_items = [
    ("[L1] dht_flow", "Đọc mẫu DHT22 & Checksum 40-bit", 6.25),
    ("[L2] light, rfid_flow", "Lọc rung phím, Ngắt GPIO đọc thẻ", 4.85),
    ("[L3] timer, lcd_flow", "Bộ đếm ngược Pomodoro & I2C", 3.45),
    ("SoftAP Wi-Fi Portal (ID 12)", "Web Server cứu hộ IP 192.168.4.1", 1.85)
]
for t, s, cy in esp_items:
    draw_rounded_box(3.95, cy - 0.50, 2.50, 1.0, bg='#fbfbfb', border='#888888', lw=1.0, rx=0.1)
    ax.text(3.95 + 1.25, cy + 0.18, t, ha='center', va='center', fontsize=11.5, fontweight='bold', color='#000000', zorder=3)
    ax.text(3.95 + 1.25, cy - 0.18, s, ha='center', va='center', fontsize=9.5, color='#444444', zorder=3)

# 3. COLUMN 3: MQTT BROKER (x=7.75, w=2.5, y=1.15, h=6.15)
draw_header_box(7.75, 1.15, 2.5, 6.15, "MQTT BROKER", "Mosquitto Port :1883", bg='#f9f9f9', border='#000000', lw=1.6)
broker_items = [
    ("[L1] study/dht", "QoS 0, Vi khí hậu chu kỳ 5s", 6.1),
    ("[L2] study/light, rfid", "QoS 0, Mức sáng ADC & UID", 4.7),
    ("[L3] study/timer, lcd", "QoS 1, Lệnh đếm & Tin nhắn", 3.3),
    ("TCP Central Bus", "Kênh truyền thông nội bộ LAN", 1.85)
]
for t, s, cy in broker_items:
    draw_rounded_box(7.90, cy - 0.50, 2.20, 1.0, bg='#ffffff', border='#888888', lw=1.0, rx=0.1)
    ax.text(7.90 + 1.10, cy + 0.18, t, ha='center', va='center', fontsize=11.5, fontweight='bold', color='#000000', zorder=3)
    ax.text(7.90 + 1.10, cy - 0.18, s, ha='center', va='center', fontsize=9.5, color='#444444', zorder=3)

# 4. COLUMN 4: NODE-RED CORE (x=11.4, w=2.8, y=0.85, h=6.75)
draw_header_box(11.4, 0.85, 2.8, 6.75, "NODE-RED CORE", "Event-Driven Engine Server", bg='#f2f2f2', border='#000000', lw=2.0)
nr_items = [
    ("[L1] Vi khí hậu & AI (ID 13)", "Dashboard Gauges & Mô hình AI", 6.25),
    ("[L2] Bộ đếm phiên (ID 2, 6, 9)", "Đối soát Supabase & Telegram Bot", 4.85),
    ("[L3] Web Server UI (ID 11)", "bcrypt Auth & REST API Điều khiển", 3.45),
    ("Báo cáo tuần SMTP (ID 10)", "Gmail SMTP tự động 20h Chủ nhật", 1.85)
]
for t, s, cy in nr_items:
    draw_rounded_box(11.55, cy - 0.50, 2.50, 1.0, bg='#ffffff', border='#888888', lw=1.0, rx=0.1)
    ax.text(11.55 + 1.25, cy + 0.18, t, ha='center', va='center', fontsize=11, fontweight='bold', color='#000000', zorder=3)
    ax.text(11.55 + 1.25, cy - 0.18, s, ha='center', va='center', fontsize=9.5, color='#444444', zorder=3)

# 5. COLUMN 5: SERVICES & CLOUD (x=14.95, w=1.75)
services = [
    ("Supabase Cloud", "PostgreSQL (ID 7)\nMô hình AI (ID 13)", 5.95, 1.65),
    ("Người học / Web", "Dashboard UI (ID 8)\nXác thực bcrypt (ID 11)", 3.65, 1.65),
    ("Telegram & Gmail", "Telegram Bot (ID 9)\nGmail SMTP (ID 10)", 1.35, 1.65)
]
for title, sub, y, h in services:
    draw_rounded_box(14.95, y, 1.75, h, bg='#ffffff', border='#000000', lw=1.5)
    ax.text(14.95 + 0.875, y + h - 0.38, title, ha='center', va='center', fontsize=11.5, fontweight='bold', color='#000000', zorder=3)
    ax.text(14.95 + 0.875, y + 0.50, sub, ha='center', va='center', fontsize=9.5, color='#444444', linespacing=1.2, zorder=3)

# ARROW & CONNECTOR DRAWING HELPERS
def draw_badge(x, y, text, fontsize=9.2):
    tw = len(text) * 0.082 + 0.20
    th = 0.32
    bx = x - tw/2
    by = y - th/2
    box = FancyBboxPatch((bx, by), tw, th, boxstyle="round,pad=0.01,rounding_size=0.06",
                         facecolor='#ffffff', edgecolor='#333333', linewidth=0.8, zorder=5)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize, fontweight='bold', color='#000000', zorder=6)

# Connecting Arrows:
# Cột 1 -> Cột 2 (distance: 3.8 - 2.8 = 1.0)
# 1. DHT22 -> ESP32 (L1 - solid)
ax.annotate('', xy=(3.8, 7.07), xytext=(2.8, 7.07),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.0, mutation_scale=16), zorder=4)
draw_badge(3.3, 7.07, "GPIO4")

# 2. LM393 -> ESP32 (L2 - dashed)
ax.annotate('', xy=(3.8, 5.67), xytext=(2.8, 5.67),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.0, linestyle='dashed', mutation_scale=16), zorder=4)
draw_badge(3.3, 5.67, "ADC1 (GPIO34)")

# 3. RC522 <-> ESP32 (L2 - dashed)
ax.annotate('', xy=(3.8, 4.27), xytext=(2.8, 4.27),
            arrowprops=dict(arrowstyle="<|-|>", color='#000000', lw=2.0, linestyle='dashed', mutation_scale=16), zorder=4)
draw_badge(3.3, 4.27, "SPI 13.56MHz")

# 4. Nút & LED <-> ESP32 (L2 - dashed)
ax.annotate('', xy=(3.8, 2.87), xytext=(2.8, 2.87),
            arrowprops=dict(arrowstyle="<|-|>", color='#000000', lw=2.0, linestyle='dashed', mutation_scale=16), zorder=4)
draw_badge(3.3, 2.87, "Ngắt & LED")

# 5. Còi & LCD <- ESP32 (L3 - dashdot)
ax.annotate('', xy=(2.8, 1.47), xytext=(3.8, 1.47),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.0, linestyle=(0, (5, 2, 1.5, 2)), mutation_scale=16), zorder=4)
draw_badge(3.3, 1.47, "GPIO25 / I2C")

# Cột 2 <-> Cột 3 (distance: 7.75 - 6.6 = 1.15)
# L1: ESP32 -> Broker (solid)
ax.annotate('', xy=(7.75, 6.1), xytext=(6.6, 6.1),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.0, mutation_scale=16), zorder=4)
draw_badge(7.17, 6.1, "Pub: study/dht")

# L2: ESP32 -> Broker (dashed)
ax.annotate('', xy=(7.75, 4.7), xytext=(6.6, 4.7),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.0, linestyle='dashed', mutation_scale=16), zorder=4)
draw_badge(7.17, 4.7, "Pub: light, rfid")

# L3: ESP32 <- Broker (dashdot)
ax.annotate('', xy=(6.6, 3.3), xytext=(7.75, 3.3),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.0, linestyle=(0, (5, 2, 1.5, 2)), mutation_scale=16), zorder=4)
draw_badge(7.17, 3.3, "Sub: timer, lcd")

# Cột 3 <-> Cột 4 (distance: 11.4 - 10.25 = 1.15)
# L1: Broker -> Node-RED (solid)
ax.annotate('', xy=(11.4, 6.1), xytext=(10.25, 6.1),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.0, mutation_scale=16), zorder=4)
draw_badge(10.82, 6.1, "Sub: study/dht")

# L2: Broker -> Node-RED (dashed)
ax.annotate('', xy=(11.4, 4.7), xytext=(10.25, 4.7),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.0, linestyle='dashed', mutation_scale=16), zorder=4)
draw_badge(10.82, 4.7, "Sub: light, rfid")

# L3: Broker <- Node-RED (dashdot)
ax.annotate('', xy=(10.25, 3.3), xytext=(11.4, 3.3),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.0, linestyle=(0, (5, 2, 1.5, 2)), mutation_scale=16), zorder=4)
draw_badge(10.82, 3.3, "Pub: timer, lcd")

# Cột 4 <-> Cột 5 (distance: 14.95 - 14.2 = 0.75)
# Node-RED <-> Supabase (solid)
ax.annotate('', xy=(14.95, 6.77), xytext=(14.2, 6.77),
            arrowprops=dict(arrowstyle="<|-|>", color='#000000', lw=2.0, mutation_scale=16), zorder=4)
draw_badge(14.57, 6.77, "SQL & AI", fontsize=8.5)

# Node-RED <-> Web User (solid)
ax.annotate('', xy=(14.95, 4.47), xytext=(14.2, 4.47),
            arrowprops=dict(arrowstyle="<|-|>", color='#000000', lw=2.0, mutation_scale=16), zorder=4)
draw_badge(14.57, 4.47, "HTTPS / Web", fontsize=8.2)

# Node-RED -> Telegram & Gmail (dashed)
ax.annotate('', xy=(14.95, 2.17), xytext=(14.2, 2.17),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.0, linestyle='dashed', mutation_scale=16), zorder=4)
draw_badge(14.57, 2.17, "API / SMTP", fontsize=8.2)

# 6. LEGEND AT BOTTOM (x=0.4, y=0.08, w=16.0, h=0.62)
leg_box = FancyBboxPatch((0.4, 0.08), 16.0, 0.62, boxstyle="round,pad=0.01,rounding_size=0.1",
                         facecolor='#ffffff', edgecolor='#000000', linewidth=1.5, zorder=2)
ax.add_patch(leg_box)

ax.text(0.7, 0.39, "Chú giải luồng:", ha='left', va='center', fontsize=12, fontweight='bold', color='#000000', zorder=3)

# L1
ax.plot([2.5, 3.3], [0.39, 0.39], color='#000000', lw=2.4, zorder=3)
ax.annotate('', xy=(3.4, 0.39), xytext=(3.1, 0.39),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.4, mutation_scale=14), zorder=4)
ax.text(3.55, 0.39, "[L1] Nét liền: Vi khí hậu & AI (Minh)", ha='left', va='center', fontsize=11.5, fontweight='bold', color='#000000', zorder=3)

# L2
ax.plot([7.2, 8.0], [0.39, 0.39], color='#000000', lw=2.4, linestyle='dashed', zorder=3)
ax.annotate('', xy=(8.1, 0.39), xytext=(7.8, 0.39),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.4, linestyle='dashed', mutation_scale=14), zorder=4)
ax.text(8.25, 0.39, "[L2] Nét đứt: Ánh sáng, RFID, Alert (Dương)", ha='left', va='center', fontsize=11.5, fontweight='bold', color='#000000', zorder=3)

# L3
ax.plot([12.3, 13.1], [0.39, 0.39], color='#000000', lw=2.4, linestyle=(0, (5, 2, 1.5, 2)), zorder=3)
ax.annotate('', xy=(13.2, 0.39), xytext=(12.9, 0.39),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.4, linestyle=(0, (5, 2, 1.5, 2)), mutation_scale=14), zorder=4)
ax.text(13.35, 0.39, "[L3] Nét chấm gạch: Hẹn giờ, LCD (Hào)", ha='left', va='center', fontsize=11.5, fontweight='bold', color='#000000', zorder=3)

out_dir = r"d:\VLCNTT\Pomodoro-Box\proposal\assets\diagrams"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "so_do_luong_du_lieu_hop_nhat.png")
plt.savefig(out_path, dpi=300, bbox_inches='tight', pad_inches=0.04)
plt.close()
print("Updated high-res diagram successfully at:", out_path)
