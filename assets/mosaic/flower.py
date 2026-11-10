"""Lily bouquet that grows and blooms, as a dense colour-character mosaic (after the reference video)."""
import sys, os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from mosaic import Mosaic, save_webp
OUT = sys.argv[1]; random.seed(8); np.random.seed(8)
COLS, ROWS, CW, CH = 170, 116, 4, 6
M = Mosaic(COLS, ROWS, CW, CH, 6, " .,:;-~=+*xX#%@")
W1, H1 = COLS*CW, ROWS*CH                 # 680 x 700
S = 2
def P(x, y): return (x*S, y*S)
BASE = (340, 690)
cl = lambda x, a=0.0, b=1.0: max(a, min(b, x))
ease = lambda x: x*x*(3-2*x)

FLOWERS = [  # x, y, size, colour, phase(0..1 order of opening), rotation deg
    (235, 120, 80,  (238, 220, 196), 0.55, 10), (505, 140, 78, (228, 204, 60), 0.75, 40),
    (130, 300, 92,  (228, 204, 60), 0.45, 25),  (565, 300, 88, (176, 44, 118), 0.65, 5),
    (360, 200, 138, (220, 36, 48), 0.10, 18),   (555, 560, 92, (156, 22, 34), 0.95, 30),
    (140, 545, 84,  (228, 204, 60), 0.85, 50),  (245, 385, 138, (220, 96, 196), 0.25, 35),
    (470, 410, 158, (236, 216, 200), 0.38, 8),  (335, 535, 140, (238, 176, 136), 0.60, 22),
]
BUDS = [(300, 40, 30, (120, 110, 70)), (425, 30, 28, (150, 60, 70)), (530, 62, 26, (130, 120, 60)), (180, 190, 26, (120, 110, 70))]
def stem_pts(tx, ty, k):
    bx = BASE[0] + (k-6)*5; by = BASE[1]
    cx = bx + (tx-bx)*0.15 + (k % 3 - 1)*14; cy = by + (ty-by)*0.55
    return [((1-u)**2*bx + 2*u*(1-u)*cx + u*u*tx, (1-u)**2*by + 2*u*(1-u)*cy + u*u*ty) for u in np.linspace(0, 1, 40)]
STEMS = [stem_pts(f[0], f[1], i) for i, f in enumerate(FLOWERS)] + [stem_pts(b[0], b[1], i+3) for i, b in enumerate(BUDS)]
LEAVES = []
for i in range(16):
    a = math.radians(-90 + (i-7.5)*9.5 + random.uniform(-4, 4)); L = random.uniform(140, 250)
    LEAVES.append((BASE[0] + (i-7.5)*5, BASE[1] - random.uniform(0, 20), a, L, random.uniform(7, 11), random.uniform(0.1, 0.4), random.uniform(-0.5, 0.5)))
for st in STEMS[:10]:
    for u in (0.35, 0.55):
        x, y = st[int(u*39)]
        side = random.choice((-1, 1)); a = math.radians(-90 + side*random.uniform(35, 70))
        LEAVES.append((x, y, a, random.uniform(60, 100), random.uniform(6, 9), random.uniform(0.25, 0.45), side*0.4))
STARS = [(random.uniform(0, W1), random.uniform(0, H1), random.uniform(40, 110)) for _ in range(70)]

def blade(x, y, a, L, wd, bend=0.0, n=14, e=(0.68, 1.1)):
    """lanceolate outline starting at (x,y) pointing along a"""
    left, right = [], []
    for i in range(n+1):
        u = i/n; aa = a + bend*u
        px = x + math.cos(a + bend*u*0.5)*L*u; py = y + math.sin(a + bend*u*0.5)*L*u
        w = wd*math.sin(math.pi*u**e[0])**e[1]
        nx, ny = -math.sin(aa), math.cos(aa)
        left.append((px + nx*w, py + ny*w)); right.append((px - nx*w, py - ny*w))
    return left + right[::-1], (x + math.cos(a + bend*0.5)*L, y + math.sin(a + bend*0.5)*L)
def sc(c, k): return tuple(int(cl(v*k, 0, 255)) for v in c)
def S2(pts): return [P(x, y) for x, y in pts]

