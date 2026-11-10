"""'The Connection' (after the reference video): a field of letters fills the screen, a pair of eyes
looks out of it and blinks, the camera dives into a pupil, two profiles meet and merge into one,
then we pull back out of the pupil."""
import sys, os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from mosaic import Mosaic, save_webp
OUT = sys.argv[1]; random.seed(6); np.random.seed(6)
COLS, ROWS, CW, CH = 180, 56, 5, 8
LETTERS = " .:;cuLCJYOQ0Zmwqpdbkhao*#MW&8%B@"
M = Mosaic(COLS, ROWS, CW, CH, 8, LETTERS)
CLASSES = [(0.08, ".:;"), (0.2, "cuL:;"), (0.34, "CJYLOQ0Z"), (0.5, "mwqpdbkhao"), (0.72, "bdpqkhwmOZ0Q"), (0.9, "MW&8%B@#")]
W1, H1 = COLS*CW, ROWS*CH                  # 900 x 448
S = 3; PW, PH = W1*S, H1*S
TINT = (242, 214, 226)
cl = lambda x, a=0.0, b=1.0: max(a, min(b, x)); ease = lambda x: x*x*(3-2*x)
EYES = [(W1*0.26, H1*0.56, 1), (W1*0.74, H1*0.56, -1)]
LASH = [(u, random.uniform(0.8, 1.25), random.uniform(-0.15, 0.15)) for u in np.linspace(-0.9, 0.92, 22)]

def paint_eyes(o):
    """greyscale field with two eyes cut into it, at S x resolution"""
    im = Image.new("L", (PW, PH), 135); d = ImageDraw.Draw(im)
    # soft face shading: brow shadow + nose bridge
    for (ex, ey, m) in EYES:
        pass
    d.rectangle([(W1*0.5-14)*S, 0, (W1*0.5+14)*S, PH], fill=165)
    im = im.filter(ImageFilter.GaussianBlur(26*S/3)); d = ImageDraw.Draw(im)
    for (ex, ey, m) in EYES:
        u = np.linspace(-1, 1, 160); hw = 185
        xs = ex + u*hw
        sag = 26*(1-u*u)*(1-o)
        up = ey - 98*o*np.clip(1-(u+0.1*m*(1-u*u))**2, 0, 1)**0.55 + sag + 8*u*m
        lo = ey + 62*o*np.clip(1-u*u, 0, 1)**0.7 + sag + 8*u*m
        pts = [(x*S, y*S) for x, y in zip(xs, up)] + [(x*S, y*S) for x, y in zip(xs[::-1], lo[::-1])]
        if o > 0.03:
            msk = Image.new("L", (PW, PH), 0); ImageDraw.Draw(msk).polygon(pts, fill=255)
            eye = Image.new("L", (PW, PH), 0); de = ImageDraw.Draw(eye)
            R = 76; ix, iy = ex, ey - 10
            de.ellipse([(ix-R)*S, (iy-R)*S, (ix+R)*S, (iy+R)*S], fill=150)
            for a in np.linspace(0, 2*math.pi, 56, endpoint=False):
                de.line([(ix+math.cos(a)*30)*S, (iy+math.sin(a)*30)*S, (ix+math.cos(a)*R)*S, (iy+math.sin(a)*R)*S], fill=random.choice((90, 170, 235)), width=3*S)
            de.ellipse([(ix-R)*S, (iy-R)*S, (ix+R)*S, (iy+R)*S], outline=255, width=7*S)
            de.ellipse([(ix-30)*S, (iy-30)*S, (ix+30)*S, (iy+30)*S], fill=0)
            de.ellipse([(ix-36)*S, (iy-40)*S, (ix-14)*S, (iy-18)*S], fill=255)
            im.paste(eye, (0, 0), msk)
        d.line([(x*S, y*S) for x, y in zip(xs, up)], fill=255, width=7*S)
        d.line([(x*S, y*S) for x, y in zip(xs[6:-6], lo[6:-6])], fill=235, width=4*S)
        cr = up - (26*o + 12)
        d.line([(x*S, y*S) for x, y in zip(xs[14:-14], cr[14:-14])], fill=20, width=6*S)
        for (lu, ln, jit) in LASH:
            x0 = float(np.interp(lu, u, xs)); y0 = float(np.interp(lu, u, up))
            a = (-math.pi/2 + lu*0.8 + jit)*o + (math.pi/2*0.6 + lu*0.5)*(1-o)
            L = (58 if abs(lu) < 0.7 else 38)*ln
            d.line([(x0*S, y0*S), ((x0+math.cos(a)*L*0.6)*S, (y0+math.sin(a)*L*0.6)*S), ((x0+math.cos(a+0.5*lu)*L)*S, (y0+math.sin(a+0.5*lu)*L)*S)], fill=255, width=4*S)
        # brow
        bx = ex + np.linspace(-185, 185, 40); by = ey - 168 - 18*np.sin(np.linspace(0.2, 2.9, 40)) 
        d.line([(x*S, y*S) for x, y in zip(bx, by)], fill=10, width=16*S)
    return im

def view(im, z, cx, cy):
    """zoom by z around (cx, cy) in 1x coords, sample down to the character grid"""
    w, h = W1/z, H1/z
    x0 = cl(cx - w/2*(1 + (cx-W1/2)/(W1/2)*0), -1e9, 1e9)
    box = ((cx-w/2)*S, (cy-h/2)*S, (cx+w/2)*S, (cy+h/2)*S)
    return np.asarray(im.resize((COLS, ROWS), Image.BOX if z < 1.5 else Image.BILINEAR, box=box), np.float32)/255

