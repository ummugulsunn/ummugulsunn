"""Animated SVGs for the GitHub profile README. Pure CSS + SMIL, no JS, no external fonts.
Designed for a 900px README column with text >= 15px so it survives GitHub's narrow layouts."""
import math, html, sys, os, random
import pyfiglet

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
random.seed(7)
W = 900
BG, FG, DIM, MUTED, ACCENT, LINE = "#0D1117", "#C9D1D9", "#8B949E", "#484F58", "#D4956A", "#21262D"
MONO = "'SFMono-Regular','SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"
HOLO = ["#EDE9FF", "#9DB3FF", "#FFF0A3", "#C8F7A8", "#FFC8E0", "#9BE7FF", "#EDE9FF"]

def esc(s): return html.escape(s, quote=False)
def tl(x, y, s, size, cw, fill, extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" textLength="{len(s)*cw:.1f}" '
            f'lengthAdjust="spacing" xml:space="preserve"{extra}>{esc(s)}</text>')
def svg_open(h, font=MONO):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" font-family="{font}">'

# ------------------------------------------------------------------ donut
def donut_frames(nf=60, cols=36, rows=18):
    frames, chars = [], ".,-~:;=!*#$@"
    for f in range(nf):
        A, B = f*(2*math.pi/nf)*2, f*(2*math.pi/nf)
        z, out = [0.0]*(cols*rows), [' ']*(cols*rows)
        cA, sA, cB, sB = math.cos(A), math.sin(A), math.cos(B), math.sin(B)
        K2 = 5.0; K1 = cols*K2*3/(8*3)*0.75
        th = 0.0
        while th < 2*math.pi:
            ct, st = math.cos(th), math.sin(th); th += 0.07
            ph = 0.0
            while ph < 2*math.pi:
                sp, cp = math.sin(ph), math.cos(ph); ph += 0.02
                h = 2 + ct
                D = 1/(sp*h*sA + st*cA + K2); t = sp*h*cA - st*sA
                xp = int(cols/2 + K1*D*(cp*h*cB - t*sB)); yp = int(rows/2 + (K1/2.1)*D*(cp*h*sB + t*cB))
                L = cp*ct*sB - cA*ct*sp - sA*st + cB*(cA*st - ct*sA*sp)
                if 0 <= xp < cols and 0 <= yp < rows:
                    i = xp + cols*yp
                    if D > z[i]:
                        z[i] = D; out[i] = chars[max(0, int(L*8))] if L > 0 else chars[0]
        frames.append([''.join(out[r*cols:(r+1)*cols]) for r in range(rows)])
    return frames

# ------------------------------------------------------------------ EEG
def eeg_rows(period=120, rows=6):
    vals = [1.4*math.sin(5*t)+0.8*math.sin(13*t+1)+0.4*math.sin(29*t) for t in (i/period*2*math.pi for i in range(period))]
    for c0 in (30, 88):
        for k in range(-4, 5): vals[(c0+k) % period] += 2.4*math.exp(-(k*k)/2.5)
    lo, hi = min(vals), max(vals)
    ys = [int(round((rows-1)-(v-lo)/(hi-lo)*(rows-1))) for v in vals]
    g = [[' ']*period for _ in range(rows)]
    for i in range(period):
        y, yn = ys[i], ys[(i+1) % period]
        g[y][i] = '-' if y == yn else ('/' if yn < y else '\\')
        step = -1 if yn < y else 1
        for yy in range(y+step, yn, step): g[yy][i] = '|'
    return [''.join(r)*2 for r in g]

