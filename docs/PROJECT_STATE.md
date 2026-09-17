# Current project state

## Scientific question

How can a formulation-design workflow for reactive polyurethane hot-melt adhesives remain useful when rheology depends not only on composition, but also on reaction history, time at temperature and experimental/process realization?

## Current answer

Treat the experimental object as a **formulation-process state**, quantify state-dependent rheology before the Agent acts, let the Agent recommend a formulation under structured uncertainty, and use human wet-lab execution as an independent physical adjudicator.

## Canonical evidence chain

```text
original measured formulation + process evidence
-> state-shift / thermal-response analysis
-> state-aware design theory
-> evidence-grounded Agent recommendation
-> freeze validation formulation + rationale + criterion
-> human wet-lab execution
-> separate physical adjudication
-> update response + uncertainty state
-> next design round
```

## Main physical/model findings

### Local state-shift structure

A compact local representation is:

```text
ln eta_r(T) = alpha_r + g(T) + epsilon
```

with a realization/state-specific viscosity scale `alpha_r` and a shared local thermal-response shape `g(T)`.

Key model comparisons:

```text
formulation-only R2 ~= 0.895
state-shift shared-shape R2 ~= 0.998
held-temperature error: ~1.406x -> ~1.055x
strict unseen-realization formulation-only error: ~1.60x
one-point state calibration error: ~1.065-1.098x
```

### Distinct rheological coordinates

```text
mean local apparent E_eta = 41.87 +/- 2.27 kJ/mol
CV = 5.4%
```

while original 120 C hold drift differs strongly:

```text
E1 15->60 min: +9.51%
E5 15->60 min: +51.54%
```

Temperature response and thermal-hold stability are therefore treated as **distinct, differently tunable rheological coordinates**.

## Agent-selected validation formulation

The current validation formulation is stored internally as `F1` but should be called the **Agent-selected validation formulation** in manuscript prose.

```text
PPG2000 = 39.60
PDP-70  = 39.60
AC1920  = 17
TK100   = 5
MDI     = 20.19
```

The research team confirms that the Agent selected this formulation before the corresponding wet-lab outcome was known to the Agent.

Human experimental execution then produced:

```text
15->60 min repeat 1: -0.16%
15->60 min repeat 2: +3.04%
mean profile:        +1.47%
```

The measured response is substantially flatter than E1 and E5 over the matched window and therefore supports the recommendation with respect to thermal-hold stability.

## Provenance status

The historical sequence is author-confirmed, but the current repository does not yet contain the original contemporaneous recommendation/freeze artifact.

Therefore:

```text
author-confirmed prospective chronology = supported by project history
original timestamped freeze provenance = not yet recovered in this repository
```

`docs/EXPERIMENTAL_CHRONOLOGY.md` records this distinction explicitly.

## V2 candidate-space role

The current V2 `4 x 3` grid is a later reproducible formalization:

```text
acrylic-like = {0, 15, 20, 25}%
minor tackifier-like = {0, 5, 10}%
```

It is useful for replay benchmarking, ablation, evidence tracing and future prospective design rounds.

It should not be presented as the historical freeze artifact unless older provenance is recovered.

## Agent contribution

The Agent contribution is defined at three levels:

```text
1. state representation
   formulation + process realization + evidence gaps

2. uncertainty-aware decision
   measurement + repeatability + process-history + extrapolation + evidence-coverage uncertainty

3. recommendation
   selected formulation + alternatives + rationale + criterion / abstention
```

The Agent does not receive credit for physical execution. The wet-lab result is the independent adjudicator.

## Infrastructure now implemented

- `configs/workflow.json` — machine-readable workflow policy;
- `configs/formulation_priors.json` — V2 evidence-constrained candidate formalization;
- `schemas/design_state.schema.json` — canonical formulation-process state;
- `schemas/agent_recommendation.schema.json` — recommendation structure;
- `schemas/experiment_adjudication.schema.json` — separate physical adjudication;
- `scripts/build_evidence_state.py` — deterministic evidence-state generator;
- `scripts/statistical_analysis.py` — formal state-aware model analysis;
- `scripts/statistical_robustness.py` — robustness and unseen-realization checks;
- `scripts/master_curve_collapse.py` — model-light master-curve collapse;
- `scripts/build_candidate_set.py` — reproducible V2 grid generator;
- `scripts/run_agent_recommendation.py` — Agent recommendation runner;
- `docs/EXPERIMENTAL_CHRONOLOGY.md` — author-confirmed chronology and provenance boundary.

## Immediate next work

1. recover/archive the original pre-result Agent recommendation record if it can be found;
2. finalize Figures 1-5 using the current chronology;
3. write the Results section around state-shift structure -> distinct stability response -> Agent recommendation -> wet-lab adjudication;
4. keep V2 replay/ablation as secondary Agent benchmarking rather than the sole validation claim;
5. finish the remaining experimental conclusion/metadata checks without overstating mechanism.
