import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

matplotlib.rcParams['font.family'] = 'Times New Roman'
matplotlib.rcParams['mathtext.fontset'] = 'stix'

out_dir = r"d:\VLCNTT\Pomodoro-Box\proposal\assets\diagrams"
os.makedirs(out_dir, exist_ok=True)

# Kích thước khung trang in dọc A4: 9.6 x 15.8 inch
fig = plt.figure(figsize=(9.6, 15.8), dpi=300)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 9.6)
ax.set_ylim(0, 15.8)
ax.axis('off')

def draw_rbox(x, y, w, h, bg='#ffffff', border='#000000', lw=1.5, rx=0.15):
    box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.01,rounding_size={rx}",
                         facecolor=bg, edgecolor=border, linewidth=lw, zorder=2)
    ax.add_patch(box)
    return box

def draw_vert_arrow(x, y1, y2, label="", style='solid', is_bidi=False, xshift=0.18, lalign='left'):
    if is_bidi:
        ax.annotate('', xy=(x, y2), xytext=(x, y1),
                    arrowprops=dict(arrowstyle="<|-|>", color='#000000', lw=2.2, linestyle=style, mutation_scale=16), zorder=4)
    else:
        ax.annotate('', xy=(x, y2), xytext=(x, y1),
                    arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.2, linestyle=style, mutation_scale=16), zorder=4)
    if label:
        ym = (y1 + y2) / 2
        ax.text(x + xshift, ym, label, ha=lalign, va='center', fontsize=9.2, fontweight='bold', color='#000000',
                bbox=dict(boxstyle="square,pad=0.14", fc="#ffffff", ec="#888888", lw=0.6), zorder=5)

# --- 1. TẦNG 1: NGOẠI VI & PHẦN CỨNG BÀN HỌC (y = 14.3 -> 15.3) ---
ax.text(4.8, 15.55, "1. LINH KIỆN NGOẠI VI & PHẦN CỨNG BÀN HỌC", ha='center', va='center', fontsize=12.5, fontweight='bold', color='#111827', zorder=3)

hw_nodes = [
    ("DHT22 (ID 1)", "GPIO4 (1-Wire)", 0.35, 1.68),
    ("LM393 (ID 4)", "GPIO34 (ADC1)", 2.17, 1.68),
    ("RC522 (ID 2)", "SPI 13.56MHz", 3.99, 1.68),
    ("Nút & LED (ID 6)", "GPIO27 & 26", 5.81, 1.68),
    ("Còi & LCD (ID 3,5)", "GPIO25 & I2C", 7.63, 1.68)
]
for t, s, x, w in hw_nodes:
    draw_rbox(x, 14.3, w, 0.95, bg='#f4f4f4', border='#000000', lw=1.3)
    ax.text(x + w/2, 14.3 + 0.62, t, ha='center', va='center', fontsize=10, fontweight='bold', color='#000000', zorder=3)
    ax.text(x + w/2, 14.3 + 0.28, s, ha='center', va='center', fontsize=8.6, color='#444444', zorder=3)

# Mũi tên từ Tầng 1 xuống Tầng 2 (y1 = 14.3 -> y2 = 13.35)
draw_vert_arrow(0.35 + 0.84, 14.3, 13.35, "[L1] GPIO4", 'solid', xshift=0.15)
draw_vert_arrow(2.17 + 0.84, 14.3, 13.35, "[L2] ADC1", 'dashed', xshift=0.15)
draw_vert_arrow(3.99 + 0.84, 14.3, 13.35, "[L2] SPI", 'dashed', is_bidi=True, xshift=0.15)
draw_vert_arrow(5.81 + 0.84, 14.3, 13.35, "[L2] Nút/LED", 'dashed', is_bidi=True, xshift=0.15)

# ESP32 -> Còi & LCD: L3 nét chấm gạch
ax.annotate('', xy=(7.63 + 0.84, 14.3), xytext=(7.63 + 0.84, 13.35),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.2, linestyle=(0, (5, 2, 1.5, 2)), mutation_scale=16), zorder=4)
ax.text(7.63 + 0.84 + 0.15, 13.82, "[L3] Còi/LCD", ha='left', va='center', fontsize=9.2, fontweight='bold', color='#000000',
        bbox=dict(boxstyle="square,pad=0.14", fc="#ffffff", ec="#888888", lw=0.6), zorder=5)

# --- 2. TẦNG 2: VI ĐIỀU KHIỂN ESP32 TRUNG TÂM (y = 10.95 -> 13.35) ---
draw_rbox(0.35, 10.95, 8.96, 2.4, bg='#ffffff', border='#000000', lw=2.0)
ax.text(4.8, 10.95 + 2.4 - 0.28, "2. TRẠM HỌC TẬP ESP32 (FreeRTOS Dual-Core C/C++)", ha='center', va='center', fontsize=12.5, fontweight='bold', color='#000000', zorder=3)
ax.plot([0.65, 9.0], [12.7, 12.7], color='#888888', lw=0.9, zorder=3)

