# Manuscript plan

## Working title

**State-Conditioned Rheological Design and Uncertainty-Aware Agent Guidance for Reactive Polyurethane Hot-Melt Adhesives**

The title should foreground the physical/statistical result before the Agent contribution. A shorter journal-specific title can be chosen later.

## Central paper logic

The manuscript should follow one continuous argument:

```text
1. Reactive PUR rheology depends on both chemistry and experimental/process realization.
2. In the present local chemistry family, realization strongly changes absolute viscosity level.
3. However, the 80-130 C relative temperature-response shape is comparatively conserved.
4. A realization-specific scale shift plus a shared thermal-response function therefore forms a low-dimensional local rheological state model.
5. One state anchor can calibrate an unseen realization far more accurately than formulation identity alone.
6. Isothermal viscosity drift is a second, differently tunable rheological response: E1/E5 differ strongly and F1 enters a low-drift regime.
7. Broad external data show that chemistry controls the wider thermal-response landscape, so the local master curve is not universal.
8. These results motivate a state-aware design representation with explicit uncertainty and separate temperature/stability objectives.
9. Independent literature/patent evidence defines a finite resin-modification hypothesis space.
10. The Agent reasons over local state evidence, external evidence and uncertainty, then recommends or abstains.
11. Human wet-lab execution provides the physical adjudication and updates the next design round.
```

The Agent is not presented as a robotic chemist. The paper should remain scientifically useful even if a reader ignores the LLM implementation: the first contribution is the **structure of reactive-PUR rheological variability**, and the second is an **evidence-grounded decision layer built on that structure**.

---

## Suggested Results and Discussion order

### 1. Local formulation design and raw temperature-dependent rheology

Introduce E1-E5 and explain the two local axes:

- NCO:OH at fixed 50/50 PPG2000/PDP-70;
- PPG2000/PDP-70 ratio at fixed NCO:OH = 1.80.

Show the 80-130 C sweeps. Emphasize that nominal formulation does not uniquely determine measured viscosity level. The strongest example is E2, whose recorded realizations differ by roughly 2.8-3.6x at matched temperatures.

Do not yet interpret GJJ/ZYX/CHH as causal categories. They are within-operator realization labels from the same operator.

### 2. State-shift master curve and one-point calibration

This is the primary modeling result.

#### 2.1 Model-free curve collapse

Normalize every recorded curve by its own 120 C viscosity:

```text
relative_eta(T) = eta(T) / eta(120 C)
```

Across the seven realizations, the non-anchor normalized-curve CV is only about 3.4-10.3% despite the much larger spread in absolute viscosity.

This is the clearest visual evidence that realization predominantly changes viscosity scale while preserving a transferable local temperature-response shape.

#### 2.2 Positive state model

Use the compact structural model:

```text
ln eta_r(T) = alpha_r + g(T) + epsilon
```

where `alpha_r` is realization/state specific and `g(T)` is shared within the measured local chemistry family.

The preferred low-complexity implementation is a quadratic function in inverse temperature. The conclusion is robust to using a quadratic function in ordinary temperature, while a cubic inverse-temperature term gives negligible cross-validation improvement and worse BIC.

#### 2.3 Formulation-only versus state-aware comparison

Report the formal comparison:

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

Because there are only seven realization groups, do not make the mixed-effects model the headline inferential result.

#### 2.4 Strict unseen-realization one-point calibration

This is the strongest predictive test.

Remove one complete realization from training. For E1/E2 cases where the nominal formulation remains represented by another realization, compare:

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

The manuscript-facing statement should be:

> Within a nominal formulation already represented in the local chemistry family, a new realization cannot be located accurately from formulation identity alone, but one state-specific viscosity anchor is sufficient to calibrate the remaining measured temperature curve to roughly 6-10% multiplicative error.

Do not call this universal chemistry extrapolation. It is state calibration within the local chemistry family.

### 3. Temperature response and thermal-hold stability are distinct, differently tunable coordinates

The individual local 80-130 C curves have a comparatively concentrated apparent temperature-sensitivity descriptor:

```text
mean apparent E_eta = 41.87 kJ/mol
SD                  = 2.27 kJ/mol
CV                  = 5.4%
median curve R2     = 0.9948
```

`E_eta` is a rheological temperature-sensitivity descriptor, not a molecular reaction activation energy.

