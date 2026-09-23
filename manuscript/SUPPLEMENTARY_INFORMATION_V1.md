# Supplementary Information

## State-Conditioned Rheology Enables Experiment Selection in Reactive Polyurethane Hot-Melt Adhesives

### Scope of this Supplementary Information

This Supplementary Information (SI) provides the analysis definitions, supporting numerical results, provenance rules, and outcome-blind decision details required to reproduce the claims made in the main manuscript.

The SI is deliberately restricted to analyses that support the final scientific framework. Superseded exploratory model variants, engineering failures, abandoned prompting strategies, and implementation diagnostics that are not part of the final scientific analysis are not presented here. All versioned raw and intermediate records remain retained in the repository for auditability.

The primary scientific claims supported here are:

1. realization-dependent viscosity variation within the local reactive-PUR family is predominantly low-dimensional;
2. a shared local temperature-response shape can be transferred to an unseen formulation after one state-specific viscosity anchor;
3. short-range 120–130 °C prediction remains accurate when both formulation identity and the high-temperature target region are withheld from thermal-shape fitting;
4. thermal-hold trajectory is a separate, strongly formulation-sensitive design coordinate;
5. the resin-modified validation formulation substantially suppresses the matched-window 120 °C viscosity drift;
6. the retrospective scientific-Agent benchmark is structurally outcome-blind and concentrates committed decisions inside the predeclared near region.

---

# Supplementary Note 1 | Local formulation design and primary analysis population

The original local formulation space consisted of five reactive polyurethane hot-melt adhesive formulations based on PPG2000, STEPANPOL PDP-70 and 4,4'-MDI. E1–E3 varied the reported NCO:OH ratio at a fixed 50/50 PPG2000/PDP-70 ratio. E4 and E5 retained NCO:OH = 1.80 while changing the polyol ratio. A later resin-modified formulation, F1, introduced AC1920 and TK100 while retaining the same PPG2000/PDP-70 nominal ratio.

## Supplementary Table S1 | Local formulations

| Formulation | Stage | PPG2000/PDP-70 | Reported NCO:OH | PPG2000 | PDP-70 | AC1920 | TK100 | MDI | Basis |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| E1 | original | 50/50 | 1.70 | 121.07 | 121.07 | — | — | 57.86 | g |
| E2 | original | 50/50 | 1.80 | 119.71 | 119.71 | — | — | 60.57 | g |
| E3 | original | 50/50 | 1.90 | 118.39 | 118.39 | — | — | 63.23 | g |
| E4 | original | 60/40 | 1.80 | 144.30 | 96.20 | — | — | 59.50 | g |
| E5 | original | 40/60 | 1.80 | 95.35 | 143.02 | — | — | 61.63 | g |
| F1 | follow-up | 50/50 | not reconstructed | 39.60 | 39.60 | 17.00 | 5.00 | 20.19 | source-reported parts |

No NCO:OH value was reconstructed for F1 because the source record did not contain the information needed to verify a stoichiometric calculation.

## Primary temperature-sweep analysis population

Seven complete 80–130 °C viscosity curves are present in the raw local table. One E1 curve is explicitly labelled with phosphoric-acid context in the source record. Because that additive condition is not represented in the compact formulation definition used for the state analysis, the primary analysis uses the six chemistry-comparable complete realizations listed below.

This exclusion is based on chemical comparability rather than on the direction of the statistical result. The excluded curve remains preserved in the versioned raw dataset.

## Supplementary Table S2 | Chemistry-audited temperature-sweep realizations

| Realization | Formulation | Retest after 1 d | n temperatures | Apparent $E_\eta$ (kJ mol$^{-1}$) | $R^2$, $\ln\eta$ vs $1/T$ |
|---|---|---:|---:|---:|---:|
| E1 R01 day-1 | E1 | yes | 6 | 42.712 | 0.9962 |
| E2 R03 | E2 | no | 6 | 37.634 | 0.9651 |
| E2 R01 | E2 | no | 6 | 42.661 | 0.9897 |
| E2 R02 | E2 | no | 6 | 41.227 | 0.9901 |
| E2 R02 day-1 | E2 | yes | 6 | 44.551 | 0.9948 |
| E3 R03 | E3 | no | 6 | 43.525 | 0.9959 |

