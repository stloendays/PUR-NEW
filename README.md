# PUR-NEW

## Uncertainty-aware, Agent-guided formulation design for reactive polyurethane hot-melt adhesives

This repository contains the **current experimental story only**. It is intentionally rebuilt as a clean project and does not carry over historical synthetic candidate-space benchmarks or legacy recovery tasks.

## Research question

A reactive polyurethane hot-melt adhesive cannot be described adequately by formulation composition alone. The measured rheology also depends on process state, especially:

- reaction history;
- thermal holding time;
- preparation / batch perturbation.

The design problem is therefore treated as

```text
formulation variables + process-state variables -> rheological response + uncertainty
```

The scientific role of the Agent is deliberately limited and auditable:

```text
existing evidence
-> quantify uncertainty / robustness
-> recommend a formulation or measurement point
-> freeze the recommendation trace
-> human operator prepares and measures the sample
-> physical experiment adjudicates the recommendation
-> feed the new stability information into the next design round
```

The Agent **does not physically operate the laboratory**. Its value is evaluated by whether its recommendations remain useful when they are executed by a human in the wet lab.

## Current experimental evidence

The local experimental system uses **PPG2000 / STEPANPOL PDP-70 / 4,4'-MDI**. The original five-point design varies NCO:OH and the PPG2000/PDP-70 blend ratio. Temperature sweeps show the expected monotonic viscosity decrease with temperature, but the more important result is the sensitivity to preparation history and time at temperature.

At 120 °C, the original formulations show substantial viscosity build-up during thermal holding:

| Formulation | 15 min | 60 min | 90 min | 15->60 drift | 15->90 drift |
|---|---:|---:|---:|---:|---:|
| E1 | 708.7 | 776.1 | 828.1 | +9.51% | +16.85% |
| E5 | 2210 | 3349 | 4267 | +51.54% | +93.08% |

A follow-up formulation uses the source-reported parts basis:

| PPG2000 | PDP-70 | AC1920 | TK100 | MDI |
|---:|---:|---:|---:|---:|
| 39.60 | 39.60 | 17 | 5 | 20.19 |

Two repeated 120 °C hold measurements of this formulation gave 15->60 min viscosity changes of **-0.16%** and **+3.04%**; the mean profile changed by about **+1.47%**. This is the central physical result: the recommended follow-up point is far more stable over the matched holding window than the unstable original cases.

The experiment directly supports **rheological stabilization**. The interpretation that AC1920/TK100 reduce the effective reactive fraction is retained as a formulation rationale, not as direct proof of a specific reaction mechanism.

## Repository structure

```text
PUR-NEW/
├─ README.md
├─ docs/
│  ├─ RESEARCH_NARRATIVE.md      # complete scientific logic
│  ├─ AGENT_ROLE.md              # what the Agent can and cannot claim
│  ├─ EXPERIMENTAL_EVIDENCE.md   # executed measurements and interpretation
│  └─ MANUSCRIPT_PLAN.md         # paper-facing structure and figures
├─ data/
│  ├─ README.md
│  ├─ formulations.csv
│  ├─ temperature_sweeps.csv
│  └─ thermal_hold.csv
└─ schemas/
   └─ agent_recommendation.schema.json
```

## Core claim

> Known process-state variables such as reaction history, thermal holding time and preparation perturbation should enter the formulation-design loop explicitly. An uncertainty-aware Agent can recommend which formulation state is worth testing, while human-executed wet-lab measurements provide the final physical adjudication.

## Claim boundary

This repository does **not** claim that the Agent autonomously performs synthesis, that the current data prove a molecular kinetic mechanism, or that a post-result recommendation can be relabelled as prospective. Any prospective manuscript claim must be backed by a timestamped pre-result recommendation trace.