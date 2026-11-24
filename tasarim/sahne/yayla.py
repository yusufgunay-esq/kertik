"""Kertik sahnesi: Yayla Yolu. Mürekkep ve suluboya, dikey tomar (Blender 5.3, EEVEE + Freestyle).

Fikir: seans bir yolculuktur. Yolcu en alttaki taş kemer köprüden çıkar, sisin
içinden geçip yukarıdaki yayla evine varır. Tomar tek bir boyalı resimdir; yolcu,
sis bantları, şelale ve kuşlar uygulamada üstüne canlı katman olarak çizilir.

Görüntü kuramı: her yüzey ışıkla değil mürekkep yoğunluğuyla boyanır. Işık yalnız
"nereye ne kadar mürekkep düşer" sorusunu yanıtlar (gölge = koyu yıkama). Sis
bantları dağların eteğini kâğıda eritir; uzak dağlar soluk mavi-griye çekilir.
Çizgiler Freestyle ile fırça kalemi gibi çekilir ve sisin içinde kaybolur.

Kullanım:
  blender -b --factory-startup --python yayla.py -- resim <cikti.png> [olcek]
  blender -b --factory-startup --python yayla.py -- yol <cikti.json> [olcek]
  blender -b --factory-startup --python yayla.py -- kaydet <dosya.blend>
"""
import bpy
import bmesh
import json
import math
import os
import random
import sys
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

KOK = os.path.dirname(os.path.abspath(__file__))
GEN = 150.0                 # tomarın genişliği (m)
ORAN = 3.4                  # boy / en
EN, BOY = 1200, int(1200 * ORAN)
EGIM = math.radians(12.0)   # kamera aşağı bakış açısı (ortografik)
TAU = math.tau

PALET = dict(
    kagit="#F4EEE1",
    murekkep="#221D1A",
    yikama="#7E8780",      # yeşilimsi gri yıkama (yakın yamaç)
    uzak="#A4AEB8",        # uzak dağların mavi-grisi
    igne="#33402F",        # ladin yıkaması
    tas="#9C968A",
    aksan="#B8382A",       # tek bilinçli aksan: yolcu ve mühür (resme girmez)
    asi="#C2A277",         # aşı boyası: ışık alan yamaç
    civit="#7487A0",       # çivit: gölge yamaç
)

# Sis bantları: (merkez yükseklik, kalınlık, başladığı derinlik, güç)
SIS = [(30.0, 11.0, 72.0, 1.0), (96.0, 15.0, 150.0, 1.0), (176.0, 16.0, 268.0, 0.95), (226.0, 20.0, 440.0, 0.95), (268.0, 26.0, 500.0, 0.9)]
UZAK = (400.0, 680.0, 0.72)

# Yol: (x, y) denetim noktaları; z araziden okunur
YOL = [(-42, 4), (-26, 7), (-8, 12.5), (21, 12.5), (28, 22), (8, 40), (34, 58), (6, 78), (36, 100), (10, 124),
       (32, 146), (8, 170), (30, 195), (4, 220), (26, 246), (0, 272), (22, 300), (8, 328), (20, 352), (16, 372), (18, 382)]
NEHIR = [(-44, 150), (-36, 118), (-28, 88), (-16, 54), (-2, 30), (8, 12.5), (16, -6), (24, -40)]


