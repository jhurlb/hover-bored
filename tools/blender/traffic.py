"""Traffic for the city, moon, volcano and sky worlds.

Sizes match the hit boxes in index.html's makeVehicle/themedBody:
car 1.9 x 4 x 1.45, van 2.05 x 5.2 x 2.55, bus 2.55 x 10.5 x 3.35 (w x d x h).
Materials named *_body / *_acc / *_stripe are recoloured per vehicle in the game.
"""
import math
import random

from mathutils import Vector

from lib import cyl, empty, join, lathe, mat, slab, sphere, tbox, torus

PINK, CYAN = 0xff3fa4, 0x3ff3ff


def _glass():
    return mat("car_glass", 0x0c0820, 0.06, 0.9, 0x0a1030, 1)


def _wheel(name, parent, loc, r, w, tire, rim, hub=None, segs=16):
    wh = empty(name, loc=loc, parent=parent)
    parts = [cyl("tire", r, w, tire, segs, rot=(0, 90, 0), bev=min(0.06, r * 0.18)),
             cyl("rim", r * 0.62, w + 0.02, rim, 10, rot=(0, 90, 0))]
    if hub:
        parts.append(cyl("hub", r * 0.22, w + 0.04, hub, 8, rot=(0, 90, 0)))
    join(name + "Mesh", parts, wh)


def city_van():
    root = empty("CityVan")
    body = mat("van_body", 0xf6eeff, 0.4, 0.35)
    stripe = mat("van_stripe", CYAN, 0.3, 0, CYAN, 3)
    trim = mat("car_trim", 0x1a1a2a, 0.5, 0.4)
    glass = _glass()
    head_l = mat("headlight", 0xfff2c0, 0.2, 0, 0xfff2c0, 6)
    tail_l = mat("taillight", 0xff2244, 0.2, 0, 0xff2244, 5)
    parts = [tbox("box", 2.05, 3.7, 2.1, body, top_w=2.0, top_d=3.66, loc=(0, -0.7, 0.36), bev=0.12, segs=3),
             tbox("cab", 2.0, 1.55, 1.15, body, top_w=1.9, top_d=1.0, top_dy=-0.25, loc=(0, 1.8, 0.36), bev=0.14, segs=3),
             tbox("windshield", 1.84, 0.5, 0.62, glass, top_w=1.74, top_d=0.12, top_dy=-0.22, loc=(0, 2.05, 1.0), bev=0.05),
             tbox("stripe", 2.09, 3.4, 0.34, stripe, loc=(0, -0.7, 1.3), bev=0.02),
             tbox("bumper_f", 2.08, 0.25, 0.3, trim, loc=(0, 2.52, 0.28), bev=0.08),
             tbox("bumper_r", 2.08, 0.25, 0.3, trim, loc=(0, -2.55, 0.28), bev=0.08),
             tbox("door_line", 2.08, 0.03, 1.6, trim, loc=(0, -2.0, 0.55), bev=0),
             tbox("roof_rack", 1.6, 2.8, 0.08, trim, loc=(0, -0.7, 2.47), bev=0.02),
             tbox("taillights", 1.8, 0.05, 0.16, tail_l, loc=(0, -2.57, 0.75), bev=0.02)]
    for s in (-1, 1):
        parts += [tbox("headlight", 0.42, 0.06, 0.16, head_l, loc=(s * 0.66, 2.58, 0.62), bev=0.03),
                  tbox("side_window", 0.04, 0.8, 0.5, glass, loc=(s * 1.0, 1.55, 1.0), bev=0.02),
                  tbox("mirror", 0.18, 0.1, 0.2, trim, loc=(s * 1.12, 2.0, 1.1), bev=0.03)]
        for y in (-1.8, 1.7):
            parts.append(tbox("arch", 0.12, 0.95, 0.4, trim, top_d=0.75, loc=(s * 1.0, y, 0.42), bev=0.04))
    join("Body", parts, root)
    tire, rim = mat("tire", 0x0b0910, 0.9, 0.1), mat("rim", 0xc8ccd8, 0.25, 0.9)
    for sx in (-1, 1):
        for sy, n in ((1, "F"), (-1, "R")):
            _wheel(f"Wheel{n}{'L' if sx < 0 else 'R'}", root, (sx * 0.93, 1.7 if sy > 0 else -1.8, 0.38), 0.38, 0.28, tire, rim)
    return root


