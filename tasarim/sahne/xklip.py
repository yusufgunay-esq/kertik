"""Reader for text DirectX .x skeletal clips (3ds Max Biped style) and a
retargeter onto the MakeHuman default rig used by murettebat.py.

Only generic format code lives here. Which clips are read, and from where,
is kept in the git-ignored local file _yerel/klipler.json; clip data and
renders made from it never enter the repository.

Conventions: .x matrices are row-major for row vectors; everything below is
converted to column-vector 4x4 numpy matrices on read.
"""
import re
import numpy as np

_TOK = re.compile(r'"[^"]*"|<[^>]*>|[A-Za-z_][A-Za-z0-9_\-.]*|-?\d+\.?\d*(?:[eE][-+]?\d+)?|[{};,]')


def _ident(t):
    return t[0].isalpha() or t[0] == "_"


def _blok(tk, i):
    node = {"data": [], "children": [], "refs": []}
    n = len(tk)
    while i < n and tk[i] != "}":
        t = tk[i]
        if t == "{":
            node["refs"].append(tk[i + 1])
            i += 3
        elif _ident(t) and i + 1 < n and (tk[i + 1] == "{" or (_ident(tk[i + 1]) and i + 2 < n and tk[i + 2] == "{")):
            typ, i, ad = t, i + 1, None
            if tk[i] != "{":
                ad, i = tk[i], i + 1
            cocuk, i = _blok(tk, i + 1)
            cocuk["type"], cocuk["name"] = typ, ad
            if typ != "template":
                node["children"].append(cocuk)
        else:
            if t not in (";", ","):
                node["data"].append(t)
            i += 1
    return node, i + 1


def _mat(vals):
    return np.array([float(v) for v in vals[:16]]).reshape(4, 4).T


def _quat_mat(w, x, y, z):
    n = (w * w + x * x + y * y + z * z) ** 0.5 or 1.0
    w, x, y, z = w / n, x / n, y / n, z / n
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


class Klip:
    """One clip: bone hierarchy, bind pose and keyed local transforms."""

    def __init__(self, yol, eslenik=True):
        with open(yol, encoding="latin-1") as f:
            metin = f.read()
        metin = metin.split("\n", 1)[1]                    # drop 'xof 0303txt 0032'
        metin = re.sub(r"//[^\n]*|#[^\n]*", "", metin)
        kok, _ = _blok(_TOK.findall(metin), 0)
        self.ebeveyn, self.yerel, self.sira = {}, {}, []
        self.bind = {}
        self.anahtar = {}
        self.eslenik = eslenik
        for c in kok["children"]:
            if c["type"] == "Frame":
                self._cerceve(c, None)
        for m in self._hepsi(kok, "SkinWeights"):
            ad = m["data"][0].strip('"')
            off = _mat(m["data"][-16:])
            self.bind[ad] = np.linalg.inv(off)
        for s in self._hepsi(kok, "AnimationSet"):
            self.ad = s["name"]
            for a in s["children"]:
                if a["type"] != "Animation" or not a["refs"]:
                    continue
                kemik = a["refs"][0]
                d = self.anahtar.setdefault(kemik, {})
                for k in a["children"]:
                    if k["type"] != "AnimationKey":
                        continue
                    v = [float(x) for x in k["data"]]
                    tur, adet, j = int(v[0]), int(v[1]), 2
                    zaman, deger = [], []
                    for _ in range(adet):
                        t, nv = v[j], int(v[j + 1])
                        zaman.append(t)
                        deger.append(v[j + 2:j + 2 + nv])
                        j += 2 + nv
                    d[tur] = (np.array(zaman), np.array(deger))
            break
        zamanlar = [z for d in self.anahtar.values() for z, _ in d.values()]
        self.t0 = min(z[0] for z in zamanlar) if zamanlar else 0.0
        self.t1 = max(z[-1] for z in zamanlar) if zamanlar else 0.0

    def _cerceve(self, c, ebeveyn):
        ad = c["name"]
        self.ebeveyn[ad] = ebeveyn
        self.sira.append(ad)
        self.yerel[ad] = np.eye(4)
        for k in c["children"]:
            if k["type"] == "FrameTransformMatrix":
                self.yerel[ad] = _mat(k["data"])
            elif k["type"] == "Frame":
                self._cerceve(k, ad)

    def _hepsi(self, n, tur):
        for c in n["children"]:
            if c["type"] == tur:
                yield c
            yield from self._hepsi(c, tur)

    @staticmethod
    def _ornek(zaman, deger, t):
        if t <= zaman[0]:
            return deger[0]
        if t >= zaman[-1]:
            return deger[-1]
        i = int(np.searchsorted(zaman, t)) - 1
        u = (t - zaman[i]) / (zaman[i + 1] - zaman[i])
        a, b = deger[i], deger[i + 1]
        if len(a) == 4:                                    # quaternion: nlerp on the short arc
            if np.dot(a, b) < 0:
                b = -b
            q = a * (1 - u) + b * u
            return q / np.linalg.norm(q)
        return a * (1 - u) + b * u

    def yerel_an(self, ad, t):
        d = self.anahtar.get(ad)
        if not d or 0 not in d:
            return self.yerel[ad]
        w, x, y, z = self._ornek(*d[0], t)
        if self.eslenik:
            x, y, z = -x, -y, -z
        m = np.eye(4)
        m[:3, :3] = _quat_mat(w, x, y, z)
        if 1 in d:
            m[:3, :3] = m[:3, :3] @ np.diag(self._ornek(*d[1], t))
        m[:3, 3] = self._ornek(*d[2], t) if 2 in d else self.yerel[ad][:3, 3]
        return m

    def dunya(self, t=None):
        """World matrices of every frame at tick t (None = static frame pose)."""
        w = {}
        for ad in self.sira:
            l = self.yerel[ad] if t is None else self.yerel_an(ad, t)
            p = self.ebeveyn[ad]
            w[ad] = l if p is None else w[p] @ l
        return w


