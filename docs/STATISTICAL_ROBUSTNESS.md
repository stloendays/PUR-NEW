# Statistical robustness checks

## Purpose

This document stress-tests the two strongest statistical conclusions in `STATISTICAL_ANALYSIS.md`.

1. repeated realizations are well represented by a shared thermal-response shape plus a realization-specific viscosity-scale shift;
2. one state-specific anchor measurement is enough to calibrate an unseen realization much more accurately than formulation identity alone.

The checks below are deliberately designed to attack shortcut explanations: dependence on one chosen temperature transform, leakage from already observed points on the same realization, and overstatement of the external database models.

---

## 1. The master-curve conclusion is not tied to one functional form

Several shared-shape state models were compared using the same realization-specific intercepts.

| thermal shape | in-sample R2 | BIC | held-temperature multiplicative error |
|---|---:|---:|---:|
| linear in 1/T | 0.9959 | -79.17 | 1.110x |
| **quadratic in 1/T** | **0.9982** | **-111.40** | **1.055x** |
| cubic in 1/T | 0.9983 | -108.10 | 1.053x |
| linear in T | 0.9931 | -57.93 | 1.153x |
| quadratic in T | 0.9982 | -110.15 | 1.060x |

The quadratic descriptions in `1/T` and in ordinary temperature give nearly the same held-temperature error. A cubic `1/T` term changes held-temperature error only from about 1.055x to 1.053x while worsening BIC relative to the quadratic model.

Therefore the useful conclusion is not that one exact equation is physically unique. It is that a **low-complexity shared thermal shape plus a realization-specific vertical shift** is sufficient over the measured 80-130 C interval. The quadratic `1/T` model is retained because it is compact, transparent and slightly favored by BIC.

---

## 2. Strict unseen-realization test: one anchor versus formulation-only prediction

The original leave-one-temperature-out analysis leaves each realization represented by its other five measurements. A stricter question is more relevant experimentally:

> Can a completely held-out realization be reconstructed after measuring only one anchor point?

For this test, one complete realization is removed from training. The comparison is restricted to E1/E2 realizations for which the same nominal formulation remains represented by another realization in the training data. The formulation-only baseline is deliberately given a quadratic shared thermal function, so it is not disadvantaged by using the simpler linear temperature model.

| anchor temperature | formulation-only error | one-point calibrated error | log-RMSE reduction |
|---:|---:|---:|---:|
| 80 C | 1.611x | 1.072x | 84.9% |
| 90 C | 1.610x | 1.081x | 83.6% |
| 100 C | 1.611x | 1.084x | 83.0% |
| 110 C | 1.610x | **1.065x** | **86.8%** |
| 120 C | 1.599x | 1.098x | 80.1% |
| 130 C | 1.603x | 1.084x | 82.8% |

The formulation-only prediction remains around **1.60x multiplicative RMSE** when the realization is genuinely unseen. One state-specific anchor collapses this to approximately **1.065-1.098x**.

The 120 C anchor is particularly useful operationally because 120 C is already the thermal-hold evaluation temperature. At this anchor, all six held-out E1/E2 realizations improve relative to their formulation-only prediction, despite substantial differences in the size of the original state shift. This directional consistency is more informative than choosing 110 C simply because it gives the smallest pooled error in this small dataset.

The paper-facing conclusion can therefore be strengthened to:

> **For a nominal formulation already represented in the local chemistry family, formulation identity does not determine the viscosity level of a new realization. A single viscosity anchor identifies the realization-specific scale sufficiently well to reconstruct the remaining measured temperature curve with approximately 6-10% multiplicative error.**

This is an interpolation-with-state-calibration result. It should not be described as universal extrapolation to new chemistry families.

---

## 3. The realization effect is approximately multiplicative

If two realization curves differ mainly by a vertical shift in log-viscosity, their viscosity ratio should stay approximately constant across temperature.

For E1, the ratio between the original and day-1 realization has a CV of only **3.3%** across 80-130 C.

