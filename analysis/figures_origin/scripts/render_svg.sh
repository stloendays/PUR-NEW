#!/usr/bin/env bash
# 把清理过的 SVG 交给 Chrome 光栅化，而不是在 PNG 上动手术。
# 文字框线只存在于矢量层，删掉之后重新渲染，字形完好无损。
set -e
B="$1"; CHROME="$2"
for f in "$B"/final/Fig*.svg; do
  n=$(basename "$f" .svg)
  read w h < <("/d/Tools/pur_bridge_env/Scripts/python.exe" -c "
import re,sys,math
s=open(r'''$f''',encoding='utf-8').read(3000)
w=float(re.search(r'width=\"([\d.]+)px\"',s).group(1))
h=float(re.search(r'height=\"([\d.]+)px\"',s).group(1))
print(math.ceil(w), math.ceil(h))")
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --default-background-color=FFFFFFFF --window-size=$w,$h \
    --screenshot="$B/png2/$n.png" "file:///$B/final/$n.svg" >/dev/null 2>&1
  echo "$n ${w}x${h}"
done
