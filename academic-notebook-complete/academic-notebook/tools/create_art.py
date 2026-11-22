"""Generate small, original mathematical SVG illustrations (no assets to license)."""
from pathlib import Path
import math
ROOT=Path(__file__).resolve().parent.parent/'assets';ROOT.mkdir(exist_ok=True)
INK='#666a5a'; RUST='#a36851'; PALE='#f2efe8'; GRID='#dedbd1'

def write(name,w,h,inner,desc):
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{desc}">
<title>{desc}</title><rect width="{w}" height="{h}" fill="{PALE}"/>{inner}</svg>'''
    (ROOT/name).write_text(svg)

def path(points,stroke=RUST,width=2.0,op=1):
    data=' '.join(('M' if i==0 else 'L')+f'{x:.2f},{y:.2f}' for i,(x,y) in enumerate(points))
    return f'<path d="{data}" fill="none" stroke="{stroke}" stroke-width="{width}" opacity="{op}" stroke-linecap="round" stroke-linejoin="round"/>'

def grid(w,h,spacing=30):
    s=''
    for x in range(0,w+1,spacing):s+=f'<path d="M{x} 0V{h}" stroke="{GRID}" opacity=".6" stroke-width=".5"/>'
    for y in range(0,h+1,spacing):s+=f'<path d="M0 {y}H{w}" stroke="{GRID}" opacity=".6" stroke-width=".5"/>'
    return s

# Homepage: an idealized orbit and symmetric flow pattern.
w,h=490,490; c=(245,238)
a=grid(w,h,35)
for r in (67,114,164,203):a+=f'<circle cx="{c[0]}" cy="{c[1]}" r="{r}" fill="none" stroke="{INK}" stroke-width=".7" opacity=".28"/>'
a+=f'<path d="M{c[0]} 15V475M20 {c[1]}H470" stroke="{INK}" stroke-width=".85" opacity=".4"/>'
# Geometric curve: closed smooth polar-like path with angular modulation
pts=[]
for i in range(1601):
    t=i/1600*2*math.pi
    r=130+48*math.cos(3*t)+15*math.sin(7*t)
    pts.append((c[0]+r*math.cos(t-.18),c[1]+r*math.sin(t-.18)))
a+=path(pts,RUST,2.6,.96)
pts2=[]
for i in range(1001):
    t=i/1000*2*math.pi
    r=130+48*math.cos(3*t)+15*math.sin(7*t)
    pts2.append((c[0]+(r*.80)*math.cos(t-.18),c[1]+(r*.80)*math.sin(t-.18)))
a+=path(pts2,INK,1,.4)
for ang in (0,.5*math.pi,math.pi,1.5*math.pi):
    x=c[0]+164*math.cos(ang); y=c[1]+164*math.sin(ang)
    a+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="{INK}" opacity=".66"/>'
a+=f'''<text x="34" y="48" font-size="11" fill="#8d887d" font-family="Georgia,serif" font-style="italic">r = f(θ)</text><text x="409" y="458" font-size="10" fill="#a29a8e" font-family="Georgia,serif">0 → 2π</text>'''
write('hero.svg',w,h,a,'A parametric mathematical curve on a coordinate grid')

# Cover thumbnails share typography-free palette.
w,h=480,260
common=grid(w,h,26)
# Fourier
body=common
for k,(col,op) in enumerate(((INK,.26),(INK,.4),(RUST,1))):
    pts=[]
    for j in range(700):
        x=j/699*w
        t=(x-w/2)/57
        y=h/2 + 43*math.sin(t) + (19 if k>0 else 0)*math.sin(2*t)/2 + (15 if k>1 else 0)*math.sin(4*t)/3
        y+=(k-1)*38
        pts.append((x,y))
    body+=path(pts,col,2.2 if k==2 else 1.6,op)
write('fourier.svg',w,h,body,'Overlayed Fourier harmonic waves')
# Compactness: overlapping circular disks
body=common
for x,y,r in [(155,130,80),(240,98,78),(279,174,65),(204,166,77)]:
    body+=f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{RUST if x==279 else INK}" stroke-width="1.7" opacity=".75"/>'
for x,y in [(150,122),(227,90),(269,174),(202,162)]:body+=f'<circle cx="{x}" cy="{y}" r="3" fill="{RUST}"/>'
write('compactness.svg',w,h,body,'Finite collection of overlapping circular regions')
# Euler unit circle
body=common;cx,cy=236,130;r=90
body+=f'<path d="M0 {cy}H480M{cx} 0V260" stroke="{INK}" stroke-width="1" opacity=".44"/><circle cx="{cx}" cy="{cy}" r="{r}" stroke="{INK}" stroke-width="1.6" fill="none"/>'
t=1.6;x=cx+r*math.cos(t);y=cy-r*math.sin(t)
body+=f'<path d="M{cx} {cy}L{x:.2f} {y:.2f}" stroke="{RUST}" stroke-width="2.2"/><circle cx="{x}" cy="{y}" r="4.5" fill="{RUST}"/>'
body+=f'<path d="M{cx+28} {cy} A28 28 0 0 0 {cx+28*math.cos(t):.1f} {cy-28*math.sin(t):.1f}" fill="none" stroke="{RUST}" stroke-width="1.1"/>'
write('euler.svg',w,h,body,'Unit circle with a radius making an angle')
# Gaussian bell
body=common+f'<path d="M0 205H480M240 0V260" stroke="{INK}" stroke-width="1" opacity=".35"/>'
pts=[(x,205-155*math.exp(-((x-240)/75)**2)) for x in range(481)]
body+=path(pts,RUST,2.6,1)
body+=f'<path d="M180 205V{205-155*math.exp(-((180-240)/75)**2):.2f}M300 205V{205-155*math.exp(-((300-240)/75)**2):.2f}" stroke="{INK}" stroke-dasharray="3 4" opacity=".7"/>'
write('gaussian.svg',w,h,body,'Gaussian bell curve on a grid')

(ROOT/'favicon.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#292a26"/><circle cx="32" cy="32" r="23" fill="none" stroke="#b9ac91" stroke-width="1.3"/><text x="32" y="43" text-anchor="middle" font-size="38" font-family="Georgia,serif" font-style="italic" fill="#f1eee7">∑</text></svg>''')
print('Wrote', len(list(ROOT.glob('*.svg'))),'SVG assets')
