"""Build README.md as a full-ASCII page (80 columns, <pre> panels with clickable links).
Run:  python3 assets/build_readme.py > README.md
Stats come from assets/stats.json (refreshed by hand or by a workflow)."""
import html, json, os, textwrap
import pyfiglet

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = "https://raw.githubusercontent.com/ummugulsunn/ummugulsunn/main/assets/"
W = 78  # inner width of a panel (plus 2 border chars = 80)

LINKS = {
    "linkedin": "https://linkedin.com/in/ummugulsunturkmen",
    "portfolio": "https://ummugulsun.me",
    "email": "mailto:ummugulsunturkmen@gmail.com",
    "ehliyet": "https://github.com/ummugulsunn/ehliyet-rehberim",
    "neurotech": "https://github.com/ummugulsunn/neurotech-blink-detection",
    "flowstate": "https://github.com/ummugulsunn/FlowStateAI",
    "github": "https://github.com/ummugulsunn",
}

def esc(s): return html.escape(s, quote=False)

class Panel:
    """Collects lines of exactly W visible chars; links are injected after padding."""
    def __init__(self): self.lines = []
    def rule(self, ch="-", left="+", right="+"): self.lines.append(left + ch*W + right)
    def blank(self): self.lines.append("|" + " "*W + "|")
    def row(self, text, links=()):
        """text: visible text (<= W). links: list of (visible_token, href) replaced by <a> after padding."""
        vis = text[:W].ljust(W)
        out = esc(vis)
        for tok, href in links:
            out = out.replace(esc(tok), f'<a href="{href}">{esc(tok)}</a>', 1)
        self.lines.append("|" + out + "|")
    def para(self, text, indent=3, width=None):
        for l in textwrap.wrap(text, width=(width or W-indent-2)):
            self.row(" "*indent + l)
    def figlet(self, word, indent=3):
        for l in pyfiglet.Figlet(font="small").renderText(word).rstrip("\n").split("\n"):
            if l.strip(): self.row(" "*indent + l)
    def render(self): return "\n".join(self.lines)

def chips(items, indent=3):
    """ASCII chips laid out in rows that fit the panel width."""
    rows, cur = [], []
    def width(xs): return sum(len(x)+4 for x in xs) + max(0, len(xs)-1)
    for it in items:
        if width(cur+[it]) + indent > W: rows.append(cur); cur = []
        cur.append(it)
    if cur: rows.append(cur)
    out = []
    for r in rows:
        top = " ".join("." + "-"*(len(x)+2) + "." for x in r)
        mid = " ".join("| " + x + " |" for x in r)
        bot = " ".join("'" + "-"*(len(x)+2) + "'" for x in r)
        out += [" "*indent + top, " "*indent + mid, " "*indent + bot]
    return out

def bar(n, maxn, width):
    k = 0 if maxn == 0 else round(n/maxn*width)
    return "#"*k + "."*(width-k)

stats = json.load(open(os.path.join(HERE, "stats.json")))

# ---------------------------------------------------------------- header (animated ASCII banner + ascii cat)
parts = []
parts.append(f'<div align="center">\n\n<img src="{RAW}header.svg" width="100%" alt="ummugulsun - animated ascii banner" />\n\n</div>\n')

# ---------------------------------------------------------------- about
p = Panel()
p.rule("=")
p.row("  01 / ABOUT")
p.rule("=")
p.blank()
p.figlet("about")
p.blank()
p.para("Computer Engineering student with a product-first mindset. I don't just write code -- I design experiences. "
       "From shipping a 5-star rated app on Google Play to prototyping touchless interfaces with EEG sensors, "
       "every project starts and ends with the user.")
p.blank()
p.row("   currently exploring")
for l in chips(["human-computer interaction", "behavioral analysis", "mobile product development"]): p.row(l)
p.blank()
p.rule()
about = p.render()

# ---------------------------------------------------------------- stack
p = Panel()
p.rule("=")
p.row("  02 / STACK")
p.rule("=")
p.blank()
p.figlet("stack")
p.blank()
p.row("   languages & frameworks")
for l in chips(["python", "dart", "c++", "sql", "flutter"]): p.row(l)
p.blank()
p.row("   tools & platforms")
for l in chips(["vs code", "android studio", "git", "arduino"]): p.row(l)
p.blank()
p.row("   product & design")
for l in chips(["ui/ux", "behavior analysis", "microcopy", "google pm"]): p.row(l)
p.blank()
p.rule()
stack = p.render()

