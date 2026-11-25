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
def kas(guc):
    """Balanced anatomical musculature for a 23-year-old natural athlete: broadens the V-taper
    and shoulders while keeping deltoid/elbow/forearm volumes clean so joints deform without pinching."""
    g = {"armslegs/{s}-upperarm-muscle-incr": 0.42,
         "armslegs/{s}-upperarm-scale-depth-incr": 0.22, "armslegs/{s}-upperarm-scale-horiz-incr": 0.22,
         "armslegs/{s}-upperarm-shoulder-muscle-incr": 0.28,
         "armslegs/{s}-lowerarm-muscle-incr": 0.38,
         "armslegs/{s}-lowerarm-scale-depth-incr": 0.18, "armslegs/{s}-lowerarm-scale-horiz-incr": 0.20,
         "torso/torso-vshape-incr": 0.48, "torso/torso-muscle-dorsi-incr": 0.38,
         "torso/torso-muscle-pectoral-incr": 0.34,
         "torso/torso-scale-horiz-incr": 0.10, "torso/torso-scale-depth-incr": 0.08,
         "neck/neck-scale-horiz-incr": 0.18, "neck/neck-scale-depth-incr": 0.12}
    return {k: v * guc for k, v in g.items()}


YUSUF = dict(
    name="yusuf",
    m=dict(sex=1.0, age=0.455, muscle=0.72, weight=0.48, boy=1.81, proportions=0.52, race=IRK),  # 23, natural athlete
    goz_olcek=(1.12, 1.14),
    atletik_gomlek=True,
    kas_indir=-0.0055,
    sac_on_indir=0.017,
    yuz_gen={
        "head/head-oval": 0.18,
        "head/head-square": 0.20,
        "head/head-scale-horiz-decr": 0.14,                 # balanced masculine oval-square face (photos 1-2)
        "head/head-scale-vert-incr": 0.05,
        "forehead/forehead-scale-vert-decr": 0.12,          # natural forehead proportion
        "eyebrows/eyebrows-trans-down": 0.36,               # low, strong masculine brow line close to eyes
        "eyebrows/eyebrows-angle-down": 0.18,
        "eyes/{s}-eye-height1-decr": 0.12,                  # calm, slightly hooded masculine upper lid
        "eyes/{s}-eye-eyefold-down": 0.20,
        "eyes/{s}-eye-scale-incr": 0.04,
        "nose/nose-scale-vert-incr": 0.14,                  # straight, masculine bridge & projection
        "nose/nose-scale-depth-incr": 0.16,
        "nose/nose-scale-horiz-decr": 0.04,
        "nose/nose-point-width-decr": 0.04,
        "mouth/mouth-upperlip-volume-incr": 0.28,           # full, well-defined lips (photo 1)
        "mouth/mouth-lowerlip-volume-incr": 0.34,
        "mouth/mouth-scale-horiz-incr": 0.06,
        "cheek/{s}-cheek-bones-incr": 0.16,                 # smooth athletic cheek planes (no gaunt pinch!)
        "cheek/{s}-cheek-volume-decr": 0.08,
        "chin/chin-height-incr": 0.05,
        "chin/chin-prominent-incr": 0.14,
        "chin/chin-width-incr": 0.08,
        "chin/chin-bones-incr": 0.32,                       # clean masculine jawline under short beard
        "head/head-fat-decr": 0.22,
        **kas(0.95),                                        # proportionate athletic V-taper, shoulders, chest & arms
        "stomach/stomach-tone-incr": 0.65,                  # flat, toned waist
        "hip/hip-scale-horiz-decr": 0.16,
    },
    ten=(0.30, 0.62), sac=(0.45, 0.48), goz=("mavi", 0.38),
    sac_stil="kisa_kivircik", kakul=False, sakal="kisa_sakal", sakal_renk=(0.52, 0.36),
    sac_parlak=False, sac_boya=True, sac_hacim=0.008,
    kas_stil="thick_warm", kas_kalin=1.28, kas_kavis=0.26,
    yuz=("smile", 0.12), bas_don=0.0, bas_eg=0.0,
    giysi=[("clothes", "male_casualsuit01", ["#F2ECE1", "#3B3027"]), ("clothes", "shoes06", "#4E3829")],
)

# Younger brother (Latif): 17 years old, NOT an athlete — narrow teen shoulders, slim build, bright blue eyes,
# tousled brown hair falling naturally on the forehead, no beard. Sand laced linen tunic (photo 3).
LATIF = dict(
    name="latif",
    m=dict(sex=1.0, age=0.30, muscle=0.30, weight=0.36, boy=1.74, proportions=0.48, race=IRK),  # 17, slim teen
    goz_olcek=(1.15, 1.18),
    ince_gomlek=True,
    bagcikli_yaka=True,
    kas_indir=-0.0035,
    sac_on_indir=0.019,
    yuz_gen={
        "head/head-oval": 0.24,
        "head/head-square": 0.06,
        "head/head-scale-horiz-decr": 0.10,
        "head/head-scale-vert-incr": 0.02,
        "forehead/forehead-scale-vert-decr": 0.14,
        "eyebrows/eyebrows-trans-down": 0.16,
        "eyes/{s}-eye-scale-incr": 0.14,                    # large, vivid sky-blue eyes (photo 3)
        "eyes/{s}-eye-height1-incr": 0.08,
        "nose/nose-scale-vert-incr": 0.06,
        "nose/nose-scale-depth-incr": 0.08,
        "nose/nose-point-width-incr": 0.05,                 # soft rounded nose tip
        "mouth/mouth-upperlip-volume-incr": 0.22,
        "mouth/mouth-lowerlip-volume-incr": 0.26,
        "chin/chin-height-incr": 0.02,
        "chin/chin-width-decr": 0.08,                       # youthful tapered chin
        "chin/chin-bones-incr": 0.18,
        "cheek/{s}-cheek-bones-incr": 0.14,                 # smooth youthful cheek contour (no hollow pinch!)
        "cheek/{s}-cheek-volume-decr": 0.06,
        "head/head-fat-decr": 0.18,
        # 17yo non-athlete slim teen frame: narrower shoulders, slim arms and torso
        # a lean boy, not a soft one (Yusuf 2026-11-24: "Latif feminen duruyor", hips too far back):
        # shoulders stay square over narrow hips, flat seat and belly, the pelvis sits under him
        "torso/torso-vshape-incr": 0.18,
        "stomach/stomach-tone-incr": 0.45,
        "stomach/stomach-pregnant-decr": 0.30,
        "hip/hip-scale-horiz-decr": 0.24,
        "hip/hip-scale-depth-decr": 0.18,
        "hip/hip-trans-forward": 0.25,
        "buttocks/buttocks-volume-decr": 0.60,
        "torso/torso-scale-depth-decr": 0.10,
        "torso/torso-muscle-pectoral-decr": 0.18,
        "torso/torso-muscle-dorsi-decr": 0.22,
        "armslegs/{s}-upperarm-shoulder-muscle-decr": 0.25,
        "armslegs/{s}-upperarm-muscle-decr": 0.22,
        "armslegs/{s}-upperarm-scale-horiz-decr": 0.16,
        "armslegs/{s}-upperarm-scale-depth-decr": 0.14,
        "armslegs/{s}-lowerarm-muscle-decr": 0.20,
        "armslegs/{s}-lowerarm-scale-horiz-decr": 0.14,
        "neck/neck-scale-horiz-decr": 0.16,
        "neck/neck-scale-depth-decr": 0.10,
    },
    ten=(0.23, 0.56), sac=(0.46, 0.48), goz=("mavi", 0.12),
    sac_stil="iki_kat_kisa", kakul=False,
    sac_parlak=False, sac_boya=True, sac_hacim=0.006,
    kas_stil="thick_warm", kas_kalin=0.90, kas_kavis=0.40,
    yuz=("smile", 0.15), bas_don=0.0, bas_eg=0.0,
    giysi=[("clothes", "male_casualsuit06", ["#DECBA8", "#947340"]), ("clothes", "shoes02", "#725C48")],
)
ABI = YUSUF
KARDES = LATIF

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


def _tam_agac(p):
    """BVHTree of the complete 13,380-vertex morphed body (p['co']) before garment face deletion."""
    from insan import mh
    _, _, faces = mh.base()
    bf = [tuple(f) for f, _, g in faces if g == "body"]
    return BVHTree.FromPolygons([Vector(x) for x in p["co"]], bf)


def _kaydir(me, yeni):
    """Move mesh vertices to yeni[i]; baked expressions are shape keys, so move every key block."""
    fark = [yeni[i] - v.co for i, v in enumerate(me.vertices)]
    for kb in (me.shape_keys.key_blocks if me.shape_keys else []):
        for i, d in enumerate(fark):
            kb.data[i].co += d
    for v, d in zip(me.vertices, fark):
        v.co += d
    me.update()


def _tam_govde(name, co, weights, sex, hidden):
    """Build body from the full 13,380-vertex base.obj (instead of the 1,591-poly male1591 proxy)
    so facial anatomy, lips, nose, pectorals, and dual-layer beard masks have full hero resolution.
    Keeps upper-chest/clavicle skin vertices unhidden so open-collar shirts reveal real 3D chest skin."""
    from insan import mh, ten
    _, uv, faces = mh.base()
    P_b = mh.to_blender(co)
    acik_gogus = {i for i in range(len(P_b)) if P_b[i, 2] > 1.22 and abs(P_b[i, 0]) < 0.095 and P_b[i, 1] < -0.03}
    gizli = set(hidden) - acik_gogus
    bf = [(f, u) for f, u, g in faces if g == "body" and not all(int(i) in gizli for i in f)]
    used = sorted({i for f, _ in bf for i in f})
    remap = {o_: n for n, o_ in enumerate(used)}
    body = kadro._mesh(name, co[used], [([remap[i] for i in f], u) for f, u in bf], uv)
    ten.apply_skin_masks(body, used)
    kadro._groups(body, weights, remap)
    body.data.polygons.foreach_set("use_smooth", [True] * len(body.data.polygons))
    body.data.materials.clear()
    return body


def _tam_ten_mat(name, srgb, sex, e):
    """Full 4-channel gouache skin (blush, highlight, natural 2-tone lips, form-AO, plus Paralives
    dual-layer stubble cheek-fade mask in skin_extra.B) wrapped in the cel toon shader."""
    mel, und = e["ten"]
    sakal_stil = e.get("sakal")
    sakal_yogun = 0.56 if sakal_stil in ("kisa_sakal", "kirli") else 0.0
    hair_c = mz.hair(*e.get("sakal_renk", e["sac"]))
    m = mz.skin_material(name, mel, und, sex=sex, blush_boost=0.85,
                         sakal_yogun=sakal_yogun, sakal_renk=hair_c)
    bs = m.node_tree.nodes["Principled BSDF"]
    base_sock = bs.inputs["Base Color"].links[0].from_socket if bs.inputs["Base Color"].links else None
    return anime.toon(m, base_sock, shade=anime.SEFTALI, rim=0.14, face_attr="yuz_w")