def city_bus():
    root = empty("CityBus")
    body = mat("bus_body", 0x18c8b0, 0.35, 0.45)
    white = mat("bus_white", 0xf6eeff, 0.4, 0.2)
    trim = mat("car_trim", 0x1a1a2a, 0.5, 0.4)
    glass = _glass()
    sign = mat("bus_sign", 0xffa020, 0.3, 0, 0xffa020, 5)
    head_l = mat("headlight", 0xfff2c0, 0.2, 0, 0xfff2c0, 6)
    tail_l = mat("taillight", 0xff2244, 0.2, 0, 0xff2244, 5)
    parts = [tbox("hull", 2.55, 10.5, 2.95, body, top_w=2.45, top_d=10.3, loc=(0, 0, 0.42), bev=0.18, segs=3),
             tbox("windows", 2.59, 9.3, 0.95, glass, loc=(0, -0.2, 1.85), bev=0.05),
             tbox("windshield", 2.3, 0.08, 1.3, glass, loc=(0, 5.23, 1.6), bev=0.03),
             tbox("belt", 2.6, 10.4, 0.16, white, loc=(0, 0, 1.32), bev=0.03),
             tbox("skirt", 2.58, 10.45, 0.3, trim, loc=(0, 0, 0.35), bev=0.06),
             tbox("ac_unit", 1.4, 2.4, 0.35, white, top_w=1.2, top_d=2.1, loc=(0, -1.0, 3.35), bev=0.08),
             tbox("sign", 1.7, 0.06, 0.36, sign, loc=(0, 5.24, 2.88), bev=0.02),
             tbox("tail", 1.9, 0.06, 0.2, tail_l, loc=(0, -5.26, 0.95), bev=0.02),
             tbox("bumper_f", 2.58, 0.22, 0.32, trim, loc=(0, 5.25, 0.3), bev=0.08),
             tbox("bumper_r", 2.58, 0.22, 0.32, trim, loc=(0, -5.25, 0.3), bev=0.08)]
    for s in (-1, 1):
        parts.append(tbox("headlight", 0.4, 0.06, 0.2, head_l, loc=(s * 0.85, 5.27, 0.7), bev=0.03))
        for y in (-3.4, 3.6):
            parts.append(tbox("arch", 0.12, 1.25, 0.5, trim, top_d=1.0, loc=(s * 1.25, y, 0.4), bev=0.05))
        for k in range(6):
            parts.append(tbox("pillar", 2.62, 0.1, 0.95, body, loc=(0, -4.5 + k * 1.6, 1.85), bev=0))
    join("Body", parts, root)
    tire, rim = mat("tire", 0x0b0910, 0.9, 0.1), mat("rim", 0xc8ccd8, 0.25, 0.9)
    for sx in (-1, 1):
        for y, n in ((3.6, "F"), (-3.4, "R")):
            _wheel(f"Wheel{n}{'L' if sx < 0 else 'R'}", root, (sx * 1.18, y, 0.48), 0.48, 0.32, tire, rim)
    return root


def _moon_mats():
    return (mat("moon_white", 0xd8dce6, 0.5, 0.35), mat("moon_gold", 0xffb820, 0.25, 0.95, 0x402800, 1),
            mat("moon_dark", 0x2a2a34, 0.8, 0.2), mat("moon_panel", 0x1a2a78, 0.2, 0.85, 0x050a30, 1),
            mat("moon_acc", 0x5ad1ff, 0.4, 0.4))


def _wire_wheel(name, parent, loc, r, w, dark, acc):
    wh = empty(name, loc=loc, parent=parent)
    parts = [torus("tread", r - 0.07, 0.08, dark, 16, 6, rot=(0, 90, 0)),
             cyl("hub", r * 0.3, w, acc, 8, rot=(0, 90, 0))]
    for k in range(6):
        a = k / 6 * math.pi
        parts.append(tbox("spoke", 0.04, (r - 0.1) * 2, 0.04, dark, loc=(0, 0, -0.02), rot=(math.degrees(a), 0, 0), bev=0))
    join(name + "Mesh", parts, wh)