The chemistry-audited primary temperature-sweep dataset therefore contains 36 observations from six complete realizations of three nominal formulations.

---

# Supplementary Note 2 | State-conditioned representation of local temperature-dependent viscosity

The analysis distinguishes nominal formulation identity from the experimentally realized rheological state.

Temperature is represented by the centered inverse-temperature coordinate

$$
z(T)=10^3\left(\frac{1}{T}-\frac{1}{T_{\mathrm{ref}}}\right),
\qquad T_{\mathrm{ref}}=393.15~\mathrm{K},
$$

with $T$ expressed in kelvin.

The formulation-only and state-conditioned models use the same quadratic thermal-response basis:

$$
\ln \eta_{fr}(T)
=
\mu_f+\beta_1 z(T)+\beta_2 z(T)^2+\varepsilon_{frT},
$$

and

$$
\ln \eta_{fr}(T)
=
a_{fr}+\beta_1 z(T)+\beta_2 z(T)^2+\varepsilon_{frT},
$$

respectively. Here $f$ denotes nominal formulation and $r$ a measured realization. The realization-specific intercept $a_{fr}$ is fitted directly and locates the realized viscosity scale. Conceptually, $a_{fr}=\mu_f+\delta_{fr}$, where $\delta_{fr}$ is the realization-specific displacement from the formulation baseline; the present regression estimates $a_{fr}$ directly rather than attempting to identify these two contributions separately.

## Supplementary Table S3 | State-model comparison

| Representation | Interpretation | Variance explained / predictive summary |
|---|---|---:|
| formulation-only, shared quadratic thermal response | nominal formulation + shared thermal shape | $R^2 = 0.8553$ |
| realization-conditioned, shared quadratic thermal response | realized viscosity scale + shared thermal shape | $R^2 = 0.9977$ |
| held-temperature multiplicative error, formulation-only quadratic | leave-one-temperature-out prediction | 1.423× |
| held-temperature multiplicative error, state-conditioned quadratic | leave-one-temperature-out prediction | 1.058× |

The same-order comparison isolates the effect of replacing formulation-level intercepts with realization-specific intercepts rather than changing the thermal basis at the same time. As an additional sensitivity check, restricting both models to a linear thermal response increases $R^2$ from 0.8519 for the formulation-only model to 0.9943 for the state-conditioned model. The same structural conclusion is also recovered without the parametric regression model. Singular-value decomposition of the chemistry-audited log-viscosity matrix after temperature-wise centering assigns 99.63% of between-realization variance to the first singular mode. The corresponding loading vector has cosine similarity 0.9998 to a constant vector.

Thus, within the present local chemistry family, the dominant realization effect is almost indistinguishable from a uniform vertical displacement in log-viscosity space.

---

# Supplementary Note 3 | Leave-one-formulation one-point calibration

To test whether the shared thermal-response shape transfers beyond the formulation used to fit it, all realizations of one nominal formulation were excluded from fitting in each fold. The shared response was $g(T)=\beta_1z(T)+\beta_2z(T)^2$.

For each held realization, one measured viscosity value at anchor temperature $T_0$ was used to estimate

$$
\hat a_{fr}=\ln \eta_{fr}(T_0)-\hat g(T_0),
$$

after which all remaining temperatures were reconstructed from $\widehat{\ln\eta}_{fr}(T)=\hat a_{fr}+\hat g(T)$.

## Supplementary Table S4 | Pooled leave-one-formulation transfer by anchor temperature

| Anchor temperature (°C) | Held realizations | Pooled multiplicative RMSE |
|---:|---:|---:|
| 80 | 6 | 1.063 |
| 90 | 6 | 1.086 |
| 100 | 6 | 1.086 |
| 110 | 6 | 1.066 |
| 120 | 6 | 1.099 |
| 130 | 6 | 1.096 |

Across the full measured temperature range, pooled one-point transfer remains approximately 1.06–1.10× in multiplicative-RMSE space.

## Supplementary Table S5 | Formulation-specific reconstruction using a 120 °C anchor

| Held formulation | Held realizations | Multiplicative RMSE |
|---|---:|---:|
| E1 | 1 | 1.028 |
| E2 | 4 | 1.119 |
| E3 | 1 | 1.049 |
| pooled | 6 | 1.099 |