def hx(c, a=1.0):
    c = c.lstrip("#")
    s = [int(c[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in s]
    return (*lin, a)


def ss(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


# ================================================================ düğüm yardımcıları
class Agac:
    def __init__(self, nt):
        self.nt, self.L = nt, nt.links

    def n(self, tip, **kw):
        d = self.nt.nodes.new(tip)
        for k, v in kw.items():
            setattr(d, k, v)
        return d

    def bag(self, a, b):
        self.L.new(a, b)

    def gir(self, dugum, ad, v):
        if isinstance(v, (int, float, tuple, list)):
            dugum.inputs[ad].default_value = v
        else:
            self.L.new(v, dugum.inputs[ad])

    def m(self, op, a, b=None, c=None, clamp=False):
        d = self.nt.nodes.new("ShaderNodeMath")
        d.operation = op
        d.use_clamp = clamp
        for i, v in enumerate((a, b, c)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                d.inputs[i].default_value = v
            else:
                self.L.new(v, d.inputs[i])
        return d.outputs[0]

    def karis(self, f, a, b):
        d = self.nt.nodes.new("ShaderNodeMix")
        d.data_type = "RGBA"
        if isinstance(f, (int, float)):
            d.inputs[0].default_value = f
        else:
            self.L.new(f, d.inputs[0])
        for sok, v in ((6, a), (7, b)):
            if isinstance(v, tuple):
                d.inputs[sok].default_value = v
            else:
                self.L.new(v, d.inputs[sok])
        return d.outputs[2]

    def aralik(self, v, a, b, c=0.0, d=1.0, tip="SMOOTHSTEP"):
        r = self.nt.nodes.new("ShaderNodeMapRange")
        r.interpolation_type = tip
        r.clamp = True
        self.gir(r, "Value", v)
        r.inputs["From Min"].default_value = a
        r.inputs["From Max"].default_value = b
        r.inputs["To Min"].default_value = c
        r.inputs["To Max"].default_value = d
        return r.outputs[0]


def yeni_malzeme(ad):
    m = bpy.data.materials.new(ad)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    return m, Agac(m.node_tree)


# ================================================================ sis (Python ve gölgelendiricide aynı formül)
def sis_py(x, y, z):
    f = 0.0
    for k, (zc, w, ymin, g) in enumerate(SIS):
        warp = w * 0.8 * (0.6 * math.sin(x / 23.0 + y / 31.0 + k) + 0.4 * math.sin(x / 9.7 - y / 13.0 + 2 * k))
        b = (1 - ss(0.0, 1.0, (z - zc + warp) / w)) * ss(ymin - 20, ymin + 20, y) * g
        f = max(f, b)
    uz = UZAK[2] * ss(UZAK[0], UZAK[1], y)
    return (1 - f) * (1 - uz)


def sis_dugum(A):
    """Görünürlük (0 sis, 1 açık) ve uzaklık (0..1) çıkışları."""
    geo = A.n("ShaderNodeNewGeometry")
    sep = A.n("ShaderNodeSeparateXYZ")
    A.bag(geo.outputs["Position"], sep.inputs[0])
    x, y, z = sep.outputs[0], sep.outputs[1], sep.outputs[2]
    f = None
    for k, (zc, w, ymin, g) in enumerate(SIS):
        s1 = A.m("SINE", A.m("ADD", A.m("ADD", A.m("DIVIDE", x, 23.0), A.m("DIVIDE", y, 31.0)), float(k)))
        s2 = A.m("SINE", A.m("ADD", A.m("SUBTRACT", A.m("DIVIDE", x, 9.7), A.m("DIVIDE", y, 13.0)), 2.0 * k))
        warp = A.m("MULTIPLY", A.m("ADD", A.m("MULTIPLY", s1, 0.6), A.m("MULTIPLY", s2, 0.4)), w * 0.8)
        t = A.m("DIVIDE", A.m("ADD", A.m("SUBTRACT", z, zc), warp), w)
        b = A.m("SUBTRACT", 1.0, A.aralik(t, 0.0, 1.0))
        b = A.m("MULTIPLY", A.m("MULTIPLY", b, A.aralik(y, ymin - 20, ymin + 20)), g)
        f = b if f is None else A.m("MAXIMUM", f, b)
    uz = A.aralik(y, UZAK[0], UZAK[1])
    vis = A.m("MULTIPLY", A.m("SUBTRACT", 1.0, f), A.m("SUBTRACT", 1.0, A.m("MULTIPLY", uz, UZAK[2])))
    return vis, uz, geo


# ================================================================ mürekkep gölgelendirici
def murekkep(ad, ton=0.8, taban=0.16, doku=0.6, yikama=None, cizik=(0.45, 0.45, 0.05), olcek=1.0,
             esik=(0.18, 0.72), yogun_fn=None, renkli=0.0):
    """Işık mürekkep yoğunluğunu belirler; yoğunluk kâğıt ile pigment arasında karışır."""
    m, A = yeni_malzeme(ad)
    dif = A.n("ShaderNodeBsdfDiffuse")
    dif.inputs["Color"].default_value = (1, 1, 1, 1)
    s2r = A.n("ShaderNodeShaderToRGB")
    A.bag(dif.outputs[0], s2r.inputs[0])
    bw = A.n("ShaderNodeRGBToBW")
    A.bag(s2r.outputs["Color"], bw.inputs[0])
    golge = A.aralik(bw.outputs[0], esik[0], esik[1], 1.0, 0.0)
    vis, uz, geo = sis_dugum(A)
    # fırça izi: uzatılmış gürültü (dikey çizikler)
    mp = A.n("ShaderNodeMapping")
    A.bag(geo.outputs["Position"], mp.inputs["Vector"])
    mp.inputs["Scale"].default_value = cizik
    nz = A.n("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = olcek
    nz.inputs["Detail"].default_value = 5.0
    nz.inputs["Roughness"].default_value = 0.65
    A.bag(mp.outputs[0], nz.inputs["Vector"])
    T = A.aralik(nz.outputs["Fac"], 0.32, 0.68)
    ince = A.n("ShaderNodeTexNoise")
    ince.inputs["Scale"].default_value = 9.0 * olcek
    ince.inputs["Detail"].default_value = 3.0
    A.bag(geo.outputs["Position"], ince.inputs["Vector"])
    T = A.m("MULTIPLY", T, A.aralik(ince.outputs["Fac"], 0.3, 0.7, 0.7, 1.15))
    tonu = ton if yogun_fn is None else yogun_fn(A, geo)
    D = A.m("MULTIPLY", tonu, A.m("ADD", taban, A.m("MULTIPLY", golge, 1.0 - taban)))
    D = A.m("MULTIPLY", D, A.m("ADD", 1.0 - doku, A.m("MULTIPLY", T, doku * 1.6)), clamp=True)
    yk = hx(yikama or PALET["yikama"])
    if renkli > 0:
        yk = A.karis(golge, hx(PALET["asi"]), hx(PALET["civit"]))
    pig = A.karis(A.aralik(D, 0.42 if renkli == 0 else 0.5, 0.92), yk, hx(PALET["murekkep"]))
    pig = A.karis(A.m("MULTIPLY", uz, 0.85), pig, hx(PALET["uzak"]))
    kat = A.m("MULTIPLY", A.m("MULTIPLY", D, vis), 1.3, clamp=True)
    if renkli > 0:
        # renk, yoğunluk az olsa da kâğıda biraz daha çıkar
        kat = A.m("MAXIMUM", kat, A.m("MULTIPLY", A.m("MULTIPLY", vis, A.m("SUBTRACT", 1.0, uz)), renkli * 0.22))
    renk = A.karis(kat, hx(PALET["kagit"]), pig)
    em = A.n("ShaderNodeEmission")
    A.bag(renk, em.inputs["Color"])
    em.inputs["Strength"].default_value = 1.0
    o = A.n("ShaderNodeOutputMaterial")
    A.bag(em.outputs[0], o.inputs["Surface"])
    aov = A.n("ShaderNodeOutputAOV")
    aov.aov_name = "gorunur"
    A.bag(vis, aov.inputs["Value"])
    return m


def kagit_mat(ad, cizgi=0.0, cizgi_yon="y", sik=0.9):
    """Kâğıt (su, şelale, patika): boş bırakılan yer; isteğe bağlı ince akış çizgileri."""
    m, A = yeni_malzeme(ad)
    vis, uz, geo = sis_dugum(A)
    renk = hx(PALET["kagit"])
    if cizgi > 0:
        sep = A.n("ShaderNodeSeparateXYZ")
        A.bag(geo.outputs["Position"], sep.inputs[0])
        w = A.n("ShaderNodeTexWave")
        w.wave_type = "BANDS"
        w.bands_direction = "Y" if cizgi_yon == "y" else "Z"
        w.inputs["Scale"].default_value = sik
        w.inputs["Distortion"].default_value = 6.0
        w.inputs["Detail"].default_value = 2.0
        A.bag(geo.outputs["Position"], w.inputs["Vector"])
        nz = A.n("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 0.35
        A.bag(geo.outputs["Position"], nz.inputs["Vector"])
        hat = A.m("MULTIPLY", A.aralik(w.outputs["Color"] if False else w.outputs[1], 0.9, 0.99), A.aralik(nz.outputs["Fac"], 0.5, 0.62))
        hat = A.m("MULTIPLY", A.m("MULTIPLY", hat, cizgi), vis)
        renk = A.karis(hat, hx(PALET["kagit"]), hx(PALET["murekkep"]))
    em = A.n("ShaderNodeEmission")
    if isinstance(renk, tuple):
        em.inputs["Color"].default_value = renk
    else:
        A.bag(renk, em.inputs["Color"])
    o = A.n("ShaderNodeOutputMaterial")
    A.bag(em.outputs[0], o.inputs["Surface"])
    aov = A.n("ShaderNodeOutputAOV")
    aov.aov_name = "gorunur"
    A.bag(vis, aov.inputs["Value"])
    return m


# ================================================================ mesh yardımcıları
KOL = {}


def koleksiyon(ad):
    if ad not in KOL:
        c = bpy.data.collections.new(ad)
        bpy.context.scene.collection.children.link(c)
        KOL[ad] = c
    return KOL[ad]


def nesne(ad, me, mat=None, ebeveyn=None, kol="cizgi"):
    o = bpy.data.objects.new(ad, me)
    koleksiyon(kol).objects.link(o)
    if mat:
        o.data.materials.append(mat)
    if ebeveyn:
        o.parent = ebeveyn
    return o


def kutu(ad, boyut, konum, mat, ebeveyn=None, don=(0, 0, 0), kol="cizgi"):
    me = bpy.data.meshes.new(ad)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * boyut[0], v.co.y * boyut[1], v.co.z * boyut[2]))
    bm.to_mesh(me)
    bm.free()
    o = nesne(ad, me, mat, ebeveyn, kol)
    o.location = konum
    o.rotation_euler = don
    return o


def prizma(ad, profil, uzunluk, mat, ebeveyn=None, kol="cizgi"):
    """XZ profilini y boyunca 0..uzunluk uzatır."""
    me = bpy.data.meshes.new(ad)
    n = len(profil)
    v = [(x, 0.0, z) for x, z in profil] + [(x, uzunluk, z) for x, z in profil]
    f = [list(range(n))[::-1], list(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        f.append([i, j, n + j, n + i])
    me.from_pydata(v, [], f)
    me.validate()
    me.update()
    return nesne(ad, me, mat, ebeveyn, kol)


# ================================================================ arazi
def sirtli(x, y, okt=6):
    s, a, w = 0.0, 0.55, 1.0
    q = Vector((x, y, 0.37))
    for _ in range(okt):
        n = 1.0 - abs(noise.noise(q, noise_basis="PERLIN_ORIGINAL"))
        n = n * n * w
        w = max(0.0, min(1.0, n * 2.0))
        s += n * a
        a *= 0.5
        q = q * 2.03
    return s


KITLELER = [  # yan kütleler ve uzak doruklar: (x, y, yarıçap, yükseklik, üs)
    (-78, 62, 38, 92, 0.9), (-86, 162, 50, 178, 0.75), (-74, 272, 44, 255, 0.85), (-100, 385, 56, 330, 0.85),
    (86, 104, 44, 132, 0.85), (98, 218, 50, 212, 0.8), (84, 322, 44, 282, 0.85), (126, 430, 58, 268, 0.95),
    (-42, 565, 112, 316, 1.15), (48, 602, 122, 330, 1.1), (132, 545, 82, 288, 1.1), (-128, 522, 80, 292, 1.1),
]
YAYLA_M = (10.0, 395.0, 62.0, 36.0, 241.0)   # yayla düzlüğü: merkez, yarı genişlikler, yükseklik


def taban(y):
    return 150.0 * ss(18.0, 365.0, y) + 70.0 * ss(430.0, 640.0, y)


def sirt_x(y):
    return 12.0 + 14.0 * math.sin(y / 55.0)


def sirt(x, y):
    """Ortadaki omurga: dereden yaylaya yükselen, kameraya bakan sırt."""
    if y < 14 or y > 400:
        return -1e9
    zc = 8.0 + 233.0 * ss(20.0, 382.0, y) ** 0.9
    w = 30.0 + 16.0 * ss(20.0, 300.0, y)
    d = abs(x - sirt_x(y)) / w
    if d >= 1.0:
        return -1e9
    tb = taban(y)
    uc = ss(14.0, 30.0, y)
    return tb + (zc - tb) * (1 - d * d) ** 1.2 * uc


def yayla_z(x, y):
    cx, cy, ax, ay, h = YAYLA_M
    d = max(abs(x - cx) / ax, abs(y - cy) / ay) * 0.6 + math.hypot((x - cx) / ax, (y - cy) / ay) * 0.4
    if d > 1.9:
        return -1e9
    return taban(y) + (h - taban(y)) * (1 - ss(1.0, 1.9, d))


def smax(a, b, k=14.0):
    hb = max(0.0, min(1.0, 0.5 + 0.5 * (b - a) / k))
    return a * (1 - hb) + b * hb + k * hb * (1 - hb)


def nokta_seg_uzaklik(px, py, pts):
    en = 1e9
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2)) if L2 > 0 else 0.0
        qx, qy = ax + t * dx - px, ay + t * dy - py
        en = min(en, qx * qx + qy * qy)
    return math.sqrt(en)


def ham_yukseklik(x, y):
    z = taban(y)
    k = -1e9
    for cx, cy, r, h, us in KITLELER:
        d = math.hypot((x - cx) / r, (y - cy) / (r * 0.8))
        if d < 1.0:
            k = max(k, h * (1.0 - d * d) ** us)
    z = smax(z, k, 16.0) if k > -1e8 else z
    s = sirt(x, y)
    if s > -1e8:
        z = smax(z, s, 10.0)
    yy = yayla_z(x, y)
    if yy > -1e8:
        z = smax(z, yy, 10.0)
    return z


def yukseklik(x, y):
    z = ham_yukseklik(x, y)
    goreli = z - taban(y)
    dy = nokta_seg_uzaklik(x, y, YOL)
    sakin = ss(3.0, 14.0, dy) * ss(0.75, 1.35, math.hypot((x - 10.0) / 62.0, (y - 395.0) / 36.0))
    amp = 2.0 + 15.0 * ss(15.0, 110.0, goreli)
    z += (sirtli(x / 52.0, y / 52.0) - 0.45) * 2.0 * amp * (0.2 + 0.8 * sakin)
    z += (sirtli(x / 15.0 + 7.1, y / 15.0) - 0.45) * 2.0 * (0.6 + 2.6 * ss(30.0, 110.0, goreli)) * sakin
    # dere yatağı
    if y < 160:
        dn = nokta_seg_uzaklik(x, y, NEHIR)
        gen = 6.5
        if dn < gen * 2.4:
            yatak = taban(y) - 2.2
            z = min(z, yatak + (dn / gen) ** 2 * 5.0)
    return z


def nehir_maske(x, y):
    if y > 160:
        return 0.0
    return 1.0 - ss(2.6, 4.4, nokta_seg_uzaklik(x, y, NEHIR))


def arazi():
    nx, ny = 340, 520
    xs = [-130 + 260 * i / (nx - 1) for i in range(nx)]
    ys = [-46 + 950 * (j / (ny - 1)) ** 1.35 for j in range(ny)]
    me = bpy.data.meshes.new("arazi")
    v, f, nm, gr = [], [], [], []
    for j, y in enumerate(ys):
        tb = taban(y)
        for i, x in enumerate(xs):
            z = yukseklik(x, y)
            v.append((x, y, z))
            nm.append(nehir_maske(x, y))
            gr.append(ss(2.0, 75.0, z - tb))
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            f.append((a, a + 1, a + nx + 1, a + nx))
    me.from_pydata(v, [], f)
    me.update()
    for ad, veri in (("nehir", nm), ("goreli", gr)):
        at = me.attributes.new(ad, "FLOAT", "POINT")
        at.data.foreach_set("value", veri)
    for p in me.polygons:
        p.use_smooth = True

    def yogun(A, geo):
        # dik yüz kaya (koyu, çizikli), yatık yüz çayır (açık); dorukta koyu, etekte soluk
        sep = A.n("ShaderNodeSeparateXYZ")
        A.bag(geo.outputs["Normal"], sep.inputs[0])
        kaya = A.aralik(sep.outputs[2], 0.9, 0.5)
        t = A.m("ADD", 0.34, A.m("MULTIPLY", kaya, 0.6))
        g = A.n("ShaderNodeAttribute")
        g.attribute_type = "GEOMETRY"
        g.attribute_name = "goreli"
        t = A.m("MULTIPLY", t, A.m("ADD", 0.3, A.m("MULTIPLY", g.outputs["Fac"], 0.75)))
        at = A.n("ShaderNodeAttribute")
        at.attribute_type = "GEOMETRY"
        at.attribute_name = "nehir"
        return A.m("MULTIPLY", t, A.m("SUBTRACT", 1.0, at.outputs["Fac"]))
    m = murekkep("m_arazi", taban=0.2, doku=0.8, cizik=(0.5, 0.5, 0.13), yogun_fn=yogun, esik=(0.2, 0.78), renkli=1.0)
    return nesne("arazi", me, m)


# ================================================================ ağaçlar
def ladin_mesh(ad, boy, tohum):
    r = random.Random(tohum)
    me = bpy.data.meshes.new(ad)
    bm = bmesh.new()
    kat = int(6 + boy / 2.0)
    for k in range(kat):
        t = k / (kat - 1)
        z = boy * (0.1 + 0.88 * t)
        rad = boy * 0.2 * (1 - t) ** 0.9 + 0.2
        yuk = boy * 0.18 * (1 - t * 0.5)
        seg = 11
        tepe = bm.verts.new((0, 0, z + yuk * 0.6))
        alt = []
        for s in range(seg):
            a = TAU * s / seg + r.uniform(-0.15, 0.15)
            rr = rad * r.uniform(0.65, 1.15)
            alt.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, z - yuk * 0.4 + r.uniform(-0.3, 0.1) * yuk)))
        for s in range(seg):
            bm.faces.new((tepe, alt[s], alt[(s + 1) % seg]))
        bm.faces.new(alt[::-1])
    gov = bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=boy * 0.025 + 0.1, radius2=0.05, depth=boy * 0.5)
    for vv in gov["verts"]:
        vv.co.z += boy * 0.25
    bm.to_mesh(me)
    bm.free()
    return me