def _bant_genisligi(z, ztop):
    if z > ztop - 0.017:
        return 0.035                  # moustache
    if z > ztop - 0.034:
        return 0.029                  # around mouth corners
    return 0.024                      # chin


def _yuz_sarma_uygula(mat, guc=0.60, taban=0.22):
    """Calibrate N.L on a toon face/beard material so facial planes cross the cel ramp gently without
    splitting the face in half when turned away from the sun."""
    if not (mat and mat.use_nodes):
        return
    for nd in mat.node_tree.nodes:
        if nd.type == "MATH" and nd.operation == "MULTIPLY_ADD":
            if nd.inputs[0].links and nd.inputs[0].links[0].from_node.type == "VECT_MATH":
                nd.inputs[1].default_value = guc
                nd.inputs[2].default_value = taban


def yuz_isik_duzelt(p, e):
    """Restore 3D sculpted facial normals on the 13,380-vertex body and lower eyebrows to match photos."""
    body = p["body"]
    with bpy.context.temp_override(object=body, active_object=body, selected_objects=[body]):
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
    # Reduce yuz_w to 0.65 so 35% of real 3D nose/cheekbone/lip diffuse shading blends with smooth wrap
    if "yuz_w" in body.data.attributes:
        yw = body.data.attributes["yuz_w"]
        vals = np.empty(len(body.data.vertices), dtype=np.float32)
        yw.data.foreach_get("value", vals)
        yw.data.foreach_set("value", (vals * 0.65).astype(np.float32))
    for m in body.data.materials:
        _yuz_sarma_uygula(m, guc=0.60, taban=0.24)
    kas_dz = float(e.get("kas_indir", 0.0))
    kas_ob = _parca(p, "_eyebrows")
    if kas_ob and abs(kas_dz) > 1e-5:
        me_k = kas_ob.data
        yeni_k = []
        for v in me_k.vertices:
            ic_egim = 1.15 if abs(v.co.x) < 0.028 else 0.85
            yeni_k.append(v.co + Vector((0.0, -0.0012, kas_dz * ic_egim)))
        _kaydir(me_k, yeni_k)


def sakal_kirp(p, e):
    """Dual-layer short beard & moustache (Photos 1-2): Layer 1 is already painted seamlessly on the
    13,380-vertex skin shader (skin_extra.B). Layer 2 here shapes the 3D sculpted moustache, soul-patch,
    and chin contour flush on base.obj with unified warm peach wrap shading."""
    sakal = _parca(p, "_beard")
    if not sakal:
        return
    me = sakal.data
    agac = _tam_agac(p)
    ztop = max(v.co.z for v in me.vertices if abs(v.co.x) < 0.012)
    yanak_ust = ztop - 0.015

    def yogunluk(co):
        ax, dz = abs(co.x), ztop - co.z
        # Clean bare skin pockets under left/right lower lip corners framing the soul patch
        if 0.015 < dz < 0.032 and 0.007 < ax < 0.025:
            return 0.0
        if dz <= 0.016 and ax <= 0.033:                         # sculpted 3D moustache
            philtrum = 0.72 if ax < 0.0035 else 1.0
            return 0.94 * philtrum * (1.0 - 0.30 * max(0.0, (ax - 0.022) / 0.012))
        if 0.016 < dz < 0.032 and ax <= 0.007:                  # soul patch
            return 0.85
        d = max(ax - _bant_genisligi(co.z, ztop), 0.0)
        if d > 0.018:
            return 0.0                                          # cheeks handled cleanly by skin_extra.B!
        y = 0.80 if d == 0.0 else 0.55 * max(0.0, 1.0 - d / 0.018)
        if d > 0.0:
            y *= min(1.0, max(0.0, (yanak_ust + 0.004 - co.z) / 0.012))
        return y

    yeni = []
    for v in me.vertices:
        yakin, nrm, _, d = agac.find_nearest(v.co)
        y_ = yogunluk(v.co)
        pay = 0.0022 if (v.co.z > ztop - 0.016 and y_ > 0.5) else (0.0014 * y_)
        yeni.append(yakin + nrm * pay if yakin is not None else v.co.copy())
    _kaydir(me, yeni)
    zs = [v.co.z for v in me.vertices]
    alt = min(zs) + 0.38 * (max(zs) - min(zs))
    arka = p["arm"].data.bones["head"].head_local.y - 0.012
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < alt or v.co.y > arka or yogunluk(v.co) < 0.08],
                     context="VERTS")
    bm.to_mesh(me); bm.free(); me.update()
    at = me.attributes.new("yogun", "FLOAT", "POINT")
    at.data.foreach_set("value", [yogunluk(v.co) * min(1.0, max(0.0, (v.co.z - alt) / 0.014))
                                  for v in me.vertices])
    yw = me.attributes.new("yuz_w", "FLOAT", "POINT")
    yw.data.foreach_set("value", [0.65] * len(me.vertices))
    if hasattr(sakal, "visible_shadow"):
        sakal.visible_shadow = False

    hair = np.array([0.09, 0.08, 0.08]) + mz.hair(*e.get("sakal_renk", e["sac"])) * 0.88
    skin = np.asarray(mz.skin(*e["ten"]), float)
    m = bpy.data.materials.new(p["name"] + "_sakal_boya"); m.use_nodes = True
    n, L = m.node_tree.nodes, m.node_tree.links
    at_n = n.new("ShaderNodeAttribute"); at_n.attribute_name = "yogun"
    renk = mz.lin(hair * 0.72 + skin * 0.28)
    col = mz._mix_rgba(n, L, 1.0, renk, renk)
    L.new(col, n["Principled BSDF"].inputs["Base Color"])
    L.new(at_n.outputs["Fac"], n["Principled BSDF"].inputs["Alpha"])
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "DITHERED"
    me.materials[0] = anime.toon(m, col, shade=anime.SEFTALI, rim=0.08, face_attr="yuz_w")
    _yuz_sarma_uygula(me.materials[0], guc=0.60, taban=0.24)


def atletik_gomlek(p):
    """Tailor the 3D white button-down shirt (male_casualsuit01) onto the athletic V-taper body:
    preserves its 3D turn-down collar, open V-neck front, button placket, and cuffs while gently
    opening the front V-collar slightly wider to reveal the upper chest skin and preventing any
    skin poke-through."""
    gom = next((o for o in p["parts"] if "casualsuit" in o.name), None)
    if not gom:
        return
    me = gom.data
    ust_v = {vi for poly in me.polygons if poly.material_index == 0 for vi in poly.vertices}
    alt_v = {vi for poly in me.polygons if poly.material_index == 1 for vi in poly.vertices}
    if not ust_v:
        return
    agac = _tam_agac(p)
    zs = [me.vertices[i].co.z for i in ust_v]
    z_min, z_max = min(zs), max(zs)
    yeni = [v.co.copy() for v in me.vertices]
    for i in ust_v:
        if i in alt_v:
            continue
        co = me.vertices[i].co.copy()
        ax = abs(co.x)
        t_z = (co.z - z_min) / max(1e-4, z_max - z_min)
        # Gently open the front V-collar of the white shirt slightly wider so upper chest skin shows cleanly
        if co.y < -0.055 and t_z > 0.74 and ax < 0.072:
            v_ac = anime.ss(t_z, 0.74, 0.96) * (1.0 - anime.ss(ax, 0.048, 0.072))
            sx = 1.0 if co.x >= 0.0 else -1.0
            co.x += sx * 0.0085 * v_ac
            co.y -= 0.0025 * v_ac
        # Pull sleeve cuffs 2.6 cm back up the forearm and taper them snugly so both gripping hands are 100% visible
        if ax > 0.34:
            k_w = anime.ss(ax, 0.34, 0.44)
            sx = 1.0 if co.x >= 0.0 else -1.0
            co.x -= sx * 0.026 * k_w
        yakin, nrm, _, _ = agac.find_nearest(co)
        if yakin is not None:
            if ax > 0.34:
                k_w = anime.ss(ax, 0.34, 0.44)
                co = co * (1.0 - 0.65 * k_w) + (yakin + nrm * 0.0042) * (0.65 * k_w)
            fark = (co - yakin).dot(nrm)
            if fark < 0.0042:
                co += nrm * (0.0045 - fark)
        yeni[i] = co
    # Prevent any skin poke-through on trousers
    for i in alt_v:
        co = yeni[i]
        yakin, nrm, _, _ = agac.find_nearest(co)
        if yakin is not None:
            fark = (co - yakin).dot(nrm)
            if fark < 0.0035:
                yeni[i] = co + nrm * (0.0038 - fark)
    _kaydir(me, yeni)


def ince_gomlek(p):
    """Collapse the puffy shoulder pads and loose sleeves of male_casualsuit06 onto the 17-year-old
    brother's slim, non-athlete frame and tuck the trouser waistband cleanly inside the shirt hem."""
    gom = next((o for o in p["parts"] if "casualsuit" in o.name), None)
    if not gom:
        return
    me = gom.data
    ust_v = {vi for poly in me.polygons if poly.material_index == 0 for vi in poly.vertices}
    alt_v = {vi for poly in me.polygons if poly.material_index == 1 for vi in poly.vertices}
    if not ust_v:
        return
    agac = _tam_agac(p)
    zs = [me.vertices[i].co.z for i in ust_v]
    z_min, z_max = min(zs), max(zs)
    yeni = [v.co.copy() for v in me.vertices]
    for i in ust_v:
        if i in alt_v:
            continue
        co = me.vertices[i].co.copy()
        t_z = (co.z - z_min) / max(1e-4, z_max - z_min)
        hem_koru = anime.ss(t_z, 0.0, 0.16)
        yakin, nrm, _, _ = agac.find_nearest(co)
        if yakin is not None:
            siki = 0.72 * hem_koru
            hedef = yakin + nrm * 0.0062
            co = co * (1.0 - siki) + hedef * siki
        yeni[i] = co
    # Tuck trouser waistband under the shirt hem so brown triangles never poke through!
    for i in alt_v:
        co = yeni[i]
        if co.z > z_min - 0.04:
            yakin, nrm, _, _ = agac.find_nearest(co)
            if yakin is not None:
                yeni[i] = co * 0.35 + (yakin + nrm * 0.0015) * 0.65
    _kaydir(me, yeni)


