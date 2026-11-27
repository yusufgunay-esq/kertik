# Kertik "Sefer" 3D scene: close chase camera, soft sunlight, coloured shadows, aerial haze.
# A small Aegean fishing boat with a red lateen sail leaves one harbour and reaches another.
#   blender -b --factory-startup --python sefer3d.py -- still <sahne> <vakit> <out.png> [width]
#     sahne: kalkis | seyir | varis      vakit: gun | aksam | sabah | gece
#   blender -b --factory-startup --python sefer3d.py -- kaydet <sahne> <vakit> <file.blend>
import bpy, bmesh, math, random, sys, os
import numpy as np
from mathutils import Vector, Matrix, noise

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["still", "seyir", "gun", "test.png"]
KOMUT, SAHNE, VAKIT = ARGS[0], ARGS[1], ARGS[2]
CIKTI = os.path.abspath(ARGS[3])
GEN = int(ARGS[4]) if len(ARGS) > 4 else 540
TAU = math.tau
F = 300


def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)


def ss(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- times of day
VAKITLER = {
    "gun": dict(
        zenit="#1F62B8", orta="#4E98DA", ufuk="#B3D6EA", pus="#D4E4E8", sis=950.0,
        gunes=(-0.55, -0.45, 0.62), gunes_renk="#FFEACB", gunes_guc=5.2, gok_guc=1.0,
        deniz="#1C76AE", turkuaz="#3BB8D4", kopuk="#F3F5F1",
        kaya=["#CFAC7E", "#B98F63", "#A57A52", "#DCC096"], ot="#DDB43C", ot2="#C58E2A",
        yaprak=["#3B4C2B", "#566831", "#7C893B", "#A4A24A", "#C4B85E"],
        badana="#F1EEE8", kiremit="#C26A46", kapi="#2F6E8C", agac="#3F6B45", servi="#2E5541",
        tas="#E3D7C2", fener_cam="#F4E2A8", fener_bant="#3E5C6E", kabuk="#6E4E3A",
    ),
    "aksam": dict(
        zenit="#3A4F86", orta="#C98C8A", ufuk="#F6C98F", pus="#EFC79A", sis=900.0,
        gunes=(-0.55, 0.80, 0.16), gunes_renk="#FFB777", gunes_guc=4.6, gok_guc=0.8,
        deniz="#273E5E", turkuaz="#3B7F8F", kopuk="#FBE9D2",
        kaya=["#E2B38C", "#CC9573", "#B07A60", "#EBC9A2"], ot="#E0A646", ot2="#C2783A",
        yaprak=["#3A3B33", "#56553A", "#7A7440", "#A6914E", "#C9A85E"],
        badana="#F6E4D0", kiremit="#C9653F", kapi="#35607C", agac="#4C5E45", servi="#36493E",
        tas="#E8D6C0", fener_cam="#FFD58A", fener_bant="#4A4F66", kabuk="#6A4637",
    ),
}
V = VAKITLER.get(VAKIT, VAKITLER["gun"])
GUNES = Vector(V["gunes"]).normalized()

# ---------------------------------------------------------------- scene layout per stage
# Camera sits at the origin looking along +Y; the boat sails ahead of it.
KAMERA_Y = 4.6          # camera height (m)
EGIM = 8.5              # pitch down (deg)
YAW = 0.0               # yaw left (deg)
YARI_FOV = 26.0         # vertical half field of view (deg)
TEKNE = dict(kalkis=(0.3, 14.0, 14.0), seyir=(-0.5, 14.0, 22.0), varis=(-0.4, 14.0, 16.0))[SAHNE]
TX, TY, TPSI = TEKNE
HD = Vector((-math.sin(math.radians(TPSI)), math.cos(math.radians(TPSI)), 0.0))   # heading
_POZ_ARG = ARGS[5] if len(ARGS) > 5 else "dumen"
YELKEN = 0.0 if (SAHNE == "kalkis" or _POZ_ARG in ("kalkis", "mola", "balik")) else (0.5 if SAHNE == "varis" else 1.0)
HIZ = 0.08 if _POZ_ARG == "balik" else dict(kalkis=0.0, seyir=1.0, varis=0.35)[SAHNE]   # fishing: sail furled, drifting

random.seed(11)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, F


def bagla(ob):
    sc.collection.objects.link(ob)
    return ob


def mesh_nesne(ad, verts, faces, mat=None, smooth=True):
    me = bpy.data.meshes.new(ad)
    me.from_pydata(verts, [], faces)
    me.validate()
    for p in me.polygons:
        p.use_smooth = smooth
    ob = bpy.data.objects.new(ad, me)
    if mat:
        me.materials.append(mat)
    return bagla(ob)


# ---------------------------------------------------------------- material helpers
BAND = (0.20, 0.34)                 # sun-normalised light: shadow -> lit (soft)
GOLGE = (0.70, 0.66, 0.85, 1.0)     # shadow multiplier, warm lilac
SICAK = (1.0, 0.92, 0.78, 1.0)      # warm rim


class Agac:
    def __init__(self, ad):
        self.m = bpy.data.materials.new(ad)
        self.m.use_nodes = True
        self.nt = self.m.node_tree
        for n in list(self.nt.nodes):
            self.nt.nodes.remove(n)
        self.out = self.n("ShaderNodeOutputMaterial")

    def n(self, tip):
        return self.nt.nodes.new(tip)

    def b(self, a, c):
        self.nt.links.new(a, c)

    def m_(self, op, a, b=None):
        n = self.n("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                self.b(v, n.inputs[i])
        return n.outputs[0]

    def aralik(self, v, a, b, c=0.0, d=1.0):
        n = self.n("ShaderNodeMapRange"); n.interpolation_type = "SMOOTHSTEP"
        n.inputs["From Min"].default_value, n.inputs["From Max"].default_value = a, b
        n.inputs["To Min"].default_value, n.inputs["To Max"].default_value = c, d
        self.b(v, n.inputs["Value"])
        return n.outputs["Result"]

    def karis(self, f, a, c):
        n = self.n("ShaderNodeMix"); n.data_type = "RGBA"
        for sok, v in ((n.inputs[0], f), (n.inputs[6], a), (n.inputs[7], c)):
            if isinstance(v, (int, float)):
                sok.default_value = v
            elif isinstance(v, tuple):
                sok.default_value = v
            else:
                self.b(v, sok)
        return n.outputs[2]

    def rampa(self, f, duraklar, interp="LINEAR"):
        r = self.n("ShaderNodeValToRGB"); cr = r.color_ramp; cr.interpolation = interp
        cr.elements[0].position, cr.elements[0].color = duraklar[0][0], lin(duraklar[0][1])
        cr.elements[1].position, cr.elements[1].color = duraklar[-1][0], lin(duraklar[-1][1])
        for p, c in duraklar[1:-1]:
            e = cr.elements.new(p); e.color = lin(c)
        self.b(f, r.inputs["Fac"])
        return r.outputs["Color"]

    def gurultu(self, olcek, detay=3.0, vektor=None):
        nz = self.n("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = olcek
        nz.inputs["Detail"].default_value = detay
        if vektor is not None:
            self.b(vektor, nz.inputs["Vector"])
        return nz.outputs["Fac"]

    def dunya(self):
        g = self.n("ShaderNodeNewGeometry")
        return g

    def yuzey(self, renk, rough=0.75, spec=0.3, boya=True):
        p = self.n("ShaderNodeBsdfPrincipled")
        if isinstance(renk, tuple):
            p.inputs["Base Color"].default_value = renk
        else:
            self.b(renk, p.inputs["Base Color"])
        p.inputs["Roughness"].default_value = rough
        p.inputs["Specular IOR Level"].default_value = spec
        return (self.boya(renk) if boya else p.outputs[0]), p

    def carp(self, a, c):
        n = self.n("ShaderNodeMix"); n.data_type = "RGBA"; n.blend_type = "MULTIPLY"
        n.inputs[0].default_value = 1.0
        for sok, v in ((n.inputs[6], a), (n.inputs[7], c)):
            if isinstance(v, tuple):
                sok.default_value = v
            else:
                self.b(v, sok)
        return n.outputs[2]

    def boya(self, renk):
        """Illustrated shading shared with the crew: diffuse light normalised by the sun, one soft
        band, shadow as a cool lavender multiplier (never black), a warm rim where the sun grazes."""
        if isinstance(renk, tuple):
            rgb = self.n("ShaderNodeRGB"); rgb.outputs[0].default_value = renk
            renk = rgb.outputs[0]
        d = self.n("ShaderNodeBsdfDiffuse"); d.inputs["Color"].default_value = (1, 1, 1, 1)
        s2r = self.n("ShaderNodeShaderToRGB"); self.b(d.outputs[0], s2r.inputs[0])
        bw = self.n("ShaderNodeRGBToBW"); self.b(s2r.outputs["Color"], bw.inputs[0])
        isik = self.m_("MULTIPLY", bw.outputs[0], 1 / (V["gunes_guc"] * 1.15))
        bant = self.aralik(isik, *BAND)
        col = self.karis(bant, self.carp(renk, GOLGE), renk)
        lw = self.n("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.3
        kenar = self.m_("MULTIPLY", self.m_("POWER", lw.outputs["Facing"], 3.0), self.m_("MULTIPLY", bant, 0.16))
        ek = self.n("ShaderNodeMix"); ek.data_type = "RGBA"; ek.blend_type = "SCREEN"
        self.b(kenar, ek.inputs[0]); self.b(col, ek.inputs[6]); ek.inputs[7].default_value = SICAK
        em = self.n("ShaderNodeEmission"); self.b(ek.outputs[2], em.inputs["Color"])
        em.inputs["Strength"].default_value = 1.27
        return em.outputs[0]

    def bitir(self, s, sis=True):
        if sis:
            s = self.sisle(s)
        self.b(s, self.out.inputs["Surface"])
        return self.m

    def sisle(self, s):
        """Aerial perspective: surfaces fade into the horizon haze with distance."""
        cam = self.n("ShaderNodeCameraData")
        e = self.m_("EXPONENT", self.m_("DIVIDE", cam.outputs["View Distance"], -V["sis"]))
        f = self.m_("SUBTRACT", 1.0, e)
        em = self.n("ShaderNodeEmission"); em.inputs["Color"].default_value = lin(V["pus"])
        mx = self.n("ShaderNodeMixShader")
        self.b(f, mx.inputs[0]); self.b(s, mx.inputs[1]); self.b(em.outputs[0], mx.inputs[2])
        return mx.outputs[0]


def duz_malzeme(ad, renk, rough=0.75, spec=0.3, oynak=0.0, olcek=0.6):
    A = Agac(ad)
    if oynak:
        g = A.gurultu(olcek, 2.0)
        c = A.karis(A.aralik(g, 0.3, 0.7), lin(renk), tuple(x * (1 - oynak) for x in lin(renk)[:3]) + (1,))
    else:
        c = lin(renk)
    s, _ = A.yuzey(c, rough, spec)
    return A.bitir(s)


def kaya_malzeme():
    A = Agac("Kaya")
    geo = A.dunya()
    sep = A.n("ShaderNodeSeparateXYZ"); A.b(geo.outputs["Position"], sep.inputs[0])
    z = sep.outputs["Z"]
    # sediment bands, warped by noise
    w = A.n("ShaderNodeTexWave"); w.wave_type = "BANDS"; w.bands_direction = "Z"
    w.inputs["Scale"].default_value = 0.022; w.inputs["Distortion"].default_value = 9.0
    w.inputs["Detail"].default_value = 2.0
    A.b(geo.outputs["Position"], w.inputs["Vector"])
    k = V["kaya"]
    renk = A.rampa(w.outputs["Fac"], [(0.0, k[0]), (0.4, k[1]), (0.62, k[1]), (0.85, k[3]), (1.0, k[0])])
    # vegetation on gentle slopes above the shore
    nz = A.n("ShaderNodeSeparateXYZ"); A.b(geo.outputs["Normal"], nz.inputs[0])
    duz = A.aralik(nz.outputs["Z"], 0.55, 0.72)
    yuk = A.aralik(z, 1.2, 2.6)
    leke = A.aralik(A.gurultu(0.05, 3.0), 0.22, 0.32)
    ot_f = A.m_("MULTIPLY", A.m_("MULTIPLY", duz, yuk), leke)
    # golden grass with long brush strokes (noise stretched along one axis)
    sk = A.n("ShaderNodeVectorMath"); sk.operation = "MULTIPLY"
    sk.inputs[1].default_value = (0.25, 1.6, 1.6)
    A.b(geo.outputs["Position"], sk.inputs[0])
    firca = A.aralik(A.gurultu(0.9, 4.0, sk.outputs[0]), 0.5, 0.62)
    ot = A.karis(firca, lin(V["ot"]), lin(V["ot2"]))
    ot = A.karis(A.m_("MULTIPLY", A.aralik(A.gurultu(0.12, 2.0), 0.55, 0.7), 0.6), ot, lin("#9A9A45"))
    renk = A.karis(ot_f, renk, ot)
    # wet rock and foam at the waterline
    kenar = A.m_("ADD", z, A.m_("MULTIPLY", A.m_("SUBTRACT", A.gurultu(0.6, 2.0), 0.5), 0.5))
    islak = A.aralik(kenar, 0.9, 0.3)
    renk = A.karis(A.m_("MULTIPLY", islak, 0.45), renk, lin("#5E4B3C"))
    kopuk = A.aralik(kenar, 0.42, 0.28)
    renk = A.karis(kopuk, renk, lin(V["kopuk"]))
    s, _ = A.yuzey(renk, 0.85, 0.2)
    return A.bitir(s)


def yaprak_malzeme(ad, koyu=0.0):
    """Painted foliage: light measured per pixel, mapped onto a soft olive-to-yellow ramp."""
    A = Agac(ad)
    d = A.n("ShaderNodeBsdfDiffuse"); d.inputs["Color"].default_value = (1, 1, 1, 1)
    s2r = A.n("ShaderNodeShaderToRGB"); A.b(d.outputs[0], s2r.inputs[0])
    bw = A.n("ShaderNodeRGBToBW"); A.b(s2r.outputs["Color"], bw.inputs[0])
    isik = A.m_("MULTIPLY", bw.outputs[0], 1 / (V["gunes_guc"] * 1.15))
    g = A.gurultu(2.4, 4.0)
    isik = A.m_("ADD", isik, A.m_("MULTIPLY", A.m_("SUBTRACT", g, 0.5), 0.35))
    isik = A.m_("SUBTRACT", isik, koyu)
    y = V["yaprak"]
    renk = A.rampa(isik, [(0.0, y[0]), (0.22, y[1]), (0.45, y[2]), (0.7, y[3]), (0.95, y[4])])
    em = A.n("ShaderNodeEmission"); A.b(renk, em.inputs["Color"]); em.inputs["Strength"].default_value = 1.0
    return A.bitir(em.outputs[0])


def tas_malzeme():
    A = Agac("Tas")
    geo = A.dunya()
    br = A.n("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 0.45
    br.inputs["Mortar Size"].default_value = 0.012
    br.inputs["Color1"].default_value = lin(V["tas"])
    br.inputs["Color2"].default_value = tuple(x * 0.86 for x in lin(V["tas"])[:3]) + (1,)
    br.inputs["Mortar"].default_value = tuple(x * 0.7 for x in lin(V["tas"])[:3]) + (1,)
    br.inputs["Row Height"].default_value = 0.5
    A.b(geo.outputs["Position"], br.inputs["Vector"])
    c = A.karis(A.m_("MULTIPLY", A.aralik(A.gurultu(0.4, 3.0), 0.45, 0.7), 0.25), br.outputs["Color"], lin("#A89A80"))
    s, _ = A.yuzey(c, 0.85, 0.2)
    return A.bitir(s)


def bayrak_malzeme():
    A = Agac("Bayrak")
    A.m.use_backface_culling = False
    img = A.n("ShaderNodeTexImage")
    img.image = bpy.data.images.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bayrak.png"))
    img.extension = "EXTEND"
    uv = A.n("ShaderNodeUVMap"); A.b(uv.outputs[0], img.inputs["Vector"])
    d, p = A.yuzey(img.outputs["Color"], 0.8, 0.2)
    t = A.n("ShaderNodeBsdfTranslucent"); A.b(img.outputs["Color"], t.inputs["Color"])
    mx = A.n("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.3
    A.b(d, mx.inputs[1]); A.b(t.outputs[0], mx.inputs[2])
    return A.bitir(mx.outputs[0])


def badana_malzeme(ad, renk):
    A = Agac(ad)
    g = A.gurultu(0.9, 3.0)
    c = A.karis(A.aralik(g, 0.35, 0.7), lin(renk), tuple(x * 0.9 for x in lin(renk)[:3]) + (1,))
    s, _ = A.yuzey(c, 0.8, 0.25)
    return A.bitir(s)


def deniz_malzeme():
    A = Agac("Deniz")
    p_s, p = A.yuzey(lin(V["deniz"]), 0.2, 0.55, boya=False)
    p.inputs["IOR"].default_value = 1.33
    lw = A.n("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    govde = A.m_("POWER", A.m_("SUBTRACT", 1.0, lw.outputs["Facing"]), 2.0)
    em = A.n("ShaderNodeEmission"); em.inputs["Color"].default_value = lin(V["turkuaz"])
    A.b(A.m_("MULTIPLY", govde, 0.55), em.inputs["Strength"])
    add = A.n("ShaderNodeAddShader"); A.b(p_s, add.inputs[0]); A.b(em.outputs[0], add.inputs[1])
    yuzey = add.outputs[0]
    # wake: V arms + centre trail behind the stern, ring around the hull
    geo = A.dunya()
    sp = A.n("ShaderNodeSeparateXYZ"); A.b(geo.outputs["Position"], sp.inputs[0])
    L = 3.6
    kx, ky = TX - HD.x * L, TY - HD.y * L
    dx = A.m_("SUBTRACT", sp.outputs["X"], kx); dy = A.m_("SUBTRACT", sp.outputs["Y"], ky)
    u = A.m_("MULTIPLY", A.m_("ADD", A.m_("MULTIPLY", dx, HD.x), A.m_("MULTIPLY", dy, HD.y)), -1.0)
    v = A.m_("ABSOLUTE", A.m_("ADD", A.m_("MULTIPLY", dx, -HD.y), A.m_("MULTIPLY", dy, HD.x)))
    on = A.aralik(u, 0.0, 1.0)
    kol_d = A.m_("ABSOLUTE", A.m_("SUBTRACT", v, A.m_("MULTIPLY", u, 0.354)))
    n_ = A.n("ShaderNodeMapRange"); n_.interpolation_type = "SMOOTHSTEP"
    n_.inputs["From Min"].default_value = 0.0
    A.b(A.m_("ADD", A.m_("MULTIPLY", u, 0.03), 0.22), n_.inputs["From Max"])
    n_.inputs["To Min"].default_value, n_.inputs["To Max"].default_value = 1.0, 0.0
    A.b(kol_d, n_.inputs["Value"])
    kol = A.m_("MULTIPLY", n_.outputs["Result"], A.m_("EXPONENT", A.m_("MULTIPLY", u, -1 / (6 + 22 * HIZ))))
    o_ = A.n("ShaderNodeMapRange"); o_.interpolation_type = "SMOOTHSTEP"
    o_.inputs["From Min"].default_value = 0.0
    A.b(A.m_("ADD", A.m_("MULTIPLY", u, 0.05), 0.7), o_.inputs["From Max"])
    o_.inputs["To Min"].default_value, o_.inputs["To Max"].default_value = 1.0, 0.0
    A.b(v, o_.inputs["Value"])
    orta = A.m_("MULTIPLY", o_.outputs["Result"], A.m_("EXPONENT", A.m_("MULTIPLY", u, -1 / (4 + 10 * HIZ))))
    iz = A.m_("MULTIPLY", A.m_("MULTIPLY", A.m_("MAXIMUM", kol, orta), on), HIZ)
    ex = A.m_("SUBTRACT", sp.outputs["X"], TX); ey = A.m_("SUBTRACT", sp.outputs["Y"], TY)
    ea = A.m_("DIVIDE", A.m_("ADD", A.m_("MULTIPLY", ex, HD.x), A.m_("MULTIPLY", ey, HD.y)), 3.7)
    eb = A.m_("DIVIDE", A.m_("ADD", A.m_("MULTIPLY", ex, -HD.y), A.m_("MULTIPLY", ey, HD.x)), 1.3)
    er = A.m_("SQRT", A.m_("ADD", A.m_("MULTIPLY", ea, ea), A.m_("MULTIPLY", eb, eb)))
    halka = A.aralik(A.m_("ABSOLUTE", A.m_("SUBTRACT", er, 1.0)), 0.0, 0.22, 1.0, 0.0)
    halka = A.m_("MULTIPLY", halka, 0.35 + 0.65 * HIZ)
    iz = A.m_("MAXIMUM", iz, halka)
    vec = A.n("ShaderNodeCombineXYZ")
    A.b(A.m_("MULTIPLY", u, 0.6), vec.inputs["X"]); A.b(A.m_("MULTIPLY", v, 1.4), vec.inputs["Y"])
    doku = A.aralik(A.gurultu(1.5, 3.0, vec.outputs[0]), 0.36, 0.6, 0.1, 1.0)
    kopuk = A.aralik(A.m_("MULTIPLY", iz, doku), 0.22, 0.42)
    fm = A.n("ShaderNodeBsdfPrincipled"); fm.inputs["Base Color"].default_value = lin(V["kopuk"])
    fm.inputs["Roughness"].default_value = 0.6
    mx = A.n("ShaderNodeMixShader")
    A.b(kopuk, mx.inputs[0]); A.b(yuzey, mx.inputs[1]); A.b(fm.outputs[0], mx.inputs[2])
    return A.bitir(mx.outputs[0])


def yelken_malzeme():
    A = Agac("Yelken")
    geo = A.dunya()
    g = A.gurultu(2.2, 2.0)
    c = A.karis(A.aralik(g, 0.35, 0.65), lin("#B8452F"), lin("#A63A28"))
    d, p = A.yuzey(c, 0.85, 0.2)
    p.inputs["Subsurface Weight"].default_value = 0.15
    p.inputs["Subsurface Radius"].default_value = (0.3, 0.1, 0.05)
    t = A.n("ShaderNodeBsdfTranslucent"); t.inputs["Color"].default_value = lin("#D2633F")
    mx = A.n("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.22
    A.b(d, mx.inputs[1]); A.b(t.outputs[0], mx.inputs[2])
    A.m.use_backface_culling = False
    return A.bitir(mx.outputs[0])


def govde_malzeme():
    A = Agac("Govde")
    at = A.n("ShaderNodeAttribute"); at.attribute_name = "v"
    renk = A.rampa(at.outputs["Fac"], [(0.0, "#1F3547"), (0.30, "#1F3547"), (0.305, "#F1ECE2"),
                                         (0.70, "#F1ECE2"), (0.705, "#2F7F86"), (0.84, "#2F7F86"),
                                         (0.845, "#EDE6D8"), (1.0, "#EDE6D8")], "CONSTANT")
    g = A.gurultu(1.4, 3.0)
    renk = A.karis(A.m_("MULTIPLY", A.aralik(g, 0.45, 0.7), 0.12), renk, lin("#8A7F70"))
    s, _ = A.yuzey(renk, 0.55, 0.35)
    return A.bitir(s)


M = {}
M["kaya"] = kaya_malzeme()
M["badana"] = badana_malzeme("Badana", V["badana"])
M["badana2"] = badana_malzeme("Badana2", "#EADFCB")
M["kiremit"] = duz_malzeme("Kiremit", V["kiremit"], 0.8, 0.25, 0.18, 2.0)
M["kapi"] = duz_malzeme("Kapi", V["kapi"], 0.7, 0.3)
M["pencere"] = duz_malzeme("Pencere", "#2A3A44", 0.5, 0.3)
M["agac"] = yaprak_malzeme("Yaprak")
M["servi"] = yaprak_malzeme("Servi", 0.18)
M["govde_agac"] = duz_malzeme("Kutuk", V["kabuk"], 0.9, 0.2, 0.25, 3.0)
M["tas"] = tas_malzeme()
M["fener_bant"] = duz_malzeme("FenerBant", V["fener_bant"], 0.6, 0.3)
M["fener_cam"] = duz_malzeme("FenerCam", V["fener_cam"], 0.3, 0.5)
M["ahsap"] = duz_malzeme("Ahsap", "#7A5236", 0.65, 0.3, 0.15, 3.0)
M["guverte"] = duz_malzeme("Guverte", "#B58E66", 0.75, 0.25, 0.15, 4.0)
M["halat"] = duz_malzeme("Halat", "#C9B48E", 0.9, 0.1)
M["deniz"] = deniz_malzeme()
M["kopuk"] = duz_malzeme("Kopuk", V["kopuk"], 0.6, 0.3)
M["bayrak"] = bayrak_malzeme()
M["kusak"] = duz_malzeme("Kusak", "#6B4A30", 0.8, 0.2)
M["balik"] = duz_malzeme("Balik", "#C9D3D6", 0.25, 0.7)
M["balik_sirt"] = duz_malzeme("BalikSirt", "#3F5D72", 0.35, 0.5)
M["balik_goz"] = duz_malzeme("BalikGoz", "#151515", 0.2, 0.6)
M["yelken"] = yelken_malzeme()
M["govde"] = govde_malzeme()

# ---------------------------------------------------------------- sky
w = bpy.data.worlds.new("Gok"); sc.world = w
w.use_nodes = True
nt = w.node_tree
for n_ in list(nt.nodes):
    nt.nodes.remove(n_)
wo = nt.nodes.new("ShaderNodeOutputWorld")
tc = nt.nodes.new("ShaderNodeTexCoord")
nrm = nt.nodes.new("ShaderNodeVectorMath"); nrm.operation = "NORMALIZE"
nt.links.new(tc.outputs["Generated"], nrm.inputs[0])
sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(nrm.outputs[0], sep.inputs[0])
mr = nt.nodes.new("ShaderNodeMapRange")
mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = -0.02, 0.75
nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
gr = nt.nodes.new("ShaderNodeValToRGB"); c = gr.color_ramp; c.interpolation = "EASE"
c.elements[0].position, c.elements[0].color = 0.0, lin(V["pus"])
c.elements[1].position, c.elements[1].color = 1.0, lin(V["zenit"])
e_ = c.elements.new(0.06); e_.color = lin(V["ufuk"])
e_ = c.elements.new(0.30); e_.color = lin(V["orta"])
nt.links.new(mr.outputs["Result"], gr.inputs["Fac"])
# soft sun halo in the sky (visible only when the sun is in view)
dot = nt.nodes.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; dot.inputs[1].default_value = GUNES
nt.links.new(nrm.outputs[0], dot.inputs[0])
hm = nt.nodes.new("ShaderNodeMapRange")
hm.inputs["From Min"].default_value, hm.inputs["From Max"].default_value = 0.93, 1.0
hm.interpolation_type = "SMOOTHSTEP"
nt.links.new(dot.outputs["Value"], hm.inputs["Value"])
hx = nt.nodes.new("ShaderNodeMath"); hx.operation = "POWER"; hx.inputs[1].default_value = 3.0
nt.links.new(hm.outputs["Result"], hx.inputs[0])
mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
nt.links.new(hx.outputs[0], mix.inputs[0]); nt.links.new(gr.outputs["Color"], mix.inputs[6])
mix.inputs[7].default_value = lin("#FFF3DA")
bg = nt.nodes.new("ShaderNodeBackground"); bg.inputs["Strength"].default_value = V["gok_guc"]
nt.links.new(mix.outputs[2], bg.inputs["Color"])
nt.links.new(bg.outputs[0], wo.inputs["Surface"])

# ---------------------------------------------------------------- sea (camera fan grid + waves)
DALGALAR = [(0.25, 1.0, 19.0, 0.20, -1), (-0.55, 1.0, 9.0, 0.09, -2), (1.0, 0.35, 5.5, 0.03, 3),
            (-0.15, 1.0, 25.0, 0.16, -1), (0.05, 1.0, 3.6, 0.018, -5)]
satir = []
y = 4.0
while y < 2600:
    satir.append(y)
    y *= 1.035
acilar = [math.radians(-50 + i * (100 / 140)) for i in range(141)]
vs = []
for yy in satir:
    for a in acilar:
        da = math.radians(100 / 140)
        aa = a + random.uniform(-0.35, 0.35) * da
        ry = yy * (1 + random.uniform(-0.012, 0.012))
        vs.append((ry * math.tan(aa), ry, 0.0))
nc = len(acilar)
fs = []
for j in range(len(satir) - 1):
    for i in range(nc - 1):
        a, b = j * nc + i, j * nc + i + 1
        fs.append((a, b, (j + 1) * nc + i + 1, (j + 1) * nc + i))
deniz = mesh_nesne("Deniz", vs, fs, M["deniz"])
gn = bpy.data.node_groups.new("Dalga", "GeometryNodeTree")
gn.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
gn.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
N = gn.nodes
gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
pos = N.new("GeometryNodeInputPosition")
spn = N.new("ShaderNodeSeparateXYZ"); gn.links.new(pos.outputs[0], spn.inputs[0])
st = N.new("GeometryNodeInputSceneTime")


def mn(op, a=None, b=None, vb=None):
    n = N.new("ShaderNodeMath"); n.operation = op
    if a is not None:
        gn.links.new(a, n.inputs[0])
    if b is not None:
        gn.links.new(b, n.inputs[1])
    elif vb is not None:
        n.inputs[1].default_value = vb
    return n.outputs[0]


top = None
for dx, dy, lam, amp, tur in DALGALAR:
    L_ = math.hypot(dx, dy); dx, dy = dx / L_, dy / L_
    k = TAU / lam
    ph = mn("ADD", mn("MULTIPLY", spn.outputs["X"], vb=k * dx), mn("MULTIPLY", spn.outputs["Y"], vb=k * dy))
    ph = mn("SUBTRACT", ph, mn("MULTIPLY", st.outputs["Frame"], vb=TAU * tur / F))
    z = mn("MULTIPLY", mn("SINE", ph), vb=amp * 1.7)
    top = z if top is None else mn("ADD", top, z)
zf = mn("DIVIDE", top, mn("ADD", mn("DIVIDE", spn.outputs["Y"], vb=90.0), vb=1.0))
cmb = N.new("ShaderNodeCombineXYZ"); gn.links.new(zf, cmb.inputs["Z"])
setp = N.new("GeometryNodeSetPosition")
gn.links.new(gi.outputs[0], setp.inputs["Geometry"]); gn.links.new(cmb.outputs[0], setp.inputs["Offset"])
gn.links.new(setp.outputs[0], go.inputs[0])
deniz.modifiers.new("Dalga", "NODES").node_group = gn
DALGA_F = F


def dalga_z(x, y, kare):
    """Height of the rendered sea at world (x, y) on a frame; the same sum the Dalga node tree builds."""
    z_ = 0.0
    for dx, dy, lam, amp, tur in DALGALAR:
        L_ = math.hypot(dx, dy)
        z_ += amp * 1.7 * math.sin(TAU / lam * (x * dx + y * dy) / L_ - kare * TAU * tur / DALGA_F)
    return z_ / (y / 90.0 + 1.0)


# ---------------------------------------------------------------- land kit
def tepe(ad, cx, cy, rx, ry, H, tohum, adim=2.0, kenar=0.22, ac=0.0, basamak=0.0):
    """Island/hill heightfield with steep shore cliffs; returns height function."""
    ca, sa = math.cos(ac), math.sin(ac)
    ofs = Vector((tohum * 13.1, tohum * 7.7, tohum * 3.3))

    def r_(x, y):
        lx, ly = (x - cx) * ca + (y - cy) * sa, -(x - cx) * sa + (y - cy) * ca
        q = math.hypot(lx / rx, ly / ry)
        ang = math.atan2(ly / ry, lx / rx)
        q *= 1.0 + 0.16 * noise.noise(Vector((math.cos(ang) * 2.2, math.sin(ang) * 2.2, 0)) + ofs)
        return q, lx, ly

    def h(x, y):
        q, lx, ly = r_(x, y)
        if q >= 1.0:
            return -3.0
        e = min(1.0, (1.0 - q) / kenar)
        sirt = e ** 0.45
        kubbe = max(0.0, 1.0 - q * q) ** 0.8
        n1 = noise.noise(Vector((x / 38.0, y / 38.0, 0)) + ofs)
        n2 = noise.noise(Vector((x / 11.0, y / 11.0, 1.7)) + ofs)
        z = H * sirt * (0.25 + 0.75 * kubbe) * (1 + 0.22 * n1) + H * 0.05 * n2 * sirt - (1 - sirt) * 2.5
        if basamak and z > 0:
            # stacked sediment ledges: flat treads, steep risers, broken by noise
            s_ = basamak * (1 + 0.25 * noise.noise(Vector((x / 23.0, y / 23.0, 4.1)) + ofs))
            k_ = math.floor(z / s_); f_ = z / s_ - k_
            zt = (k_ + ss(0.5, 0.92, f_)) * s_
            z = zt * 0.88 + z * 0.12
        return z

    nx = int(2.3 * max(rx, ry) / adim) + 2
    xs = [cx - 1.15 * max(rx, ry) + i * adim for i in range(nx)]
    ys = [cy - 1.15 * max(rx, ry) + j * adim for j in range(nx)]
    vs_, fs_ = [], []
    for y_ in ys:
        for x_ in xs:
            vs_.append((x_, y_, h(x_, y_)))
    for j in range(nx - 1):
        for i in range(nx - 1):
            a = j * nx + i
            if max(vs_[a][2], vs_[a + 1][2], vs_[a + nx][2], vs_[a + nx + 1][2]) < -2.9:
                continue
            fs_.append((a, a + 1, a + nx + 1, a + nx))
    mesh_nesne(ad, vs_, fs_, M["kaya"])
    return h


def kutu(ad, boyut, konum, mat, ac=0.0, pah=0.12):
    bpy.ops.mesh.primitive_cube_add(size=1, location=konum, rotation=(0, 0, ac))
    ob = bpy.context.active_object; ob.name = ad
    ob.scale = boyut
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if pah:
        bv = ob.modifiers.new("Pah", "BEVEL"); bv.width = pah; bv.segments = 3
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    ob.data.shade_smooth() if hasattr(ob.data, "shade_smooth") else None
    if hasattr(ob.data, "set_sharp_from_angle"):
        ob.data.set_sharp_from_angle(angle=math.radians(40))
    return ob


def elden(ob, genlik, frek=0.4, kes=5, egim=0.0):
    """Hand-made, not machined: split the faces, then push the surface with low-frequency noise
    (bulging walls, uneven edges) and lean it a little. genlik in metres."""
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=kes, use_grid_fill=True)
    o = Vector((ob.location.x * 0.37 + 11.3, ob.location.y * 0.53 - 4.1, ob.location.z * 0.11))
    for v in bm.verts:
        v.co += noise.noise_vector(v.co * frek + o) * genlik
        v.co.x += v.co.z * egim
    bm.to_mesh(me); bm.free()
    return ob


def silindir(ad, r1, r2, h, konum, mat, seg=24):
    bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r1, radius2=r2, depth=h,
                                    location=(konum[0], konum[1], konum[2] + h / 2))
    ob = bpy.context.active_object; ob.name = ad
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    if hasattr(ob.data, "set_sharp_from_angle"):
        ob.data.set_sharp_from_angle(angle=math.radians(50))
    return ob


def ev(x, y, z, w_, d_, h_, ac, cati):
    g = kutu("Ev", (w_, d_, h_), (x, y, z + h_ / 2), random.choice([M["badana"], M["badana"], M["badana2"]]), ac, 0.18)
    elden(g, 0.07, 0.42, 6, random.uniform(-0.012, 0.012))
    if cati == "kiremit":
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.0, radius2=0.0, depth=1.0,
                                        location=(x, y, z + h_ + 0.55), rotation=(0, 0, ac + math.pi / 4))
        r_ = bpy.context.active_object
        r_.scale = (w_ * 0.78, d_ * 0.78, 1.15)
        elden(r_, 0.06, 1.3, 4)
        r_.data.materials.append(M["kiremit"])
    else:
        elden(kutu("Parapet", (w_ + 0.15, d_ + 0.15, 0.35), (x, y, z + h_ + 0.12), M["badana"], ac, 0.08),
              0.05, 0.6, 5)
    # door and windows on the face towards the camera
    yon = Vector((math.sin(ac), -math.cos(ac), 0))
    yan = Vector((math.cos(ac), math.sin(ac), 0))
    on = Vector((x, y, z)) + yon * (d_ / 2 + 0.02)
    elden(kutu("Kapi", (0.9, 0.26, 1.9), (on + yan * (-w_ * 0.22) + Vector((0, 0, 0.95)))[:], M["kapi"], ac, 0.03),
          0.02, 1.5, 2)
    for k in range(1 if h_ < 4 else 2):
        elden(kutu("Pencere", (0.7, 0.26, 0.8), (on + yan * (w_ * 0.2) + Vector((0, 0, 1.6 + k * 1.7)))[:],
                   M["pencere"], ac, 0.03), 0.02, 1.5, 2)
    return g


def servi(x, y, z, h):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=10, radius=1.0, location=(x, y, z + h * 0.5))
    ob = bpy.context.active_object
    for v_ in ob.data.vertices:
        v_.co.x *= 1.0 + 0.12 * noise.noise(v_.co * 3 + Vector((x, y, 0)))
        if v_.co.z > 0:
            v_.co.x *= 1 - v_.co.z * 0.55; v_.co.y *= 1 - v_.co.z * 0.55
    ob.scale = (h * 0.13, h * 0.13, h * 0.5)
    ob.data.materials.append(M["servi"])
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def yaprak_kumesi(x, y, z, r, yass=0.55, adet=5, mat=None, tohum=0):
    """Canopy as overlapping soft blobs with broken, leafy edges."""
    rnd = random.Random(tohum)
    for k in range(adet):
        a = rnd.uniform(0, TAU); d = rnd.uniform(0.0, 0.65) * r if k else 0.0
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0,
                                              location=(x + math.cos(a) * d, y + math.sin(a) * d,
                                                        z + rnd.uniform(-0.15, 0.25) * r * yass))
        ob = bpy.context.active_object
        s_ = r * (0.62 if k else 0.8) * rnd.uniform(0.8, 1.1)
        ob.scale = (s_, s_, s_ * yass)
        o_ = Vector((x, y, k * 3.1 + tohum))
        for v_ in ob.data.vertices:
            n = v_.co
            v_.co = n * (1 + 0.16 * noise.noise(n * 1.6 + o_) + 0.10 * noise.noise(n * 5.5 + o_))
            if v_.co.z < -0.35:
                v_.co.z = -0.35 + (v_.co.z + 0.35) * 0.4
        ob.data.materials.append(mat or M["agac"])
        for p in ob.data.polygons:
            p.use_smooth = True


def egri_dal(nok, r0, r1, mat):
    cu = bpy.data.curves.new("Dal", "CURVE"); cu.dimensions = "3D"
    cu.bevel_depth = 1.0; cu.bevel_resolution = 2
    sp_ = cu.splines.new("BEZIER"); sp_.bezier_points.add(len(nok) - 1)
    for k, p in enumerate(nok):
        bp = sp_.bezier_points[k]
        bp.co = p; bp.handle_left_type = bp.handle_right_type = "AUTO"
        bp.radius = r0 + (r1 - r0) * k / (len(nok) - 1)
    ob = bpy.data.objects.new("Dal", cu); bagla(ob)
    cu.materials.append(mat)
    return ob


def cam_agaci(x, y, z, h):
    """Umbrella pine: a leaning, slightly twisted trunk splitting into flat canopy clusters."""
    rnd = random.Random(int(x * 7 + y * 13))
    egim = rnd.uniform(0, TAU); e = rnd.uniform(0.08, 0.2) * h
    tepe_ = Vector((x + math.cos(egim) * e, y + math.sin(egim) * e, z + h * 0.72))
    orta = Vector((x - math.cos(egim) * e * 0.3, y - math.sin(egim) * e * 0.3, z + h * 0.38))
    egri_dal([Vector((x, y, z - 0.4)), orta, tepe_], 0.32 * h / 8, 0.16 * h / 8, M["govde_agac"])
    dallar = rnd.randint(2, 3)
    for k in range(dallar):
        a = egim + k * TAU / dallar + rnd.uniform(-0.5, 0.5)
        L_ = h * rnd.uniform(0.22, 0.34)
        uc = tepe_ + Vector((math.cos(a) * L_, math.sin(a) * L_, h * rnd.uniform(0.12, 0.22)))
        egri_dal([tepe_, tepe_.lerp(uc, 0.5) + Vector((0, 0, h * 0.06)), uc], 0.14 * h / 8, 0.06 * h / 8,
                 M["govde_agac"])
        yaprak_kumesi(uc.x, uc.y, uc.z + h * 0.05, h * rnd.uniform(0.2, 0.27), 0.5, 5, None,
                      int(x * 3 + y + k))


def cali(x, y, z, r):
    yaprak_kumesi(x, y, z + r * 0.3, r, 0.7, 3, None, int(x * 5 + y * 3))


def fener(x, y, z, h=10.0):
    elden(silindir("FenerKule", 1.7, 1.15, h, (x, y, z), M["badana"], 28), 0.07, 0.35, 8, 0.006)
    silindir("FenerBant", 1.36, 1.3, h * 0.12, (x, y, z + h * 0.58), M["fener_bant"], 28)
    silindir("FenerBalkon", 1.75, 1.75, 0.25, (x, y, z + h), M["fener_bant"], 28)
    silindir("FenerCam", 0.95, 0.95, 1.5, (x, y, z + h + 0.25), M["fener_cam"], 16)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1.1, location=(x, y, z + h + 1.75))
    k = bpy.context.active_object; k.scale = (1, 1, 0.7); k.data.materials.append(M["fener_bant"])
    for p in k.data.polygons:
        p.use_smooth = True


def rihtim(x0, y0, x1, y1, gen=4.0, ust=1.1):
    d = Vector((x1 - x0, y1 - y0, 0)); L_ = d.length
    ac = math.atan2(d.y, d.x) - math.pi / 2
    kutu("Rihtim", (gen, L_, ust + 2.0), ((x0 + x1) / 2, (y0 + y1) / 2, ust - (ust + 2.0) / 2), M["tas"], ac, 0.25)
    n_ = int(L_ / 7)
    yan = Vector((math.cos(ac), math.sin(ac), 0))
    for k in range(n_):
        p = Vector((x0, y0, 0)) + d * ((k + 0.5) / n_) + yan * (-gen / 2 + 0.6)
        silindir("Baba", 0.25, 0.2, 0.55, (p.x, p.y, ust), M["fener_bant"], 12)


def kasaba(h, cx, cy, rx, ry, adet, tohum, ac_yon=0.0, tam=0.82):
    random.seed(tohum)
    konan = []
    deneme = 0
    while len(konan) < adet and deneme < adet * 40:
        deneme += 1
        x = cx + random.uniform(-rx, rx); y = cy + random.uniform(-ry, ry)
        if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 > 1:
            continue
        z = h(x, y)
        if z < 1.5:
            continue
        w_, d_ = random.uniform(4.5, 7.5), random.uniform(4.0, 6.5)
        if any((x - a) ** 2 + (y - b) ** 2 < ((w_ + c_) * 0.62) ** 2 for a, b, c_ in konan):
            continue
        zs = min(h(x + dx, y + dy) for dx in (-w_ / 2, w_ / 2) for dy in (-d_ / 2, d_ / 2))
        ev(x, y, zs - 0.4, w_, d_, random.uniform(3.2, 5.6), ac_yon + random.uniform(-0.25, 0.25),
           "kiremit" if random.random() < 0.45 else "duz")
        konan.append((x, y, w_))
    return konan


def bitki(h, cx, cy, rx, ry, adet, tohum, servi_orani=0.25, kacin=(), adet_cali=0):
    random.seed(tohum)
    for _ in range(adet * 6):
        if adet <= 0:
            break
        x = cx + random.uniform(-rx, rx); y = cy + random.uniform(-ry, ry)
        z = h(x, y)
        if z < 2.0 or any((x - a) ** 2 + (y - b) ** 2 < (c_ * 0.9) ** 2 for a, b, c_ in kacin):
            continue
        if random.random() < servi_orani:
            servi(x, y, z - 0.3, random.uniform(7, 12))
        else:
            cam_agaci(x, y, z - 0.3, random.uniform(7, 11))
        adet -= 1
    for _ in range(adet_cali * 6):
        if adet_cali <= 0:
            break
        x = cx + random.uniform(-rx, rx); y = cy + random.uniform(-ry, ry)
        z = h(x, y)
        if z < 1.5 or any((x - a) ** 2 + (y - b) ** 2 < (c_ * 0.8) ** 2 for a, b, c_ in kacin):
            continue
        cali(x, y, z - 0.2, random.uniform(0.9, 2.0))
        adet_cali -= 1


# ---------------------------------------------------------------- the boat (tirhandil, lateen rig)
def tekne(yelken=1.0):
    kok = bpy.data.objects.new("Tekne", None); bagla(kok)
    L_, B = 7.0, 1.15
    NS, NK = 24, 12
    bm = bmesh.new()
    vl = bm.verts.layers.float.new("v")
    kes = []
    serenler = []
    for i in range(NS + 1):
        t = i / NS
        yy = (t - 0.5) * L_
        b = B * max(0.03, math.sin(math.pi * t) ** 0.55) * (1.0 + 0.06 * (0.5 - t))
        zs = 0.78 + 0.32 * (2 * t - 1) ** 2 + 0.22 * max(0.0, 2 * t - 1) ** 3
        zk = -0.55 * math.sin(math.pi * t) ** 0.5
        s_ = []
        for k in range(NK + 1):
            a = -math.pi / 2 + math.pi * k / NK
            x = b * math.sin(a)
            z = zk + (zs - zk) * (1 - math.cos(a)) ** 0.85 / (1.0 ** 0.85)
            vv = bm.verts.new((x, yy, z))
            vv[vl] = (z - zk) / max(1e-3, zs - zk) * 0.98 + 0.01
            s_.append(vv)
        kes.append(s_)
        serenler.append((b, yy, zs))
    for i in range(NS):
        for k in range(NK):
            bm.faces.new((kes[i][k], kes[i + 1][k], kes[i + 1][k + 1], kes[i][k + 1]))
    me = bpy.data.meshes.new("Govde"); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    g = bpy.data.objects.new("Govde", me); bagla(g); g.parent = kok
    me.materials.append(M["govde"])
    sub = g.modifiers.new("Yumusak", "SUBSURF"); sub.levels = 1; sub.render_levels = 2
    # deck slightly below the sheer
    dv, df = [], []
    for i, (b, yy, zs) in enumerate(serenler):
        dv += [(-b * 0.93, yy, zs - 0.12), (b * 0.93, yy, zs - 0.12)]
    for i in range(NS):
        df.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    gv = mesh_nesne("Guverte", dv, df, M["guverte"]); gv.parent = kok
    # rails along the sheer (smooth NURBS)
    for yan in (-1, 1):
        cu = bpy.data.curves.new("Kupeste", "CURVE"); cu.dimensions = "3D"
        cu.bevel_depth = 0.07; cu.bevel_resolution = 4; cu.resolution_u = 8
        sp_ = cu.splines.new("NURBS"); sp_.points.add(len(serenler) - 1)
        sp_.order_u = 4; sp_.use_endpoint_u = True
        for k, (b, yy, zs) in enumerate(serenler):
            sp_.points[k].co = (yan * b * 1.01, yy, zs + 0.03, 1)
        ob = bpy.data.objects.new("Kupeste", cu); bagla(ob); ob.parent = kok
        cu.materials.append(M["ahsap"])
    # cabin-less fishing boat: a small wheel box, crates, a tiller, a lantern post
    for ad, boyut, kon, mat in (("Sandik", (0.8, 0.6, 0.45), (0.25, -1.6, 0.9), M["ahsap"]),
                                ("Sandik2", (0.55, 0.48, 0.35), (0.56, -0.92, 0.85), M["guverte"])):
        o = elden(kutu(ad, boyut, kon, mat, 0.1, 0.04), 0.014, 2.2, 3); o.parent = kok
    kangal(Vector((0.62, -0.5, 0.70)), 0.27, 5, 0.032, kok)
    yeke = kutu("Yeke", (0.08, 1.1, 0.08), (0, -3.5, 1.35), M["ahsap"], 0, 0.02); yeke.rotation_euler.x = 0.25
    yeke.parent = kok
    # mast (raked forward) and lateen yard
    direk_alt, direk_ust = Vector((0, 1.0, 0.7)), Vector((0, 1.3, 5.3))
    cubuk("Direk", direk_alt, direk_ust, 0.1, M["ahsap"], kok, uc_oran=0.72, elle=0.006)
    beta = math.radians(34 if yelken > 0.6 else 30)

    def dondur(p):
        q = p - Vector((0, 1.15, 0))
        return Vector((q.x * math.cos(beta) + q.y * math.sin(beta) * 1.0 * 0 + math.sin(beta) * -q.y * -1 * 0,
                       q.y, q.z)) if False else Vector((math.sin(beta) * -(q.y), math.cos(beta) * q.y, q.z)) + Vector((0, 1.15, 0))

    if yelken > 0.05:
        tack, peak = Vector((0, 3.3, 1.3)), Vector((0, -2.5, 6.7))
        clew = Vector((0, -2.4, 1.55)).lerp(Vector((0, 0.2, 4.0)), 1.0 - yelken)
    else:
        tack, peak = Vector((0, 3.1, 1.5)), Vector((0, -2.6, 4.6))
        clew = None
    T_, P_ = dondur(tack), dondur(peak)
    cubuk("Seren", T_ + (T_ - P_) * 0.05, P_ + (P_ - T_) * 0.04, 0.075, M["ahsap"], kok, uc_oran=0.55, elle=0.005)
    if clew is not None:
        C_ = dondur(clew)
        nrm_ = (P_ - T_).cross(C_ - T_).normalized()
        if nrm_.x < 0:
            nrm_ = -nrm_
        bm = bmesh.new()
        n_ = 14
        idx = {}
        for i in range(n_ + 1):
            for j in range(n_ + 1 - i):
                u_, v_ = i / n_, j / n_
                w3 = 1 - u_ - v_
                p = T_ + (P_ - T_) * u_ + (C_ - T_) * v_
                kar = 27 * u_ * v_ * w3 * 0.55 * yelken + 0.25 * v_ * w3 * 4 * 0.5 * yelken
                idx[(i, j)] = bm.verts.new(p + nrm_ * kar)
        for i in range(n_):
            for j in range(n_ - i):
                bm.faces.new((idx[(i, j)], idx[(i, j + 1)], idx[(i + 1, j)]))
                if (i + 1, j + 1) in idx:
                    bm.faces.new((idx[(i, j + 1)], idx[(i + 1, j + 1)], idx[(i + 1, j)]))
        me = bpy.data.meshes.new("Yelken"); bm.to_mesh(me); bm.free()
        for p in me.polygons:
            p.use_smooth = True
        ob = bpy.data.objects.new("Yelken", me); bagla(ob); ob.parent = kok
        me.materials.append(M["yelken"])
        sl = ob.modifiers.new("Kalinlik", "SOLIDIFY"); sl.thickness = 0.02
        # sheet line from clew to the stern
        cubuk("Iskota", C_, Vector((0.3, -3.2, 1.2)), 0.015, M["halat"], kok)
    else:
        sarili_yelken(T_.lerp(P_, 0.06), P_.lerp(T_, 0.08), kok)
    # lantern post at the stern
    cubuk("FenerDirek", Vector((-0.4, -3.0, 1.0)), Vector((-0.4, -3.0, 2.3)), 0.04, M["ahsap"], kok)
    f_ = kutu("Fener", (0.13, 0.13, 0.17), (-0.4, -3.0, 2.38), M["fener_cam"], 0, 0.02); f_.parent = kok
    f2 = kutu("FenerSapka", (0.17, 0.17, 0.04), (-0.4, -3.0, 2.49), M["fener_bant"], 0, 0.015); f2.parent = kok
    kok.location = (TX, TY, 0.0)
    kok.rotation_euler = (0, 0, math.radians(TPSI))
    return kok


def kangal(merkez, r, tur, kalin, ebeveyn, dik=False):
    """A coil of rope: a few loose, uneven loops stacked and slumped, not a torus.
    dik hangs it from a hand (loops in a vertical plane)."""
    cu = bpy.data.curves.new("Kangal", "CURVE"); cu.dimensions = "3D"
    cu.bevel_depth = kalin; cu.bevel_resolution = 3
    sp_ = cu.splines.new("POLY")
    n = tur * 28
    sp_.points.add(n)
    for i in range(n + 1):
        u = i / 28.0
        a = u * TAU
        rr = r * (1.0 - 0.05 * u) * (1 + 0.07 * noise.noise(Vector((math.cos(a), math.sin(a), u * 0.7))))
        h = kalin * 1.7 * u * 0.55 + kalin * 0.8 * noise.noise(Vector((u * 2.1, 3.3, 0.5)))
        p = Vector((math.cos(a) * rr, math.sin(a) * rr * 0.92, h))
        if dik:
            p = Vector((p.x, p.z, -p.y * 1.25))
        sp_.points[i].co = (*(merkez + p), 1)
    ob = bpy.data.objects.new("Kangal", cu); bagla(ob); ob.parent = ebeveyn
    cu.materials.append(M["halat"])
    return ob


def sarili_yelken(a, b, ebeveyn):
    """Furled lateen sail: smooth Catmull-Clark subdivided canvas bunched under the yard,
    pinched by NURBS gaskets, sagging naturally between them."""
    u = (b - a); L = u.length; u.normalize()
    asagi = Vector((0, 0, -1)); asagi = (asagi - u * asagi.dot(u)).normalized()
    yan = u.cross(asagi)
    NS, NA, ties = 72, 20, 6
    bm = bmesh.new(); hal = []
    for i in range(NS + 1):
        t = i / NS
        kis = 0.48 + 0.52 * abs(math.sin(math.pi * t * ties)) ** 0.85      # smoothly pinched at the gaskets
        boy = (0.10 + 0.13 * math.sin(math.pi * t) ** 0.65) * kis          # fuller mid-yard
        sark = boy * (0.88 + 0.45 * abs(math.sin(math.pi * t * ties)))
        c = a + u * (L * t) + asagi * sark
        ring = []
        for k in range(NA):
            ang = TAU * k / NA
            ca, sa = math.cos(ang), math.sin(ang)
            damla = 1.0 + 0.42 * max(0.0, ca)                              # hangs heavier below
            n_ = noise.noise(Vector((t * 7.5, ca * 1.2, sa * 1.2))) * 0.20 + \
                noise.noise(Vector((t * 22.0, ca * 2.2, sa * 2.2 + 4))) * 0.055
            rr = boy * damla * (1 + n_)
            ring.append(bm.verts.new(c + asagi * (ca * rr) + yan * (sa * rr * 0.82)))
        hal.append(ring)
    for i in range(NS):
        for k in range(NA):
            bm.faces.new((hal[i][k], hal[i][(k + 1) % NA], hal[i + 1][(k + 1) % NA], hal[i + 1][k]))
    me = bpy.data.meshes.new("Sarili"); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("Sarili", me); bagla(ob); ob.parent = ebeveyn
    sub = ob.modifiers.new("Yumusak", "SUBSURF")
    sub.levels = 2; sub.render_levels = 2
    me.materials.append(M["yelken"])
    for k in range(1, ties):                                               # smooth NURBS gaskets
        t = k / ties
        c = a + u * (L * t)
        cu = bpy.data.curves.new("Kalcete", "CURVE"); cu.dimensions = "3D"
        cu.bevel_depth = 0.013; cu.bevel_resolution = 4; cu.resolution_u = 8
        sp_ = cu.splines.new("NURBS"); sp_.points.add(15); sp_.use_cyclic_u = True; sp_.order_u = 4
        boy = 0.10 + 0.13 * math.sin(math.pi * t) ** 0.65
        for j in range(16):
            ang = TAU * j / 16
            q = c + asagi * (boy * 0.45 + math.cos(ang) * boy * 0.62) + yan * (math.sin(ang) * boy * 0.55) + \
                u * (0.018 * math.sin(ang * 2))
            sp_.points[j].co = (*q, 1)
        g = bpy.data.objects.new("Kalcete", cu); bagla(g); g.parent = ebeveyn
        cu.materials.append(M["halat"])


def balik_yap(konum, boy, ebeveyn):
    """The catch hanging from the line, head up: a real fish profile (deep body, pointed snout,
    dark back, silver belly, forked tail, dorsal fin, eye). Local z = length, x = back(+)/belly(-),
    y = thickness. boy is the length in metres."""
    NZ, NA = 22, 16
    bm = bmesh.new(); hal = []; prof = []
    for i in range(NZ + 1):
        u = i / NZ                                           # 0 tail root .. 1 snout
        h = 0.13 * math.sin(math.pi * (0.10 + 0.86 * u)) ** 0.75 * (0.35 + 0.65 * min(1.0, u * 2.4)) + 0.008
        t = h * 0.34
        c = 0.012 * math.sin(math.pi * u)                    # back slightly fuller than belly
        z = u - 0.5
        ring = [bm.verts.new((c + h * math.cos(TAU * k / NA), t * math.sin(TAU * k / NA), z)) for k in range(NA)]
        hal.append(ring); prof.append((h, c, z))
    burun = bm.verts.new((0.01, 0, 0.53))
    yuz = []
    for i in range(NZ):
        for k in range(NA):
            yuz.append(bm.faces.new((hal[i][k], hal[i][(k + 1) % NA], hal[i + 1][(k + 1) % NA], hal[i + 1][k])))
    for k in range(NA):
        yuz.append(bm.faces.new((hal[NZ][k], hal[NZ][(k + 1) % NA], burun)))
    for f in yuz:                                            # dark back, silver belly
        f.material_index = 1 if f.calc_center_median().x > 0.02 else 0
    kok = bm.verts.new((0, 0, -0.5)); a_ = bm.verts.new((0.19, 0, -0.74)); b_ = bm.verts.new((0, 0, -0.62))
    c_ = bm.verts.new((-0.19, 0, -0.74)); r1 = bm.verts.new((0.04, 0, -0.47)); r2 = bm.verts.new((-0.04, 0, -0.47))
    for f in (bm.faces.new((r1, kok, a_)), bm.faces.new((kok, b_, a_)), bm.faces.new((kok, c_, b_)),
              bm.faces.new((r2, c_, kok))):
        f.material_index = 1
    h5, c5, z5 = prof[int(NZ * 0.55)]; h7, c7, z7 = prof[int(NZ * 0.78)]
    d1 = bm.verts.new((c5 + h5 * 0.9, 0, z5)); d2 = bm.verts.new((c7 + h7 * 0.9, 0, z7))
    d3 = bm.verts.new((c5 + h5 + 0.075, 0, z5 + 0.02))
    bm.faces.new((d1, d2, d3)).material_index = 1
    me = bpy.data.meshes.new("Balik"); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(M["balik"]); me.materials.append(M["balik_sirt"])
    ob = bpy.data.objects.new("Balik", me); bagla(ob)
    ob.location = konum; ob.scale = (boy, boy, boy); ob.parent = ebeveyn
    for yan in (1, -1):                                      # eyes
        hg, cg, zg = prof[int(NZ * 0.9)]
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.018,
                                             location=(cg + hg * 0.25, yan * hg * 0.30, zg))
        g = bpy.context.active_object; g.data.materials.append(M["balik_goz"]); g.parent = ob
    return ob


def cubuk(ad, p1, p2, r, mat, ebeveyn, uc_oran=1.0, elle=0.0):
    d = p2 - p1
    if uc_oran != 1.0:
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=r, radius2=r * uc_oran, depth=d.length,
                                        location=((p1 + p2) / 2)[:])
    else:
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=r, depth=d.length, location=((p1 + p2) / 2)[:])
    ob = bpy.context.active_object; ob.name = ad
    if elle:
        elden(ob, elle, 1.6, 8)
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    ob.parent = ebeveyn
    return ob



