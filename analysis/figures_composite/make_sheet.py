"""Compose the individual figure SVGs into one sheet, then render PDF and PNG.

Each figure stays a nested <svg> with its own coordinate system, so the sheet
is still vector and still carries live text -- it is a composition, not a
screenshot of one. Figures may be scaled down individually; a contact sheet
does not have to show everything at submission size.

Two things this has to get right:

  * every child's ids must be namespaced. Matplotlib writes <defs> full of
    glyph paths and clip paths referenced by xlink:href and url(), and the
    names repeat across files. Without a per-child prefix the later figures
    render with the earlier ones' glyphs and clips.
  * the parent must declare xmlns:xlink, or the href references do not resolve
    and the whole sheet silently loses its text.

PDF comes from headless Chrome with an @page box the exact size of the sheet,
so the PDF is the sheet rather than the sheet letterboxed onto A4.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_sheet.py
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PT_MM = 25.4 / 72.0

GAP, PAD, TOP = 9.0, 8.0, 17.0      # between figures, around the sheet, header
CAP = 4.6                           # caption strip above each figure

# (file, caption, scale). Scale is per figure: the column figure is already
# narrow, so it does not need cutting down as far as the 183 mm ones.
COLUMNS = [
    [("fig1/Fig1.svg", "Fig 1   Formulation chemistry and the reaction", 0.78),
     ("fig_structure/Fig_structure.svg",
      "Fig S   Hard-segment association, modelled from a generated CIF", 0.78),
     ("fig_hold/Fig_hold.svg",
      "Fig S   120 \u00b0C thermal hold against the dilution null", 0.78)],
    [("fig_arrhenius/Fig_arrhenius.svg",
      "Fig S   Viscosity-temperature master panel", 0.78),
     ("fig_column/Fig_column.svg",
      "Fig S   Seven realizations, one property, one column", 0.78)],
]


def read_svg(path):
    """Return (width_mm, height_mm, viewbox, body) for a matplotlib SVG."""
    s = open(path, encoding="utf-8").read()
    m = re.search(r"<svg\b[^>]*>", s)
    head = m.group(0)
    w = float(re.search(r'width="([0-9.]+)pt"', head).group(1))
    h = float(re.search(r'height="([0-9.]+)pt"', head).group(1))
    vb = re.search(r'viewBox="([^"]+)"', head).group(1)
    body = s[m.end():s.rindex("</svg>")]
    return w * PT_MM, h * PT_MM, vb, body


def namespace(body, tag):
    """Prefix every id in the child, and every reference to one."""
    ids = set(re.findall(r'\bid="([^"]+)"', body))
    for oid in sorted(ids, key=len, reverse=True):
        new = "%s-%s" % (tag, oid)
        body = body.replace('id="%s"' % oid, 'id="%s"' % new)
        body = body.replace("url(#%s)" % oid, "url(#%s)" % new)
        body = body.replace('xlink:href="#%s"' % oid, 'xlink:href="#%s"' % new)
        body = body.replace('href="#%s"' % oid, 'href="#%s"' % new)
    return body


def main():
    cols = []
    for spec in COLUMNS:
        items, y = [], 0.0
        for path, caption, scale in spec:
            w, h, vb, body = read_svg(os.path.join(HERE, path))
            items.append(dict(path=path, caption=caption, vb=vb, body=body,
                              w=w * scale, h=h * scale, y=y, scale=scale))
            y += CAP + h * scale + GAP
        cols.append(dict(items=items, w=max(i["w"] for i in items),
                         h=y - GAP))

    x, parts = PAD, []
    for ci, col in enumerate(cols):
        col["x"] = x
        x += col["w"] + GAP + 3.0
    sheet_w = x - GAP - 3.0 + PAD
    sheet_h = TOP + max(c["h"] for c in cols) + PAD

    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'width="%.2fmm" height="%.2fmm" viewBox="0 0 %.2f %.2f">'
        % (sheet_w, sheet_h, sheet_w, sheet_h))
    parts.append('<rect x="0" y="0" width="%.2f" height="%.2f" fill="#ffffff"/>'
                 % (sheet_w, sheet_h))
    parts.append('<text x="%.2f" y="%.2f" font-family="Arial" font-size="5.0" '
                 'font-weight="700" fill="#1B1B1B">PUR-NEW composite figures'
                 '</text>' % (PAD, 7.0))
    parts.append('<text x="%.2f" y="%.2f" font-family="Arial" font-size="3.0" '
                 'fill="#6B6F76">Each panel is the same vector artwork as its '
                 'own PDF and SVG; scales differ on this sheet only.</text>'
                 % (PAD, 11.6))

    n = 0
    for col in cols:
        for it in col["items"]:
            yy = TOP + it["y"]
            parts.append('<text x="%.2f" y="%.2f" font-family="Arial" '
                         'font-size="3.4" font-weight="700" fill="#1B1B1B">%s'
                         '</text>' % (col["x"], yy + 3.0, it["caption"]))
            parts.append('<svg x="%.2f" y="%.2f" width="%.2f" height="%.2f" '
                         'viewBox="%s" preserveAspectRatio="xMinYMin meet">'
                         % (col["x"], yy + CAP, it["w"], it["h"], it["vb"]))
            parts.append(namespace(it["body"], "f%d" % n))
            parts.append("</svg>")
            n += 1
    parts.append("</svg>")

    svg_path = os.path.join(HERE, "Sheet_all_figures.svg")
    open(svg_path, "w", encoding="utf-8").write("\n".join(parts))
    print("wrote Sheet_all_figures.svg   %.1f x %.1f mm, %d figures"
          % (sheet_w, sheet_h, n))

    html = os.path.join(HERE, "_sheet_tmp.html")
    open(html, "w", encoding="utf-8").write(
        "<!doctype html><meta charset='utf-8'><style>"
        "@page{size:%.2fmm %.2fmm;margin:0}"
        "html,body{margin:0;padding:0;background:#fff}svg{display:block}"
        "</style>%s" % (sheet_w, sheet_h, "\n".join(parts)))
    url = "file:///" + html.replace("\\", "/")
    # --window-size is CSS pixels at 96 dpi, not device pixels. Sizing it from
    # the target dpi makes the window far larger than the sheet, and the figure
    # renders into a corner of it at about a third of the intended scale.
    # Size the window in CSS px and raise resolution with the scale factor.
    css = lambda mm: max(1, round(mm * 96.0 / 25.4))
    SCALE = 3                                               # -> 288 dpi
    jobs = [
        (["--print-to-pdf=%s" % os.path.join(HERE, "Sheet_all_figures.pdf"),
          "--no-pdf-header-footer"], "pdf"),
        (["--screenshot=%s" % os.path.join(HERE, "Sheet_all_figures.png"),
          "--window-size=%d,%d" % (css(sheet_w), css(sheet_h)),
          "--force-device-scale-factor=%d" % SCALE], "png"),
    ]
    try:
        for flags, ext in jobs:
            out = os.path.join(HERE, "Sheet_all_figures.%s" % ext)
            if os.path.exists(out):
                os.remove(out)
            r = subprocess.run(
                [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                 "--default-background-color=FFFFFFFF"] + flags + [url],
                check=False, capture_output=True, timeout=300)
            if os.path.exists(out):
                print("  %-3s ok   %.0f kB" % (ext, os.path.getsize(out) / 1024))
            else:
                print("  %-3s FAILED  %s" % (ext, r.stderr.decode("utf-8", "ignore")[-300:]))
    finally:
        if os.path.exists(html):
            os.remove(html)


if __name__ == "__main__":
    main()
