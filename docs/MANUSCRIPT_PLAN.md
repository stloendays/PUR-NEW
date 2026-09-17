# Manuscript plan

## Working title

**State-Conditioned Rheological Design and Uncertainty-Aware Agent Guidance for Reactive Polyurethane Hot-Melt Adhesives**

The title should foreground the physical/statistical result before the Agent contribution.

## Central paper logic

The paper should follow the research team's confirmed chronology:

```text
1. Original local experiments reveal that reactive-PUR rheology depends on chemistry and experimental/process realization.
2. State-shift modeling shows that repeated realizations mainly change viscosity scale while preserving a comparatively transferable local thermal-response shape.
3. One state anchor calibrates an unseen realization far better than formulation identity alone.
4. Temperature response and thermal-hold stability emerge as distinct, differently tunable rheological coordinates.
5. These physical/model findings establish the state-aware design theory.
6. External evidence defines a scientifically constrained resin-modification hypothesis.
7. The Agent reasons over the available pre-result evidence and selects a validation formulation.
8. The Agent-selected candidate and rationale are frozen before the corresponding wet-lab outcome is known to the Agent.
9. The human experimental team executes the recommended formulation.
10. The resulting thermal-hold measurement independently supports, rejects, or qualifies the recommendation.
11. The physical adjudication updates the next design state.
```

The main methodological statement is:

> **The physical/model findings first establish a state-aware design theory; the Agent then makes a blinded, falsifiable formulation recommendation within that theory; human wet-lab execution provides an independent physical adjudication of the pre-result recommendation.**

The paper should remain scientifically useful even if a reader ignores the LLM implementation. The first contribution is the **structure of reactive-PUR rheological variability**; the second is an **evidence-grounded decision layer tested against a subsequent physical experiment**.

The formulation stored internally as `F1` should be called the **Agent-selected validation formulation** in manuscript prose.

---

## Suggested Results and Discussion order

### 1. Local formulation design and raw temperature-dependent rheology

Introduce E1-E5 and the two local axes:

- NCO:OH at fixed 50/50 PPG2000/PDP-70;
- PPG2000/PDP-70 ratio at fixed NCO:OH = 1.80.

Show the 80-130 C sweeps. Emphasize that nominal formulation does not uniquely determine measured viscosity level. E2 realizations differ by roughly 2.8-3.6x at matched temperatures.

GJJ/ZYX/CHH are within-operator realization labels from the same operator, not operator categories.

### 2. State-shift master curve and one-point calibration

This is the primary modeling result.

#### 2.1 Model-light curve collapse

Normalize every recorded curve by its own 120 C viscosity:

```text
relative_eta(T) = eta(T) / eta(120 C)
```

Across the seven realizations, the non-anchor normalized-curve CV is only about 3.4-10.3% despite much larger absolute-viscosity spread.

#### 2.2 Positive state model

Use:

```text
ln eta_r(T) = alpha_r + g(T) + epsilon
```

where `alpha_r` is realization/state specific and `g(T)` is shared within the measured local chemistry family.

The preferred implementation is a low-complexity quadratic function in inverse temperature. The conclusion is robust to a quadratic function in ordinary temperature; a cubic inverse-temperature term gives negligible cross-validation improvement and worse BIC.

#### 2.3 Formulation-only versus state-aware comparison

Report:

```text
formulation-only R2 ~= 0.895
state-shift shared-shape R2 ~= 0.998
held-temperature formulation-only error ~= 1.406x
held-temperature state-aware error      ~= 1.055x
```

Mixed-effects analysis is supporting evidence only:

```text
random-intercept SD ~= 0.325 log-unit
point residual SD   ~= 0.047 log-unit
ICC                 ~= 0.979
```

#### 2.4 Strict unseen-realization one-point calibration

For eligible E1/E2 realizations:

```text
formulation-only error: ~1.599-1.611x
one-point calibrated:   ~1.065-1.098x
```

At the operationally relevant 120 C anchor, all six eligible held-out E1/E2 realizations improve relative to formulation-only prediction.

Use:

> Within a nominal formulation already represented in the local chemistry family, one state-specific viscosity anchor is sufficient to calibrate the remaining measured temperature curve to roughly 6-10% multiplicative error.

### 3. Temperature response and thermal-hold stability as distinct coordinates

Local temperature sensitivity:

```text
mean apparent E_eta = 41.87 kJ/mol
SD                  = 2.27 kJ/mol
CV                  = 5.4%
median curve R2     = 0.9948
```

Thermal-hold response at 120 C:

```text
E1 fitted dln(eta)/dt ~= 0.125 h^-1
E5 fitted dln(eta)/dt ~= 0.537 h^-1
ratio                 ~= 4.29x
```

Use the phrase:

> **distinct, differently tunable rheological coordinates**

Do not use `independent` or `orthogonal` because matched temperature-and-hold characterization is incomplete across formulations.

### 4. External database defines the generalization boundary

The 39 external prepolymer curves contain 4559 temperature-viscosity points.

```text
median ln(eta)-1/T R2 = 0.9967
37 / 39 curves have R2 >= 0.98
apparent E_eta range ~= 34.7-94.2 kJ/mol
```

Prefer cross-validated composition-model strength:

```text
thermal descriptor LOOCV R2 ~= 0.59-0.62
fitted 75 C log-viscosity LOOCV R2 ~= 0.80-0.82
```

The multiscale interpretation is:

```text
chemistry controls the broad rheological landscape
+
process / experimental state controls where a local realization sits within that landscape
```

### 5. State-aware design theory and uncertainty representation

Only after the physical/statistical results are established, introduce the design object:

```text
formulation state
+ process / realization state
+ thermal-response descriptor
+ hold-stability descriptor
+ repeatability
+ missingness
```