PROFILE = [(0.42, 0.02), (0.56, 0.05), (0.64, 0.14), (0.69, 0.30), (0.68, 0.36), (0.84, 0.52), (0.73, 0.57), (0.76, 0.63), (0.70, 0.67),
           (0.75, 0.72), (0.69, 0.78), (0.71, 0.88), (0.56, 0.97), (0.40, 1.0), (0.24, 1.0), (0.10, 0.82), (0.03, 0.56), (0.08, 0.28), (0.22, 0.10)]
STARS = [(random.uniform(0, W1), random.uniform(0, H1), random.uniform(0.25, 0.9), random.uniform(0, 6.28)) for _ in range(28)]

def paint_inner(p, q, r):
    """p: faces appear/approach 0..1, q: merge to sphere 0..1, r: sphere shrink 0..1"""
    S2 = 2; im = Image.new("L", (W1*S2, H1*S2), 0); d = ImageDraw.Draw(im)
    for (x, y, b, ph) in STARS:
        v = int(255*b*(0.5+0.5*math.sin(ph + p*8 + q*5 + r*5))*cl(p*3))
        if v > 20:
            d.line([(x-7)*S2, y*S2, (x+7)*S2, y*S2], fill=v, width=1); d.line([x*S2, (y-7)*S2, x*S2, (y+7)*S2], fill=v, width=1)
            d.ellipse([x*S2-2, y*S2-2, x*S2+2, y*S2+2], fill=min(255, v+60))
    size = 300; cy = H1*0.5
    gap = 150*(1-ease(p)) + 6
    alpha = cl(p*2.2)*(1-q)
    if alpha > 0.01:
        layer = Image.new("L", im.size, 0); dl = ImageDraw.Draw(layer)
        for side in (-1, 1):
            # left face looks right (nose at +x); right face is mirrored
            ox = W1*0.5 + side*(gap + size*0.84) 
            pts = [((ox - side*(px)*size)*S2, (cy + (py-0.5)*size)*S2) for px, py in PROFILE]
            dl.polygon(pts, fill=255)
        layer = layer.filter(ImageFilter.GaussianBlur(2))
        yy, xx = np.mgrid[0:H1*S2, 0:W1*S2].astype(np.float32)
        shade = 0.55 + 0.45*np.clip(1-np.abs(xx/S2-W1*0.5)/(size*0.9), 0, 1)       # brighter where they meet
        arr = np.maximum(np.asarray(im, np.float32), np.asarray(layer, np.float32)*shade*alpha*0.92)
        im = Image.fromarray(arr.astype(np.uint8))
    if q > 0.01:
        R = 118*(1-ease(r)) + 0.0
        if R > 2:
            yy, xx = np.mgrid[0:H1*S2, 0:W1*S2].astype(np.float32)
            dd = np.sqrt((xx/S2-W1*0.5)**2 + (yy/S2-cy)**2)/R
            sph = np.clip(1-dd**2, 0, 1)**0.5*(dd < 1)*255*(0.55+0.45*np.clip(1-dd, 0, 1))*ease(q)
            im = Image.fromarray(np.maximum(np.asarray(im, np.float32), sph).astype(np.uint8))
    return np.asarray(im.resize((COLS, ROWS), Image.BOX), np.float32)/255

frames, durs = [], []
def emit(b, reveal=None, dur=80):
    frames.append(M.letters(b, TINT, CLASSES, bloom=0.4, reveal=reveal)); durs.append(dur)
order = np.random.RandomState(3).rand(ROWS, COLS)*0.35 + np.linspace(0, 0.65, ROWS)[:, None]
base_open = paint_eyes(1.0)
ex, ey = EYES[1][0], EYES[1][1] - 10
b_open = view(base_open, 1, W1/2, H1/2)
for i in range(13): emit(b_open, reveal=order <= (i/12)*1.0001)                      # the field types itself in
for i in range(6): emit(b_open)
for o in (0.7, 0.35, 0.0, 0.0, 0.35, 0.7, 1.0): emit(view(paint_eyes(o), 1, W1/2, H1/2), dur=55)   # blink
for i in range(7): emit(b_open)
ZN = 15
def zoomf(t):
    z = math.exp(ease(t)*math.log(46)); k = cl(t*1.6)
    return view(base_open, z, W1/2 + (ex-W1/2)*ease(k), H1/2 + (ey-H1/2)*ease(k))
for i in range(ZN): emit(zoomf(i/(ZN-1)))
for i in range(22): emit(paint_inner(i/21, 0, 0))                                   # two profiles meet
for i in range(6): emit(paint_inner(1, 0, 0))
for i in range(8): emit(paint_inner(1, (i+1)/8, 0))                                 # ... and become one
for i in range(5): emit(paint_inner(1, 1, 0))
for i in range(9): emit(paint_inner(1, 1, (i+1)/9))                                 # shrinks to a point
for i in range(ZN): emit(zoomf(1 - i/(ZN-1)))                                       # pull back out of the pupil
emit(b_open, dur=1600)
save_webp(os.path.join(OUT, "connection.webp"), frames, durs, quality=45)
for name, i in (("field", 14), ("zoom", 36), ("faces", 62), ("one", 78)): frames[i].save(os.path.join(OUT, f"conn_{name}.png"))
print("connection", len(frames), "frames", os.path.getsize(os.path.join(OUT, "connection.webp")), "bytes", frames[0].size)
