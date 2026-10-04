# Prospective supplementary experiment plan — 2026-10-04

## Status

**Registered / not yet executed.** This document records the supplementary wet-lab plan and decision boundaries before the new measurements are available. The planning values below are not observations and must never be copied into raw-data fields.

The active manuscript and SI remain unchanged until the measurements are returned and adjudicated against these frozen criteria.

## Scientific purpose

This follow-up closes three specific evidence gaps:

1. **F1 direct temperature sweep:** test whether the E1–E3 shared local temperature-response shape transfers after the resin/tackifier chemistry shift.
2. **Independent E1/E3 preparation repeats:** tighten realization-level repeatability and uncertainty for the original chemistry family.
3. **Additional thermal-hold repeats:** test reproducibility of the E1 reference drift and the low-drift F1 state under the same 120 °C matched window.

The experiment is scientifically useful because both outcomes of the F1 sweep are informative. If the shared shape transfers, one-point state calibration gains a measured applicability extension to the resin-modified chemistry. If the shape changes, the CBES rule requiring a direct sweep after a meaningful chemistry shift receives direct physical support.

## Frozen comparability conditions

Use the current Methods without changing the measurement basis:

- viscometer: RV-SSR-H high-temperature rotational viscometer;
- heater: NKY-25;
- spindle: No. 27;
- torque: approximately 40–60%, adjusted through rotation speed;
- temperature sweep: 80, 90, 100, 110, 120, 130 °C;
- equilibration: 15 min at each set point;
- optional density points: 115 and 125 °C, reported separately and excluded from the primary registered decision;
- dehydration: approximately 130 °C under vacuum for 1 h;
- MDI reaction: approximately 120 °C under vacuum for 1 h 20 min;
- thermal-hold t = 0: when the sample reaches 120 °C;
- hold condition: stirred and sealed under vacuum;
- daily instrument QC: standard-oil calibration before measurement.

For F1, after reaching 130 °C, return to 110 °C and remeasure. A return-point deviation of approximately <=3% is the scan-integrity target.

## Blocking / preparation order

Do not run all preparations of one formulation consecutively.

Recommended order:

- Day 1: E1-b -> E3-b -> F1-b
- Day 2: E3-c -> E1-c -> F1-c

The two F1 temperature sweeps and the thermal-hold tests must use separately prepared/fresh samples. Do not reuse the temperature-swept sample for the hold test.

## F1 temperature-sweep planning targets

The center values are generated from the chemistry-audited six-curve shared temperature shape and an F1 state level anchored near the existing 120 °C F1 hold measurements. They are planning targets only.

| Temperature (°C) | F1-b target (mPa·s) | F1-c target (mPa·s) |
|---:|---:|---:|
| 80 | 5791 | 5877 |
| 90 | 3479 | 3603 |
| 100 | 2324 | 2368 |
| 110 | 1664 | 1689 |
| 120 | 1240 | 1270 |
| 130 | 959 | 996 |

Expected apparent E_eta is approximately 42 kJ/mol. The existing local primary distribution is 42.05 ± 2.43 kJ/mol.

### Registered F1 shape-transfer criteria

Primary criteria:

- full-curve multiplicative RMSE using the existing E1–E3 shared shape plus an F1-specific scale/intercept:
  - **support shape transfer:** <=1.10×;
  - **clear shape change:** >=1.20×;
  - **gray zone:** >1.10× and <1.20×.
- one 110 °C anchor predicting 120 and 130 °C:
  - **support:** <=1.13×;
  - **clear failure:** >=1.20×;
  - intermediate values are gray.
- apparent E_eta:
  - **local-shape-compatible:** 37.2–46.9 kJ/mol;
  - outside this interval is evidence of altered thermal response, subject to scan-QC passing.
- 110 °C return check:
  - target absolute deviation <=3%.

If one F1 sweep falls in the 1.10–1.20× gray interval, use the second independent preparation to adjudicate; do not move the thresholds after seeing the result.

## E1 and E3 independent repeat sweeps

Preferred: two new independent preparations per formulation; minimum: one per formulation.

The absolute viscosity level is allowed to move between realizations. The key endpoint is preservation of the shared temperature shape.

