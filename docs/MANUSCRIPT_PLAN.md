# Manuscript plan

## Working title

**State-Conditioned Rheological Design and Uncertainty-Aware Agent Guidance for Reactive Polyurethane Hot-Melt Adhesives**

The title should foreground the physical/statistical result before the Agent contribution.

## Central paper logic

The paper must follow the real scientific chronology rather than presenting the Agent as the origin of the physical insight.

```text
1. Local experiments reveal that reactive-PUR rheology depends on chemistry and experimental/process realization.
2. State-shift modeling shows that repeated realizations mainly change viscosity scale while preserving a comparatively transferable local thermal-response shape.
3. One state anchor calibrates an unseen realization far better than formulation identity alone.
4. Thermal response and thermal-hold stability emerge as distinct, differently tunable rheological coordinates.
5. These physical/model findings establish the state-aware design theory.
6. External evidence and the original E2 reactive core define an admissible resin-modification candidate space.
7. The Agent receives only pre-result evidence, reasons within this state-aware design theory, and selects a new candidate.
8. The candidate, rationale, uncertainty assessment and falsifiable criterion are frozen before the corresponding wet-lab outcome is available to the Agent.
9. The human experimental team executes the recommended formulation.
10. The later experiment independently supports, partially supports, rejects, or qualifies the frozen recommendation.
11. The physical adjudication updates the next design state.
```

The main methodological statement is therefore:

> **The physical/model findings first establish a state-aware design theory; the Agent then makes a blinded, falsifiable recommendation within that theory; human wet-lab execution provides an independent physical adjudication of the pre-frozen recommendation.**

The paper should remain scientifically useful even if a reader ignores the LLM implementation. The first contribution is the **structure of reactive-PUR rheological variability**; the second is an **evidence-grounded decision layer tested prospectively against physical experiment**.

See `docs/PROSPECTIVE_VALIDATION_PROTOCOL.md`.

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

This provides direct visual evidence that realization predominantly changes viscosity scale while preserving a transferable local temperature-response shape.

#### 2.2 Positive state model

Use:

```text
ln eta_r(T) = alpha_r + g(T) + epsilon
```

where `alpha_r` is realization/state specific and `g(T)` is shared within the measured local chemistry family.

The preferred implementation is a low-complexity quadratic function in inverse temperature. The conclusion is robust to using a quadratic function in ordinary temperature; a cubic inverse-temperature term gives negligible cross-validation improvement and worse BIC.

#### 2.3 Formulation-only versus state-aware comparison

Report:

```text
formulation-only R2 ~= 0.895
state-shift shared-shape R2 ~= 0.998
```

and held-temperature validation:

```text
formulation-only multiplicative error ~= 1.406x
state-shift quadratic error          ~= 1.055x
```

Mixed-effects analysis is supporting evidence only:

```text
random-intercept SD ~= 0.325 log-unit
point residual SD   ~= 0.047 log-unit
ICC                 ~= 0.979
```

With only seven realization groups, mixed-effects should not be the headline inferential result.

#### 2.4 Strict unseen-realization one-point calibration

Remove one complete realization from training. For E1/E2 cases where the nominal formulation remains represented, compare:

```text
formulation identity + shared quadratic thermal response
versus
shared state master curve + one anchor from the held realization
```

Across anchor temperatures from 80 to 130 C:

```text
formulation-only error: ~1.599-1.611x
one-point calibrated:   ~1.065-1.098x
```

At the operationally relevant 120 C anchor, all six eligible held-out E1/E2 realizations improve relative to formulation-only prediction.

Use the manuscript-facing statement:

> Within a nominal formulation already represented in the local chemistry family, a new realization cannot be located accurately from formulation identity alone, but one state-specific viscosity anchor is sufficient to calibrate the remaining measured temperature curve to roughly 6-10% multiplicative error.

### 3. Temperature response and thermal-hold stability are distinct, differently tunable coordinates

Local temperature sensitivity:

```text
mean apparent E_eta = 41.87 kJ/mol
SD                  = 2.27 kJ/mol
CV                  = 5.4%
median curve R2      = 0.9948
```

`E_eta` is an apparent rheological temperature-sensitivity descriptor, not a molecular reaction activation energy.

Thermal-hold response at 120 C:

```text
E1 fitted dln(eta)/dt ~= 0.125 h^-1
E5 fitted dln(eta)/dt ~= 0.537 h^-1
ratio                 ~= 4.29x
```

Matched 15-60 min drift:

```text
E1      +9.51%
E5     +51.54%
F1 mean +1.47%
```

Use:

> **distinct, differently tunable rheological coordinates**

Do not use `independent` or `orthogonal` because matched temperature-and-hold characterization is still incomplete across formulations.

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

The external thermal-curve dataset and viscosity-rise-rate records are not sample-matched, so they must not be used to claim universal statistical independence between thermal sensitivity and stability.

### 5. State-aware design theory and uncertainty representation

Only after the physical/statistical results are established, introduce the design object:

```text
formulation state
+ process / realization state
+ measured support
+ thermal-response descriptor
+ hold-stability descriptor
+ repeatability
+ missingness
```

Uncertainty is separated into:

```text
measurement
repeatability
process history
extrapolation
evidence coverage
```

This is the key bridge to the Agent: state is retained because the experimental/model results show that composition-only representation discards predictive information.

### 6. Evidence-derived candidate-space hypothesis

The candidate space answers:

> Why should these formulation families be considered at all?

Use `docs/CANDIDATE_SPACE_HYPOTHESIS.md` as the source of truth.

The E2 reactive core is the local anchor:

```text
PPG2000 39.9047%
PDP-70  39.9047%
MDI     20.1907%
```

