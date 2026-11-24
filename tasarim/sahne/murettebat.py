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
    """One musculature knob, the way character creators do it: a single strength drives arms,
    shoulders, back, chest and neck together (neck widening capped at 0.38), so no limb ends up
    stick-thin next to a broad chest. Clothes are fitted afterwards, so they follow the build."""
    g = {"armslegs/{s}-upperarm-muscle-incr": 1.05, "armslegs/{s}-upperarm-fat-incr": 0.38,
         "armslegs/{s}-upperarm-scale-depth-incr": 0.68, "armslegs/{s}-upperarm-scale-horiz-incr": 0.68,
         "armslegs/{s}-upperarm-shoulder-muscle-incr": 0.72,
         "armslegs/{s}-lowerarm-muscle-incr": 1.05, "armslegs/{s}-lowerarm-fat-incr": 0.35,
         "armslegs/{s}-lowerarm-scale-depth-incr": 0.62, "armslegs/{s}-lowerarm-scale-horiz-incr": 0.72,
         "torso/torso-vshape-incr": 0.68, "torso/torso-muscle-dorsi-incr": 0.62,
         "torso/torso-muscle-pectoral-incr": 0.46,
         "torso/torso-scale-horiz-incr": 0.16, "torso/torso-scale-depth-incr": 0.12,
         "neck/neck-scale-horiz-incr": 0.36, "neck/neck-scale-depth-incr": 0.22}
    tavan = {"neck/neck-scale-horiz-incr": 0.38, "neck/neck-scale-depth-incr": 0.24}
    return {k: min(v * guc, tavan.get(k, 9.0)) for k, v in g.items()}


