"""One property, seven realizations, stacked in a single column.

Every panel carries the same axes and the same seven fitted curves. Six are
drawn in pale grey as a backdrop and one is highlighted, so a reader sees at a
glance where that realization sits in the family without moving their eye to a
legend. The backdrop also fills the panel, which a lone curve on a shared
log axis would not.

Labels live in a left gutter rather than inside the panels. An earlier build
placed them in the top-right corner on the assumption that descending curves
leave it empty; that is true for the low-viscosity realizations and false for
E2 R03 and E2 R02, where the text landed on the data.

Panels butt against one another and only the bottom one carries tick labels;
the shared axis is what makes the comparison direct.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig_column.py
"""
import os
import sys

import numpy as np
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import figdata as D
import layout as L
from style import DARK_B, DARK_G, FE, GRID, INK, MID, OS, PALE_B, RED, RU, Page

HERE = os.path.dirname(os.path.abspath(__file__))

COL = {
    "E1 +P": RED,
    "E1 R01 \u00b7 1 d": DARK_G,
    "E2 R01": RU,
    "E2 R02": DARK_B,
    "E2 R03": OS,
    "E2 R02 \u00b7 1 d": DARK_B,
    "E3 R03": FE,
}
ORDER = list(COL)
BACK = "#DEDEDE"

X0, X1 = 77.0, 133.0
Y0, Y1 = 450.0, 34000.0
GUT_X, GUT_W = 2.0, 33.0                            # label gutter
LEFT, WIDTH = 40.0, 74.0                            # plot column
BOT, PH = 12.5, 18.4
DEV_HALF = 5.0                                      # kJ/mol at the gutter bar ends


def curve(f, t_c):
    """Fitted viscosity at temperatures t_c, from the realization's Arrhenius fit."""
    return np.exp(f.lnA + f.slope / (t_c + 273.15))


def main():
    sw, fits = D.sweeps(), D.arrhenius()
    mu = D.primary(fits).E_eta.mean()

    n = len(ORDER)
    pg = Page(120.0, BOT + n * PH + 11.0)
    tt = np.linspace(X0, X1, 120)

    for k, rid in enumerate(ORDER):
        y = BOT + (n - 1 - k) * PH                  # first realization at the top
        f = fits[fits.rid == rid].iloc[0]
        g = sw[sw.rid == rid].sort_values("temperature_c")
        c = COL[rid]

        # ---- plot ---------------------------------------------------------
        ax = pg.ax(LEFT, y, WIDTH, PH)
        for other in ORDER:                         # the family, as context
            ax.plot(tt, curve(fits[fits.rid == other].iloc[0], tt),
                    lw=0.7, color=BACK, zorder=1)
        ax.plot(tt, curve(f, tt), lw=1.1, color=c, zorder=3)
        ax.scatter(g.temperature_c, g.viscosity_reported, s=9, fc="white",
                   ec=c, lw=0.8, zorder=4)

        ax.set_yscale("log")
        ax.set_xlim(X0, X1)
        ax.set_ylim(Y0, Y1)
        ax.set_yticks([1000, 10000])
        ax.set_yticklabels(["10$^3$", "10$^4$"], fontsize=5.6)
        ax.tick_params(axis="y", length=2.0, width=0.5)
        ax.minorticks_off()
        ax.set_xticks([80, 90, 100, 110, 120, 130])
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        if k == n - 1:
            ax.set_xlabel("temperature  (\u00b0C)", labelpad=2)
        else:
            ax.set_xticklabels([])
            ax.tick_params(axis="x", length=1.6)

        # ---- gutter: name, value, and the deviation drawn to scale --------
        cv = pg.canvas(GUT_X, y, GUT_W, PH)
        mid_y = PH / 2.0
        cv.text(GUT_W - 1.0, mid_y + 5.0, rid, fontsize=6.4, color=c,
                ha="right", va="center", fontweight="bold")
        d = f.E_eta - mu
        cv.text(GUT_W - 1.0, mid_y + 0.7, "$E_\\eta$ = %.1f kJ mol$^{-1}$" % f.E_eta,
                fontsize=5.6, color=INK, ha="right", va="center")

        mid, half, by = GUT_W - 15.0, 11.0, mid_y - 4.2   # deviation bar
        cv.plot([mid - half, mid + half], [by, by], lw=0.6, color=GRID, zorder=1)
        cv.plot([mid, mid], [by - 1.2, by + 1.2], lw=0.6, color=MID, zorder=2)
        cv.add_patch(Rectangle((min(mid, mid + d * half / DEV_HALF), by - 0.7),
                               abs(d) * half / DEV_HALF, 1.4,
                               fc=c, ec="none", zorder=3))
        cv.text(GUT_W - 1.0, by, "%+.1f" % d, fontsize=5.4, color=MID,
                ha="right", va="center")

    # The y label sits horizontally above the column. Rotated at the axis it
    # landed on the 10^3 / 10^4 tick labels, which have no room beside them.
    top = BOT + n * PH
    pg.fig.text(LEFT / pg.W, (top + 0.6) / pg.H,
                r"viscosity  $\eta$  (mPa s)", fontsize=6.4, color=INK,
                va="bottom", ha="left")
    pg.fig.text(GUT_X / pg.W, (top + 7.6) / pg.H,
                "Seven realizations on one axis", fontsize=7.6,
                fontweight="bold", va="bottom", ha="left")
    pg.fig.text(GUT_X / pg.W, (top + 4.2) / pg.H,
                "grey = the other six.  Bar: deviation of $E_\\eta$ from the "
                "primary mean (%.1f, n = 6), full scale \u00b1 5 kJ mol$^{-1}$." % mu,
                fontsize=5.2, color=MID, va="bottom", ha="left")

    L.audit(pg.fig)
    pg.save(HERE, "Fig_column")


if __name__ == "__main__":
    main()
