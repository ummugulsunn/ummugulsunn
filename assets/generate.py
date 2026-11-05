"""Animated SVGs for the GitHub profile README (pure CSS + SMIL, no JS, no external fonts)."""
import math, html, sys, os, random
import pyfiglet

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
random.seed(42)
BG, FG, DIM, MUTED, ACCENT, LINE = "#0D1117", "#C9D1D9", "#8B949E", "#484F58", "#D4956A", "#21262D"
MONO = "'SFMono-Regular','SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"
HOLO = ["#EDE9FF", "#9DB3FF", "#FFF0A3", "#C8F7A8", "#FFC8E0", "#9BE7FF", "#EDE9FF"]

def esc(s): return html.escape(s, quote=False)
def tl(x, y, s, size, cw, fill, extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" textLength="{len(s)*cw:.1f}" '
            f'lengthAdjust="spacing" xml:space="preserve"{extra}>{esc(s)}</text>')

# ------------------------------------------------------------------ donut
def donut_frames(nf=60, cols=50, rows=24):
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
def eeg_strip(period=160, rows=8):
    vals = [1.4*math.sin(5*t)+0.8*math.sin(13*t+1)+0.4*math.sin(29*t) for t in (i/period*2*math.pi for i in range(period))]
    for c0 in (38, 118):
        for k in range(-5, 6): vals[(c0+k) % period] += 2.6*math.exp(-(k*k)/3.0)
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
    W, H = 1000, 340
    name = pyfiglet.Figlet(font="ansi_shadow", width=200).renderText("ummugulsun").rstrip("\n").split("\n")
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">']
    nf, T = 60, 6.0
    css = f""".d{{opacity:0;animation:show {T}s steps(1) infinite}}
@keyframes show{{0%{{opacity:1}}{100/nf:.4f}%{{opacity:0}}100%{{opacity:0}}}}
.cur{{animation:blink 1.1s steps(1) infinite}}@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}100%{{opacity:1}}}}
.ty{{opacity:0;animation:fi .01s linear forwards}}@keyframes fi{{to{{opacity:1}}}}
.in{{opacity:0;animation:fi .6s ease forwards;animation-delay:2.6s}}
.lbl{{animation:fo .5s ease forwards;animation-delay:1.9s}}@keyframes fo{{to{{opacity:0}}}}
"""
    for i in range(nf): css += f".d{i}{{animation-delay:{i*T/nf:.3f}s}}\n"
    p.append(f'<style>{css}</style>')
    stops = ''.join(f'<stop offset="{i/(len(HOLO)-1):.3f}" stop-color="{c}"/>' for i, c in enumerate(HOLO))
    p.append('<defs>'
        f'<linearGradient id="holo" gradientUnits="userSpaceOnUse" spreadMethod="repeat" x1="0" y1="0" x2="600" y2="90">{stops}'
        '<animateTransform attributeName="gradientTransform" type="translate" values="-600 0;0 0" dur="6s" repeatCount="indefinite"/></linearGradient>'
        '<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#0D1117"/><stop offset="0.08" stop-color="#0D1117" stop-opacity="0"/>'
        '<stop offset="0.92" stop-color="#0D1117" stop-opacity="0"/><stop offset="1" stop-color="#0D1117"/></linearGradient>'
        '<linearGradient id="door" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A1F27"/><stop offset="1" stop-color="#0D1117"/></linearGradient>'
        '<clipPath id="eegclip"><rect x="40" y="226" width="920" height="100"/></clipPath>'
        f'<clipPath id="all"><rect width="{W}" height="{H}" rx="12"/></clipPath>'
        '</defs>')
    p.append(f'<rect width="{W}" height="{H}" fill="{BG}" rx="12"/>')
    # floating particles (wowww-style dust)
    p.append('<g>')
    for _ in range(70):
        x, y = random.uniform(0, W), random.uniform(0, H); s = random.choice([2, 2, 3, 4])
        c = random.choice(HOLO[:-1]); d = random.uniform(8, 18); dy = random.uniform(-40, -120)
        p.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{s}" height="{s}" fill="{c}" opacity="0.35">'
                 f'<animateTransform attributeName="transform" type="translate" values="0 0;{random.uniform(-25,25):.0f} {dy:.0f}" dur="{d:.1f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;0.5;0" dur="{d:.1f}s" repeatCount="indefinite"/></rect>')
    p.append('</g>')
    # name: pixel mosaic, every cell flies in from a random position (SMIL, once), then holographic shimmer
    bw, bh, ln = 7.0, 12.0, 2.0
    x0, y0 = 44, 40
    p.append('<g>')
    for r, l in enumerate(name):
        for c, ch in enumerate(l):
            x, y = x0 + c*bw, y0 + r*bh
            if ch == '█':
                ang = random.uniform(0, 2*math.pi); rad = random.uniform(120, 420)
                dx, dy = math.cos(ang)*rad, math.sin(ang)*rad
                beg = 2.0 + random.uniform(0, 0.7)
                p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-1:.1f}" height="{bh-1:.1f}" fill="url(#holo)" opacity="0">'
                         f'<animateTransform attributeName="transform" type="translate" from="{dx:.0f} {dy:.0f}" to="0 0" begin="{beg:.2f}s" dur="1.1s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
                         f'<animate attributeName="opacity" from="0" to="1" begin="{beg:.2f}s" dur="0.5s" fill="freeze"/></rect>')
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
    # subtitle + typed command
    p.append('<g class="in">' + tl(x0, 150, "Computer Engineering Student  ·  HCI  ·  Mobile Product", 13, 7.8, DIM) + '</g>')
    typed = "$ ./build --user-centric --bio-signals"
    for i, ch in enumerate(typed):
        p.append(f'<text x="{x0+i*7.8:.1f}" y="180" font-size="13" fill="{ACCENT if i==0 else FG}" class="ty" style="animation-delay:{3.2+i*0.05:.2f}s" xml:space="preserve">{esc(ch)}</text>')
    p.append(f'<text x="{x0+len(typed)*7.8:.1f}" y="180" font-size="13" fill="{ACCENT}" class="cur" style="animation-delay:3.2s">▌</text>')
    # donut
    dx, dy = 700, 22
    p.append(f'<g class="in"><text x="{dx}" y="{dy-6}" font-size="9" fill="{MUTED}" xml:space="preserve">{esc("// torus.render(θ, φ)")}</text></g>')
    p.append('<g class="in">')
    for fi, fr in enumerate(donut_frames(nf)):
        p.append(f'<g class="d d{fi}">' + ''.join(tl(dx, dy+8+r*10.5, l, 9, 5.4, ACCENT) for r, l in enumerate(fr) if l.strip()) + '</g>')
    p.append('</g>')
    # EEG
    strip = eeg_strip(); per = 160*6.6
    p.append(f'<g class="in"><text x="44" y="238" font-size="9" fill="{MUTED}" xml:space="preserve">{esc("// eeg.stream  ·  blink artifacts detected: 2")}</text>')
    p.append(f'<g clip-path="url(#eegclip)"><g><animateTransform attributeName="transform" type="translate" from="44 0" to="{44-per:.1f} 0" dur="9s" repeatCount="indefinite"/>'
             + ''.join(tl(0, 252+r*12, l, 11, 6.6, ACCENT if r < 3 else DIM) for r, l in enumerate(strip)) + '</g></g>')
    p.append('<rect x="40" y="226" width="920" height="100" fill="url(#fade)"/></g>')
    # darasoba-style entrance: two door panels + nameplate, open once
    p.append('<g clip-path="url(#all)">')
    for side in (0, 1):
        x = 0 if side == 0 else W/2; to = -W/2 if side == 0 else W/2
        p.append(f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="{to:.0f} 0" begin="1.9s" dur="1.0s" fill="freeze" calcMode="spline" keySplines="0.7 0 0.3 1"/>'
                 f'<rect x="{x}" y="0" width="{W/2}" height="{H}" fill="url(#door)"/>'
                 f'<rect x="{x+40}" y="40" width="{W/2-80}" height="{H-80}" fill="none" stroke="#2A313B" stroke-width="2" rx="4"/>'
                 f'<rect x="{x+60}" y="60" width="{W/2-120}" height="{H-120}" fill="none" stroke="#1E242C" stroke-width="1" rx="2"/>'
                 f'<rect x="{(W/2-10) if side==0 else (W/2+6)}" y="{H/2-18}" width="4" height="36" rx="2" fill="#5A6472"/></g>')
    p.append(f'<g class="lbl"><text x="{W/2}" y="{H/2-10}" font-size="22" fill="{FG}" text-anchor="middle" font-family="{SANS}" font-weight="300" letter-spacing="2">ummugulsun turkmen</text>'
             f'<text x="{W/2}" y="{H/2+14}" font-size="10" fill="{DIM}" text-anchor="middle" letter-spacing="3">COMPUTER ENGINEERING  ·  STUDIO</text>'
             f'<text x="{W/2}" y="{H-28}" font-size="9" fill="{MUTED}" text-anchor="middle" letter-spacing="2">LETTING UMMUGULSUN KNOW YOU\'RE HERE</text>'
             f'<rect x="{W/2-60}" y="{H-20}" width="120" height="2" fill="{LINE}"/>'
             f'<rect x="{W/2-60}" y="{H-20}" width="0" height="2" fill="{ACCENT}"><animate attributeName="width" from="0" to="120" begin="0.2s" dur="1.6s" fill="freeze"/></rect></g>')
    p.append('</g></svg>')
    open(os.path.join(OUT, "header.svg"), "w").write('\n'.join(p))

