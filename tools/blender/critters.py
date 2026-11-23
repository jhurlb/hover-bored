"""Road-crossing pedestrians and critters, rider outfits, and the coin.

Walkers expose LegL/LegR/ArmL/ArmR nodes pivoting at hip/shoulder, hanging down,
which the game's walkAnim swings about X. Materials named ped_* are recoloured per
pedestrian in the game.
"""
import math

from mathutils import Vector

from lib import cyl, empty, join, lathe, limb, mat, slab, sphere, tbox, torus

PINK, CYAN = 0xff3fa4, 0x3ff3ff


def _eyes(parts, x, y, z, r, white=True, look=0.0):
    w, b = mat("eye_white", 0xffffff, 0.3), mat("eye_black", 0x050505, 0.1, 0.2)
    for s in (-1, 1):
        if white:
            parts.append(sphere("eye", r, w, 10, 6, loc=(s * x, y, z)))
            parts.append(sphere("pupil", r * 0.55, b, 8, 5, loc=(s * (x + look), y + r * 0.62, z)))
        else:
            parts.append(sphere("eye", r, b, 8, 5, loc=(s * x, y, z), scale=(1, 0.5, 1.3)))


def _walker_limbs(root, legs, arms, leg_len, arm_len, leg_r, arm_r, leg_m, arm_m, foot_m=None, hand_m=None):
    for name, (x, z) in (("LegL", (-legs[0], legs[1])), ("LegR", (legs[0], legs[1]))):
        n = empty(name, loc=(x, 0, z), parent=root)
        p = [limb("leg", (0, 0, 0), (0, 0.02, -leg_len + leg_r), leg_r, leg_r * 0.9, leg_m, 8)]
        if foot_m:
            p.append(tbox("foot", leg_r * 2.3, leg_r * 3.4, leg_r * 1.2, foot_m, top_d=leg_r * 2.4, loc=(0, leg_r * 0.6, -leg_len), bev=leg_r * 0.4))
        join(name + "Mesh", p, n)
    for name, (x, z) in (("ArmL", (-arms[0], arms[1])), ("ArmR", (arms[0], arms[1]))):
        n = empty(name, loc=(x, 0, z), parent=root)
        p = [limb("arm", (0, 0, 0), (0, 0.04, -arm_len + arm_r), arm_r, arm_r * 0.85, arm_m, 8)]
        if hand_m:
            p.append(sphere("hand", arm_r * 1.1, hand_m, 8, 5, loc=(0, 0.05, -arm_len)))
        join(name + "Mesh", p, n)


def pedestrian():
    root = empty("Pedestrian")
    top, pants = mat("ped_top", 0xff3fa4, 0.7), mat("ped_pants", 0x24305e, 0.8)
    skin, hair = mat("ped_skin", 0xc98a5a, 0.6), mat("ped_hair", 0x2a1a10, 0.8)
    shoe = mat("ped_shoe", 0xf6eeff, 0.5)
    parts = [tbox("hips", 0.44, 0.26, 0.2, pants, loc=(0, 0, 0.74), bev=0.05),
             tbox("torso", 0.46, 0.28, 0.62, top, top_w=0.52, top_d=0.3, loc=(0, 0, 0.86), bev=0.09, segs=3),
             limb("neck", (0, 0, 1.45), (0, 0, 1.52), 0.07, 0.07, skin, 6),
             sphere("head", 0.2, skin, 12, 8, loc=(0, 0, 1.68), scale=(1, 1, 1.08)),
             lathe("hair", [(0.215 * math.sin(math.radians(d)), 0.215 * math.cos(math.radians(d))) for d in (105, 80, 50, 25, 0)],
                   hair, 12, loc=(0, -0.015, 1.7), rot=(-15, 0, 0), cap_bottom=False, cap_top=False)]
    _eyes(parts, 0.07, 0.17, 1.7, 0.03, white=False)
    join("Body", parts, root)
    _walker_limbs(root, (0.12, 0.8), (0.31, 1.42), 0.78, 0.56, 0.085, 0.065, pants, top, shoe, skin)
    return root


