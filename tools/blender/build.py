"""Build the trial models, export .glb files and render previews.

Run: blender --background --python build.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
import critters  # noqa: E402
import traffic  # noqa: E402
from lib import (bevel, cyl, empty, export_glb, join, lathe, limb, mat, render_preview,  # noqa: E402
                 reset_scene, setup_render, slab, sphere, stadium, tbox, torus, tri_count)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

PINK, CYAN, ORANGE = 0xff3fa4, 0x3ff3ff, 0xff8a2a


def board_outline():
    """Pointed nose at +Y (forward), squared tail at -Y, so the board's direction reads at a glance."""
    right = []
    for i in range(15):
        y = -1.05 + 2.25 * i / 14
        if y > 0.45:
            t = (y - 0.45) / 0.75
            hw = 0.475 * math.sqrt(max(0.0, 1 - t * t)) ** 0.8
        elif y < -0.92:
            t = (-0.92 - y) / 0.13
            hw = 0.475 - 0.09 * (1 - math.sqrt(max(0.0, 1 - t * t)))
        else:
            hw = 0.475
        right.append((max(hw, 0.02), y))
    return [(x, y) for x, y in right] + [(-x, y) for x, y in reversed(right)]


def rider():
    root = empty("HoverRider")

    board = empty("Board", parent=root)
    deck_m = mat("deck", PINK, 0.3, 0.5)
    glow = mat("cyan_glow", CYAN, 0.3, 0, CYAN, 4)
    dark = mat("gunmetal", 0x2a2a40, 0.35, 0.8)

    def kick(x, y):
        nose = max(0.0, y - 0.55)
        tail = max(0.0, -y - 0.8)
        return 0.8 * nose * nose + 0.6 * tail * tail
    parts = [slab("deck", board_outline(), 0.1, deck_m, kick, (0, 0, -0.05), bev=0.03),
             slab("grip", stadium(0.32, 1.4, 6), 0.02, glow, None, (0, -0.1, 0.045), bev=0),
             sphere("nose_light", 0.07, mat("nose_light", 0xfff2c0, 0.2, 0, 0xfff2c0, 6), 8, 5,
                    loc=(0, 1.12, 0.3), scale=(1.4, 0.8, 0.6))]
    for s in (-1, 1):
        parts.append(tbox("rail", 0.04, 1.3, 0.05, glow, loc=(s * 0.47, 0, -0.06), bev=0.01))
        parts.append(cyl("pod", 0.2, 0.1, dark, 10, loc=(s * 0.0, s * 0.62, -0.1)))
        parts.append(cyl("pod_glow", 0.16, 0.02, glow, 10, loc=(0, s * 0.62, -0.155)))
    for s in (-0.26, 0.26):
        parts.append(cyl("thruster", 0.12, 0.3, dark, 10, loc=(s, -0.92, -0.12), rot=(90, 0, 0), r2=0.1, bev=0.02))
        parts.append(cyl("thruster_glow", 0.085, 0.02, glow, 10, loc=(s, -1.075, -0.12), rot=(90, 0, 0)))
    join("Board", parts, board).name = "BoardMesh"

    stance = empty("Stance", rot=(0, 0, 54), parent=root)
    pants = mat("pants", 0x24305e, 0.8)
    hoodie = mat("hoodie", ORANGE, 0.7, 0, 0x301000, 1)
    hood_dk = mat("hoodie_dark", 0xd8661a, 0.75)
    skin = mat("skin", 0xc98a5a, 0.6)
    shoe = mat("shoe", 0xf6eeff, 0.45)
    sole = mat("sole", PINK, 0.5)
    pack_m = mat("pack", 0x2b2244, 0.35, 0.7)

    body = []
    for s in (-1, 1):
        x = s * 0.27
        body += [limb("thigh", (x, 0.02, 0.92), (x * 1.05, 0.12, 0.52), 0.14, 0.12, pants),
                 limb("shin", (x * 1.05, 0.12, 0.52), (x * 1.1, 0.0, 0.18), 0.12, 0.1, pants),
                 tbox("shoe", 0.28, 0.42, 0.14, shoe, top_w=0.26, top_d=0.3, top_dy=-0.04,
                      loc=(x * 1.1, 0.05, 0.05), bev=0.05),
                 tbox("sole", 0.29, 0.43, 0.05, sole, loc=(x * 1.1, 0.05, 0.03), bev=0.02)]
    body += [tbox("hips", 0.62, 0.34, 0.2, pants, top_w=0.64, loc=(0, 0, 0.84), bev=0.06),
             tbox("torso", 0.6, 0.36, 0.62, hoodie, top_w=0.72, top_d=0.4, loc=(0, 0, 0.98), bev=0.09, segs=3),
             tbox("pocket", 0.4, 0.04, 0.16, hood_dk, top_w=0.36, loc=(0, 0.19, 1.03), bev=0.02),
             tbox("chest_stripe", 0.5, 0.03, 0.06, glow, top_w=0.56, loc=(0, 0.2, 1.3), bev=0),
             torus("hood", 0.2, 0.07, hood_dk, 14, 6, loc=(0, -0.08, 1.62), rot=(20, 0, 0)),
             limb("neck", (0, 0, 1.55), (0, 0, 1.72), 0.09, 0.09, skin, 8)]
    for s in (-1, 1):
        body.append(limb("string", (s * 0.07, 0.2, 1.56), (s * 0.08, 0.22, 1.38), 0.015, 0.015, shoe, 4))
    join("Body", body, stance)

    pack = empty("Pack", loc=(0, -0.3, 1.25), parent=stance)
    pk = [tbox("pack", 0.5, 0.24, 0.58, pack_m, top_w=0.46, loc=(0, 0, -0.3), bev=0.06),
          cyl("coil_post", 0.05, 0.14, pack_m, 6, loc=(0, 0, 0.32))]
    # The spark coil and charge cells stay code-built in the game, which recolours them per frame.
    join("PackMesh", pk, pack)

    for s, name in ((-1, "ArmL"), (1, "ArmR")):
        arm = empty(name, loc=(s * 0.38, 0, 1.48), rot=(0, -s * 62, 0), parent=stance)
        join(name + "Mesh", [limb("upper", (0, 0, 0), (0, 0.02, -0.34), 0.1, 0.09, hoodie, 8),
                             limb("fore", (0, 0.02, -0.34), (0, 0.12, -0.62), 0.09, 0.075, hoodie, 8),
                             tbox("cuff", 0.17, 0.17, 0.06, hood_dk, loc=(0, 0.115, -0.64), rot=(20, 0, 0), bev=0.02),
                             sphere("hand", 0.08, skin, 8, 6, loc=(0, 0.14, -0.72))], arm)

    head = empty("Head", loc=(0, 0, 1.92), parent=root)
    helm_m = mat("helmet", 0xf6eeff, 0.25, 0.4)
    hair_m = mat("hair", 0x3a2418, 0.8)
    eye_m = mat("eye_black", 0x050505, 0.1, 0.2)
    # Split so each world's outfit can hide the helmet, goggles and fin separately.
    join("HeadMesh", [sphere("head", 0.24, skin, 12, 8, scale=(1, 1, 1.05)),
                      lathe("hair", [(0.255 * math.sin(math.radians(d)), 0.255 * math.cos(math.radians(d)) + 0.01)
                                     for d in (110, 90, 60, 30, 0)], hair_m, 12, cap_bottom=False, cap_top=False,
                            rot=(-12, 0, 0)),
                      sphere("eye", 0.035, eye_m, 6, 4, loc=(-0.09, 0.225, -0.04), scale=(1, 0.5, 1.4)),
                      sphere("eye", 0.035, eye_m, 6, 4, loc=(0.09, 0.225, -0.04), scale=(1, 0.5, 1.4)),
                      tbox("smile", 0.1, 0.02, 0.025, dark, loc=(0, 0.2, -0.17), bev=0)], head)
    join("HelmetMesh", [lathe("helmet", [(0.31 * math.sin(a), 0.31 * math.cos(a) + 0.03) for a in
                                         [math.radians(d) for d in (100, 80, 60, 40, 20, 0)]],
                              helm_m, 14, smooth=60, cap_bottom=False, cap_top=False),
                        sphere("ear", 0.06, helm_m, 8, 5, loc=(-0.29, 0, -0.02), scale=(0.6, 1, 1)),
                        sphere("ear", 0.06, helm_m, 8, 5, loc=(0.29, 0, -0.02), scale=(0.6, 1, 1))], head)
    join("VisorMesh", [torus("goggle_strap", 0.255, 0.035, dark, 16, 5, loc=(0, 0, -0.05)),
                       sphere("lens", 0.09, glow, 10, 6, loc=(-0.1, 0.215, -0.05), scale=(1, 0.45, 0.8)),
                       sphere("lens", 0.09, glow, 10, 6, loc=(0.1, 0.215, -0.05), scale=(1, 0.45, 0.8))], head)
    join("FinMesh", [tbox("fin", 0.07, 0.42, 0.16, mat("fin", PINK, 0.4, 0.3), top_d=0.26, top_dy=-0.04,
                          loc=(0, -0.02, 0.29), bev=0.025)], head)

    scarf = empty("Scarf", loc=(0, -0.12, 1.62), parent=root)
    scarf_m = mat("scarf", PINK, 0.6, 0, 0x500a30, 1)
    join("ScarfMesh", [torus("wrap", 0.13, 0.05, scarf_m, 12, 5),
                       tbox("tail1", 0.2, 0.75, 0.05, scarf_m, top_w=0.16, loc=(0.04, -0.4, -0.05), rot=(-8, 0, 6), bev=0.02),
                       tbox("tail2", 0.16, 0.55, 0.05, scarf_m, top_w=0.12, loc=(-0.08, -0.32, -0.14), rot=(-18, 0, -10), bev=0.02)],
         scarf)
    return root