# ------------------------------------------------------------------ story.svg (uibeawuchi-style chapters)
def build_story():
    W = 1000
    chapters = [
        ("01", "CONNECT", [("It starts with ", False), ("one user.", True)], None,
         ["One screen, one tap, and one person who needs it to just work.", "Every project I build starts and ends there."]),
        ("02", "SHIP", None, "5.0 ★",
         ["Ehliyet Rehberim on Google Play. Designed, built and shipped solo,", "used daily by people preparing for their driving exam."]),
        ("03", "SENSE", [("No screens. No touch. ", False), ("Just thought.", True)], None,
         ["Real-time EEG prototypes that turn a blink into a command.", "Brain-computer interfaces as the next interaction layer."]),
        ("04", "MEASURE", [("Behavior is ", False), ("data.", True)], None,
         ["FlowStateAI reads keystroke dynamics to understand", "how people really use a system, not how they say they do."]),
    ]
    ch_h = 180; H = 40 + ch_h*len(chapters)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">']
    p.append('<style>.c{opacity:0;animation:up .9s cubic-bezier(.2,.8,.2,1) forwards}@keyframes up{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}</style>')
    p.append('<defs><radialGradient id="glow" cx="85%" cy="0%" r="80%"><stop offset="0" stop-color="#B87333" stop-opacity="0.22"/><stop offset="1" stop-color="#0D1117" stop-opacity="0"/></radialGradient></defs>')
    p.append(f'<rect width="{W}" height="{H}" fill="{BG}" rx="12"/><rect width="{W}" height="{H}" fill="url(#glow)" rx="12"/>')
    for i, (num, lab, head, big, sub) in enumerate(chapters):
        y = 40 + i*ch_h; d = 0.3 + i*0.45
        p.append(f'<g class="c" style="animation-delay:{d:.2f}s">')
        p.append(f'<line x1="48" y1="{y+22}" x2="68" y2="{y+22}" stroke="{ACCENT}" stroke-width="1.5"/>')
        p.append(f'<text x="78" y="{y+26}" font-size="11" fill="{ACCENT}" font-family="{MONO}" letter-spacing="3">{num} · {lab}</text>')
        if head:
            p.append(f'<text x="48" y="{y+78}" font-size="46" fill="{FG}" font-weight="300" letter-spacing="-1">'
                     + ''.join(f'<tspan font-weight="{700 if b else 300}">{esc(t)}</tspan>' for t, b in head) + '</text>')
        else:
            p.append(f'<text x="48" y="{y+96}" font-size="92" fill="{FG}" font-weight="700" letter-spacing="-3">{esc(big)}</text>')
        oy = y + (112 if head else 128)
        for k, s in enumerate(sub):
            p.append(f'<text x="48" y="{oy+k*22}" font-size="15" fill="{DIM}">{esc(s)}</text>')
        p.append('</g>')
        if i < len(chapters)-1:
            p.append(f'<line x1="48" y1="{y+ch_h-8}" x2="{W-48}" y2="{y+ch_h-8}" stroke="{LINE}"/>')
    p.append('</svg>')
    open(os.path.join(OUT, "story.svg"), "w").write('\n'.join(p))