def yaprakli_mesh(ad, boy, tohum):
    """Kayın / kızılağaç: gövde üstünde düzensiz yaprak öbekleri (mürekkep lekesi gibi)."""
    r = random.Random(tohum)
    me = bpy.data.meshes.new(ad)
    bm = bmesh.new()
    for k in range(r.randint(4, 6)):
        c = Vector((r.uniform(-0.22, 0.22) * boy, r.uniform(-0.22, 0.22) * boy, boy * r.uniform(0.55, 0.92)))
        rad = boy * r.uniform(0.17, 0.27)
        sp = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=rad)
        for vv in sp["verts"]:
            n = noise.noise(vv.co * (2.2 / rad) + Vector((tohum, k, 0)))
            vv.co = vv.co * (1.0 + 0.32 * n) + c
            vv.co.z = c.z + (vv.co.z - c.z) * 0.78
    gov = bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=boy * 0.035 + 0.1, radius2=0.06, depth=boy * 0.7)
    for vv in gov["verts"]:
        vv.co.z += boy * 0.35
    bm.to_mesh(me)
    bm.free()
    return me


def ormanlar():
    m = murekkep("m_igne", ton=1.0, taban=0.55, doku=0.45, yikama=PALET["igne"], cizik=(0.8, 0.8, 0.5), olcek=1.6,
                 esik=(0.25, 0.8))
    my = murekkep("m_yaprak", ton=0.95, taban=0.45, doku=0.6, yikama="#6F7A63", cizik=(1.6, 1.6, 1.6), olcek=1.3,
                  esik=(0.2, 0.75))
    ladinler = [ladin_mesh(f"ladin{i}", 10.0, 50 + i) for i in range(7)]
    yaprakli = [yaprakli_mesh(f"yaprakli{i}", 9.0, 80 + i) for i in range(5)]
    for me in ladinler:
        me.materials.append(m)
    for me in yaprakli:
        me.materials.append(my)
    r = random.Random(7)
    adet = 0
    deneme = 0
    while adet < 900 and deneme < 60000:
        deneme += 1
        x, y = r.uniform(-130, 130), r.uniform(-30, 480)
        z = yukseklik(x, y)
        tb = taban(y)
        if nehir_maske(x, y) > 0 or (y < 160 and nokta_seg_uzaklik(x, y, NEHIR) < 7):
            continue
        if nokta_seg_uzaklik(x, y, YOL) < 3.2:
            continue
        if -8 < y < 26 and -58 < x < 24:      # köy ve köprü açıklığı
            continue
        if y < 4 and abs(x) < 62:              # ön kıyı açık kalır, başlangıç görünsün
            continue
        if 360 < y < 425 and -40 < x < 60:    # yayla çayırı
            continue
        e = 0.6
        gx = (yukseklik(x + e, y) - yukseklik(x - e, y)) / (2 * e)
        gy = (yukseklik(x, y + e) - yukseklik(x, y - e)) / (2 * e)
        if math.hypot(gx, gy) > 1.15:
            continue
        # sırtlarda ve sis kıyısında kümelenir; sisin dibinde ağaç dikmek boşuna
        goreli = ss(6.0, 40.0, z - tb)
        kume = noise.noise(Vector((x / 30.0, y / 30.0, 4.2)))
        olas = (0.15 + 0.85 * goreli) * ss(-0.15, 0.35, kume) * sis_py(x, y, z) ** 0.5
        if y < 40:
            olas = max(olas, 0.35 * ss(-0.3, 0.2, kume))
        if r.random() > olas:
            continue
        yakin = y < 40
        boy = r.uniform(0.75, 1.3) * (1.6 if yakin else 1.0)
        alcak = z < 70 and r.random() < 0.65
        kume_m = yaprakli if alcak else ladinler
        o = bpy.data.objects.new(f"agac{adet}", kume_m[adet % len(kume_m)])
        koleksiyon("agac").objects.link(o)
        o.location = (x, y, z - 0.6)
        o.scale = (boy, boy, boy * r.uniform(0.95, 1.2))
        o.rotation_euler = (r.uniform(-0.04, 0.04), r.uniform(-0.04, 0.04), r.uniform(0, TAU))
        adet += 1
    print("AGAC", adet)


