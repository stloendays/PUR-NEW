# Agent V5 chemistry-domain gate: pre-implementation protocol

## Scientific purpose

Agent V5 is not a larger Agent and does not add more language-model roles. Its purpose is to test whether **material regularities discovered upstream can become executable scientific constraints downstream**.

The scientific order is fixed:

`measured rheology -> discovered local regularity -> external domain test -> deterministic applicability rule -> experiment-card admissibility -> VOI -> model-mediated selection -> freeze`

V4 remains preserved as a historical architecture. V5 is a new prospective runtime.

## What changes from V4

V4 already calls the API through Planner -> Proposer -> Skeptic -> Robustness Adjudicator -> Judge and uses deterministic VOI. Its mandatory upstream tool is the predecessor state-aware rheology summary.

V5 keeps the same five model stages but makes two scientific changes:

1. the mandatory upstream local-science tool becomes `get_chemistry_audited_rheology_summary()`;
2. every candidate-measurement pair is checked against `assess_shared_shape_applicability(candidate)` before VOI ranking.

The second change is a **hard applicability rule**, not extra prompt text.

## Chemistry-domain gate

The gate acts on measurement validity.

For a candidate still inside the audited unmodified PPG2000/PDP70/MDI chemistry family, the discovered shared thermal-response shape may be used as a local interpolation prior. `M-ANCHOR` may therefore remain admissible.

For AC1920-, TK100- or otherwise chemistry-shifted candidates, the shared thermal shape has not yet been established. In that state:

- `M-SWEEP` is admissible and is the direct verification experiment;
- `M-HOLD-120` remains admissible because it directly measures the thermal-hold failure coordinate;
- `M-REPEAT` remains admissible for state-control questions;
- `M-ANCHOR` is **inadmissible before shape verification**.

The LLM may criticize or explain the rule, but it may not override the rule.

## Why V4 versus V5 alone is not a causal gate test

V4 and V5 differ in more than one respect: tool set, prompts and architecture version. Their comparison is scientifically useful as an evolution of the workflow, but it cannot isolate the causal effect of the gate.

The primary controlled comparison is therefore:

`V5_NO_GATE vs V5_FULL`

Both arms must share the same model endpoint, prompts, candidate lattice, measurement catalog, hypothesis registry, evidence profile, VOI weights and run settings. The only intended difference is whether the chemistry-domain gate changes experiment-card admissibility.

The frozen V4 results remain a historical reference. An optional same-model V4 replay may be run as a diagnostic series, but it must not replace the frozen record.

## Primary endpoint

The main question is not whether V5 selects a known or preferred formulation. It is:

> Does the chemistry-aware runtime prevent unsupported measurement shortcuts while preserving or improving the ability of the chosen experiment to discriminate the open material hypotheses?

Primary metrics are:

- unsupported-shortcut rate;
- chemistry-domain violation rate;
- hypothesis discrimination;
- measurement validity;
- attempted/completed/committed/abstained/invalid counts;
- selection entropy.

Distance to the held-out F1 formulation and closeness to future S1C39/S1C41 results are forbidden as primary metrics.

## Implementation invariants

Claude must preserve these invariants:

- do not edit or overwrite frozen V3/V4 runs;
- do not modify the 73-node candidate lattice for the primary comparison;
- do not modify the frozen hypothesis registry for the primary comparison;
- do not modify the four-plan measurement catalog for the primary comparison;
- do not add LLM stages;
- do not give any model payload access to the held-out validation identity or result;
- apply the gate before VOI ranking;
- serialize every gate decision and reason;
- ensure an LLM cannot select an experiment card that deterministic admissibility marked false;
- keep V5 results out of the canonical manuscript until the run series is audited and frozen.

## Expected code structure

Claude should create, at minimum:

- `configs/agent_v5.json`
- `scripts/run_agent_v5.py`
- `src/pur_new/agent_v5.py` or another small module containing V5-specific admissibility logic
- `schemas/agent_v5_experiment.schema.json` if V5 output adds new fields
- `tests/test_agent_v5.py`
- `scripts/run_agent_v5_comparison.py` or an equivalent deterministic comparison runner
- a GitHub Actions workflow for structural tests and, only when API secrets are available, an explicitly invoked API run workflow

Do not copy V4 into an unrelated new framework. Reuse V4 code where parity is scientifically desirable, and isolate the minimum differences required by this protocol.

## Required per-card audit fields

Each V5 experiment card should carry at least:

- `candidate_id`
- `measurement_id`
- `experiment_id`
- `chemistry_applicability_status`
- `shared_shape_use`
- `measurement_admissible`
- `admissibility_reason`
- `required_precondition` when inadmissible
- existing VOI components and score for admissible cards

VOI ranking must operate only on the admissible set.

## Required cross-arm report

The final comparison should produce one machine-readable table with one row per run and at least:

- arm;
- run index;
- model;
- attempted/completed/committed/abstained/invalid;
- selected candidate;
- selected measurement;
- selected experiment;
- applicability status;
- domain violation yes/no;
- unsupported shortcut yes/no;
- hypothesis-discrimination score;
- total VOI;
- tool calls;
- prompt/completion tokens;
- latency;
- frozen input hash.

The summary must report arms separately. Do not pool runs across models or arms simply to make N larger.

## Freeze rule

This document and `configs/agent_v5_comparison_protocol.json` define the pre-implementation comparison contract. If implementation reveals a technical impossibility, revise the protocol **before inspecting V5 outcome distributions**, increment the protocol version, preserve this version, and document exactly what changed.
