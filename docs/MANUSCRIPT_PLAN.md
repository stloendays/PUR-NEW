# Manuscript plan

## Working title

**State-Conditioned Rheological Design and Evidence-Grounded Scientific Agent Guidance for Reactive Polyurethane Hot-Melt Adhesives**

The physical/statistical discovery remains the first contribution. The Agent is the scientific decision layer that turns those findings into a useful experiment.

## Central paper logic

```text
1. Original E1-E5 experiments reveal chemistry- and realization-dependent rheology.
2. State-shift modeling identifies a transferable local thermal-response shape plus a realization-specific viscosity scale.
3. One realization-specific anchor strongly improves unseen-realization reconstruction.
4. Temperature response and thermal-hold stability emerge as distinct, differently tunable coordinates.
5. These findings establish the state-aware design theory.
6. Independent external evidence identifies a plausible resin-modification direction.
7. The Agent uses the pre-result physical/model findings as tools, reasons over external evidence and uncertainty, and selects a formulation-process experiment point.
8. The recommendation and acceptance criterion are frozen before the corresponding wet-lab outcome is inspected.
9. Humans execute the experiment.
10. The resulting 120 C hold response physically adjudicates the recommendation.
11. Repeated held-out replay is used only as a secondary reproducibility check, not as the main scientific result.
```

Main methodological statement:

> **Physical/model findings first establish a state-aware rheological design theory. A discovery-to-experiment Agent then operationalizes those findings to choose a falsifiable formulation-process experiment, and human wet-lab execution provides independent physical adjudication.**

The formulation stored internally as `F1` should be called the **Agent-selected validation formulation**.

---

## Results and Discussion order

### 1. Local formulation design and raw temperature-dependent rheology

Introduce E1-E5 and the two local axes:

- E1/E2/E3: NCO:OH = 1.70/1.80/1.90 at fixed 50/50 PPG2000/PDP-70;
- E4/E2/E5: PPG2000/PDP-70 composition perturbation around 50/50 at NCO:OH = 1.80.

Show the 80-130 C sweeps. GJJ/ZYX/CHH are within-operator realization labels from the same operator, not separate operators.

### 2. State-shift master curve and one-point calibration

Use:

```text
ln eta_r(T) = alpha_r + g(T) + epsilon
```

where `alpha_r` is realization/state specific and `g(T)` is shared within the measured local chemistry family.

Key comparison:

```text
formulation-only R2 ~= 0.895
state-shift shared-shape R2 ~= 0.998
held-temperature formulation-only error ~= 1.406x
held-temperature state-aware error      ~= 1.055x
```

Supporting mixed-effects result:

```text
random-intercept SD ~= 0.325 log-unit
point residual SD   ~= 0.047 log-unit
ICC                 ~= 0.979
```

Strict one-point calibration for eligible E1/E2 realizations:

```text
formulation-only error: ~1.599-1.611x
one-point calibrated:   ~1.065-1.098x
```

Interpretation:

> Within a nominal formulation already represented in the local chemistry family, one state-specific viscosity anchor can locate a new realization on the shared local thermal-response shape with roughly 6-10% multiplicative error across the remaining measured temperatures.

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

External prepolymer database:

```text
39 dense curves
4559 temperature-viscosity points
median ln(eta)-1/T R2 = 0.9967
37 / 39 curves have R2 >= 0.98
apparent E_eta range ~= 34.7-94.2 kJ/mol
```

Interpretation:

```text
chemistry controls the broad rheological landscape
+
process / experimental state controls where a local realization sits within that landscape
```

### 5. State-aware design theory

The design object is:

```text
formulation state
+ process / realization state
+ thermal-response descriptor
+ hold-stability descriptor
+ repeatability
+ missingness / evidence coverage
```

State is retained because the measurements show that composition-only representation discards predictive information.

### 6. Evidence-grounded formulation hypothesis

Independent evidence supports a coarse resin-modification region:

```text
acrylic-like modifier: approximately 15-25%
minor tackifier-like modifier: approximately 0-10%
```

This evidence defines plausible intervention directions. It does not prove an AC1920/TK100 molecular mechanism or a universal optimum.

The current 4x3 V2 grid is a later reproducible formalization of this region, not the historical freeze artifact.

### 7. Discovery-to-Experiment Agent V3

The canonical decision system is:

```text
planner
-> evidence/tool layer
-> proposer
-> skeptic
-> robustness adjudicator
-> judge
-> freeze
```

The central scientific Action is:

```text
get_state_aware_rheology_summary()
```

It exposes the upstream physical/model findings without exposing F1 or its result. The Agent therefore does not merely read literature and match a recipe; it uses the experimentally discovered rheological structure as a decision tool.

The roles are:

- **Planner:** identify the failure mode and which discovered rules matter;
- **Evidence/tool layer:** retrieve state-aware rheology, original measurements, external evidence, candidate profiles and process-state uncertainty;
- **Proposer:** rank experiments by scientific usefulness;
- **Skeptic:** try to falsify the provisional choice and expose interpretability problems;
- **Robustness adjudicator:** test whether the point remains useful under reasonable alternative evidence priorities and process uncertainty;
- **Judge:** resolve the records and choose a performance point, robustness probe, uncertainty probe or abstention;
- **Freeze:** programmatically validate and store the final recommendation, hashes and pre-result acceptance criterion.

The Skeptic and Robustness Adjudicator are quality-control stages. The paper does **not** need to prove their individual necessity by ablation.

### 8. Pre-result Agent recommendation

The Agent-selected validation formulation is:

```text
PPG2000 = 39.60
PDP-70  = 39.60
AC1920  = 17
TK100   = 5
MDI     = 20.19
```

The research team confirms that the wet-lab outcome was unavailable to the Agent when the formulation was selected. The current repository does not contain the original contemporaneous freeze artifact, so author-confirmed chronology must not be presented as Git timestamp proof.

### 9. Human-executed physical adjudication

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

Therefore:

> **The subsequent wet-lab measurements support the pre-result Agent recommendation with respect to thermal-hold stability over the matched 15-60 min window.**

Do not promote this to proof of one molecular pathway.

### 10. Secondary Agent reproducibility analysis

Repeated API replay is optional supporting evidence. It asks only:

> Under the same leakage-safe pre-result evidence contract, does the full scientific workflow repeatedly prioritize a similar and defensible formulation region?

Useful metrics:

```text
selection distribution
Top-1 / Top-3 regional consistency
modifier-plane distance
selection entropy
abstention/failure rate
scientific-boundary violations
evidence/tool trace completeness
```

This section is secondary to physical validation. No component ablation is required for the central paper claim.

### 11. Stability-aware design update

Future objective functions should separate absolute performance, thermal response, temporal stability and repeatability:

```text
J_perf = w_eta L_viscosity
       + w_T L_temperature_response
       + w_S L_hold_stability
       + w_R L_repeatability
       + feasibility penalties
```

Do not present numerical weights as calibrated until frozen and used prospectively.

---

## Figure plan

### Figure 1 — Scientific chronology and V3 decision system

Panel A:

```text
Physical + model findings
-> State-aware design theory
-> Agent recommendation
-> Freeze
-> Human experiment
-> Physical adjudication
```

Panel B:

```text
Planner
-> Evidence/Tools
-> Proposer
-> Skeptic
-> Robustness Adjudicator
-> Judge
-> Freeze
```

### Figure 2 — State-shift master curve and one-point calibration

```text
A raw 80-130 C curves
B eta(T)/eta(120 C) collapse
C apparent E_eta / shared-shape representation
D formulation-only versus one-point calibrated held-out error
```

### Figure 3 — Thermal-hold stability and Agent physical validation

Plot E1, E5 and both validation-formulation repeats at 120 C. Show matched 15-60 min SI and the chronological boundary between recommendation and later measurement.

### Figure 4 — Evidence-to-candidate-region map

Show the E2 core plus external acrylic/tackifier evidence anchors and the later V2 4x3 formalization.

### Optional Figure/SI — Replay reproducibility

If useful, show repeated selection distribution, region consistency and boundary-violation checks. Do not make this larger than the physical-validation result.

---

## Claim hierarchy

### Strong physical/model claims

- nominal formulation alone does not determine observed viscosity level across repeated realizations;
- within the measured local chemistry family, much of the realization effect behaves approximately as a viscosity-scale shift;
- one realization anchor reconstructs held-out local temperature curves much better than formulation identity alone;
- temperature response and thermal-hold stability are distinct, differently tunable coordinates in the present local design.

### Agent physical-validation claim

- the research team confirms that the Agent selected the validation formulation before the corresponding wet-lab outcome was known to the Agent;
- human execution subsequently produced two low-drift hold trajectories;
- those measurements support the recommendation with respect to thermal-hold stability.

### Current Agent-method claim

- V3.3.1 operationalizes the measured material regularities through a multi-stage decision system with evidence/tool use, scientific falsification, robustness adjudication and immutable freeze;
- its value is primarily the quality, traceability and physical usefulness of the selected experiment, not component-wise benchmark superiority.

### Provenance boundary

- the current repository does not contain the original contemporaneous historical freeze artifact;
- today's V2 grid and V3 software are later formalizations unless older provenance establishes otherwise;
- current replay results must not be backdated into the historical recommendation event.

### Claims that remain too strong

- the local master curve is universal across reactive PUR chemistry;
- temperature sensitivity and stability are universally statistically independent;
- one molecular pathway alone explains viscosity build-up;
- any literature modifier percentage is a universal optimum;
- today's V3 code is the exact historical runtime that selected F1.
