# Uncertainty propagation for the H-CORE adjudication (Section 2.9)

Script: `scripts/hcore_adjudication_uncertainty.py` (seed 20261003, 10⁶ Monte Carlo draws). Inputs: `data/thermal_hold.csv` and `data/formulations.csv`; their SHA-256 hashes are in `summary.json`.

## Headline

| Quantity | Value |
|---|---|
| H-CORE prediction (0.819 × 9.51%) | 7.79% |
| Registered H-RESIN support threshold | 3.89% |
| Observed mean absolute 15–60 min drift (two repeats) | 1.60% |
| Hold-drift repeatability, from within-trajectory scatter (√2 σ_point, 8 dof) | 0.0226 in ln η |
| Hold-drift repeatability, from the two validation repeats (1 dof) | 0.0224 in ln η |
| **P(mean absolute drift ≤ 1.60% under H-CORE), primary** | **0.0097** |
| P(registered H-RESIN criterion met under H-CORE) | 0.079 |
| Largest P(≤ 1.60% under H-CORE) with σ inflated up to 8× | < 0.05 at every multiple |

The two repeatability estimates are independent and agree to within 1%:
- point scatter about a straight line in time, pooled over the E1, E5 and both validation trajectories;
- the spread between the two validation repeats.

The primary scenario propagates four sources of uncertainty:
- uncertainty in the single E1 reference drift that defines H-CORE;
- the sampling uncertainty of σ itself (scaled-inverse-χ² with 8 dof; the larger of the two σ estimates is used);
- ±0.03 uncertainty in the reactive mass fraction;
- independent noise on each of the two validation repeats.

The registered statistic, mean absolute drift, gets larger when noise is added. Inflating σ therefore cannot make 1.60% easy to reach under H-CORE: the probability peaks at 0.032 near 2× σ and falls again at larger multiples (`hcore_sigma_breakeven.csv`).

## Proposed manuscript text (Section 2.9, after the registered comparison)

> Propagating hold-drift repeatability — estimated independently from point scatter within the measured hold trajectories and from the spread between the two validation repeats (0.023 and 0.022 in ln η) — together with the uncertainty of the single E1 reference drift and of the reactive fraction, H-CORE would produce a mean absolute drift as low as the observed 1.60% with probability 0.010 (10⁶ Monte Carlo draws). This probability stays below 0.05 when the repeatability is inflated up to eightfold.

Methods addition (Section 3.11):

> Hold-drift uncertainty was propagated by Monte Carlo simulation (10⁶ draws, seed 20261003). Repeatability was estimated from residual scatter of ln η about a linear time trend within each measured hold trajectory and, independently, from the two validation repeats; the larger estimate and its scaled-inverse-χ² sampling uncertainty were used.