def astronaut():
    root = empty("Astronaut")
    suit, packm = mat("suit", 0xe8eaf2, 0.55), mat("suit_pack", 0xb8bcc8, 0.5, 0.3)
    visor = mat("visor_gold", 0xffb020, 0.1, 1.0, 0x402000, 1)
    acc = mat("suit_acc", 0xff5a3a, 0.5)
    parts = [tbox("torso", 0.56, 0.4, 0.7, suit, top_w=0.6, loc=(0, 0, 0.82), bev=0.12, segs=3),
             tbox("pack", 0.48, 0.3, 0.62, packm, loc=(0, -0.33, 0.88), bev=0.07),
             tbox("chest", 0.3, 0.05, 0.2, acc, loc=(0, 0.21, 1.15), bev=0.02),
             torus("collar", 0.24, 0.06, packm, 14, 5, loc=(0, 0, 1.53)),
             sphere("helmet", 0.36, suit, 14, 10, loc=(0, 0, 1.8)),
             sphere("visor", 0.3, visor, 12, 8, loc=(0, 0.2, 1.82), scale=(0.85, 0.6, 0.68)),
             cyl("antenna", 0.02, 0.35, packm, 5, loc=(0.18, -0.4, 1.35)),
             sphere("tip", 0.05, mat("beacon", 0xff3344, 0.3, 0, 0xff3344, 6), 6, 4, loc=(0.18, -0.4, 1.55))]
    join("Body", parts, root)
    _walker_limbs(root, (0.14, 0.82), (0.37, 1.45), 0.8, 0.6, 0.12, 0.095, suit, suit, packm, packm)
    return root


def alien():
    root = empty("Alien")
    skin = mat("alien", 0x6aff6a, 0.5, 0, 0x1a5a1a, 0.6)
    tipm = mat("ufo_core", 0x7affb0, 0.3, 0, 0x7affb0, 6)
    parts = [lathe("body", [(0, 0.5), (0.2, 0.52), (0.24, 0.7), (0.2, 0.95), (0.1, 1.05), (0, 1.06)], skin, 12),
             sphere("head", 0.34, skin, 14, 10, loc=(0, 0, 1.32), scale=(1.25, 1, 1))]
    _eyes(parts, 0.15, 0.27, 1.36, 0.11, white=False)
    for s in (-1, 1):
        parts += [limb("antenna", (s * 0.12, 0, 1.6), (s * 0.18, -0.02, 1.9), 0.025, 0.02, skin, 5),
                  sphere("tip", 0.06, tipm, 8, 5, loc=(s * 0.185, -0.02, 1.93))]
    join("Body", parts, root)
    _walker_limbs(root, (0.12, 0.55), (0.26, 1.0), 0.55, 0.48, 0.07, 0.05, skin, skin, skin, skin)
    return root


def imp():
    root = empty("LavaImp")
    skin, horn = mat("imp", 0xd8301a, 0.6, 0, 0x601008, 1), mat("horn", 0x2a1a14, 0.5)
    glow = mat("imp_eye", 0xffd060, 0.3, 0, 0xffd060, 8)
    flame = mat("lava_glow", 0xff7a20, 0.3, 0, 0xff6a10, 8)
    parts = [sphere("body", 0.32, skin, 12, 8, loc=(0, 0, 0.98), scale=(0.95, 0.8, 1.05)),
             sphere("head", 0.26, skin, 12, 8, loc=(0, 0.03, 1.45), scale=(1.05, 1.0, 0.95)),
             tbox("grin", 0.22, 0.03, 0.04, horn, loc=(0, 0.27, 1.33), bev=0),
             limb("tail", (0, -0.25, 0.75), (0, -0.6, 0.6), 0.05, 0.03, skin, 5),
             sphere("tail_tip", 0.07, flame, 6, 4, loc=(0, -0.63, 0.6), scale=(1, 1, 1.5)),
             sphere("flame", 0.13, flame, 8, 5, loc=(0, -0.02, 1.76), scale=(1, 1, 1.6))]
    for s in (-1, 1):
        parts += [limb("horn", (s * 0.14, 0, 1.64), (s * 0.24, -0.04, 1.86), 0.05, 0.015, horn, 6),
                  sphere("eye", 0.055, glow, 8, 5, loc=(s * 0.1, 0.22, 1.5), scale=(1, 0.5, 0.8))]
    join("Body", parts, root)
    _walker_limbs(root, (0.13, 0.66), (0.32, 1.18), 0.62, 0.48, 0.085, 0.065, skin, skin, horn, skin)
    return root