Separate uncertainty into measurement, repeatability, process history, extrapolation, and evidence coverage.

### 6. Evidence-grounded formulation hypothesis

Explain why resin modification is scientifically admissible before discussing the Agent-selected validation formulation.

Use independent evidence for:

```text
acrylic-like region: approximately 15-25%
minor tackifier-like region: approximately 0-10%
```

and for modifier functionality/effective reactive-group density as a plausible stability variable.

The current 12-cell V2 software grid is a **later formalized reproducible abstraction** of this evidence-constrained region. It is useful for benchmark replay and future design rounds, but should not be presented as the contemporaneous freeze artifact unless an older record establishes that.

### 7. Blinded Agent recommendation

This is the decisive chronology for the Agent claim.

The Agent reasons over:

```text
state-aware physical/model findings
+ original local evidence
+ structured uncertainty
+ external formulation evidence
+ deterministic scientific Actions
```

The target wet-lab result is unavailable to the Agent at recommendation time.

The internal `F1` formulation is the **Agent-selected validation formulation**:

```text
PPG2000 = 39.60
PDP-70  = 39.60
AC1920  = 17
TK100   = 5
MDI     = 20.19
```

The manuscript should preserve whatever original recommendation rationale/criterion can be recovered. The current repository does not yet contain the contemporaneous freeze artifact, so author-confirmed chronology and repository timestamp evidence must not be conflated.

### 8. Human-executed wet-lab adjudication of the Agent recommendation

After recommendation/freeze, the human experimental team prepared and measured the formulation.

Two 120 C hold repeats give:

```text
15-60 min repeat 1: -0.16%
15-60 min repeat 2: +3.04%
mean profile:        +1.47%
```

Matched original references:

```text
E1: +9.51%
E5: +51.54%
```

Thus the Agent-selected validation formulation enters a substantially lower-drift regime over the matched window.

The manuscript-facing conclusion is:

> **The subsequent wet-lab measurements supported the pre-result Agent recommendation with respect to the thermal-hold stability objective.**

Do not promote this to proof of one molecular kinetic mechanism.

### 9. V2 replay benchmark as secondary reproducibility analysis

The formal V2 grid is:

```text
acrylic-like         = {0, 15, 20, 25}%
minor tackifier-like = {0, 5, 10}%
```

Use the V2 replay to test whether the formalized evidence stack ranks a region compatible with the Agent-selected validation formulation when its composition/outcome is hidden from the evaluated model.

This is a **secondary benchmark/ablation analysis**, not the primary source of the prospective validation claim.

Report deterministic/literature baselines so the Agent is not credited merely for reproducing an obvious external prior.

### 10. Stability-aware design update

The next-generation objective should separate absolute performance, relative temperature response, temporal stability and repeatability:

```text
J_perf = w_eta L_viscosity
       + w_T L_temperature_response
       + w_S L_hold_stability
       + w_R L_repeatability
       + feasibility penalties
```

and the uncertainty/information layer:

```text
A(candidate) = -J_perf - lambda_U U_penalty + beta_IG information_value
```

---

## Figure plan

### Figure 1 — Scientific chronology and runtime architecture

```text
Physical + model findings
-> State-aware design theory
-> Evidence-grounded Agent decision
-> FROZEN Agent-selected validation formulation
-> Human wet-lab execution
-> Independent physical adjudication
-> State / model update
```

### Figure 2 — State-shift master curve and one-point calibration

```text
A raw 80-130 C curves
B curves normalized by eta(120 C)
C shared-shape bootstrap band and/or apparent E_eta by realization
D strict unseen-realization error: formulation-only vs one-point calibrated
```

### Figure 3 — Thermal-hold stability and Agent validation

Plot E1, E5 and both Agent-selected validation-formulation repeats at 120 C. Show the matched 15-60 min SI and make the temporal boundary explicit: the recommendation precedes these validation measurements.

### Figure 4 — Evidence-to-candidate-space formalization

Show the E2 core plus external acrylic/tackifier evidence anchors and the later V2 4x3 abstraction. Label it as reproducible candidate-space formalization rather than the historical freeze artifact.

### Figure 5 — Agent evidence trace and adjudication

Show:

```text
pre-result Agent evidence
-> selected validation formulation
-> frozen rationale / uncertainty / criterion
|| experiment boundary ||
human execution
-> observed low-drift result
-> recommendation supported
```

The V2 replay/ablation can be placed in the same figure or Supplementary Information depending on space.

---

## Claim hierarchy

### Strong physical/model claims

- nominal formulation alone does not determine observed viscosity level across repeated realizations;
- within the measured local chemistry family, much of the realization effect behaves approximately as a viscosity-scale shift;
- one realization anchor predicts the remaining held-out local temperature curve much more accurately than formulation identity alone;
- thermal-hold stability differs strongly across tested formulations.

### Agent-validation claim

- the research team confirms that the Agent selected the validation formulation before the corresponding wet-lab result was known to the Agent;
- human execution subsequently produced two low-drift hold trajectories;
- those measurements support the recommendation with respect to thermal-hold stability.

### Provenance boundary

- the current repository does not yet contain the original contemporaneous freeze artifact;
- today's chronology documentation is not a substitute for the original timestamp;
- the exact current V2 4x3 grid is a later formalization unless older evidence establishes otherwise.

### Claims that remain too strong

- the local master curve is universal across reactive PUR chemistry;
- temperature sensitivity and stability are universally statistically independent;
- one molecular pathway alone explains viscosity build-up;
- any literature modifier percentage is a universal optimum.

## Writing rule

Always preserve this direction of causality:

```text
physical/model finding
-> design theory
-> blinded Agent recommendation
-> freeze
-> human experiment
-> adjudication
```

Never write the experimental outcome as an input used to select the formulation that it later validates.
