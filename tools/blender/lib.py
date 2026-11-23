"""Shared helpers for building stylized low-poly Hover Bored models in Blender.

Axis convention: model "forward" is Blender +Y, which the glTF exporter turns
into three.js -Z, matching the game's forward direction. Units are game metres.
"""
import math
import bpy
import bmesh
from mathutils import Vector

_mats = {}


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()


def mat(name, color, rough=0.5, metal=0.0, emit=None, strength=1.0, alpha=1.0):
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*srgb(color), 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit is not None:
        p.inputs["Emission Color"].default_value = (*srgb(emit), 1)
        p.inputs["Emission Strength"].default_value = strength
    if alpha < 1:
        p.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
    m.diffuse_color = (*srgb(color), alpha)
    _mats[name] = m
    return m


def srgb(hexcol):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(lin((hexcol >> s) & 255) for s in (16, 8, 0))


def _obj(name, bm, material, parent, smooth_angle):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if material:
        me.materials.append(material)
    if parent:
        ob.parent = parent
    if smooth_angle is not None:
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(smooth_angle))
    return ob


def place(ob, loc=(0, 0, 0), rot=(0, 0, 0), scale=None):
    ob.location = loc
    ob.rotation_euler = [math.radians(a) for a in rot]
    if scale:
        ob.scale = scale
    return ob