def goose():
    root = empty("Goose")
    fea, beak = mat("goose", 0xf4f0ea, 0.7), mat("beak", 0xff9a20, 0.5)
    parts = [sphere("body", 1.0, fea, 14, 9, loc=(0, -0.05, 0.88), scale=(0.38, 0.62, 0.36)),
             tbox("tail", 0.3, 0.25, 0.12, fea, top_w=0.1, loc=(0, -0.68, 0.95), rot=(20, 0, 0), bev=0.04),
             limb("neck", (0, 0.42, 1.05), (0, 0.52, 1.55), 0.09, 0.075, fea, 8),
             sphere("head", 0.13, fea, 10, 7, loc=(0, 0.55, 1.62), scale=(0.9, 1.2, 0.9)),
             tbox("beak", 0.1, 0.2, 0.07, beak, top_w=0.06, top_d=0.16, loc=(0, 0.74, 1.56), bev=0.02)]
    _eyes(parts, 0.08, 0.6, 1.66, 0.025, white=False)
    join("Body", parts, root)
    for name, x in (("LegL", -0.12), ("LegR", 0.12)):
        n = empty(name, loc=(x, 0, 0.6), parent=root)
        join(name + "Mesh", [limb("leg", (0, 0, 0), (0, 0, -0.55), 0.035, 0.03, beak, 5),
                             tbox("foot", 0.16, 0.2, 0.03, beak, top_w=0.04, top_d=0.04, top_dy=-0.08, loc=(0, 0.06, -0.6), bev=0)], n)
    for name, s in (("ArmL", -1), ("ArmR", 1)):
        n = empty(name, loc=(s * 0.34, 0, 0.98), parent=root)
        join(name + "Mesh", [sphere("wing", 1.0, fea, 10, 6, loc=(s * 0.02, -0.05, -0.05), scale=(0.07, 0.42, 0.2))], n)
    return root


def crab():
    root = empty("Crab")
    shell, leg = mat("crab", 0xff5a3a, 0.5, 0, 0x401008, 1), mat("crab_leg", 0xd8401a, 0.6)
    parts = [sphere("shell", 1.0, shell, 16, 9, loc=(0, 0, 0.95), scale=(0.78, 0.55, 0.38))]
    for s in (-1, 1):
        parts += [limb("stalk", (s * 0.16, 0.38, 1.18), (s * 0.18, 0.4, 1.48), 0.03, 0.03, leg, 5)]
    _eyes(parts, 0.18, 0.36, 1.53, 0.07)
    parts.append(tbox("mouth", 0.2, 0.03, 0.03, mat("eye_black", 0x050505, 0.1, 0.2), loc=(0, 0.54, 0.92), bev=0))
    join("Body", parts, root)
    for name, s in (("LegL", -1), ("LegR", 1)):
        n = empty(name, loc=(s * 0.55, 0, 0.95), parent=root)
        legs = []
        for k in range(3):
            y = (1 - k) * 0.28
            knee = (s * 0.4, y, 0.1)
            legs += [limb("upper", (0, y, 0), knee, 0.045, 0.04, leg, 5),
                     limb("lower", knee, (s * 0.62, y, -0.9), 0.04, 0.02, leg, 5)]
        join(name + "Mesh", legs, n)
    for name, s in (("ArmL", -1), ("ArmR", 1)):
        n = empty(name, loc=(s * 0.5, 0.35, 1.05), parent=root)
        join(name + "Mesh", [limb("claw_arm", (0, 0, 0), (s * 0.15, 0.2, 0), 0.06, 0.06, leg, 6),
                             sphere("claw", 0.2, shell, 10, 7, loc=(s * 0.2, 0.36, 0.02), scale=(0.8, 1.2, 0.7)),
                             tbox("pincer", 0.1, 0.24, 0.08, shell, top_d=0.08, loc=(s * 0.26, 0.55, 0.08), bev=0.03),
                             tbox("pincer", 0.1, 0.22, 0.07, shell, top_d=0.07, loc=(s * 0.14, 0.53, -0.04), bev=0.03)], n)
    return root


