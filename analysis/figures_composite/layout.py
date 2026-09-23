"""House legend boxes, and a check that nothing in the figure overlaps.

A legend frame is allowed and often better than direct labels once a panel
carries more than four or five series. What is not allowed is a legend sitting
on the data or on another label, so `audit` measures it instead of trusting the
eye: it draws the figure, collects every text and legend bounding box, and
reports any pair that genuinely intersects.

Call `audit(pg.fig)` right before `pg.save(...)`. It prints what it found and
returns the list, so a build can be made to fail on a regression.
"""
import itertools

from matplotlib.text import Text

INK, MID, LINE = "#1B1B1B", "#6B6F76", "#D6D6D6"

# Ticks and their axis label are laid out by matplotlib and are allowed to sit
# close; only real collisions between things we placed are interesting.
MIN_FRAC = 0.18            # ignore an intersection smaller than this share of
                           # the smaller box -- antialiasing and descenders touch


def legend(ax, handles=None, labels=None, loc="lower right", ncol=1,
           fontsize=5.4, title=None, frame=True, **kw):
    """A legend in the house style: hairline frame, white fill, tight padding."""
    kw.setdefault("handlelength", 1.5)
    kw.setdefault("handletextpad", 0.45)
    kw.setdefault("labelspacing", 0.32)
    kw.setdefault("columnspacing", 0.9)
    kw.setdefault("borderpad", 0.42)
    kw.setdefault("borderaxespad", 0.5)
    lg = (ax.legend(handles, labels, loc=loc, ncol=ncol, fontsize=fontsize, **kw)
          if handles is not None else
          ax.legend(loc=loc, ncol=ncol, fontsize=fontsize, **kw))
    fr = lg.get_frame()
    fr.set_linewidth(0.5 if frame else 0.0)
    fr.set_edgecolor(LINE if frame else "none")
    fr.set_facecolor("white")
    fr.set_alpha(1.0 if frame else 0.0)
    lg.set_zorder(6)
    if title:
        lg.set_title(title, prop=dict(size=fontsize, weight="bold"))
        lg.get_title().set_color(INK)
    for t in lg.get_texts():
        t.set_color(INK)
    return lg


def _boxes(fig):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    out = []
    for ax in fig.axes:
        for t in ax.texts:
            if t.get_text().strip():
                out.append(("text:%s" % _short(t), t.get_window_extent(r)))
        lg = ax.get_legend()
        if lg is not None:
            out.append(("legend", lg.get_window_extent(r)))
    for t in fig.texts:
        if isinstance(t, Text) and t.get_text().strip():
            out.append(("figtext:%s" % _short(t), t.get_window_extent(r)))
    return out


def _short(t, n=28):
    s = " ".join(t.get_text().split())
    return s if len(s) <= n else s[:n - 1] + "…"


def audit(fig, min_frac=MIN_FRAC, verbose=True):
    """Report text/legend boxes that intersect. Returns a list of collisions."""
    boxes = _boxes(fig)
    hits = []
    for (na, ba), (nb, bb) in itertools.combinations(boxes, 2):
        x0, x1 = max(ba.x0, bb.x0), min(ba.x1, bb.x1)
        y0, y1 = max(ba.y0, bb.y0), min(ba.y1, bb.y1)
        if x1 <= x0 or y1 <= y0:
            continue
        inter = (x1 - x0) * (y1 - y0)
        smaller = min(ba.width * ba.height, bb.width * bb.height)
        if smaller <= 0:
            continue
        frac = inter / smaller
        if frac >= min_frac:
            hits.append((frac, na, nb))
    hits.sort(reverse=True)
    if verbose:
        if hits:
            print("  OVERLAP  %d pair(s):" % len(hits))
            for frac, na, nb in hits:
                print("    %3.0f%%  %-34s  x  %s" % (100 * frac, na, nb))
        else:
            print("  overlap audit clean (%d boxes)" % len(boxes))
    return hits
