"""
Build the complete 3D CAD model of Pomodoro-Box in Autodesk Fusion 360
via the live AntigravityBridge (http://127.0.0.1:18080/exec).

All coordinates and dimensions strictly follow:
- docs/design/thong_so_ve_fusion.md
- proposal/assets/design/hinh_3d_1..6.png
- proposal/main.pdf (Section 2.1)
"""

import json
import urllib.request

BRIDGE_URL = "http://127.0.0.1:18080"

FUSION_CODE = r'''
# Reset current document by deleting existing occurrences, bodies, and sketches in root
for i in range(root.occurrences.count - 1, -1, -1):
    root.occurrences.item(i).deleteMe()
for i in range(root.bRepBodies.count - 1, -1, -1):
    root.bRepBodies.item(i).deleteMe()
for i in range(root.sketches.count - 1, -1, -1):
    root.sketches.item(i).deleteMe()

# Hide origin planes/axes for a clean viewport
root.isOriginFolderLightBulbOn = False

# Appearance helper
lib = app.materialLibraries.itemByName('Fusion Appearance Library')
base_paint = lib.appearances.itemByName('Paint - Enamel Glossy (Black)')

def get_color(name, r, g, b, roughness=0.38):
    app_item = design.appearances.itemByName(name)
    if not app_item:
        app_item = design.appearances.addByCopy(base_paint, name)
    c_prop = app_item.appearanceProperties.itemById('opaque_albedo')
    if c_prop and isinstance(c_prop, adsk.core.ColorProperty):
        c_prop.value = adsk.core.Color.create(int(r), int(g), int(b), 255)
    r_prop = app_item.appearanceProperties.itemById('surface_roughness')
    if r_prop and isinstance(r_prop, adsk.core.FloatProperty):
        r_prop.value = float(roughness)
    return app_item

col_coral      = get_color('Pomodoro_Coral', 232, 93, 74, 0.35)
col_lid_white  = get_color('Pomodoro_LidWhite', 236, 236, 236, 0.40)
col_dark_gray  = get_color('Pomodoro_DarkGray', 38, 42, 48, 0.45)
col_silver     = get_color('Pomodoro_Silver', 200, 206, 214, 0.20)
col_brass      = get_color('Pomodoro_Brass', 205, 165, 65, 0.25)
col_perfboard  = get_color('Pomodoro_Perfboard', 214, 182, 108, 0.45)
col_pcb_blue   = get_color('Pomodoro_PCB_Blue', 37, 116, 218, 0.35)
col_pcb_green  = get_color('Pomodoro_PCB_Green', 46, 148, 75, 0.35)
col_lcd_screen = get_color('Pomodoro_LCD_Screen', 59, 130, 246, 0.15)
col_red_accent = get_color('Pomodoro_Red_Accent', 239, 62, 54, 0.25)
col_led_orange = get_color('Pomodoro_LED_OrangeRed', 255, 95, 55, 0.15)
col_white_dht  = get_color('Pomodoro_White_Sensor', 245, 247, 250, 0.35)
col_rfid_mark  = get_color('Pomodoro_RFID_Accent', 238, 124, 107, 0.40)

# Geometry helpers
def sk_pt(sk, x_mm, y_mm, z_mm):
    p = sk.modelToSketchSpace(pt(x_mm, y_mm, z_mm))
    return adsk.core.Point3D.create(p.x, p.y, 0.0)

def draw_rounded_rect_xy(sk, x_min, y_min, x_max, y_max, r_mm):
    lines = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs
    rect = lines.addTwoPointRectangle(sk_pt(sk, x_min, y_min, 0), sk_pt(sk, x_max, y_max, 0))
    if r_mm > 0:
        for i in range(4):
            l1 = rect.item(i)
            l2 = rect.item((i + 1) % 4)
            arcs.addFillet(l1, l1.endSketchPoint.geometry, l2, l2.startSketchPoint.geometry, mm(r_mm))

def draw_rounded_rect_xz(sk, x_min, z_min, x_max, z_max, r_mm):
    lines = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs
    rect = lines.addTwoPointRectangle(sk_pt(sk, x_min, 0, z_min), sk_pt(sk, x_max, 0, z_max))
    if r_mm > 0:
        for i in range(4):
            l1 = rect.item(i)
            l2 = rect.item((i + 1) % 4)
            arcs.addFillet(l1, l1.endSketchPoint.geometry, l2, l2.startSketchPoint.geometry, mm(r_mm))

def draw_slot_yz(sk, y_center, z_center, length_mm, height_mm):
    r = height_mm / 2.0
    half_flat = (length_mm / 2.0) - r
    lines = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs
    l1 = lines.addByTwoPoints(
        sk_pt(sk, 0, y_center - half_flat, z_center - r),
        sk_pt(sk, 0, y_center + half_flat, z_center - r)
    )
    l2 = lines.addByTwoPoints(
        sk_pt(sk, 0, y_center + half_flat, z_center + r),
        sk_pt(sk, 0, y_center - half_flat, z_center + r)
    )
    arcs.addByThreePoints(l1.endSketchPoint, sk_pt(sk, 0, y_center + half_flat + r, z_center), l2.startSketchPoint)
    arcs.addByThreePoints(l2.endSketchPoint, sk_pt(sk, 0, y_center - half_flat - r, z_center), l1.startSketchPoint)

def extrude_all(comp, sk, start_mm, end_mm, op, target_bodies=None, name=None, color=None):
    profs = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count):
        profs.add(sk.profiles.item(i))
    ext_in = comp.features.extrudeFeatures.createInput(profs, op)
    if abs(start_mm) > 1e-6:
        ext_in.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(mm(start_mm)))
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(end_mm - start_mm)))
    if target_bodies:
        ext_in.participantBodies = target_bodies
    feat = comp.features.extrudeFeatures.add(ext_in)
    sk.isVisible = False
    if op == adsk.fusion.FeatureOperations.NewBodyFeatureOperation and feat.bodies.count > 0:
        for i in range(feat.bodies.count):
            b = feat.bodies.item(i)
            if name:
                b.name = name if feat.bodies.count == 1 else f"{name}_{i+1}"
            if color:
                b.appearance = color
    return feat


# ==============================================================================
# 1. THAN HOP (Bottom Case: 150 x 100 x 47 mm)
# ==============================================================================
comp_bottom = root
comp_top = root
comp_bot_parts = root
comp_top_parts = root

# 1a. Outer block 150 x 100 x 47 mm, R6
sk_outer = comp_bottom.sketches.add(comp_bottom.xYConstructionPlane)
sk_outer.name = "Sk_Vien_Ngoai_150x100"
draw_rounded_rect_xy(sk_outer, 0, 0, 150, 100, 6.0)
feat_outer = extrude_all(
    comp_bottom, sk_outer, 0, 47.0,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="01_Than_Hop_BottomCase", color=col_coral
)
body_bottom = feat_outer.bodies.item(0)

# 1b. Inner cavity (wall 2.5 mm, bottom 2.5 mm, inner corner R3.5)
sk_cavity = comp_bottom.sketches.add(comp_bottom.xYConstructionPlane)
sk_cavity.name = "Sk_Long_Hop_145x95"
draw_rounded_rect_xy(sk_cavity, 2.5, 2.5, 147.5, 97.5, 3.5)
extrude_all(
    comp_bottom, sk_cavity, 2.5, 48.0,
    adsk.fusion.FeatureOperations.CutFeatureOperation,
    target_bodies=[body_bottom]
)

# 1c. 4 Corner Screw Bosses (Ø9 mm at (7,7), (143,7), (7,93), (143,93), Z = 2.5..47)
boss_coords = [(7.0, 7.0), (143.0, 7.0), (7.0, 93.0), (143.0, 93.0)]
sk_boss = comp_bottom.sketches.add(comp_bottom.xYConstructionPlane)
sk_boss.name = "Sk_4_Tru_Vit_M3_D9"
for bx, by in boss_coords:
    sk_boss.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_boss, bx, by, 0), mm(4.5))
extrude_all(
    comp_bottom, sk_boss, 2.5, 47.0,
    adsk.fusion.FeatureOperations.JoinFeatureOperation,
    target_bodies=[body_bottom]
)

# 1d. 4 Screw Pilot Holes (Ø2.5 mm in bosses, Z = 5.0..47.5)
sk_boss_hole = comp_bottom.sketches.add(comp_bottom.xYConstructionPlane)
sk_boss_hole.name = "Sk_4_Lo_Ren_M3_D2_5"
for bx, by in boss_coords:
    sk_boss_hole.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_boss_hole, bx, by, 0), mm(1.25))
extrude_all(
    comp_bottom, sk_boss_hole, 5.0, 47.5,
    adsk.fusion.FeatureOperations.CutFeatureOperation,
    target_bodies=[body_bottom]
)

# 1e. Back Wall Cutouts: USB (13 x 9, R2 at x=126, z=23) and DC Jack (Ø8 at x=30, z=16)
sk_back = comp_bottom.sketches.add(comp_bottom.xZConstructionPlane)
sk_back.name = "Sk_Mat_Sau_USB_JackDC"
draw_rounded_rect_xz(sk_back, 126.0 - 6.5, 23.0 - 4.5, 126.0 + 6.5, 23.0 + 4.5, 2.0)
sk_back.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_back, 30.0, 0, 16.0), mm(4.0))
extrude_all(
    comp_bottom, sk_back, 95.0, 102.0,
    adsk.fusion.FeatureOperations.CutFeatureOperation,
    target_bodies=[body_bottom]
)

# 1f. Left Wall Cutouts (ID 1: 5 air intake slots 30 x 2.4 for DHT22 at y=67, z=9, 13.5, 18, 22.5, 27)
sk_left = comp_bottom.sketches.add(comp_bottom.yZConstructionPlane)
sk_left.name = "Sk_Mat_Trai_5_Khe_DHT22"
for zc in [9.0, 13.5, 18.0, 22.5, 27.0]:
    draw_slot_yz(sk_left, 67.0, zc, 30.0, 2.4)
extrude_all(
    comp_bottom, sk_left, -1.0, 5.0,
    adsk.fusion.FeatureOperations.CutFeatureOperation,
    target_bodies=[body_bottom]
)

# 1g. Right Wall Cutouts (3 heat exhaust slots 30 x 2.4 at y=72, z=31, 35.5, 40)
sk_right = comp_bottom.sketches.add(comp_bottom.yZConstructionPlane)
sk_right.name = "Sk_Mat_Phai_3_Khe_Thoat_Nhiet"
for zc in [31.0, 35.5, 40.0]:
    draw_slot_yz(sk_right, 72.0, zc, 30.0, 2.4)
extrude_all(
    comp_bottom, sk_right, 145.0, 151.0,
    adsk.fusion.FeatureOperations.CutFeatureOperation,
    target_bodies=[body_bottom]
)
body_bottom.appearance = col_coral


# ==============================================================================
# 2. NAP HOP (Top Cover: 150 x 100 x 3 mm, Z = 47..50 mm)
# ==============================================================================

# 2a. Lid plate 150 x 100 x 3 mm (Z = 47..50 mm)
sk_lid = comp_top.sketches.add(comp_top.xYConstructionPlane)
sk_lid.name = "Sk_Nap_Hop_150x100"
draw_rounded_rect_xy(sk_lid, 0, 0, 150, 100, 6.0)
feat_lid = extrude_all(
    comp_top, sk_lid, 47.0, 50.0,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="02_Nap_Hop_TopCover", color=col_lid_white
)
body_lid = feat_lid.bodies.item(0)

# 2b. LCD Window Cutout (ID 6: 73 x 26, R1 at center (52, 68))
sk_lcd_win = comp_top.sketches.add(comp_top.xYConstructionPlane)
sk_lcd_win.name = "Sk_Cua_So_LCD_73x26"
draw_rounded_rect_xy(sk_lcd_win, 52.0 - 36.5, 68.0 - 13.0, 52.0 + 36.5, 68.0 + 13.0, 1.0)
extrude_all(
    comp_top, sk_lcd_win, 46.5, 50.5,
    adsk.fusion.FeatureOperations.CutFeatureOperation,
    target_bodies=[body_lid]
)

# 2c. Circular Through-Holes on Lid:
# - 4 corner M3 holes Ø3.4 at (7,7), (143,7), (7,93), (143,93)
# - ID 4 Button Ø12.2 at (133, 76)
# - ID 4 Red LED Ø6.0 at (110, 76)
# - ID 2 Photoresistor LDR Ø5.6 at (134, 18)
# - ID 3 Buzzer 19 holes Ø2.2 at (122, 48): 1 center + 6 on R4 + 12 on R8
sk_holes = comp_top.sketches.add(comp_top.xYConstructionPlane)
sk_holes.name = "Sk_Cac_Lo_Tron_Tren_Nap"
circles = sk_holes.sketchCurves.sketchCircles

for bx, by in boss_coords:
    circles.addByCenterRadius(sk_pt(sk_holes, bx, by, 0), mm(1.7))

circles.addByCenterRadius(sk_pt(sk_holes, 133.0, 76.0, 0), mm(6.1))
circles.addByCenterRadius(sk_pt(sk_holes, 110.0, 76.0, 0), mm(3.0))
circles.addByCenterRadius(sk_pt(sk_holes, 134.0, 18.0, 0), mm(2.8))

# 19 buzzer holes Ø2.2
bz_x, bz_y = 122.0, 48.0
circles.addByCenterRadius(sk_pt(sk_holes, bz_x, bz_y, 0), mm(1.1))
for k in range(6):
    ang = math.radians(k * 60.0)
    circles.addByCenterRadius(sk_pt(sk_holes, bz_x + 4.0 * math.cos(ang), bz_y + 4.0 * math.sin(ang), 0), mm(1.1))
for k in range(12):
    ang = math.radians(k * 30.0)
    circles.addByCenterRadius(sk_pt(sk_holes, bz_x + 8.0 * math.cos(ang), bz_y + 8.0 * math.sin(ang), 0), mm(1.1))

extrude_all(
    comp_top, sk_holes, 46.5, 50.5,
    adsk.fusion.FeatureOperations.CutFeatureOperation,
    target_bodies=[body_lid]
)

# 2d. Shallow recess for buzzer grille (Ø21 mm, depth 0.25 mm) & 4 screw countersinks (Ø6 mm, depth 0.4 mm)
sk_recess = comp_top.sketches.add(comp_top.xYConstructionPlane)
sk_recess.name = "Sk_Vi_Sa_Loa_Va_Vit"
sk_recess.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_recess, bz_x, bz_y, 0), mm(10.5))
for bx, by in boss_coords:
    sk_recess.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_recess, bx, by, 0), mm(3.0))
extrude_all(
    comp_top, sk_recess, 49.7, 50.2,
    adsk.fusion.FeatureOperations.CutFeatureOperation,
    target_bodies=[body_lid]
)

# 2e. ID 5: RFID Tap Zone "QUET THE" (52 x 34 mm at center (42, 26), embossed/inlaid 0.15 mm on top surface, not cut through)
sk_rfid_zone = comp_top.sketches.add(comp_top.xYConstructionPlane)
sk_rfid_zone.name = "Sk_Vung_Quet_The_52x34"
draw_rounded_rect_xy(sk_rfid_zone, 42.0 - 20.0, 26.0 - 7.0, 42.0 + 4.0, 26.0 + 9.0, 2.5)
extrude_all(
    comp_top, sk_rfid_zone, 50.0, 50.15,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="Bieu_Tuong_The_RFID", color=col_rfid_mark
)

# 2f. 4 Underside Standoffs for LCD 1602 (M3 pillars, length 7 mm, Z = 40..47 mm)
lcd_standoffs = [(14.5, 52.5), (89.5, 52.5), (14.5, 83.5), (89.5, 83.5)]
sk_lcd_post = comp_top.sketches.add(comp_top.xYConstructionPlane)
sk_lcd_post.name = "Sk_4_Cot_Do_LCD_Dai_7mm"
for lx, ly in lcd_standoffs:
    sk_lcd_post.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_lcd_post, lx, ly, 0), mm(2.75))
extrude_all(
    comp_top, sk_lcd_post, 40.0, 47.0,
    adsk.fusion.FeatureOperations.JoinFeatureOperation,
    target_bodies=[body_lid]
)
body_lid.appearance = col_lid_white


# ==============================================================================
# 3. LINH KIEN DAY HOP (Bottom Case Internal Components)
# ==============================================================================

# 3a. 4 Rubber Feet (Ø10 x 2 mm at (14,12), (136,12), (14,88), (136,88), Z = -2..0)
feet_coords = [(14.0, 12.0), (136.0, 12.0), (14.0, 88.0), (136.0, 88.0)]
sk_feet = comp_bot_parts.sketches.add(comp_bot_parts.xYConstructionPlane)
sk_feet.name = "Sk_4_Chan_Cao_Su"
for fx, fy in feet_coords:
    sk_feet.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_feet, fx, fy, 0), mm(5.0))
extrude_all(
    comp_bot_parts, sk_feet, -2.0, 0.0,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="Chan_Cao_Su", color=col_dark_gray
)

# 3b. 4 Brass Standoffs (Ø4 x 5 mm, Z = 2.5..7.5) + Perfboard 70 x 50 mm (x=75..145, y=46..96, Z=7.5..9.1)
pb_standoffs = [(78.0, 49.0), (142.0, 49.0), (78.0, 93.0), (142.0, 93.0)]
sk_pb_post = comp_bot_parts.sketches.add(comp_bot_parts.xYConstructionPlane)
sk_pb_post.name = "Sk_4_Cot_Dong_Cao_5mm"
for px, py in pb_standoffs:
    sk_pb_post.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_pb_post, px, py, 0), mm(2.0))
extrude_all(
    comp_bot_parts, sk_pb_post, 2.5, 7.5,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="Cot_Dong_M3", color=col_brass
)

sk_pb = comp_bot_parts.sketches.add(comp_bot_parts.xYConstructionPlane)
sk_pb.name = "Sk_Board_Duc_Lo_70x50"
sk_pb.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_pb, 75.0, 46.0, 0), sk_pt(sk_pb, 145.0, 96.0, 0))
extrude_all(
    comp_bot_parts, sk_pb, 7.5, 9.1,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="Board_Duc_Lo_70x50", color=col_perfboard
)

# 3c. ESP32 DevKit V1 (x=112..140, y=45.5..97, USB facing rear at x=126)
sk_esp_hdr = comp_bot_parts.sketches.add(comp_bot_parts.xYConstructionPlane)
sk_esp_hdr.name = "Sk_ESP32_Headers"
sk_esp_hdr.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_esp_hdr, 113.0, 48.0, 0), sk_pt(sk_esp_hdr, 115.5, 94.0, 0))
sk_esp_hdr.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_esp_hdr, 136.5, 48.0, 0), sk_pt(sk_esp_hdr, 139.0, 94.0, 0))
extrude_all(
    comp_bot_parts, sk_esp_hdr, 9.1, 17.5,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="ESP32_Header", color=col_dark_gray
)

sk_esp_pcb = comp_bot_parts.sketches.add(comp_bot_parts.xYConstructionPlane)
sk_esp_pcb.name = "Sk_ESP32_PCB"
draw_rounded_rect_xy(sk_esp_pcb, 112.0, 45.5, 140.0, 97.0, 1.0)
extrude_all(
    comp_bot_parts, sk_esp_pcb, 17.5, 19.1,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="ESP32_DevKit_V1_PCB", color=col_dark_gray
)

sk_esp_can = comp_bot_parts.sketches.add(comp_bot_parts.xYConstructionPlane)
sk_esp_can.name = "Sk_ESP32_WROOM_Shield"
sk_esp_can.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_esp_can, 117.0, 52.0, 0), sk_pt(sk_esp_can, 135.0, 78.0, 0))
extrude_all(
    comp_bot_parts, sk_esp_can, 19.1, 22.3,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="ESP32_WROOM32_Shield", color=col_silver
)

sk_esp_usb = comp_bot_parts.sketches.add(comp_bot_parts.xYConstructionPlane)
sk_esp_usb.name = "Sk_ESP32_MicroUSB"
sk_esp_usb.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_esp_usb, 122.0, 92.0, 0), sk_pt(sk_esp_usb, 130.0, 98.5, 0))
extrude_all(
    comp_bot_parts, sk_esp_usb, 19.1, 22.1,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="ESP32_Cong_MicroUSB", color=col_silver
)

# 3d. ID 1: DHT22 Sensor + L-Bracket near Left Vent Slots (y=59.5..74.5, z=5..30)
sk_dht_br = comp_bot_parts.sketches.add(comp_bot_parts.xYConstructionPlane)
sk_dht_br.name = "Sk_DHT22_Gia_Chu_L"
sk_dht_br.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_dht_br, 5.0, 58.5, 0), sk_pt(sk_dht_br, 16.0, 75.5, 0))
extrude_all(
    comp_bot_parts, sk_dht_br, 2.5, 5.0,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="DHT22_De_Kep_L", color=col_silver
)

sk_dht_pcb = comp_bot_parts.sketches.add(comp_bot_parts.xYConstructionPlane)
sk_dht_pcb.name = "Sk_DHT22_Module"
sk_dht_pcb.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_dht_pcb, 9.5, 59.5, 0), sk_pt(sk_dht_pcb, 11.2, 74.5, 0))
extrude_all(
    comp_bot_parts, sk_dht_pcb, 5.0, 30.0,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="DHT22_PCB", color=col_pcb_blue
)

sk_dht_body = comp_bot_parts.sketches.add(comp_bot_parts.xYConstructionPlane)
sk_dht_body.name = "Sk_DHT22_Sensor"
sk_dht_body.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_dht_body, 3.8, 59.5, 0), sk_pt(sk_dht_body, 9.5, 74.5, 0))
extrude_all(
    comp_bot_parts, sk_dht_body, 8.0, 28.0,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="DHT22_Cam_Bien", color=col_white_dht
)

# 3e. DC 5V Power Jack at Rear Wall (x=30, z=16, y=85..101.2)
sk_dc = comp_bot_parts.sketches.add(comp_bot_parts.xZConstructionPlane)
sk_dc.name = "Sk_Jack_DC_5V"
sk_dc.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_dc, 30.0, 0, 16.0), mm(3.9))
extrude_all(
    comp_bot_parts, sk_dc, 85.0, 101.2,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="Jack_DC_5V_Than", color=col_dark_gray
)

sk_dc_nut = comp_bot_parts.sketches.add(comp_bot_parts.xZConstructionPlane)
sk_dc_nut.name = "Sk_Jack_DC_5V_Collar"
sk_dc_nut.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_dc_nut, 30.0, 0, 16.0), mm(5.4))
extrude_all(
    comp_bot_parts, sk_dc_nut, 100.0, 101.5,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="Jack_DC_5V_Vien_Ngoai", color=col_dark_gray
)


# ==============================================================================
# 4. LINH KIEN DUOI NAP (Underside of Lid Components)
# ==============================================================================

# 4a. ID 6: LCD 1602 + I2C Module (x=12..92, y=50..86, under lid at Z=35..47)
sk_lcd_pcb = comp_top_parts.sketches.add(comp_top_parts.xYConstructionPlane)
sk_lcd_pcb.name = "Sk_LCD1602_PCB_80x36"
sk_lcd_pcb.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_lcd_pcb, 12.0, 50.0, 0), sk_pt(sk_lcd_pcb, 92.0, 86.0, 0))
extrude_all(
    comp_top_parts, sk_lcd_pcb, 38.4, 40.0,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="LCD1602_PCB_Xanh", color=col_pcb_green
)

sk_lcd_bz = comp_top_parts.sketches.add(comp_top_parts.xYConstructionPlane)
sk_lcd_bz.name = "Sk_LCD1602_Khung_Den"
draw_rounded_rect_xy(sk_lcd_bz, 52.0 - 35.5, 68.0 - 12.0, 52.0 + 35.5, 68.0 + 12.0, 0.8)
extrude_all(
    comp_top_parts, sk_lcd_bz, 40.0, 46.8,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="LCD1602_Khung_Vien", color=col_dark_gray
)

sk_lcd_scr = comp_top_parts.sketches.add(comp_top_parts.xYConstructionPlane)
sk_lcd_scr.name = "Sk_LCD1602_Man_Hinh"
sk_lcd_scr.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_lcd_scr, 52.0 - 32.2, 68.0 - 8.0, 0), sk_pt(sk_lcd_scr, 52.0 + 32.2, 68.0 + 8.0, 0))
extrude_all(
    comp_top_parts, sk_lcd_scr, 46.8, 47.1,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="LCD1602_Man_Hinh_Hien_Thi", color=col_lcd_screen
)

sk_i2c = comp_top_parts.sketches.add(comp_top_parts.xYConstructionPlane)
sk_i2c.name = "Sk_LCD1602_Module_I2C"
sk_i2c.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_i2c, 18.0, 58.0, 0), sk_pt(sk_i2c, 60.0, 77.0, 0))
extrude_all(
    comp_top_parts, sk_i2c, 35.0, 38.4,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="LCD1602_Module_I2C", color=col_dark_gray
)

# 4b. ID 5: RFID RC522 Module (x=22..82, y=6..46, Z=44.4..46.0, 1mm below lid)
sk_rc522 = comp_top_parts.sketches.add(comp_top_parts.xYConstructionPlane)
sk_rc522.name = "Sk_RFID_RC522_60x40"
sk_rc522.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_rc522, 22.0, 6.0, 0), sk_pt(sk_rc522, 82.0, 46.0, 0))
extrude_all(
    comp_top_parts, sk_rc522, 44.4, 46.0,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="RFID_RC522_PCB", color=col_pcb_blue
)

# 4c. ID 3: Active Buzzer Module (x=95..128, y=41.5..54.5, buzzer Ø12 at (122, 48))
sk_bz_pcb = comp_top_parts.sketches.add(comp_top_parts.xYConstructionPlane)
sk_bz_pcb.name = "Sk_Module_Buzzer_PCB"
sk_bz_pcb.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_bz_pcb, 95.0, 41.5, 0), sk_pt(sk_bz_pcb, 128.0, 54.5, 0))
extrude_all(
    comp_top_parts, sk_bz_pcb, 36.0, 37.6,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="Buzzer_Module_PCB", color=col_pcb_blue
)

sk_bz_cyl = comp_top_parts.sketches.add(comp_top_parts.xYConstructionPlane)
sk_bz_cyl.name = "Sk_Buzzer_Cyl_D12"
sk_bz_cyl.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_bz_cyl, 122.0, 48.0, 0), mm(6.0))
extrude_all(
    comp_top_parts, sk_bz_cyl, 37.6, 47.0,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="Buzzer_Chu_Dong_D12", color=col_dark_gray
)

# 4d. ID 2: LDR Photoresistor Module LM393 (x=104..136, y=11..25, sensor at (134, 18))
sk_ldr_pcb = comp_top_parts.sketches.add(comp_top_parts.xYConstructionPlane)
sk_ldr_pcb.name = "Sk_Module_Quang_Tro_PCB"
sk_ldr_pcb.sketchCurves.sketchLines.addTwoPointRectangle(sk_pt(sk_ldr_pcb, 104.0, 11.0, 0), sk_pt(sk_ldr_pcb, 136.0, 25.0, 0))
extrude_all(
    comp_top_parts, sk_ldr_pcb, 39.0, 40.6,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="Quang_Tro_LM393_PCB", color=col_pcb_blue
)

sk_ldr_head = comp_top_parts.sketches.add(comp_top_parts.xYConstructionPlane)
sk_ldr_head.name = "Sk_Quang_Tro_Dau_Doc"
sk_ldr_head.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_ldr_head, 134.0, 18.0, 0), mm(2.4))
extrude_all(
    comp_top_parts, sk_ldr_head, 40.6, 49.2,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="Quang_Tro_Cam_Bien", color=col_perfboard
)

# 4e. ID 4: Push Button at (133, 76) & Red LED 5mm at (110, 76)
sk_btn_body = comp_top_parts.sketches.add(comp_top_parts.xYConstructionPlane)
sk_btn_body.name = "Sk_Nut_Nhan_Than_Ren"
sk_btn_body.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_btn_body, 133.0, 76.0, 0), mm(5.9))
extrude_all(
    comp_top_parts, sk_btn_body, 32.0, 50.0,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="Nut_Nhan_Than_Duoi", color=col_dark_gray
)

sk_btn_bezel = comp_top_parts.sketches.add(comp_top_parts.xYConstructionPlane)
sk_btn_bezel.name = "Sk_Nut_Nhan_Vien_Va_De_LED"
sk_btn_bezel.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_btn_bezel, 133.0, 76.0, 0), mm(7.4))
sk_btn_bezel.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_btn_bezel, 110.0, 76.0, 0), mm(3.8))
extrude_all(
    comp_top_parts, sk_btn_bezel, 50.0, 51.3,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="Vien_Giu_Nut_Va_LED", color=col_silver
)

sk_btn_cap = comp_top_parts.sketches.add(comp_top_parts.xYConstructionPlane)
sk_btn_cap.name = "Sk_Nut_Nhan_Mu_Do"
sk_btn_cap.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_btn_cap, 133.0, 76.0, 0), mm(5.5))
extrude_all(
    comp_top_parts, sk_btn_cap, 51.3, 54.5,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="Nut_Nhan_Do_ID4", color=col_red_accent
)

sk_led_dome = comp_top_parts.sketches.add(comp_top_parts.xYConstructionPlane)
sk_led_dome.name = "Sk_LED_Do_5mm"
sk_led_dome.sketchCurves.sketchCircles.addByCenterRadius(sk_pt(sk_led_dome, 110.0, 76.0, 0), mm(2.5))
extrude_all(
    comp_top_parts, sk_led_dome, 42.0, 55.2,
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    name="LED_Do_5mm_ID4", color=col_led_orange
)

# Set isometric front-top camera matching hinh_3d_1_ben_ngoai_truoc.png
vp = app.activeViewport
cam = vp.camera
cam.target = pt(75.0, 50.0, 24.0)
cam.eye = pt(-95.0, -145.0, 165.0)
cam.upVector = vec(0, 0, 1)
cam.isSmoothTransition = False
vp.camera = cam
vp.fit()
vp.refresh()

result = {"status": "built_successfully"}
'''


def main():
    payload = json.dumps({"code": FUSION_CODE, "fitView": True, "timeout": 60.0}).encode("utf-8")
    req = urllib.request.Request(
        f"{BRIDGE_URL}/exec",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=65.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(json.dumps(data, indent=2, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        print("HTTP ERROR:", e.code)
        print(e.read().decode("utf-8"))


if __name__ == "__main__":
    main()