# ---------------------------------------------------------------- small props (the crew lives in murettebat.py)
def kure(c_, r_, mat, ebeveyn, olcek=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=r_, location=Vector(c_)[:])
    s_ = bpy.context.active_object; s_.scale = olcek
    s_.data.materials.append(mat)
    for p in s_.data.polygons:
        p.use_smooth = True
    s_.parent = ebeveyn
    return s_


def bayrak(x, y, z, direk=6.0, L=1.8, H=1.2, ac=0.6):
    silindir("Gonder", 0.06, 0.04, direk, (x, y, z), M["badana"], 10)
    kure((x, y, z + direk + 0.05), 0.09, M["fener_bant"], None)
    nx, nz = 24, 16
    vs_, uvs, fs_ = [], [], []
    for i in range(nx + 1):
        for j in range(nz + 1):
            u, v = i / nx, j / nz
            dal = (0.16 * math.sin(u * 7.5 - 0.6) + 0.05 * math.sin(u * 15 + v * 4)) * u ** 1.2
            vs_.append((dal, u * L, -H + v * H - 0.06 * u * u)); uvs.append((u, v))
    for i in range(nx):
        for j in range(nz):
            a = i * (nz + 1) + j
            fs_.append((a, a + nz + 1, a + nz + 2, a + 1))
    ob = mesh_nesne("Bayrak", vs_, fs_, M["bayrak"])
    uvl = ob.data.uv_layers.new(name="UVMap")
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            uvl.data[li].uv = uvs[ob.data.loops[li].vertex_index]
    ob.location = (x, y, z + direk - 0.05)
    ob.rotation_euler = (0, 0, ac)

