# README redesign — working notes

Branch `readme-redesign` holds every iteration of the profile README redesign.
`main` was reset to the original README (commit `d82550d`) so the live profile is untouched
until a version is approved. Nothing here is on GitHub's profile page yet.

## How to build

```bash
pip install pyfiglet
python3 assets/generate.py assets        # writes the SVGs next to this file
```

Preview on the Mac: the helper files live in `/tmp/readme-preview/` (generate.py, wrap2.py,
cat.json); `wrap2.py <theme>` renders README.md through GitHub's markdown API into `index_<theme>.html`.

## Versions, in order (one commit each)

| v | What | Verdict |
|---|------|---------|
| 1 | capsule-render banner, GitHub stats, snake + 3D calendar workflows | pushed without asking, reverted. Never push without approval. |
| 2 | ASCII pixel name + rotating torus + EEG strip, typed terminal | pushed on approval; later judged gimmicky |
| 3 | door intro (darasoba), holographic pixel name (wowww), story chapters (uibeawuchi), lock screen (frvky) | "unprofessional and fake" |
| 4 | 900px assets, no tables, EEG dividers, phone cards | too much, too gray |
| 5 | original structure + one ASCII banner | ok-ish |
| 6 | torus replaced by a blinking ASCII eye synced to EEG spikes | "what is that spinning circle" → eye not liked either |
| — | full 80-column ASCII README with panels, ASCII cat, ASCII stats | boxes crude, gray, long |
| 7 | modern banner: ASCII shader field + clean type "I design experiences, then I ship them." | "nice-ish", wanted gray-heavy or turquoise |
| 8 | holographic pixel name over the living ASCII field, curated projects, stats kept | — |
| 9 | "signal → interface": static resolves into the name as a scan line sweeps | my own designer concept |
| 10 | dark-luxury glass dashboard: thin-line name (`shadow` font) with neon Ü dots, EEG→sample→interface hero, about panel, 4 project cards, 3 buttons | user's detailed brief; "ok but not sure" |

## What the user has said they want / don't want

- Wow effect, modern, compact, professional. Not gimmicky, not fake-looking.
- ASCII is liked; the pixel/holographic name was liked; the torus and the eye were not.
- Gray-heavy palette preferred; turquoise also liked. Copper was tried and dropped.
- The ASCII cat must stay (converted from the pixel-cat GIF, frames in `cat.json`).
- The streak card at the bottom is liked and may stay.
- Featured projects (my pick from the 37 public repos): Stremio Dual Subtitles (37★, live),
  Ehliyet Rehberim (Google Play 5.0), Neurotech Blink Detection (EEG), Automata Theory Simulator (live).
  The v10 brief also asked for GlowIsland and FaceGlow (TurkmenApps, not on GitHub): need real
  taglines + store links from the user.
- Never push to main without an explicit "push et". Keep commits authored by the user, no Claude trailers.

## Facts used

- Public API (Nov 2026): 37 public repos, 53 stars total, 6 followers; languages Python 9, HTML 5, TS 4, JS 2, Dart 2.
- GitHub README column is ~690–1010px wide; SVG text must be ≥15px at 900px width to stay readable.
- `github-readme-stats-sigma-five.vercel.app` (used in the original README) is down; the official
  `github-readme-stats.vercel.app` and `streak-stats.demolab.com` work.

## Character-mosaic animations (Nov 10)

The user showed reference reels (git-koi, an ASCII eye "The Connection", an ASCII lily bouquet) and wants
that dense, coloured, glowing look, not thin line-art ASCII. SVG text cannot carry that density, so these
are rendered to animated WebP: paint the scene with PIL/numpy, map every cell to a glyph + colour, add bloom.

- `assets/mosaic/mosaic.py` shared renderer; `flower.py` -> `lily.webp`, `koi.py` -> `koi.webp` (both approved: "iyi duruyor").
- `connection.py` (letter field with eyes, zoom into pupil, two profiles merge) and `eye2.py` (single turquoise eye)
  are drafts; the user has not approved them. Eyes in the letter field look cartoonish.
- Run: `pip install numpy pillow && python3 assets/mosaic/flower.py assets` (needs DejaVu Sans Mono Bold).
- Thin-line demos (TerminalTextEffects decrypt, asciimatics plasma, line-art koi) were rejected as "not like the videos".
- git-koi itself (yalongwastaken/git-koi, a GitHub Action) was not installed: its repo could not be reached from the cloud session.
