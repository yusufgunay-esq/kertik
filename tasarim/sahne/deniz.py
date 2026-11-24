"""Kertik sahnesi: Sefer. Mürekkep ve açık renk (aşı, çivit) ile boyanmış dikey deniz tomarı.

Fikir: seans bir deniz yolculuğudur. Pomodoro'da kırmızı yelkenli tekne alttaki
limandan çıkar, adaların ve sis kümelerinin arasından geçip karşı kıyıdaki limana
süre dolarken yanaşır. Kronometre'de aynı limandan çıkar, varış yoktur; tekne açık
denize, ufka doğru gider. Tomar tek bir boyalı resimdir; tekne, iz, sis, balık ve
mühür uygulamada canlı katman olarak üstüne çizilir.

Görüntü kuramı: yüzeyler ışıkla değil mürekkep yoğunluğuyla boyanır; ışık yalnız
"nereye ne kadar mürekkep düşer" sorusunu yanıtlar. Işık alan yamaç aşı boyasına,
gölge çivite çalar; deniz kâğıttır, kıyıya koşut ince dalga çizgileri taşır. Çizgiler
Freestyle ile fırça kalemi gibi çekilir ve sisin içinde silinir. Tek aksan kırmızı
yelkendir; resmin kendisine kırmızı girmez.

Kullanım:
  blender -b --factory-startup --python deniz.py -- resim <cikti.png> [olcek]
  blender -b --factory-startup --python deniz.py -- yol <cikti.json> [olcek]
  blender -b --factory-startup --python deniz.py -- tekne <klasor>
  blender -b --factory-startup --python deniz.py -- kaydet <dosya.blend>
"""
import bpy
import bmesh
import json
import math
import os
import random
import sys
from mathutils import Vector, noise

KOK = os.path.dirname(os.path.abspath(__file__))
GEN = 150.0                 # tomarın genişliği (m)
ORAN = 3.6                  # boy / en
EN, BOY = 1200, int(1200 * ORAN)
EGIM = math.radians(34.0)   # kamera aşağı bakış açısı (ortografik)
ALT_PAY = 40.0              # tomarın alt kenarı: limanın altında kıyı mahallesi kalır, kalkış ekran ortasına oturur
ISIK_YON = (0.86, 0.18, 0.52)  # ışık sağ arkadan: kameraya bakan yarlar gölgede, koyu mürekkep alır
TAU = math.tau

PALET = dict(
    kagit="#F4EEE1",
    murekkep="#221D1A",
    yikama="#7E8780",
    uzak="#A4AEB8",
    igne="#33402F",
    tas="#9C968A",
    aksan="#B8382A",       # tek bilinçli aksan: yelken ve mühür
    asi="#C2A277",         # aşı boyası: ışık alan yamaç
    civit="#7487A0",       # çivit: gölge yamaç
    deniz="#8FA2B8",       # denizin soluk çivit yıkaması
    deniz_koyu="#3E4F66",  # dalga çizgisi
)

SIS = [(40.0, 26.0, 640.0, 0.95)]                    # yükseklik bantları: uzak dağ etekleri
SIS_Y = [(176.0, 15.0, 0.85), (405.0, 20.0, 0.7)]    # deniz sisi kümeleri: (merkez y, kalınlık, güç)
UZAK = (560.0, 980.0, 0.72)