def bagcikli_yaka_doku(p):
    """Paint a subtle, tailored laced V-neck collar directly into the brother's sand linen tunic
    shader (Object coordinates on the front chest) — 100% flush with the cloth, tonal linen palette."""
    gom = next((o for o in p["parts"] if "casualsuit" in o.name), None)
    if not gom or not gom.data.materials:
        return
    mat = gom.data.materials[0]
    if not (mat and mat.use_nodes):
        return
    ust_zs = [v.co.z for v in gom.data.vertices if abs(v.co.x) < 0.025 and v.co.y < -0.05]
    z_ust = (max(ust_zs) + 0.006) if ust_zs else 1.45
    z_alt = z_ust - 0.092
    w_yarim = 0.044

    W, H = 512, 512
    j, i = np.mgrid[0:H, 0:W]
    u = ((i + 0.5) / W) * 2.0 - 1.0
    v = (j + 0.5) / H
    au = np.abs(u)
    t_v = np.clip((v - 0.08) / 0.90, 0.0, 1.0)
    v_kenar = 0.05 + 0.42 * (t_v ** 0.95)
    in_y = (v >= 0.06) & (v <= 1.0)

    base_c = mz._rgb("#DECBA8")
    ic_c = mz._rgb("#B58E70")        # warm shadowed chest skin / inner linen shadow (never harsh black!)
    biye_c = mz._rgb("#D2BE98")      # subtle stitched linen placket border
    dikis_c = mz._rgb("#A48A66")     # fine inner edge seam
    ip_c = mz._rgb("#EAE0CA")        # natural tonal linen cord
    ip_golge = mz._rgb("#9C8262")

    col = np.broadcast_to(base_c, (H, W, 3)).copy()
    ic_m = anime.ss(v_kenar - au, -0.015, 0.015) * anime.ss(v, 0.08, 0.12)
    col = col * (1.0 - ic_m[..., None]) + ic_c * ic_m[..., None]
    d_kenar = au - v_kenar
    biye_m = (1.0 - anime.ss(np.abs(d_kenar - 0.055), 0.038, 0.055)) * anime.ss(v, 0.05, 0.10)
    col = col * (1.0 - biye_m[..., None]) + biye_c * biye_m[..., None]
    seam_m = (1.0 - anime.ss(np.abs(d_kenar), 0.005, 0.014)) * anime.ss(v, 0.08, 0.12)
    col = col * (1.0 - 0.55 * seam_m[..., None]) + dikis_c * (0.55 * seam_m[..., None])

    vs_ = [0.22, 0.45, 0.68, 0.90]
    ip_mask = np.zeros((H, W), dtype=np.float64)
    golge_mask = np.zeros((H, W), dtype=np.float64)

    def cizgi(u0, v0, u1, v1, kalin=0.020):
        du, dv = u1 - u0, v1 - v0
        L2 = du * du + dv * dv + 1e-9
        t_ = np.clip(((u - u0) * du + (v - v0) * dv) / L2, 0.0, 1.0)
        dist = np.hypot(u - (u0 + t_ * du), v - (v0 + t_ * dv))
        dist_g = np.hypot(u - (u0 + t_ * du), (v + 0.012) - (v0 + t_ * dv))
        return 1.0 - anime.ss(dist, kalin * 0.5, kalin), 1.0 - anime.ss(dist_g, kalin * 0.5, kalin * 1.2)

    for k in range(len(vs_) - 1):
        v0, v1 = vs_[k], vs_[k + 1]
        w0 = 0.05 + 0.42 * (((v0 - 0.08) / 0.90) ** 0.95) + 0.045
        w1 = 0.05 + 0.42 * (((v1 - 0.08) / 0.90) ** 0.95) + 0.045
        for s in (-1.0, 1.0):
            m_ip, m_g = cizgi(s * w0, v0, -s * w1, v1, 0.020)
            ip_mask = np.maximum(ip_mask, m_ip)
            golge_mask = np.maximum(golge_mask, m_g)
    w_top = 0.05 + 0.42 * (((vs_[-1] - 0.08) / 0.90) ** 0.95) + 0.045
    for s in (-1.0, 1.0):
        m_ip, m_g = cizgi(s * w_top, vs_[-1], s * (w_top * 0.75), vs_[-1] - 0.30, 0.017)
        ip_mask = np.maximum(ip_mask, m_ip)
        golge_mask = np.maximum(golge_mask, m_g)

    golge_mask = np.clip(golge_mask * (1.0 - ip_mask), 0.0, 1.0) * 0.35
    col = col * (1.0 - golge_mask[..., None]) + ip_golge * golge_mask[..., None]
    col = col * (1.0 - ip_mask[..., None]) + ip_c * ip_mask[..., None]
    alpha = np.clip(np.maximum.reduce([ic_m, biye_m, seam_m, ip_mask, golge_mask]) * in_y, 0.0, 1.0)

    img = bpy.data.images.new(p["name"] + "_yaka_tex", W, H, alpha=True)
    img.pixels.foreach_set(np.concatenate([mz.lin(col), alpha[..., None]], -1).astype(np.float32).ravel())
    img.update(); img.pack()

    # Bake collar projection on the undeformed T-pose shirt vertices so sitting/bending never shifts it
    attr = gom.data.attributes.new(name="yaka_uv", type="FLOAT_VECTOR", domain="POINT")
    uv_data = np.zeros((len(gom.data.vertices), 3), dtype=np.float32)
    for idx_v, v_ in enumerate(gom.data.vertices):
        u_val = (v_.co.x / (2.0 * w_yarim)) + 0.5
        v_val = (v_.co.z - z_alt) / max(1e-5, (z_ust - z_alt))
        on_val = 1.0 if (v_.co.y < -0.02 and 0.0 <= u_val <= 1.0 and 0.0 <= v_val <= 1.02) else 0.0
        uv_data[idx_v] = (u_val, v_val, on_val)
    attr.data.foreach_set("vector", uv_data.ravel())

    n, L = mat.node_tree.nodes, mat.node_tree.links
    rgb = next((nd for nd in n if nd.type == "RGB"), None)
    if rgb is None:
        return
    at_node = n.new("ShaderNodeAttribute")
    at_node.attribute_name = "yaka_uv"
    sep = n.new("ShaderNodeSeparateXYZ"); L.new(at_node.outputs["Vector"], sep.inputs["Vector"])
    tx = n.new("ShaderNodeTexImage"); tx.image = img; tx.extension = "CLIP"
    L.new(at_node.outputs["Vector"], tx.inputs["Vector"])
    on_m = mz._math(n, L, "GREATER_THAN", sep.outputs["Z"], 0.5)
    fac = mz._math(n, L, "MULTIPLY", tx.outputs["Alpha"], on_m)
    hedefler = [lk.to_socket for lk in L if lk.from_socket == rgb.outputs[0]]
    mix = mz._mix_rgba(n, L, fac, rgb.outputs[0], tx.outputs["Color"])
    for sk in hedefler:
        L.new(mix, sk)


