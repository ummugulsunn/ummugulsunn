"""Dark-luxury ASCII dashboard for the GitHub profile README. Pure SVG: CSS + SMIL animations, no JS,
no external fonts. Every panel is a separate SVG so the README can wrap each one in a link.

  hero.svg        EEG signal -> samples -> code composition, thin-line ASCII name, typed motto
  about.svg       glass panel: bio + stat chips + the ASCII cat (cat.json)
  card-*.svg      four project cards (wrapped in links by the README)
  btn-*.svg       social buttons (wrapped in links by the README)

Run:  python3 assets/generate.py assets
"""
import math, html, sys, os, json, random
import pyfiglet

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
random.seed(5)

BG0, BG1 = "#06080C", "#0D1117"
TEXT, DIM, MUTED, LINE = "#E6EDF3", "#8B949E", "#3D4753", "#1F262E"
CYAN, PURPLE, MINT = "#22D3EE", "#A78BFA", "#5EEAD4"
MONO = "'SFMono-Regular','SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

def esc(s): return html.escape(s, quote=False)
def tl(x, y, s, size, cw, fill, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" textLength="{len(s)*cw:.1f}" '
            f'lengthAdjust="spacing" xml:space="preserve"{extra}>{esc(s)}</text>')
def t(x, y, s, size, fill, extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra} xml:space="preserve">{esc(s)}</text>'

# ------------------------------------------------------------------ shared defs: glass, glow, grid
def defs(uid):
    return (
        '<defs>'
        f'<radialGradient id="{uid}bg" cx="35%" cy="20%" r="90%"><stop offset="0" stop-color="#121923"/><stop offset="0.55" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/></radialGradient>'
        f'<linearGradient id="{uid}glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.07"/><stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0.025"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0.05"/></linearGradient>'
        f'<linearGradient id="{uid}edge" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="0.35" stop-color="{CYAN}" stop-opacity="0.9"/><stop offset="0.65" stop-color="{PURPLE}" stop-opacity="0.9"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="{uid}sheen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/><stop offset="0.45" stop-color="#FFFFFF" stop-opacity="0.045"/><stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="{uid}sig" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{PURPLE}"/></linearGradient>'
        f'<filter id="{uid}glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        f'<filter id="{uid}glow2" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        f'<pattern id="{uid}dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.7" fill="#FFFFFF" fill-opacity="0.07"/></pattern>'
        '</defs>'
    )

def glass(x, y, w, h, uid, r=16, edge=True):
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#{uid}glass)" stroke="#FFFFFF" stroke-opacity="0.10"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#{uid}sheen)"/>')
    if edge:
        s += f'<rect x="{x+r}" y="{y-0.5}" width="{w-2*r}" height="1.5" fill="url(#{uid}edge)" class="pulse"/>'
    return s

def ascii_frame(x, y, w, h, label=None, tag=None):
    """thin brackets at the corners + optional labels, like a blueprint callout"""
    s = ''
    for (cx, cy, hx, vy) in ((x, y, 1, 1), (x+w, y, -1, 1), (x, y+h, 1, -1), (x+w, y+h, -1, -1)):
        s += f'<path d="M{cx+hx*14},{cy} L{cx},{cy} L{cx},{cy+vy*14}" fill="none" stroke="{MUTED}" stroke-width="1"/>'
    if label: s += t(x+22, y-7, label, 10, DIM, f' font-family="{MONO}" letter-spacing="2"')
    if tag:   s += t(x+w-22, y-7, tag, 10, MUTED, f' font-family="{MONO}" letter-spacing="1" text-anchor="end"')
    return s

CSS_COMMON = """
.pulse{animation:pulse 3.6s ease-in-out infinite}@keyframes pulse{0%,100%{opacity:.55}50%{opacity:1}}
.glowpulse{animation:gp 4s ease-in-out infinite}@keyframes gp{0%,100%{opacity:.35}50%{opacity:.9}}
.fi{opacity:0;animation:fi 1s ease forwards}@keyframes fi{to{opacity:1}}
"""

