"""Figure 3. One-point state calibration transfers the shared thermal response.

a  Pooled leave-one-formulation-out reconstruction error against the anchor
   temperature. Every anchor works; the 120 C one used in b is marked.
b  The same at the 120 C anchor, resolved by held formulation, with the other
   anchors behind it so a reader can see whether 120 C is a lucky choice.
c  The strict holdout: the shared response never sees the held formulation and
   never sees above 110 C, and one 110 C point predicts 120 and 130 C.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig3.py
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import figdata as D
import layout as L
from style import DARK_B, DARK_G, FE, GRID, INK, MID, OS, PALE_B, RED, RU, Page

HERE = os.path.dirname(os.path.abspath(__file__))
ANCHOR_B = 120.0
FCOL = {"E1": DARK_G, "E2": RU, "E3": FE}


def main():
    pooled = pd.read_csv(os.path.join(D.RESULTS,
                                      "local_leave_one_formulation_pooled.csv"))
    onept = pd.read_csv(os.path.join(D.RESULTS,
                                     "local_leave_one_formulation_one_point.csv"))
    c = D.panel("p3C")
    summ = pd.read_csv(os.path.join(
        D.RESULTS, "local_joint_formulation_temperature_extrapolation_summary.csv"))
    ov = summ[summ.scope == "overall"].iloc[0]

    pg = Page(183.0, 68.0)

    # ---- a  anchor sweep -------------------------------------------------
    ax = pg.ax(14, 13, 44, 45)
    ax.axhline(1.0, color=GRID, lw=0.6, zorder=1)
    ax.plot(pooled.anchor_temperature_c, pooled.pooled_multiplicative_error,
            lw=1.0, color=DARK_B, zorder=3)
    mark = pooled.anchor_temperature_c == ANCHOR_B
    ax.scatter(pooled.anchor_temperature_c[~mark],
               pooled.pooled_multiplicative_error[~mark], s=16, fc="white",
               ec=DARK_B, lw=0.9, zorder=4)
    ax.scatter(pooled.anchor_temperature_c[mark],
               pooled.pooled_multiplicative_error[mark], s=22, fc=RED,
               ec="white", lw=0.6, zorder=5)
    v = float(pooled.loc[mark, "pooled_multiplicative_error"].iloc[0])
    ax.annotate("%.3f\u00d7 at %.0f \u00b0C\n(used in b)" % (v, ANCHOR_B),
                (ANCHOR_B, v), (108, 1.113), fontsize=5.4, color=RED,
                ha="center", va="bottom", linespacing=1.5,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.6,
                                shrinkA=0, shrinkB=3))
    ax.set_xlim(76, 134)
    ax.set_ylim(1.0, 1.135)
    ax.set_xticks([80, 90, 100, 110, 120, 130])
    ax.set_xlabel("anchor temperature  (\u00b0C)")
    ax.set_ylabel("pooled multiplicative error  (\u00d7)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.text(0.03, 0.04, "6 held realizations at every anchor",
            transform=ax.transAxes, fontsize=5.2, color=MID, ha="left",
            va="bottom")
    pg.letter("a", 3, 66)

    # ---- b  per formulation, 120 C anchor -------------------------------
    ax = pg.ax(74, 13, 38, 45)
    forms = ["E1", "E2", "E3"]
    at120 = onept[onept.anchor_temperature_c == ANCHOR_B].set_index(
        "held_formulation")
    ax.axhline(1.0, color=GRID, lw=0.6, zorder=1)
    for i, f in enumerate(forms):
        other = onept[(onept.held_formulation == f)
                      & (onept.anchor_temperature_c != ANCHOR_B)]
        ax.scatter(np.full(len(other), i) + 0.30, other.multiplicative_error,
                   s=7, fc=PALE_B, ec="none", zorder=2)
        val = float(at120.loc[f, "multiplicative_error"])
        ax.bar(i, val - 1.0, bottom=1.0, width=.44, color=FCOL[f], zorder=3)
        ax.text(i, val + 0.004, "%.3f" % val, fontsize=5.6, color=INK,
                ha="center", va="bottom", fontweight="bold")
        ax.text(i, 1.003, "n = %d" % int(at120.loc[f, "n_held_realizations"]),
                fontsize=5.0, color="white", ha="center", va="bottom")
    ax.axhline(v, color=RED, lw=0.8, ls=(0, (2.6, 1.6)), zorder=4)
    ax.text(2.42, v, "pooled %.3f\u00d7" % v, fontsize=5.2, color=RED,
            ha="right", va="bottom")
    ax.set_xticks(range(3), forms)
    ax.set_xlim(-.6, 2.62)
    ax.set_ylim(1.0, 1.135)
    ax.set_xlabel("held formulation")
    ax.set_ylabel("multiplicative error  (\u00d7)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    # Below the axes: E2's bar reaches 1.119, close to the top of the range,
    # and the audit found this note sitting on its value label.
    pg.fig.text(74 / pg.W, 2.0 / pg.H,
                "bars: %.0f \u00b0C anchor\ndots: the other five anchors"
                % ANCHOR_B, fontsize=5.0, color=MID, va="bottom", ha="left",
                linespacing=1.5)
    pg.letter("b", 64, 66)

    # ---- c  strict holdout parity ---------------------------------------
    ax = pg.ax(128, 13, 48, 45)
    lo, hi = 420.0, 9600.0
    band = float(ov.multiplicative_rmse)
    xx = np.array([lo, hi])
    ax.fill_between(xx, xx / band, xx * band, color=PALE_B, alpha=.45, lw=0,
                    zorder=1)
    ax.plot(xx, xx, lw=0.7, color=MID, zorder=2)
    for obs, pred, lab, col, mk in (("Observed 120", "Predicted 120",
                                     "120 \u00b0C", DARK_B, "o"),
                                    ("Observed 130", "Predicted 130",
                                     "130 \u00b0C", FE, "s")):
        ax.scatter(c[obs], c[pred], s=17, fc="white", ec=col, lw=0.9,
                   marker=mk, zorder=4, label=lab)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ticks = [500, 1000, 2000, 5000]
    ax.set_xticks(ticks, ["0.5", "1", "2", "5"])
    ax.set_yticks(ticks, ["0.5", "1", "2", "5"])
    ax.minorticks_off()
    ax.set_xlabel("observed viscosity  (10$^3$ mPa s)")
    ax.set_ylabel("predicted viscosity  (10$^3$ mPa s)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    L.legend(ax, loc="upper left", fontsize=5.2)
    ax.text(0.04, 0.70, "band = \u00b1 pooled RMSE", transform=ax.transAxes,
            fontsize=5.0, color=MID, ha="left", va="center")
    # One box rather than a strip under the panel: at 5 pt the strip ran off
    # the right edge of the page.
    ax.text(0.97, 0.03,
            "%d predictions\npooled RMSE %.3f\u00d7\n"
            "median abs. error %.2f%%\n"
            "cluster bootstrap 95%% %.3f\u2013%.3f\u00d7\n"
            "(10 000 realization-level replicates)"
            % (int(ov.n_predictions), band,
               100 * float(ov.median_absolute_percentage_error),
               float(ov.bootstrap_ci95_low), float(ov.bootstrap_ci95_high)),
            transform=ax.transAxes, fontsize=5.2, color=INK, ha="right",
            va="bottom", linespacing=1.6)
    pg.letter("c", 118, 66)

    L.audit(pg.fig)
    pg.save(HERE, "Fig3")


if __name__ == "__main__":
    main()
