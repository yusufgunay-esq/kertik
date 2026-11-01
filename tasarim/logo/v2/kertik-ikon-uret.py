import math, cairosvg, os

# Yusuf'un onayladığı v2 kertik işareti — tasarim/logo/v2/kertik-logo-uret.py ile birebir aynı geometri.
C = 432; CX = CY = 216.0
INK = "#16181B"; PAPER = "#F2EFE7"; ACC = "#9E4429"
SAFE = 132.0; W = 24.0; PITCH = 38.0; SEAM = 16.0
SWEEPS = [360, 360, 252, 118]

def arc(r, a0, a1, w, col):
    p = lambda a: (CX + r * math.cos(math.radians(a - 90)), CY + r * math.sin(math.radians(a - 90)))
    x0, y0 = p(a0); x1, y1 = p(a1); big = 1 if (a1 - a0) > 180 else 0
    return (f'<path d="M {x0:.2f} {y0:.2f} A {r:.2f} {r:.2f} 0 {big} 1 {x1:.2f} {y1:.2f}" fill="none" '
            f'stroke="{col}" stroke-width="{w:.2f}" stroke-linecap="butt"/>')

def mark(ink=INK, acc=ACC):
    n = len(SWEEPS); r_out = SAFE - W / 2
    R = [r_out - (n - 1 - i) * PITCH for i in range(n)]
    out = []
    for i, (r, sw) in enumerate(zip(R, SWEEPS)):
        if r <= W / 2:
            out.append(f'<circle cx="{CX}" cy="{CY}" r="{r + W / 2:.2f}" fill="{ink}"/>'); continue
        g = math.degrees(SEAM / r); a0 = g / 2
        a1 = (360 - g / 2) if sw >= 360 else min(a0 + sw, 360 - g / 2)
        out.append(arc(r, a0, a1, W, acc if i == n - 1 else ink))
    return "".join(out)

def svg(body, bg=None):
    b = f'<rect width="{C}" height="{C}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{C}" height="{C}" viewBox="0 0 {C} {C}">{b}{body}</svg>'

def masked_circle(inner, bg):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{C}" height="{C}" viewBox="0 0 {C} {C}">'
            f'<defs><clipPath id="cp"><circle cx="216" cy="216" r="216"/></clipPath></defs>'
            f'<g clip-path="url(#cp)"><rect width="{C}" height="{C}" fill="{bg}"/>{inner}</g></svg>')

ONPLAN = svg(mark())                      # şeffaf zemin, ön plan katmanı (adaptive icon foreground)
TEKRENK = svg(mark(ink="#000", acc="#000"))  # tek renk, monochrome katmanı
TAM_DAIRE = masked_circle(mark(), PAPER)  # eski (legacy) ikon — kağıt zemin + daire maske

DENS = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
BASE_FG = 108   # dp, adaptive icon foreground/monochrome canvas
BASE_LEGACY = 48  # dp, eski launcher ikonu

out_root = "/tmp/kertik-ikon"
for dens, mult in DENS.items():
    d = f"{out_root}/mipmap-{dens}"
    os.makedirs(d, exist_ok=True)
    px_fg = round(BASE_FG * mult)
    px_legacy = round(BASE_LEGACY * mult)
    cairosvg.svg2png(bytestring=ONPLAN.encode(), write_to=f"{d}/ic_launcher_foreground.png",
                      output_width=px_fg, output_height=px_fg)
    cairosvg.svg2png(bytestring=TEKRENK.encode(), write_to=f"{d}/ic_launcher_monochrome.png",
                      output_width=px_fg, output_height=px_fg)
    cairosvg.svg2png(bytestring=TAM_DAIRE.encode(), write_to=f"{d}/ic_launcher.png",
                      output_width=px_legacy, output_height=px_legacy)
    print(dens, px_fg, px_legacy)

print("bitti")
