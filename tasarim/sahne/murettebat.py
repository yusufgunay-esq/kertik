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
# The band is read on light normalised by the sun's strength, the same scale the world is painted on
# (sefer3d.BAND), so people and places share one light-to-shadow edge.
anime.RAMP = (0.20, 0.34)
PARLAK = 1.27            # emission gain; 2 ** 0.35 undoes the scene exposure of -0.35
OLCEK = None             # 1 / (sun strength * 1.15), set by isik()


def isik(gunes, guc):
    """Sun direction (towards the light, world space) and strength of the scene."""
    global OLCEK
    anime.SUN_DIR = tuple(Vector(gunes).normalized())
    OLCEK = 1.0 / (guc * 1.15)


def isik_olcegi(p, olcek):
    """Scale the measured diffuse light (Shader-to-RGB -> luminance) before the band."""
    for o in [p["body"]] + p["parts"]:
        for m in (o.data.materials if o.type == "MESH" else []):
            if not (m and m.use_nodes):
                continue
            nt = m.node_tree
            for nd in list(nt.nodes):
                if nd.type != "RGBTOBW" or not nd.inputs[0].links:
                    continue
                s2r = nd.inputs[0].links[0].from_node
                if s2r.type != "SHADERTORGB" or not s2r.inputs[0].links:
                    continue
                if s2r.inputs[0].links[0].from_node.type != "BSDF_DIFFUSE":
                    continue                       # leave the glossy hair sheen alone
                hedefler = [l.to_socket for l in nd.outputs[0].links]
                mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
                mul.inputs[1].default_value = olcek
                nt.links.new(nd.outputs[0], mul.inputs[0])
                for t in hedefler:
                    nt.links.new(mul.outputs[0], t)

IRK = {"caucasian": 0.90, "african": 0.04, "asian": 0.06}

# Elder brother: late twenties, lean, long face, long straight nose, high cheekbones,
# grey-blue eyes, wavy brown hair swept back; dense moustache and chin, light stubble on the cheeks.
# Sea clothes: undyed linen shirt, dark brown trousers.
ABI = dict(
    name="abi",
    m=dict(sex=1.0, age=0.52, muscle=0.74, weight=0.38, boy=1.80, proportions=0.85, race=IRK),
    yuz_gen={
        "head/head-oval": 0.10,
        "head/head-square": 0.20,
        "head/head-scale-horiz-decr": 0.12,
        "head/head-scale-vert-incr": 0.08,
        "nose/nose-scale-vert-incr": 0.30,
        "nose/nose-scale-depth-incr": 0.22,
        "nose/nose-point-width-decr": 0.10,
        "cheek/{s}-cheek-bones-incr": 0.40,
        "cheek/{s}-cheek-volume-decr": 0.15,
        "chin/chin-height-incr": 0.12,
        "chin/chin-prominent-incr": 0.10,
        "chin/chin-bones-incr": 0.45,                       # slight jawline under the beard
        "head/head-fat-decr": 0.35,
        "torso/torso-vshape-incr": 0.55,                    # athlete's back: wide lats, narrow waist
        "torso/torso-muscle-dorsi-incr": 0.50,
        "torso/torso-muscle-pectoral-incr": 0.22,
        "armslegs/{s}-upperarm-shoulder-muscle-incr": 0.30,
        "armslegs/{s}-upperarm-muscle-incr": 0.18,
        "eyebrows/eyebrows-trans-down": 0.12,
        "eyes/{s}-eye-eyefold-down": 0.15,
        "eyes/{s}-eye-scale-decr": 0.08,
        "forehead/forehead-scale-vert-incr": 0.10,
    },
    ten=(0.36, 0.62), sac=(0.56, 0.44), goz=("mavi", 0.35),
    sac_stil="geriye_tarak", kakul=False, sakal="kisa_sakal", sakal_renk=(0.52, 0.50),
    kas_stil="thick_warm", kas_kalin=1.05, kas_kavis=0.70,
    yuz=("smile", 0.15), bas_don=0.0, bas_eg=0.0,
    giysi=[("clothes", "male_casualsuit04", ["#EDE6D6", "#4A3B30"]), ("clothes", "shoes06", "#5A4030")],
)

