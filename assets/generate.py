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
    "mono":      ("#C9D1D9", "#FFFFFF", "#2E3640", "#6E7681"),
    "turquoise": ("#2DD4BF", "#99F6E4", "#263A44", "#4B7C86"),
}
THEME = sys.argv[2] if len(sys.argv) > 2 else "mono"
ACCENT, ACCENT2, FDIM, FMID = THEMES[THEME]
BG, FG, DIM, MUTED = "#0D1117", "#E6EDF3", "#8B949E", "#2C333D"
MONO = "'SFMono-Regular','SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"

def esc(s): return html.escape(s, quote=False)
def tl(x, y, s, size, cw, fill, extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" textLength="{len(s)*cw:.1f}" '
            f'lengthAdjust="spacing" xml:space="preserve"{extra}>{esc(s)}</text>')

# ------------------------------------------------------------------ ASCII field (the "shader")
RAMP = " .,:;-=+*#%@"
def field_frames(cols, rows, nf):
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
                fade = min(1.0, max(0.0, (x/cols - 0.28)/0.5))
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
    H = 230
    size, cw, lh = 12, 7.5, 15.0
    cols, rows = int(W/cw), int(H/lh)
    nf, T = 36, 7.2
    css = f".k{{opacity:0;animation:k {T}s steps(1) infinite}}@keyframes k{{0%{{opacity:1}}{100/nf:.4f}%{{opacity:0}}100%{{opacity:0}}}}\n"
    css += ''.join(f".k{i}{{animation-delay:{i*T/nf:.3f}s}}\n" for i in range(nf))
    css += ".in{opacity:0;animation:fi 1.2s ease forwards}.in2{animation-delay:.35s}.in3{animation-delay:.6s}@keyframes fi{to{opacity:1}}\n"
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">',
         f'<style>{css}</style>',
         '<defs>'
         f'<linearGradient id="shade" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset="0.52" stop-color="{BG}" stop-opacity="0.96"/>'
         f'<stop offset="0.8" stop-color="{BG}" stop-opacity="0"/></linearGradient>'
         f'<linearGradient id="acc" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{ACCENT2}"/></linearGradient>'
         f'<clipPath id="r"><rect width="{W}" height="{H}" rx="14"/></clipPath>'
         '</defs>',
         f'<g clip-path="url(#r)"><rect width="{W}" height="{H}" fill="{BG}"/>']
    frames = field_frames(cols, rows, nf)
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
    # type block (left)
    x0 = 48
    p.append(f'<g font-family="{SANS}">')
    p.append(f'<text class="in" x="{x0}" y="78" font-size="13" fill="{ACCENT}" font-family="{MONO}" letter-spacing="3">UMMUGULSUN TURKMEN</text>')
    p.append(f'<text class="in in2" x="{x0}" y="128" font-size="44" font-weight="700" fill="{FG}" letter-spacing="-1.5">I design <tspan fill="url(#acc)">experiences</tspan>,</text>')
    p.append(f'<text class="in in2" x="{x0}" y="172" font-size="44" font-weight="300" fill="{FG}" letter-spacing="-1">then I ship them.</text>')
    p.append(f'<text class="in in3" x="{x0}" y="204" font-size="14" fill="{DIM}">Computer Engineering student  ·  HCI  ·  bio-signal interfaces  ·  mobile product</text>')
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