def car(color=0x39d0ff):
    root = empty("CityCar")
    body_m = mat("car_body", color, 0.28, 0.65)
    glass = mat("car_glass", 0x0c0820, 0.06, 0.9, 0x0a1030, 1)
    trim = mat("car_trim", 0x1a1a2a, 0.5, 0.4)
    head_l = mat("headlight", 0xfff2c0, 0.2, 0, 0xfff2c0, 6)
    tail_l = mat("taillight", 0xff2244, 0.2, 0, 0xff2244, 5)
    neon = mat("neon", PINK, 0.3, 0, PINK, 6)

    parts = [tbox("lower", 1.9, 4.0, 0.5, body_m, top_w=1.86, top_d=3.9, loc=(0, 0, 0.28), bev=0.14, segs=3),
             tbox("hood", 1.84, 1.25, 0.12, body_m, top_w=1.7, top_d=1.1, top_dy=-0.04, loc=(0, 1.3, 0.74), bev=0.06),
             tbox("trunk", 1.84, 0.7, 0.12, body_m, top_w=1.72, top_d=0.6, loc=(0, -1.6, 0.74), bev=0.06),
             tbox("cabin_glass", 1.7, 2.3, 0.56, glass, top_w=1.42, top_d=1.45, top_dy=-0.2, loc=(0, -0.3, 0.76), bev=0.08, segs=3),
             tbox("roof", 1.45, 1.5, 0.08, body_m, top_w=1.4, top_d=1.4, loc=(0, -0.5, 1.3), bev=0.04),
             tbox("bumper_f", 1.92, 0.22, 0.24, trim, loc=(0, 1.96, 0.24), bev=0.08),
             tbox("bumper_r", 1.92, 0.22, 0.24, trim, loc=(0, -1.96, 0.24), bev=0.08),
             tbox("grille", 1.0, 0.04, 0.16, trim, loc=(0, 2.0, 0.5), bev=0.02),
             tbox("taillight", 1.6, 0.06, 0.12, tail_l, loc=(0, -2.0, 0.62), bev=0.02),
             tbox("spoiler", 1.6, 0.32, 0.05, trim, loc=(0, -1.78, 1.0), rot=(-8, 0, 0), bev=0.02),
             tbox("underglow", 1.6, 3.2, 0.03, neon, loc=(0, 0, 0.2), bev=0)]
    for s in (-1, 1):
        parts += [tbox("headlight", 0.42, 0.06, 0.14, head_l, top_w=0.36, loc=(s * 0.62, 1.99, 0.58), bev=0.03),
                  tbox("pillar", 0.06, 0.08, 0.5, body_m, top_w=0.05, loc=(s * 0.79, -0.3, 0.78), rot=(0, s * -14, 0), bev=0),
                  tbox("mirror", 0.2, 0.1, 0.1, body_m, loc=(s * 1.02, 0.62, 0.86), bev=0.03),
                  tbox("side_stripe", 0.02, 3.0, 0.05, neon, loc=(s * 0.955, 0, 0.6), bev=0)]
        for y in (-1.25, 1.25):
            parts.append(tbox("arch", 0.12, 1.0, 0.36, trim, top_d=0.8, loc=(s * 0.92, y, 0.42), bev=0.04))
    join("Body", parts, root)

    tire = mat("tire", 0x0b0910, 0.9, 0.1)
    rim = mat("rim", 0xc8ccd8, 0.25, 0.9)
    hub = mat("hub_glow", CYAN, 0.3, 0, CYAN, 3)
    for sx, sy, n in ((-1, 1, "WheelFL"), (1, 1, "WheelFR"), (-1, -1, "WheelRL"), (1, -1, "WheelRR")):
        w = empty(n, loc=(sx * 0.86, sy * 1.25, 0.36), parent=root)
        join(n + "Mesh", [cyl("tire", 0.36, 0.3, tire, 18, rot=(0, 90, 0), bev=0.06),
                          cyl("rim", 0.22, 0.32, rim, 12, rot=(0, 90, 0)),
                          cyl("hub", 0.08, 0.34, hub, 8, rot=(0, 90, 0))], w)
    return root