def hx(c, a=1.0):
    c = c.lstrip("#")
    s = [int(c[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in s]
    return (*lin, a)


def ss(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


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


def murekkep(ad, ton=0.8, taban=0.16, doku=0.6, yikama=None, cizik=(0.45, 0.45, 0.05), olcek=1.0,
             esik=(0.18, 0.72), yogun_fn=None, renkli=0.0, ek_fn=None):
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
    if ek_fn is not None:
        renk = A.karis(A.m("MULTIPLY", ek_fn(A, geo), vis), renk, hx(PALET["murekkep"]))
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


def smax(a, b, k=14.0):
    hb = max(0.0, min(1.0, 0.5 + 0.5 * (b - a) / k))
    return a * (1 - hb) + b * hb + k * hb * (1 - hb)


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
    c.location = yukari * (H / 2 - ALT_PAY) - ileri * 900
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
    yon = Vector(ISIK_YON).normalized()
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


def _ince_takim(fs):
    """Küçük nesneler (ev, fener, kayık, tekne) için ince kalem."""
    ls = fs.linesets.new("ince")
    ls.select_by_visibility = True
    ls.visibility = "VISIBLE"
    ls.select_by_edge_types = True
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.select_external_contour = True
    ls.select_by_collection = True
    ls.collection = koleksiyon("ince")
    ls.linestyle = bpy.data.linestyles.new("ince")
    st = ls.linestyle
    st.color = hx(PALET["murekkep"])[:3]
    k = EN / 1200.0
    st.thickness = 1.5 * k
    st.thickness_position = "CENTER"
    th = st.thickness_modifiers.new("firca", "CALLIGRAPHY")
    th.orientation = math.radians(55)
    th.thickness_min = 0.5 * k
    th.thickness_max = 2.0 * k
    th.blend = "MULTIPLY"


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
    ls.select_border = False
    ls.select_crease = False
    ls.select_external_contour = True
    ls.select_by_collection = True
    ls.collection = koleksiyon("cizgi")
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("murekkep")
    st = ls.linestyle
    st.color = hx(PALET["murekkep"])[:3]
    k = EN / 1200.0
    st.thickness = 2.1 * k
    st.thickness_position = "CENTER"
    st.use_length_min = True
    st.length_min = 26 * k
    try:
        st.chaining = "PLAIN"
    except Exception:
        pass
    _ince_takim(fs)
    th = st.thickness_modifiers.new("firca", "CALLIGRAPHY")
    th.orientation = math.radians(55)
    th.thickness_min = 0.7 * k
    th.thickness_max = 3.0 * k
    th.blend = "MULTIPLY"
    tn = st.thickness_modifiers.new("titrek", "NOISE")
    tn.amplitude = 0.7 * k
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
    ku.inputs["Size"].default_value = max(2, int(round(5 * EN / 1200)))
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


# ================================================================ sis: yükseklik bantları + deniz sisi kümeleri
def sis_py(x, y, z):
    f = 0.0
    for k, (zc, w, ymin, g) in enumerate(SIS):
        warp = w * 0.8 * (0.6 * math.sin(x / 23.0 + y / 31.0 + k) + 0.4 * math.sin(x / 9.7 - y / 13.0 + 2 * k))
        b = (1 - ss(0.0, 1.0, (z - zc + warp) / w)) * ss(ymin - 20, ymin + 20, y) * g
        f = max(f, b)
    for k, (yc, w, g) in enumerate(SIS_Y):
        warp = w * 0.9 * (0.6 * math.sin(x / 21.0 + k * 1.7) + 0.4 * math.sin(x / 8.3 - k * 2.3))
        t = (y - yc + warp) / w
        b = g * math.exp(-t * t) * (1 - ss(6.0, 34.0, z))
        f = max(f, b)
    uz = UZAK[2] * ss(UZAK[0], UZAK[1], y)
    return (1 - f) * (1 - uz)


def sis_dugum(A):
    """Görünürlük (0 sis, 1 açık) ve uzaklık (0..1) çıkışları; sis_py ile aynı formül."""
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
    for k, (yc, w, g) in enumerate(SIS_Y):
        s1 = A.m("SINE", A.m("ADD", A.m("DIVIDE", x, 21.0), k * 1.7))
        s2 = A.m("SINE", A.m("SUBTRACT", A.m("DIVIDE", x, 8.3), k * 2.3))
        warp = A.m("MULTIPLY", A.m("ADD", A.m("MULTIPLY", s1, 0.6), A.m("MULTIPLY", s2, 0.4)), w * 0.9)
        t = A.m("DIVIDE", A.m("ADD", A.m("SUBTRACT", y, yc), warp), w)
        b = A.m("MULTIPLY", A.m("EXPONENT", A.m("MULTIPLY", A.m("MULTIPLY", t, t), -1.0)), g)
        b = A.m("MULTIPLY", b, A.m("SUBTRACT", 1.0, A.aralik(z, 6.0, 34.0)))
        f = b if f is None else A.m("MAXIMUM", f, b)
    uz = A.aralik(y, UZAK[0], UZAK[1])
    vis = A.m("MULTIPLY", A.m("SUBTRACT", 1.0, f), A.m("SUBTRACT", 1.0, A.m("MULTIPLY", uz, UZAK[2])))
    return vis, uz, geo


# ================================================================ arazi: iki kıyı, adalar, kayalar, uzak dağlar
DENIZ_TABAN = -24.0
# Burunlar: iki yandan sırayla uzanan yalı yarlı kara dilleri (taraf, sırt y, uç x, sırt yüksekliği, yarı en)
BURUNLAR = [(-1, 92, -24, 30, 18), (1, 172, 22, 50, 22), (-1, 262, -12, 72, 26), (1, 350, 28, 64, 25),
            (1, 452, 48, 36, 16)]
ADALAR = [  # küçük adalar ve kayalar: (x, y, yarıçap, yükseklik, üs)
    (-76, 2, 42, 44, 0.8), (86, 24, 32, 30, 0.9),
    (-6, 226, 11, 17, 0.8),
    (20, 124, 9.0, 3.5, 0.5),
    (-70, 560, 14, 16, 0.9), (-100, 700, 18, 20, 0.9),
]
DAGLAR = [(30, 662, 70, 55, 1.0), (96, 650, 55, 50, 1.0), (60, 708, 80, 62, 1.1), (140, 700, 60, 58, 1.0)]
MENDIREK = [(-60, 14), (-49, 31), (-31, 44), (-13, 51), (-3, 52)]
MAHALLE = [(-34, -24), (-16, -30), (2, -22), (20, -28), (36, -18), (-54, -20), (-70, -36), (-4, -48), (24, -50)]
VARIS_ISKELE = ((26.0, 598.0), (17.0, 581.0))

ROTA_POMODORO = [(-24, 24), (-6, 34), (12, 52), (10, 80), (-6, 112), (-14, 140), (-4, 176), (-24, 210), (-28, 240),
                 (-6, 276), (4, 306), (-10, 340), (-4, 378), (12, 420), (8, 470), (14, 520), (20, 556), (21, 572)]
ROTA_KRONOMETRE = [(-24, 24), (-6, 34), (12, 52), (10, 80), (-6, 112), (-14, 140), (-4, 176), (-24, 210), (-28, 240),
                   (-6, 276), (4, 306), (-10, 340), (-22, 380), (-30, 440), (-44, 520), (-40, 610), (-50, 720),
                   (-62, 860), (-70, 1000)]


def kiyi_yakin(x):
    return 13.0 + 5.0 * math.sin(x / 17.0) + 3.0 * math.sin(x / 7.3)


def kiyi_uzak(x):
    return 594.0 + 12.0 * math.sin(x / 26.0 + 1.0) + 5.0 * math.sin(x / 9.0) + max(0.0, -16.0 - x) ** 1.55 * 0.9


def burun(x, y, taraf, yc, xt, h, w0):
    ic = (xt - x) if taraf < 0 else (x - xt)          # uçtan kıyıya doğru (+)
    if ic < -22:
        return -1e9
    hc = h * (0.55 + 0.45 * ss(0.0, 70.0, ic)) * ss(-22.0, 0.0, ic)
    w = (w0 * (0.55 + 0.45 * ss(-10.0, 60.0, ic)))
    sy = yc + 7.0 * math.sin(x / 19.0 + yc) + 4.0 * math.sin(x / 7.0)
    t = abs(y - sy) / w
    if t > 1.35:
        return -1e9
    p = 0.62 * (1.0 - ss(0.5, 1.0, t)) + 0.38 * max(0.0, 1.0 - t * t)
    p *= 1.0 - ss(1.0, 1.35, t) * 0.0
    return DENIZ_TABAN + (hc - DENIZ_TABAN) * max(0.0, p)


def ham_yukseklik(x, y):
    z = DENIZ_TABAN
    s = kiyi_yakin(x)
    if y < s + 14:
        z = max(z, 2.2 + min(14.0, max(0.0, s - y) * 0.12) - max(0.0, y - s) * 2.0)
    u = kiyi_uzak(x)
    wx = ss(-80.0, -45.0, x)
    if y > u - 14 and wx > 0:
        zf = 2.0 + (y - u) * 0.1 if y > u else 2.0 - (u - y) * 2.0
        z = max(z, DENIZ_TABAN + (zf - DENIZ_TABAN) * wx)
    for b in BURUNLAR:
        k = burun(x, y, *b)
        if k > -1e8:
            z = smax(z, k, 5.0)
    for cx, cy, r, h, us in ADALAR:
        a = math.atan2(y - cy, x - cx)
        rr = r * (1.0 + 0.18 * math.sin(3 * a + cx) + 0.1 * math.sin(5 * a + cy))
        d = math.hypot((x - cx) / rr, (y - cy) / (rr * 0.85))
        if d < 1.0:
            p = 0.55 * (1.0 - ss(0.45, 1.0, d)) + 0.45 * (1.0 - d * d) ** us
            z = smax(z, DENIZ_TABAN + (h - DENIZ_TABAN) * p, 5.0)
    for cx, cy, r, h, us in DAGLAR:
        d = math.hypot((x - cx) / r, (y - cy) / (r * 0.75))
        if d < 1.0:
            z = smax(z, (h * (1.0 - d * d) ** us + 2.0) * wx, 14.0)
    return z


def yukseklik(x, y):
    z = ham_yukseklik(x, y)
    if z > -4.0:
        amp = 1.5 + 9.0 * ss(4.0, 70.0, z)
        z += (sirtli(x / 26.0, y / 26.0) - 0.45) * 2.0 * amp * ss(-4.0, 3.0, z)
        z += (sirtli(x / 8.0 + 5.3, y / 8.0) - 0.45) * 2.0 * (0.4 + 2.2 * ss(5.0, 50.0, z)) * ss(0.0, 4.0, z)
    return z


def arazi():
    nx, ny = 300, 460
    xs = [-132 + 264 * i / (nx - 1) for i in range(nx)]
    ys = [-90 + 950 * (j / (ny - 1)) ** 1.25 for j in range(ny)]
    me = bpy.data.meshes.new("arazi")
    v, f = [], []
    for y in ys:
        for x in xs:
            v.append((x, y, yukseklik(x, y)))
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            f.append((a, a + 1, a + nx + 1, a + nx))
    me.from_pydata(v, [], f)
    me.update()
    for p in me.polygons:
        p.use_smooth = True

    def yogun(A, geo):
        sep = A.n("ShaderNodeSeparateXYZ")
        A.bag(geo.outputs["Normal"], sep.inputs[0])
        kaya = A.aralik(sep.outputs[2], 0.92, 0.5)
        sp = A.n("ShaderNodeSeparateXYZ")
        A.bag(geo.outputs["Position"], sp.inputs[0])
        yuk = A.aralik(sp.outputs[2], 0.0, 60.0)
        return A.m("MULTIPLY", A.m("ADD", 0.34, A.m("MULTIPLY", kaya, 0.6)), A.m("ADD", 0.55, A.m("MULTIPLY", yuk, 0.5)))

    def kiyi(A, geo):
        # su çizgisi: kara ile denizin buluştuğu yerde ince koyu mürekkep
        sp = A.n("ShaderNodeSeparateXYZ")
        A.bag(geo.outputs["Position"], sp.inputs[0])
        return A.m("MULTIPLY", A.aralik(sp.outputs[2], -0.3, 0.05), A.aralik(sp.outputs[2], 0.75, 0.2))
    m = murekkep("m_arazi", taban=0.24, doku=0.7, cizik=(0.9, 0.9, 0.09), olcek=1.3, yogun_fn=yogun, esik=(0.2, 0.78),
                 renkli=1.0, ek_fn=kiyi)
    return nesne("arazi", me, m)


def deniz():
    """Kâğıt deniz: soluk çivit yıkama, kıyıya koşut dalga çizgileri, açıkta seyrek fırça çizikleri."""
    nx, ny = 240, 420
    xs = [-132 + 264 * i / (nx - 1) for i in range(nx)]
    ys = [-40 + 1240 * (j / (ny - 1)) ** 1.2 for j in range(ny)]
    me = bpy.data.meshes.new("deniz")
    v, f, der = [], [], []
    for y in ys:
        for x in xs:
            v.append((x, y, 0.0))
            der.append(max(0.0, min(1.0, -ham_yukseklik(x, y) / -DENIZ_TABAN)))
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            f.append((a, a + 1, a + nx + 1, a + nx))
    me.from_pydata(v, [], f)
    me.update()
    at = me.attributes.new("derinlik", "FLOAT", "POINT")
    at.data.foreach_set("value", der)

    m, A = yeni_malzeme("m_deniz")
    vis, uz, geo = sis_dugum(A)
    sp = A.n("ShaderNodeSeparateXYZ")
    A.bag(geo.outputs["Position"], sp.inputs[0])
    x, y = sp.outputs[0], sp.outputs[1]
    d = A.n("ShaderNodeAttribute")
    d.attribute_type = "GEOMETRY"
    d.attribute_name = "derinlik"
    der = d.outputs["Fac"]
    nz = A.n("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.06
    nz.inputs["Detail"].default_value = 3.0
    A.bag(geo.outputs["Position"], nz.inputs["Vector"])
    nb = A.m("SUBTRACT", nz.outputs["Fac"], 0.5)

    def ince_hat(faz, gen):
        u = A.m("ABSOLUTE", A.m("SUBTRACT", A.m("FRACT", A.m("ADD", faz, 0.5)), 0.5))
        return A.m("SUBTRACT", 1.0, A.aralik(u, gen * 0.35, gen))
    # kıyıya koşut çizgiler (sığlıkta)
    k_faz = A.m("ADD", A.m("MULTIPLY", der, 9.0), A.m("MULTIPLY", nb, 0.6))
    k_hat = A.m("MULTIPLY", ince_hat(k_faz, 0.11), A.m("SUBTRACT", 1.0, A.aralik(der, 0.25, 0.55)))
    k_hat = A.m("MULTIPLY", k_hat, A.aralik(der, 0.0, 0.04))
    # açık deniz: y boyunca dalgalı, kesik kesik çizikler
    a_faz = A.m("ADD", A.m("DIVIDE", y, 2.7), A.m("ADD", A.m("MULTIPLY", nb, 5.0), A.m("DIVIDE", x, 40.0)))
    kes = A.n("ShaderNodeTexNoise")
    kes.inputs["Scale"].default_value = 0.22
    kes.inputs["Detail"].default_value = 2.0
    mp = A.n("ShaderNodeMapping")
    A.bag(geo.outputs["Position"], mp.inputs["Vector"])
    mp.inputs["Scale"].default_value = (0.55, 2.2, 1.0)
    A.bag(mp.outputs[0], kes.inputs["Vector"])
    a_hat = A.m("MULTIPLY", ince_hat(a_faz, 0.1), A.aralik(kes.outputs["Fac"], 0.53, 0.63))
    hat = A.m("MAXIMUM", A.m("MULTIPLY", k_hat, 0.95), A.m("MULTIPLY", a_hat, 0.85))
    hat = A.m("MULTIPLY", hat, A.m("MULTIPLY", vis, A.m("SUBTRACT", 1.0, A.m("MULTIPLY", uz, 0.8))))
    # yıkama: derinde biraz daha çivit, sığda kâğıda açılır
    yik = A.m("ADD", 0.1, A.m("MULTIPLY", A.aralik(der, 0.05, 0.8), 0.16))
    yik = A.m("MULTIPLY", A.m("ADD", yik, A.m("MULTIPLY", nb, 0.12)), vis, clamp=True)
    renk = A.karis(yik, hx(PALET["kagit"]), hx(PALET["deniz"]))
    renk = A.karis(hat, renk, hx(PALET["deniz_koyu"]))
    em = A.n("ShaderNodeEmission")
    A.bag(renk, em.inputs["Color"])
    o = A.n("ShaderNodeOutputMaterial")
    A.bag(em.outputs[0], o.inputs["Surface"])
    aov = A.n("ShaderNodeOutputAOV")
    aov.aov_name = "gorunur"
    A.bag(vis, aov.inputs["Value"])
    return nesne("deniz", me, m, kol="su")


# ================================================================ liman yapıları
def serit_duvar(ad, pts, gen, alt, ust, mat):
    """Nokta dizisi boyunca taş duvar (mendirek, iskele)."""
    me = bpy.data.meshes.new(ad)
    v, f = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        j, k = min(i + 1, n - 1), max(i - 1, 0)
        dx, dy = pts[j][0] - pts[k][0], pts[j][1] - pts[k][1]
        L = math.hypot(dx, dy) or 1.0
        nx_, ny_ = -dy / L * gen / 2, dx / L * gen / 2
        for (ox, oy) in ((nx_, ny_), (-nx_, -ny_)):
            v.append((x + ox, y + oy, alt))
            v.append((x + ox, y + oy, ust))
    for i in range(n - 1):
        a, b = 4 * i, 4 * (i + 1)
        f += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a + 1, b + 1, b + 3, a + 3)]
    f += [(0, 1, 3, 2), (4 * (n - 1), 4 * (n - 1) + 2, 4 * (n - 1) + 3, 4 * (n - 1) + 1)]
    me.from_pydata(v, [], f)
    me.validate()
    me.update()
    return nesne(ad, me, mat, kol="ince")


def egri(pts, adim=24):
    P = [Vector(p) for p in pts]
    out = []
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)]
        for s in range(adim):
            t = s / adim
            t2, t3 = t * t, t * t * t
            q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            out.append((q.x, q.y))
    out.append(tuple(P[-1]))
    return out