The one-point experiment should be interpreted as state calibration inside a validated local chemistry neighborhood. It is not evidence for a universal polyurethane master curve.

---

# Supplementary Note 4 | Joint formulation-and-temperature holdout

A stricter stress test withheld both formulation identity and the high-temperature prediction region.

For each fold:

1. one nominal formulation was removed completely from thermal-shape fitting;
2. the shared thermal response was fitted only to the other formulations at temperatures $\leq110~^\circ\mathrm{C}$;
3. one measured 110 °C viscosity value from the unseen realization was supplied to determine the state offset;
4. viscosity was predicted at 120 and 130 °C, neither of which contributed to fitting the shared shape.

## Supplementary Table S6 | Strict local extrapolation summary

| Scope | Group | n predictions | Multiplicative RMSE | Median absolute percentage error | Mean absolute percentage error |
|---|---|---:|---:|---:|---:|
| overall | all | 12 | 1.088 | 5.68% | 6.32% |
| target temperature | 120 °C | 6 | 1.087 | 5.68% | 6.18% |
| target temperature | 130 °C | 6 | 1.089 | 6.18% | 6.47% |
| held formulation | E1 | 2 | 1.096 | 9.10% | 9.10% |
| held formulation | E2 | 8 | 1.080 | 1.64% | 4.56% |
| held formulation | E3 | 2 | 1.110 | 10.58% | 10.58% |

A 10,000-replicate bootstrap that resampled complete held realizations produced:

$$
\mathrm{multiplicative\ RMSE}_{50\%}=1.087,
$$

with a 95% interval of

$$
1.043\text{--}1.126\times .
$$

The maximum individual multiplicative error in this test was approximately 1.189×.

The supported claim is therefore limited to **10–20 °C short-range extrapolation inside the chemistry-audited E1–E3 neighborhood after one state-specific anchor**.

---

# Supplementary Note 5 | Apparent local temperature-response descriptor

For each chemistry-audited complete realization, $\ln\eta$ was regressed against $1/T$ with $T$ in kelvin. The descriptor was calculated as $E_\eta=R\,\mathrm{d}\ln\eta/\mathrm{d}(1/T)$ using $R=8.314462618~\mathrm{J\,mol^{-1}\,K^{-1}}$.

This descriptor is used only to summarize the local temperature dependence of viscosity and is not interpreted as a reaction activation energy.

Across the six chemistry-audited realizations:

$$
E_\eta \approx 42.05\pm2.43~\mathrm{kJ\,mol^{-1}},
$$

corresponding to a coefficient of variation of approximately 5.77%.

The important result is not exact equality of slopes, but the comparatively narrow local spread of the temperature-response coordinate relative to the much larger changes observed in viscosity level and thermal-hold trajectory.

---

# Supplementary Note 6 | Thermal-hold dynamics and matched-window validation

Original E1 and E5 formulations were measured during isothermal holding at 120 °C at 15, 30, 60 and 90 min.

The follow-up resin-modified formulation F1 was measured in two repeat runs at 15, 30, 45 and 60 min.

The matched-window stability index used for direct comparison is

$$
SI_{15\rightarrow60}
=
\frac{\eta_{60}-\eta_{15}}{\eta_{15}}.
$$

## Supplementary Table S7 | Raw 120 °C thermal-hold measurements

| Formulation | Repeat | 15 min | 30 min | 45 min | 60 min | 90 min |
|---|---|---:|---:|---:|---:|---:|
| E1 | R01 | 708.7 | 728.6 | — | 776.1 | 828.1 |
| E5 | R02 | 2210 | 2470 | — | 3349 | 4267 |
| F1 | repeat 1 | 1230 | 1189 | 1203 | 1228 | — |
| F1 | repeat 2 | 1281 | 1260 | 1289 | 1320 | — |

## Supplementary Table S8 | Thermal-hold response descriptors

| Formulation / repeat | Measured window | 15→60 min change | 15→90 min change | Descriptive $\mathrm{d}\ln\eta/\mathrm{d}t$ |
|---|---|---:|---:|---:|
| E1 | 15–90 min | +9.51% | +16.85% | 0.125 h$^{-1}$ |
| E5 | 15–90 min | +51.54% | +93.08% | 0.537 h$^{-1}$ |
| F1 repeat 1 | 15–60 min | −0.16% | — | not used as headline kinetic descriptor |
| F1 repeat 2 | 15–60 min | +3.04% | — | not used as headline kinetic descriptor |

