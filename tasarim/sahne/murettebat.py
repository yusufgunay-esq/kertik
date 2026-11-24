# Kertik crew: two brothers, built from MakeHuman CC0 data through the shared person pipeline
# (D:/Projelerim/Ahali/araclar/blender/insan; data in D:/Ortak/varlik).
# The elder steers; the younger hauls the sail, lounges, fishes and points at the next harbour.
#   blender -b --factory-startup --python murettebat.py -- deneme <out_prefix>
import math
import os
import sys

AHALI = os.environ.get("AHALI_BLENDER", "D:/Projelerim/Ahali/araclar/blender")
if AHALI not in sys.path:
    sys.path.insert(0, AHALI)

import bmesh  # noqa: E402
import numpy as np  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Quaternion, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

from insan import kadro  # noqa: E402
from insan import malzeme as mz  # noqa: E402
from insan import anime  # noqa: E402

# Art: the shared illustrated-people recipe (stylised MakeHuman mesh, painted eyes, ribbon hair,
# own-colour contour, colour shadows) softened for a sunlit sea: a wider light-to-shadow band and
# emission lifted to sit under the scene's tone mapping.
anime.RAMP = (0.09, 0.27)
PARLAK = 1.27            # emission gain; 2 ** 0.35 undoes the scene exposure of -0.35


def isik(gunes):
    """Unit vector towards the sun (world space): faces are lit by N.L against it."""
    anime.SUN_DIR = tuple(Vector(gunes).normalized())

IRK = {"caucasian": 0.90, "african": 0.04, "asian": 0.06}

# Elder brother: late twenties, lean, long face, long straight nose, high cheekbones,
# grey-blue eyes, wavy brown hair swept back; dense moustache and chin, light stubble on the cheeks.
# Sea clothes: undyed linen shirt, dark brown trousers.
ABI = dict(
    name="abi",
    m=dict(sex=1.0, age=0.52, muscle=0.55, weight=0.42, boy=1.80, proportions=0.85, race=IRK),
    yuz_gen={
        "head/head-oval": 0.25,
        "head/head-scale-horiz-decr": 0.12,
        "head/head-scale-vert-incr": 0.08,
        "nose/nose-scale-vert-incr": 0.30,
        "nose/nose-scale-depth-incr": 0.22,
        "nose/nose-point-width-decr": 0.10,
        "cheek/{s}-cheek-bones-incr": 0.30,
        "cheek/{s}-cheek-volume-decr": 0.15,
        "chin/chin-height-incr": 0.12,
        "chin/chin-width-decr": 0.12,
        "chin/chin-prominent-incr": 0.10,
        "eyebrows/eyebrows-trans-down": 0.12,
        "eyes/{s}-eye-eyefold-down": 0.15,
        "eyes/{s}-eye-scale-decr": 0.08,
        "forehead/forehead-scale-vert-incr": 0.10,
    },
    ten=(0.36, 0.62), sac=(0.56, 0.44), goz=("mavi", 0.35),
    sac_stil="geriye_tarak", kakul=False, sakal="kisa_sakal", sakal_renk=(0.52, 0.50),
    kas_stil="thick_warm", kas_kalin=1.05, kas_kavis=0.70,
    yuz=("smile", 0.15), bas_don=0.0, bas_eg=0.0,
    giysi=[("clothes", "male_casualsuit01", ["#EDE6D6", "#4A3B30"]), ("clothes", "shoes06", "#5A4030")],
)

# Younger brother: about eighteen, slim, oval face, bright blue eyes, brown hair falling on the
# forehead, no beard. Undyed linen tee, ochre trousers, a red neckerchief that answers the sail.
KARDES = dict(
    name="kardes",
    m=dict(sex=1.0, age=0.37, muscle=0.45, weight=0.40, boy=1.76, proportions=0.85, race=IRK),
    yuz_gen={
        "head/head-oval": 0.35,
        "head/head-scale-horiz-decr": 0.08,
        "head/head-scale-vert-incr": 0.06,
        "nose/nose-scale-vert-incr": 0.16,
        "nose/nose-point-width-decr": 0.08,
        "eyes/{s}-eye-scale-incr": 0.04,
        "chin/chin-height-incr": 0.06,
        "chin/chin-width-decr": 0.08,
        "cheek/{s}-cheek-volume-decr": 0.12,
    },
    ten=(0.31, 0.56), sac=(0.60, 0.34), goz=("mavi", 0.18),
    sac_stil="kisa_dalga", kakul=True, kas_stil="thick_warm", kas_kalin=0.90, kas_kavis=0.85,
    yuz=("smile", 0.22), bas_don=0.0, bas_eg=0.0,
    giysi=[("clothes", "male_casualsuit06", ["#E2D3B6", "#9E7C45"]), ("clothes", "shoes02", "#7A6450")],
    mendil="#B5412C",
)