# ================================================================ yapılar
def kemer_kopru(x0, x1, y, en=3.2):
    """Tek kemerli taş köprü: XZ profili, y boyunca uzar."""
    m = murekkep("m_tas", ton=0.62, taban=0.22, doku=0.7, yikama=PALET["tas"], cizik=(1.2, 1.2, 1.2), olcek=1.4)
    ac = x1 - x0
    orta = (x0 + x1) / 2
    ust = []
    for i in range(25):
        t = i / 24
        xx = x0 - 4 + (ac + 8) * t
        ust.append((xx, 6.6 + 1.6 * math.sin(math.pi * t)))
    profil = [(x0 - 4, -2.0)] + ust + [(x1 + 4, -2.0), (x1, -2.0)]
    R = ac / 2
    for i in range(1, 24):
        a = math.pi * i / 24
        profil.append((orta + R * math.cos(a), 1.2 * R * math.sin(a) * 0.78 - 2.0 + 0.6))
    profil.append((x0, -2.0))
    o = prizma("kopru", profil, en, m)
    o.location = (0, y - en / 2, 0)
    # korkuluk taşları
    for i in range(1, 24, 2):
        t = i / 24
        xx = x0 - 4 + (ac + 8) * t
        zz = 6.6 + 1.6 * math.sin(math.pi * t)
        for yy in (y - en / 2 + 0.2, y + en / 2 - 0.2):
            kutu(f"korkuluk{i}_{yy:.0f}", (0.9, 0.35, 0.7), (xx, yy, zz + 0.35), m)
    return o