# ------------------------------------------------------------------ header.svg
def build_header():
    H = 300
    name = pyfiglet.Figlet(font="ansi_shadow", width=200).renderText("ummugulsun").rstrip("\n").split("\n")
    nf, T = 60, 6.0
    css = f""".d{{opacity:0;animation:show {T}s steps(1) infinite}}
@keyframes show{{0%{{opacity:1}}{100/nf:.4f}%{{opacity:0}}100%{{opacity:0}}}}
.cur{{animation:blink 1.1s steps(1) infinite}}@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}100%{{opacity:1}}}}
.ty{{opacity:0;animation:fi .01s linear forwards}}@keyframes fi{{to{{opacity:1}}}}
.in{{opacity:0;animation:fi .8s ease forwards;animation-delay:1.1s}}
"""
    for i in range(nf): css += f".d{i}{{animation-delay:{i*T/nf:.3f}s}}\n"
    stops = ''.join(f'<stop offset="{i/(len(HOLO)-1):.3f}" stop-color="{c}"/>' for i, c in enumerate(HOLO))
    p = [svg_open(H), f'<style>{css}</style>',
         '<defs>'
         f'<linearGradient id="holo" gradientUnits="userSpaceOnUse" spreadMethod="repeat" x1="0" y1="0" x2="600" y2="90">{stops}'
         '<animateTransform attributeName="gradientTransform" type="translate" values="-600 0;0 0" dur="6s" repeatCount="indefinite"/></linearGradient>'
         '</defs>',
         f'<rect width="{W}" height="{H}" fill="{BG}" rx="12"/>']
    # subtle drifting dust (few, monochrome)
    p.append('<g>')
    for _ in range(36):
        x, y = random.uniform(0, W), random.uniform(0, H); s = random.choice([2, 2, 3])
        d = random.uniform(9, 18); dy = random.uniform(-40, -110)
        p.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{s}" height="{s}" fill="{DIM}" opacity="0">'
                 f'<animateTransform attributeName="transform" type="translate" values="0 0;{random.uniform(-20,20):.0f} {dy:.0f}" dur="{d:.1f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;0.45;0" dur="{d:.1f}s" repeatCount="indefinite"/></rect>')
    p.append('</g>')
    # name: pixel mosaic, cells fly in once, holographic shimmer forever
    bw, bh, ln = 7.6, 13.0, 2.0
    x0, y0 = 36, 44
    p.append('<g>')
    for r, l in enumerate(name):
        for c, ch in enumerate(l):
            x, y = x0 + c*bw, y0 + r*bh
            if ch == '█':
                ang = random.uniform(0, 2*math.pi); rad = random.uniform(100, 380)
                dx, dy = math.cos(ang)*rad, math.sin(ang)*rad
                beg = random.uniform(0.05, 0.6)
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
                p.append(f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="{sh:.1f}" fill="{MUTED}" class="in"/>')
    p.append('</g>')
    # subtitle + typed line (16px)
    cw = 9.6
    p.append('<g class="in">' + tl(x0, 170, "Computer Engineering Student  ·  HCI  ·  Mobile Product", 16, cw, DIM) + '</g>')
    typed = "$ ./build --user-centric --bio-signals"
    for i, ch in enumerate(typed):
        p.append(f'<text x="{x0+i*cw:.1f}" y="206" font-size="16" fill="{ACCENT if i==0 else FG}" class="ty" style="animation-delay:{1.6+i*0.045:.2f}s" xml:space="preserve">{esc(ch)}</text>')
    p.append(f'<text x="{x0+len(typed)*cw:.1f}" y="206" font-size="16" fill="{ACCENT}" class="cur" style="animation-delay:1.6s">▌</text>')
    p.append('<g class="in">' + tl(x0, 262, "// scroll ↓  the signal continues", 13, 7.8, MUTED) + '</g>')
    # donut (right)
    dx, dy = 624, 36
    p.append(f'<g class="in"><text x="{dx}" y="{dy-10}" font-size="12" fill="{MUTED}" xml:space="preserve">{esc("// torus.render(θ, φ)")}</text></g>')
    p.append('<g class="in">')
    for fi, fr in enumerate(donut_frames(nf)):
        p.append(f'<g class="d d{fi}">' + ''.join(tl(dx, dy+10+r*13, l, 11, 6.6, ACCENT) for r, l in enumerate(fr) if l.strip()) + '</g>')
    p.append('</g></svg>')
    open(os.path.join(OUT, "header.svg"), "w").write('\n'.join(p))

# ------------------------------------------------------------------ signal.svg (EEG divider, the thread of the page)
def build_signal(label="// eeg.stream  ·  blink artifacts: 2"):
    H = 96; rows = eeg_rows(); cw, lh, size = 7.5, 12.0, 12
    per = 120*cw
    p = [svg_open(H),
         '<defs><linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#0D1117"/><stop offset="0.08" stop-color="#0D1117" stop-opacity="0"/>'
         '<stop offset="0.92" stop-color="#0D1117" stop-opacity="0"/><stop offset="1" stop-color="#0D1117"/></linearGradient>'
         f'<clipPath id="c"><rect width="{W}" height="{H}"/></clipPath></defs>',
         f'<rect width="{W}" height="{H}" fill="{BG}" rx="12"/>',
         tl(36, 18, label, 12, 7.2, MUTED),
         f'<g clip-path="url(#c)"><g><animateTransform attributeName="transform" type="translate" from="0 0" to="{-per:.1f} 0" dur="8s" repeatCount="indefinite"/>'
         + ''.join(tl(0, 34+r*lh, l, size, cw, ACCENT if r < 2 else DIM) for r, l in enumerate(rows)) + '</g></g>',
         f'<rect width="{W}" height="{H}" fill="url(#fade)"/></svg>']
    open(os.path.join(OUT, "signal.svg"), "w").write('\n'.join(p))

# ------------------------------------------------------------------ story.svg (two chapters)
def build_story():
    chapters = [
        ("01", "CONNECT", [("It starts with ", False), ("one user.", True)],
         ["One screen, one tap, and one person who needs it to just work.",
          "I'm a Computer Engineering student with a product-first mindset:",
          "I don't just write code, I design the experience around it."]),
        ("02", "SENSE", [("No screens. No touch. ", False), ("Just thought.", True)],
         ["I prototype touchless interfaces with EEG sensors and study",
          "how people really behave, not how they say they do.",
          "HCI  ·  behavioral analysis  ·  mobile product."]),
    ]
    ch_h = 210; H = 30 + ch_h*len(chapters)
    p = [svg_open(H, SANS),
         '<style>.c{opacity:0;animation:up .9s cubic-bezier(.2,.8,.2,1) forwards}@keyframes up{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}</style>',
         '<defs><radialGradient id="glow" cx="90%" cy="0%" r="75%"><stop offset="0" stop-color="#B87333" stop-opacity="0.2"/><stop offset="1" stop-color="#0D1117" stop-opacity="0"/></radialGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="{BG}" rx="12"/><rect width="{W}" height="{H}" fill="url(#glow)" rx="12"/>']
    for i, (num, lab, head, sub) in enumerate(chapters):
        y = 30 + i*ch_h; d = 0.2 + i*0.5
        p.append(f'<g class="c" style="animation-delay:{d:.2f}s">')
        p.append(f'<line x1="40" y1="{y+24}" x2="60" y2="{y+24}" stroke="{ACCENT}" stroke-width="1.5"/>')
        p.append(f'<text x="70" y="{y+28}" font-size="12" fill="{ACCENT}" font-family="{MONO}" letter-spacing="3">{num} · {lab}</text>')
        p.append(f'<text x="40" y="{y+84}" font-size="44" fill="{FG}" letter-spacing="-1">'
                 + ''.join(f'<tspan font-weight="{700 if b else 300}">{esc(t)}</tspan>' for t, b in head) + '</text>')
        for k, s in enumerate(sub):
            p.append(f'<text x="40" y="{y+120+k*25}" font-size="17" fill="{DIM}">{esc(s)}</text>')
        p.append('</g>')
        if i < len(chapters)-1:
            p.append(f'<line x1="40" y1="{y+ch_h-6}" x2="{W-40}" y2="{y+ch_h-6}" stroke="{LINE}"/>')
    p.append('</svg>')
    open(os.path.join(OUT, "story.svg"), "w").write('\n'.join(p))

# ------------------------------------------------------------------ terminal.svg
def build_terminal():
    lines = [("$ ", "whoami", ACCENT), ("", "ummugulsun · computer engineering student · product-first", FG),
             ("$ ", "cat interests.txt", ACCENT), ("", "human-computer interaction · bio-signals · behavioral analysis", FG),
             ("$ ", "ls ~/projects", ACCENT), ("", "ehliyet-rehberim/   neurotech-blink-detection/   FlowStateAI/", FG),
             ("$ ", "./status", ACCENT), ("", "[████████████░░░░]  building the next thing…", DIM), ("$ ", "", ACCENT)]
    size, cw, lh = 16, 9.6, 27; H = 66 + len(lines)*lh
    p = [svg_open(H),
         '<style>.c{opacity:0;animation:in .01s linear forwards}@keyframes in{to{opacity:1}}.cur{animation:blink 1s steps(1) infinite}@keyframes blink{0%{opacity:1}50%{opacity:0}100%{opacity:1}}</style>',
         f'<rect width="{W}" height="{H}" fill="{BG}" rx="12"/><rect width="{W}" height="40" fill="#161B22" rx="12"/><rect y="28" width="{W}" height="12" fill="#161B22"/>']
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")): p.append(f'<circle cx="{24+i*22}" cy="20" r="6.5" fill="{c}" opacity="0.85"/>')
    p.append(f'<text x="{W/2}" y="25" font-size="13" fill="{DIM}" text-anchor="middle">ummugulsun@github ~ zsh</text>')
    t, y = 0.3, 74
    for prompt, cmd, color in lines:
        x = 28
        if prompt:
            p.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{MUTED}" class="c" style="animation-delay:{t:.2f}s">{esc(prompt)}</text>'); x += 2*cw
            for ch in cmd:
                p.append(f'<text x="{x:.1f}" y="{y}" font-size="{size}" fill="{color}" class="c" style="animation-delay:{t:.2f}s" xml:space="preserve">{esc(ch)}</text>'); x += cw; t += 0.04
            t += 0.35
        else:
            p.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" class="c" style="animation-delay:{t:.2f}s" xml:space="preserve">{esc(cmd)}</text>'); t += 0.55
        y += lh
    p.append(f'<text x="{28+2*cw}" y="{y-lh}" font-size="{size}" fill="{ACCENT}" class="c cur" style="animation-delay:{t:.2f}s">▌</text></svg>')
    open(os.path.join(OUT, "terminal.svg"), "w").write('\n'.join(p))

# ------------------------------------------------------------------ phone.svg (project notifications, all true statements)
def build_phone():
    PW, PH = 360, 560
    notes = [("ER", "Ehliyet Rehberim", "Live on Google Play · 5.0 ★ rating", "mobile"),
             ("NT", "Neurotech", "Blink detection on real-time EEG", "hci"),
             ("FS", "FlowStateAI", "Keystroke dynamics → behavior analysis", "ai"),
             ("GH", "github.com/ummugulsunn", "open to collaboration", "now")]
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}" font-family="{SANS}">',
         '<style>.n{opacity:0;animation:pop .7s cubic-bezier(.2,.9,.2,1.1) forwards}@keyframes pop{from{opacity:0;transform:translateY(36px)}to{opacity:1;transform:translateY(0)}}'
         '.ar{animation:bob 1.6s ease-in-out infinite}@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}</style>',
         '<defs><linearGradient id="wall" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1A2030"/><stop offset="0.55" stop-color="#0D1117"/><stop offset="1" stop-color="#2A1F19"/></linearGradient>'
         f'<clipPath id="ph"><rect x="10" y="10" width="{PW-20}" height="{PH-20}" rx="42"/></clipPath></defs>',
         f'<rect width="{PW}" height="{PH}" fill="{BG}"/>',
         f'<rect x="4" y="4" width="{PW-8}" height="{PH-8}" rx="48" fill="#161B22" stroke="#30363D" stroke-width="2"/>',
         f'<g clip-path="url(#ph)"><rect x="10" y="10" width="{PW-20}" height="{PH-20}" fill="url(#wall)"/>']
    for r in range(12):
        row = ''.join(random.choice(" .:-=+*") for _ in range(44))
        p.append(tl(14, 60 + r*40, row, 11, 7.6, "#FFFFFF", ' opacity="0.05"'))
    p.append(f'<rect x="{PW/2-48}" y="22" width="96" height="26" rx="13" fill="#000"/>')
    p.append(f'<text x="{PW/2}" y="92" font-size="14" fill="{DIM}" text-anchor="middle" letter-spacing="2">PROJECTS</text>')
    p.append(f'<text x="{PW/2}" y="150" font-size="60" fill="{FG}" text-anchor="middle" font-weight="200" letter-spacing="-2">3 + 1</text>')
    y = 232
    for i, (ab, app, msg, when) in enumerate(notes):
        d = 0.5 + i*0.6
        p.append(f'<g class="n" style="animation-delay:{d:.1f}s"><rect x="20" y="{y}" width="{PW-40}" height="62" rx="16" fill="#FFFFFF" fill-opacity="0.08" stroke="#FFFFFF" stroke-opacity="0.08"/>'
                 f'<rect x="32" y="{y+15}" width="32" height="32" rx="8" fill="{ACCENT if i < 3 else MUTED}"/>'
                 f'<text x="48" y="{y+36}" font-size="11" fill="#0D1117" text-anchor="middle" font-weight="700" font-family="{MONO}">{ab}</text>'
                 f'<text x="76" y="{y+27}" font-size="13" fill="{FG}" font-weight="600">{esc(app)}</text>'
                 f'<text x="{PW-32}" y="{y+27}" font-size="10" fill="{DIM}" text-anchor="end">{esc(when)}</text>'
                 f'<text x="76" y="{y+47}" font-size="12" fill="{DIM}">{esc(msg)}</text></g>')
        y += 70
    p.append(f'<g class="ar"><text x="{PW/2}" y="{PH-50}" font-size="12" fill="{DIM}" text-anchor="middle">⌃</text></g>')
    p.append(f'<text x="{PW/2}" y="{PH-32}" font-size="10" fill="{MUTED}" text-anchor="middle" letter-spacing="1">details on the left</text>')
    p.append(f'<rect x="{PW/2-56}" y="{PH-22}" width="112" height="4" rx="2" fill="{FG}" opacity="0.5"/></g></svg>')
    open(os.path.join(OUT, "phone.svg"), "w").write('\n'.join(p))