# ---------------------------------------------------------------- stages
def uzak_adalar():
    tepe("UzakAda1", -260, 1300, 240, 80, 60, 21, adim=10, basamak=12)
    tepe("UzakAda2", 330, 1900, 380, 110, 105, 22, adim=14, basamak=16)
    tepe("UzakAda3", -60, 2400, 280, 80, 70, 23, adim=16, basamak=14)


if KOMUT == "sprite":
    pass
elif SAHNE == "kalkis":
    # home harbour: quay along the boat's port side, town on the hill behind it, light at the mole
    rihtim(-4.6, -4.0, -4.6, 70.0, gen=6.0)
    rihtim(-4.6, 68.0, -26.0, 92.0, gen=6.0)
    h = tepe("Liman", -62, 120, 58, 70, 30, 3, adim=1.0, kenar=0.12, ac=0.2, basamak=5.0)
    konan = kasaba(h, -40, 105, 34, 40, 24, 5, ac_yon=math.radians(-20))
    bitki(h, -45, 125, 45, 55, 16, 6, 0.3, konan, 26)
    hb = tepe("Mendirek", 16, 128, 11, 8, 4.5, 9, adim=0.5, kenar=0.3, basamak=1.6)
    fener(16, 128, hb(16, 128) - 0.2, 10)
    bayrak(-6.4, 64.0, 1.1, 6.0, ac=0.9)
    for k in range(4):
        cali(-6.5 + random.uniform(-1, 1), 8 + k * 14, 1.1, random.uniform(0.6, 1.0))
    uzak_adalar()
