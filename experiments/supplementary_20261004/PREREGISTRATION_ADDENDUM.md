# Pre-result addendum to the 2026-10-04 follow-up plan

**Status:** computed and committed before any follow-up measurement exists. No threshold in `PLAN.md` or `preregistered_targets.csv` is changed. This addendum adds two things:
- the frozen hypothesis-registry predictions for the acrylic-only contrast;
- the operating characteristics of the registered decision rules.

Script: `scripts/preregistration_addendum_20261004.py` (seed 20261004). Machine-readable record: `preregistration_addendum.json`; the SHA-256 hashes of every input are stored there.

## 1. Acrylic-only 120 °C hold: registered predictions

The acrylic-only card is S1C39: 15 wt% acrylic-like modifier, no tackifier-like modifier, reactive mass fraction φ_r = 0.850. Predictions use `src/pur_new/voi.predict_drift` with the frozen registry (`configs/hypothesis_registry.json`) and the E1 reference drift of 9.51%.

| Hypothesis | Predicted 15→60 min drift |
|---|---:|
| H-CORE (proportional dilution) | 8.08% |
| H-RESIN (resin modification suffices) | below 4.04% |
| H-DUAL (tackifier axis required) | 8.08% (no low-drift regime without tackifier) |

**Decision rule.** The statistic is the mean absolute 15→60 min drift of the acrylic-only repeats.
- Below 4.04%: supports H-RESIN and falsifies H-DUAL.
- At or above 4.04%: supports H-DUAL.

When the planned E1 reference holds are measured, the prediction and threshold are recomputed with the mean E1 drift by the same formula, threshold = 0.5 × φ_r × mean E1 drift.

### Operating characteristics

Hold-drift repeatability is σ = 0.0226 in ln η, from within-trajectory scatter with 8 dof; its sampling uncertainty is propagated.

| Acrylic-only repeats | E1 reference holds | P(H-RESIN supported \| H-DUAL true) | P(H-RESIN supported \| H-RESIN true at the F1-level suppression) |
|---:|---:|---:|---:|
| 2 | 1 | 0.076 | 0.87 |
| 2 | 3 | 0.038 | 0.87 |
| 3 | 1 | 0.061 | 0.90 |
| 3 | 3 | 0.023 | 0.90 |
| 4 | 3 | 0.016 | 0.92 |

**Recommendation.** Use three acrylic-only repeats. Together with the two planned E1 reference holds, this keeps the false-support rate near 2% while detecting H-RESIN with 90% probability.

## 2. F1 direct sweeps: operating characteristics of the registered criteria

The simulation has three ingredients:
- **Shape.** The E1–E3 shared quadratic shape, with realization-level bootstrap uncertainty.
- **Level.** A free level for each simulated curve.
- **Noise.** Realization-specific noise from the heteroscedastic hierarchical posterior.

A shape change is modelled as a shift dE in the apparent temperature-response descriptor.

| dE (kJ mol⁻¹) | P(full-curve ≤ 1.10×) | P(full-curve ≥ 1.20×) | P(110 °C anchor ≤ 1.13×) | P(E_η inside 37.2–46.9) |
|---:|---:|---:|---:|---:|
| 0 (shape transfers) | 0.89 | 0.03 | 0.86 | 0.96 |
| ±5 | 0.72–0.73 | 0.04 | 0.80 | 0.43–0.47 |
| ±10 | 0.01 | 0.12 | 0.41–0.45 | 0.02 |
| ±15 | 0.00 | 0.96 | 0.09 | 0.00 |

- **When the shape transfers,** the registered criteria classify it correctly in 86–96% of single sweeps.
- **The E_η interval detects moderate changes.** A 10 kJ mol⁻¹ shift leaves the full-curve error mostly in the gray zone, but places E_η outside the registered interval 98% of the time.
- **The full-curve contradiction threshold (≥ 1.20×)** responds reliably only to shifts of about 15 kJ mol⁻¹ or more.
- **Two independent F1 preparations,** as planned, reduce single-sweep misclassification further.
