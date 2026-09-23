"""Figure 1 - the chemistry the formulation controls, and the loop built on it.

Panel a is drawn atom-for-atom where the formula is public: PPG2000 is a polypropylene
glycol diol and 4,4'-MDI is 4,4'-methylenediphenyl diisocyanate. STEPANPOL PDP-70 is a
supplier aromatic polyester polyol whose exact backbone is not public, so it is a
labelled block rather than a guessed structure.

Panel b is the urethane N-H...O=C association in the hard segment, beside the measured
120 C drift. It shows the chemistry the formulation varies; it does not claim the drift
is caused by this association, which nothing in the repository measures.

    pur_bridge_env/python make_fig1.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import chem as C                                                  # noqa: E402
import layout as L                                                # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch    # noqa: E402
from style import DARK_B, INK, MID, PALE_B, RED, TINT_B, TINT_G, Page  # noqa: E402

W, H = 183.0, 124.0
GREEN_D = "#5E7A52"


def arrow(ax, p, q, color=MID, lw=0.9, ms=2.4, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms * 3.2,
                                 lw=lw, color=color, linestyle=ls,
                                 shrinkA=0, shrinkB=0, zorder=3))


# ---------------------------------------------------------------- panel a ---
def panel_a(page):
    ax = page.canvas(4, 82, 175, 38)
    yb = 20.0                                       # backbone line of the row

    # --- PPG2000: HO-CH2-CH(CH3)-[O-CH2-CH(CH3)]n-OH --------------------------
    # The chain must end on carbon. Terminating on the ether oxygen would draw a
    # peroxide, which is what a first pass of this panel actually showed.
    # Vertices: p0 = O of HO, p1 CH2, p2 CH(CH3), p3 ether O, p4 CH2,
    # p5 CH(CH3), p6 = O of OH. The terminal labels sit ON p0 and p6 so the
    # oxygens are unambiguous; they used to float 2 mm off the chain ends.
    p = C.zig((6.0, yb), 6, up_first=True)
    C.chain(ax, p)
    C.atom(ax, (p[0][0] + 0.7, p[0][1]), "HO", ha="right")
    C.atom(ax, p[3], "O")                            # the single ether oxygen shown
    C.atom(ax, (p[6][0] - 0.7, p[6][1]), "OH", ha="left")
    # A substituent leaves its carbon on the exterior of the chain angle: down
    # from a valley vertex, up from a peak. The p5 methyl was drawn down into
    # the angle, putting all three bonds of that carbon in one half-plane.
    for i in (2, 5):
        peak = p[i][1] > yb + 0.1
        C.bond(ax, p[i], (p[i][0], p[i][1] + (2.1 if peak else -2.1)))
    # Repeat unit [O-CH2-CH(CH3)]n. The left bracket crosses the CH-O bond
    # (p2-p3) and the right one the CH-OH bond (p5-p6); both open inward. The
    # first version put the left bracket one bond early, enclosing
    # [CH(CH3)-O-CH2-CH(CH3)], which does not repeat into PPG, and drew both
    # brackets facing outward so they enclosed nothing.
    xl = (p[2][0] + p[3][0]) / 2.0
    xr = (p[5][0] + p[6][0]) / 2.0
    for xb, serif in ((xl, +0.6), (xr, -0.6)):
        ax.plot([xb + serif, xb, xb, xb + serif],
                [yb - 3.6, yb - 3.6, yb + 3.6, yb + 3.6], lw=0.7, color=MID, zorder=1)
    ax.text(xr + 0.3, yb - 3.9, "n", fontsize=5.0, color=MID, ha="left", va="top")
    ax.text(p[3][0], yb - 8.6, "PPG2000", fontsize=6.2, ha="center", fontweight="bold")
    ax.text(p[3][0], yb - 11.6, "polyether diol, $M_n$ 2000", fontsize=5.4, ha="center",
            color=MID)
    ax.text(p[3][0], yb + 9.2, "soft segment", fontsize=5.4, ha="center", color=GREEN_D,
            fontweight="bold")

    ax.text(30.5, yb, "+", fontsize=8, ha="center", va="center", color=MID)

    # --- STEPANPOL PDP-70, backbone not public --------------------------------
    C.block(ax, 35.0, yb - 5.0, 25.0, 10.0, "PDP-70", "aromatic polyester diol",
            fc=TINT_G, ec=GREEN_D)
    ax.text(47.5, yb - 8.6, "STEPANPOL", fontsize=6.2, ha="center", fontweight="bold")
    ax.text(47.5, yb - 11.6, "supplier polyol", fontsize=5.4, ha="center", color=MID)
    ax.text(47.5, yb + 9.2, "soft segment", fontsize=5.4, ha="center", color=GREEN_D,
            fontweight="bold")

    ax.text(64.5, yb, "+", fontsize=8, ha="center", va="center", color=MID)

    # --- 4,4'-MDI: OCN-C6H4-CH2-C6H4-NCO --------------------------------------
    r1 = C.benzene(ax, (79.0, yb), rot=0)
    r2 = C.benzene(ax, (96.0, yb), rot=0)
    mid = ((r1[0][0] + r2[3][0]) / 2.0, yb + 1.5)
    C.bond(ax, r1[0], mid)                            # the methylene bridge
    C.bond(ax, mid, r2[3])
    # The isocyanate is written in condensed form, OCN- / -NCO, as polyurethane
    # schemes conventionally do. Drawn skeletally, N=C=O is linear, so an
    # implicit carbon sits on a straight line between two double bonds and
    # vanishes: the group read as O=N, a nitroso group, which is what this panel
    # showed until it was read as chemistry. Labelling that carbon instead left
    # 2.2 mm bonds almost entirely under the label boxes, and there is no room
    # to lengthen them before the O runs into the "+".
    for ring, vert, sgn in ((r1, r1[3], -1), (r2, r2[0], +1)):
        n = (vert[0] + sgn * 2.4, vert[1])
        C.bond(ax, vert, n)
        if sgn < 0:
            C.atom(ax, (n[0] + 0.9, n[1]), "OCN", ha="right")
        else:
            C.atom(ax, (n[0] - 0.9, n[1]), "NCO", ha="left")
    ax.text(87.5, yb - 8.6, "4,4'-MDI", fontsize=6.2, ha="center", fontweight="bold")
    ax.text(87.5, yb - 11.6, "diisocyanate, NCO:OH 1.70-1.90", fontsize=5.4, ha="center",
            color=MID)
    ax.text(87.5, yb + 9.2, "hard segment", fontsize=5.4, ha="center", color=DARK_B,
            fontweight="bold")

    # --- reaction arrow -------------------------------------------------------
    arrow(ax, (112.0, yb), (126.0, yb), color=INK, lw=1.0, ms=2.8)
    ax.text(119.0, yb + 2.2, "130 → 120 °C", fontsize=5.4,
            ha="center", color=MID)
    ax.text(119.0, yb - 3.4, "vacuum", fontsize=5.4, ha="center", color=MID)

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
                                fc="none", ec=DARK_B, lw=0.7, ls=(0, (2.4, 1.6)),
                                zorder=1))
    ax.text(u + 6.3, yb - 8.6, "urethane linkage", fontsize=6.2, ha="center",
            fontweight="bold")
    ax.text(u + 6.3, yb - 11.6, "prepolymer", fontsize=5.4, ha="center", color=MID)


# ---------------------------------------------------------------- panel b ---
def panel_b(page):
    ax = page.canvas(4, 6, 56, 68)

    def urethane(y, flip=False, x0=8.0):
        """One urethane group along x, its N-H and C=O pointing at the partner."""
        s = -1 if flip else 1
        C.bond(ax, (x0, y), (x0 + 3.0, y))
        C.atom(ax, (x0 + 3.0, y), "O")
        C.bond(ax, (x0 + 3.0, y), (x0 + 6.4, y))
        tip = (x0 + 6.4, y + s * 3.0)
        C.bond(ax, (x0 + 6.4, y), tip, 2)
        C.atom(ax, (tip[0], tip[1] + s * 0.7), "O")
        C.bond(ax, (x0 + 6.4, y), (x0 + 9.8, y))
        C.atom(ax, (x0 + 9.8, y), "N")
        h = (x0 + 9.8, y + s * 2.7)
        C.bond(ax, (x0 + 9.8, y), h)
        C.atom(ax, (h[0], h[1] + s * 0.6), "H", size=5.0)
        C.bond(ax, (x0 + 9.8, y), (x0 + 12.8, y))
        return tip, h

    # Offset the upper group so its C=O sits directly over the lower N-H. Only that
    # one contact is drawn: with a rigid offset the reciprocal pair cannot also be
    # vertical, and crossing the two dotted lines would draw a geometry that does
    # not exist.
    _, h_low = urethane(31.0, flip=False, x0=6.0)
    o_up, _ = urethane(44.0, flip=True, x0=6.0 + 3.4)

    C.hbond(ax, (h_low[0], h_low[1] + 1.4), (o_up[0], o_up[1] - 1.4))
    ax.text(h_low[0] + 1.6, 37.5, "N$-$H$\\cdots$O=C", fontsize=6.0, color=RED,
            fontweight="bold", ha="left", va="center")
    ax.text(h_low[0] + 1.6, 34.2, "hard-segment association", fontsize=5.4, color=MID,
            ha="left", va="center")

    ax.text(2.0, 66.0, "What the hold measures", fontsize=6.4, fontweight="bold",
            ha="left", va="top")
    # States what is measured, not why. An earlier wording said holding "lets
    # this association keep building", a mechanism nothing in the repository
    # measures; the drift itself and the fixed composition are measured.
    ax.text(2.0, 62.0,
            "At 120 °C the composition is fixed, yet viscosity\n"
            "still changes with time. Drift is therefore a coordinate\n"
            "of its own, not a second reading of temperature\n"
            "response.",
            fontsize=5.6, ha="left", va="top", color=INK, linespacing=1.45)

    ax.add_patch(FancyBboxPatch((1.0, 8.0), 54.0, 10.0,
                                boxstyle="round,pad=0,rounding_size=1.0",
                                fc=TINT_B, ec=PALE_B, lw=0.7, zorder=1))
    ax.text(28.0, 14.6, "E1 $+$9.51%    E5 $+$51.54%", fontsize=6.0, ha="center",
            fontweight="bold", zorder=4)
    ax.text(28.0, 10.8, "15→60 min at 120 °C, same window",
            fontsize=5.4, ha="center", color=MID, zorder=4)


# ---------------------------------------------------------------- panel c ---
def panel_c(page):
    ax = page.canvas(64, 6, 115, 68)
    nodes = [
        ("1  Hidden state", "same recipe,\ndifferent measured state",
         "one-point calibration", TINT_B, PALE_B),
        ("2  Failure mode", "thermal-hold drift is\nformulation sensitive",
         "the actionable coordinate", TINT_B, PALE_B),
        ("3  Hypotheses", "H-CORE   H-RESIN\nH-DUAL", "falsifiable and registered",
         "#FDECEC", RED),
        ("4  Experiment", "formulation $\\times$ measurement,\nranked by VOI",
         "selected before the result", TINT_B, PALE_B),
        ("5  Adjudication", "wet-lab thermal hold", "physics decides", TINT_G, GREEN_D),
    ]
    bw, gap, y0, bh = 19.6, 4.35, 30.0, 26.0
    cx = []
    for i, (title, body, foot, fc, ec) in enumerate(nodes):
        x = i * (bw + gap)
        cx.append(x + bw / 2)
        ax.add_patch(FancyBboxPatch((x, y0), bw, bh,
                                    boxstyle="round,pad=0,rounding_size=1.2",
                                    fc=fc, ec=ec, lw=0.8, zorder=2))
        ax.text(x + bw / 2, y0 + bh - 3.4, title, fontsize=6.0, ha="center",
                fontweight="bold", zorder=4)
        ax.text(x + bw / 2, y0 + bh - 8.2, body, fontsize=5.3, ha="center", va="top",
                zorder=4, linespacing=1.3)
        ax.text(x + bw / 2, y0 + 2.2, foot, fontsize=4.9, ha="center", color=MID,
                zorder=4)
        if i:
            arrow(ax, (x - gap + 0.5, y0 + bh / 2), (x - 0.6, y0 + bh / 2), color=INK)

    # the loop that closes back on the hypotheses
    y_ret = 20.0
    ax.add_line(__import__("matplotlib").lines.Line2D(
        [cx[4], cx[4]], [y0, y_ret], lw=0.9, color=RED, zorder=3))
    ax.add_line(__import__("matplotlib").lines.Line2D(
        [cx[2], cx[4]], [y_ret, y_ret], lw=0.9, color=RED, zorder=3))
    arrow(ax, (cx[2], y_ret), (cx[2], y0 - 0.6), color=RED)
    ax.text((cx[2] + cx[4]) / 2, y_ret - 3.0,
            "the measured outcome updates the hypothesis state", fontsize=5.4,
            ha="center", color=RED)

    ax.add_patch(FancyBboxPatch((0.0, 3.0), 115.0, 11.0,
                                boxstyle="round,pad=0,rounding_size=1.0",
                                fc="#FAFAFA", ec=PALE_B, lw=0.7, zorder=1))
    ax.text(57.5, 10.2, "measured drift 1.60%     proportional-dilution null 7.79%",
            fontsize=6.2, ha="center", fontweight="bold", zorder=4)
    ax.text(57.5, 6.0, "H-CORE falsified under the frozen acceptance rule; H-RESIN retained",
            fontsize=5.4, ha="center", color=MID, zorder=4)


def main():
    page = Page(W, H)
    panel_a(page)
    panel_b(page)
    panel_c(page)
    page.letter("a", 2.0, H - 1.0)
    page.title("The formulation chemistry the workflow acts on", 8.0, H - 1.0)
    page.letter("b", 2.0, 78.0)
    page.title("Hard-segment association", 8.0, 78.0)
    page.letter("c", 62.0, 78.0)
    page.title("One closed loop, from rheological state to physical adjudication",
               68.0, 78.0)
    L.audit(page.fig)
    page.save(HERE, "Fig1")


if __name__ == "__main__":
    main()
