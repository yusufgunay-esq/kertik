# Kertik "Sefer" fish: a library of Aegean fish, rigged and animated, painted with the crew's brush.
#   blender -b --factory-startup --python baliklar.py -- levha <out.png> [width]
#   blender -b --factory-startup --python baliklar.py -- hareket <tur> <hal> <out.png> [width]
#   blender -b --factory-startup --python baliklar.py -- kaydet <out.blend>     (all swimming, press play)
#   blender -b --factory-startup --python baliklar.py -- video <out.mp4> [width]
# As a module (sefer3d):  baliklar.isik(gunes, guc); arm = baliklar.yap("levrek", 0.5, ebeveyn)
#                         baliklar.canlandir(arm, "asili", 1, 300)
#
# Body: lofted rings over a species profile (top, bottom, half width along the length), so every fish
# is data, not a hand mesh. Fish space: +Y snout, +Z back, X side; body from y=-0.5 (tail root) to
# y=+0.5 (snout), caudal fin behind it. Rig: a spine chain (head to tail fin) plus two pectoral bones.
# Swimming is the textbook travelling body wave x(s,t) = A(s) sin(2pi(t/T - s/lambda)), with the
# envelope A(s) per swimming mode (carangiform, thunniform, anguilliform); each bone takes the slope
# of that wave, so the motion is the measured kinematics, not a wiggle. Rays use a travelling wing wave.
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix

TAU = math.tau
BAND = (0.20, 0.34)                  # sun-normalised light: shadow -> lit (same edge as sefer3d)
GOLGE = (0.70, 0.66, 0.85, 1.0)      # shadow multiplier, warm lilac
SICAK = (1.0, 0.92, 0.78, 1.0)       # warm rim
PARLAK = 1.27
OLCEK = 1.0 / (5.2 * 1.15)
SIS = None                           # (distance, haze colour) when used inside a scene


def isik(gunes, guc, sis=None):
    """Sun strength of the scene (and optional aerial haze), so fish share the world's light edge."""
    global OLCEK, SIS
    OLCEK = 1.0 / (guc * 1.15)
    SIS = sis


def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)


def koyu(h, k):
    return tuple(x * k for x in lin(h)[:3]) + (1.0,)


def egri(nok, x):
    """Catmull-Rom through (x, value...) control points; returns the interpolated tuple."""
    if x <= nok[0][0]:
        return nok[0][1:]
    if x >= nok[-1][0]:
        return nok[-1][1:]
    for i in range(len(nok) - 1):
        if nok[i][0] <= x <= nok[i + 1][0]:
            break
    p0, p1, p2, p3 = nok[max(i - 1, 0)], nok[i], nok[i + 1], nok[min(i + 2, len(nok) - 1)]
    t = (x - p1[0]) / (p2[0] - p1[0])
    out = []
    for k in range(1, len(p1)):
        m1 = (p2[k] - p0[k]) / max(p2[0] - p0[0], 1e-6) * (p2[0] - p1[0])
        m2 = (p3[k] - p1[k]) / max(p3[0] - p1[0], 1e-6) * (p2[0] - p1[0])
        t2, t3 = t * t, t * t * t
        out.append((2 * t3 - 3 * t2 + 1) * p1[k] + (t3 - 2 * t2 + t) * m1 + (-2 * t3 + 3 * t2) * p2[k] + (t3 - t2) * m2)
    return tuple(out)


def kapali_egri(nok, n):
    """Sample an open polyline of 2D points smoothly (Catmull-Rom by index)."""
    idx = [(i,) + tuple(p) for i, p in enumerate(nok)]
    return [egri(idx, (len(nok) - 1) * j / (n - 1)) for j in range(n)]


