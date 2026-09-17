# Anchor-normalized master-curve collapse

## Why this analysis matters

The regression models in `STATISTICAL_ANALYSIS.md` show that a realization-specific intercept plus a shared thermal-response function explains the local temperature-sweep data well. This document provides a simpler, nearly model-free check of the same claim.

If process realization mainly changes the viscosity scale, dividing every curve by its own viscosity at one common anchor temperature should remove most of the between-realization spread.

The default anchor is **120 C**, chosen because it is already the temperature used for the thermal-hold experiment. It is therefore operationally meaningful rather than selected only because it minimizes prediction error.

---

## 1. Direct 120 C normalization collapses the seven curves

For every realization, define

```text
relative_eta(T) = eta(T) / eta(120 C)
```

Across the seven recorded 80-130 C realizations:

| Temperature | mean eta(T)/eta(120 C) | across-realization CV |
|---:|---:|---:|
| 80 C | 4.611 | 8.18% |
| 90 C | 2.833 | 10.24% |
| 100 C | 1.888 | 10.34% |
| 110 C | 1.345 | 7.23% |
| 120 C | 1.000 | 0% by construction |
| 130 C | 0.778 | 3.39% |

The non-anchor CV range is therefore only **3.4-10.3%**, with a mean of **7.9%**.

This is notable because the unnormalized E2 realizations differ by factors of roughly 2.8-3.6 at matched temperatures. The large absolute-level variation therefore collapses to a much narrower relative thermal profile after one state-specific scale measurement is supplied.

This is the most direct visual evidence for the state-shift master-curve interpretation.

---

## 2. Group-bootstrap uncertainty of the shared shape

A 10,000-resample group bootstrap was performed by resampling complete realization trajectories, removing each trajectory's intercept by within-realization centering, and refitting the common quadratic thermal shape.

The resulting relative-viscosity profile referenced to 120 C is:

| Temperature | bootstrap median | 95% group-bootstrap interval |
|---:|---:|---:|
| 80 C | 4.598 | 4.400-4.789 |
| 90 C | 2.849 | 2.718-2.954 |
| 100 C | 1.895 | 1.817-1.951 |
| 110 C | 1.340 | 1.305-1.364 |
| 120 C | 1.000 | 1.000-1.000 |
| 130 C | 0.783 | 0.764-0.811 |

The bootstrap is based on only seven realization groups, so these intervals are descriptive robustness intervals rather than a universal population claim. Their value is to show that the inferred relative thermal shape is not being driven by one single trajectory.

---

## 3. Relationship to one-point calibration

The normalized collapse and the predictive calibration test answer complementary questions.

```text
anchor-normalized collapse
-> model-light structural evidence that the curves are nearly parallel on a log scale

leave-one-realization-out one-point calibration
-> predictive evidence that the structure can reconstruct an unseen realization
```

Together they support the compact model

```text
ln eta_r(T) = alpha_r + g(T) + epsilon
```

where `alpha_r` is a realization/state-specific viscosity scale and `g(T)` is a shared local thermal-response shape.

The one-point calibration result should remain the primary quantitative performance claim. The normalized collapse should be the primary visual/mechanistic-statistical illustration.

---

## 4. Recommended Figure 2 structure

A strong four-panel Figure 2 would be:

```text
A  raw 80-130 C viscosity curves
B  same curves normalized by eta(120 C), showing master-curve collapse
C  shared-shape bootstrap band / apparent thermal descriptor by realization
D  strict unseen-realization prediction error: formulation-only vs one-point calibrated
```

Panel B is especially valuable because it does not require the reader to accept a mixed-effects model or a particular probabilistic assumption before seeing the underlying structure.

---

## 5. Claim boundary

Supported:

> Within the current local chemistry family and measured 80-130 C interval, repeated realizations differ strongly in absolute viscosity but exhibit a substantially more conserved relative thermal-response shape after one state-specific normalization point is supplied.

Not yet supported:

- that every reactive PUR chemistry admits the same master curve;
- that the 120 C anchor is universally optimal;
- that the state shift is caused by one identified physical variable;
- that the same shared shape transfers to the resin-modified F1 chemistry without a matched temperature sweep.

The external 39-curve database in fact shows that thermal sensitivity changes substantially across chemistry families, which is why the master curve is explicitly treated as a **local-chemistry** result.

## Reproducibility

```bash
python scripts/master_curve_collapse.py \
  --anchor-temperature 120 \
  --bootstrap 10000 \
  --output-dir derived/master_curve_collapse
```
