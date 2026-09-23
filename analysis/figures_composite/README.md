# Composite main figures

Built the way the Catalyst-Essay figures are built: matplotlib assembles each figure on
a page measured in millimetres, schematics are drawn rather than exported, and every
figure is written as SVG, PDF and PNG at 600 dpi in one pass.

- `style.py` — the shared visual system, taken unchanged from Catalyst-Essay so the two
  manuscripts look like they came from one group. 183 mm pages, Arial 5.3-9 pt, ticks
  in, pastel blue/green with one red for the element a panel is about.
- `chem.py` — skeletal-formula primitives. Structures here are repeat units and
  linkages, which chemistry journals draw as 2D skeletal formulae rather than render
  as 3D atoms.
- `figN/make_figN.py` — one script per figure. Run with the project interpreter.

```
/d/Tools/pur_bridge_env/Scripts/python.exe fig1/make_fig1.py
```

## What is drawn atom-for-atom, and what is not

PPG2000 and 4,4'-MDI have public, unambiguous formulae and are drawn atom-for-atom.
STEPANPOL PDP-70 is a supplier aromatic polyester polyol whose exact backbone is not
public, so it is a labelled block. Drawing a guessed backbone would be an invented
structure in a figure that otherwise reports measurements.

The urethane N-H...O=C contact in Fig 1b is drawn as a single vertical hydrogen bond.
With a rigid offset between two urethane groups the reciprocal contact cannot also be
vertical, so drawing both would show a geometry that does not exist.

## Additional composites (2026-09-23)

Built on the same `style.py` as Fig 1. All read the repository tables through
`figdata.py`, so every number in them is derived, not transcribed.

| Directory | Size | What it claims |
|---|---|---|
| `fig_arrhenius/` | 183 x 86 mm | Seven realizations share a local thermal response; E_eta scatters by 2.43 kJ/mol around 42.05; a linear Arrhenius form costs 11.8 % held-temperature error against 5.5 % for VFT. |
| `fig_column/` | 120 x 152 mm | The same property for each realization, stacked in one column against the other six in grey, so level and slope compare directly. |
| `fig_structure/` | 183 x 88 mm | The N-H...O=C association, as a 3D model, a 2D unit and the geometry achieved. |
| `fig_hold/` | 183 x 64 mm | F1 holds flat at 120 C while E5 runs away; the 1.60 % mean absolute drift falls below the 7.79 % proportional-dilution null. |

### `figdata.py`

One loader for every figure. Two things it fixes that are easy to get wrong:

* **The hold window is 15-60 min, matched.** E1 and E5 ran to 90 min and the
  validation repeats only to 60, so a first-to-last drift would compare 75
  minutes against 45. The manuscript's 9.51 %, 51.54 % and 1.60 % are all
  15-60 min, and `hold_drift()` reproduces them exactly.
* **E1 +P is never pooled.** It is a deliberate H3PO4 perturbation and sits
  outside the primary population; `primary()` excludes it, giving n = 6,
  42.05 +- 2.43 kJ/mol, CV 5.77 %.

### The structure model

`fig_structure/` carries a CIF this repository generated; there was no measured
structure to use and this polymer is amorphous.

* The unit is dimethyl 4,4'-methylenediphenyl dicarbamate, MMFF94-optimized
  from SMILES by RDKit. That part is ordinary computational chemistry.
* The three-unit stack is **constructed**: a rigid transform is searched for
  under explicit acceptance criteria (N...O 2.90 +- 0.15 A, N-H...O >= 150 deg,
  no heavy-heavy contact below 3.05 A), then every criterion is re-checked on
  the result. It achieved N...O 2.92 A, N-H...O 164 deg, closest heavy contact
  3.20 A.
* It is a model of the association, not a crystal structure, and the figure
  says so on its face.

Three things the builder now refuses to do, each hit during development:
translating along N-H (buries the units in one another), counting the H...O
bond itself as a steric clash (fights its own objective), and accepting a
solution without re-checking the N...O distance it was optimizing -- that last
one once wrote a "hydrogen bond" of 5.63 A with every other check passing.