# ------------------------------------------------------------------ thin-line ASCII name with neon diaeresis
def name_block(word, font="shadow"):
    """Render each letter separately (no smushing) so every letter's column span is known."""
    fig = pyfiglet.Figlet(font=font, width=200)
    pieces = [fig.renderText(ch).rstrip("\n").split("\n") for ch in word]
    rows = max(len(p) for p in pieces)
    norm = []
    for p in pieces:
        w = max(len(x) for x in p)
        norm.append([l.ljust(w) for l in p] + [' '*w]*(rows-len(p)))
    spans, x = [], 0
    for p in norm:
        w = len(p[0]); spans.append((x, w)); x += w
    lines = [''.join(p[r] for p in norm) for r in range(rows)]
    while lines and not lines[0].strip(): lines.pop(0)
    while lines and not lines[-1].strip(): lines.pop()
    return lines, spans

# ------------------------------------------------------------------ hero
def build_hero():
    W, H = 900, 430; uid = "h"
    css = CSS_COMMON + """
.ty{opacity:0;animation:fi .01s linear forwards}
.cur{opacity:0;animation:fi .01s linear 3.4s forwards, blink 1.1s steps(1) 3.4s infinite}@keyframes blink{0%{opacity:1}50%{opacity:0}100%{opacity:1}}
.tok{animation:tok 2.8s ease-in-out infinite}@keyframes tok{0%,100%{opacity:.15}50%{opacity:.9}}
.d1{animation-delay:.3s}.d2{animation-delay:.6s}.d3{animation-delay:.9s}.d4{animation-delay:1.2s}.d5{animation-delay:1.5s}.d6{animation-delay:1.8s}.d7{animation-delay:2.1s}
"""
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">',
         f'<style>{css}</style>', defs(uid),
         f'<rect width="{W}" height="{H}" rx="18" fill="url(#{uid}bg)"/>',
         f'<rect width="{W}" height="{H}" rx="18" fill="url(#{uid}dots)"/>']
    p.append(f'<circle cx="700" cy="120" r="160" fill="{CYAN}" fill-opacity="0.05" filter="url(#{uid}glow2)" class="glowpulse"/>')
    p.append(f'<circle cx="820" cy="360" r="120" fill="{PURPLE}" fill-opacity="0.06" filter="url(#{uid}glow2)" class="glowpulse" style="animation-delay:2s"/>')
    p.append(glass(18, 18, W-36, H-36, uid, r=16))
    p.append(ascii_frame(18, 18, W-36, H-36, label="// PORTFOLIO  ·  HCI  ·  BIO-SIGNAL INTERFACES", tag="v2026.11  ·  SIG:EEG"))

    # ---- left: the name in a thin-line font, neon diaeresis on every Ü
    x0, y0 = 52, 80
    size, cw, lh = 12, 7.2, 14.0
    def draw_name(word, y, delay):
        lines, spans = name_block(word)
        out = [f'<g class="fi" style="animation-delay:{delay}s">']
        for (st, w), ch in zip(spans, word):
            if ch == 'U':
                cxp = x0 + (st + w/2 - 0.5)*cw
                for dx in (-4, 4):
                    out.append(f'<circle cx="{cxp+dx:.1f}" cy="{y-6:.1f}" r="1.7" fill="{CYAN}" filter="url(#{uid}glow)" class="pulse"/>')
        for r, l in enumerate(lines):
            out.append(tl(x0, y + 10 + r*lh, l, size, cw, TEXT, f' filter="url(#{uid}glow)" fill-opacity="0.95"'))
        out.append('</g>')
        return ''.join(out), len(lines)
    s1, n1 = draw_name("UMMUGULSUN", y0, 0.2); p.append(s1)
    y1 = y0 + n1*lh + 22
    s2, n2 = draw_name("TURKMEN", y1, 0.5); p.append(s2)
    yb = y1 + n2*lh + 34
    typed = "I design experiences, then I ship them."
    p.append(t(x0, yb, "$", 14, CYAN, ' class="fi" style="animation-delay:1.0s"'))
    for i, ch in enumerate(typed):
        p.append(f'<text x="{x0+16+i*8.4:.1f}" y="{yb}" font-size="14" fill="{TEXT}" class="ty" style="animation-delay:{1.3+i*0.05:.2f}s" xml:space="preserve">{esc(ch)}</text>')
    p.append(f'<rect x="{x0+16+len(typed)*8.4:.1f}" y="{yb-12}" width="8" height="15" fill="{CYAN}" class="cur"/>')
    p.append(t(x0, yb+30, "computer engineering  ·  product design  ·  hci  ·  mobile", 11, DIM, ' class="fi" style="animation-delay:3.6s" letter-spacing="0.5"'))

    # ---- right: signal -> samples -> code, three nested svgs
    zx, zy, zw, zh = 500, 62, 364, 280
    p.append(ascii_frame(zx, zy, zw, zh, label="EEG → SAMPLE → INTERFACE", tag="Fp1 · 256 Hz"))
    z1w = 112
    p.append(f'<svg x="{zx}" y="{zy}" width="{z1w}" height="{zh}" viewBox="0 0 {z1w} {zh}">')
    ecw, elh = 6.0, 11.0
    per_cols, rows = 40, 9
    vals = [1.1*math.sin(i/per_cols*2*math.pi*2) + 0.5*math.sin(i/per_cols*2*math.pi*5 + 1) for i in range(per_cols)]
    for c0 in (12, 31):
        for k in range(-3, 4): vals[(c0+k) % per_cols] += 2.2*math.exp(-(k*k)/1.6)
    lo, hi = min(vals), max(vals)
    ys = [int(round((rows-1)-(v-lo)/(hi-lo)*(rows-1))) for v in vals]
    g = [[' ']*per_cols for _ in range(rows)]
    for i in range(per_cols):
        y, yn = ys[i], ys[(i+1) % per_cols]
        g[y][i] = '_' if y == yn else ('/' if yn < y else '\\')
        step = -1 if yn < y else 1
        for yy in range(y+step, yn, step): g[yy][i] = '|'
    trace = [''.join(r)*2 for r in g]
    per_px = per_cols*ecw
    for ch_i, (oy, col, op) in enumerate(((58, CYAN, 1.0), (158, PURPLE, 0.55))):
        p.append(f'<g opacity="{op}" filter="url(#{uid}glow)"><g><animateTransform attributeName="transform" type="translate" from="0 0" to="{-per_px:.1f} 0" dur="{6 if ch_i==0 else 8}s" repeatCount="indefinite"/>'
                 + ''.join(tl(0, oy + r*elh, l, 10, ecw, col) for r, l in enumerate(trace) if l.strip()) + '</g></g>')
    p.append(t(4, zh-8, "signal", 9, DIM, ' letter-spacing="2"'))
    p.append('</svg>')
    z2x, z2w = zx + z1w + 6, 96
    p.append(f'<svg x="{z2x}" y="{zy}" width="{z2w}" height="{zh}" viewBox="0 0 {z2w} {zh}">')
    qcols, qrows, qcw, qlh = 14, 8, 6.8, 11.0
    for oy, base in ((56, 0), (156, 7)):
        grid = [[' ']*qcols for _ in range(qrows)]
        for c in range(qcols):
            v = ys[(c*2 + base) % per_cols]
            r = int(round(v/(rows-1)*(qrows-1)))
            for rr in range(r, qrows): grid[rr][c] = '#' if rr == r else ':'
        for r in range(qrows):
            line = ''.join(grid[r])
            if line.strip(): p.append(tl(0, oy + r*qlh, line, 10, qcw, f"url(#{uid}sig)", f' fill-opacity="{0.9 if r%2==0 else 0.6}"'))
        p.append(tl(0, oy + qrows*qlh + 4, "|  |  |  |  |  |", 9, qcw, MUTED))
    p.append(f'<rect x="0" y="40" width="{z2w}" height="{zh-70}" fill="{CYAN}" fill-opacity="0.04" class="pulse"/>')
    p.append(t(4, zh-8, "sample", 9, DIM, ' letter-spacing="2"'))
    p.append('</svg>')
    z3x, z3w = z2x + z2w + 6, zw - z1w - z2w - 12
    p.append(f'<svg x="{z3x}" y="{zy}" width="{z3w}" height="{zh}" viewBox="0 0 {z3w} {zh}">')
    tokens = ["if blink:", "  emit(cmd)", "fp1 = 0x1F", "ui.toggle()", "01 10 11", "{ x, y }", "fn → view", "λ 8–13 Hz",
              "state: idle", "tap → ok", "→ render()", "# 5.0 ★", "snr 24 dB", "await ui", "<Interface/>", "ok ✓"]
    for i, tok in enumerate(tokens):
        col = i % 2; row = i // 2
        xx = 6 + col*70; yy = 52 + row*24
        c = [CYAN, PURPLE, TEXT, MINT][i % 4]
        p.append(t(xx, yy, tok, 9, c, f' class="tok d{(i%7)+1}" fill-opacity="0.9"'))
    p.append(t(4, zh-8, "interface", 9, DIM, ' letter-spacing="2"'))
    p.append('</svg>')
    for ax in (zx + z1w - 2, z2x + z2w - 2):
        p.append(t(ax, zy + zh/2, "→", 12, DIM, ' text-anchor="middle" class="pulse"'))
    p.append(t(52, H-34, "● live", 10, MINT, ' class="pulse"'))
    p.append(t(100, H-34, "ummugulsun.me   ·   github.com/ummugulsunn", 10, DIM, ' letter-spacing="1"'))
    p.append(t(W-52, H-34, "built from signals", 10, MUTED, ' text-anchor="end" letter-spacing="1"'))
    p.append('</svg>')
    open(os.path.join(OUT, "hero.svg"), "w").write('\n'.join(p))