# Younger brother: about eighteen, slim, oval face, bright blue eyes, brown hair falling on the
# forehead, no beard. Undyed linen tee, ochre trousers.
KARDES = dict(
    name="kardes",
    m=dict(sex=1.0, age=0.37, muscle=0.45, weight=0.37, boy=1.76, proportions=0.85, race=IRK),
    yuz_gen={
        "head/head-oval": 0.10,
        "head/head-square": 0.25,
        "head/head-scale-horiz-decr": 0.08,
        "head/head-scale-vert-incr": 0.06,
        "nose/nose-scale-vert-incr": 0.16,
        "nose/nose-point-width-decr": 0.08,
        "eyes/{s}-eye-scale-incr": 0.04,
        "chin/chin-height-incr": 0.06,
        "chin/chin-width-incr": 0.15,
        "chin/chin-bones-incr": 0.80,                       # bony face: jaw corner, high cheekbones,
        "cheek/{s}-cheek-bones-incr": 0.80,                 # a little hollow under them
        "cheek/{s}-cheek-volume-decr": 0.70,
        "head/head-fat-decr": 0.80,
    },
    ten=(0.31, 0.56), sac=(0.60, 0.34), goz=("mavi", 0.18),
    sac_stil="kisa_dalga", kakul=True, kas_stil="thick_warm", kas_kalin=0.90, kas_kavis=0.85,
    yuz=("smile", 0.22), bas_don=0.0, bas_eg=0.0,
    giysi=[("clothes", "male_casualsuit06", ["#E2D3B6", "#9E7C45"]), ("clothes", "shoes02", "#7A6450")],
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
    """Light short beard: moustache and chin, the cheeks only a faint shadow below the mouth line
    (he is not that bearded). The shell hugs the skin and melts into it through a density map."""
    sakal = _parca(p, "_beard")
    if not sakal:
        return
    me = sakal.data
    agac = _agac(p["body"])
    ztop = max(v.co.z for v in me.vertices if abs(v.co.x) < 0.012)
    yanak_ust = ztop - 0.014                                    # cheek line: at the mouth corners

    def yogunluk(co):
        """1 = full beard colour, 0 = bare skin. Cheeks hold a faint shadow that fades out
        towards the cheek line, so the trimmed edge melts into the skin instead of stepping."""
        d = max(abs(co.x) - _bant_genisligi(co.z, ztop), 0.0)
        y = max(0.18, 1.0 - d / 0.014 * 0.82)
        if d > 0.0:
            y *= min(1.0, max(0.0, (yanak_ust + 0.010 - co.z) / 0.014))
        return y
    yeni = []
    for v in me.vertices:
        yakin, _, _, d = agac.find_nearest(v.co)
        y_ = yogunluk(v.co)
        k = 0.95 if v.co.z > ztop - 0.018 and y_ > 0.99 else 0.40 + 0.30 * y_
        yeni.append(yakin + (v.co - yakin) * k if yakin is not None and d > 0.002 else v.co.copy())
    _kaydir(me, yeni)
    zs = [v.co.z for v in me.vertices]
    alt = min(zs) + 0.36 * (max(zs) - min(zs))     # not down under the jaw
    arka = p["arm"].data.bones["head"].head_local.y - 0.01     # nothing behind the jaw hinge
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < alt or v.co.y > arka or (
        v.co.z > yanak_ust + 0.010 and abs(v.co.x) > _bant_genisligi(v.co.z, ztop) + 0.004)], context="VERTS")
    bm.to_mesh(me); bm.free(); me.update()
    at = me.attributes.new("yogun", "FLOAT", "POINT")
    at.data.foreach_set("value", [yogunluk(v.co) for v in me.vertices])

    # painted, not stippled: one beard colour whose coverage follows the density map, so the
    # cheek shadow fades into whatever the skin shading is underneath
    hair = np.array([0.11, 0.10, 0.13]) + mz.hair(*e.get("sakal_renk", e["sac"])) * 0.88
    skin = np.asarray(mz.skin(*e["ten"]), float)
    m = bpy.data.materials.new(p["name"] + "_sakal_boya"); m.use_nodes = True
    n, L = m.node_tree.nodes, m.node_tree.links
    at_n = n.new("ShaderNodeAttribute"); at_n.attribute_name = "yogun"
    renk = mz.lin(hair * 0.50 + skin * 0.50)
    col = mz._mix_rgba(n, L, 1.0, renk, renk)
    L.new(col, n["Principled BSDF"].inputs["Base Color"])
    L.new(at_n.outputs["Fac"], n["Principled BSDF"].inputs["Alpha"])   # density = coverage
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"
    me.materials[0] = anime.toon(m, col, rim=0.12)


