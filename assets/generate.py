"""Assets for the GitHub profile README. Pure CSS + SMIL, no JS, no external fonts.
  header.svg  modern banner: animated ASCII field (brightness -> character density) with the name set in clean type
  cat.svg     the cat GIF converted to ASCII frames (cat.json)
Run:  python3 assets/generate.py assets [copper|mono|turquoise]"""
import math, html, sys, os, json

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
W = 900
THEMES = {  # accent, accent-light, field dim, field mid
    "copper":    ("#D4956A", "#F0C9A6", "#3A4250", "#6E7681"),
    "mono":      ("#8B949E", "#FFFFFF", "#1E252E", "#3B4654"),
    "turquoise": ("#2DD4BF", "#99F6E4", "#263A44", "#4B7C86"),
}
THEME = sys.argv[2] if len(sys.argv) > 2 else "mono"
ACCENT, ACCENT2, FDIM, FMID = THEMES[THEME]
BG, FG, DIM, MUTED = "#0D1117", "#E6EDF3", "#8B949E", "#2C333D"
HOLO = ["#EDE9FF", "#9DB3FF", "#FFF0A3", "#C8F7A8", "#FFC8E0", "#9BE7FF", "#EDE9FF"]
MONO = "'SFMono-Regular','SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"

def esc(s): return html.escape(s, quote=False)
def tl(x, y, s, size, cw, fill, extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" textLength="{len(s)*cw:.1f}" '
            f'lengthAdjust="spacing" xml:space="preserve"{extra}>{esc(s)}</text>')

# ------------------------------------------------------------------ ASCII field (the "shader")
RAMP = " .,:;-=+*#%@"
def field_frames(cols, rows, nf, left_floor=0.0):
    frames = []
    cx, cy = cols*0.62, rows*0.5
    for f in range(nf):
        t = f/nf*2*math.pi
        grid = []
        for y in range(rows):
            row = []
            for x in range(cols):
                dx, dy = (x-cx)/cols*2.2, (y-cy)/rows*1.1
                r = math.hypot(dx, dy)
                a = math.sin(x*0.085 + t + 1.8*math.sin(y*0.23 + t*0.5))        # flowing bands
                b = math.sin(r*6.5 - t*2.0)                                      # ripple from the right
                c = math.sin((x*0.03 - y*0.17) + t*0.8)                          # slow diagonal drift
                v = (a*0.45 + b*0.4 + c*0.15 + 1.0)/2.0                           # 0..1
                v = v**1.6
                # vignette: strongest on the right half, fades toward the text block on the left
                fade = left_floor + (1-left_floor)*min(1.0, max(0.0, (x/cols - 0.28)/0.5))
                v = v*fade*1.3
                row.append(RAMP[min(len(RAMP)-1, max(0, int(v*len(RAMP))))])
            grid.append(''.join(row))
        frames.append(grid)
    return frames

def split_layers(line):
    """Return (dim, mid, bright) strings with spaces where the char belongs to another layer."""
    dim = ''.join(c if c in ".,:;" else ' ' for c in line)
    mid = ''.join(c if c in "-=+*" else ' ' for c in line)
    bri = ''.join(c if c in "#%@" else ' ' for c in line)
    return dim, mid, bri

