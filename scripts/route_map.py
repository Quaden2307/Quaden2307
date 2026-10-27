#!/usr/bin/env python3
"""Draw the flight-price-predictor route network as light and dark SVG maps.

Usage: route_map.py <flight-price-predictor dir> <out dir> [key=value ...]
Writes <out dir>/routes-light.svg and <out dir>/routes-dark.svg.

Reads the routes from data_collector/routes.py (parsed, never imported) and the
airport coordinates from models/airports.csv. Every route is drawn as its true great
circle on an Equal Earth projection centred on North America (90°W), so the seam falls
in the Bay of Bengal where almost nothing crosses it. Land is Natural Earth 1:110m
(public domain). d3-geo does the projection, great-circle resampling and seam clipping
in headless Chrome. Needs network access and Google Chrome (set CHROME to override).

Options: centre=-90 top=86 bottom=-36 width=846 arc_width=0.8 dot_r=1.8
         arc_opacity_light=0.36 arc_opacity_dark=0.3
"""
import ast
import csv
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
D3 = "https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"
LAND = "https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@v5.1.2/geojson/ne_110m_land.geojson"
THEMES = {  # GitHub's text colour in each theme, and one tone step off its page colour for land
    "light": dict(ink="#1f2328", land="#eef1f4"),
    "dark": dict(ink="#f0f6fc", land="#161b22"),
}

PAGE = """<!doctype html><meta charset="utf-8"><script src="%(d3)s"></script><pre id="out"></pre><script>
const cfg = %(cfg)s, land = %(land)s;
const proj = d3.geoEqualEarth().rotate([-cfg.centre, 0]).precision(0.2);
// fit the whole width, then crop to the latitude band [bottom, top]
// (Equal Earth is pseudocylindrical: y depends on latitude only)
proj.fitWidth(cfg.width - 2 * cfg.pad, {type: "Sphere"});
proj.translate([proj.translate()[0] + cfg.pad, proj.translate()[1]]);
const yTop = proj([cfg.centre, cfg.top])[1], yBot = proj([cfg.centre, cfg.bottom])[1];
proj.translate([proj.translate()[0], proj.translate()[1] - yTop + cfg.pad]);
const path = d3.geoPath(proj).digits(1);
const line = r => ({type: "LineString", coordinates: [cfg.airports[r[0]], cfg.airports[r[1]]]});
document.getElementById("out").textContent = JSON.stringify({
  height: Math.ceil(yBot - yTop + 2 * cfg.pad),
  sphere: path({type: "Sphere"}),
  land: path({type: "FeatureCollection", features: land.features.filter(f => d3.geoBounds(f)[1][1] > cfg.bottom)}),
  arcs: path({type: "GeometryCollection", geometries: cfg.routes.map(line)}),
  dots: [...new Set(cfg.routes.flat())].map(a => proj(cfg.airports[a]).map(v => +v.toFixed(1))),
});
</script>"""


def load_routes(project):
    with open(os.path.join(project, "data_collector", "routes.py")) as f:
        tree = ast.parse(f.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ROUTES":
            return ast.literal_eval(node.value)
    raise SystemExit("ROUTES not found in data_collector/routes.py")


def load_airports(project):
    with open(os.path.join(project, "models", "airports.csv")) as f:
        return {r["iata"]: [float(r["longitude"]), float(r["latitude"])] for r in csv.DictReader(f)}


def main():
    project, out_dir = sys.argv[1:3]
    opt = dict(a.split("=", 1) for a in sys.argv[3:])
    routes = load_routes(project)
    airports = load_airports(project)
    cfg = dict(
        centre=float(opt.get("centre", -90)),
        top=float(opt.get("top", 86)),
        bottom=float(opt.get("bottom", -36)),
        width=float(opt.get("width", 846)),
        pad=2,
        routes=routes,
        airports=airports,
    )
    land = urllib.request.urlopen(LAND, timeout=60).read().decode()
    with tempfile.TemporaryDirectory() as tmp:
        page = os.path.join(tmp, "map.html")
        with open(page, "w") as f:
            f.write(PAGE % dict(d3=D3, cfg=json.dumps(cfg), land=land))
        dom = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=5000", "--dump-dom", "file://" + page],
            capture_output=True, text=True, timeout=120,
        ).stdout
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    if not m or not m.group(1).strip():
        raise SystemExit("d3 produced no output")
    data = json.loads(html.unescape(m.group(1)))

    w, h = cfg["width"], data["height"]
    n_airports = len({a for r in routes for a in r})
    label = (
        f"Map of the {len(routes)} routes between {n_airports} airports that the flight price "
        "pipeline collects fares on every day"
    )
    for name, c in THEMES.items():
        stroke = (
            f'fill="none" stroke="{c["ink"]}" stroke-width="{opt.get("arc_width", "0.8")}" '
            f'stroke-opacity="{opt.get("arc_opacity_" + name, "0.36" if name == "light" else "0.3")}" '
            'stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"'
        )
        r = opt.get("dot_r", "1.8")
        dots = "".join(f'<circle cx="{x:g}" cy="{y:g}" r="{r}"/>' for x, y in data["dots"])
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}" height="{h}" viewBox="0 0 {w:g} {h}" '
            f'role="img" aria-label="{label}"><title>{label}</title>'
            f'<clipPath id="s"><path d="{data["sphere"]}"/></clipPath><g clip-path="url(#s)">'
            f'<path d="{data["land"]}" fill="{c["land"]}"/>'
            f'<path d="{data["arcs"]}" {stroke}/>'
            f'<g fill="{c["ink"]}">{dots}</g></g></svg>\n'
        )
        path = os.path.join(out_dir, f"routes-{name}.svg")
        with open(path, "w") as f:
            f.write(svg)
        print(f"{path}  {w:g}x{h}  {len(svg) / 1024:.0f} KB")
    print(f"{len(routes)} routes, {n_airports} airports")


if __name__ == "__main__":
    main()