def kur(e, x=0.0, parlak=None):
    p = anime.make(e, x, kakul=e.get("kakul", True))
    if e.get("sakal") == "kisa_sakal":
        sakal_kirp(p, e)
    if OLCEK is not None and parlak is None:
        isik_olcegi(p, OLCEK)
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


def dik_otur(arm, ileri=0.0, gogus=9.0, bakis=0.8):
    """Sit tall like an athlete: the trunk stacks over the hips (ileri deg, + forward), the
    sideways lean squares up, the shoulder blades go back and down so the chest opens. The head
    keeps most of where it was looking (bakis share); the rest lifts the chin a little."""
    pb = arm.pose.bones
    zincir = ("spine05", "spine04", "spine03", "spine02")
    on_t = yan_t = 0.0
    for _ in range(3):
        v = pb["neck01"].head - pb["spine05"].head
        on = ileri - math.degrees(math.atan2(-v.y, v.z))
        yan = -math.degrees(math.atan2(v.x, v.z))
        on_t += on; yan_t += yan
        for k in zincir:
            kadro._rotate(arm, k, Quaternion(Vector((1, 0, 0)), math.radians(on / len(zincir))))
            kadro._rotate(arm, k, Quaternion(Vector((0, 1, 0)), math.radians(yan / len(zincir))))
    kadro._rotate(arm, "head", Quaternion(Vector((1, 0, 0)), math.radians(-on_t * bakis)))
    kadro._rotate(arm, "head", Quaternion(Vector((0, 1, 0)), math.radians(-yan_t)))
    for side, sx in ((".L", 1), (".R", -1)):
        kadro._rotate(arm, "clavicle" + side, Quaternion(Vector((0, 0, 1)), math.radians(sx * gogus)))
        kadro._rotate(arm, "clavicle" + side, Quaternion(Vector((0, 1, 0)), math.radians(sx * 4.0)))
    print(f"dik_otur: govde {on_t:+.1f} derece one, {yan_t:+.1f} yana duzeltildi")
    return on_t


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
    z = zemin + 0.11 - kr.z if oturuyor else zemin
    arm.location = (nokta[0] - kr.x, nokta[1] - kr.y, z)
    bpy.context.view_layer.update()
    ters = Matrix.Rotation(-yon_z, 4, "Z")
    duz = Matrix.Rotation(yon_z, 4, "Z")
    return (lambda q: ters @ (Vector(q) - Vector(arm.location))), (lambda q: duz @ Vector(q) + Vector(arm.location))


def diz_ustu(arm, side):
    return arm.pose.bones["lowerleg01" + side].head + Vector((0.0, -0.02, 0.09))


# ---------------------------------------------------------------- motion from reference clips
# Body poses come from captured humanoid motion retargeted onto the rig (xklip). Which clip and
# moment stands for each pose is a local, git-ignored table: _yerel/klipler.json
#   {"kok": <clip folder>, "pozlar": {<pose>: [<clip>, <0..1 moment>], ...}}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xklip  # noqa: E402

_TABLO, _KLIPLER = None, {}
PARMAK = [f"finger{f}-{j}" for f in range(1, 6) for j in range(1, 4)]
UST_SAG = {"spine03", "neck01", "head", "clavicle.R", "upperarm01.R", "lowerarm01.R", "wrist.R"} | \
          {b + ".R" for b in PARMAK}
UST = UST_SAG | {"clavicle.L", "upperarm01.L", "lowerarm01.L", "wrist.L"} | {b + ".L" for b in PARMAK}


def _tablo():
    global _TABLO
    if _TABLO is None:
        yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_yerel", "klipler.json")
        if not os.path.exists(yol):
            raise SystemExit("murettebat: pose clips missing, expected " + yol)
        import json
        with open(yol, encoding="utf-8") as f:
            _TABLO = json.load(f)
    return _TABLO


def hareket(p, poz, sadece=None):
    """Pose p's rig from the reference clip that stands for poz. Returns the retargeter and tick.
    A table entry [clip, moment, true] plays the clip mirrored."""
    t = _tablo()
    ad, an, *ayna = t["pozlar"][poz]
    if ad not in _KLIPLER:
        _KLIPLER[ad] = xklip.Klip(os.path.join(t["kok"], ad + ".x"))
    k = _KLIPLER[ad]
    a = xklip.Aktarici(k, p["arm"])
    tik = k.t0 + (k.t1 - k.t0) * an
    a.poz(tik, sadece=sadece, ayna=bool(ayna and ayna[0]))
    bpy.context.view_layer.update()
    return a, tik


