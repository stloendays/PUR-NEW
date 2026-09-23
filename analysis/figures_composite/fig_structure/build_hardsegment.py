"""Build an idealized hydrogen-bonded MDI hard-segment stack and write it as CIF.

What is real here and what is constructed, stated plainly because the figure
will be read as chemistry:

  * The molecule is dimethyl 4,4'-methylenediphenyl dicarbamate, the MDI unit
    capped at both ends by the urethane linkage this polymer actually forms.
    Its SMILES is unambiguous and its 3D geometry is MMFF94-optimized by RDKit.
    That part is ordinary computational chemistry, not an assumption.

  * The stack is constructed. One rigid transform -- a rotation and a
    translation -- is searched for, and applying it repeatedly generates the
    next unit each time, so successive units are related by a single operation
    and the N-H...O=C contact repeats along the stack.

  * The result is a finite cluster written into a P1 box with vacuum, not a
    crystal. The repository holds no measured structure and polyurethane of
    this composition is amorphous. The figure says so.

Three traps this script guards against, all hit while writing it:

  * translating along the N-H vector buries the units in one another, because
    MDI biscarbamate is long and a urethane ladder actually stacks laterally;

  * a blanket minimum-contact test counts the H...O hydrogen bond itself as a
    clash, so it fights the objective. The bonding pair is excluded and
    heavy-heavy and hydrogen-involving contacts get separate cutoffs;

  * a pure translation admits no solution for this conformer at all. The search
    therefore covers a rotation as well, which is also what a real urethane
    ladder looks like.

Every acceptance criterion is re-checked after the search, including the N...O
distance the search was optimizing. An earlier version checked only the clash
and the angle, and cheerfully wrote a "hydrogen bond" of 5.63 A.

    D:/Tools/pur_bridge_env/Scripts/python.exe build_hardsegment.py
"""
import os
import sys

import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation

HERE = os.path.dirname(os.path.abspath(__file__))

SMILES = "COC(=O)Nc1ccc(Cc2ccc(NC(=O)OC)cc2)cc1"   # dimethyl MDI-biscarbamate
TARGET_NO = 2.90                                   # N...O, A, a typical urethane H bond
TOL_NO = 0.15
MIN_ANGLE = 150.0                                  # deg, N-H...O near linear
MIN_HEAVY = 3.05                                   # A, heavy-heavy between units
MIN_WITH_H = 1.95                                  # A, any contact involving H
N_IMAGES = 3
PAD = 8.0


def optimized():
    m = Chem.AddHs(Chem.MolFromSmiles(SMILES))
    if AllChem.EmbedMolecule(m, randomSeed=0xF00D) != 0:
        sys.exit("embedding failed")
    AllChem.MMFFOptimizeMolecule(m, maxIters=2000)
    return m


def carbamate_sites(m):
    """(N, H on N, carbonyl C, carbonyl O) index tuples for each urethane group."""
    patt = Chem.MolFromSmarts("[NX3;H1][CX3](=[OX1])[OX2]")
    out = []
    for n, c, o, _ in m.GetSubstructMatches(patt):
        h = next(a.GetIdx() for a in m.GetAtomWithIdx(n).GetNeighbors()
                 if a.GetSymbol() == "H")
        out.append((n, h, c, o))
    return out


def images(P, p, k_max):
    """Unit 0 .. unit k_max, each obtained from the previous by one transform."""
    R = Rotation.from_rotvec(p[:3]).as_matrix()
    cen = P.mean(axis=0)
    out, X = [P], P
    for _ in range(k_max):
        X = (X - cen) @ R.T + cen + p[3:]
        out.append(X)
    return out


def geometry(P, isH, p, n, h, o):
    """H-bond geometry between consecutive units, and the worst clash."""
    U = images(P, p, 2)
    d_no = float(np.linalg.norm(U[1][o] - U[0][n]))
    d_ho = float(np.linalg.norm(U[1][o] - U[0][h]))
    v1, v2 = U[0][n] - U[0][h], U[1][o] - U[0][h]
    ang = float(np.degrees(np.arccos(np.clip(
        v1 @ v2 / (np.linalg.norm(v1) * np.linalg.norm(v2)), -1, 1))))

    hh = isH[:, None] | isH[None, :]
    heavy_min, h_min = np.inf, np.inf
    for i, j in ((0, 1), (0, 2), (1, 2)):
        d = np.linalg.norm(U[i][:, None, :] - U[j][None, :, :], axis=-1)
        if j == i + 1:
            d[n, o] = d[h, o] = np.inf                # the hydrogen bond itself
        heavy_min = min(heavy_min, float(d[~hh].min()))
        h_min = min(h_min, float(d[hh].min()))
    return d_no, d_ho, ang, heavy_min, h_min


