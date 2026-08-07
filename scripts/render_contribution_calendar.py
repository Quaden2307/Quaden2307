#!/usr/bin/env python3
"""Render the GitHub-style contribution calendar in the profile's blue palette.

Reads the JSON from https://github-contributions-api.jogruber.de/v4/<user>?y=last
and writes an SVG laid out like GitHub's regular contribution graph:
Sunday-first week columns, month labels, Mon/Wed/Fri row labels, and a
Less-to-More legend.

Usage: render_contribution_calendar.py <contributions.json> <output.svg>
"""
import json
import sys
from datetime import date

LEVELS = ["#161616", "#1e3a8a", "#1d4ed8", "#3b82f6", "#60a5fa"]
BG, BORDER, MUTED = "#0a0a0a", "#262626", "#737373"
FONT = "Segoe UI, Ubuntu, sans-serif"
CELL, GAP = 11, 3
PITCH = CELL + GAP


def main(src, dst):
    with open(src) as f:
        days = json.load(f)["contributions"]

    # Sunday-first week columns, like github.com
    weeks, col = [], [None] * 7
    for d in days:
        y, m, dd = map(int, d["date"].split("-"))
        row = (date(y, m, dd).weekday() + 1) % 7  # Sun=0 ... Sat=6
        if row == 0 and any(col):
            weeks.append(col)
            col = [None] * 7
        col[row] = d
    weeks.append(col)

    pad, left, top = 14, 46, 30
    w = left + len(weeks) * PITCH - GAP + pad
    h = top + 7 * PITCH - GAP + 34
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="GitHub contribution calendar">',
        f'  <rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
    ]

    last_month, last_x = None, -100
    for i, wk in enumerate(weeks):
        first = next(d for d in wk if d)
        month = first["date"][5:7]
        x = left + i * PITCH
        if month != last_month and x - last_x >= 2 * PITCH:
            name = date(2000, int(month), 1).strftime("%b")
            out.append(
                f'  <text x="{x}" y="{top-9}" font-family="{FONT}" font-size="11" fill="{MUTED}">{name}</text>'
            )
            last_x = x
        last_month = month

    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = top + row * PITCH + CELL - 2
        out.append(
            f'  <text x="{pad}" y="{y}" font-family="{FONT}" font-size="11" fill="{MUTED}">{name}</text>'
        )

    for i, wk in enumerate(weeks):
        for row, d in enumerate(wk):
            if d is None:
                continue
            x, y = left + i * PITCH, top + row * PITCH
            out.append(
                f'  <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{LEVELS[d["level"]]}"><title>{d["date"]}: {d["count"]}</title></rect>'
            )

    ly = h - 22
    lx = w - pad - 104
    out.append(
        f'  <text x="{lx-34}" y="{ly+9}" font-family="{FONT}" font-size="11" fill="{MUTED}">Less</text>'
    )
    for level, color in enumerate(LEVELS):
        out.append(
            f'  <rect x="{lx + level*PITCH}" y="{ly}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>'
        )
    out.append(
        f'  <text x="{lx + 5*PITCH + 4}" y="{ly+9}" font-family="{FONT}" font-size="11" fill="{MUTED}">More</text>'
    )
    out.append("</svg>")

    with open(dst, "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
