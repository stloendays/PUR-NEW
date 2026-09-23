"""Render the hard-segment stack CIF to a transparent PNG with OVITO.

Runs in the OVITO environment, which has no matplotlib and no RDKit:

    D:/Tools/render-venv/Scripts/python.exe build_render.py

Covalent bonds come from element-pair cutoffs, not one global cutoff: a single
1.75 A cutoff also bonds the geminal H-H pairs inside a methyl group, which
draws triangles where there are none.

The hydrogen bonds are found rather than hard-coded, so the render cannot
disagree with the geometry the builder wrote. Distance alone will not do it: a
1.70-2.10 A H...O window also catches 20 intramolecular contacts inside the
carbamates and their methyl caps. A bond here must also be intermolecular,
donated by N-H, and bent by no more than 30 degrees from linear.

The camera looks along the direction of least spatial variance, which is the
view that shows the ladder rather than looking down it.
"""
import os
import sys

import numpy as np
from ovito.io import import_file
from ovito.modifiers import CreateBondsModifier
from ovito.pipeline import Pipeline, StaticSource
from ovito.vis import BondsVis, TachyonRenderer, Viewport

HERE = os.path.dirname(os.path.abspath(__file__))
CIF = os.path.join(HERE, "mdi_hard_segment_stack.cif")
OUT = os.path.join(HERE, "renders")
SIZE = (2600, 2200)

# House palette, so the render sits beside the drawn panels rather than beside
# a default CPK figure. Oxygen keeps red because the hydrogen bond is the
# subject of the panel.
COLOR = {"C": (0.42, 0.44, 0.47), "N": (0.35, 0.39, 0.50),
         "O": (0.92, 0.41, 0.41), "H": (0.88, 0.88, 0.88)}
RADIUS = {"C": 0.40, "N": 0.38, "O": 0.37, "H": 0.22}
PAIR_CUTOFF = {
    ("C", "C"): 1.70, ("C", "N"): 1.60, ("C", "O"): 1.55, ("C", "H"): 1.25,
    ("N", "H"): 1.15, ("N", "O"): 1.50, ("O", "H"): 1.10, ("N", "N"): 1.60,
    ("O", "O"): 1.55, ("H", "H"): 0.90,
}
HB_LO, HB_HI = 1.70, 2.10
BOND_COV = (0.45, 0.47, 0.50)
BOND_HB = (0.92, 0.41, 0.41)
HB_MIN_ANGLE = 150.0                               # deg, N-H...O
N_UNITS = 3                                        # units written by build_hardsegment.py


def main():
    os.makedirs(OUT, exist_ok=True)
    if not os.path.exists(CIF):
        sys.exit("missing %s -- run build_hardsegment.py first" % CIF)

    pipe = import_file(CIF)
    cb = CreateBondsModifier(mode=CreateBondsModifier.Mode.Pairwise)
    for (a, b), r in PAIR_CUTOFF.items():
        cb.set_pairwise_cutoff(a, b, r)
    pipe.modifiers.append(cb)
    data = pipe.compute()

    names = [data.particles.particle_types.type_by_id(int(t)).name
             for t in data.particles.particle_types]
    pos = np.array(data.particles.positions)
    print("%d particles, %d covalent bonds" % (len(names), data.particles.bonds.count))

    # OVITO shares type objects between pipeline stages; they must be requested
    # in mutable form or the assignment raises rather than being ignored.
    ptypes = data.particles_.particle_types_
    for t in list(ptypes.types):
        mt = ptypes.type_by_id_(t.id)
        mt.color = COLOR[t.name]
        mt.radius = RADIUS[t.name]

    covalent = {tuple(sorted(map(int, b))) for b in data.particles.bonds.topology}
    heavy_of = {}                                  # H index -> the atom it hangs off
    for a, b in covalent:
        if names[a] == "H" and names[b] != "H":
            heavy_of[a] = b
        elif names[b] == "H" and names[a] != "H":
            heavy_of[b] = a

    # Distance alone is not enough. A 1.7-2.1 A H...O window also catches the
    # intramolecular contacts inside a carbamate and its methyl cap -- 20 of
    # them here against the 2 real ones. A hydrogen bond is intermolecular,
    # donated by N-H, and near-linear.
    per_unit = len(names) // N_UNITS
    hb = []
    for i, ni in enumerate(names):
        if ni != "H" or names[heavy_of.get(i, i)] != "N":
            continue
        for j, nj in enumerate(names):
            if nj != "O" or i // per_unit == j // per_unit:
                continue
            d = float(np.linalg.norm(pos[i] - pos[j]))
            if not (HB_LO <= d <= HB_HI):
                continue
            n = heavy_of[i]
            v1, v2 = pos[n] - pos[i], pos[j] - pos[i]
            ang = float(np.degrees(np.arccos(np.clip(
                v1 @ v2 / (np.linalg.norm(v1) * np.linalg.norm(v2)), -1, 1))))
            if ang >= HB_MIN_ANGLE:
                hb.append((i, j, d, ang))
    print("hydrogen bonds: %d  %s"
          % (len(hb), ", ".join("%.2f A / %.0f deg" % (d, a) for *_, d, a in hb)))
    if not hb:
        sys.exit("no N-H...O contact in the expected range; the CIF is not what "
                 "the builder reported")

    n_cov = data.particles.bonds.count
    for i, j, _, _ in hb:
        data.particles_.bonds_.create_bond(i, j)
    n_all = data.particles.bonds.count

    col = np.tile(np.array(BOND_COV), (n_all, 1))
    col[n_cov:] = BOND_HB
    data.particles_.bonds_.create_property("Color", data=col)
    wid = np.full(n_all, 0.20)
    wid[n_cov:] = 0.085
    try:
        data.particles_.bonds_.create_property("Width", data=wid)
    except Exception as exc:                       # older OVITO: uniform width only
        print("per-bond Width unavailable (%s); hydrogen bonds keep the "
              "covalent width and are distinguished by colour" % type(exc).__name__)
    data.particles_.bonds_.vis = BondsVis(width=0.20,
                                          shading=BondsVis.Shading.Normal)

    # The box is vacuum padding with no physical meaning, so it must not be
    # drawn; left on, it is the most prominent thing in the render.
    data.cell_.vis.enabled = False

    # Look along the flattest direction so the ladder is seen side-on.
    c = pos.mean(axis=0)
    _, _, vt = np.linalg.svd(pos - c, full_matrices=False)
    view = vt[2]

    # OVITO picks the screen up-vector itself, so the safe field of view is the
    # largest in-plane radius rather than the extent along an axis we guessed.
    # The first attempt sized it from one axis and clipped the top unit off.
    rel = pos - c
    perp = rel - np.outer(rel @ view, view)
    fov = float(np.linalg.norm(perp, axis=1).max()) + 1.6

    # render_image draws the scene, so the edited DataCollection has to be
    # wrapped in its own pipeline; passing it as data= is silently not an option.
    scene = Pipeline(source=StaticSource(data=data))
    scene.add_to_scene()

    vp = Viewport(type=Viewport.Type.Ortho, camera_dir=tuple(-view),
                  camera_pos=tuple(c + view * 120.0), fov=fov)
    png = os.path.join(OUT, "hard_segment_stack.png")
    vp.render_image(size=SIZE, filename=png, background=(1, 1, 1), alpha=True,
                    renderer=TachyonRenderer(ambient_occlusion=True,
                                             ambient_occlusion_brightness=0.85,
                                             shadows=False,
                                             direct_light_intensity=0.95))
    print("wrote %s" % png)


if __name__ == "__main__":
    main()