def acik_yaka_gomlek_doku(p, e):
    """Paint an open-collar button-down shirt (Paralives HumanShirtShortSleeves1OpenButtonPec & CK3
    portrait_cloth style) onto Yusuf's shirt using a baked T-pose vertex attribute (gomlek_uv):
    unbuttoned V-neck opening revealing upper chest skin & clavicle shade, folded turn-down collar
    wings (lapels) with drop shadow, full-length vertical front button placket, horn buttons, and
    subtle pectoral drape folds."""
    gom = next((o for o in p["parts"] if "casualsuit" in o.name), None)
    if not gom or not gom.data.materials:
        return
    mat = gom.data.materials[0]
    if not (mat and mat.use_nodes):
        return
    ust_v = {vi for poly in gom.data.polygons if poly.material_index == 0 for vi in poly.vertices}
    on_zs = [gom.data.vertices[i].co.z for i in ust_v if abs(gom.data.vertices[i].co.x) < 0.03 and gom.data.vertices[i].co.y < -0.05]
    tum_zs = [gom.data.vertices[i].co.z for i in ust_v]
    z_ust = (max(on_zs) + 0.005) if on_zs else 1.48
    z_alt = (min(tum_zs) + 0.015) if tum_zs else 0.96
    w_yarim = 0.16

    W, H = 768, 768
    j, i = np.mgrid[0:H, 0:W]
    u = ((i + 0.5) / W) * 2.0 - 1.0          # -1..+1 across front torso (-0.16m..+0.16m)
    v = (j + 0.5) / H                        # 0 at bottom shirt hem, 1 at top collar rim
    au = np.abs(u)

    base_c = mz._rgb("#566343")              # olive linen shirt base
    ten_c = np.asarray(mz.skin(*e["ten"]), float)
    ten_golge = ten_c * np.array([0.80, 0.74, 0.72])
    yaka_ust = mz._rgb("#687752")            # sunlit folded collar lapel & placket highlight
    yaka_alt = mz._rgb("#343D28")            # under-lapel drop shadow & deep crease
    pat_c = mz._rgb("#5F6D4B")               # vertical center button placket
    dikis_c = mz._rgb("#3D472F")             # double stitch seam
    dugme_c = mz._rgb("#E4D8C1")             # warm natural horn/bone buttons
    dugme_g = mz._rgb("#8E7F68")

    col = np.broadcast_to(base_c, (H, W, 3)).copy()
    alpha = np.zeros((H, W), dtype=np.float64)

    # 1. Subtle pectoral & waist tension folds (Paralives 1OpenButtonPec style)
    pec_fold = np.exp(-((v - (0.62 + 0.04 * (au / 0.55) ** 2)) / 0.042) ** 2) * anime.ss(au, 0.10, 0.24) * (1.0 - anime.ss(au, 0.62, 0.88))
    waist_fold = (0.5 + 0.5 * np.sin((v - 0.18) * 34.0 + au * 6.0)) * anime.ss(v, 0.10, 0.22) * (1.0 - anime.ss(v, 0.48, 0.62)) * (1.0 - anime.ss(au, 0.45, 0.75))
    fold_m = np.clip(0.32 * pec_fold + 0.14 * waist_fold, 0.0, 0.45)
    col = col * (1.0 - fold_m[..., None]) + yaka_alt * fold_m[..., None]
    alpha = np.maximum(alpha, fold_m * 0.85)

    # 2. Full-length vertical center button placket (from bottom hem v=0.01 up to V-opening base v=0.72)
    pat_w = 0.078
    pat_in = (1.0 - anime.ss(au, pat_w * 0.82, pat_w)) * anime.ss(v, 0.01, 0.03) * (1.0 - anime.ss(v, 0.71, 0.75))
    pat_seam = ((1.0 - anime.ss(np.abs(au - pat_w), 0.004, 0.013)) + (1.0 - anime.ss(np.abs(u + pat_w * 0.55), 0.003, 0.010))) * anime.ss(v, 0.01, 0.03) * (1.0 - anime.ss(v, 0.71, 0.75))
    pat_seam = np.clip(pat_seam, 0.0, 1.0)
    col = col * (1.0 - pat_in[..., None]) + pat_c * pat_in[..., None]
    col = col * (1.0 - 0.75 * pat_seam[..., None]) + dikis_c * (0.75 * pat_seam[..., None])
    alpha = np.maximum.reduce([alpha, pat_in, pat_seam])

    # 3. Open V-neck cutout (v = 0.70..1.00): unbuttoned top revealing chest skin & clavicle contour
    t_v = np.clip((v - 0.70) / 0.29, 0.0, 1.0)
    v_kenar = 0.018 + 0.30 * (t_v ** 0.88)             # widens smoothly to ~9.5 cm at the collar top
    acik_m = anime.ss(v_kenar - au, -0.010, 0.010) * anime.ss(v, 0.695, 0.725)
    # Warm sunlit chest skin with soft cloth-edge shadow & sternal groove
    kenar_g = anime.ss(au / np.maximum(1e-4, v_kenar), 0.58, 1.0)
    sternum_g = np.exp(-(u / 0.035) ** 2) * 0.25 * (1.0 - t_v * 0.5)
    ten_renk = ten_c * (1.0 - (0.42 * kenar_g + sternum_g)[..., None]) + ten_golge * (0.42 * kenar_g + sternum_g)[..., None]
    col = col * (1.0 - acik_m[..., None]) + ten_renk * acik_m[..., None]
    alpha = np.maximum(alpha, acik_m)

    # 4. Folded turn-down collar wings (lapels) flanking the open V-neck
    d_v = au - v_kenar
    yaka_gen = 0.085 + 0.115 * np.sin(np.clip(t_v, 0.0, 1.0) * math.pi * 0.82)
    lapel_m = anime.ss(d_v, -0.006, 0.008) * (1.0 - anime.ss(d_v, yaka_gen - 0.012, yaka_gen + 0.008)) * anime.ss(v, 0.68, 0.72)
    lapel_golge = anime.ss(d_v, yaka_gen - 0.008, yaka_gen + 0.006) * (1.0 - anime.ss(d_v, yaka_gen + 0.022, yaka_gen + 0.048)) * anime.ss(v, 0.67, 0.71)
    lapel_dikis = (1.0 - anime.ss(np.abs(d_v - (yaka_gen - 0.015)), 0.003, 0.010)) * anime.ss(v, 0.69, 0.72)
    ic_dikis = (1.0 - anime.ss(np.abs(d_v - 0.008), 0.003, 0.010)) * anime.ss(v, 0.69, 0.72)
    col = col * (1.0 - 0.72 * lapel_golge[..., None]) + yaka_alt * (0.72 * lapel_golge[..., None])
    col = col * (1.0 - lapel_m[..., None]) + yaka_ust * lapel_m[..., None]
    col = col * (1.0 - 0.75 * np.maximum(lapel_dikis, ic_dikis)[..., None]) + dikis_c * (0.75 * np.maximum(lapel_dikis, ic_dikis)[..., None])
    alpha = np.maximum.reduce([alpha, lapel_m, lapel_golge, lapel_dikis, ic_dikis])

    # 5. Shirt buttons along the front placket + 1 unbuttoned button on the upper lapel flap
    dugmeler = [(0.0, 0.67, 0.022), (0.0, 0.53, 0.022), (0.0, 0.39, 0.022), (0.0, 0.25, 0.022), (0.0, 0.11, 0.022),
                (-0.14, 0.83, 0.019)]
    for bu, bv, br in dugmeler:
        dist = np.hypot(u - bu, (v - bv) * 1.45)
        b_m = 1.0 - anime.ss(dist, br * 0.65, br)
        b_ring = (1.0 - anime.ss(np.abs(dist - br * 0.68), 0.0025, 0.006)) * b_m
        col = col * (1.0 - b_m[..., None]) + dugme_c * b_m[..., None]
        col = col * (1.0 - 0.7 * b_ring[..., None]) + dugme_g * (0.7 * b_ring[..., None])
        alpha = np.maximum(alpha, b_m)

    alpha = np.clip(alpha * (v >= 0.01) * (v <= 1.0), 0.0, 1.0)
    img = bpy.data.images.new(p["name"] + "_acik_gomlek_tex", W, H, alpha=True)
    img.pixels.foreach_set(np.concatenate([mz.lin(col), alpha[..., None]], -1).astype(np.float32).ravel())
    img.update(); img.pack()

    attr = gom.data.attributes.new(name="gomlek_uv", type="FLOAT_VECTOR", domain="POINT")
    uv_data = np.zeros((len(gom.data.vertices), 3), dtype=np.float32)
    for idx_v, v_ in enumerate(gom.data.vertices):
        u_val = (v_.co.x / (2.0 * w_yarim)) + 0.5
        v_val = (v_.co.z - z_alt) / max(1e-5, (z_ust - z_alt))
        on_val = 1.0 if (v_.co.y < -0.015 and 0.0 <= u_val <= 1.0 and 0.0 <= v_val <= 1.03) else 0.0
        uv_data[idx_v] = (u_val, v_val, on_val)
    attr.data.foreach_set("vector", uv_data.ravel())

    n, L = mat.node_tree.nodes, mat.node_tree.links
    rgb = next((nd for nd in n if nd.type == "RGB"), None)
    if rgb is None:
        return
    at_node = n.new("ShaderNodeAttribute"); at_node.attribute_name = "gomlek_uv"
    sep = n.new("ShaderNodeSeparateXYZ"); L.new(at_node.outputs["Vector"], sep.inputs["Vector"])
    tx = n.new("ShaderNodeTexImage"); tx.image = img; tx.extension = "CLIP"
    L.new(at_node.outputs["Vector"], tx.inputs["Vector"])
    on_m = mz._math(n, L, "GREATER_THAN", sep.outputs["Z"], 0.5)
    fac = mz._math(n, L, "MULTIPLY", tx.outputs["Alpha"], on_m)
    hedefler = [lk.to_socket for lk in L if lk.from_socket == rgb.outputs[0]]
    mix = mz._mix_rgba(n, L, fac, rgb.outputs[0], tx.outputs["Color"])
    for sk in hedefler:
        L.new(mix, sk)


def sac_duzelt(p, e):
    """Lower front hair locks naturally over the forehead (Photos 1-3) and disable the inverted-hull
    black outline along the forehead hairline so the hair never looks like a dark-rimmed swim cap."""
    sac_ = _parca(p, "_hair")
    if not sac_:
        return
    me = sac_.data
    vs = me.vertices
    z0 = min(v.co.z for v in vs); z1 = max(v.co.z for v in vs)
    y0 = min(v.co.y for v in vs); y1 = max(v.co.y for v in vs)
    hacim = float(e.get("sac_hacim", 0.0))
    on_indir = float(e.get("sac_on_indir", 0.0))
    vg_k = sac_.vertex_groups.new(name="sac_dis_kontur")
    yeni = []
    for i, v in enumerate(vs):
        co = v.co.copy()
        tz = (co.z - z0) / max(1e-4, z1 - z0)
        ty = (y1 - co.y) / max(1e-4, y1 - y0)              # 1.0 at front forehead, 0.0 at back of head
        # Lift crown gently
        if hacim:
            co.z += hacim * anime.ss(tz, 0.42, 1.0) * (0.45 + 0.55 * anime.ss(ty, 0.25, 1.0))
        # Slide front locks down onto the upper forehead (Photos 1-3)
        if on_indir:
            on_w = anime.ss(ty, 0.55, 0.92) * (1.0 - anime.ss(tz, 0.72, 0.96)) * (1.0 - anime.ss(abs(co.x), 0.055, 0.088))
            co.z -= on_indir * on_w
            co.y -= 0.0025 * on_w
        yeni.append(co)
        # Disable inverted-hull contour on front hairline touching forehead skin; keep on outer crown!
        ic_alin = anime.ss(ty, 0.58, 0.85) * (1.0 - anime.ss(tz, 0.55, 0.82)) * (1.0 - anime.ss(abs(co.x), 0.060, 0.090))
        vg_k.add([i], float(max(0.0, 1.0 - ic_alin)), "REPLACE")
    _kaydir(me, yeni)
    for md in sac_.modifiers:
        if md.type == "SOLIDIFY" and md.name == "kontur":
            md.vertex_group = "sac_dis_kontur"


def kur(e, x=0.0, parlak=None):
    eski_gen = anime.YUZ_GENLERI
    eski_goz = anime.buyut_goz
    eski_govde = anime.govde
    eski_skin = anime.skin_mat
    fx, fy = e.get("goz_olcek", (1.12, 1.14))
    anime.YUZ_GENLERI = ()
    anime.buyut_goz = lambda co, fx=fx, fy=fy: eski_goz(co, fx=fx, fy=fy)
    anime.govde = _tam_govde
    anime.skin_mat = lambda name, srgb, sex: _tam_ten_mat(name, srgb, sex, e)
    try:
        p = anime.make(e, x, kakul=e.get("kakul", False))
    finally:
        anime.YUZ_GENLERI = eski_gen
        anime.buyut_goz = eski_goz
        anime.govde = eski_govde
        anime.skin_mat = eski_skin
    yuz_isik_duzelt(p, e)
    if e.get("atletik_gomlek"):
        atletik_gomlek(p)
    if e.get("acik_yaka_gomlek"):
        acik_yaka_gomlek_doku(p, e)
    if e.get("ince_gomlek"):
        ince_gomlek(p)
    if e.get("bagcikli_yaka"):
        bagcikli_yaka_doku(p)
    if not e.get("sac_parlak", True):
        for o in p["parts"]:
            for m in (o.data.materials if o.type == "MESH" else []):
                if m and m.use_nodes and m.name.startswith(e["name"] + "_sac"):
                    for nd in m.node_tree.nodes:
                        if nd.type == "BSDF_GLOSSY":
                            nd.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    if e.get("sac_boya"):
        hs = np.array([0.11, 0.10, 0.13]) + mz.hair(*e["sac"]) * 0.88
        for o in p["parts"]:
            for m in (o.data.materials if o.type == "MESH" else []):
                if not (m and m.use_nodes and m.name.startswith(e["name"] + "_sac")):
                    continue
                n, L = m.node_tree.nodes, m.node_tree.links
                rgb = next((nd for nd in n if nd.type == "RGB"), None)
                if rgb is None:
                    continue
                tc = n.new("ShaderNodeTexCoord")
                tx = n.new("ShaderNodeTexImage"); tx.extension = "REPEAT"
                tx.image = mz.hair_strand_image(e["name"] + "_teller", hs)
                L.new(tc.outputs["UV"], tx.inputs["Vector"])
                hedefler = [lk.to_socket for lk in L if lk.from_socket == rgb.outputs[0]]
                yumusak = mz._mix_rgba(n, L, 0.28, rgb.outputs[0], tx.outputs["Color"])
                for sk in hedefler:
                    L.new(yumusak, sk)
    sac_duzelt(p, e)
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