def bevel(ob, width=0.03, segs=2, angle=40):
    """Bevel sharp edges directly in the mesh data (no modifier, so nothing to evaluate later)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    lim = math.radians(angle)
    edges = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > lim]
    bmesh.ops.bevel(bm, geom=edges, offset=width, segments=segs, profile=0.5,
                    affect="EDGES", clamp_overlap=True)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.shade_smooth()
    ob.data.set_sharp_from_angle(angle=math.radians(35))
    return ob


def tbox(name, w, d, h, material, top_w=None, top_d=None, top_dy=0.0, loc=(0, 0, 0),
         rot=(0, 0, 0), parent=None, bev=0.03, segs=2):
    """Box (or frustum when top size differs) sitting on z=0, centred in x/y."""
    top_w = w if top_w is None else top_w
    top_d = d if top_d is None else top_d
    bm = bmesh.new()
    vs = [bm.verts.new((x * w / 2, y * d / 2, 0)) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    vt = [bm.verts.new((x * top_w / 2, y * top_d / 2 + top_dy, h)) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    bm.faces.new(vs[::-1])
    bm.faces.new(vt)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((vs[i], vs[j], vt[j], vt[i]))
    ob = _obj(name, bm, material, parent, 40)
    place(ob, loc, rot)
    if bev:
        bevel(ob, bev, segs)
    return ob


def lathe(name, profile, material, segs=12, loc=(0, 0, 0), rot=(0, 0, 0), parent=None,
          scale=None, smooth=50, cap_bottom=True, cap_top=True):
    """Revolve [(radius, z), ...] around Z. Zero radius ends become poles."""
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        if r < 1e-6:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z))
                          for a in (2 * math.pi * i / segs for i in range(segs))])
    for a, b in zip(rings, rings[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            if len(a) == 1:
                bm.faces.new((a[0], b[i], b[j]))
            elif len(b) == 1:
                bm.faces.new((a[i], a[j], b[0]))
            else:
                bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap_bottom and len(rings[0]) > 1:
        bm.faces.new(rings[0][::-1])
    if cap_top and len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, material, parent, smooth)
    return place(ob, loc, rot, scale)


def sphere(name, r, material, segs=10, rings=7, loc=(0, 0, 0), scale=None, parent=None, rot=(0, 0, 0)):
    prof = [(r * math.sin(math.pi * i / rings), -r * math.cos(math.pi * i / rings)) for i in range(rings + 1)]
    return lathe(name, prof, material, segs, loc, rot, parent, scale, smooth=80)


def cyl(name, r, h, material, segs=10, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, r2=None, bev=0.0):
    """Cylinder centred on its origin along local Z; r2 tapers the top."""
    r2 = r if r2 is None else r2
    ob = lathe(name, [(r, -h / 2), (r2, h / 2)], material, segs, loc, rot, parent, smooth=50)
    if bev:
        bevel(ob, bev, 2, 50)
    return ob


def torus(name, R, r, material, segs=16, csegs=6, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    bm = bmesh.new()
    grid = []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        ring = []
        for k in range(csegs):
            b = 2 * math.pi * k / csegs
            rr = R + r * math.cos(b)
            ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), r * math.sin(b))))
        grid.append(ring)
    for i in range(segs):
        for k in range(csegs):
            a, b = grid[i], grid[(i + 1) % segs]
            k2 = (k + 1) % csegs
            bm.faces.new((a[k], b[k], b[k2], a[k2]))
    ob = _obj(name, bm, material, parent, 80)
    return place(ob, loc, rot)


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.parent = parent
    return place(e, loc, rot)


def join(name, objs, parent=None):
    """Merge unparented parts, authored in parent-local space, into one mesh node (fewer draw calls)."""
    bm = bmesh.new()
    mats = []
    for ob in objs:
        me = ob.data.copy()
        me.transform(ob.matrix_basis)
        offset = len(mats)
        mats += list(me.materials)
        for p in me.polygons:
            p.material_index += offset
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    uniq = []
    remap = []
    for m in mats:
        if m not in uniq:
            uniq.append(m)
        remap.append(uniq.index(m))
    for m in uniq:
        me.materials.append(m)
    for p in me.polygons:
        p.material_index = remap[p.material_index]
    for ob in objs:
        old = ob.data
        bpy.data.objects.remove(ob)
        bpy.data.meshes.remove(old)
    out = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(out)
    out.parent = parent
    return out


def tri_count(root):
    return sum(len(p.vertices) - 2 for ob in root.children_recursive if ob.type == "MESH" for p in ob.data.polygons)


def export_glb(root, path):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in [root, *root.children_recursive]:
        ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True,
                              export_apply=True, export_yup=True)


def render_preview(root, path, cam_dir=(1.0, -1.3, 0.75), bg=0x2a1240, size=900, fill=1.35, floor=0x3a2260):
    """Throwaway studio (floor, lights, camera) around root; removed after rendering."""
    sc = bpy.context.scene
    tmp = []
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in [root, *root.children_recursive]:
        if ob.type == "MESH":
            pts += [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centre = (lo + hi) / 2
    radius = (hi - lo).length / 2

    floor_m = mat(f"_floor{floor}", floor, rough=0.6, metal=0.2)
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, radius=radius * 6, segments=48)
    fl = _obj("_floor", bm, floor_m, None, None)
    fl.location.z = lo.z - 0.002
    tmp.append(fl)

    def light(kind, energy, loc, color=(1, 1, 1), size_=1.0):
        ld = bpy.data.lights.new("_l", kind)
        ld.energy = energy
        ld.color = color
        if kind == "AREA":
            ld.size = size_
        lo_ = bpy.data.objects.new("_l", ld)
        sc.collection.objects.link(lo_)
        lo_.location = centre + Vector(loc) * radius
        d = centre - lo_.location
        lo_.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        tmp.append(lo_)

    light("AREA", 900 * radius ** 2, (2.0, -2.5, 3.0), (1, 0.95, 0.9), 3 * radius)
    light("AREA", 450 * radius ** 2, (-3.0, -0.5, 1.5), (0.55, 0.75, 1.0), 3 * radius)
    light("AREA", 600 * radius ** 2, (0.5, 3.0, 2.0), (1.0, 0.45, 0.8), 2 * radius)

    cd = bpy.data.cameras.new("_cam")
    cd.lens = 55
    cam = bpy.data.objects.new("_cam", cd)
    sc.collection.objects.link(cam)
    dirv = Vector(cam_dir).normalized()
    dist = radius * fill / math.tan(cd.angle / 2)
    cam.location = centre + dirv * dist
    cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    tmp.append(cam)

    world = sc.world or bpy.data.worlds.new("w")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (*srgb(bg), 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6

    sc.render.resolution_x = size
    sc.render.resolution_y = size
    sc.render.filepath = path
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    for ob in tmp:
        bpy.data.objects.remove(ob)


def setup_render():
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.cycles.device = "CPU"
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"


def limb(name, p1, p2, r1, r2, material, segs=8, parent=None):
    """Tapered cylinder from p1 (radius r1) to p2 (radius r2), with rounded ends."""
    a, b = Vector(p1), Vector(p2)
    n = (b - a).length
    prof = [(0, -r1 * 0.6), (r1 * 0.8, -r1 * 0.45), (r1, 0), (r2, n), (r2 * 0.8, n + r2 * 0.45), (0, n + r2 * 0.6)]
    ob = lathe(name, prof, material, segs, parent=parent, smooth=60)
    ob.location = a
    ob.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    return ob


def slab(name, outline, thick, material, bend=None, loc=(0, 0, 0), parent=None, bev=0.02):
    """Extrude an XY outline by thick; bend(x, y) -> z offset warps it (board kicks)."""
    bm = bmesh.new()
    bend = bend or (lambda x, y: 0.0)
    lo = [bm.verts.new((x, y, bend(x, y))) for x, y in outline]
    hi = [bm.verts.new((x, y, bend(x, y) + thick)) for x, y in outline]
    bm.faces.new(lo[::-1])
    bm.faces.new(hi)
    k = len(outline)
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, material, parent, 35)
    place(ob, loc)
    if bev:
        bevel(ob, bev, 2, 35)
    return ob


def stadium(w, d, segs=8):
    """Rounded-end outline, w across x, d along y."""
    r = w / 2
    half = d / 2 - r
    pts = []
    for end, sgn in ((half, 1), (-half, -1)):
        for i in range(segs + 1):
            a = math.pi * i / segs
            pts.append((sgn * r * math.cos(a), end + sgn * r * math.sin(a)))
    return pts