elif SAHNE == "seyir":
    h = tepe("Ada", -78, 250, 62, 46, 28, 4, adim=1.2, kenar=0.15, basamak=5.5)
    konan = kasaba(h, -60, 236, 22, 16, 3, 8, ac_yon=math.radians(10))
    bitki(h, -70, 250, 52, 40, 18, 9, 0.3, konan, 24)
    tepe("Kaya", 24, 120, 6, 4.5, 4.0, 12, adim=0.5, kenar=0.35, basamak=1.5)
    uzak_adalar()
else:
    # destination: a town filling the horizon, a light on a rock at the harbour mouth
    h = tepe("Varis", -24, 250, 82, 58, 38, 7, adim=1.2, kenar=0.12, ac=-0.1, basamak=6.0)
    konan = kasaba(h, -24, 228, 60, 34, 34, 10, ac_yon=math.radians(0))
    bitki(h, -24, 250, 75, 52, 20, 11, 0.35, konan, 30)
    rihtim(-46, 190, 14, 190, gen=6.0)
    bayrak(10.0, 188.5, 1.1, 7.0, L=2.2, H=1.47, ac=0.9)
    hb = tepe("FenerKaya", 30, 176, 8, 6, 4.0, 13, adim=0.5, kenar=0.3, basamak=1.5)
    fener(30, 176, hb(30, 176) - 0.2, 10)
    uzak_adalar()

TK = tekne(YELKEN)
POZ = "dumen" if (len(ARGS) > 5 and ARGS[5] == "mola") else (ARGS[5] if len(ARGS) > 5 else "dumen")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import murettebat  # noqa: E402  (two brothers, MakeHuman)
murettebat.isik(GUNES, V["gunes_guc"])
EKIP = murettebat.murettebat(TK, POZ, SAHNE)
_olta_statik = {}
for tur, *a_ in EKIP["cizim"]:
    if tur == "cubuk":
        ad, p1, p2, r_, mk = a_
        if ad in ("Olta", "Misina") and POZ in ("olta", "olta_vurus", "tuttu"):
            _olta_statik[ad] = (Vector(p1), Vector(p2))
        else:
            cubuk(ad, Vector(p1), Vector(p2), r_, M[mk], TK)
    elif tur == "balik":
        _olta_statik["balik"] = Vector(a_[0])
    elif tur == "kangal":
        kangal(Vector(a_[0]), 0.14, 4, 0.022, TK, dik=True)
    elif tur == "yeke":      # the tiller swings to where the helmsman's hand is
        yk = bpy.data.objects.get("Yeke")
        if yk is not None:
            pv = Vector((0.0, -4.03, 1.214))
            d_ = Vector(a_[0]) - pv
            L_ = d_.length + 0.06
            yk.location = pv + d_.normalized() * (L_ / 2)
            yk.rotation_euler = d_.to_track_quat("Y", "Z").to_euler()
            yk.scale = (1.0, L_ / 1.1, 1.0)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -2.55, 1.06))