def fener(ad, konum, olcek=1.0):
    """Taş fener kulesi: ak gövde, koyu kuşak, küçük fener odası (ışık efekti yok)."""
    tas = bpy.data.materials["m_tas"]
    koyu = bpy.data.materials.get("m_koyu") or murekkep("m_koyu", ton=1.0, taban=0.9, doku=0.2)
    ak = bpy.data.materials.get("m_ak") or murekkep("m_ak", ton=0.35, taban=0.12, doku=0.5, yikama=PALET["tas"],
                                                    cizik=(1.0, 1.0, 0.4))
    kok = bpy.data.objects.new(ad, None)
    koleksiyon("ince").objects.link(kok)
    H = 9.0 * olcek

    def sil(n, r1, r2, h, z, mat):
        me = bpy.data.meshes.new(n)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=14, radius1=r1, radius2=r2, depth=h)
        bm.to_mesh(me)
        bm.free()
        o = nesne(n, me, mat, kok)
        o.location = (0, 0, z + h / 2)
        for p in me.polygons:
            p.use_smooth = True
        return o
    sil(ad + "_govde", 1.45 * olcek, 1.05 * olcek, H, 0.8, ak)
    sil(ad + "_kusak", 1.28 * olcek, 1.22 * olcek, 1.3 * olcek, 0.8 + H * 0.45, koyu)
    sil(ad + "_balkon", 1.4 * olcek, 1.4 * olcek, 0.3, 0.8 + H, ak)
    sil(ad + "_oda", 0.85 * olcek, 0.85 * olcek, 1.4 * olcek, 1.15 + H, ak)
    sil(ad + "_kubbe", 1.0 * olcek, 0.05, 1.1 * olcek, 1.15 + H + 1.4 * olcek, koyu)
    kok.location = konum
    return kok


