#!/usr/bin/env python
"""Remove the spurious text-frame rule this Origin build draws along every text object.

Origin emits, right after each <text>, an axis-aligned <path> at the text's cap height
(vertical for rotated titles). The SVG carries the exact geometry, so the SVG and the
matching PNG can both be cleaned deterministically instead of guessed from pixels.
"""
from __future__ import annotations

import re
import sys

from PIL import Image

RULE = re.compile(
    r"(<text\b[^>]*>.*?</text>\s*)"
    r"<path d=\"M (-?[\d.]+),(-?[\d.]+) L (-?[\d.]+),(-?[\d.]+)\""
    r"[^>]*?stroke-width:\s*([\d.]+)[^>]*?/>",
    re.S,
)
VIEWBOX = re.compile(r'viewBox="([\d.,\s-]+)"')
FSIZE = re.compile(r'font-size="([\d.]+)"')


def clean(svg_path: str, png_path: str | None = None) -> int:
    src = open(svg_path, encoding="utf-8").read()
    rules: list[tuple[float, float, float, float, float]] = []

    def drop(m):
        head = m.group(1)
        x1, y1, x2, y2, sw = (float(m.group(i)) for i in (2, 3, 4, 5, 6))
        horizontal, vertical = abs(y1 - y2) < 0.5, abs(x1 - x2) < 0.5
        if not (horizontal or vertical):
            return m.group(0)
        # A real frame rule is at most one line-height long in its thin direction and
        # roughly as long as the text it decorates; anything longer is a genuine line.
        fs = FSIZE.search(head)
        span = abs(x2 - x1) if horizontal else abs(y2 - y1)
        if fs and span > 60 * float(fs.group(1)):
            return m.group(0)
        rules.append((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2), sw))
        return head

    out, n = RULE.subn(drop, src)
    open(svg_path, "w", encoding="utf-8").write(out)

    if png_path and rules:
        vb = [float(v) for v in re.split(r"[,\s]+", VIEWBOX.search(src).group(1).strip())]
        im = Image.open(png_path).convert("RGB")
        sx, sy = im.width / vb[2], im.height / vb[3]
        px = im.load()
        for x1, y1, x2, y2, sw in rules:
            # The raster is offset from the SVG coordinates by a few pixels, so search a
            # band around the nominal position and erase only rows that are actually the
            # rule: a near-continuous dark run spanning most of its length.
            # 端点要多留几像素：抗锯齿会让线头拖出标称范围，只擦到标称端点
            # 会在文字两侧留下两个小勾。
            a, b = int(x1 * sx) - 7, int(x2 * sx) + 7
            c, e = int(y1 * sy) - 7, int(y2 * sy) + 7
            horizontal = (b - a) >= (e - c)
            span = (b - a) if horizontal else (e - c)
            lo, hi = (c - 9, e + 9) if horizontal else (a - 9, b + 9)
            for k in range(lo, hi + 1):
                if horizontal:
                    line = [(x, k) for x in range(a, b + 1)]
                else:
                    line = [(k, y) for y in range(c, e + 1)]
                line = [(x, y) for x, y in line if 0 <= x < im.width and 0 <= y < im.height]
                if not line:
                    continue
                dark = sum(1 for x, y in line if sum(px[x, y]) < 330)
                if dark >= 0.6 * span:
                    for x, y in line:
                        px[x, y] = (255, 255, 255)
        im.save(png_path)
    return len(rules)


if __name__ == "__main__":
    print(f"{sys.argv[1]}: removed {clean(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)} text rules")
