#!/usr/bin/env python3
"""Draw a pixel cat passing through a 3x3 convolution, as light and dark SVGs.

Usage: cat_conv.py <out dir> [cell=14] [kernel_cell=26]
Writes <out dir>/cat-conv-light.svg and <out dir>/cat-conv-dark.svg.

Left: a black-and-white pixel cat on its grid, with a 3x3 window outlined on the edge of
its right ear. Middle: that window's pixels, enlarged. Right: the real result of sliding an
edge-detecting kernel ([-1 -1 -1; -1 8 -1; -1 -1 -1]) over every pixel (zero padding, then
ReLU), which keeps exactly the cat's edge pixels; the cell the window produces is
outlined. Dashed lines run window -> enlarged window -> output cell.
"""
import os
import sys

HALF = [  # left half of the cat, mirrored to full width; '#' is an ink pixel
    "..#.......",
    "..##......",
    "..###.....",
    "..####....",
    ".#######..",
    ".#########",
    "##########",
    "##########",
    "###..#####",
    "###..#####",
    "##########",
    "#########.",
    "##########",
    ".#########",
    "..########",
    "....######",
]
KERNEL = [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]
WINDOW = (17, 1)  # top-left (column, row) of the outlined window, on the right ear's outer edge
PAD = 1  # empty cells around the cat, so the output can show its outer edge
THEMES = {  # GitHub's text and page colours in each theme
    "light": dict(ink="#1f2328", page="#ffffff"),
    "dark": dict(ink="#f0f6fc", page="#0d1117"),
}


def squares(cells, x0, size, inset):
    """One path of inset squares: reads as pixels and leaves no antialiasing seams."""
    s = size - 2 * inset
    return "".join(f"M{x0 + x * size + inset:g} {y * size + inset:g}h{s:g}v{s:g}h{-s:g}z" for x, y in cells)


def main():
    out_dir = sys.argv[1]
    opt = dict(a.split("=", 1) for a in sys.argv[2:])
    c = float(opt.get("cell", 14))
    k = float(opt.get("kernel_cell", 26))

    body = [[1 if ch == "#" else 0 for ch in h + h[::-1]] for h in HALF]
    width_cells = len(body[0]) + 2 * PAD
    cat = [[0] * width_cells for _ in range(PAD)]
    cat += [[0] * PAD + row + [0] * PAD for row in body]
    cat += [[0] * width_cells for _ in range(PAD)]
    rows, cols = len(cat), width_cells

    def px(y, x):
        return cat[y][x] if 0 <= y < rows and 0 <= x < cols else 0

    out = [[max(0, sum(KERNEL[j][i] * px(y + j - 1, x + i - 1) for j in range(3) for i in range(3)))
            for x in range(cols)] for y in range(rows)]  # ReLU, as in a CNN layer

    width = 846.0
    grid_w, grid_h = cols * c, rows * c
    out_x = width - grid_w
    kx = (width - 3 * k) / 2
    ky = (grid_h - 3 * k) / 2 + 0.18 * grid_h  # a little below centre, like a funnel
    height = grid_h

    wx, wy = WINDOW
    win = (wx * c, wy * c, 3 * c)
    cell_out = (out_x + (wx + 1) * c, (wy + 1) * c, c)  # output cell under the window's centre

    ink_cells = [(x, y) for y in range(rows) for x in range(cols) if cat[y][x]]
    strong = [(x, y) for y in range(rows) for x in range(cols) if out[y][x] >= 3]
    mid = [(x, y) for y in range(rows) for x in range(cols) if out[y][x] == 2]
    weak = [(x, y) for y in range(rows) for x in range(cols) if out[y][x] == 1]
    assert all(cat[y][x] for x, y in strong + mid + weak), "output pixels must sit on input pixels"

    for name, t in THEMES.items():
        ink, page = t["ink"], t["page"]
        lines = []
        for x0 in (0, out_x):
            lines += [f"M{x0 + i * c:g} 0V{grid_h:g}" for i in range(cols + 1)]
            lines += [f"M{x0:g} {j * c:g}H{x0 + grid_w:g}" for j in range(rows + 1)]
        lines += [f"M{kx + i * k:g} {ky:g}V{ky + 3 * k:g}" for i in range(4)]
        lines += [f"M{kx:g} {ky + j * k:g}H{kx + 3 * k:g}" for j in range(4)]
        patch = [(i, j) for j in range(3) for i in range(3) if cat[wy + j][wx + i]]  # the window's own pixels
        zoom_inset = k / c  # the input's 1px inset, enlarged with the cells

        def zoom_path(cells):
            s = k - 2 * zoom_inset
            return "".join(f"M{kx + i * k + zoom_inset:g} {ky + j * k + zoom_inset:g}h{s:g}v{s:g}h{-s:g}z" for i, j in cells)

        x0, y0, sz = win
        ox, oy, osz = cell_out
        dashes = [
            (x0 + sz, y0, kx, ky), (x0 + sz, y0 + sz, kx, ky + 3 * k),
            (kx + 3 * k, ky, ox, oy), (kx + 3 * k, ky + 3 * k, ox, oy + osz),
        ]

        def outline(x, y, size):
            x, y, size = x - 1.5, y - 1.5, size + 3  # just outside the cells, so they stay visible
            return (
                f'<rect x="{x:g}" y="{y:g}" width="{size:g}" height="{size:g}" fill="none" stroke="{page}" stroke-width="4"/>'
                f'<rect x="{x:g}" y="{y:g}" width="{size:g}" height="{size:g}" fill="none" stroke="{ink}" stroke-width="2"/>'
            )

        label = ("A pixel cat with a 3 by 3 window over the edge of its ear, that window enlarged, "
                 "and the edge map a convolution produces")
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}" viewBox="0 0 {width:g} {height:g}" '
            f'role="img" aria-label="{label}"><title>{label}</title>'
            f'<path d="{"".join(lines)}" stroke="{ink}" stroke-opacity="0.1" stroke-width="1" fill="none"/>'
            f'<path d="{"".join(f"M{a:g} {b:g}L{p:g} {q:g}" for a, b, p, q in dashes)}" stroke="{ink}" '
            'stroke-opacity="0.5" stroke-width="1" stroke-dasharray="4 4" fill="none"/>'
            f'<path d="{squares(ink_cells, 0, c, 1)}" fill="{ink}"/>'
            f'<path d="{squares(strong, out_x, c, 1)}" fill="{ink}"/>'
            f'<path d="{squares(mid, out_x, c, 1)}" fill="{ink}" fill-opacity="0.6"/>'
            f'<path d="{squares(weak, out_x, c, 1)}" fill="{ink}" fill-opacity="0.35"/>'
            f'<path d="{zoom_path(patch)}" fill="{ink}"/>'
            f"{outline(*win)}{outline(*cell_out)}</svg>\n"
        )
        path = os.path.join(out_dir, f"cat-conv-{name}.svg")
        with open(path, "w") as f:
            f.write(svg)
        print(f"{path}  {width:g}x{height:g}  {len(svg) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
