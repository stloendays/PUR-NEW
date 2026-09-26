# Composite figures

The manuscript figures and several supplementary/diagnostic figure assets. Each is
built by one script that assembles it on a page measured in millimetres,
draws schematics rather than exporting them, reads its numbers from the
repository tables, and writes **SVG, PDF and PNG** (600 dpi) in one pass.

Rebuild everything with the project interpreter:

```
for d in fig1 fig2 fig3 fig4 fig5 fig_arrhenius fig_column fig_structure; do
  (cd $d && D:/Tools/pur_bridge_env/Scripts/python.exe make_*.py)
done
D:/Tools/pur_bridge_env/Scripts/python.exe make_sheet.py

The current SI also uses `analysis/figures/Supplementary_Figure_S1_PUR_chemistry.svg`
as Supplementary Figure S1. `fig_arrhenius/Fig_arrhenius.svg` is Supplementary
Figure S2. The column and constructed-structure figures remain repository
diagnostics and are not cited as manuscript evidence.
```

The structure render in `fig_structure/` is a separate, slower step that needs
the OVITO environment (see *The structure model* below).

## The figures

| Figure | Directory | Size (mm) | Reads |
|---|---|---|---|
| 1 | `fig1/` | 183 x 143 | drawn chemistry; every loop number and glyph through `figdata` (sweeps, holds, strict holdout, 292 cards) |
| 2 | `fig2/` | 183 x 100 | `figures_origin/data/p2A-D`, the state-conditioned fit (`figdata.state_model`), `results/local_model_free_state_shift_summary.json` |
| 3 | `fig3/` | 183 x 98 | strict-holdout detail and summary, `derived/state_anchor_bridge/`, `results/local_leave_one_formulation_pooled.csv`, the bootstrap re-run with seed 20260918 |
| 4 | `fig4/` | 183 x 144 | every run's `voi_full_ranking.json`, `recommendation.json` and `deliberation.json` under `results/agent_v4_voi/`, checked against `rule_layer_ablation.json` |
| 5 | `fig5/` | 183 x 100 | `data/temperature_sweeps.csv`, `data/thermal_hold.csv`, `results/local_hold_dynamics.csv`, `analysis/results/analysis_summary.json`, `series_n10/adjudication_summary.json` |

### 2026-09-26 redesign of Figures 1-5

Each main figure now answers a different question with a different visual
grammar, and one colour language runs through all five (`style.py`): blue for
realization / state / temperature response, orange for thermal-hold failure,
green for validated outcomes and retained directions, grey for null models,
inactive and inadmissible cards. The previous versions remain in git history.

* **Figure 1** — a two-layer closed loop instead of a linear chain: the
  physical/material layer (left) feeds one structured evidence state (centre),
  the only input to the decision/experiment layer (right); the wet-lab outcome
  returns to the evidence state. An "order of authority" strip puts
  model-mediated selection below physical evidence and deterministic rules.
  Glyphs are drawn from the data they name. The hard-segment H-bond panel was
  dropped: it was context, not evidence.
* **Figure 2** — raw and aligned E2 curves as one before/after pair joined by
  the operation (subtract `a_fr`); the fitted state intercept as a latent axis
  beside the formulation-only level; the singular-mode loading on an axis from
  zero, where a constant shift is flat; dumbbells for the matched-basis model
  comparison.
* **Figure 3** — the calibration geometry drawn on one real strict-holdout
  realization (shape from other formulations at <= 110 C, one anchor, predicted
  vs measured); formulation identity vs one state anchor as a fork with every
  prediction; parity; the bootstrap distribution (a histogram, since six
  clusters make it lumpy) with the anchor-temperature sweep on the same axis.
* **Figure 4** — the 292 experiment cards drawn as four measurement maps of the
  formulation lattice: VOI fill, discrimination dots, the tied top set, CBES
  inadmissibility (M-ANCHOR on resin-modified candidates, 64 cards; the RGES
  series ran without this gate) and the rule-complete selections. A VOI
  anatomy panel, the arms' selections on the lattice, and a run-by-run tile
  map with the critique flags replace the three proportion bars.