def ufo():
    root = empty("MoonUFO")
    hull_m = mat("ufo_hull", 0xc8ccd8, 0.22, 0.85)
    band_m = mat("ufo_band", 0x3a3a52, 0.4, 0.7)
    core_m = mat("ufo_core", 0x7affb0, 0.3, 0, 0x7affb0, 6)
    dome_m = mat("ufo_dome", 0x9affc8, 0.05, 0.1, 0x1a7a4a, 0.6, alpha=0.4)
    alien_m = mat("alien", 0x6aff6a, 0.5, 0, 0x1a5a1a, 0.6)
    eye_m = mat("alien_eye", 0x050505, 0.05, 0.3)

    craft = empty("Craft", loc=(0, 0, 0.95), parent=root)
    R = 1.3
    hull = [lathe("hull", [(0, -0.3), (0.45, -0.3), (0.9, -0.22), (1.2, -0.08), (R, 0.0),
                           (1.18, 0.1), (0.8, 0.2), (0.55, 0.24), (0, 0.24)], hull_m, 24, smooth=35),
            torus("band", R - 0.02, 0.05, band_m, 24, 5),
            lathe("core", [(0.55, -0.31), (0.5, -0.38), (0, -0.4)], core_m, 16, cap_bottom=False),
            torus("core_ring", 0.58, 0.04, band_m, 16, 5, loc=(0, 0, -0.32))]
    for a in range(3):
        ang = math.radians(a * 120 + 90)
        hull.append(tbox("fin", 0.08, 0.5, 0.2, mat("ufo_fin", PINK, 0.35, 0.4), top_d=0.3, top_dy=-0.08,
                         loc=(math.cos(ang) * 0.85, math.sin(ang) * 0.85, 0.12), rot=(0, 0, a * 120), bev=0.02))
    join("Hull", hull, craft)

    ring = empty("LightRing", parent=craft)
    yel = mat("light_y", 0xffd23f, 0.3, 0, 0xffd23f, 6)
    pink = mat("light_p", PINK, 0.3, 0, PINK, 6)
    join("LightRingMesh", [sphere("bulb", 0.07, yel if i % 2 else pink, 8, 5,
                                  loc=(math.cos(i / 12 * 2 * math.pi) * (R + 0.02),
                                       math.sin(i / 12 * 2 * math.pi) * (R + 0.02), 0.0))
                           for i in range(12)], ring)

    pilot = empty("Alien", loc=(0, 0, 0.12), parent=craft)
    al = [sphere("head", 0.2, alien_m, 12, 8, loc=(0, 0, 0.28), scale=(1.15, 1, 1.05)),
          lathe("body", [(0, 0), (0.16, 0.02), (0.14, 0.14), (0.07, 0.2), (0, 0.2)], alien_m, 10)]
    for s in (-1, 1):
        al += [sphere("eye", 0.08, eye_m, 10, 6, loc=(s * 0.1, 0.15, 0.3), scale=(1, 0.5, 1.4),
                      rot=(0, s * 25, 0)),
               limb("antenna", (s * 0.08, 0, 0.45), (s * 0.14, -0.02, 0.55), 0.015, 0.012, alien_m, 5),
               sphere("tip", 0.04, core_m, 8, 5, loc=(s * 0.145, -0.02, 0.57))]
    join("AlienMesh", al, pilot)

    join("Dome", [sphere("dome", 0.6, dome_m, 18, 10, loc=(0, 0, 0.2), scale=(1, 1, 0.95))], craft)
    return root