def moon_rover():
    root = empty("MoonRover")
    white, gold, dark, panel, acc = _moon_mats()
    parts = [tbox("chassis", 1.9, 4.0, 0.3, white, loc=(0, 0, 0.55), bev=0.06),
             tbox("trim", 1.92, 4.02, 0.1, acc, loc=(0, 0, 0.8), bev=0.02),
             tbox("seat", 0.8, 0.6, 0.35, acc, loc=(-0.35, 0.3, 0.85), bev=0.06),
             tbox("seat_back", 0.8, 0.12, 0.55, acc, loc=(-0.35, -0.02, 0.9), bev=0.04),
             tbox("seat2", 0.8, 0.6, 0.35, acc, loc=(0.4, 0.3, 0.85), bev=0.06),
             tbox("seat2_back", 0.8, 0.12, 0.55, acc, loc=(0.4, -0.02, 0.9), bev=0.04),
             tbox("console", 1.2, 0.4, 0.4, gold, top_d=0.25, loc=(0, 1.35, 0.85), bev=0.05),
             tbox("cargo", 1.6, 1.1, 0.45, gold, loc=(0, -1.45, 0.85), bev=0.06),
             tbox("solar", 1.8, 2.4, 0.06, panel, loc=(0, -0.2, 1.4), bev=0.02),
             limb_post(-0.8, 1.7, dark), cyl("dish_mast", 0.03, 0.9, dark, 6, loc=(0.75, -1.6, 1.7)),
             lathe("dish", [(0, 0), (0.22, 0.05), (0.4, 0.17)], white, 12, loc=(0.75, -1.6, 2.15), rot=(-30, 0, 0),
                   cap_top=False, cap_bottom=False)]
    for x in (-0.85, 0.85):
        for y in (-1.1, 1.1):
            parts.append(cyl("post", 0.04, 0.6, dark, 6, loc=(x, y, 1.1)))
    join("Body", parts, root)
    for sx in (-1, 1):
        for y, n in ((1.3, "F"), (-1.3, "R")):
            _wire_wheel(f"Wheel{n}{'L' if sx < 0 else 'R'}", root, (sx * 1.02, y, 0.42), 0.42, 0.3, dark, acc)
    return root


def limb_post(x, y, m):
    return cyl("antenna", 0.025, 1.2, m, 6, loc=(x, y, 1.6))


def moon_van():
    root = empty("MoonVan")
    white, gold, dark, panel, acc = _moon_mats()
    glass = _glass()
    parts = [tbox("hab", 2.05, 4.8, 1.9, white, top_w=1.9, top_d=4.6, loc=(0, 0, 0.6), bev=0.3, segs=3),
             tbox("foil", 1.75, 4.0, 0.12, gold, loc=(0, 0, 2.48), bev=0.04),
             tbox("window", 1.8, 0.3, 0.5, glass, top_d=0.1, loc=(0, 2.35, 1.6), bev=0.05),
             tbox("band", 2.08, 4.7, 0.12, acc, loc=(0, 0, 0.9), bev=0.03),
             cyl("hatch", 0.45, 0.06, dark, 12, loc=(0, -2.42, 1.5), rot=(90, 0, 0)),
             cyl("hatch_ring", 0.5, 0.04, gold, 12, loc=(0, -2.4, 1.5), rot=(90, 0, 0))]
    for s in (-1, 1):
        parts += [tbox("panel", 0.08, 1.6, 1.0, panel, loc=(s * 1.15, 0.6, 1.1), bev=0.02),
                  tbox("panel_arm", 0.2, 0.08, 0.08, dark, loc=(s * 1.06, 0.6, 1.6), bev=0)]
        for y in (-1.8, 0, 1.8):
            parts.append(tbox("strut", 0.15, 0.2, 0.5, dark, loc=(s * 0.85, y, 0.35), bev=0.02))
    join("Body", parts, root)
    for sx in (-1, 1):
        for y, n in ((1.8, "F"), (0.0, "M"), (-1.8, "R")):
            _wire_wheel(f"Wheel{n}{'L' if sx < 0 else 'R'}", root, (sx * 0.98, y, 0.35), 0.36, 0.28, dark, acc)
    return root


