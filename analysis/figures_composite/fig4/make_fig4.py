"""Figure 4. Explicit scientific rules shape which experiment is informative.

A  The decision object itself: 292 experiment cards = 73 formulation candidates
   x 4 measurement plans. Each measurement gets one map of the formulation
   lattice (acrylic-like x tackifier-like wt%, with the nine reactive-core-only
   candidates as a separate block), and each tile is one card filled by its
   deterministic VOI. A dot marks non-zero hypothesis discrimination, a green
   outline the tied top set, hatching the cards the CBES chemistry-applicability
   rule makes inadmissible. Rings count the confirmatory selections.
B  Why cards differ: the weighted VOI components of four representative cards,
   benefit terms right of zero and risk terms left of it.
C  Where each arm's frozen selections landed on the M-HOLD-120 lattice, with
   the discriminating cards shaded. Marker shape is the measurement chosen.
D  Every run, one tile each, coloured by what its selected experiment can do.
   For the order-inverted arm the critique flags sit above the tiles: the
   defect was detected and the selection was not changed.

Scores and cards are read from the frozen voi_full_ranking.json files, the
selections from each run's recommendation.json and the critique flags from each
deliberation.json; all are asserted against rule_layer_ablation.json and the
manuscript's Table 1 before anything is drawn. The VOI, the ranking and the
tied top set are deterministic; only the selections are model-mediated.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig4.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import figdata as D  # noqa: E402
import layout as L  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, Normalize  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from style import (GRN, GRN_D, GRY, GRY_D, GRY_L, GRY_M, GRY_XL, INK,  # noqa: E402
                   VOI_RAMP, Page)

HERE = os.path.dirname(os.path.abspath(__file__))
CMAP = LinearSegmentedColormap.from_list("voi", VOI_RAMP)
NORM = Normalize(0.10, 0.70)
MNAME = {"M-HOLD-120": "matched-window 120 \u00b0C hold",
         "M-REPEAT": "repeatability check",
         "M-ANCHOR": "one-point anchor",
         "M-SWEEP": "80\u2013130 \u00b0C sweep"}
ARMS = ["full", "voi_withheld", "order_inverted"]
ANAME = {"full": "rule-complete", "voi_withheld": "VOI score withheld",
         "order_inverted": "rule order inverted"}
C_OTHER = "#6F829C"               # discriminating, outside the supported family
C_ZERO = GRY_M
TW, TH = 0.84, 0.80               # tile size in lattice units


def pos(cid, acr, tack):
    """Tile centre. The core-only candidates S1C01-09 form a 3 x 3 block left of
    the lattice; they share acrylic = tackifier = 0 and differ in the core."""
    k = int(cid[3:])
    if k <= 9:
        i = k - 1
        return -3.2 + (i % 3) * 0.72, 3.0 - (i // 3) * 0.95, 0.62, 0.78
    return acr / 2.5, tack / 2.5, TW, TH


def _find(obj, key):
    """Every value stored under `key` anywhere in a parsed JSON document."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                yield v
            yield from _find(v, key)
    elif isinstance(obj, list):
        for v in obj:
            yield from _find(v, key)


def tile(ax, x, y, w, h, **kw):
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, **kw))


def lattice_frame(ax, ylab=True, fs=5.6):
    ax.set_xlim(-3.75, 12.55)
    ax.set_ylim(-0.55, 4.55)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_bounds(-0.4, 4.4)
    ax.spines["bottom"].set_bounds(-0.45, 12.45)
    ax.spines["left"].set_position(("data", -0.62))
    ax.set_xticks([0, 4, 8, 12], ["0", "10", "20", "30"])
    ax.set_yticks([0, 2, 4], ["0", "5", "10"] if ylab else [])
    ax.tick_params(labelsize=fs, length=1.6, pad=1.2)
    ax.text(-2.48, -0.5, "core-\nonly", fontsize=4.9, color=GRY_D, ha="center",
            va="top", linespacing=1.0)


