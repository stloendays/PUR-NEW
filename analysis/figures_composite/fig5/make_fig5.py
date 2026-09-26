"""Figure 5. Which rheological coordinate changed, and which hypothesis was adjudicated.

A  Two rheological coordinates drawn as an orthogonal frame. E5 and the
   validation formulation have no temperature sweep, so no sample carries both
   coordinates and none is plotted in the interior: each axis carries its own
   measurements as a margin. The x margin puts the six chemistry-audited E_eta
   values (and the defined E1 +P perturbation, open) against the 34.7-94.2
   kJ/mol span of 39 external PUR-prepolymer curves; the y margin puts the
   matched 15-60 min drift of E1, E5 and the two validation repeats. Nothing is
   imputed to make a 2D map.
B  Normalized 120 C hold trajectories; the H-CORE proportional-dilution
   prediction is marked at 60 min, not drawn as a trajectory it does not make.
C  The null-model test on one drift axis: E1 reference, the dilution
   prediction, the frozen H-RESIN acceptance threshold, and the two measured
   repeats with their mean absolute drift.
D  The registered hypotheses and their status after the measurement.

All values come from figdata (15-60 min matched window) and the frozen
adjudication record, and are asserted against the manuscript.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig5.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import figdata as D  # noqa: E402
import layout as L  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402
from style import (BLUE, BLUE_D, BLUE_L, BLUE_XL, GRID, GRN, GRN_D, GRN_L,  # noqa: E402
                   GRN_XL, GRY, GRY_D, GRY_L, GRY_M, GRY_XL, INK, ORNG, ORNG_D,
                   ORNG_M, ORNG_XL, Page, tidy)

HERE = os.path.dirname(os.path.abspath(__file__))
HC = {"E5 R02": ORNG_D, "E1 R01": ORNG_M, "F1 repeat_1": GRN, "F1 repeat_2": GRN_D}
HL = {"E5 R02": "E5", "E1 R01": "E1", "F1 repeat_1": "validation 1",
      "F1 repeat_2": "validation 2"}
HORDER = ["E5 R02", "E1 R01", "F1 repeat_1", "F1 repeat_2"]


def swarm(y, min_dy, dx):
    """Offsets for a one-column strip: 0 unless a point would hide another."""
    y = np.asarray(y, dtype=float)
    x = np.zeros(len(y))
    placed = []
    for i in np.argsort(y):
        for k in [0, 1, -1, 2, -2]:
            if all(abs(y[i] - py) >= min_dy or abs(k * dx - px) >= dx * 0.99
                   for px, py in placed):
                x[i] = k * dx
                break
        placed.append((x[i], y[i]))
    return x


def main():
    allfits = D.arrhenius()
    fits = D.primary(allfits)
    mu, sd = fits.E_eta.mean(), fits.E_eta.std(ddof=1)
    e_p = float(allfits.loc[allfits.perturbed, "E_eta"].iloc[0])
    dr = D.hold_drift().set_index("series")
    v = D.validation_drift()
    t0, t1 = D.HOLD_WINDOW
    dyn = pd.read_csv(os.path.join(D.RESULTS, "local_hold_dynamics.csv"))
    k = {r.formulation_id: r.linear_lneta_slope_per_h
         for r in dyn[dyn.formulation_id.isin(["E1", "E5"])].itertuples()}
    with open(os.path.join(D.RESULTS, "analysis_summary.json"), encoding="utf-8") as fh:
        summ = json.load(fh)
    ext = None
    stack = [summ]
    while stack:                                   # find the external E range
        o = stack.pop()
        if isinstance(o, dict):
            if "apparent_E_range_kJ_mol" in o:
                ext = o["apparent_E_range_kJ_mol"]
            stack.extend(o.values())
    with open(os.path.join(D.AGENT, "series_n10", "adjudication_summary.json"),
              encoding="utf-8") as fh:
        adj = json.load(fh)["hypothesis_adjudication"]["hypothesis_verdicts"]
    thr = adj["H-RESIN"]["predicted_drift_pct"]

    assert (round(mu, 2), round(sd, 2), round(e_p, 2)) == (42.05, 2.43, 40.77)
    assert (round(dr.loc["E1 R01", "drift_pct"], 2), round(dr.loc["E5 R02", "drift_pct"], 2),
            round(v["measured"], 2), round(v["null"], 2)) == (9.51, 51.54, 1.60, 7.79)
    assert abs(adj["H-CORE"]["predicted_drift_pct"] - v["null"]) < 1e-3
    assert not adj["H-CORE"]["survives"] and adj["H-RESIN"]["survives"]
    assert adj["H-DUAL"]["separable_by_this_measurement"] is False
    assert (round(ext[0], 1), round(ext[1], 1)) == (34.7, 94.2)
    assert round(k["E5"] / k["E1"], 2) == 4.29

    pg = Page(183.0, 100.0)

    # ---- A  orthogonal coordinates ---------------------------------------
    ax = pg.ax(22, 56, 58, 36)
    ax.set_xlim(20, 100)
    ax.set_ylim(-14, 57)
    # Each coordinate is drawn as a margin outside the other axis's range, so
    # the empty interior reads as "not jointly measured", not as missing data.
    ax.spines["bottom"].set_bounds(30, 100)
    ax.spines["left"].set_bounds(0, 55)
    ym, xm = -8.0, 24.0                               # margin positions
    ax.plot(ext, [ym, ym], color=GRY_L, lw=3.6, solid_capstyle="butt", zorder=1)
    ax.text(ext[1], ym + 2.2, "39 external PUR-prepolymer curves", fontsize=5.1,
            color=GRY_D, ha="right", va="bottom")
    ax.add_patch(Rectangle((mu - sd, ym - 2.2), 2 * sd, 4.4, fc=BLUE_L, ec="none",
                           zorder=2))
    xs_ = fits.E_eta.to_numpy()
    ax.scatter(xs_, np.full(len(xs_), ym) + swarm(xs_, 0.9, 2.6), s=12, fc=BLUE_D,
               ec="white", lw=0.4, zorder=4)
    ax.scatter([e_p], [ym - 3.3], s=12, fc="white", ec=BLUE_D, lw=0.7, zorder=5)
    ax.text(mu + sd + 1.2, ym - 3.3, "E1 +P", fontsize=4.9, color=BLUE_D,
            ha="left", va="center")
    ax.text(mu, ym + 3.9, "local six: CV %.2f%%" % (100 * sd / mu), fontsize=5.4,
            color=BLUE_D, ha="center", va="bottom", fontweight="bold")
    for s_ in HORDER:
        ax.scatter([xm], [dr.loc[s_, "drift_pct"]], s=16, fc=HC[s_], ec="white",
                   lw=0.5, zorder=4)
    ax.text(xm + 2.0, dr.loc["E5 R02", "drift_pct"], "E5", fontsize=5.4,
            color=ORNG_D, va="center", fontweight="bold")
    ax.text(xm + 2.0, dr.loc["E1 R01", "drift_pct"], "E1", fontsize=5.4,
            color=ORNG_D, va="center", fontweight="bold")
    ax.text(xm + 2.0, 1.6, "validation", fontsize=5.4, color=GRN_D, va="center",
            fontweight="bold")
    ax.text(66, 30, "measured on different samples:\nno joint points drawn",
            fontsize=5.2, color=GRY_D, ha="center", va="center", linespacing=1.3)
    ax.set_xlabel(r"temperature response  $E_\eta$  (kJ mol$^{-1}$)")
    ax.set_ylabel("thermal-hold drift, 15\u201360 min (%)")
    ax.set_xticks([40, 60, 80, 100])
    ax.set_yticks([0, 10, 20, 30, 40, 50])
    tidy(ax, grid=None)
    pg.letter("A", 2, 97)

    # ---- B  trajectories -----------------------------------------------------
    h = D.holds()
    ax = pg.ax(104, 58, 72, 33)
    ax.axvspan(t0, t1, color=BLUE_XL, lw=0, zorder=0)
    ax.text(t1 - 1.2, 1.97, "matched window", fontsize=5.2, color=BLUE_D,
            ha="right", va="top")
    ax.axhline(1.0, color=GRID, lw=0.6, zorder=1)
    for s_ in HORDER:
        g = h[h.series == s_].sort_values("time_min")
        y = g.viscosity_reported.to_numpy() / g.viscosity_reported.iloc[0]
        ax.plot(g.time_min, y, lw=1.2, color=HC[s_], zorder=3)
        ax.scatter(g.time_min, y, s=11, fc=HC[s_], ec="white", lw=0.5, zorder=4)
    ax.scatter([t1], [1 + v["null"] / 100], marker="D", s=16, fc="white", ec=GRY_D,
               lw=0.8, zorder=5)
    ax.annotate("H-CORE dilution\nprediction at 60 min", (t1 + 1.0, 1 + v["null"] / 100),
                (67, 1.30), fontsize=5.2, color=GRY_D, ha="left", va="center",
                linespacing=1.2, arrowprops=dict(arrowstyle="-", color=GRY_D,
                                                 lw=0.5, shrinkA=1, shrinkB=2))
    ends = {s_: h[h.series == s_].sort_values("time_min") for s_ in HORDER}
    for s_, dy in (("E5 R02", 0), ("E1 R01", 0)):
        g = ends[s_]
        ax.text(g.time_min.iloc[-1] + 1.5, g.viscosity_reported.iloc[-1]
                / g.viscosity_reported.iloc[0] + dy, HL[s_], fontsize=5.6,
                color=HC[s_], ha="left", va="center", fontweight="bold")
    ax.text(62.0, 0.955, "validation 1, 2", fontsize=5.6, color=GRN_D,
            ha="left", va="center", fontweight="bold")
    ax.text(12.5, 1.62, "$k_{\\mathrm{drift}}$, 15\u201390 min\nE5 / E1 = %.2f\u00d7"
            % (k["E5"] / k["E1"]), fontsize=5.4, color=ORNG_D, ha="left",
            va="center", linespacing=1.3)
    ax.set_xlim(10, 99)
    ax.set_ylim(0.93, 1.99)
    ax.set_xticks([15, 30, 45, 60, 75, 90])
    ax.set_xlabel("hold time at 120 \u00b0C  (min)")
    ax.set_ylabel("\u03b7 / \u03b7(15 min)")
    tidy(ax)
    pg.letter("B", 93, 97)

    # ---- C  the null-model test -------------------------------------------
    ax = pg.ax(14, 12, 86, 26)
    e1 = dr.loc["E1 R01", "drift_pct"]
    reps = [abs(dr.loc[s_, "drift_pct"]) for s_ in ("F1 repeat_1", "F1 repeat_2")]
    ax.axvspan(-0.3, thr, ymin=0.0, ymax=1.0, color=GRN_XL, lw=0, zorder=0)
    ax.axvline(thr, color=GRN, lw=0.7, ls=(0, (2.4, 1.4)), zorder=1)
    ax.text(-0.15, 3.35, "H-RESIN accepted below %.2f%%\n(half the dilution "
            "prediction;\nfrozen rule)" % thr, fontsize=5.1, color=GRN_D, ha="left",
            va="top", linespacing=1.25)
    ax.plot([v["null"], v["null"]], [0.35, 1.78], color=GRY, lw=0.6,
            ls=(0, (1.2, 1.2)), zorder=1)
    # the null is derived from E1 by proportional dilution
    ax.scatter([e1], [2.0], marker="o", s=30, fc=ORNG_M, ec="white", lw=0.6, zorder=4)
    ax.text(e1, 2.42, "E1 reference\n%.2f%%" % e1, fontsize=5.4, color=ORNG_D,
            ha="center", va="bottom", linespacing=1.2)
    ax.annotate("", (v["null"] + 0.12, 2.0), (e1 - 0.14, 2.0),
                arrowprops=dict(arrowstyle="-|>", color=GRY_D, lw=0.8,
                                mutation_scale=6, shrinkA=0, shrinkB=0))
    ax.text(v["null"] + 0.2, 1.62, "\u00d7 %.3f reactive\nmass fraction"
            % v["core_fraction"], fontsize=5.0, color=GRY_D, ha="left",
            va="top", linespacing=1.2)
    ax.scatter([v["null"]], [2.0], marker="D", s=26, fc="white", ec=GRY_D, lw=0.9,
               zorder=5)
    ax.text(v["null"], 2.42, "H-CORE\nprediction\n%.2f%%" % v["null"], fontsize=5.4,
            color=GRY_D, ha="center", va="bottom", linespacing=1.2,
            fontweight="bold")
    # measured
    ax.scatter(reps, [0.6, 0.6], s=16, fc="white", ec=GRN_D, lw=0.8, zorder=4)
    ax.scatter([v["measured"]], [0.6], s=40, fc=GRN_D, ec="white", lw=0.6, zorder=5)
    ax.text(v["measured"], 0.12, "measured, mean |drift| %.2f%%" % v["measured"],
            fontsize=5.6, color=GRN_D, ha="left", va="center", fontweight="bold")
    ax.set_xlim(-0.3, 10.6)
    ax.set_ylim(-0.3, 3.4)
    ax.set_yticks([2.0, 0.6], ["registered\nnull", "two\nrepeats"])
    ax.tick_params(axis="y", length=0, labelsize=5.8)
    ax.set_xticks(range(0, 11, 2))
    ax.set_xlabel("|viscosity change|, 15\u201360 min at 120 \u00b0C  (%)")
    for s_ in ("top", "right", "left"):
        ax.spines[s_].set_visible(False)
    pg.letter("C", 2, 45)

    # ---- D  hypothesis status --------------------------------------------
    cv = pg.canvas(110, 10, 70, 32)
    rows = [("H-CORE", "drift from the reactive core alone;\nproportional dilution of E1",
             "rejected", GRY_L, GRY_D, "-"),
            ("H-RESIN", "resin suppresses drift beyond\ndilution", "retained",
             GRN_L, GRN_D, "-"),
            ("H-DUAL", "low drift needs the tackifier axis;\nneeds an acrylic-only hold",
             "unresolved", "white", GRY_D, (0, (2.0, 1.4)))]
    for i, (name, pred, status, fc, ec, ls) in enumerate(rows):
        y = 23.0 - i * 10.2
        cv.text(0, y + 3.6, name, fontsize=6.4, fontweight="bold", ha="left",
                va="center", color=INK)
        cv.text(0, y - 0.6, pred, fontsize=5.1, ha="left", va="center",
                color=INK, linespacing=1.25)
        cv.add_patch(FancyBboxPatch((50.5, y + 0.9), 18.0, 5.2,
                                    boxstyle="round,pad=0,rounding_size=1.0",
                                    fc=fc, ec=ec, lw=0.7, ls=ls))
        cv.text(59.5, y + 3.5, status, fontsize=6.0, ha="center", va="center",
                color=ec, fontweight="bold")
        if i < 2:
            cv.plot([0, 69], [y - 4.6, y - 4.6], color=GRID, lw=0.5)
    cv.text(0, 31.8, "formulation-level hypotheses, registered before selection",
            fontsize=5.4, color=INK, ha="left", va="top")
    pg.letter("D", 104, 45)

    L.audit(pg.fig)
    pg.save(HERE, "Fig5")


if __name__ == "__main__":
    main()