# Boat-local landmarks (bow +Y), from sefer3d.tekne()
YEKE_UCU = Vector((0.05, -2.97, 1.49))     # forward end of the tiller
OTURAK_Z = 1.10                            # top of the helm thwart
SANDIK_Z = 1.125                           # top of the crate
OLTA_UCU = Vector((2.5, -1.25, 3.05))      # rod tip while fishing seated
MANDAR = (Vector((0.05, 1.17, 5.0)), Vector((0.05, 0.89, 1.0)))   # halyard along the mast's aft face


def guverte_z(y):
    """Deck height at boat-local y (same curve as the hull sheer, 0.12 below it)."""
    t = y / 7.0 + 0.5
    return 0.78 + 0.32 * (2 * t - 1) ** 2 + 0.22 * max(0.0, 2 * t - 1) ** 3 - 0.12


def _parca(p, sonek):
    return next((o for o in p["parts"] if o.name.endswith(sonek)), None)


def _agac(o):
    return BVHTree.FromPolygons([v.co.copy() for v in o.data.vertices],
                                [tuple(f.vertices) for f in o.data.polygons])


def _kaydir(me, yeni):
    """Move mesh vertices to yeni[i]; baked expressions are shape keys, so move every key block."""
    fark = [yeni[i] - v.co for i, v in enumerate(me.vertices)]
    for kb in (me.shape_keys.key_blocks if me.shape_keys else []):
        for i, d in enumerate(fark):
            kb.data[i].co += d
    for v, d in zip(me.vertices, fark):
        v.co += d
    me.update()


def _bant_genisligi(z, ztop):
    if z > ztop - 0.018:
        return 0.036                  # moustache
    if z > ztop - 0.036:
        return 0.031                  # down past the mouth corners
    return 0.025                      # chin


def sakal_kirp(p, e):
    """Short beard that is dense on the moustache and chin and sparse on the cheeks: the cheek
    shell is pulled close to the skin and painted towards the skin tone through a density map."""
    sakal = _parca(p, "_beard")
    if not sakal:
        return
    me = sakal.data
    agac = _agac(p["body"])
    ztop = max(v.co.z for v in me.vertices if abs(v.co.x) < 0.012)

    def yogunluk(co):
        d = max(abs(co.x) - _bant_genisligi(co.z, ztop), 0.0)
        return max(0.40, 1.0 - d / 0.022 * 0.60)
    yeni = []
    for v in me.vertices:
        yakin, _, _, d = agac.find_nearest(v.co)
        y_ = yogunluk(v.co)
        k = 1.3 if v.co.z > ztop - 0.018 and y_ > 0.99 else 0.55 + 0.35 * y_
        yeni.append(yakin + (v.co - yakin) * k if yakin is not None and d > 0.002 else v.co.copy())
    _kaydir(me, yeni)
    zs = [v.co.z for v in me.vertices]
    alt = min(zs) + 0.25 * (max(zs) - min(zs))
    arka = p["arm"].data.bones["head"].head_local.y - 0.01     # nothing behind the jaw hinge
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < alt or v.co.y > arka], context="VERTS")
    bm.to_mesh(me); bm.free(); me.update()
    at = me.attributes.new("yogun", "FLOAT", "POINT")
    at.data.foreach_set("value", [yogunluk(v.co) for v in me.vertices])

    # painted, not stippled: full beard colour on the moustache and chin, a stubble tone that
    # melts into the skin on the cheeks
    hair = np.array([0.11, 0.10, 0.13]) + mz.hair(*e.get("sakal_renk", e["sac"])) * 0.88
    skin = np.asarray(mz.skin(*e["ten"]), float)
    m = bpy.data.materials.new(p["name"] + "_sakal_boya"); m.use_nodes = True
    n, L = m.node_tree.nodes, m.node_tree.links
    at_n = n.new("ShaderNodeAttribute"); at_n.attribute_name = "yogun"
    fac = mz._math(n, L, "MULTIPLY_ADD", at_n.outputs["Fac"], 1 / 0.6, -0.4 / 0.6)
    col = mz._mix_rgba(n, L, fac, mz.lin(hair * 0.20 + skin * 0.80), mz.lin(hair * 0.86 + skin * 0.14))
    L.new(col, n["Principled BSDF"].inputs["Base Color"])
    me.materials[0] = anime.toon(m, col, rim=0.12)