* **Figure 5** — E5 and the validation formulation have no temperature sweep,
  so the coordinate panel is an orthogonal frame with margins only; no joint
  point is imputed. The null-model test is one drift axis (E1 reference,
  dilution prediction, frozen H-RESIN acceptance threshold, measured repeats),
  and the hypotheses carry an understated status.

### `data/` — the tables the new panels draw

Written by the scripts on every build: `fig2C_state_axis.csv` (fitted `a_fr`
and `mu_f`), `fig3D_strict_holdout_bootstrap.csv` (10,000 replicates),
`fig4A_experiment_cards.csv` (all 292 cards with VOI components, tied-top and
CBES admissibility), `fig4CD_runs.csv` (each frozen run's selection and
critique flags).
| SI S2 | `fig_arrhenius/` | 183 x 86 | all seven realizations, and `derived/thermal_model_robustness/` |
| diagnostic | `fig_column/` | 120 x 152 | one property, seven realizations, stacked against each other |
| diagnostic | `fig_structure/` | 183 x 88 | the generated hard-segment CIF; constructed model, not measured structure |

Before the 2026-09-26 redesign, three panels had already been redrawn because
the earlier drawings implied relationships the data does not have (the same
rules still hold in the redesign):

* **2d** — two model specifications were joined by a thick diagonal, implying
  intermediate states that were never fitted. Now two metrics, each on its own
  axis, two bars each.
* **4d** — three different outcomes counted over the same ten runs were joined
  by a polyline, implying a trajectory. Now three separate rows, one segment
  per run.
* **5d** — a CV in percent and a ratio of drift rates shared one axis, while
  the caption said no common scale was implied. Now two axes, each with its own
  units and the data it comes from.

## `figdata.py` — one data layer

Every figure reads through it, so a number cannot differ between two figures.
Conventions it settles:

* **The hold window is 15-60 min, matched.** E1 and E5 ran to 90 min and the
  validation repeats only to 60, so a first-to-last drift would compare 75
  minutes against 45. `hold_drift()` reproduces the manuscript's 9.51 %,
  51.54 % and 1.60 % exactly. The E5/E1 drift-rate ratio of 4.29 is a
  different descriptor, fitted over the full 15-90 min hold, and Figure 5
  labels which is which.
* **E1 +P is never pooled.** It is a deliberate H3PO4 perturbation;
  `primary()` excludes it, giving n = 6, 42.05 +- 2.43 kJ/mol, CV 5.77 %.
* **Ablation runs are read one by one.** `ablation_runs()` walks each run's
  `recommendation.json`, so Figure 4 can show every run. Figure 4 asserts that
  the per-run records reproduce the frozen aggregate before it draws anything.
  The order-inverted arm's ten runs all live in the `_n5` folder: it was
  declared at n = 5 and extended to 10 after the first five were observed.
* `wilson()` gives the two-sided 95 % intervals quoted in Figure 4.
* **Recomputations are asserted, not trusted.** `state_model()` refits the
  formulation-only and state-conditioned models (R^2 0.8553 / 0.9977);
  `strict_holdout_curve()` reproduces every strict-holdout prediction to 1e-9;
  `strict_holdout_bootstrap()` reproduces the 1.043-1.126x interval with the
  analysis seed; `experiment_cards()` asserts the 292-card inventory is
  identical in every frozen run; `run_critique()` reproduces the critique counts
  of `rule_layer_ablation.json`.

## Chemistry that is drawn

PPG2000 and 4,4'-MDI have public, unambiguous formulae and are drawn atom for
atom. STEPANPOL PDP-70 is a supplier polyester polyol whose backbone is not
public, so it is a labelled block rather than a guessed structure.

Read every drawn structure as chemistry, atom by atom. Each of these rendered
cleanly and was wrong:

* **PPG2000 ended on the ether oxygen** — an O-OH peroxide. The chain ends on
  carbon.
* **Its repeat brackets faced outward and sat one bond early**, enclosing
  [CH(CH3)-O-CH2-CH(CH3)], which does not repeat into PPG. The unit is
  [O-CH2-CH(CH3)]n, brackets crossing the CH-O and CH-OH bonds.
* **A methyl pointed into its chain angle**, putting all three bonds of that
  carbon in one half-plane. Substituents leave on the exterior: down from a
  valley vertex, up from a peak.
* **MDI's isocyanates read as nitroso groups.** N=C=O is linear, so the
  implicit carbon vanishes between two collinear double bonds and the group
  reads O=N. It is written OCN- / -NCO, as polyurethane schemes do.
* **Two reciprocal H-bonds crossed in an X.** With a rigid offset both cannot be
  vertical; Figure 1b draws the one contact that can.
* **Figure 1b stated a mechanism** — that holding "lets this association keep
  building". Nothing here measures that. It now states what is measured: the
  composition is fixed and the viscosity still changes.

## The structure model

`fig_structure/mdi_hard_segment_stack.cif` is **generated by this repository**,
not measured. There was no experimental structure to use, and this polymer is
amorphous.

* The unit is dimethyl 4,4'-methylenediphenyl dicarbamate, MMFF94-optimized
  from SMILES by RDKit.
* The three-unit stack is constructed: a rigid transform is searched for under
  explicit acceptance criteria (N...O 2.90 +- 0.15 A, N-H...O >= 150 deg, no
  heavy-heavy contact below 3.05 A), and every criterion is re-checked on the
  result. It achieved N...O 2.92 A, N-H...O 164 deg, closest heavy contact
  3.20 A. The figure says on its face that it is a model.

```
D:/Tools/pur_bridge_env/Scripts/python.exe fig_structure/build_hardsegment.py   # CIF
D:/Tools/render-venv/Scripts/python.exe    fig_structure/build_render.py        # OVITO
```

The builder refuses three things, each hit during development: translating
along N-H (buries the units in each other), counting the H...O bond itself as
a clash (fights its own objective), and accepting a result without re-checking
the N...O distance it optimized -- that once wrote a 5.63 A "hydrogen bond".
The renderer identifies hydrogen bonds by being intermolecular, N-H-donated and
near-linear, not by distance alone, which returned 20 contacts against the 2
real ones.

**A privacy grep reports two false matches here.** Searching the repository
for the retired run labels finds one match each in `Fig_structure.svg` and
`Sheet_supplementary_figures.svg`. Both sit inside the base64 data of the
embedded OVITO render: random runs of the encoding, not text. Every text
element in these figures uses only R01-R03. Do not edit the base64 to remove
them; that corrupts the image.

## `layout.py` — legends, and a measured overlap audit

* **`legend(...)`** — the house legend frame, used where a panel carries more
  than four or five series or where end labels would collide.
* **`audit(fig)`** — runs before every `save`. It draws the figure, measures
  every placed text, legend, axis label, title and *drawn* tick label, and
  reports real intersections. Tick labels outside the view limits and on
  switched-off axes are skipped: matplotlib returns them but never draws them.
  It has caught collisions that survived a visual check, and it is tested
  against planted ones.

It does **not** check text against data marks. A label sitting on a data point,
and two data points hiding each other, still have to be seen: an n = 6 strip
once showed five dots because two values sat 0.12 % apart.

## Sheets

`make_sheet.py` composes the finished figures into
`Sheet_main_figures.{svg,pdf,png}` (Figures 1-5, in reading order) and
`Sheet_supplementary_figures.{svg,pdf,png}` (a repository review sheet containing the three composite supplementary/diagnostic assets). The SI numbering is independent: the chemistry schematic is S1 and the Arrhenius/model-form figure is S2. Each figure is nested as
an SVG, so a sheet is vector with live text; each is scaled independently. The
per-figure files remain the submission artifacts.