def ev(ad, konum, aci, olcek=1.0, kat=2):
    """Karadeniz yayla evi: taş zemin kat, ahşap üst kat, geniş saçaklı alçak çatı."""
    tas = bpy.data.materials.get("m_tas")
    ahsap = bpy.data.materials.get("m_ahsap") or murekkep("m_ahsap", ton=0.95, taban=0.4, doku=0.55,
                                                          yikama="#5A4D42", cizik=(3.0, 3.0, 0.15), olcek=1.0)
    cati = bpy.data.materials.get("m_cati") or murekkep("m_cati", ton=0.7, taban=0.3, doku=0.6, yikama="#6C6A66",
                                                        cizik=(0.2, 2.5, 2.5), olcek=1.2)
    kok = bpy.data.objects.new(ad, None)
    koleksiyon("cizgi").objects.link(kok)
    W, L = 6.0 * olcek, 7.5 * olcek
    h1, h2 = 2.6 * olcek, 2.5 * olcek
    kutu(ad + "_tas", (W, L, h1), (0, 0, h1 / 2 - 0.4), tas, kok)
    if kat > 1:
        kutu(ad + "_ahsap", (W + 0.3, L + 0.3, h2), (0, 0, h1 + h2 / 2 - 0.4), ahsap, kok)
    H = h1 + (h2 if kat > 1 else 0) - 0.4
    egim = math.radians(24)
    sacak = 0.9 * olcek
    yari = W / 2 + sacak
    tepe = yari * math.tan(egim)
    kal = 0.25
    profil = [(-yari, 0), (yari, 0), (yari, kal), (0, tepe + kal), (-yari, kal)]
    c = prizma(ad + "_cati", profil, L + 2 * sacak, cati, kok)
    c.location = (0, -(L / 2 + sacak), H)
    # alın üçgeni
    ucgen = [(-W / 2 - 0.15, 0), (W / 2 + 0.15, 0), (0, (W / 2) * math.tan(egim))]
    for s in (-1, 1):
        u = prizma(ad + f"_alin{s}", ucgen, 0.2, ahsap, kok)
        u.location = (0, s * (L / 2 + 0.15) - 0.1, H)
    # pencere ve kapı (koyu kesik)
    koyu = bpy.data.materials.get("m_koyu") or murekkep("m_koyu", ton=1.0, taban=0.9, doku=0.2)
    kutu(ad + "_kapi", (1.1 * olcek, 0.2, 1.9 * olcek), (W * 0.18, -L / 2 - 0.05, 0.55 * olcek), koyu, kok)
    if kat > 1:
        for px in (-W * 0.25, W * 0.22):
            kutu(ad + f"_pen{px:.0f}", (0.9 * olcek, 0.2, 0.9 * olcek), (px, -L / 2 - 0.2, h1 + h2 * 0.5 - 0.3), koyu, kok)
    # baca
    kutu(ad + "_baca", (0.7, 0.7, 2.0), (W * 0.22, L * 0.25, H + tepe * 0.5 + 0.6), tas, kok)
    kok.location = konum
    kok.rotation_euler = (0, 0, math.radians(aci))
    return kok


