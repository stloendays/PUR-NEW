# Local operator prompt: run the PUR-NEW full-Agent blind GPT benchmark

You are working locally on `stloendays/PUR-NEW`.

Your task is to implement and execute a reproducible benchmark of the **full PUR-NEW Agent system** across multiple GPT-family models.

## Core scientific question

Can an uncertainty-aware Agent, using the information it is genuinely supposed to have before the follow-up experiment, repeatedly prioritize the resin-modified formulation region that is later supported by physical experiment?

## Important clarification: what "blind" means

The evaluated GPT is blind only to the **held-out follow-up experimental outcome and benchmark labels**.

The primary benchmark MUST give the evaluated Agent access to:

1. original local formulation/rheology evidence available before the follow-up experiment;
2. explicit process-state and missingness information;
3. uncertainty-aware actions/tool outputs;
4. external PUR database/literature evidence available before the follow-up result;
5. finite admissible candidate set;
6. the normal scientific decision contract in `prompts/agent_system.txt`.

Do **not** cripple the primary Agent by hiding its database or uncertainty-aware actions. Removing those capabilities is an ablation experiment only.

The evaluated GPT must NOT receive:

- F1/follow-up thermal-hold measurements;
- repeat-1/repeat-2 final stability values;
- follow-up adjudication labels;
- benchmark target region/success labels;
- post-hoc prose derived from the held-out follow-up result.

## Read first

Read:

- `README.md`
- `docs/WORKFLOW.md`
- `docs/BLIND_AGENT_BENCHMARK.md`
- `docs/AGENT_EVALUATION.md`
- `docs/UNCERTAINTY_MODEL.md`
- `configs/blind_benchmark.json`
- `configs/evidence_access_profiles.json`
- `configs/action_catalog.json`
- `configs/formulation_priors.json`
- `data/external_evidence_hints.csv`
- `prompts/agent_system.txt`
- `scripts/build_candidate_set.py`
- `scripts/build_agent_context.py`
- `scripts/run_agent_recommendation.py`
- `src/pur_new/actions.py`

## Primary condition

Use `blind_pre_result`, but interpret it correctly:

```text
original local evidence
+ uncertainty-aware actions
+ external database/literature evidence
+ candidate set
+ process-state uncertainty
------------------------------
Agent decision
```

Only the later wet-lab result is held out.

If feasible, prefer exposing database evidence through retrieval/actions rather than dumping an opaque hand-picked answer into the prompt. The Agent should be able to call or consume outputs from actions such as:

- `query_external_priors`
- `inspect_formulation`
- `get_hold_stability`
- `get_repeatability_risk`
- `get_temperature_support`
- `audit_process_unknowns`
- `candidate_profile`
- `compare_candidate_to_priors`
- `stress_test_candidate`
- `rank_candidate_support`

Record which actions/evidence were used for each decision.

## Anti-leakage audit

Before any API call, programmatically verify that the final Agent payload/tool-access layer contains no held-out follow-up values, no adjudication label, and no benchmark scoring region. Fail closed on leakage.

Do not confuse legitimate database evidence with leakage. External patent/literature evidence is intentionally available to the Agent in the primary condition.

## Benchmark implementation

1. Pull latest `main` and create a clean branch, e.g. `benchmark/full-agent-blind-v1`.
2. Build the canonical candidate set using the existing generator; do not change the V1 grid.
3. Build the Agent context using `blind_pre_result`.
4. Implement `scripts/run_blind_benchmark.py`.
5. Read models from `PUR_BENCHMARK_MODELS`.
6. Use `OPENAI_API_KEY` and optional `OPENAI_BASE_URL`; never print or commit secrets.
7. Pilot with 5 runs/model; support >=30 runs/model.
8. Use the same frozen candidate set, pre-result evidence, database evidence, action policy, and system prompt for all compared models.
9. Save every run, including abstentions, invalid outputs, and API failures.
10. Save raw output, normalized recommendation, action/evidence trace, hashes, timestamp, git commit, model, and run index.
11. Implement deterministic post-hoc scorer `scripts/score_blind_benchmark.py`.
12. Do not let scoring labels flow back into the evaluated Agent.

## Primary metrics

Compute after recommendations are frozen:

- exact-grid Top-1 recovery at 18% modifier;
- 15-21% supported-region Top-1 recovery;
- 15-21% supported-region Top-3 recall;
- 17-20% near-experimental Top-3 recall;
- candidate/modifier selection distribution;
- abstention rate;
- invalid/API-failure rate;
- descriptive enrichment over random.

Also summarize:

- whether process-history/repeatability uncertainty was recognized;
- whether database evidence was actually used;
- which actions were used;
- whether the Agent distinguished analogue support from direct proof.

## Ablations

The main scientific result is the **full Agent** condition above.

Then, as secondary ablations, compare:

### A. Full Agent / primary

```text
local evidence + uncertainty actions + database evidence
```

### B. No external database

```text
local evidence + uncertainty actions
```

Remove only external database/literature evidence.

### C. No action enrichment

```text
local evidence + database evidence, but without deterministic action-derived summaries/tools
```

Keep the same scientific objective and do not intentionally degrade the prompt.

### D. Literature-only sanity check

```text
database evidence only
```

This is a diagnostic, not the main benchmark.

These ablations answer whether performance comes from the full Agent architecture, the local experiment, the database, or their combination.

## Database discipline

The Agent should see genuine pre-result database evidence. However, do not create a post-hoc database summary whose only purpose is to encode the known experimental answer.

For the strongest paper claim:

- freeze the retrieval query/rule;
- preserve returned source IDs/evidence locators;
- record retrieved rows/chunks;
- allow broad relevant evidence, including evidence that may not support the final candidate;
- keep source limitations visible.

The database is evidence available to the Agent, not a hidden scoring oracle.

## Artifacts

Store under:

```text
records/benchmarks/<benchmark_id>/
  manifest.json
  runs.jsonl
  summary.json
  model_<sanitized_model_name>/
    recommendations/
    action_traces/
```

## Tests

Add tests for:

- anti-leakage;
- candidate-grid parsing;
- database/action visibility in the full-Agent condition;
- Top-3 extraction;
- scoring;
- abstention/invalid output handling;
- reproducible manifests/hashes.

Run `pytest` before and after implementation.

## Final report

Report:

1. models actually used;
2. runs/model;
3. exact Top-1;
4. supported-region Top-1;
5. supported-region Top-3;
6. near-experimental Top-3;
7. abstention and invalid rates;
8. selection distributions;
9. action-use frequencies;
10. database-evidence-use diagnostics;
11. full-Agent vs no-database vs no-action ablation differences;
12. leakage audit result;
13. artifact paths;
14. commit SHA(s).

## Interpretation

The benchmark must remain capable of failing. Do not tune candidate priors, prompts, scoring intervals, retrieval rules, or database summaries after seeing pilot outputs in order to improve recovery.

The primary claim we are testing is not "a plain GPT guessed 18%". It is:

> A full uncertainty-aware scientific Agent, equipped with pre-result local evidence, database evidence and deterministic actions, can concentrate experimental recommendations in a formulation region later supported by wet-lab measurements.