# ---------------------------------------------------------------- retarget onto the MakeHuman default rig
# target bone <- source Biped bone. Unlisted target bones keep their rest relation to the parent.
HARITA = {"root": "Bip01_Pelvis", "spine05": "Bip01_Spine", "spine03": "Bip01_Spine1",
          "neck01": "Bip01_Neck", "head": "Bip01_Head"}
for _t, _s in (("L", "L"), ("R", "R")):
    HARITA.update({f"clavicle.{_t}": f"Bip01_{_s}_Clavicle", f"upperarm01.{_t}": f"Bip01_{_s}_UpperArm",
                   f"lowerarm01.{_t}": f"Bip01_{_s}_Forearm", f"wrist.{_t}": f"Bip01_{_s}_Hand",
                   f"upperleg01.{_t}": f"Bip01_{_s}_Thigh", f"lowerleg01.{_t}": f"Bip01_{_s}_Calf",
                   f"foot.{_t}": f"Bip01_{_s}_Foot", f"finger1-1.{_t}": f"Bip01_{_s}_Finger0"})
    for _f in (2, 3, 4, 5):
        HARITA[f"finger{_f}-1.{_t}"] = f"Bip01_{_s}_Finger1"
# source bone -> the joint it points at (to align rest directions)
UC = {"Bip01_Pelvis": "Bip01_Spine", "Bip01_Spine": "Bip01_Spine1", "Bip01_Spine1": "Bip01_Neck",
      "Bip01_Neck": "Bip01_Head", "Bip01_Head": "Bip01_HeadNub"}
for _s in ("L", "R"):
    UC.update({f"Bip01_{_s}_Clavicle": f"Bip01_{_s}_UpperArm", f"Bip01_{_s}_UpperArm": f"Bip01_{_s}_Forearm",
               f"Bip01_{_s}_Forearm": f"Bip01_{_s}_Hand", f"Bip01_{_s}_Hand": f"Bip01_{_s}_Finger1",
               f"Bip01_{_s}_Thigh": f"Bip01_{_s}_Calf", f"Bip01_{_s}_Calf": f"Bip01_{_s}_Foot",
               f"Bip01_{_s}_Foot": f"Bip01_{_s}_Toe0", f"Bip01_{_s}_Finger0": f"Bip01_{_s}_Finger0Nub",
               f"Bip01_{_s}_Finger1": f"Bip01_{_s}_Finger1Nub"})


def _karsi(ad):
    """Bip01_L_x <-> Bip01_R_x."""
    if "_L_" in ad:
        return ad.replace("_L_", "_R_")
    if "_R_" in ad:
        return ad.replace("_R_", "_L_")
    return ad


AYNA = np.diag([-1.0, 1.0, 1.0])          # mirror across the body's mid plane (target armature space)


def _rot(m):
    r = m[:3, :3].copy()
    u, _, vt = np.linalg.svd(r)
    return u @ vt