otur = bpy.context.active_object
otur.scale = (1.9, 0.32, 0.08)
otur.data.materials.append(M["ahsap"])
otur.parent = TK

# ---------------------------------------------------------------- fishing sequence props (poz "balik")
YEKE_PIVOT = Vector((0.0, -4.03, 1.214))


def yeke_koy(el):
    yk = bpy.data.objects.get("Yeke")
    d_ = el - YEKE_PIVOT
    L_ = d_.length + 0.06
    yk.location = YEKE_PIVOT + d_.normalized() * (L_ / 2)
    yk.rotation_euler = d_.to_track_quat("Y", "Z").to_euler()
    yk.scale = (1.0, L_ / 1.1, 1.0)
    return yk


def _su_damla_malzeme():
    """Glossy translucent sea-spray material (backlit Aegean water glints instead of opaque white balls)."""
    if "su_damla" in M:
        return M["su_damla"]
    A = Agac("SuDamla")
    s, p = A.yuzey(lin("#EAF7FA"), rough=0.06, spec=0.85, boya=False)
    if "Coat Weight" in p.inputs:
        p.inputs["Coat Weight"].default_value = 1.0
        p.inputs["Coat Roughness"].default_value = 0.04
    if "Alpha" in p.inputs:
        p.inputs["Alpha"].default_value = 0.80
    if "Emission Color" in p.inputs:
        p.inputs["Emission Color"].default_value = lin("#DDF2F8")
        p.inputs["Emission Strength"].default_value = 0.28
    m = A.bitir(s, sis=False)
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"
    M["su_damla"] = m
    return m


def _misina_malzeme():
    """Fine sunlit wet-monofilament fishing line material."""
    if "misina" in M:
        return M["misina"]
    M["misina"] = duz_malzeme("MisinaMat", "#DCE4E7", rough=0.18, spec=0.85)
    return M["misina"]


def _bezier_fcurves(nesneler):
    """Set every animation F-curve keyframe on nesneler (and their data blocks) to BEZIER
    with AUTO_CLAMPED handles for silk-smooth 30 fps interpolation (Blender 4.x & 5.x safe)."""
    aksiyonlar = set()
    for o in nesneler:
        if o is None:
            continue
        ad = getattr(o, "animation_data", None)
        if ad and ad.action:
            aksiyonlar.add(ad.action)
        dt = getattr(o, "data", None)
        ad2 = getattr(dt, "animation_data", None) if dt else None
        if ad2 and ad2.action:
            aksiyonlar.add(ad2.action)
    for act in aksiyonlar:
        fcs = []
        if hasattr(act, "fcurves") and act.fcurves:
            fcs.extend(act.fcurves)
        if hasattr(act, "layers"):
            for lyr in act.layers:
                for stp in getattr(lyr, "strips", ()):
                    for cb in getattr(stp, "channelbags", ()):
                        fcs.extend(getattr(cb, "fcurves", ()))
        for fc in fcs:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = "AUTO_CLAMPED"
                kp.handle_right_type = "AUTO_CLAMPED"
            fc.update()


def serit(ad, n, r, mat, uc_oran=1.0, tip="NURBS"):
    """An animatable rod/line: smooth endpoint-clamped NURBS curve (or taut POLY for guide-threaded line)."""
    cu = bpy.data.curves.new(ad, "CURVE"); cu.dimensions = "3D"
    cu.bevel_depth = r; cu.bevel_resolution = 4; cu.resolution_u = 10; cu.use_fill_caps = True
    sp_ = cu.splines.new(tip); sp_.points.add(n - 1)
    if tip == "NURBS":
        sp_.order_u = min(4, n); sp_.use_endpoint_u = True
    for k in range(n):
        sp_.points[k].radius = 1.0 + (uc_oran - 1.0) * k / max(1, n - 1)
    ob = bpy.data.objects.new(ad, cu); bagla(ob); ob.parent = TK
    cu.materials.append(mat)
    return ob


def serit_anahtar(ob, noktalar, f):
    for k, q in enumerate(noktalar):
        pt = ob.data.splines[0].points[k]
        pt.co = (q.x, q.y, q.z, 1.0)
        pt.keyframe_insert("co", frame=f)


def kova(merkez):
    """A full Aegean wooden catch pail on the deck with aged iron hoops and sea water inside."""
    z0 = murettebat.guverte_z(merkez[1])
    M.setdefault("kova_cember", duz_malzeme("KovaCember", "#3A312A", 0.55, 0.35))
    bpy.ops.mesh.primitive_cone_add(vertices=36, radius1=0.175, radius2=0.215, depth=0.31,
                                    location=(merkez[0], merkez[1], z0 + 0.155), end_fill_type="NOTHING")
    k_ = bpy.context.active_object; k_.name = "Kova"
    k_.modifiers.new("Kalin", "SOLIDIFY").thickness = 0.017
    k_.data.materials.append(M["ahsap"]); k_.parent = TK
    for p in k_.data.polygons:
        p.use_smooth = True
    for zz in (0.065, 0.245):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.180 + zz * 0.115, minor_radius=0.008,
                                         major_segments=36, minor_segments=12,
                                         location=(merkez[0], merkez[1], z0 + zz))
        c_ = bpy.context.active_object; c_.data.materials.append(M["kova_cember"]); c_.parent = TK
        for p in c_.data.polygons:
            p.use_smooth = True
    bpy.ops.mesh.primitive_circle_add(vertices=36, radius=0.198, fill_type="NGON",
                                      location=(merkez[0], merkez[1], z0 + 0.21))
    s_ = bpy.context.active_object; s_.data.materials.append(M["deniz"]); s_.parent = TK
    return Vector((merkez[0], merkez[1], z0))


def kova_doldur(kv, baliklar_mod):
    """Layer 3 distinct previously caught Aegean species inside the wooden catch bucket so the
    pail visually fills up with a multi-species haul (Barbun, Mercan, Uskumru)."""
    dizilim = (
        ("barbun",  0.22, Vector((-0.065,  0.045, 0.22)), (math.radians(-58), math.radians(-18), math.radians(125))),
        ("mercan",  0.28, Vector(( 0.060,  0.055, 0.23)), (math.radians(-62), math.radians( 22), math.radians(-35))),
        ("uskumru", 0.27, Vector((-0.055, -0.065, 0.24)), (math.radians(-55), math.radians(-12), math.radians(210))),
    )
    for idx_k, (tur_k, boy_k, ofs, rot) in enumerate(dizilim):
        try:
            ob_k = baliklar_mod.yap(tur_k, boy_k, ebeveyn=TK, ad=f"KovaBalik_{idx_k}_{tur_k}")
            ob_k.location = kv + ofs
            ob_k.rotation_euler = rot
        except Exception:
            pass


def sicrama(ad, damla_say=8, kalin=0.008, ebeveyn=True):
    """A water-surface foam ripple ring paired with velocity-stretched glossy ballistic spray streaks.
    ebeveyn=False keeps it in world space, so a ring on the open sea stays put while the boat rolls."""
    damla_mat = _su_damla_malzeme()
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=kalin, major_segments=40, minor_segments=10, location=(0, 0, 0))
    h_ = bpy.context.active_object; h_.name = ad
    for p in h_.data.polygons:
        p.use_smooth = True
    h_.scale = (0, 0, 0); h_.data.materials.append(M["kopuk"]); h_.parent = TK if ebeveyn else None
    h_.visible_shadow = False
    h_.keyframe_insert("scale", frame=0)
    damlalar = []
    for k in range(damla_say):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.014, location=(0, 0, 0))
        d_ = bpy.context.active_object; d_.name = f"{ad}_Damla{k}"
        for p in d_.data.polygons:
            p.use_smooth = True
        d_.scale = (0, 0, 0); d_.data.materials.append(damla_mat); d_.parent = TK if ebeveyn else None
        d_.visible_shadow = False
        d_.keyframe_insert("scale", frame=0)
        damlalar.append(d_)
    h_["damlalar"] = [d_.name for d_ in damlalar]
    return h_


def sicrat(h_, yer, f, sure=20, boy=1.0, z0=0.012):
    """Animate a smooth ease-out expanding ripple ring and velocity-aligned ballistic water streaks."""
    fps = murettebat.FPS
    T_tot = max(0.18, sure / fps)
    def su_(k_):
        return dalga_z(yer.x, yer.y, k_) if h_.parent is None else 0.0
    h_.scale = (0, 0, 0); h_.keyframe_insert("scale", frame=f - 1)
    for df in range(-1, sure + 2):
        h_.location = (yer.x, yer.y, z0 + su_(f + df))
        h_.keyframe_insert("location", frame=f + df)
        if 0 <= df <= sure:
            u_ = df / max(1, sure)
            e_out = 1.0 - (1.0 - u_) ** 2.2
            sk_xy = (0.18 + 1.08 * e_out) * boy
            fade_z = max(0.0, math.sin(min(1.0, u_ * 5.0) * math.pi * 0.5) * ((1.0 - u_) ** 1.35))
            h_.scale = (sk_xy, sk_xy, max(0.001, 0.22 * boy * fade_z))
            h_.keyframe_insert("scale", frame=f + df)
        if h_.parent is None:      # lie on the swell's slope, else half the ring sinks into the rising side
            e_ = 0.05
            gx = (dalga_z(yer.x + e_, yer.y, f + df) - dalga_z(yer.x - e_, yer.y, f + df)) / (2 * e_)
            gy = (dalga_z(yer.x, yer.y + e_, f + df) - dalga_z(yer.x, yer.y - e_, f + df)) / (2 * e_)
            h_.rotation_euler = Vector((-gx, -gy, 1.0)).normalized().to_track_quat("Z", "Y").to_euler()
            h_.keyframe_insert("rotation_euler", frame=f + df)
    h_.scale = (0, 0, 0); h_.keyframe_insert("scale", frame=f + sure + 1)
    d_adlar = h_.get("damlalar", [])
    n_d = len(d_adlar)
    for idx_d, d_ad in enumerate(d_adlar):
        d_ = bpy.data.objects.get(d_ad)
        if not d_:
            continue
        aci = idx_d * (math.tau / max(1, n_d)) + 0.41 * ((idx_d * 7) % 5)
        r_max = (0.17 + 0.08 * (idx_d % 3)) * boy
        h_max = (0.26 + 0.10 * ((idx_d + 1) % 3)) * boy
        # True ballistic velocities matching r_max and h_max over flight duration T_tot
        v_r = (r_max * 0.82) / T_tot
        vz0 = (4.0 * h_max) / T_tot
        g_eff = (8.0 * h_max) / (T_tot * T_tot)
        ca, sa = math.cos(aci), math.sin(aci)
        d_.scale = (0, 0, 0); d_.location = (yer.x, yer.y, z0)
        d_.keyframe_insert("scale", frame=f - 1); d_.keyframe_insert("location", frame=f - 1)
        for df in range(0, sure + 1):
            u_ = df / max(1, sure)
            t_ = u_ * T_tot
            rr = r_max * 0.18 + v_r * t_
            zz = z0 + su_(f + df) + vz0 * t_ - 0.5 * g_eff * t_ * t_
            vel = Vector((v_r * ca, v_r * sa, vz0 - g_eff * t_))
            spd = vel.length
            env = math.sin(min(1.0, u_ * 6.0) * math.pi * 0.5) * ((1.0 - u_) ** 0.78)
            en = (0.52 + 0.28 * (1.0 - u_)) * boy * env
            uzun = (1.15 + min(2.3, spd * 0.45)) * boy * env
            d_.location = (yer.x + rr * ca, yer.y + rr * sa, zz)
            if spd > 1e-4:
                d_.rotation_euler = vel.normalized().to_track_quat("Z", "Y").to_euler()
            d_.scale = (max(0.001, en), max(0.001, en), max(0.001, uzun))
            d_.keyframe_insert("location", frame=f + df)
            d_.keyframe_insert("rotation_euler", frame=f + df)
            d_.keyframe_insert("scale", frame=f + df)
        d_.scale = (0, 0, 0)
        d_.keyframe_insert("scale", frame=f + sure + 1)


def samandira():
    """A small cork float: red cap, cream belly, a thin red antenna; it rides on the water at the line's end."""
    M.setdefault("sam_kirmizi", duz_malzeme("SamKirmizi", "#B23A24", 0.5, 0.4))
    M.setdefault("sam_beyaz", duz_malzeme("SamBeyaz", "#EDE4D2", 0.6, 0.3))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.05, location=(0, 0, 0))
    s_ = bpy.context.active_object; s_.name = "Samandira"; s_.scale = (1, 1, 1.25)
    s_.data.materials.append(M["sam_beyaz"]); s_.data.materials.append(M["sam_kirmizi"])
    for p in s_.data.polygons:
        p.use_smooth = True
        p.material_index = 1 if p.center.z > 0.006 else 0
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.005, depth=0.1, location=(0, 0, 0.1))
    a_ = bpy.context.active_object; a_.name = "SamandiraUc"; a_.data.materials.append(M["sam_kirmizi"])
    a_.parent = s_
    s_.parent = TK
    return s_


KILAVUZ = ((0.30, 0.012), (0.46, 0.010), (0.60, 0.0085), (0.73, 0.0072), (0.85, 0.0062), (0.95, 0.0052))


def olta_takimi():
    """A modelled spinning rod around the animated blank: rear and fore cork grips, a butt cap,
    a reel seat with a spinning reel hanging under it (stem, body, spool, crank and knob), and
    six line guides that shrink towards the tip. Grip and reel are one rigid piece keyed to the
    hand; the guides are keyed along the bending blank every frame."""
    import bmesh as bm_
    M.setdefault("mantar", duz_malzeme("Mantar", "#B98A5C", 0.9, 0.15, oynak=0.18, olcek=40.0))
    M.setdefault("olta_metal", duz_malzeme("OltaMetal", "#2F3337", 0.35, 0.6))
    M.setdefault("makara", duz_malzeme("Makara", "#A7AEB2", 0.3, 0.7))
    M.setdefault("olta_govde", duz_malzeme("OltaGovde", "#2E3A2B", 0.4, 0.5))
    parca = []

    def silindir(y0, y1, r0, r1, mat, z=0.0, x=0.0, n=18):
        bpy.ops.mesh.primitive_cone_add(vertices=n, radius1=r0, radius2=r1, depth=abs(y1 - y0),
                                        location=(x, (y0 + y1) / 2, z), rotation=(-math.pi / 2, 0, 0))
        o = bpy.context.active_object
        o.data.materials.append(mat)
        for pl in o.data.polygons:
            pl.use_smooth = True
        parca.append(o)
        return o

    OS_ = murettebat.OLTA_SAP
    silindir(-OS_ - 0.012, -OS_, 0.018, 0.018, M["olta_metal"])              # butt cap
    silindir(-OS_, -0.11, 0.0165, 0.0150, M["mantar"])                       # rear cork grip (gripped by left hand at y=-0.19)
    silindir(-0.11, -0.04, 0.0132, 0.0132, M["olta_metal"])                  # reel seat (between left and right hands)
    silindir(-0.04, 0.14, 0.0155, 0.0110, M["mantar"])                       # fore cork grip (gripped by right hand at y=0.0)
    silindir(0.14, 0.16, 0.0110, 0.0090, M["olta_metal"])                    # winding check
    # spinning reel under the seat (centered at y=-0.075 between the two hands)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.075, -0.032)); st = bpy.context.active_object
    st.scale = (0.006, 0.045, 0.038); st.data.materials.append(M["olta_metal"]); parca.append(st)
    silindir(-0.105, -0.055, 0.020, 0.018, M["olta_metal"], z=-0.062)        # gearbox body
    silindir(-0.055, -0.020, 0.025, 0.025, M["makara"], z=-0.062)            # spool with the line
    silindir(-0.020, -0.008, 0.025, 0.012, M["olta_metal"], z=-0.062)        # spool lip
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.003, depth=0.048,
                                        location=(0.024, 0.0, 0.0), rotation=(0, math.pi / 2, 0))
    kr = bpy.context.active_object; kr.data.materials.append(M["olta_metal"])
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.0065, depth=0.016,
                                        location=(0.048, 0.0, -0.013))
    kn = bpy.context.active_object; kn.data.materials.append(M["mantar"])
    for o_ in (kr, kn):
        for pl in o_.data.polygons:
            pl.use_smooth = True
    bpy.ops.object.select_all(action="DESELECT")
    kr.select_set(True); kn.select_set(True)
    bpy.context.view_layer.objects.active = kr
    bpy.ops.object.join()
    kol_ob = bpy.context.active_object; kol_ob.name = "MakaraKol"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bpy.ops.object.select_all(action="DESELECT")
    for o in parca:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parca[0]
    bpy.ops.object.join()
    sap = bpy.context.active_object; sap.name = "OltaSap"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    sap.parent = TK
    kol_ob.parent = sap
    kol_ob.location = (0.0, -0.078, -0.062)
    kil = []
    for i, (s_, r_) in enumerate(KILAVUZ):
        bpy.ops.mesh.primitive_torus_add(major_radius=r_, minor_radius=0.0014, major_segments=20,
                                         minor_segments=8, location=(0, 0, 0))
        g = bpy.context.active_object; g.name = f"Kilavuz{i}"
        for pl in g.data.polygons:
            pl.use_smooth = True
        g.data.materials.append(M["makara"]); g.parent = TK
        kil.append(g)
    ic = serit("MisinaIc", 2 + len(KILAVUZ), 0.0014, _misina_malzeme(), tip="POLY")
    return sap, kil, ic


