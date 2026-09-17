# Local operator prompt: run PUR-NEW V2 multi-GPT benchmark

You are working locally on `stloendays/PUR-NEW`.

Your task is to implement and run the **V2 full-Agent held-out-result benchmark** across multiple GPT-family models.

## Scientific objective

Test whether the Agent, while blinded to the current follow-up formulation and its thermal-hold result, can use:

- original local PUR experiments;
- structured process/repeatability uncertainty;
- deterministic scientific actions;
- the evidence-derived candidate-space hypothesis;
- external PUR patent/literature/database evidence;
- the finite V2 candidate set;

to rank candidates close to the later successful follow-up region.

This is a **retrospective held-out-result blind replay** for the current experiment, because the V2 hypothesis was formalized after the follow-up result was already known. Do not describe V2 itself as prospectively validated. Future rounds can become prospective after this configuration is frozen.

## Read first

Read:

- `README.md`
- `docs/CANDIDATE_SPACE_HYPOTHESIS.md`
- `docs/BLIND_AGENT_BENCHMARK.md`
- `docs/WORKFLOW.md`
- `docs/AGENT_EVALUATION.md`
- `docs/UNCERTAINTY_MODEL.md`
- `configs/blind_benchmark_v2.json`
- `configs/formulation_priors.json`
- `configs/evidence_access_profiles.json`
- `configs/action_catalog.json`
- `data/external_evidence_hints.csv`
- `prompts/agent_system.txt`
- `scripts/build_candidate_set.py`
- `scripts/build_agent_context.py`
- `scripts/run_agent_recommendation.py`
- `src/pur_new/actions.py`

`configs/blind_benchmark.json` is deprecated V1 history only. Do not use it for new benchmark runs or scoring.

## V2 candidate construction

Do not use the old scalar modifier grid.

V2 uses:

```text
acrylic-like modifier = {0, 15, 20, 25}%
minor tackifier-like modifier = {0, 5, 10}%
```

The Cartesian product gives 12 candidates.

The reactive core is derived only from original local formulation E2 and preserves its normalized PPG2000/PDP-70/MDI proportions in the remaining mass fraction.

Generate:

```bash
python scripts/build_candidate_set.py
```

Expected default output:

```text
derived/candidate_set_hypothesis_v2.json
```

The exact current follow-up recipe must not be inserted as a discrete candidate.

## Allowed evidence in the primary Agent condition

The evaluated model SHOULD see:

- original E1-E5 evidence that predates the follow-up outcome;
- original E1/E5 thermal-hold drift;
- E2 repeat/run variability;
- the V2 candidate-space hypothesis;
- source-level external evidence supporting 15/20/25% acrylic-like levels;
- source-level external evidence supporting ~5% and coarse <=10% minor tackifier levels;
- the external hot-hold comparison showing lower-OH versus higher-OH acrylic stability differences;
- process-state/missingness uncertainty;
- all permitted deterministic actions;
- all 12 candidate states.

Do NOT hide uncertainty-aware actions or database evidence in the primary condition. Those are core Agent capabilities.

## Forbidden held-out information

The evaluated model MUST NOT see:

- current follow-up formulation amounts;
- normalized current follow-up composition;
- follow-up repeat-1/repeat-2 hold measurements;
- follow-up adjudication labels;
- controller-only nearest-candidate ID;
- controller distance thresholds or success labels;
- prose derived from the follow-up result.

Before each API run, audit the actual final payload and fail closed if any held-out information leaks into it.

## Build the blind Agent context

Run:

```bash
python scripts/build_agent_context.py \
  --candidate-set derived/candidate_set_hypothesis_v2.json \
  --profile blind_pre_result \
  --output derived/agent_context_blind_v2.json
```

Audit this context before API use.

## Action use

The Agent should be able to use or consume outputs from:

```text
query_external_priors
get_candidate_hypothesis
inspect_formulation
get_hold_stability
get_repeatability_risk
get_temperature_support
candidate_profile
compare_candidate_to_priors
audit_process_unknowns
stress_test_candidate
rank_candidate_support
```

Record the evidence/action trace for every run.

## API output ranking contract

The model output is structured JSON. Preserve the raw response before normalization.

For every valid non-abstaining response:

```text
Rank 1 = selected_candidate_id
Rank 2 = alternatives_considered[0]
Rank 3 = alternatives_considered[1]
```

The alternatives list must be treated as a strict preference ranking, not an unordered explanation list.

Validation rules:

- all ranked IDs must exist in the supplied candidate set;
- alternatives must be unique;
- selected candidate must not repeat in alternatives;
- provide at least two alternatives when at least three candidates exist;
- abstain requires `selected_candidate_id = null`;
- alternatives on an abstention are stored as an uncertainty shortlist only and do not count toward primary Top-1/Top-3 recovery.

The repository runner now enforces candidate validity, uniqueness, non-repetition and the minimum-two-alternatives rule. Semantic preference ordering is enforced by the system prompt and audited in saved output.

## Implement/run the multi-model benchmark

Add or update `scripts/run_blind_benchmark.py`.

Requirements:

- model list from `PUR_BENCHMARK_MODELS`;
- credentials from `OPENAI_API_KEY` and optional `OPENAI_BASE_URL` only;
- never print or commit secrets;
- identical frozen candidate set/context/system prompt for compared models;
- pilot default: 5 runs/model;
- CLI support for >=30 runs/model;
- save valid recommendations, abstentions, invalid outputs and API failures;
- save raw response, normalized recommendation, action/evidence trace, timestamps, hashes, model, run index and git commit;
- never overwrite an existing benchmark directory.

## Run-level statistics table

Create a controller-side flat table with one row per API call. At minimum include:

```text
model
run_index
run_status
decision_mode
rank1_candidate_id
rank2_candidate_id
rank3_candidate_id
rank1_acrylic_pct
rank1_tackifier_pct
rank1_total_modifier_pct
nearest_candidate_rank
modifier_plane_l1_distance_top1
modifier_plane_l1_distance_best_top3
abstain
invalid_output
api_failure
scientific_boundary_violation
```

Use `run_status` values:

```text
valid_recommendation
abstain
invalid_output
api_failure
```

Do not coerce abstention into API failure, and do not silently drop invalid/API-failure rows.

## Scoring

Add/update `scripts/score_blind_benchmark.py`.

Only after model outputs are frozen may the controller read `configs/blind_benchmark_v2.json`.

Do not use the old exact-18%-modifier metric.

Report:

```text
nearest-candidate rank
nearest-candidate Top-1 recovery
nearest-candidate Top-3 recall
Top-1 L1 distance in (acrylic %, tackifier %) space
best Top-3 L1 distance
Top-1 / Top-3 within controller-only distance threshold
resin-modified Top-1 rate
selection distribution
abstention rate
invalid/API-failure rate
scientific-boundary violation rate
```

Primary Top-3 recovery is defined only for valid non-abstaining recommendations. If an abstaining run lists plausible alternatives, score those only in a separate abstention-shortlist diagnostic.

## Baselines

Compare against:

1. uniform random over all 12 candidates;
2. deterministic `rank_candidate_support` baseline;
3. database-only class-specific evidence ranker;
4. full Agent.

If the deterministic evidence ranker already puts the nearest held-out candidate first, do not claim that GPT uniquely discovered the region. Evaluate Agent value via uncertainty handling, evidence integration, alternative ranking, robustness and abstention.

## Ablations

When API budget permits, compare:

```text
full Agent
without external database
without action enrichment
literature-only sanity
without explicit candidate-hypothesis context
```

Do not make ablation prompts intentionally worse beyond removing the named capability.

## Tests

Add tests for:

- V2 candidate generation from E2;
- candidate count == 12;
- every candidate sums to approximately 100;
- no F1/follow-up numbers used in candidate generation;
- class-specific prior comparison;
- anti-leakage;
- strict Top-3 extraction from selected + ordered alternatives;
- rejection of duplicate/repeated alternatives;
- two-dimensional distance scoring;
- abstention/invalid output handling;
- abstention shortlist separated from primary Top-3;
- reproducible manifests/hashes.

Run `pytest` before any API calls.

## Artifact layout

Use:

```text
records/benchmarks/PUR_NEW_BLIND_AGENT_V2/<run_id>/
  manifest.json
  runs.jsonl
  run_table.csv
  summary.json
  model_<name>/
    recommendations/
    action_traces/
```

## Run policy

Start with 5 runs/model. Do not automatically launch the full >=30 runs/model experiment until the pilot is technically valid.

At the end report:

- models used;
- runs/model;
- nearest-candidate rank distribution;
- nearest-candidate Top-1/Top-3;
- 2D modifier-distance metrics;
- selection distribution;
- abstention/invalid rates;
- action-use frequencies;
- database-evidence-use diagnostics;
- full-Agent versus ablations;
- leakage-audit result;
- artifact paths;
- commit SHA(s).

The benchmark must remain capable of failing. Do not tune priors, candidate axes, prompts, retrieval rules or scoring after seeing pilot results merely to increase agreement with the held-out experiment.