# ------------------------------------------------------------------ lockscreen.svg (frvky-style)
def build_lockscreen():
    W, H = 380, 640
    notes = [("GP", "#2FB457", "Google Play", "New 5★ review on Ehliyet Rehberim", "now"),
             ("NT", "#B87333", "Neurotech", "Blink detected · UI toggled hands-free", "2m ago"),
             ("GH", "#30363D", "GitHub", "ummugulsunn pushed to main", "9m ago"),
             ("FS", "#4C5BD4", "FlowStateAI", "Session analyzed · flow state: 87%", "1h ago")]
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">']
    p.append('<style>.n{opacity:0;animation:pop .7s cubic-bezier(.2,.9,.2,1.1) forwards}@keyframes pop{from{opacity:0;transform:translateY(40px) scale(.96)}to{opacity:1;transform:translateY(0) scale(1)}}'
             '.ar{animation:bob 1.6s ease-in-out infinite}@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}</style>')
    p.append('<defs><linearGradient id="wall" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1B2130"/><stop offset="0.5" stop-color="#0D1117"/><stop offset="1" stop-color="#2A1F19"/></linearGradient>'
             f'<clipPath id="ph"><rect x="10" y="10" width="{W-20}" height="{H-20}" rx="44"/></clipPath></defs>')
    p.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    p.append(f'<rect x="4" y="4" width="{W-8}" height="{H-8}" rx="50" fill="#161B22" stroke="#30363D" stroke-width="2"/>')
    p.append(f'<g clip-path="url(#ph)"><rect x="10" y="10" width="{W-20}" height="{H-20}" fill="url(#wall)"/>')
    # ascii texture on wallpaper
    for r in range(14):
        row = ''.join(random.choice(" .:-=+*") for _ in range(48))
        p.append(tl(14, 70 + r*38, row, 10, 7.3, "#FFFFFF", ' opacity="0.05"'))
    p.append(f'<rect x="{W/2-50}" y="22" width="100" height="26" rx="13" fill="#000"/>')
    p.append(f'<text x="{W/2}" y="86" font-size="14" fill="{DIM}" text-anchor="middle">Wednesday · building</text>')
    p.append(f'<text x="{W/2}" y="150" font-size="68" fill="{FG}" text-anchor="middle" font-weight="200" letter-spacing="-2">23:47</text>')
    y = 300
    for i, (ab, col, app, msg, when) in enumerate(notes):
        d = 0.6 + i*0.7
        p.append(f'<g class="n" style="animation-delay:{d:.1f}s"><rect x="22" y="{y}" width="{W-44}" height="60" rx="16" fill="#FFFFFF" fill-opacity="0.09" stroke="#FFFFFF" stroke-opacity="0.08"/>'
                 f'<rect x="34" y="{y+14}" width="32" height="32" rx="8" fill="{col}"/>'
                 f'<text x="50" y="{y+35}" font-size="11" fill="#FFF" text-anchor="middle" font-weight="700" font-family="{MONO}">{ab}</text>'
                 f'<text x="78" y="{y+26}" font-size="12" fill="{FG}" font-weight="600">{esc(app)}</text>'
                 f'<text x="{W-34}" y="{y+26}" font-size="10" fill="{DIM}" text-anchor="end">{esc(when)}</text>'
                 f'<text x="78" y="{y+45}" font-size="11.5" fill="{DIM}">{esc(msg)}</text></g>')
        y += 68
    p.append(f'<g class="ar"><text x="{W/2}" y="{H-54}" font-size="12" fill="{DIM}" text-anchor="middle">⌃</text></g>')
    p.append(f'<text x="{W/2}" y="{H-36}" font-size="10" fill="{MUTED}" text-anchor="middle" letter-spacing="1">swipe up to see the projects</text>')
    p.append(f'<rect x="{W/2-60}" y="{H-24}" width="120" height="4" rx="2" fill="{FG}" opacity="0.5"/>')
    p.append('</g></svg>')
    open(os.path.join(OUT, "lockscreen.svg"), "w").write('\n'.join(p))