def mendil(p, renk):
    """A knotted neckerchief: a soft roll around the neck and a triangle on the chest, fitted
    to whatever the person wears, skinned to neck01 / spine01."""
    arm = p["arm"]
    c = arm.data.bones["neck01"].head_local.copy() + Vector((0, 0.004, 0.012))
    nesneler = [p["body"]] + [o for o in p["parts"] if "suit" in o.name]
    agaclar = [_agac(o) for o in nesneler]

    def on(x, z):                       # front-most surface y at (x, z)
        ys = []
        for t in agaclar:
            h = t.ray_cast(Vector((x, -1.0, z)), Vector((0, 1, 0)))[0]
            if h is not None:
                ys.append(h.y)
        return min(ys) if ys else c.y - 0.08
    body = p["body"].data.vertices
    kesit = [v.co for v in body if abs(v.co.z - c.z) < 0.008]
    rx = max(abs(q.x - c.x) for q in kesit if abs(q.y - c.y) < 0.02) + 0.006
    ry = max(abs(q.y - c.y) for q in kesit if abs(q.x - c.x) < 0.02) + 0.006
    bm = bmesh.new()
    N, K, r = 28, 8, 0.0095
    halka = []
    for i in range(N):
        a = 2 * math.pi * i / N
        P = Vector((c.x + rx * math.cos(a), c.y + ry * math.sin(a), c.z))
        R = Vector((math.cos(a), math.sin(a), 0)).normalized()
        halka.append([bm.verts.new(P + r * (math.cos(2 * math.pi * j / K) * R * 0.45
                                            + math.sin(2 * math.pi * j / K) * Vector((0, 0, 1)) * 1.4))
                      for j in range(K)])
    for i in range(N):
        for j in range(K):
            bm.faces.new((halka[i][j], halka[(i + 1) % N][j], halka[(i + 1) % N][(j + 1) % K],
                          halka[i][(j + 1) % K]))
    n_halka = len(bm.verts)
    satir = []
    for k in range(6):
        s = k / 5
        z = c.z - 0.004 - 0.105 * s
        w = 0.05 * (1 - s)
        xs = [c.x - w, c.x, c.x + w] if k < 5 else [c.x]
        satir.append([bm.verts.new((x, on(x, z) - 0.007 - 0.004 * (1 - abs(x - c.x) / 0.05), z)) for x in xs])
    for k in range(4):
        a, b = satir[k], satir[k + 1]
        bm.faces.new((a[0], a[1], b[1], b[0])); bm.faces.new((a[1], a[2], b[2], b[1]))
    a, t = satir[4], satir[5][0]
    bm.faces.new((a[0], a[1], t)); bm.faces.new((a[1], a[2], t))
    me = bpy.data.meshes.new(p["name"] + "_mendil"); bm.to_mesh(me); bm.free()
    for f in me.polygons:
        f.use_smooth = True
    o = bpy.data.objects.new(p["name"] + "_mendil", me)
    bpy.context.scene.collection.objects.link(o)
    so = o.modifiers.new("kalin", "SOLIDIFY"); so.thickness = 0.006
    gn, gs = o.vertex_groups.new(name="neck01"), o.vertex_groups.new(name="spine01")
    gn.add(list(range(n_halka)), 1.0, "REPLACE")
    gs.add(list(range(n_halka, len(me.vertices))), 1.0, "REPLACE")
    md = o.modifiers.new("rig", "ARMATURE"); md.object = arm
    o.parent = arm
    me.materials.append(anime.flat(p["name"] + "_mendil", mz.cloth(renk)))
    anime.kontur(o, np.asarray(mz.cloth(renk), float) * 0.42, 0.0018)
    p["parts"].append(o)


