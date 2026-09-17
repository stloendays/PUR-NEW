# Agent runtime architecture

## Design principle

The Agent should not be trusted with raw arithmetic that can be made deterministic, and it should not be given laboratory actuation authority that it does not possess.

The runtime is therefore split into five layers.

```text
L0  raw evidence
L1  deterministic scientific descriptors
L2  Agent reasoning over state + uncertainty
L3  immutable recommendation freeze
L4  human wet-lab execution + physical adjudication
```

## L0 — Raw evidence

Inputs are the versioned formulation and rheology tables under `data/`.

Raw evidence is never overwritten by model output.

## L1 — Deterministic scientific layer

This layer owns numerical facts that can be computed reproducibly, including:

- hold-stability index;
- matched-window hold loss;
- descriptive stability gain;
- replicate CV / max:min spread;
- measured support ranges;
- descriptive `ln(eta)` vs `1/T` fits.

Current implementation:

```text
src/pur_new/metrics.py
scripts/build_evidence_state.py
```

The Agent consumes these outputs instead of recalculating them in free-form language.

## L2 — Agent reasoning layer

The Agent receives:

```text
design state
+ deterministic descriptors
+ uncertainty vector
+ hard constraints
+ candidate states
```

Its responsibilities are limited to:

1. identify the dominant uncertainty source;
2. identify whether the current decision is performance-seeking, robustness-seeking or information-seeking;
3. compare admissible candidates;
4. state which process variables must be controlled or deliberately perturbed;
5. recommend one test point or abstain;
6. state a falsifiable acceptance criterion;
7. explain why alternatives were not selected.

## Allowed logical actions

The Agent may conceptually call read-only scientific operations such as:

```text
get_design_state()
get_measured_support()
get_hold_stability(candidate)
get_repeatability_summary(candidate)
get_uncertainty_vector(candidate)
compare_candidates(candidate_ids)
check_extrapolation(candidate)
check_constraints(candidate)
```

The implementation may expose these as functions, tools or precomputed JSON fields. Numerical truth remains deterministic.

## Forbidden Agent actions

The Agent must not have tools named or behaving like:

```text
prepare_sample()
start_reaction()
set_instrument()
measure_viscosity()
write_experimental_result()
```

unless real laboratory automation is separately introduced and validated in the future.

In the present project, laboratory execution is human.

## L3 — Freeze gate

A recommendation cannot enter the prospective evidence chain until it passes the freeze gate.

Required checks:

```text
selected candidate is explicit
process state is explicit or missingness is declared
uncertainty vector is present
alternatives are recorded
acceptance criterion is falsifiable
unsupported extrapolation is flagged
result_inspection_status is recorded
provenance fields are populated where available
```

If any required scientific field is unresolved, the correct action is `abstain` or `human_review`, not silent completion.

After the gate, the record is written using `schemas/agent_recommendation.schema.json` and is immutable.

## L4 — Human execution and adjudication

A human operator prepares and measures the sample. The resulting record is stored separately using `schemas/experiment_adjudication.schema.json`.

The adjudicator compares the physical result with the **criterion as frozen**, not with a criterion rewritten after measurement.

## Why this architecture matters scientifically

This split makes three claims independently testable:

```text
1. Are the deterministic descriptors reproducible?
2. Does the Agent make a defensible recommendation under uncertainty?
3. Does the real experiment support that recommendation?
```

A failure in one layer does not get hidden inside another.

## Recommended next runtime implementation

The next code layer should expose the deterministic evidence state to the Agent through a small read-only toolbox and require schema-valid JSON output. The runner should then:

```text
build evidence state
-> hash input state
-> call Agent
-> validate recommendation
-> freeze JSON + hashes
-> stop
```

No experimental result should be visible to that process for a prospective round. The later adjudication should run as a separate command on the frozen recommendation plus the new wet-lab record.
