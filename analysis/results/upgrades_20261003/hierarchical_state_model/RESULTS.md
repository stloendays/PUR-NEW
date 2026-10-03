# Hierarchical Bayesian state model, anchor prediction intervals and thermal-basis comparison

Script: `scripts/hierarchical_state_model.py`. It runs as a single job of about 26 min. Base seed is 20261003. Every fit uses 4 chains with 5,000 kept draws after 2,000 warm-up draws.

Population: the 36-point, six-realization chemistry-audited E1–E3 set, defined as rows with `analysis_role` in {primary, primary_with_caveat}. The E1 +P curve is excluded from every fit and is used only as an external check.

There are two noise models:
- **Homoscedastic:** one σ for all realizations (sections 1–2).
- **Heteroscedastic:** one σ_r per realization, partially pooled (section 4).

The homoscedastic CSVs from the first run were reproduced byte-for-byte; their SHA-256 hashes were checked.

## Headline

| Quantity | Value |
|---|---|
| Manuscript numbers reproduced: R² 0.8553/0.9977; held-T 1.423×/1.058×; strict 1.088× [1.043–1.126]; E2 1.824×→1.086× [75.0–97.3%]; LOFO@120 1.028/1.119/1.049, pooled 1.099× | 17/17 exact |
| Convergence, homoscedastic (114 fits) | max R̂ 1.0016; min bulk ESS 1,290 |
| Convergence, heteroscedastic (248 fits: 4 ω priors × 62) | max R̂ 1.009; min bulk ESS 775 (main prior: max R̂ 1.006, min bulk ESS 1,019) |
| State spread τ, homoscedastic / heteroscedastic | 0.58 [0.29, 1.55] / 0.59 [0.30, 1.57] in ln η |
| Residual noise | Homoscedastic σ = 0.052 [0.041, 0.070]. Heteroscedastic σ_r medians span 0.011 (E1 R01) to 0.101 (E2 R03); typical exp(λ) = 0.032 |
| **τ / noise** | **Homoscedastic τ/σ = 11.1 [5.2, 30.7]. Heteroscedastic τ/exp(λ) = 18.6 [6.2, 64]**. Across all τ and ω prior settings the median stays between 7.9 and 18.6. |
| Apparent E_η at T_ref = 120 °C | 33.9 [30.9, 36.8] kJ mol⁻¹ (homoscedastic); 36.6 [34.6, 37.7] (heteroscedastic) |
| Full-data predictive fit | elpd_LOO: homoscedastic 49.8; heteroscedastic 66.5 (Δ = 16.7) |
| Posterior-mean anchor error, heteroscedastic (LOFO / strict / E2 / LORO) | 1.080× / 1.093× / 1.091× / 1.083× |
| 95% coverage, heteroscedastic | Pooled (a–c) 171/200 = 0.86 (0.80–0.90). LOFO 0.86 (0.80–0.91). LORO 0.92 (0.87–0.96). Strict 10/12. E2 anchor 6/8. |
| 95% coverage, homoscedastic | Pooled 0.63 (0.56–0.70). LOFO 0.61 (0.54–0.68). LORO 0.90 (0.85–0.94). Strict 10/12. E2 anchor 6/8. |
| 50% / 80% coverage on LOFO | **Neither model is calibrated.** Homoscedastic 0.32 / 0.49; heteroscedastic 0.35 / 0.56. The E2-held folds are worst (heteroscedastic 0.13 / 0.33). |
| Best thermal basis by AICc/BIC | VFT (ΔAICc 0). Quadratic +0.53, cubic +3.84, Arrhenius +29.3. |

## 1. State model (homoscedastic)

The model is:
- ln η_rT = a_r + β1 z + β2 z² + ε, with ε ~ N(0, σ²).
- a_r ~ N(μ_f(r), τ²).
- μ_f ~ N(7.5, 3²) for each nominal formulation.
- β_k ~ N(0, 50²); σ ~ half-Cauchy(0, 0.5); τ ~ half-Cauchy(0, 1).