def leaf(length, width, segs=8, bulge=0.7):
    """Flipper/fin outline running along +X from the root at x=0."""
    top = [(length * i / segs, width / 2 * math.sin(math.pi * i / segs) ** bulge * (1 - 0.35 * i / segs) + 0.03)
           for i in range(segs + 1)]
    return top + [(x, -y * 0.8) for x, y in reversed(top[1:-1])]


def turtle(golden=False):
    root = empty("SeaTurtle")
    shell_m = mat("shell_gold" if golden else "shell", 0xffc81a if golden else 0x2a8a5a, 0.5, 0.15,
                  0x302000 if golden else 0x061a0c, 1)
    plate_m = mat("plate_gold" if golden else "plate", 0xffe060 if golden else 0x5aaa6a, 0.55)
    skin_m = mat("turtle_skin", 0xc8d87a if golden else 0x8ac87a, 0.65)
    belly_m = mat("turtle_belly", 0xf0e6b0, 0.7)
    eye_m = mat("eye_black", 0x050505, 0.1, 0.2)
    white_m = mat("eye_white", 0xffffff, 0.3)

    body = empty("Body", loc=(0, 0.3, 0.75), parent=root)
    sx, sy, sz = 0.95, 1.45, 0.6
    shell = [lathe("shell", [(0, 1), (0.42, 0.92), (0.74, 0.68), (0.93, 0.38), (1.0, 0.1), (0.98, 0.0)],
                   shell_m, 16, scale=(sx, sy, sz), smooth=40, cap_top=False),
             torus("rim", 1.0, 0.07, shell_m, 20, 5, loc=(0, 0, 0.02), rot=(0, 0, 0)),
             sphere("plastron", 1.0, belly_m, 16, 8, scale=(0.9, 1.38, 0.16)),
             cyl("tail", 0.12, 0.35, skin_m, 6, loc=(0, -1.55, -0.02), rot=(90, 0, 0), r2=0.01)]
    shell[1].scale = (sx * 0.99, sy * 0.99, 1)
    for x, y in ((0, 0), (0, 0.6), (0, -0.6), (0.48, 0.3), (-0.48, 0.3), (0.48, -0.32), (-0.48, -0.32)):
        u, v = x / sx, y / sy
        z = sz * math.sqrt(max(0.0, 1 - u * u - v * v)) - 0.02
        nrm = Vector((u / sx, v / sy, z / sz / sz)).normalized()
        plate = cyl("plate", 0.26, 0.05, plate_m, 6, r2=0.22, bev=0.015)
        plate.location = Vector((x, y, z)) + nrm * 0.01
        plate.rotation_euler = nrm.to_track_quat("Z", "Y").to_euler()
        shell.append(plate)
    join("ShellMesh", shell, body)

    head = empty("Head", loc=(0, 1.38, 0.05), parent=body)
    hd = [limb("neck", (0, -0.2, -0.02), (0, 0.15, 0.02), 0.2, 0.2, skin_m, 10),
          sphere("head", 0.3, skin_m, 12, 8, loc=(0, 0.3, 0.05), scale=(1.05, 1.3, 0.88)),
          tbox("beak", 0.26, 0.05, 0.03, mat("beak", 0x3a4a2a, 0.6), loc=(0, 0.66, -0.04), bev=0)]
    for s in (-1, 1):
        hd += [sphere("eye", 0.09, white_m, 10, 6, loc=(s * 0.21, 0.45, 0.14)),
               sphere("pupil", 0.055, eye_m, 8, 5, loc=(s * 0.25, 0.5, 0.15))]
    join("HeadMesh", hd, head)

    for name, x, y, L, W, yaw in (("FlipperFL", 0.75, 0.7, 1.25, 0.5, 25), ("FlipperFR", -0.75, 0.7, 1.25, 0.5, -25),
                                  ("FlipperRL", 0.62, -0.95, 0.6, 0.36, -30), ("FlipperRR", -0.62, -0.95, 0.6, 0.36, 30)):
        side = 1 if x > 0 else -1
        f = empty(name, loc=(x, y, -0.02), rot=(0, 0, yaw), parent=body)
        outline = [(side * px, py) for px, py in leaf(L, W)]
        if side < 0:
            outline.reverse()
        join(name + "Mesh", [slab("flipper", outline, 0.07, skin_m, None, (0, 0, -0.035), bev=0.025)], f)
    return root