def zemin(x, y):
    return yukseklik(x, y)


def yapilar():
    kemer_kopru(-6.5, 20.5, 12.5)
    ev("ev_koy1", (-44, -1.5, zemin(-44, -1.5)), -8, 1.0)
    ev("ev_koy2", (-63, 16, zemin(-63, 16) - 0.3), 12, 0.95)
    ev("ev_koy3", (-30, 26, zemin(-30, 26) - 0.3), -20, 0.85, kat=1)
    ev("ev_yayla", (18, 384, zemin(18, 384) - 0.3), 6, 1.0)
    ev("ev_yayla2", (36, 398, zemin(36, 398) - 0.3), -14, 0.85, kat=1)
    ev("ev_yayla3", (-6, 404, zemin(-6, 404) - 0.3), 18, 0.8, kat=1)


def su_ve_selale():
    su = kagit_mat("m_su", cizgi=0.85, cizgi_yon="y", sik=1.3)
    # dere yüzeyi: yatağın üstünde ince şerit
    me = bpy.data.meshes.new("dere")
    v, f = [], []
    pts = []
    for i in range(len(NEHIR) - 1):
        ax, ay = NEHIR[i]
        bx, by = NEHIR[i + 1]
        for s in range(12):
            t = s / 12
            pts.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    pts.append(NEHIR[-1])
    for i, (x, y) in enumerate(pts):
        if i + 1 < len(pts):
            dx, dy = pts[i + 1][0] - x, pts[i + 1][1] - y
        else:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        L = math.hypot(dx, dy) or 1
        nx_, ny_ = -dy / L, dx / L
        zz = (taban(y) * 0.92 - 2.5 + 0.6) if y < 175 else yukseklik(x, y)
        gen = 4.2
        v.append((x + nx_ * gen, y + ny_ * gen, zz))
        v.append((x - nx_ * gen, y - ny_ * gen, zz))
    for i in range(len(pts) - 1):
        a = 2 * i
        f.append((a, a + 1, a + 3, a + 2))
    me.from_pydata(v, [], f)
    me.update()
    nesne("dere", me, su, kol="su")
    # şelale: sol uçurumdan düşen ak şerit
    sel = kagit_mat("m_selale", cizgi=0.6, cizgi_yon="z", sik=2.2)
    me = bpy.data.meshes.new("selale")
    ust, alt_ = Vector((-49.0, 150.0, 158.0)), Vector((-45.0, 146.0, 70.0))
    v, f = [], []
    for i in range(16):
        t = i / 15
        p = ust.lerp(alt_, t)
        g = 1.6 + 2.6 * t
        v.append((p.x - g, p.y - 1.5, p.z))
        v.append((p.x + g, p.y - 1.5, p.z))
    for i in range(15):
        a = 2 * i
        f.append((a, a + 1, a + 3, a + 2))
    me.from_pydata(v, [], f)
    me.update()
    nesne("selale", me, sel, kol="cizgi")