The E5/E1 ratio of fitted descriptive log-viscosity slopes is

$$
0.537/0.125 \approx 4.29.
$$

For F1, the matched-window physical validation is more informative than fitting a kinetic coefficient because the observed 15–60 min profiles are nearly flat.

The two F1 repeats give:

- repeat 1: −0.16%;
- repeat 2: +3.04%;
- replicate-mean net change: +1.47%;
- mean absolute drift: 1.60%.

Relative to E1, the best original local reference over the same 15–60 min interval, the F1 mean absolute drift is reduced by approximately 83%.

A proportional-dilution null was evaluated from the source-reported formulation parts. The reactive-core fraction in F1 is

$
rac{39.60+39.60+20.19}{39.60+39.60+20.19+17.00+5.00}
=
rac{99.39}{121.39}
=
0.8189.
$

If the E1 15–60 min drift of 9.51% scaled linearly with this fraction, the dilution-only expectation would be

$
9.51%	imes0.8189=7.79%.
$

The measured F1 mean absolute drift is 1.60%. Thus the observed reduction from E1 is 7.91 percentage points, whereas proportional dilution predicts a reduction of only 1.72 percentage points. The measured suppression is approximately 4.6-fold larger than the dilution-only reduction.

The validation therefore supports a low-drift rheological region and shows that the stabilization exceeds simple proportional dilution of the original reactive core.

---

# Supplementary Note 7 | External PUR evidence and generalization boundary

The external evidence layer is used to define chemical plausibility and the boundary of the local result, not as a direct predictor of the validation formulation.

The curated HMPUR database integrates public papers, patents, open datasets and structured protocol records. The associated project database contains 21 sources, 85 standardized formulations, 278 formulation-component records, 547 property/performance observations, 22 experimental/process protocols, 4559 temperature-viscosity curve points and 1599 descriptor records.

The dense external polyurethane-prepolymer set contains 39 temperature-viscosity curves and 4559 individual measurements.

Reanalysis of these external curves shows that $\ln\eta$ versus $1/T$ is generally well represented locally:

- median $R^2 \approx 0.9967$;
- 37 of 39 curves have $R^2\ge0.98$.

However, the apparent temperature-response descriptor spans approximately

$$
34.7\text{--}94.2~\mathrm{kJ\,mol^{-1}},
$$

which is much broader than the local E1–E3 range.

This broader distribution is important for claim scope. The local shared thermal shape is treated as a **local transferable representation**, not a universal PUR relation.

External formulation records containing acrylic-like and tackifier-like modifiers are used as evidence-bounded intervention priors. Numeric modifier fractions are used as quantitative anchors only when their denominator basis is sufficiently explicit. Records with ambiguous bases remain directional evidence.

---

# Supplementary Note 8 | Outcome-blind candidate space

The retrospective decision benchmark tests whether the later validated formulation region is recoverable when the runtime is denied access to the validation formulation and its measured outcome.

The benchmark does not claim that the current software architecture existed before the original wet-lab follow-up. It evaluates recoverability under a formalized outcome-blind reconstruction.

The scored candidate space contains 73 nodes.

The candidate space includes:

- the measured E1–E5 reactive-core formulations;
- interpolation points inside the measured reactive-core space;
- a uniform AC1920-like / TK100-like modifier lattice built on the E2 reactive core;
- external evidence references attached to candidate construction;
- no post-result validation information.

The true F1 validation formulation is deliberately not one of the 73 nodes.

After unblinding, the normalized modifier coordinates of F1 are:

$$
\mathrm{AC1920}=14.004\%,\qquad
\mathrm{TK100}=4.119\%.
$$

The predeclared near region is defined by an $L_1$ modifier-plane distance threshold of 7.5 percentage points.

Eighteen of 73 candidate nodes fall inside this region.

Thus, exact recovery was impossible by construction; the benchmark evaluates direction and region recovery.

---

# Supplementary Note 9 | Frozen Agent evaluation

The confirmatory outcome-blind series contains 10 attempted runs under the same evidence contract.

Results:

- attempted runs: 10;
- valid runs: 10;
- abstentions: 2;
- committed decisions: 8;
- committed decisions inside the predeclared near region: 8/8.