esp_subs = [
    ("[L1] dht_flow", "Đọc mẫu DHT22 5s\nChecksum 40-bit", 0.55, 2.05),
    ("[L2] light, rfid_flow", "Lọc rung phím, đọc ADC\nNgắt GPIO quét thẻ RFID", 2.75, 2.15),
    ("[L3] timer, lcd_flow", "Bộ đếm ngược Pomodoro\nGiao tiếp I2C hiển thị LCD", 5.05, 2.15),
    ("SoftAP Wi-Fi (ID 12)", "Web Server cứu hộ Wi-Fi\nIP: 192.168.4.1", 7.35, 1.8)
]
for t, s, x, w in esp_subs:
    draw_rbox(x, 11.1, w, 1.45, bg='#fbfbfb', border='#666666', lw=1.0, rx=0.1)
    ax.text(x + w/2, 11.1 + 1.05, t, ha='center', va='center', fontsize=10.5, fontweight='bold', color='#000000', zorder=3)
    ax.text(x + w/2, 11.1 + 0.45, s, ha='center', va='center', fontsize=8.6, color='#444444', linespacing=1.2, zorder=3)

# Mũi tên từ ESP32 xuống MQTT Broker (y1 = 10.95 -> y2 = 9.95)
draw_vert_arrow(1.6, 10.95, 9.95, "Pub: study/dht", 'solid', xshift=-0.2, lalign='right')
draw_vert_arrow(3.8, 10.95, 9.95, "Pub: light, rfid", 'dashed', xshift=0.18, lalign='left')
ax.annotate('', xy=(6.1, 10.95), xytext=(6.1, 9.95),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.2, linestyle=(0, (5, 2, 1.5, 2)), mutation_scale=16), zorder=4)
ax.text(6.3, 10.45, "Sub: timer, lcd", ha='left', va='center', fontsize=9.2, fontweight='bold', color='#000000',
        bbox=dict(boxstyle="square,pad=0.14", fc="#ffffff", ec="#888888", lw=0.6), zorder=5)

# --- 3. TẦNG 3: MÁY CHỦ MQTT BROKER (y = 8.45 -> 9.95) ---
draw_rbox(0.35, 8.45, 8.96, 1.5, bg='#f9f9f9', border='#000000', lw=1.8)
ax.text(4.8, 8.45 + 1.5 - 0.28, "3. MQTT BROKER (Mosquitto Port :1883 - TCP Central Bus)", ha='center', va='center', fontsize=12, fontweight='bold', color='#000000', zorder=3)
ax.plot([0.65, 9.0], [9.4, 9.4], color='#888888', lw=0.9, zorder=3)

broker_subs = [
    ("[L1] Topic: study/dht", "QoS 0, Vi khí hậu bàn học 5s", 0.6, 2.65),
    ("[L2] Topic: study/light, rfid", "QoS 0, Mức sáng ADC & UID thẻ", 3.45, 2.75),
    ("[L3] Topic: study/timer, lcd", "QoS 1, Lệnh đếm Pomodoro & LCD", 6.38, 2.75)
]
for t, s, x, w in broker_subs:
    draw_rbox(x, 8.57, w, 0.72, bg='#ffffff', border='#666666', lw=0.9, rx=0.1)
    ax.text(x + w/2, 8.57 + 0.46, t, ha='center', va='center', fontsize=9.8, fontweight='bold', color='#000000', zorder=3)
    ax.text(x + w/2, 8.57 + 0.18, s, ha='center', va='center', fontsize=8.2, color='#444444', zorder=3)

# Mũi tên từ MQTT Broker xuống Node-RED (y1 = 8.45 -> y2 = 7.45)
draw_vert_arrow(1.6, 8.45, 7.45, "Sub: study/dht", 'solid', xshift=-0.2, lalign='right')
draw_vert_arrow(3.8, 8.45, 7.45, "Sub: light, rfid", 'dashed', xshift=0.18, lalign='left')
ax.annotate('', xy=(6.1, 8.45), xytext=(6.1, 7.45),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.2, linestyle=(0, (5, 2, 1.5, 2)), mutation_scale=16), zorder=4)
ax.text(6.3, 7.95, "Pub: timer, lcd", ha='left', va='center', fontsize=9.2, fontweight='bold', color='#000000',
        bbox=dict(boxstyle="square,pad=0.14", fc="#ffffff", ec="#888888", lw=0.6), zorder=5)

# --- 4. TẦNG 4: NODE-RED CORE PROCESSING ENGINE (y = 5.05 -> 7.45) ---
draw_rbox(0.35, 5.05, 8.96, 2.4, bg='#f2f2f2', border='#000000', lw=2.0)
ax.text(4.8, 5.05 + 2.4 - 0.28, "4. NODE-RED CORE (Event-Driven Processing Engine & UI Server)", ha='center', va='center', fontsize=12.5, fontweight='bold', color='#000000', zorder=3)
ax.plot([0.65, 9.0], [6.8, 6.8], color='#888888', lw=0.9, zorder=3)