YUSUF = dict(
    name="yusuf",
    m=dict(sex=1.0, age=0.455, muscle=0.86, weight=0.50, boy=1.81, proportions=0.52, race=IRK),  # 23, natural athlete
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
    ten=(0.30, 0.62), sac=(0.43, 0.53), goz=("mavi", 0.38),
    sac_stil="kisa_kivircik", kakul=False, sakal="kisa_sakal", sakal_renk=(0.44, 0.54),
    sac_parlak=False, sac_boya=True, sac_hacim=0.008,
    kas_stil="thick_warm", kas_kalin=1.28, kas_kavis=0.26,
    yuz=("smile", 0.10), bas_don=0.0, bas_eg=0.0,
    giysi=[("clothes", "male_casualsuit04", ["#464E35", "#2B231D"]), ("clothes", "shoes06", "#4A3426")],
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
        "torso/torso-vshape-decr": 0.22,
        "torso/torso-scale-horiz-decr": 0.16,
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
    so facial anatomy, lips, nose, pectorals, and dual-layer beard masks have full hero resolution."""
    from insan import mh, ten
    _, uv, faces = mh.base()
    bf = [(f, u) for f, u, g in faces if g == "body" and not all(int(i) in hidden for i in f)]
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
    """Tailor the shirt onto the unbroken 13,380-vertex athletic V-taper body (p['co']):
    hugs broad shoulders, deep pectoral chest, and narrow waist smoothly (no shoulder bunching,
    and tucks the trouser waistband under the shirt hem so zero triangles poke through)."""
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
        hem_koru = anime.ss(t_z, 0.0, 0.12) * (1.0 - 0.55 * anime.ss(t_z, 0.72, 0.95))
        yakin, nrm, _, _ = agac.find_nearest(co)
        if yakin is not None:
            siki = (0.62 if (ax < 0.19 and t_z < 0.72) else 0.35) * hem_koru
            hedef = yakin + nrm * 0.0052
            co = co * (1.0 - siki) + hedef * siki
        yeni[i] = co
    # Tuck upper trouser waistband vertices slightly inward below the shirt hem
    for i in alt_v:
        co = yeni[i]
        if co.z > z_min - 0.03:
            yakin, nrm, _, _ = agac.find_nearest(co)
            if yakin is not None:
                yeni[i] = co * 0.45 + (yakin + nrm * 0.0018) * 0.55
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

    n, L = mat.node_tree.nodes, mat.node_tree.links
    rgb = next((nd for nd in n if nd.type == "RGB"), None)
    if rgb is None:
        return
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs["Vector"])
    u_n = mz._math(n, L, "MULTIPLY_ADD", sep.outputs["X"], 1.0 / (2.0 * w_yarim), 0.5)
    v_n = mz._math(n, L, "MULTIPLY_ADD", mz._math(n, L, "SUBTRACT", sep.outputs["Z"], z_alt), 1.0 / (z_ust - z_alt), 0.0)
    comb = n.new("ShaderNodeCombineXYZ")
    L.new(u_n, comb.inputs["X"]); L.new(v_n, comb.inputs["Y"])
    tx = n.new("ShaderNodeTexImage"); tx.image = img; tx.extension = "CLIP"
    L.new(comb.outputs["Vector"], tx.inputs["Vector"])
    on_m = mz._math(n, L, "LESS_THAN", sep.outputs["Y"], -0.02)
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
    hareket(kardes, "otur")
    if an == "kalkis":       # waves back to the quay while holding the tiller
        hareket(kardes, "el_salla", sadece=UST_SAG)
    elif an == "varis":      # hand at the brow against the low sun, looking at the town
        hareket(kardes, "siper", sadece=UST_SAG)
    ic_k, dis_k = yerlestir(kardes, kok, (0.46, -2.66), math.radians(-143), OTURAK_Z, True)
    ayaklar_yere(kardes, ic_k, dis_k, 0.36, 0.13)
    dik_otur(c, {"dumen": -3.0, "olta": 3.0, "olta_vurus": 1.0, "tuttu": -1.0, "varis": -2.0}.get(an, 0.0))
    el_uygula(kardes, kavra_k, ".L")
    if an == "kalkis":
        bas(c, 24.0, -4.0); gulus(kardes, 0.45)
    elif an == "varis":
        bas(c, -10.0, 0.0); gulus(kardes, 0.2)
    else:
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
        hareket(abi, "dur")
        hareket(abi, "ip_cek", sadece=UST)
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
        hareket(abi, "otur")
        ic_a, dis_a = yerlestir(abi, kok, (0.30, -1.6), math.radians(-90), SANDIK_Z, True)
        ayaklar_yere(abi, ic_a, dis_a, 0.40, 0.12)
        dik_otur(a, 2.0)
        bas(a, -16.0, -14.0); gulus(abi, 0.35)
    elif an in ("olta", "olta_vurus", "tuttu"):   # Yusuf seated on the midship crate, fishing over the port-forward rail
        hareket(abi, "otur")
        hareket(abi, "olta" if an in ("olta", "olta_vurus") else "cekti", sadece=UST)
        ic_a, dis_a = yerlestir(abi, kok, (0.26, -1.55), math.radians(-82), SANDIK_Z, True)
        ayaklar_yere(abi, ic_a, dis_a, 0.38, 0.12)
        dik_otur(a, {"olta": 4.0, "olta_vurus": 1.5, "tuttu": -2.0}[an])
        yon = {
            "olta": Vector((-0.82, 0.28, 0.50)).normalized(),
            "olta_vurus": Vector((-0.78, 0.26, 0.58)).normalized(),
            "tuttu": Vector((-0.65, 0.24, 0.72)).normalized(),
        }[an]
        hedef_el = Vector((-0.18, -1.35, {"olta": 1.50, "olta_vurus": 1.57, "tuttu": 1.70}[an]))
        kol(a, ".R", ic_a(hedef_el), (0.2, -0.4, -1.0))
        kol(a, ".L", ic_a(hedef_el - yon * 0.18), (-0.2, -0.4, -1.0))
        el_uygula(abi, kavra_a, ".R"); el_uygula(abi, kavra_a, ".L")
        bas(a, -14.0, {"olta": 6.0, "olta_vurus": 1.0, "tuttu": -14.0}[an])
        gulus(abi, {"olta": 0.2, "olta_vurus": 0.45, "tuttu": 0.85}[an])
        bpy.context.view_layer.update()
        el = dis_a(avuc(a, ".R"))
        uc = el + yon * 2.05
        cizim.append(("cubuk", "Olta", el - yon * 0.34, uc, 0.022, "kusak"))
        if an in ("olta", "olta_vurus"):
            cizim.append(("cubuk", "Misina", uc, Vector((uc.x - 0.35, uc.y + 0.15, -0.05)), 0.006, "halat"))
        else:
            balik = uc + Vector((0.0, 0.0, -0.72))
            cizim += [("cubuk", "Misina", uc, balik + Vector((0, 0, 0.26)), 0.006, "halat"), ("balik", balik)]
    else:                    # varis: beside the mast, points clearly over port bow at the town
        hareket(abi, "dur")
        hareket(abi, "goster", sadece=UST_SAG)
        y = 0.68
        ic_a, dis_a = yerlestir(abi, kok, (-0.24, y), math.radians(142), guverte_z(y), False)
        yere_bas(abi, kok, guverte_z(y))
        kol(a, ".R", ic_a(Vector((-0.95, y + 0.62, 2.02))), (0.25, -0.4, -1.0))
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


def balik_tut(ekip, kok, yeke_pivot, f0=1, harman=5):
    """Key the whole fishing sequence and return one record per frame for the props.

    The elder brother plays captured seated-fishing motion in order (wait, cast, wait for the bite,
    strike, fight the fish, land it, settle), retargeted frame by frame onto his upper body, with
    short crossfades between clips; his hands keep their grip. Latif first pushes the tiller over
    to round the boat up and stop it, holds it there with small corrections, turns to watch the
    fight and smiles at the catch. The hull rides the swell throughout.
    Records: f, faz (phase), u (0..1 inside the phase), el_R, el_L, yon (rod axis), all boat-local."""
    t = _tablo()
    tps = t.get("tps", 4800)
    abi, kardes = ekip["abi"], ekip["kardes"]
    a, c = abi["arm"], kardes["arm"]
    Y = ekip["yer"]
    ic_a, dis_a, ic_k, dis_k = Y["ic_a"], Y["dis_a"], Y["ic_k"], Y["dis_k"]
    for arm in (a, c):
        for pb in arm.pose.bones:
            pb.rotation_mode = "QUATERNION"
    # timeline: (phase, retargeter, tick, u)
    akt = {}
    akis = []
    for faz, ad, tekrar in t["akislar"]["balik_tut"]:
        k = _klip(ad)
        if ad not in akt:
            akt[ad] = xklip.Aktarici(k, a)
        n = max(2, round((k.t1 - k.t0) / tps * 24))
        toplam = n * tekrar
        for j in range(toplam):
            tik = k.t0 + (k.t1 - k.t0) * ((j % n) / n if tekrar > 1 else j / (n - 1))
            akis.append((faz, ad, tik, j / max(1, toplam - 1)))
    # Latif's rest state
    pbk = c.pose.bones
    bpy.context.view_layer.update()
    el0 = dis_k(avuc(c, ".L"))
    pv = Vector(yeke_pivot)
    v0 = el0 - pv
    k_q0 = {b: pbk[b].rotation_quaternion.copy() for b in ("head", "neck01", "spine03", "spine04")}
    kol_k = ["upperarm01.L", "lowerarm01.L", "wrist.L"] + [b + ".L" for b in PARMAK]
    ust_a = sorted(UST)
    kok_r0 = kok.rotation_euler.copy(); kok_z0 = kok.location.z
    kayit = []
    onceki = None
    yon_onceki = None
    f = f0
    for i, (faz, ad, tik, u) in enumerate(akis):
        sc = bpy.context.scene
        sc.frame_set(f)
        # 1. hull on the swell (4 s period)
        ph = math.tau * (f - f0) / 96.0
        kok.rotation_euler = (kok_r0.x + math.radians(0.9) * math.cos(ph), kok_r0.y + math.radians(1.6) * math.sin(ph), kok_r0.z)
        kok.location.z = kok_z0 + 0.035 * math.sin(ph - 0.4)
        kok.keyframe_insert("rotation_euler", frame=f); kok.keyframe_insert("location", index=2, frame=f)
        # 2. elder brother: the clip, crossfaded from the previous clip's last moment
        A = akt[ad]
        w = 1.0
        bas_i = next(q for q in range(i, -1, -1) if q == 0 or akis[q - 1][1] != ad or akis[q - 1][0] != faz)
        if bas_i > 0 and i - bas_i < harman:
            pf = akis[bas_i - 1]
            akt[pf[1]].poz(pf[2], sadece=UST)
            w = (i - bas_i + 1) / (harman + 1)
        A.poz(tik, sadece=UST, agirlik=w)
        el_uygula(abi, ekip["kavra_a"], ".R")
        el_uygula(abi, ekip["kavra_a"], ".L")
        bpy.context.view_layer.update()
        _anahtarla(a, ust_a, f)
        R = A.tutamak(tik, "R")[1]
        yon = (dis_a(Vector(R[:, 1].tolist())) - dis_a(Vector((0, 0, 0)))).normalized()   # prop Y = rod
        if w < 1.0 and yon_onceki is not None:
            yon = yon_onceki.lerp(yon, w).normalized()
        yon_onceki = yon
        gulus_a = {"vurus": 0.45, "cekis": 0.35, "al": 0.35 + 0.5 * min(1.0, u * 3), "son": 0.85}.get(faz, 0.2)
        _gulus_anahtar(abi, gulus_a, f)
        # 3. Latif: tiller hard over to stop the boat, then held with small corrections
        if faz == "durdur":
            ac = 24.0 * (u * u * (3 - 2 * u))
        else:
            ac = 24.0 - 6.0 * min(1.0, i / 200.0) + 1.5 * math.sin(f * 0.11)
        hedef = pv + Matrix.Rotation(math.radians(ac), 4, "Z") @ v0
        kol(c, ".L", ic_k(hedef), (-0.2, -0.4, -1.0))
        el_uygula(kardes, ekip["kavra_k"], ".L")
        izle = {"durdur": 0.0, "atis": 0.3, "bekle": 0.4, "vurus": 0.9, "cekis": 1.0, "al": 1.0, "son": 0.7}[faz]
        nefes = math.radians(1.4) * math.sin(ph * 3)
        pbk["head"].rotation_quaternion = k_q0["head"] @ Quaternion(Vector((0, 0, 1)), math.radians(28.0 * izle))             @ Quaternion(Vector((1, 0, 0)), math.radians(6.0 * izle))
        pbk["spine03"].rotation_quaternion = k_q0["spine03"] @ Quaternion(Vector((1, 0, 0)), nefes + math.radians(5 * izle))
        _anahtarla(c, kol_k + ["head", "spine03"], f)
        gulus_k = {"vurus": 0.55, "cekis": 0.6, "al": 0.6 + 0.3 * min(1.0, u * 3), "son": 0.85}.get(faz, 0.3)
        _gulus_anahtar(kardes, gulus_k, f)
        bpy.context.view_layer.update()
        kayit.append(dict(f=f, faz=faz, u=u, el_R=dis_a(avuc(a, ".R")), el_L=dis_a(avuc(a, ".L")), yon=yon,
                          yeke=dis_k(avuc(c, ".L"))))
        onceki = (ad, faz)
        f += 1
    bpy.context.scene.frame_set(f0)
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
