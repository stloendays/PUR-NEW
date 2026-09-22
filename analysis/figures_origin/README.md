# Origin panel set (PUR-NEW V5 figures, split and unified)

Every V5 main-text data panel is rebuilt as its own Origin graph, with one colour
per physical entity shared across all panels. The R multi-panel figures in
`analysis/figures/` are untouched.

Two generations are kept:

- **`panels_v2/` — current.** Single-column typography (89 × 70 mm page), varied
  chart forms, PNG rasterized from the cleaned SVG.
- `panels/` — first pass. Same data and palette, default page size, line/bar
  throughout.

## Files

- `panels_v2/FigNX.svg` — vector master, 89 × 70 mm.
- `panels_v2/FigNX.png` — 2000 px, rasterized from that SVG.
- `PUR_NEW_panels_v2.opju` / `PUR_NEW_panels.opju` — the Origin projects.
- `data/p*.csv` — v2 panel tables; `data/fig*.csv` — v1 tables. Column long
  names are the legend labels.
- `scripts/` — rebuilds the tables and post-processes the exports.

## Panels and chart forms

| Panel | v2 form | Content |
|---|---|---|
| Fig2A | line + symbol, log Y | E2 realizations, raw viscosity |
| Fig2B | line + symbol, log Y | E2 realizations, state-adjusted viscosity |
| Fig2C | line + symbol vs grey reference | PC1 loading vs ideal constant shift |
| Fig2D | slope (paired change) | leave-one-temperature-out error, two models |
| Fig3A | line + acceptance reference | pooled one-point transfer error vs anchor |
| Fig3B | dot plot | held-out formulation error, 120 °C anchor |
| Fig3C | parity scatter, log-log | bounded extrapolation |
| Fig4A | point + Wilson 95% whisker | supported-family selection rate |
| Fig4B | dot plot | mean hypothesis discrimination |
| Fig4C | point + Wilson 95% whisker | matched 120 °C hold selection rate |
| Fig4D | slope trajectory | critique stages, minimality-first arm |
| Fig5A | jittered strip + mean line | apparent E across audited realizations |
| Fig5B | line + symbol | normalized 120 °C hold trajectories |
| Fig5C | column, per-entity fill | matched-window 15→60 min drift |
| Fig5D | two-descriptor dot plot | the two native rheological descriptors |

Interval panels carry an explicit (x, y) pair per whisker with a NaN break
between arms, so the confidence interval is drawn from the exact Wilson bounds
rather than from a symmetric error-bar approximation.

## Typography (v2)

Page 89 × 70 mm (`page.width=3504; page.height=2756`), layer at
`layer.unit=7; left=17; top=8; width=78; height=76`.

| Element | Size |
|---|---|
| Axis titles | Arial 8 pt |
| Tick labels | Arial 7 pt |
| Legend | Arial 7 pt |
| Axis line | 0.75 |
| Data lines | `-w 900` (≈0.9 pt) |
| Symbols | `-z 4..8` |

Ticks point in, major length 3, no minor ticks, no grid.

## Unified palette

The same entity keeps the same colour in every panel.

| Entity | Hex |
|---|---|
| E1 | `#1F4E79` |
| E2 GJJ | `#14524F` |
| E2 ZYX | `#1F7A78` |
| E2 ZYX day-1 | `#46A8A0` |
| E2 CHH | `#84C9C0` |
| E3 | `#6B4C9A` |
| E5 | `#C1502E` |
| F1 (rep 1 / rep 2) | `#C8952A` / `#E0BE72` |
| Rule-complete arm | `#1F4E79` |
| VOI withheld arm | `#C8952A` |
| Order inverted arm | `#C1502E` |
| Formulation-only model / reference | `#8A9199` |
| Guide line | `#B9C0C7` |

The four E2 realizations are four tints of one hue because they are the same
recipe; distinct symbol shapes keep them separable in greyscale.

## Regenerating

```bash
D:/Tools/pur_bridge_env/Scripts/python.exe scripts/build_panels.py
D:/Tools/pur_bridge_env/Scripts/python.exe scripts/build_v2.py
```

Then open `PUR_NEW_panels_v2.opju`, re-import `data/p*.csv` and export SVG + PNG
at 2000 px. Three Origin behaviours on this machine need handling:

- Origin renders graphs in dark mode (`@GVC=2`), which turns the exported page
  dark and remaps light colours. Run `@GVC=0` in the Script Window first.
- Grouped plots ignore per-curve styling. Build ungrouped, or run
  `Layer.Plot.Ungroup()` before setting colours, widths, styles or symbols.
- This Origin build draws a stray rule along every text object. Remove it from
  the SVG, then rasterize the cleaned SVG — do not edit the PNG, because the
  rule sits exactly on the top bar of capital letters:

```bash
D:/Tools/pur_bridge_env/Scripts/python.exe scripts/clean_origin_export.py panels_v2/Fig2A.svg
bash scripts/render_svg.sh "$(pwd)" "/c/Program Files/Google/Chrome/Application/chrome.exe"
```

`import_csv` needs ≳5 data rows and no blank cells to detect a header, and it
does not re-type columns on re-import — import into a new sheet name.

Panel values were recomputed from `data/` and `analysis/results/` and match the
V5 manuscript: PC1 variance 99.63%, cosine 0.9998, 1.423×/1.058× held-temperature
error, R² 85.53%/99.77%, pooled 1.099× at the 120 °C anchor, E = 42.05 ± 2.43
kJ mol⁻¹ (CV 5.77%), drift ratio 4.29×.
