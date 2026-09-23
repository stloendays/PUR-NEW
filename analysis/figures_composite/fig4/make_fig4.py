"""Figure 4. Scientific decision quality depends on rule content and rule order.

a  Recovery of the evidence-supported intervention family, per arm, with
   two-sided 95 % Wilson intervals.
b  Hypothesis discrimination of the frozen selected experiment. Every run is a
   dot; the bar is the arm mean. Read straight from each run's
   recommendation.json, and checked against rule_layer_ablation.json.
c  Selection of the matched-window 120 C hold measurement, with Wilson
   intervals. Withholding the score leaves this intact; inverting order does not.
d  The order-inverted arm: the critique found the defect and the selection
   committed anyway.

Panel d is deliberately not the old drawing. The three quantities are three
different outcomes counted over the same ten runs, not stages of one process,
so joining them with a line implied a trajectory that does not exist. They are
three separate rows here.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig4.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import figdata as D
import layout as L
from matplotlib.patches import Rectangle
from style import DARK_B, DARK_G, GRID, INK, LINE, MID, OS, PALE_B, RED, Page

HERE = os.path.dirname(os.path.abspath(__file__))

ARMS = ["full", "voi_withheld", "order_inverted"]
NAME = {"full": "rule-\ncomplete", "voi_withheld": "VOI\nwithheld",
        "order_inverted": "order\ninverted"}
COL = {"full": DARK_G, "voi_withheld": OS, "order_inverted": DARK_B}
JSON_KEY = {"full": "full", "voi_withheld": "ablated",
            "order_inverted": "rule_order_inverted"}


def spread(values, width=0.30):
    """x offsets that fan tied values out symmetrically, like a small beeswarm."""
    values = np.asarray(values)
    x = np.zeros(len(values))
    for v in np.unique(values):
        idx = np.where(values == v)[0]
        k = len(idx)
        if k > 1:
            x[idx] = np.linspace(-width, width, k)
    return x


def proportion_panel(ax, counts, ylabel):
    for i, arm in enumerate(ARMS):
        k, n = counts[arm]
        lo, hi = D.wilson(k, n)
        p = k / n
        ax.plot([i, i], [lo, hi], lw=1.0, color=COL[arm], zorder=3,
                solid_capstyle="butt")
        for yy in (lo, hi):
            ax.plot([i - .09, i + .09], [yy, yy], lw=1.0, color=COL[arm], zorder=3)
        ax.scatter(i, p, s=34, fc=COL[arm], ec="white", lw=0.7, zorder=4)
        ax.text(i + 0.16, p, "%d/%d" % (k, n), fontsize=5.6, color=INK,
                ha="left", va="center", fontweight="bold")
    ax.set_xticks(range(3), [NAME[a] for a in ARMS], fontsize=5.4)
    ax.set_xlim(-.55, 2.7)
    ax.set_ylim(-0.04, 1.06)
    ax.set_yticks([0, .25, .5, .75, 1.0], ["0", "0.25", "0.5", "0.75", "1"])
    ax.set_ylabel(ylabel)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)


def main():
    runs = D.ablation_runs()
    js = D.ablation_summary()["arms"]
    by = {a: runs[runs.arm == a] for a in ARMS}

    # the per-run records must reproduce the frozen aggregate before plotting
    for a in ARMS:
        agg = js[JSON_KEY[a]]["hypothesis_discrimination_of_selection"]
        assert abs(by[a].discrimination.mean() - agg["mean"]) < 1e-4, a
        assert (by[a].discrimination == 0).sum() == agg["n_with_zero_discrimination"], a

    pg = Page(183.0, 88.0)

    # ---- a  family recovery ---------------------------------------------
    ax = pg.ax(15, 46, 42, 34)
    proportion_panel(ax, {a: (int(by[a].supported.sum()), len(by[a])) for a in ARMS},
                     "supported-family recovery")
    ax.text(0.98, 0.98, "error bars: 95% Wilson", transform=ax.transAxes,
            fontsize=5.0, color=MID, ha="right", va="top")
    pg.letter("a", 3, 86.5)

    # ---- b  discrimination, every run ------------------------------------
    ax = pg.ax(75, 46, 42, 34)
    for i, a in enumerate(ARMS):
        d = by[a].discrimination.to_numpy()
        ax.bar(i, d.mean(), width=.62, color=COL[a], alpha=.22, zorder=2)
        ax.plot([i - .31, i + .31], [d.mean(), d.mean()], lw=1.1,
                color=COL[a], zorder=3)
        ax.scatter(i + spread(d), d, s=10, fc=COL[a], ec="white", lw=0.4,
                   zorder=4)
        z = int((d == 0).sum())
        ax.text(i, 0.80, "mean %.3f" % d.mean(), fontsize=5.2, color=INK,
                ha="center", va="bottom", fontweight="bold")
        ax.text(i, 0.745, "%d/%d at zero" % (z, len(d)), fontsize=5.0,
                color=MID, ha="center", va="bottom")
    ax.set_xticks(range(3), [NAME[a] for a in ARMS], fontsize=5.4)
    ax.set_xlim(-.55, 2.55)
    ax.set_ylim(-0.05, 0.92)
    ax.set_yticks([0, 1 / 3, 2 / 3], ["0", "1/3", "2/3"])
    ax.set_ylabel("hypothesis discrimination\nof the selected experiment")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    pg.letter("b", 63, 86.5)

    # ---- c  measurement choice ------------------------------------------
    ax = pg.ax(135, 46, 42, 34)
    proportion_panel(ax, {a: (int((by[a].measurement == "M-HOLD-120").sum()),
                              len(by[a])) for a in ARMS},
                     "matched-window 120 \u00b0C hold\nselected")
    pg.letter("c", 123, 86.5)

    # ---- d  critique vs commitment, order-inverted arm --------------------
    ic = js["rule_order_inverted"]["internal_critique"]
    n = int(ic["of_completed"])
    zero = int(js["rule_order_inverted"]["hypothesis_discrimination_of_selection"]
               ["n_with_zero_discrimination"])
    rows = [
        ("critique raised a high-severity objection",
         int(ic["high_severity_objection"]), DARK_B),
        ("robustness check recommended changing the experiment",
         int(ic["robustness_said_change_experiment"]), OS),
        ("selection still committed to a zero-discrimination experiment",
         zero, RED),
    ]
    # Compact on purpose: the first build left ~8 mm between the title and
    # the first bar and more below the last, which is exactly the in-figure
    # whitespace this house style is trying to remove.
    cv = pg.canvas(3.0, 2.5, 177.0, 28.0)
    cv.text(0.0, 27.6, "order-inverted arm, %d runs — three separate outcomes "
            "counted over the same runs; each segment is one run" % n,
            fontsize=5.8, color=INK, ha="left", va="top", fontweight="bold")
    track_x, track_w, h = 86.0, 74.0, 4.6
    for r, (label, k, col) in enumerate(rows):
        y = 16.6 - r * 6.9
        cv.text(track_x - 3.0, y + h / 2, label, fontsize=5.8, color=INK,
                ha="right", va="center")
        cv.add_patch(Rectangle((track_x, y), track_w, h, fc="#F2F2F2",
                               ec="none", zorder=1))
        cv.add_patch(Rectangle((track_x, y), track_w * k / n, h, fc=col,
                               ec="none", zorder=2))
        for t in range(1, n):                       # one tick per run
            xx = track_x + track_w * t / n
            cv.plot([xx, xx], [y, y + h], lw=0.5, color="white", zorder=3)
        cv.text(track_x + track_w + 2.4, y + h / 2, "%d/%d" % (k, n),
                fontsize=6.2, color=col if col == RED else INK, ha="left",
                va="center", fontweight="bold")
    pg.letter("d", 3, 33.5)

    L.audit(pg.fig)
    pg.save(HERE, "Fig4")


if __name__ == "__main__":
    main()
