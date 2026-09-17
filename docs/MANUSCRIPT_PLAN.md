# Manuscript plan

## Working title

**State-Conditioned Rheological Design and Evidence-Grounded Scientific Agent Guidance for Reactive Polyurethane Hot-Melt Adhesives**

The title should foreground the physical/statistical result while making the Agent contribution visible as a scientific decision layer rather than a generic chatbot.

## Central paper logic

The paper should follow the research team's confirmed chronology:

```text
1. Original local experiments reveal that reactive-PUR rheology depends on chemistry and experimental/process realization.
2. State-shift modeling shows that repeated realizations mainly change viscosity scale while preserving a comparatively transferable local thermal-response shape.
3. One state anchor calibrates an unseen realization far better than formulation identity alone.
4. Temperature response and thermal-hold stability emerge as distinct, differently tunable rheological coordinates.
5. These physical/model findings establish the state-aware design theory.
6. External evidence defines a scientifically constrained resin-modification hypothesis.
7. An evidence-grounded Agent reasons over the available pre-result information and selects a validation formulation.
8. The Agent-selected candidate and rationale are frozen before the corresponding wet-lab outcome is known to the Agent.
9. The human experimental team executes the recommended formulation.
10. The resulting thermal-hold measurement independently supports, rejects, or qualifies the recommendation.
11. The present-day Agent architecture is reconstructed as a leakage-safe scientific decision system and benchmarked against deterministic, direct-LLM, single-pass and ablated alternatives.
12. Physical adjudication and architecture benchmarking together define the next design state.
```

The main methodological statement is:

> **The physical/model findings first establish a state-aware design theory; an evidence-grounded Agent then makes a blinded, falsifiable formulation recommendation within that theory; human wet-lab execution provides independent physical adjudication; and a leakage-safe architecture benchmark tests whether the advanced scientific Agent contributes beyond a generic LLM or encoded literature prior.**

The paper should remain scientifically useful even if a reader ignores the LLM implementation. The first contribution is the **structure of reactive-PUR rheological variability**; the second is an **evidence-grounded decision layer tested against a subsequent physical experiment and rigorous architecture baselines**.

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

This remains the primary modeling result.

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

The key bridge to the Agent is causal and data-driven: state is retained because the measurements show that composition-only representation discards predictive information.

### 6. Evidence-grounded formulation hypothesis

Explain why resin modification is scientifically admissible before discussing the Agent-selected validation formulation.

Use independent evidence for:

```text
acrylic-like region: approximately 15-25%
minor tackifier-like region: approximately 0-10%
```

and for modifier functionality/effective reactive-group density as a plausible stability variable.

The current 12-cell V2 software grid is a **later formalized reproducible abstraction** of this evidence-constrained region. It is useful for benchmark replay and future design rounds, but should not be presented as the contemporaneous freeze artifact unless an older record establishes that.

### 7. Pre-result Agent recommendation and current validation formulation

This section establishes the actual experimental chronology before introducing the newer V3 software architecture.

The Agent reasoned over the available pre-result physical/model evidence, uncertainty and formulation evidence. The target wet-lab result was unavailable to it at recommendation time.

The internal `F1` formulation is the **Agent-selected validation formulation**:

```text
PPG2000 = 39.60
PDP-70  = 39.60
AC1920  = 17
TK100   = 5
MDI     = 20.19
```

The manuscript should preserve whatever original recommendation rationale/criterion can be recovered. The current repository does not contain the contemporaneous historical freeze artifact, so author-confirmed chronology and repository timestamp evidence must not be conflated.

Do not claim that today's V3 code was necessarily the exact historical runtime that selected F1.

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

### 9. Scientific Decision Agent V3

The current implementation should be presented as a rigorous formalization and improvement of the Agent decision layer, not merely as a larger prompt.

Architecture:

```text
structural evidence firewall
-> Planner
-> planner-selected read-only scientific Actions
-> deterministic candidate scorecards
-> weight-free Pareto + robustness scenarios
-> Proposer
-> Skeptic / falsification audit
-> Judge
-> frozen recommendation / robustness probe / uncertainty probe / abstention
```

#### 9.1 Structural evidence firewall

For blind replay, remove target identity, follow-up measurements, follow-up descriptors and controller labels before any LLM payload is built.

An audit found that the older runner passed the full `evidence_state.json` alongside a correctly filtered Action context. Because the raw evidence state contains follow-up rows, old blind results may contain leakage. This is now fixed structurally in both the single-pass baselines and V3.

The paper should report this correction transparently. Old benchmark runs should not be primary evidence unless their exact payload is independently shown to be leakage-free.

#### 9.2 State-aware scientific Action

V3 can actively request:

```text
get_state_aware_rheology_summary()
```

This deterministic Action recomputes, from original pre-validation CSVs only:

- realization spread;
- anchor-normalized curve collapse;
- apparent `E_eta` descriptors;
- original E1/E5 hold-failure evidence;
- state-aware claim boundaries.

This is important because the Agent should reason from the paper's physical discovery rather than only from literature priors.

#### 9.3 Planner and scientific tool selection

The Planner defines the failure mode, assumptions, evidence needs, abstention triggers and counterfactual tests before candidate selection.

#### 9.4 Deterministic robustness layer

For every candidate compute transparent scorecards and a weight-free Pareto front. Compare rankings under:

```text
evidence_first
robustness_first
hypothesis_test_first
```

These are robustness diagnostics, not a surrogate property predictor.

#### 9.5 Proposer-Skeptic-Judge loop