def kur(e, x=0.0, parlak=None):
    p = anime.make(e, x, kakul=e.get("kakul", True))
    if e.get("sakal") == "kisa_sakal":
        sakal_kirp(p, e)
    if e.get("mendil"):
        mendil(p, e["mendil"])
    g = PARLAK if parlak is None else parlak
    for o in [p["body"]] + p["parts"]:
        for m in (o.data.materials if o.type == "MESH" else []):
            for nd in (m.node_tree.nodes if m and m.use_nodes else []):
                if nd.type == "EMISSION":
                    nd.inputs["Strength"].default_value *= g
    return p


# ---------------------------------------------------------------- posing
def _iki_kemik(S, H, a, b, kutup):
    """Two-bone IK: elbow/knee position from root S, end H, lengths a, b and a pole direction."""
    d = H - S
    L = max(1e-4, min(d.length, (a + b) * 0.999))
    dn = d.normalized()
    x = (a * a - b * b + L * L) / (2 * L)
    y = math.sqrt(max(0.0, a * a - x * x))
    k = (kutup - dn * kutup.dot(dn))
    k = k.normalized() if k.length > 1e-6 else Vector((0, 0, 1))
    return S + dn * x + k * y


def uzuv(arm, kok, orta, uc_kemik, hedef, kutup):
    """Pose a limb chain (kok -> orta -> uc_kemik) so its end reaches hedef (armature space)."""
    pb = arm.pose.bones
    bpy.context.view_layer.update()
    S = pb[kok].head.copy(); M_ = pb[orta].head.copy(); E = pb[uc_kemik].head.copy()
    a, b = (M_ - S).length, (E - M_).length
    dirsek = _iki_kemik(S, Vector(hedef), a, b, Vector(kutup))
    kadro._aim(arm, kok, orta, dirsek - S)
    bpy.context.view_layer.update()
    kadro._aim(arm, orta, uc_kemik, Vector(hedef) - pb[orta].head)
    bpy.context.view_layer.update()


def kol(arm, side, hedef, kutup):
    uzuv(arm, "upperarm01" + side, "lowerarm01" + side, "wrist" + side, hedef, kutup)


def omuz(arm, side):
    return arm.pose.bones["upperarm01" + side].head.copy()


def otur(arm, diz_acik=0.10):
    """Seated: thighs forward, shins down. Armature space: -Y front, +X person's left."""
    for side, sx in ((".L", 1), (".R", -1)):
        kadro._aim(arm, "upperleg01" + side, "lowerleg01" + side, (sx * diz_acik, -1.0, 0.04))
        bpy.context.view_layer.update()
        kadro._aim(arm, "lowerleg01" + side, "foot" + side, (sx * 0.03, -0.22, -1.0))
        bpy.context.view_layer.update()


def egil(arm, derece):
    """Bend the upper body at the lower spine: + forward, - back."""
    kadro._rotate(arm, "spine04", Quaternion(Vector((1, 0, 0)), math.radians(derece)))


def bas(arm, don=0.0, egik=0.0):
    """Turn the head (deg, + = towards the person's left) and nod (deg, + = down)."""
    if don:
        kadro._rotate(arm, "head", Quaternion(Vector((0, 0, 1)), math.radians(don)))
    if egik:
        kadro._rotate(arm, "head", Quaternion(Vector((1, 0, 0)), math.radians(egik)))


def gulus(p, v):
    for o in [p["body"]] + p["parts"]:
        sk = o.data.shape_keys if o.type == "MESH" else None
        if sk and "smile" in sk.key_blocks:
            sk.key_blocks["smile"].value = v


