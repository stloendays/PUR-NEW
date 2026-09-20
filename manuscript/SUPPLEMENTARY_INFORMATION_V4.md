# Supplementary Information

## State-Conditioned Rheology and Explicit Decision Rules Guide Reactive Polyurethane Formulation Experiments

### Scope of this Supplementary Information

This Supplementary Information (SI) supports the V4 manuscript by separating the physical rheology evidence from the experiment-selection architecture. Notes 1–7 preserve the audited formulation, temperature-sweep, state-calibration, thermal-hold and external-evidence analyses inherited from V3. Notes 8 onward document the V4 hypothesis registry, 292-card experiment space, deterministic value-of-information (VOI) layer, confirmatory series, controlled ablations, tie-break attribution, freeze/adjudication order and the relationship to the earlier V3 benchmark.

The SI does not pool development-stage strategy variants to enlarge denominators. Confirmatory, diagnostic and extended series retain their own provenance and are summarized separately where that distinction matters.

The principal V4 claims supported here are:

1. realization-dependent viscosity variation in the local reactive-PUR family is predominantly a calibratable scale shift on a shared local thermal response;
2. one-point state calibration transfers that local thermal shape to a held formulation over the tested short temperature range;
3. thermal-hold trajectory is a separate formulation-sensitive coordinate;
4. the resin-modified validation formulation exhibits 1.60% mean absolute 15–60 min drift and falls well below the 7.79% proportional-dilution null;
5. the V4 decision problem contains 292 formulation-measurement cards generated from 73 formulation nodes and four measurement plans;
6. full V4 selects the evidence-supported family in 9/10 runs with zero zero-discrimination selections, whereas withholding the VOI score yields 0/5 supported-family selections and 3/5 zero-discrimination selections;
7. the rule-order arm yields 10/10 zero-discrimination selections overall;
8. critique alone does not repair a defective upstream decision order: the Skeptic identifies the zero-discrimination defect at high severity in 10/10 order-inverted runs, yet all ten frozen decisions commit.

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
| E1 GJJ day-1 | E1 | yes | 6 | 42.712 | 0.9962 |
| E2 CHH | E2 | no | 6 | 37.634 | 0.9651 |
| E2 GJJ | E2 | no | 6 | 42.661 | 0.9897 |
| E2 ZYX | E2 | no | 6 | 41.227 | 0.9901 |
| E2 ZYX day-1 | E2 | yes | 6 | 44.551 | 0.9948 |
| E3 CHH | E3 | no | 6 | 43.525 | 0.9959 |

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
| E1 | GJJ | 708.7 | 728.6 | — | 776.1 | 828.1 |
| E5 | ZYX | 2210 | 2470 | — | 3349 | 4267 |
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

$$
\frac{39.60+39.60+20.19}{39.60+39.60+20.19+17.00+5.00}
=
\frac{99.39}{121.39}
=
0.8189.
$$

If the E1 15–60 min drift of 9.51% scaled linearly with this fraction, the dilution-only expectation would be

$$
9.51\%\times0.8189=7.79\%.
$$

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

# Supplementary Note 8 | V3 predecessor benchmark and candidate-space inheritance

V4 inherits the 73-node formulation lattice and the outcome-blind evidence firewall established in V3. The held-out validation formulation is not itself a lattice node. This predecessor benchmark remains useful for provenance because it established that the later validated region could be recovered without exposing the validation formulation or its outcome to the runtime.

The V3 confirmatory series contained 10 attempts, 8 committed decisions and 2 abstentions. All 8 committed decisions entered the predeclared near region. The strategy-ladder analysis further showed that most of the numerical distance improvement came from explicit deterministic scientific policy rather than unconstrained language-model generation.

These V3 results are not pooled with V4. Their role in the V4 manuscript is architectural: they justify retaining the same blinded evidence boundary and formulation lattice while changing the decision object from a formulation candidate to an experiment card.

The full V3 strategy ladder, random-lattice comparison, cross-model transfer and approximately 94.4% distance decomposition remain preserved in `manuscript/SUPPLEMENTARY_INFORMATION_V1.md`, `results/STAGE1_AI4SCI_REPORT.md` and the frozen V3 result directories.

