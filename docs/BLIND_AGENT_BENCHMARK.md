# Blind multi-model Agent benchmark

## Objective

Quantify how reliably the PUR-NEW decision Agent recovers the formulation region that is later supported by wet-lab thermal-hold measurements, **without exposing those follow-up outcomes to the evaluated model**.

The benchmark is designed to answer a narrow question:

> Given only the original-system rheology, structured uncertainty, admissible candidate grid, and external PUR analogue priors, how often does an Agent rank a resin-modified formulation in the experimentally relevant modifier region near the top?

This benchmark evaluates recommendation quality, not autonomous laboratory control.

## 1. Strict separation of roles

There are two roles:

### Benchmark controller

The controller may know the held-out experimental result and may read this benchmark plan. It is responsible for:

- building the candidate set;
- building the blind Agent context;
- calling one or more GPT models repeatedly;
- storing raw recommendation records;
- scoring recommendations after all runs finish;
- never inserting held-out labels into the evaluated model payload.

### Evaluated Agent

The evaluated Agent receives only:

```text
configs/workflow.json
+ deterministic original-system evidence
+ configs/formulation_priors.json / external evidence hints
+ action-enriched blind context
+ finite admissible candidate set
+ prompts/agent_system.txt
```

It must not receive:

```text
follow-up hold measurements
follow-up adjudication labels
benchmark target region
benchmark success labels
text derived from the follow-up outcome
```

The evaluated model selects only from the candidate set or abstains.

## 2. Evidence profile

Use `blind_pre_result` from `configs/evidence_access_profiles.json`.

This profile permits:

- original temperature sweeps;
- original thermal-hold evidence;
- external analogue priors;
- formulation/process uncertainty descriptors.

It blocks follow-up hold results and post-result adjudication.

A run that exposes held-out follow-up outcomes is invalid and must not be included in benchmark statistics.

## 3. Candidate set

Generate the canonical candidate set with:

```bash
python scripts/build_candidate_set.py
```

Default total modifier grid:

```text
0, 5, 10, 15, 18, 20, 25 wt/parts-% of normalized total
```

The generator uses a transparent 80/20 AC1920/TK100 modifier split and a fixed normalized MDI fraction for this candidate family. These are candidate-generation assumptions, not learned mechanistic laws.

The experimentally used follow-up formulation normalizes to approximately 18.12% combined AC1920+TK100. Therefore the 18% grid point is the closest canonical recovery point, while 15-21% is treated as the broader supported modifier region for region-level scoring.

**Important:** this scoring information belongs to the benchmark controller only and is not injected into the evaluated Agent request.

## 4. Action-enriched context

Build the blind context with:

```bash
python scripts/build_agent_context.py \
  --candidate-set derived/candidate_set_external_prior_grid.json \
  --profile blind_pre_result \
  --output derived/agent_context_blind.json
```

The context exposes deterministic action outputs rather than asking the LLM to rediscover everything from raw CSVs. Current action families include:

- external-prior lookup;
- original hold-stability inspection;
- repeatability-risk inspection;
- temperature-support inspection;
- candidate composition profiling;
- process-history missingness audit;
- analogue-region comparison;
- candidate stress testing;
- transparent support ranking.

These actions are allowed to make relevant evidence easier to use. They are not allowed to encode the held-out experimental answer.

## 5. Models and repetitions

Use multiple GPT-family models available through the configured OpenAI-compatible endpoint.

Recommended protocol:

```text
pilot: 5 independent runs per model
full benchmark: >=30 independent runs per model
```

Use the same candidate set, blind context, system prompt, evidence-access profile, and decoding policy for all models unless the benchmark explicitly studies one of those factors.

Record for every run:

```text
model
run index
UTC timestamp
selected candidate
ordered alternatives
decision mode
uncertainty vector
acceptance criterion
input hash
prompt hash
candidate-set hash
raw model response
validated frozen recommendation path
```

Do not silently drop failed or abstaining runs.

## 6. Primary metrics

### A. Exact-grid Top-1 recovery

```text
selected candidate == 18% modifier grid point
```

This is the strictest discrete recovery metric.

### B. Supported-region Top-1 recovery

```text
selected modifier fraction in [15%, 21%]
```

This evaluates whether the Agent identifies the correct formulation region rather than one exact discretization point.

### C. Supported-region Top-3 recall

Treat the selected candidate plus the first two ordered alternatives as Top-3.

```text
at least one Top-3 candidate in [15%, 21%]
```

### D. Near-experimental Top-3 recall

A stricter regional metric:

```text
at least one Top-3 candidate in [17%, 20%]
```

### E. Rank stability

For each model, report the empirical selection distribution over candidate IDs and modifier fractions. High concentration around one region is stronger evidence than a single successful run.

### F. Abstention rate

Report abstentions as outcomes, not errors. Excessive abstention may indicate that the uncertainty policy is too conservative.

### G. Resin-family enrichment over random

For a candidate set of size `N`, compare observed recovery with the random-selection baseline. Report enrichment descriptively; do not imply statistical independence across repeated LLM calls without an appropriate analysis.

## 7. Secondary diagnostics

Record whether the Agent correctly identifies the dominant evidence pattern:

- original reactive-only system shows thermal-hold drift;
- nominally identical formulations can show large run-to-run spread;
- process history is an explicit uncertainty source;
- external PUR evidence supports resin/tackifier-modified formulation families;
- acrylic-like modifier examples cluster near ~20% total-formulation fraction in the curated analogue evidence;
- analogue evidence supports a design region, not the exact wet-lab optimum.

Also record whether the Agent violates any scientific boundary:

- invents missing viscosity values;
- treats unknown process metadata as zero;
- claims a molecular mechanism from rheology alone;
- cites held-out follow-up results in blind mode;
- selects a candidate outside the supplied finite set.

## 8. Ablations

Run at least three evidence conditions when budget permits:

### `literature_only_sanity`

Question: do external database priors alone enrich resin-modified candidates?

### `blind_pre_result`

Primary benchmark. Original local evidence + external priors, no follow-up result.

### `blind_pre_result` without external hints

Ablation created by withholding `external_prior_hints` and analogue actions while retaining the original-system evidence.

This comparison estimates how much the curated database contributes beyond the local failure evidence.

Do not use `closed_loop_design` as a blind benchmark condition because it may expose the follow-up result.

## 9. Interpretation

The strongest useful result is not that an LLM reproduces the exact source-parts recipe digit-for-digit. The scientifically relevant result is that a structured Agent repeatedly concentrates recommendation mass in the same resin-modified region that is later supported by wet-lab measurements.

A defensible paper-facing statement, if supported by the benchmark, is:

> Under a held-out evidence protocol, the Agent repeatedly prioritized the resin-modified formulation region later supported by physical thermal-hold measurements, with the exact hit/Top-k recovery reported across repeated model runs.

Use the measured frequencies from the benchmark. Do not replace them with subjective confidence estimates.

## 10. Artifacts

Store benchmark outputs under:

```text
records/benchmarks/<benchmark_id>/
  manifest.json
  runs.jsonl
  summary.json
  model_<name>/recommendations/*.json
```

The manifest must include hashes of:

- candidate set;
- Agent context;
- system prompt;
- benchmark config;
- git commit.

This makes the benchmark auditable and prevents later changes in prompt/data from being mixed into the same reported result.