# ------------------------------------------------------------------ about panel (with the cat)
def build_about():
    W, H = 900, 200; uid = "a"
    d = json.load(open(os.path.join(HERE, "cat.json")))
    cols, rows, frames, ms = d["cols"], d["rows"], d["frames"], d["duration_ms"]
    nf, T = len(frames), len(frames)*ms/1000.0
    css = CSS_COMMON + f".f{{opacity:0;animation:cat {T:.3f}s steps(1) infinite}}@keyframes cat{{0%{{opacity:1}}{100/nf:.4f}%{{opacity:0}}100%{{opacity:0}}}}\n"
    css += ''.join(f".f{i}{{animation-delay:{i*T/nf:.3f}s}}\n" for i in range(nf))
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">',
         f'<style>{css}</style>', defs(uid),
         f'<rect width="{W}" height="{H}" rx="18" fill="url(#{uid}bg)"/>', glass(18, 18, W-36, H-36, uid)]
    p.append(ascii_frame(18, 18, W-36, H-36, label="[ ABOUT ]", tag="01"))
    x0 = 52
    lines = ["Computer Engineering student with a product-first mindset. I take raw signals —",
             "EEG, keystrokes, behavior — and turn them into interfaces people actually use.",
             "Shipped a 5.0-rated app on Google Play; prototyping touchless interaction with EEG."]
    for i, l in enumerate(lines):
        p.append(t(x0, 66 + i*22, l, 13.5, TEXT if i < 2 else DIM, f' font-family="{SANS}"'))
    chips = [("5.0 ★  Google Play", CYAN), ("37 ★  Stremio addon", PURPLE), ("EEG  prototype", MINT)]
    cx = x0
    for label, col in chips:
        w = len(label)*7.2 + 26
        p.append(f'<rect x="{cx:.0f}" y="138" width="{w:.0f}" height="26" rx="13" fill="{col}" fill-opacity="0.08" stroke="{col}" stroke-opacity="0.45"/>')
        p.append(t(cx+13, 155, label, 11, col, ' letter-spacing="0.5"'))
        cx += w + 10
    scw, slh, ssz = 3.6, 4.6, 5.5
    ox, oy = W - 70 - cols*scw, 22
    p.append('<g opacity="0.85">')
    for i, fr in enumerate(frames):
        p.append(f'<g class="f f{i}">' + ''.join(tl(ox, oy + 8 + r*slh, l, ssz, scw, "#BFEFF7") for r, l in enumerate(fr) if l.strip()) + '</g>')
    p.append('</g></svg>')
    open(os.path.join(OUT, "about.svg"), "w").write('\n'.join(p))

