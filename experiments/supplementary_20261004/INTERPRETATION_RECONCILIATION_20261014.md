# Prospective adjudication reconciliation — 2026-10-14

**Status:** interpretation and reporting correction made before any S1C39/S1C41
follow-up wet-lab result is entered in the repository. This document does
not alter any protected prospective file, raw observation, experimental
composition, or prospective measurement time.

## The protected order of evidence

1. **2026-09-20 independent freeze:**
   `experiments/prospective/S1C39_M-HOLD-120_20260920.md`.
   Contains the composition, experiment card, measurement times and the
   three-region H-RESIN/H-DUAL discrimination protocol.
2. **2026-10-04 supplemental planning:**
   `experiments/supplementary_20261004/PLAN.md`. This planned multiple
   validation, E1/E3 and F1 sweeps and allowed an optional acrylic-only
   contrast. The September 20 S1C39 rule remains the controlling protocol
   for the same registered S1C39 experiment.
3. **2026-10-04 computed pre-result addendum (merged on 2026-10-14):**
   `PREREGISTRATION_ADDENDUM.md`, `preregistration_addendum.json`,
   and `scripts/preregistration_addendum_20261004.py`.

The computed addendum states that S1C39 drift **>=4.04%** supports H-DUAL,
and proposes automatically recomputing the verdict threshold from later
E1 references. That **does not follow** from the September 20 frozen
three-region rule. It collapsed a declared 2.0-percentage-point
indeterminate interval and removed the prerequisite contemporaneous
dual-axis control. The manuscript's earlier summary repeated the
collapsed interpretation. All three were subsequently corrected in the
current MAIN_TEXT and SI *interpretation*, without rewriting the
historical frozen sources.

## Governing S1C39 result interpretation

Use **three independent S1C39 syntheses** where practical; retain all
individual signed 15-to-60 minute drift values and use the **mean absolute
drift** as the primary adjudication statistic.

| Outcome | Frozen numerical region | Interpretation |
|---|---|---|
| A | S1C39 mean absolute drift **<=4.04%** | Supports H-RESIN: acrylic alone reaches the low-drift regime; formulation-level H-DUAL requirement falsified |
| B | S1C39 mean absolute drift **>=6.08%** **AND** contemporaneous S1C41 mean absolute drift **<=3.80%** | Supports H-DUAL for this local formulation and matched processing window |
| C | S1C39 in **(4.04%, 6.08%)** or S1C41 fails low-drift criterion | **UNRESOLVED**; record an additional independent S1C39 synthesis repeat without changing thresholds |

Where the S1C41 contemporaneous control has not been measured, an S1C39
drift >=6.08% **cannot** by itself establish H-DUAL. The original control
was recommended "when laboratory capacity permits", but it is required
*to make the positive H-DUAL inference* under Outcome B.

At the numeric boundary **4.04%**, use the frozen inclusive A criterion;
at **6.08%**, B also requires the S1C41 control. Report unrounded
experimental statistics for adjudication, rather than classifying using
prematurely rounded drift percentages.

The numerical 4.04%, 6.08%, and 3.80% values were frozen before the
registered future S1C39 data. Measuring more E1 references helps quantify
uncertainty around the physical proportional-dilution baseline but does
**not automatically reset** these original result-interpretation
thresholds. An intentional prospective amendment would require an
author-authorized, separately dated version created **before inspecting
affected outcomes**, explicitly preserving and referencing the predecessor.

## What the existing operating-characteristic simulation does show

The computed `analysis/results/upgrades_20261003/preregistration_addendum/`
exercise sampled drift noise and threshold uncertainty, then counted
the event `mean absolute S1C39 drift <= ~4.04%`.

The simulations estimate a **one-sided low-drift event probability**, not
a full two-sided H-DUAL verdict:

- Under the simulated H-DUAL state, 3 acrylic-only repeats and 3 E1
  references yield approximately **0.023** probability of S1C39 reaching
  the H-RESIN support threshold.
- Under F1-level simulated H-RESIN suppression, the same event has
  probability approximately **0.90**.
- These probabilities assume the modelled drift magnitude, noise model,
  sample independence and E1 uncertainty. They are **not** new wet-lab
  outcome frequencies and are **not** the operating characteristics of
  the full A/B/C decision scheme.
- The simulation did not establish how often **Outcome B** occurs, because
  its recorded event does not include the S1C41 matched-control
  measurement. Do not interpret `1 - P(A)` as `P(B)`.

The original stored simulation JSON and source script remain untouched
and version-traceable, even where their narrative `decision_rule` strings
have the obsolete binary H-DUAL interpretation.

## Measurement integrity

Do not silently populate results from the October 4 workbook's
hypothetical targets. Do not pool technical time points as independent
syntheses or infer wet-lab validation from simulation. Preserve exact
sample preparation order, additive addition stage, Karl Fischer water,
final NCO%, rheometer torque and 15/30/45/60 minute original readings.

**Current measurements:** The repository contains E1, E5 and F1 hold
results, but no returned S1C39/S1C41 prospective outcome. The
H-RESIN/H-DUAL distinction therefore remains **not yet physically
adjudicated**.