def pufferfish():
    root = empty("Pufferfish")
    r = 1.15
    body_m = mat("puffer", 0xffd23f, 0.55, 0, 0x2a1a00, 1)
    belly_m = mat("puffer_belly", 0xfff8e8, 0.6)
    spot_m = mat("puffer_spot", 0xc88a1a, 0.6)
    spike_m = mat("spike", 0xfff0c0, 0.5)
    white_m = mat("eye_white", 0xffffff, 0.3)
    eye_m = mat("eye_black", 0x050505, 0.1, 0.2)
    lip_m = mat("lips", 0xff7a7a, 0.4)

    body = empty("Body", loc=(0, 0, 1.3), parent=root)
    parts = [sphere("body", r, body_m, 18, 12),
             sphere("belly", r, belly_m, 16, 10, loc=(0, 0.05, -0.32), scale=(0.88, 0.88, 0.72))]
    n = 34
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        a = i * math.pi * (3 - math.sqrt(5))
        q = math.sqrt(1 - z * z)
        x, y = math.cos(a) * q, math.sin(a) * q
        if y > 0.55 and abs(z) < 0.6:
            continue
        p = (x * r * 0.97, y * r * 0.97, z * r * 0.97)
        ob = cyl("spike", 0.09, 0.42, spike_m, 5, r2=0.0)
        d = Vector((x, y, z))
        ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        ob.location = Vector(p) + d * 0.18
        parts.append(ob)
        if i % 3 == 0 and z > -0.2:
            parts.append(sphere("spot", 0.1, spot_m, 8, 5, loc=Vector(p) + (d.cross(Vector((0, 0, 1))).normalized() * 0.22 if abs(z) < 0.95 else Vector()),
                                scale=(1, 1, 0.4)))
    for s in (-1, 1):
        parts += [sphere("eye", 0.27, white_m, 12, 8, loc=(s * 0.45, 0.88, 0.38)),
                  sphere("pupil", 0.15, eye_m, 10, 6, loc=(s * 0.48, 1.1, 0.38))]
    parts.append(torus("lips", 0.13, 0.06, lip_m, 12, 6, loc=(0, r * 0.99, -0.12), rot=(90, 0, 0)))
    join("BodyMesh", parts, body)

    for name, s in (("FinL", 1), ("FinR", -1)):
        f = empty(name, loc=(s * r * 0.95, 0.1, -0.1), rot=(0, 0, s * -20), parent=body)
        outline = [(s * px, py) for px, py in leaf(0.55, 0.6, 6, 0.5)]
        if s < 0:
            outline.reverse()
        join(name + "Mesh", [slab("fin", outline, 0.06, body_m, None, (0, 0, -0.03), bev=0.02)], f)
    tail = empty("Tail", loc=(0, -r * 0.95, 0), parent=body)
    fan = [(0, 0.0)] + [(math.sin(math.radians(a)) * 0.7, -math.cos(math.radians(a)) * 0.7 - 0.05)
                        for a in range(-50, 51, 10)]
    tl = slab("tail", [(x, y) for x, y in fan], 0.06, body_m, None, (0, 0, -0.03), bev=0.02)
    tl.rotation_euler = (0, math.radians(90), 0)
    join("TailMesh", [tl], tail)
    return root


