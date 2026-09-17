# PUR-NEW

## Uncertainty-aware, Agent-guided formulation design for reactive polyurethane hot-melt adhesives

PUR-NEW is organized around a single experimental question:

> How should a reactive PUR formulation be selected when the measured rheology depends on both composition and process history?

The project treats a test point as a **formulation-process state**, not composition alone:

```text
formulation state
+ reaction / preparation history
+ thermal hold state
+ observed variability
-> rheological response + structured uncertainty
```

## Canonical workflow

```text
1. ingest measured formulation + rheology evidence
2. construct formulation-process state
3. derive temperature / hold / repeatability descriptors
4. decompose uncertainty
5. generate admissible candidate states
6. Agent recommends the next test point
7. freeze recommendation + criterion + provenance
8. human operator executes the wet-lab experiment
9. experiment adjudicates the recommendation
10. update response evidence and uncertainty for the next round
```

The Agent is an **uncertainty-aware scientific recommender**. It does not physically prepare samples or operate the instrument. Its scientific value is judged by whether the recommendation remains useful after human execution.

The full contract is in [`docs/WORKFLOW.md`](docs/WORKFLOW.md).

## What uncertainty means here

The workflow keeps five sources separate:

```text
measurement
repeatability
process history
extrapolation
evidence coverage
```

This prevents a single confidence score from hiding why a recommendation is fragile. See [`docs/UNCERTAINTY_MODEL.md`](docs/UNCERTAINTY_MODEL.md).

The Agent may recommend one of three useful experiment types:

```text
performance_candidate  -> seek a practically strong formulation state
robustness_probe       -> test survival under process perturbation
uncertainty_probe      -> reduce the most consequential evidence gap
```

It may also abstain when the evidence does not support a defensible recommendation.

## Current experimental system

The local system uses **PPG2000 / STEPANPOL PDP-70 / 4,4'-MDI**. The original local design varies NCO:OH and PPG2000/PDP-70 ratio.

The measured temperature sweeps decrease monotonically with temperature, while repeated realizations show that absolute viscosity can depend strongly on preparation/run history. Thermal holding makes the practical stability problem especially clear.

At 120 °C:

| Formulation | 15 min | 60 min | 90 min | 15->60 drift | 15->90 drift |
|---|---:|---:|---:|---:|---:|
| E1 | 708.7 | 776.1 | 828.1 | +9.51% | +16.85% |
| E5 | 2210 | 3349 | 4267 | +51.54% | +93.08% |

The follow-up formulation is reported on the source parts basis:

| PPG2000 | PDP-70 | AC1920 | TK100 | MDI |
|---:|---:|---:|---:|---:|
| 39.60 | 39.60 | 17 | 5 | 20.19 |

Two repeated 120 °C hold measurements give 15->60 min changes of **-0.16%** and **+3.04%**; the mean profile changes by about **+1.47%**.

The direct experimental conclusion is **rheological stabilization over the matched hold window**. The explanation that the added resin components reduce the effective reactive fraction remains a formulation rationale rather than direct molecular-kinetic proof.

## Repository structure

```text
PUR-NEW/
├─ README.md
├─ configs/
│  └─ workflow.json                    # machine-readable decision policy
├─ docs/
│  ├─ WORKFLOW.md                      # canonical closed-loop workflow
│  ├─ UNCERTAINTY_MODEL.md             # uncertainty decomposition
│  ├─ PROJECT_STATE.md                 # current state and next work
│  ├─ RESEARCH_NARRATIVE.md            # scientific narrative
│  ├─ AGENT_ROLE.md                    # Agent evidence contract
│  ├─ EXPERIMENTAL_EVIDENCE.md         # executed measurements
│  └─ MANUSCRIPT_PLAN.md               # paper-facing structure
├─ data/
│  ├─ README.md
│  ├─ formulations.csv
│  ├─ temperature_sweeps.csv
│  └─ thermal_hold.csv
└─ schemas/
   ├─ design_state.schema.json          # formulation + process + evidence state
   └─ agent_recommendation.schema.json  # frozen recommendation + adjudication
```

## Paper-level claim

> Known process-state variables such as reaction history, thermal holding time and preparation perturbation should be represented explicitly in reactive-PUR formulation design. An uncertainty-aware Agent can use those variables to recommend which formulation-process state should be tested, while human-executed wet-lab measurements provide the final physical adjudication and update the next design round.

## Claim boundary

The repository does not claim that the Agent autonomously operates a laboratory, that rheology alone proves a specific molecular reaction pathway, or that a recommendation written after seeing a result is prospective.

A manuscript claim of **prospective physical validation of an Agent recommendation** requires a timestamped, frozen recommendation record created before the corresponding result was inspected. Without that provenance, the same experiment remains valid as **Agent-guided closed-loop validation**.
