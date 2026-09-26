"""Figure 2. Nominal formulation does not define the realized rheological state.

A  Four realizations of one nominal formulation (E2), as measured. One hue,
   shaded by realized level, so the vertical displacement is read first; a
   bracket gives the spread at 120 C.
B  The same four after subtracting the realization-specific intercept a_fr.
   A and B are one before/after pair joined by the operation between them.
C  The realized state as a coordinate. exp(a_fr) is the level of the shared
   curve at T_ref = 120 C, so every realization sits on one viscosity axis with
   the formulation-only estimate beside it. The inset draws the first
   between-realization singular mode on an axis from zero, where a constant
   vertical shift is a flat line -- the old panel zoomed to 0.395-0.425 and made
   a 99.63 % constant mode look like a trend.
D  The matched-basis model comparison as dumbbells: one row per metric, each on
   its own scale, formulation-only to state-conditioned.

Every number is recomputed or read here and asserted against the manuscript.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig2.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import figdata as D  # noqa: E402
import layout as L  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402
from style import (BLUE, BLUE_D, BLUE_L, BLUE_M, BLUE_XD, GRID, GRY,  # noqa: E402
                   GRY_D, GRY_L, INK, Page, tidy)

HERE = os.path.dirname(os.path.abspath(__file__))

# Ordered by realized level, lowest first: the shade follows the level.
SERIES = ["E2 R01", "E2 R02", "E2 R02 day-1", "E2 R03"]
SHADE = {"E2 R01": BLUE_M, "E2 R02": BLUE, "E2 R02 day-1": BLUE_D, "E2 R03": BLUE_XD}
LAB = {"E2 R01": "R01", "E2 R02": "R02", "E2 R02 day-1": "R02 \u00b7 1 d",
       "E2 R03": "R03"}
RID2SER = {"E2 R01": "E2 R01", "E2 R02": "E2 R02",
           "E2 R02 \u00b7 1 d": "E2 R02 day-1", "E2 R03": "E2 R03"}
YT, YL = [1000, 2000, 5000, 10000, 20000], ["1", "2", "5", "10", "20"]


def curves(ax, df):
    for s in SERIES:
        ls = (0, (3.0, 1.5)) if "day-1" in s else "-"
        ax.plot(df["Temperature"], df[s], lw=1.1, color=SHADE[s], ls=ls, zorder=3)
        ax.scatter(df["Temperature"], df[s], s=12, fc=SHADE[s], ec="white",
                   lw=0.5, zorder=4)
    ax.set_yscale("log")
    ax.set_xlim(76, 141)
    ax.set_ylim(1150, 36000)
    ax.set_xticks([80, 90, 100, 110, 120, 130])
    ax.set_yticks(YT, YL)
    ax.minorticks_off()
    ax.set_xlabel("temperature  (\u00b0C)")
    ax.set_ylabel("viscosity  (10$^3$ mPa s)")
    tidy(ax)


def bracket(ax, x, lo, hi):
    ax.annotate("", (x, lo), (x, hi),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=0.7,
                                shrinkA=0, shrinkB=0, mutation_scale=5))
    ax.text(x + 1.2, np.sqrt(lo * hi), "%.2f\u00d7" % (hi / lo), fontsize=6.4,
            fontweight="bold", color=INK, ha="left", va="center")


def main():
    a, b = D.panel("p2A"), D.panel("p2B")
    c, d = D.panel("p2C"), D.panel("p2D")
    ss = D.state_shift_summary()
    m = D.state_model()
    st = D.state_axis()

    r2_f, r2_s = 100 * m["formulation_only"]["r2"], 100 * m["state"]["r2"]
    e_f, e_s = d["Leave-one-temperature-out error"].to_numpy()
    assert abs(r2_f - d["Fitted R2"].iloc[0]) < 1e-6
    assert abs(r2_s - d["Fitted R2"].iloc[1]) < 1e-6
    assert (round(r2_f, 2), round(r2_s, 2), round(e_f, 3), round(e_s, 3)) == \
        (85.53, 99.77, 1.423, 1.058)
    pc1 = 100 * ss["pc1_explained_between_realization_variance_fraction"]
    cos = ss["pc1_constant_vertical_shift_cosine_similarity"]
    assert (round(pc1, 2), round(cos, 4)) == (99.63, 0.9998)
    D.export_table(st, "fig2C_state_axis")

    pg = Page(183.0, 100.0)
    at120 = lambda df: df.loc[df.Temperature == 120, SERIES].iloc[0]  # noqa: E731

    # ---- A  as measured ---------------------------------------------------
    ax = pg.ax(14, 56, 64, 36)
    curves(ax, a)
    bracket(ax, 133.5, at120(a).min(), at120(a).max())
    ax.plot([120, 133.5], [at120(a).min()] * 2, color=GRY, lw=0.5, ls=":", zorder=1)
    ax.plot([120, 133.5], [at120(a).max()] * 2, color=GRY, lw=0.5, ls=":", zorder=1)
    ax.text(0.03, 0.05, "one nominal formulation (E2)\nfour realizations",
            transform=ax.transAxes, fontsize=5.8, color=INK, ha="left",
            va="bottom", linespacing=1.4)
    ax.set_title("as measured", fontsize=6.6, fontweight="bold", pad=3)
    pg.letter("A", 2, 98)

    # ---- the operation between A and B ------------------------------------
    cv = pg.canvas(80, 56, 22, 36)
    cv.add_patch(FancyArrowPatch((2.0, 20.0), (20.0, 20.0), arrowstyle="-|>",
                                 mutation_scale=9, lw=1.6, color=BLUE_D))
    cv.text(11.0, 23.0, "state\nalignment", fontsize=6.2, fontweight="bold",
            color=BLUE_D, ha="center", va="bottom", linespacing=1.2)
    cv.text(11.0, 16.8, "subtract the\nrealization-\nspecific\nintercept $a_{fr}$",
            fontsize=5.4, color=INK, ha="center", va="top", linespacing=1.3)

    # ---- B  aligned --------------------------------------------------------
    ax = pg.ax(113, 56, 64, 36)
    curves(ax, b)
    sb = b[SERIES].max(axis=1) / b[SERIES].min(axis=1)
    bracket(ax, 133.5, at120(b).min(), at120(b).max())
    ax.plot([120, 133.5], [at120(b).min()] * 2, color=GRY, lw=0.5, ls=":", zorder=1)
    ax.plot([120, 133.5], [at120(b).max()] * 2, color=GRY, lw=0.5, ls=":", zorder=1)
    ax.text(0.03, 0.05, "one shared thermal response\nmax/min %.2f\u2013%.2f\u00d7 across T"
            % (sb.min(), sb.max()), transform=ax.transAxes, fontsize=5.8,
            color=INK, ha="left", va="bottom", linespacing=1.4)
    handles = [ax.plot([], [], lw=1.1, color=SHADE[s],
                       ls=(0, (3.0, 1.5)) if "day-1" in s else "-",
                       label=LAB[s])[0] for s in SERIES]
    # top right: every aligned curve has fallen below 3000 mPa s by 110 C
    L.legend(ax, handles, [h.get_label() for h in handles], loc="upper right",
             ncol=2, fontsize=5.2, handlelength=1.8)
    ax.set_title("after alignment", fontsize=6.6, fontweight="bold", pad=3)
    pg.letter("B", 102, 98)

    # ---- C  the state coordinate ------------------------------------------
    ax = pg.ax(22, 12, 66, 28)
    rows = {"E1": 2, "E2": 1, "E3": 0}
    for yv in rows.values():
        ax.axhline(yv, color=GRID, lw=0.5, zorder=0)
    for f, g in st.groupby("formulation_id"):
        yv = rows[f]
        ax.scatter([float(g.eta_formulation.iloc[0])], [yv + 0.32], marker="v",
                   s=22, fc=GRY_L, ec=GRY_D, lw=0.6, zorder=3)
        if len(g) > 1:
            ax.plot([g.eta_ref.min(), g.eta_ref.max()], [yv, yv], color=BLUE_L,
                    lw=3.4, solid_capstyle="round", zorder=2)
        for r in g.itertuples():
            col = SHADE[RID2SER[r.rid]] if f == "E2" else BLUE_D
            ax.scatter([r.eta_ref], [yv], s=28, fc=col, ec="white", lw=0.6,
                       zorder=4)
    e2 = st[st.formulation_id == "E2"]
    ax.text(float(e2.eta_ref.max()) * 1.13, 1, "one formulation,\nfour states",
            fontsize=5.8, color=BLUE_D, ha="left", va="center", fontweight="bold",
            linespacing=1.2)
    ax.set_xscale("log")
    ax.set_xlim(560, 13000)
    ax.set_xticks([1000, 2000, 5000, 10000], ["1", "2", "5", "10"])
    ax.minorticks_off()
    ax.set_ylim(-0.6, 2.75)
    ax.set_yticks([2, 1, 0], ["E1", "E2", "E3"])
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("realized level exp($a_{fr}$) at 120 \u00b0C  (10$^3$ mPa s)")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.annotate("", (0.99, 1.09), (0.01, 1.09), xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=BLUE_D, lw=0.8,
                                mutation_scale=6, shrinkA=0, shrinkB=0))
    ax.text(0.01, 1.13, "lower realized viscosity state", transform=ax.transAxes,
            fontsize=5.6, color=BLUE_D, ha="left", va="bottom")
    ax.text(0.99, 1.13, "higher", transform=ax.transAxes, fontsize=5.6,
            color=BLUE_D, ha="right", va="bottom")
    h1 = ax.scatter([], [], s=28, fc=BLUE_D, ec="white", label="realization, $a_{fr}$")
    h2 = ax.scatter([], [], marker="v", s=22, fc=GRY_L, ec=GRY_D, lw=0.6,
                    label="formulation-only level, $\\mu_f$")
    # upper right: the E1 row ends below 1000 mPa s, so its right half is empty
    L.legend(ax, [h1, h2], [h1.get_label(), h2.get_label()], loc="upper right",
             fontsize=5.2)
    pg.letter("C", 2, 49)

    # inset: the first between-realization mode on an axis from zero
    ax = pg.ax(100, 14, 21, 21)
    ax.axhline(float(c["Ideal shift"].iloc[0]), color=GRY, lw=0.7,
               ls=(0, (2.4, 1.4)), zorder=2)
    ax.plot(c["Temperature"], c["PC1 loading"], color=BLUE_D, lw=1.0, zorder=3)
    ax.scatter(c["Temperature"], c["PC1 loading"], s=9, fc=BLUE_D, ec="white",
               lw=0.4, zorder=4)
    ax.set_ylim(0, 0.6)
    ax.set_yticks([0, 0.2, 0.4, 0.6], ["0", "0.2", "0.4", "0.6"])
    ax.set_xlim(75, 135)
    ax.set_xticks([80, 105, 130])
    ax.tick_params(labelsize=5.6)
    ax.set_xlabel("T  (\u00b0C)", fontsize=6.0, labelpad=1)
    ax.set_ylabel("mode-1 loading", fontsize=6.0, labelpad=1)
    tidy(ax)
    ax.text(0.5, 1.06, "PC1 %.2f%%\ncosine to shift %.4f" % (pc1, cos),
            transform=ax.transAxes, fontsize=5.5, color=INK, ha="center",
            va="bottom", linespacing=1.35, fontweight="bold")
    ax.text(0.97, 0.47, "constant shift", transform=ax.transAxes, fontsize=5.0,
            color=GRY_D, ha="right", va="top")

    # ---- D  dumbbells ------------------------------------------------------
    rowsD = [("fitted $R^2$ (%)", r2_f, r2_s, (80, 101), [80, 85, 90, 95, 100],
              "%.2f"),
             ("held-temperature\nerror (\u00d7)", e_f, e_s, (1.0, 1.5),
              [1.0, 1.1, 1.2, 1.3, 1.4, 1.5], "%.3f")]
    for k, (lab, vf, vs, lim, ticks, fmt) in enumerate(rowsD):
        ax = pg.ax(146, 27.0 - k * 17.0, 31, 7.0)
        ax.plot([vf, vs], [0, 0], color=BLUE_L, lw=3.0, solid_capstyle="butt",
                zorder=2)
        ax.annotate("", (vs, 0), (vf, 0), arrowprops=dict(
            arrowstyle="-|>", color=BLUE_D, lw=0.8, mutation_scale=6,
            shrinkA=4, shrinkB=4), zorder=3)
        ax.scatter([vf], [0], s=34, fc="white", ec=GRY_D, lw=0.9, zorder=4)
        ax.scatter([vs], [0], s=34, fc=BLUE_D, ec="white", lw=0.6, zorder=4)
        ax.text(vf, 1.0, fmt % vf, fontsize=5.8, color=GRY_D, ha="center",
                va="bottom")
        ax.text(vs, 1.0, fmt % vs, fontsize=5.8, color=BLUE_D, ha="center",
                va="bottom", fontweight="bold")
        ax.set_xlim(*lim)
        ax.set_xticks(ticks)
        ax.set_ylim(-1, 2.2)
        ax.set_yticks([])
        ax.tick_params(labelsize=5.6)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.set_ylabel(lab, fontsize=6.0, rotation=0, ha="right", va="center",
                      labelpad=3, linespacing=1.2)
    pg.fig.text(132 / pg.W, 45.2 / pg.H, "same quadratic thermal basis",
                fontsize=5.6, color=INK, ha="left", va="bottom")
    pg.fig.text(132 / pg.W, 41.6 / pg.H, "\u25cb formulation-only", fontsize=5.6,
                color=GRY_D, ha="left", va="bottom")
    pg.fig.text(155 / pg.W, 41.6 / pg.H, "\u25cf state-conditioned",
                fontsize=5.6, color=BLUE_D, ha="left", va="bottom")
    pg.letter("D", 126, 49)

    L.audit(pg.fig)
    pg.save(HERE, "Fig2")


if __name__ == "__main__":
    main()