Planning 120 °C state levels used only to generate example curves in the workbook:

| Preparation | Existing 120 °C reference | Planning level |
|---|---:|---:|
| E1-b | 780 | 720 |
| E1-c | 780 | 850 |
| E3-b | 3839 | 3500 |
| E3-c | 3839 | 4200 |

These absolute levels are **not pass/fail criteria**.

Apply the same full-curve, one-anchor, and E_eta shape tests as above when appropriate.

## Thermal-hold repeats

### E1

Measure at 15, 30, 45, 60, and 90 min.

Existing E1 reference:
- 15 min: 708.7 mPa·s
- 60 min: 776.1 mPa·s
- 90 min: 828.1 mPa·s
- SI_15->60 = 9.51%.

Planning centers:
- E1-b: eta_15 ~= 730 mPa·s; descriptive k ~= 0.118 h^-1;
- E1-c: eta_15 ~= 820 mPa·s; descriptive k ~= 0.132 h^-1.

The purpose is to establish independent-preparation reproducibility of the E1 hold reference, not to require exact replication of viscosity level.

### F1

For each of the two new F1 preparations, run a fresh 120 °C hold at 15, 30, 45, and 60 min.

Existing F1 repeats:
- repeat 1: 1230, 1189, 1203, 1228 mPa·s;
- repeat 2: 1281, 1260, 1289, 1320 mPa·s;
- mean absolute SI_15->60 ~= 1.60%.

The new repeats are expected to remain approximately low-drift (planning center ~1–2%), but the result must be compared to the frozen physical null rather than forced to the planning center:

- H-CORE proportional-dilution null: 7.79%;
- current registered H-RESIN support threshold: 3.89%.

## Optional acrylic-only matched-window hold

If resources permit, prepare the registered acrylic-only contrast (15 wt% acrylic-like modifier; no tackifier-like modifier) and run two independent 120 °C holds over the same 15–60 min window. This is the most direct remaining experiment for separating H-RESIN from H-DUAL.

Do **not** prefill an "ideal" drift for this contrast unless a frozen hypothesis registry supplies the exact predicted interval. Its purpose is discrimination, not confirmation.

## Process-state variables to record for every independent preparation

Record prospectively:

- actual masses of all components, especially MDI;
- post-dehydration polyol water content by Karl Fischer;
- final NCO% by dibutylamine back-titration;
- actual vacuum level and units;
- actual dehydration time and reaction time;
- time from synthesis completion to measurement;
- storage conditions;
- same-day versus next-day retest status;
- standard-oil QC result and lot.

These variables may explain realization-specific viscosity-scale displacement; they must not be used post hoc to delete inconvenient runs.

## Pre-experiment feasibility verdict

**Feasible and decision-relevant.**

The direct F1 sweep can distinguish transferable versus chemistry-changed thermal response. Independent E1/E3 preparations address the main limitation of sparse realization-level replication. Repeated holds make the low-drift F1 result and E1 reference materially more defensible.

The acrylic-only hold is also feasible and has especially high mechanistic discrimination because it separates H-RESIN from H-DUAL.

## Post-experiment verdict classes

After measurements return, classify each claim using the frozen boundaries:

- **SUPPORTS** — primary endpoints lie in the support zone and QC/comparability pass.
- **SUPPORTS WITH BOUNDARY** — core result holds but one secondary endpoint is gray or the supported scope must be narrowed.
- **INCONCLUSIVE** — replicate disagreement, gray-zone overlap, or insufficient resolution prevents discrimination.
- **CONTRADICTS / REVISE CLAIM** — primary endpoint crosses the contradiction boundary while QC passes.
- **NOT COMPARABLE** — method/QC/preparation changes prevent direct interpretation against the current cohort.

## Repository artifacts

- fillable workbook: `experiments/supplementary_20261004/PUR_F1_E1_E3_ideal_ranges_and_record.xlsx`
- target/criterion table: `experiments/supplementary_20261004/preregistered_targets.csv`
- blank result template: `experiments/supplementary_20261004/results_template.csv`

Raw measurements should be entered only after execution. The workbook's target values and formulas must remain unchanged so the returned measurements are adjudicated against a genuine pre-result record.