def find_stack(P, isH, sites):
    """Search a rigid transform giving a repeating N-H...O=C contact."""
    best = None
    for (n, h, _, _) in sites:
        for (_, _, _, o) in sites:
            for seed in range(60):
                rng = np.random.default_rng(seed)
                p0 = np.concatenate([rng.normal(0, 0.7, 3),
                                     P[n] - P[o] + rng.normal(0, 4.0, 3)])

                def cost(p):
                    d_no, _, ang, hv, hm = geometry(P, isH, p, n, h, o)
                    rot = np.degrees(np.linalg.norm(p[:3]))
                    return ((d_no - TARGET_NO) ** 2
                            + 0.02 * max(0.0, MIN_ANGLE - ang) ** 2
                            + 25.0 * max(0.0, MIN_HEAVY + 0.10 - hv) ** 2
                            + 25.0 * max(0.0, MIN_WITH_H + 0.10 - hm) ** 2
                            # a real hard-segment ladder stacks near-parallel,
                            # so a large inter-unit rotation is a worse model
                            # even when it satisfies every hard constraint
                            + 0.0006 * rot ** 2)

                r = minimize(cost, p0, method="Nelder-Mead",
                             options=dict(maxiter=20000, maxfev=20000,
                                          xatol=1e-4, fatol=1e-8))
                d_no, d_ho, ang, hv, hm = geometry(P, isH, r.x, n, h, o)
                if (abs(d_no - TARGET_NO) > TOL_NO or ang < MIN_ANGLE
                        or hv < MIN_HEAVY or hm < MIN_WITH_H):
                    continue
                score = (abs(d_no - TARGET_NO) - 0.02 * min(hv, 6.0)
                         + 0.006 * np.degrees(np.linalg.norm(r.x[:3])))
                if best is None or score < best[0]:
                    best = (score, r.x, d_no, d_ho, ang, hv, hm, n, h, o)
    if best is None:
        sys.exit("no feasible stacking transform found")
    return best


def main():
    m = optimized()
    P = m.GetConformer().GetPositions()
    sym = [a.GetSymbol() for a in m.GetAtoms()]
    isH = np.array([s == "H" for s in sym])
    sites = carbamate_sites(m)
    if len(sites) != 2:
        sys.exit("expected two carbamate groups, found %d" % len(sites))

    _, p, d_no, d_ho, ang, hv, hm, n_d, h_d, o_a = find_stack(P, isH, sites)
    rot_deg = np.degrees(np.linalg.norm(p[:3]))
    print("rotation per unit      %.1f deg" % rot_deg)
    print("translation per unit   %.3f A" % np.linalg.norm(p[3:]))
    print("N...O                  %.3f A   (target %.2f)" % (d_no, TARGET_NO))
    print("H...O                  %.3f A" % d_ho)
    print("N-H...O angle          %.1f deg" % ang)
    print("closest heavy-heavy    %.3f A   (min %.2f)" % (hv, MIN_HEAVY))
    print("closest involving H    %.3f A   (min %.2f)" % (hm, MIN_WITH_H))

    assert abs(d_no - TARGET_NO) <= TOL_NO, "N...O out of tolerance"
    assert ang >= MIN_ANGLE, "N-H...O angle too bent"
    assert hv >= MIN_HEAVY and hm >= MIN_WITH_H, "steric clash"

    U = images(P, p, N_IMAGES - 1)
    coords = np.vstack(U)
    symbols = sym * N_IMAGES
    span = coords.max(axis=0) - coords.min(axis=0)
    a, b, c = span + 2 * PAD
    origin = coords.min(axis=0) - PAD
    frac = (coords - origin) / np.array([a, b, c])

    cif = os.path.join(HERE, "mdi_hard_segment_stack.cif")
    with open(cif, "w", encoding="utf-8") as fh:
        fh.write("# Idealized N-H...O=C bonded MDI hard-segment stack.\n"
                 "# Single-unit geometry: MMFF94 (RDKit). Stacking: constructed by a\n"
                 "# searched rigid transform (%.1f deg rotation + %.2f A translation\n"
                 "# per unit), giving N...O = %.3f A and N-H...O = %.1f deg.\n"
                 "# A MODEL of the urethane association, NOT a measured crystal\n"
                 "# structure; this polymer is amorphous. The box is vacuum padding,\n"
                 "# not a unit cell with physical meaning.\n"
                 "# Built by analysis/figures_composite/fig_structure/"
                 "build_hardsegment.py\n"
                 % (rot_deg, np.linalg.norm(p[3:]), d_no, ang))
        fh.write("data_mdi_hard_segment_stack\n")
        fh.write("_chemical_name_common 'dimethyl MDI-biscarbamate, %d-unit stack'\n"
                 % N_IMAGES)
        for k, v in (("a", a), ("b", b), ("c", c)):
            fh.write("_cell_length_%s %.5f\n" % (k, v))
        for k in ("alpha", "beta", "gamma"):
            fh.write("_cell_angle_%s 90.0\n" % k)
        fh.write("_symmetry_space_group_name_H-M 'P 1'\n_symmetry_Int_Tables_number 1\n")
        fh.write("loop_\n_atom_site_label\n_atom_site_type_symbol\n"
                 "_atom_site_fract_x\n_atom_site_fract_y\n_atom_site_fract_z\n")
        for idx, (s, f) in enumerate(zip(symbols, frac)):
            fh.write("%s%d %s %.6f %.6f %.6f\n" % (s, idx + 1, s, f[0], f[1], f[2]))

    marks = np.array([np.vstack([U[k][h_d], U[k + 1][o_a], U[k][n_d]]) - origin
                      for k in range(N_IMAGES - 1)])
    np.save(os.path.join(HERE, "_hbond_marks.npy"), marks)
    with open(os.path.join(HERE, "model_stats.txt"), "w", encoding="utf-8") as fh:
        fh.write("N_O %.3f\nH_O %.3f\nangle %.1f\nheavy_min %.3f\nh_min %.3f\n"
                 "rot_deg %.2f\ntrans %.3f\ncell_a %.3f\ncell_b %.3f\ncell_c %.3f\n"
                 "n_atoms %d\nn_units %d\n"
                 % (d_no, d_ho, ang, hv, hm, rot_deg, np.linalg.norm(p[3:]),
                    a, b, c, len(symbols), N_IMAGES))
    print("wrote %s  (%d atoms, box %.2f x %.2f x %.2f A)"
          % (os.path.basename(cif), len(symbols), a, b, c))


if __name__ == "__main__":
    main()
