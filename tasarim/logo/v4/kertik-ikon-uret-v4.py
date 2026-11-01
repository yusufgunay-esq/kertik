import math, cairosvg, os

# v4 "Nefes" — G4 varyantı, adaptive icon güvenli alanına (SAFE) oturtulmuş.
# Geometri mantığı v2 script'iyle birebir aynı: C=432 tuval, SAFE=132 güvenli yarıçap.
# Ring + tek zincifre mühür kertiği + çekirdek nokta. Kayıt (çentik/çubuk) paletiyle
# aynı köke bağlı ama logo kendi başına: --ink gövde, --accent (shu-iro) tek vurgu.
C = 432; CX = CY = 216.0
INK = "#1A1B1E"; PAPER = "#F5F1E6"; ACC = "#B4432B"
SAFE = 132.0

RING_R = 104.0; RING_W = 8.0; RING_OP = .34
TICK_R0 = 70.0; TICK_R1 = 122.0; TICK_W0 = 16.0; TICK_W1 = 6.0
CORE_R = 10.0; CORE_OP = .62

def tick(r0, r1, w0, w1, col, op=1.0):
    # -90° = tepe (saat kertiği). Fırça: girişte dolgun, uçta ince.
    a = math.radians(-90)
    x0, y0 = CX + r0 * math.cos(a), CY + r0 * math.sin(a)
    x1, y1 = CX + r1 * math.cos(a), CY + r1 * math.sin(a)
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    px, py = -dy / L, dx / L
    pts = []
    segs = 8
    for i in range(segs + 1):
        t = i / segs
        e = (1 - t) ** 1.15
        w = (w1 + (w0 - w1) * e) / 2
        cx, cy = x0 + dx * t, y0 + dy * t
        pts.append((cx + px * w, cy + py * w))
    for i in range(segs, -1, -1):
        t = i / segs
        e = (1 - t) ** 1.15
        w = (w1 + (w0 - w1) * e) / 2
        cx, cy = x0 + dx * t, y0 + dy * t
        pts.append((cx - px * w, cy - py * w))
    d = "M" + "L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + "Z"
    return f'<path d="{d}" fill="{col}" opacity="{op}"/>'

def mark(ink=INK, acc=ACC, ring_op=RING_OP, core_op=CORE_OP):
    out = [f'<circle cx="{CX}" cy="{CY}" r="{RING_R}" fill="none" stroke="{ink}" stroke-width="{RING_W}" opacity="{ring_op}"/>']
    out.append(tick(TICK_R0, TICK_R1, TICK_W0, TICK_W1, acc, 1.0))
    out.append(f'<circle cx="{CX}" cy="{CY}" r="{CORE_R}" fill="{ink}" opacity="{core_op}"/>')
    return "".join(out)

def svg(body, bg=None):
    b = f'<rect width="{C}" height="{C}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{C}" height="{C}" viewBox="0 0 {C} {C}">{b}{body}</svg>'

def masked_circle(inner, bg):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{C}" height="{C}" viewBox="0 0 {C} {C}">'
            f'<defs><clipPath id="cp"><circle cx="216" cy="216" r="216"/></clipPath></defs>'
            f'<g clip-path="url(#cp)"><rect width="{C}" height="{C}" fill="{bg}"/>{inner}</g></svg>')

ONPLAN = svg(mark())
TEKRENK = svg(mark(ink="#000", acc="#000", ring_op=.55, core_op=.85))
TAM_DAIRE = masked_circle(mark(), PAPER)

DENS = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
BASE_FG = 108
BASE_LEGACY = 48

out_root = "/tmp/kertik-ikon-v4"
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

# Play Store / tanıtım için 512px tam kare
cairosvg.svg2png(bytestring=svg(mark(), PAPER).encode(), write_to=f"{out_root}/play-512.png",
                  output_width=512, output_height=512)
print("bitti ->", out_root)