def yerlestir(p, kok, nokta, yon_z, zemin, oturuyor):
    """Parent an armature to the boat, facing yon_z (0 = facing aft, pi = facing the bow).
    Seated: hips over nokta on a seat at height zemin. Standing: feet on a deck at height zemin.
    Returns (boat-local -> armature space, armature space -> boat-local)."""
    arm = p["arm"]
    bpy.context.view_layer.update()
    pb = arm.pose.bones
    k = (pb["upperleg01.L"].head + pb["upperleg01.R"].head) / 2
    kr = Matrix.Rotation(yon_z, 4, "Z") @ k
    arm.parent = kok
    arm.rotation_euler = (0, 0, yon_z)
    z = zemin + 0.09 - kr.z if oturuyor else zemin
    arm.location = (nokta[0] - kr.x, nokta[1] - kr.y, z)
    bpy.context.view_layer.update()
    ters = Matrix.Rotation(-yon_z, 4, "Z")
    duz = Matrix.Rotation(yon_z, 4, "Z")
    loc = Vector(arm.location)
    return (lambda q: ters @ (Vector(q) - loc)), (lambda q: duz @ Vector(q) + loc)


def diz_ustu(arm, side):
    return arm.pose.bones["lowerleg01" + side].head + Vector((0.0, -0.02, 0.09))


def murettebat(kok, poz="dumen", sahne="seyir"):
    """sahne: kalkis | seyir | varis; poz (seyir): dumen | olta | tuttu.
    Returns dict(abi, kardes, cizim) where cizim lists props for the scene to draw in boat-local
    coordinates: ("cubuk", name, p1, p2, radius, material), ("balik", pos), ("kangal", pos)."""
    cizim = []
    an = sahne if sahne != "seyir" else poz        # kalkis | dumen | olta | tuttu | varis

    # elder brother: always at the helm, left hand on the tiller
    abi = kur(ABI)
    a = abi["arm"]
    otur(a, 0.14)
    ic, _ = yerlestir(abi, kok, (0.46, -2.58), math.radians(-143), OTURAK_Z, True)
    egil(a, {"dumen": -6, "olta": 4, "tuttu": -4}.get(an, 0))
    kol(a, ".L", ic(YEKE_UCU + Vector((0.02, 0.04, 0.03))), (0.6, 0.6, -0.8))
    if an == "kalkis":       # waves back to the quay
        kol(a, ".R", omuz(a, ".R") + Vector((-0.2, -0.16, 0.5)), (-1.0, 0.3, -0.5))
        bas(a, 34.0, -6.0); gulus(abi, 0.45)
    elif an == "varis":      # shades his eyes towards the town
        kol(a, ".R", a.pose.bones["head"].head + Vector((-0.02, -0.14, 0.10)), (-1.0, 0.2, -0.8))
        bas(a, -14.0, -2.0); gulus(abi, 0.2)
    else:
        kol(a, ".R", diz_ustu(a, ".R"), (-1.0, 0.2, -0.5))
        bas(a, {"dumen": -22.0, "olta": -34.0, "tuttu": -40.0}[an], {"olta": 6.0}.get(an, 0.0))
        gulus(abi, {"dumen": 0.35, "olta": 0.25, "tuttu": 0.85}[an])

    kardes = kur(KARDES)
    c = kardes["arm"]
    if an == "kalkis":       # hauls the sail up the mast
        y = 0.6
        ic2, dis2 = yerlestir(kardes, kok, (0.08, y), math.pi, guverte_z(y), False)
        egil(c, -8)
        ust, alt_ = MANDAR

        def ip(z):
            s = (ust.z - z) / (ust.z - alt_.z)
            return ust.lerp(alt_, s)
        kol(c, ".L", ic2(ip(2.6)), (1.0, 0.3, -0.3))
        kol(c, ".R", ic2(ip(1.9)), (-1.0, 0.2, -0.7))
        bas(c, 0.0, -32.0); gulus(kardes, 0.3)
        cizim.append(("cubuk", "Mandar", ust, alt_, 0.012, "halat"))
    elif an == "dumen":      # leans back on his hands, watching the sail
        otur(c, 0.18)
        ic2, _ = yerlestir(kardes, kok, (0.16, -1.6), math.radians(90), SANDIK_Z, True)
        egil(c, -16)
        kol(c, ".L", ic2((-0.12, -1.38, SANDIK_Z + 0.03)), (0.6, 1.0, 0.0))
        kol(c, ".R", ic2((-0.12, -1.82, SANDIK_Z + 0.03)), (-0.6, 1.0, 0.0))
        bas(c, 16.0, -22.0); gulus(kardes, 0.35)
    elif an == "olta":       # rod over the starboard rail
        otur(c, 0.16)
        ic2, _ = yerlestir(kardes, kok, (0.24, -1.55), math.radians(45), SANDIK_Z, True)
        egil(c, 12)
        alt = Vector((0.52, -1.86, 1.36))
        yon = (OLTA_UCU - alt).normalized()
        kol(c, ".R", ic2(alt), (-1.0, 0.2, -0.8))
        kol(c, ".L", ic2(alt + yon * 0.38), (1.0, 0.0, -1.0))
        bas(c, 10.0, -12.0); gulus(kardes, 0.2)
        cizim += [("cubuk", "Olta", alt - yon * 0.3, OLTA_UCU, 0.022, "kusak"),
                  ("cubuk", "Misina", OLTA_UCU, Vector((3.3, -0.5, 0.05)), 0.006, "halat")]
    elif an == "tuttu":      # stands up and lifts the catch
        # on the port side, clear of the sail, so the catch hangs against open water
        y = -0.55
        ic2, dis2 = yerlestir(kardes, kok, (-0.3, y), math.radians(-60), guverte_z(y), False)
        kol(c, ".R", omuz(c, ".R") + Vector((-0.06, -0.26, 0.36)), (-1.0, 0.3, -0.6))
        kol(c, ".L", omuz(c, ".L") + Vector((0.16, -0.06, 0.52)), (1.0, 0.3, -0.4))
        bas(c, -12.0, -14.0); gulus(kardes, 0.9)
        bpy.context.view_layer.update()
        el = dis2(c.pose.bones["wrist.R"].head)
        uc = el + Vector((-0.62, 0.05, 0.78)).normalized() * 1.9
        balik = Vector((uc.x + 0.05, uc.y, el.z - 0.15))
        cizim += [("cubuk", "Olta", el - (uc - el).normalized() * 0.3, uc, 0.022, "kusak"),
                  ("cubuk", "Misina", uc, balik + Vector((0, 0, 0.3)), 0.006, "halat"),
                  ("balik", balik)]
    else:                    # varis: at the bow, points at the town, coil in hand
        y = 2.05
        ic2, dis2 = yerlestir(kardes, kok, (0.28, y), math.pi, guverte_z(y), False)
        kol(c, ".R", omuz(c, ".R") + Vector((-0.10, -0.60, 0.20)), (-0.3, 0.0, -1.0))
        kol(c, ".L", c.pose.bones["upperleg01.L"].head + Vector((0.17, -0.10, 0.04)), (1.0, 0.4, 0.0))
        bas(c, -6.0, -4.0); gulus(kardes, 0.5)
        bpy.context.view_layer.update()
        cizim.append(("kangal", dis2(c.pose.bones["wrist.L"].head) + Vector((0, 0, -0.06))))
    return dict(abi=abi, kardes=kardes, cizim=cizim)