---

# Supplementary Note 9 | V4 decision object: 292 experiment cards

V4 crosses the frozen 73-node formulation lattice with four measurement plans:

1. `M-HOLD-120`: matched-window 120 °C thermal hold;
2. `M-REPEAT`: repeatability/state-control measurement;
3. `M-ANCHOR`: one-point viscosity anchor;
4. `M-SWEEP`: temperature sweep.

The Cartesian product therefore contains

$$
73\times4=292
$$

experiment cards.

The change is scientifically important because formulation choice and measurement choice are no longer conflated. A plausible composition can still be a poor experiment if its measurement cannot discriminate the registered hypotheses, and an appropriate measurement can still be wasted on a composition whose competing predictions collapse.

---

# Supplementary Note 10 | Frozen formulation-level hypothesis registry

Three formulation-level hypotheses were registered before V4 model runs and before post-freeze adjudication loaded the held-out wet-lab outcome.

## Supplementary Table S9 | Registered hypotheses

| ID | Formulation-level statement | Pre-result prediction | Falsification logic |
|---|---|---|---|
| H-CORE | matched-window drift is set by the reactive core; modifiers act only through inert-mass dilution | $SI_{15\rightarrow60}=9.51\%\times\phi_r$ | observed drift falls well below the dilution prediction |
| H-RESIN | resin modification suppresses drift beyond simple dilution | drift substantially below the H-CORE prediction | drift remains at or above the dilution prediction |
| H-DUAL | acrylic and tackifier axes play different roles; low drift requires the tackifier-containing dual-axis intervention | low drift only for tackifier-containing compositions | an acrylic-only composition reaches the same low-drift regime |

Here $\phi_r$ is the source-reported reactive-core mass fraction. The hypotheses do not claim a molecularly resolved reaction pathway.

For the completed dual-axis validation formulation,

$$
\phi_r=\frac{99.39}{121.39}=0.8189,
$$

giving the H-CORE prediction

$$
9.51\%\times0.8189=7.79\%.
$$

The measured mean absolute matched-window drift is 1.60%, which is used only in post-freeze adjudication.

---

# Supplementary Note 11 | Deterministic VOI and decision stability

Each V4 experiment card receives a deterministic score

$$
\mathrm{VOI}
=
w_{\mathrm{hyp}}D_{\mathrm{hyp}}
+w_{\mathrm{unc}}R_{\mathrm{unc}}
+w_{\mathrm{dec}}R_{\mathrm{dec}}
+w_{\mathrm{int}}I_{\mathrm{meas}}
-w_{\mathrm{ext}}X_{\mathrm{risk}}
-w_{\mathrm{proc}}P_{\mathrm{risk}}.
$$

The six normalized components represent hypothesis discrimination, uncertainty reduction, decision relevance, measurement interpretability, extrapolation risk and process-state risk. Base weights are 0.30, 0.20, 0.25, 0.10, 0.10 and 0.05, respectively.

The VOI score is a transparent scientific decision rule. It is not a Bayesian posterior and is not described as calibrated expected information gain.

Under the frozen registry, only the matched-window 120 °C hold carries non-zero hypothesis discrimination. The other three measurement plans observe coordinates on which the registered hypotheses do not make distinct predictions.

Independent perturbation of each VOI weight from 0.5× to 1.5× preserves the same five-card top set, the same intervention family and the same 120 °C hold measurement. The deterministic layer is therefore stable at the level of the tied top set rather than at the level of an arbitrary single representative.

---

# Supplementary Note 12 | Confirmatory V4 series

The full V4 confirmatory series was declared at $N=10$ before its first run. Model endpoint, prompts, evidence profile, candidate lattice, experiment-card inventory, hypothesis registry, measurement catalog and deterministic VOI implementation were held fixed.

## Supplementary Table S10 | Full V4 confirmatory series

