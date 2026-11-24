"""Kertik sahnesi: kuzey ışığında guaş boyalı, yaşayan bir fiyort (Blender 5.3, EEVEE).

Tarz: ışık seçilmiştir (sıcak ana ışık, serin gökyüzü dolgusu), uzaklık hava
perspektifiyle soluklaşır, yüzeyler mat pigment gibidir, çekim sonunda
anizotropik Kuwahara filtresi kareyi fırça darbesine çevirir. Gren ve kâğıt
dokusu videoya gömülmez; uygulamada ince bir katman olarak eklenir.

Kullanım:
  blender -b --factory-startup --python fiyort.py -- kare  <vakit> <durgunluk> <kare> <cikti.png> [olcek]
  blender -b --factory-startup --python fiyort.py -- dongu <vakit> <durgunluk> <klasor>
  blender -b --factory-startup --python fiyort.py -- kaydet <vakit> <durgunluk> <dosya.blend>
vakit: safak | gun | aksam | gece      durgunluk: S0 (rüzgâr) .. S3 (ayna)
"""
import bpy
import bmesh
import math
import os
import random
import sys
from mathutils import Vector, noise

KOK = os.path.dirname(os.path.abspath(__file__))
FPS = 12
F = 192            # 16 sn döngü
EN, BOY = 720, 1440
TAU = math.tau


def hx(c, a=1.0):
    c = c.lstrip("#")
    s = [int(c[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in s]
    return (*lin, a)


VAKITLER = {
    "aksam": dict(
        zenit="#3B4C86", orta="#A595C2", ufuk="#FFC89C", ufuk_soguk="#CDB6CF", gunes_hale="#FFE2B4",
        pus="#D6B9C2", pus_mesafe=9000.0,
        gunes_renk="#FFA866", gunes_guc=8.0, gunes_yon=(70.0, 9.0),   # azimut (sağa), yükseklik
        dunya_guc=0.7, dolgu="#3D5BA0", dolgu_alt="#7A7EAA", dolgu_guc=0.5, bulut_isik="#FFC9A0", bulut_golge="#8E7C9E",
        su_derin="#1A2B3D", pencere=5.0,
    ),
    "gun": dict(
        zenit="#3E6FA3", orta="#86AFCB", ufuk="#DCE7E4", gunes_hale="#F4F1E2",
        pus="#B9CCD3", pus_mesafe=12000.0,
        gunes_renk="#FFF2DC", gunes_guc=5.0, gunes_yon=(48.0, 42.0),
        dunya_guc=1.0, bulut_isik="#FFFFFF", bulut_golge="#A9B8C8",
        su_derin="#1C3A4A", pencere=0.0,
    ),
    "safak": dict(
        zenit="#5B6C9A", orta="#B7A7C2", ufuk="#F6CDB8", gunes_hale="#FFE6CF",
        pus="#CDB8C4", pus_mesafe=7000.0,
        gunes_renk="#FFC6A0", gunes_guc=3.0, gunes_yon=(-55.0, 6.0),
        dunya_guc=0.9, bulut_isik="#FFD6C2", bulut_golge="#9A93B5",
        su_derin="#2A3550", pencere=0.0,
    ),
    "gece": dict(
        zenit="#0C1428", orta="#1C2A48", ufuk="#33456A", gunes_hale="#5C6E92",
        pus="#25324F", pus_mesafe=8000.0,
        gunes_renk="#9DB3E0", gunes_guc=0.9, gunes_yon=(-35.0, 28.0),
        dunya_guc=0.35, bulut_isik="#6F7FA6", bulut_golge="#2A3554",
        su_derin="#070D18", pencere=14.0,
    ),
}

DURGUNLUK = {
    "S0": dict(genlik=0.20, chop=1.0, salla=1.0, duman_egim=0.9),
    "S1": dict(genlik=0.07, chop=0.35, salla=0.45, duman_egim=0.45),
    "S2": dict(genlik=0.025, chop=0.08, salla=0.15, duman_egim=0.2),
    "S3": dict(genlik=0.006, chop=0.0, salla=0.04, duman_egim=0.08),
}

DALGALAR = [  # (dalga boyu m, yön derece, döngüde tur, ağırlık, faz)
    (5.2, 0.0, 1, 1.00, 0.0), (3.3, 14.0, 2, 0.60, 1.3), (2.4, -19.0, 2, 0.45, 2.1), (8.0, 6.0, 1, 0.55, 4.0),
]
CHOP = [(1.05, 27.0, 3, 0.40, 0.7), (0.75, -33.0, 4, 0.32, 3.3), (1.4, 52.0, 3, 0.28, 5.1)]


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
        self.gir(d, 0, f) if not isinstance(f, (int, float)) else None
        if isinstance(f, (int, float)):
            d.inputs[0].default_value = f
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


def pus_ekle(A, yuzey, V):
    """Hava perspektifi: uzaklıkla pus rengine karışan yayım."""
    cam = A.n("ShaderNodeCameraData")
    d = A.m("DIVIDE", cam.outputs["View Distance"], V["pus_mesafe"])
    f = A.m("SUBTRACT", 1.0, A.m("EXPONENT", A.m("MULTIPLY", d, -1.0)))
    f = A.m("MULTIPLY", f, 0.85, clamp=True)
    em = A.n("ShaderNodeEmission")
    em.inputs["Color"].default_value = hx(V["pus"])
    em.inputs["Strength"].default_value = 1.0
    mx = A.n("ShaderNodeMixShader")
    A.bag(f, mx.inputs[0])
    A.bag(yuzey, mx.inputs[1])
    A.bag(em.outputs[0], mx.inputs[2])
    return mx.outputs[0]


def cikis(A, s):
    o = A.n("ShaderNodeOutputMaterial")
    A.bag(s, o.inputs["Surface"])


def mat_boya(ad, renk, puruz=0.85, V=None, varyasyon=0.0, olcek=2.0, bump=0.0, pus=True):
    """Mat pigment yüzey; isteğe bağlı ton oynaması ve kabartma."""
    m, A = yeni_malzeme(ad)
    p = A.n("ShaderNodeBsdfPrincipled")
    p.inputs["Roughness"].default_value = puruz
    p.inputs["Specular IOR Level"].default_value = 0.25
    if varyasyon > 0:
        tx = A.n("ShaderNodeTexNoise")
        tx.inputs["Scale"].default_value = olcek
        tx.inputs["Detail"].default_value = 6.0
        c = A.karis(A.aralik(tx.outputs["Fac"], 0.3, 0.7), tuple(x * (1 - varyasyon) for x in hx(renk)[:3]) + (1,),
                    tuple(min(1, x * (1 + varyasyon)) for x in hx(renk)[:3]) + (1,))
        A.bag(c, p.inputs["Base Color"])
        if bump > 0:
            b = A.n("ShaderNodeBump")
            b.inputs["Strength"].default_value = bump
            A.bag(tx.outputs["Fac"], b.inputs["Height"])
            A.bag(b.outputs["Normal"], p.inputs["Normal"])
    else:
        p.inputs["Base Color"].default_value = hx(renk)
    s = p.outputs[0]
    if pus and V:
        s = pus_ekle(A, s, V)
    cikis(A, s)
    return m


# ================================================================ mesh yardımcıları
def nesne(ad, me, mat=None, ebeveyn=None):
    o = bpy.data.objects.new(ad, me)
    bpy.context.scene.collection.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    if ebeveyn:
        o.parent = ebeveyn
    return o


def kutu(ad, boyut, konum, mat, ebeveyn=None, don=(0, 0, 0)):
    me = bpy.data.meshes.new(ad)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * boyut[0], v.co.y * boyut[1], v.co.z * boyut[2]))
    bm.to_mesh(me)
    bm.free()
    o = nesne(ad, me, mat, ebeveyn)
    o.location = konum
    o.rotation_euler = don
    return o


