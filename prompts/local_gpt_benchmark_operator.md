# Local operator prompt: run the PUR-NEW blind GPT benchmark

You are working locally on the repository `stloendays/PUR-NEW`.

Your task is to implement and execute a reproducible blind benchmark of the PUR-NEW formulation Agent across multiple GPT-family models using the repository's current evidence/action framework.

## Scientific objective

Test whether the Agent, **without seeing the follow-up thermal-hold outcomes**, repeatedly prioritizes the resin-modified formulation region that is later supported by physical experiment.

Do not optimize the benchmark after seeing model outputs. Do not modify target labels, prior ranges, candidate grid, or success metrics to improve apparent performance.

## Read first

Read these files before changing code:

- `README.md`
- `docs/WORKFLOW.md`
- `docs/BLIND_AGENT_BENCHMARK.md`
- `docs/AGENT_EVALUATION.md`
- `docs/UNCERTAINTY_MODEL.md`
- `configs/blind_benchmark.json`
- `configs/evidence_access_profiles.json`
- `configs/action_catalog.json`
- `configs/formulation_priors.json`
- `prompts/agent_system.txt`
- `scripts/build_candidate_set.py`
- `scripts/build_agent_context.py`
- `scripts/run_agent_recommendation.py`
- `src/pur_new/actions.py`

## Non-negotiable anti-leakage rule

The GPT model being evaluated must never receive:

- F1/follow-up thermal-hold measurements;
- follow-up adjudication labels;
- the benchmark target region or success labels;
- any prose derived from the held-out follow-up outcome.

The benchmark controller may know these only for post-hoc scoring.

Use `blind_pre_result` for the main benchmark.

## Work to do

1. Pull the latest `main` and create a clean working branch such as `benchmark/blind-gpt-v1`.

2. Build the canonical candidate set with the existing generator. Do not alter the default candidate grid for the primary benchmark.

3. Build the blind Agent context with `blind_pre_result`.

4. Audit the generated context before any API call. Programmatically assert that it does not contain follow-up hold values, follow-up adjudication labels, or benchmark scoring labels. Fail closed if leakage is detected.

5. Add a benchmark runner, preferably `scripts/run_blind_benchmark.py`, that:
   - reads model names from environment variable `PUR_BENCHMARK_MODELS` as a comma-separated list;
   - uses `OPENAI_API_KEY` and optional `OPENAI_BASE_URL` without printing secrets;
   - uses the same frozen candidate set, context, and system prompt for every model;
   - performs a pilot of 5 runs/model by default, with a CLI option for 30+ runs/model;
   - records every run, including API failures and abstentions;
   - stores raw model output and validated recommendation data;
   - does not overwrite existing benchmark artifacts;
   - hashes the candidate set, blind context, system prompt, benchmark config, and git commit.

6. For the evaluated GPT call, reuse the scientific decision contract in `prompts/agent_system.txt`. The model should select one supplied candidate or abstain, and should return ordered alternatives. Do not tell the evaluated model which modifier region is considered successful.

7. Add a deterministic scoring script, preferably `scripts/score_blind_benchmark.py`. The scoring script may read `configs/blind_benchmark.json` because scoring happens after model output is frozen. Compute at least:
   - exact-grid Top-1 recovery at the 18% grid point;
   - supported-region Top-1 recovery for 15-21% modifier;
   - supported-region Top-3 recall;
   - near-experimental Top-3 recall for 17-20%;
   - selection distribution by candidate and modifier fraction;
   - abstention rate;
   - invalid-output/API-failure rate;
   - descriptive enrichment over random selection.

8. Add three benchmark conditions when feasible:
   - `literature_only_sanity`;
   - `blind_pre_result`;
   - `blind_pre_result_without_external_hints`.

   For the third condition, remove external-prior information from the Agent payload without otherwise changing the original-system evidence. Do not create a weaker straw-man prompt.

9. Add tests for:
   - anti-leakage filtering;
   - candidate-grid parsing;
   - scoring logic;
   - Top-3 extraction;
   - abstention handling;
   - reproducible artifact manifests.

10. Store outputs under:

```text
records/benchmarks/<benchmark_id>/
  manifest.json
  runs.jsonl
  summary.json
  model_<sanitized_model_name>/
    recommendations/
```

11. Run the local test suite before and after the benchmark implementation.

12. Run a small pilot first. If the API/model names are valid, run 5 calls per model. Do not automatically launch a costly 30-run/model benchmark unless the environment clearly indicates that this is intended or the user has asked for the full run.

13. At the end, report:
   - exact commands executed;
   - models actually available and used;
   - per-model pilot metrics;
   - aggregate metrics;
   - any leakage/validation failures;
   - where artifacts were written;
   - commit SHA(s);
   - what would be needed for the full 30-run/model benchmark.

## Environment

Use:

```bash
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=...        # optional, for the user's OpenAI-compatible proxy
export PUR_BENCHMARK_MODELS='model-a,model-b,model-c'
```

Never commit or print API keys.

## Interpretation discipline

A good result is not defined as reproducing the exact source-parts formulation digit-for-digit. The primary scientific question is whether the Agent repeatedly concentrates recommendations in the resin-modified region supported by the external analogue evidence and later physical experiment.

The benchmark must remain capable of failing. If GPT models prefer another region, abstain, or show unstable rankings, report that result faithfully and diagnose why.

Do not change candidate priors, scoring intervals, or prompts after seeing the pilot in order to increase hit rate. If a methodological change is scientifically justified, version it as a new benchmark rather than silently replacing V1.
