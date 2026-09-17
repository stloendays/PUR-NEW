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

## 4. Physical/model findings establish the state-aware design theory

The 80-130 C measurements decrease monotonically with temperature for every recorded full sweep. However, nominally identical E2 measurements show large differences in absolute viscosity level across recorded realizations.

The stronger statistical result is that much of this variation behaves as a state-specific viscosity-scale shift superimposed on a comparatively transferable local thermal-response shape:

```text
ln eta_r(T) = alpha_r + g(T) + epsilon
```

where `alpha_r` is realization/state specific and `g(T)` is shared within the present local chemistry family.

A one-point anchor from a held-out realization reconstructs the remaining measured temperature curve substantially better than formulation identity alone. This establishes a positive design principle:

> **composition defines the chemical formulation, but the experimentally realized rheological state must also be represented explicitly.**

The 120 C hold experiment establishes the second design principle. E1 increases by 9.51% from 15 to 60 min, while E5 increases by 51.54% over the same interval. By 90 min the increases are 16.85% and 93.08%, respectively.

The local apparent temperature-sensitivity descriptor is comparatively concentrated, whereas hold-time drift changes strongly with formulation. The project therefore treats temperature response and thermal-hold stability as **distinct, differently tunable rheological coordinates** rather than reducing rheology to a single static viscosity target.

Together, these physical and modeling findings establish the state-aware design theory **before the Agent is asked to select a new experimental candidate**.

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

The exact historical F1 follow-up recipe is not encoded as a discrete candidate.

## 6. Agent role: prospective recommendation after theory, before outcome

The Agent is not a robotic laboratory controller. It is a **decision layer** operating over:

```text
state-aware physical/model findings
+ local measured evidence
+ deterministic response descriptors
+ structured uncertainty
+ candidate-space hypothesis
+ external database/literature evidence
+ finite admissible candidates
```

The scientific chronology is explicit:

```text
physical/model findings
-> state-aware design theory
-> admissible candidate space
-> Agent recommendation while blinded to the corresponding wet-lab outcome
-> frozen candidate + rationale + falsifiable criterion
-> human experimental execution
-> independent physical adjudication
```

For the prospective validation round, the Agent is not allowed to see the corresponding target experiment result before freeze. It must record why the candidate was selected, what alternatives were considered, what uncertainty remains, and what experimental result would count as support or failure.

This is essential: the later wet-lab result is not an input used to construct the recommendation. It is the external physical test of a decision already frozen.

See `docs/PROSPECTIVE_VALIDATION_PROTOCOL.md`.

## 7. Human wet-lab execution and adjudication

After the recommendation record is frozen, the human researcher / experimental team performs the synthesis and rheology measurement.

Experimental deviations, missing process metadata and protocol changes are recorded separately from the original recommendation. The Agent does not silently revise the candidate after seeing the outcome.

Only after measurement is the wet-lab result compared with the frozen criterion. The outcome is classified as:

```text
supported
partially supported
not supported
or inconclusive because of execution / measurement uncertainty
```

This makes both positive and negative experiments scientifically useful: a positive result supports the recommendation, while a negative result falsifies or weakens it and updates the next design state.

## 8. Historical F1 physical result

The historical follow-up formulation uses the source-reported parts basis:

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

Compared on the same 15-60 min interval, the historical follow-up point is markedly flatter than E1 (+9.51%) and E5 (+51.54%).

Normalized only for post-hoc comparison, it contains approximately 14.00% AC1920 and 4.12% TK100. It therefore lies close to the independently motivated coarse `15% acrylic-like + 5% minor tackifier-like` cell.

This historical result is useful physical evidence and a retrospective benchmark anchor. It should not be confused with the separate prospective new-candidate validation cycle described above.

## 9. Retrospective replay versus prospective validation

Two evaluation modes coexist and must remain clearly separated.

### 9.1 Retrospective F1 / V2 held-out replay

The formal V2 candidate-space hypothesis was documented after the historical F1 result was already known. Therefore the F1 benchmark is described as a **held-out-result blind replay**.

The evaluated model may see:

```text
original experiments
+ external evidence
+ V2 hypothesis
+ uncertainty-aware actions
```

but not:

```text
historical F1 formulation/outcome
controller-side scoring labels derived from that outcome
```

This tests whether the evidence-grounded design logic is consistent with the already observed physical result. It is not a prospective historical prediction.

### 9.2 Prospective new-candidate validation

For a new validation round, the chronology is different and stronger:

```text
state-aware theory already established
-> Agent sees no corresponding future wet-lab result
-> recommendation and criterion frozen
-> human experiment performed
-> result released only for adjudication
```

This is the chronology that supports a prospective Agent-validation claim.

## 10. Manuscript-level interpretation

The strongest overall narrative is:

```text
physical/model findings
-> state-aware design theory
-> evidence-derived candidate hypothesis
-> blinded Agent recommendation
-> frozen candidate + criterion
-> human wet-lab execution
-> independent experimental support / rejection
-> update next design objective
```

The paper should therefore not be framed as "an Agent generated a formulation and we later rationalized it." The intended claim is the reverse:

> **the physical/model findings first define a scientifically constrained state-aware design problem; the Agent then makes a falsifiable recommendation within that problem before the corresponding experimental outcome is known to it.**

## 11. Next design objective

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

## 12. Provenance rule

For every prospective validation round, the repository should preserve an immutable recommendation record generated before the corresponding wet-lab outcome is made available to the Agent.

That record should contain:

- candidate identity and formulation-process state;
- alternatives considered;
- evidence / Action trace;
- structured uncertainty;
- pre-result acceptance or falsification criterion;
- freeze timestamp and provenance.

The later physical result is stored separately and linked to the frozen recommendation only during adjudication.
