# Research narrative

## 1. Problem definition

The project is not framed as a static composition-to-viscosity regression problem. In reactive polyurethane hot-melt adhesives, the response observed at the instrument depends on both **formulation** and **process state**.

We therefore separate the design state into two blocks:

```text
x_chem = formulation variables
z_proc = reaction history, thermal holding time, preparation / batch perturbation
```

and treat the measured response conceptually as

```text
y = rheology(x_chem, z_proc) + experimental uncertainty
```

The practical objective is not merely to hit one viscosity value. It is to identify formulations whose rheology remains useful and sufficiently stable under realistic processing history.

## 2. What was known before the experiment

Reaction history, time at temperature and preparation disturbance were already recognized as relevant variables. The scientific gap was that they had not yet been represented explicitly enough in the formulation-selection objective.

The role of the experiment is therefore **not** to discover that process history exists. It is to quantify how strongly the real system responds to those variables and to determine whether an Agent recommendation remains useful after physical execution.

## 3. Local experimental design

The local chemistry is based on:

- PPG2000;
- STEPANPOL PDP-70;
- 4,4'-MDI.

The five-point design separates two local axes:

1. **stoichiometric axis** — E1/E2/E3 change NCO:OH from 1.70 to 1.90 at a 50/50 PPG2000/PDP-70 ratio;
2. **composition axis** — E4/E5 change the PPG2000/PDP-70 ratio at NCO:OH = 1.80.

This gives a compact local experimental neighbourhood rather than an attempt to map the entire formulation universe.

## 4. What the initial measurements show

The 80-130 °C measurements decrease monotonically with temperature for every recorded full sweep. However, nominally identical E2 measurements show large differences in absolute viscosity level across recorded runs. This means that a single deterministic target value is not enough to describe the laboratory system.

The 120 °C hold experiment makes the process-time effect explicit. E1 increases by 9.51% from 15 to 60 min, while E5 increases by 51.54% over the same interval. By 90 min the increases are 16.85% and 93.08%, respectively.

The important conclusion is therefore:

> thermal-hold stability is a formulation-dependent design response, not merely metadata attached to a viscosity measurement.

## 5. Agent role in the design loop

The Agent is not a robotic laboratory controller. It is a **decision layer** operating before physical execution.

Its intended responsibilities are:

```text
represent known process-state variables
-> evaluate uncertainty / robustness
-> compare candidate formulation states
-> recommend the next formulation or measurement point
-> record why the point was selected
```

The human operator then executes the synthesis and rheology measurement. The experimental result is the external physical adjudicator.

This distinction matters: the Agent is evaluated on the quality of its recommendation, not on whether it can manipulate laboratory equipment.

## 6. Follow-up formulation and physical result

The follow-up formulation uses the source-reported parts basis:

| PPG2000 | PDP-70 | AC1920 | TK100 | MDI |
|---:|---:|---:|---:|---:|
| 39.60 | 39.60 | 17 | 5 | 20.19 |

Two repeated 120 °C hold measurements give:

| time | repeat 1 | repeat 2 | mean |
|---:|---:|---:|---:|
| 15 min | 1230 | 1281 | 1255.5 |
| 30 min | 1189 | 1260 | 1224.5 |
| 45 min | 1203 | 1289 | 1246.0 |
| 60 min | 1228 | 1320 | 1274.0 |

The corresponding 15->60 min drifts are -0.16% and +3.04%; the mean profile changes by approximately +1.47%.

Compared on the same 15-60 min interval, the follow-up point is markedly flatter than E1 (+9.51%) and E5 (+51.54%).

## 7. How the result should be interpreted

The strongest defensible result is a **design-loop result**:

```text
known formulation + process-state problem
-> uncertainty-aware recommendation
-> human wet-lab execution
-> physical stability measurement
-> experimental adjudication
-> update the next design objective
```

The rheology directly demonstrates improved thermal-hold stability for the follow-up formulation. A plausible formulation rationale is that adding AC1920/TK100 reduces the effective fraction of reaction-capable material in the original resin/polyol phase, but the present experiment does not directly measure reaction conversion or molecular kinetics.

## 8. Next design objective

Future selection should treat viscosity magnitude and stability separately. A generic objective can be written as

```text
J = w_eta * L_viscosity
  + w_T   * L_temperature_response
  + w_S   * L_hold_stability
  + feasibility penalties
```

A simple hold-stability descriptor is

```text
SI(T; t0,t1) = [eta(T,t1) - eta(T,t0)] / eta(T,t0)
```

The current measurements establish why such a term is needed. They do not yet establish a universal numerical threshold for all PUR systems.

## 9. Provenance rule

If the manuscript describes the final experiment as a **prospective validation of an Agent recommendation**, the repository must contain the recommendation record generated before the corresponding result was inspected. If that record cannot be recovered, the experiment remains valid physical evidence but should be described as an Agent-guided or closed-loop follow-up rather than retroactively preregistered.