def moon_bus():
    root = empty("MoonBus")
    white, gold, dark, panel, acc = _moon_mats()
    glass = _glass()
    parts = [lathe("hab", [(0, -5.1), (0.8, -5.05), (1.15, -4.7), (1.22, -4.0), (1.22, 4.0), (1.15, 4.7), (0.8, 5.05), (0, 5.12)],
                   white, 16, loc=(0, 0, 1.75), rot=(-90, 0, 0), scale=(1.04, 1, 1.0), smooth=40),
             torus("ring_f", 1.24, 0.08, acc, 20, 5, loc=(0, 3.0, 1.75), rot=(90, 0, 0)),
             torus("ring_m", 1.24, 0.08, acc, 20, 5, loc=(0, 0, 1.75), rot=(90, 0, 0)),
             torus("ring_r", 1.24, 0.08, acc, 20, 5, loc=(0, -3.0, 1.75), rot=(90, 0, 0)),
             tbox("windows", 2.6, 7.5, 0.5, glass, loc=(0, 0.2, 1.75), bev=0.1),
             sphere("cockpit", 0.9, glass, 14, 8, loc=(0, 4.55, 1.9), scale=(1.0, 0.7, 0.6)),
             tbox("chassis", 2.0, 9.2, 0.35, dark, loc=(0, 0, 0.45), bev=0.08),
             tbox("solar", 1.6, 3.0, 0.06, panel, loc=(0, -1.5, 3.05), bev=0.02),
             cyl("mast", 0.05, 1.2, dark, 6, loc=(0.8, -4.0, 3.4)),
             sphere("beacon", 0.1, mat("beacon", 0xff3344, 0.3, 0, 0xff3344, 6), 8, 5, loc=(0.8, -4.0, 4.05))]
    join("Body", parts, root)
    for sx in (-1, 1):
        for i, y in enumerate((-3.8, -1.3, 1.3, 3.8)):
            _wire_wheel(f"Wheel{i}{'L' if sx < 0 else 'R'}", root, (sx * 1.15, y, 0.45), 0.45, 0.35, dark, acc)
    return root


def boulder():
    """Unit-radius lava boulder, scaled per vehicle size in the game; Roll is the node it spins."""
    import bmesh
    from lib import _obj
    root = empty("Boulder")
    roll = empty("Roll", loc=(0, 0, 1.0), parent=root)
    rock_m = mat("rock", 0x3a2a2a, 0.9, 0.1, 0x2a0800, 1)
    lava = mat("lava_glow", 0xff7a20, 0.3, 0, 0xff6a10, 8)
    rng = random.Random(7)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    for v in bm.verts:
        n = v.co.normalized()
        bump = 0.82 + 0.1 * math.sin(n.x * 5.1 + 1) * math.cos(n.y * 4.3) + 0.08 * math.sin(n.z * 6.7 + 2) + rng.uniform(-0.04, 0.04)
        v.co = n * bump
    for f in bm.faces:
        c = f.calc_center_median().normalized()
        vein = math.sin(c.x * 7 + c.y * 3) * math.cos(c.z * 6 - c.x * 2)
        f.material_index = 1 if vein > 0.55 or rng.random() < 0.06 else 0
    rock = _obj("rock", bm, rock_m, None, None)
    rock.data.materials.append(lava)
    parts = [rock]
    join("RockMesh", parts, roll)
    return root


def _sky_mats():
    return (mat("sky_body", 0x8ad8ff, 0.35, 0.4), mat("sky_wing", 0xf0e8ff, 0.4, 0.3),
            mat("sky_dark", 0x4a4478, 0.5, 0.5), mat("sky_jet", 0xff8ad0, 0.3, 0, 0xff8ad0, 6))


def _jet(parts, x, y, z, r, dark, jet):
    parts.append(cyl("jet", r, r * 2.2, dark, 12, loc=(x, y, z), rot=(90, 0, 0), r2=r * 0.8, bev=0.03))
    parts.append(cyl("jet_glow", r * 0.75, 0.03, jet, 12, loc=(x, y - r * 1.12, z), rot=(90, 0, 0)))


