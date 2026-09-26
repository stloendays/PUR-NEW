"""Figure 1. One closed loop from experimental realization to physical adjudication.

A  The formulation chemistry. PPG2000 is drawn atom-for-atom as a
   polypropylene glycol diol and 4,4'-MDI as 4,4'-methylenediphenyl
   diisocyanate. STEPANPOL PDP-70 is a supplier aromatic polyester polyol whose
   exact backbone is not public, so it is a labelled block, not a guessed
   structure.
B  The closed loop as two layers joined by one evidence state. The physical /
   material layer (left, top to bottom) turns heterogeneous realizations into a
   identified rheological state, a reusable thermal response and an actionable
   failure coordinate. The structured evidence state (centre) is the only thing
   the decision / experiment layer (right, bottom to top) receives. Deterministic
   rules build and rank the experiment cards, model-mediated selection works
   inside that ranked set, and the wet-lab measurement adjudicates; its outcome
   returns to the evidence state. Every glyph is drawn from the repository data
   it names, and every number is read through figdata and asserted.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig1.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import chem as C  # noqa: E402
import figdata as D  # noqa: E402
import layout as L  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, Normalize  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402
from style import (BLUE, BLUE_D, BLUE_L, BLUE_M, BLUE_XD, BLUE_XL, GRN, GRN_D,  # noqa: E402
                   GRN_L, GRN_XL, GRY, GRY_D, GRY_L, GRY_M, GRY_XL, INK, MID,
                   ORNG, ORNG_D, ORNG_L, ORNG_M, ORNG_XL, VOI_RAMP, Page)

W, H = 183.0, 143.0
CMAP = LinearSegmentedColormap.from_list("voi", VOI_RAMP)


def arrow(ax, p, q, color=INK, lw=0.9, ms=2.4, ls="-", z=3, cs=None):
    kw = dict(arrowstyle="-|>", mutation_scale=ms * 3.2, lw=lw, color=color,
              linestyle=ls, shrinkA=0, shrinkB=0, zorder=z)
    if cs:
        kw["connectionstyle"] = cs
    ax.add_patch(FancyArrowPatch(p, q, **kw))


# ---------------------------------------------------------------- panel A ---
def panel_a(page):
    ax = page.canvas(4, H - 37, 175, 34)
    yb = 17.0                                       # backbone line of the row

    # --- PPG2000: HO-CH2-CH(CH3)-[O-CH2-CH(CH3)]n-OH --------------------------
    # The chain ends on carbon (ending on the ether O drew a peroxide). The
    # terminal labels sit ON p0 and p6 so the oxygens are unambiguous.
    p = C.zig((6.0, yb), 6, up_first=True)
    C.chain(ax, p)
    C.atom(ax, (p[0][0] + 0.7, p[0][1]), "HO", ha="right")
    C.atom(ax, p[3], "O")
    C.atom(ax, (p[6][0] - 0.7, p[6][1]), "OH", ha="left")
    # Substituents leave on the exterior of the chain angle.
    for i in (2, 5):
        peak = p[i][1] > yb + 0.1
        C.bond(ax, p[i], (p[i][0], p[i][1] + (2.1 if peak else -2.1)))
    # Repeat unit [O-CH2-CH(CH3)]n: brackets cross the CH-O (p2-p3) and CH-OH
    # (p5-p6) bonds and open inward.
    xl = (p[2][0] + p[3][0]) / 2.0
    xr = (p[5][0] + p[6][0]) / 2.0
    for xb, serif in ((xl, +0.6), (xr, -0.6)):
        ax.plot([xb + serif, xb, xb, xb + serif],
                [yb - 3.6, yb - 3.6, yb + 3.6, yb + 3.6], lw=0.7, color=MID, zorder=1)
    ax.text(xr + 0.3, yb - 3.9, "n", fontsize=5.0, color=MID, ha="left", va="top")
    ax.text(p[3][0], yb - 8.2, "PPG2000", fontsize=6.2, ha="center", fontweight="bold")
    ax.text(p[3][0], yb - 11.2, "polyether diol, $M_n$ 2000", fontsize=5.4,
            ha="center", color=INK)
    ax.text(p[3][0], yb + 8.6, "soft segment", fontsize=5.4, ha="center",
            color=GRY_D, fontweight="bold")

    ax.text(30.5, yb, "+", fontsize=8, ha="center", va="center", color=MID)

    # --- STEPANPOL PDP-70, backbone not public --------------------------------
    C.block(ax, 35.0, yb - 5.0, 25.0, 10.0, "PDP-70", "aromatic polyester diol",
            fc=GRY_XL, ec=GRY_D)
    ax.text(47.5, yb - 8.2, "STEPANPOL", fontsize=6.2, ha="center", fontweight="bold")
    ax.text(47.5, yb - 11.2, "supplier polyol", fontsize=5.4, ha="center", color=INK)
    ax.text(47.5, yb + 8.6, "soft segment", fontsize=5.4, ha="center", color=GRY_D,
            fontweight="bold")

    ax.text(64.5, yb, "+", fontsize=8, ha="center", va="center", color=MID)

    # --- 4,4'-MDI: OCN-C6H4-CH2-C6H4-NCO --------------------------------------
    r1 = C.benzene(ax, (79.0, yb), rot=0)
    r2 = C.benzene(ax, (96.0, yb), rot=0)
    mid = ((r1[0][0] + r2[3][0]) / 2.0, yb + 1.5)
    C.bond(ax, r1[0], mid)                            # the methylene bridge
    C.bond(ax, mid, r2[3])
    # Isocyanates in condensed form, OCN- / -NCO: drawn skeletally the linear
    # sp carbon vanishes and the group reads as a nitroso O=N.
    for ring, vert, sgn in ((r1, r1[3], -1), (r2, r2[0], +1)):
        n = (vert[0] + sgn * 2.4, vert[1])
        C.bond(ax, vert, n)
        if sgn < 0:
            C.atom(ax, (n[0] + 0.9, n[1]), "OCN", ha="right")
        else:
            C.atom(ax, (n[0] - 0.9, n[1]), "NCO", ha="left")
    ax.text(87.5, yb - 8.2, "4,4'-MDI", fontsize=6.2, ha="center", fontweight="bold")
    ax.text(87.5, yb - 11.2, "diisocyanate, NCO:OH 1.70\u20131.90", fontsize=5.4,
            ha="center", color=INK)
    ax.text(87.5, yb + 8.6, "hard segment", fontsize=5.4, ha="center", color=GRY_D,
            fontweight="bold")

    arrow(ax, (112.0, yb), (126.0, yb), color=INK, lw=1.0, ms=2.8)
    ax.text(119.0, yb + 2.2, "130 \u2192 120 \u00b0C", fontsize=5.4, ha="center",
            color=INK)
    ax.text(119.0, yb - 3.4, "vacuum", fontsize=5.4, ha="center", color=INK)

    # --- the urethane linkage that forms --------------------------------------
    u = 134.0
    C.bond(ax, (u, yb), (u + 2.4, yb))
    C.atom(ax, (u + 2.4, yb), "O")
    C.bond(ax, (u + 2.4, yb), (u + 5.4, yb))
    C.carbonyl(ax, (u + 5.4, yb), up=True)
    C.bond(ax, (u + 5.4, yb), (u + 8.4, yb))
    C.atom(ax, (u + 8.4, yb), "N")
    C.atom(ax, (u + 8.4, yb - 2.6), "H", size=5.0)
    C.bond(ax, (u + 8.4, yb), (u + 11.4, yb))
    ax.add_patch(FancyBboxPatch((u - 1.2, yb - 6.2), 15.0, 13.5,
                                boxstyle="round,pad=0,rounding_size=0.8",
                                fc="none", ec=GRY_D, lw=0.7, ls=(0, (2.4, 1.6)),
                                zorder=1))
    ax.text(u + 6.3, yb - 8.2, "urethane linkage", fontsize=6.2, ha="center",
            fontweight="bold")
    ax.text(u + 6.3, yb - 11.2, "reactive prepolymer", fontsize=5.4, ha="center",
            color=INK)
    ax.text(164.0, yb + 1.0, "E1\u2013E5:\nNCO:OH and\npolyol ratio\nvaried",
            fontsize=5.3, ha="center", va="center", color=INK, linespacing=1.3)


# ---------------------------------------------------------------- panel B ---
def glyph_ax(page, cx, cy, x, y, w, h):
    """A tick-less data inset at canvas-mm (x, y) of the panel-B canvas."""
    a = page.ax(cx + x, cy + y, w, h)
    a.set_xticks([])
    a.set_yticks([])
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        a.spines[s].set_linewidth(0.4)
        a.spines[s].set_color(GRY)
    a.patch.set_alpha(0)
    return a


def station(ax, x, y, w, h, num, title, body, fc, ec):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.4",
                                fc=fc, ec=ec, lw=0.8, zorder=1))
    ax.text(x + 22.5, y + h - 3.2, title, fontsize=6.1, fontweight="bold",
            ha="left", va="center", color=INK, zorder=4)
    ax.text(x + 22.5, y + h - 6.6, body, fontsize=5.3, ha="left", va="top",
            color=INK, linespacing=1.3, zorder=4)
    ax.text(x + 1.6, y + h - 2.6, num, fontsize=5.6, fontweight="bold", color="white",
            ha="center", va="center", zorder=5,
            bbox=dict(boxstyle="circle,pad=0.16", fc=ec, ec="none"))


def panel_b(page, nums):
    CX, CY, CW, CH = 2.0, 2.0, 179.0, 101.0
    ax = page.canvas(CX, CY, CW, CH)
    bw, bh = 60.0, 17.0
    lx, rx = 0.0, CW - bw
    ly = [75.0, 54.0, 33.0, 12.0]                 # stations 1-4, top to bottom
    ry = [12.0, 37.0, 62.0]                       # stations 5-7, bottom to top

    ax.text(lx, 95.2, "physical / material layer", fontsize=6.6,
            fontweight="bold", color=BLUE_D, ha="left", va="center")
    ax.text(CW, 95.2, "decision / experiment layer", fontsize=6.6,
            fontweight="bold", color=GRY_D, ha="right", va="center")

    left = [
        ("1", "Experimental realization",
         "same nominal recipe, different\npreparation and measurement history"),
        ("2", "Rheological state identification",
         "state intercept $a_{fr}$ on a shared curve\n$R^2$ %.4f \u2192 %.4f; PC1 %.2f%%"
         % (nums["r2f"], nums["r2s"], nums["pc1"])),
        ("3", "Reusable local thermal response",
         "one anchor locates a new realization\nheld-out 120\u2013130 \u00b0C: %.3f\u00d7"
         % nums["rmse"]),
        ("4", "Actionable thermal-hold failure",
         "15\u201360 min drift: E1 +%.2f%%, E5 +%.2f%%\nformulation-sensitive coordinate"
         % (nums["e1"], nums["e5"])),
    ]
    fills = [(BLUE_XL, BLUE_D), (BLUE_XL, BLUE_D), (BLUE_XL, BLUE_D),
             (ORNG_XL, ORNG_D)]
    for (n, t, b), yy, (fc, ec) in zip(left, ly, fills):
        station(ax, lx, yy, bw, bh, n, t, b, fc, ec)
    for i in range(3):
        arrow(ax, (bw / 2, ly[i] - 0.3), (bw / 2, ly[i + 1] + bh + 0.3), color=BLUE_D)

    right = [
        ("5", "Deterministic decision geometry",
         "%d formulations \u00d7 4 measurements\n= %d cards; VOI rank; CBES gate"
         % (nums["n_form"], nums["n_cards"])),
        ("6", "Model-mediated selection",
         "five model stages choose within the\nranked cards; frozen before the result"),
        ("7", "Wet-lab adjudication",
         "drift %.2f%% vs %.2f%% dilution null\nH-CORE rejected, H-RESIN retained"
         % (nums["meas"], nums["null"])),
    ]
    rfills = [(GRY_XL, "#3F5470"), ("white", GRY_D), (GRN_XL, GRN_D)]
    for (n, t, b), yy, (fc, ec) in zip(right, ry, rfills):
        station(ax, rx, yy, bw, bh, n, t, b, fc, ec)
    for i in range(2):
        arrow(ax, (rx + bw / 2, ry[i] + bh + 0.3), (rx + bw / 2, ry[i + 1] - 0.3),
              color=GRY_D)
    # station 6 is the only model-mediated step: dashed outline
    ax.add_patch(FancyBboxPatch((rx, ry[1]), bw, bh,
                                boxstyle="round,pad=0,rounding_size=1.4", fc="none",
                                ec=GRY_D, lw=0.8, ls=(0, (2.4, 1.4)), zorder=2))

    # ---- the hub ----------------------------------------------------------
    hx, hw, hy, hh = bw + 8.0, CW - 2 * bw - 16.0, 12.0, 80.0
    ax.add_patch(FancyBboxPatch((hx, hy), hw, hh, boxstyle="round,pad=0,rounding_size=1.8",
                                fc="white", ec=INK, lw=1.0, zorder=1))
    ax.text(hx + hw / 2, hy + hh - 4.0, "Structured evidence state", fontsize=6.6,
            fontweight="bold", ha="center", va="center")
    ax.text(hx + hw / 2, hy + hh - 8.0, "provenance-preserved, pre-result",
            fontsize=5.3, ha="center", va="center", color=INK)
    items = [
        (BLUE_D, "realized state and\nshared thermal shape"),
        (BLUE_D, "one-anchor transfer:\nvalid in audited chemistry"),
        (GRY_M, "polyol-family boundary\n(external curves)"),
        (ORNG_D, "failure coordinate:\n15\u201360 min drift"),
        (GRY_M, "external resin and\ntackifier priors"),
        (INK, "H-CORE \u00b7 H-RESIN \u00b7 H-DUAL\nregistered"),
        (INK, "measurement semantics:\nHOLD, REPEAT, ANCHOR, SWEEP"),
    ]
    for i, (col, txt) in enumerate(items):
        yy = hy + hh - 16.0 - i * 9.4
        ax.add_patch(Rectangle((hx + 3.0, yy - 1.3), 2.6, 2.6, fc=col, ec="none",
                               zorder=3))
        ax.text(hx + 7.0, yy, txt, fontsize=5.2, ha="left", va="center",
                linespacing=1.2, zorder=3)
    # into and out of the hub
    arrow(ax, (bw + 0.4, ly[3] + bh / 2), (hx - 0.4, ly[3] + bh / 2), color=ORNG_D,
          lw=1.1)
    for yy in (ly[0], ly[1], ly[2]):
        arrow(ax, (bw + 0.4, yy + bh / 2), (hx - 0.4, yy + bh / 2), color=BLUE_M,
              lw=0.7, ms=1.9)
    arrow(ax, (hx + hw + 0.4, ry[0] + bh / 2), (rx - 0.4, ry[0] + bh / 2),
          color=INK, lw=1.1)
    # the outcome returns: to the evidence state, and on to the next round
    arrow(ax, (rx - 0.4, ry[2] + bh / 2), (hx + hw + 0.4, ry[2] + bh / 2),
          color=GRN_D, lw=1.1)
    ax.text((hx + hw + rx) / 2, ry[2] + bh / 2 + 1.4, "new\nevidence",
            fontsize=5.0, color=GRN_D, ha="center", va="bottom", linespacing=1.1)
    yl = 99.5
    # Clear of both layer headers: up from the left of station 7, down into
    # the right of station 1.
    xr_, xl_ = rx + 6.0, bw - 6.0
    ax.add_line(Line2D([xr_, xr_], [ry[2] + bh + 0.3, yl],
                       lw=1.0, color=GRN_D, ls=(0, (3, 1.6)), zorder=2))
    ax.add_line(Line2D([xr_, xl_], [yl, yl], lw=1.0, color=GRN_D,
                       ls=(0, (3, 1.6)), zorder=2))
    arrow(ax, (xl_, yl), (xl_, ly[0] + bh + 0.3), color=GRN_D, lw=1.0,
          ls=(0, (3, 1.6)))
    ax.text(CW / 2, yl + 0.9, "updated evidence state \u2192 next design round",
            fontsize=5.4, color=GRN_D, ha="center", va="bottom")

    # ---- order of authority -----------------------------------------------
    chips = [("physical evidence", BLUE_XL, BLUE_D, "-"),
             ("external prior", GRY_XL, GRY_D, "-"),
             ("deterministic rules", "#D6DCE4", "#3F5470", "-"),
             ("model-mediated selection", "white", GRY_D, (0, (2.4, 1.4))),
             ("wet-lab adjudication", GRN_XL, GRN_D, "-")]
    ax.text(0, 4.2, "order of authority", fontsize=5.6, fontweight="bold", ha="left",
            va="center")
    x = 23.0
    for i, (lab, fc, ec, ls) in enumerate(chips):
        wch = 1.02 * len(lab) + 4.0
        ax.add_patch(FancyBboxPatch((x, 1.4), wch, 5.6,
                                    boxstyle="round,pad=0,rounding_size=1.2",
                                    fc=fc, ec=ec, lw=0.7, ls=ls, zorder=2))
        ax.text(x + wch / 2, 4.2, lab, fontsize=5.4, ha="center", va="center",
                color=INK, zorder=3)
        x += wch
        if i < len(chips) - 1:
            arrow(ax, (x + 0.6, 4.2), (x + 3.4, 4.2), color=INK, lw=0.7, ms=1.8)
            x += 4.0
    return CX, CY, lx, rx, ly, ry, bh


def glyphs(page, nums, geo):
    CX, CY, lx, rx, ly, ry, bh = geo
    gx, gy, gw, gh = 2.2, 2.0, 18.5, bh - 5.0
    a2 = D.panel("p2A")
    b2 = D.panel("p2B")
    ser = ["E2 R01", "E2 R02", "E2 R02 day-1", "E2 R03"]
    shades = [BLUE_M, BLUE, BLUE_D, BLUE_XD]

    g = glyph_ax(page, CX, CY, lx + gx, ly[0] + gy, gw, gh)
    for s, c in zip(ser, shades):
        g.plot(a2.Temperature, a2[s], color=c, lw=0.8)
    g.set_yscale("log")
    g.minorticks_off()
    g.set_yticks([])

    g = glyph_ax(page, CX, CY, lx + gx, ly[1] + gy, gw, gh)
    for s, c in zip(ser, shades):
        g.plot(b2.Temperature, b2[s], color=c, lw=0.8)
    g.set_yscale("log")
    g.minorticks_off()
    g.set_yticks([])
    g.set_ylim(*page.fig.axes[-2].get_ylim())   # same scale as the raw glyph

    s = D.strict_holdout_curve("E2__R02__day1_0")
    g = glyph_ax(page, CX, CY, lx + gx, ly[2] + gy, gw, gh)
    fitm = s["grid"] <= 110
    g.plot(s["grid"][fitm], s["curve"][fitm], color=BLUE_D, lw=0.9)
    g.plot(s["grid"][~fitm], s["curve"][~fitm], color=BLUE_D, lw=0.9, ls=(0, (2, 1)))
    for f in (0.5, 2.0):
        g.plot(s["grid"][fitm], s["curve"][fitm] * f, color=BLUE_M, lw=0.5,
               ls=(0, (1.6, 1.2)))
    g.scatter([110], [s["anchor"].viscosity_reported], s=10, fc=BLUE_D, ec="white",
              lw=0.4, zorder=4)
    obs = s["held"][s["held"].temperature_c >= 120]
    g.scatter(obs.temperature_c, obs.viscosity_reported, s=4, c=INK, zorder=5)
    g.set_yscale("log")
    g.minorticks_off()
    g.set_yticks([])

    h = D.holds()
    g = glyph_ax(page, CX, CY, lx + gx, ly[3] + gy, gw, gh)
    for srs, c in (("E5 R02", ORNG_D), ("E1 R01", ORNG_M)):
        q = h[h.series == srs].sort_values("time_min")
        g.plot(q.time_min, q.viscosity_reported / q.viscosity_reported.iloc[0],
               color=c, lw=0.9)
    g.set_ylim(0.9, 2.0)

    cards = D.experiment_cards()
    for k, m in enumerate(D.MEASUREMENTS):
        g = glyph_ax(page, CX, CY, rx + gx + k * 4.7, ry[0] + gy + 1.0, 4.2, gh - 2.0)
        g.axis("off")
        sub = cards[(cards.measurement == m) & (cards.candidate_id > "S1C09")]
        norm = Normalize(0.10, 0.70)
        for r in sub.itertuples():
            fc = CMAP(norm(r.voi)) if r.admissible_cbes else "white"
            g.add_patch(Rectangle((r.tackifier / 2.5, r.acrylic / 2.5), 0.9, 0.9,
                                  fc=fc, ec=GRY_M if not r.admissible_cbes else "none",
                                  lw=0.2))
        g.set_xlim(0, 5)
        g.set_ylim(0, 13)

    g = glyph_ax(page, CX, CY, rx + gx, ry[1] + gy, gw, gh)
    g.axis("off")
    g.set_xlim(0, 18.5)
    g.set_ylim(0, gh)
    stages = ["Planner", "Proposer", "Skeptic", "Robustness", "Judge"]
    for i, lab in enumerate(stages):
        yy = gh - 1.2 - i * (gh - 2.0) / 4.0
        g.scatter([1.2], [yy], s=5, c=GRY_D, lw=0)
        g.text(2.4, yy, lab, fontsize=5.0, ha="left", va="center")
    g.plot([1.2, 1.2], [gh - 1.2, 0.8], color=GRY_D, lw=0.5, zorder=0)

    g = glyph_ax(page, CX, CY, rx + gx, ry[2] + gy, gw, gh)
    q = h[h.series == "E1 R01"].sort_values("time_min")
    q = q[q.time_min <= 60]
    g.plot(q.time_min, q.viscosity_reported / q.viscosity_reported.iloc[0],
           color=ORNG_M, lw=0.9)
    for srs, c in (("F1 repeat_1", GRN), ("F1 repeat_2", GRN_D)):
        q = h[h.series == srs].sort_values("time_min")
        g.plot(q.time_min, q.viscosity_reported / q.viscosity_reported.iloc[0],
               color=c, lw=0.9)
    g.scatter([60], [1 + nums["null"] / 100], marker="D", s=7, fc="white", ec=GRY_D,
              lw=0.5, zorder=4)
    g.set_ylim(0.95, 1.12)


def main():
    m = D.state_model()
    ss = D.state_shift_summary()
    summ = __import__("pandas").read_csv(os.path.join(
        D.RESULTS, "local_joint_formulation_temperature_extrapolation_summary.csv"))
    dr = D.hold_drift().set_index("series")
    v = D.validation_drift()
    cards = D.experiment_cards()
    nums = dict(r2f=m["formulation_only"]["r2"], r2s=m["state"]["r2"],
                pc1=100 * ss["pc1_explained_between_realization_variance_fraction"],
                rmse=float(summ[summ.scope == "overall"].multiplicative_rmse.iloc[0]),
                e1=dr.loc["E1 R01", "drift_pct"], e5=dr.loc["E5 R02", "drift_pct"],
                meas=v["measured"], null=v["null"],
                n_form=cards.candidate_id.nunique(), n_cards=len(cards))
    assert (round(nums["r2f"], 4), round(nums["r2s"], 4), round(nums["pc1"], 2),
            round(nums["rmse"], 3), round(nums["e1"], 2), round(nums["e5"], 2),
            round(nums["meas"], 2), round(nums["null"], 2), nums["n_form"],
            nums["n_cards"]) == (0.8553, 0.9977, 99.63, 1.088, 9.51, 51.54, 1.60,
                                 7.79, 73, 292)

    page = Page(W, H)
    panel_a(page)
    geo = panel_b(page, nums)
    glyphs(page, nums, geo)
    page.letter("A", 2.0, H - 1.0)
    page.title("The formulation chemistry", 8.0, H - 1.2)
    page.letter("B", 2.0, 107.5)
    page.title("One closed loop from experimental realization to physical adjudication",
               8.0, 107.3)
    L.audit(page.fig)
    page.save(HERE, "Fig1")


if __name__ == "__main__":
    main()
