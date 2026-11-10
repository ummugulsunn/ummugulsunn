"""Swimming koi (top view) as a dense colour-character mosaic on deep blue water (after git-koi's look)."""
import sys, os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from mosaic import Mosaic, save_webp
OUT = sys.argv[1]; random.seed(2); np.random.seed(2)
COLS, ROWS, CW, CH = 190, 62, 5, 8
M = Mosaic(COLS, ROWS, CW, CH, 8, " .:-=+*xX#%@")
W1, H1 = COLS*CW, ROWS*CH                 # 950 x 496
S = 2
N = 70
PROF_S = [0, 0.03, 0.1, 0.25, 0.45, 0.7, 0.88, 1.0]
PROF_W = [0, 34, 56, 66, 58, 36, 15, 9]
PATCH = [  # s, v, rs, rv, colour
    (0.06, 0.0, 0.035, 0.5, (240, 110, 40)), (0.2, 0.35, 0.09, 0.6, (243, 128, 38)), (0.3, -0.5, 0.07, 0.5, (228, 64, 40)),
    (0.36, 0.2, 0.10, 0.28, (58, 58, 70)), (0.47, -0.25, 0.08, 0.5, (240, 150, 50)), (0.52, 0.55, 0.06, 0.4, (58, 58, 70)),
    (0.58, 0.0, 0.05, 0.7, (232, 70, 44)), (0.72, 0.1, 0.09, 0.9, (62, 150, 182)), (0.8, -0.3, 0.05, 0.6, (30, 70, 110)),
    (0.9, 0.0, 0.04, 0.9, (245, 190, 60)),
]
def tex(s, v):
    col = np.array([246, 246, 240.])
    for (ps, pv, rs, rv, c) in PATCH:
        if ((s-ps)/rs)**2 + ((v-pv)/rv)**2 < 1 + 0.25*math.sin(s*90 + v*7): col = np.array(c, float)
    shade = 1.0 - 0.22*abs(v)**3
    scale = 0.86 + 0.14*(((int(s*46) + int((v+1)*4)) % 2))          # scale texture
    return tuple(int(x) for x in np.clip(col*shade*scale, 0, 255))

yy, xx = np.mgrid[0:H1, 0:W1].astype(np.float32)
r = np.sqrt(((xx-W1*0.5)/(W1*0.62))**2 + ((yy-H1*0.5)/(H1*0.75))**2)
BG = (np.array([10, 30, 52.])[None, None] + np.clip(1-r, 0, 1)[..., None]**1.3*np.array([16, 62, 92.])[None, None]).astype(np.float32)

