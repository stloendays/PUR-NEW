# Research narrative

## 1. Problem definition

The project is not framed as a static composition-to-viscosity regression problem. In reactive polyurethane hot-melt adhesives, the measured response depends on both **formulation** and **process state**.

```text
x_chem = formulation variables
z_proc = reaction history, thermal holding time, preparation / batch perturbation
```

Conceptually:

```text
y = rheology(x_chem, z_proc) + experimental uncertainty
```

The practical objective is not merely to hit one viscosity value. It is to identify formulation-process states whose rheology remains useful and sufficiently stable under realistic processing history.

## 2. What was already known

Reaction history, time at temperature and preparation disturbance were already recognized as relevant variables. The scientific gap was that they had not yet been represented explicitly enough in the formulation-selection objective.

The role of the experiment is therefore not to discover that process history exists. It is to quantify how strongly the local system responds to those variables and to determine whether a recommendation remains physically useful after execution.

## 3. Local experimental design

The local chemistry is based on:

- PPG2000;
- STEPANPOL PDP-70;
- 4,4'-MDI.

The five-point design separates two local axes:

1. **stoichiometric axis** — E1/E2/E3 change NCO:OH from 1.70 to 1.90 at a 50/50 PPG2000/PDP-70 ratio;
2. **composition axis** — E4/E5 change the PPG2000/PDP-70 ratio around the 50/50 point at NCO:OH = 1.80.

E2 is therefore the centre of the original local design, not a point selected from the later follow-up result.

## 4. What the initial measurements show

The 80-130 C measurements decrease monotonically with temperature for every recorded full sweep. However, nominally identical E2 measurements show large differences in absolute viscosity level across recorded runs. A single deterministic viscosity target is therefore not enough to describe the laboratory system.

The 120 C hold experiment makes the process-time effect explicit. E1 increases by 9.51% from 15 to 60 min, while E5 increases by 51.54% over the same interval. By 90 min the increases are 16.85% and 93.08%, respectively.

The important conclusion is:

> thermal-hold stability is a formulation-dependent design response, not merely metadata attached to a viscosity measurement.

## 5. Candidate-space hypothesis from independent evidence

The next question is not simply which candidate the Agent should select, but **why a resin-modified candidate family should enter the search space at all**.

The V2 hypothesis is built from two independent sources of information:

```text
original local E2 reactive core
+
external PUR formulation/stability evidence
```

### 5.1 Original reactive-core anchor

Normalizing the original E2 amounts gives approximately:

```text
PPG2000 39.9047%
PDP-70  39.9047%
MDI     20.1907%
```

Candidate construction preserves these relative core proportions while allocating part of the total formulation to resin modifiers.

### 5.2 Acrylic-like evidence anchors

Independent external evidence supports coarse acrylic-modifier levels at:

```text
15%  — peer-reviewed 2025 heat-resistant reactive-PUR study
~20% — repeated US20160215185A1 acrylic-tackifying-resin examples
25%  — US6465104B1 acrylic-copolymer example with direct hot-hold stability data
```

This motivates:

```text
acrylic-like axis = {0, 15, 20, 25}%
```

### 5.3 Minor tackifier-like evidence anchors

US5932680A contains working examples around 4.8-6.4% tackifying/hydrocarbon resin and gives a preferred resin range of roughly 3-10 wt%. US20070155859A1 separately describes tackifiers/rheology-control agents as typically used below about 10 wt%.

This motivates:

```text
minor tackifier-like axis = {0, 5, 10}%
```

### 5.4 Stability rationale

US6465104B1 compares two 25 wt% acrylic formulations at 121 C. The lower-OH acrylic example exhibited substantially slower viscosity rise than the higher-OH acrylic comparator. This supports a hypothesis that modifier functionality/effective reactive-group density can influence hot-hold stability.

US20030022973A1 provides additional directional evidence that changing functional tackifier/acrylic formulations changes reported hot-melt stability, although those comparisons are confounded by other formulation changes.

The resulting hypothesis is:

> Partial replacement of an unstable reactive-only PUR formulation by an acrylic-like modifier and an optional minor tackifier-like modifier may reduce thermal-hold viscosity build-up, while modifier functionality and process history remain explicit uncertainties.

