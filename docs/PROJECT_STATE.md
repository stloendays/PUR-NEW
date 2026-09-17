# Current project state

## Scientific question

How can a formulation-design workflow for reactive polyurethane hot-melt adhesives remain useful when rheology depends not only on composition, but also on reaction history, time at temperature and preparation perturbation?

## Current answer

Treat the experimental object as a **formulation-process state**, keep uncertainty decomposed, let the Agent recommend the next test under that uncertainty, and let a human-executed wet-lab experiment adjudicate the recommendation.

## Canonical evidence chain

```text
measured formulation + process evidence
-> construct design state
-> derive temperature / hold / repeatability descriptors
-> decompose uncertainty
-> generate admissible candidate states
-> Agent recommends performance / robustness / uncertainty probe
-> freeze recommendation and criterion
-> human wet-lab execution
-> separate experimental adjudication record
-> update response + uncertainty state
-> next design round
```

The detailed contract is in `WORKFLOW.md`.

## Key experimental observations

- E1 at 120 °C: +9.51% viscosity drift from 15 to 60 min.
- E5 at 120 °C: +51.54% over the same interval.
- Follow-up repeat 1: -0.16% from 15 to 60 min.
- Follow-up repeat 2: +3.04% from 15 to 60 min.
- Follow-up mean profile: approximately +1.47%.

On the matched 15-60 min window, the absolute mean-profile drift of the follow-up point is approximately 6.45x smaller than E1 and 34.98x smaller than E5. These are descriptive stability-gain ratios, not significance tests.

## Agent contribution

The Agent contribution is now defined at three levels:

```text
1. state representation
   formulation + process history + evidence gaps

2. uncertainty-aware decision
   measurement + repeatability + process-history + extrapolation + evidence-coverage uncertainty

3. recommendation
   performance candidate / robustness probe / uncertainty probe / abstain
```

The Agent does not receive credit for physical execution. The wet-lab result is an independent physical adjudicator.

## Workflow infrastructure now ready

- `configs/workflow.json` — machine-readable workflow policy;
- `schemas/design_state.schema.json` — canonical formulation-process state;
- `schemas/agent_recommendation.schema.json` — immutable pre-result recommendation;
- `schemas/experiment_adjudication.schema.json` — separate post-result physical adjudication;
- `docs/UNCERTAINTY_MODEL.md` — decomposed uncertainty contract;
- `docs/AGENT_EVALUATION.md` — how the final experiment evaluates the recommendation;
- clean formulation, temperature-sweep and thermal-hold tables.

## One provenance item still matters

To use the strongest wording — **prospective physical validation of an Agent recommendation** — the repository still needs the timestamped recommendation record generated before the corresponding follow-up measurement was inspected.

If that historical trace cannot be recovered, the experiment remains valid physical evidence and the paper should use **Agent-guided closed-loop validation** rather than retrospective preregistration language.

## Immediate next implementation work

1. recover the historical recommendation provenance if it exists;
2. build the deterministic state/descriptor generator from the clean CSV tables;
3. implement the recommendation runner against the schemas and `workflow.json`;
4. write immutable recommendation records and separate adjudication records for future rounds;
5. render Figures 1-4 directly from the clean tables and workflow records;
6. draft the paper around the sequence: state -> uncertainty -> recommendation -> human experiment -> adjudication -> update.