def uzuv(arm, kok, orta, uc_kemik, hedef, kutup, baslangic=None):
    """Pose a limb chain (kok -> orta -> uc_kemik) cleanly from untwisted rest pose so its end
    reaches hedef (armature space) without residual Biped axial twist or T-pose holonomy roll."""
    pb = arm.pose.bones
    kok_baz = kok.replace("01.", "{}.")
    orta_baz = orta.replace("01.", "{}.")
    for b_ad in (kok, kok_baz.format("02"), orta, orta_baz.format("02"), uc_kemik):
        if b_ad in pb:
            pb[b_ad].matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    if baslangic is not None:
        ust_yon, alt_yon = baslangic
        kadro._aim(arm, kok, orta, ust_yon)
        kadro._aim(arm, orta, uc_kemik, alt_yon)
        bpy.context.view_layer.update()
    S = pb[kok].head.copy(); M_ = pb[orta].head.copy(); E = pb[uc_kemik].head.copy()
    a, b = (M_ - S).length, (E - M_).length
    dirsek = _iki_kemik(S, Vector(hedef), a, b, Vector(kutup))
    kadro._aim(arm, kok, orta, dirsek - S)
    bpy.context.view_layer.update()
    kadro._aim(arm, orta, uc_kemik, Vector(hedef) - pb[orta].head)
    bpy.context.view_layer.update()


def kol(arm, side, hedef, kutup=None, kavra_yon=None):
    pb = arm.pose.bones
    sx = 1.0 if side == ".L" else -1.0
    if "clavicle" + side in pb:
        pb["clavicle" + side].matrix_basis = Matrix.Identity(4)
    # First adduct from horizontal T-pose to natural hanging-at-side stance so shoulder/bicep roll
    # is 100% anatomical before flexing toward the target; elbow pole points down, back and outward.
    kt = kutup if kutup is not None else (sx * 0.38, 0.38, -0.85)
    baslangic = ((0.14 * sx, 0.04, -1.0), (0.06 * sx, -0.20, -1.0))
    uzuv(arm, "upperarm01" + side, "lowerarm01" + side, "wrist" + side, hedef, kt, baslangic=baslangic)
    if "finger2-1" + side in pb and "finger5-1" + side in pb:
        axis = (pb["wrist" + side].head - pb["lowerarm01" + side].head).normalized()
        across = pb["finger2-1" + side].head - pb["finger5-1" + side].head
        want = Vector(kavra_yon).normalized() if kavra_yon is not None else Vector((0.20 * sx, -0.25, 0.95)).normalized()
        a_p = (across - axis * across.dot(axis))
        w_p = (want - axis * want.dot(axis))
        if a_p.length > 1e-5 and w_p.length > 1e-5:
            a_p.normalize(); w_p.normalize()
            ang = math.atan2(a_p.cross(w_p).dot(axis), a_p.dot(w_p))
            ang = max(-1.15, min(1.15, ang))
            if "lowerarm02" + side in pb:
                kadro._rotate(arm, "lowerarm01" + side, Quaternion(axis, ang * 0.40))
                kadro._rotate(arm, "lowerarm02" + side, Quaternion(axis, ang * 0.55))
            else:
                kadro._rotate(arm, "lowerarm01" + side, Quaternion(axis, ang * 0.85))
            pb["wrist" + side].matrix_basis = Matrix.Identity(4)
            bpy.context.view_layer.update()
        if kavra_yon is not None:
            # Fine-align the wrist so the fist tunnel (finger5 -> finger2) is coaxial with the gripped rod/tiller
            across2 = (pb["finger2-1" + side].head - pb["finger5-1" + side].head).normalized()
            q_w = across2.rotation_difference(Vector(kavra_yon).normalized())
            kadro._rotate(arm, "wrist" + side, Quaternion(q_w.axis, q_w.angle * 0.65))


def omuz(arm, side):
    return arm.pose.bones["upperarm01" + side].head.copy()


def otur(arm, diz_acik=0.10):
    """Seated: thighs forward, shins down. Armature space: -Y front, +X person's left."""
    for side, sx in ((".L", 1), (".R", -1)):
        kadro._aim(arm, "upperleg01" + side, "lowerleg01" + side, (sx * diz_acik, -1.0, 0.04))
        bpy.context.view_layer.update()
        kadro._aim(arm, "lowerleg01" + side, "foot" + side, (sx * 0.03, -0.22, -1.0))
        bpy.context.view_layer.update()


def dik_otur(arm, ileri=0.0, gogus=0.0, bakis=0.8):
    """Sit tall like an athlete: reset spine/pelvis/clavicle twist and stack the trunk cleanly over
    the hips (ileri deg, + forward) while keeping the clavicles at their natural anatomical width."""
    pb = arm.pose.bones
    for b_ad in ("root", "pelvis.L", "pelvis.R", "spine05", "spine04", "spine03", "spine02", "spine01",
                 "neck01", "neck02", "neck03", "head", "clavicle.L", "clavicle.R"):
        if b_ad in pb:
            pb[b_ad].matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    zincir = ("spine05", "spine04", "spine03", "spine02")
    for k in zincir:
        if k in pb:
            kadro._rotate(arm, k, Quaternion(Vector((1, 0, 0)), math.radians(ileri / len(zincir))))
    bpy.context.view_layer.update()
    return ileri


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


def yerlestir(p, kok, nokta, yon_z, zemin, oturuyor, ileri=0.0):
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
    on = Matrix.Rotation(yon_z, 4, "Z") @ Vector((0.0, -1.0, 0.0))     # the way the figure faces
    arm.location = (nokta[0] - kr.x + on.x * ileri, nokta[1] - kr.y + on.y * ileri, z)
    bpy.context.view_layer.update()
    if oturuyor and not any(m.name == "Oturak" for m in p["body"].modifiers):
        oturak_bas(p, zemin - z)
    ters = Matrix.Rotation(-yon_z, 4, "Z")
    duz = Matrix.Rotation(yon_z, 4, "Z")
    return (lambda q: ters @ (Vector(q) - Vector(arm.location))), (lambda q: duz @ Vector(q) + Vector(arm.location))


OTURAN = ("pelvis.L", "pelvis.R", "upperleg01.L", "upperleg01.R", "upperleg02.L", "upperleg02.R")


def oturak_bas(p, yuzey_z, yumusak=0.025):
    """Soft tissue on a seat: after skinning, buttocks and thigh backs that sink below the seat
    surface are pressed onto it with a smooth floor (smooth max), the way a seated body flattens.
    Linear skinning alone balloons the buttocks when the thigh folds 90 degrees. Applied to the
    body and to the garment over it, after the Armature modifier, limited to hip and thigh weights.
    yuzey_z is the seat top in the figure's own space (the rig only turns about Z on the boat)."""
    hedefler = [p["body"]] + [o for o in p["parts"] if "casualsuit" in o.name or "pants" in o.name]
    for o in hedefler:
        idx = {o.vertex_groups[g].index for g in OTURAN if g in o.vertex_groups}
        if not idx:
            continue
        vg = o.vertex_groups.get("oturak") or o.vertex_groups.new(name="oturak")
        for v in o.data.vertices:
            w = sum(g.weight for g in v.groups if g.group in idx)
            if w > 0.001:
                vg.add([v.index], min(1.0, w * 1.6), "REPLACE")
        ng = bpy.data.node_groups.new(o.name + "_oturak", "GeometryNodeTree")
        ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
        N, L = ng.nodes, ng.links
        gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
        pos = N.new("GeometryNodeInputPosition")
        ay = N.new("ShaderNodeSeparateXYZ")
        tab = N.new("ShaderNodeMath"); tab.operation = "SMOOTH_MAX"
        tab.inputs[1].default_value = yuzey_z; tab.inputs[2].default_value = yumusak
        ag = N.new("GeometryNodeInputNamedAttribute"); ag.data_type = "FLOAT"
        ag.inputs["Name"].default_value = "oturak"
        kar = N.new("ShaderNodeMix"); kar.data_type = "FLOAT"
        bir = N.new("ShaderNodeCombineXYZ")
        sp = N.new("GeometryNodeSetPosition")
        L.new(pos.outputs[0], ay.inputs[0])
        L.new(ay.outputs["Z"], tab.inputs[0])
        L.new(ag.outputs["Attribute"], kar.inputs["Factor"])
        L.new(ay.outputs["Z"], kar.inputs["A"]); L.new(tab.outputs[0], kar.inputs["B"])
        L.new(ay.outputs["X"], bir.inputs["X"]); L.new(ay.outputs["Y"], bir.inputs["Y"])
        L.new(kar.outputs["Result"], bir.inputs["Z"])
        L.new(gi.outputs[0], sp.inputs["Geometry"]); L.new(bir.outputs[0], sp.inputs["Position"])
        L.new(sp.outputs[0], go.inputs[0])
        md = o.modifiers.new("Oturak", "NODES"); md.node_group = ng
        sira = [m.name for m in o.modifiers]
        hedef_i = next(i for i, m in enumerate(o.modifiers) if m.type == "ARMATURE") + 1
        with bpy.context.temp_override(object=o):
            bpy.ops.object.modifier_move_to_index(modifier=md.name, index=hedef_i)


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
    """True interior grip centre of the closed fist (inside the tunnel between knuckles and curled fingers), armature space."""
    pb = arm.pose.bones
    k1 = (pb["finger2-1" + side].head + pb["finger5-1" + side].head) * 0.5
    if "finger2-2" + side in pb and "finger5-2" + side in pb:
        k2 = (pb["finger2-2" + side].tail + pb["finger5-2" + side].tail) * 0.5
        return k1 * 0.42 + k2 * 0.58
    return k1


def kol_kavra(p, kalip, side, hedef_avuc, kutup=None):
    """Pose arm and close fingers so the interior grip centre of the closed fist (avuc) lands
    directly on hedef_avuc (the cork rod handle axis)."""
    arm = p["arm"]
    kol(arm, side, hedef_avuc, kutup=kutup)
    el_uygula(p, kalip, side)
    d_avuc = avuc(arm, side) - arm.pose.bones["wrist" + side].head
    kol(arm, side, Vector(hedef_avuc) - d_avuc, kutup=kutup)
    el_uygula(p, kalip, side)


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


def ayaklar_yere(p, ic, dis, adim=0.38, acik=0.04):
    """Seated on a raised seat: plant both feet flat on the deck in front of the hips with knees
    tracking straight ahead in their anatomical hinge plane (zero bow-legged splay)."""
    arm = p["arm"]
    pb = arm.pose.bones
    for b_ad in ("root", "pelvis.L", "pelvis.R"):
        if b_ad in pb:
            pb[b_ad].matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    for side, sx in ((".L", 1), (".R", -1)):
        kalca = pb["upperleg01" + side].head.copy()
        b = dis(kalca + Vector((sx * acik, -adim, 0.0)))
        b.z = guverte_z(b.y) + 0.085
        # Knee pole straight forward (-Y) and up (+Z) in armature space so knees never bow outward
        uzuv(arm, "upperleg01" + side, "lowerleg01" + side, "foot" + side, ic(b), (sx * 0.03, -1.0, 0.90))
        pb["foot" + side].matrix_basis = Matrix.Identity(4)
        bpy.context.view_layer.update()
        kadro._aim(arm, "foot" + side, "toe1-1" + side, (sx * 0.02, -1.0, -0.32))
    bpy.context.view_layer.update()