def paint(ph):
    im = Image.new("RGB", (W1*S, H1*S), (0, 0, 0)); d = ImageDraw.Draw(im)
    heading = math.radians(16 + 3*math.sin(2*math.pi*ph)); dx, dy = math.cos(heading), math.sin(heading)
    nx, ny = -dy, dx
    L = 430; hx, hy = W1*0.5 + dx*(L*0.5+70) + 6*math.sin(2*math.pi*ph), H1*0.5 + dy*(L*0.5+70)
    pts = []
    for k in range(N+1):
        s = k/N; A = 44*(0.08 + s**1.6)
        off = A*math.sin(2*math.pi*(s*1.05 - ph))
        pts.append((hx - dx*L*s + nx*off, hy - dy*L*s + ny*off))
    def frame_at(k):
        k = max(1, min(N-1, k)); tx, ty = pts[k-1][0]-pts[k+1][0], pts[k-1][1]-pts[k+1][1]
        n = math.hypot(tx, ty); tx, ty = tx/n, ty/n
        return pts[k], (tx, ty), (-ty, tx)
    def fan(k, side, length, spread, back, col, rays=7, wag=0.0):
        (px, py), (tx, ty), (ux, uy) = frame_at(k)
        w = np.interp(k/N, PROF_S, PROF_W)*0.7
        bx, by = px + ux*w*side, py + uy*w*side
        base = math.atan2(-ty, -tx) - side*(back + wag)
        poly = [(bx, by)]
        for j in range(rays+1):
            a = base - side*spread*(j/rays - 0.2); Lr = length*(0.75 + 0.25*math.sin(math.pi*j/rays))
            poly.append((bx + math.cos(a)*Lr, by + math.sin(a)*Lr))
        d.polygon([(x*S, y*S) for x, y in poly], fill=col)
        for j in range(rays+1):
            d.line([(bx*S, by*S), (poly[j+1][0]*S, poly[j+1][1]*S)], fill=tuple(int(c*0.72) for c in col), width=S)
    wag = 0.25*math.sin(2*math.pi*ph)
    fan(int(N*0.22), 1, 92, 0.6, 0.85, (205, 210, 214), wag=wag); fan(int(N*0.22), -1, 92, 0.6, 0.85, (205, 210, 214), wag=-wag)
    fan(int(N*0.55), 1, 56, 0.55, 0.7, (195, 200, 206)); fan(int(N*0.55), -1, 56, 0.55, 0.7, (195, 200, 206))
    # tail: two lobes
    (px, py), (tx, ty), (ux, uy) = frame_at(N-1)
    ta = math.atan2(-ty, -tx)
    for sgn in (-1, 1):
        poly = [(px, py)]
        for j in range(9):
            a = ta + sgn*(0.10 + 0.75*j/8); Lr = 150*(0.45 + 0.55*math.sin(math.pi*(j/8)**0.8))
            poly.append((px + math.cos(a)*Lr, py + math.sin(a)*Lr))
        d.polygon([(x*S, y*S) for x, y in poly], fill=(214, 218, 222))
        for q in poly[1:]: d.line([(px*S, py*S), (q[0]*S, q[1]*S)], fill=(176, 180, 182), width=S)
    # body quads with the pattern texture
    AC = 10
    for k in range(N):
        (p0, _, u0), (p1, _, u1) = frame_at(k), frame_at(k+1)
        if k == 0: p0 = pts[0]
        w0, w1 = np.interp(k/N, PROF_S, PROF_W), np.interp((k+1)/N, PROF_S, PROF_W)
        for a in range(AC):
            v0, v1 = -1 + 2*a/AC, -1 + 2*(a+1)/AC
            quad = [(p0[0]+u0[0]*w0*v0, p0[1]+u0[1]*w0*v0), (p0[0]+u0[0]*w0*v1, p0[1]+u0[1]*w0*v1),
                    (p1[0]+u1[0]*w1*v1, p1[1]+u1[1]*w1*v1), (p1[0]+u1[0]*w1*v0, p1[1]+u1[1]*w1*v0)]
            d.polygon([(x*S, y*S) for x, y in quad], fill=tex((k+0.5)/N, (v0+v1)/2))
    for sgn in (-1, 1):                                                   # eyes
        (p, _, u) = frame_at(int(N*0.06)); w = np.interp(0.06, PROF_S, PROF_W)*0.78
        ex, ey = p[0]+u[0]*w*sgn, p[1]+u[1]*w*sgn
        d.ellipse([ex*S-7, ey*S-7, ex*S+7, ey*S+7], fill=(20, 20, 24))
    return im.filter(ImageFilter.GaussianBlur(0.8))

NF = 28; frames = []
for i in range(NF):
    hi = paint(i/NF)
    small = hi.resize((COLS, ROWS), Image.BOX)
    mask = np.asarray(hi.resize((W1, H1), Image.BOX).convert("L"), np.float32)/255
    sh = np.asarray(Image.fromarray((np.clip(mask*3, 0, 1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)).transform((W1, H1), Image.AFFINE, (1, 0, -16, 0, 1, -20)), np.float32)/255
    bg = BG*(1-0.55*sh[..., None])
    frames.append(M.ramp(small, gamma=0.55, bloom=0.25, bg=bg, boost=1.25))
save_webp(os.path.join(OUT, "koi.webp"), frames, [70]*NF, quality=62)
frames[0].save(os.path.join(OUT, "koi_0.png")); frames[9].save(os.path.join(OUT, "koi_9.png"))
print("koi", NF, "frames", os.path.getsize(os.path.join(OUT, "koi.webp")), "bytes", frames[0].size)
