"""Figure 5. Temperature response is concentrated; hold trajectory is not.

a  E_eta for the six chemistry-audited realizations, each fitted over its own
   six temperatures, against the mean +- 1 s.d. E1 +P is a deliberate
   perturbation and is not among the six.
b  120 C hold trajectories normalized to 15 min, the matched window shaded.
c  Matched 15-60 min change, with the proportional-dilution prediction.
d  The two native descriptors, side by side on separate axes.

Panel d is deliberately not the old drawing. A CV in percent and a ratio of
drift rates were on one axis, and the caption had to say "no common
effect-size scale is implied" about a drawing that implied exactly that. Here
each descriptor has its own axis, its own units and the data it comes from.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig5.py
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import figdata as D
import layout as L
from style import (DARK_B, DARK_G, FE, GRID, INK, LINE, MID, OS, PALE_B, RED,
                   RU, Page)

HERE = os.path.dirname(os.path.abspath(__file__))

EC = {"E1 R01 \u00b7 1 d": DARK_G, "E2 R01": RU, "E2 R02": DARK_B,
      "E2 R03": OS, "E2 R02 \u00b7 1 d": DARK_B, "E3 R03": FE}
HC = {"E5 R02": RED, "E1 R01": OS, "F1 repeat_1": DARK_G, "F1 repeat_2": FE}
HL = {"E5 R02": "E5", "E1 R01": "E1", "F1 repeat_1": "F1 repeat 1",
      "F1 repeat_2": "F1 repeat 2"}
HORDER = ["E5 R02", "E1 R01", "F1 repeat_1", "F1 repeat_2"]


def swarm(y, min_dy, dx):
    """x offsets for a one-column strip: 0 unless a point would sit on another
    within min_dy, then the nearest free slot of +-dx, +-2dx, ..."""
    y = np.asarray(y, dtype=float)
    x = np.zeros(len(y))
    placed = []
    for i in np.argsort(y):
        for k in [0, 1, -1, 2, -2, 3, -3]:
            cand = k * dx
            if all(abs(y[i] - py) >= min_dy or abs(cand - px) >= dx * 0.99
                   for px, py in placed):
                x[i] = cand
                break
        placed.append((x[i], y[i]))
    return x


def tidy(ax, grid="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis=grid, color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)


def main():
    fits = D.primary(D.arrhenius())
    mu, sd = fits.E_eta.mean(), fits.E_eta.std(ddof=1)
    cv_pct = 100 * sd / mu
    h = D.holds()
    dr = D.hold_drift().set_index("series")
    v = D.validation_drift()
    t0, t1 = D.HOLD_WINDOW
    dyn = pd.read_csv(os.path.join(D.RESULTS, "local_hold_dynamics.csv"))
    k = {r.formulation_id: r.linear_lneta_slope_per_h
         for r in dyn[dyn.formulation_id.isin(["E1", "E5"])].itertuples()}

    pg = Page(183.0, 96.0)

    # ---- a  E_eta, six realizations ---------------------------------------
    ax = pg.ax(14, 55, 68, 33)
    ax.axhspan(mu - sd, mu + sd, color=PALE_B, alpha=.5, lw=0, zorder=0)
    ax.axhline(mu, color=DARK_B, lw=0.7, zorder=1)
    order = list(EC)
    for i, rid in enumerate(order):
        f = fits[fits.rid == rid].iloc[0]
        ax.errorbar(i, f.E_eta, yerr=f.E_se, color=EC[rid], lw=0.8,
                    capsize=1.8, capthick=0.7, zorder=3)
        ax.scatter(i, f.E_eta, s=18, fc=EC[rid], ec="white", lw=0.5, zorder=4)
    ax.set_xticks(range(len(order)), [r.replace(" \u00b7 ", "\n") for r in order],
                  fontsize=5.0)
    ax.set_xlim(-.6, len(order) - .4)
    ax.set_ylim(33.6, 47.4)
    ax.set_yticks([35, 38, 41, 44, 47])
    ax.set_ylabel(r"$E_\eta$  (kJ mol$^{-1}$)")
    tidy(ax)
    ax.text(0.02, 0.97, "mean %.2f \u00b1 %.2f kJ mol$^{-1}$, n = 6, CV %.2f%%"
            % (mu, sd, cv_pct), transform=ax.transAxes, fontsize=5.4,
            color=DARK_B, ha="left", va="top")
    pg.letter("a", 3, 93.5)

    # ---- b  hold trajectories ----------------------------------------------
    ax = pg.ax(104, 55, 72, 33)
    ax.axvspan(t0, t1, color=PALE_B, alpha=.38, lw=0, zorder=0)
    # Top of the shaded span, clear of the legend: along the bottom it sat on
    # the F1 trajectories, which dip to 0.97.
    ax.text(t1 - 1.0, 1.96, "matched window", fontsize=5.0, color=DARK_B,
            ha="right", va="top")
    ax.axhline(1.0, color=GRID, lw=0.6, zorder=1)
    handles = []
    for s in HORDER:
        g = h[h.series == s].sort_values("time_min")
        y = g.viscosity_reported.to_numpy() / g.viscosity_reported.iloc[0]
        ln, = ax.plot(g.time_min, y, lw=1.0, color=HC[s], zorder=3, label=HL[s])
        ax.scatter(g.time_min, y, s=10, fc="white", ec=HC[s], lw=0.8, zorder=4)
        handles.append(ln)
    L.legend(ax, handles, [x.get_label() for x in handles], loc="upper left",
             fontsize=5.0)
    ax.set_xlim(10, 95)
    ax.set_ylim(0.93, 1.99)
    ax.set_xticks([15, 30, 45, 60, 75, 90])
    ax.set_xlabel("hold time at 120 \u00b0C  (min)")
    ax.set_ylabel("\u03b7 / \u03b7(15 min)")
    tidy(ax)
    pg.letter("b", 93, 93.5)

    # ---- c  matched drift and the dilution null ---------------------------
    ax = pg.ax(30, 11, 52, 31)
    vals = [dr.loc[s, "drift_pct"] for s in HORDER]
    ax.barh(range(4), vals, height=.62, color=[HC[s] for s in HORDER], zorder=3)
    for i, val in enumerate(vals):
        ax.text(max(val, 0.0) + 1.0, i, "%+.2f%%" % val, fontsize=5.4,
                color=INK, va="center", ha="left", fontweight="bold", zorder=5,
                bbox=dict(boxstyle="square,pad=0.12", fc="white", ec="none"))
    ax.axvline(v["null"], color=INK, lw=0.7, ls=(0, (2.6, 1.6)), zorder=4)
    ax.text(v["null"] + 1.2, 3.72, "dilution-only prediction %.2f%%" % v["null"],
            fontsize=5.0, color=INK, ha="left", va="center")
    ax.text(26.0, 2.55, "F1 mean |change|\n%.2f%%, below it" % v["measured"],
            fontsize=5.2, color=DARK_G, ha="left", va="center",
            fontweight="bold", linespacing=1.5)
    ax.set_yticks(range(4), [HL[s] for s in HORDER], fontsize=5.6)
    ax.set_xlim(-3, 60)
    ax.set_ylim(-0.6, 4.2)
    ax.set_xticks([0, 15, 30, 45, 60])
    ax.set_xlabel("change in \u03b7, %d\u2013%d min  (%%)" % (t0, t1), labelpad=2)
    tidy(ax, "x")
    pg.letter("c", 3, 47)

    # ---- d  the two native descriptors, two axes --------------------------
    # d1: dispersion of the temperature-response descriptor
    ax = pg.ax(104, 11, 26, 31)
    dev = 100 * (fits.E_eta.to_numpy() - mu) / mu
    ax.axhspan(-cv_pct, cv_pct, color=PALE_B, alpha=.5, lw=0, zorder=0)
    ax.axhline(0, color=DARK_B, lw=0.6, zorder=1)
    # One column, offset only where points would collide. Sorting the values and
    # fanning them across x drew a rising diagonal -- a trend along an axis that
    # means nothing -- while a plain column hid E1 R01 1 d behind E2 R01, which
    # sit 0.12 % apart. n = 6 has to show six dots.
    ax.scatter(swarm(dev, min_dy=1.4, dx=0.16), dev, s=16, fc=DARK_B,
               ec="white", lw=0.6, zorder=3)
    ax.set_xlim(-.6, .6)
    ax.set_xticks([])
    ax.set_ylim(-14, 14)
    ax.set_yticks([-10, -5, 0, 5, 10])
    ax.set_ylabel(r"$E_\eta$ deviation from mean  (%)", fontsize=5.8)
    tidy(ax)
    ax.set_title("temperature response\nCV %.2f%%" % cv_pct, fontsize=5.6,
                 color=INK, pad=3, fontweight="bold")

    # d2: formulation sensitivity of the hold trajectory
    ax = pg.ax(150, 11, 26, 31)
    ax.bar([0, 1], [k["E1"], k["E5"]], width=.58, color=[OS, RED], zorder=3)
    for i, f in enumerate(["E1", "E5"]):
        ax.text(i, k[f] + 0.015, "%.3f" % k[f], fontsize=5.4, color=INK,
                ha="center", va="bottom", fontweight="bold")
    ax.set_xticks([0, 1], ["E1", "E5"])
    ax.set_xlim(-.6, 1.6)
    ax.set_ylim(0, 0.66)
    ax.set_yticks([0, .2, .4, .6])
    ax.set_ylabel("ln \u03b7 drift rate  (h$^{-1}$)", fontsize=5.8)
    tidy(ax)
    ax.set_title("hold trajectory\nE5 / E1 = %.2f\u00d7" % (k["E5"] / k["E1"]),
                 fontsize=5.6, color=INK, pad=3, fontweight="bold")

    # No "separate scales" note: each half already has its own axis, units
    # and title, and the note landed on the right half's y-axis label.
    pg.letter("d", 93, 47)

    L.audit(pg.fig)
    pg.save(HERE, "Fig5")


if __name__ == "__main__":
    main()
