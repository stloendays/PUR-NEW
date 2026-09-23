"""Figure 2. Realization-dependent viscosity variation is a calibratable state shift.

a  Four E2 realizations. Same nominal formulation, persistent offsets.
b  The same four after the realization-specific intercept a_fr is removed: the
   offsets are gone and one shared thermal response is left.
c  The dominant between-realization mode against an ideal constant vertical
   shift, per temperature.
d  The matched-specification model comparison. Both models use the same
   quadratic inverse-temperature response; only the state conditioning differs.

Panel d is deliberately not the old drawing. Two numbers joined by a thick
diagonal implies intermediate states that were never fitted; these are two
specifications, so they are drawn as two points on two separate scales.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig2.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import figdata as D
import layout as L
from style import DARK_B, DARK_G, FE, GRID, INK, MID, OS, PALE_B, RED, RU, Page

HERE = os.path.dirname(os.path.abspath(__file__))

SERIES = ["E2 R01", "E2 R02", "E2 R02 day-1", "E2 R03"]
COL = {"E2 R01": RU, "E2 R02": DARK_B, "E2 R02 day-1": DARK_G, "E2 R03": OS}
DASH = {s: ((0, (3.2, 1.6)) if "day-1" in s else "-") for s in SERIES}
LAB = {s: s.replace(" day-1", " \u00b7 1 d") for s in SERIES}


def curves(ax, df, ylim, ylabel, note):
    for s in SERIES:
        ax.plot(df["Temperature"], df[s], lw=1.0, color=COL[s],
                linestyle=DASH[s], zorder=3)
        ax.scatter(df["Temperature"], df[s], s=11, fc="white", ec=COL[s],
                   lw=0.8, zorder=4)
    ax.set_yscale("log")
    ax.set_xlim(76, 134)
    ax.set_ylim(*ylim)
    ax.set_xticks([80, 90, 100, 110, 120, 130])
    ax.set_xlabel("temperature  (\u00b0C)")
    ax.set_ylabel(ylabel)
    ax.minorticks_off()
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.text(0.5, 1.03, note, transform=ax.transAxes, fontsize=5.6,
            color=INK, ha="center", va="bottom", fontweight="bold")


def main():
    a, b = D.panel("p2A"), D.panel("p2B")
    c, d = D.panel("p2C"), D.panel("p2D")
    ss = D.state_shift_summary()

    pg = Page(183.0, 104.0)

    # ---- a  raw ----------------------------------------------------------
    ax = pg.ax(13, 60, 72, 34)
    curves(ax, a, (1200, 34000), "viscosity  (mPa s)",
           "as measured \u2014 four E2 realizations")
    ax.set_yticks([2000, 5000, 10000, 20000])
    ax.set_yticklabels(["2", "5", "10", "20"])
    ax.set_ylabel("viscosity  (10$^3$ mPa s)")
    spread = a[SERIES].max(axis=1) / a[SERIES].min(axis=1)
    ax.text(0.97, 0.94, "max / min  %.2f\u2013%.2f\u00d7"
            % (spread.min(), spread.max()), transform=ax.transAxes,
            fontsize=5.4, color=MID, ha="right", va="top")
    pg.letter("a", 3, 102)

    # ---- b  collapsed ----------------------------------------------------
    ax = pg.ax(101, 60, 72, 34)
    curves(ax, b, (1200, 34000), "",
           "after removing the state intercept $a_{fr}$")
    ax.set_yticks([2000, 5000, 10000, 20000])
    ax.set_yticklabels(["2", "5", "10", "20"])
    ax.set_ylabel("viscosity  (10$^3$ mPa s)")
    spread_b = b[SERIES].max(axis=1) / b[SERIES].min(axis=1)
    ax.text(0.97, 0.94, "max / min  %.2f\u2013%.2f\u00d7"
            % (spread_b.min(), spread_b.max()), transform=ax.transAxes,
            fontsize=5.4, color=MID, ha="right", va="top")
    handles = [ax.plot([], [], lw=1.0, color=COL[s], linestyle=DASH[s],
                       label=LAB[s])[0] for s in SERIES]
    L.legend(ax, handles, [h.get_label() for h in handles], loc="lower left",
             ncol=2, fontsize=5.0)
    pg.letter("b", 91, 102)

    # ---- c  the mode -----------------------------------------------------
    ax = pg.ax(13, 12, 72, 34)
    ideal = float(c["Ideal shift"].iloc[0])
    ax.axhline(ideal, color=RED, lw=0.8, ls=(0, (2.6, 1.6)), zorder=2)
    ax.plot(c["Temperature"], c["PC1 loading"], lw=1.0, color=DARK_B, zorder=3)
    ax.scatter(c["Temperature"], c["PC1 loading"], s=16, fc="white",
               ec=DARK_B, lw=0.9, zorder=4)
    ax.text(133, ideal, "ideal constant vertical shift  %.4f" % ideal,
            fontsize=5.2, color=RED, ha="right", va="center",
            bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none"))
    ax.set_xlim(76, 134)
    ax.set_ylim(0.394, 0.427)
    ax.set_xticks([80, 90, 100, 110, 120, 130])
    ax.set_xlabel("temperature  (\u00b0C)")
    ax.set_ylabel("first mode loading")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    # Top-left: the loading dips at 90-110 and rises at 120-130, so the lower
    # band is where the data is. The first placement put this on the 90 C point.
    ax.text(0.03, 0.95,
            "explains %.2f%% of between-realization variance\n"
            "cosine similarity to the ideal shift  %.4f"
            % (100 * ss["pc1_explained_between_realization_variance_fraction"],
               ss["pc1_constant_vertical_shift_cosine_similarity"]),
            transform=ax.transAxes, fontsize=5.4, color=INK, ha="left",
            va="top", linespacing=1.6)
    pg.letter("c", 3, 54)

    # ---- d  matched-specification comparison ----------------------------
    # Two specifications, two metrics, different units. One axis each, and no
    # line between the points: nothing was fitted in between them.
    names = ["formulation\nonly", "state\nconditioned"]
    cols = [OS, DARK_B]
    for k, (col_name, label, lo, hi, fmt) in enumerate([
            ("Fitted R2", "fitted $R^2$  (%)", 80.0, 102.0, "%.2f"),
            ("Leave-one-temperature-out error",
             "leave-one-temperature-out\nmultiplicative error  (\u00d7)",
             1.0, 1.52, "%.3f")]):
        ax = pg.ax(101 + k * 40, 12, 30, 34)
        vals = d[col_name].to_numpy()
        ax.bar([0, 1], vals - lo, bottom=lo, width=.56, color=cols, zorder=3)
        for i, v in enumerate(vals):
            ax.text(i, v + (hi - lo) * 0.025, fmt % v, fontsize=5.6,
                    color=INK, ha="center", va="bottom", fontweight="bold")
        ax.set_xticks([0, 1], names, fontsize=5.2)
        ax.set_xlim(-.62, 1.62)
        ax.set_ylim(lo, hi)
        ax.set_ylabel(label, fontsize=5.8)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.grid(axis="y", color=GRID, lw=0.4, zorder=0)
        ax.set_axisbelow(True)
    pg.fig.text(101 / pg.W, 50.0 / pg.H,
                "Same quadratic inverse-temperature response in both models; "
                "only the state conditioning differs.",
                fontsize=5.2, color=MID, va="bottom", ha="left")
    pg.letter("d", 91, 54)

    L.audit(pg.fig)
    pg.save(HERE, "Fig2")


if __name__ == "__main__":
    main()