def anemone():
    root = empty("Anemone")
    stalk = mat("anemone", 0xff5a9a, 0.5, 0, 0x3f1a26, 1)
    tip = mat("anemone_tip", 0xfff0f8, 0.4, 0, 0x7f2a4a, 1)
    join("Body", [lathe("stalk", [(0.44, 0), (0.4, 0.15), (0.34, 0.5), (0.4, 0.68), (0.56, 0.76), (0.5, 0.8), (0, 0.78)], stalk, 16),
                  sphere("mouth", 0.12, mat("anemone_mouth", 0x7a1a3a, 0.5), 8, 5, loc=(0, 0, 0.78), scale=(1, 1, 0.3))], root)
    for name, odd in (("ArmL", 0), ("ArmR", 1)):
        n = empty(name, loc=(0, 0, 0.76), parent=root)
        ts = []
        for k in range(12):
            if k % 2 != odd:
                continue
            a = k / 12 * 2 * math.pi
            base = Vector((math.cos(a) * 0.4, math.sin(a) * 0.4, 0))
            out = Vector((math.cos(a) * 0.55, math.sin(a) * 0.55, 1)).normalized()
            mid = base + out * 0.36
            end = mid + (out + Vector((0, 0, 0.6))).normalized() * 0.3
            ts += [limb("tent", base, mid, 0.06, 0.05, stalk, 6), limb("tent", mid, end, 0.05, 0.035, stalk, 6),
                   sphere("tip", 0.055, tip, 6, 4, loc=end)]
        join(name + "Mesh", ts, n)
    return root


def octopus():
    root = empty("Octopus")
    skin = mat("octopus", 0xb44aff, 0.5, 0, 0x2f122f, 1)
    spots = mat("octopus_spot", 0xe0a0ff, 0.5)
    parts = [sphere("head", 1.0, skin, 14, 10, loc=(0, -0.05, 1.2), scale=(0.5, 0.55, 0.62)),
             tbox("smile", 0.16, 0.03, 0.03, mat("eye_black", 0x050505, 0.1, 0.2), loc=(0, 0.46, 0.92), bev=0)]
    for x, z in ((0.25, 1.5), (-0.2, 1.6), (0.05, 1.7), (-0.3, 1.35)):
        parts.append(sphere("spot", 0.06, spots, 6, 4, loc=(x, -0.15, z), scale=(1, 0.4, 1)))
    _eyes(parts, 0.2, 0.36, 1.08, 0.1)
    join("Body", parts, root)
    for gi, name in enumerate(("LegL", "LegR", "ArmL", "ArmR")):
        n = empty(name, loc=(0, 0, 0.72), parent=root)
        ts = []
        for j in range(2):
            a = (gi * 2 + j) / 8 * 2 * math.pi
            d = Vector((math.cos(a), math.sin(a), 0))
            p0 = d * 0.3 + Vector((0, 0, 0.1))
            p1 = d * 0.5 + Vector((0, 0, -0.3))
            p2 = d * 0.72 + Vector((0, 0, -0.62))
            p3 = d * 0.95 + Vector((0, 0, -0.6))
            ts += [limb("t", p0, p1, 0.11, 0.08, skin, 7), limb("t", p1, p2, 0.08, 0.055, skin, 7),
                   limb("t", p2, p3, 0.055, 0.03, skin, 6)]
        join(name + "Mesh", ts, n)
    return root


def seahorse():
    root = empty("Seahorse")
    skin = mat("seahorse", 0xffd23f, 0.5, 0, 0x3f3410, 1)
    belly = mat("seahorse_belly", 0xfff0c0, 0.5)
    fl = empty("Float", parent=root)
    spine = [(0, 0.0, 1.45), (0, -0.02, 1.15), (0, 0.06, 0.85), (0, 0.16, 0.6), (0, 0.12, 0.38), (0, -0.02, 0.24),
             (0, -0.12, 0.3), (0, -0.1, 0.42)]
    radii = [0.2, 0.22, 0.2, 0.16, 0.12, 0.08, 0.06, 0.04]
    parts = []
    for (a, b), ra, rb in zip(zip(spine, spine[1:]), radii, radii[1:]):
        parts.append(limb("seg", a, b, ra, rb, skin, 10))
    for z, y in ((1.25, 0.15), (1.0, 0.16), (0.78, 0.22)):
        parts.append(sphere("belly", 0.13, belly, 8, 5, loc=(0, y, z), scale=(1, 0.5, 1)))
    parts += [sphere("head", 0.2, skin, 12, 8, loc=(0, 0.05, 1.55), scale=(0.9, 1.1, 0.95)),
              limb("snout", (0, 0.18, 1.52), (0, 0.48, 1.47), 0.07, 0.05, skin, 8),
              tbox("crest", 0.05, 0.18, 0.2, skin, top_d=0.06, loc=(0, -0.05, 1.68), bev=0.02)]
    for k in range(4):
        parts.append(tbox("ridge", 0.04, 0.08, 0.1, skin, loc=(0, -0.2 + k * 0.01, 1.35 - k * 0.22), bev=0.01))
    _eyes(parts, 0.13, 0.1, 1.6, 0.06)
    join("BodyMesh", parts, fl)
    fin = empty("Fin", loc=(0, -0.2, 1.0), parent=fl)
    fan = [(0, 0)] + [(math.sin(math.radians(a)) * 0.3, -math.cos(math.radians(a)) * 0.3) for a in range(-70, 71, 20)]
    f = slab("fin", [(y, x) for x, y in fan], 0.03, belly, None, (0, 0, 0), bev=0.01)
    f.rotation_euler = (0, math.radians(90), 0)
    join("FinMesh", [f], fin)
    return root