# ---------------------------------------------------------------- projects
ICON_PHONE = [" .----. ", " |####| ", " |####| ", " |    | ", " '-o--' "]
ICON_EYE   = ["        ", " .-\"\"-. ", "( (@) ) ", " '-..-' ", "        "]
ICON_KEYS  = [" .-----.", " |=====|", " |=====|", " |_____|", "        "]
PROJECTS = [
    ("EHLIYET REHBERIM", "mobile product & ux", ICON_PHONE,
     "Solo-developed driving education app, live on Google Play with a 5.0 rating. Every flow designed from scratch; used daily by people preparing for their driving exam.",
     "flutter . dart . google play", "ehliyet"),
    ("NEUROTECH", "hci & bio-signals", ICON_EYE,
     "Touchless interaction prototype on real-time EEG signal processing. No screens, no touch: a blink becomes a command.",
     "c++ . arduino . eeg sensors", "neurotech"),
    ("FLOWSTATEAI", "ai & behavior analysis", ICON_KEYS,
     "Decodes how people really use a system from keystroke dynamics, combining Python data analysis with behavioral pattern recognition.",
     "python . data analysis", "flowstate"),
]
p = Panel()
p.rule("=")
p.row("  03 / SELECTED WORK")
p.rule("=")
p.blank()
p.figlet("projects")
p.blank()
for title, role, icon, desc, tech, key in PROJECTS:
    p.rule()
    body = textwrap.wrap(desc, width=W-14-2)
    tag = "[ view repo ]"
    lines = [title.ljust(W-14-len(role)-2) + role] + body
    while len(lines) < 4: lines.append("")
    lines.append(tech.ljust(W-14-len(tag)-2) + tag)
    for i, l in enumerate(lines):
        ic = icon[i] if i < len(icon) else " "*8
        text = "  " + ic + "  " + l
        p.row(text, links=[(tag, LINKS[key])] if tag in l else ())
p.rule()
projects = p.render()

# ---------------------------------------------------------------- stats (ascii, from stats.json)
p = Panel()
p.rule("=")
p.row("  04 / GITHUB")
p.rule("=")
p.blank()
p.figlet("stats")
p.blank()
mx = max(stats["public_repos"], stats["stars"], stats["followers"], 1)
BW = 40
p.row(f"   public repos   {stats['public_repos']:>4}   {bar(stats['public_repos'], mx, BW)}")
p.row(f"   stars earned   {stats['stars']:>4}   {bar(stats['stars'], mx, BW)}")
p.row(f"   followers      {stats['followers']:>4}   {bar(stats['followers'], mx, BW)}")
p.blank()
p.row("   languages across public repos")
lmax = max(v for _, v in stats["languages"]) if stats["languages"] else 1
for name, cnt in stats["languages"][:6]:
    p.row(f"   {name.lower():<14} {cnt:>3}   {bar(cnt, lmax, BW)}")
p.blank()
p.row(f"   on github since {stats['since']}   .   last refreshed {stats['updated']}")
p.blank()
p.rule()
ghstats = p.render()

# ---------------------------------------------------------------- footer / links
p = Panel()
p.rule("=")
p.row("  05 / CONTACT")
p.rule("=")
p.blank()
p.row("   open to collaboration on HCI, mobile product and AI projects.")
p.blank()
line = "   [ linkedin ]   [ portfolio ]   [ email ]   [ github ]"
p.row(line, links=[("[ linkedin ]", LINKS["linkedin"]), ("[ portfolio ]", LINKS["portfolio"]),
                   ("[ email ]", LINKS["email"]), ("[ github ]", LINKS["github"])])
p.blank()
p.rule()
contact = p.render()

cat = f'<div align="center">\n\n<img src="{RAW}cat.svg" width="300" alt="ascii cat, typing" />\n\n<sub><samp>// ascii.cat is typing...</samp></sub>\n\n</div>\n'

readme = "\n".join([
    parts[0],
    "<pre>\n" + about + "\n</pre>\n",
    cat,
    "<pre>\n" + stack + "\n</pre>\n",
    "<pre>\n" + projects + "\n</pre>\n",
    "<pre>\n" + ghstats + "\n</pre>\n",
    "<pre>\n" + contact + "\n</pre>\n",
    '<div align="center"><sub><samp>built in ascii, by hand. thanks for scrolling.</samp></sub></div>\n',
])
print(readme)