In contrast, the 120 C hold response is strongly formulation dependent:

```text
E1 fitted dln(eta)/dt ~= 0.125 h^-1
E5 fitted dln(eta)/dt ~= 0.537 h^-1
ratio                 ~= 4.29x
```

Matched 15-60 min drift:

```text
E1  +9.51%
E5 +51.54%
F1 mean +1.47%
```

F1 therefore reduces absolute matched-window drift by about 84.5% versus E1 and 97.1% versus E5.

Use the phrase:

> **distinct, differently tunable rheological coordinates**

Do not use `independent` or `orthogonal`, because E5 and F1 do not yet have matched full temperature sweeps and the external thermal/stability datasets do not overlap sample-by-sample.

### 4. External database defines the generalization boundary

The 39 external prepolymer curves contain 4559 temperature-viscosity points.

Their temperature curves remain highly regular:

```text
median ln(eta)-1/T R2 = 0.9967
37 / 39 curves have R2 >= 0.98
```

but apparent thermal sensitivity spans roughly:

```text
34.7-94.2 kJ/mol
```

Thus the approximately 42 kJ/mol local scale is not a universal PUR constant.

Prefer cross-validated composition-model strength over in-sample R2 when discussing the database:

```text
thermal descriptor:
  additive composition LOOCV R2 ~= 0.593
  pNCO x polyol model LOOCV R2 ~= 0.616

fitted 75 C log-viscosity:
  additive composition LOOCV R2 ~= 0.797
  pNCO x polyol model LOOCV R2 ~= 0.822
```

The correct multiscale interpretation is:

```text
chemistry controls the broad rheological landscape
+
process/experimental state controls where a local realization sits within that landscape
```

The external temperature-curve dataset and the nine viscosity-rise-rate patent records have no shared sample identifiers, so they must not be used to claim direct external statistical independence between thermal sensitivity and stability.

### 5. Deterministic state construction and uncertainty decomposition

Only after the physical/statistical result is established, introduce the design-state representation:

```text
formulation state
+ process / realization state
+ measured support
+ thermal-response descriptor
+ hold-stability descriptor
+ repeatability
+ missingness
```

Separate uncertainty into:

```text
measurement
repeatability
process history
extrapolation
evidence coverage
```

This section should explicitly connect to the modeling result: the workflow keeps state because the data show that collapsing realizations into composition alone destroys predictive information.

### 6. Evidence-derived candidate-space hypothesis

This section answers:

> Why were these formulation candidates considered?

Use `docs/CANDIDATE_SPACE_HYPOTHESIS.md` as the source of truth.

#### 6.1 Local reactive-core anchor

E2 is the central local design point:

```text
PPG2000:PDP-70 = 50:50
NCO:OH = 1.80
```

Its normalized reactive core is approximately:

```text
PPG2000 39.9047%
PDP-70  39.9047%
MDI     20.1907%
```

#### 6.2 Acrylic-like modifier axis

Independent evidence defines:

```text
acrylic-like axis = {0, 15, 20, 25}%
```

using the peer-reviewed 15% example, repeated ~19-20% patent examples and the 25% hot-hold-stability example already documented in the repository.

#### 6.3 Minor tackifier-like axis

Independent PUR formulation evidence supports:

```text
minor tackifier-like axis = {0, 5, 10}%
```

The resulting V2 candidate set is the 12-point Cartesian product.

The exact current follow-up recipe is not encoded as a discrete candidate.

#### 6.4 Chronology caveat

The formal V2 hypothesis was written after the current follow-up experiment was known. Therefore the current benchmark is a **held-out-result blind replay**, not prospective validation of V2 itself. Future rounds can be prospective once V2 is frozen.

### 7. Agent-guided recommendation under uncertainty

Describe the Agent as a decision layer above deterministic descriptors and evidence retrieval.

The Agent may choose:

```text
performance candidate
robustness probe
uncertainty probe
abstain
```

The primary Agent condition should include:

```text
original local evidence
+ state-aware rheology descriptors
+ structured uncertainty
+ candidate-space hypothesis
+ uncertainty-aware actions
+ external database/literature retrieval
+ finite candidate set
```

The paper should show an immutable recommendation record containing selected state, alternatives, uncertainty, evidence/action trace, rationale, controlled/perturbed process variables, acceptance criterion, timestamp and provenance.