def el_kalibi(p, poz="kavra"):
    """Finger rotations (local to the hand) of a gripping hand, both sides."""
    hareket(p, poz)
    pb = p["arm"].pose.bones
    return {b + s: pb[b + s].matrix_basis.to_quaternion() for s in (".L", ".R") for b in PARMAK
            if b + s in pb}


def el_uygula(p, kalip, side, duz=()):
    """Close a hand around a held object; fingers in duz stay straight (a pointing index)."""
    pb = p["arm"].pose.bones
    for b in PARMAK:
        n = b + side
        if n in pb and n in kalip:
            pb[n].rotation_mode = "QUATERNION"
            pb[n].rotation_quaternion = Quaternion() if b.split("-")[0] in duz else kalip[n]
    bpy.context.view_layer.update()


def avuc(arm, side):
    """Centre of the closed fist (between the knuckles), armature space."""
    pb = arm.pose.bones
    return (pb["finger2-1" + side].head + pb["finger5-1" + side].head) / 2


def en_alt(p, kok):
    """Lowest point of the dressed, posed body (evaluated mesh incl. clothes), boat-local z."""
    dg = bpy.context.evaluated_depsgraph_get()
    T = kok.matrix_world.inverted()
    enk = 1e9
    for o in [p["body"]] + p["parts"]:
        if o.type != "MESH":
            continue
        oe = o.evaluated_get(dg)
        me = oe.to_mesh()
        n = len(me.vertices)
        if n:
            co = np.empty(n * 3)
            me.vertices.foreach_get("co", co)
            M_ = np.array(T @ oe.matrix_world)
            z = co.reshape(-1, 3) @ M_[2, :3] + M_[2, 3]
            enk = min(enk, float(z.min()))
        oe.to_mesh_clear()
    return enk


def yere_bas(p, kok, zemin):
    """Rest the figure on a surface: its lowest point (soles, or seat and legs) touches zemin."""
    p["arm"].location.z += zemin - en_alt(p, kok)
    bpy.context.view_layer.update()


def ayaklar_yere(p, ic, dis, adim=0.40, acik=0.12):
    """Seated on a raised seat: plant both feet flat on the deck in front of it (leg IK)."""
    arm = p["arm"]
    pb = arm.pose.bones
    bpy.context.view_layer.update()
    for side, sx in ((".L", 1), (".R", -1)):
        b = dis(pb["upperleg01" + side].head + Vector((sx * acik, -adim, 0.0)))
        b.z = guverte_z(b.y) + 0.085
        uzuv(arm, "upperleg01" + side, "lowerleg01" + side, "foot" + side, ic(b), (sx * 0.15, -1.0, 0.3))
        if "toe1-1" + side in pb:
            kadro._aim(arm, "foot" + side, "toe1-1" + side, (sx * 0.06, -1.0, -0.10))
    bpy.context.view_layer.update()


def olta_yonu(akt, tik, dis):
    """Rod direction held in the right hand at tick, in boat-local space."""
    _, R = akt.tutamak(tik, "R")
    d = Vector(R[:, 1].tolist())
    return (dis(d) - dis(Vector((0, 0, 0)))).normalized()


