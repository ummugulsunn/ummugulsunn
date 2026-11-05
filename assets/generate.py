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
    for c0 in (30, 90):
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


# ------------------------------------------------------------------ ASCII eye (procedural, blinks in sync with the EEG spikes)
def eye_frame(openness=1.0, look=0.0, cols=40, rows=15):
    cx, cy = cols/2, rows/2
    def lid(x):  # almond half-height in y-units for x in [-1,1]
        return 0.62*max(0.0, 1-x*x)**0.55
    grid = [[' ']*cols for _ in range(rows)]
    inside = [[False]*cols for _ in range(rows)]
    for r in range(rows):
        y = (r-cy)/cy*0.72
        for c in range(cols):
            x = (c-cx)/cx
            h = lid(x)
            inside[r][c] = (-h*openness <= y <= h*openness) and abs(x) < 0.985
    ix, iy = cx + look*5, cy
    for r in range(rows):
        for c in range(cols):
            if not inside[r][c]: continue
            up = r == 0 or not inside[r-1][c]; dn = r == rows-1 or not inside[r+1][c]
            lf = c == 0 or not inside[r][c-1]; rt = c == cols-1 or not inside[r][c+1]
            d = math.hypot((c-ix)/2.1, r-iy)
            if up or dn:
                if c < cx: ch = ('.' if up else "'") if (lf or (c < cx*0.35)) and openness > 0.3 else ('-' if abs(c-cx) < cx*0.5 else ('/' if up else '\\'))
                else:      ch = ('.' if up else "'") if (rt or (c > cx*1.65)) and openness > 0.3 else ('-' if abs(c-cx) < cx*0.5 else ('\\' if up else '/'))
                if openness < 0.15: ch = '-'
            elif lf: ch = '('
            elif rt: ch = ')'
            elif d < 1.3: ch = '@'
            elif d < 2.6: ch = '%' if not (r < iy and c < ix) else "'"
            elif d < 4.0: ch = ';' if (r+c) % 2 else ':'
            elif d < 4.6: ch = '.'
            else: ch = ' '
            grid[r][c] = ch
    return [''.join(r) for r in grid]

def eye_frames(nf=60, T=8.0, blink_times=(3.33, 7.33)):
    frames, flags = [], []
    for f in range(nf):
        t = f*T/nf
        o = 1.0; blinking = False
        for bt in blink_times:
            dt = t - bt
            if -0.27 <= dt <= 0.27:
                o = min(o, max(0.0, abs(dt)/0.27)**1.2); blinking = True
        look = 0.6*math.sin(2*math.pi*t/T) if not blinking else 0.0
        frames.append(eye_frame(o, look)); flags.append(blinking)
    return frames, flags

# ------------------------------------------------------------------ header.svg
def build_header():
    H = 300; x0, y0 = 36, 44; EEGW = 560
    name = pyfiglet.Figlet(font="ansi_shadow", width=200).renderText("ummugulsun").rstrip("\n").split("\n")
    nf, T = 60, 8.0
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
         '<linearGradient id="fadeh" x1="0" x2="1"><stop offset="0" stop-color="#0D1117"/><stop offset="0.06" stop-color="#0D1117" stop-opacity="0"/>'
         '<stop offset="0.94" stop-color="#0D1117" stop-opacity="0"/><stop offset="1" stop-color="#0D1117"/></linearGradient>'
         f'<clipPath id="eegclip"><rect x="{x0}" y="200" width="{EEGW}" height="90"/></clipPath>'
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
    bw, bh, ln = 6.8, 12.0, 2.0
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
    # EEG strip under the name (the bio-signal thread)
    rows = eeg_rows(); ecw, elh, esz = 7.0, 11.5, 11; per = 120*ecw
    p.append(f'<g class="in">' + tl(x0, 198, "// eeg.stream  ·  spike = blink", 12, 7.2, MUTED))
    p.append(f'<g clip-path="url(#eegclip)"><g><animateTransform attributeName="transform" type="translate" from="{x0} 0" to="{x0-per:.1f} 0" dur="8s" repeatCount="indefinite"/>'
             + ''.join(tl(0, 214+r*elh, l, esz, ecw, ACCENT if r < 2 else DIM) for r, l in enumerate(rows)) + '</g></g>')
    p.append(f'<rect x="{x0-4}" y="200" width="{EEGW+8}" height="90" fill="url(#fadeh)"/>')
    p.append(f'<line x1="{x0+40*ecw:.1f}" y1="204" x2="{x0+40*ecw:.1f}" y2="288" stroke="{ACCENT}" stroke-opacity="0.35" stroke-dasharray="2 3"/></g>')
    # ASCII eye (right): blinks exactly when a spike crosses the EEG strip
    dx, dy = 636, 40; ecw2, elh2 = 6.4, 12.5
    p.append(f'<g class="in"><text x="{dx}" y="{dy-10}" font-size="12" fill="{MUTED}" xml:space="preserve">{esc("// neurotech.blink_detection()")}</text></g>')
    p.append('<g class="in">')
    frames, flags = eye_frames(nf, T)
    for fi, (fr, bl) in enumerate(zip(frames, flags)):
        body = ''.join(tl(dx, dy+12+r*elh2, l, 11, ecw2, FG if not bl else ACCENT) for r, l in enumerate(fr) if l.strip())
        if bl:
            body += tl(dx+40, dy+12+16*elh2+6, "⚡ blink → command", 13, 7.8, ACCENT, ' font-weight="bold"')
        else:
            body += tl(dx+40, dy+12+16*elh2+6, "  watching…", 13, 7.8, MUTED)
        p.append(f'<g class="d d{fi}">' + body + '</g>')
    p.append('</g></svg>')
    open(os.path.join(OUT, "header.svg"), "w").write('\n'.join(p))


build_header()
print('header.svg', os.path.getsize(os.path.join(OUT, 'header.svg')), 'bytes')
