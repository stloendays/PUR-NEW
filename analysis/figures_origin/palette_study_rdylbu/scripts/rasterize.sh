#!/usr/bin/env bash
# Rasterize a cleaned Origin SVG to PNG with headless Chrome.
# The SVG has already had the phantom text hairlines removed by export_figure;
# re-rasterizing from it is the only way to get a PNG without them.
# usage: rasterize.sh <file.svg> [scale]
set -e
SVG="$1"
SCALE="${2:-2}"
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
OUT="${SVG%.svg}.png"

read W H < <("/d/Tools/origin-mcp/.venv/Scripts/python.exe" - "$SVG" <<'PY'
import re, sys, math
s = open(sys.argv[1], encoding='utf-8', errors='ignore').read(4000)
def dim(tag):
    m = re.search(tag + r'="([0-9.]+)', s)
    return float(m.group(1)) if m else None
w, h = dim('width'), dim('height')
if w is None or h is None:
    m = re.search(r'viewBox="[-0-9.]+ [-0-9.]+ ([0-9.]+) ([0-9.]+)', s)
    w, h = float(m.group(1)), float(m.group(2))
print(int(math.ceil(w)), int(math.ceil(h)))
PY
)

WIN_SVG=$(cygpath -w "$SVG" | sed 's|\\|/|g')
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor="$SCALE" --default-background-color=FFFFFFFF \
  --window-size="$W,$H" --screenshot="$(cygpath -w "$OUT")" \
  "file:///$WIN_SVG" >/dev/null 2>&1
echo "$OUT  ${W}x${H} @${SCALE}x"