def murettebat(kok, poz="dumen", sahne="seyir"):
    """sahne: kalkis | seyir | varis; poz (seyir): dumen | olta | tuttu.
    Returns dict(abi, kardes, cizim) where cizim lists props for the scene to draw in boat-local
    coordinates: ("cubuk", name, p1, p2, radius, material), ("balik", pos), ("kangal", pos)."""
    cizim = []
    an = sahne if sahne != "seyir" else poz        # kalkis | dumen | olta | tuttu | varis

    # elder brother: always seated at the helm; the tiller comes to his left hand
    abi = kur(ABI)
    a = abi["arm"]
    kavra = el_kalibi(abi)
    hareket(abi, "otur")
    if an == "kalkis":       # waves back to the quay
        hareket(abi, "el_salla", sadece=UST_SAG)
    elif an == "varis":      # hand at the brow against the low sun, looking at the town
        hareket(abi, "siper", sadece=UST_SAG)
    ic, dis = yerlestir(abi, kok, (0.46, -2.66), math.radians(-143), OTURAK_Z, True)
    ayaklar_yere(abi, ic, dis, 0.36, 0.13)
    dik_otur(a, {"dumen": -3.0, "olta": 3.0, "tuttu": -1.0, "varis": -2.0}.get(an, 0.0))
    el_uygula(abi, kavra, ".L")
    if an == "kalkis":
        bas(a, 24.0, -4.0); gulus(abi, 0.45)
    elif an == "varis":
        bas(a, -10.0, 0.0); gulus(abi, 0.2)
    else:
        bas(a, {"dumen": -22.0, "olta": -34.0, "tuttu": -40.0}[an], {"olta": 6.0}.get(an, 0.0))
        gulus(abi, {"dumen": 0.35, "olta": 0.25, "tuttu": 0.85}[an])
    bpy.context.view_layer.update()
    cizim.append(("yeke", dis(avuc(a, ".L")) + Vector((0, 0, -0.03))))

    kardes = kur(KARDES)
    c = kardes["arm"]
    kavra = el_kalibi(kardes)
    if an == "kalkis":       # hauls the sail up: the halyard runs through both fists
        hareket(kardes, "dur")
        hareket(kardes, "ip_cek", sadece=UST)
        ic2, dis2 = yerlestir(kardes, kok, (0.08, 0.5), math.pi, guverte_z(0.5), False)
        el_uygula(kardes, kavra, ".L"); el_uygula(kardes, kavra, ".R")
        bpy.context.view_layer.update()
        orta = (dis2(avuc(c, ".L")) + dis2(avuc(c, ".R"))) / 2
        c.location.x += 0.05 - orta.x
        c.location.y += 0.84 - orta.y
        bpy.context.view_layer.update()
        yere_bas(kardes, kok, guverte_z(c.location.y))
        gulus(kardes, 0.3)
        e1, e2 = dis2(avuc(c, ".L")), dis2(avuc(c, ".R"))
        ust_el, alt_el = (e1, e2) if e1.z > e2.z else (e2, e1)
        bas_ = MANDAR[0]
        cizim += [("cubuk", "Mandar", bas_, ust_el, 0.012, "halat"),
                  ("cubuk", "Mandar", ust_el, alt_el, 0.012, "halat"),
                  ("cubuk", "Mandar", alt_el, Vector((0.12, 0.95, guverte_z(0.95) + 0.25)), 0.012, "halat")]
    elif an == "dumen":      # sits on the crate, watching the sail fill
        hareket(kardes, "otur")
        ic2, dis2 = yerlestir(kardes, kok, (0.30, -1.6), math.radians(-90), SANDIK_Z, True)
        ayaklar_yere(kardes, ic2, dis2, 0.40, 0.12)
        bas(c, -16.0, -22.0); gulus(kardes, 0.35)
    elif an in ("olta", "tuttu"):   # sits on the deck, trolling over the port quarter
        akt, tik = hareket(kardes, "olta")
        if an == "tuttu":    # rod up, the catch swinging in over the rail
            akt, tik = hareket(kardes, "cekti", sadece=UST)
        ic2, dis2 = yerlestir(kardes, kok, (0.10, 0.0), math.radians(-45), guverte_z(0.0), True)
        yere_bas(kardes, kok, guverte_z(0.0))
        el_uygula(kardes, kavra, ".R")
        bas(c, 0.0, {"olta": 8.0, "tuttu": -16.0}[an]); gulus(kardes, {"olta": 0.2, "tuttu": 0.9}[an])
        bpy.context.view_layer.update()
        el = dis2(avuc(c, ".R"))
        yon = olta_yonu(akt, tik, dis2)
        uc = el + yon * 2.1
        cizim.append(("cubuk", "Olta", el - yon * 0.32, uc, 0.022, "kusak"))
        if an == "olta":
            cizim.append(("cubuk", "Misina", uc, Vector((uc.x - 0.4, uc.y - 0.5, 0.05)), 0.006, "halat"))
        else:
            balik = uc + Vector((0.0, 0.0, -0.75))
            cizim += [("cubuk", "Misina", uc, balik + Vector((0, 0, 0.26)), 0.006, "halat"), ("balik", balik)]
    else:                    # varis: beside the mast, points at the town, coil in the other hand
        hareket(kardes, "dur")
        hareket(kardes, "goster", sadece=UST_SAG)
        y = 0.72
        ic2, dis2 = yerlestir(kardes, kok, (-0.34, y), math.pi, guverte_z(y), False)
        yere_bas(kardes, kok, guverte_z(y))
        el_uygula(kardes, kavra, ".R", duz=("finger2",))
        el_uygula(kardes, kavra, ".L")
        bas(c, -6.0, -4.0); gulus(kardes, 0.5)
        bpy.context.view_layer.update()
        cizim.append(("kangal", dis2(avuc(c, ".L")) + Vector((0, 0, -0.08))))
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
