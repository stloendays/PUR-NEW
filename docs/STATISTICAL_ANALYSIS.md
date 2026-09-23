# Statistical and model analysis

> **Status — exploratory historical analysis.** This document predates the final chemistry audit and retains all seven complete temperature-sweep curves, including the deliberate E1 +P phosphoric-acid perturbation. Its 42-point fit statistics are therefore **not** the canonical manuscript headline values. The reader-facing manuscript and SI use six chemistry-comparable realizations (36 observations) for the primary same-composition analysis and treat E1 +P separately. Use `manuscript/MAIN_TEXT_V5.md`, `manuscript/SUPPLEMENTARY_INFORMATION_V5.md` and the current versioned analysis outputs for manuscript statistics.

## Scope

This exploratory analysis asks two separate questions.

1. **Does a formulation-only temperature model leave structured residual variation that is captured by experimental realization / process state?**
2. **Do temperature response and thermal-hold stability behave as distinct rheological coordinates in the current chemistry?**

The full local sweep table contains 42 measurements from 3 nominal formulations and 7 recorded curves. R01, R02 and R03 are opaque realization codes and do not encode operator identity. The analysis does not assign realization-to-realization variation to any specific physical cause.

Current audited manuscript and figure outputs report viscosity in mPa·s. The regression comparisons below operate on `ln(viscosity_reported)` or dimensionless ratios.

---

## Result 1 — a state-shift master curve is substantially stronger than a formulation-only model

### Competing models

The deliberately generous formulation-only baseline is

```text
M0: ln(eta) = formulation identity + shared temperature response
```

where formulation identity is categorical, so the model does not assume a linear NCO:OH effect.

The state-aware family is

```text
M2:  ln(eta_r) = alpha_r + beta1 * dx
M2q: ln(eta_r) = alpha_r + beta1 * dx + beta2 * dx^2
```

with

```text
dx = 1000/T_K - 1000/393.15 K
alpha_r = realization-specific vertical offset
```

`M2q` therefore assumes that different realizations share a common thermal-response shape but may occupy different absolute viscosity levels.

### Fit comparison

| model | R² | log-RMSE | multiplicative RMSE | AIC | BIC |
|---|---:|---:|---:|---:|---:|
| formulation only | 0.8952 | 0.3320 | 1.394× | 34.57 | 41.52 |
| formulation + day-1 flag | 0.9064 | 0.3137 | 1.368× | 31.80 | 40.49 |
| realization intercept + shared linear thermal shape | 0.9959 | 0.0660 | 1.068× | -93.07 | -79.17 |
| **realization intercept + shared quadratic thermal shape** | **0.9982** | **0.0430** | **1.044×** | **-127.04** | **-111.40** |
| realization-specific intercept + realization-specific slope | 0.9967 | 0.0587 | 1.060× | -90.98 | -66.65 |

Adding realization state to the formulation-only model reduces in-sample log-RMSE by about **87.0%** once the shared quadratic thermal shape is used. The AIC and BIC improvements are approximately **161.6** and **152.9** units, respectively.

A nested fixed-effects comparison gives a large realization contribution even against a formulation-only model that is allowed to have formulation-specific thermal slopes (`F = 198.6`, nominal `p = 4.2e-22`). Because temperature points within one realization are repeated measurements on the same trajectory, this nominal p-value is not treated as the primary evidence. The magnitude of the error reduction and the cross-validation results below are more important.

### Temperature shape does not need realization-specific slopes

After allowing a realization-specific vertical offset, adding a separate thermal slope for every realization does **not** improve the linear state-aware model (`F = 1.24`, nominal `p = 0.316`). Likewise, allowing formulation-specific thermal slopes after the state offsets are included does not improve the model (`F = 0.365`, nominal `p = 0.697`).

The main remaining systematic structure is slight shared curvature in inverse temperature: adding one common quadratic term improves the state-aware model strongly (`F = 44.7`, nominal `p = 1.3e-7`).

The resulting positive structural model is therefore

```text
ln(eta_r(T)) = alpha_r + g(T) + epsilon
```

where `alpha_r` is realization/state dependent and `g(T)` is a transferable thermal-response shape within the current local chemistry.

### Cross-validation

Leave-one-temperature-out validation keeps every realization represented in training but withholds one temperature from all curves.

| model | held-temperature log-RMSE | multiplicative error factor |
|---|---:|---:|
| formulation only | 0.3408 | 1.406× |
| state intercept + linear shape | 0.1048 | 1.110× |
| **state intercept + quadratic shared shape** | **0.0533** | **1.055×** |

