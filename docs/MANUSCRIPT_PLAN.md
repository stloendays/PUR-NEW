# Manuscript plan

## Working title

**Uncertainty-Aware Agent-Guided Formulation Design with Wet-Lab Validation for Reactive Polyurethane Hot-Melt Adhesives**

## Central paper logic

The manuscript should follow one continuous argument:

```text
1. Reactive PUR rheology depends on both formulation and process state.
2. Reaction history, thermal hold time and preparation perturbation are known variables and should enter the design loop.
3. Static viscosity targeting alone is therefore incomplete.
4. Deterministic descriptors quantify temperature response, hold drift and repeatability.
5. Independent literature/patent evidence is used to formulate a finite resin-modification hypothesis space.
6. The Agent reasons over local evidence, external evidence, structured uncertainty and the finite candidate set.
7. The Agent recommends a formulation-process state and freezes a falsifiable criterion.
8. A human executes the experiment.
9. A separate wet-lab record adjudicates the recommendation.
10. The measured stability information updates the next design state.
```

The Agent is not presented as a robotic chemist. The scientific claim is about **evidence-grounded decision quality under uncertainty** and **physical adjudication of a recommendation**.

---

## Suggested Results and Discussion order

### 1. Local formulation design and temperature-dependent rheology

Introduce E1-E5 and explain the two local axes:

- NCO:OH at fixed 50/50 PPG2000/PDP-70;
- PPG2000/PDP-70 ratio at fixed NCO:OH = 1.80.

Show the 80-130 C sweeps and the large E2 run-to-run spread. The purpose is to establish that process realization materially changes the absolute viscosity level.

### 2. Thermal holding exposes the process-stability problem

Show E1 and E5 at 120 C. Quantify drift using the shared stability index.

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

This section prevents the Agent contribution from becoming an opaque language-model decision.

### 4. Evidence-derived candidate-space hypothesis

This section must explicitly answer:

> Why were these formulation candidates considered in the first place?

Use `docs/CANDIDATE_SPACE_HYPOTHESIS.md` as the source of truth.

#### 4.1 Local reactive-core anchor

E2 is used as the central local design point because it sits at:

```text
PPG2000:PDP-70 = 50:50
NCO:OH = 1.80
```

between the E1/E3 stoichiometric perturbations and E4/E5 composition perturbations.

Its normalized reactive core is approximately:

```text
PPG2000 39.9047%
PDP-70  39.9047%
MDI     20.1907%
```

The candidate generator preserves these relative core proportions and allocates part of the total formulation to modifier axes.

#### 4.2 Acrylic-like modifier axis

Three independent external anchors define the coarse acrylic axis:

- **15%**: peer-reviewed 2025 heat-resistant reactive-PUR study reporting 15% acrylic resin as the preferred overall level in that system;
- **~20%**: repeated US20160215185A1 examples containing roughly 19-20% acrylic tackifying resin;
- **25%**: US6465104B1 Example 10, which also provides direct 121 C viscosity-stability data.

Therefore:

```text
acrylic-like axis = {0, 15, 20, 25}%
```

#### 4.3 Minor tackifier-like axis

US5932680A provides working examples around 4.8-6.4% resin and a preferred resin range of about 3-10 wt%. US20070155859A1 separately describes tackifiers/rheology-control agents as typically used below about 10 wt%.

Therefore:

```text
minor tackifier-like axis = {0, 5, 10}%
```

#### 4.4 Stability hypothesis

US6465104B1 reports substantially slower hot-hold viscosity increase for a low-OH acrylic copolymer than for a higher-OH acrylic at the same 25 wt% loading. This supports the hypothesis that **modifier functionality/effective reactive-group density**, rather than loading alone, can affect hot-hold stability.

US20030022973A1 provides additional directional evidence that functional-tackifier/acrylic formulation changes alter reported stability values.

The paper-facing hypothesis is:

> Partial replacement of an unstable reactive-only PUR formulation by an acrylic-like modifier and an optional minor tackifier-like modifier may reduce thermal-hold viscosity build-up, with modifier functionality and process history treated as explicit uncertainties.

The candidate set is the 12-point Cartesian product:

```text
{0,15,20,25}% acrylic-like
x
{0,5,10}% tackifier-like
```

The exact current follow-up recipe is **not** encoded as a discrete candidate.

#### 4.5 Chronology caveat

This formal V2 hypothesis was written after the current follow-up experiment was already known. Therefore the current multi-model benchmark is a **held-out-result blind replay**, not prospective validation of V2 itself. Future rounds can be prospective once V2 is frozen.

### 5. Agent-guided recommendation under uncertainty

