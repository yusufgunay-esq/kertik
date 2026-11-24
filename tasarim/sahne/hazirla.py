"""Sefer prototipi için varlıkları hazırlar (Blender'ın Python'u: OpenImageIO + numpy).

blender -b --factory-startup --python hazirla.py -- <cikti_klasoru> <sefer_klasoru>
- tomar_gun.png  -> sefer/tomar_gun.jpg (q84)
- tekne/*.png    -> sefer/tekne_atlas.png (16 yön x 3 yelken hâli, RGBA)
- rota.json      -> sefer/rota.js (window.ROTA)
- _incele_*.jpg  -> tam çözünürlük kırpıntılar (göz kontrolü)
"""
import json
import os
import sys
import numpy as np
import OpenImageIO as oiio


def oku(p):
    i = oiio.ImageInput.open(p)
    s = i.spec()
    px = np.asarray(i.read_image(oiio.FLOAT)).reshape(s.height, s.width, s.nchannels)
    i.close()
    return px


def yaz(p, px, q=None):
    h, w, c = px.shape
    o = oiio.ImageOutput.create(p)
    sp = oiio.ImageSpec(w, h, c, oiio.UINT8)
    if q:
        sp.attribute("Compression", f"jpeg:{q}")
    o.open(p, sp)
    o.write_image((np.clip(px, 0, 1) * 255 + 0.5).astype(np.uint8))
    o.close()


a = sys.argv[sys.argv.index("--") + 1:]
ck, sf = a[0], a[1]
tomar = oku(os.path.join(ck, "tomar_gun.png"))[..., :3]
yaz(os.path.join(sf, "tomar_gun.jpg"), tomar, 84)
H = tomar.shape[0]
for ad, (y0, y1, x0, x1) in {"alt": (H - 900, H, 0, 1200), "orta": (H // 2 - 450, H // 2 + 450, 0, 1200),
                             "ust": (900, 1800, 0, 1200)}.items():
    yaz(os.path.join(ck, f"_incele_{ad}.jpg"), tomar[y0:y1, x0:x1], 88)
satirlar = []
for ek in ("a", "y", "s"):
    satirlar.append(np.concatenate([oku(os.path.join(ck, "tekne", f"tekne_{ek}_{i:02d}.png")) for i in range(16)], axis=1))
yaz(os.path.join(sf, "tekne_atlas.png"), np.concatenate(satirlar, axis=0))
with open(os.path.join(ck, "rota.json"), encoding="utf-8") as f:
    rota = json.load(f)
with open(os.path.join(sf, "rota.js"), "w", encoding="utf-8") as f:
    f.write("window.ROTA = " + json.dumps(rota, separators=(",", ":")) + ";\n")
print("HAZIR_OK")