**Why formulation-level means.** E1–E3 are designed NCO/OH levels (1.70/1.80/1.90), not exchangeable draws, and three levels cannot support a second variance component. τ is therefore the within-formulation state spread, δ_fr in a_fr = μ_f + δ_fr.

**Sampler.** A two-block Gibbs sampler:
- (a, β, μ) are drawn jointly from their multivariate normal conditional.
- σ² and τ² are drawn from inverse-gamma conditionals, using the half-Cauchy auxiliary-variable representation.

**State spread versus noise.** τ/σ = 11.1 [5.2, 30.7]. Realization state carries 99.2% of the non-thermal variance.

**τ prior sensitivity** (`tau_prior_sensitivity.csv`): five settings (half-Cauchy 0.25/1/2.5, flat on τ, IG(1, 0.01) on τ²) give τ/σ medians of 7.9–13.0. β is unchanged across them.

**Apparent E_η.** The quadratic basis gives E_η = 33.9 kJ mol⁻¹ at 120 °C and 43.8 kJ mol⁻¹ at 100 °C. The manuscript's linear descriptor (42.05 kJ mol⁻¹) is the slope averaged over 80–130 °C, which matches the local slope near 100 °C.

## 2. Posterior predictive intervals (homoscedastic)

The anchor observation enters the likelihood of the held realization's a_r. Point accuracy matches the frequentist plug-in procedure: 1.084× (LOFO), 1.088× (strict), 1.087× (E2).

Calibration depends on how many realizations the single σ is learned from:

| Setting | Coverage at 50/80/95% |
|---|---|
| Leave-one-realization-out (5 training realizations, 180 predictions) | 62/82/90% |
| E1 or E3 held out | 73/100/100% |
| E2 held out | 11/23/42% |

When E2 is held out, the training set is only E1 R01 and E3 R03. These are the two smoothest curves, with nearly identical residual patterns, so the fold σ is 0.012 against 0.052 for the full fit.

## 3. Thermal-basis comparison (`thermal_basis_comparison.csv`)

| Basis | fit × | ΔAICc | ΔBIC | held-T × | LOFO anchor × (pooled; range over anchors) | strict × | E2 anchor × | LORO anchor × |
|---|---|---|---|---|---|---|---|---|
| Arrhenius (linear 1/T) | 1.073 | 29.3 | 29.3 | 1.118 | 1.119 (1.102–1.141) | 1.168 | 1.142 | 1.120 |
| **Quadratic z** | 1.046 | 0.53 | 0.53 | 1.058 | 1.084 (1.063–1.099) | 1.088 | 1.086 | 1.082 |
| Cubic z | 1.045 | 3.84 | 3.55 | 1.055 | 1.084 (1.064–1.100) | 1.115 | 1.085 | 1.084 |
| VFT (shared B, T0) | 1.045 | 0 | 0 | 1.055 | 1.084 (1.063–1.099) | 1.081 | 1.087 | 1.082 |
| WLF (Tr = 120 °C) | identical to VFT (exact reparameterization; C1 = 3.49, C2 = 130.9 K) | | | | | | | |

Bayesian (homoscedastic) elpd_LOO: 35.5 (Arrhenius), 49.8 (quadratic), 48.9 (cubic).

- **Quadratic vs VFT:** tied on every task. They differ by ≤ 0.007× in error and by 0.53 AICc.
- **Cubic:** matches on interpolation, but extrapolates worse (strict holdout 1.115×).
- **Arrhenius:** worst on every metric.
- **VFT stability:** T0 is 262 K on the full data and moves between 237 and 271 K across the strict-holdout folds.

## 4. Heteroscedastic hierarchical noise model

**Model.**
- Noise: ε_rT ~ N(0, σ_r²), with log σ_r ~ N(λ, ω²).
- Hyperpriors: λ ~ N(log 0.05, 1.5²); ω ~ half-Normal(0, 1) (main setting).
- σ_r support is truncated to [1e-4, 10] as a numerical guard. The truncated mass is negligible at the posterior ω.
- All other priors are as in section 1.

