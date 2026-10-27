#!/usr/bin/env python3
"""Set the README header ("Caden Sun") as outlined SVG paths, light and dark.

Usage: name_header.py <out dir> [size=76] [track=-0.02] [gap=22]
Writes <out dir>/name-light.svg and <out dir>/name-dark.svg.

The face is Archivo (SIL Open Font License) at 125% width, the typeface of the
personal website. Subsets with only these letters come from Google Fonts; the dark
version is a touch lighter (460 against 500) because light text on a dark ground
reads heavier. opentype.js shapes the text (kerning on) in headless Chrome, and the
letters are written out as paths, so the SVG needs no font to load anywhere.
Each SVG is trimmed to the ink: the C starts at x=0 so it lines up with the text
below it, the tallest letter touches the top, and `gap` px follow the baseline.
Needs network access and Google Chrome (set CHROME to use another binary).
"""
import base64
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
OPENTYPE = "https://cdnjs.cloudflare.com/ajax/libs/opentype.js/1.3.4/opentype.min.js"
TEXT = "Caden Sun"
WEIGHTS = {"light": 500, "dark": 460}
INK = {"light": "#1f2328", "dark": "#f0f6fc"}  # GitHub's default text colour in each theme

PAGE = """<!doctype html><meta charset="utf-8"><script src="%(lib)s"></script><pre id="out"></pre><script>
const cfg = %(cfg)s, out = {};
for (const [name, b64] of Object.entries(cfg.fonts)) {
  const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const font = opentype.parse(bytes.buffer);
  const path = font.getPath(cfg.text, 0, 0, cfg.size, {kerning: true, letterSpacing: cfg.track});
  const bb = path.getBoundingBox();
  // move the ink to the origin: left edge at x=0, top of the tallest letter at y=0
  for (const c of path.commands) for (const k of ["x", "x1", "x2"]) if (k in c) c[k] -= bb.x1;
  for (const c of path.commands) for (const k of ["y", "y1", "y2"]) if (k in c) c[k] -= bb.y1;
  out[name] = {d: path.toPathData(2), width: bb.x2 - bb.x1, baseline: -bb.y1};
}
document.getElementById("out").textContent = JSON.stringify(out);
</script>"""


def fetch_subset(weight):
    """TrueType subset of Archivo with only the letters of TEXT."""
    query = urllib.parse.urlencode({"family": f"Archivo:wdth,wght@125,{weight}", "text": TEXT})
    css = urllib.request.urlopen(f"https://fonts.googleapis.com/css2?{query}", timeout=30).read().decode()
    url = re.search(r"url\((https://[^)]+)\)", css).group(1)
    return urllib.request.urlopen(url, timeout=30).read()


def main():
    out_dir = sys.argv[1]
    opt = dict(a.split("=", 1) for a in sys.argv[2:])
    size = float(opt.get("size", 76))
    gap = float(opt.get("gap", 22))
    cfg = dict(
        text=TEXT, size=size, track=float(opt.get("track", -0.02)),
        fonts={name: base64.b64encode(fetch_subset(w)).decode() for name, w in WEIGHTS.items()},
    )
    with tempfile.TemporaryDirectory() as tmp:
        page = os.path.join(tmp, "shape.html")
        with open(page, "w") as f:
            f.write(PAGE % dict(lib=OPENTYPE, cfg=json.dumps(cfg)))
        dom = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=5000", "--dump-dom", "file://" + page],
            capture_output=True, text=True, timeout=120,
        ).stdout
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    if not m or not m.group(1).strip():
        raise SystemExit("opentype.js produced no output")
    shapes = json.loads(html.unescape(m.group(1)))

    # one canvas for both themes: the <img> width in the README applies to whichever loads
    w = int(-(-max(s["width"] for s in shapes.values()) // 1)) + 1
    h = round(max(s["baseline"] for s in shapes.values()) + gap)
    for name, s in shapes.items():
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{TEXT}"><title>{TEXT}</title>'
            f'<path fill="{INK[name]}" d="{s["d"]}"/></svg>\n'
        )
        path = os.path.join(out_dir, f"name-{name}.svg")
        with open(path, "w") as f:
            f.write(svg)
        print(f"{path}  {w}x{h}")


if __name__ == "__main__":
    main()