def silindir(ad, r, h, konum, mat, ebeveyn=None, kose=8, don=(0, 0, 0)):
    me = bpy.data.meshes.new(ad)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=kose, radius1=r, radius2=r, depth=h)
    bm.to_mesh(me)
    bm.free()
    o = nesne(ad, me, mat, ebeveyn)
    o.location = konum
    o.rotation_euler = don
    return o


def prizma(ad, profil, uzunluk, mat, ebeveyn=None):
    """XZ profilini y boyunca 0..uzunluk uzatır."""
    me = bpy.data.meshes.new(ad)
    n = len(profil)
    v = [(x, 0.0, z) for x, z in profil] + [(x, uzunluk, z) for x, z in profil]
    f = [list(range(n)), list(range(n, 2 * n))[::-1]]
    for i in range(n):
        j = (i + 1) % n
        f.append([i, n + i, n + j, j])
    me.from_pydata(v, [], f)
    me.validate()
    me.update()
    o = nesne(ad, me, mat, ebeveyn)
    return o


def duzgun_golge(o):
    for p in o.data.polygons:
        p.use_smooth = True


# ================================================================ arazi
def sirtli(p, okt=7):
    s, a, w = 0.0, 0.55, 1.0
    q = Vector(p)
    for _ in range(okt):
        n = 1.0 - abs(noise.noise(q, noise_basis="PERLIN_ORIGINAL"))
        n = n * n * w
        w = max(0.0, min(1.0, n * 2.0))
        s += n * a
        a *= 0.5
        q = q * 2.03
    return s


def fiyort_yukseklik(x, y):
    merkez = 55.0 * math.sin(y / 1100.0 + 0.6) - 30.0
    yari = 330.0 - 200.0 * min(1.0, max(0.0, (y - 250.0) / 4200.0))
    d = abs(x - merkez) - yari
    if y > 5200:
        d = max(d, (y - 5200) * 0.9)
    if d <= 0:
        return -25.0
    duvar = 1.0 - math.exp(-d / 85.0)
    p = (x / 760.0 + 13.1, y / 760.0 - 4.7, 0.31)
    r = sirtli(p)
    zarf = 120.0 + 820.0 * min(1.0, (y / 4500.0)) ** 1.3
    h = duvar * zarf * (0.55 + 0.95 * r)
    h += 18.0 * noise.noise((x / 90.0, y / 90.0, 2.0))
    return h - 4.0


def arazi(V):
    nx, ny = 520, 320
    vs, fs = [], []
    for j in range(ny):
        t = j / (ny - 1)
        y = 230.0 + 6500.0 * t ** 1.9
        for i in range(nx):
            x = -1900.0 + 3800.0 * i / (nx - 1)
            vs.append((x, y, fiyort_yukseklik(x, y)))
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            fs.append([a, a + 1, a + nx + 1, a + nx])
    me = bpy.data.meshes.new("dag")
    me.from_pydata(vs, [], fs)
    me.update()
    o = nesne("dag", me, dag_malzemesi(V))
    o.visible_shadow = False   # ışık seçilir: dağ duvarı ön plana gölge düşürmez
    duzgun_golge(o)
    return o