def sandal(ad, konum, aci, boy=4.2):
    """Limanda bağlı küçük kayık."""
    m = bpy.data.materials.get("m_ahsap")
    me = bpy.data.meshes.new(ad)
    bm = bmesh.new()
    kes = []
    for i in range(9):
        t = i / 8
        y = (t - 0.5) * boy
        w = 0.75 * math.sin(math.pi * t) ** 0.7 + 0.04
        dz = 0.25 * (2 * t - 1) ** 2
        kes.append([bm.verts.new((-w, y, 0.55 + dz)), bm.verts.new((-w * 0.6, y, 0.05 + dz * 0.4)),
                    bm.verts.new((w * 0.6, y, 0.05 + dz * 0.4)), bm.verts.new((w, y, 0.55 + dz))])
    for i in range(8):
        a, b = kes[i], kes[i + 1]
        for k in range(3):
            bm.faces.new((a[k], b[k], b[k + 1], a[k + 1]))
    bm.to_mesh(me)
    bm.free()
    o = nesne(ad, me, m, kol="ince")
    o.location = konum
    o.rotation_euler = (0, 0, math.radians(aci))
    return o


def kiyi_evi(ad, konum, aci, olcek=1.0, kat=1):
    """Kıyı evi: kireç badanalı duvar, kırma (dört yüzlü) çatı, küçük koyu pencereler."""
    ak = bpy.data.materials.get("m_badana") or murekkep("m_badana", ton=0.3, taban=0.08, doku=0.45,
                                                        yikama=PALET["tas"], cizik=(1.0, 1.0, 0.5))
    cati = bpy.data.materials.get("m_kiremit") or murekkep("m_kiremit", ton=0.78, taban=0.42, doku=0.55,
                                                          yikama="#9C7A55", cizik=(3.0, 0.4, 3.0), olcek=1.3)
    koyu = bpy.data.materials.get("m_koyu") or murekkep("m_koyu", ton=1.0, taban=0.9, doku=0.2)
    kok = bpy.data.objects.new(ad, None)
    koleksiyon("ince").objects.link(kok)
    W, L = 4.6 * olcek, 5.8 * olcek
    H = (3.0 if kat == 1 else 5.6) * olcek
    kutu(ad + "_duvar", (W, L, H + 0.6), (0, 0, H / 2 - 0.3), ak, kok, kol="ince")
    # kırma çatı: saçaklı taban dikdörtgeni, kısa mahya
    s = 0.45 * olcek
    me = bpy.data.meshes.new(ad + "_cati")
    bm = bmesh.new()
    a, b = W / 2 + s, L / 2 + s
    tepe = 1.5 * olcek
    taban_v = [bm.verts.new((x, y, 0)) for x, y in ((-a, -b), (a, -b), (a, b), (-a, b))]
    m1, m2 = bm.verts.new((0, -b * 0.35, tepe)), bm.verts.new((0, b * 0.35, tepe))
    bm.faces.new((taban_v[0], taban_v[1], m1))
    bm.faces.new((taban_v[1], taban_v[2], m2, m1))
    bm.faces.new((taban_v[2], taban_v[3], m2))
    bm.faces.new((taban_v[3], taban_v[0], m1, m2))
    bm.faces.new(taban_v[::-1])
    bm.to_mesh(me)
    bm.free()
    c = nesne(ad + "_cati", me, cati, kok, kol="ince")
    c.location = (0, 0, H)
    for px in ((-W * 0.22, W * 0.24) if W > 3.5 else (0,)):
        kutu(ad + f"_pen{px:.1f}", (0.55 * olcek, 0.12, 0.7 * olcek), (px, -L / 2 - 0.04, H * 0.62), koyu, kok, kol="ince")
    kutu(ad + "_kapi", (0.75 * olcek, 0.12, 1.5 * olcek), (W * 0.05, -L / 2 - 0.04, 0.45), koyu, kok, kol="ince")
    kok.location = konum
    kok.rotation_euler = (0, 0, math.radians(aci))
    return kok