# ---------------------------------------------------------------- species
# profil: (u, top, bottom, half width), u 0 = tail root .. 1 = snout, body-length units.
# kuyruk: (shape, length, half height). yuzgec lists: dorsal/anal (u0, u1, heights, spiny fraction),
# gogus: (u, height 0..1, length, width, spread deg, droop deg, shape), karin: (u, length).
# desen: pattern layers on (u, h) where h is 0 belly .. 1 back.
TURLER = {
    "cipura": dict(ad="Çipura", boy=0.35, mod="karangi", T=30,
        profil=[(0, .045, -.045, .018), (.12, .09, -.085, .03), (.3, .19, -.16, .06), (.5, .24, -.19, .075),
                (.68, .235, -.18, .08), (.82, .19, -.14, .07), (.92, .11, -.09, .05), (.97, .045, -.06, .03),
                (1, -.02, -.04, .012)],
        kuyruk=("catal", .30, .17), sirt=[(.17, .72, [.07, .11, .1, .09, .08, .075, .075, .055, .02], .55)],
        anal=[(.12, .36, [.05, .07, .06, .05, .02], .3)], gogus=(.74, .32, .2, .06, 25, -6, "sivri"),
        karin=(.62, .08), goz=(.86, .66, .032), iris="#D8B24A",
        renk=dict(sirt="#5E7280", yan="#B9C3C6", karin="#EEEFE8", yuzgec="#8E989C", kenar="#5A6670"),
        parilti=.5,
        desen=[("bar", .93, .02, .74, 1.0, "#D9A93A", .8), ("leke", .775, .74, .012, .07, "#3C3A44", .55),
               ("serit", .5, .015, .15, .85, "#8F9DA3", .35), ("serit", .62, .012, .15, .85, "#8F9DA3", .3),
               ("serit", .38, .012, .15, .8, "#9AA6AA", .25)],
        agiz=(.965, -.035), solungac=(.80, .0, .14)),
    "levrek": dict(ad="Levrek", boy=0.5, mod="karangi", T=34,
        profil=[(0, .04, -.04, .02), (.15, .075, -.07, .035), (.35, .13, -.11, .06), (.55, .15, -.12, .068),
                (.75, .14, -.11, .065), (.88, .105, -.085, .05), (.96, .055, -.05, .03), (1, .0, -.025, .012)],
        kuyruk=("catal", .24, .13), sirt=[(.5, .74, [.04, .1, .09, .07, .05, .02], 1.0),
                                          (.2, .46, [.03, .07, .065, .055, .045, .02], 0)],
        anal=[(.12, .3, [.03, .06, .05, .04, .015], .25)], gogus=(.74, .35, .15, .05, 25, -6, "sivri"),
        karin=(.66, .07), goz=(.89, .64, .026), iris="#C9C4A8",
        renk=dict(sirt="#46566A", yan="#AEB8BE", karin="#ECEEE9", yuzgec="#7A858C", kenar="#4F5A63"),
        parilti=.55,
        desen=[("serit", .63, .01, .02, .86, "#3D4A57", .55)],
        agiz=(.93, -.005), solungac=(.80, .01, .1)),
    "barbun": dict(ad="Barbun", boy=0.22, mod="karangi", T=24,
        profil=[(0, .035, -.035, .018), (.15, .07, -.065, .035), (.4, .13, -.11, .06), (.6, .15, -.12, .07),
                (.78, .14, -.12, .068), (.9, .10, -.11, .055), (.97, .03, -.09, .035), (1, -.05, -.085, .015)],
        kuyruk=("catal", .26, .13), sirt=[(.58, .76, [.05, .12, .11, .08, .04], 1.0),
                                          (.25, .42, [.03, .07, .06, .045, .02], 0)],
        anal=[(.18, .34, [.03, .055, .045, .02], 0)], gogus=(.75, .4, .14, .05, 25, -6, "sivri"),
        karin=(.66, .07), goz=(.90, .72, .03), iris="#E6C26A", biyik=True,
        renk=dict(sirt="#C2453F", yan="#E3846C", karin="#F5DDCB", yuzgec="#E9A07E", kenar="#C9584A"),
        parilti=.35,
        desen=[("serit", .5, .03, .05, .9, "#EAC35C", .75), ("serit", .38, .02, .05, .85, "#EAC35C", .5),
               ("serit", .62, .015, .05, .85, "#D0574A", .4)],
        agiz=(.975, -.085), solungac=(.82, -.02, .12)),
    "uskumru": dict(ad="Uskumru", boy=0.3, mod="ton", T=22,
        profil=[(0, .025, -.025, .02), (.15, .05, -.05, .04), (.4, .1, -.09, .07), (.6, .11, -.1, .075),
                (.8, .095, -.085, .065), (.92, .06, -.055, .042), (1, .0, -.012, .01)],
        kuyruk=("catal", .27, .16), sirt=[(.55, .72, [.03, .08, .065, .045, .02], 1.0),
                                          (.3, .42, [.02, .05, .04, .015], 0)],
        anal=[(.3, .4, [.02, .045, .035, .012], 0)], finlet=(.05, .27, 5), gogus=(.76, .55, .1, .035, 18, -6, "sivri"),
        karin=(.64, .04), goz=(.91, .6, .022), iris="#BFC8C2",
        renk=dict(sirt="#2E6B6A", yan="#C2D5D1", karin="#F2F2EB", yuzgec="#5E7C78", kenar="#3E5C5A"),
        parilti=.7,
        desen=[("dalga", 13, .55, 1.0, "#1B2B33", .95, .58), ("serit", .5, .02, .1, .9, "#7FA8A2", .35)],
        agiz=(.955, -.008), solungac=(.84, .0, .09)),
    "palamut": dict(ad="Palamut", boy=0.6, mod="ton", T=24,
        profil=[(0, .025, -.025, .02), (.15, .06, -.055, .045), (.4, .14, -.12, .09), (.6, .15, -.13, .095),
                (.8, .12, -.11, .08), (.92, .07, -.065, .05), (1, .0, -.015, .01)],
        kuyruk=("hilal", .26, .2), sirt=[(.5, .78, [.03, .1, .07, .05, .03, .02], 1.0),
                                         (.28, .4, [.02, .06, .045, .015], 0)],
        anal=[(.27, .38, [.02, .05, .035, .012], 0)], finlet=(.04, .25, 7), gogus=(.76, .55, .12, .035, 15, -6, "sivri"),
        karin=(.66, .04), goz=(.92, .62, .02), iris="#AEB6BE",
        renk=dict(sirt="#2F4A6B", yan="#C6CED5", karin="#EFF1ED", yuzgec="#3D4F66", kenar="#27384F"),
        parilti=.7,
        desen=[("egik", 11, .85, .56, 1.0, "#1D2C43", .9)],
        agiz=(.955, -.01), solungac=(.84, .0, .11)),
    "sardalya": dict(ad="Sardalya", boy=0.18, mod="karangi", T=16,
        profil=[(0, .03, -.03, .015), (.2, .06, -.065, .03), (.5, .095, -.11, .05), (.75, .09, -.1, .048),
                (.9, .06, -.065, .035), (1, .005, -.015, .01)],
        kuyruk=("catal", .27, .14), sirt=[(.45, .6, [.03, .07, .055, .03, .01], 0)],
        anal=[(.12, .25, [.015, .03, .02, .01], 0)], gogus=(.78, .3, .1, .03, 15, -6, "sivri"),
        karin=(.5, .05), goz=(.92, .58, .028), iris="#C9D0CF", saydam=.35,
        renk=dict(sirt="#2E7A8C", yan="#D0DBDC", karin="#F5F5F0", yuzgec="#A9BBBD", kenar="#6E8C92"),
        parilti=.8,
        desen=[("nokta", .62, .7, .028, "#22323C", .85), ("serit", .58, .03, .02, .9, "#4E9AA6", .35)],
        agiz=(.97, -.005), solungac=(.86, -.01, .08)),
    "orfoz": dict(ad="Orfoz", boy=0.9, mod="subkarangi", T=44,
        profil=[(0, .05, -.05, .03), (.15, .1, -.095, .055), (.4, .17, -.15, .09), (.6, .19, -.16, .1),
                (.8, .17, -.15, .095), (.92, .12, -.11, .075), (.98, .05, -.05, .04), (1, .01, -.03, .02)],
        kuyruk=("yuvarlak", .22, .14), sirt=[(.16, .76, [.04, .07, .075, .07, .065, .07, .085, .07, .02], .55)],
        anal=[(.1, .32, [.04, .08, .085, .06, .02], .2)], gogus=(.72, .4, .17, .08, 30, -6, "yuvarlak"),
        karin=(.62, .09), goz=(.88, .7, .022), iris="#B38A4A",
        renk=dict(sirt="#5A4636", yan="#7E6850", karin="#CBB89A", yuzgec="#56453A", kenar="#C8B48E"),
        parilti=.15,
        desen=[("benek", 9, .56, "#C7B38C", .85), ("benek", 15, .6, "#3E3128", .45)],
        agiz=(.93, -.02), solungac=(.76, .0, .17)),
    "mercan": dict(ad="Mercan", boy=0.35, mod="karangi", T=30,
        profil=[(0, .04, -.04, .018), (.12, .085, -.08, .03), (.3, .17, -.14, .055), (.5, .21, -.17, .07),
                (.68, .21, -.165, .075), (.82, .17, -.13, .066), (.92, .1, -.085, .048), (.97, .04, -.055, .03),
                (1, -.015, -.035, .012)],
        kuyruk=("catal", .3, .16), sirt=[(.17, .72, [.06, .1, .095, .085, .075, .07, .07, .05, .02], .55)],
        anal=[(.12, .35, [.045, .065, .055, .045, .02], .3)], gogus=(.74, .32, .2, .06, 25, -6, "sivri"),
        karin=(.62, .08), goz=(.87, .66, .032), iris="#D98A7A",
        renk=dict(sirt="#C66A78", yan="#E8A8A4", karin="#F7E5DC", yuzgec="#E6A6A2", kenar="#C2606C"),
        parilti=.45,
        desen=[("nokta", .62, .95, .02, "#6E9FCB", .85), ("leke", .775, .76, .012, .06, "#9E3E50", .45)],
        agiz=(.965, -.03), solungac=(.80, .0, .13)),
    "lufer": dict(ad="Lüfer", boy=0.55, mod="karangi", T=26,
        profil=[(0, .035, -.035, .02), (.15, .07, -.065, .035), (.4, .13, -.12, .06), (.6, .14, -.13, .065),
                (.8, .12, -.11, .058), (.93, .07, -.06, .035), (1, .005, -.02, .01)],
        kuyruk=("catal", .27, .15), sirt=[(.5, .66, [.02, .05, .04, .02], 1.0),
                                          (.15, .46, [.03, .08, .065, .045, .03, .015], 0)],
        anal=[(.12, .42, [.03, .07, .05, .035, .02, .01], 0)], gogus=(.75, .45, .13, .04, 20, -6, "sivri"),
        karin=(.65, .05), goz=(.9, .62, .022), iris="#D6C46A",
        renk=dict(sirt="#2E6878", yan="#AFC7CA", karin="#EEF1EC", yuzgec="#7E9A8E", kenar="#3A5E66"),
        parilti=.6,
        desen=[("leke", .73, .45, .02, .03, "#1C2830", .8), ("serit", .55, .02, .1, .9, "#7FA2A8", .3)],
        agiz=(.95, -.012), solungac=(.80, .0, .11)),
    "muren": dict(ad="Müren", boy=1.1, mod="yilan", T=40,
        profil=[(0, .012, -.012, .006), (.1, .03, -.03, .015), (.3, .045, -.045, .03), (.6, .05, -.05, .04),
                (.85, .052, -.05, .042), (.95, .036, -.034, .03), (1, .0, -.01, .01)],
        kuyruk=("sivri", .06, .03), sirt=[(.0, .84, [.03, .035, .035, .03, .025, .022], 0)],
        anal=[(.0, .5, [.03, .03, .025, .02], 0)], goz=(.95, .66, .011), iris="#D9C25E",
        renk=dict(sirt="#5E4C26", yan="#6F5A2E", karin="#8C7840", yuzgec="#5E4C26", kenar="#4A3C1E"),
        parilti=.1, agiz_acik=True,
        desen=[("benek", 22, .5, "#D6C179", .95), ("benek", 40, .6, "#3A2E16", .5)],
        agiz=(.955, -.004), solungac=None),
    "kilic": dict(ad="Kılıç", boy=2.5, mod="ton", T=30,
        profil=[(0, .02, -.02, .018), (.15, .05, -.045, .04), (.4, .12, -.1, .08), (.65, .13, -.11, .085),
                (.85, .1, -.085, .07), (.95, .05, -.045, .04), (1, .01, -.01, .015)],
        kuyruk=("hilal", .22, .23), sirt=[(.66, .8, [.03, .22, .12, .05, .02], 0)],
        anal=[(.2, .3, [.02, .07, .03, .01], 0)], gogus=(.8, .3, .2, .04, 20, -6, "sivri"),
        goz=(.92, .62, .026), iris="#5E6E8A", kilic=.5,
        renk=dict(sirt="#3B3550", yan="#8E8CA2", karin="#DAD8E0", yuzgec="#46405A", kenar="#2E2940"),
        parilti=.5, desen=[], agiz=(.96, -.006), solungac=(.86, .0, .1)),
    "kirlangic": dict(ad="Kırlangıç", boy=0.4, mod="karangi", T=30,
        profil=[(0, .03, -.03, .018), (.2, .06, -.06, .04), (.5, .1, -.095, .065), (.72, .12, -.11, .08),
                (.88, .11, -.11, .085), (.96, .06, -.1, .07), (1, -.02, -.08, .03)],
        kuyruk=("kesik", .22, .12), sirt=[(.62, .82, [.03, .1, .09, .06, .02], 1.0),
                                          (.18, .56, [.02, .06, .055, .05, .04, .015], 0)],
        anal=[(.12, .5, [.02, .05, .045, .04, .03, .01], 0)], gogus=(.72, .22, .34, .13, 14, 15, "kanat"),
        kanat=dict(yuzgec="#3F7C82", kenar="#6A9CBC", benek="#1F3C44"),
        karin=(.7, .07), goz=(.92, .82, .028), iris="#E3A24A",
        renk=dict(sirt="#C24A3A", yan="#E27B5C", karin="#F4DCCA", yuzgec="#DA7D60", kenar="#B4473C"),
        parilti=.3,
        desen=[("serit", .7, .1, .3, .9, "#B03A34", .4)],
        agiz=(.975, -.07), solungac=(.82, -.02, .13)),
}
VATOZ = dict(ad="Vatoz", boy=0.8, T=60, renk=dict(ust="#9A8466", benek="#5A4A36", alt="#EEE7DB"))
SIRA = ["sardalya", "uskumru", "barbun", "cipura", "mercan", "levrek", "lufer", "kirlangic",
        "palamut", "orfoz", "muren", "kilic", "vatoz"]