**Sampler (Metropolis-within-Gibbs).**
- (a, β, μ) are drawn jointly from their multivariate normal conditional, given σ_r and τ.
- Each (log σ_r, a_r) pair is updated as a block: random-walk Metropolis on log σ_r with a_r integrated out, then an exact draw of a_r.
- τ² uses the conjugate half-Cauchy auxiliary update; λ has a normal conditional; log ω is updated by Metropolis.
- Interweaving scale and shift moves on (ω, λ, log σ_r) remove the funnel between ω and the anchor-only σ_r.
- Step sizes adapt only during warm-up. Acceptance rates are 0.41–0.44.

**Prediction for a held realization.** The held realization's σ_r is informed only by its anchor, so its predictive draws come essentially from the population distribution of σ_r, integrated over (λ, ω).

**Fit.** The posterior separates a low-noise group (E1 R01 0.011, E3 R03 0.017, E2 R01 0.028) from E2 R03 (0.101 [0.062, 0.197]), with ω = 0.87 [0.43, 1.71]. The predictive fit improves sharply: elpd_LOO rises from 49.8 to 66.5 and WAIC falls from −101.0 to −135.1. Downweighting E2 R03 moves the shape slightly (β1 4.40, β2 3.37; E_η at 120 °C 36.6 kJ mol⁻¹).

### Model comparison (main ω prior; `model_comparison_coverage.csv` has all priors)

| Task (n) | Model | 50% | 80% | 95% (Clopper–Pearson) | 95% half-width ×/÷ | Post-mean error × |
|---|---|---|---|---|---|---|
| LOFO, all anchors (180) | homo | 0.32 | 0.49 | 0.61 (0.54–0.68) | 1.089 | 1.084 |
| | hetero | 0.35 | 0.56 | 0.86 (0.80–0.91) | 1.167 | 1.080 |
| LOFO, E2 held (120) | homo | 0.11 | 0.23 | 0.42 (0.33–0.51) | 1.041 | 1.098 |
| | hetero | 0.13 | 0.33 | 0.79 (0.71–0.86) | 1.105 | 1.098 |
| LOFO, E1/E3 held (60) | homo | 0.73 | 1.00 | 1.00 (0.94–1.00) | 1.185 | 1.044 |
| | hetero | 0.80 | 1.00 | 1.00 (0.94–1.00) | 1.292 | 1.025 |
| Strict holdout (12) | homo | 0.33 | 0.58 | 0.83 (0.52–0.98) | 1.114 | 1.088 |
| | hetero | 0.33 | 0.58 | 0.83 (0.52–0.98) | 1.144 | 1.093 |
| E2 same-formulation anchor (8) | homo | 0.63 | 0.75 | 0.75 (0.35–0.97) | 1.157 | 1.087 |
| | hetero | 0.63 | 0.75 | 0.75 (0.35–0.97) | 1.360 | 1.091 |
| Leave-one-realization-out (180) | homo | 0.62 | 0.82 | 0.90 (0.85–0.94) | 1.167 | 1.082 |
| | hetero | 0.49 | 0.82 | 0.92 (0.87–0.96) | 1.338 | 1.083 |
| Pooled a–c (200) | homo | 0.33 | 0.51 | 0.63 (0.56–0.70) | 1.093 | 1.084 |
| | hetero | 0.36 | 0.57 | 0.86 (0.80–0.90) | 1.174 | 1.082 |

Realization-cluster bootstrap 95% intervals for the 95% coverage (heteroscedastic):
- Pooled (a–c): 0.62–0.99.
- LORO: 0.77–1.00.

### ω prior sensitivity (`hetero_omega_prior_sensitivity.csv`; all four settings run on every task)

| ω prior | ω median | τ/exp(λ) | 95% cov. LOFO | 95% cov. LOFO E2-held | 95% cov. pooled | 95% cov. LORO | 80% cov. pooled |
|---|---|---|---|---|---|---|---|
| half-Normal(0, 0.5) | 0.72 | 18.2 | 0.70 | 0.55 | 0.71 | 0.91 | 0.52 |
| **half-Normal(0, 1)** (main) | 0.87 | 18.6 | 0.86 | 0.79 | 0.86 | 0.92 | 0.57 |
| half-Cauchy(0, 1) | 0.89 | 18.3 | 0.89 | 0.83 | 0.88 | 0.92 | 0.58 |
| half-Normal(0, 2) | 0.99 | 18.3 | 0.96 | 0.93 | 0.95 | 0.94 | 0.65 |