def _egri_nokta(nk, s_):
    """Point and tangent at s_ (0..1) along a polyline of evenly spaced samples."""
    t = s_ * (len(nk) - 1)
    i = min(len(nk) - 2, int(t))
    q = t - i
    return nk[i].lerp(nk[i + 1], q), (nk[i + 1] - nk[i]).normalized()


def _damla_havuzu(ad, n=8):
    """Pool of glossy falling water droplets (RDR2 scr_mg_fishing_drips) dripping off the lifted fish."""
    mat = _su_damla_malzeme()
    havuz = []
    for k in range(n):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=0.011, location=(0, 0, 0))
        d_ = bpy.context.active_object; d_.name = f"{ad}_{k}"
        for pl in d_.data.polygons:
            pl.use_smooth = True
        d_.data.materials.append(mat); d_.parent = TK
        d_.visible_shadow = False
        d_.scale = (0, 0, 0); d_.keyframe_insert("scale", frame=0)
        havuz.append(d_)
    return havuz


def _damla_dusur(d_, p0, v0, f_bas, sure=16, z_taban=0.05):
    """Animate a single dripping water bead falling under gravity g=-9.81 m/s^2 with velocity stretch."""
    fps = murettebat.FPS
    d_.scale = (0, 0, 0); d_.location = p0
    d_.keyframe_insert("scale", frame=f_bas - 1); d_.keyframe_insert("location", frame=f_bas - 1)
    bitti = f_bas + sure
    for df in range(0, sure + 1):
        t_ = df / fps
        p = p0 + v0 * t_ + Vector((0.0, 0.0, -0.5 * 9.81 * t_ * t_))
        vel = v0 + Vector((0.0, 0.0, -9.81 * t_))
        if p.z <= z_taban and df > 2:
            bitti = f_bas + df
            break
        u_ = df / max(1, sure)
        env = math.sin(min(1.0, u_ * 6.0) * math.pi * 0.5) * (1.0 - 0.35 * u_)
        spd = vel.length
        d_.location = p
        if spd > 1e-4:
            d_.rotation_euler = vel.normalized().to_track_quat("Z", "Y").to_euler()
        d_.scale = (0.58 * env, 0.58 * env, (1.15 + min(2.2, spd * 0.42)) * env)
        d_.keyframe_insert("location", frame=f_bas + df)
        d_.keyframe_insert("rotation_euler", frame=f_bas + df)
        d_.keyframe_insert("scale", frame=f_bas + df)
    d_.scale = (0, 0, 0); d_.keyframe_insert("scale", frame=bitti + 1)


def _sarkac_adim(p, v, piv0, piv1, L_uzun, dt_kare, sub=16, damp=0.996, itme=Vector((0, 0, 0))):
    """Advance a 3D taut-string spherical pendulum hanging directly from moving rod tip piv0 -> piv1
    using exact 480 Hz Cartesian constraint projection (zero gimbal lock, exact rope length)."""
    dt_s = dt_kare / sub
    g_v = Vector((0.0, 0.0, -9.81)) + itme
    for sv in range(1, sub + 1):
        piv = piv0.lerp(piv1, sv / sub)
        v = (v + g_v * dt_s) * damp
        p = p + v * dt_s
        d = p - piv
        dl = d.length
        if dl > 1e-6:
            n = d / dl
            p = piv + n * L_uzun
            # Remove radial velocity component along the taut string (exact pendulum constraint)
            vr = v.dot(n)
            v = v - n * vr
    return p, v