For the six pairwise E2 realization comparisons, the median ratio CV is **8.5%**. Some pairs are less parallel than others, so an exact multiplicative law would be too strong; however, the ratios are far more stable than the absolute viscosity levels themselves.

A second collapse diagnostic gives the same result. For E2, the mean between-realization log-viscosity SD across matched temperatures is about **0.497** before state alignment. After fitting realization intercepts plus the common quadratic thermal shape, the mean residual log-SD falls to **0.054**, an **89.1% reduction**.

This is a direct structural explanation for why a one-point state anchor works.

---

## 4. External database: retain the broad-landscape claim, but report out-of-sample strength

The external database contains 39 dense prepolymer curves and 4559 temperature-viscosity points. Curve-level `ln(eta)` versus `1/T` behavior remains highly regular:

```text
median curve R2 = 0.9967
37 / 39 curves have R2 >= 0.98
apparent E_eta range = 34.7-94.2 kJ/mol
```

The previous in-sample composition models are useful but should not be reported without an out-of-sample check.

### Apparent thermal-sensitivity descriptor

| composition model | in-sample R2 | leave-one-curve-out R2 | LOOCV RMSE |
|---|---:|---:|---:|
| pNCO + polyol + isocyanate | 0.771 | 0.593 | 7.90 kJ/mol |
| pNCO x polyol + isocyanate | 0.798 | **0.616** | **7.68 kJ/mol** |

### Fitted log-viscosity at 75 C

| composition model | in-sample R2 | leave-one-curve-out R2 | multiplicative LOOCV error |
|---|---:|---:|---:|
| pNCO + polyol + isocyanate | 0.884 | 0.797 | 1.645x |
| pNCO x polyol + isocyanate | 0.904 | **0.822** | **1.593x** |

The external result therefore remains useful, but the correct interpretation is:

> **composition explains a substantial part of the broad rheological landscape across chemistry families, while significant curve-to-curve variability remains.**

The cross-validated values are preferable to the larger in-sample R2 values when discussing predictive strength.

---

## 5. External data cannot yet directly prove orthogonality of thermal sensitivity and stability

The 39 temperature-viscosity curves come from `DATA_PUGAR_VISCOSITY`. The nine viscosity-rise-rate observations come from a separate patent family (`PAT_US20030022973A1`). There are no shared source/sample identifiers between these two evidence sets.

Therefore the database does **not** currently permit a direct sample-matched test of correlation between apparent `E_eta` and viscosity-rise rate.

This is an important boundary for the second manuscript claim. The present evidence supports:

> **temperature response and thermal-hold stability are distinct, differently tunable rheological coordinates in the current experimental design.**

It does not yet support the stronger universal statement that the two properties are statistically independent across PUR chemistry.

The earlier patent observation that static viscosity and viscosity-rise rate are weakly correlated in a nine-formulation family remains useful contextual evidence, but it is not a substitute for matched `E_eta`-versus-stability measurements.

---

## 6. Recommended statistical hierarchy for the manuscript

Use the evidence in this order:

```text
Primary evidence
  strict leave-one-realization-out + one-point calibration
  master-curve residual collapse
  held-temperature cross-validation

Model-selection support
  AIC / BIC
  functional-form sensitivity

Hierarchical robustness
  mixed-effects random-intercept variance / ICC

External generalization boundary
  curve-level database descriptors
  leave-one-curve-out composition models
  separate stability records
```

The mixed-effects model remains useful, but it should not replace the more transparent calibration experiment as the headline result.

## Reproducibility

Run the local robustness checks with:

```bash
python scripts/statistical_robustness.py \
  --output-dir derived/statistical_robustness
```

When the private/local HMPUR SQLite database is available, add:

```bash
python scripts/statistical_robustness.py \
  --external-db /path/to/hmpur_external.db \
  --output-dir derived/statistical_robustness
```

The external database is intentionally optional because unpublished/private evidence assets are not required for repository CI.
