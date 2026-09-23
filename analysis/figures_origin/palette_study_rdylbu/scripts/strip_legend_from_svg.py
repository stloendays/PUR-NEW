"""Delete an Origin object from an exported SVG by bounding box.

Origin's contour template keeps a legend that `label -r Legend`,
`set_legend(visible=False)` and `Legend.show=0` all fail to remove silently. The
workaround is to shrink it (`set_legend(font_size=1)`), then drop the elements
that survive inside its box here, and rasterize from the cleaned SVG.

Two traps this avoids:
  * a fill like "#115FA4" yields the digits 115 and 4 to a naive number regex,
    so coordinates are read only from points=, d= and the element's own x=/y=;
  * a <text> carries x on both the element and its tspan but y only once, so
    pairing numbers by index mis-assigns y and deletes unrelated tick labels.

usage: strip_legend_from_svg.py <file.svg> <x0> <y0> <x1> <y1>
"""
import re
import sys

PATH, X0, Y0, X1, Y1 = sys.argv[1], *map(float, sys.argv[2:6])


def coords(block):
    pts = []
    for attr in ("points", "d"):
        for m in re.finditer(r'\b%s="([^"]*)"' % attr, block):
            v = [float(x) for x in re.findall(r"-?\d+\.?\d*", m.group(1))]
            pts += list(zip(v[0::2], v[1::2]))
    if block.startswith("<text"):
        mx = re.search(r'<text[^>]*?\bx="(-?\d+\.?\d*)"', block)
        my = re.search(r'<text[^>]*?\by="(-?\d+\.?\d*)"', block)
        if mx and my:
            pts.append((float(mx.group(1)), float(my.group(1))))
    return pts


src = open(PATH, encoding="utf-8", errors="ignore").read()
blocks = re.split(r"(?=<(?:text|polyline|path|rect))", src)
kept, removed, i = [], 0, 0
while i < len(blocks):
    b = blocks[i]
    if b.startswith("<text"):
        while "</text>" not in b and i + 1 < len(blocks):
            i += 1
            b += blocks[i]
    pts = coords(b)
    if pts and all(X0 <= x <= X1 and Y0 <= y <= Y1 for x, y in pts):
        removed += 1
        i += 1
        continue
    kept.append(b)
    i += 1

open(PATH, "w", encoding="utf-8").write("".join(kept))
print("removed %d elements from %s" % (removed, PATH))
