# Current project state

## Scientific question

How can reactive-PUR experiments remain scientifically comparable and decision-useful when nominally identical formulations are realized under different preparation, reaction and measurement histories?

## Current answer

Treat the experimental object as a **realization-aware rheological state** rather than a nominal recipe alone. First separate reusable material structure from realization-dependent viscosity displacement; then identify thermal-hold drift as the actionable formulation coordinate; finally let a chemistry-bounded Agent integrate structured local data, external evidence and measurement semantics to choose the next discriminating experiment. Human wet-lab measurement remains the physical adjudicator.

## Canonical evidence chain

```text
real-world experimental realization
-> realization-aware rheological state
-> reusable local thermal-response structure
-> actionable thermal-hold failure coordinate
-> provenance-preserved evidence + chemistry-domain limits
-> deterministic experiment geometry
-> model-mediated experiment selection
-> human wet-lab adjudication
-> updated evidence state
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
formulation-only quadratic R2 ~= 0.8553
state-conditioned quadratic R2 ~= 0.9977
held-temperature error: ~1.423x -> ~1.058x
same-formulation 110 C anchor: 1.824x -> 1.086x at 120-130 C
held-formulation one-point calibration: ~1.06-1.10x pooled
```

### Distinct rheological coordinates

```text
mean local apparent E_eta = 42.05 +/- 2.43 kJ/mol
CV = 5.77%
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

The Agent contribution is downstream of the material analysis:

```text
1. consume the realization-aware evidence state
2. respect chemistry-domain and measurement-admissibility rules
3. integrate local measurements with provenance-preserved external priors
4. choose a formulation x measurement experiment that resolves the open hypothesis
5. commit / abstain under explicit scientific rules
```

The Agent does not receive credit for the state-shift discovery, deterministic chemistry/VOI rules, or physical execution. The wet-lab result is the independent adjudicator.

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