# ------------------------------------------------------------------ project cards
PROJECTS = [
    ("01", "GlowIsland", "mobile app · TurkmenApps", "Consumer mobile app, designed and shipped end to end.", "Flutter · product design", CYAN, "glowisland"),
    ("02", "FaceGlow", "mobile app · TurkmenApps", "Face-science app: analysis turned into a clear daily routine.", "Flutter · UX research", PURPLE, "faceglow"),
    ("03", "Stremio Dual Subtitles", "language learning · 37 ★", "Two subtitle languages at once. The most-used thing I have built.", "JavaScript · Node.js · live", MINT, "stremio"),
    ("04", "Ehliyet Rehberim", "Google Play · 5.0 rating", "Driving-license exam prep for Turkey, built solo, used daily.", "Flutter · Dart", CYAN, "ehliyet"),
]
def build_card(idx, title, meta, desc, tech, col, key):
    W, H = 440, 132; uid = "c" + key
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">',
         f'<style>{CSS_COMMON}</style>', defs(uid),
         f'<rect width="{W}" height="{H}" rx="16" fill="url(#{uid}bg)"/>', glass(6, 6, W-12, H-12, uid, r=14, edge=False)]
    p.append(f'<rect x="6" y="30" width="2" height="{H-60}" rx="1" fill="{col}" filter="url(#{uid}glow)" class="pulse"/>')
    p.append(ascii_frame(6, 6, W-12, H-12))
    p.append(t(28, 38, idx, 11, col, ' letter-spacing="2"'))
    p.append(t(56, 40, title, 16, TEXT, f' font-weight="600" font-family="{SANS}"'))
    p.append(t(28, 62, meta, 10.5, DIM, ' letter-spacing="0.5"'))
    p.append(t(28, 86, desc, 11.5, "#C9D1D9", f' font-family="{SANS}"'))
    p.append(t(28, 110, tech, 10, MUTED, ' letter-spacing="0.5"'))
    p.append(t(W-26, 110, "open  →", 10, col, ' text-anchor="end" letter-spacing="1" class="pulse"'))
    p.append('</svg>')
    open(os.path.join(OUT, f"card-{key}.svg"), "w").write('\n'.join(p))