# ------------------------------------------------------------------ terminal.svg
def build_terminal():
    W = 1000
    lines = [("$ ", "whoami", ACCENT), ("", "ummugulsun · computer engineering student · product-first builder", FG),
             ("$ ", "cat interests.txt", ACCENT), ("", "human-computer interaction  ·  bio-signal interfaces  ·  behavioral analysis", FG),
             ("$ ", "ls ~/projects", ACCENT), ("", "ehliyet-rehberim/   neurotech-blink-detection/   FlowStateAI/", FG),
             ("$ ", "git log --oneline -1 --author=ummugulsun", ACCENT), ("", "a5c3f2e  feat: ship a 5.0★ app to google play", FG),
             ("$ ", "./status", ACCENT), ("", "[████████████░░░░]  building the next thing…", DIM), ("$ ", "", ACCENT)]
    size, cw, lh = 13, 7.8, 22; H = 60 + len(lines)*lh
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">',
         '<style>.c{opacity:0;animation:in .01s linear forwards}@keyframes in{to{opacity:1}}.cur{animation:blink 1s steps(1) infinite}@keyframes blink{0%{opacity:1}50%{opacity:0}100%{opacity:1}}</style>',
         f'<rect width="{W}" height="{H}" fill="{BG}" rx="12"/><rect width="{W}" height="36" fill="#161B22" rx="12"/><rect y="24" width="{W}" height="12" fill="#161B22"/>']
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")): p.append(f'<circle cx="{22+i*20}" cy="18" r="6" fill="{c}" opacity="0.85"/>')
    p.append(f'<text x="{W/2}" y="22" font-size="11" fill="{DIM}" text-anchor="middle">ummugulsun@github ~ zsh</text>')
    t, y = 0.3, 64
    for prompt, cmd, color in lines:
        x = 24
        if prompt:
            p.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{MUTED}" class="c" style="animation-delay:{t:.2f}s">{esc(prompt)}</text>'); x += 2*cw
            for ch in cmd:
                p.append(f'<text x="{x:.1f}" y="{y}" font-size="{size}" fill="{color}" class="c" style="animation-delay:{t:.2f}s" xml:space="preserve">{esc(ch)}</text>'); x += cw; t += 0.04
            t += 0.35
        else:
            p.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" class="c" style="animation-delay:{t:.2f}s" xml:space="preserve">{esc(cmd)}</text>'); t += 0.55
        y += lh
    p.append(f'<text x="{24+2*cw}" y="{y-lh}" font-size="{size}" fill="{ACCENT}" class="c cur" style="animation-delay:{t:.2f}s">▌</text></svg>')
    open(os.path.join(OUT, "terminal.svg"), "w").write('\n'.join(p))

