"""
Capture all 6 views of the 3D Pomodoro-Box directly from Autodesk Fusion 360
and overlay matching Vietnamese callouts, ID badges, leader lines, and dimension annotations.

Saves output to:
- D:/Pomodoro/Pomodoro-Box/proposal/assets/design_fusion360/
- D:/Pomodoro/Pomodoro-Box/docs/design_fusion360/
"""

import json
import os
import shutil
import urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BRIDGE_URL = "http://127.0.0.1:18080"
OUT_DIR_PROPOSAL = r"D:\Pomodoro\Pomodoro-Box\proposal\assets\design_fusion360"
OUT_DIR_DOCS = r"D:\Pomodoro\Pomodoro-Box\docs\design_fusion360"
RAW_DIR = r"C:\Users\Admin\.gemini\antigravity\brain\ad1ce98c-dc99-4061-8c0c-1872cfcd08c2\scratch\raw_fusion"

os.makedirs(OUT_DIR_PROPOSAL, exist_ok=True)
os.makedirs(OUT_DIR_DOCS, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

# Fonts (Windows system fonts with full Vietnamese Unicode support)
FONT_REG = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"


def get_font(bold=False, size=24):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def fusion_exec(code, timeout=30.0):
    payload = json.dumps({"code": code, "fitView": False, "timeout": timeout}).encode("utf-8")
    req = urllib.request.Request(
        f"{BRIDGE_URL}/exec",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout + 5.0) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fusion_screenshot(filepath, width, height, fit_view=False):
    payload = json.dumps({
        "path": filepath,
        "width": int(width),
        "height": int(height),
        "fitView": bool(fit_view),
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{BRIDGE_URL}/screenshot",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20.0) as resp:
        return json.loads(resp.read().decode("utf-8"))


def capture_scene_with_points(scene_name, setup_code, points_dict, cleanup_code=""):
    """
    Runs setup_code in Fusion 360, queries 2D projected coordinates for points_dict,
    saves a 2x resolution screenshot, and runs cleanup_code.
    """
    pts_json = json.dumps(points_dict)
    query_code = f"""
doc.activate()
{setup_code}
vp = app.activeViewport
vp.refresh()
adsk.doEvents()

pts_in = {pts_json}
pts_out = {{}}
for k, coords in pts_in.items():
    p2d = vp.modelToViewSpace(pt(coords[0], coords[1], coords[2]))
    pts_out[k] = [p2d.x, p2d.y]

result = {{
    'vp_w': vp.width,
    'vp_h': vp.height,
    'pts': pts_out
}}
"""
    res = fusion_exec(query_code)
    if not res.get("ok"):
        raise RuntimeError(f"Fusion exec failed for {scene_name}: {res}")

    info = res["result"]
    vp_w = info["vp_w"]
    vp_h = info["vp_h"]
    raw_path = os.path.join(RAW_DIR, f"{scene_name}_raw.png")
    img_w = vp_w * 2
    img_h = vp_h * 2
    fusion_screenshot(raw_path, img_w, img_h, fit_view=False)

    if cleanup_code.strip():
        fusion_exec(cleanup_code)

    # Compute DPI ratio between modelToViewSpace physical pixels and 2x image pixels
    # On 125% Windows scaling, vp_w * 1.25 is physical width, so 2x image has factor 2.0 / 1.25 = 1.6
    scale_factor = 1.6
    scaled_pts = {}
    for k, (px, py) in info["pts"].items():
        scaled_pts[k] = (px * scale_factor, py * scale_factor)

    return raw_path, (img_w, img_h), scaled_pts


def clean_background_and_pad(raw_path, pts_dict, out_w=2200, out_h=1100, scale_render=1.08):
    """
    Places the raw Fusion 360 render onto a clean white canvas (out_w x out_h)
    with soft vignette fading of outer grid lines so callouts sit on pure white.
    Returns (PIL.Image, transformed_pts_dict).
    """
    im = Image.open(raw_path).convert("RGBA")
    rw, rh = im.size

    if abs(scale_render - 1.0) > 1e-3:
        new_rw = int(rw * scale_render)
        new_rh = int(rh * scale_render)
        im = im.resize((new_rw, new_rh), Image.Resampling.LANCZOS)
    else:
        new_rw, new_rh = rw, rh

    # Create elliptical alpha mask to softly fade the outer grid lines into pure white
    arr = np.array(im)
    r, g, b = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
    # Identify background/grid pixels (neutral light gray/white or faint red/green axis lines far from center)
    yy, xx = np.mgrid[0:new_rh, 0:new_rw]
    cx, cy = new_rw * 0.5, new_rh * 0.5
    norm_dist = np.sqrt(((xx - cx) / (new_rw * 0.34)) ** 2 + ((yy - cy) / (new_rh * 0.46)) ** 2)

    is_neutral_light = (r > 195) & (g > 195) & (b > 195) & (np.abs(r - g) < 12) & (np.abs(g - b) < 12)
    is_outer_axis = (norm_dist > 0.72) & ((r > 180) | (g > 180)) & (b > 150)
    bg_mask = is_neutral_light | is_outer_axis

    # Only fade background pixels strictly in the outer margin (norm_dist > 0.72) so the 3D model is 100% untouched
    fade = np.clip((norm_dist - 0.72) / 0.25, 0.0, 1.0)
    blend = np.where(bg_mask, fade, 0.0)[:, :, None]
    cleaned_rgb = (arr[:, :, :3].astype(float) * (1.0 - blend) + 255.0 * blend).astype(np.uint8)
    im_clean = Image.fromarray(cleaned_rgb, mode="RGB")

    canvas = Image.new("RGB", (out_w, out_h), (255, 255, 255))
    off_x = (out_w - new_rw) // 2
    off_y = (out_h - new_rh) // 2
    canvas.paste(im_clean, (off_x, off_y))

    new_pts = {}
    for k, (px, py) in pts_dict.items():
        new_pts[k] = (px * scale_render + off_x, py * scale_render + off_y)

    return canvas, new_pts


def draw_callouts(canvas, callouts):
    """
    Draws anti-aliased leader lines, target dots, and rounded callout boxes with optional ID badges.
    Each item in callouts:
      {
        "side": "left" | "right",
        "box_y": int,
        "box_x": int (optional),
        "id_text": "ID 6" or None,
        "label": "LCD 1602 (lời nhắc)",
        "color": "#6d4c41",
        "target": (tx, ty)
      }
    """
    # Render at 2x supersampling for crisp anti-aliased lines and rounded rectangles
    w, h = canvas.size
    overlay = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    drw = ImageDraw.Draw(overlay)

    f_id = get_font(bold=True, size=23 * 2)
    f_lbl = get_font(bold=False, size=25 * 2)

    for c in callouts:
        col_rgb = hex_to_rgb(c["color"])
        tx, ty = c["target"][0] * 2, c["target"][1] * 2
        side = c["side"]
        cy = c["box_y"] * 2
        id_text = c.get("id_text")
        label = c["label"]

        # Measure text
        lbl_bbox = drw.textbbox((0, 0), label, font=f_lbl)
        lbl_w = lbl_bbox[2] - lbl_bbox[0]
        box_h = 48 * 2
        pad_x = 16 * 2

        if id_text:
            id_bbox = drw.textbbox((0, 0), id_text, font=f_id)
            id_w = (id_bbox[2] - id_bbox[0]) + 24 * 2
            box_w = pad_x + id_w + 14 * 2 + lbl_w + pad_x
        else:
            id_w = 0
            box_w = pad_x + lbl_w + pad_x

        if side == "left":
            x1 = c.get("box_x", 36) * 2
            x2 = x1 + box_w
            line_start_x = x2
        else:
            x2 = (c.get("box_x", w - 36)) * 2
            x1 = x2 - box_w
            line_start_x = x1

        y1 = cy - box_h // 2
        y2 = cy + box_h // 2

        # Leader line (horizontal elbow or direct line like in original renders)
        # In original renders, leader line goes horizontally from box edge or with a clean segment to target
        drw.line([(line_start_x, cy), (tx, ty)], fill=col_rgb + (255,), width=4)

        # Target dot (white fill with colored ring)
        r_dot = 7 * 2
        drw.ellipse([tx - r_dot, ty - r_dot, tx + r_dot, ty + r_dot], fill=(255, 255, 255, 255), outline=col_rgb + (255,), width=5)

        # Callout outer rounded box
        drw.rounded_rectangle([x1, y1, x2, y2], radius=10 * 2, fill=(255, 255, 255, 250), outline=col_rgb + (255,), width=4)

        # ID badge if present
        if id_text:
            bx1 = x1 + 8 * 2
            by1 = y1 + 7 * 2
            bx2 = bx1 + id_w
            by2 = y2 - 7 * 2
            drw.rounded_rectangle([bx1, by1, bx2, by2], radius=7 * 2, fill=col_rgb + (255,))
            id_tb = drw.textbbox((0, 0), id_text, font=f_id)
            id_tx = bx1 + (id_w - (id_tb[2] - id_tb[0])) // 2
            id_ty = by1 + ((by2 - by1) - (id_tb[3] - id_tb[1])) // 2 - id_tb[1]
            drw.text((id_tx, id_ty), id_text, font=f_id, fill=(255, 255, 255, 255))
            tx_lbl = bx2 + 14 * 2
        else:
            tx_lbl = x1 + pad_x

        lbl_tb = drw.textbbox((0, 0), label, font=f_lbl)
        ty_lbl = y1 + (box_h - (lbl_tb[3] - lbl_tb[1])) // 2 - lbl_tb[1]
        drw.text((tx_lbl, ty_lbl), label, font=f_lbl, fill=(30, 30, 30, 255))

    overlay_small = overlay.resize((w, h), Image.Resampling.LANCZOS)
    out = canvas.convert("RGBA")
    out.alpha_composite(overlay_small)
    return out.convert("RGB")


def save_both(img, filename):
    p1 = os.path.join(OUT_DIR_PROPOSAL, filename)
    p2 = os.path.join(OUT_DIR_DOCS, filename)
    img.save(p1, "PNG", optimize=True)
    shutil.copy2(p1, p2)
    print(f"Saved: {p1}")


def build_all_6_images():
    # ==========================================================================
    # IMAGE 1: hinh_3d_1_ben_ngoai_truoc.png
    # ==========================================================================
    setup_1 = """
for i in range(root.bRepBodies.count):
    b = root.bRepBodies.item(i)
    b.isVisible = True
    b.opacity = 1.0
vp = app.activeViewport
cam = vp.camera
cam.target = pt(75.0, 50.0, 24.0)
cam.eye = pt(195.0, -140.0, 150.0)
cam.upVector = vec(0, 0, 1)
cam.isSmoothTransition = False
vp.camera = cam
vp.fit()
"""
    pts_1 = {
        "lcd": [52.0, 68.0, 47.1],
        "rfid": [34.0, 27.0, 50.15],
        "led": [110.0, 76.0, 54.5],
        "btn": [133.0, 76.0, 54.0],
        "buzzer": [122.0, 48.0, 50.0],
        "vent_right": [150.0, 72.0, 35.5],
        "ldr": [134.0, 18.0, 50.0],
    }
    raw_1, _, p2d_1 = capture_scene_with_points("view1_front", setup_1, pts_1)
    canvas_1, tp_1 = clean_background_and_pad(raw_1, p2d_1, out_w=2200, out_h=1060, scale_render=1.12)
    callouts_1 = [
        {"side": "left", "box_y": 250, "id_text": "ID 6", "label": "LCD 1602 (lời nhắc)", "color": "#6d4c41", "target": tp_1["lcd"]},
        {"side": "left", "box_y": 330, "id_text": "ID 5", "label": "Vùng quẹt thẻ (RC522)", "color": "#43a047", "target": tp_1["rfid"]},
        {"side": "right", "box_y": 220, "id_text": "ID 4", "label": 'LED đỏ "đang tập trung"', "color": "#8e24aa", "target": tp_1["led"]},
        {"side": "right", "box_y": 310, "id_text": "ID 4", "label": "Nút nhấn", "color": "#8e24aa", "target": tp_1["btn"]},
        {"side": "right", "box_y": 410, "id_text": "ID 3", "label": "Lỗ thoát âm buzzer", "color": "#1e88e5", "target": tp_1["buzzer"]},
        {"side": "right", "box_y": 510, "id_text": None, "label": "Khe thoát nhiệt", "color": "#546e7a", "target": tp_1["vent_right"]},
        {"side": "right", "box_y": 605, "id_text": "ID 2", "label": "Quang trở (lỗ lấy sáng)", "color": "#fb8c00", "target": tp_1["ldr"]},
    ]
    img_1 = draw_callouts(canvas_1, callouts_1)
    save_both(img_1, "hinh_3d_1_ben_ngoai_truoc.png")

    # ==========================================================================
    # IMAGE 2: hinh_3d_2_ben_ngoai_sau.png
    # ==========================================================================
    setup_2 = """
for i in range(root.bRepBodies.count):
    b = root.bRepBodies.item(i)
    b.isVisible = True
    b.opacity = 1.0
vp = app.activeViewport
cam = vp.camera
cam.target = pt(75.0, 50.0, 24.0)
cam.eye = pt(-95.0, 235.0, 150.0)
cam.upVector = vec(0, 0, 1)
cam.isSmoothTransition = False
vp.camera = cam
vp.fit()
"""
    pts_2 = {
        "usb": [126.0, 100.0, 22.0],
        "lcd": [52.0, 68.0, 47.1],
        "screw": [7.0, 93.0, 50.0],
        "vent_dht": [0.0, 67.0, 18.0],
        "dc_jack": [30.0, 101.2, 16.0],
    }
    raw_2, _, p2d_2 = capture_scene_with_points("view2_back", setup_2, pts_2)
    canvas_2, tp_2 = clean_background_and_pad(raw_2, p2d_2, out_w=2200, out_h=1060, scale_render=1.12)
    callouts_2 = [
        {"side": "left", "box_y": 420, "id_text": None, "label": "Cổng USB nạp code", "color": "#546e7a", "target": tp_2["usb"]},
        {"side": "right", "box_y": 320, "id_text": "ID 6", "label": "LCD 1602", "color": "#6d4c41", "target": tp_2["lcd"]},
        {"side": "right", "box_y": 430, "id_text": None, "label": "Vít M3 giữ nắp (4 góc)", "color": "#546e7a", "target": tp_2["screw"]},
        {"side": "right", "box_y": 565, "id_text": "ID 1", "label": "Khe hút gió cho DHT22", "color": "#e53935", "target": tp_2["vent_dht"]},
        {"side": "right", "box_y": 665, "id_text": None, "label": "Jack DC 5V", "color": "#546e7a", "target": tp_2["dc_jack"]},
    ]
    img_2 = draw_callouts(canvas_2, callouts_2)
    save_both(img_2, "hinh_3d_2_ben_ngoai_sau.png")

    # ==========================================================================
    # IMAGE 3: hinh_3d_3_ben_trong_than_hop.png
    # ==========================================================================
    setup_3 = """
lid_prefixes = ('02_Nap_Hop', 'Bieu_Tuong', 'LCD1602', 'RFID_', 'Buzzer_', 'Quang_Tro', 'Nut_Nhan', 'LED_', 'Vien_Giu')
for i in range(root.bRepBodies.count):
    b = root.bRepBodies.item(i)
    b.opacity = 1.0
    b.isVisible = not any(b.name.startswith(p) for p in lid_prefixes)
vp = app.activeViewport
cam = vp.camera
cam.target = pt(75.0, 52.0, 18.0)
cam.eye = pt(135.0, -105.0, 175.0)
cam.upVector = vec(0, 0, 1)
cam.isSmoothTransition = False
vp.camera = cam
vp.fit()
"""
    pts_3 = {
        "dc_jack": [30.0, 91.0, 16.0],
        "dht22": [6.5, 67.0, 22.0],
        "usb": [126.0, 96.0, 21.5],
        "esp32": [126.0, 65.0, 22.3],
        "perfboard": [90.0, 65.0, 9.1],
    }
    raw_3, _, p2d_3 = capture_scene_with_points("view3_inside_bottom", setup_3, pts_3)
    canvas_3, tp_3 = clean_background_and_pad(raw_3, p2d_3, out_w=2200, out_h=1060, scale_render=1.12)
    callouts_3 = [
        {"side": "left", "box_y": 235, "id_text": None, "label": "Jack nguồn DC 5V", "color": "#546e7a", "target": tp_3["dc_jack"]},
        {"side": "left", "box_y": 325, "id_text": "ID 1", "label": "DHT22 sát khe hút gió", "color": "#e53935", "target": tp_3["dht22"]},
        {"side": "right", "box_y": 395, "id_text": None, "label": "Cổng USB (thẳng lỗ mặt sau)", "color": "#546e7a", "target": tp_3["usb"]},
        {"side": "right", "box_y": 495, "id_text": None, "label": "ESP32 DevKit V1", "color": "#546e7a", "target": tp_3["esp32"]},
        {"side": "right", "box_y": 590, "id_text": None, "label": "Board đục lỗ (hàn mạch)", "color": "#546e7a", "target": tp_3["perfboard"]},
    ]
    img_3 = draw_callouts(canvas_3, callouts_3)
    save_both(img_3, "hinh_3d_3_ben_trong_than_hop.png")

    # ==========================================================================
    # IMAGE 4: hinh_3d_4_ben_trong_mat_duoi_nap.png
    # ==========================================================================
    setup_4 = """
bot_prefixes = ('01_Than_Hop', 'Chan_Cao_Su', 'Cot_Dong', 'Board_Duc_Lo', 'ESP32_', 'DHT22_', 'Jack_DC', 'Bieu_Tuong')
for i in range(root.bRepBodies.count):
    b = root.bRepBodies.item(i)
    b.opacity = 1.0
    b.isVisible = not any(b.name.startswith(p) for p in bot_prefixes)
vp = app.activeViewport
cam = vp.camera
cam.target = pt(75.0, 50.0, 44.0)
cam.eye = pt(125.0, 195.0, -85.0)
cam.upVector = vec(0, 0, -1)
cam.isSmoothTransition = False
vp.camera = cam
vp.fit()
"""
    pts_4 = {
        "rc522": [52.0, 26.0, 44.4],
        "lcd_i2c": [40.0, 68.0, 35.0],
        "ldr": [120.0, 18.0, 39.0],
        "buzzer": [111.0, 48.0, 36.0],
        "led": [110.0, 76.0, 42.5],
        "btn": [133.0, 76.0, 35.0],
    }
    raw_4, _, p2d_4 = capture_scene_with_points("view4_under_lid", setup_4, pts_4)
    canvas_4, tp_4 = clean_background_and_pad(raw_4, p2d_4, out_w=2200, out_h=1060, scale_render=1.12)
    callouts_4 = [
        {"side": "left", "box_y": 230, "id_text": "ID 5", "label": "Đầu đọc RFID RC522", "color": "#43a047", "target": tp_4["rc522"]},
        {"side": "left", "box_y": 510, "id_text": "ID 6", "label": "LCD 1602 + module I2C", "color": "#6d4c41", "target": tp_4["lcd_i2c"]},
        {"side": "right", "box_y": 355, "id_text": "ID 2", "label": "Module quang trở LM393", "color": "#fb8c00", "target": tp_4["ldr"]},
        {"side": "right", "box_y": 450, "id_text": "ID 3", "label": "Buzzer chủ động", "color": "#1e88e5", "target": tp_4["buzzer"]},
        {"side": "right", "box_y": 695, "id_text": "ID 4", "label": "LED đỏ 5 mm + đế giữ", "color": "#8e24aa", "target": tp_4["led"]},
        {"side": "right", "box_y": 780, "id_text": "ID 4", "label": "Nút nhấn (thân ren + đai ốc)", "color": "#8e24aa", "target": tp_4["btn"]},
    ]
    img_4 = draw_callouts(canvas_4, callouts_4)
    save_both(img_4, "hinh_3d_4_ben_trong_mat_duoi_nap.png")

    # ==========================================================================
    # IMAGE 5: hinh_3d_5_tach_nap.png (Exploded View with translucent shell & lid)
    # ==========================================================================
    dz_explode = 52.0
    setup_5 = f"""
lid_prefixes = ('02_Nap_Hop', 'Bieu_Tuong', 'LCD1602', 'RFID_', 'Buzzer_', 'Quang_Tro', 'Nut_Nhan', 'LED_', 'Vien_Giu')
move_objs = adsk.core.ObjectCollection.create()
for i in range(root.bRepBodies.count):
    b = root.bRepBodies.item(i)
    b.isVisible = True
    if b.name == '02_Nap_Hop_TopCover':
        b.opacity = 0.30
    elif b.name == '01_Than_Hop_BottomCase':
        b.opacity = 0.42
    else:
        b.opacity = 1.0
    if any(b.name.startswith(p) for p in lid_prefixes):
        move_objs.add(b)

transform = adsk.core.Matrix3D.create()
transform.translation = vec(0, 0, mm({dz_explode}))
mv_in = root.features.moveFeatures.createInput2(move_objs)
mv_in.defineAsFreeMove(transform)
mv_feat = root.features.moveFeatures.add(mv_in)
mv_feat.name = 'Temp_Explode_Move'

vp = app.activeViewport
cam = vp.camera
cam.target = pt(75.0, 50.0, 48.0)
cam.eye = pt(205.0, -165.0, 160.0)
cam.upVector = vec(0, 0, 1)
cam.isSmoothTransition = False
vp.camera = cam
vp.fit()
"""
    cleanup_5 = """
for i in range(root.features.moveFeatures.count - 1, -1, -1):
    mf = root.features.moveFeatures.item(i)
    if mf.name == 'Temp_Explode_Move':
        mf.deleteMe()
for i in range(root.bRepBodies.count):
    b = root.bRepBodies.item(i)
    b.isVisible = True
    b.opacity = 1.0
"""
    pts_5 = {
        "lcd": [52.0, 68.0, 46.8 + dz_explode],
        "rc522": [52.0, 26.0, 45.2 + dz_explode],
        "led": [110.0, 76.0, 54.5 + dz_explode],
        "btn": [133.0, 76.0, 54.0 + dz_explode],
        "buzzer": [122.0, 48.0, 42.0 + dz_explode],
        "ldr": [120.0, 18.0, 39.8 + dz_explode],
        "dht22": [6.5, 67.0, 20.0],
        "dc_jack": [30.0, 91.0, 16.0],
        "usb": [126.0, 96.0, 21.5],
        "esp32": [126.0, 65.0, 22.3],
    }
    raw_5, _, p2d_5 = capture_scene_with_points("view5_exploded", setup_5, pts_5, cleanup_code=cleanup_5)
    canvas_5, tp_5 = clean_background_and_pad(raw_5, p2d_5, out_w=2200, out_h=1120, scale_render=1.12)
    callouts_5 = [
        {"side": "left", "box_y": 175, "id_text": "ID 6", "label": "LCD 1602 + module I2C", "color": "#6d4c41", "target": tp_5["lcd"]},
        {"side": "left", "box_y": 255, "id_text": "ID 5", "label": "Đầu đọc RFID RC522", "color": "#43a047", "target": tp_5["rc522"]},
        {"side": "left", "box_y": 565, "id_text": "ID 1", "label": "DHT22 sát khe hút gió", "color": "#e53935", "target": tp_5["dht22"]},
        {"side": "left", "box_y": 645, "id_text": None, "label": "Jack nguồn DC 5V", "color": "#546e7a", "target": tp_5["dc_jack"]},
        {"side": "right", "box_y": 135, "id_text": "ID 4", "label": 'LED đỏ "đang tập trung"', "color": "#8e24aa", "target": tp_5["led"]},
        {"side": "right", "box_y": 210, "id_text": "ID 4", "label": "Nút nhấn", "color": "#8e24aa", "target": tp_5["btn"]},
        {"side": "right", "box_y": 300, "id_text": "ID 3", "label": "Buzzer chủ động", "color": "#1e88e5", "target": tp_5["buzzer"]},
        {"side": "right", "box_y": 380, "id_text": "ID 2", "label": "Module quang trở LM393", "color": "#fb8c00", "target": tp_5["ldr"]},
        {"side": "right", "box_y": 640, "id_text": None, "label": "Cổng USB (thẳng lỗ mặt sau)", "color": "#546e7a", "target": tp_5["usb"]},
        {"side": "right", "box_y": 725, "id_text": None, "label": "ESP32 DevKit V1", "color": "#546e7a", "target": tp_5["esp32"]},
    ]
    img_5 = draw_callouts(canvas_5, callouts_5)
    save_both(img_5, "hinh_3d_5_tach_nap.png")

    # ==========================================================================
    # IMAGE 6: hinh_3d_6_ban_ve_kich_thuoc.png
    # Orthographic views captured from Fusion 360 + full 2D engineering dimensions
    # ==========================================================================
    build_dimension_sheet()

    # Restore nice front-right isometric view in Fusion 360
    fusion_exec("""
vp = app.activeViewport
cam = vp.camera
cam.target = pt(75.0, 50.0, 24.0)
cam.eye = pt(195.0, -140.0, 150.0)
cam.upVector = vec(0, 0, 1)
cam.isSmoothTransition = False
vp.camera = cam
vp.fit()
vp.refresh()
""")


def crop_by_2d_corners(raw_path, p_min, p_max):
    """Crops the exact 2D bounding box projected by Fusion 360 modelToViewSpace."""
    im = Image.open(raw_path).convert("RGB")
    x1 = int(min(p_min[0], p_max[0]))
    y1 = int(min(p_min[1], p_max[1]))
    x2 = int(max(p_min[0], p_max[0]))
    y2 = int(max(p_min[1], p_max[1]))
    return im.crop((x1, y1, x2, y2))


def build_dimension_sheet():
    # Capture 4 orthographic views directly from Fusion 360 using exact corner projections:
    # a) Top view (only lid)
    raw_top, _, p_top = capture_scene_with_points(
        "ortho_top",
        """
for i in range(root.bRepBodies.count):
    b = root.bRepBodies.item(i)
    b.opacity = 1.0
    b.isVisible = (b.name in ('02_Nap_Hop_TopCover', 'Bieu_Tuong_The_RFID'))
vp = app.activeViewport
cam = vp.camera
cam.target = pt(75.0, 50.0, 50.0)
cam.eye = pt(75.0, 50.0, 300.0)
cam.upVector = vec(0, 1, 0)
cam.isSmoothTransition = False
vp.camera = cam
vp.fit()
""",
        {"p1": [0.0, 0.0, 50.0], "p2": [150.0, 100.0, 50.0]},
    )

    # b) Top X-Ray view (inside components with semi-transparent lid)
    raw_xray, _, p_xray = capture_scene_with_points(
        "ortho_xray",
        """
for i in range(root.bRepBodies.count):
    b = root.bRepBodies.item(i)
    b.isVisible = True
    b.opacity = 0.18 if b.name == '02_Nap_Hop_TopCover' else 1.0
vp = app.activeViewport
cam = vp.camera
cam.target = pt(75.0, 50.0, 25.0)
cam.eye = pt(75.0, 50.0, 300.0)
cam.upVector = vec(0, 1, 0)
cam.isSmoothTransition = False
vp.camera = cam
vp.fit()
""",
        {"p1": [0.0, 0.0, 50.0], "p2": [150.0, 100.0, 50.0]},
    )

    # c) Rear orthographic view (looking at back wall, flipped horizontally to match "nhìn từ phía trước xuyên qua hộp")
    raw_back, _, p_back = capture_scene_with_points(
        "ortho_back",
        """
for i in range(root.bRepBodies.count):
    b = root.bRepBodies.item(i)
    b.isVisible = (b.name in ('01_Than_Hop_BottomCase', '02_Nap_Hop_TopCover'))
    b.opacity = 1.0
vp = app.activeViewport
cam = vp.camera
cam.target = pt(75.0, 100.0, 25.0)
cam.eye = pt(75.0, 320.0, 25.0)
cam.upVector = vec(0, 0, 1)
cam.isSmoothTransition = False
vp.camera = cam
vp.fit()
""",
        {"p1": [0.0, 100.0, 0.0], "p2": [150.0, 100.0, 50.0]},
    )

    # d1) Left side orthographic view (5 DHT22 intake slots)
    raw_left, _, p_left = capture_scene_with_points(
        "ortho_left",
        """
vp = app.activeViewport
cam = vp.camera
cam.target = pt(0.0, 50.0, 25.0)
cam.eye = pt(-220.0, 50.0, 25.0)
cam.upVector = vec(0, 0, 1)
cam.isSmoothTransition = False
vp.camera = cam
vp.fit()
""",
        {"p1": [0.0, 0.0, 0.0], "p2": [0.0, 100.0, 50.0]},
    )

    # d2) Right side orthographic view (3 heat exhaust slots)
    raw_right, _, p_right = capture_scene_with_points(
        "ortho_right",
        """
vp = app.activeViewport
cam = vp.camera
cam.target = pt(150.0, 50.0, 25.0)
cam.eye = pt(370.0, 50.0, 25.0)
cam.upVector = vec(0, 0, 1)
cam.isSmoothTransition = False
vp.camera = cam
vp.fit()
""",
        {"p1": [150.0, 0.0, 0.0], "p2": [150.0, 100.0, 50.0]},
        cleanup_code="""
for i in range(root.bRepBodies.count):
    b = root.bRepBodies.item(i)
    b.isVisible = True
    b.opacity = 1.0
""",
    )

    im_top = crop_by_2d_corners(raw_top, p_top["p1"], p_top["p2"]).resize((900, 600), Image.Resampling.LANCZOS)
    im_xray = crop_by_2d_corners(raw_xray, p_xray["p1"], p_xray["p2"]).resize((900, 600), Image.Resampling.LANCZOS)
    # Flip back view horizontally so x=0 is left and x=150 is right ("vẽ như nhìn từ phía trước, xuyên qua hộp")
    im_back = crop_by_2d_corners(raw_back, p_back["p1"], p_back["p2"]).transpose(Image.Transpose.FLIP_LEFT_RIGHT).resize((900, 300), Image.Resampling.LANCZOS)
    im_left = crop_by_2d_corners(raw_left, p_left["p1"], p_left["p2"]).resize((420, 210), Image.Resampling.LANCZOS)
    im_right = crop_by_2d_corners(raw_right, p_right["p1"], p_right["p2"]).resize((420, 210), Image.Resampling.LANCZOS)

    sheet = Image.new("RGB", (2400, 1480), (255, 255, 255))
    drw = ImageDraw.Draw(sheet)

    f_title = get_font(bold=True, size=28)
    f_sub = get_font(bold=False, size=19)
    f_dim = get_font(bold=False, size=19)
    f_small = get_font(bold=False, size=17)
    f_bold_sm = get_font(bold=True, size=17)

    # Paste the 5 orthographic Fusion 360 views onto the 2400x1480 sheet
    sheet.paste(im_top, (140, 170))
    drw.rounded_rectangle([140, 170, 1040, 770], radius=36, outline=(34, 34, 34), width=3)

    sheet.paste(im_xray, (1330, 170))
    drw.rounded_rectangle([1330, 170, 2230, 770], radius=36, outline=(34, 34, 34), width=3)

    sheet.paste(im_back, (140, 1090))
    drw.rectangle([140, 1090, 1040, 1390], outline=(34, 34, 34), width=3)

    sheet.paste(im_left, (1330, 1090))
    drw.rectangle([1330, 1090, 1750, 1300], outline=(34, 34, 34), width=3)

    sheet.paste(im_right, (1840, 1090))
    drw.rectangle([1840, 1090, 2260, 1300], outline=(34, 34, 34), width=3)

    # Panel headings
    drw.text((140, 68), "a) Nắp (mặt trên), nhìn từ trên xuống (Fusion 360 Ortho)", font=f_title, fill=(17, 17, 17))
    drw.text((140, 105), "Gốc tọa độ (0, 0) ở góc trước bên trái. x: sang phải, y: về phía sau. Đơn vị mm.", font=f_sub, fill=(85, 85, 85))

    drw.text((1330, 68), "b) Bố trí linh kiện bên trong (nhìn xuyên nắp từ Fusion 360)", font=f_title, fill=(17, 17, 17))
    drw.text((1330, 105), "Thân hộp chứa ESP32, board đục lỗ, DHT22, jack DC; dưới nắp chứa LCD 1602, RC522, Buzzer, Quang trở.", font=f_sub, fill=(85, 85, 85))

    drw.text((140, 985), "c) Mặt sau (nhìn xuyên từ phía trước, x = 0..150 mm)", font=f_title, fill=(17, 17, 17))
    drw.text((140, 1022), "Chiều cao tính từ mặt đáy hộp (không tính chân cao su). Nắp dày 3 mm, thân cao 47 mm.", font=f_sub, fill=(85, 85, 85))

    drw.text((1330, 985), "d) Mặt trái và mặt phải (nhìn từ bên ngoài)", font=f_title, fill=(17, 17, 17))
    drw.text((1330, 1022), "Khe 30 × 2.4 mm, bo đầu tròn R1.2. Tâm khe tính theo khoảng cách tới mặt trước.", font=f_sub, fill=(85, 85, 85))

    # Helper to draw ID pill badge on sheet
    def draw_badge(x, y, id_str, text_str, col_hex):
        c_rgb = hex_to_rgb(col_hex)
        tb = drw.textbbox((0, 0), text_str, font=f_small)
        tw = tb[2] - tb[0]
        if id_str:
            bw = 54 + tw + 26
            drw.rounded_rectangle([x, y, x + bw, y + 32], radius=6, fill=(255, 255, 255), outline=c_rgb, width=2)
            drw.rounded_rectangle([x + 3, y + 3, x + 53, y + 29], radius=4, fill=c_rgb)
            drw.text((x + 10, y + 6), id_str, font=f_bold_sm, fill=(255, 255, 255))
            drw.text((x + 60, y + 6), text_str, font=f_small, fill=(30, 30, 30))
        else:
            bw = tw + 24
            drw.rounded_rectangle([x, y, x + bw, y + 32], radius=6, fill=(255, 255, 255), outline=c_rgb, width=2)
            drw.text((x + 12, y + 6), text_str, font=f_small, fill=(30, 30, 30))

    # Panel (a) badges & dimensions
    draw_badge(224, 235, "ID 6", "LCD 1602 (cửa sổ 73 × 26)", "#6d4c41")
    draw_badge(615, 235, "ID 4", "Ø6 LED", "#8e24aa")
    draw_badge(860, 235, "ID 4", "Ø12.2 nút nhấn", "#8e24aa")
    draw_badge(775, 550, "ID 3", "19 lỗ Ø2.2", "#1e88e5")
    draw_badge(685, 680, "ID 2", "Ø5.6 quang trở", "#fb8c00")
    draw_badge(240, 720, "ID 5", "Vùng quẹt thẻ RC522 (52 × 34)", "#43a047")
    drw.text((200, 185), "4 lỗ Ø3.4 (vít M3)", font=f_small, fill=(60, 80, 95))

    # Dimension lines for Panel (a): 150 mm width, 100 mm depth
    drw.line([(140, 820), (1040, 820)], fill=(50, 50, 50), width=2)
    drw.line([(140, 770), (140, 830)], fill=(120, 120, 120), width=1)
    drw.line([(1040, 770), (1040, 830)], fill=(120, 120, 120), width=1)
    drw.text((572, 792), "150 mm", font=f_dim, fill=(30, 30, 30))

    drw.line([(95, 170), (95, 770)], fill=(50, 50, 50), width=2)
    drw.line([(85, 170), (140, 170)], fill=(120, 120, 120), width=1)
    drw.line([(85, 770), (140, 770)], fill=(120, 120, 120), width=1)
    drw.text((35, 460), "100", font=f_dim, fill=(30, 30, 30))

    # Coordinate ticks on Panel (a)
    for x_mm, px in [(52, 452), (110, 800), (122, 872), (133, 938)]:
        drw.line([(px, 770), (px, 855)], fill=(150, 150, 150), width=1)
        drw.text((px - 14, 862), str(x_mm), font=f_small, fill=(50, 50, 50))
    drw.text((100, 862), "x =", font=f_small, fill=(50, 50, 50))

    for y_mm, py in [(76, 314), (68, 362), (48, 482), (18, 662)]:
        drw.line([(1040, py), (1068, py)], fill=(150, 150, 150), width=1)
        drw.text((1074, py - 10), str(y_mm), font=f_small, fill=(50, 50, 50))
    drw.text((1070, 145), "y =", font=f_small, fill=(50, 50, 50))
    drw.text((160, 905), "Tâm lỗ: LCD (52, 68) · nút (133, 76) · LED (110, 76) · loa (122, 48) · quang trở (134, 18) · vùng thẻ (42, 26)", font=f_small, fill=(50, 50, 50))

    # Panel (b) labels
    draw_badge(1360, 360, "ID 1", "DHT22 sát khe gió", "#e53935")
    draw_badge(1450, 200, None, "Jack DC 5V", "#546e7a")
    draw_badge(1540, 390, "ID 6", "LCD 1602 + I2C", "#6d4c41")
    draw_badge(1540, 610, "ID 5", "RFID RC522", "#43a047")
    draw_badge(1800, 200, None, "Board đục lỗ 70×50", "#7a5c1f")
    draw_badge(2020, 360, None, "ESP32 DevKit V1", "#1e293b")
    draw_badge(1905, 485, "ID 3", "Buzzer", "#1e88e5")
    draw_badge(1960, 650, "ID 2", "Quang trở LM393", "#fb8c00")
    drw.text((1430, 805), "DHT22 cách ESP32 khoảng 100 mm để nhiệt của ESP32 không làm sai số đo.", font=f_small, fill=(50, 50, 50))
    drw.text((1415, 835), "Khe hút gió đặt thấp bên trái, khe thoát nhiệt đặt cao bên phải (đối lưu tự nhiên).", font=f_small, fill=(50, 50, 50))

    # Panel (c) labels & dimensions
    draw_badge(460, 1170, None, "USB 13 × 9, tâm x = 126, cao 23", "#546e7a")
    draw_badge(355, 1305, None, "Jack DC Ø8, tâm x = 30, cao 16", "#546e7a")
    drw.line([(95, 1090), (95, 1390)], fill=(50, 50, 50), width=2)
    drw.text((42, 1230), "50", font=f_dim, fill=(30, 30, 30))
    drw.line([(140, 1435), (1040, 1435)], fill=(50, 50, 50), width=2)
    drw.text((572, 1408), "150 mm", font=f_dim, fill=(30, 30, 30))

    # Panel (d) labels
    drw.text((1370, 1320), "Mặt trái: 5 khe hút gió cho DHT22 (ID 1)", font=f_bold_sm, fill=(211, 47, 47))
    drw.text((1355, 1352), "tâm cách mặt trước 67 mm · cao 9, 13.5, 18, 22.5, 27 mm", font=f_small, fill=(60, 60, 60))

    drw.text((1895, 1320), "Mặt phải: 3 khe thoát nhiệt", font=f_bold_sm, fill=(55, 71, 79))
    drw.text((1885, 1352), "tâm cách mặt trước 72 mm · cao 31, 35.5, 40 mm", font=f_small, fill=(60, 60, 60))

    drw.text((1610, 1430), "Hộp 150 × 100 × 50 mm · thành 2.5 · bo góc R6 · trụ vít Ø9 lỗ Ø2.5 ở 4 góc (7, 7)", font=f_small, fill=(100, 100, 100))

    save_both(sheet, "hinh_3d_6_ban_ve_kich_thuoc.png")


if __name__ == "__main__":
    build_all_6_images()