def coin():
    root = empty("Coin")
    gold = mat("coin_gold", 0xffd23f, 0.25, 0.9, 0x8a5a00, 1)
    face = mat("coin_face", 0xfff4a0, 0.3, 0, 0xfff4a0, 2)
    star = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        r = 0.24 if i % 2 == 0 else 0.1
        star.append((math.cos(a) * r, math.sin(a) * r))
    parts = [cyl("disc", 0.42, 0.1, gold, 20, rot=(90, 0, 0), bev=0.03),
             torus("rim", 0.37, 0.035, gold, 20, 5, rot=(90, 0, 0))]
    for s in (-1, 1):
        st = slab("star", star, 0.03, face, None, (0, 0, 0), bev=0.008)
        st.rotation_euler = (math.radians(90 * s), 0, 0)
        st.location = (0, -s * 0.045, 0)
        parts.append(st)
    join("CoinMesh", parts, root)
    return root


# Outfits: nodes Head / Pack / Feet are authored in the frames of the game's headG,
# pack and stance groups, so their meshes drop straight into those groups.

def outfit_moon():
    root = empty("OutfitMoon")
    white, gold = mat("suit", 0xe8eaf2, 0.55), mat("visor_gold", 0xffb020, 0.1, 1.0, 0x402000, 1)
    bubble = mat("bubble", 0xdff0ff, 0.05, 0.1, 0x2a4a6a, 1, alpha=0.35)
    head = empty("Head", parent=root)
    join("HeadMesh", [sphere("bubble", 0.45, bubble, 18, 12),
                      torus("collar", 0.34, 0.07, white, 16, 6, loc=(0, 0, -0.33)),
                      tbox("visor_band", 0.5, 0.06, 0.1, gold, loc=(0, 0.42, 0.06), rot=(-10, 0, 0), bev=0.02),
                      cyl("antenna", 0.02, 0.32, white, 5, loc=(0.24, -0.1, 0.5)),
                      sphere("tip", 0.05, mat("beacon", 0xff3344, 0.3, 0, 0xff3344, 6), 6, 4, loc=(0.24, -0.1, 0.68))], head)
    pack = empty("Pack", parent=root)
    pk = []
    for s in (-1, 1):
        pk += [cyl("tank", 0.1, 0.6, white, 10, loc=(s * 0.34, 0, 0), bev=0.04),
               cyl("cap", 0.07, 0.1, gold, 8, loc=(s * 0.34, 0, 0.34))]
    join("PackMesh", pk, pack)
    return root


