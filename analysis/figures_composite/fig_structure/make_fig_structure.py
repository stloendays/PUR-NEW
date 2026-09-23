"""Hard-segment association: the modelled stack, the unit, and the geometry.

a  The three-unit stack rendered from mdi_hard_segment_stack.cif (OVITO).
b  The unit itself as a 2D skeletal formula, drawn by RDKit from the same
   SMILES the 3D model was built from, so the two panels cannot disagree.
c  The hydrogen-bond geometry the model actually achieved, drawn to the same
   bond length as every other schematic in this manuscript.

Panel c reports numbers read from model_stats.txt rather than repeating them by
hand, so the figure cannot drift away from the structure on disk.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig_structure.py
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chem as C
from style import DARK_B, GRID, INK, MID, PALE_B, RED, Page, crop_rgba

HERE = os.path.dirname(os.path.abspath(__file__))
SMILES = "COC(=O)Nc1ccc(Cc2ccc(NC(=O)OC)cc2)cc1"


def stats():
    out = {}
    with open(os.path.join(HERE, "model_stats.txt"), encoding="utf-8") as fh:
        for line in fh:
            k, v = line.split()
            out[k] = float(v)
    return out


def rdkit_png(px=(2200, 620)):
    from rdkit import Chem
    from rdkit.Chem import rdDepictor
    from rdkit.Chem.Draw import rdMolDraw2D

    m = Chem.MolFromSmiles(SMILES)
    rdDepictor.Compute2DCoords(m)
    d = rdMolDraw2D.MolDraw2DCairo(*px)
    o = d.drawOptions()
    o.baseFontSize = 0.62
    o.bondLineWidth = 5
    o.useBWAtomPalette()                 # ink only, to match the drawn panels
    o.setBackgroundColour((1, 1, 1, 0))
    d.DrawMolecule(m)
    d.FinishDrawing()
    return d.GetDrawingText()


def urethane(ax, y, x0, flip):
    """-NH-C(=O)-O- at height y; flip puts the N-H up and the carbonyl down."""
    s = -1 if flip else 1
    n, c, o_e = (x0, y), (x0 + C.L, y + s * 1.3), (x0 + 2 * C.L, y)
    C.bond(ax, n, c)
    C.bond(ax, c, o_e)
    C.atom(ax, n, "N")
    h = (n[0], n[1] - s * 1.9)
    C.atom(ax, h, "H", size=5.0)
    C.atom(ax, o_e, "O")
    tip = C.carbonyl(ax, c, up=not flip)
    return (tip[0], tip[1] - (0.55 if flip else -0.55)), h


def main():
    import matplotlib.image as mpimg

    st = stats()
    pg = Page(183.0, 88.0)

    # ---- a  the rendered stack ------------------------------------------
    # The projection of a stack of long molecules is a diagonal band, so its
    # two off-diagonal corners are always empty. The key and the run
    # description go there rather than below the panel.
    img = crop_rgba(os.path.join(HERE, "renders", "hard_segment_stack.png"), pad=4)
    h_px, w_px = img.shape[0], img.shape[1]
    box_w, box_h = 74.0, 83.0
    scale = min(box_w / w_px, box_h / h_px)
    w, h = w_px * scale, h_px * scale
    ax = pg.canvas(3.0 + (box_w - w) / 2.0, 2.5 + (box_h - h) / 2.0, w, h)
    ax.imshow(img, extent=[0, w, 0, h], zorder=2)

    ax.plot([w * 0.40, w * 0.47], [h * 0.955, h * 0.955], lw=1.1, color=RED,
            solid_capstyle="round", zorder=4)
    ax.text(w * 0.49, h * 0.955, "N\u2013H\u00b7\u00b7\u00b7O=C", fontsize=5.8,
            color=RED, ha="left", va="center", fontweight="bold")
    ax.text(w * 0.49, h * 0.905, "2 contacts, %.2f \u00c5" % st["H_O"],
            fontsize=5.2, color=MID, ha="left", va="center")
    # bottom-right, right-aligned: the bottom-LEFT is where the lowest unit
    # sits, and the first attempt put this text behind it
    ax.text(w * 0.99, h * 0.02,
            "%d units \u00b7 %d atoms\n%.0f\u00b0 twist, %.2f \u00c5 offset per unit"
            % (st["n_units"], st["n_atoms"], st["rot_deg"], st["trans"]),
            fontsize=5.2, color=MID, ha="right", va="bottom", linespacing=1.5)
    pg.letter("a", 2.0, 86)

    # ---- b  the unit, 2D -------------------------------------------------
    png = rdkit_png()
    mol = mpimg.imread(io.BytesIO(png), format="png")
    mh, mw = mol.shape[0], mol.shape[1]
    bw = 100.0
    bh = bw * mh / mw
    ax = pg.canvas(80.0, 54.0, bw, bh)
    ax.imshow(mol, extent=[0, bw, 0, bh], zorder=2)
    pg.letter("b", 77, 86)
    pg.fig.text(80.0 / pg.W, 51.0 / pg.H,
                "dimethyl 4,4'-methylenediphenyl dicarbamate \u2014 the MDI unit "
                "closed by the urethane linkage",
                fontsize=5.4, color=MID, va="bottom", ha="left")

    # ---- c  the geometry the model achieved ------------------------------
    cv = pg.canvas(80.0, 3.0, 100.0, 45.0)
    X = 19.0
    _, h_low = urethane(cv, 15.0, X, flip=True)
    o_up, _ = urethane(cv, 29.0, X - C.L, flip=True)
    C.hbond(cv, (h_low[0], h_low[1] + 0.9), (o_up[0], o_up[1] - 0.9))
    cv.annotate("", (X + 2.2, h_low[1] + 1.0), (X + 2.2, o_up[1] - 1.0),
                arrowprops=dict(arrowstyle="<->", color=MID, lw=0.5,
                                shrinkA=0, shrinkB=0))
    cv.text(X + 3.0, (h_low[1] + o_up[1]) / 2.0,
            "H\u00b7\u00b7\u00b7O\n%.2f \u00c5" % st["H_O"], fontsize=5.6, color=INK,
            ha="left", va="center", linespacing=1.5)

    rows = [("N\u00b7\u00b7\u00b7O", "%.2f \u00c5" % st["N_O"]),
            ("N\u2013H\u00b7\u00b7\u00b7O", "%.0f\u00b0" % st["angle"]),
            ("closest heavy\u2013heavy", "%.2f \u00c5" % st["heavy_min"])]
    x0, x1 = 44.0, 99.0
    cv.text(x0, 42.0, "model geometry", fontsize=5.6, color=INK,
            ha="left", va="center", fontweight="bold")
    for i, (k, v) in enumerate(rows):
        yy = 36.6 - i * 4.4
        cv.text(x0, yy, k, fontsize=5.6, color=MID, ha="left", va="center")
        cv.text(x1, yy, v, fontsize=5.6, color=INK, ha="right", va="center",
                fontweight="bold")
    cv.plot([x0, x1], [39.2, 39.2], lw=0.5, color=GRID)
    cv.plot([x0, x1], [16.8, 16.8], lw=0.5, color=GRID)
    cv.text(x0, 13.4,
            "Single-unit geometry MMFF94. The stack is a constructed\n"
            "model of the association, not a measured structure \u2014 this\n"
            "polymer is amorphous and the repository holds no structure.",
            fontsize=5.2, color=RED, ha="left", va="top", linespacing=1.55)
    cv.text(x0, 1.6, "mdi_hard_segment_stack.cif", fontsize=5.0, color=MID,
            ha="left", va="bottom", family="monospace")
    pg.letter("c", 77, 48)

    pg.save(HERE, "Fig_structure")


if __name__ == "__main__":
    main()
