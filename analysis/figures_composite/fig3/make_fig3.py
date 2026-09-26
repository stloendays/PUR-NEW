"""Figure 3. One viscosity anchor is an observation of the realized state.

A  The calibration geometry on real data, for one held realization of the
   strict formulation-and-temperature holdout: (1) the thermal shape is learned
   from the other formulations at <= 110 C, so its level for the new
   realization is unknown; (2) one 110 C anchor fixes that level; (3) 120 and
   130 C are predicted and compared with what was measured.
B  Formulation identity against a state anchor, as a fork. Both branches predict
   the same eight 120-130 C points of the four held E2 realizations; each dot
   is one prediction's predicted/observed ratio. The E2 bridge is read from
   derived/state_anchor_bridge/ and is explanatory manuscript evidence only.
C  Parity for all 12 strict-holdout predictions, 120 and 130 C encoded.
D  The error scale: the cluster-bootstrap distribution of the strict-holdout
   pooled RMSE (recomputed with the analysis seed and asserted against the
   stored interval), with the leave-one-formulation-out pooled error at each of
   the six anchor temperatures on the same axis.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig3.py
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import figdata as D  # noqa: E402
import layout as L  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402
from style import (BLUE, BLUE_D, BLUE_L, BLUE_M, BLUE_XD, BLUE_XL, GRY,  # noqa: E402
                   GRY_D, GRY_L, GRY_M, GRY_XL, INK, Page, tidy)

HERE = os.path.dirname(os.path.abspath(__file__))
SHOWN = "E2__R02__day1_0"           # a held realization near the pooled error


def step(ax, x, y, n, text, ha="left"):
    ax.text(x, y, n, fontsize=5.6, color="white", fontweight="bold", ha="center",
            va="center", zorder=7,
            bbox=dict(boxstyle="circle,pad=0.18", fc=BLUE_D, ec="none"))
    ax.text(x + (2.2 if ha == "left" else -2.2), y, text, fontsize=5.6, color=INK,
            ha=ha, va="center", zorder=7, linespacing=1.25)


def main():
    summ = pd.read_csv(os.path.join(
        D.RESULTS, "local_joint_formulation_temperature_extrapolation_summary.csv"))
    ov = summ[summ.scope == "overall"].iloc[0]
    det = D.strict_holdout_detail()
    pooled = pd.read_csv(os.path.join(D.RESULTS, "local_leave_one_formulation_pooled.csv"))
    bdet, bsum = D.anchor_bridge()
    boot = D.strict_holdout_bootstrap()
    lo95, hi95 = np.quantile(boot, [0.025, 0.975])
    assert abs(lo95 - ov.bootstrap_ci95_low) < 1e-6 and abs(hi95 - ov.bootstrap_ci95_high) < 1e-6
    rm = float(ov.multiplicative_rmse)
    assert (round(rm, 3), round(100 * ov.median_absolute_percentage_error, 2),
            round(lo95, 3), round(hi95, 3)) == (1.088, 5.68, 1.043, 1.126)
    fo = bsum["formulation_only"]["multiplicative_rmse"]
    oa = bsum["one_anchor_state_calibration"]["multiplicative_rmse"]
    assert (round(fo, 3), round(oa, 3)) == (1.824, 1.086)
    for rid in det.held_realization.unique():      # the geometry is the analysis
        s = D.strict_holdout_curve(rid)
        for t in (120, 130):
            ref = det[(det.held_realization == rid) & (det.target_temperature_c == t)]
            assert abs(float(s["pred"](t)) / ref.predicted_viscosity_reported.iloc[0] - 1) < 1e-9
    D.export_table(pd.DataFrame({"pooled_multiplicative_rmse": boot}),
                   "fig3D_strict_holdout_bootstrap")

    pg = Page(183.0, 98.0)

    # ---- A  calibration geometry ------------------------------------------
    g = D.strict_holdout_curve(SHOWN)
    ax = pg.ax(14, 55, 70, 36)
    ax.axvspan(114.5, 134, color=BLUE_XL, lw=0, zorder=0)
    ax.text(124.2, 1180, "unseen\ntemperatures", fontsize=5.4, color=BLUE_D,
            ha="center", va="top", linespacing=1.2)
    for rid, t in g["train"].groupby("realization_id"):
        t = t.sort_values("temperature_c")
        ax.plot(t.temperature_c, t.viscosity_reported, color=GRY_M, lw=0.8, zorder=2)
        ax.scatter(t.temperature_c, t.viscosity_reported, s=6, fc=GRY_M, ec="none",
                   zorder=2)
    # the learned shape at candidate levels: shape known, level not
    held = g["held"]
    fit_T = g["grid"][g["grid"] <= 110.0]
    base = g["curve"][g["grid"] <= 110.0]
    for f in (0.42, 0.62, 1.6, 2.4):
        ax.plot(fit_T, base * f, color=BLUE_M, lw=0.7, ls=(0, (2.2, 1.6)), zorder=2)
    ax.plot(g["grid"][g["grid"] <= 110.0], base, color=BLUE_D, lw=1.3, zorder=4)
    ax.plot(g["grid"][g["grid"] >= 110.0], g["curve"][g["grid"] >= 110.0],
            color=BLUE_D, lw=1.3, ls=(0, (3.2, 1.4)), zorder=4)
    obs = held[held.temperature_c >= 120]
    ax.scatter(held.temperature_c[held.temperature_c < 110],
               held.viscosity_reported[held.temperature_c < 110], s=11, fc="white",
               ec=BLUE_D, lw=0.7, zorder=5)
    ax.scatter([110], [g["anchor"].viscosity_reported], s=46, fc=BLUE_D, ec="white",
               lw=0.8, zorder=6)
    ax.scatter(obs.temperature_c, [float(g["pred"](t)) for t in obs.temperature_c],
               marker="D", s=22, fc="white", ec=BLUE_XD, lw=0.9, zorder=6)
    ax.scatter(obs.temperature_c, obs.viscosity_reported, s=12, fc=INK, ec="none",
               zorder=7)
    step(ax, 79.5, 800, "1", "shape from other formulations, \u2264110 \u00b0C")
    step(ax, 100, 30000, "2", "one 110 \u00b0C anchor\nlocates the state", ha="left")
    ax.annotate("", (109.2, g["anchor"].viscosity_reported * 1.15), (103.5, 21500),
                arrowprops=dict(arrowstyle="-|>", color=BLUE_D, lw=0.6,
                                mutation_scale=5, shrinkA=0, shrinkB=1))
    step(ax, 116.8, 2050, "3", "predict", ha="left")
    ax.set_yscale("log")
    ax.set_xlim(76, 134)
    ax.set_ylim(640, 42000)
    ax.set_xticks([80, 90, 100, 110, 120, 130])
    ax.set_yticks([1000, 2000, 5000, 10000, 20000], ["1", "2", "5", "10", "20"])
    ax.minorticks_off()
    ax.set_xlabel("temperature  (\u00b0C)")
    ax.set_ylabel("viscosity  (10$^3$ mPa s)")
    tidy(ax)
    hs = [ax.plot([], [], color=GRY_M, lw=0.8, label="training realizations")[0],
          ax.plot([], [], color=BLUE_M, lw=0.7, ls=(0, (2.2, 1.6)),
                  label="shape, level unknown")[0],
          ax.plot([], [], color=BLUE_D, lw=1.3, label="calibrated")[0],
          ax.scatter([], [], marker="D", s=22, fc="white", ec=BLUE_XD, lw=0.9,
                     label="predicted"),
          ax.scatter([], [], s=12, fc=INK, ec="none", label="measured")]
    # upper right sits over the unseen band, above every curve (< 10^4 there)
    L.legend(ax, hs, [h.get_label() for h in hs], loc="upper right", fontsize=5.0,
             borderaxespad=0.3)
    pg.letter("A", 2, 96)

    # ---- B  the fork -------------------------------------------------------
    cv = pg.canvas(94, 50, 86, 44)
    cv.add_patch(FancyBboxPatch((0.5, 17.0), 17.0, 10.0,
                                boxstyle="round,pad=0,rounding_size=1.0",
                                fc=BLUE_XL, ec=BLUE_M, lw=0.7))
    cv.text(9.0, 23.8, "held E2\nrealization", fontsize=5.8, ha="center",
            va="center", fontweight="bold", linespacing=1.2)
    cv.text(9.0, 19.4, "predict 120, 130 \u00b0C", fontsize=5.0, ha="center",
            va="center", color=INK)
    for yv, col, lw in ((34.0, GRY, 1.2), (10.0, BLUE_D, 1.6)):
        cv.add_patch(FancyArrowPatch((17.8, 22.0), (27.0, yv), arrowstyle="-|>",
                                     connectionstyle="arc3,rad=%s" % ("-0.25" if yv > 22 else "0.25"),
                                     mutation_scale=7, lw=lw, color=col))
    cv.text(28.0, 38.6, "formulation identity only", fontsize=6.0,
            fontweight="bold", color=GRY_D, ha="left", va="center")
    cv.text(28.0, 34.9, "level unresolved", fontsize=5.6, color=GRY_D, ha="left",
            va="center")
    cv.text(28.0, 14.6, "+ one 110 \u00b0C state anchor", fontsize=6.0,
            fontweight="bold", color=BLUE_D, ha="left", va="center")
    cv.text(28.0, 10.9, "state located", fontsize=5.6, color=BLUE_D, ha="left",
            va="center")
    cv.text(86.0, 41.2, "RMSE", fontsize=5.4, color=INK, ha="right", va="bottom")
    cv.text(86.0, 34.5, "%.3f\u00d7" % fo, fontsize=7.4, fontweight="bold",
            color=GRY_D, ha="right", va="center")
    cv.text(86.0, 10.5, "%.3f\u00d7" % oa, fontsize=7.4, fontweight="bold",
            color=BLUE_D, ha="right", va="center")
    for yb, col, key, face in ((25.2, GRY_D, "formulation_only_log_error", "white"),
                               (1.4, BLUE_D, "one_anchor_log_error", BLUE_D)):
        sa = pg.ax(94 + 50.0, 50 + yb, 23.0, 7.0)
        r = np.exp(bdet[key].to_numpy())
        # 120 C upper row, 130 C lower: the two targets of one realization have
        # nearly the same ratio and would otherwise hide each other.
        yj = np.where(bdet.target_temperature_c.to_numpy() == 120, 0.4, -0.4)
        sa.axvline(1.0, color=GRY_L, lw=0.7, zorder=1)
        sa.scatter(r, yj, s=12, fc=face, ec=col, lw=0.7, alpha=0.9, zorder=3)
        sa.set_xscale("log")
        sa.set_xlim(0.45, 2.8)
        sa.set_ylim(-1, 1)
        sa.set_yticks([])
        sa.set_xticks([0.5, 1, 2], ["0.5", "1", "2"])
        sa.minorticks_off()
        sa.tick_params(labelsize=5.4, length=1.6, pad=1)
        for s in ("top", "right", "left"):
            sa.spines[s].set_visible(False)
    pg.fig.text((94 + 61.5) / pg.W, 48.2 / pg.H,
                "predicted / observed\n(upper row 120 °C, lower 130 °C)",
                fontsize=5.6, ha="center", va="top")
    pg.letter("B", 91, 96)

    # ---- C  parity -----------------------------------------------------------
    ax = pg.ax(16, 10, 34, 32)
    lo, hi = 480.0, 9000.0
    xx = np.array([lo, hi])
    ax.fill_between(xx, xx / rm, xx * rm, color=BLUE_L, alpha=.7, lw=0, zorder=1)
    ax.plot(xx, xx, lw=0.7, color=GRY_D, zorder=2)
    for t, mk, fc in ((120, "o", BLUE_D), (130, "D", "white")):
        dd = det[det.target_temperature_c == t]
        ax.scatter(dd.observed_viscosity_reported, dd.predicted_viscosity_reported,
                   s=16 if mk == "o" else 12, marker=mk, fc=fc, ec=BLUE_D, lw=0.8,
                   zorder=4, label="%d \u00b0C" % t)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ticks = [500, 1000, 2000, 5000]
    ax.set_xticks(ticks, ["0.5", "1", "2", "5"])
    ax.set_yticks(ticks, ["0.5", "1", "2", "5"])
    ax.minorticks_off()
    ax.set_xlabel("measured  (10$^3$ mPa s)")
    ax.set_ylabel("predicted  (10$^3$ mPa s)")
    tidy(ax, grid=None)
    L.legend(ax, loc="upper left", fontsize=5.2)
    ax.text(1.06, 0.02,
            "12 predictions\n6 held realizations\n\npooled RMSE\n%.3f\u00d7\n\n"
            "median abs. error\n%.2f%%\n\nband: \u00d7/\u00f7 RMSE"
            % (rm, 100 * float(ov.median_absolute_percentage_error)),
            transform=ax.transAxes, fontsize=5.5, color=INK, ha="left", va="bottom",
            linespacing=1.3)
    pg.letter("C", 2, 46)

    # ---- D  error scale ----------------------------------------------------
    ax = pg.ax(106, 26, 71, 14)
    # A histogram, not a smoothed density: six resampled clusters make the
    # bootstrap distribution lumpy, and a kernel would invent a smooth shape.
    edges = np.linspace(1.0, 1.16, 33)
    cnt, _ = np.histogram(boot, bins=edges)
    dens = cnt / cnt.max()
    mids = 0.5 * (edges[1:] + edges[:-1])
    inside = (mids >= lo95) & (mids <= hi95)
    ax.bar(mids, dens, width=np.diff(edges), color=np.where(inside, BLUE_L, GRY_L),
           lw=0, zorder=1)
    ax.step(edges, np.r_[dens, dens[-1]], where="post", color=BLUE_D, lw=0.6,
            zorder=2)
    ax.plot([rm, rm], [0, 1.08], color=BLUE_XD, lw=1.0, zorder=3)
    ax.text(rm, 1.12, "%.3f\u00d7" % rm, fontsize=6.0, fontweight="bold",
            color=BLUE_XD, ha="center", va="bottom")
    ax.text(hi95 + 0.002, 0.35, "95%% cluster bootstrap\n%.3f\u2013%.3f\u00d7"
            % (lo95, hi95), fontsize=5.5, color=INK, ha="left", va="center",
            linespacing=1.3)
    ax.set_xlim(1.0, 1.16)
    ax.set_ylim(0, 1.45)
    ax.set_yticks([])
    ax.set_xticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_ylabel("strict holdout,\nbootstrap", fontsize=6.0, rotation=0, ha="right",
                  va="center", labelpad=3, linespacing=1.2)

    ax = pg.ax(106, 10, 71, 10)
    # 90 and 100 C give the same pooled error to five decimals; offset that pair
    # vertically so six anchors show six dots.
    ev = pooled.pooled_multiplicative_error.to_numpy()
    yo = np.zeros(len(ev))
    for i in range(len(ev)):
        for j in range(i):
            if abs(ev[i] - ev[j]) < 0.0015:
                yo[j], yo[i] = 0.32, -0.32
    ax.scatter(ev, yo, s=16, fc="white", ec=BLUE_D, lw=0.8, zorder=3)
    for r, y0 in zip(pooled.itertuples(), yo):
        up = r.anchor_temperature_c in (80, 90, 120)
        ax.text(r.pooled_multiplicative_error, (0.55 if up else -0.62) + y0,
                "%d" % r.anchor_temperature_c, fontsize=5.0, color=BLUE_D,
                ha="center", va="bottom" if up else "top")
    ax.set_xlim(1.0, 1.16)
    ax.set_ylim(-1.4, 1.4)
    ax.set_yticks([])
    ax.set_xticks([1.00, 1.04, 1.08, 1.12, 1.16])
    ax.tick_params(labelsize=5.8)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_ylabel("leave-one-\nformulation-out,\nby anchor \u00b0C", fontsize=6.0,
                  rotation=0, ha="right", va="center", labelpad=3, linespacing=1.2)
    ax.set_xlabel("pooled multiplicative error  (\u00d7)")
    pg.letter("D", 80, 46)

    L.audit(pg.fig)
    pg.save(HERE, "Fig3")


if __name__ == "__main__":
    main()