The finite V2 grid is the 12-point Cartesian product:

```text
{0,15,20,25}% acrylic-like
x
{0,5,10}% minor tackifier-like
```

The exact later follow-up recipe is not encoded as a discrete candidate.

## 6. Agent role in the design loop

The Agent is not a robotic laboratory controller. It is a **decision layer** operating over:

```text
local measured evidence
+ deterministic response descriptors
+ structured uncertainty
+ candidate-space hypothesis
+ external database/literature evidence
+ finite admissible candidates
```

Its intended responsibilities are:

```text
retrieve evidence
-> inspect thermal-hold / repeatability risk
-> compare class-specific candidate priors
-> audit process-history uncertainty
-> stress-test alternatives
-> recommend or abstain
-> record why the point was selected
```

The human operator performs synthesis and rheology measurement. The experimental result is the physical adjudicator.

## 7. Follow-up formulation and physical result

The follow-up formulation uses the source-reported parts basis:

| PPG2000 | PDP-70 | AC1920 | TK100 | MDI |
|---:|---:|---:|---:|---:|
| 39.60 | 39.60 | 17 | 5 | 20.19 |

Two repeated 120 C hold measurements give:

| time | repeat 1 | repeat 2 | mean |
|---:|---:|---:|---:|
| 15 min | 1230 | 1281 | 1255.5 |
| 30 min | 1189 | 1260 | 1224.5 |
| 45 min | 1203 | 1289 | 1246.0 |
| 60 min | 1228 | 1320 | 1274.0 |

The corresponding 15->60 min drifts are -0.16% and +3.04%; the mean profile changes by approximately +1.47%.

Compared on the same 15-60 min interval, the follow-up point is markedly flatter than E1 (+9.51%) and E5 (+51.54%).

Normalized only for post-hoc comparison, the follow-up contains approximately 14.00% AC1920 and 4.12% TK100. It therefore lies close to the independently motivated coarse `15% acrylic-like + 5% minor tackifier-like` cell. This correspondence is **post-hoc physical consistency with the hypothesis**, not proof that V2 was prospectively registered before the experiment.

## 8. How the current result should be interpreted

The strongest defensible result is:

```text
known formulation/process-state problem
-> evidence-derived candidate hypothesis
-> uncertainty-aware Agent ranking
-> human wet-lab execution
-> physical stability measurement
-> experimental adjudication
-> update next design objective
```

The local rheology directly demonstrates improved thermal-hold stability for the follow-up formulation. The external evidence makes a resin-modification / lower-effective-reactivity hypothesis scientifically plausible, but the current local experiment does not directly measure reaction conversion or identify one molecular mechanism.

## 9. Benchmark chronology

The V2 candidate-space hypothesis was formalized after the current follow-up result was already known. Therefore the current benchmark must be described as a **held-out-result blind replay**.

The evaluated model may see:

```text
original experiments
+ external evidence
+ V2 hypothesis
+ uncertainty-aware actions
```

but not:

```text
current follow-up formulation
current follow-up thermal-hold result
controller-side scoring labels
```

If the full Agent repeatedly ranks candidates near the held-out modifier coordinates, that supports consistency between the evidence-grounded design logic and the physical result. It is not the same as a prospective historical prediction.

Future rounds conducted after V2 is frozen can be genuinely prospective.

## 10. Next design objective

Future selection should treat viscosity magnitude and stability separately:

```text
J = w_eta * L_viscosity
  + w_T   * L_temperature_response
  + w_S   * L_hold_stability
  + w_R   * L_repeatability
  + feasibility penalties
```

A simple hold-stability descriptor is:

```text
SI(T; t0,t1) = [eta(T,t1) - eta(T,t0)] / eta(T,t0)
```

The current measurements establish why such a term is needed. They do not establish a universal numerical threshold for all PUR systems.

## 11. Provenance rule

A claim of **prospective physical validation of an Agent recommendation** requires a recommendation record generated and frozen before the corresponding experiment was inspected.

Without that historical provenance, the current experiment remains valid physical evidence and the V2 benchmark remains valid as a held-out-result replay, but neither should be described as retroactively preregistered.