| Quantity | Result |
|---|---:|
| declared / completed runs | 10 / 10 |
| abstentions | 0 / 10 |
| matched-window 120 °C hold selected | 10 / 10 |
| evidence-supported dual-axis family selected | 9 / 10 |
| 95% Wilson interval for supported-family selection | [0.596, 0.982] |
| selected experiment inside deterministic tied top set | 9 / 10 |
| zero-discrimination selections | 0 / 10 |
| mean hypothesis discrimination | 0.667 |
| mean post-hoc VOI | 0.6850 |
| Judge output-contract repairs | 0 / 10 |

Nine runs selected `S1C41::M-HOLD-120`. One run selected the acrylic-only `S1C39::M-HOLD-120` as a discriminating probe.

The result should not be interpreted as ten independent discoveries of a formulation. The series measures reproducibility of a frozen decision architecture under the same evidence contract.

---

# Supplementary Note 13 | Tie-break attribution and the measurable model-layer departure

The deterministic VOI layer is indifferent among five top-scoring dual-axis cards. A coded baseline then applies the supplied minimum-sufficient-intervention policy: maximize VOI, minimize total modifier burden, and finally break any remaining tie by identifier.

That deterministic baseline selects `S1C41::M-HOLD-120` in 10/10 cases. The frozen V4 series agrees in 9/10 runs and departs once.

The single departure, `S1C39::M-HOLD-120`, gives up 0.075 VOI relative to the tied maximum and selects an acrylic-only probe because it separates H-RESIN from H-DUAL, the pair left entangled by the dual-axis experiment.

This is the measurable model-layer contribution in the confirmatory series. The other 9/10 selections demonstrate competent application of a supplied scientific policy rather than independent inference of that policy.

---

# Supplementary Note 14 | Controlled VOI-score withholding

The score-withheld arm was declared at $N=5$. The model, endpoint, all five stage prompts, hypothesis registry, measurement catalog, evidence profile, structural firewall, 73-node lattice and all 292 experiment cards were held fixed. Only the deterministic VOI score, component vector, ranking/tie set, stability sweep and tool-generated acceptance/falsification criteria were withheld.

## Supplementary Table S11 | Full V4 versus VOI-score-withheld arm

| Quantity | Full V4 | VOI withheld |
|---|---:|---:|
| runs | 10 | 5 |
| evidence-supported family | 9/10 | 0/5 |
| 95% Wilson interval | [0.596, 0.982] | [0.000, 0.435] |
| reactive-core-only selections | 0/10 | 3/5 |
| matched-window 120 °C hold | 10/10 | 5/5 |
| zero-discrimination selections | 0/10 | 3/5 |
| mean hypothesis discrimination | 0.667 | 0.267 |
| mean post-hoc VOI | 0.6850 | 0.3931 |

The measurement choice survives score withholding because the registered failure mode still points to the 120 °C hold. The composition choice does not: three of five runs spend the experiment on a reactive-core-only composition that cannot separate the registered hypotheses.

---

# Supplementary Note 15 | Controlled rule-order inversion

The rule-order arm retains the same cards and VOI components but changes the lexicographic priority from `coverage → discrimination → relevance → burden` to `burden → coverage → discrimination → relevance`.

Under sufficiency-first ordering, the deterministic rank-1 experiment is a dual-axis hold with hypothesis discrimination 0.667. Under minimality-first ordering, the rank-1 experiment is a reactive-core-only hold with hypothesis discrimination 0.

The rule-order result comprises ten completed runs analyzed as a distinct decision-architecture arm and is not pooled with either full V4 or the score-withheld arm. Run-level provenance is retained in the versioned repository.

## Supplementary Table S12 | Rule-order arm

| Quantity | Result |
|---|---:|
| runs | 10 |
| zero-discrimination selections | 10/10 |
| reactive-core-only selections | 10/10 |
| evidence-supported family | 0/10 |
| matched-window 120 °C hold | 7/10 |
| high-severity Skeptic objection | 10/10 |
| Robustness recommended changing experiment | 5/10 |
| committed anyway | 10/10 |
| mean hypothesis discrimination | 0.000 |

