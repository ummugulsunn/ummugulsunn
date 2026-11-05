"""Generate animated ASCII-art SVGs for the GitHub profile README.
No JS: pure CSS keyframes + SMIL so they animate inside GitHub's <img> tags."""
import math, html, sys, os
import pyfiglet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

BG, FG, DIM, MUTED, ACCENT, ACCENT2 = "#0D1117", "#C9D1D9", "#8B949E", "#484F58", "#D4956A", "#B87333"
MONO = "'SFMono-Regular','SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"

def esc(s): return html.escape(s, quote=False)

def text_line(x, y, s, size, cw, fill, extra="", cls=""):
    """One monospace row. textLength pins the grid so every font renders the same width."""
    n = len(s)
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" textLength="{n*cw:.1f}" '
            f'lengthAdjust="spacing" xml:space="preserve"{(" class=%s"%chr(34)+cls+chr(34)) if cls else ""}{extra}>{esc(s)}</text>')

# ---------------------------------------------------------------- donut frames
def donut_frames(nf=60, cols=50, rows=24):
    frames = []
    chars = ".,-~:;=!*#$@"
    for f in range(nf):
        A = f * (2*math.pi/nf) * 2      # two full turns per loop on A
        B = f * (2*math.pi/nf)          # one on B
        z = [0.0]*(cols*rows); out = [' ']*(cols*rows)
        cA, sA, cB, sB = math.cos(A), math.sin(A), math.cos(B), math.sin(B)
        K2 = 5.0; K1 = cols*K2*3/(8*3)*0.75
        th = 0.0
        while th < 2*math.pi:
            ct, st = math.cos(th), math.sin(th); th += 0.07
            ph = 0.0
            while ph < 2*math.pi:
                sp, cp = math.sin(ph), math.cos(ph); ph += 0.02
                cx = 2 + ct; 
                h = cx
                D = 1/(sp*h*sA + st*cA + K2)
                t = sp*h*cA - st*sA
                xp = int(cols/2 + K1*D*(cp*h*cB - t*sB))
                yp = int(rows/2 + (K1/2.1)*D*(cp*h*sB + t*cB))
                L = cp*ct*sB - cA*ct*sp - sA*st + cB*(cA*st - ct*sA*sp)
                if 0 <= xp < cols and 0 <= yp < rows:
                    idx = xp + cols*yp
                    if D > z[idx]:
                        z[idx] = D
                        out[idx] = chars[max(0, int(L*8))] if L > 0 else chars[0]
        frames.append([''.join(out[r*cols:(r+1)*cols]) for r in range(rows)])
    return frames

# ---------------------------------------------------------------- EEG strip
def eeg_strip(period_cols=160, rows=8):
    """Periodic ASCII EEG trace with blink spikes. Returns rows of 2*period text (seamless scroll)."""
    import random
    random.seed(7)
    vals = []
    for i in range(period_cols):
        t = i / period_cols * 2*math.pi
        v = 1.4*math.sin(5*t) + 0.8*math.sin(13*t+1) + 0.4*math.sin(29*t)
        vals.append(v)
    # two eye-blink artifacts (big positive spikes), like the blink-detection project
    for c0 in (38, 118):
        for k in range(-5, 6):
            vals[(c0+k) % period_cols] += 2.6*math.exp(-(k*k)/3.0)
    lo, hi = min(vals), max(vals)
    grid = [[' ']*(period_cols) for _ in range(rows)]
    ys = [int(round((rows-1) - (v-lo)/(hi-lo)*(rows-1))) for v in vals]
    for i in range(period_cols):
        y, yn = ys[i], ys[(i+1) % period_cols]
        ch = '-' if y == yn else ('/' if yn < y else '\\')
        grid[y][i] = ch
        # vertical connector for steep moves
        step = -1 if yn < y else 1
        for yy in range(y+step, yn, step):
            grid[yy][i] = '|'
    lines = [''.join(r) for r in grid]
    return [l + l for l in lines]   # doubled for seamless loop