def patika():
    """Yol: arazinin üstünde ince açık şerit (kâğıt), kenarları mürekkep çizgisi alır."""
    m = kagit_mat("m_patika")
    pts = yol_ornekle(240)
    me = bpy.data.meshes.new("patika")
    v, f = [], []
    for i, (x, y, z) in enumerate(pts):
        j = min(i + 1, len(pts) - 1)
        k = max(i - 1, 0)
        dx, dy = pts[j][0] - pts[k][0], pts[j][1] - pts[k][1]
        L = math.hypot(dx, dy) or 1
        nx_, ny_ = -dy / L, dx / L
        g = 0.9
        v.append((x + nx_ * g, y + ny_ * g, yukseklik(x + nx_ * g, y + ny_ * g) + 0.25))
        v.append((x - nx_ * g, y - ny_ * g, yukseklik(x - nx_ * g, y - ny_ * g) + 0.25))
    for i in range(len(pts) - 1):
        a = 2 * i
        f.append((a, a + 1, a + 3, a + 2))
    me.from_pydata(v, [], f)
    me.update()
    nesne("patika", me, m, kol="su")


def yol_ornekle(n):
    """Denetim noktalarından Catmull-Rom ile eşit aralıklı n nokta (x, y, z)."""
    P = [Vector((x, y)) for x, y in YOL]
    ince = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]
        p1, p2 = P[i], P[i + 1]
        p3 = P[min(i + 2, len(P) - 1)]
        for s in range(40):
            t = s / 40
            t2, t3 = t * t, t * t * t
            q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            ince.append(q)
    ince.append(P[-1])
    uz = [0.0]
    for i in range(1, len(ince)):
        uz.append(uz[-1] + (ince[i] - ince[i - 1]).length)
    top = uz[-1]
    out = []
    j = 0
    for k in range(n):
        hedef = top * k / (n - 1)
        while j < len(uz) - 2 and uz[j + 1] < hedef:
            j += 1
        t = (hedef - uz[j]) / max(1e-6, uz[j + 1] - uz[j])
        q = ince[j].lerp(ince[j + 1], t)
        z = yukseklik(q.x, q.y)
        if -8 <= q.x <= 22 and 10 <= q.y <= 15:
            z = 6.6 + 1.6 * math.sin(math.pi * max(0, min(1, (q.x + 10.5) / 35.0))) + 0.05
        out.append((q.x, q.y, z))
    return out


# ================================================================ kamera, ışık, çekim
def kamera():
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("kam")
    cd.type = "ORTHO"
    cd.ortho_scale = GEN
    cd.sensor_fit = "HORIZONTAL"
    cd.clip_start = 1.0
    cd.clip_end = 4000.0
    c = bpy.data.objects.new("kam", cd)
    sc.collection.objects.link(c)
    ileri = Vector((0, math.cos(EGIM), -math.sin(EGIM)))
    yukari = Vector((0, math.sin(EGIM), math.cos(EGIM)))
    H = GEN * ORAN
    c.location = yukari * (H / 2 - 7.0) - ileri * 900
    c.rotation_euler = (math.pi / 2 - EGIM, 0, 0)
    sc.camera = c
    return c, ileri, yukari


def isik():
    sc = bpy.context.scene
    g = bpy.data.lights.new("gunes", "SUN")
    g.energy = 4.0
    g.angle = math.radians(4)
    o = bpy.data.objects.new("gunes", g)
    sc.collection.objects.link(o)
    yon = Vector((-0.55, -0.45, 0.70)).normalized()   # ışık sol-önden ve yukarıdan
    o.rotation_euler = (-yon).to_track_quat("-Z", "Y").to_euler()
    w = bpy.data.worlds.new("dunya")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    A = Agac(nt)
    lp = A.n("ShaderNodeLightPath")
    bg1 = A.n("ShaderNodeBackground")
    bg1.inputs["Color"].default_value = hx(PALET["kagit"])
    bg2 = A.n("ShaderNodeBackground")
    bg2.inputs["Color"].default_value = (1, 1, 1, 1)
    bg2.inputs["Strength"].default_value = 0.22
    mx = A.n("ShaderNodeMixShader")
    A.bag(lp.outputs["Is Camera Ray"], mx.inputs[0])
    A.bag(bg2.outputs[0], mx.inputs[1])
    A.bag(bg1.outputs[0], mx.inputs[2])
    out = A.n("ShaderNodeOutputWorld")
    A.bag(mx.outputs[0], out.inputs["Surface"])


