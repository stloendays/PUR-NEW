"""Viscosity-temperature master figure.

a  Arrhenius lines for all seven realizations, with a framed legend.
b  Activation energy per realization against the primary mean +- 1 s.d.
c  Held-temperature error for four functional forms, which is what actually
   decides between them.

Axis ranges are cut to the data plus its error bars. An Arrhenius panel always
leaves two empty corners, so the legend takes the lower-right one and the run
description the upper-left, and neither costs page area. `layout.audit` checks
that claim rather than leaving it to the eye.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig_arrhenius.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import figdata as D
import layout as L
from style import DARK_B, DARK_G, FE, GRID, INK, MID, OS, PALE_B, RED, RU, Page

HERE = os.path.dirname(os.path.abspath(__file__))

# A one-day retest shares its parent's colour and is dashed, so the pair reads
# as a pair. That frees colour to separate the distinct realizations; the first
# build used two near-identical navies that were genuinely unreadable.
COL = {
    "E1 +P": RED,
    "E1 R01 \u00b7 1 d": DARK_G,
    "E2 R01": RU,
    "E2 R02": DARK_B,
    "E2 R03": OS,
    "E2 R02 \u00b7 1 d": DARK_B,
    "E3 R03": FE,
}
DASH = {r: ((0, (3.2, 1.6)) if "1 d" in r else "-") for r in COL}
ORDER = list(COL)
# Data spans 1000/T = 2.4805 (130 C) to 2.8316 (80 C). Lines are drawn only
# just past that: running a fit out to the axis edge both clipped it against
# the top of the panel and extrapolated the model beyond anything measured.
XLO, XHI = 2.455, 2.862
FIT_LO, FIT_HI = 2.470, 2.845


def main():
    sw, fits = D.sweeps(), D.arrhenius()
    prim = D.primary(fits)
    mu, sd = prim.E_eta.mean(), prim.E_eta.std(ddof=1)

    pg = Page(183.0, 86.0)

    # ---- a  Arrhenius ----------------------------------------------------
    ax = pg.ax(12.5, 10, 84, 70)
    xs = np.array([FIT_LO, FIT_HI])
    handles = []
    for rid in ORDER:
        g = sw[sw.rid == rid].sort_values("inv_T")
        f = fits[fits.rid == rid].iloc[0]
        c = COL[rid]
        ln, = ax.plot(xs, f.lnA + f.slope * xs / 1000.0, lw=0.9, color=c,
                      linestyle=DASH[rid], zorder=2, label=rid)
        ax.scatter(g.inv_T, g.ln_eta, s=11, fc="white", ec=c, lw=0.8, zorder=3)
        handles.append(ln)

    ax.set_xlim(XLO, XHI)
    ax.set_ylim(6.05, 10.45)
    ax.set_xlabel("1000 / T   (K$^{-1}$)")
    ax.set_ylabel(r"ln [ $\eta$ / (mPa s) ]")
    ax.set_xticks([2.5, 2.6, 2.7, 2.8])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)

    tp = ax.secondary_xaxis("top", functions=(lambda v: 1000.0 / v - 273.15,
                                              lambda t: 1000.0 / (t + 273.15)))
    tp.set_xticks([130, 110, 90, 80])
    tp.set_xlabel("temperature  (\u00b0C)", labelpad=2)
    tp.tick_params(length=2.4, width=0.6, direction="in")

    # The lower-right triangle is structurally empty in an Arrhenius plot, so
    # the legend lives there instead of eating a label column off the right
    # edge, which is where the seven names were crowded before.
    L.legend(ax, handles, [h.get_label() for h in handles], loc="lower right",
             ncol=2, title="realization  (dashed = 1 d retest)")
    # Top-left is the other structurally empty corner: eta falls with
    # temperature, so every line is at its lowest at small 1000/T. Putting this
    # bottom-left ran it into the legend.
    ax.text(XLO + 0.007, 10.38, "7 realizations \u00b7 6 temperatures each \u00b7 42 points\n"
                          "per-realization $R^2$ = 0.965 \u2013 0.998",
            fontsize=5.2, color=MID, ha="left", va="top", linespacing=1.6)
    pg.letter("a", 3, 84)

    # ---- b  E_eta per realization ---------------------------------------
    ax = pg.ax(110, 47, 67, 33)
    ax.axhspan(mu - sd, mu + sd, color=PALE_B, alpha=.5, lw=0, zorder=0)
    ax.axhline(mu, color=DARK_B, lw=0.7, zorder=1)
    for i, rid in enumerate(ORDER):
        f = fits[fits.rid == rid].iloc[0]
        ax.errorbar(i, f.E_eta, yerr=f.E_se, color=COL[rid], lw=0.8,
                    capsize=1.8, capthick=0.7, zorder=3)
        ax.scatter(i, f.E_eta, s=17, fc=COL[rid], ec="white", lw=0.5, zorder=4)
    ax.text(-0.42, mu + sd + .25,
            "primary mean %.2f \u00b1 %.2f  (n = 6)" % (mu, sd),
            fontsize=5.4, color=DARK_B, ha="left", va="bottom")
    ax.annotate("H$_3$PO$_4$", (0, 40.77), (0.42, 35.0), fontsize=5.4, color=RED,
                ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.6,
                                shrinkA=0, shrinkB=2))
    ax.set_xticks(range(7), [r.replace(" \u00b7 ", "\n") for r in ORDER],
                  fontsize=5.0)
    ax.set_xlim(-.6, 6.6)
    ax.set_ylim(33.6, 47.2)
    ax.set_yticks([35, 38, 41, 44, 47])
    ax.set_ylabel(r"$E_\eta$   (kJ mol$^{-1}$)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    pg.letter("b", 100, 84)

    # ---- c  functional form ---------------------------------------------
    mc = D.model_comparison().iloc[::-1].reset_index(drop=True)
    name = {"state_shared_linear": "linear (Arrhenius)",
            "state_shared_quadratic": "quadratic",
            "state_shared_cubic": "cubic", "state_shared_vft": "VFT"}
    ax = pg.ax(110, 10, 67, 25)
    err = (mc.held_temperature_multiplicative_error - 1.0) * 100.0
    cols = [RED if v > 10 else RU for v in err]
    ax.barh(range(len(mc)), err, height=.68, color=cols, zorder=2)
    for i, (v, a) in enumerate(zip(err, mc.aicc)):
        ax.text(v - .35, i, "%.1f%%" % v, fontsize=5.4, color="white",
                va="center", ha="right", fontweight="bold")
        ax.text(12.35, i, "%.0f" % a, fontsize=5.4, color=INK,
                va="center", ha="right")
    ax.text(12.35, 3.62, "AICc", fontsize=5.4, color=MID, va="center", ha="right")
    ax.set_yticks(range(len(mc)), [name[m] for m in mc.model], fontsize=5.6)
    ax.set_xlim(0, 12.6)
    ax.set_ylim(-.6, 3.9)
    ax.set_xticks([0, 3, 6, 9, 12])
    ax.set_xlabel("held-temperature error  (%)", labelpad=2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    pg.letter("c", 100, 41)

    L.audit(pg.fig)
    pg.save(HERE, "Fig_arrhenius")


if __name__ == "__main__":
    main()