Order inversion damages more than composition choice. Three of ten runs also divert from `M-HOLD-120` to `M-REPEAT`, whereas the score-withheld arm retains the matched-window hold in all five runs.

---

# Supplementary Note 16 | Critique does not substitute for decision authority

The order-inverted arm provides a direct architecture test.

In 10/10 runs, the Skeptic raises a high-severity objection identifying the same scientific defect: the selected reactive-core composition contains no modifier intervention and collapses the registered mechanism predictions, so the experiment cannot discriminate them.

The Robustness Adjudicator recommends changing the experiment in 5/10 runs. Nevertheless, all 10 frozen decisions commit to the rule-prioritized experiment.

The important result is therefore structural rather than rhetorical. A critique stage can diagnose a scientific failure and still fail to change the selected experiment when upstream rule priority retains decision authority.

---

# Supplementary Note 17 | Freeze and post-freeze adjudication

V4 preserves a strict order: pre-result evidence → experiment generation → deterministic VOI and stability diagnostics → Planner/Proposer/Skeptic/Robustness/Judge → Freeze → blind-phase closure → held-out wet-lab adjudication.

The adjudicator verifies the frozen recommendation hash before scoring.

Nine confirmatory V4 runs selected the dual-axis experiment family represented by the completed wet-lab validation. The remaining selection corresponds to a different formulation contrast and is therefore outside the available physical adjudication set.

For the dual-axis validation result:

- observed mean absolute $SI_{15\rightarrow60}=1.60\%$;
- H-CORE dilution prediction $=7.79\%$;
- H-CORE is falsified under the frozen criterion;
- H-RESIN survives;
- H-DUAL remains entangled with H-RESIN for a dual-axis experiment and requires an acrylic-only measurement for direct separation.

Because the wet-lab result existed before the V4 software architecture was formalized, this is a retrospective outcome-blind adjudication rather than a claim that V4 prospectively caused the original experiment to be run.

---

# Supplementary Note 18 | Reproducibility map

| Scientific quantity | Primary source |
|---|---|
| local formulations | `data/formulations.csv` |
| temperature-sweep measurements | `data/temperature_sweeps.csv` |
| thermal-hold measurements | `data/thermal_hold.csv` |
| experimental method metadata | `data/experimental_methods_metadata.csv` |
| realization provenance | `data/realization_metadata.csv` |
| apparent local $E_\eta$ fits | `analysis/results/local_thermal_curve_fits.csv` |
| one-point LOFO transfer | `analysis/results/local_leave_one_formulation_one_point.csv` |
| strict formulation + temperature holdout | `analysis/results/local_joint_formulation_temperature_extrapolation.csv` |
| candidate lattice | `derived/stage1_blind_candidate_space_v1.json` |
| V4 hypothesis registry | `configs/hypothesis_registry.json` |
| V4 measurement catalog | `configs/measurement_catalog.json` |
| V4 configuration | `configs/agent_v4.json` |
| deterministic VOI implementation | `src/pur_new/voi.py` |
| V4 confirmatory series | `results/agent_v4_voi/series_n10/` |
| VOI-score-withheld series | `results/agent_v4_voi/series_ablation_voi_withheld_n5/` |
| rule-order series | `results/agent_v4_voi/series_ablation_rule_order_minimality_first_n5/` |
| controlled-ablation summary | `results/agent_v4_voi/rule_layer_ablation.json` |
| V4 report | `results/agent_v4_voi/AGENT_V4_REPORT.md` |
| V3 predecessor SI | `manuscript/SUPPLEMENTARY_INFORMATION_V1.md` |

---

# Supplementary reporting boundary

The V4 SI reports only evidence needed to reproduce or audit the manuscript claims. Full engineering history, superseded prompt drafts, infrastructure failures and abandoned exploratory strategies remain in repository provenance but are not treated as scientific evidence.

V3 and V4 are intentionally not pooled. V3 establishes outcome-blind candidate-region recoverability and the importance of deterministic policy. V4 asks the narrower and more causal question: under the same evidence contract, what happens when experiment-level rule content or rule order is manipulated while the model and candidate inventory are held fixed?
