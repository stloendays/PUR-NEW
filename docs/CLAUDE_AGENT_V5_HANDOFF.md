# Claude handoff: implement Agent V5 exactly against the frozen protocol

Implement Agent V5 in this repository. Read these files first, in this order:

1. `configs/agent_v5_comparison_protocol.json` — authoritative experimental contract.
2. `docs/AGENT_V5_CHEMISTRY_GATE_PROTOCOL.md` — scientific rationale and implementation invariants.
3. `scripts/run_agent_v4.py` — predecessor API runtime.
4. `configs/agent_v4.json` — predecessor architecture.
5. `src/pur_new/agent_v3.py` and `src/pur_new/actions.py` — tool execution and planner action validation.
6. `src/pur_new/chemistry_tools.py` — shared-shape applicability tool.
7. `src/pur_new/scientific_tools.py` — chemistry-audited rheology summary.
8. `src/pur_new/voi.py` — experiment-card and VOI implementation.
9. `configs/hypothesis_registry.json`
10. `configs/measurement_catalog.json`

## Required implementation

Create a prospective V5 runtime; do not modify frozen V4 records.

The V5 API architecture remains:

`Planner -> deterministic tools -> Proposer -> Skeptic -> Robustness Adjudicator -> Judge -> Freeze`

No additional LLM role is allowed.

### Mandatory science flow

Before experiment ranking:

1. force execution of `get_chemistry_audited_rheology_summary()`;
2. compute `assess_shared_shape_applicability(candidate)` for every candidate relevant to an experiment card;
3. convert the result into measurement-card admissibility;
4. remove or mark inadmissible cards before VOI ranking;
5. pass the audited admissibility trace, admissible VOI ranking and tool trace to all downstream model stages.

### Hard gate

Unless a versioned prior direct sweep has verified transferability for the same chemistry:

- unmodified local-family candidate + `M-ANCHOR`: allowed;
- chemistry-shifted candidate + `M-ANCHOR`: blocked;
- chemistry-shifted candidate + `M-SWEEP`: allowed;
- `M-HOLD-120`: allowed if otherwise valid;
- `M-REPEAT`: allowed if otherwise valid.

Do not implement the gate as a prompt suggestion or a small VOI penalty. It is deterministic admissibility and the LLM cannot override it.

## Primary experiment

Implement two V5 modes from the same code path:

- `V5_NO_GATE`
- `V5_FULL`

They must use identical prompts, model endpoint, evidence, candidate lattice, hypothesis registry, measurement catalog, VOI weights and run settings. The only intended difference is gate enforcement.

Support 10 declared runs per primary arm by default, but make run count configurable. Never silently replace failed/invalid runs; preserve attempted/completed/committed/abstained/invalid denominators.

## Historical V4

Do not rewrite V4. The existing frozen V4 series is the historical reference. If you implement an optional same-model V4 replay, write it into a new clearly labeled results directory and describe it as diagnostic.

## Output contract

Every V5 run must save:

- `deliberation.json`
- `recommendation.json`
- `admissibility_audit.json`
- `experiment_cards.json`
- model/token/latency usage
- all hashes needed to reproduce the run

The comparison runner must write:

- `cross_arm_runs.csv`
- `cross_arm_summary.json`
- `comparison_manifest.json`

Do not write V5 numerical results into `manuscript/MAIN_TEXT_V5.md` or `manuscript/SUPPLEMENTARY_INFORMATION_V5.md` yet.

## Tests that must exist

At minimum test:

1. resin-modified + M-ANCHOR is blocked without verified sweep;
2. unmodified local-family + M-ANCHOR remains allowed;
3. resin-modified + M-SWEEP remains allowed;
4. blocked cards never enter the VOI ranked set;
5. a model output naming a blocked experiment is rejected at freeze;
6. V5_NO_GATE and V5_FULL use byte-identical candidate/hypothesis/measurement inputs;
7. held-out F1 identity/outcome cannot enter planner or downstream payloads;
8. mandatory chemistry-audited summary is always executed;
9. V4 files and frozen result directories remain unchanged.

## GitHub Actions

Add a normal CI workflow that does not require an API key and checks schemas, unit tests, blindness and comparison parity.

If you add an API workflow, make it manual (`workflow_dispatch`) and require repository secrets. It must never run paid API calls automatically on every push.

## Completion report

When finished, report:

- files changed;
- exact implementation of the gate;
- tests added and results;
- whether existing CI remains green;
- any protocol ambiguity you encountered;
- the command to run V5_NO_GATE and V5_FULL;
- the command to produce the cross-arm comparison.

Do not claim V5 is better before the comparison runs exist.