def sky_car():
    root = empty("SkyCar")
    body, wing, dark, jet = _sky_mats()
    glass = _glass()
    parts = [lathe("hull", [(0, -2.0), (0.45, -1.95), (0.8, -1.5), (0.95, -0.5), (0.95, 0.8), (0.75, 1.6), (0.35, 1.98), (0, 2.02)],
                   body, 16, loc=(0, 0, 0.75), rot=(-90, 0, 0), scale=(1.0, 1.0, 0.55), smooth=45),
             sphere("canopy", 0.75, glass, 14, 8, loc=(0, 0.15, 1.05), scale=(0.95, 1.5, 0.75)),
             tbox("fin", 0.08, 0.8, 0.6, wing, top_d=0.35, top_dy=-0.25, loc=(0, -1.55, 1.0), bev=0.03)]
    for s in (-1, 1):
        w = slab("wing", [(0, 0.55), (s * 1.45, 0.1), (s * 1.55, -0.4), (0, -0.5)][:: s], 0.09, wing, None, (s * 0.8, 0.2, 0.62), bev=0.03)
        parts.append(w)
        parts.append(tbox("wing_tip", 0.06, 0.55, 0.06, jet, loc=(s * 2.3, 0.0, 0.62), bev=0))
        _jet(parts, s * 0.55, -1.65, 0.6, 0.22, dark, jet)
    parts.append(tbox("nose_light", 0.9, 0.05, 0.08, mat("headlight", 0xfff2c0, 0.2, 0, 0xfff2c0, 6), loc=(0, 1.92, 0.72), bev=0))
    join("Body", parts, root)
    return root


def sky_van():
    root = empty("SkyVan")
    body, wing, dark, jet = _sky_mats()
    glass = _glass()
    parts = [tbox("hull", 2.05, 4.8, 1.8, body, top_w=1.85, top_d=4.4, top_dy=-0.15, loc=(0, 0, 0.6), bev=0.4, segs=3),
             tbox("windshield", 1.7, 0.4, 0.55, glass, top_d=0.1, top_dy=-0.2, loc=(0, 2.1, 1.55), bev=0.08),
             tbox("roof_fin", 0.1, 1.2, 0.55, wing, top_d=0.5, top_dy=-0.3, loc=(0, -1.7, 2.35), bev=0.03),
             tbox("belly", 1.6, 4.0, 0.2, dark, loc=(0, 0, 0.45), bev=0.06),
             tbox("stripe", 2.08, 4.2, 0.12, jet, loc=(0, 0, 1.2), bev=0.02)]
    for s in (-1, 1):
        parts.append(slab("wing", [(0, 0.8), (s * 0.95, 0.3), (s * 1.0, -0.5), (0, -0.8)][:: s], 0.1, wing, None, (s * 1.0, 0.4, 1.15), bev=0.03))
        _jet(parts, s * 0.6, -2.45, 0.9, 0.26, dark, jet)
    join("Body", parts, root)
    return root


def sky_bus():
    root = empty("SkyBus")
    body, wing, dark, jet = _sky_mats()
    glass = _glass()
    parts = [lathe("hull", [(0, -5.25), (0.6, -5.15), (1.15, -4.4), (1.3, -2.5), (1.3, 3.2), (1.15, 4.6), (0.7, 5.15), (0, 5.25)],
                   body, 18, loc=(0, 0, 1.85), rot=(-90, 0, 0), scale=(0.98, 1.0, 1.1), smooth=45),
             tbox("windows", 2.6, 8.0, 0.55, glass, loc=(0, 0.3, 2.05), bev=0.12),
             sphere("cockpit", 0.95, glass, 14, 8, loc=(0, 4.45, 2.15), scale=(1.0, 0.75, 0.55)),
             tbox("top_wing", 1.9, 8.5, 0.12, wing, loc=(0, 0, 3.22), bev=0.05),
             tbox("tail_fin", 0.12, 1.6, 1.0, wing, top_d=0.7, top_dy=-0.4, loc=(0, -4.4, 3.0), bev=0.04)]
    for s in (-1, 1):
        parts.append(slab("wing", [(0, 1.3), (s * 1.4, 0.6), (s * 1.45, -0.7), (0, -1.2)][:: s], 0.12, wing, None, (s * 1.2, 0.0, 1.5), bev=0.04))
        for y in (-4.0, 3.2):
            _jet(parts, s * 0.9, y, 0.7, 0.32, dark, jet)
    join("Body", parts, root)
    return root