def whale():
    root = empty("Whale")
    skin_m = mat("whale", 0x2a3e5c, 0.55, 0.05, 0x060c18, 1)
    belly_m = mat("whale_belly", 0xb8c8d8, 0.6)
    groove_m = mat("whale_groove", 0x8a9ab0, 0.6)
    barn_m = mat("barnacle", 0xe8e8e0, 0.8)
    white_m = mat("eye_white", 0xffffff, 0.3)
    eye_m = mat("eye_black", 0x050505, 0.1, 0.2)

    body = empty("Body", loc=(0, 0, 1.75), parent=root)
    prof = [(0, -3.2), (0.45, -3.1), (0.75, -2.6), (1.05, -1.6), (1.3, -0.4), (1.42, 0.8), (1.45, 1.9),
            (1.4, 2.9), (1.25, 3.6), (0.95, 4.15), (0.5, 4.45), (0, 4.55)]
    parts = [lathe("body", prof, skin_m, 18, rot=(-90, 0, 0), scale=(0.92, 1.0, 1.05), smooth=50),
             lathe("belly", [(0, -1.6), (0.8, -1.3), (1.1, 0.4), (1.15, 2.4), (1.0, 3.6), (0.55, 4.25), (0, 4.4)],
                   belly_m, 16, loc=(0, 0, -0.55), rot=(-90, 0, 0), scale=(0.95, 1.0, 0.78), smooth=50)]
    for k in range(5):
        x = (k - 2) * 0.26
        parts.append(tbox("groove", 0.05, 3.0, 0.03, groove_m, loc=(x, 2.1, -1.48 + abs(x) * 0.12), rot=(4, 0, 0), bev=0))
    for s in (-1, 1):
        parts += [sphere("eye", 0.16, white_m, 10, 6, loc=(s * 1.18, 3.3, -0.15)),
                  sphere("pupil", 0.1, eye_m, 8, 5, loc=(s * 1.26, 3.36, -0.15)),
                  limb("mouth", (s * 0.4, 4.25, -0.38), (s * 1.12, 3.2, -0.42), 0.035, 0.035, eye_m, 5)]
        fl = slab("flipper", [(s * px, py) for px, py in leaf(1.9, 0.75)][:: s], 0.1, skin_m, None, (0, 0, -0.05), bev=0.03)
        fl.location = (s * 1.15, 2.0, -0.85)
        fl.rotation_euler = (0, math.radians(s * 30), math.radians(s * -25))
        parts.append(fl)
    parts += [cyl("blowhole", 0.14, 0.08, eye_m, 8, loc=(0, 2.9, 1.42)),
              tbox("dorsal", 0.12, 0.7, 0.35, skin_m, top_d=0.25, top_dy=-0.25, loc=(0, -1.4, 1.05), bev=0.04)]
    for x, y in ((0.4, 3.6), (-0.3, 3.8), (0.6, 3.2), (-0.55, 3.4), (0.1, 4.0)):
        parts.append(sphere("barnacle", 0.09, barn_m, 6, 4, loc=(x, y, 1.25 - abs(x) * 0.25 - (y - 3) * 0.2), scale=(1, 1, 0.6)))
    join("BodyMesh", parts, body)

    tail = empty("Tail", loc=(0, -3.0, 0.1), parent=body)
    flukes = empty("Flukes", loc=(0, -1.0, 0), parent=tail)
    join("TailMesh", [lathe("stock", [(0.5, 0), (0.32, -1.1)], skin_m, 12, rot=(90, 0, 0), smooth=50, cap_top=False, cap_bottom=False)], tail)
    fluke = []
    for s in (-1, 1):
        pts = [(0, 0.15), (s * 0.6, 0.05), (s * 1.3, -0.25), (s * 1.75, -0.7), (s * 1.5, -0.75), (s * 0.8, -0.55), (s * 0.2, -0.6), (0, -0.35)]
        if s < 0:
            pts.reverse()
        fluke.append(slab("fluke", pts, 0.12, skin_m, lambda x, y: 0.08 * abs(x), (0, 0, -0.06), bev=0.03))
    join("FlukesMesh", fluke, flukes)
    return root