# ------------------------------------------------------------------ footer.svg (single marquee)
def build_footer():
    H = 110; size, cw = 17, 10.2
    row = "   ✦   ".join(["OPEN TO COLLABORATION", "HCI", "MOBILE PRODUCT", "BIO-SIGNAL INTERFACES", "BEHAVIORAL ANALYSIS", "AI"]) + "   ✦   "
    unit = len(row)*cw; line = row*(int(W*2/unit)+2)
    p = [svg_open(H),
         '<defs><linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#0D1117"/><stop offset="0.1" stop-color="#0D1117" stop-opacity="0"/><stop offset="0.9" stop-color="#0D1117" stop-opacity="0"/><stop offset="1" stop-color="#0D1117"/></linearGradient>'
         f'<clipPath id="clip"><rect width="{W}" height="{H}"/></clipPath></defs>',
         f'<rect width="{W}" height="{H}" fill="{BG}" rx="12"/><line x1="0" y1="62" x2="{W}" y2="62" stroke="{LINE}"/>',
         f'<g clip-path="url(#clip)"><g><animateTransform attributeName="transform" type="translate" from="0 0" to="{-unit:.1f} 0" dur="16s" repeatCount="indefinite"/>'
         + tl(0, 42, line, size, cw, FG, ' font-weight="bold" letter-spacing="1"') + '</g></g>',
         f'<text x="{W/2}" y="90" font-size="13" fill="{MUTED}" text-anchor="middle" xml:space="preserve">{esc("// thanks for scrolling  ·  built with ascii, coffee and a 5.0★ app")}</text>',
         f'<rect width="{W}" height="{H}" fill="url(#fade)"/></svg>']
    open(os.path.join(OUT, "footer.svg"), "w").write('\n'.join(p))

build_header(); build_signal(); build_story(); build_terminal(); build_phone(); build_footer()
for f in sorted(os.listdir(OUT)):
    if f.endswith('.svg'): print(f, os.path.getsize(os.path.join(OUT, f)), "bytes")