def ayakta_dur(arm, acik=0.04):
    """Clean untwisted athletic standing leg stance on deck."""
    pb = arm.pose.bones
    for side, sx in ((".L", 1), (".R", -1)):
        kalca = pb["upperleg01" + side].head.copy()
        hedef_ayak = Vector((kalca.x + sx * acik, -0.02 + sx * 0.03, 0.085))
        uzuv(arm, "upperleg01" + side, "lowerleg01" + side, "foot" + side, hedef_ayak, (sx * 0.03, -1.0, 0.25))
        pb["foot" + side].matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()


def olta_yonu(akt, tik, dis):
    """Rod direction held in the right hand at tick, in boat-local space."""
    _, R = akt.tutamak(tik, "R")
    d = Vector(R[:, 1].tolist())
    return (dis(d) - dis(Vector((0, 0, 0)))).normalized()


def murettebat(kok, poz="dumen", sahne="seyir"):
    """sahne: kalkis | seyir | varis; poz (seyir): dumen | olta | olta_vurus | tuttu.
    Younger brother (Latif) holds the tiller at the helm to steady/stop the boat;
    elder brother (Yusuf) hauls the lateen halyard, fishes from the midship crate, and spots the harbour."""
    cizim = []
    an = sahne if sahne != "seyir" else poz        # kalkis | dumen | olta | olta_vurus | tuttu | varis
    balik = an == "balik"                          # the fishing sequence starts from the rod-out pose
    if balik:
        an = "olta"

    # Younger brother (Latif): seated at the stern helm, holding the tiller to steady/stop the boat
    kardes = kur(KARDES)
    c = kardes["arm"]
    kavra_k = el_kalibi(kardes)
    otur(c, 0.05)
    ic_k, dis_k = yerlestir(kardes, kok, (0.46, -2.66), math.radians(-143), OTURAK_Z, True, ileri=0.09)
    ayaklar_yere(kardes, ic_k, dis_k, 0.36, 0.04)
    dik_otur(c, {"dumen": -2.0, "olta": 3.0, "olta_vurus": 1.0, "tuttu": -1.0, "varis": -2.0}.get(an, 0.0))
    # Left hand grips the tiller (yeke); right hand waves (kalkis), shades brow (varis), or rests on right thigh
    kol(c, ".L", Vector((0.22, -0.34, 1.00)))
    el_uygula(kardes, kavra_k, ".L")
    if an == "kalkis":
        kol(c, ".R", Vector((-0.34, -0.22, 1.48)))
        bas(c, 24.0, -4.0); gulus(kardes, 0.45)
    elif an == "varis":
        kol(c, ".R", Vector((-0.12, -0.22, 1.54)), (-0.65, -0.10, -0.50))
        bas(c, -10.0, 0.0); gulus(kardes, 0.2)
    else:
        kol(c, ".R", Vector((-0.18, -0.30, 0.98)))
        el_uygula(kardes, kavra_k, ".R")
        bas(c, {"dumen": -22.0, "olta": -34.0, "olta_vurus": -37.0, "tuttu": -40.0}[an],
            {"olta": 6.0, "olta_vurus": 3.0}.get(an, 0.0))
        gulus(kardes, {"dumen": 0.35, "olta": 0.25, "olta_vurus": 0.45, "tuttu": 0.85}[an])
    bpy.context.view_layer.update()
    cizim.append(("yeke", dis_k(avuc(c, ".L")) + Vector((0, 0, -0.03))))

    # Elder brother (Yusuf): athletic build, midship on crate/deck — hauls sail, fishes & lands the catch
    abi = kur(ABI)
    a = abi["arm"]
    kavra_a = el_kalibi(abi)
    if an == "kalkis":       # hauls the sail up at the mast
        dik_otur(a, -3.0)
        ayakta_dur(a, 0.04)
        kol(a, ".R", Vector((-0.06, -0.34, 1.56)))
        kol(a, ".L", Vector((0.06, -0.32, 1.38)))
        ic_a, dis_a = yerlestir(abi, kok, (0.08, 0.5), math.radians(156), guverte_z(0.5), False)
        el_uygula(abi, kavra_a, ".L"); el_uygula(abi, kavra_a, ".R")
        bpy.context.view_layer.update()
        orta = (dis_a(avuc(a, ".L")) + dis_a(avuc(a, ".R"))) / 2
        a.location.x += 0.05 - orta.x
        a.location.y += 0.84 - orta.y
        bpy.context.view_layer.update()
        yere_bas(abi, kok, guverte_z(a.location.y))
        bas(a, 16.0, -8.0); gulus(abi, 0.35)
        e1, e2 = dis_a(avuc(a, ".L")), dis_a(avuc(a, ".R"))
        ust_el, alt_el = (e1, e2) if e1.z > e2.z else (e2, e1)
        bas_ = MANDAR[0]
        cizim += [("cubuk", "Mandar", bas_, ust_el, 0.012, "halat"),
                  ("cubuk", "Mandar", ust_el, alt_el, 0.012, "halat"),
                  ("cubuk", "Mandar", alt_el, Vector((0.12, 0.95, guverte_z(0.95) + 0.25)), 0.012, "halat")]
    elif an == "dumen":      # sits on the crate, watching the sea & sail
        otur(a, 0.05)
        ic_a, dis_a = yerlestir(abi, kok, (0.30, -1.6), math.radians(-90), SANDIK_Z, True)
        ayaklar_yere(abi, ic_a, dis_a, 0.40, 0.04)
        dik_otur(a, 2.0)
        kol(a, ".L", Vector((0.20, -0.32, 1.00)))
        kol(a, ".R", Vector((-0.20, -0.32, 1.00)))
        el_uygula(abi, kavra_a, ".L"); el_uygula(abi, kavra_a, ".R")
        bas(a, -16.0, -14.0); gulus(abi, 0.35)
    elif an in ("olta", "olta_vurus", "tuttu"):   # Yusuf seated on the midship crate below the lateen sail, fishing over port rail
        otur(a, 0.05)
        ic_a, dis_a = yerlestir(abi, kok, (0.26, -1.55), math.radians(-88), SANDIK_Z, True)
        ayaklar_yere(abi, ic_a, dis_a, 0.38, 0.04)
        dik_otur(a, {"olta": 3.5, "olta_vurus": 1.5, "tuttu": -1.5}[an])
        bpy.context.view_layer.update()
        yon = {
            "olta": Vector((-0.74, 0.42, 0.52)).normalized(),
            "olta_vurus": Vector((-0.70, 0.42, 0.58)).normalized(),
            "tuttu": Vector((-0.65, 0.44, 0.62)).normalized(),
        }[an]
        # Right hand grips the fore cork handle above the reel seat; left hand grips the rear cork handle below the reel seat
        hedef_el = Vector((-0.08, -1.48, {"olta": 1.35, "olta_vurus": 1.40, "tuttu": 1.46}[an]))
        kol_kavra(abi, kavra_a, ".R", ic_a(hedef_el))
        kol_kavra(abi, kavra_a, ".L", ic_a(hedef_el - yon * 0.14))
        bas(a, -12.0, {"olta": 6.0, "olta_vurus": 1.0, "tuttu": -12.0}[an])
        gulus(abi, {"olta": 0.25, "olta_vurus": 0.45, "tuttu": 0.88}[an])
        bpy.context.view_layer.update()
        el_r = dis_a(avuc(a, ".R"))
        uc = el_r + yon * 2.05
        cizim.append(("cubuk", "Olta", el_r - yon * OLTA_SAP, uc, 0.022, "kusak"))
        if an in ("olta", "olta_vurus"):
            cizim.append(("cubuk", "Misina", uc, Vector((uc.x - 0.35, uc.y + 0.15, -0.05)), 0.006, "halat"))
        else:
            balik_konum = uc + Vector((0.0, 0.0, -0.82))
            cizim += [("cubuk", "Misina", uc, balik_konum + Vector((0, 0, 0.14)), 0.006, "halat"), ("balik", balik_konum)]
    else:                    # varis: beside the mast, points clearly over port bow at the town
        dik_otur(a, 2.0)
        ayakta_dur(a, 0.04)
        y = 0.68
        ic_a, dis_a = yerlestir(abi, kok, (-0.24, y), math.radians(142), guverte_z(y), False)
        yere_bas(abi, kok, guverte_z(y))
        kol(a, ".R", ic_a(Vector((-0.95, y + 0.62, 2.02))))
        kol(a, ".L", Vector((0.22, -0.18, 1.02)))
        el_uygula(abi, kavra_a, ".R", duz=("finger2",))
        el_uygula(abi, kavra_a, ".L")
        bas(a, -10.0, -6.0); gulus(abi, 0.5)
        bpy.context.view_layer.update()
        cizim.append(("kangal", dis_a(avuc(a, ".L")) + Vector((0, 0, -0.08))))
    if balik:                # rod and line are animated by the scene, not drawn once
        cizim = [c_ for c_ in cizim if not (c_[0] == "cubuk" and c_[1] in ("Olta", "Misina"))]
    return dict(yusuf=abi, latif=kardes, abi=abi, kardes=kardes, cizim=cizim,
                yer=dict(ic_a=ic_a, dis_a=dis_a, ic_k=ic_k, dis_k=dis_k), kavra_a=kavra_a, kavra_k=kavra_k)


# ---------------------------------------------------------------- fishing: the elder fishes, Latif stops the boat
FPS = 30                 # 30 divides a 60 Hz phone refresh evenly; 24 would judder (3:2 cadence)
KS = FPS / 24.0          # frame-count scale for timings first tuned at 24 fps
OLTA_BOY = 2.05          # rod length beyond the hand (m)
OLTA_SAP = 0.34          # butt behind the hand


def _klip(ad):
    if ad not in _KLIPLER:
        _KLIPLER[ad] = xklip.Klip(os.path.join(_tablo()["kok"], ad + ".x"))
    return _KLIPLER[ad]


def _anahtarla(arm, kemikler, f):
    pb = arm.pose.bones
    for b in kemikler:
        if b in pb:
            pb[b].keyframe_insert("rotation_quaternion", frame=f)


def _gulus_anahtar(p, v, f):
    for o in [p["body"]] + p["parts"]:
        sk = o.data.shape_keys if o.type == "MESH" else None
        if sk and "smile" in sk.key_blocks:
            sk.key_blocks["smile"].value = v
            sk.key_blocks["smile"].keyframe_insert("value", frame=f)


def _sigma(i, sigma, sinirlar, sinir_sigma, sinir_gen):
    """Per-frame blur width: a base width plus a wider blur around phase boundaries."""
    if not sinirlar or sinir_sigma <= 0:
        return sigma
    d = min(abs(i - b) for b in sinirlar)
    return sigma + sinir_sigma * math.exp(-0.5 * (d / sinir_gen) ** 2)


