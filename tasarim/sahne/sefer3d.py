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
CIKTI = ARGS[3]
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
YELKEN = dict(kalkis=0.0, seyir=1.0, varis=0.5)[SAHNE]
HIZ = dict(kalkis=0.0, seyir=1.0, varis=0.35)[SAHNE]

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
M["bayrak"] = bayrak_malzeme()
M["kusak"] = duz_malzeme("Kusak", "#6B4A30", 0.8, 0.2)
M["balik"] = duz_malzeme("Balik", "#B9C6CC", 0.25, 0.7)
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
    if cati == "kiremit":
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.0, radius2=0.0, depth=1.0,
                                        location=(x, y, z + h_ + 0.55), rotation=(0, 0, ac + math.pi / 4))
        r_ = bpy.context.active_object
        r_.scale = (w_ * 0.78, d_ * 0.78, 1.15)
        r_.data.materials.append(M["kiremit"])
    else:
        kutu("Parapet", (w_ + 0.15, d_ + 0.15, 0.35), (x, y, z + h_ + 0.12), M["badana"], ac, 0.08)
    # door and windows on the face towards the camera
    yon = Vector((math.sin(ac), -math.cos(ac), 0))
    yan = Vector((math.cos(ac), math.sin(ac), 0))
    on = Vector((x, y, z)) + yon * (d_ / 2 + 0.02)
    kutu("Kapi", (0.9, 0.12, 1.9), (on + yan * (-w_ * 0.22) + Vector((0, 0, 0.95)))[:], M["kapi"], ac, 0.03)
    for k in range(1 if h_ < 4 else 2):
        kutu("Pencere", (0.7, 0.12, 0.8), (on + yan * (w_ * 0.2) + Vector((0, 0, 1.6 + k * 1.7)))[:],
             M["pencere"], ac, 0.03)
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
    silindir("FenerKule", 1.7, 1.15, h, (x, y, z), M["badana"], 28)
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
    # rails along the sheer
    for yan in (-1, 1):
        cu = bpy.data.curves.new("Kupeste", "CURVE"); cu.dimensions = "3D"
        cu.bevel_depth = 0.07; cu.bevel_resolution = 2
        sp_ = cu.splines.new("POLY"); sp_.points.add(len(serenler) - 1)
        for k, (b, yy, zs) in enumerate(serenler):
            sp_.points[k].co = (yan * b * 1.01, yy, zs + 0.03, 1)
        ob = bpy.data.objects.new("Kupeste", cu); bagla(ob); ob.parent = kok
        cu.materials.append(M["ahsap"])
    # cabin-less fishing boat: a small wheel box, crates, a tiller, a lantern post
    for ad, boyut, kon, mat in (("Sandik", (0.8, 0.6, 0.45), (0.25, -1.6, 0.9), M["ahsap"]),
                                ("Sandik2", (0.6, 0.5, 0.35), (-0.3, -1.1, 0.85), M["guverte"])):
        o = kutu(ad, boyut, kon, mat, 0.1, 0.04); o.parent = kok
    bpy.ops.mesh.primitive_torus_add(major_radius=0.35, minor_radius=0.08, location=(-0.35, 0.3, 0.85))
    hl = bpy.context.active_object; hl.data.materials.append(M["halat"]); hl.parent = kok
    yeke = kutu("Yeke", (0.08, 1.1, 0.08), (0, -3.5, 1.35), M["ahsap"], 0, 0.02); yeke.rotation_euler.x = 0.25
    yeke.parent = kok
    # mast (raked forward) and lateen yard
    direk_alt, direk_ust = Vector((0, 1.0, 0.7)), Vector((0, 1.3, 5.3))
    cubuk("Direk", direk_alt, direk_ust, 0.1, M["ahsap"], kok)
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
    cubuk("Seren", T_ + (T_ - P_) * 0.05, P_ + (P_ - T_) * 0.04, 0.075, M["ahsap"], kok)
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
        cubuk("Sarili", T_.lerp(P_, 0.08), P_.lerp(T_, 0.1), 0.2, M["yelken"], kok)
    # lantern post at the stern
    cubuk("FenerDirek", Vector((-0.4, -3.0, 1.0)), Vector((-0.4, -3.0, 2.3)), 0.04, M["ahsap"], kok)
    f_ = kutu("Fener", (0.13, 0.13, 0.17), (-0.4, -3.0, 2.38), M["fener_cam"], 0, 0.02); f_.parent = kok
    f2 = kutu("FenerSapka", (0.17, 0.17, 0.04), (-0.4, -3.0, 2.49), M["fener_bant"], 0, 0.015); f2.parent = kok
    kok.location = (TX, TY, 0.0)
    kok.rotation_euler = (0, 0, math.radians(TPSI))
    return kok


def cubuk(ad, p1, p2, r, mat, ebeveyn):
    d = p2 - p1
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=r, depth=d.length, location=((p1 + p2) / 2)[:])
    ob = bpy.context.active_object; ob.name = ad
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


if SAHNE == "kalkis":
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
POZ = ARGS[5] if len(ARGS) > 5 else "dumen"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import murettebat  # noqa: E402  (two brothers, MakeHuman)
murettebat.isik(GUNES, V["gunes_guc"])
EKIP = murettebat.murettebat(TK, POZ, SAHNE)
for tur, *a_ in EKIP["cizim"]:
    if tur == "cubuk":
        ad, p1, p2, r_, mk = a_
        cubuk(ad, Vector(p1), Vector(p2), r_, M[mk], TK)
    elif tur == "balik":
        bal = kure(a_[0], 0.27, M["balik"], TK, (0.3, 0.42, 1.0))
        bal.rotation_euler = (0.25, 0, 0.5)
    elif tur == "kangal":
        bpy.ops.mesh.primitive_torus_add(major_radius=0.13, minor_radius=0.032, location=a_[0][:],
                                         rotation=(1.35, 0.0, 0.3))
        kg = bpy.context.active_object; kg.data.materials.append(M["halat"]); kg.parent = TK
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -2.55, 1.06))
otur = bpy.context.active_object
otur.scale = (1.9, 0.32, 0.08)
otur.data.materials.append(M["ahsap"])
otur.parent = TK

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
if os.environ.get("SEFER_YAKIN"):  # close-up on the crew, for checking poses
    bpy.context.view_layer.update()
    W_ = TK.matrix_world
    hedef = W_ @ Vector((0.2, -0.6, 1.8))
    cam.location = W_ @ Vector((4.2, -7.4, 3.1))
    cam.rotation_euler = (hedef - cam.location).to_track_quat("-Z", "Y").to_euler()
    cd.lens = 38

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

def grenle(yol, guc=0.026, tohum=7):
    """Film grain baked into a still: fine monochrome grain, strongest in the mid-tones."""
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
elif KOMUT == "kaydet":
    bpy.ops.wm.save_as_mainfile(filepath=CIKTI)
print("BITTI", KOMUT, SAHNE, VAKIT)