Thus the state-aware quadratic model reduces held-temperature log-RMSE by about **84.4%** relative to formulation identity + temperature alone.

### One-point state calibration

A stricter test leaves one entire realization out while learning the shared thermal shape from the other realizations. One viscosity point from the held-out realization is then used only to calibrate its vertical offset; the remaining five temperatures are predicted.

Depending on which temperature is used as the single anchor, the multiplicative RMSE for the other five temperatures ranges from **1.062× to 1.093×**. In practical terms, one state-specific anchor measurement is sufficient to reconstruct the remaining 80–130 °C curve to roughly **6–9% multiplicative RMSE** in this small local dataset.

This is a stronger and more useful conclusion than simply stating that process history matters:

> **Within the present chemistry family, experimental realization primarily shifts the viscosity scale, while the temperature-response shape is transferable enough that one state anchor can calibrate the rest of the curve.**

### Bounded local formulation-and-temperature extrapolation

A stricter stress test withheld **both** formulation identity and the high-temperature prediction region. For each fold, one formulation was removed completely from shape fitting. The shared quadratic thermal response was learned only from the other formulations at temperatures **<=110 C**. For each realization of the unseen formulation, a single measured **110 C** viscosity value was then used to set the state offset, after which the model predicted the unseen **120 C and 130 C** responses.

Across 12 held predictions from six realizations and three nominal formulations, the pooled log-RMSE was **0.0845**, corresponding to a multiplicative RMSE of **1.088x**. The median absolute percentage error was **5.68%** and the mean absolute percentage error was **6.32%**. Performance was similar at the two extrapolated temperatures:

| held target temperature | multiplicative RMSE |
|---|---:|
| 120 C | **1.087x** |
| 130 C | **1.089x** |

A 10,000-replicate cluster bootstrap that resampled complete held realizations gave a 95% interval of approximately **1.043x-1.126x** for the pooled multiplicative RMSE. The largest individual multiplicative error was approximately **1.189x**.

This test is stronger than ordinary interpolation because neither the held formulation nor the 120-130 C target region contributes to fitting the shared thermal shape. It therefore supports a **short-range local extrapolation** claim:

> **Within the chemistry-audited E1-E3 neighborhood, the shared thermal-response representation can transfer to a completely unseen formulation and extrapolate 10-20 C beyond the fitted temperature range after one state-specific anchor measurement.**

The scope is deliberately narrow. This result does **not** establish cross-family transfer, long-range extrapolation, or a universal reactive-PUR master curve. The broader external database shows substantially wider thermal-sensitivity variation across chemistry families, so cross-chemistry extrapolation remains outside the supported claim.

### Mixed-effects sensitivity analysis

A mixed-effects model with formulation fixed effects, a shared quadratic thermal response and realization random intercept gives:

```text
random-intercept SD (log scale) = 0.325
residual SD (log scale)         = 0.047
ICC                              = 0.979
```

This is consistent with most remaining variance being organized at the realization/state level rather than as pointwise measurement scatter. However, there are only **7 realization groups**, so this mixed-effects estimate is supporting evidence rather than the headline inferential result.

---

## Result 2 — temperature response and time stability are distinct, differently tunable rheological coordinates

### Temperature coordinate

Individual local 80–130 °C curves remain well described by `ln(eta)` versus `1/T` as a compact descriptor:

```text
mean apparent E_eta = 41.87 kJ/mol
SD                  = 2.27 kJ/mol
CV                  = 5.4%
median R²            = 0.9948
```

This `E_eta` is an **apparent rheological temperature-sensitivity descriptor**, not a molecular reaction activation energy.

The narrow local dispersion is consistent with the master-curve result above: in the present chemistry family, much of the variation appears as a vertical viscosity-state shift rather than a wholesale change in thermal shape.

### Temporal coordinate

At 120 °C, E1 and E5 show approximately log-linear viscosity growth over 15–90 min:

| formulation | fitted dln(eta)/dt | R² | endpoint 15→90 drift |
|---|---:|---:|---:|
| E1 | 0.125 h⁻¹ | 0.9994 | +16.85% |
| E5 | 0.537 h⁻¹ | 0.9972 | +93.08% |

The fitted drift coefficients differ by about **4.29×**. The curve-level interaction is very large, but because E1 and E5 each contribute only one original hold trajectory, this is interpreted primarily as an effect-size result rather than a population-level significance claim.

The resin-modified follow-up formulation moves into a low-drift regime over the matched 15–60 min window:

```text
F1 repeat 1 SI = -0.16%
F1 repeat 2 SI = +3.04%
F1 mean SI     = +1.47%
```

Relative to the matched absolute drift, the F1 mean profile reduces drift by approximately:

```text
84.5% versus E1
97.1% versus E5
```

A pooled descriptive model across the two F1 repeats gives a common time slope of `0.0239 h^-1` with a 95% interval of `[-0.0337, 0.0815] h^-1`; with only two repeat trajectories this should not be promoted to a general null-hypothesis result. The important experimental fact is the small observed drift in both repeats.

The two F1 repeats differ in absolute level by an average factor of about **1.062×**, but that repeat-to-repeat ratio has only **1.42% CV** across the four time points. This mirrors the temperature-sweep result: an absolute state offset can coexist with a reproducible response shape.

### What can be claimed now

The current evidence supports the positive statement:

> **Reactive-PUR rheology in the tested system contains a comparatively transferable thermal-response shape and a strongly formulation-tunable temporal-stability response.**

It is still too strong to call the two axes statistically *orthogonal* or *independent*, because E5 and F1 do not yet have the same complete temperature-sweep characterization used for E1–E3. The paper should therefore use **distinct rheological coordinates** rather than **independent coordinates**.

---

## External-database context

The external database contains **4559 temperature-viscosity points from 39 prepolymer curves**. Across this much broader chemistry space, `ln(eta)` versus `1/T` remains highly regular (median curve R² = **0.9967**; 37/39 curves have R² >= 0.98), but the apparent thermal-sensitivity descriptor spans **34.7–94.2 kJ/mol**.

This is an important guardrail: the approximately 42 kJ/mol scale observed locally is **not universal across all PUR chemistry**. Thermal sensitivity is itself chemistry dependent at the broader database level.

A composition-level model using pNCO, polyol code and isocyanate code explains about **77.1%** of between-curve variation in the apparent thermal descriptor and about **88.4%** of fitted log viscosity at 75 °C. In that model, increasing pNCO by one percentage point is associated with a fitted `-1.43 kJ/mol` change in the apparent thermal descriptor (`p = 0.0074`) and a fitted viscosity multiplier of about `0.750×` at 75 °C (`p < 1e-9`). These are database-level associations, not causal kinetic coefficients.

The database also contains one patent family with **9 formulations** reporting both static melt viscosity and viscosity rise rate. Within this small set, static viscosity is not strongly correlated with rise rate (Pearson correlation between log viscosity and rise rate `r = -0.218`, `p = 0.574`; Spearman `rho = -0.351`, `p = 0.354`). The sample is too small to establish absence of correlation, but it supports treating stability as a non-redundant response. Two formulations with the same reported viscosity of 7900 cP have rise rates of **4.4%/h** and **7.9%/h**.

---

## Which result is stronger?

### Primary paper claim — strongest current result

**State-shift master curve + one-point state calibration + bounded local extrapolation.**

This result has the cleanest quantitative support because the same nominal formulations were measured across repeated realizations and the competing models can be compared directly. It produces a positive, practically testable statement:

> **A realization-specific viscosity-scale parameter plus a shared thermal-response function reconstructs the local 80–130 °C rheology far better than formulation identity and temperature alone; one anchor measurement transfers that shape to an unseen local formulation, and a stricter formulation-plus-temperature holdout retains approximately 1.09x pooled multiplicative error for 120–130 °C predictions.**

This should be the main statistical/modeling result.

### Secondary paper claim — scientifically interesting, slightly weaker with current coverage

**Temperature sensitivity and temporal stability are distinct design coordinates.**

The result is physically compelling because the thermal shape is comparatively stable while the 120 °C hold drift changes by several-fold and is strongly suppressed in F1. It should be retained as the second mechanistic/design result, but the manuscript should not claim formal statistical orthogonality without matched temperature-and-time characterization for more formulations.

### Role of mixed-effects / hierarchical modeling

Mixed-effects modeling should be kept as a robustness analysis showing that realization-level variance is large. It should not be the headline result because the number of realization groups is small. The fixed-state master-curve model, cross-validation and one-point calibration are more transparent and harder to overinterpret.

---

## Recommended manuscript-level formulation

The combined experimental/database story can now be written as:

> **Reactive PUR prepolymers exhibit a low-dimensional rheological state structure. Within the local chemistry family, repeated realizations primarily alter the viscosity scale while preserving a transferable temperature-response shape, enabling one-point state calibration of the full measured temperature curve. In contrast, isothermal viscosity drift is strongly formulation dependent and can be suppressed into a low-drift regime by formulation engineering. Broad external data show that the thermal-response scale changes across chemistry families, while independent industrial records treat viscosity stability as a separate property. Together, these results motivate state-conditioned rheological design using both thermal response and temporal stability rather than a single static viscosity target.**