def jellyfish():
    root = empty("Jellyfish")
    bell_m = mat("jelly_bell", 0xff7ad8, 0.2, 0, 0x8a1a6a, 1.5, alpha=0.75)
    core_m = mat("jelly_core", 0xffb8f0, 0.3, 0, 0xff7ad8, 3)
    tent_m = mat("jelly_tentacle", 0xff9ae8, 0.4, 0, 0xff5ad0, 1.2)

    bell = empty("Bell", loc=(0, 0, 1.5), parent=root)
    prof = [(0, 1.05), (0.25, 1.03), (0.48, 0.96), (0.66, 0.85), (0.8, 0.7), (0.9, 0.5), (0.96, 0.28), (0.98, 0.1), (0.9, 0.0), (0.8, 0.12), (0, 0.2)]
    parts = [lathe("bell", prof, bell_m, 20, smooth=60, cap_top=False, cap_bottom=False),
             sphere("core", 0.35, core_m, 12, 8, loc=(0, 0, 0.5), scale=(1, 1, 0.8))]
    for i in range(10):
        a = i / 10 * 2 * math.pi
        parts.append(sphere("frill", 0.12, bell_m, 8, 5, loc=(math.cos(a) * 0.9, math.sin(a) * 0.9, 0.02), scale=(1, 1, 0.5)))
    join("BellMesh", parts, bell)

    tent = empty("Tentacles", loc=(0, 0, 1.52), parent=root)
    tp = []
    for i in range(8):
        a = i / 8 * 2 * math.pi
        r0 = 0.6 if i % 2 else 0.3
        x0, y0 = math.cos(a) * r0, math.sin(a) * r0
        side = Vector((math.cos(a + 1.6), math.sin(a + 1.6), 0))
        pts = [Vector((x0, y0, -k * 0.2)) + side * 0.1 * math.sin(k * 0.9 + i) for k in range(9)]
        for k, (p, q) in enumerate(zip(pts, pts[1:])):
            rad = 0.06 * (1 - k / 9) + 0.015
            tp.append(limb("tentacle", p, q, rad, rad * 0.9, tent_m if i % 2 else core_m, 6))
    join("TentaclesMesh", tp, tent)
    return root