# ------------------------------------------------------------------ footer.svg
def build_footer():
    W, H = 1000, 150; size, cw = 15, 9.0
    row = "   ✦   ".join(["OPEN TO COLLABORATION", "HCI", "MOBILE PRODUCT", "BIO-SIGNAL INTERFACES", "BEHAVIORAL ANALYSIS", "AI"]) + "   ✦   "
    unit = len(row)*cw; line1 = row*(int(W*2/unit)+2)
    row2 = "   ·   ".join(["design experiences, not just code", "ship it to real users", "measure the behavior", "iterate"]) + "   ·   "
    unit2 = len(row2)*cw*0.8; line2 = row2*(int(W*2/unit2)+2)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">',
         '<defs><linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#0D1117"/><stop offset="0.1" stop-color="#0D1117" stop-opacity="0"/><stop offset="0.9" stop-color="#0D1117" stop-opacity="0"/><stop offset="1" stop-color="#0D1117"/></linearGradient>'
         f'<clipPath id="clip"><rect width="{W}" height="{H}"/></clipPath></defs>',
         f'<rect width="{W}" height="{H}" fill="{BG}" rx="12"/><line x1="0" y1="52" x2="{W}" y2="52" stroke="{LINE}"/><line x1="0" y1="98" x2="{W}" y2="98" stroke="{LINE}"/>',
         '<g clip-path="url(#clip)">',
         f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="{-unit:.1f} 0" dur="14s" repeatCount="indefinite"/>' + tl(0, 36, line1, size, cw, FG, ' font-weight="bold" letter-spacing="1"') + '</g>',
         f'<g><animateTransform attributeName="transform" type="translate" from="{-unit2:.1f} 0" to="0 0" dur="18s" repeatCount="indefinite"/>' + tl(0, 80, line2, 12, cw*0.8, ACCENT) + '</g></g>',
         f'<text x="{W/2}" y="128" font-size="11" fill="{MUTED}" text-anchor="middle" xml:space="preserve">{esc("// thanks for scrolling  ·  built with ascii, coffee and a 5.0★ app")}</text>',
         f'<rect width="{W}" height="{H}" fill="url(#fade)"/></svg>']
    open(os.path.join(OUT, "footer.svg"), "w").write('\n'.join(p))

build_header(); build_story(); build_lockscreen(); build_terminal(); build_footer()
for f in sorted(os.listdir(OUT)): print(f, os.path.getsize(os.path.join(OUT, f)), "bytes")