# ------------------------------------------------------------------ social buttons
BUTTONS = [("linkedin", "in", "LinkedIn", CYAN), ("portfolio", "~/", "ummugulsun.me", PURPLE), ("email", "@", "Email", MINT)]
def build_button(key, glyph, label, col):
    W, H = 220, 46; uid = "b" + key
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">',
         f'<style>{CSS_COMMON}</style>', defs(uid),
         f'<rect width="{W}" height="{H}" rx="12" fill="url(#{uid}bg)"/>', glass(3, 3, W-6, H-6, uid, r=10, edge=False),
         f'<rect x="12" y="11" width="24" height="24" rx="7" fill="{col}" fill-opacity="0.12" stroke="{col}" stroke-opacity="0.5"/>',
         t(24, 27, glyph, 11, col, ' text-anchor="middle" font-weight="700"'),
         t(48, 28, label, 12, TEXT, ' letter-spacing="0.5"'),
         t(W-14, 28, "↗", 12, col, ' text-anchor="end" class="pulse"'),
         '</svg>']
    open(os.path.join(OUT, f"btn-{key}.svg"), "w").write('\n'.join(p))

build_hero(); build_about()
for pr in PROJECTS: build_card(*pr)
for b in BUTTONS: build_button(*b)
for f in sorted(os.listdir(OUT)):
    if f.endswith('.svg'): print(f, os.path.getsize(os.path.join(OUT, f)), "bytes")