class Aktarici:
    """Retargets one clip onto one armature. Rotations only: placement stays with the caller."""

    def __init__(self, klip, arm):
        from mathutils import Matrix, Vector
        self.k, self.arm = klip, arm
        k = klip
        bind = dict(k.bind)
        w0 = k.dunya(k.t0)
        for ad in k.sira:                               # unskinned bones: parent bind @ constant offset
            if ad not in bind and k.ebeveyn[ad] in bind:
                l = k.yerel_an(ad, k.t0)
                bind[ad] = bind[k.ebeveyn[ad]] @ l
        self.bind = bind
        p = lambda a: bind[a][:3, 3]
        up = p("Bip01_Head") - p("Bip01_Pelvis"); up /= np.linalg.norm(up)
        sol = p("Bip01_L_Thigh") - p("Bip01_R_Thigh"); sol -= up * sol.dot(up); sol /= np.linalg.norm(sol)
        on = p("Bip01_L_Toe0") - p("Bip01_L_Foot"); on -= up * on.dot(up) + sol * on.dot(sol); on /= np.linalg.norm(on)
        S = np.stack([sol, on, up], 1)
        T = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]], float).T
        self.C = T @ S.T                                # source world -> target armature space
        self.olcek = 1.0
        rest = {b.name: b.matrix_local.copy() for b in arm.data.bones}
        self.rest = rest
        self.hiza, self.hiza_ayna = {}, {}
        for tb, sb in HARITA.items():
            if tb not in rest:
                continue
            dt = Vector(rest[tb].to_3x3().col[1])
            if sb in bind and UC.get(sb) in bind:
                ds = self.C @ (p(UC[sb]) - p(sb))
                self.hiza[tb] = dt.rotation_difference(Vector(ds)).to_matrix()
            km = _karsi(sb)
            if km in bind and UC.get(km) in bind:
                ds = AYNA @ self.C @ (p(UC[km]) - p(km))
                self.hiza_ayna[tb] = dt.rotation_difference(Vector(ds)).to_matrix()
        sira, gor = [], set()

        def gez(b):
            sira.append(b.name)
            for c in b.children:
                gez(c)
        for b in arm.data.bones:
            if b.parent is None:
                gez(b)
        self.sira = sira

    def poz(self, t, sadece=None, agirlik=1.0, ayna=False):
        """Pose the armature at tick t. sadece: optional set of target bones to drive (others keep
        their current basis). agirlik blends the driven rotation from the current pose (0..1).
        ayna plays the clip mirrored (a left-handed gesture done with the right hand)."""
        from mathutils import Matrix
        k, arm, C = self.k, self.arm, self.C
        w = k.dunya(t)
        pb = arm.pose.bones
        if sadece is None:                              # a full pose starts from the rest pose
            for b in pb:
                b.matrix_basis = Matrix.Identity(4)
        P = {}
        for ad in self.sira:
            b = arm.data.bones[ad]
            rest = self.rest[ad]
            if b.parent is None:
                temel = rest
            else:
                temel = P[b.parent.name] @ self.rest[b.parent.name].inverted() @ rest
            sb = HARITA.get(ad)
            hiza = self.hiza_ayna if ayna else self.hiza
            if ayna and sb:
                sb = _karsi(sb)
            surulur = sb in w and sb in self.bind and ad in hiza and (sadece is None or ad in sadece)
            if surulur:
                D = C @ (_rot(w[sb]) @ _rot(self.bind[sb]).T) @ C.T
                if ayna:
                    D = AYNA @ D @ AYNA
                R = Matrix(D.tolist()) @ hiza[ad] @ rest.to_3x3()
                if agirlik < 1.0:
                    R = temel.to_3x3().to_quaternion().slerp(R.to_quaternion(), agirlik).to_matrix()
                hedef = R.to_4x4()
                hedef.translation = temel.translation
                P[ad] = hedef
            else:
                yerel = (self.rest[b.parent.name].inverted() @ rest) if b.parent else rest
                P[ad] = (P[b.parent.name] @ yerel if b.parent else rest) @ pb[ad].matrix_basis
        for ad in self.sira:
            b = arm.data.bones[ad]
            yerel = (self.rest[b.parent.name].inverted() @ self.rest[ad]) if b.parent else self.rest[ad]
            ust = P[b.parent.name] if b.parent else Matrix.Identity(4)
            pb[ad].matrix_basis = (ust @ yerel).inverted() @ P[ad]
        self._parmak_dagit()

    def _parmak_dagit(self):
        """The source hand has a single finger segment; spread its bend over three MakeHuman joints."""
        pb = self.arm.pose.bones
        for s in (".L", ".R"):
            for f in (2, 3, 4, 5):
                a = pb.get(f"finger{f}-1{s}")
                if a is None:
                    continue
                q = a.matrix_basis.to_quaternion()
                from mathutils import Quaternion
                bir = Quaternion()
                a.rotation_mode = "QUATERNION"
                a.rotation_quaternion = bir.slerp(q, 0.55)
                for j, pay in ((2, 0.55), (3, 0.40)):
                    c = pb.get(f"finger{f}-{j}{s}")
                    if c is not None:
                        c.rotation_mode = "QUATERNION"
                        c.rotation_quaternion = bir.slerp(q, pay)

    def tutamak(self, t, el="R"):
        """Prop bone pose relative to the hand, mapped to target space: (offset, rotation 3x3)."""
        w = self.k.dunya(t)
        el_s, pr = w[f"Bip01_{el}_Hand"], w["Bip01_Prop1" if el == "R" else "Bip01_Prop2"]
        rel = np.linalg.inv(el_s) @ pr
        return rel, self.C @ _rot(pr)