def zemin(x, y):
    return yukseklik(x, y)


def yapilar():
    tas = murekkep("m_tas", ton=0.62, taban=0.22, doku=0.7, yikama=PALET["tas"], cizik=(1.2, 1.2, 1.2), olcek=1.4)
    murekkep("m_ahsap", ton=0.95, taban=0.4, doku=0.55, yikama="#5A4D42", cizik=(3.0, 3.0, 0.15), olcek=1.0)
    # kalkış limanı: mendirek, fener, rıhtım evleri, bağlı kayıklar
    serit_duvar("mendirek", egri(MENDIREK, 10), 4.2, -3.0, 2.4, tas)
    fener("fener_kalkis", (-2.0, 52.5, 2.2), 1.0)
    for i, (x, y, a, o, k) in enumerate([(-52, 2, -6, 1.0, 2), (-64, 9, 10, 0.95, 2), (-38, 4, -12, 0.9, 1),
                                          (-24, -5, 4, 1.0, 2), (-8, -3, -8, 0.9, 1), (8, -1, 6, 1.0, 2),
                                          (22, 2, -4, 0.85, 1), (-80, 16, 14, 0.9, 1), (-90, 2, -10, 1.0, 2),
                                          (-34, -24, 6, 0.9, 2), (-16, -30, -4, 0.85, 1), (2, -22, 8, 0.9, 2),
                                          (20, -28, -6, 0.85, 1), (36, -18, 4, 0.9, 2), (-54, -20, -8, 0.85, 1),
                                          (-70, -36, 10, 0.9, 2), (-4, -48, -2, 0.85, 1), (24, -50, 6, 0.9, 1)]):
        kiyi_evi(f"ev_k{i}", (x, y, zemin(x, y) - 0.3), a, o * 0.85, kat=k)
    sandal("sandal1", (-34, 22, 0.0), 70)
    sandal("sandal2", (-40, 26, 0.0), 60, 3.6)
    sandal("sandal3", (6, 20, 0.0), 100, 3.8)
    # varış limanı: taş iskele, fener, köy
    (ax, ay), (bx, by) = VARIS_ISKELE
    serit_duvar("iskele_varis", [(ax, ay), (bx, by)], 3.2, -3.0, 1.1, tas)
    serit_duvar("mendirek_varis", egri([(-26, 604), (-20, 590), (-10, 583)], 8), 3.4, -3.0, 2.0, tas)
    fener("fener_varis", (-9.5, 582.5, 2.0), 0.8)
    for i, (x, y, a, o, k) in enumerate([(8, 610, -4, 0.8, 2), (22, 614, 6, 0.85, 2), (36, 608, -10, 0.75, 1),
                                          (50, 616, 8, 0.85, 2), (15, 626, -6, 0.75, 1), (31, 629, 4, 0.8, 2),
                                          (64, 612, -14, 0.7, 1), (-4, 618, 10, 0.7, 1)]):
        kiyi_evi(f"ev_v{i}", (x, y, zemin(x, y) - 0.3), a, o, kat=k)
    sandal("sandal4", (32, 590, 0.0), 80, 3.6)