def yumusat_liste(vals, sigma=2.0, sinirlar=(), sinir_sigma=0.0, sinir_gen=6.0):
    """Gaussian low-pass over a per-frame list of floats or Vectors (indices are list positions)."""
    n = len(vals)
    out = []
    for i in range(n):
        s_ = _sigma(i, sigma, sinirlar, sinir_sigma, sinir_gen)
        if s_ < 0.3:
            out.append(vals[i]); continue
        r = int(math.ceil(3 * s_))
        top, ws = None, 0.0
        for j in range(i - r, i + r + 1):
            w = math.exp(-0.5 * ((j - i) / s_) ** 2)
            v = vals[min(n - 1, max(0, j))]
            top = v * w if top is None else top + v * w
            ws += w
        out.append(top / ws)
    return out


def yumusat(armlar, f0, f1, sigma=1.6, sinirlar=(), sinir_sigma=0.0, sinir_gen=6.0):
    """Low-pass every animated pose-bone rotation of the armatures between f0 and f1.

    Captured motion carries sensor jitter and every clip change or loop seam is a small pop; a
    film-weight Gaussian (wider around the given boundary frames) turns that into weighty,
    continuous motion. Quaternions are hemisphere-aligned, blurred and renormalised; Euler
    channels are blurred per axis. Bones that never move are left alone."""
    sc = bpy.context.scene
    kare = list(range(f0, f1 + 1))
    veri = {arm: {} for arm in armlar}
    for f in kare:
        sc.frame_set(f)
        for arm in armlar:
            for pb in arm.pose.bones:
                q = pb.rotation_quaternion if pb.rotation_mode == "QUATERNION" else pb.rotation_euler
                veri[arm].setdefault(pb.name, []).append(Vector(tuple(q)))
    sin_i = [b - f0 for b in sinirlar]
    for arm in armlar:
        for ad, dizi in veri[arm].items():
            if max((v - dizi[0]).length for v in dizi) < 1e-5:
                continue
            quat = arm.pose.bones[ad].rotation_mode == "QUATERNION"
            if quat:
                for i in range(1, len(dizi)):
                    if dizi[i].dot(dizi[i - 1]) < 0:
                        dizi[i] = -dizi[i]
            yum = yumusat_liste(dizi, sigma, sin_i, sinir_sigma, sinir_gen)
            pb = arm.pose.bones[ad]
            for i, f in enumerate(kare):
                if (yum[i] - dizi[i]).length < 1e-6:
                    continue
                if quat:
                    pb.rotation_quaternion = Quaternion(yum[i]).normalized()
                    pb.keyframe_insert("rotation_quaternion", frame=f)
                else:
                    pb.rotation_euler = tuple(yum[i])
                    pb.keyframe_insert("rotation_euler", frame=f)


def lerp(a, b, t):
    return a + (b - a) * t


NEON_PAY = 0.3           # share of the hand-authored phase layer on top of the captured motion
EL_TABAN = Vector((-0.08, -1.48, 1.33))              # framing: right fist over the port rail (boat-local)
YON_TABAN = Vector((-0.74, 0.42, 0.52)).normalized()  # framing: rod axis out over the water
SIZMA = 1.0 / (1.5 * FPS)  # captured hand/rod offsets leak back to the framing over about 1.5 s


def _neon_hedef(faz, u):
    """Hand-authored phase choreography (Neon): trunk lean and turn, head pitch, both fists and the
    rod axis, boat-local. Used as a light layer over the captured motion, not as the motion."""
    s_u = u * u * (3 - 2 * u)
    egim_one, don_z, bas_y = 2.0, 0.0, 4.0
    el_R, yon, el_L = EL_TABAN.copy(), YON_TABAN.copy(), None
    if faz == "durdur":
        egim_one, don_z, bas_y = 2.0 - 1.5 * s_u, -12.0 * math.sin(math.pi * s_u), 2.0
        yon = Vector((-0.68, 0.40, 0.60)).normalized()
        el_R = Vector((-0.07, -1.48, 1.35))
    elif faz == "atis":
        if u < 0.45:
            q = u / 0.45; q = q * q * (3 - 2 * q)
            egim_one, don_z, bas_y = lerp(0.5, -6.5, q), lerp(0.0, 10.0, q), lerp(2.0, -10.0, q)
            yon = Vector((-0.68, 0.40, 0.60)).lerp(Vector((-0.44, 0.28, 0.85)), q).normalized()
            el_R = Vector((-0.07, -1.48, 1.35)).lerp(Vector((-0.03, -1.50, 1.46)), q)
        else:
            q = (u - 0.45) / 0.55; q = q * q * (3 - 2 * q)
            egim_one, don_z, bas_y = lerp(-6.5, 4.5, q), lerp(10.0, -4.0, q), lerp(-10.0, 6.0, q)
            yon = Vector((-0.44, 0.28, 0.85)).lerp(Vector((-0.76, 0.42, 0.49)), q).normalized()
            el_R = Vector((-0.03, -1.50, 1.46)).lerp(Vector((-0.09, -1.48, 1.33)), q)
    elif faz == "bekle":
        sal = math.sin(u * math.tau * 2.0)
        egim_one, don_z, bas_y = 3.0 + sal, -2.0 + 1.5 * math.cos(u * math.tau), 6.0 + 2.0 * sal
        yon = Vector((-0.74, 0.42, 0.52 + 0.03 * sal)).normalized()
        el_R = Vector((-0.08, -1.48, 1.33 + 0.015 * sal))
    elif faz == "vurus":
        v_ = math.sin(math.pi * s_u)
        egim_one, don_z, bas_y = 3.0 - 8.5 * v_, -4.0 + 6.0 * v_, 6.0 - 12.0 * v_
        yon = YON_TABAN.lerp(Vector((-0.62, 0.40, 0.67)), v_).normalized()
        el_R = EL_TABAN.lerp(Vector((-0.06, -1.48, 1.45)), v_)
    elif faz == "cekis":
        pompa = 0.5 - 0.5 * math.cos(u * math.tau * 2.0)
        egim_one, don_z, bas_y = lerp(3.0, -5.5, pompa), -3.0 + 4.0 * pompa, lerp(4.0, -8.0, pompa)
        yon = Vector((-0.70, 0.42, 0.57)).lerp(Vector((-0.60, 0.40, 0.69)), pompa).normalized()
        el_R = Vector((-0.08, -1.48, 1.35)).lerp(Vector((-0.06, -1.48, 1.46)), pompa)
        makara = Vector((0.0, 0.022 * math.sin(u * math.tau * 6.0), 0.022 * math.cos(u * math.tau * 6.0)))
        el_L = el_R - yon * 0.15 + makara                 # left hand turns the reel crank
    elif faz == "al":
        yon = Vector((-0.58, 0.40, 0.71)).normalized()
        el_R = Vector((-0.05, -1.48, 1.46))
        olta_L, yakala, kova_ = el_R - yon * 0.15, Vector((-0.24, -1.26, 1.36)), Vector((-0.26, -1.04, 1.18))
        if u < 0.35:
            q = u / 0.35; q = q * q * (3 - 2 * q)
            egim_one, don_z, bas_y, el_L = lerp(-2.0, 4.0, q), lerp(0.0, -10.0, q), lerp(-8.0, 4.0, q), olta_L.lerp(yakala, q)
        elif u < 0.78:
            q = (u - 0.35) / 0.43; q = q * q * (3 - 2 * q)
            egim_one, don_z, bas_y, el_L = lerp(4.0, 9.5, q), lerp(-10.0, -18.0, q), lerp(4.0, 14.0, q), yakala.lerp(kova_, q)
        else:
            q = (u - 0.78) / 0.22; q = q * q * (3 - 2 * q)
            egim_one, don_z, bas_y, el_L = lerp(9.5, 2.0, q), lerp(-18.0, -6.0, q), lerp(14.0, 4.0, q), kova_.lerp(olta_L, q)
    elif faz == "son":
        egim_one, don_z, bas_y = 2.0, -8.0 * (1.0 - 0.4 * s_u), 2.0
        yon = Vector((-0.68, 0.40, 0.60)).normalized()
        el_R = Vector((-0.07, -1.48, 1.36))
    if el_L is None:
        el_L = el_R - yon * 0.15
    return egim_one, don_z, bas_y, el_R, el_L, yon


