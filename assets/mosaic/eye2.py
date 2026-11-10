"""High-density colour-character eye, rendered to an animated WebP (like the reference videos)."""
import sys, os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
random.seed(4); np.random.seed(4)
COLS, ROWS, CW, CH = 250, 76, 5, 9
W, H = COLS*CW, ROWS*CH                      # 1250 x 684
S = 2; PW, PH = W*S, H*S
K = PW/1800.0
CX, CY, HWID = PW/2, PH/2 + 20*K, PW*0.36
RAMP = " .,:;-~=+*xX#%@"
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 8)
GL = []
for ch in RAMP:
    im = Image.new("L", (CW, CH), 0); ImageDraw.Draw(im).text((0, -1), ch, fill=255, font=font)
    GL.append(np.asarray(im, np.float32)/255)
GL = np.stack(GL)                            # (n, CH, CW)

def curves(o):
    u = np.linspace(-1, 1, 300); us = u + 0.12*(1-u*u)
    sag = 46*K*(1-u*u)*(1-o)
    up = CY - 250*K*o*np.clip(1-us*us, 0, 1)**0.55 + sag - 18*K*u
    lo = CY + 150*K*o*np.clip(1-u*u, 0, 1)**0.7 + sag - 18*K*u
    return u, CX + u*HWID, up, lo