The eight committed decisions comprise:

- S1C41: 6 selections;
- S1C46: 1 selection;
- S1C40: 1 selection.

The mean modifier-plane $L_1$ distance of the eight committed decisions to the held-out F1 composition is 2.281 percentage points, with median 1.877 percentage points and maximum 4.377 percentage points.

## Supplementary Table S9 | Run-level outcome-blind decisions

| Run | Decision | Selected candidate | AC1920 (%) | TK100 (%) |
|---:|---|---|---:|---:|
| 1 | commit | S1C41 | 15.0 | 5.0 |
| 2 | abstain | — | — | — |
| 3 | commit | S1C46 | 17.5 | 5.0 |
| 4 | commit | S1C41 | 15.0 | 5.0 |
| 5 | commit | S1C41 | 15.0 | 5.0 |
| 6 | commit | S1C41 | 15.0 | 5.0 |
| 7 | commit | S1C41 | 15.0 | 5.0 |
| 8 | abstain | — | — | — |
| 9 | commit | S1C41 | 15.0 | 5.0 |
| 10 | commit | S1C40 | 15.0 | 2.5 |

The naive single-pass LLM baseline and uniform-random lattice baseline are retained because they are required to interpret the structured Agent result.

For a single uniform-random draw from the same candidate lattice, the exact near-region probability is

$$
18/73 = 24.66\%.
$$

At the run level, the confirmatory Agent recovered the near region in 8 of 10 attempted runs (80%); the remaining two runs abstained. Conditional on commitment, all 8 of 8 selected candidates were inside the near region.

The benchmark should not be interpreted as evidence that the language model independently discovered the formulation. The deterministic scientific policy defines most of the useful geometry of the decision space.

## Supplementary Table S10 | Strategy-ladder comparison

| Strategy | Attempted runs | Named decisions | Abstentions | Dual-axis recovery | Near-region recovery | Mean modifier-plane $L_1$ (pp) |
|---|---:|---:|---:|---:|---:|---:|
| initial proximity-reward strategy | 5 | 5 | 0 | 0/5 | 0/5 | 12.115 |
| minimum-intervention diagnostic | 3 | 1 | 1 | 0/1 | 0/1 | 15.623 |
| + intervention-coverage gate | 5 | 3 | 2 | 3/3 | 3/3 | 1.877 |
| + deterministic ordering withheld | 5 | 4 | 1 | 4/4 | 4/4 | 2.061 |
| confirmatory series | 10 | 8 | 2 | 8/8 | 8/8 | 2.281 |

For named decisions, the 95% Wilson interval for dual-axis/near-region recovery changed from [0.00, 0.43] in the initial 0/5 series to [0.68, 1.00] in the final 8/8 series. These intervals do not overlap. The minimum-intervention series is retained as a diagnostic because its small number of named outputs does not support the headline rate comparison.

The naive single-pass baseline produced 7 named decisions from 10 attempts, with 0/7 near-region and 0/7 dual-axis recovery. All seven named outputs selected the same reactive-core-only candidate. Its mean modifier-plane $L_1$ distance was 18.123 percentage points, compared with 12.074 percentage points under uniform random selection on the frozen lattice. Thus both the observed near-region rate (0/7 versus a 24.66% random-lattice expectation) and mean distance were worse than the corresponding uniform-random baselines.

## Supplementary Table S11 | Cross-model transfer under the same blinded evidence contract

| Model configuration | Attempted runs | Named decisions | Abstentions | Dual-axis recovery | Near-region recovery | Mean modifier-plane $L_1$ (pp) | Named selections |
|---|---:|---:|---:|---:|---:|---:|---|
| GPT-5.6-luna | 10 | 8 | 2 | 8/8 | 8/8 | 2.281 | S1C41 ×6, S1C46 ×1, S1C40 ×1 |
| GPT-5.5 | 5 | 4 | 0 | 4/4 | 4/4 | 1.877 | S1C41 ×4 |
| GPT-5.6-sol | 5 | 2 | 3 | 1/2 | 1/2 | 10.000 | S1C41 ×1, S1C02 ×1 |

Across the three model configurations, 13 of 14 named decisions retained both supported modifier axes and 13 of 14 entered the near region; S1C41 accounted for 11 of 14 named decisions. The intervention region therefore transferred across model configurations, while commitment reliability remained model dependent.

