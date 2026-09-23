"""Assemble single-panel Origin SVG exports into one multi-panel figure.

Each child keeps its own coordinate system inside a nested <svg> viewport, so
the result stays vector. Panel letters are drawn by this script rather than
placed in Origin, because Origin's per-panel page has no room above the axes
and its text objects do not render at all on 3D or ternary layers.

Two things this must get right, both learned the hard way:
  * the parent has to declare xmlns:olab. Origin writes olab:comment on its
    elements, and dropping the root declaration makes the whole file fail to
    parse, which a browser shows as a broken-image icon rather than an error.
  * every child carries <mask id="Cp_1">. Without namespacing the ids, the
    masks collide and whole panels get clipped away.

usage: compose_figure.py <out.svg> <cols> <panel.svg> [panel.svg ...]
"""
import pathlib
import re
import sys

OUT = pathlib.Path(sys.argv[1])
COLS = int(sys.argv[2])
CHILDREN = [pathlib.Path(p) for p in sys.argv[3:]]

CELL_W, CELL_H = 3100, 2440       # user units per cell; letters sit in the band
GUT = 70                          # gutter between cells
LETTER_PT = 150                   # panel-letter size in the same user units


def load(path, tag):
    s = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'<svg\b[^>]*viewBox="([^"]+)"[^>]*>', s)
    vb = re.split(r"[ ,]+", m.group(1).strip())
    vw, vh = float(vb[2]), float(vb[3])
    body = s[m.end():s.rindex("</svg>")]
    for oid in set(re.findall(r'\bid="([^"]+)"', body)):
        body = body.replace('id="%s"' % oid, 'id="%s_%s"' % (tag, oid))
        body = body.replace("url(#%s)" % oid, "url(#%s_%s)" % (tag, oid))
    return vw, vh, body


rows = (len(CHILDREN) + COLS - 1) // COLS
W = COLS * CELL_W + (COLS - 1) * GUT
H = rows * CELL_H + (rows - 1) * GUT

parts = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<svg xmlns="http://www.w3.org/2000/svg" '
    'xmlns:xlink="http://www.w3.org/1999/xlink" '
    'xmlns:olab="http://www.originlab.com/namespaces/olab" '
    'viewBox="0 0 %d %d" width="183mm" height="%.2fmm">' % (W, H, 183.0 * H / W),
    '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H),
]

for i, path in enumerate(CHILDREN):
    tag = "p%d" % i
    vw, vh, body = load(path, tag)
    x = (i % COLS) * (CELL_W + GUT)
    y = (i // COLS) * (CELL_H + GUT)
    parts.append(
        '<text x="%d" y="%d" font-family="Arial" font-size="%d" font-weight="700" '
        'fill="#000000">%s</text>' % (x + 40, y + LETTER_PT, LETTER_PT,
                                      chr(ord("a") + i)))
    parts.append(
        '<svg x="%d" y="%d" width="%d" height="%d" viewBox="0 0 %g %g" '
        'preserveAspectRatio="xMidYMid meet">'
        % (x, y + int(LETTER_PT * 0.45), CELL_W, CELL_H - int(LETTER_PT * 0.45),
           vw, vh))
    parts.append(body)
    parts.append("</svg>")

parts.append("</svg>")
OUT.write_text("\n".join(parts), encoding="utf-8")
print("%s  <- %d panels, %d cols, 183 mm wide" % (OUT, len(CHILDREN), COLS))