LASH = [(u, random.uniform(0.75, 1.3), random.uniform(-0.18, 0.18)) for u in np.linspace(-0.93, 0.95, 46)]
FIB = np.convolve(np.random.rand(720), np.ones(3)/3, mode="same")
yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
NOISE = np.asarray(Image.fromarray((np.random.rand(PH//6, PW//6)*255).astype(np.uint8)).resize((PW, PH), Image.BICUBIC), np.float32)/255
_, _, UP1, LO1 = curves(1.0)

def mask(xs, upc, loc):
    m = Image.new("L", (PW, PH), 0)
    ImageDraw.Draw(m).polygon(list(zip(xs, upc)) + list(zip(xs[::-1], loc[::-1])), fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(2)), np.float32)/255

def paint(o, look):
    u, xs, up, lo = curves(o)
    img = np.zeros((PH, PW, 3), np.float32)
    d = np.sqrt(((xx-CX)/(HWID*1.5))**2 + ((yy-CY)/(PH*0.6))**2)
    glow = np.clip(1-d, 0, 1)**1.4*(0.75+0.5*NOISE)
    img += glow[..., None]*np.array([120, 84, 104], np.float32)
    m_open, m_full = mask(xs, up, lo), mask(xs, UP1, LO1)
    lid = np.clip(m_full - m_open, 0, 1)
    lidshade = (0.5 + 0.5*np.clip((yy-(CY-270*K))/(400*K), 0, 1))*(0.8+0.4*NOISE)
    img = img*(1-lid[..., None]) + lid[..., None]*(np.array([170, 124, 146], np.float32)*lidshade[..., None])
    upi = np.interp(xx[0], xs, up); ux = (xx-CX)/HWID
    scl = 175*(1-0.55*np.abs(ux)**1.4)
    shadow = np.clip((yy-upi[None, :])/(95*K), 0.22, 1)
    img = img*(1-m_open[..., None]) + m_open[..., None]*np.stack([scl*shadow*1.0, scl*shadow*0.96, scl*shadow*1.0], -1)
    ix, iy, R = CX + look*110*K, CY - 30*K + 30*K*(1-o), 236*K
    r = np.sqrt((xx-ix)**2 + (yy-iy)**2); t = np.clip(r/R, 0, 1)
    ang = ((np.degrees(np.arctan2(yy-iy, xx-ix)) % 360)*2).astype(int) % 720
    fib = 0.7 + 0.75*FIB[ang]*t
    c_in, c_mid, c_out = np.array([200, 255, 245.]), np.array([34, 211, 238.]), np.array([10, 60, 110.])
    col = np.where(t[..., None] < 0.5, c_in + (c_mid-c_in)*(t[..., None]/0.5), c_mid + (c_out-c_mid)*((t[..., None]-0.5)/0.5)**1.5)
    col = col*fib[..., None]*shadow[..., None]
    mi = np.clip((R-r)/4, 0, 1)*m_open
    img = img*(1-mi[..., None]) + mi[..., None]*col
    mp = np.clip((62*K-r)/4, 0, 1)*m_open
    img = img*(1-mp[..., None]) + mp[..., None]*np.array([4, 6, 10.])
    hl = np.clip(1-np.sqrt((xx-(ix-80*K))**2 + (yy-(iy-88*K))**2)/(46*K), 0, 1)**0.7*m_open
    hl2 = np.clip(1-np.sqrt((xx-(ix+70*K))**2 + (yy-(iy+60*K))**2)/(20*K), 0, 1)*m_open*0.6
    img = img + (hl+hl2)[..., None]*255
    pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(pil)
    crease = up - (70*K*o + 24*K)
    dr.line(list(zip(xs[40:260], crease[40:260])), fill=(190, 140, 165), width=int(5*K))
    dr.line(list(zip(xs, up)), fill=(255, 240, 248), width=int(13*K))
    dr.line(list(zip(xs[12:288], lo[12:288])), fill=(215, 180, 196), width=int(5*K))
    for (lu, ln, jit) in LASH:
        x0 = float(np.interp(lu, u, xs)); y0 = float(np.interp(lu, u, up))
        a = (-math.pi/2 + lu*0.8 + jit)*o + (math.pi/2*0.55 + lu*0.5)*(1-o)
        L = (165 if abs(lu) < 0.7 else 105)*ln*K
        pts = [(x0, y0)]
        for k in range(1, 9):
            f = k/8; aa = a + (0.6*lu + 0.12)*f*o
            pts.append((x0 + math.cos(aa)*L*f, y0 + math.sin(aa)*L*f))
        dr.line(pts[:5], fill=(255, 244, 250), width=int(7*K)); dr.line(pts[4:], fill=(235, 215, 228), width=int(4*K))
    for lu in np.linspace(-0.75, 0.8, 22):
        x0 = float(np.interp(lu, u, xs)); y0 = float(np.interp(lu, u, lo))
        dr.line([(x0, y0), (x0 + lu*30*K, y0 + (38*o + 8)*K)], fill=(190, 160, 176), width=int(3*K))
    return np.asarray(pil.filter(ImageFilter.GaussianBlur(1.0)).resize((COLS, ROWS), Image.BOX), np.float32)

def to_chars(small):
    lum = small.max(-1)/255
    idx = np.clip((lum**0.75*len(RAMP)).astype(int), 0, len(RAMP)-1)
    colr = small/np.maximum(lum, 0.2)[..., None]*np.clip(lum*1.3+0.15, 0, 1)[..., None]     # bright tinted glyph colour
    g = GL[idx]                                                    # (R, C, CH, CW)
    out = g[..., None]*colr[:, :, None, None, :]
    out = out.transpose(0, 2, 1, 3, 4).reshape(ROWS*CH, COLS*CW, 3)
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    bloom = im.filter(ImageFilter.GaussianBlur(4))
    res = np.clip(np.asarray(im, np.float32) + 0.55*np.asarray(bloom, np.float32) + np.array([5, 7, 11.]), 0, 255)
    return Image.fromarray(res.astype(np.uint8))

ease = lambda x: x*x*(3-2*x)
FPS = 20; tl = []
def seg(n, f): tl.extend(f(i/max(1, n-1)) for i in range(n))
seg(8,  lambda t: (0.0, 0.0))
seg(18, lambda t: (ease(t), 0.0))
seg(14, lambda t: (1.0, 0.0))
seg(12, lambda t: (1.0, -0.85*ease(t)))
seg(10, lambda t: (1.0, -0.85))
seg(16, lambda t: (1.0, -0.85 + 1.7*ease(t)))
seg(10, lambda t: (1.0, 0.85))
seg(10, lambda t: (1.0, 0.85*(1-ease(t))))
seg(4,  lambda t: (1-ease(t), 0.0)); seg(5, lambda t: (ease(t), 0.0))
seg(20, lambda t: (1.0, 0.0))
seg(16, lambda t: (1-ease(t), 0.0))
cache = {}; frames = []
for o, l in tl:
    key = (round(o, 2), round(l, 2))
    if key not in cache: cache[key] = to_chars(paint(*key))
    frames.append(cache[key])
frames[0].save(os.path.join(OUT, "eye.webp"), save_all=True, append_images=frames[1:], duration=int(1000/FPS), loop=0, quality=72, method=4)
frames[40].save(os.path.join(OUT, "eye2_open.png")); frames[60].save(os.path.join(OUT, "eye2_left.png")); frames[20].save(os.path.join(OUT, "eye2_half.png"))
print(len(frames), "frames,", len(cache), "unique;", os.path.getsize(os.path.join(OUT, "eye.webp")), "bytes")