def paint(t):
    im = Image.new("RGB", (W1*S, H1*S), (0, 0, 0)); d = ImageDraw.Draw(im)
    for (x, y, b) in STARS:
        v = int(b*cl(t*3)); d.ellipse([x*S-2, y*S-2, x*S+2, y*S+2], fill=(v, v, int(v*0.9)))
    # leaves
    for (x, y, a, L, wd, t0, bend) in LEAVES:
        g = ease(cl((t-t0*0.9)/0.3))
        if g <= 0: continue
        poly, tip = blade(x, y, a, L*g, wd*(0.4+0.6*g), bend, e=(0.6, 1.4))
        d.polygon(S2(poly), fill=(46, 140, 44));
        inner, _ = blade(x, y, a, L*g*0.96, wd*(0.4+0.6*g)*0.55, bend, e=(0.6, 1.4))
        d.polygon(S2(inner), fill=(78, 190, 66))
        d.line(S2([(x, y), tip]), fill=(150, 225, 120), width=2*S)
    # stems
    for i, st in enumerate(STEMS):
        g = ease(cl((t - 0.02*i)/0.3)); n = max(2, int(g*len(st)))
        if g > 0:
            d.line(S2(st[:n]), fill=(60, 160, 52), width=4*S); d.line(S2(st[:n]), fill=(120, 215, 96), width=1*S)
    def bud(x, y, size, col, ang, g):
        poly, _ = blade(x - math.cos(ang)*size*0.15, y - math.sin(ang)*size*0.15, ang, size*g, size*0.2*g)
        d.polygon(S2(poly), fill=sc(col, 0.75));
        inner, _ = blade(x - math.cos(ang)*size*0.1, y - math.sin(ang)*size*0.1, ang, size*g*0.85, size*0.09*g)
        d.polygon(S2(inner), fill=sc(col, 1.05))
    for i, (x, y, size, col) in enumerate(BUDS):
        g = ease(cl((t-0.3-0.03*i)/0.15)); st = STEMS[len(FLOWERS)+i]
        ang = math.atan2(st[-1][1]-st[-4][1], st[-1][0]-st[-4][0])
        if g > 0: bud(x, y, size*1.6, col, ang, g)
    # flowers (painter's order as listed)
    for i, (x, y, size, col, ph, rot) in enumerate(FLOWERS):
        st = STEMS[i]; ang = math.atan2(st[-1][1]-st[-4][1], st[-1][0]-st[-4][0])
        gb = ease(cl((t-0.3-0.02*i)/0.15))
        o = ease(cl((t-0.44-ph*0.3)/0.24))
        if gb <= 0: continue
        if o <= 0.02:
            bud(x, y, size*0.75, sc(col, 0.8), ang, gb); continue
        for ring, k in ((0, 0.86), (1, 1.0)):
            for j in range(3):
                target = math.radians(rot + j*120 + ring*60)
                dlt = (target - ang + math.pi) % (2*math.pi) - math.pi
                a = ang + dlt*o
                L = size*(0.5+0.5*o)*(1.0 if ring else 1.08); wd = size*(0.06+0.2*o)*(1.0 if ring else 0.85)
                poly, tip = blade(x, y, a, L, wd, bend=0.25*math.sin(j*2.1+i))
                d.polygon(S2(poly), fill=sc(col, k*0.42))
                for q, kk in ((0.82, 0.7), (0.6, 1.0), (0.32, 1.22)):
                    inner, _ = blade(x, y, a, L*(0.9+0.1*q), wd*q, bend=0.25*math.sin(j*2.1+i))
                    d.polygon(S2(inner), fill=sc(col, k*kk))
                d.line(S2([(x, y), tip]), fill=sc(col, k*0.36), width=3*S)
                for sgn in (-1, 1):                                    # side veins
                    d.line(S2([(x, y), (x + math.cos(a+sgn*0.16)*L*0.8, y + math.sin(a+sgn*0.16)*L*0.8)]), fill=sc(col, k*0.72), width=1*S)
        if o > 0.55:
            so = cl((o-0.55)/0.45)
            d.ellipse([P(x-size*0.07, y-size*0.07)[0], P(x-size*0.07, y-size*0.07)[1], P(x+size*0.07, y+size*0.07)[0], P(x+size*0.07, y+size*0.07)[1]], fill=(150, 170, 70))
            for j in range(6):
                a = math.radians(rot + 30 + j*60 + 8*math.sin(j)); L = size*0.42*so
                ex, ey = x + math.cos(a)*L, y + math.sin(a)*L
                d.line(S2([(x, y), (ex, ey)]), fill=(255, 240, 180), width=2*S)
                d.ellipse([ex*S-7, ey*S-7, ex*S+7, ey*S+7], fill=(120, 52, 14))
    return im.filter(ImageFilter.GaussianBlur(0.8)).resize((COLS, ROWS), Image.BOX)

N = 66
frames = [M.ramp(paint(i/(N-1)), gamma=0.6, bloom=0.4, boost=1.35) for i in range(N)]
durs = [90]*N; durs[-1] = 3800
save_webp(os.path.join(OUT, "lily.webp"), frames, durs, quality=60)
frames[-1].save(os.path.join(OUT, "lily_final.png")); frames[22].save(os.path.join(OUT, "lily_mid.png")); frames[40].save(os.path.join(OUT, "lily_mid2.png"))
print("lily", N, "frames", os.path.getsize(os.path.join(OUT, "lily.webp")), "bytes", frames[0].size)
