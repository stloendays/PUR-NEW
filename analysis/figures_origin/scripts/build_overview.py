"""Rebuild a contact sheet from a panel directory.

The overview is a rendered PNG, so it carries panel text as glyphs rather than
as strings. A grep-based label audit cannot see it, and it therefore goes stale
silently whenever the panels are relabelled. Regenerate it from the SVGs
whenever a panel changes.

usage: build_overview.py <panels_dir> <out.png> [columns]
"""
import pathlib
import re
import subprocess
import sys

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

panels_dir = pathlib.Path(sys.argv[1]).resolve()
out_png = pathlib.Path(sys.argv[2]).resolve()
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4


def sort_key(p):
    m = re.match(r"Fig(\d+)([A-Z])", p.stem)
    return (int(m.group(1)), m.group(2)) if m else (99, p.stem)


svgs = sorted(panels_dir.glob("*.svg"), key=sort_key)
if not svgs:
    sys.exit("no SVG panels in %s" % panels_dir)

cells = "\n".join(
    '<figure><figcaption>%s</figcaption><img src="%s"></figure>'
    % (p.stem, p.name)
    for p in svgs
)
html = """<!doctype html><meta charset="utf-8">
<style>
 body{margin:0;background:#fff;font:13px Arial,Helvetica,sans-serif;color:#111}
 .g{display:grid;grid-template-columns:repeat(%d,1fr);gap:10px;padding:10px}
 figure{margin:0}
 img{width:100%%;display:block;border:1px solid #ccc}
 figcaption{padding:2px;font-size:15px;font-weight:700}
</style>
<div class="g">
%s
</div>
""" % (cols, cells)

tmp = panels_dir / "_overview_tmp.html"
tmp.write_text(html, encoding="utf-8")
rows = (len(svgs) + cols - 1) // cols
try:
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=1", "--default-background-color=FFFFFFFF",
         "--window-size=%d,%d" % (700 * cols, 560 * rows + 40),
         "--screenshot=%s" % out_png, tmp.as_uri()],
        check=True, capture_output=True)
finally:
    tmp.unlink(missing_ok=True)

print("%s  <- %d panels, %d cols" % (out_png, len(svgs), cols))
