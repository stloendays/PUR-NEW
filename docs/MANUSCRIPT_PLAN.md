# Manuscript plan

## Working title

**State-Conditioned Rheological Design and Evidence-Grounded Scientific Agent Guidance for Reactive Polyurethane Hot-Melt Adhesives**

The title should foreground the physical/statistical result while keeping the Agent visible as a scientific decision layer.

## Central paper logic

The manuscript should preserve the confirmed research chronology:

```text
1. Original E1-E5 experiments reveal chemistry- and realization-dependent rheology.
2. State-shift modeling identifies a comparatively transferable local thermal-response shape.
3. One realization-specific anchor strongly improves unseen-realization reconstruction.
4. Temperature response and thermal-hold stability emerge as distinct, differently tunable coordinates.
5. These findings establish the state-aware design theory.
6. Independent external evidence identifies a plausible resin-modification direction.
7. An Agent uses the pre-result physical/model evidence and formulation evidence to select a validation formulation.
8. The target wet-lab outcome is unavailable to the Agent at selection time.
9. Humans execute the selected formulation.
10. The later 120 C hold experiment physically adjudicates the recommendation.
11. The present-day V3 Agent formalizes and strengthens that decision process.
12. A simple unguided LLM baseline is compared with the full strategy; stronger matched-information controls are secondary robustness checks.
```

The main methodological statement is:

> **Physical/model findings first establish a state-aware rheological design theory. An evidence-grounded Agent then converts those findings into a blinded formulation decision, and a subsequent human-executed wet-lab experiment physically adjudicates the recommendation.**

The formulation stored internally as `F1` should be called the **Agent-selected validation formulation** in manuscript prose.

---

## Suggested Results and Discussion order

### 1. Local formulation design and raw temperature-dependent rheology

Introduce E1-E5 and the two local axes:

- E1/E2/E3: NCO:OH = 1.70/1.80/1.90 at fixed 50/50 PPG2000/PDP-70;
- E4/E2/E5: PPG2000/PDP-70 composition perturbation around 50/50 at NCO:OH = 1.80.

Show the 80-130 C sweeps. Emphasize that nominal formulation does not uniquely determine measured viscosity level. E2 realizations differ by several-fold at matched temperature.

GJJ/ZYX/CHH are within-operator realization labels from the same operator, not separate operators.

### 2. State-shift master curve and one-point calibration

This is the main modeling result.

#### 2.1 Model-light collapse

Normalize each complete curve by its own 120 C viscosity:

```text
relative_eta(T) = eta(T) / eta(120 C)
```

Across seven realizations, non-anchor normalized-curve CV is only about 3.4-10.3% despite much larger absolute-viscosity spread.

#### 2.2 Positive state model

Use:

```text
ln eta_r(T) = alpha_r + g(T) + epsilon
```

where `alpha_r` is realization/state specific and `g(T)` is shared within the measured local chemistry family.

The preferred low-complexity implementation is quadratic in inverse temperature.

#### 2.3 Formulation-only versus state-aware comparison

Report:

```text
formulation-only R2 ~= 0.895
state-shift shared-shape R2 ~= 0.998
held-temperature formulation-only multiplicative error ~= 1.406x
held-temperature state-aware error                  ~= 1.055x
```

Mixed-effects analysis remains supporting evidence only:

```text
random-intercept SD ~= 0.325 log-unit
point residual SD   ~= 0.047 log-unit
ICC                 ~= 0.979
```

#### 2.4 Strict unseen-realization calibration

For eligible E1/E2 realizations:

```text
formulation-only error: ~1.599-1.611x
one-point calibrated:   ~1.065-1.098x
```

Use:

> Within a nominal formulation already represented in the local chemistry family, one state-specific viscosity anchor is sufficient to calibrate the remaining measured temperature curve to roughly 6-10% multiplicative error.

### 3. Temperature response and thermal-hold stability as distinct coordinates

Local apparent thermal-response descriptor:

```text
mean apparent E_eta = 41.87 kJ/mol
SD                  = 2.27 kJ/mol
CV                  = 5.4%
median curve R2     = 0.9948
```

`E_eta` is a rheological temperature-sensitivity descriptor, not a molecular reaction activation energy.

Thermal-hold response at 120 C:

```text
E1 fitted dln(eta)/dt ~= 0.125 h^-1
E5 fitted dln(eta)/dt ~= 0.537 h^-1
ratio                 ~= 4.29x
```

Use:

> **temperature response and thermal-hold stability are distinct, differently tunable rheological coordinates in the current design.**

Do not use `independent` or `orthogonal`.

### 4. External database defines the generalization boundary

The external database contains 39 dense prepolymer curves and 4559 temperature-viscosity points.

```text
median ln(eta)-1/T R2 = 0.9967
37 / 39 curves have R2 >= 0.98
apparent E_eta range ~= 34.7-94.2 kJ/mol
```

Cross-validated composition-model strength:

```text
thermal descriptor LOOCV R2 ~= 0.59-0.62
fitted 75 C log-viscosity LOOCV R2 ~= 0.80-0.82
```

Interpretation:

```text
chemistry controls the broad rheological landscape
+
process / experimental state controls where a local realization sits within that landscape
```

### 5. State-aware design theory

Define the design object as:

```text
formulation state
+ process / realization state
+ thermal-response descriptor
+ hold-stability descriptor
+ repeatability
+ missingness / evidence coverage
```

This is the bridge to the Agent. State is retained because the experiments show that composition-only representation discards predictive information.

### 6. Evidence-grounded formulation hypothesis

Explain why a resin-modified family is scientifically admissible.

Independent evidence supports a coarse region:

```text
acrylic-like modifier: approximately 15-25%
minor tackifier-like modifier: approximately 0-10%
```

Modifier functionality/effective reactive-group density is treated as a plausible stability variable, not as a proven AC1920/TK100 mechanism.

The current 4x3 V2 software grid is a later reproducible formalization of this chemistry region. It is useful for replay benchmarking and future design, but it is not presented as the original historical freeze artifact unless earlier provenance is recovered.

### 7. Pre-result Agent recommendation

The Agent is positioned after the physical/model findings and before the validation experiment.

The Agent-selected validation formulation is:

```text
PPG2000 = 39.60
PDP-70  = 39.60
AC1920  = 17
TK100   = 5
MDI     = 20.19
```

The target wet-lab result was unavailable to the Agent when this formulation was selected, according to the research team's confirmed chronology.

The current repository does not contain the contemporaneous historical freeze artifact, so author-confirmed chronology must not be presented as a Git timestamp claim.

### 8. Human-executed physical adjudication

Two 120 C hold repeats for the Agent-selected validation formulation give:

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

Therefore:

> **The subsequent wet-lab measurements support the pre-result Agent recommendation with respect to thermal-hold stability over the matched 15-60 min window.**

Do not promote this to proof of one molecular pathway.

### 9. Discovery-to-Experiment Agent V3

The present-day Agent formalizes and strengthens the decision layer.

Architecture:

```text
structural evidence firewall
-> Planner
-> state-aware / local scientific Actions
-> external evidence Actions
-> scientific translation to design rules
-> deterministic candidate diagnostics
-> Proposer
-> Skeptic
-> Judge
-> frozen recommendation / probe / abstention
```

The core scientific Action is:

```text
get_state_aware_rheology_summary()
```

which gives the Agent explicit access to the upstream physical/model findings without exposing the later validation outcome.

The Agent should be described as using the discovered material regularities to choose an informative experiment, not as simply matching a literature recipe.

See `docs/AGENT_V3_ARCHITECTURE.md`.

### 10. Headline Agent benchmark: simple baseline versus complete strategy

This section should test the practical value of the whole PUR-NEW strategy.

#### 10.1 Primary baseline — naive direct LLM

The headline baseline receives only:

```text
raw original E1-E5 measurements
+ original local formulation information
+ candidate compositions
+ the experimental task
```

It does **not** receive:

```text
state-aware theory summary
external literature/database evidence
scientific Actions
candidate-space rationale
candidate support scores
Planner
Skeptic
robustness diagnostics
```

This baseline represents the natural question:

> What if the same model is simply given the local data and asked to choose a candidate?

The baseline remains fully blinded to the validation formulation identity and validation outcome.

#### 10.2 Full Agent

The full Agent receives the complete proposed strategy:

```text
state-aware physical/model findings
+ scientific Actions
+ external evidence
+ process-state uncertainty
+ scientific planning
+ candidate diagnostics
+ scientific quality control
```

The main-text comparison is therefore:

```text
naive direct LLM
versus
full PUR-NEW Agent
```

This comparison measures the value of the **complete strategy stack**, not pure architecture at a matched information budget.

#### 10.3 Main metrics

Report repeated-run behavior using:

```text
held-out-near candidate rank
Top-1 regional recovery
Top-3 regional recovery
L1 distance in the acrylic/tackifier plane
selection distribution
selection entropy
abstention rate
failure rate
scientific-boundary violations
structural leakage checks
```

Use 3-5 calls for pilot only. Prefer >=30 stochastic calls per LLM condition for the manuscript benchmark.

A defensible result, if observed, is:

> The unguided direct-LLM baseline showed weaker and less stable recovery of the validation region, whereas the complete state-aware and evidence-grounded Agent strategy converged more consistently on a physically compatible experimental recommendation.

#### 10.4 Supplementary strong controls

Do not make the strongest controls the headline baseline. Keep them as reviewer-facing robustness tests:

```text
single-pass tool-context LLM
deterministic evidence ranker
selected V3 module ablations
```

These answer narrower questions such as whether the full Agent is merely following encoded literature priors or whether a one-shot tool-enriched LLM already captures most of the benefit.

The most scientifically important ablation is removal of the state-aware rheology Action, because it directly tests whether the paper's physical discovery contributes to experiment selection.

See `docs/AGENT_BASELINE_PROTOCOL.md`.

### 11. Stability-aware design update

Future objective functions should separate absolute performance, thermal response, temporal stability and repeatability:

```text
J_perf = w_eta L_viscosity
       + w_T L_temperature_response
       + w_S L_hold_stability
       + w_R L_repeatability
       + feasibility penalties
```

and a separate uncertainty/information term may be used for future design rounds.

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
-> scientific translation
-> candidate diagnostics
-> Proposer
-> Skeptic
-> Judge
```

### Figure 2 — State-shift master curve and one-point calibration

```text
A raw 80-130 C curves
B eta(T)/eta(120 C) collapse
C shared-shape bootstrap band and/or apparent E_eta
D formulation-only versus one-point calibrated held-out error
```

### Figure 3 — Thermal-hold stability and Agent physical validation

Plot E1, E5 and both validation-formulation repeats at 120 C. Show matched 15-60 min SI and mark the temporal boundary between recommendation and later measurement.

### Figure 4 — Evidence-to-candidate-region map

Show the E2 core plus external acrylic/tackifier evidence anchors and the later 4x3 V2 formalization.

### Figure 5 — Agent strategy benchmark

Main panels should emphasize:

```text
A naive direct LLM versus full Agent Top-1/Top-3 recovery
B modifier-plane distance / selection distribution
C selection entropy and failure/abstention behavior
D optional strategy ablation, especially removal of state-aware Action
```

Evidence-rich single-pass and deterministic controls can be placed in a supplementary panel/table if the main figure becomes crowded.

---

## Claim hierarchy

### Strong physical/model claims

- nominal formulation alone does not determine observed viscosity level across repeated realizations;
- within the measured local chemistry family, much of the realization effect behaves approximately as a viscosity-scale shift;
- one realization anchor reconstructs held-out local temperature curves much better than formulation identity alone;
- thermal-hold stability differs strongly across tested formulations.

### Agent physical-validation claim

- the research team confirms that the Agent selected the validation formulation before the corresponding wet-lab outcome was known to the Agent;
- human execution subsequently produced two low-drift hold trajectories;
- those measurements support the recommendation with respect to thermal-hold stability.

### Agent strategy claim — pending benchmark

If repeated runs support it:

- the complete state-aware/evidence-grounded Agent strategy outperforms an unguided direct-LLM formulation selector on recovery and stability of the validation region;
- removal of selected strategy components may identify which parts contribute most strongly;
- stronger matched-information controls are supplementary evidence, not the headline comparison.

### Provenance boundary

- the current repository does not contain the original contemporaneous historical freeze artifact;
- today's V2 grid and V3 software are later formalizations unless older provenance establishes otherwise;
- current benchmark results must not be backdated into the historical recommendation event.

### Claims that remain too strong

- the local master curve is universal across reactive PUR chemistry;
- temperature sensitivity and stability are universally statistically independent;
- one molecular pathway alone explains viscosity build-up;
- any literature modifier percentage is a universal optimum;
- full V3 is superior before the repeated benchmark demonstrates it.

## Writing rule

Always preserve:

```text
physical/model finding
-> design theory
-> blinded Agent recommendation
-> freeze
-> human experiment
-> adjudication
```

For current software benchmarking, preserve:

```text
blind pre-result inputs
-> naive baseline OR full Agent
-> freeze outputs
-> controller-side comparison
```

Never use the experimental outcome as an input to the recommendation it later appears to validate.
