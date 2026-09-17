# Manuscript plan

## Working title

**Uncertainty-Aware Agent-Guided Formulation Design with Wet-Lab Validation for Reactive Polyurethane Hot-Melt Adhesives**

The title can be shortened later once the final journal scope is chosen.

## Central paper logic

The manuscript should follow one continuous argument:

```text
1. Reactive PUR rheology depends on both formulation and process state.
2. Reaction history, thermal hold time and preparation perturbation are known variables and should enter the design loop.
3. A static viscosity target alone is therefore insufficient.
4. The Agent's role is to quantify uncertainty / robustness and recommend what should be tested.
5. A human executes the recommended formulation and measurement.
6. The wet-lab result adjudicates the recommendation.
7. The measured stability information is fed back into the next design objective.
```

The Agent is not presented as a robotic chemist. The scientific claim is about **decision quality under uncertainty** and **physical validation of the recommendation**.

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

### 3. Agent-guided recommendation under uncertainty

Describe the information available to the Agent:

```text
formulation state
+ reaction / preparation history
+ thermal hold conditions
+ observed variability
-> uncertainty-aware recommendation
```

State explicitly that the Agent recommends; the operator executes.

The paper should show a recommendation record containing the formulation point, rationale, uncertainty summary, process conditions and timestamp/provenance.

### 4. Human-executed wet-lab adjudication

Present the follow-up formulation and the two repeated 120 °C hold measurements.

Use the common 15-60 min window only:

- repeat 1: -0.16%;
- repeat 2: +3.04%;
- mean profile: +1.47%.

This is the physical evidence used to judge the quality of the recommendation.

### 5. Stability-aware design update

Introduce the next-generation objective conceptually:

```text
J = w_eta L_viscosity
  + w_T L_temperature_response
  + w_S L_hold_stability
  + feasibility penalties
```

The central methodological advance is the transition from one-shot target matching to an iterative formulation-process design loop.

## Figure plan

### Figure 1 — Scientific architecture

A compact workflow figure:

```text
Evidence
  -> formulation + process state
  -> uncertainty-aware Agent
  -> recommended test point
  -> human wet-lab execution
  -> rheology / stability result
  -> adjudication
  -> next design round
```

### Figure 2 — Temperature-dependent viscosity and preparation sensitivity

Show the recorded 80-130 °C curves. Highlight the spread among E2-labelled runs without over-interpreting the GJJ/ZYX/CHH labels.

### Figure 3 — 120 °C hold stability

Plot E1, E5 and both follow-up repeats together. The visual comparison should emphasize the matched 15-60 min interval. E1/E5 may retain their 90 min points, but the figure caption must state that follow-up measurements stop at 60 min.

### Figure 4 — Recommendation-to-experiment adjudication

Summarize:

```text
Agent recommendation
-> uncertainty rationale
-> human execution
-> observed stability drift
-> supported / partially supported / falsified
```

This should be the figure that makes the Agent contribution concrete.

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

Do not bring unrelated historical benchmark narratives into this paper. Every section should serve one of four functions:

```text
physical problem
Agent recommendation logic
wet-lab adjudication
closed-loop design update
```

Anything that does not strengthen one of these four functions should remain outside the main repository and manuscript.