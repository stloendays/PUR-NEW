"""Thermal-hold trajectory at 120 C, and the null model it is judged against.

a  Trajectories normalized to the 15 min point. The matched 15-60 min window
   is shaded, because that is the window every drift number in the manuscript
   is computed over -- E1 and E5 ran to 90 min and the validation repeats only
   to 60, so a first-to-last comparison would not be like for like.
b  The matched drifts, against the proportional-dilution null. The null is what
   the drift would be if the resin did nothing but dilute the reactive core.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig_hold.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import figdata as D
import layout as L
from style import DARK_B, DARK_G, FE, GRID, INK, MID, OS, PALE_B, RED, Page

HERE = os.path.dirname(os.path.abspath(__file__))

COL = {"E5 R02": RED, "E1 R01": OS, "F1 repeat_1": DARK_G, "F1 repeat_2": FE}
LABEL = {"E5 R02": "E5", "E1 R01": "E1",
         "F1 repeat_1": "F1 repeat 1", "F1 repeat_2": "F1 repeat 2"}
ORDER = ["E5 R02", "E1 R01", "F1 repeat_1", "F1 repeat_2"]


def main():
    h = D.holds()
    dr = D.hold_drift().set_index("series")
    v = D.validation_drift()
    t0, t1 = D.HOLD_WINDOW

    pg = Page(183.0, 64.0)

    # ---- a  normalized trajectories --------------------------------------
    ax = pg.ax(13, 11, 70, 45)
    ax.axvspan(t0, t1, color=PALE_B, alpha=.38, lw=0, zorder=0)
    ax.text((t0 + t1) / 2.0, 0.945, "matched window", fontsize=5.2, color=DARK_B,
            ha="center", va="bottom")
    ax.axhline(1.0, color=GRID, lw=0.6, zorder=1)

    # A legend, not end labels: the two F1 repeats finish 3 % apart and their
    # labels collided, which the overlap audit caught at 40 %.
    handles = []
    for s in ORDER:
        g = h[h.series == s].sort_values("time_min")
        y = g.viscosity_reported.to_numpy() / g.viscosity_reported.iloc[0]
        ln, = ax.plot(g.time_min, y, lw=1.0, color=COL[s], zorder=3,
                      label=LABEL[s])
        ax.scatter(g.time_min, y, s=11, fc="white", ec=COL[s], lw=0.8, zorder=4)
        handles.append(ln)
    L.legend(ax, handles, [h_.get_label() for h_ in handles], loc="upper left")

    ax.set_xlim(10, 104)
    ax.set_ylim(0.93, 1.99)
    ax.set_xticks([15, 30, 45, 60, 75, 90])
    ax.set_xlabel("hold time at 120 \u00b0C  (min)")
    ax.set_ylabel("viscosity / viscosity at 15 min")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    pg.letter("a", 3, 62)

    # ---- b  matched drift against the dilution null ----------------------
    ax = pg.ax(100, 11, 76, 45)
    vals = [dr.loc[s, "drift_pct"] for s in ORDER]
    ax.barh(range(4), vals, height=.62, color=[COL[s] for s in ORDER], zorder=3)
    # Value labels always sit to the right of zero. Hanging a negative one off
    # the left end of its bar runs it into the category label.
    for i, val in enumerate(vals):
        ax.text(max(val, 0.0) + 1.0, i, "%+.2f%%" % val,
                fontsize=5.6, color=INK, va="center", ha="left",
                fontweight="bold", zorder=5,
                bbox=dict(boxstyle="square,pad=0.12", fc="white", ec="none"))

    ax.axvline(v["null"], color=RED, lw=0.8, ls=(0, (2.6, 1.6)), zorder=4)
    ax.text(v["null"] + 1.2, 4.18,
            "proportional-dilution null %.2f%%" % v["null"], fontsize=5.4,
            color=RED, ha="left", va="center")
    ax.text(v["null"] + 1.2, 3.72,
            "= E1 %.2f%% \u00d7 %.3f reactive-core fraction"
            % (v["e1"], v["core_fraction"]), fontsize=5.0, color=MID,
            ha="left", va="center")

    ax.set_yticks(range(4), [LABEL[s] for s in ORDER], fontsize=6.0)
    ax.set_xlim(-4, 58)
    ax.set_ylim(-0.6, 4.5)
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    ax.set_xlabel("viscosity change, %d\u2013%d min  (%%)" % (t0, t1), labelpad=2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)

    # the adjudication, placed beside the short bars rather than on the long
    # E5 one, which is where it landed first
    ax.text(24.0, 3.02,
            "F1 mean |drift| %.2f%%\nfalls below the null, so\ndilution alone "
            "does not explain\nthe stabilization." % v["measured"],
            fontsize=5.4, color=INK, ha="left", va="top", linespacing=1.6)
    pg.letter("b", 90, 62)

    L.audit(pg.fig)
    pg.save(HERE, "Fig_hold")


if __name__ == "__main__":
    main()
