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
