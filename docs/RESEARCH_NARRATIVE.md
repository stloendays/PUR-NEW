# Research narrative

## 1. Problem definition

The project is not framed as a static composition-to-viscosity regression problem. In reactive polyurethane hot-melt adhesives, the measured response depends on both **formulation** and **process state**.

```text
x_chem = formulation variables
z_proc = reaction history, thermal holding time, preparation / realization perturbation
```

Conceptually:

```text
y = rheology(x_chem, z_proc) + experimental uncertainty
```

The practical objective is not merely to hit one viscosity value. It is to identify formulation-process states whose rheology remains useful and sufficiently stable under realistic processing history.

## 2. Original experimental design

The local chemistry is based on:

- PPG2000;
- STEPANPOL PDP-70;
- 4,4'-MDI.

The original five-point design separates two local axes:

1. **stoichiometric axis** — E1/E2/E3 change NCO:OH from 1.70 to 1.90 at a 50/50 PPG2000/PDP-70 ratio;
2. **composition axis** — E4/E5 change the PPG2000/PDP-70 ratio around the 50/50 point at NCO:OH = 1.80.

E2 is therefore the centre of the original local design.

## 3. Physical/model findings establish the state-aware design theory

The 80-130 C measurements decrease monotonically with temperature for every recorded complete sweep, but nominally identical formulations can occupy very different absolute viscosity levels across recorded realizations.

The stronger statistical result is that much of this variation behaves as a state-specific viscosity-scale shift superimposed on a comparatively transferable local thermal-response shape:

```text
ln eta_r(T) = alpha_r + g(T) + epsilon
```

where `alpha_r` is realization/state specific and `g(T)` is shared within the present local chemistry family.

Formal model comparison gives approximately:

```text
formulation-only R2 ~= 0.895
state-shift shared-shape R2 ~= 0.998
```

and held-temperature multiplicative error improves from about `1.406x` to `1.055x`.

A stricter leave-one-realization-out test gives roughly `1.60x` error for formulation identity + temperature, whereas one state-specific anchor reduces the error to approximately `1.065-1.098x` for eligible E1/E2 realizations.

The corresponding design principle is:

> **composition defines the chemical formulation, but the experimentally realized rheological state must also be represented explicitly.**

The 120 C hold experiment establishes a second design principle. E1 increases by 9.51% from 15 to 60 min, while E5 increases by 51.54% over the same interval; by 90 min the increases are 16.85% and 93.08%, respectively.

The local apparent temperature-sensitivity descriptor is comparatively concentrated, whereas hold-time drift changes strongly with formulation. The project therefore treats temperature response and thermal-hold stability as:

> **distinct, differently tunable rheological coordinates**

rather than reducing rheology to one static viscosity target.

These physical and model findings are upstream of the Agent. They establish the state-aware design theory first.

## 4. External evidence defines the chemistry search rationale

The next question is why a resin-modified candidate family should enter the search space.

Independent external evidence supports:

```text
acrylic-like modifier region: approximately 15-25%
minor tackifier-like region: approximately 0-10%
```

with additional directional evidence that acrylic functionality/effective reactive-group density can affect hot-hold viscosity stability.

The mechanistic interpretation remains bounded: external analogues justify testing resin identity and functionality, but do not prove one molecular pathway for AC1920/TK100.

## 5. Agent recommendation before the validation result

After the state-aware problem had been established, the Agent was used as a decision layer over the available pre-result evidence.

The research team confirms the following historical order:

```text
state-aware physical/model findings
+ pre-result local evidence
+ external formulation evidence
-> Agent recommendation
-> candidate + rationale frozen
-> human experiment
-> wet-lab adjudication
```

The target validation result was not available to the Agent when the recommendation was made.

The formulation stored internally with `formulation_id = F1` should be referred to in the manuscript as the:

> **Agent-selected validation formulation**

Its source-reported parts basis is:

| PPG2000 | PDP-70 | AC1920 | TK100 | MDI |
|---:|---:|---:|---:|---:|
| 39.60 | 39.60 | 17 | 5 | 20.19 |

The Agent does not synthesize material or operate rheology hardware. The recommendation is a decision that must survive human execution and physical measurement.

## 6. Human wet-lab execution and physical adjudication

After the recommendation had been selected/frozen, the human experimental team prepared and tested the formulation.

Two repeated 120 C hold measurements give:

| time | repeat 1 | repeat 2 | mean |
|---:|---:|---:|---:|
| 15 min | 1230 | 1281 | 1255.5 |
| 30 min | 1189 | 1260 | 1224.5 |
| 45 min | 1203 | 1289 | 1246.0 |
| 60 min | 1228 | 1320 | 1274.0 |

The corresponding 15->60 min drifts are:

```text
repeat 1: -0.16%
repeat 2: +3.04%
mean profile: approximately +1.47%
```

Compared on the matched 15-60 min interval, the Agent-selected validation formulation is markedly flatter than E1 (+9.51%) and E5 (+51.54%).

The experimental result is therefore interpreted as **physical support for the pre-result Agent recommendation with respect to the stated thermal-hold stability objective**.

It does not by itself prove that stabilization arises from one specific reaction mechanism.

## 7. Provenance status

The research team confirms that the Agent recommendation preceded knowledge of the corresponding validation result.

However, the current GitHub repository does not yet contain the original contemporaneous freeze artifact. This distinction must remain explicit:

```text
author-confirmed historical chronology
!=
repository timestamp proof
```

`docs/EXPERIMENTAL_CHRONOLOGY.md` records the confirmed order of work. If an older raw chat, notebook, message, commit, or recommendation record is recovered later, it should be archived under `records/` without changing its original metadata.

## 8. Relationship to the V2 12-candidate grid

The current repository contains a later formalized V2 candidate-space abstraction:

```text
acrylic-like = {0, 15, 20, 25}%
minor tackifier-like = {0, 5, 10}%
```

The grid is valuable because it makes the evidence-constrained chemistry region explicit, reproducible, and benchmarkable.

But the paper should distinguish two provenance statements:

```text
Agent-selected validation formulation was recommended before its result was known
-> author-confirmed historical chronology

current exact V2 4x3 software grid existed in its present form before that experiment
-> not established by the current repository
```

Therefore the V2 grid is best treated as a reproducible candidate-space/benchmark formalization and as the basis for future prospective rounds, rather than as the only evidence that the historical recommendation was prospective.

## 9. Benchmark role

The V2 held-out-result replay remains useful as a **secondary benchmark**.

It asks whether an evaluated Agent, when the validation formulation/outcome is hidden, preferentially ranks candidates in a compatible acrylic/tackifier region using the formalized evidence stack.

This benchmark evaluates reproducibility, evidence use, ablations, and robustness. It is not the primary historical chronology claim.

The primary validation chain is already:

```text
physical/model findings
-> state-aware theory
-> pre-result Agent recommendation
-> freeze
-> human experiment
-> physical adjudication
```

## 10. Manuscript-level interpretation

The strongest overall narrative is:

> **The physical/model findings first established a state-aware rheological design problem. The Agent then selected a validation formulation without access to its later experimental outcome. Human wet-lab execution subsequently produced a low-drift response that supported the recommendation with respect to thermal-hold stability.**

This is stronger and more scientifically coherent than presenting the experiment as an input that the Agent later appears to predict.

## 11. Next design objective

Future selection should continue to treat viscosity magnitude and stability separately:

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