def balik_tut(ekip, kok, yeke_pivot, f0=1, harman=None, yavas=1.4):
    """Key the whole fishing sequence and return one record per frame for the props.

    Motion comes from captured seated-fishing clips, in the order the clip table gives (wait, cast,
    wait for the bite, strike, fight the fish, land it, settle). Each clip drives the elder brother's
    trunk, neck and head, crossfaded (smoothstep) from the previous clip's last moment. His fists are
    solved onto the rod grips by IK: the captured hand and rod motion is high-passed onto a fixed
    framing over the rail, with a light hand-authored phase layer on top. A Gaussian pass over every
    rotation then gives the motion its weight. Latif first pushes the tiller over to round the boat
    up and stop it, holds it with small corrections, turns to watch the fight and smiles at the
    catch. The hull rides the swell throughout.
    Records: f, faz (phase), u (0..1 inside the phase), el_R, el_L, yon (rod axis), yeke, boat-local."""
    t = _tablo()
    tps = t.get("tps", 4800)
    harman = harman or round(16 * KS)
    abi, kardes = ekip["abi"], ekip["kardes"]
    a, c = abi["arm"], kardes["arm"]
    Y = ekip["yer"]
    ic_a, dis_a, ic_k, dis_k = Y["ic_a"], Y["dis_a"], Y["ic_k"], Y["dis_k"]
    yon_a = lambda v: dis_a(v) - dis_a(Vector((0.0, 0.0, 0.0)))       # rotate only, armature -> boat
    for arm in (a, c):
        for pb in arm.pose.bones:
            pb.rotation_mode = "QUATERNION"
    # timeline: (phase, clip, tick, u, first index of its segment)
    akt, akis = {}, []
    for satir in t["akislar"][os.environ.get("SEFER_AKIS", "balik_tut")]:
        faz, ad, tekrar = satir[:3]
        k = _klip(ad)
        if ad not in akt:
            akt[ad] = xklip.Aktarici(k, a)
        n = max(2, round((k.t1 - k.t0) / tps * FPS * yavas * (satir[3] if len(satir) > 3 else 1.0)))
        toplam = n * tekrar
        bas_ = len(akis)
        for j in range(toplam):
            tik = k.t0 + (k.t1 - k.t0) * ((j % n) / n if tekrar > 1 else j / (n - 1))
            akis.append((faz, ad, tik, j / max(1, toplam - 1), bas_))
    deniz_ob = bpy.data.objects.get("Deniz")
    if deniz_ob and "Dalga" in deniz_ob.modifiers:
        deniz_ob.modifiers["Dalga"].show_viewport = False
    pba, pbk = a.pose.bones, c.pose.bones
    bpy.context.view_layer.update()
    a_q0 = {b: pba[b].rotation_quaternion.copy() for b in ("spine02",) if b in pba}
    el0 = dis_k(avuc(c, ".L"))
    pv = Vector(yeke_pivot)
    v0 = el0 - pv
    k_q0 = {b: pbk[b].rotation_quaternion.copy() for b in ("head", "neck01", "spine03", "spine04")}
    kol_k = ["upperarm01.L", "lowerarm01.L", "wrist.L"] + [b + ".L" for b in PARMAK]
    ust_a = sorted(b for b in UST if b in pba)
    kok_r0 = kok.rotation_euler.copy(); kok_z0 = kok.location.z

    def klip_q(A, tik):
        A.poz(tik, sadece=UST)
        return {b: pba[b].rotation_quaternion.copy() for b in ust_a}

    kayit, sinirlar = [], []
    izle = 0.0
    off, q_off, h_onceki, y_onceki = Vector(), Quaternion(), None, None
    f = f0
    sc = bpy.context.scene
    for i, (faz, ad, tik, u, bas_i) in enumerate(akis):
        sc.frame_set(f)
        if bas_i == i and i > 0:
            sinirlar.append(f)
        # 1. hull on the swell (4 s period)
        ph = math.tau * (f - f0) / (4.0 * FPS)
        kok.rotation_euler = (kok_r0.x + math.radians(0.9) * math.cos(ph), kok_r0.y + math.radians(1.6) * math.sin(ph), kok_r0.z)
        kok.location.z = kok_z0 + 0.035 * math.sin(ph - 0.4)
        kok.keyframe_insert("rotation_euler", frame=f); kok.keyframe_insert("location", index=2, frame=f)

        # 2. elder brother. a) trunk, neck and head from the clip, crossfaded from the previous
        # clip's last moment (blended bone by bone in local space, so the arms never snap to rest)
        A = akt[ad]
        qa = klip_q(A, tik)
        y_klip = olta_yonu(A, tik, dis_a)
        w = 1.0
        if bas_i > 0 and i - bas_i < harman:
            pf = akis[bas_i - 1]
            w = (i - bas_i + 1) / (harman + 1); w = w * w * (3 - 2 * w)
            qp = klip_q(akt[pf[1]], pf[2])
            y_klip = olta_yonu(akt[pf[1]], pf[2], dis_a).lerp(y_klip, w).normalized()
        for b in ust_a:
            q_ = qa[b]
            if w < 1.0:
                if qp[b].dot(q_) < 0:
                    q_ = -q_
                q_ = qp[b].slerp(q_, w)
            pba[b].rotation_quaternion = q_
        bpy.context.view_layer.update()
        # b) captured hand and rod motion, high-passed onto the framing
        h_R = yon_a(avuc(a, ".R"))
        if h_onceki is not None:
            off = off * (1.0 - SIZMA) + (h_R - h_onceki)
            q_off = Quaternion().slerp(y_onceki.rotation_difference(y_klip) @ q_off, 1.0 - SIZMA)
        h_onceki, y_onceki = h_R, y_klip
        e1, d1, b1, nR, nL, nY = _neon_hedef(faz, u)
        yon = (q_off @ YON_TABAN.lerp(nY, NEON_PAY)).normalized()
        el_R = EL_TABAN + off + (nR - EL_TABAN) * NEON_PAY
        el_L = el_R - yon * 0.15 + (nL - (nR - nY * 0.15))
        # c) the light hand-authored layer on the trunk and head, plus breathing
        nefes_a = math.radians(1.0) * math.sin(ph * 2.0 + 0.6)
        for sp_b, pay in (("spine02", 0.45), ("spine03", 0.55)):
            if sp_b in pba:
                taban = a_q0[sp_b] if sp_b in a_q0 else pba[sp_b].rotation_quaternion.copy()
                pba[sp_b].rotation_quaternion = (
                    taban
                    @ Quaternion(Vector((1, 0, 0)), math.radians(e1 * pay * NEON_PAY) + nefes_a * pay)
                    @ Quaternion(Vector((0, 0, 1)), math.radians(d1 * pay * NEON_PAY)))
        pba["head"].rotation_quaternion = (
            pba["head"].rotation_quaternion
            @ Quaternion(Vector((0, 0, 1)), math.radians((-10.0 + d1 * 0.6) * NEON_PAY))
            @ Quaternion(Vector((1, 0, 0)), math.radians(b1 * NEON_PAY)))
        # d) fists on the grips
        kol_kavra(abi, ekip["kavra_a"], ".R", ic_a(el_R))
        kol_kavra(abi, ekip["kavra_a"], ".L", ic_a(el_L))
        _anahtarla(a, ust_a + ["spine02"], f)
        gulus_a = {"vurus": 0.45, "cekis": 0.35, "al": 0.45 + 0.4 * min(1.0, u * 2.5), "son": 0.85}.get(faz, 0.22)
        _gulus_anahtar(abi, gulus_a, f)

        # 3. Latif: tiller hard over to stop the boat, then held with small corrections
        if faz == "durdur":
            ac = 24.0 * (u * u * (3 - 2 * u))
        else:
            ac = 24.0 - 6.0 * min(1.0, i / (200.0 * KS)) + 1.5 * math.sin(f * 0.11 / KS)
        hedef = pv + Matrix.Rotation(math.radians(ac), 4, "Z") @ v0
        kol(c, ".L", ic_k(hedef))
        el_uygula(kardes, ekip["kavra_k"], ".L")
        izle_h = {"durdur": 0.0, "atis": 0.3, "bekle": 0.4, "vurus": 0.9, "cekis": 1.0, "al": 1.0, "son": 0.7}.get(faz, 0.5)
        izle = izle_h if i == 0 else izle + (izle_h - izle) * 0.06 / KS
        nefes = math.radians(1.4) * math.sin(ph * 3)
        pbk["head"].rotation_quaternion = k_q0["head"] @ Quaternion(Vector((0, 0, 1)), math.radians(28.0 * izle)) @ Quaternion(Vector((1, 0, 0)), math.radians(6.0 * izle))
        pbk["spine03"].rotation_quaternion = k_q0["spine03"] @ Quaternion(Vector((1, 0, 0)), nefes + math.radians(5 * izle))
        _anahtarla(c, kol_k + ["head", "spine03"], f)
        gulus_k = {"vurus": 0.55, "cekis": 0.6, "al": 0.6 + 0.3 * min(1.0, u * 3), "son": 0.85}.get(faz, 0.3)
        _gulus_anahtar(kardes, gulus_k, f)
        kayit.append(dict(f=f, faz=faz, u=u, yon=yon.copy(), yeke=hedef.copy()))
        f += 1
    # weight: a film-weight low-pass over every rotation, wider at each clip change; fists and the
    # tiller are read back from the smoothed result so rod and tiller ride the hands exactly
    yumusat([a, c], f0, f - 1, sigma=1.8 * KS, sinirlar=sinirlar, sinir_sigma=3.0 * KS, sinir_gen=7.0 * KS)
    yonler = yumusat_liste([k["yon"] for k in kayit], 1.8 * KS, [s - f0 for s in sinirlar], 3.0 * KS, 7.0 * KS)
    for k, y_ in zip(kayit, yonler):
        sc.frame_set(k["f"])
        k["yon"] = y_.normalized()
        k["el_R"], k["el_L"] = dis_a(avuc(a, ".R")), dis_a(avuc(a, ".L"))
    if deniz_ob and "Dalga" in deniz_ob.modifiers:
        deniz_ob.modifiers["Dalga"].show_viewport = True
    kayit[0]["sinirlar"] = sinirlar
    print("BALIK_TUT", len(kayit), "kare,", len(sinirlar), "klip geçişi")
    sc.frame_set(f0)
    return kayit


def canlandir(ekip, kok, sahne="seyir", poz="dumen", f0=1, f1=48):
    """Keyframe a seamless 48-frame living cycle on the boat and both brothers: gentle Aegean swell
    pitch/roll on the hull, chest breathing, head counter-sway, and task motion (waving, hauling,
    trolling rod bob, or landing a fish)."""
    an = sahne if sahne != "seyir" else poz
    kok_r0 = kok.rotation_euler.copy()
    kok_z0 = kok.location.z
    a_arm, k_arm = ekip["abi"]["arm"], ekip["kardes"]["arm"]
    kemikler = ("spine03", "spine04", "neck01", "head", "upperarm01.R", "lowerarm01.R", "upperarm01.L")
    a_q0 = {b: a_arm.pose.bones[b].rotation_quaternion.copy() for b in kemikler if b in a_arm.pose.bones}
    k_q0 = {b: k_arm.pose.bones[b].rotation_quaternion.copy() for b in kemikler if b in k_arm.pose.bones}

    for f in range(f0, f1 + 1):
        bpy.context.scene.frame_set(f)
        ph = math.tau * (f - f0) / max(1, (f1 - f0 + 1))
        # 1. Gentle boat roll & pitch on the swell
        roll = math.radians(1.6) * math.sin(ph)
        pitch = math.radians(0.9) * math.cos(ph)
        kok.rotation_euler = (kok_r0.x + pitch, kok_r0.y + roll, kok_r0.z)
        kok.location.z = kok_z0 + 0.035 * math.sin(ph - 0.4)
        kok.keyframe_insert(data_path="rotation_euler", frame=f)
        kok.keyframe_insert(data_path="location", index=2, frame=f)

        # 2. Younger brother (Latif at the tiller): calm breathing + helm micro-adjustment / wave in kalkis
        nefes_k = math.radians(1.4) * math.sin(ph)
        for b, q0 in k_q0.items():
            pb = k_arm.pose.bones[b]
            dq = Quaternion()
            if b in ("spine03", "spine04"):
                dq = Quaternion(Vector((1, 0, 0)), nefes_k)
            elif b == "head":
                dq = Quaternion(Vector((0, 0, 1)), math.radians(1.8) * math.cos(ph))
            elif b == "lowerarm01.R" and an == "kalkis":
                dq = Quaternion(Vector((0, 0, 1)), math.radians(12.0) * math.sin(ph * 2.0))
            pb.rotation_quaternion = q0 @ dq
            pb.keyframe_insert(data_path="rotation_quaternion", frame=f)

        # 3. Elder brother (Yusuf fishing on deck): phase-offset breathing + rod bob / catch pull
        nefes_a = math.radians(1.7) * math.sin(ph + 1.1)
        for b, q0 in a_q0.items():
            pb = a_arm.pose.bones[b]
            dq = Quaternion()
            if b in ("spine03", "spine04"):
                dq = Quaternion(Vector((1, 0, 0)), nefes_a)
            elif b == "head":
                dq = Quaternion(Vector((1, 0, 0)), math.radians(2.0) * math.sin(ph + 0.5))
            elif b == "upperarm01.R" and an in ("olta", "olta_vurus", "tuttu"):
                amp = 3.5 if an in ("olta", "olta_vurus") else 6.0
                dq = Quaternion(Vector((1, 0, 0)), math.radians(amp) * math.sin(ph))
            pb.rotation_quaternion = q0 @ dq
            pb.keyframe_insert(data_path="rotation_quaternion", frame=f)
    bpy.context.scene.frame_set(f0)


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