The main ω prior was fixed before any coverage was computed and was not changed afterwards. The other three settings are reported as run.

### Reading

The heteroscedastic model is the better-calibrated model.
- It fits held-out observations much better (ΔelpdLOO = +16.7).
- It is near nominal coverage at 80% and 95% when held out by realization (0.82 and 0.92).
- It raises 95% coverage on the formulation-held tasks from 0.61–0.63 to 0.86, with no change in point accuracy.

LOFO remains uncalibrated in the centre of the distribution, under both models:
- 50% and 80% coverage is 0.35 and 0.56 for the heteroscedastic model.
- In the E2-held folds the shape and the population noise level are learned from two realizations only (E1 R01, E3 R03), and both are smooth.
- The widened tails recover most of the 95% shortfall, but the central intervals stay too narrow.
- The tail coverage on these folds depends on the ω prior (E2-held 95% coverage 0.55–0.93). This sensitivity is expected, because the data contain no information about between-realization noise variability once E2 is removed.

The strict-holdout and E2-anchor coverages are the same under both models (10/12 and 6/8). Both 95% misses in each task are the E2 R03 points at 120 and 130 °C.

## How this strengthens manuscript sections 2.2–2.3

- **2.2:** The level-shift picture becomes a variance decomposition. The state spread is 11–19 times the residual noise in both noise models and under every τ and ω prior tested.
- **2.2, basis paragraph:** The quadratic choice is supported against Arrhenius, cubic, VFT and WLF across fit, held-temperature and all three anchor tasks.
- **2.3:** The one-anchor reconstructions gain posterior predictive intervals. The heteroscedastic model gives near-nominal 80% and 95% coverage for new realizations and keeps the manuscript's point accuracy.

## Proposed manuscript / SI text (heteroscedastic model)

> A hierarchical Bayesian version of the state-conditioned model with realization intercepts nested in formulation means and partially pooled realization-specific noise (Metropolis-within-Gibbs, four chains, R̂ ≤ 1.01) placed the between-realization state spread at τ = 0.59 (95% CrI 0.30–1.57) in ln η, 19-fold (6–64) larger than the typical residual scatter of 0.032. Conditioning each held realization on a single anchor through its likelihood reproduced the reconstruction errors (posterior-mean errors of 1.093× in the strict holdout and 1.091× for E2) and, for held realizations, gave nominal 80% and 95% predictive intervals with 82% and 92% empirical coverage over 180 predictions. Among alternative thermal bases, the shared quadratic form performed as well as a Vogel–Fulcher–Tammann form (ΔAICc = 0.5; strict-holdout error 1.088× versus 1.081×) and better than Arrhenius (1.168×) or cubic (1.115×) forms.

## Files

**Shared**
- `summary.json`: reproduction checks, seeds, R̂/ESS, posteriors, coverage and input SHA-256. The `heteroscedastic` block holds the section-4 results.
- `hierarchical_state_model_diagnostics.png`:
  - (A) strict-holdout predictive bands (homoscedastic);
  - (B) coverage for both models, all tasks, 50/80/95% with Clopper–Pearson intervals;
  - (C) basis comparison.
- `model_comparison_coverage.csv`: homoscedastic versus heteroscedastic, all ω priors.

**Homoscedastic**
- `posterior_summary_quadratic.csv`
- `mcmc_diagnostics_full_quadratic.csv`
- `mcmc_diagnostics_task_fits.csv`
- `tau_prior_sensitivity.csv`
- `posterior_predictive_anchor_tasks.csv`
- `coverage_summary.csv`
- `thermal_basis_comparison.csv`
- `thermal_basis_lofo_by_anchor.csv`

**Heteroscedastic**
- `hetero_posterior_summary_quadratic.csv`
- `hetero_posterior_predictive_anchor_tasks.csv`
- `hetero_coverage_summary.csv`
- `hetero_mcmc_diagnostics_task_fits.csv`
- `hetero_omega_prior_sensitivity.csv`
