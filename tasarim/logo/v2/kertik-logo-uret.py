import math, cairosvg, os
C=432; CX=CY=216.0
INK="#16181B"; PAPER="#F2EFE7"; ACC="#9E4429"
INK_D="#16171A"; PAPER_D="#EDE9E0"; ACC_D="#C86A48"
SAFE=132.0; W=24.0; PITCH=38.0; SEAM=16.0
SWEEPS=[360,360,252,118]

def arc(r,a0,a1,w,col):
    p=lambda a:(CX+r*math.cos(math.radians(a-90)), CY+r*math.sin(math.radians(a-90)))
    x0,y0=p(a0); x1,y1=p(a1); big=1 if (a1-a0)>180 else 0
    return (f'<path d="M {x0:.2f} {y0:.2f} A {r:.2f} {r:.2f} 0 {big} 1 {x1:.2f} {y1:.2f}" fill="none" '
            f'stroke="{col}" stroke-width="{w:.2f}" stroke-linecap="butt"/>')

def mark(ink=INK, acc=ACC, scale=1.0):
    n=len(SWEEPS); r_out=SAFE-W/2
    R=[r_out-(n-1-i)*PITCH for i in range(n)]
    out=[]
    for i,(r,sw) in enumerate(zip(R,SWEEPS)):
        if r<=W/2:
            out.append(f'<circle cx="{CX}" cy="{CY}" r="{r+W/2:.2f}" fill="{ink}"/>'); continue
        g=math.degrees(SEAM/r); a0=g/2
        a1=(360-g/2) if sw>=360 else min(a0+sw,360-g/2)
        out.append(arc(r,a0,a1,W,acc if i==n-1 else ink))
    s="".join(out)
    if scale!=1.0:
        s=f'<g transform="translate({CX},{CY}) scale({scale}) translate({-CX},{-CY})">{s}</g>'
    return s

def svg(body,bg=None,size=C):
    b=f'<rect width="{C}" height="{C}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 {C} {C}">{b}{body}</svg>')

FILES={
 "kertik-tam":      svg(mark(),PAPER),
 "kertik-onplan":   svg(mark()),
 "kertik-tekrenk":  svg(mark(ink="#000",acc="#000")),
 "kertik-gece":     svg(mark(ink=PAPER_D,acc=ACC_D),INK_D),
 "kertik-play":     svg(mark(scale=1.30),PAPER),
}

# ---- TEST SAYFASI ----
def masked(inner,mask):
    shapes={"daire":f'<circle cx="216" cy="216" r="216"/>',
            "kare":f'<rect width="432" height="432" rx="96"/>',
            "squircle":'<path d="M216 0C400 0 432 32 432 216S400 432 216 432 0 400 0 216 32 0 216 0Z"/>',
            "damla":'<path d="M216 0A216 216 0 0 1 432 216 216 216 0 0 1 216 432 216 216 0 0 1 0 216 216 216 0 0 1 216 0Z"/>'}
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="432" height="432" viewBox="0 0 432 432">'
            f'<defs><clipPath id="cp">{shapes[mask]}</clipPath></defs>'
            f'<g clip-path="url(#cp)"><rect width="432" height="432" fill="{PAPER}"/>{inner}</g></svg>')

os.makedirs("/tmp/lg/fin",exist_ok=True)
for k,v in FILES.items():
    open(f"/tmp/lg/fin/{k}.svg","w").write(v)

m=mark()
for shp in ("daire","kare","squircle"):
    s=masked(m,shp)
    cairosvg.svg2png(bytestring=s.encode(),write_to=f"/tmp/lg/fin/mask-{shp}.png",output_width=256,output_height=256)
for px in (512,192,96,48,24):
    cairosvg.svg2png(bytestring=masked(m,"daire").encode(),
                     write_to=f"/tmp/lg/fin/boy-{px:04d}.png",output_width=px,output_height=px)
cairosvg.svg2png(bytestring=FILES["kertik-gece"].encode(),write_to="/tmp/lg/fin/gece.png",output_width=256,output_height=256)
cairosvg.svg2png(bytestring=svg(mark(ink="#5A5F6B",acc="#5A5F6B"),"#C9CBD6").encode(),
                 write_to="/tmp/lg/fin/temali.png",output_width=256,output_height=256)
cairosvg.svg2png(bytestring=FILES["kertik-play"].encode(),write_to="/tmp/lg/fin/play-512.png",output_width=512,output_height=512)
print("ok")