def ormanlar():
    m = murekkep("m_igne", ton=1.0, taban=0.55, doku=0.45, yikama=PALET["igne"], cizik=(0.8, 0.8, 0.5), olcek=1.6,
                 esik=(0.25, 0.8))
    my = murekkep("m_yaprak", ton=0.95, taban=0.45, doku=0.6, yikama="#6F7A63", cizik=(1.6, 1.6, 1.6), olcek=1.3,
                  esik=(0.2, 0.75))
    camlar = [ladin_mesh(f"cam{i}", 9.0, 50 + i) for i in range(6)]
    yaprakli = [yaprakli_mesh(f"yaprakli{i}", 8.0, 80 + i) for i in range(5)]
    for me in camlar:
        me.materials.append(m)
    for me in yaprakli:
        me.materials.append(my)
    r = random.Random(11)
    adet = deneme = 0
    while adet < 900 and deneme < 80000:
        deneme += 1
        x, y = r.uniform(-130, 130), r.uniform(-80, 820)
        z = yukseklik(x, y)
        if z < 3.0:
            continue
        if -14 < y < 26 and -96 < x < 44:     # rıhtım, kıyı evleri ve liman açık kalır
            continue
        if y <= -14 and min(math.hypot(x - hx_, y - hy_) for hx_, hy_ in MAHALLE) < 7.5:
            continue
        if 598 < y < 640 and -15 < x < 80:    # varış köyü
            continue
        e = 0.6
        gx = (yukseklik(x + e, y) - yukseklik(x - e, y)) / (2 * e)
        gy = (yukseklik(x, y + e) - yukseklik(x, y - e)) / (2 * e)
        if math.hypot(gx, gy) > 1.2:
            continue
        kume = noise.noise(Vector((x / 26.0, y / 26.0, 2.7)))
        olas = (0.2 + 0.8 * ss(4.0, 30.0, z)) * ss(-0.25, 0.25, kume) * sis_py(x, y, z) ** 0.5
        if r.random() > olas:
            continue
        boy = r.uniform(0.75, 1.3) * (1.35 if y < 30 else 1.0)
        kume_m = yaprakli if (z < 14 and r.random() < 0.5) else camlar
        o = bpy.data.objects.new(f"agac{adet}", kume_m[adet % len(kume_m)])
        koleksiyon("agac").objects.link(o)
        o.location = (x, y, z - 0.6)
        o.scale = (boy, boy, boy * r.uniform(0.95, 1.2))
        o.rotation_euler = (r.uniform(-0.04, 0.04), r.uniform(-0.04, 0.04), r.uniform(0, TAU))
        adet += 1
    print("AGAC", adet)