# swimming modes: envelope A(s) (s 0 head .. 1 tail root), wavelength in body lengths, tail amplitude
MODLAR = {
    "karangi": (lambda s: 0.12 + 0.88 * s * s, 0.95, 0.10),
    "subkarangi": (lambda s: 0.2 + 0.8 * s ** 1.5, 0.9, 0.09),
    "ton": (lambda s: 0.04 + 0.96 * s ** 4, 1.25, 0.10),
    "yilan": (lambda s: 0.35 + 0.65 * s, 0.6, 0.075),
}


# ---------------------------------------------------------------- painted materials
class Firca:
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

    def _gir(self, sok, v):
        if isinstance(v, (int, float)):
            sok.default_value = v
        elif isinstance(v, tuple):
            sok.default_value = v
        else:
            self.b(v, sok)

    def m_(self, op, a, b=None):
        n = self.n("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b)):
            if v is not None:
                self._gir(n.inputs[i], v)
        return n.outputs[0]

    def aralik(self, v, a, b, c=0.0, d=1.0):
        n = self.n("ShaderNodeMapRange"); n.interpolation_type = "SMOOTHSTEP"
        n.inputs["From Min"].default_value, n.inputs["From Max"].default_value = a, b
        n.inputs["To Min"].default_value, n.inputs["To Max"].default_value = c, d
        self._gir(n.inputs["Value"], v)
        return n.outputs["Result"]

    def karis(self, f, a, c, tur="MIX"):
        n = self.n("ShaderNodeMix"); n.data_type = "RGBA"; n.blend_type = tur
        for sok, v in ((n.inputs[0], f), (n.inputs[6], a), (n.inputs[7], c)):
            self._gir(sok, v)
        return n.outputs[2]

    def uv(self, ad):
        u = self.n("ShaderNodeUVMap"); u.uv_map = ad
        s = self.n("ShaderNodeSeparateXYZ"); self.b(u.outputs[0], s.inputs[0])
        return s.outputs[0], s.outputs[1]

    def vek(self, x, y, z=0.0):
        c = self.n("ShaderNodeCombineXYZ")
        for i, v in enumerate((x, y, z)):
            self._gir(c.inputs[i], v)
        return c.outputs[0]

    def gurultu(self, v, olcek, detay=2.0):
        nz = self.n("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = olcek
        nz.inputs["Detail"].default_value = detay
        self.b(v, nz.inputs["Vector"])
        return nz.outputs["Fac"]

    def voronoi(self, v, olcek):
        vo = self.n("ShaderNodeTexVoronoi")
        vo.inputs["Scale"].default_value = olcek
        vo.inputs["Randomness"].default_value = 0.8
        self.b(v, vo.inputs["Vector"])
        return vo.outputs["Distance"]

    def bant(self, x, c, w, yum=0.012):
        d = self.m_("ABSOLUTE", self.m_("SUBTRACT", x, c))
        return self.aralik(d, w * 0.5, w * 0.5 + yum, 1.0, 0.0)

    def boya(self, renk, kenar_guc=0.16, parilti=0.0):
        """Illustrated shading shared with the crew: sun-normalised diffuse, one soft band,
        lilac shadow multiplier, warm rim, plus a silver sheen for scaled sides."""
        d = self.n("ShaderNodeBsdfDiffuse"); d.inputs["Color"].default_value = (1, 1, 1, 1)
        s2r = self.n("ShaderNodeShaderToRGB"); self.b(d.outputs[0], s2r.inputs[0])
        bw = self.n("ShaderNodeRGBToBW"); self.b(s2r.outputs["Color"], bw.inputs[0])
        isik_ = self.m_("MULTIPLY", bw.outputs[0], OLCEK)
        bant = self.aralik(isik_, *BAND)
        golge = self.karis(1.0, renk, GOLGE, "MULTIPLY")
        col = self.karis(bant, golge, renk)
        lw = self.n("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.3
        if parilti:
            # silver scales: grazing views lift towards a cool white, more where lit
            par = self.m_("MULTIPLY", self.m_("POWER", lw.outputs["Facing"], 1.6),
                          self.m_("MULTIPLY", self.m_("ADD", bant, 0.35), parilti * 0.38))
            col = self.karis(par, col, (0.93, 0.96, 0.98, 1.0), "SCREEN")
        kenar = self.m_("MULTIPLY", self.m_("POWER", lw.outputs["Facing"], 3.0), self.m_("MULTIPLY", bant, kenar_guc))
        col = self.karis(kenar, col, SICAK, "SCREEN")
        em = self.n("ShaderNodeEmission"); self.b(col, em.inputs["Color"])
        em.inputs["Strength"].default_value = PARLAK
        return em.outputs[0]

    def bitir(self, s, alfa=None):
        if alfa is not None:
            tr = self.n("ShaderNodeBsdfTransparent")
            mx = self.n("ShaderNodeMixShader")
            self._gir(mx.inputs[0], alfa); self.b(tr.outputs[0], mx.inputs[1]); self.b(s, mx.inputs[2])
            s = mx.outputs[0]
        if SIS:
            cam = self.n("ShaderNodeCameraData")
            e = self.m_("EXPONENT", self.m_("DIVIDE", cam.outputs["View Distance"], -SIS[0]))
            em = self.n("ShaderNodeEmission"); em.inputs["Color"].default_value = lin(SIS[1])
            mx = self.n("ShaderNodeMixShader")
            self.b(self.m_("SUBTRACT", 1.0, e), mx.inputs[0]); self.b(s, mx.inputs[1]); self.b(em.outputs[0], mx.inputs[2])
            s = mx.outputs[0]
        self.b(s, self.out.inputs["Surface"])
        return self.m


def govde_malzeme(tur, d):
    R = d["renk"]
    A = Firca("Balik_" + tur)
    u, h = A.uv("balik")
    _, z = A.uv("boy")
    # countershading: belly -> side -> back
    col = A.karis(A.aralik(h, 0.18, 0.46), lin(R["karin"]), lin(R["yan"]))
    col = A.karis(A.aralik(h, 0.58, 0.8), col, lin(R["sirt"]))
    vz = A.vek(u, z)
    for p in d.get("desen", []):
        k = p[0]
        if k == "bar":                       # vertical bar: u centre, width, h range
            _, c, w, h0, h1, rk, g = p
            f = A.m_("MULTIPLY", A.bant(u, c, w, 0.01), A.aralik(h, h0, h0 + 0.05))
            f = A.m_("MULTIPLY", f, A.aralik(h, h1, h1 + 0.05, 1, 0))
        elif k == "serit":                   # horizontal stripe: h centre, width, u range
            _, c, w, u0, u1, rk, g = p
            f = A.m_("MULTIPLY", A.bant(h, c, w, 0.015), A.aralik(u, u0, u0 + 0.06))
            f = A.m_("MULTIPLY", f, A.aralik(u, u1 - 0.06, u1, 1, 0))
        elif k == "leke":                    # spot at (u, h) with radii
            _, cu, ch, ru, rh, rk, g = p
            du = A.m_("DIVIDE", A.m_("SUBTRACT", u, cu), ru)
            dh = A.m_("DIVIDE", A.m_("SUBTRACT", h, ch), rh)
            r_ = A.m_("SQRT", A.m_("ADD", A.m_("MULTIPLY", du, du), A.m_("MULTIPLY", dh, dh)))
            f = A.aralik(r_, 0.75, 1.0, 1, 0)
        elif k == "dalga":                   # wavy dark bars over the back (mackerel)
            _, frq, h0, h1, rk, g, esik = p
            s_ = A.m_("SINE", A.m_("ADD", A.m_("MULTIPLY", u, frq * TAU),
                                    A.m_("MULTIPLY", A.m_("SINE", A.m_("MULTIPLY", h, 9.0)), 1.6)))
            f = A.m_("MULTIPLY", A.aralik(s_, 0.35, 0.6), A.aralik(h, esik, esik + 0.05))
            f = A.m_("MULTIPLY", f, A.aralik(u, 0.06, 0.12))
            f = A.m_("MULTIPLY", f, A.aralik(u, 0.84, 0.88, 1, 0))
        elif k == "egik":                    # oblique stripes (bonito)
            _, frq, egim, h0, h1, rk, g = p
            s_ = A.m_("SINE", A.m_("MULTIPLY", A.m_("ADD", u, A.m_("MULTIPLY", h, egim * 0.12)), frq * TAU))
            f = A.m_("MULTIPLY", A.aralik(s_, 0.45, 0.7), A.aralik(h, h0, h0 + 0.05))
            f = A.m_("MULTIPLY", f, A.aralik(u, 0.08, 0.14))
            f = A.m_("MULTIPLY", f, A.aralik(u, 0.83, 0.87, 1, 0))
        elif k == "benek":                   # blotches from noise
            _, olc, esik, rk, g = p
            f = A.aralik(A.gurultu(vz, olc, 3.0), esik, esik + 0.05)
        elif k == "nokta":                   # dot row / field (voronoi cells)
            _, h0, h1, r_, rk, g = p
            dist = A.voronoi(vz, 1.0 / (r_ * 3.2))
            f = A.m_("MULTIPLY", A.aralik(dist, 0.28, 0.36, 1, 0), A.aralik(h, h0, h0 + 0.04))
            f = A.m_("MULTIPLY", f, A.aralik(h, h1, h1 + 0.04, 1, 0))
            f = A.m_("MULTIPLY", f, A.aralik(u, 0.2, 0.26))
            f = A.m_("MULTIPLY", f, A.aralik(u, 0.8, 0.84, 1, 0))
        else:
            continue
        col = A.karis(A.m_("MULTIPLY", f, g), col, lin(rk))
    # gill cover arc and mouth line: the body colour darkened, never black
    if d.get("solungac"):
        cu, cz, r_ = d["solungac"]
        du = A.m_("SUBTRACT", u, cu + r_ * 0.6)
        dz = A.m_("SUBTRACT", z, cz)
        rr = A.m_("SQRT", A.m_("ADD", A.m_("MULTIPLY", du, du), A.m_("MULTIPLY", A.m_("MULTIPLY", dz, dz), 0.55)))
        f = A.m_("MULTIPLY", A.bant(rr, r_, 0.009, 0.006), A.aralik(u, cu + r_ * 0.6, cu + r_ * 0.4, 1, 0))
        col = A.karis(A.m_("MULTIPLY", f, 0.55), col, A.karis(1.0, col, (0.45, 0.42, 0.48, 1), "MULTIPLY"))
    if d.get("agiz"):
        au, az = d["agiz"]
        f = A.m_("MULTIPLY", A.bant(z, az, 0.007, 0.004), A.aralik(u, au, au + 0.01))
        col = A.karis(A.m_("MULTIPLY", f, 0.8), col, A.karis(1.0, col, (0.35, 0.3, 0.33, 1), "MULTIPLY"))
    # faint scale shimmer, so silver sides are not plastic
    sh = A.aralik(A.voronoi(vz, 70.0), 0.0, 0.5, 0.94, 1.04)
    col = A.karis(1.0, col, A.vek(sh, sh, sh), "MULTIPLY")
    return A.bitir(A.boya(col, parilti=d.get("parilti", 0.0)))


def yuzgec_malzeme(tur, ana, kenar, saydam=0.0, benek=None):
    A = Firca("Yuzgec_" + tur)
    t, v = A.uv("yuzgec")
    col = A.karis(A.aralik(v, 0.55, 1.0), lin(ana), lin(kenar))
    isin = A.aralik(A.m_("SINE", A.m_("MULTIPLY", t, 64.0)), 0.55, 0.9)      # fin rays
    col = A.karis(A.m_("MULTIPLY", isin, 0.35), col, A.karis(1.0, col, (0.62, 0.6, 0.66, 1), "MULTIPLY"))
    if benek:
        vb = A.vek(A.m_("MULTIPLY", t, 3.0), v)
        f = A.aralik(A.gurultu(vb, 6.0, 2.0), 0.58, 0.63)
        col = A.karis(A.m_("MULTIPLY", f, 0.8), col, lin(benek))
    alfa = None
    if saydam:
        alfa = A.m_("SUBTRACT", 1.0, A.m_("MULTIPLY", A.aralik(v, 0.1, 1.0), saydam))
    return A.bitir(A.boya(col, kenar_guc=0.1), alfa)


def goz_malzeme(tur, iris):
    A = Firca("Goz_" + tur)
    x, y = A.uv("goz")
    r_ = A.m_("SQRT", A.m_("ADD", A.m_("MULTIPLY", x, x), A.m_("MULTIPLY", y, y)))
    col = A.karis(A.aralik(r_, 0.86, 0.95), lin(iris), koyu(iris, 0.45))           # iris, dark rim
    col = A.karis(A.aralik(r_, 0.5, 0.56, 1, 0), col, lin("#121418"))             # pupil
    gx, gy = A.m_("SUBTRACT", x, 0.22), A.m_("SUBTRACT", y, 0.28)
    gr = A.m_("SQRT", A.m_("ADD", A.m_("MULTIPLY", gx, gx), A.m_("MULTIPLY", gy, gy)))
    col = A.karis(A.aralik(gr, 0.13, 0.17, 1, 0), col, (1.0, 0.98, 0.94, 1))      # catch light
    em = A.n("ShaderNodeEmission"); A.b(col, em.inputs["Color"]); em.inputs["Strength"].default_value = PARLAK
    return A.bitir(em.outputs[0])


def duz(ad, renk):
    A = Firca(ad)
    return A.bitir(A.boya(lin(renk)))


# ---------------------------------------------------------------- geometry
class Parca:
    """Vertex/face soup with per-vertex attributes, turned into one mesh."""
    def __init__(self):
        self.v, self.f, self.mi, self.uv, self.uv2, self.grp = [], [], [], [], [], []

    def nokta(self, p, uv=(0, 0), uv2=(0, 0), grp=None):
        self.v.append(tuple(p)); self.uv.append(uv); self.uv2.append(uv2); self.grp.append(grp)
        return len(self.v) - 1

    def yuz(self, idx, mi=0):
        self.f.append(tuple(idx)); self.mi.append(mi)

    def mesh(self, ad, uvadlari, mats, smooth=True):
        me = bpy.data.meshes.new(ad)
        me.from_pydata(self.v, [], self.f)
        for p, m in zip(me.polygons, self.mi):
            p.material_index = m
            p.use_smooth = smooth
        for k, ad_ in enumerate(uvadlari):
            lay = me.uv_layers.new(name=ad_)
            src = self.uv if k == 0 else self.uv2
            for l in me.loops:
                lay.data[l.index].uv = src[l.vertex_index]
        for m in mats:
            me.materials.append(m)
        return me


def profil_fn(d):
    pr = d["profil"]
    def f(u):
        t, b, w = egri(pr, u)
        return t, b, max(w, 0.004)
    return f


def govde(d, P):
    """Lofted body rings; UV 'balik' = (u, h 0 belly..1 back), 'boy' = (u, z)."""
    f = profil_fn(d)
    NU, NA = 56, 28
    halka = []
    for i in range(NU + 1):
        u = 0.5 - 0.5 * math.cos(math.pi * i / NU)
        t, b, w = f(u)
        c, hh = (t + b) / 2, max((t - b) / 2, 0.004)
        ring = []
        for k in range(NA):
            a = TAU * k / NA
            x = w * math.cos(a) * (1 + 0.12 * math.sin(a))
            z = c + hh * math.sin(a)
            ring.append(P.nokta((x, u - 0.5, z), (u, (math.sin(a) + 1) / 2), (u, z)))
        halka.append(ring)
    for i in range(NU):
        for k in range(NA):
            P.yuz((halka[i][k], halka[i][(k + 1) % NA], halka[i + 1][(k + 1) % NA], halka[i + 1][k]))
    t, b, _ = f(1.0)
    burun = P.nokta((0, 0.505, (t + b) / 2), (1.0, 0.5), (1.0, (t + b) / 2))
    t0, b0, _ = f(0.0)
    kok = P.nokta((0, -0.5, (t0 + b0) / 2), (0.0, 0.5), (0.0, 0))
    for k in range(NA):
        P.yuz((halka[NU][k], halka[NU][(k + 1) % NA], burun))
        P.yuz((halka[0][(k + 1) % NA], halka[0][k], kok))
    return f


def sirt_yuzgeci(P, f, u0, u1, boylar, dikenli, alt=False, yatik=0.55, mi=0):
    """Dorsal (or anal) fin along the top (bottom) line, swept back; spiny part notched between rays."""
    N = 30
    taban, uc = [], []
    hn = [(i / (len(boylar) - 1), b) for i, b in enumerate(boylar)]
    for j in range(N + 1):
        t = j / N
        u = u0 + t * (u1 - u0)
        top, bot, w = f(u)
        zb = (bot + 0.004) if alt else (top - 0.004)
        hg = egri(hn, t)[0]
        if t < dikenli and dikenli > 0:
            n_ = max(3, int(9 * (u1 - u0) * dikenli / 0.3))
            hg *= 0.8 + 0.2 * abs(math.cos(math.pi * n_ * t / dikenli))
        s = -1 if alt else 1
        taban.append(P.nokta((0, u - 0.5, zb), (t, 0)))
        orta = P.nokta((0, u - 0.5 - yatik * hg * 0.5, zb + s * hg * 0.52), (t, 0.5))
        uc.append((orta, P.nokta((0, u - 0.5 - yatik * hg, zb + s * hg), (t, 1))))
    for j in range(N):
        P.yuz((taban[j], taban[j + 1], uc[j + 1][0], uc[j][0]), mi)
        P.yuz((uc[j][0], uc[j + 1][0], uc[j + 1][1], uc[j][1]), mi)


def kuyruk_yuzgeci(P, f, tip, L, H, mi=0):
    t0, b0, _ = f(0.0)
    hp = (t0 - b0) / 2 * 0.9
    sek = {
        "catal": [(0.0, hp), (.45 * L, .62 * H), (L, H), (.72 * L, .45 * H), (.42 * L, 0), (.72 * L, -.45 * H),
                  (L, -H), (.45 * L, -.62 * H), (0.0, -hp)],
        "hilal": [(0.0, hp), (.3 * L, .45 * H), (L, H), (.6 * L, .3 * H), (.45 * L, 0), (.6 * L, -.3 * H),
                  (L, -H), (.3 * L, -.45 * H), (0.0, -hp)],
        "yuvarlak": [(0.0, hp), (.4 * L, .82 * H), (.85 * L, .72 * H), (L, 0), (.85 * L, -.72 * H),
                     (.4 * L, -.82 * H), (0.0, -hp)],
        "kesik": [(0.0, hp), (.5 * L, .85 * H), (L, .95 * H), (.94 * L, 0), (L, -.95 * H), (.5 * L, -.85 * H),
                  (0.0, -hp)],
        "sivri": [(0.0, hp), (.55 * L, .55 * H), (L, 0), (.55 * L, -.55 * H), (0.0, -hp)],
    }[tip]
    cizgi = kapali_egri(sek, 44)
    merkez = P.nokta((0, -0.5 + 0.01, 0), (0.5, 0))
    orta, dis = [], []
    for j, (dd, zz) in enumerate(cizgi):
        t = j / (len(cizgi) - 1)
        orta.append(P.nokta((0, -0.5 + 0.01 - dd * 0.5, zz * 0.5), (t, 0.5)))
        dis.append(P.nokta((0, -0.5 + 0.01 - dd, zz), (t, 1.0)))
    for j in range(len(cizgi) - 1):
        P.yuz((merkez, orta[j + 1], orta[j]), mi)
        P.yuz((orta[j], orta[j + 1], dis[j + 1], dis[j]), mi)


def kanat_yuzgec(P, f, u, hrel, L, W, acik, sarkma, sekil, yan, grp, mi=0, yatay=False):
    """Pectoral / pelvic fin: a fan from its root, pointing back, opened from the body by `acik`."""
    top, bot, w = f(u)
    c, hh = (top + bot) / 2, (top - bot) / 2
    a_ = math.asin(max(-1, min(1, hrel * 2 - 1)))
    kok = Vector((yan * w * math.cos(a_) * 0.95, u - 0.5, c + hh * math.sin(a_)))
    yon = Vector((0, -1, 0))
    yon = Matrix.Rotation(math.radians(sarkma), 3, "X") @ yon        # droop: tip down
    yon = Matrix.Rotation(math.radians(yan * acik), 3, "Z") @ yon    # spread: tip away from the body
    dik = Vector((0, 0, 1)) if not yatay else Vector((yan, 0, 0))
    dik = (dik - yon * dik.dot(yon)).normalized()
    if sekil == "kanat":
        sek = [(0, .25), (.35, .9), (.8, 1.0), (1.0, .55), (.95, 0), (.75, -.6), (.35, -.7), (0, -.25)]
    elif sekil == "yuvarlak":
        sek = [(0, .4), (.45, .95), (.9, .7), (1.0, 0), (.9, -.7), (.45, -.95), (0, -.4)]
    else:
        sek = [(0, .45), (.5, .75), (1.0, .2), (.95, -.1), (.5, -.45), (0, -.35)]
    cizgi = kapali_egri(sek, 26)
    m_ = P.nokta(kok, (0.5, 0), grp=grp)
    orta, dis = [], []
    for j, (a, b) in enumerate(cizgi):
        t = j / (len(cizgi) - 1)
        p1 = kok + yon * (a * L * 0.5) + dik * (b * W * 0.5)
        p2 = kok + yon * (a * L) + dik * (b * W) + Vector((yan * 0.01 * a, 0, 0))
        orta.append(P.nokta(p1, (t, 0.5), grp=grp)); dis.append(P.nokta(p2, (t, 1.0), grp=grp))
    for j in range(len(cizgi) - 1):
        P.yuz((m_, orta[j + 1], orta[j]), mi)
        P.yuz((orta[j], orta[j + 1], dis[j + 1], dis[j]), mi)
    return kok, kok + yon * L


def finletler(P, f, u0, u1, n, mi=0):
    for k in range(n):
        u = u0 + (u1 - u0) * (k + 0.5) / n
        du = (u1 - u0) / n * 0.4
        for alt in (False, True):
            top, bot, _ = f(u)
            zb = bot + 0.003 if alt else top - 0.003
            s = -1 if alt else 1
            hg = 0.025 + 0.01 * (k / n)
            a = P.nokta((0, u - 0.5 + du, zb), (0, 0)); b = P.nokta((0, u - 0.5 - du, zb), (1, 0))
            c = P.nokta((0, u - 0.5 - du * 2.2, zb + s * hg), (0.5, 1))
            P.yuz((a, b, c), mi)


def koni(P, kok, uc, r0, r1, n=10, mi=1, yassi=1.0, grp=None):
    ax = (uc - kok).normalized()
    y1 = Vector((1, 0, 0)) if abs(ax.x) < 0.9 else Vector((0, 0, 1))
    y1 = (y1 - ax * y1.dot(ax)).normalized(); y2 = ax.cross(y1)
    halka = []
    for j, (p, r) in enumerate(((kok, r0), ((kok + uc) / 2, (r0 + r1) / 2 * 1.05), (uc, r1))):
        halka.append([P.nokta(p + (y1 * math.cos(TAU * k / n) * yassi + y2 * math.sin(TAU * k / n)) * r,
                              (k / n, j / 2), grp=grp) for k in range(n)])
    for j in range(2):
        for k in range(n):
            P.yuz((halka[j][k], halka[j][(k + 1) % n], halka[j + 1][(k + 1) % n], halka[j + 1][k]), mi)
    tep = P.nokta(uc + ax * r1, (0.5, 1), grp=grp)
    for k in range(n):
        P.yuz((halka[2][k], halka[2][(k + 1) % n], tep), mi)


def gozler(P, f, d):
    u, hrel, r = d["goz"]
    r *= 1.25
    top, bot, w = f(u)
    c, hh = (top + bot) / 2, (top - bot) / 2
    a_ = math.asin(max(-1, min(1, hrel * 2 - 1)))
    z = c + hh * math.sin(a_)
    x = w * math.cos(a_) * (1 + 0.12 * math.sin(a_)) * 0.78
    for yan in (1, -1):
        NA, NR = 14, 8
        rows = []
        for i in range(NR + 1):
            th = math.pi * i / NR
            row = []
            for k in range(NA):
                ph = TAU * k / NA
                lx, ly, lz = math.cos(th), math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph)
                p = (yan * (x + lx * r * 0.5), u - 0.5 + ly * r, z + lz * r)
                row.append(P.nokta(p, (ly * yan if yan > 0 else ly, lz)))
            rows.append(row)
        if yan < 0:
            for i in range(NR):
                for k in range(NA):
                    P.yuz((rows[i][k], rows[i + 1][k], rows[i + 1][(k + 1) % NA], rows[i][(k + 1) % NA]))
        else:
            for i in range(NR):
                for k in range(NA):
                    P.yuz((rows[i][k], rows[i][(k + 1) % NA], rows[i + 1][(k + 1) % NA], rows[i + 1][k]))


# ---------------------------------------------------------------- rig
def _ekleme(sc, ob):
    (sc.collection if sc else bpy.context.scene.collection).objects.link(ob)


def _eklem_y(L):
    return [0.5, 0.28, 0.1, -0.07, -0.22, -0.36, -0.5, -0.5 - L]


def _agirlik(y, ey):
    """Spine weights by position along the body: linear between bone midpoints, rigid head."""
    mids = [(ey[i] + ey[i + 1]) / 2 for i in range(len(ey) - 1)]
    if y >= mids[0]:
        return {0: 1.0}
    if y <= mids[-1]:
        return {len(mids) - 1: 1.0}
    for i in range(len(mids) - 1):
        if mids[i] >= y >= mids[i + 1]:
            t = (mids[i] - y) / (mids[i] - mids[i + 1])
            t = t * t * (3 - 2 * t)
            return {i: 1 - t, i + 1: t}
    return {0: 1.0}


def _iskelet(ad, ey, pektoral):
    arm_d = bpy.data.armatures.new(ad)
    arm = bpy.data.objects.new(ad, arm_d)
    _ekleme(None, arm)
    vl = bpy.context.view_layer
    for o in vl.objects:
        o.select_set(False)
    vl.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    onceki = None
    for i in range(len(ey) - 1):
        b = arm_d.edit_bones.new(f"K{i}")
        b.head, b.tail = (0, ey[i], 0), (0, ey[i + 1], 0)
        b.roll = 0.0
        if onceki:
            b.parent = onceki; b.use_connect = True
        onceki = b
    for ad_, (kok, uc), ebeveyn in pektoral:
        b = arm_d.edit_bones.new(ad_)
        b.head, b.tail = kok, uc
        b.parent = arm_d.edit_bones[ebeveyn]
    bpy.ops.object.mode_set(mode="OBJECT")
    return arm


def _eksen(bone, hedef):
    """Index of the bone-local axis that points closest to a world direction, with its sign."""
    m = bone.matrix_local.to_3x3()
    best = max(range(3), key=lambda k: abs(m.col[k].dot(hedef)))
    return best, (1 if m.col[best].dot(hedef) > 0 else -1)


def _bagla(ob, arm, gruplar):
    ob.parent = arm
    mod = ob.modifiers.new("Iskelet", "ARMATURE"); mod.object = arm
    for ad_ in {g for vg in gruplar for g in vg}:
        ob.vertex_groups.new(name=ad_)
    for i, vg in enumerate(gruplar):
        for g, w in vg.items():
            if w > 1e-4:
                ob.vertex_groups[g].add([i], w, "REPLACE")


def yap(tur, boy=None, ebeveyn=None, konum=(0, 0, 0), ad=None):
    """Build one rigged fish; returns the armature object (fish length = boy metres, snout +Y)."""
    if tur == "vatoz":
        return vatoz_yap(boy, ebeveyn, konum, ad)
    d = TURLER[tur]
    ad = ad or d["ad"]
    kL, kH = d["kuyruk"][1], d["kuyruk"][2]
    ey = _eklem_y(kL)
    R = d["renk"]
    m_gov = govde_malzeme(tur, d)
    m_yuz = yuzgec_malzeme(tur, R["yuzgec"], R["kenar"], d.get("saydam", 0.0))
    m_ser = duz(f"Sert_{tur}", R["sirt"] if not d.get("biyik") else "#F1E2C2")
    mats_y = [m_yuz, m_ser]
    if d.get("kanat"):
        k = d["kanat"]
        mats_y.append(yuzgec_malzeme(tur + "_kanat", k["yuzgec"], k["kenar"], 0.0, k["benek"]))
    # body
    P = Parca()
    f = govde(d, P)
    gov = bpy.data.objects.new(ad + "_govde", P.mesh(ad + "_govde", ["balik", "boy"], [m_gov]))
    gov_grp = [{f"K{i}": w for i, w in _agirlik(v[1], ey).items()} for v in P.v]
    # fins
    Y = Parca()
    for u0, u1, hs, sp in d.get("sirt", []):
        sirt_yuzgeci(Y, f, u0, u1, hs, sp)
    for u0, u1, hs, sp in d.get("anal", []):
        sirt_yuzgeci(Y, f, u0, u1, hs, sp, alt=True)
    kuyruk_yuzgeci(Y, f, d["kuyruk"][0], kL, kH)
    if d.get("finlet"):
        finletler(Y, f, *d["finlet"])
    pekt = []
    if d.get("gogus"):
        u, hr, L, W, ac, sa, sek = d["gogus"]
        mi = 2 if d.get("kanat") else 0
        for yan, s_ in ((1, "L"), (-1, "R")):
            kok, uc = kanat_yuzgec(Y, f, u, hr, L, W, ac, sa, sek, yan, f"Gogus.{s_}", mi)
            pekt.append((f"Gogus.{s_}", (tuple(kok), tuple(uc)), "K1"))
    if d.get("karin"):
        u, L = d["karin"]
        for yan in (1, -1):
            kanat_yuzgec(Y, f, u, 0.04, L, L * 0.45, 22, 55, "sivri", yan, None)
    if d.get("kilic"):
        t, b, _ = f(1.0)
        koni(Y, Vector((0, 0.49, (t + b) / 2)), Vector((0, 0.5 + d["kilic"], (t + b) / 2 - 0.01)), 0.018, 0.003,
             12, 1, 0.45)
    if d.get("biyik"):
        top, bot, w = f(0.975)
        for yan in (1, -1):
            koni(Y, Vector((yan * 0.012, 0.47, bot + 0.008)), Vector((yan * 0.02, 0.53, bot - 0.07)), 0.006, 0.002, 6, 1)
    if d.get("agiz_acik"):
        top, bot, w = f(0.96)
        koni(Y, Vector((0, 0.43, bot + 0.004)), Vector((0, 0.505, bot - 0.012)), 0.014, 0.004, 10, 1, 1.6)
    yuz = bpy.data.objects.new(ad + "_yuzgec", Y.mesh(ad + "_yuzgec", ["yuzgec"], mats_y))
    yuz_grp = []
    for v, g in zip(Y.v, Y.grp):
        yuz_grp.append({g: 1.0} if g else {f"K{i}": w for i, w in _agirlik(v[1], ey).items()})
    # eyes
    G = Parca()
    gozler(G, f, d)
    goz = bpy.data.objects.new(ad + "_goz", G.mesh(ad + "_goz", ["goz"], [goz_malzeme(tur, d["iris"])]))
    # rig
    arm = _iskelet(ad, ey, pekt)
    for ob, grp in ((gov, gov_grp), (yuz, yuz_grp), (goz, [{"K0": 1.0}] * len(G.v))):
        _ekleme(None, ob)
        _bagla(ob, arm, grp)
    sub = gov.modifiers.new("Yumusat", "SUBSURF"); sub.levels = 1; sub.render_levels = 1
    arm["tur"] = tur
    arm["kuyruk"] = kL
    s_ = (boy or d["boy"]) / (1 + kL)
    arm.scale = (s_, s_, s_)
    arm.location = konum
    if ebeveyn is not None:
        arm.parent = ebeveyn
    arm.show_in_front = True
    arm.hide_render = True
    return arm


def vatoz_yap(boy=None, ebeveyn=None, konum=(0, 0, 0), ad=None):
    """A ray: flat disc with eyes on top and a whip tail; wings ripple with a travelling wave."""
    d = VATOZ
    R = d["renk"]
    ad = ad or d["ad"]
    A = Firca("Balik_vatoz")
    x, y = A.uv("balik")
    vz = A.vek(x, y)
    col = A.karis(A.aralik(A.gurultu(vz, 10.0, 3.0), 0.56, 0.62), lin(R["ust"]), lin(R["benek"]))
    yan_ = A.aralik(A.voronoi(vz, 22.0), 0.2, 0.32, 1, 0)
    col = A.karis(A.m_("MULTIPLY", yan_, 0.35), col, lin("#C8B490"))
    m_ust = A.bitir(A.boya(col, parilti=0.1))
    m_alt = duz("Vatoz_alt", R["alt"])
    P = Parca()
    NR, NA = 18, 48
    def kenar(a):                       # rhombic disc outline, rounded, nose forward (+Y)
        c, s = math.cos(a), math.sin(a)
        r = 0.5 / (abs(c) ** 1.6 + abs(s) ** 1.6) ** (1 / 1.6)
        if s > 0:
            r *= 1.0 - 0.18 * s ** 4
        return r * c * 1.05, r * s * 0.95 + 0.02
    rows = []
    for i in range(NR + 1):
        q = i / NR
        row = []
        for k in range(NA):
            a = TAU * k / NA
            ex, ey_ = kenar(a)
            z = 0.06 * (1 - q * q) ** 1.5
            row.append((P.nokta((ex * q, ey_ * q, z), (ex * q, ey_ * q)),
                        P.nokta((ex * q, ey_ * q, -0.25 * z), (ex * q, ey_ * q))))
        rows.append(row)
    ust_c = P.nokta((0, 0.02, 0.06), (0, 0)); alt_c = P.nokta((0, 0.02, -0.015), (0, 0))
    for k in range(NA):
        P.yuz((ust_c, rows[1][k][0], rows[1][(k + 1) % NA][0]), 0)
        P.yuz((alt_c, rows[1][(k + 1) % NA][1], rows[1][k][1]), 1)
    for i in range(1, NR):
        for k in range(NA):
            k2 = (k + 1) % NA
            P.yuz((rows[i][k][0], rows[i + 1][k][0], rows[i + 1][k2][0], rows[i][k2][0]), 0)
            P.yuz((rows[i][k2][1], rows[i + 1][k2][1], rows[i + 1][k][1], rows[i][k][1]), 1)
    for k in range(NA):
        k2 = (k + 1) % NA
        P.yuz((rows[NR][k][0], rows[NR][k][1], rows[NR][k2][1], rows[NR][k2][0]), 0)
    koni(P, Vector((0, -0.42, 0.01)), Vector((0, -1.25, 0.0)), 0.035, 0.004, 8, 0)
    for yan in (1, -1):                 # eyes and spiracles on top
        koni(P, Vector((yan * 0.06, 0.2, 0.05)), Vector((yan * 0.065, 0.21, 0.075)), 0.016, 0.012, 8, 2)
    me = P.mesh(ad, ["balik"], [m_ust, m_alt, duz("Vatoz_goz", "#2A2620")])
    ob = bpy.data.objects.new(ad, me)
    _ekleme(None, ob)
    vg = ob.vertex_groups.new(name="Kanat")
    for i, v in enumerate(P.v):
        w = min(1.0, (abs(v[0]) / 0.5) ** 1.4) if v[1] > -0.45 else min(1.0, (-0.45 - v[1]) * 1.2)
        vg.add([i], w, "REPLACE")
    wv = ob.modifiers.new("Kanat", "WAVE")
    wv.use_x, wv.use_y, wv.use_normal = False, True, False
    wv.use_cyclic = True
    wv.vertex_group = "Kanat"
    wv.height, wv.width, wv.narrowness, wv.speed = 0.07, 0.55, 0.9, -0.012
    wv.start_position_y = 2.0
    s_ = (boy or d["boy"])
    ob.scale = (s_, s_, s_)
    ob.location = konum
    ob["tur"] = "vatoz"
    if ebeveyn is not None:
        ob.parent = ebeveyn
    return ob


# ---------------------------------------------------------------- animation
HALLER = ("yuz", "hizli", "dur", "cirpin", "asili")


def canlandir(arm, hal="yuz", f0=1, f1=120, faz=0.0, hiz=1.0):
    """Key the spine wave (and pectoral sculling) every frame from f0 to f1.
    hal: yuz (cruise), hizli (dart), dur (hover), cirpin (flapping out of water), asili (on a line)."""
    tur = arm.get("tur")
    if tur == "vatoz" or tur is None:
        wv = arm.modifiers.get("Kanat")
        if wv:
            wv.speed = {"hizli": -0.02, "dur": -0.006}.get(hal, -0.012)
        return
    d = TURLER[tur]
    env, lam, A0 = MODLAR[d["mod"]]
    T = d["T"] / hiz
    kL = arm["kuyruk"]
    ey = _eklem_y(kL)
    s_j = [0.5 - y for y in ey]                       # head 0 .. tail root 1 .. fin tip 1+kL
    spine = [arm.pose.bones[f"K{i}"] for i in range(len(ey) - 1)]
    ax, _ = _eksen(arm.data.bones["K0"], Vector((0, 0, 1)))
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"
    pek = []
    for s_ in ("L", "R"):
        if f"Gogus.{s_}" in arm.pose.bones:
            b = arm.data.bones[f"Gogus.{s_}"]
            k, sg = _eksen(b, Vector((0, 0, 1)))
            # sign so that a positive angle opens the fin away from the body
            m = b.matrix_local.to_3x3()
            uc = m @ (Matrix.Rotation(0.2, 3, "XYZ"[k]) @ Vector((0, 1, 0)))
            sg = 1 if abs(uc.x) > abs(m.col[1].x) else -1
            pek.append((arm.pose.bones[f"Gogus.{s_}"], k, sg))
    genlik = {"yuz": 1.0, "hizli": 1.35, "dur": 0.22, "cirpin": 1.0, "asili": 0.25}[hal]
    periyot = {"yuz": T, "hizli": T * 0.55, "dur": T * 1.7, "cirpin": max(8.0, T * 0.45), "asili": T * 1.6}[hal]
    for fr in range(f0, f1 + 1):
        t = (fr - f0) / periyot + faz
        if hal in ("cirpin", "asili"):
            # standing C-bend: every joint bends the same way, alternating sides
            if hal == "cirpin":
                g = math.sin(TAU * t) * (0.75 + 0.25 * math.sin(TAU * t * 0.37))
                bukum = 0.32 * g
            else:
                kasil = max(0.0, math.sin(TAU * t * 0.41)) ** 6             # a flick every few beats
                bukum = 0.05 * math.sin(TAU * t) + 0.25 * kasil * math.sin(TAU * t * 3)
            acilar = [0.0] + [bukum * (0.6 + 0.4 * i / len(spine)) for i in range(1, len(spine))]
        else:
            def x(s):
                return A0 * genlik * env(min(s, 1.0) + max(0.0, s - 1.0) * 0.5) * math.sin(TAU * (t - s / lam))
            teta = [math.atan2(x(s_j[i + 1]) - x(s_j[i]), s_j[i + 1] - s_j[i]) for i in range(len(spine))]
            acilar = [teta[0]] + [teta[i] - teta[i - 1] for i in range(1, len(spine))]
        for pb, a in zip(spine, acilar):
            r = [0.0, 0.0, 0.0]; r[ax] = a
            pb.rotation_euler = r
            pb.keyframe_insert("rotation_euler", index=ax, frame=fr)
        if hal == "dur":
            ac, gp = 0.55, 0.4
        elif hal == "hizli":
            ac, gp = -0.15, 0.03
        elif hal == "cirpin":
            ac, gp = 0.6, 0.5
        else:
            ac, gp = 0.15, 0.12
        for j, (pb, k, sg) in enumerate(pek):
            a = sg * (ac + gp * math.sin(TAU * t * (1.4 if hal == "dur" else 1.0) + j * 0.4))
            r = [0.0, 0.0, 0.0]; r[k] = a
            pb.rotation_euler = r
            pb.keyframe_insert("rotation_euler", index=k, frame=fr)


# ---------------------------------------------------------------- standalone: plate, motion sheet, blend
def _sahne(gen, oran, kag=1.0):
    sc = bpy.context.scene
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    r = sc.render
    r.engine = "BLENDER_EEVEE"
    r.resolution_x, r.resolution_y, r.resolution_percentage = gen, int(gen * oran), 100
    ee = sc.eevee
    ee.taa_render_samples = 48
    for ad_, d_ in (("use_raytracing", True), ("use_shadows", True)):
        if hasattr(ee, ad_):
            setattr(ee, ad_, d_)
    sc.view_settings.view_transform = "Khronos PBR Neutral"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = -0.35
    w = bpy.data.worlds.new("Dunya"); sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = lin("#EFE6D3")
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    bpy.ops.object.light_add(type="SUN")
    gun = bpy.context.active_object
    gun.data.energy = 5.2; gun.data.color = lin("#FFEACB")[:3]; gun.data.angle = math.radians(3)
    gun.rotation_euler = Vector((-0.4, -0.6, 0.7)).normalized().to_track_quat("Z", "Y").to_euler()
    return sc


def _kagit(z, boyut, renk=("#F2EADA", "#EBE1CD")):
    m = bpy.data.materials.new("Kagit"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    mx.inputs[6].default_value, mx.inputs[7].default_value = lin(renk[0]), lin(renk[1])
    nt.links.new(nz.outputs["Fac"], mx.inputs[0])
    sd = nt.nodes.new("ShaderNodeBsdfDiffuse"); sd.inputs["Color"].default_value = (1, 1, 1, 1)
    s2 = nt.nodes.new("ShaderNodeShaderToRGB"); nt.links.new(sd.outputs[0], s2.inputs[0])
    bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(s2.outputs[0], bw.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")          # only cast shadows darken it, softly and lilac
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.12 / OLCEK, 0.3 / OLCEK
    nt.links.new(bw.outputs[0], mr.inputs["Value"])
    gm = nt.nodes.new("ShaderNodeMix"); gm.data_type = "RGBA"
    nt.links.new(mr.outputs[0], gm.inputs[0])
    gm2 = nt.nodes.new("ShaderNodeMix"); gm2.data_type = "RGBA"; gm2.blend_type = "MULTIPLY"
    gm2.inputs[0].default_value = 1.0; gm2.inputs[7].default_value = (0.82, 0.79, 0.9, 1)
    nt.links.new(mx.outputs[2], gm2.inputs[6])
    nt.links.new(gm2.outputs[2], gm.inputs[6]); nt.links.new(mx.outputs[2], gm.inputs[7])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = PARLAK
    nt.links.new(gm.outputs[2], em.inputs[0])
    o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], o.inputs[0])
    bpy.ops.mesh.primitive_plane_add(size=boyut, location=(0, 0, z))
    p = bpy.context.active_object; p.data.materials.append(m)
    return p


def _yazi(metin, konum, boy, renk="#3A3530"):
    cu = bpy.data.curves.new("Yazi", "FONT"); cu.body = metin
    cu.align_x = "CENTER"; cu.size = boy
    ob = bpy.data.objects.new("Yazi", cu); _ekleme(None, ob)
    ob.location = konum
    m = bpy.data.materials.new("Murekkep"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = lin(renk); em.inputs[1].default_value = 1.0
    o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], o.inputs[0])
    cu.materials.append(m)
    return ob


def _yandan_kamera(merkez, yuk, oran, uzak=20.0):
    cd = bpy.data.cameras.new("Kamera"); cd.type = "ORTHO"; cd.ortho_scale = yuk / oran if oran > 1 else yuk
    cam = bpy.data.objects.new("Kamera", cd); _ekleme(None, cam)
    bpy.context.scene.camera = cam
    return cam, cd


def levha(cikti, gen=1600):
    """A naturalist's plate: every species side by side on paper, named, in a mid-swim pose."""
    sc = _sahne(gen, 1.0)
    kol, sat = 3, 5
    hucre_x, hucre_y = 2.35, 1.5
    for i, tur in enumerate(SIRA):
        c, r_ = i % kol, i // kol
        if i == 12:
            c = 1
        x = (c - 1) * hucre_x
        z = (sat / 2 - 0.5 - r_) * hucre_y
        if tur == "vatoz":
            ob = yap(tur, 0.95, konum=(x - 0.2, 0, z + 0.25))
            ob.rotation_euler = (math.radians(58), 0, 0)
            canlandir(ob, "yuz", 1, 1)
            ad = VATOZ["ad"]
        else:
            uz = {"muren": 2.0, "kilic": 1.55}.get(tur, 1.75)
            arm = yap(tur, uz, konum=(x, 0, z + 0.1))
            arm.rotation_euler = (0, 0, math.radians(-90))          # snout to the right, left side to camera
            canlandir(arm, "yuz", 1, 1, faz=0.15 + 0.07 * i)
            ad = TURLER[tur]["ad"]
        y = _yazi(ad, (x + (0.9 if tur == "vatoz" else 0), -0.6, z - (0.0 if tur == "vatoz" else 0.52)), 0.15)
        y.rotation_euler = (math.radians(90), 0, 0)
    pk = _kagit(0, 30); pk.rotation_euler = (math.radians(90), 0, 0); pk.location = (0, 1.2, 0)
    cam, cd = _yandan_kamera(None, 0, 1)
    cd.ortho_scale = kol * hucre_x * 1.06
    cam.location = (0, -20, 0); cam.rotation_euler = (math.radians(90), 0, 0)
    sc.frame_set(1)
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = os.path.abspath(cikti)
    bpy.ops.render.render(write_still=True)


def hareket(tur, hal, cikti, gen=1600, kare=8):
    """Motion check: the same fish from above at `kare` moments of one stroke, in one image."""
    sc = _sahne(gen, 0.62)
    d = TURLER.get(tur, VATOZ)
    T = d["T"]
    per = {"yuz": T, "hizli": T * 0.55, "dur": T * 1.7, "cirpin": max(8.0, T * 0.45), "asili": T * 1.6}[hal]
    kolon = 4
    for j in range(kare):
        c, r_ = j % kolon, j // kolon
        x, y = (c - 1.5) * 1.3, (0.5 - r_) * 1.55
        arm = yap(tur, 1.0, konum=(x, y, 0), ad=f"{d['ad']}_{j}")
        if tur != "vatoz":
            canlandir(arm, hal, 1, 1, faz=j / kare)
        yz = _yazi(f"{j + 1}/{kare}", (x, y - 0.75, 0), 0.09)
    _kagit(-0.25, 30)
    cd = bpy.data.cameras.new("Kamera"); cd.type = "ORTHO"; cd.ortho_scale = 5.6
    cam = bpy.data.objects.new("Kamera", cd); _ekleme(None, cam); sc.camera = cam
    cam.location = (0, 0, 20); cam.rotation_euler = (0, 0, 0)
    sc.frame_set(1)
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = os.path.abspath(cikti)
    bpy.ops.render.render(write_still=True)


GOSTER = {"sardalya": .55, "uskumru": .8, "barbun": .6, "cipura": .75, "mercan": .75, "levrek": 1.0,
          "lufer": 1.0, "kirlangic": .8, "palamut": 1.2, "orfoz": 1.3, "muren": 1.6, "kilic": 2.0, "vatoz": 1.0}


def halka(F=96):
    """Every species swims one seamless lap of a ring over shallow sand in F frames."""
    sc = _sahne(1280, 0.5625)
    sc.frame_start, sc.frame_end = 1, F
    sc.render.fps = 24
    R = 3.0
    for i, tur in enumerate(SIRA):
        a0 = TAU * i / len(SIRA)
        ob = yap(tur, GOSTER[tur])
        yuk = 0.35 + 0.25 * ((i * 7) % 5) / 4
        for fr in range(1, F + 1):
            a = a0 + TAU * (fr - 1) / F
            ob.location = (R * math.cos(a), R * math.sin(a), yuk + 0.04 * math.sin(TAU * (fr - 1) / F * 2 + i))
            ob.rotation_euler = (0, 0, a)
            ob.keyframe_insert("location", frame=fr); ob.keyframe_insert("rotation_euler", frame=fr)
        if tur != "vatoz":
            T = TURLER[tur]["T"]
            n = max(1, round(F / T))
            canlandir(ob, "yuz", 1, F, faz=i * 0.13, hiz=n * T / F)
    _kagit(0.0, 40, ("#E9D7AE", "#DCC593"))
    cd = bpy.data.cameras.new("Kamera"); cd.lens = 32
    cam = bpy.data.objects.new("Kamera", cd); _ekleme(None, cam); sc.camera = cam
    cam.location = (0, -7.2, 6.4)
    cam.rotation_euler = (Vector((0, -0.3, 0.3)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    return sc


def kaydet(cikti):
    halka()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(cikti))


def video(cikti, gen=960):
    sc = halka()
    r = sc.render
    r.resolution_x, r.resolution_y = gen, int(gen * 0.5625) // 2 * 2
    sc.eevee.taa_render_samples = 24
    im = r.image_settings
    if hasattr(im, "media_type"):
        im.media_type = "VIDEO"
    im.file_format = "FFMPEG"
    r.ffmpeg.format = "MPEG4"; r.ffmpeg.codec = "H264"; r.ffmpeg.constant_rate_factor = "HIGH"
    r.filepath = os.path.abspath(cikti)
    bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    A_ = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["levha", "levha.png"]
    if A_[0] == "levha":
        levha(A_[1], int(A_[2]) if len(A_) > 2 else 1600)
    elif A_[0] == "hareket":
        hareket(A_[1], A_[2], A_[3], int(A_[4]) if len(A_) > 4 else 1600)
    elif A_[0] == "kaydet":
        kaydet(A_[1])
    elif A_[0] == "video":
        video(A_[1], int(A_[2]) if len(A_) > 2 else 960)
    print("BITTI", A_[0])