### 8. Human-executed wet-lab adjudication

Present the follow-up formulation and the two repeated 120 C hold measurements.

Use the common 15-60 min window only:

- repeat 1: -0.16%;
- repeat 2: +3.04%;
- mean profile: +1.47%.

The physical result is stored separately from the recommendation and linked by `recommendation_id`.

### 9. Held-out-result Agent benchmark

Use V2 rather than the older answer-shaped scalar modifier grid.

Primary question:

> Does the full Agent, while blinded to the current follow-up formulation/outcome, rank candidates close to the later experimental composition in the two-dimensional modifier plane?

Primary metrics:

```text
nearest-candidate rank
Top-1 / Top-3 regional recovery
modifier-plane distance
selection distribution
abstention rate
scientific-boundary violation rate
```

Report deterministic/literature baselines so the Agent is not credited merely for following an obvious ~20% literature prior.

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

Do not present numerical weights as calibrated until they are frozen and used prospectively.

---

## Figure plan

### Figure 1 — Scientific and runtime architecture

```text
raw evidence
-> rheological state structure
-> deterministic descriptors + uncertainty
-> external evidence / candidate hypothesis
-> Agent recommendation
-> immutable freeze
-> human wet-lab execution
-> physical adjudication
-> state update
```

### Figure 2 — State-shift master curve and one-point calibration

Recommended four panels:

```text
A raw 80-130 C curves, showing absolute realization spread
B curves normalized by eta(120 C), showing master-curve collapse
C shared-shape bootstrap band and/or apparent E_eta by realization
D strict unseen-realization error: formulation-only vs one-point calibrated
```

This should be the strongest quantitative figure in the paper.

### Figure 3 — Thermal-hold stability as a second rheological coordinate

Plot E1, E5 and both F1 repeats at 120 C. Show matched-window SI and, where appropriate, fitted log-drift rates. A small inset may contrast the narrow local E_eta distribution with the much larger hold-rate effect size, while avoiding an orthogonality claim.

### Figure 4 — Evidence-to-candidate-space map

Show:

```text
local E2 core
+
15 / 20 / 25% acrylic evidence anchors
+
5 / 10% minor tackifier evidence anchors
-> 4 x 3 finite hypothesis grid
```

Include evidence limitations.

### Figure 5 — Agent recommendation and held-out physical comparison

Show candidate ranking/action trace and the held-out follow-up composition only on the controller/evaluation side.

---

## Claim hierarchy

### Strong claims supported by current local data

- nominal formulation alone does not determine observed viscosity level across repeated realizations;
- within the measured local chemistry family, much of the realization effect behaves approximately as a viscosity-scale shift;
- a shared local temperature-response shape plus one realization anchor predicts held-out realization curves much more accurately than formulation identity alone;
- thermal-hold stability differs strongly across tested formulations;
- the F1 follow-up enters a substantially lower-drift regime over the matched 15-60 min interval.

### Strong claims supported by external database context

- dense external PUR/prepolymer temperature curves are individually regular in `ln(eta)` versus `1/T`;
- the thermal-sensitivity scale varies substantially across chemistry families;
- composition explains a meaningful but incomplete fraction of between-curve thermal and viscosity variation.

### Evidence-supported hypotheses

- resin-modified PUR is a justified candidate family when reactive-only formulations show robustness problems;
- acrylic-like and minor-tackifier-like axes used in V2 are independently grounded in external evidence;
- modifier functionality/reactive-group density may influence hot-hold stability.

### Claims that require prospective provenance

- a future experimental point was selected before its result was known;
- a future wet-lab result prospectively validates a frozen Agent recommendation.

### Claims that remain too strong

- the local master curve is universal across reactive PUR chemistry;
- temperature sensitivity and stability are universally statistically independent;
- one molecular pathway alone explains the observed viscosity build-up;
- any literature modifier percentage is a universal optimum.

## Writing rule

Every main-text section should strengthen one of seven functions:

```text
physical variability problem
low-dimensional rheological state structure
distinct stability response
state + uncertainty representation
evidence-derived candidate hypothesis
Agent recommendation logic
wet-lab adjudication / closed-loop update
```

Material that does not strengthen one of these functions should remain in Supplementary Information.
