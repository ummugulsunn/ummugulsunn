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

# ------------------------------------------------------------------ header.svg  ("signal -> interface")
# 0-1s: the canvas is noise (faint static). 1-2.5s: one bright scan line sweeps left to right and, where it
# passes, the static resolves into the name. After: the name stays, the static breathes slowly, one line is typed.
def build_header():
    import random, pyfiglet
    random.seed(11)
    H = 320
    size, cw, lh = 12, 7.5, 15.0
    cols, rows = 120, 21
    NOISE = ".,:;-=+*"
    TONES = [("#1C232C", 0.55), ("#2A323C", 0.33), ("#3D4753", 0.12)]       # dim / mid / brighter
    # name mask from a block font, doubled vertically
    fig = pyfiglet.Figlet(font="banner3", width=200).renderText("ummugulsun").rstrip("\n").split("\n")
    mw = max(len(l) for l in fig); fig = [l.ljust(mw) for l in fig]
    mx0, my0 = 6, 3
    mask = set()
    for r, l in enumerate(fig):
        for c, ch in enumerate(l):
            if ch != ' ':
                mask.add((my0 + 2*r, mx0 + c)); mask.add((my0 + 2*r + 1, mx0 + c))
    def pick_tone():
        u = random.random(); acc = 0
        for col, w in TONES:
            acc += w
            if u <= acc: return col
        return TONES[-1][0]
    def noise_layer():
        """one static field: per tone, rows of chars (spaces elsewhere) so each tone is one <text> per row"""
        parts = []
        grid = [[(random.choice(NOISE), pick_tone()) for _ in range(cols)] for _ in range(rows)]
        for col, _ in TONES:
            for r in range(rows):
                line = ''.join(ch if tone == col else ' ' for ch, tone in grid[r])
                if line.strip(): parts.append(tl(0, 12 + r*lh, line, size, cw, col))
        return ''.join(parts)
    # the name: dense glyphs; edges a little lighter than the core
    name_parts = []
    for r in range(rows):
        line = []
        for c in range(cols):
            if (r, c) in mask:
                nb = sum(((r+dr, c+dc) in mask) for dr in (-1, 0, 1) for dc in (-1, 0, 1))
                line.append('@' if nb >= 8 else ('#' if nb >= 6 else '%'))
            else:
                line.append(' ')
        line = ''.join(line)
        if line.strip():
            # backing so the static underneath does not bleed through the glyphs
            for c, ch in enumerate(line):
                if ch != ' ':
                    name_parts.append(f'<rect x="{c*cw:.1f}" y="{r*lh:.1f}" width="{cw:.1f}" height="{lh:.1f}" fill="{BG}"/>')
            name_parts.append(tl(0, 13 + r*lh, line, 16, cw, "#E6EDF3", ' font-weight="bold"'))
    reveal_x0, reveal_x1 = (mx0-1)*cw, (mx0+mw+1)*cw
    css = """
.nA{animation:xa 6s ease-in-out infinite}.nB{animation:xb 6s ease-in-out infinite}
@keyframes xa{0%,100%{opacity:1}50%{opacity:0}}@keyframes xb{0%,100%{opacity:0}50%{opacity:1}}
.static{animation:settle 1.4s ease forwards;animation-delay:1.6s}@keyframes settle{to{opacity:.55}}
.ty{opacity:0;animation:fi .01s linear forwards}@keyframes fi{to{opacity:1}}
.cur{opacity:0;animation:fi .01s linear 2.7s forwards, blink 1.1s steps(1) 2.7s infinite}@keyframes blink{0%{opacity:1}50%{opacity:0}100%{opacity:1}}
.sub{opacity:0;animation:fi 1s ease forwards;animation-delay:4.2s}
"""
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">',
         f'<style>{css}</style>',
         '<defs>'
         f'<clipPath id="r"><rect width="{W}" height="{H}" rx="14"/></clipPath>'
         f'<clipPath id="reveal"><rect x="{reveal_x0:.1f}" y="0" width="0" height="{H}">'
         f'<animate attributeName="width" from="0" to="{reveal_x1-reveal_x0:.1f}" begin="1.0s" dur="1.5s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/></rect></clipPath>'
         '<linearGradient id="trail" x1="0" x2="1"><stop offset="0" stop-color="#E6EDF3" stop-opacity="0"/><stop offset="1" stop-color="#E6EDF3" stop-opacity="0.35"/></linearGradient>'
         '</defs>',
         f'<g clip-path="url(#r)"><rect width="{W}" height="{H}" fill="{BG}"/>']
    p.append('<g class="static"><g class="nA">' + noise_layer() + '</g><g class="nB">' + noise_layer() + '</g></g>')
    p.append('<g clip-path="url(#reveal)">' + ''.join(name_parts) + '</g>')
    # the scan line with a short trail, sweeping with the reveal, then gone
    p.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.05;0.9;1" begin="1.0s" dur="1.6s" fill="freeze"/>'
             f'<g><animateTransform attributeName="transform" type="translate" from="{reveal_x0:.1f} 0" to="{reveal_x1:.1f} 0" begin="1.0s" dur="1.5s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/>'
             f'<rect x="-70" y="0" width="70" height="{H}" fill="url(#trail)"/><rect x="-1" y="0" width="2" height="{H}" fill="#FFFFFF"/></g></g>')
    # typed line + subtitle
    typed = "signal  →  interface"
    tx, ty = mx0*cw, 12 + 18*lh
    for i, ch in enumerate(typed):
        p.append(f'<text x="{tx+i*cw:.1f}" y="{ty}" font-size="13" fill="#E6EDF3" class="ty" style="animation-delay:{2.7+i*0.06:.2f}s" xml:space="preserve">{esc(ch)}</text>')
    p.append(f'<text x="{tx+len(typed)*cw:.1f}" y="{ty}" font-size="13" fill="#E6EDF3" class="cur">▌</text>')
    p.append(f'<text class="sub" x="{tx}" y="{ty+26}" font-size="12" fill="{DIM}" xml:space="preserve">{esc("ummugulsun turkmen  ·  computer engineering student  ·  hci  ·  bio-signal interfaces  ·  mobile product")}</text>')
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
