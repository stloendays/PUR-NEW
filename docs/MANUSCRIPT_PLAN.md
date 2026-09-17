# Manuscript plan

## Working title

**Uncertainty-Aware Agent-Guided Formulation Design with Wet-Lab Validation for Reactive Polyurethane Hot-Melt Adhesives**

The title can be shortened later once the final journal scope is chosen.

## Central paper logic

The manuscript should follow one continuous argument:

```text
1. Reactive PUR rheology depends on both formulation and process state.
2. Reaction history, thermal hold time and preparation perturbation are known variables and should enter the design loop.
3. Static viscosity targeting alone is therefore incomplete.
4. Deterministic descriptors quantify temperature response, hold drift and repeatability.
5. The Agent reasons over those descriptors plus structured uncertainty.
6. The Agent recommends a formulation-process state and freezes a falsifiable criterion.
7. A human executes the recommended experiment.
8. A separate wet-lab record adjudicates the frozen recommendation.
9. The measured stability information updates the next design state.
```

The Agent is not presented as a robotic chemist. The scientific claim is about **decision quality under uncertainty** and **physical validation of a recommendation**.

## Suggested Results and Discussion order

### 1. Local formulation design and temperature-dependent rheology

Introduce E1-E5 and explain the two local axes:

- NCO:OH at fixed 50/50 PPG2000/PDP-70;
- PPG2000/PDP-70 ratio at fixed NCO:OH = 1.80.

Show the 80-130 °C sweeps and the large E2 run-to-run spread. The purpose is to establish that process realization materially changes the absolute viscosity level.

### 2. Thermal holding exposes the process-stability problem

Show E1 and E5 at 120 °C. Quantify drift using the shared stability index.

Key numbers:

- E1, 15->60 min: +9.51%;
- E5, 15->60 min: +51.54%;
- E1, 15->90 min: +16.85%;
- E5, 15->90 min: +93.08%.

The conclusion is not that hold time was previously unknown. The conclusion is that its **effect size is formulation dependent and large enough to become a design objective**.

### 3. Deterministic state construction and uncertainty decomposition

Before introducing the Agent, show what information is made explicit:

```text
formulation state
+ process state
+ measured support
+ hold / temperature / repeatability descriptors
+ missingness
```

Then separate uncertainty into:

```text
measurement
repeatability
process history
extrapolation
evidence coverage
```

This section is important because it prevents the Agent contribution from becoming an opaque language-model decision.

### 4. Agent-guided recommendation under uncertainty

Describe the Agent as a decision layer above deterministic descriptors.

The Agent may choose among:

```text
performance candidate
robustness probe
uncertainty probe
abstain
```

The paper should show an immutable pre-result recommendation record containing:

- selected formulation-process state;
- alternatives considered;
- structured uncertainty;
- recommendation rationale;
- process variables to control / perturb;
- falsifiable acceptance criterion;
- timestamp and provenance.

If the historical pre-result record for the current follow-up point is recovered, show it directly. If it is not recovered, retain the workflow as the forward design contract and describe the existing follow-up result as Agent-guided closed-loop validation rather than retroactive preregistration.

### 5. Human-executed wet-lab adjudication

Present the follow-up formulation and the two repeated 120 °C hold measurements.

Use the common 15-60 min window only:

- repeat 1: -0.16%;
- repeat 2: +3.04%;
- mean profile: +1.47%.

Relative to the mean-profile absolute drift, the observed flattening is approximately:

- 6.45x versus E1;
- 34.98x versus E5.

These are descriptive stability-gain ratios on a matched window, not significance tests.

The physical result must be stored separately from the recommendation and linked by `recommendation_id`. This makes the experimental adjudication independent of the original Agent wording.

### 6. Stability-aware design update

Introduce the next-generation objective conceptually:

```text
J_perf = w_eta L_viscosity
       + w_T L_temperature_response
       + w_S L_hold_stability
       + w_R L_repeatability
       + feasibility penalties
```

Then introduce the uncertainty/information layer conceptually:

```text
A(candidate) = -J_perf - lambda_U U_penalty + beta_IG information_value
```

The paper should state explicitly that this is the architecture of the next design round. Numerical weights should not be presented as calibrated unless they are actually frozen and used prospectively.

## Figure plan

### Figure 1 — Scientific and runtime architecture

Use a two-level diagram:

```text
Raw evidence
-> deterministic descriptors
-> formulation-process state + uncertainty
-> Agent recommendation
-> immutable freeze
-> human wet-lab execution
-> separate physical adjudication
-> state update
```

This should make the boundary between deterministic computation, Agent reasoning and human actuation visually explicit.

### Figure 2 — Temperature-dependent viscosity and preparation sensitivity

Show the recorded 80-130 °C curves. Highlight the spread among E2-labelled runs without assigning unverified meanings to GJJ/ZYX/CHH.

### Figure 3 — 120 °C hold stability

Plot E1, E5 and both follow-up repeats together. Emphasize the matched 15-60 min interval. E1/E5 may retain their 90 min points, but the caption must state that follow-up measurements stop at 60 min.

### Figure 4 — Recommendation-to-experiment adjudication

Show the evidence contract rather than a generic Agent cartoon:

```text
uncertainty vector
-> selected candidate + alternatives
-> frozen criterion
-> human execution
-> measured SI / repeat consistency
-> supported / partially supported / falsified / out-of-domain
```

If the historical recommendation record is recoverable, Figure 4 should include its actual timestamp/provenance. Otherwise use this as the forward workflow and keep the current experiment labelled closed-loop.

## Agent evaluation

Avoid a single vague "Agent accuracy" number. Report a compact scorecard built from:

```text
physical criterion success
matched-window stability gain
replicate consistency
uncertainty calibration, when a prior uncertainty statement exists
decision margin / robustness
```

The detailed contract is in `AGENT_EVALUATION.md`.

## Claim hierarchy

### Strong claims supported by current measurements

- process state materially affects observed rheology;
- thermal-hold stability differs strongly across the tested formulations;
- the follow-up formulation is substantially flatter over 15-60 min than E1 and E5;
- repeated measurements reproduce the near-flat response qualitatively and quantitatively.

### Claims that require provenance

- the follow-up point was recommended by the Agent before result inspection;
- the experiment is a strictly prospective physical validation of that recommendation.

These claims should be used only when the timestamped recommendation record is attached.

### Claims that should remain mechanistic hypotheses

- stabilization occurs specifically because AC1920/TK100 reduce reaction kinetics;
- one particular molecular reaction pathway is responsible for the viscosity build-up.

Current rheology supports stabilization, not direct molecular-kinetic proof.

## Writing rule

Every manuscript section should strengthen one of five functions:

```text
physical problem
state + uncertainty representation
Agent recommendation logic
wet-lab adjudication
closed-loop update
```

Material that does not strengthen one of these five functions should remain outside the main manuscript.