def cizgiler(sc):
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = "ABSOLUTE"
    sc.render.line_thickness = 1.0
    vl = sc.view_layers[0]
    fs = vl.freestyle_settings
    fs.as_render_pass = True
    fs.crease_angle = math.radians(128)
    ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("cizgi")
    ls.select_by_visibility = True
    ls.visibility = "VISIBLE"
    ls.select_by_edge_types = True
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = False
    ls.select_external_contour = True
    ls.select_by_collection = True
    ls.collection = koleksiyon("cizgi")
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("murekkep")
    st = ls.linestyle
    st.color = hx(PALET["murekkep"])[:3]
    k = EN / 1200.0
    st.thickness = 2.8 * k
    st.thickness_position = "CENTER"
    st.use_length_min = True
    st.length_min = 26 * k
    try:
        st.chaining = "PLAIN"
    except Exception:
        pass
    th = st.thickness_modifiers.new("firca", "CALLIGRAPHY")
    th.orientation = math.radians(55)
    th.thickness_min = 0.7 * k
    th.thickness_max = 4.0 * k
    th.blend = "MULTIPLY"
    tn = st.thickness_modifiers.new("titrek", "NOISE")
    tn.amplitude = 1.2 * k
    tn.period = 22 * k
    tn.blend = "ADD"
    gs = st.geometry_modifiers.new("ornek", "SAMPLING")
    gs.sampling = 3.0
    gb = st.geometry_modifiers.new("yumusak", "BEZIER_CURVE")
    gb.error = 6.0 * k
    gm = st.geometry_modifiers.new("el", "PERLIN_NOISE_1D")
    gm.amplitude = 0.8 * k
    gm.frequency = 10 * k


def ayarla(sc):
    sc.render.engine = "BLENDER_EEVEE"
    e = sc.eevee
    e.taa_render_samples = 32
    e.use_shadows = True
    sc.render.resolution_x, sc.render.resolution_y = EN, BOY
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    try:
        sc.view_settings.look = "None"
    except Exception:
        pass
    vl = sc.view_layers[0]
    a = vl.aovs.add()
    a.name = "gorunur"
    a.type = "VALUE"
    cizgiler(sc)
    # birleştirme: çizgi, sisin örttüğü yerde silinir
    ng = bpy.data.node_groups.new("tomar", "CompositorNodeTree")
    ng.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    N, Lk = ng.nodes, ng.links
    rl = N.new("CompositorNodeRLayers")
    rl.scene = sc
    print("RL_CIKIS", [s.name for s in rl.outputs if s.enabled])
    sep = N.new("CompositorNodeSeparateColor")
    Lk.new(rl.outputs["Freestyle"], sep.inputs[0])
    carp = N.new("ShaderNodeMath")
    carp.operation = "MULTIPLY"
    Lk.new(sep.outputs["Alpha"], carp.inputs[0])
    Lk.new(rl.outputs["gorunur"], carp.inputs[1])
    ku = N.new("CompositorNodeKuwahara")
    try:
        ku.inputs["Type"].default_value = "Anisotropic"
    except Exception:
        pass
    ku.inputs["Size"].default_value = max(2, int(round(7 * EN / 1200)))
    ku.inputs["Uniformity"].default_value = 4
    ku.inputs["Sharpness"].default_value = 0.9
    ku.inputs["Eccentricity"].default_value = 1.2
    Lk.new(rl.outputs["Image"], ku.inputs["Image"])
    mx = N.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    Lk.new(carp.outputs[0], mx.inputs[0])
    Lk.new(ku.outputs[0], mx.inputs[6])
    mx.inputs[7].default_value = hx(PALET["murekkep"])
    out = N.new("NodeGroupOutput")
    Lk.new(mx.outputs[2], out.inputs[0])
    sc.compositing_node_group = ng
    sc.render.use_compositing = True
    isf = sc.render.image_settings
    isf.file_format = "PNG"
    isf.color_mode = "RGB"
    isf.color_depth = "8"


def kur():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    isik()
    arazi()
    yapilar()
    su_ve_selale()
    patika()
    ormanlar()
    kamera()
    ayarla(sc)
    return sc


def yol_disari(sc, yol_json):
    """Yolun ekran izdüşümü: her örnek için (u, v) 0..1, görünürlük ve örtülme."""
    from bpy_extras.object_utils import world_to_camera_view
    dg = bpy.context.evaluated_depsgraph_get()
    cam = sc.camera
    ileri = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    pts = yol_ornekle(600)
    cikti = []
    for (x, y, z) in pts:
        p = Vector((x, y, z + 0.9))
        q = world_to_camera_view(sc, cam, p)
        hit, loc, nrm, idx, ob, mtx = sc.ray_cast(dg, p - ileri * 0.6, -ileri)
        ortu = bool(hit and ob and ob.name not in ("patika", "dere"))
        cikti.append([round(q.x, 5), round(1 - q.y, 5), round(sis_py(x, y, z), 3), 1 if ortu else 0])
    with open(yol_json, "w", encoding="utf-8") as f:
        json.dump(dict(en=sc.render.resolution_x, boy=sc.render.resolution_y, nokta=cikti), f)


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["resim", "onizleme.png"]
    komut = a[0]
    if len(a) > 2:
        k = float(a[2])
        EN, BOY = int(EN * k), int(BOY * k)
    sc = kur()
    if komut == "resim":
        sc.render.filepath = os.path.abspath(a[1])
        bpy.ops.render.render(write_still=True)
        print("RESIM_OK", a[1])
    elif komut == "yol":
        yol_disari(sc, os.path.abspath(a[1]))
        print("YOL_OK", a[1])
    elif komut == "kaydet":
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a[1]))
        print("KAYDET_OK", a[1])
