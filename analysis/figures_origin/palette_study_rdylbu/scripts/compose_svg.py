# Assemble several Origin SVG exports into one multi-panel figure, keeping vectors.
# Each child is nested in its own <svg> viewport; ids are namespaced to avoid collisions.
import os
import re
import sys

OUT = sys.argv[1]
COLS = int(sys.argv[2])
CHILDREN = sys.argv[3:]

CELL_W, CELL_H = 3100, 2380          # user units per panel cell
GUT = 60                             # gutter between cells


def load(path, tag):
    s = open(path, encoding="utf-8", errors="ignore").read()
    m = re.search(r'<svg\b[^>]*viewBox="([^"]+)"[^>]*>', s)
    vb = re.split(r"[ ,]+", m.group(1).strip())
    vw, vh = float(vb[2]), float(vb[3])
    body = s[m.end():s.rindex("</svg>")]
    # namespace every id and its url(#...) references
    for oid in set(re.findall(r'\bid="([^"]+)"', body)):
        body = body.replace('id="%s"' % oid, 'id="%s_%s"' % (tag, oid))
        body = body.replace('url(#%s)' % oid, 'url(#%s_%s)' % (tag, oid))
    return vw, vh, body


rows = (len(CHILDREN) + COLS - 1) // COLS
W = COLS * CELL_W + (COLS - 1) * GUT
H = rows * CELL_H + (rows - 1) * GUT

parts = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<svg xmlns="http://www.w3.org/2000/svg" '
         'xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:olab="http://www.originlab.com/namespaces/olab" '
         'viewBox="0 0 %d %d" width="183mm" height="%.2fmm">' % (W, H, 183.0 * H / W),
         '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H)]

for i, path in enumerate(CHILDREN):
    tag = "p%d" % i
    vw, vh, body = load(path, tag)
    x = (i % COLS) * (CELL_W + GUT)
    y = (i // COLS) * (CELL_H + GUT)
    parts.append('<svg x="%d" y="%d" width="%d" height="%d" viewBox="0 0 %g %g" '
                 'preserveAspectRatio="xMidYMid meet">' % (x, y, CELL_W, CELL_H, vw, vh))
    parts.append(body)
    parts.append('</svg>')

parts.append('</svg>')
open(OUT, "w", encoding="utf-8").write("\n".join(parts))
print("wrote %s  (%d panels, %dx%d units, 183 mm wide)" % (OUT, len(CHILDREN), W, H))