---

# Supplementary Note 10 | Attribution of decision improvement

The final decision architecture separates deterministic scientific rules from the language-model selection step.

Using modifier-plane distance to the later held-out formulation as the quantitative diagnostic:

- earlier rule-only reference: 15.115 percentage points;
- best final rule-only candidate: 2.615 percentage points;
- best attainable / selected Agent-region distance: approximately 1.877 percentage points.

Along the reported strategy ladder, the deterministic-policy stage accounts for approximately 94.4% of the observed best-case distance reduction before the final model-level choice.

The remaining approximately 5.6% corresponds to the additional best-case reduction between the final rule-only candidate and the final Agent-region floor.

This decomposition is used to support the conclusion that explicit scientific structure, not unconstrained language-model generation, supplies most of the quantitative decision improvement.

---

# Supplementary Note 11 | Blindness and provenance controls

The outcome-blind evaluation uses a programmatic evidence boundary.

Before the model payload is assembled, the scored runtime profile excludes:

- the held-out validation formulation;
- follow-up viscosity measurements;
- post-result derived statistics;
- post-result adjudication labels;
- direct aliases that would expose the held-out formulation through runtime tools.

The action layer blocks access attempts targeting blinded formulation information.

For each benchmark run:

1. the evidence contract and candidate space are fixed;
2. the Agent produces a recommendation or abstention;
3. the recommendation is serialized and hashed;
4. a blind-phase closure record is written;
5. the held-out truth is loaded only after closure;
6. adjudication verifies the frozen recommendation hash before scoring.

The held-out composition is therefore used only for post-closure scoring.

The benchmark remains retrospective because the current software and evaluation policy were formalized after the wet-lab follow-up. The manuscript therefore describes it as an **outcome-blind reconstruction**, not as a historical replay.

---

# Supplementary Note 12 | Recommended reproducibility map

The principal manuscript quantities can be regenerated from the following versioned files:

| Scientific quantity | Primary source |
|---|---|
| local formulations | `data/formulations.csv` |
| temperature-sweep measurements | `data/temperature_sweeps.csv` |
| thermal-hold measurements | `data/thermal_hold.csv` |
| apparent local $E_\eta$ fits | `analysis/results/local_thermal_curve_fits.csv` |
| one-point LOFO transfer | `analysis/results/local_leave_one_formulation_one_point.csv` |
| pooled anchor analysis | `analysis/results/local_leave_one_formulation_pooled.csv` |
| strict formulation + temperature holdout | `analysis/results/local_joint_formulation_temperature_extrapolation.csv` |
| strict extrapolation summary + bootstrap | `analysis/results/local_joint_formulation_temperature_extrapolation_summary.csv` |
| hold-time drift descriptors | `analysis/results/local_hold_dynamics.csv` |
| candidate lattice | `derived/stage1_blind_candidate_space_v1.json` |
| frozen confirmatory decisions | `results/stage1_blind_replay_v3h/arm_b_blind/frozen_recommendations.csv` |
| post-closure adjudication summary | `results/stage1_blind_replay_v3h/arm_b_blind/adjudication_summary.json` |
| strategy-ladder benchmark | `results/STAGE1_AI4SCI_REPORT.md` |
| GPT-5.5 transfer runs | `results/multimodel/gpt-5_5/arm_b_blind/` |
| GPT-5.6-sol transfer runs | `results/multimodel/gpt-5_6-sol/arm_b_blind/` |

Main-text Figures 1–5 are generated from versioned scripts and analysis outputs. The SI reports the corresponding numerical robustness checks and run-level tables without duplicating those main-text visualizations.

---

# Supplementary reporting boundary

The SI is intended to support the final manuscript claims rather than reproduce the full project-development history.

Accordingly, the following are not part of the scientific SI:

- software installation or environment failures;
- malformed-output runs;
- infrastructure retries;
- superseded prompt drafts;
- abandoned exploratory ranking policies;
- preliminary analyses that were replaced before the final claim set was frozen;
- historical engineering diagnostics unrelated to the final scientific comparison.

These records may remain available in the repository where useful for development provenance, but they are not treated as scientific evidence in the manuscript.

By contrast, all measurements and analyses that materially define the final reported conclusions are retained in the versioned scientific data and analysis files listed above.