def balik_sahnesi(tur="cipura", boy=0.34):
    """The elder brother casts, waits, strikes, fights and lands a fish; Latif keeps the boat stopped.
    Unified zero-blur physics engine:
    1. 2nd-order damped Euler-Bernoulli cantilever rod beam (cast whip + fight bend + unhook recoil).
    2. 480 Hz Cartesian spherical pendulum hanging DIRECTLY from real elastic rod tip uc_b (pre-cast
       bobber swing, lifted swinging fish over bucket, post-drop empty hook swing — zero phantom pivot!).
    3. True g=-9.81 m/s^2 unblurred free-fall drop into the multi-species catch bucket with elastic
       water-surface buoyancy dip & rebound + 14 velocity-stretched glossy splash streaks.
    4. 48-iteration 240 Hz Position-Based Verlet fishing line + taut local-normal guide-threaded line."""
    import baliklar
    baliklar.isik(GUNES, V["gunes_guc"], sis=(V["sis"], V["pus"]))
    kayit = murettebat.balik_tut(EKIP, TK, YEKE_PIVOT, 1)
    KS = murettebat.KS
    FPS = murettebat.FPS
    DT = 1.0 / FPS
    N_K = len(kayit)
    F_ = kayit[-1]["f"]
    sc.frame_start, sc.frame_end = 1, F_
    OB, OS = murettebat.OLTA_BOY, murettebat.OLTA_SAP
    olta_takimi()
    sap = bpy.data.objects["OltaSap"]
    makara_kol = bpy.data.objects.get("MakaraKol")
    kilavuzlar = [bpy.data.objects[f"Kilavuz{i}"] for i in range(len(KILAVUZ))]
    ic_misina = bpy.data.objects["MisinaIc"]
    N_OLTA, N_MIS = 16, 20
    olta = serit("Olta", N_OLTA, 0.0102, M["olta_govde"], 0.22)
    misina = serit("Misina", N_MIS, 0.0032, _misina_malzeme())
    kv = kova((-0.42, -0.86))
    kova_doldur(kv, baliklar)
    z_kova_su = kv.z + 0.21
    bal = baliklar.yap(tur, boy, ebeveyn=TK)
    ag = boy / (1 + bal["kuyruk"]) * 0.5                # body centre -> mouth
    su1 = sicrama("Sicrama1", 10, ebeveyn=False)
    su2 = sicrama("Sicrama2", 10, ebeveyn=False)
    su_muc1 = sicrama("SicramaMuc1", 9, ebeveyn=False)
    su_muc2 = sicrama("SicramaMuc2", 9, ebeveyn=False)
    su_kova = sicrama("SicramaKova", 14, kalin=0.007, ebeveyn=True)
    damlalar_bal = _damla_havuzu("BalikDamla", 10)

    # Sample the hull's motion once so world-space sea physics matches the rolling boat
    TKM = {}
    for f_ in range(0, F_ + 2):
        sc.frame_set(f_)
        TKM[f_] = TK.matrix_world.copy()

    def deniz_xy(f_, p_):
        w_ = TKM[min(max(f_, 0), F_ + 1)] @ Vector((p_.x, p_.y, 0.0))
        return Vector((w_.x, w_.y, 0.0))

    def su_kilidi(f_, p_, w_=1.0):
        w0 = TKM[min(max(f_, 0), F_ + 1)] @ Vector((p_.x, p_.y, 0.0))
        return p_ - Vector((0, 0, (w0.z - dalga_z(w0.x, w0.y, f_)) * w_))

    def su_z_yerel(f_, p_):
        w0 = TKM[min(max(f_, 0), F_ + 1)] @ Vector((p_.x, p_.y, 0.0))
        return dalga_z(w0.x, w0.y, f_) - w0.z

    meraKli_tur = "levrek" if tur != "levrek" else "cipura"
    bal2 = baliklar.yap(meraKli_tur, boy * 0.85, ebeveyn=TK, ad="Merakli")
    bekle_f = [k["f"] for k in kayit if k["faz"] == "bekle"]
    vurus_f = [k["f"] for k in kayit if k["faz"] == "vurus"]
    son_atis = [k for k in kayit if k["faz"] == "atis"][-1]
    uc_ = son_atis["el_R"] + son_atis["yon"] * OB
    yatay = Vector((son_atis["yon"].x, son_atis["yon"].y, 0)).normalized()
    W = uc_ + yatay * 2.15; W.z = 0.02
    yakin = uc_ + yatay * 0.32; yakin.z = -0.32         # under the rod tip, beside the hull
    sicradi = set()
    iz = [sicrama(f"Iz{i}", 0, kalin=0.010, ebeveyn=False) for i in range(10)]
    iz_ara, iz_say = round(12 * KS), 0
    sam = samandira()
    DURTME = (0.58, 0.71, 0.84)

    # Pass 1: Precompute tension & approximate underwater pull vector for the elastic cantilever beam
    uc_ham = [k["el_R"] + k["yon"] * OB for k in kayit]
    ger_ham, ref_ham = [], []
    for i, k in enumerate(kayit):
        f, faz, u = k["f"], k["faz"], k["u"]
        uc = uc_ham[i]
        if faz == "bekle":
            dip = sum(math.exp(-((u - c_) / 0.022) ** 2) for c_ in DURTME)
            g_ = 0.03 + 0.06 * dip; r_ = W.copy()
        elif faz == "vurus":
            g_ = 0.32 + 0.36 * math.sin(math.pi * u); r_ = W + Vector((0, 0, -0.18))
        elif faz == "cekis":
            yan = Vector((-yatay.y, yatay.x, 0)) * (0.55 * math.sin(u * math.tau * 1.85))
            r_ = W.lerp(yakin, u ** 1.25) + yan * (1.0 - 0.85 * u)
            r_.z = min(r_.z, -0.10 - 0.24 * u)
            g_ = 0.46 + 0.16 * math.sin(f * 0.42 / KS) + 0.06 * math.sin(f * 0.96 / KS)
        elif faz == "al" and u < 0.64:
            # Real weight of the fish pulling rod tip down + thrash vibration, dropping to 0 on unhook!
            g_ = 0.36 * (1.0 - min(1.0, u / 0.24)) + 0.22 + 0.065 * math.sin(f * 0.92 / KS)
            r_ = uc - Vector((0, 0, 1.4))
        else:
            g_ = 0.0; r_ = uc - Vector((0, 0, 1.0))
        ger_ham.append(g_); ref_ham.append(r_)

    # Smooth rod-tip acceleration (central 2nd difference) for authentic cast-whip inertia
    a_tip = []
    for i in range(N_K):
        p_ = uc_ham[max(0, i - 1)]; c_ = uc_ham[i]; n_ = uc_ham[min(N_K - 1, i + 1)]
        acc = (n_ - 2.0 * c_ + p_) / (DT * DT)
        if acc.length > 26.0:
            acc = acc.normalized() * 26.0
        a_tip.append(acc)
    a_tip = murettebat.yumusat_liste(a_tip, 1.4, [], 0.0, 4.0)

    # Pass 2: 2nd-Order Damped Elastic Euler-Bernoulli Cantilever Rod Beam -> exact uc_b_all[i]
    olta_n_all, uc_b_all = [], []
    d_cur, v_cur = Vector((0, 0, 0)), Vector((0, 0, 0))
    omega_r, zeta_r, sub_r = 15.5, 0.24, 4
    dt_r = DT / sub_r
    for i, k in enumerate(kayit):
        el, yon = k["el_R"], k["yon"]
        uc = uc_ham[i]
        cek = ref_ham[i] - uc
        cek_dik = cek - yon * cek.dot(yon)
        cek_dik = cek_dik.normalized() if cek_dik.length > 1e-4 else Vector((0, 0, -1))
        a_perp = a_tip[i] - yon * a_tip[i].dot(yon)
        hedef_d = cek_dik * (ger_ham[i] * 0.84) - a_perp * 0.036
        if hedef_d.length > 0.95:
            hedef_d = hedef_d.normalized() * 0.95
        for _ in range(sub_r):
            acc_d = (omega_r * omega_r) * (hedef_d - d_cur) - (2.0 * zeta_r * omega_r) * v_cur
            v_cur += acc_d * dt_r
            d_cur += v_cur * dt_r
        d_perp = d_cur - yon * d_cur.dot(yon)
        if d_perp.length > 0.98:
            d_perp = d_perp.normalized() * 0.98
        d_len = d_perp.length
        olta_n = []
        for j in range(N_OLTA):
            s_ = j / (N_OLTA - 1)
            u_s = max(0.0, (s_ - 0.14) / 0.86)
            phi = 0.5 * u_s * u_s * (3.0 - u_s)
            kisal = -0.34 * (d_len * d_len / max(0.5, OB)) * (u_s * u_s)
            olta_n.append(el - yon * OS + yon * ((OS + OB) * s_ + kisal) + d_perp * phi)
        olta_n_all.append(olta_n)
        uc_b_all.append(olta_n[-1].copy())

    # Pass 3: True Unblurred Physics Simulation for Lure, Swinging Pendulum Fish & Gravity Bucket Drop!
    L_serbest = 0.44
    p_uc = uc_b_all[0] + Vector((0.0, 0.0, -L_serbest))
    v_uc = Vector((0.0, 0.0, 0.0))
    p_cast0, v_cast0 = p_uc.copy(), Vector((0.0, 0.0, 0.0))
    cast_basladi = False

    # State variables for the landed fish in "al" & "son"
    al_basladi = False
    L_al0 = 1.8
    L_hang_hedef = 1.55
    p_bal_f = yakin.copy()
    v_bal_f = Vector((0.0, 0.0, 0.0))
    serbest_dustu = False
    suya_degdi = False
    bob_z, bob_vz = z_kova_su, 0.0
    hedef_kova_xy = Vector((kv.x + 0.03, kv.y - 0.01))
    fall_t = 0.0
    p_drop0, v_drop0 = Vector((0, 0, 0)), Vector((0, 0, 0))
    drop_sure_est = 0.36
    damla_say = 0

    for i, k in enumerate(kayit):
        f, faz, u = k["f"], k["faz"], k["u"]
        uc_b0 = uc_b_all[max(0, i - 1)]
        uc_b1 = uc_b_all[i]
        bal_yer, bal_don, bal_hal = Vector((W.x, W.y, -1.2)), (0.0, 0.0, 0.0), "yuz"
        sam_d = 0.0

        if faz == "durdur" or (faz == "atis" and u < 0.48):
            # REAL 480 Hz gravity pendulum for the dangling bobber/lure!
            p_uc, v_uc = _sarkac_adim(p_uc, v_uc, uc_b0, uc_b1, L_serbest, DT, sub=16, damp=0.995)
            uc_nokta = p_uc.copy()
            cast_basladi = False
        elif faz == "atis":
            # Crisp parabolic cast flight launching directly from the swinging pendulum release state
            if not cast_basladi:
                p_cast0 = p_uc.copy()
                cast_basladi = True
            q = (u - 0.48) / 0.52
            w_su = su_kilidi(f, W)
            uc_nokta = p_cast0.lerp(w_su, q) + Vector((0.0, 0.0, 1.55 * q * (1.0 - q)))
            p_uc = uc_nokta.copy()
            if q > 0.96 and "atis" not in sicradi:
                sicrat(su1, deniz_xy(f, W), f, round(18 * KS), 0.68); sicradi.add("atis")
        elif faz == "bekle":
            dip = sum(math.exp(-((u - c_) / 0.022) ** 2) for c_ in DURTME)
            uc_nokta = su_kilidi(f, W + Vector((0.018 * math.sin(f * 0.16 / KS), 0.012 * math.cos(f * 0.13 / KS),
                                                0.014 * math.sin(f * 0.22 / KS) - 0.060 * dip)))
            for c_ in DURTME:
                if u >= c_ and ("durt", c_) not in sicradi:
                    sicrat(iz[iz_say % len(iz)], deniz_xy(f, W), f, round(18 * KS), 0.45)
                    iz_say += 1; sicradi.add(("durt", c_))
            th = -2.5 * math.pi * (1 - u)
            r_ = 1.3 - 1.05 * u
            bal_yer = su_kilidi(f, W + Vector((r_ * math.cos(th), r_ * math.sin(th),
                                               -1.2 + 0.8 * min(1.0, u / 0.3) + 0.15 * max(0.0, (u - 0.8) / 0.2))))
            bal_don, bal_hal = (0.0, 0.0, th), "yuz"
        elif faz == "vurus":
            uc_nokta = su_kilidi(f, W + Vector((0.14 * math.sin(f * 0.48 / KS), 0.05 * math.cos(f * 0.36 / KS),
                                                -0.18 * min(1.0, u / 0.16))))
            if "vurus" not in sicradi:
                sicrat(su2, deniz_xy(f, W), f, round(16 * KS), 0.62); sicradi.add("vurus")
            bal_yer = su_kilidi(f, W + Vector((0.14 * math.sin(f * 0.48 / KS), 0.0, -0.14)))
            bal_hal = "hizli"
        elif faz == "cekis":
            yan = Vector((-yatay.y, yatay.x, 0)) * (0.55 * math.sin(u * math.tau * 1.85))
            uc_n = W.lerp(yakin, u ** 1.25) + yan * (1.0 - 0.85 * u)
            uc_n.z = min(uc_n.z, -0.08 - 0.24 * u)
            uc_nokta = su_kilidi(f, uc_n)
            bal_yer = uc_nokta - Vector((0.0, 0.0, 0.18))
            bal_hal = "hizli"; sam_d = 0.45
            if u >= 0.22 and "muc1" not in sicradi:
                sicrat(su_muc1, deniz_xy(f, uc_nokta), f, round(18 * KS), 0.74); sicradi.add("muc1")
            if u >= 0.56 and "muc2" not in sicradi:
                sicrat(su_muc2, deniz_xy(f, uc_nokta), f, round(18 * KS), 0.70); sicradi.add("muc2")
            p_bal_f = uc_nokta.copy()
        elif faz == "al":
            if not al_basladi:
                al_basladi = True
                p_bal_f = p_bal_f.copy()
                v_bal_f = Vector((0.2, 0.2, 1.4))
                L_al0 = max(1.2, (p_bal_f - uc_b1).length)
                # Target line length at release so fish hangs ~0.62 m cleanly above the bucket water
                al_son_i = max(idx_ for idx_, k_ in enumerate(kayit) if k_["faz"] == "al" and k_["u"] <= 0.64)
                L_hang_hedef = max(1.05, uc_b_all[al_son_i].z - (z_kova_su + 0.68))

            if u < 0.64:
                # REAL 480 Hz spherical pendulum hanging DIRECTLY from moving elastic rod tip uc_b!
                q_reel = min(1.0, u / 0.48)
                q_s = q_reel * q_reel * (3.0 - 2.0 * q_reel)
                L_cur = L_al0 + (L_hang_hedef - L_al0) * q_s
                # Fish tail thrash lateral impulse (real swing oscillation!)
                thr = max(0.20, 1.0 - 0.78 * (u / 0.64))
                itme_bal = Vector((4.2 * math.sin(f * 0.55 / KS) * thr,
                                   3.2 * math.cos(f * 0.47 / KS) * thr, 0.0))
                # Gentle aerodynamic stabilization near release so fish lands squarely in the bucket mouth
                damp_p = 0.994 if u < 0.48 else 0.980
                p_bal_f, v_bal_f = _sarkac_adim(p_bal_f, v_bal_f, uc_b0, uc_b1, L_cur, DT, sub=16, damp=damp_p, itme=itme_bal)
                # Gently guide XY toward bucket center only in final 0.16s (hand steadying/aiming line)
                if u > 0.48:
                    q_aim = (u - 0.48) / 0.16
                    err_xy = Vector((hedef_kova_xy.x - p_bal_f.x, hedef_kova_xy.y - p_bal_f.y, 0.0))
                    p_bal_f += err_xy * (0.14 * q_aim)
                    # Re-project onto exact sphere around uc_b1 so rope stays 100% taut!
                    d_fix = p_bal_f - uc_b1
                    if d_fix.length > 1e-5:
                        p_bal_f = uc_b1 + d_fix.normalized() * L_cur

                uc_nokta = p_bal_f.copy()
                sam_d = 0.42
                if uc_nokta.z > su_z_yerel(f, uc_nokta) + 0.03 and "cik" not in sicradi:
                    sicrat(su1, deniz_xy(f, uc_nokta), f, round(22 * KS), 1.0); sicradi.add("cik")

                # Align fish body axis directly with the taut fishing line string (mouth up along string!)
                ip_yon = (uc_b1 - p_bal_f).normalized()
                bal_yer = p_bal_f - ip_yon * ag
                eg_x = math.atan2(-ip_yon.y, max(0.15, ip_yon.z))
                eg_y = math.atan2(ip_yon.x, max(0.15, ip_yon.z))
                bal_don = (math.radians(90) + eg_x * 1.15, eg_y * 1.15,
                           math.radians(32.0) * math.sin(f * 0.65 / KS) * thr)
                bal_hal = "cirpin"

                # RDR2 scr_mg_fishing_drips: sparkling water drops falling off the lifted swinging fish
                if 0.12 <= u <= 0.62 and (f % 5 == 0):
                    d_ = damlalar_bal[damla_say % len(damlalar_bal)]
                    damla_say += 1
                    v_drop = Vector((v_bal_f.x * 0.35, v_bal_f.y * 0.35, -0.30))
                    _damla_dusur(d_, bal_yer + Vector((0.0, 0.0, -0.10)), v_drop, f, sure=16, z_taban=kv.z + 0.08)

                # Keep light-pendulum state synchronized in case next frame is unhook!
                p_uc = uc_nokta.copy(); v_uc = v_bal_f.copy()
            else:
                # UNHOOKED! True g=-9.81 m/s^2 FREE-FALL into wooden bucket + damped water-surface bounce!
                if not serbest_dustu:
                    serbest_dustu = True
                    p_drop0 = bal_yer.copy()
                    dz_drop = max(0.15, p_drop0.z - (z_kova_su + 0.04))
                    drop_sure_est = math.sqrt(2.0 * dz_drop / 9.81)
                    # Horizontal velocity aimed straight into bucket water over exact gravity fall duration
                    v_drop0 = Vector(((hedef_kova_xy.x - p_drop0.x) / max(0.12, drop_sure_est),
                                      (hedef_kova_xy.y - p_drop0.y) / max(0.12, drop_sure_est),
                                      min(-0.15, v_bal_f.z * 0.35)))
                    fall_t = 0.0
                    # Empty hook + bobber recoils upward cleanly onto free light pendulum from uc_b
                    L_serbest = 0.56
                    p_uc = uc_b1 + (p_bal_f - uc_b1).normalized() * L_serbest
                    v_uc = v_bal_f * 0.45 + Vector((0.0, 0.0, 0.85))

                # 1. Empty hook/bobber swings freely on real gravity pendulum from uc_b
                p_uc, v_uc = _sarkac_adim(p_uc, v_uc, uc_b0, uc_b1, L_serbest, DT, sub=16, damp=0.993)
                uc_nokta = p_uc.copy()
                sam_d = 0.14

                # 2. Fish falls under REAL g=-9.81 m/s^2 gravity, splashes hard, dips & bobs back up!
                if not suya_degdi:
                    fall_t += DT
                    p_now = p_drop0 + v_drop0 * fall_t + Vector((0.0, 0.0, -0.5 * 9.81 * fall_t * fall_t))
                    q_rot = min(1.0, fall_t / max(0.12, drop_sure_est))
                    bal_don = (math.radians(90 - 156 * (q_rot * q_rot)),
                               math.radians(18 * q_rot),
                               math.radians(28 * q_rot))
                    bal_hal = "cirpin"
                    if p_now.z <= z_kova_su + 0.05:
                        suya_degdi = True
                        bob_z = z_kova_su + 0.04
                        bob_vz = v_drop0.z - 9.81 * fall_t     # real impact velocity entering bucket water!
                        bal_yer = Vector((hedef_kova_xy.x, hedef_kova_xy.y, bob_z))
                        if "kova_su" not in sicradi:
                            sicrat(su_kova, kv, f, round(22 * KS), 0.82, z0=z_kova_su + 0.03)
                            sicradi.add("kova_su")
                    else:
                        bal_yer = p_now
                else:
                    # Damped buoyancy plunge & rebound settling naturally on top of the catch haul!
                    z_dinlen = z_kova_su + 0.055
                    for _ in range(4):
                        dt_b = DT / 4.0
                        acc_b = (15.0 * 15.0) * (z_dinlen - bob_z) - (2.0 * 0.42 * 15.0) * bob_vz
                        bob_vz += acc_b * dt_b
                        bob_z += bob_vz * dt_b
                    bob_z = max(kv.z + 0.14, bob_z)
                    bal_yer = Vector((hedef_kova_xy.x, hedef_kova_xy.y, bob_z))
                    bal_don = (math.radians(-66), math.radians(18), math.radians(28))
                    bal_hal = "asili"
        else:                                                   # son: relaxed settle, empty bobber gently swinging
            p_uc, v_uc = _sarkac_adim(p_uc, v_uc, uc_b0, uc_b1, L_serbest, DT, sub=16, damp=0.992)
            uc_nokta = p_uc.copy(); sam_d = 0.14
            z_dinlen = z_kova_su + 0.055
            for _ in range(4):
                dt_b = DT / 4.0
                acc_b = (15.0 * 15.0) * (z_dinlen - bob_z) - (2.0 * 0.42 * 15.0) * bob_vz
                bob_vz += acc_b * dt_b
                bob_z += bob_vz * dt_b
            bal_yer = Vector((hedef_kova_xy.x, hedef_kova_xy.y, max(kv.z + 0.14, bob_z)))
            bal_don = (math.radians(-66), math.radians(18), math.radians(28))
            bal_hal = "asili"

        k.update(uc_nokta_sim=uc_nokta, bal_yer_sim=bal_yer, bal_don_sim=bal_don,
                 bal_hal=bal_hal, sam_d=sam_d)

    # Pass 4: Keyframe elastic rod, flush local-normal guides + POLY MisinaIc, 48-iter 240Hz Verlet Misina,
    # rotating reel crank, float & fish (ZERO Gaussian blur on physical gravity/pendulum!)
    P_ver = None
    P_prev = None
    L_rest_cur = L_serbest
    uc_b_prev = None
    uc_n_prev = None
    makara_aci = 0.0
    for i, k in enumerate(kayit):
        f, faz, u = k["f"], k["faz"], k["u"]
        el, yon = k["el_R"], k["yon"]
        olta_n = olta_n_all[i]
        uc_b = uc_b_all[i]
        uc_nokta = k["uc_nokta_sim"]
        bal_yer = k["bal_yer_sim"]
        bal_don = k["bal_don_sim"]

        serit_anahtar(olta, olta_n, f)

        # Grip, reel & animated rotating crank
        don_q = yon.to_track_quat("Y", "Z")
        sap.location = el; sap.rotation_euler = don_q.to_euler()
        sap.keyframe_insert("location", frame=f); sap.keyframe_insert("rotation_euler", frame=f)
        if makara_kol is not None:
            if faz == "cekis" and u >= 0.44:
                makara_aci += math.tau * 5.0 / max(1, round(96 * 0.56))
            elif faz == "al" and u < 0.35:
                makara_aci += 0.24
            makara_kol.rotation_euler = (makara_aci, 0.0, 0.0)
            makara_kol.keyframe_insert("rotation_euler", index=0, frame=f)

        # Six smooth guide rings seated flush along the CURVED blank local normal + razor-straight POLY MisinaIc
        alt_y = don_q @ Vector((0, 0, -1))
        ic_n = [el + don_q @ Vector((0.0, -0.02, -0.062 + 0.024))]
        for g, (s_g, r_g) in zip(kilavuzlar, KILAVUZ):
            pn, tn = _egri_nokta(olta_n, s_g)
            n_g = alt_y - tn * alt_y.dot(tn)
            n_g = n_g.normalized() if n_g.length > 1e-4 else alt_y
            merkez = pn + n_g * (0.0102 * (1.0 - 0.78 * s_g) + r_g + 0.001)
            g.location = merkez
            g.rotation_euler = tn.to_track_quat("Z", "Y").to_euler()
            g.keyframe_insert("location", frame=f); g.keyframe_insert("rotation_euler", frame=f)
            ic_n.append(merkez)
        ic_n.append(uc_b)
        serit_anahtar(ic_misina, ic_n, f)

        # 20-Node 240 Hz Position-Based Verlet Rope Solver (48 PBD iterations/sub-step -> zero rubbery droop!)
        dist_c = max(0.15, (uc_nokta - uc_b).length)
        if P_ver is None:
            P_ver = [uc_b.lerp(uc_nokta, j / (N_MIS - 1)) for j in range(N_MIS)]
            P_prev = [p.copy() for p in P_ver]
            uc_b_prev = uc_b.copy(); uc_n_prev = uc_nokta.copy()
            L_rest_cur = dist_c * 1.0005
        else:
            if faz == "atis" and u >= 0.48:
                q_c = (u - 0.48) / 0.52
                hedef_L = dist_c * (1.02 + 0.13 * math.sin(math.pi * q_c))
            elif faz == "bekle":
                hedef_L = dist_c * 1.045
            elif faz in ("vurus", "cekis"):
                hedef_L = dist_c * 1.0002
            else:
                # Pendulum phases (durdur, atis wind-up, al, son): taut real pendulum string!
                hedef_L = dist_c * 1.0004
            L_rest_cur += (hedef_L - L_rest_cur) * (0.75 if faz != "bekle" else 0.30)
            seg_len = max(0.008, L_rest_cur / (N_MIS - 1))
            sub_v = 8
            dt_v = DT / sub_v
            grav_v = Vector((0.0, 0.0, -9.81)) * (dt_v * dt_v)
            su_yuz = su_z_yerel(f, uc_nokta)
            taut_faz = faz in ("vurus", "cekis", "durdur", "son") or faz == "al" or (faz == "atis" and u < 0.48)
            for sv in range(1, sub_v + 1):
                al_s = sv / sub_v
                p_start = uc_b_prev.lerp(uc_b, al_s)
                p_end = uc_n_prev.lerp(uc_nokta, al_s)
                P_ver[0] = p_start.copy(); P_prev[0] = p_start.copy()
                P_ver[-1] = p_end.copy(); P_prev[-1] = p_end.copy()
                damp = 0.92 if taut_faz else 0.985
                for m_i in range(1, N_MIS - 1):
                    vel_m = (P_ver[m_i] - P_prev[m_i]) * damp
                    P_prev[m_i] = P_ver[m_i].copy()
                    P_ver[m_i] = P_ver[m_i] + vel_m + grav_v
                # 48 Gauss-Seidel iterations -> inextensible, zero-sag taut fishing line!
                for _ in range(48):
                    P_ver[0] = p_start
                    P_ver[-1] = p_end
                    for m_i in range(N_MIS - 1):
                        delta = P_ver[m_i + 1] - P_ver[m_i]
                        dl = delta.length
                        if dl < 1e-6:
                            continue
                        diff = (dl - seg_len) / dl
                        if m_i == 0:
                            P_ver[1] -= delta * diff
                        elif m_i == N_MIS - 2:
                            P_ver[N_MIS - 2] += delta * diff
                        else:
                            corr = delta * (0.5 * diff)
                            P_ver[m_i] += corr
                            P_ver[m_i + 1] -= corr
                    if faz == "bekle":
                        for m_i in range(3, N_MIS - 1):
                            if P_ver[m_i].z < su_yuz + 0.014:
                                P_ver[m_i].z = su_yuz + 0.014
            uc_b_prev = uc_b.copy(); uc_n_prev = uc_nokta.copy()
        serit_anahtar(misina, P_ver, f)

        # Bobber / float sits cleanly along the terminal Verlet line segment
        boy_ = P_ver[-2] - P_ver[-1]
        b_dir = boy_.normalized() if boy_.length > 1e-4 else Vector((0, 0, 1))
        sam.location = uc_nokta + b_dir * k["sam_d"]
        dik_ = Vector((0, 0, 1)).lerp(b_dir, min(1.0, k["sam_d"] / 0.42))
        sam.rotation_euler = dik_.to_track_quat("Z", "Y").to_euler()
        sam.keyframe_insert("location", frame=f); sam.keyframe_insert("rotation_euler", frame=f)

        bal.location = bal_yer; bal.rotation_euler = bal_don
        bal.keyframe_insert("location", frame=f); bal.keyframe_insert("rotation_euler", frame=f)

        # The curious second fish: circles the opposite way, bolts when the line snaps tight
        if bekle_f and bekle_f[0] <= f <= bekle_f[-1]:
            u2 = (f - bekle_f[0]) / max(1, bekle_f[-1] - bekle_f[0])
            th2 = math.pi - 2.0 * math.pi * (1 - u2)
            r2 = 1.3 - 0.5 * u2
            m_ = W + Vector((r2 * math.cos(th2), r2 * math.sin(th2), -1.2 + 0.65 * min(1.0, u2 / 0.3)))
            bal2.location = su_kilidi(f, m_); bal2.rotation_euler = (0, 0, th2)
            kacis = (m_.copy(), th2)
        elif vurus_f and f > bekle_f[-1] and f <= vurus_f[0] + round(50 * KS):
            q2 = (f - bekle_f[-1]) / round(50 * KS)
            p0, h0 = kacis
            ileri_ = Vector((-math.sin(h0), math.cos(h0), 0))
            bal2.location = p0 + ileri_ * (2.6 * q2 * q2) + Vector((0, 0, -1.2 * q2))
            bal2.rotation_euler = (math.radians(-25) * q2, 0, h0)
        else:
            bal2.location = W + Vector((0, 0, -3.0)); bal2.rotation_euler = (0, 0, 0)
        bal2.keyframe_insert("location", frame=f); bal2.keyframe_insert("rotation_euler", frame=f)
        if faz == "bekle" and (f - bekle_f[0]) % iz_ara == 0:
            for yer_ in (bal_yer, bal2.location):
                if yer_.z > -0.7:
                    sicrat(iz[iz_say % len(iz)], deniz_xy(f, Vector(yer_)), f, round(24 * KS), 0.55)
                    iz_say += 1
        yk = yeke_koy(k["yeke"])
        for dp in ("location", "rotation_euler", "scale"):
            yk.keyframe_insert(dp, frame=f)

    # Fish body motion, phase by phase
    seg = []
    for k in kayit:
        h_ = k["bal_hal"] or "yuz"
        if seg and seg[-1][0] == h_:
            seg[-1][2] = k["f"]
        else:
            seg.append([h_, k["f"], k["f"]])
    for h_, a_, b_ in seg:
        baliklar.canlandir(bal, h_, a_, b_, hiz=1.0 / KS)
    if bekle_f and vurus_f:
        baliklar.canlandir(bal2, "yuz", bekle_f[0], bekle_f[-1], faz=0.3, hiz=1.0 / KS)
        baliklar.canlandir(bal2, "hizli", bekle_f[-1] + 1, vurus_f[0] + round(50 * KS), hiz=1.0 / KS)

    # Smooth Bezier F-curves on camera/armatures/rod/line (leaving bal's gravity drop & impact crisp!)
    _bezier_fcurves([TK, EKIP["abi"]["arm"], EKIP["kardes"]["arm"], sap, makara_kol,
                     olta, misina, ic_misina, sam, bal2, bpy.data.objects.get("Yeke")] + kilavuzlar)
    print("BALIK_SAHNESI", F_, "kare (480Hz Pendulum + g=-9.81 Free-Fall + 48-iter Verlet + Multi-Fish Bucket)",
          [(h_, a_, b_) for h_, a_, b_ in seg])
    ilk = {}
    for k in kayit:
        ilk.setdefault(k["faz"], k["f"])
    ilk["W"] = W.copy()
    return F_, ilk