# ================================================================ tekne (yolcu): ayrı çizilir, sprite olur
def tekne(ad="tekne", yelken=1.0):
    """Tek direkli kıyı teknesi, kırmızı latin yelkeni. yelken: 0 sarılı, 1 tam açık."""
    kok = bpy.data.objects.new(ad, None)
    koleksiyon("ince").objects.link(kok)
    gov = bpy.data.materials.get("m_govde") or murekkep("m_govde", ton=0.6, taban=0.3, doku=0.4, yikama="#7A6550",
                                                        cizik=(2.5, 0.3, 2.5))
    gov_ak = bpy.data.materials.get("m_govde_ak") or murekkep("m_govde_ak", ton=0.3, taban=0.1, doku=0.4,
                                                              yikama=PALET["tas"], cizik=(2.5, 0.3, 2.5))
    me = bpy.data.meshes.new(ad + "_govde")
    bm = bmesh.new()
    L = 7.2
    kes = []
    for i in range(13):
        t = i / 12
        y = (t - 0.45) * L
        w = 1.25 * math.sin(math.pi * min(1.0, t * 1.08)) ** 0.62 + 0.03
        sh = 0.55 * (2 * t - 1) ** 2 + (0.35 if t > 0.92 else 0.0) * (t - 0.92) / 0.08
        kes.append([bm.verts.new((-w, y, 1.05 + sh)), bm.verts.new((-w * 0.75, y, 0.35 + sh * 0.4)),
                    bm.verts.new((0, y, -0.25 + sh * 0.3)), bm.verts.new((w * 0.75, y, 0.35 + sh * 0.4)),
                    bm.verts.new((w, y, 1.05 + sh))])
    for i in range(12):
        a, b = kes[i], kes[i + 1]
        for k in range(4):
            bm.faces.new((a[k], b[k], b[k + 1], a[k + 1]))
    bm.faces.new([k[0] for k in kes] [::-1] + [k[4] for k in kes])
    bm.to_mesh(me)
    bm.free()
    nesne(ad + "_govde", me, gov, kok, kol="ince")
    kutu(ad + "_kusak", (2.55, L * 0.86, 0.18), (0, -0.25, 0.95), gov_ak, kok, kol="ince")
    kutu(ad + "_direk", (0.16, 0.16, 7.2), (0, 0.9, 4.4), gov, kok, kol="ince")
    # latin yelkeni: çapraz seren + üçgen bez (aksan kırmızısı)
    yel = bpy.data.materials.get("m_yelken")
    if yel is None:
        yel, A = yeni_malzeme("m_yelken")
        dif = A.n("ShaderNodeBsdfDiffuse")
        s2r = A.n("ShaderNodeShaderToRGB")
        A.bag(dif.outputs[0], s2r.inputs[0])
        bw = A.n("ShaderNodeRGBToBW")
        A.bag(s2r.outputs["Color"], bw.inputs[0])
        g = A.aralik(bw.outputs[0], 0.15, 0.75, 1.0, 0.0)
        geo = A.n("ShaderNodeNewGeometry")
        nz = A.n("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 1.4
        A.bag(geo.outputs["Position"], nz.inputs["Vector"])
        t = A.aralik(nz.outputs["Fac"], 0.35, 0.65, 0.85, 1.0)
        renk = A.karis(A.m("MULTIPLY", g, 0.55), hx(PALET["aksan"]), hx("#6E2219"))
        renk = A.karis(A.m("MULTIPLY", A.m("SUBTRACT", 1.0, t), 0.6), renk, hx(PALET["kagit"]))
        em = A.n("ShaderNodeEmission")
        A.bag(renk, em.inputs["Color"])
        o = A.n("ShaderNodeOutputMaterial")
        A.bag(em.outputs[0], o.inputs["Surface"])
        yel.use_backface_culling = False
    ust, alt = Vector((0, -2.6, 9.6)), Vector((0, 3.7, 1.7))
    seren = ust - alt
    sr = kutu(ad + "_seren", (0.1, 0.1, seren.length), ((ust + alt) / 2).to_tuple(), gov, kok, kol="ince")
    sr.rotation_euler = seren.to_track_quat("Z", "Y").to_euler()
    if yelken > 0.02:
        # latin yelkeni: baş-alt (alt), kıç-tepe (ust), kıç-alt (ard); yarım açıkta ard başa doğru toplanır
        ard = alt.lerp(Vector((0, -3.1, 1.9)), yelken)
        tepe = alt.lerp(ust, 0.35 + 0.65 * yelken)
        meY = bpy.data.meshes.new(ad + "_bez")
        bm = bmesh.new()
        N = 10
        idx = {}
        for i in range(N + 1):
            for j in range(N + 1 - i):
                u, w = i / N, j / N
                p = alt + (tepe - alt) * u + (ard - alt) * w
                kar = math.sin(math.pi * min(1.0, u + w)) * math.sin(math.pi * max(u, 1e-3)) * 0.7 * yelken
                idx[(i, j)] = bm.verts.new((p.x + kar, p.y, p.z))
        for i in range(N):
            for j in range(N - i):
                a, b, c = idx[(i, j)], idx[(i, j + 1)], idx[(i + 1, j)]
                bm.faces.new((a, b, c))
                if (i + 1, j + 1) in idx:
                    bm.faces.new((b, idx[(i + 1, j + 1)], c))
        bm.to_mesh(meY)
        bm.free()
        for p in meY.polygons:
            p.use_smooth = True
        nesne(ad + "_bez", meY, yel, kok, kol="ince")
    else:
        sar = kutu(ad + "_sarili", (0.38, 0.38, seren.length * 0.8), ((ust + alt) / 2).to_tuple(), yel, kok, kol="ince")
        sar.rotation_euler = seren.to_track_quat("Z", "Y").to_euler()
    return kok


# ================================================================ kur, çek, yol dışarı
def rota_ornekle(rota, n):
    ince = [Vector(p) for p in egri(rota, 40)]
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
        out.append((q.x, q.y, 0.0))
    return out, top


def kur():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    KOL.clear()
    sc = bpy.context.scene
    isik()
    arazi()
    deniz()
    yapilar()
    ormanlar()
    kamera()
    ayarla(sc)
    return sc


def sprite_kur(yelken):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    KOL.clear()
    sc = bpy.context.scene
    isik()
    murekkep("m_tas", ton=0.62, taban=0.22, doku=0.7, yikama=PALET["tas"])
    tekne("tekne", yelken)
    c, ileri, yukari = kamera()
    c.data.ortho_scale = SPRITE_M
    c.location = Vector((0, 0, 3.2)) - ileri * 200
    ayarla(sc)
    sc.render.resolution_x = sc.render.resolution_y = SPRITE_PX
    sc.render.film_transparent = True
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.line_thickness = 1.0
    return sc


def ekran(sc, p):
    from bpy_extras.object_utils import world_to_camera_view
    q = world_to_camera_view(sc, sc.camera, Vector(p))
    return q.x, 1 - q.y


def yol_disari(sc, yol_json):
    dg = bpy.context.evaluated_depsgraph_get()
    cam = sc.camera
    ileri = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    veri = dict(en=sc.render.resolution_x, boy=sc.render.resolution_y, metre_px=sc.render.resolution_x / GEN, rotalar={})
    for ad, rota in (("pomodoro", ROTA_POMODORO), ("kronometre", ROTA_KRONOMETRE)):
        pts, top = rota_ornekle(rota, 700)
        cikti = []
        for (x, y, z) in pts:
            u, v = ekran(sc, (x, y, 1.2))
            hit, loc, nrm, idx, ob, mtx = sc.ray_cast(dg, Vector((x, y, 1.2)) - ileri * 0.5, -ileri)
            ortu = bool(hit and ob and ob.name not in ("deniz",))
            cikti.append([round(u, 5), round(v, 5), round(sis_py(x, y, 1.0), 3), 1 if ortu else 0, round(x, 2), round(y, 2)])
        veri["rotalar"][ad] = dict(uzunluk_m=round(top, 1), nokta=cikti)
    u, v = ekran(sc, (VARIS_ISKELE[1][0], VARIS_ISKELE[1][1], 2.0))
    veri["varis"] = [round(u, 5), round(v, 5)]
    with open(yol_json, "w", encoding="utf-8") as f:
        json.dump(veri, f)


SPRITE_M, SPRITE_PX = 20.0, 160

if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["resim", "onizleme.png"]
    komut = a[0]
    if komut in ("resim", "yol") and len(a) > 2:
        k = float(a[2])
        EN, BOY = int(EN * k), int(BOY * k)
    if komut == "resim":
        sc = kur()
        sc.render.filepath = os.path.abspath(a[1])
        bpy.ops.render.render(write_still=True)
        print("RESIM_OK", a[1])
    elif komut == "yol":
        sc = kur()
        yol_disari(sc, os.path.abspath(a[1]))
        print("YOL_OK", a[1])
    elif komut == "tekne":
        # tekne <klasor> : 16 yön x (açık, yarım, sarılı) yelken, şeffaf PNG
        os.makedirs(a[1], exist_ok=True)
        for yk, ek in ((1.0, "a"), (0.5, "y"), (0.0, "s")):
            sc = sprite_kur(yk)
            kok = bpy.data.objects["tekne"]
            for i in range(16):
                kok.rotation_euler = (0, 0, -TAU * i / 16)
                sc.render.filepath = os.path.join(os.path.abspath(a[1]), f"tekne_{ek}_{i:02d}.png")
                bpy.ops.render.render(write_still=True)
        print("TEKNE_OK", a[1])
    elif komut == "kaydet":
        kur()
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a[1]))
        print("KAYDET_OK", a[1])