def dag_malzemesi(V):
    m, A = yeni_malzeme("m_dag")
    geo = A.n("ShaderNodeNewGeometry")
    sep = A.n("ShaderNodeSeparateXYZ")
    A.bag(geo.outputs["Position"], sep.inputs[0])
    nsep = A.n("ShaderNodeSeparateXYZ")
    A.bag(geo.outputs["Normal"], nsep.inputs[0])
    z, nz = sep.outputs[2], nsep.outputs[2]
    tx = A.n("ShaderNodeTexNoise")
    tx.inputs["Scale"].default_value = 0.012
    tx.inputs["Detail"].default_value = 8.0
    tx.inputs["Roughness"].default_value = 0.62
    A.bag(geo.outputs["Position"], tx.inputs["Vector"])
    gur = tx.outputs["Fac"]
    # orman (alçak, yumuşak eğim), kaya (dik), çayır, kar (yüksek, yumuşak)
    orman, orman2, cayir = hx("#17302C"), hx("#2A4A3C"), hx("#5C7448")
    kaya, kaya2 = hx("#4A5466"), hx("#6A7182")
    kar = hx("#EDEAF2")
    dik = A.aralik(nz, 0.32, 0.6, 1.0, 0.0)               # 1 = uçurum
    yuk = A.m("ADD", z, A.m("MULTIPLY", A.m("SUBTRACT", gur, 0.5), 260.0))
    ormanr = A.karis(A.aralik(gur, 0.3, 0.7), orman, orman2)
    ust = A.karis(A.aralik(gur, 0.4, 0.62), cayir, kaya2)
    renk = A.karis(A.aralik(yuk, 170.0, 330.0), ormanr, ust)
    renk = A.karis(A.m("MULTIPLY", dik, A.aralik(yuk, 60.0, 200.0)), renk, kaya)
    karf = A.m("MULTIPLY", A.aralik(yuk, 520.0, 640.0), A.aralik(nz, 0.5, 0.72))
    renk = A.karis(karf, renk, kar)
    p = A.n("ShaderNodeBsdfPrincipled")
    A.bag(renk, p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.95
    p.inputs["Specular IOR Level"].default_value = 0.15
    b = A.n("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.35
    tx2 = A.n("ShaderNodeTexNoise")
    tx2.inputs["Scale"].default_value = 0.08
    tx2.inputs["Detail"].default_value = 10.0
    A.bag(geo.outputs["Position"], tx2.inputs["Vector"])
    A.bag(tx2.outputs["Fac"], b.inputs["Height"])
    A.bag(b.outputs["Normal"], p.inputs["Normal"])
    cikis(A, pus_ekle(A, p.outputs[0], V))
    return m


def burun(V):
    """Sol ön: kulübenin oturduğu kayalık çayırlı burun."""
    vs, fs = [], []
    nx, ny = 90, 70
    for j in range(ny):
        y = 30.0 + 70.0 * j / (ny - 1)
        for i in range(nx):
            x = -46.0 + 46.0 * i / (nx - 1)
            u = (x + 46.0) / 46.0               # 0 sol, 1 kıyı ucu
            kenar = 1.0 - u
            h = 9.0 * kenar ** 1.4 + 2.2 * noise.noise((x / 7.0, y / 7.0, 0.5)) * kenar
            h += 1.2 * noise.noise((x / 2.2, y / 2.2, 3.0))
            on = (y - 30.0) / 70.0
            h *= min(1.0, on * 2.2 + 0.25)
            h -= 0.7
            if u > 0.86:
                h -= (u - 0.86) * 40.0
            vs.append((x, y, h))
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            fs.append([a, a + 1, a + nx + 1, a + nx])
    me = bpy.data.meshes.new("burun")
    me.from_pydata(vs, [], fs)
    me.update()
    m, A = yeni_malzeme("m_burun")
    geo = A.n("ShaderNodeNewGeometry")
    nsep = A.n("ShaderNodeSeparateXYZ")
    A.bag(geo.outputs["Normal"], nsep.inputs[0])
    sep = A.n("ShaderNodeSeparateXYZ")
    A.bag(geo.outputs["Position"], sep.inputs[0])
    tx = A.n("ShaderNodeTexNoise")
    tx.inputs["Scale"].default_value = 0.35
    tx.inputs["Detail"].default_value = 8.0
    A.bag(geo.outputs["Position"], tx.inputs["Vector"])
    cim = A.karis(A.aralik(tx.outputs["Fac"], 0.35, 0.7), hx("#4F6A36"), hx("#8B8A4E"))
    kaya = A.karis(A.aralik(tx.outputs["Fac"], 0.4, 0.6), hx("#4A4850"), hx("#6E6A70"))
    renk = A.karis(A.aralik(nsep.outputs[2], 0.62, 0.85, 1.0, 0.0), cim, kaya)
    renk = A.karis(A.aralik(sep.outputs[2], 0.6, -0.2), renk, hx("#3A3A40"))  # ıslak kıyı
    p = A.n("ShaderNodeBsdfPrincipled")
    A.bag(renk, p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.92
    p.inputs["Specular IOR Level"].default_value = 0.2
    cikis(A, pus_ekle(A, p.outputs[0], V))
    o = nesne("burun", me, m)
    duzgun_golge(o)
    return o


def kaya_tasi(ad, konum, olcek, mat, tohum):
    me = bpy.data.meshes.new(ad)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    r = random.Random(tohum)
    ofs = Vector((r.uniform(0, 50), r.uniform(0, 50), r.uniform(0, 50)))
    for v in bm.verts:
        d = noise.noise(v.co * 1.3 + ofs) * 0.28 + noise.noise(v.co * 3.1 + ofs) * 0.1
        v.co = v.co * (1.0 + d)
        v.co.z *= 0.62
    bm.to_mesh(me)
    bm.free()
    o = nesne(ad, me, mat)
    o.location = konum
    o.scale = olcek
    o.rotation_euler = (0, 0, r.uniform(0, TAU))
    duzgun_golge(o)
    return o


# ================================================================ kulübe (rorbu)
def kulube(V, konum, aci):
    kok = bpy.data.objects.new("kulube", None)
    bpy.context.scene.collection.objects.link(kok)
    kok.location = konum
    kok.rotation_euler = (0, 0, math.radians(aci))

    W, L, Hw, egim = 4.6, 6.6, 2.8, math.radians(40)
    Hr = Hw + (W / 2) * math.tan(egim)

    # kırmızı tahta kaplama: dikey tahtalar (bump), hafif yıpranmış ton
    m, A = yeni_malzeme("m_kirmizi")
    tc = A.n("ShaderNodeTexCoord")
    sep = A.n("ShaderNodeSeparateXYZ")
    A.bag(tc.outputs["Object"], sep.inputs[0])
    xy = A.m("ADD", sep.outputs[0], sep.outputs[1])
    birles = A.n("ShaderNodeCombineXYZ")
    A.bag(xy, birles.inputs[0])
    dal = A.n("ShaderNodeTexWave")
    dal.wave_type = "BANDS"
    dal.bands_direction = "X"
    dal.wave_profile = "SAW"
    dal.inputs["Scale"].default_value = 1.0 / 0.19 / 1.0
    dal.inputs["Distortion"].default_value = 0.0
    A.bag(birles.outputs[0], dal.inputs["Vector"])
    tx = A.n("ShaderNodeTexNoise")
    tx.inputs["Scale"].default_value = 3.0
    tx.inputs["Detail"].default_value = 9.0
    A.bag(tc.outputs["Object"], tx.inputs["Vector"])
    renk = A.karis(A.aralik(tx.outputs["Fac"], 0.3, 0.75), hx("#7E2A22"), hx("#A23B2C"))
    p = A.n("ShaderNodeBsdfPrincipled")
    A.bag(renk, p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.8
    p.inputs["Specular IOR Level"].default_value = 0.3
    b = A.n("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.6
    b.inputs["Distance"].default_value = 0.02
    A.bag(A.aralik(dal.outputs["Fac"], 0.88, 0.97, 1.0, 0.0), b.inputs["Height"])
    A.bag(b.outputs["Normal"], p.inputs["Normal"])
    cikis(A, pus_ekle(A, p.outputs[0], V))
    kirmizi = m

    beyaz = mat_boya("m_beyaz", "#EDE7DA", 0.7, V)
    koyu_cati = mat_boya("m_cati", "#2B2D33", 0.9, V, varyasyon=0.25, olcek=6.0, bump=0.3)
    tahta = mat_boya("m_tahta", "#6B5440", 0.9, V, varyasyon=0.3, olcek=4.0, bump=0.2)
    direk = mat_boya("m_direk", "#3D3129", 0.95, V, varyasyon=0.2, olcek=5.0)
    tas = mat_boya("m_tas", "#5C5856", 0.95, V, varyasyon=0.35, olcek=8.0, bump=0.4)
    kapi = mat_boya("m_kapi", "#3E5248", 0.7, V)

    # cam: gündüz koyu, gece sıcak ışık
    m, A = yeni_malzeme("m_cam")
    p = A.n("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = hx("#1E2A33")
    p.inputs["Roughness"].default_value = 0.08
    p.inputs["Emission Color"].default_value = hx("#FFB25E")
    p.inputs["Emission Strength"].default_value = V["pencere"]
    cikis(A, pus_ekle(A, p.outputs[0], V))
    cam = m

    govde = prizma("kulube_govde", [(-W / 2, 0), (W / 2, 0), (W / 2, Hw), (0, Hr), (-W / 2, Hw)], L, kirmizi, kok)
    govde.location = (0, 0, 0)

    # çatı: iki levha, saçak ve alın taşması
    sacak, alin, kal = 0.45, 0.38, 0.16
    eg = (W / 2 + sacak) / math.cos(egim)
    xc = (W / 2 + sacak) / 2
    cz = Hr - xc * math.tan(egim) + kal / (2 * math.cos(egim))
    for yon in (-1, 1):
        kutu(f"cati_{yon}", (eg, L + 2 * alin, kal), (yon * xc, L / 2, cz), koyu_cati, kok, don=(0, yon * egim, 0))
    kutu("mahya", (0.3, L + 2 * alin + 0.02, 0.16), (0, L / 2, Hr + 0.1), koyu_cati, kok)

    # beyaz pervazlar: köşe tahtaları ve alın tahtaları
    for x in (-W / 2, W / 2):
        for y in (0.0, L):
            kutu("kose", (0.16, 0.16, Hw), (x, y, Hw / 2), beyaz, kok)
    uz = (W / 2 + 0.3) / math.cos(egim)
    xb = (W / 2 + 0.3) / 2
    for y in (-alin + 0.02, L + alin - 0.02):
        for yon in (-1, 1):
            kutu("alin_tahtasi", (uz, 0.08, 0.24), (yon * xb, y, Hr - xb * math.tan(egim) + 0.05), beyaz, kok,
                 don=(0, yon * egim, 0))

    # pencereler: beyaz çerçeve, dört bölmeli cam
    def pencere(ad, merkez, yon_normal, gen=1.0, yuk=1.15):
        nx, ny = yon_normal
        rot = math.atan2(nx, -ny)
        p0 = Vector(merkez)
        dis = Vector((nx, ny, 0)) * 0.05
        kutu(ad + "_cer", (gen + 0.2, 0.08, yuk + 0.2), p0 + dis, beyaz, kok, don=(0, 0, rot))
        kutu(ad + "_cam", (gen, 0.08, yuk), p0 + dis * 1.6, cam, kok, don=(0, 0, rot))
        kutu(ad + "_d", (0.07, 0.1, yuk), p0 + dis * 2.0, beyaz, kok, don=(0, 0, rot))
        kutu(ad + "_y", (gen, 0.1, 0.07), p0 + dis * 2.0, beyaz, kok, don=(0, 0, rot))

    pencere("pen_yan1", (-W / 2, 1.9, 1.55), (-1, 0))
    pencere("pen_yan2", (-W / 2, 4.7, 1.55), (-1, 0))
    pencere("pen_on", (0.95, 0.0, 1.55), (0, -1), 0.8, 1.0)
    pencere("pen_tavan", (0, 0.0, Hw + 0.75), (0, -1), 0.7, 0.7)
    pencere("pen_arka", (W / 2, 3.3, 1.55), (1, 0))
    # kapı ön alınlıkta
    kutu("kapi", (0.9, 0.08, 2.0), (-0.9, -0.05, 1.0), kapi, kok)
    kutu("kapi_cer", (1.08, 0.06, 2.12), (-0.9, -0.03, 1.06), beyaz, kok)
    # baca
    kutu("baca", (0.55, 0.55, 1.6), (-0.9, L * 0.68, Hr - 0.1), tas, kok)
    kutu("baca_bas", (0.68, 0.68, 0.12), (-0.9, L * 0.68, Hr + 0.72), tas, kok)
    # güverte ve kazıklar (önü suyun üstünde)
    kutu("guverte", (W + 1.6, L + 3.2, 0.18), (0.3, L / 2 - 1.2, -0.12), tahta, kok)
    for x in (-W / 2 - 0.5, 0.3, W / 2 + 1.1):
        for y in (-2.6, -0.2, 2.4, 5.0, L + 0.3):
            silindir("kazik", 0.13, 4.2, (x, y, -2.2), direk, kok, kose=7)
    # merdiven/çit küçük dokunuş
    for i in range(6):
        kutu("korkuluk", (0.07, 0.07, 0.9), (W / 2 + 1.05, -2.6 + i * 0.6, 0.45), beyaz, kok)
    kutu("korkuluk_ust", (0.08, 3.2, 0.08), (W / 2 + 1.05, -1.1, 0.9), beyaz, kok)
    return kok


# ================================================================ iskele, kayık
def iskele(V, bas, son, gen=1.6):
    tahta = bpy.data.materials["m_tahta"]
    direk = bpy.data.materials["m_direk"]
    a, b = Vector((bas[0], bas[1], 0.0)), Vector((son[0], son[1], 0.0))
    d = b - a
    uz = d.length
    yon = math.atan2(d.x, d.y)
    n = int(uz / 0.26)
    dikey = Vector((d.y, -d.x, 0)).normalized()
    r = random.Random(4)
    for i in range(n):
        u = (i + 0.5) / n
        p = a + d * u
        kutu("tahta", (gen * r.uniform(0.95, 1.05), 0.22, 0.07), (p.x, p.y, 0.95 + r.uniform(-0.015, 0.015)), tahta,
             don=(r.uniform(-0.01, 0.01), 0, -yon + r.uniform(-0.02, 0.02)))
    k = max(2, int(uz / 2.4))
    for i in range(k + 1):
        p = a + d * (i / k)
        for s in (-1, 1):
            q = p + dikey * s * gen * 0.45
            silindir("iskele_kazik", 0.11, 3.6, (q.x, q.y, -0.75), direk, kose=7)
    for s in (-1, 1):
        q = a + d * 0.5 + dikey * s * gen * 0.45
        kutu("kiris", (0.12, uz, 0.16), (q.x, q.y, 0.84), direk, don=(0, 0, -yon))


def kayik(V, konum, aci):
    """Kuzey tipi sandal: iki ucu sivri, kalkık burun, beyaz gövde, mavi şerit."""
    L, B, D = 4.6, 1.45, 0.62
    n_ust, n_kes = 24, 9
    vs, fs = [], []
    for i in range(n_ust):
        u = i / (n_ust - 1)
        y = (u - 0.5) * L
        en = B / 2 * math.sin(math.pi * u) ** 0.75
        kalk = 0.38 * (abs(u - 0.5) * 2) ** 2.6
        for j in range(n_kes):
            v = j / (n_kes - 1)
            th = math.pi * v
            x = -math.cos(th) * en
            z = -math.sin(th) * D * (0.35 + 0.65 * math.sin(math.pi * u) ** 0.5) + kalk
            vs.append((x, y, z))
    for i in range(n_ust - 1):
        for j in range(n_kes - 1):
            a = i * n_kes + j
            fs.append([a, a + n_kes, a + n_kes + 1, a + 1])
    me = bpy.data.meshes.new("kayik")
    me.from_pydata(vs, [], fs)
    me.update()
    m, A = yeni_malzeme("m_kayik")
    tc = A.n("ShaderNodeTexCoord")
    sep = A.n("ShaderNodeSeparateXYZ")
    A.bag(tc.outputs["Object"], sep.inputs[0])
    serit = A.m("MULTIPLY", A.aralik(sep.outputs[2], -0.2, -0.16, 0.0, 1.0, "LINEAR"),
                A.aralik(sep.outputs[2], -0.08, -0.04, 1.0, 0.0, "LINEAR"))
    renk = A.karis(serit, hx("#ECE6D8"), hx("#3F5C7A"))
    renk = A.karis(A.aralik(sep.outputs[2], -0.5, -0.42, 1.0, 0.0, "LINEAR"), renk, hx("#5A3A30"))
    p = A.n("ShaderNodeBsdfPrincipled")
    A.bag(renk, p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.6
    cikis(A, pus_ekle(A, p.outputs[0], V))
    o = nesne("kayik", me, m)
    o.data.materials[0].use_backface_culling = False
    duzgun_golge(o)
    ic = mat_boya("m_kayik_ic", "#7A5E45", 0.9, V)
    kutu("oturak", (B * 0.8, 0.22, 0.05), (0, 0.3, -0.12), ic, o)
    kutu("oturak2", (B * 0.7, 0.22, 0.05), (0, -1.1, -0.12), ic, o)
    for s in (-1, 1):
        kutu("kurek", (0.06, 2.6, 0.03), (s * 0.55, 0.2, 0.02), ic, o, don=(0, s * 0.18, s * 0.12))
    o.location = konum
    o.rotation_euler = (0, 0, math.radians(aci))
    return o


# ================================================================ ağaçlar
def ladin(ad, konum, boy, mat, tohum):
    """Ladin: sarkık dal katmanları, düzensiz kenar."""
    r = random.Random(tohum)
    kok = bpy.data.objects.new(ad, None)
    bpy.context.scene.collection.objects.link(kok)
    kok.location = konum
    me = bpy.data.meshes.new(ad + "_m")
    bm = bmesh.new()
    kat = int(7 + boy / 2.2)
    for k in range(kat):
        t = k / (kat - 1)
        z = boy * (0.12 + 0.86 * t)
        rad = boy * 0.23 * (1 - t) ** 0.95 + 0.25
        yuk = boy * 0.2 * (1 - t * 0.5)
        seg = 14
        alt = []
        tepe = bm.verts.new((0, 0, z + yuk * 0.65))
        for s in range(seg):
            a = TAU * s / seg + r.uniform(-0.12, 0.12)
            rr = rad * r.uniform(0.72, 1.12)
            alt.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, z - yuk * 0.35 + r.uniform(-0.25, 0.1) * yuk)))
        for s in range(seg):
            bm.faces.new((tepe, alt[s], alt[(s + 1) % seg]))
        bm.faces.new(alt[::-1])
    bm.to_mesh(me)
    bm.free()
    o = nesne(ad + "_dal", me, mat, kok)
    silindir(ad + "_govde", boy * 0.03 + 0.08, boy * 0.4, (0, 0, boy * 0.2), bpy.data.materials["m_direk"], kok, kose=6)
    kok.rotation_euler = (r.uniform(-0.03, 0.03), r.uniform(-0.03, 0.03), r.uniform(0, TAU))
    return kok


def igne_malzemesi(V):
    m, A = yeni_malzeme("m_igne")
    geo = A.n("ShaderNodeNewGeometry")
    sep = A.n("ShaderNodeSeparateXYZ")
    A.bag(geo.outputs["Normal"], sep.inputs[0])
    tx = A.n("ShaderNodeTexNoise")
    tx.inputs["Scale"].default_value = 2.5
    tx.inputs["Detail"].default_value = 8.0
    A.bag(geo.outputs["Position"], tx.inputs["Vector"])
    renk = A.karis(A.aralik(tx.outputs["Fac"], 0.3, 0.7), hx("#1D3326"), hx("#3A5634"))
    renk = A.karis(A.aralik(sep.outputs[2], 0.2, 0.9, 0.0, 0.35), renk, hx("#6E7F4A"))
    p = A.n("ShaderNodeBsdfPrincipled")
    A.bag(renk, p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.9
    p.inputs["Specular IOR Level"].default_value = 0.1
    b = A.n("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.8
    A.bag(tx.outputs["Fac"], b.inputs["Height"])
    A.bag(b.outputs["Normal"], p.inputs["Normal"])
    cikis(A, pus_ekle(A, p.outputs[0], V))
    return m


# ================================================================ su, gök, bulut, duman
def su(V, D):
    me = bpy.data.meshes.new("su")
    S = 12000
    me.from_pydata([(-S, -10, 0), (S, -10, 0), (S, S, 0), (-S, S, 0)], [], [[0, 1, 2, 3]])
    m, A = yeni_malzeme("m_su")
    geo = A.n("ShaderNodeNewGeometry")
    sep = A.n("ShaderNodeSeparateXYZ")
    A.bag(geo.outputs["Position"], sep.inputs[0])
    x, y = sep.outputs[0], sep.outputs[1]
    tau = A.n("ShaderNodeValue")
    tau.name = tau.label = "tau"

    def toplam(liste, carpan):
        s, w = None, 0.0
        for lam, deg, tur, wt, ph in liste:
            k = TAU / lam
            dx, dy = math.sin(math.radians(deg)) * k, -math.cos(math.radians(deg)) * k
            arg = A.m("MULTIPLY_ADD", x, dx, A.m("MULTIPLY_ADD", y, dy, A.m("MULTIPLY_ADD", tau.outputs[0], -TAU * tur, ph)))
            t = A.m("MULTIPLY", A.m("SINE", arg), wt * carpan)
            s = t if s is None else A.m("ADD", s, t)
            w += wt * carpan
        return s, w

    ana, w1 = toplam(DALGALAR, 1.0)
    kir, w2 = toplam(CHOP, D["chop"]) if D["chop"] > 0 else (None, 0.0)
    h = ana if kir is None else A.m("ADD", ana, kir)
    h = A.m("MULTIPLY", h, D["genlik"] / (w1 + w2))
    # uzakta dalga söner (aliasing yerine sakin ayna)
    cam = A.n("ShaderNodeCameraData")
    son = A.aralik(cam.outputs["View Distance"], 40.0, 900.0, 1.0, 0.15)
    h = A.m("MULTIPLY", h, son)
    b = A.n("ShaderNodeBump")
    b.inputs["Distance"].default_value = 1.0
    b.inputs["Strength"].default_value = 1.0
    A.bag(h, b.inputs["Height"])
    p = A.n("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = hx(V["su_derin"])
    p.inputs["Roughness"].default_value = 0.04
    p.inputs["Specular IOR Level"].default_value = 0.5
    A.bag(b.outputs["Normal"], p.inputs["Normal"])
    ayna = A.n("ShaderNodeBsdfPrincipled")
    ayna.inputs["Base Color"].default_value = (0.86, 0.88, 0.9, 1)
    ayna.inputs["Metallic"].default_value = 1.0
    ayna.inputs["Roughness"].default_value = 0.015
    A.bag(b.outputs["Normal"], ayna.inputs["Normal"])
    lw = A.n("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    A.bag(b.outputs["Normal"], lw.inputs["Normal"])
    yans = A.m("ADD", A.m("MULTIPLY", lw.outputs["Fresnel"], 0.5), 0.45, clamp=True)
    mx = A.n("ShaderNodeMixShader")
    A.bag(yans, mx.inputs[0])
    A.bag(p.outputs[0], mx.inputs[1])
    A.bag(ayna.outputs[0], mx.inputs[2])
    cikis(A, pus_ekle(A, mx.outputs[0], V))
    o = nesne("su", me, m)
    # tau: döngü boyunca 0→1
    tau.outputs[0].default_value = 0.0
    tau.outputs[0].keyframe_insert("default_value", frame=1)
    tau.outputs[0].default_value = 1.0
    tau.outputs[0].keyframe_insert("default_value", frame=F + 1)
    dogrusal(m.node_tree)
    # Not: düzlemsel yansıma probu (PLANE) bu sahnede yansımayı bozuyor; ekran izleme yeterli.
    return o


def dogrusal(idblock):
    ad = idblock.animation_data
    if not ad or not ad.action:
        return
    act = ad.action
    egriler = list(getattr(act, "fcurves", []) or [])
    if not egriler:
        for layer in getattr(act, "layers", []):
            for strip in layer.strips:
                for bag in strip.channelbags:
                    egriler.extend(bag.fcurves)
    for fc in egriler:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


def gok(V):
    w = bpy.data.worlds.new("gok")
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    A = Agac(nt)
    tc = A.n("ShaderNodeTexCoord")
    nrm = A.n("ShaderNodeVectorMath", operation="NORMALIZE")
    A.bag(tc.outputs["Generated"], nrm.inputs[0])
    sep = A.n("ShaderNodeSeparateXYZ")
    A.bag(nrm.outputs[0], sep.inputs[0])
    z = sep.outputs[2]
    az, el = V["gunes_yon"]
    gy = Vector((math.sin(math.radians(az)) * math.cos(math.radians(el)),
                 math.cos(math.radians(az)) * math.cos(math.radians(el)),
                 math.sin(math.radians(el))))
    dot = A.n("ShaderNodeVectorMath", operation="DOT_PRODUCT")
    A.bag(nrm.outputs[0], dot.inputs[0])
    dot.inputs[1].default_value = gy
    yatay = A.n("ShaderNodeVectorMath", operation="DOT_PRODUCT")
    A.bag(nrm.outputs[0], yatay.inputs[0])
    yatay.inputs[1].default_value = Vector((gy.x, gy.y, 0.0)).normalized()
    ufuk = A.karis(A.aralik(yatay.outputs["Value"], -0.2, 0.9), hx(V.get("ufuk_soguk", V["ufuk"])), hx(V["ufuk"]))
    renk = A.karis(A.aralik(z, 0.0, 0.2), ufuk, hx(V["orta"]))
    renk = A.karis(A.aralik(z, 0.14, 0.85), renk, hx(V["zenit"]))
    renk = A.karis(A.m("MULTIPLY", A.aralik(dot.outputs["Value"], 0.82, 1.0), 0.75), renk, hx(V["gunes_hale"]))
    # ufkun altı: suya yansıyan alt gök
    renk = A.karis(A.aralik(z, 0.0, -0.08), renk, ufuk)
    bg = A.n("ShaderNodeBackground")
    A.bag(renk, bg.inputs["Color"])
    bg.inputs["Strength"].default_value = V["dunya_guc"]
    # sahneyi aydınlatan gök: serin dolgu (gölgeler mavi kalır)
    dolgu = A.n("ShaderNodeBackground")
    A.bag(A.karis(A.aralik(z, -0.2, 0.6), hx(V.get("dolgu_alt", V["ufuk_soguk"] if "ufuk_soguk" in V else V["ufuk"])),
                  hx(V.get("dolgu", V["zenit"]))), dolgu.inputs["Color"])
    dolgu.inputs["Strength"].default_value = V.get("dolgu_guc", V["dunya_guc"])
    lp = A.n("ShaderNodeLightPath")
    mx = A.n("ShaderNodeMixShader")
    A.bag(lp.outputs["Is Camera Ray"], mx.inputs[0])
    A.bag(dolgu.outputs[0], mx.inputs[1])
    A.bag(bg.outputs[0], mx.inputs[2])
    o = A.n("ShaderNodeOutputWorld")
    A.bag(mx.outputs[0], o.inputs["Surface"])
    return w, gy


def bulutlar(V, gy):
    m, A = yeni_malzeme("m_bulut")
    tc = A.n("ShaderNodeTexCoord")
    tx = A.n("ShaderNodeTexNoise")
    tx.noise_dimensions = "4D"
    tx.inputs["Scale"].default_value = 2.2
    tx.inputs["Detail"].default_value = 7.0
    tx.inputs["Roughness"].default_value = 0.58
    A.bag(tc.outputs["Generated"], tx.inputs["Vector"])
    sep = A.n("ShaderNodeSeparateXYZ")
    A.bag(tc.outputs["Generated"], sep.inputs[0])
    gx, gyy = sep.outputs[0], sep.outputs[2]
    # kenarlara doğru söner (elips)
    dx = A.m("MULTIPLY", A.m("SUBTRACT", gx, 0.5), 2.0)
    dy = A.m("MULTIPLY", A.m("SUBTRACT", gyy, 0.5), 2.0)
    r = A.m("SQRT", A.m("ADD", A.m("MULTIPLY", dx, dx), A.m("MULTIPLY", dy, dy)))
    yog = A.m("SUBTRACT", tx.outputs["Fac"], A.m("MULTIPLY", r, 0.42))
    alfa = A.aralik(yog, 0.2, 0.3)
    isik = A.aralik(A.m("ADD", gyy, A.m("MULTIPLY", tx.outputs["Fac"], 0.6)), 0.55, 1.1)
    renk = A.karis(isik, hx(V["bulut_golge"]), hx(V["bulut_isik"]))
    em = A.n("ShaderNodeEmission")
    A.bag(renk, em.inputs["Color"])
    em.inputs["Strength"].default_value = V["dunya_guc"] * 1.05
    tr = A.n("ShaderNodeBsdfTransparent")
    mx = A.n("ShaderNodeMixShader")
    A.bag(alfa, mx.inputs[0])
    A.bag(tr.outputs[0], mx.inputs[1])
    A.bag(em.outputs[0], mx.inputs[2])
    cikis(A, mx.outputs[0])
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        pass
    r = random.Random(11)
    out = []
    for i, (x, y, z, s) in enumerate([(-1500, 6000, 1650, 2300), (900, 7000, 2100, 2600), (2400, 5200, 1300, 1700),
                                      (-200, 8000, 2700, 3000), (-2600, 6500, 2350, 1900)]):
        me = bpy.data.meshes.new(f"bulut_{i}")
        me.from_pydata([(-0.5, 0, -0.5), (0.5, 0, -0.5), (0.5, 0, 0.5), (-0.5, 0, 0.5)], [], [[0, 1, 2, 3]])
        me.uv_layers.new()
        o = nesne(f"bulut_{i}", me, m)
        o.location = (x, y, z)
        o.scale = (s * 1.9, 1, s * 0.55)
        o.visible_shadow = False
        out.append(o)
    return out


# ================================================================ sahne
def kur(vakit, durgunluk):
    V, D = VAKITLER[vakit], DURGUNLUK[durgunluk]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, F
    sc.render.resolution_x, sc.render.resolution_y = EN, BOY

    w, gy = gok(V)
    sc.world = w

    # kamera: sudan 3 m, ufuk hafif aşağıda
    cd = bpy.data.cameras.new("kamera")
    cd.lens = 27.0
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = 24.0
    cd.shift_y = 0.05
    cd.clip_start = 0.5
    cd.clip_end = 40000
    kam = bpy.data.objects.new("kamera", cd)
    sc.collection.objects.link(kam)
    kam.location = (0, 0, 3.0)
    kam.rotation_euler = (math.radians(91.0), 0, 0)
    sc.camera = kam

    # güneş
    ld = bpy.data.lights.new("gunes", "SUN")
    ld.color = hx(V["gunes_renk"])[:3]
    ld.energy = V["gunes_guc"]
    ld.angle = math.radians(1.2)
    lo = bpy.data.objects.new("gunes", ld)
    sc.collection.objects.link(lo)
    lo.rotation_euler = Vector((0, 0, -1)).rotation_difference(-gy).to_euler()

    arazi(V)
    burun(V)
    kaya_mat = mat_boya("m_kaya", "#56535A", 0.9, V, varyasyon=0.35, olcek=1.2, bump=0.5)
    r = random.Random(3)
    for i in range(14):
        x = -4.0 - r.uniform(0, 14)
        y = 30 + r.uniform(0, 24)
        kaya_tasi(f"kaya_{i}", (x, y, r.uniform(-0.5, 0.3)), (r.uniform(0.8, 2.2), r.uniform(0.8, 2.0), r.uniform(0.6, 1.3)),
                  kaya_mat, i)
    kulube(V, (-4.6, 49.0, 1.15), 35.0)
    igne = igne_malzemesi(V)
    for i, (x, y, b) in enumerate([(-15.5, 52.0, 13.0), (-12.2, 57.0, 10.5), (-19.0, 47.0, 15.0), (-10.2, 63.0, 8.0),
                                   (-23.0, 60.0, 16.0), (-4.2, 54.0, 6.5)]):
        ladin(f"ladin_{i}", (x, y, 2.0 + 6.5 * max(0, (-x - 4) / 20)), b, igne, i)
    iskele(V, (-2.2, 46.5), (4.2, 35.5))
    kayik(V, (5.6, 35.0, 0.18), 20.0)
    # karşı adacık
    for i, (x, y, b) in enumerate([(64, 262, 17), (72, 255, 14), (80, 268, 19), (58, 270, 12)]):
        ladin(f"ada_ladin_{i}", (x, y, 3.0), b, igne, 40 + i)
    ada_mat = bpy.data.materials["m_burun"]
    for i in range(3):
        kaya_tasi(f"ada_{i}", (62 + i * 9, 262 + i * 3, 0.2), (14, 10, 4.5), ada_mat, 90 + i)
    su(V, D)
    bulutlar(V, gy)
    ayarla(sc)
    return sc


def ayarla(sc):
    sc.render.engine = "BLENDER_EEVEE"
    e = sc.eevee
    e.taa_render_samples = 48
    e.use_raytracing = True
    try:
        e.ray_tracing_method = "SCREEN"
        e.ray_tracing_options.resolution_scale = "1"
    except Exception:
        pass
    e.use_shadows = True
    e.shadow_ray_count = 2
    e.use_fast_gi = True
    sc.view_settings.view_transform = "Standard"
    try:
        sc.view_settings.look = "None"
    except Exception:
        pass
    sc.view_settings.exposure = -0.1
    # Kuwahara: kare fırça darbesine döner
    ng = bpy.data.node_groups.new("boya", "CompositorNodeTree")
    ng.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    rl = ng.nodes.new("CompositorNodeRLayers")
    rl.scene = sc
    ku = ng.nodes.new("CompositorNodeKuwahara")
    try:
        ku.inputs["Type"].default_value = "Anisotropic"
    except Exception:
        pass
    ku.inputs["Size"].default_value = int(round(8 * EN / 720))
    ku.inputs["Uniformity"].default_value = 4
    ku.inputs["Sharpness"].default_value = 0.85
    ku.inputs["Eccentricity"].default_value = 1.1
    ng.links.new(rl.outputs["Image"], ku.inputs["Image"])
    out = ng.nodes.new("NodeGroupOutput")
    ng.links.new(ku.outputs[0], out.inputs[0])
    sc.compositing_node_group = ng
    sc.render.use_compositing = True
    isf = sc.render.image_settings
    isf.file_format = "PNG"
    isf.color_mode = "RGB"
    isf.color_depth = "8"


def cek(sc, kareler, yol_sablon):
    for f in kareler:
        sc.frame_set(f)
        sc.render.filepath = yol_sablon.format(f=f)
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["kare", "aksam", "S2", "1", "onizleme.png"]
    komut, vakit, dur = a[0], a[1], a[2]
    if komut == "kare" and len(a) > 5:
        EN, BOY = int(EN * float(a[5])), int(BOY * float(a[5]))
    sc = kur(vakit, dur)
    if komut == "kare":
        cek(sc, [int(a[3])], os.path.abspath(a[4]))
        print("KARE_OK", a[4])
    elif komut == "dongu":
        os.makedirs(a[3], exist_ok=True)
        cek(sc, range(1, F + 1), os.path.join(os.path.abspath(a[3]), "k_{f:04d}.png"))
        print("DONGU_OK", a[3])
    elif komut == "kaydet":
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a[3]))
        print("KAYDET_OK", a[3])