if __name__ == "__main__" and "--" in sys.argv:
    args = sys.argv[sys.argv.index("--") + 1:]
    if args[0] == "deneme":
        s = anime.sahne()
        b = kur(ABI, -0.45, parlak=1.0)
        c = kur(KARDES, 0.45, parlak=1.0)
        pb = b["arm"].pose.bones
        print("PARENTS", {k: (pb[k].parent.name if pb[k].parent else None)
                          for k in ("upperleg01.L", "spine05", "spine04", "neck01", "spine01")})
        for p in (b, c):
            print("BUILT", p["name"], round(float(p["co"][:, 2].max()), 3), [o.name for o in p["parts"]])
        out = os.path.abspath(args[1])
        mz.camera((0.0, -4.2, 1.0), (0, 0, 0.85), 50)
        s.render.resolution_x, s.render.resolution_y = 1000, 1000
        s.render.filepath = out + "_boy.png"
        bpy.ops.render.render(write_still=True)
        for p in (b, c):
            x = p["arm"].location.x
            z = float(p["co"][:, 2].max()) - 0.15
            for c_ in [c_ for c_ in s.objects if c_.type == "CAMERA"]:
                bpy.data.objects.remove(c_)
            mz.camera((x + 0.25, -1.2, z), (x, 0, z - 0.06), 85)
            s.render.resolution_x, s.render.resolution_y = 600, 700
            s.render.filepath = f"{out}_{p['name']}.png"
            bpy.ops.render.render(write_still=True)
        print("DENEME_OK")
