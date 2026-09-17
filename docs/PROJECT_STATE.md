# Current project state

## Scientific question

How can a formulation-design workflow for reactive polyurethane hot-melt adhesives remain useful when rheology depends not only on composition, but also on reaction history, time at temperature and preparation perturbation?

## Current answer

Treat formulation and process state together, let the Agent reason over the resulting uncertainty, and judge the Agent by a human-executed experiment rather than by whether it can physically operate laboratory equipment.

## Evidence chain

```text
Local formulation design
-> temperature-dependent rheology
-> preparation/run sensitivity
-> 120 C thermal-hold instability
-> uncertainty-aware follow-up recommendation
-> human wet-lab execution
-> repeated near-flat hold response
-> stability-aware next design objective
```

## Key experimental observations

- E1 at 120 °C: +9.51% viscosity drift from 15 to 60 min.
- E5 at 120 °C: +51.54% over the same interval.
- Follow-up repeat 1: -0.16% from 15 to 60 min.
- Follow-up repeat 2: +3.04% from 15 to 60 min.
- Follow-up mean profile: approximately +1.47%.

## Agent contribution

The Agent's scientific contribution is **recommendation under uncertainty**:

```text
known formulation state
+ known process-state variables
+ observed variability
-> uncertainty / robustness assessment
-> recommended test point
```

The laboratory operator then prepares and measures the sample. The experiment is the physical adjudicator.

## What is already ready

- clean formulation table;
- temperature-sweep data;
- thermal-hold data;
- coherent experimental interpretation;
- Agent role definition;
- recommendation/adjudication schema;
- manuscript-facing result order and figure plan.

## One provenance item still needed

To use the strongest wording — **prospective physical validation of an Agent recommendation** — attach the timestamped Agent recommendation generated before the corresponding follow-up measurement was inspected.

If that historical trace cannot be recovered, keep the experimental conclusion unchanged but describe the final stage as an Agent-guided / closed-loop follow-up rather than a preregistered prospective test.

## Immediate next work

1. recover or reconstruct the immutable recommendation provenance without rewriting chronology;
2. generate publication-quality Figures 1-4 from the clean data tables;
3. draft Abstract, Methods, Results and Discussion directly from this evidence chain;
4. define the next stability-aware design state so reaction history, hold time and preparation perturbation become explicit Agent inputs.