# ------------------------------------------------------------------ header.svg
def build_header():
    import random, pyfiglet
    random.seed(7)
    H = 270
    size, cw, lh = 12, 7.5, 15.0
    cols, rows = int(W/cw), int(H/lh) + 1
    nf, T = 36, 7.2
    css = f".k{{opacity:0;animation:k {T}s steps(1) infinite}}@keyframes k{{0%{{opacity:1}}{100/nf:.4f}%{{opacity:0}}100%{{opacity:0}}}}\n"
    css += ''.join(f".k{i}{{animation-delay:{i*T/nf:.3f}s}}\n" for i in range(nf))
    css += ".in{opacity:0;animation:fi 1.0s ease forwards;animation-delay:1.2s}.in2{animation-delay:1.5s}@keyframes fi{to{opacity:1}}\n"
    stops = ''.join(f'<stop offset="{i/(len(HOLO)-1):.3f}" stop-color="{c}"/>' for i, c in enumerate(HOLO))
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">',
         f'<style>{css}</style>',
         '<defs>'
         f'<linearGradient id="holo" gradientUnits="userSpaceOnUse" spreadMethod="repeat" x1="0" y1="0" x2="600" y2="90">{stops}'
         '<animateTransform attributeName="gradientTransform" type="translate" values="-600 0;0 0" dur="6s" repeatCount="indefinite"/></linearGradient>'
         f'<linearGradient id="shade" x1="0" x2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0.55"/><stop offset="0.55" stop-color="{BG}" stop-opacity="0.35"/>'
         f'<stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>'
         f'<clipPath id="r"><rect width="{W}" height="{H}" rx="14"/></clipPath>'
         '</defs>',
         f'<g clip-path="url(#r)"><rect width="{W}" height="{H}" fill="{BG}"/>']
    # living ASCII field across the whole banner, quieter on the left where the name sits
    frames = field_frames(cols, rows, nf, left_floor=0.42)
    for i, fr in enumerate(frames):
        parts = []
        for r, line in enumerate(fr):
            if not line.strip(): continue
            dim, mid, bri = split_layers(line)
            y = 12 + r*lh
            if dim.strip(): parts.append(tl(0, y, dim, size, cw, FDIM))
            if mid.strip(): parts.append(tl(0, y, mid, size, cw, FMID))
            if bri.strip(): parts.append(tl(0, y, bri, size, cw, ACCENT))
        p.append(f'<g class="k k{i}">' + ''.join(parts) + '</g>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#shade)"/>')
    # holographic pixel name, cells fly in from around and assemble
    name = pyfiglet.Figlet(font="ansi_shadow", width=200).renderText("ummugulsun").rstrip("\n").split("\n")
    bw, bh, ln = 8.0, 14.0, 2.0
    x0, y0 = 48, 46
    p.append('<g>')
    for r, l in enumerate(name):
        for c, ch in enumerate(l):
            x, y = x0 + c*bw, y0 + r*bh
            if ch == '█':
                ang = random.uniform(0, 2*math.pi); rad = random.uniform(120, 420)
                dx, dy = math.cos(ang)*rad, math.sin(ang)*rad
                beg = random.uniform(0.05, 0.7)
                p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-1:.1f}" height="{bh-1:.1f}" fill="url(#holo)" opacity="0">'
                         f'<animateTransform attributeName="transform" type="translate" from="{dx:.0f} {dy:.0f}" to="0 0" begin="{beg:.2f}s" dur="1.0s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
                         f'<animate attributeName="opacity" from="0" to="1" begin="{beg:.2f}s" dur="0.4s" fill="freeze"/></rect>')
                continue
            segs = []
            if ch == '║': segs.append((x+bw/2-ln/2, y, ln, bh))
            if ch == '═': segs.append((x, y+bh/2-ln/2, bw, ln))
            if ch in '╔╚': segs.append((x+bw/2-ln/2, y+bh/2-ln/2, bw/2+ln/2, ln))
            if ch in '╗╝': segs.append((x, y+bh/2-ln/2, bw/2+ln/2, ln))
            if ch in '╔╗': segs.append((x+bw/2-ln/2, y+bh/2-ln/2, ln, bh/2+ln/2))
            if ch in '╚╝': segs.append((x+bw/2-ln/2, y, ln, bh/2+ln/2))
            for sx, sy, sw, sh in segs:
                p.append(f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="{sh:.1f}" fill="#1F262E" class="in"/>')
    p.append('</g>')
    # type under the name
    p.append(f'<g font-family="{SANS}">')
    p.append(f'<text class="in" x="{x0}" y="190" font-size="22" font-weight="600" fill="{FG}" letter-spacing="-0.3">I design experiences, then I ship them.</text>')
    p.append(f'<text class="in in2" x="{x0}" y="222" font-size="14" fill="{DIM}">Computer Engineering student  ·  HCI  ·  bio-signal interfaces  ·  mobile product</text>')
    p.append('</g>')
    p.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="#30363D"/>')
    p.append('</g></svg>')
    open(os.path.join(OUT, "header.svg"), "w").write('\n'.join(p))

# ------------------------------------------------------------------ cat.svg
def build_cat():
    d = json.load(open(os.path.join(HERE, "cat.json")))
    cols, rows, frames, ms = d["cols"], d["rows"], d["frames"], d["duration_ms"]
    size, cw, lh = 11, 6.6, 12.0
    CW, CH = int(cols*cw + 16), int(rows*lh + 16)
    nf, T = len(frames), len(frames)*ms/1000.0
    css = f".f{{opacity:0;animation:cat {T:.3f}s steps(1) infinite}}@keyframes cat{{0%{{opacity:1}}{100/nf:.4f}%{{opacity:0}}100%{{opacity:0}}}}\n"
    css += ''.join(f".f{i}{{animation-delay:{i*T/nf:.3f}s}}\n" for i in range(nf))
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}" font-family="{MONO}">',
         f'<style>{css}</style>']
    for i, fr in enumerate(frames):
        p.append(f'<g class="f f{i}">' + ''.join(tl(8, 8+size+r*lh, l, size, cw, FG) for r, l in enumerate(fr) if l.strip()) + '</g>')
    p.append('</svg>')
    open(os.path.join(OUT, "cat.svg"), "w").write('\n'.join(p))

build_header(); build_cat()
for f in ("header.svg", "cat.svg"): print(f, os.path.getsize(os.path.join(OUT, f)), "bytes")
