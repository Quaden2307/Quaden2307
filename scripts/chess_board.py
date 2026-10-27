#!/usr/bin/env python3
"""Draw a chess position with move arrows as light and dark SVGs.

Usage: chess_board.py <out-prefix> fen="<FEN>" arrows="c4f7,e8e7,c3d5" [opacity=0.85,0.3,0.85]
                      [square=40] [label="..."]
Writes <out-prefix>-light.svg and <out-prefix>-dark.svg.

Arrows are UCI moves; each gets the matching opacity. The pieces are the Unicode chess
glyphs of Noto Sans Symbols 2 (SIL Open Font License), fetched as a subset from Google
Fonts and outlined with opentype.js in headless Chrome. In the light theme white pieces
are the hollow glyphs and black pieces the solid ones; the dark theme swaps the sets so
white pieces still read as the light side. Needs network access and Google Chrome.

The README's position is Légal's Mate, where Quaden2307/chess-engine's live API
(/api/best-move and /api/suggested-moves, 2026-10-26) finds 6.Bxf7+ Ke7 7.Nd5#:
  fen="rn1qkbnr/ppp2p1p/3p2p1/4N3/2B1P3/2N5/PPPP1PPP/R1BbK2R w KQkq - 0 6"
"""
import base64
import html
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
OPENTYPE = "https://cdnjs.cloudflare.com/ajax/libs/opentype.js/1.3.4/opentype.min.js"
HOLLOW = {"K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙"}
SOLID = {"K": "♚", "Q": "♛", "R": "♜", "B": "♝", "N": "♞", "P": "♟"}
THEMES = {  # GitHub's text colour as ink; two quiet square tones per theme
    "light": dict(ink="#1f2328", light_sq="#f6f8fa", dark_sq="#e3e8ed", white=HOLLOW, black=SOLID),
    "dark": dict(ink="#f0f6fc", light_sq="#1b212a", dark_sq="#131820", white=SOLID, black=HOLLOW),
}

PAGE = """<!doctype html><meta charset="utf-8"><script src="%(lib)s"></script><pre id="out"></pre><script>
const cfg = %(cfg)s;
const bytes = Uint8Array.from(atob(cfg.font), c => c.charCodeAt(0));
const font = opentype.parse(bytes.buffer);
const out = {};
for (const ch of cfg.chars) {
  const p = font.getPath(ch, 0, 0, 100);
  const bb = p.getBoundingBox();
  // centre each glyph's ink on the origin
  const cx = (bb.x1 + bb.x2) / 2, cy = (bb.y1 + bb.y2) / 2;
  for (const c of p.commands) {
    for (const k of ["x", "x1", "x2"]) if (k in c) c[k] -= cx;
    for (const k of ["y", "y1", "y2"]) if (k in c) c[k] -= cy;
  }
  out[ch] = {d: p.toPathData(2), h: bb.y2 - bb.y1};
}
document.getElementById("out").textContent = JSON.stringify(out);
</script>"""


def fetch_glyph_font():
    chars = "".join(HOLLOW.values()) + "".join(SOLID.values())
    query = urllib.parse.urlencode({"family": "Noto Sans Symbols 2", "text": chars})
    css = urllib.request.urlopen(f"https://fonts.googleapis.com/css2?{query}", timeout=30).read().decode()
    url = re.search(r"url\((https://[^)]+)\)", css).group(1)
    return urllib.request.urlopen(url, timeout=30).read()


def glyph_paths():
    cfg = dict(font=base64.b64encode(fetch_glyph_font()).decode(), chars=list(HOLLOW.values()) + list(SOLID.values()))
    with tempfile.TemporaryDirectory() as tmp:
        page = os.path.join(tmp, "glyphs.html")
        with open(page, "w") as f:
            f.write(PAGE % dict(lib=OPENTYPE, cfg=json.dumps(cfg)))
        dom = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=5000", "--dump-dom", "file://" + page],
            capture_output=True, text=True, timeout=120,
        ).stdout
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    if not m or not m.group(1).strip():
        raise SystemExit("opentype.js produced no output")
    return json.loads(html.unescape(m.group(1)))


def parse_fen(fen):
    board = {}
    for r, row in enumerate(fen.split()[0].split("/")):
        f = 0
        for ch in row:
            if ch.isdigit():
                f += int(ch)
            else:
                board[(f, 7 - r)] = ch  # file 0..7 is a..h, rank 0..7 is 1..8
                f += 1
    return board


def arrow(x1, y1, x2, y2, sq):
    """Polygon for an arrow from square centre to square centre, tip short of the target."""
    length = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    px, py = -uy, ux
    shaft, head_w, head_l = sq * 0.16, sq * 0.46, sq * 0.42
    start, tip = sq * 0.18, length - sq * 0.12
    base = tip - head_l

    def at(t, w):
        return (x1 + ux * t + px * w, y1 + uy * t + py * w)

    pts = [at(start, shaft / 2), at(base, shaft / 2), at(base, head_w / 2), at(tip, 0),
           at(base, -head_w / 2), at(base, -shaft / 2), at(start, -shaft / 2)]
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def main():
    prefix = sys.argv[1]
    opt = dict(a.split("=", 1) for a in sys.argv[2:])
    sq = float(opt.get("square", 40))
    board = parse_fen(opt["fen"])
    moves = [m for m in opt.get("arrows", "").split(",") if m]
    opacity = [float(o) for o in opt.get("opacity", ",".join(["0.85"] * len(moves))).split(",")]
    label = opt.get("label", "Chess position with the engine's moves drawn as arrows")
    glyphs = glyph_paths()
    scale = 0.8 * sq / max(g["h"] for g in glyphs.values())  # tallest piece fills 80% of a square
    size = round(8 * sq)

    def centre(f, r):
        return (f + 0.5) * sq, (7.5 - r) * sq

    for name, t in THEMES.items():
        defs = [
            f'<path id="{side}{piece}" d="{glyphs[ch]["d"]}"/>'
            for side, table in (("w", t["white"]), ("b", t["black"]))
            for piece, ch in table.items()
        ]
        squares = [
            f'<rect x="{f * sq:g}" y="{(7 - r) * sq:g}" width="{sq:g}" height="{sq:g}" '
            f'fill="{t["light_sq"] if (f + r) % 2 else t["dark_sq"]}"/>'
            for f in range(8) for r in range(8)
        ]
        pieces = []
        for (f, r), ch in sorted(board.items()):
            x, y = centre(f, r)
            side = "w" if ch.isupper() else "b"
            pieces.append(f'<use href="#{side}{ch.upper()}" transform="translate({x:g} {y:g}) scale({scale:.4f})"/>')
        arrows = []
        for mv, op in zip(moves, opacity):
            (x1, y1), (x2, y2) = centre(ord(mv[0]) - 97, int(mv[1]) - 1), centre(ord(mv[2]) - 97, int(mv[3]) - 1)
            arrows.append(f'<polygon points="{arrow(x1, y1, x2, y2, sq)}" fill="{t["ink"]}" fill-opacity="{op:g}"/>')
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
            f'role="img" aria-label="{label}"><title>{label}</title>'
            f"<defs>{''.join(defs)}</defs>{''.join(squares)}"
            f'<g fill="{t["ink"]}">{"".join(pieces)}</g>{"".join(arrows)}</svg>\n'
        )
        path = f"{prefix}-{name}.svg"
        with open(path, "w") as f:
            f.write(svg)
        print(f"{path}  {size}x{size}  {len(svg) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