# ---------------------------------------------------------------- header.svg
def build_header():
    W, H = 1000, 340
    name = pyfiglet.Figlet(font="ansi_shadow", width=200).renderText("ummugulsun").rstrip("\n").split("\n")
    ncols = max(len(l) for l in name); name = [l.ljust(ncols) for l in name]
    size, cw, lh = 12, 7.2, 14.0
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">')
    nf, T = 60, 6.0
    css = f"""
    .d{{opacity:0;animation:show {T}s steps(1) infinite}}
    @keyframes show{{0%{{opacity:1}}{100/nf:.4f}%{{opacity:0}}100%{{opacity:0}}}}
    .cur{{animation:blink 1.1s steps(1) infinite}}
    @keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}100%{{opacity:1}}}}
    .typed{{opacity:0;animation:fadein .01s linear forwards}}
    @keyframes fadein{{to{{opacity:1}}}}
    """
    for i in range(nf):
        css += f".d{i}{{animation-delay:{i*T/nf:.3f}s}}\n"
    parts.append(f'<style>{css}</style>')
    parts.append('<defs>'
        f'<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="520" y2="0">'
        f'<stop offset="0" stop-color="{FG}"/><stop offset="0.45" stop-color="{FG}"/>'
        f'<stop offset="0.5" stop-color="{ACCENT}"/><stop offset="0.55" stop-color="{FG}"/><stop offset="1" stop-color="{FG}"/>'
        '<animateTransform attributeName="gradientTransform" type="translate" from="-560 0" to="560 0" dur="3.6s" repeatCount="indefinite"/>'
        '</linearGradient>'
        '<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#0D1117"/><stop offset="0.08" stop-color="#0D1117" stop-opacity="0"/>'
        '<stop offset="0.92" stop-color="#0D1117" stop-opacity="0"/><stop offset="1" stop-color="#0D1117"/></linearGradient>'
        '<clipPath id="eegclip"><rect x="40" y="226" width="920" height="100"/></clipPath>'
        '</defs>')
    parts.append(f'<rect width="{W}" height="{H}" fill="{BG}" rx="12"/>')
    # subtle grid dots
    parts.append(f'<g fill="{MUTED}" opacity="0.18">' + ''.join(
        f'<circle cx="{x}" cy="{y}" r="0.8"/>' for x in range(20, W, 20) for y in range(20, H, 20)) + '</g>')
    # name
    x0, y0 = 44, 50
    # font-independent: every figlet cell becomes a rect (block = solid, box-drawing = thin shadow line)
    bw, bh, ln = 7.0, 12.0, 2.0
    y0 = 40
    parts.append('<g>')
    for r, l in enumerate(name):
        for c, ch in enumerate(l):
            x, y = x0 + c*bw, y0 + r*bh
            if ch == '█':
                parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="url(#shine)"/>')
                continue
            segs = []
            if ch in '║': segs.append((x+bw/2-ln/2, y, ln, bh))
            if ch in '═': segs.append((x, y+bh/2-ln/2, bw, ln))
            if ch in '╔╚': segs.append((x+bw/2-ln/2, y+bh/2-ln/2, bw/2+ln/2, ln))
            if ch in '╗╝': segs.append((x, y+bh/2-ln/2, bw/2+ln/2, ln))
            if ch in '╔╗': segs.append((x+bw/2-ln/2, y+bh/2-ln/2, ln, bh/2+ln/2))
            if ch in '╚╝': segs.append((x+bw/2-ln/2, y, ln, bh/2+ln/2))
            for sx, sy, sw, sh in segs:
                parts.append(f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="{sh:.1f}" fill="{MUTED}"/>')
    parts.append('</g>')
    # subtitle + typed line
    sub = "Computer Engineering Student  ·  HCI  ·  Mobile Product"
    parts.append(text_line(x0, 150, sub, 13, 7.8, DIM))
    typed = "$ ./build --user-centric --bio-signals"
    for i, ch in enumerate(typed):
        parts.append(f'<text x="{x0 + i*7.8:.1f}" y="180" font-size="13" fill="{ACCENT if i==0 else FG}" class="typed" style="animation-delay:{0.6+i*0.055:.3f}s" xml:space="preserve">{esc(ch)}</text>')
    parts.append(f'<text x="{x0 + len(typed)*7.8:.1f}" y="180" font-size="13" fill="{ACCENT}" class="cur">▌</text>')
    # donut
    dsz, dcw, dlh = 9, 5.4, 10.5
    dx, dy = 700, 22
    parts.append(f'<text x="{dx}" y="{dy-6}" font-size="9" fill="{MUTED}" xml:space="preserve">{esc("// torus.render(θ, φ)")}</text>')
    for fi, fr in enumerate(donut_frames(nf)):
        parts.append(f'<g class="d d{fi}">')
        for r, l in enumerate(fr):
            if l.strip():
                parts.append(text_line(dx, dy + 8 + r*dlh, l, dsz, dcw, ACCENT))
        parts.append('</g>')
    # EEG strip
    esz, ecw, elh = 11, 6.6, 12.0
    strip = eeg_strip(period_cols=160, rows=8)
    period_px = 160*ecw
    parts.append(f'<text x="44" y="238" font-size="9" fill="{MUTED}" xml:space="preserve">{esc("// eeg.stream  ·  blink artifacts detected: 2")}</text>')
    parts.append('<g clip-path="url(#eegclip)"><g>'
                 f'<animateTransform attributeName="transform" type="translate" from="44 0" to="{44-period_px:.1f} 0" dur="9s" repeatCount="indefinite"/>')
    for r, l in enumerate(strip):
        parts.append(text_line(0, 252 + r*elh, l, esz, ecw, ACCENT if r < 3 else DIM))
    parts.append('</g></g>')
    parts.append('<rect x="40" y="226" width="920" height="100" fill="url(#fade)"/>')
    parts.append('</svg>')
    open(os.path.join(OUT, "header.svg"), "w").write('\n'.join(parts))

# ---------------------------------------------------------------- terminal.svg
def build_terminal():
    W = 1000
    lines = [
        ("$ ", "whoami", ACCENT),
        ("", "ummugulsun · computer engineering student · product-first builder", FG),
        ("$ ", "cat interests.txt", ACCENT),
        ("", "human-computer interaction  ·  bio-signal interfaces  ·  behavioral analysis", FG),
        ("$ ", "ls ~/projects", ACCENT),
        ("", "ehliyet-rehberim/   neurotech-blink-detection/   FlowStateAI/", FG),
        ("$ ", "git log --oneline -1 --author=ummugulsun", ACCENT),
        ("", "a5c3f2e  feat: ship a 5.0★ app to google play", FG),
        ("$ ", "./status", ACCENT),
        ("", "[████████████░░░░]  building the next thing…", DIM),
        ("$ ", "", ACCENT),
    ]
    size, cw, lh = 13, 7.8, 22
    H = 60 + len(lines)*lh
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">']
    css = """.c{opacity:0;animation:in .01s linear forwards}@keyframes in{to{opacity:1}}
    .cur{animation:blink 1s steps(1) infinite}@keyframes blink{0%{opacity:1}50%{opacity:0}100%{opacity:1}}"""
    p.append(f'<style>{css}</style>')
    p.append(f'<rect width="{W}" height="{H}" fill="{BG}" rx="12"/>')
    p.append(f'<rect width="{W}" height="36" fill="#161B22" rx="12"/><rect y="24" width="{W}" height="12" fill="#161B22"/>')
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        p.append(f'<circle cx="{22+i*20}" cy="18" r="6" fill="{c}" opacity="0.85"/>')
    p.append(f'<text x="{W/2}" y="22" font-size="11" fill="{DIM}" text-anchor="middle">ummugulsun@github ~ zsh</text>')
    t = 0.3
    y = 64
    for prompt, cmd, color in lines:
        x = 24
        if prompt:
            p.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{MUTED}" class="c" style="animation-delay:{t:.2f}s">{esc(prompt)}</text>')
            x += 2*cw
            for ch in cmd:   # typed char by char
                p.append(f'<text x="{x:.1f}" y="{y}" font-size="{size}" fill="{color}" class="c" style="animation-delay:{t:.2f}s" xml:space="preserve">{esc(ch)}</text>')
                x += cw; t += 0.04
            t += 0.35
        else:
            p.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" class="c" style="animation-delay:{t:.2f}s" xml:space="preserve">{esc(cmd)}</text>')
            t += 0.55
        y += lh
    p.append(f'<text x="{24+2*cw}" y="{y-lh}" font-size="{size}" fill="{ACCENT}" class="c cur" style="animation-delay:{t:.2f}s">▌</text>')
    p.append('</svg>')
    open(os.path.join(OUT, "terminal.svg"), "w").write('\n'.join(p))

build_header(); build_terminal()
for f in os.listdir(OUT): print(f, os.path.getsize(os.path.join(OUT, f)), "bytes")

# ---------------------------------------------------------------- footer.svg (website-style marquee)
def build_footer():
    W, H = 1000, 150
    size, cw = 15, 9.0
    items = ["OPEN TO COLLABORATION", "HCI", "MOBILE PRODUCT", "BIO-SIGNAL INTERFACES", "BEHAVIORAL ANALYSIS", "AI"]
    row = ("   ✦   ".join(items)) + "   ✦   "
    unit = len(row)*cw
    reps = int(W*2/unit) + 2
    line1 = row*reps
    items2 = ["design experiences, not just code", "ship it to real users", "measure the behavior", "iterate"]
    row2 = ("   ·   ".join(items2)) + "   ·   "
    unit2 = len(row2)*cw*0.8
    line2 = row2*(int(W*2/unit2)+2)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">']
    p.append('<defs><linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#0D1117"/><stop offset="0.1" stop-color="#0D1117" stop-opacity="0"/>'
             '<stop offset="0.9" stop-color="#0D1117" stop-opacity="0"/><stop offset="1" stop-color="#0D1117"/></linearGradient>'
             f'<clipPath id="clip"><rect width="{W}" height="{H}"/></clipPath></defs>')
    p.append(f'<rect width="{W}" height="{H}" fill="{BG}" rx="12"/>')
    p.append(f'<line x1="0" y1="52" x2="{W}" y2="52" stroke="#21262D"/><line x1="0" y1="98" x2="{W}" y2="98" stroke="#21262D"/>')
    p.append('<g clip-path="url(#clip)">')
    p.append(f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="{-unit:.1f} 0" dur="14s" repeatCount="indefinite"/>'
             + text_line(0, 36, line1, size, cw, FG, ' font-weight="bold" letter-spacing="1"') + '</g>')
    p.append(f'<g><animateTransform attributeName="transform" type="translate" from="{-unit2:.1f} 0" to="0 0" dur="18s" repeatCount="indefinite"/>'
             + text_line(0, 80, line2, 12, cw*0.8, ACCENT) + '</g>')
    p.append('</g>')
    p.append(f'<text x="{W/2}" y="128" font-size="11" fill="{MUTED}" text-anchor="middle" xml:space="preserve">{esc("// thanks for scrolling  ·  built with ascii, coffee and a 5.0★ app")}</text>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#fade)"/>')
    p.append('</svg>')
    open(os.path.join(OUT, "footer.svg"), "w").write('\n'.join(p))

build_footer()
