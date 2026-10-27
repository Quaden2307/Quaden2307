#!/usr/bin/env python3
"""Draw the last year of GitHub contributions like GitHub's own graph, in white.

Usage: contributions.py <contributions.json> <out dir> [width=846]
Writes <out dir>/contributions-light.svg and <out dir>/contributions-dark.svg.

Reads the JSON from https://github-contributions-api.jogruber.de/v4/<user>?y=last and
copies the layout of the contribution section on a GitHub profile: the "N contributions
in the last year" line, a rounded bordered box, month labels, Mon/Wed/Fri labels, one
column per week with Sunday on top (10px rounded squares on a 13px grid) and the
Less/More legend. Levels run from GitHub's empty square up to white in the dark theme,
and up to GitHub's text colour in the light theme.
"""
import json
import os
import sys
from datetime import date

FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
THEMES = {
    # level 0 is GitHub's own empty square; levels 1-4 blend the text colour over the page
    "dark": dict(text="#f0f6fc", muted="#9198a1", border="#3d444d",
                 levels=["#151b23", "#363a40", "#686d73", "#a1a6ac", "#f0f6fc"]),
    "light": dict(text="#1f2328", muted="#59636e", border="#d1d9e0",
                  levels=["#eff2f5", "#d7d7d8", "#a5a7a9", "#6d7073", "#1f2328"]),
}
CELL, PITCH = 10, 13  # GitHub's square and grid spacing
LABEL_W = 30  # weekday label column
MORE_W = 30  # room for the word "More" at 12px
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def square(x, y, fill):
    # GitHub draws each day with a faint 1px inner outline
    return (f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{fill}"/>'
            f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{CELL - 1}" height="{CELL - 1}" rx="1.5" '
            f'fill="none" stroke="currentColor" stroke-opacity="0.06"/>')


def main():
    src, out_dir = sys.argv[1:3]
    opt = dict(a.split("=", 1) for a in sys.argv[3:])
    width = float(opt.get("width", 846))

    with open(src) as f:
        days = json.load(f)["contributions"]
    total = sum(d["count"] for d in days)

    weeks, column = [], [None] * 7
    for d in days:
        row = (date.fromisoformat(d["date"]).weekday() + 1) % 7  # Sunday = 0
        if row == 0 and any(column):
            weeks.append(column)
            column = [None] * 7
        column[row] = d
    weeks.append(column)

    # month labels: at the first week of each month, dropped when the next label is too close
    starts = []
    for i, week in enumerate(weeks):
        month = int(next(d for d in week if d)["date"][5:7])
        if not starts or starts[-1][1] != month:
            starts.append((i, month))
    starts = [s for k, s in enumerate(starts) if k + 1 == len(starts) or starts[k + 1][0] - s[0] >= 3]

    grid_w = len(weeks) * PITCH - (PITCH - CELL)
    left = round((width - LABEL_W - grid_w) / 2)  # graph centred in the box, as on wide screens
    gx = left + LABEL_W
    box_y = 30  # the "N contributions" line sits above the box
    gy = box_y + 32  # month labels sit in the 32px above the grid
    legend_y = gy + 7 * PITCH - (PITCH - CELL) + 12
    box_h = legend_y + CELL + 14 - box_y
    height = box_y + box_h + 18  # room before the README text below

    more_x = gx + grid_w  # "More" ends at the grid's right edge
    legend_x = more_x - MORE_W - 5 * PITCH + (PITCH - CELL) - 4  # first legend square

    label = f"{total:,} contributions in the last year"
    for name, t in THEMES.items():
        cells = "".join(
            square(gx + x * PITCH, gy + y * PITCH, t["levels"][d["level"]])
            for x, week in enumerate(weeks) for y, d in enumerate(week) if d is not None
        )
        legend_cells = "".join(square(legend_x + i * PITCH, legend_y, t["levels"][i]) for i in range(5))
        months = "".join(f'<text x="{gx + i * PITCH}" y="{gy - 10}">{MONTHS[m - 1]}</text>' for i, m in starts)
        weekdays = "".join(
            f'<text x="{left}" y="{gy + r * PITCH + 9}">{word}</text>' for r, word in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
        )
        legend_text = (
            f'<text x="{legend_x - 6}" y="{legend_y + 9}" text-anchor="end">Less</text>'
            f'<text x="{more_x}" y="{legend_y + 9}" text-anchor="end">More</text>'
        )
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height}" '
            f'viewBox="0 0 {width:g} {height}" role="img" aria-label="{label}" color="{t["text"]}">'
            f"<title>{label}</title>"
            f'<text x="0" y="18" font-family="{FONT}" font-size="16" fill="{t["text"]}">{label}</text>'
            f'<rect x="0.5" y="{box_y + 0.5}" width="{width - 1:g}" height="{box_h - 1}" rx="6" '
            f'fill="none" stroke="{t["border"]}"/>'
            f'<g font-family="{FONT}" font-size="12" fill="{t["muted"]}">{months}{weekdays}{legend_text}</g>'
            f"{cells}{legend_cells}</svg>\n"
        )
        path = os.path.join(out_dir, f"contributions-{name}.svg")
        with open(path, "w") as f:
            f.write(svg)
        print(f"{path}  {width:g}x{height}  {len(weeks)} weeks  {total} contributions")


if __name__ == "__main__":
    main()