nr_subs = [
    ("[L1] Vi khí hậu & AI", "Dashboard Gauges & Chart\nMô hình AI tối ưu (ID 13)", 0.6, 2.65),
    ("[L2] Bộ đếm phiên", "Đối soát Supabase & Lịch sử\nTelegram Bot báo ngồi lâu (ID 9)", 3.45, 2.75),
    ("[L3] Web UI & Bảo mật", "bcrypt Auth & Session Token\nREST API điều khiển trạm (ID 11)", 6.38, 2.75)
]
for t, s, x, w in nr_subs:
    draw_rbox(x, 5.2, w, 1.45, bg='#ffffff', border='#666666', lw=1.0, rx=0.1)
    ax.text(x + w/2, 5.2 + 1.05, t, ha='center', va='center', fontsize=11, fontweight='bold', color='#000000', zorder=3)
    ax.text(x + w/2, 5.2 + 0.45, s, ha='center', va='center', fontsize=8.8, color='#444444', linespacing=1.2, zorder=3)

# Mũi tên từ Node-RED xuống Dịch vụ Đám mây (y1 = 5.05 -> y2 = 3.65)
# Rộng rãi, không có bất kỳ chữ nào đè lên!
draw_vert_arrow(1.9, 5.05, 3.65, "SQL & AI", 'solid', is_bidi=True, xshift=-0.18, lalign='right')
draw_vert_arrow(4.8, 5.05, 3.65, "HTTPS / Web", 'solid', is_bidi=True, xshift=0.18, lalign='left')
draw_vert_arrow(7.7, 5.05, 3.65, "API / SMTP", 'dashed', xshift=0.18, lalign='left')

# --- 5. TẦNG 5: DỊCH VỤ ĐÁM MÂY, NGOẠI VI & NGƯỜI DÙNG (y = 2.05 -> 3.65) ---
# Tiêu đề tầng 5 nằm TRONG hoặc SÁT MÉT TRÊN KHỐI TẦNG 5
ax.text(4.8, 3.45, "5. CƠ SỞ DỮ LIỆU ĐÁM MÂY, DỊCH VỤ NGOẠI VI & NGƯỜI DÙNG", ha='center', va='center', fontsize=12, fontweight='bold', color='#111827', zorder=3)

bottom_services = [
    ("Supabase Cloud", "PostgreSQL (ID 7)\nMô hình AI (ID 13)", 0.5, 2.65),
    ("Người học / Web", "Dashboard UI (ID 8)\nXác thực bcrypt (ID 11)", 3.45, 2.75),
    ("Telegram & Gmail", "Telegram Bot (ID 9)\nGmail SMTP (ID 10)", 6.38, 2.75)
]
for title, sub, x, w in bottom_services:
    draw_rbox(x, 2.05, w, 1.15, bg='#ffffff', border='#000000', lw=1.4)
    ax.text(x + w/2, 2.05 + 0.78, title, ha='center', va='center', fontsize=11, fontweight='bold', color='#000000', zorder=3)
    ax.text(x + w/2, 2.05 + 0.35, sub, ha='center', va='center', fontsize=8.8, color='#444444', linespacing=1.1, zorder=3)

# --- 6. KHUNG CHÚ GIẢI Ở ĐÁY CÙNG (y = 0.55 -> 1.45) ---
draw_rbox(0.35, 0.55, 8.96, 0.9, bg='#ffffff', border='#000000', lw=1.5)
ax.text(4.8, 1.18, "CHÚ GIẢI CÁC LUỒNG DỮ LIỆU KỸ THUẬT (CHUẨN IN ẤN TRẮNG ĐEN)", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#111827', zorder=3)

# L1: Minh
ax.annotate('', xy=(1.35, 0.8), xytext=(0.55, 0.8),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.4, mutation_scale=14), zorder=4)
ax.text(1.48, 0.8, "[L1] Vi khí hậu & AI (Minh)", ha='left', va='center', fontsize=9.0, fontweight='bold', color='#000000', zorder=3)

# L2: Dương
ax.annotate('', xy=(4.5, 0.8), xytext=(3.7, 0.8),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.4, linestyle='dashed', mutation_scale=14), zorder=4)
ax.text(4.63, 0.8, "[L2] Ánh sáng, RFID, Alert (Dương)", ha='left', va='center', fontsize=9.0, fontweight='bold', color='#000000', zorder=3)

# L3: Hào
ax.annotate('', xy=(7.45, 0.8), xytext=(6.65, 0.8),
            arrowprops=dict(arrowstyle="-|>", color='#000000', lw=2.2, linestyle=(0, (5, 2, 1.5, 2)), mutation_scale=14), zorder=4)
ax.text(7.58, 0.8, "[L3] Hẹn giờ, LCD (Hào)", ha='left', va='center', fontsize=9.0, fontweight='bold', color='#000000', zorder=3)

path_vert = os.path.join(out_dir, "so_do_luong_du_lieu_hop_nhat_doc.png")
plt.savefig(path_vert, dpi=300, bbox_inches='tight', pad_inches=0.04)
plt.close()
print("Sơ đồ dọc hoàn thiện 100% không đè chữ tại:", path_vert)