Independent evidence defines:

```text
acrylic-like axis         = {0, 15, 20, 25}%
minor tackifier-like axis = {0, 5, 10}%
```

The resulting V2 candidate set is the 12-point Cartesian product, with the E2 reactive core scaled into the remaining formulation fraction.

This section explains the **admissible chemistry search space**. It does not determine which candidate the Agent must choose.

### 7. Blinded Agent recommendation and freeze

This is the decisive chronology for the Agent claim.

The Agent is a decision layer above the already established state-aware theory. It may use:

```text
original local evidence
+ state-aware rheology descriptors
+ structured uncertainty
+ candidate-space hypothesis
+ deterministic Actions
+ external database/literature evidence
+ finite candidate set
```

For the prospective validation round, it must **not** see:

```text
the corresponding future wet-lab result
post-result interpretation
outcome-derived adjudication labels
```

The Agent may choose:

```text
performance candidate
robustness probe
uncertainty probe
abstain
```

Before wet-lab adjudication, freeze an immutable recommendation record containing:

- selected formulation-process state;
- alternatives considered;
- evidence and Action trace;
- uncertainty and missing variables;
- rationale;
- process variables to control / perturb;
- falsifiable acceptance or rejection criterion;
- timestamp and provenance.

The candidate must not be changed after the outcome becomes known.

### 8. Human-executed prospective wet-lab adjudication

After freeze, the human experimental team prepares and measures the candidate.

The experiment is not an additional pre-selection input to the Agent. It is an **external physical adjudicator** of the frozen decision.

The result should be classified against the pre-frozen criterion as:

```text
supported
partially supported
not supported
or inconclusive because of execution / measurement uncertainty
```

A negative experiment remains informative because it falsifies or weakens the recommendation and updates the next design state.

### 9. Historical F1 result and retrospective V2 replay

Keep the historical F1 result as useful physical evidence:

```text
15-60 min repeat 1: -0.16%
15-60 min repeat 2: +3.04%
mean profile:        +1.47%
```

However, distinguish it from the prospective new-candidate validation.

The formal V2 candidate-space documentation was written after the historical F1 result was already known. Therefore an F1 benchmark that hides its result from the evaluated model is a **retrospective held-out-result blind replay**, not the prospective validation claim.

Use the replay for robustness / benchmarking, while the main Agent-validation chronology is:

```text
state-aware theory
-> blinded recommendation
-> freeze
-> human experiment
-> independent adjudication
```

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

Numerical weights should not be presented as calibrated until frozen and used prospectively.

---

## Figure plan

### Figure 1 — Scientific chronology and runtime architecture

```text
Physical + model findings
-> State-aware design theory
-> Evidence-constrained candidate space
-> Blinded Agent recommendation
-> FROZEN candidate + criterion
-> Human wet-lab execution
-> Independent physical adjudication
-> State / model update
```

The figure must visually prevent an arrow from the target experimental result back into the pre-freeze recommendation stage.

### Figure 2 — State-shift master curve and one-point calibration

```text
A raw 80-130 C curves
B curves normalized by eta(120 C)
C shared-shape bootstrap band and/or apparent E_eta by realization
D strict unseen-realization error: formulation-only vs one-point calibrated
```

This should be the strongest quantitative figure in the paper.

### Figure 3 — Thermal-hold stability as a second rheological coordinate

Plot E1, E5 and historical F1 repeats at 120 C. Show matched-window SI and fitted log-drift rates where appropriate.

### Figure 4 — Evidence-to-candidate-space map

```text
local E2 core
+
15 / 20 / 25% acrylic evidence anchors
+
5 / 10% minor tackifier evidence anchors
-> 4 x 3 finite hypothesis grid
```

### Figure 5 — Frozen Agent recommendation and prospective physical adjudication

Show:

```text
pre-result Agent inputs
-> selected candidate + alternatives
-> frozen rationale / uncertainty / criterion
|| temporal boundary ||
human experiment
-> observed result
-> support / reject / qualify
```

Historical F1/V2 replay can be placed in a supplementary benchmark figure if needed.

---

## Claim hierarchy

### Strong physical/model claims

- nominal formulation alone does not determine observed viscosity level across repeated realizations;
- within the measured local chemistry family, much of the realization effect behaves approximately as a viscosity-scale shift;
- a shared local temperature-response shape plus one realization anchor predicts held-out realization curves much more accurately than formulation identity alone;
- thermal-hold stability differs strongly across tested formulations;
- the historical F1 follow-up enters a substantially lower-drift regime over the matched 15-60 min interval.

### Strong methodological claim for the prospective round

- the physical/model findings establish the state-aware design theory first;
- the Agent makes a recommendation without access to the corresponding wet-lab outcome;
- the recommendation and criterion are frozen before adjudication;
- humans execute the experiment;
- the later physical result independently supports, rejects, or qualifies the frozen recommendation.

### Strong external-database context

- dense external PUR/prepolymer temperature curves are individually regular in `ln(eta)` versus `1/T`;
- thermal-sensitivity scale varies substantially across chemistry families;
- composition explains a meaningful but incomplete fraction of between-curve rheological variation.

### Claims that remain too strong

- the local master curve is universal across reactive PUR chemistry;
- temperature sensitivity and stability are universally statistically independent;
- one molecular pathway alone explains viscosity build-up;
- any literature modifier percentage is a universal optimum;
- the historical F1/V2 replay was itself prospectively preregistered.

## Writing rule

The manuscript should always preserve this direction of causality:

```text
physical/model finding
-> design theory
-> blinded recommendation
-> freeze
-> experiment
-> adjudication
```

Never write the story as if the experimental outcome was used to choose the candidate that it later appears to validate.