def outfit_sea():
    root = empty("OutfitSea")
    yel, dark = mat("scuba_yellow", 0xffd23f, 0.45, 0, 0x302000, 1), mat("scuba_dark", 0x1a2a34, 0.6)
    lens = mat("scuba_lens", 0x0a2a48, 0.05, 0.3, 0x0a3a60, 1)
    head = empty("Head", parent=root)
    join("HeadMesh", [torus("strap", 0.26, 0.035, dark, 16, 5, loc=(0, 0, 0.04)),
                      tbox("mask", 0.5, 0.1, 0.26, yel, top_w=0.48, loc=(0, 0.22, -0.08), bev=0.05),
                      tbox("lens", 0.42, 0.04, 0.18, lens, loc=(0, 0.28, -0.04), bev=0.03),
                      tbox("nose", 0.12, 0.08, 0.1, dark, loc=(0, 0.27, -0.18), bev=0.03),
                      cyl("snorkel", 0.03, 0.5, yel, 8, loc=(0.29, 0.03, 0.12)),
                      tbox("mouthpiece", 0.06, 0.25, 0.05, yel, loc=(0.27, 0.12, -0.12), bev=0.02)], head)
    pack = empty("Pack", parent=root)
    pk = []
    for s in (-1, 1):
        pk += [cyl("tank", 0.11, 0.68, yel, 10, loc=(s * 0.36, 0, 0), bev=0.05),
               cyl("valve", 0.04, 0.12, dark, 6, loc=(s * 0.36, 0, 0.4))]
    join("PackMesh", pk, pack)
    feet = empty("Feet", parent=root)
    fin_m = mat("scuba_fin", 0x2affd0, 0.4, 0, 0x0a3a30, 1)
    fins = []
    for s in (-1, 1):
        fins.append(slab("fin", [(-0.14, -0.05), (0.14, -0.05), (0.2, 0.7), (0, 0.62), (-0.2, 0.7)], 0.04, fin_m, None,
                         (s * 0.3, 0.05, 0.03), bev=0.01))
    join("FeetMesh", fins, feet)
    return root


def outfit_lava():
    root = empty("OutfitLava")
    silver = mat("heat_silver", 0xe0e0ea, 0.3, 0.8, 0x3a3a44, 1)
    visor = mat("heat_visor", 0xffa030, 0.1, 0.9, 0x8a3a00, 1)
    can = mat("heat_can", 0x3a3a44, 0.5, 0.6)
    head = empty("Head", parent=root)
    join("HeadMesh", [sphere("hood", 0.34, silver, 14, 10, loc=(0, 0, 0.03), scale=(1, 1.05, 1.05)),
                      torus("hood_rim", 0.3, 0.05, silver, 14, 5, loc=(0, 0, -0.3)),
                      sphere("visor", 0.28, visor, 12, 8, loc=(0, 0.15, 0.05), scale=(0.85, 0.7, 0.45)),
                      cyl("can_l", 0.07, 0.13, can, 8, loc=(-0.14, 0.3, -0.15), rot=(70, 0, 0)),
                      cyl("can_r", 0.07, 0.13, can, 8, loc=(0.14, 0.3, -0.15), rot=(70, 0, 0))], head)
    return root


def outfit_sky():
    root = empty("OutfitSky")
    leather, brass = mat("leather", 0x8a5a32, 0.7, 0, 0x1a0a00, 1), mat("brass", 0xd8a040, 0.3, 0.9)
    lens = mat("goggle_lens", 0x9ae8ff, 0.1, 0.3, 0x2a6a80, 1)
    head = empty("Head", parent=root)
    hd = [lathe("cap", [(0.31 * math.sin(math.radians(d)), 0.31 * math.cos(math.radians(d)) + 0.04) for d in (105, 80, 55, 30, 0)],
                leather, 14, cap_bottom=False, cap_top=False),
          tbox("flap_l", 0.07, 0.2, 0.24, leather, loc=(-0.29, 0, -0.22), bev=0.03),
          tbox("flap_r", 0.07, 0.2, 0.24, leather, loc=(0.29, 0, -0.22), bev=0.03),
          torus("strap", 0.29, 0.03, leather, 16, 5, loc=(0, 0, 0.14)),
          cyl("mast", 0.025, 0.2, brass, 6, loc=(0, 0, 0.38))]
    for x in (-0.12, 0.12):
        hd += [torus("ring", 0.085, 0.025, brass, 12, 5, loc=(x, 0.25, 0.15), rot=(90, 0, 0)),
               cyl("lens", 0.075, 0.02, lens, 12, loc=(x, 0.26, 0.15), rot=(90, 0, 0))]
    join("HeadMesh", hd, head)
    prop = empty("Prop", loc=(0, 0, 0.45), parent=head)
    blades = [sphere("hub", 0.05, brass, 8, 5)]
    for a, col in ((0, PINK), (90, CYAN)):
        b = tbox("blade", 0.62, 0.1, 0.025, mat(f"blade_{col}", col, 0.4, 0, col, 1), loc=(0, 0, -0.012), rot=(0, 8, a), bev=0.01)
        blades.append(b)
    join("PropMesh", blades, prop)
    return root