The Proposer ranks candidates; the Skeptic tries to falsify the provisional recommendation and audits leakage/scientific boundaries; the Judge resolves the conflict and may abstain or select an uncertainty probe.

Only concise audit records are stored; hidden chain-of-thought is neither required nor part of the scientific evidence.

See `docs/AGENT_V3_ARCHITECTURE.md`.

### 10. Architecture benchmark: does the Agent add value beyond priors and a generic LLM?

This should become the main computational Agent result.

Use identical model/candidate/evidence conditions wherever applicable and compare:

```text
B0 deterministic evidence ranker
B1 direct LLM blind
B2 single-pass tool-context model
A1 V3 without Skeptic
A2 V3 without deterministic robustness
A3 V3 without state-aware rheology Action
A4 full V3
```

`B2` should receive the same precomputed state-aware/action evidence available to V3. Therefore V3 cannot receive credit simply for seeing more data.

Controller-side metrics:

```text
held-out-near candidate rank
Top-1 regional recovery
Top-3 regional recovery
L1 distance in (acrylic-like %, tackifier-like %) plane
selection entropy across repeated runs
abstention rate
scientific-boundary violation rate
structural leakage rate
tool/evidence trace completeness
tool call count and success fraction
```

For V3 also report:

```text
whether Skeptic changed/qualified the provisional decision
Skeptic leakage failures
Skeptic scientific-boundary failures
agreement across deterministic robustness scenarios
```

Use 3-5 stochastic repetitions as pilot only. Prefer at least 30 independent runs per stochastic model condition for the paper benchmark unless a different sample size is explicitly justified.

Do not claim Agent-architecture superiority until the repeated results show it.

A strong result would be:

> Under the same leakage-safe pre-result evidence and candidate constraints, full V3 converged more consistently on the physically compatible formulation region while reducing boundary violations or fragile decisions relative to direct, deterministic, single-pass and ablated alternatives.

If V3 does not outperform a deterministic/literature baseline, the paper must instead say that the evidence prior explains most of the recovery and restrict the Agent claim to traceability/uncertainty integration.

### 11. Stability-aware design update

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

Do not present numerical weights as calibrated until they are frozen and used prospectively.

---

## Figure plan

### Figure 1 — Scientific chronology and Agent architecture

Panel A:

```text
Physical + model findings
-> State-aware design theory
-> Pre-result Agent recommendation
-> Human experiment
-> Physical adjudication
```

Panel B:

```text
Evidence firewall
-> Planner
-> Actions
-> deterministic robustness
-> Proposer
-> Skeptic
-> Judge
```

### Figure 2 — State-shift master curve and one-point calibration

```text
A raw 80-130 C curves
B curves normalized by eta(120 C)
C shared-shape bootstrap band and/or apparent E_eta by realization
D strict unseen-realization error: formulation-only vs one-point calibrated
```

### Figure 3 — Thermal-hold stability and Agent physical validation

Plot E1, E5 and both Agent-selected validation-formulation repeats at 120 C. Show matched 15-60 min SI and make the temporal boundary explicit: the recommendation precedes these validation measurements.

### Figure 4 — Evidence-to-candidate-space formalization

Show the E2 core plus external acrylic/tackifier evidence anchors and the later V2 4x3 abstraction. Label it as reproducible candidate-space formalization rather than the historical freeze artifact.

### Figure 5 — Agent architecture benchmark and ablations

Recommended panels:

```text
A Top-1 / Top-3 region recovery by condition
B modifier-plane distance by condition
C selection entropy / selection distribution
D boundary violations, abstention and leakage checks
```

Optionally add a small flow inset showing how removing the Skeptic, deterministic robustness layer, or state-aware Action changes the V3 graph.

This figure should provide the evidence that the Agent architecture adds value beyond a literature prior or a generic LLM.

---

## Claim hierarchy

### Strong physical/model claims

- nominal formulation alone does not determine observed viscosity level across repeated realizations;
- within the measured local chemistry family, much of the realization effect behaves approximately as a viscosity-scale shift;
- one realization anchor predicts the remaining held-out local temperature curve much more accurately than formulation identity alone;
- thermal-hold stability differs strongly across tested formulations.

### Agent physical-validation claim

- the research team confirms that the Agent selected the validation formulation before the corresponding wet-lab result was known to the Agent;
- human execution subsequently produced two low-drift hold trajectories;
- those measurements support the recommendation with respect to thermal-hold stability.

### Agent architecture claim — pending benchmark

- V3 structurally prevents target-result leakage before LLM calls;
- it separates planning, scientific tools, deterministic robustness, proposal, falsification and final adjudication;
- whether this architecture outperforms strong baselines is an empirical question to be established by the repeated benchmark.

### Provenance boundary

- the current repository does not contain the original contemporaneous historical freeze artifact;
- today's chronology documentation is not a substitute for the original timestamp;
- the exact current V2 4x3 grid and V3 architecture are later formalizations unless older evidence establishes otherwise.

### Claims that remain too strong

- the local master curve is universal across reactive PUR chemistry;
- temperature sensitivity and stability are universally statistically independent;
- one molecular pathway alone explains viscosity build-up;
- any literature modifier percentage is a universal optimum;
- full V3 is superior before the benchmark demonstrates that result.

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

For the software architecture, separately preserve:

```text
same blind evidence
-> baseline / ablation / full V3
-> controller-side comparison only after outputs are frozen
```

Never write the experimental outcome as an input used to select the formulation that it later validates.