MODELS = {
    "rider": (rider, (1.0, 1.0, 0.45), {}),
    "car": (car, (1.4, 1.6, 0.9), {}),
    "ufo": (ufo, (1.0, 1.6, 0.7), {}),
    "turtle": (turtle, (1.3, 1.5, 0.8), {}),
    "pufferfish": (pufferfish, (0.9, 1.5, 0.45), {}),
    "whale": (whale, (1.6, 1.3, 0.55), {}),
    "jellyfish": (jellyfish, (1.0, 1.4, 0.35), {}),
    "city_van": (traffic.city_van, (1.4, 1.6, 0.8), {}),
    "city_bus": (traffic.city_bus, (1.5, 1.4, 0.7), {}),
    "moon_rover": (traffic.moon_rover, (1.4, 1.6, 0.9), {}),
    "moon_van": (traffic.moon_van, (1.4, 1.6, 0.8), {}),
    "moon_bus": (traffic.moon_bus, (1.5, 1.4, 0.7), {}),
    "boulder": (traffic.boulder, (1.2, 1.5, 0.6), {}),
    "sky_car": (traffic.sky_car, (1.4, 1.6, 0.9), {}),
    "sky_van": (traffic.sky_van, (1.4, 1.6, 0.8), {}),
    "sky_bus": (traffic.sky_bus, (1.5, 1.4, 0.7), {}),
    "pedestrian": (critters.pedestrian, (0.8, 1.5, 0.4), {}),
    "astronaut": (critters.astronaut, (0.8, 1.5, 0.4), {}),
    "alien": (critters.alien, (0.8, 1.5, 0.4), {}),
    "crab": (critters.crab, (0.8, 1.5, 0.6), {}),
    "anemone": (critters.anemone, (0.8, 1.5, 0.6), {}),
    "octopus": (critters.octopus, (0.8, 1.5, 0.5), {}),
    "seahorse": (critters.seahorse, (1.5, 0.8, 0.4), {}),
    "imp": (critters.imp, (0.8, 1.5, 0.4), {}),
    "goose": (critters.goose, (1.4, 1.2, 0.4), {}),
    "coin": (critters.coin, (0.6, 1.5, 0.3), {}),
    "outfit_moon": (critters.outfit_moon, (0.8, 1.5, 0.4), {}),
    "outfit_sea": (critters.outfit_sea, (0.8, 1.5, 0.4), {}),
    "outfit_lava": (critters.outfit_lava, (0.8, 1.5, 0.4), {}),
    "outfit_sky": (critters.outfit_sky, (0.8, 1.5, 0.4), {}),
}
SEA = dict(bg=0x062a4a, floor=0x1a5a6a)
LOOK = {
    **{k: SEA for k in ("turtle", "pufferfish", "whale", "jellyfish", "crab", "anemone", "octopus", "seahorse", "outfit_sea")},
    **{k: dict(bg=0x0a0a1a, floor=0x6a6a74) for k in ("moon_rover", "moon_van", "moon_bus", "astronaut", "alien", "outfit_moon")},
    **{k: dict(bg=0x2a0800, floor=0x3a1a10) for k in ("boulder", "imp", "outfit_lava")},
    **{k: dict(bg=0x6a9ad8, floor=0xa8c8f0) for k in ("sky_car", "sky_van", "sky_bus", "goose", "outfit_sky")},
}


def lineup(path, items, cam, size=1400, fill=1.05, **look):
    reset_scene()
    setup_render()
    group = empty("Lineup")
    for build, loc in items:
        ob = build()
        ob.location = loc
        ob.parent = group
    render_preview(group, path, cam, size=size, fill=fill, **look)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    names = [n for n in argv if n in MODELS] or list(MODELS)
    stats_path = os.path.join(OUT, "stats.txt")
    stats = dict(line.split(": ", 1) for line in open(stats_path).read().splitlines()) if os.path.exists(stats_path) else {}
    for name in names:
        build, cam, _ = MODELS[name]
        reset_scene()
        setup_render()
        root = build()
        glb = os.path.join(OUT, name + ".glb")
        export_glb(root, glb)
        stats[name] = f"{tri_count(root)} tris, {os.path.getsize(glb) // 1024} KB"
        look = LOOK.get(name, {})
        render_preview(root, os.path.join(OUT, name + ".png"), cam, **look)
    if "lineups" in argv or not argv:
        lineup(os.path.join(OUT, "lineup.png"),
               [(rider, (0, 0, 0.45)), (lambda: car(0xff4f6d), (2.6, -1.2, 0)), (ufo, (-3.1, -1.6, 0.4))],
               (0.15, 1.6, 0.55))
        lineup(os.path.join(OUT, "lineup_sea.png"),
               [(rider, (0, 2.5, 0.45)), (turtle, (2.8, 1.0, 0)), (pufferfish, (-3.0, 1.0, 0)),
                (whale, (0.5, -6.5, 0)), (jellyfish, (5.5, -1.5, 0.3))],
               (0.35, 1.5, 0.55), **SEA)
    open(stats_path, "w").write("".join(f"{k}: {v}\n" for k, v in stats.items()))
    print("".join(f"{k}: {v}\n" for k, v in stats.items()))


main()