def main():
    cards = D.experiment_cards()
    runs = D.ablation_runs()
    crit = D.run_critique()
    agg = D.ablation_summary()["arms"]
    key = {"full": "full", "voi_withheld": "ablated",
           "order_inverted": "rule_order_inverted"}
    by = {a: runs[runs.arm == a].sort_values("run") for a in ARMS}

    # ---- the numbers this figure must reproduce ---------------------------
    table1 = {"full": (10, 9, 0, 0.667), "voi_withheld": (5, 0, 3, 0.267),
              "order_inverted": (10, 0, 10, 0.000)}
    for a in ARMS:
        n, sup, zero, mean = table1[a]
        r = by[a]
        assert (len(r), int(r.supported.sum()), int((r.discrimination == 0).sum()),
                round(r.discrimination.mean(), 3)) == (n, sup, zero, mean), a
        ic = agg[key[a]]["internal_critique"]
        c = crit[crit.arm == a]
        assert int(c.high_severity.sum()) == ic["high_severity_objection"], a
        assert int(c.robustness_change.sum()) == ic["robustness_said_change_experiment"], a
    assert (by["order_inverted"].measurement == "M-HOLD-120").sum() == 7
    assert sorted(cards[cards.tied_top].candidate_id) == \
        ["S1C41", "S1C46", "S1C51", "S1C56", "S1C61"]
    # The inverted order's deterministic rank-1 card, as every frozen run of
    # that arm recorded it.
    import glob
    import json
    r1 = set()
    for p in glob.glob(os.path.join(D.AGENT, D.ARM_DIRS["order_inverted"], "run_*",
                                    "*", "deliberation.json")):
        with open(p, encoding="utf-8") as fh:
            r1 |= set(_find(json.load(fh), "policy_rank_1_experiment_id"))
    assert len(r1) == 1, r1
    inv_rank1 = r1.pop()
    assert inv_rank1 == "S1C01::M-HOLD-120", inv_rank1
    D.export_table(cards, "fig4A_experiment_cards")
    D.export_table(runs.merge(crit, on=["arm", "run"]), "fig4CD_runs")

    pg = Page(183.0, 144.0)

    # ---- A  the card landscape -------------------------------------------
    pg.letter("A", 2, 142.5)
    pg.fig.text(8 / pg.W, 142.3 / pg.H,
                "292 experiment cards = 73 formulation candidates \u00d7 4 measurement "
                "plans, ranked by deterministic VOI", fontsize=6.8,
                fontweight="bold", va="top", ha="left")
    x0s = [13, 55, 97, 139]
    for k, m in enumerate(D.MEASUREMENTS):
        ax = pg.ax(x0s[k], 110, 41, 20)
        sub = cards[cards.measurement == m]
        for r in sub.itertuples():
            x, y, w, h = pos(r.candidate_id, r.acrylic, r.tackifier)
            if not r.admissible_cbes:
                tile(ax, x, y, w, h, fc="white", ec=GRY_M, lw=0.35, hatch="//////",
                     zorder=2)
                continue
            tile(ax, x, y, w, h, fc=CMAP(NORM(r.voi)), ec="none", zorder=2)
            if r.discrimination > 0:
                ax.scatter([x], [y], s=1.5, c="white", lw=0, zorder=3)
            if r.tied_top:
                tile(ax, x, y, w, h, fc="none", ec=GRN, lw=1.0, zorder=4)
        if m == "M-HOLD-120":
            for cid, n in by["full"].candidate_id.value_counts().items():
                r = sub[sub.candidate_id == cid].iloc[0]
                x, y, _, _ = pos(cid, r.acrylic, r.tackifier)
                ax.scatter([x], [y], s=26, fc="none", ec="white", lw=1.6, zorder=5)
                ax.scatter([x], [y], s=26, fc="none", ec=GRN, lw=0.9, zorder=6)
                ax.text(x - 0.62, y, str(n), fontsize=5.6, fontweight="bold",
                        color=GRN_D, ha="right", va="center", zorder=7,
                        bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none"))
        lattice_frame(ax, ylab=(k == 0))
        nd = int((sub.discrimination > 0).sum())
        na = int((~sub.admissible_cbes).sum())
        stats = "max VOI %.2f \u00b7 %d discriminating" % (sub.voi.max(), nd)
        if na:
            stats = "max VOI %.2f \u00b7 %d inadmissible" % (sub.voi.max(), na)
        ax.set_title("%s  %s\n%s" % (m, MNAME[m], stats), fontsize=5.7, pad=2.5,
                     linespacing=1.3,
                     fontweight="bold" if m == "M-HOLD-120" else "normal")
    # Left of the core block, so the label cannot read as belonging to it.
    pg.fig.text(9.5 / pg.W, 120 / pg.H, "tackifier-like (wt%)", fontsize=5.8,
                rotation=90, ha="center", va="center")
    pg.fig.text(97 / pg.W, 104.6 / pg.H, "acrylic-like modifier (wt%)",
                fontsize=5.8, ha="center", va="center")
    cb = pg.ax(14, 96.5, 26, 2.2)
    # Vector steps rather than imshow, so the figure carries no raster image.
    steps = np.linspace(0.10, 0.70, 61)
    for lo_, hi_ in zip(steps[:-1], steps[1:]):
        cb.add_patch(Rectangle((lo_, 0), hi_ - lo_ + 1e-4, 1,
                               fc=CMAP(NORM(0.5 * (lo_ + hi_))), ec="none"))
    cb.set_xlim(0.10, 0.70)
    cb.set_ylim(0, 1)
    cb.set_yticks([])
    cb.set_xticks([0.1, 0.4, 0.7])
    cb.tick_params(labelsize=5.2, length=1.4, pad=1)
    cb.text(0.72, 0.5, "VOI", fontsize=5.6, va="center", ha="left")
    kx = pg.canvas(52, 94.2, 130, 6)
    tile(kx, 1.2, 3.3, 2.4, 2.4, fc=VOI_RAMP[4], ec="none")
    kx.scatter([1.2], [3.3], s=1.5, c="white", lw=0)
    kx.text(3.2, 3.3, "hypothesis discrimination > 0", fontsize=5.4, va="center")
    tile(kx, 36.2, 3.3, 2.4, 2.4, fc=VOI_RAMP[5], ec=GRN, lw=1.0)
    kx.text(38.2, 3.3, "tied top set (5 cards)", fontsize=5.4, va="center")
    tile(kx, 63.2, 3.3, 2.4, 2.4, fc="white", ec=GRY_M, lw=0.35, hatch="//////")
    kx.text(65.2, 3.3, "inadmissible under the CBES chemistry rule", fontsize=5.4,
            va="center")
    kx.scatter([107.2], [3.3], s=26, fc="none", ec=GRN, lw=0.9)
    kx.text(109.2, 3.3, "selected, rule-complete", fontsize=5.4, va="center")

    # ---- B  VOI anatomy ----------------------------------------------------
    w = D.voi_weights()
    comp = [("hypothesis_discrimination", "discrimination", VOI_RAMP[5], +1),
            ("uncertainty_reduction", "uncertainty reduction", VOI_RAMP[4], +1),
            ("decision_relevance", "decision relevance", VOI_RAMP[3], +1),
            ("measurement_interpretability", "interpretability", VOI_RAMP[2], +1),
            ("extrapolation_risk", "extrapolation risk", GRY, -1),
            ("process_state_risk", "process-state risk", GRY_L, -1)]
    reps = [("S1C41::M-HOLD-120", "dual-axis 15/5, hold", "tied top"),
            ("S1C39::M-HOLD-120", "acrylic-only 15, hold", ""),
            (inv_rank1, "core-only E1, hold", "rank 1, inverted order"),
            ("S1C41::M-ANCHOR", "dual-axis 15/5, anchor", "CBES-inadmissible")]
    ax = pg.ax(33, 58, 42, 26)
    for i, (eid, lab, note) in enumerate(reps):
        r = cards[cards.experiment_id == eid].iloc[0]
        yv = len(reps) - 1 - i
        px, nx = 0.0, 0.0
        for c, _, col, sgn in comp:
            v = w[c] * getattr(r, "c_" + c)
            if v == 0:
                continue
            if sgn > 0:
                ax.barh(yv, v, left=px, height=0.58, color=col, lw=0, zorder=2)
                px += v
            else:
                ax.barh(yv, v, left=nx - v, height=0.58, color=col, lw=0, zorder=2)
                nx -= v
        assert abs(px + nx - r.voi) < 1e-3, eid
        ax.plot([r.voi, r.voi], [yv - 0.42, yv + 0.42], color=INK, lw=1.1, zorder=4)
        ax.text(px + 0.02, yv, "%.3f" % r.voi, fontsize=5.8, va="center",
                ha="left", fontweight="bold")
        ax.text(-0.13, yv + (0.14 if note else 0), lab, fontsize=5.6, va="center",
                ha="right")
        if note:
            ax.text(-0.13, yv - 0.3, note, fontsize=5.0, va="center", ha="right",
                    color=GRN_D if note == "tied top" else GRY_D)
    ax.axvline(0, color=INK, lw=0.6, zorder=3)
    ax.set_xlim(-0.12, 0.82)
    ax.set_ylim(-0.55, 3.55)
    ax.set_yticks([])
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8], ["0", "0.2", "0.4", "0.6", "0.8"])
    ax.tick_params(labelsize=5.6)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_xlabel("weighted contribution to VOI  (net VOI: black tick)",
                  fontsize=5.8, labelpad=1.5)
    hs = [Rectangle((0, 0), 1, 1, fc=col, lw=0) for _, _, col, _ in comp]
    lg = L.legend(ax, hs, [n for _, n, _, _ in comp], loc="upper center",
                  ncol=3, fontsize=5.0, handlelength=1.0, columnspacing=0.8,
                  bbox_to_anchor=(0.32, -0.30), frame=False)
    lg.set_in_layout(False)
    pg.letter("B", 2, 90)

    # ---- C  decision-space shift ------------------------------------------
    hold = cards[cards.measurement == "M-HOLD-120"]
    for k, a in enumerate(ARMS):
        ax = pg.ax(95 + k * 29, 60, 26, 20)
        for r in hold.itertuples():
            x, y, w_, h_ = pos(r.candidate_id, r.acrylic, r.tackifier)
            tile(ax, x, y, w_, h_, fc="#D6DCE4" if r.discrimination > 0 else GRY_XL,
                 ec="none", zorder=1)
            if r.tied_top:
                tile(ax, x, y, w_, h_, fc="none", ec=GRN, lw=0.8, zorder=2)
        sel = by[a].groupby(["candidate_id", "measurement"]).size()
        for (cid, meas), n in sel.items():
            r = hold[hold.candidate_id == cid].iloc[0]
            x, y, _, _ = pos(cid, r.acrylic, r.tackifier)
            col = (GRN_D if r.family == D.SUPPORTED_FAMILY else
                   C_OTHER if r.discrimination > 0 else GRY_D)
            hold_m = meas == "M-HOLD-120"
            yy = y if hold_m else y - 1.05
            ax.scatter([x], [yy], s=8 + 4 * n, marker="o" if hold_m else "s",
                       fc=col, ec="white", lw=0.5, zorder=5)
            ax.text(x + 0.62, yy, str(n), fontsize=5.4, color=col, ha="left",
                    va="center", fontweight="bold", zorder=6,
                    bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none",
                              alpha=0.85))
        lattice_frame(ax, ylab=(k == 0), fs=5.0)
        ax.set_title(ANAME[a], fontsize=6.0, pad=2, fontweight="bold")
    kc = pg.canvas(95, 49.5, 84, 5)
    kc.scatter([1.5], [2.5], s=14, marker="o", fc=INK, ec="white", lw=0.4)
    kc.text(3.2, 2.5, "hold", fontsize=5.3, va="center")
    kc.scatter([12.5], [2.5], s=14, marker="s", fc=INK, ec="white", lw=0.4)
    kc.text(14.2, 2.5, "repeatability", fontsize=5.3, va="center")
    tile(kc, 33.5, 2.5, 2.4, 2.2, fc="#D6DCE4", ec="none")
    kc.text(35.3, 2.5, "discriminating hold card", fontsize=5.3, va="center")
    kc.text(63, 2.5, "numbers: runs", fontsize=5.3, va="center")
    pg.letter("C", 84, 90)

    # ---- D  every run -----------------------------------------------------
    pg.letter("D", 2, 43)
    cv = pg.canvas(2, 2, 179, 38)
    tx, tw, th, gap = 44.0, 5.6, 4.8, 0.7
    rows_y = {"full": 26.0, "voi_withheld": 18.0, "order_inverted": 5.4}
    xs = tx + 10 * (tw + gap) + 2.0
    cols = [(xs + 7, "supported\nfamily"), (xs + 22, "zero\ndiscrimination"),
            (xs + 37, "hold\nselected")]
    for x, lab in cols:
        cv.text(x, 31.8, lab, fontsize=5.5, ha="center", va="bottom",
                linespacing=1.1, fontweight="bold")
    for a in ARMS:
        y = rows_y[a]
        r = by[a]
        cv.text(tx - 2.5, y + th / 2, ANAME[a], fontsize=6.0, ha="right",
                va="center", fontweight="bold")
        for i, row in enumerate(r.itertuples()):
            x = tx + i * (tw + gap)
            col = GRN if row.supported else C_OTHER if row.discrimination > 0 else C_ZERO
            cv.add_patch(Rectangle((x, y), tw, th, fc=col, ec="none", zorder=2))
            cv.text(x + tw / 2, y + th / 2,
                    "H" if row.measurement == "M-HOLD-120" else "R",
                    fontsize=5.0, color="white", ha="center", va="center",
                    fontweight="bold", zorder=3)
        n = len(r)
        sup, zero = int(r.supported.sum()), int((r.discrimination == 0).sum())
        hold_n = int((r.measurement == "M-HOLD-120").sum())
        for (x, _), txt, col in zip(cols, ("%d/%d" % (sup, n), "%d/%d" % (zero, n),
                                           "%d/%d" % (hold_n, n)),
                                    (GRN_D if sup else INK, GRY_D if zero else INK,
                                     INK)):
            cv.text(x, y + th / 2, txt, fontsize=6.6, fontweight="bold",
                    color=col, ha="center", va="center")
    # the critique track for the order-inverted arm
    c = crit[crit.arm == "order_inverted"].sort_values("run")
    yk = rows_y["order_inverted"] + th + 1.9
    for i, row in enumerate(c.itertuples()):
        x = tx + i * (tw + gap) + tw / 2
        if row.high_severity:
            cv.scatter([x - 1.1], [yk], marker="v", s=10, c=INK, lw=0, zorder=4)
        if row.robustness_change:
            cv.scatter([x + 1.2], [yk], marker="D", s=7, fc="white", ec=INK,
                       lw=0.6, zorder=4)
    cv.scatter([tx - 30.5], [yk], marker="v", s=10, c=INK, lw=0)
    cv.text(tx - 29.2, yk, "defect flagged", fontsize=5.2, ha="left", va="center")
    cv.scatter([tx - 14.6], [yk], marker="D", s=7, fc="white", ec=INK, lw=0.6)
    cv.text(tx - 13.3, yk, "change advised", fontsize=5.2, ha="left", va="center")
    nf, nc = int(c.high_severity.sum()), int(c.robustness_change.sum())
    cv.text(xs + 0.5, yk, "flagged %d/%d · change advised %d/%d · "
            "selection unchanged %d/%d" % (nf, len(c), nc, len(c), len(c), len(c)),
            fontsize=5.3, ha="left", va="center", color=INK)
    # tile key
    for dx, lab, col in ((0, "evidence-supported family", GRN),
                         (31, "other discriminating", C_OTHER),
                         (57, "zero discrimination", C_ZERO)):
        cv.add_patch(Rectangle((tx + dx, 0.0), 2.8, 2.4, fc=col, ec="none"))
        cv.text(tx + dx + 3.8, 1.2, lab, fontsize=5.3, va="center")
    cv.text(tx + 84, 1.2, "H hold \u00b7 R repeatability", fontsize=5.3,
            ha="left", va="center")

    L.audit(pg.fig)
    pg.save(HERE, "Fig4")


if __name__ == "__main__":
    main()