def olta_statik_kur(kv_merkez):
    """Build the full 3D Blender spinning rod (cork grips, reel, 6 guide rings, parabolic bending
    blank, threaded line) and dynamic caught fish + bucket splash for still and sprite renders."""
    if "Olta" not in _olta_statik:
        return
    p1, uc = _olta_statik["Olta"]
    OS, OB = murettebat.OLTA_SAP, murettebat.OLTA_BOY
    yon = (uc - p1).normalized()
    el = p1 + yon * OS
    _, uc_nokta = _olta_statik.get("Misina", (uc, uc + Vector((-0.35, 0.15, -0.95))))
    gerilim = {"olta": 0.12, "olta_vurus": 0.44, "tuttu": 0.36}.get(POZ, 0.12)
    sarkma = {"olta": 0.14, "olta_vurus": 0.02, "tuttu": 0.0}.get(POZ, 0.08)

    olta_takimi()
    sap = bpy.data.objects["OltaSap"]
    kilavuzlar = [bpy.data.objects[f"Kilavuz{i}"] for i in range(len(KILAVUZ))]
    ic_misina = bpy.data.objects["MisinaIc"]
    olta = serit("Olta", 16, 0.0102, M["olta_govde"], 0.22)
    misina = serit("Misina", 16, 0.0032, _misina_malzeme())

    cek = uc_nokta - uc
    cek_dik = cek - yon * cek.dot(yon)
    cek_dik = cek_dik.normalized() if cek_dik.length > 1e-4 else Vector((0, 0, -1))
    olta_n = []
    d_len = gerilim * 0.78
    for j in range(16):
        s_ = j / 15
        u_s = max(0.0, (s_ - 0.14) / 0.86)
        phi = 0.5 * u_s * u_s * (3.0 - u_s)
        kisal = -0.34 * (d_len * d_len / max(0.5, OB)) * (u_s * u_s)
        olta_n.append(el - yon * OS + yon * ((OS + OB) * s_ + kisal) + cek_dik * (d_len * phi))
    serit_anahtar(olta, olta_n, 1)
    uc_b = olta_n[-1]
    don_q = yon.to_track_quat("Y", "Z")
    sap.location = el; sap.rotation_euler = don_q.to_euler()
    alt_y = don_q @ Vector((0, 0, -1))
    ic_n = [el + don_q @ Vector((0.0, -0.02, -0.062 + 0.025))]
    for g, (s_g, r_g) in zip(kilavuzlar, KILAVUZ):
        pn, tn = _egri_nokta(olta_n, s_g)
        merkez = pn + alt_y * (0.0105 * (1 - 0.76 * s_g) + r_g + 0.004)
        g.location = merkez
        g.rotation_euler = tn.to_track_quat("Z", "Y").to_euler()
        ic_n.append(merkez + alt_y * (r_g * 0.6))
    ic_n.append(uc_b)
    serit_anahtar(ic_misina, ic_n, 1)

    if POZ == "tuttu" and "balik" in _olta_statik:
        # Fish swinging mid-air on the line right above the bucket + active water droplets splashing out of the bucket!
        bal_yer = uc_b + Vector((0.04, -0.03, -0.74))
        uc_nokta = bal_yer + Vector((0.0, 0.0, 0.14))
        bal = balik_yap(bal_yer, 0.36, TK)
        bal.rotation_euler = (math.radians(14), math.radians(-12), math.pi / 2 + 0.28)
    mis = []
    for j in range(16):
        s_ = j / 15
        mis.append(uc_b.lerp(uc_nokta, s_) - Vector((0, 0, sarkma * 4 * s_ * (1 - s_))))
    serit_anahtar(misina, mis, 1)


if POZ in ("olta", "olta_vurus", "tuttu"):
    kv_ = kova((-0.32, -0.92))
    olta_statik_kur(kv_)
    if POZ == "tuttu":
        bal_k = balik_yap(kv_ + Vector((0.02, -0.02, 0.26)), 0.34, TK)
        bal_k.rotation_euler = (math.radians(-66), math.radians(16), math.radians(22))
        su_k = sicrama("SicramaKovaStatik", 8)
        sicrat(su_k, kv_, -3, sure=12, boy=0.72, z0=kv_.z + 0.24)
        sc.frame_set(1)

# ---------------------------------------------------------------- light
bpy.ops.object.light_add(type="SUN")
gun = bpy.context.active_object
gun.data.energy = V["gunes_guc"]
gun.data.color = lin(V["gunes_renk"])[:3]
gun.data.angle = math.radians(1.6)
gun.rotation_euler = GUNES.to_track_quat("Z", "Y").to_euler()

# ---------------------------------------------------------------- camera
cd = bpy.data.cameras.new("Kamera")
cd.sensor_fit = "VERTICAL"; cd.sensor_height = 24.0
cd.lens = 12.0 / math.tan(math.radians(YARI_FOV))
cd.clip_start, cd.clip_end = 0.5, 6000
cam = bpy.data.objects.new("Kamera", cd); bagla(cam); sc.camera = cam
cam.location = (0, 0, KAMERA_Y)
cam.rotation_euler = (math.radians(90 - EGIM), 0, math.radians(YAW))
if os.environ.get("SEFER_YAKIN"):  # close-up from the port bow quarter: faces and hands
    bpy.context.view_layer.update()
    W_ = TK.matrix_world
    hedef = W_ @ Vector((0.1, -0.85, 1.5))
    cam.location = W_ @ Vector((-6.0, -0.05, 2.9))
    cam.rotation_euler = (hedef - cam.location).to_track_quat("-Z", "Y").to_euler()
    cd.lens = 20
if os.environ.get("SEFER_BAK"):     # check camera, boat-local "cx,cy,cz,hx,hy,hz,lens"
    bpy.context.view_layer.update()
    W_ = TK.matrix_world
    b_ = [float(x) for x in os.environ["SEFER_BAK"].split(",")]
    cam.location = W_ @ Vector(b_[0:3])
    cam.rotation_euler = (W_ @ Vector(b_[3:6]) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cd.lens = b_[6]

# ---------------------------------------------------------------- render
r = sc.render
r.engine = "BLENDER_EEVEE"
r.resolution_x, r.resolution_y, r.resolution_percentage = GEN, int(GEN * 16 / 9), 100
ee = sc.eevee
ee.taa_render_samples = 48
for ad_, d_ in (("use_raytracing", True), ("use_shadows", True)):
    if hasattr(ee, ad_):
        setattr(ee, ad_, d_)
sc.view_settings.view_transform = "Khronos PBR Neutral"
sc.view_settings.look = "None"
sc.view_settings.exposure = -0.35

def grenle(yol, guc=0.011, tohum=7):
    """Whisper-quiet tactile print grain (~1.1% in mid-tones; breaks CG sterility without noise)."""
    im = bpy.data.images.load(yol)
    w, h = im.size
    px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
    n = np.random.default_rng(tohum).normal(0.0, 1.0, (h, w)).astype(np.float32)
    n = 0.6 * n + 0.2 * (np.roll(n, 1, 0) + np.roll(n, 1, 1))      # a touch of clumping
    lum = px[..., :3].mean(-1)
    agirlik = 0.45 + 0.55 * (1.0 - np.abs(lum - 0.5) * 2.0)
    px[..., :3] = np.clip(px[..., :3] + (n * guc * agirlik)[..., None], 0.0, 1.0)
    im.pixels.foreach_set(px.ravel())
    im.filepath_raw = yol
    im.file_format = "PNG"
    im.save()


if KOMUT == "still":
    sc.frame_set(1)
    r.image_settings.file_format = "PNG"
    r.filepath = CIKTI
    bpy.ops.render.render(write_still=True)
    if not os.environ.get("SEFER_GRENSIZ"):
        grenle(CIKTI)
elif KOMUT == "anim":
    kare = int(ARGS[6]) if len(ARGS) > 6 else 24
    sc.frame_start, sc.frame_end = 1, kare
    murettebat.canlandir(EKIP, TK, SAHNE, POZ, 1, kare)
    r.image_settings.file_format = "PNG"
    for f_ in range(1, kare + 1):
        sc.frame_set(f_)
        yol_ = f"{CIKTI}_{f_:03d}.png"
        r.filepath = yol_
        bpy.ops.render.render(write_still=True)
elif KOMUT == "sprite":
    # Transparent 3D boat + crew (Yusuf & Latif) cutout for live app canvas animation
    deniz.hide_render = True
    r.film_transparent = True
    r.resolution_x = GEN
    r.resolution_y = int(GEN * 0.92)
    cd.sensor_fit = "AUTO"
    bpy.context.view_layer.update()
    W_ = TK.matrix_world
    hedef = W_ @ Vector((0.08, -0.32, 2.72))
    cam.location = W_ @ Vector((-9.4, -1.85, 3.22))
    cam.rotation_euler = (hedef - cam.location).to_track_quat("-Z", "Y").to_euler()
    cd.lens = 33.0
    sc.frame_set(1)
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    r.filepath = CIKTI
    bpy.ops.render.render(write_still=True)
elif KOMUT == "balik":     # the fishing sequence as a video (and .blend with SEFER_KAYDET)
    if "Dalga" in deniz.modifiers:
        deniz.modifiers["Dalga"].show_viewport = False
    F_, ilk = balik_sahnesi(os.environ.get("SEFER_BALIK", "cipura"))
    if not (os.environ.get("SEFER_BAK") or os.environ.get("SEFER_YAKIN")):
        # port-aft quarter looking forward (+Y towards the Aegean islands, lateen yard, Yusuf's standing pose & bucket)
        bpy.context.view_layer.update()
        W_ = TK.matrix_world
        # while the fish circles and takes the lure, the frame leans towards the water out there
        # the camera steps out over the port beam: float in front, fisher behind, both in one tall frame
        su_ = Vector((-0.30, -0.95, 1.65)).lerp(Vector((ilk["W"].x, ilk["W"].y, -0.2)), 0.5)
        su_k = tuple(su_ + Vector((-6.6, -1.9, 2.75)))
        cekimler = ((1, (-0.30, -0.95, 1.65), (-5.2, -3.2, 2.55), 20.0),
                    (ilk["bekle"], (-0.30, -0.95, 1.65), (-5.2, -3.2, 2.55), 20.0),
                    (ilk["bekle"] + 26, tuple(su_), su_k, 22.0),
                    (ilk["cekis"] + 18, tuple(su_), su_k, 22.0),
                    (ilk["cekis"] + 64, (-0.30, -0.95, 1.65), (-5.2, -3.2, 2.55), 20.0),
                    (ilk["al"] - 4, (-0.28, -1.00, 1.66), (-4.6, -2.90, 2.40), 22.0),
                    (ilk["al"] + 48, (-0.16, -1.06, 1.65), (-3.5, -2.35, 2.15), 27.0),
                    (F_, (-0.14, -1.06, 1.66), (-3.4, -2.30, 2.12), 28.0))
        for f_, h_, k_, l_ in cekimler:
            hedef = W_ @ Vector(h_)
            cam.location = W_ @ Vector(k_)
            cam.rotation_euler = (hedef - cam.location).to_track_quat("-Z", "Y").to_euler()
            cd.lens = l_
            cam.keyframe_insert("location", frame=f_); cam.keyframe_insert("rotation_euler", frame=f_)
            cd.keyframe_insert("lens", frame=f_)
        taban = []
        for f_ in range(1, F_ + 1, 8):
            sc.frame_set(f_)
            taban.append((f_, cam.location.copy(), cam.rotation_euler.copy()))
        for f_, l0_, r0_ in taban:
            t_ = f_ / murettebat.FPS
            cam.location = l0_; cam.rotation_euler = r0_
            cam.location += Vector((0.028 * math.sin(t_ * 0.47), 0.020 * math.sin(t_ * 0.34 + 1.1),
                                    0.016 * math.sin(t_ * 0.62 + 0.4)))
            cam.rotation_euler.z += math.radians(0.28) * math.sin(t_ * 0.27 + 0.7)
            cam.rotation_euler.x += math.radians(0.20) * math.sin(t_ * 0.39)
            cam.keyframe_insert("location", frame=f_); cam.keyframe_insert("rotation_euler", frame=f_)
        _bezier_fcurves([cam, cd])
    if "Dalga" in deniz.modifiers:
        deniz.modifiers["Dalga"].show_viewport = True
    if os.environ.get("SEFER_KAYDET"):
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(os.environ["SEFER_KAYDET"]))
    kareler = os.environ.get("SEFER_KARELER")      # "12,80,150": stills only, for checking
    if kareler:
        r.image_settings.file_format = "PNG"
        for f_ in [int(x) for x in kareler.split(",")]:
            sc.frame_set(f_)
            r.filepath = f"{CIKTI}_{f_:03d}.png"
            bpy.ops.render.render(write_still=True)
    else:
        ee.taa_render_samples = 24
        sc.render.fps = murettebat.FPS
        im_ = r.image_settings
        if hasattr(im_, "media_type"):
            im_.media_type = "VIDEO"
        im_.file_format = "FFMPEG"
        r.ffmpeg.format = "MPEG4"; r.ffmpeg.codec = "H264"; r.ffmpeg.constant_rate_factor = "HIGH"
        r.filepath = CIKTI
        bpy.ops.render.render(animation=True)
elif KOMUT == "kaydet":
    murettebat.canlandir(EKIP, TK, SAHNE, POZ, 1, 48)
    bpy.ops.wm.save_as_mainfile(filepath=CIKTI)
print("BITTI", KOMUT, SAHNE, VAKIT)