Describe the Agent as a decision layer above deterministic descriptors and evidence retrieval.

The Agent may choose among:

```text
performance candidate
robustness probe
uncertainty probe
abstain
```

The primary Agent condition should include:

```text
original local evidence
+ structured uncertainty
+ candidate-space hypothesis
+ uncertainty-aware actions
+ external database/literature retrieval
+ finite candidate set
```

The Agent should preserve an evidence trace showing which source rows/actions informed the recommendation.

The paper should show an immutable recommendation record containing:

- selected formulation-process state;
- alternatives considered;
- structured uncertainty;
- evidence/action trace;
- recommendation rationale;
- process variables to control / perturb;
- falsifiable acceptance criterion;
- timestamp and provenance.

### 6. Human-executed wet-lab adjudication

Present the follow-up formulation and the two repeated 120 C hold measurements.

Use the common 15-60 min window only:

- repeat 1: -0.16%;
- repeat 2: +3.04%;
- mean profile: +1.47%.

Relative to the mean-profile absolute drift, the observed flattening is approximately:

- 6.45x versus E1;
- 34.98x versus E5.

These are descriptive stability-gain ratios on a matched window, not significance tests.

The physical result must be stored separately from the recommendation and linked by `recommendation_id`.

### 7. Held-out-result Agent benchmark

Use V2 rather than the older answer-shaped scalar-modifier grid.

Primary benchmark question:

> Does the full Agent, while blinded to the current follow-up formulation/outcome, rank candidates close to the later experimental composition in the two-dimensional acrylic/tackifier modifier plane?

Primary metrics should include:

```text
nearest-candidate rank
nearest-candidate Top-1 / Top-3 recovery
modifier-plane distance of Top-1 and Top-3
selection distribution
abstention rate
scientific-boundary violation rate
```

Ablations:

```text
full Agent
without external database
without action enrichment
literature-only sanity
without explicit candidate-hypothesis context
```

### 8. Stability-aware design update

Introduce the next-generation objective conceptually:

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

Numerical weights should not be presented as calibrated unless they are actually frozen and used prospectively.

---

## Figure plan

### Figure 1 — Scientific and runtime architecture

```text
Raw evidence
-> deterministic descriptors
-> formulation-process state + uncertainty
-> external evidence -> candidate-space hypothesis
-> Agent recommendation
-> immutable freeze
-> human wet-lab execution
-> separate physical adjudication
-> state update
```

### Figure 2 — Temperature-dependent viscosity and preparation sensitivity

Show 80-130 C curves and E2 spread.

### Figure 3 — Evidence-to-candidate-space map

Show:

```text
local E2 core
+
15 / 20 / 25% acrylic evidence anchors
+
5 / 10% minor tackifier evidence anchors
-> 4 x 3 finite hypothesis grid
```

Include source labels and limitations rather than only a cartoon.

### Figure 4 — 120 C hold stability

Plot E1, E5 and both follow-up repeats together; emphasize the matched 15-60 min interval.

### Figure 5 — Agent recommendation and held-out physical comparison

Show candidate ranking/action trace and the position of the held-out follow-up composition only on the controller/evaluation side.

---

## Claim hierarchy

### Strong claims supported by current measurements

- process state materially affects observed rheology;
- thermal-hold stability differs strongly across the tested formulations;
- the follow-up formulation is substantially flatter over 15-60 min than E1 and E5;
- repeated measurements reproduce the near-flat response qualitatively and quantitatively.

### Evidence-supported hypotheses

- resin-modified PUR is a justified candidate family when reactive-only formulations show robustness problems;
- independent external evidence supports coarse acrylic-like levels around 15, 20 and 25%;
- independent external evidence supports a minor tackifier-like axis around 5% with a coarse upper level near 10%;
- acrylic reactive-group density/functionality can affect hot-hold viscosity stability.

### Claims that require provenance

- the current follow-up point was prospectively recommended by the Agent before result inspection;
- the current experiment is a strictly prospective validation of the V2 Agent hypothesis.

Do not use these unless a pre-result timestamped record is recovered.

### Claims that should remain mechanistic hypotheses

- stabilization occurs specifically because AC1920/TK100 reduce one particular reaction rate;
- one molecular pathway alone is responsible for the viscosity build-up.

Current rheology supports stabilization and the external literature supports a formulation hypothesis, not direct local molecular-kinetic proof.

## Writing rule

Every manuscript section should strengthen one of six functions:

```text
physical problem
state + uncertainty representation
evidence-derived candidate hypothesis
Agent recommendation logic
wet-lab adjudication
closed-loop update
```

Material that does not strengthen one of these functions should remain outside the main manuscript.
