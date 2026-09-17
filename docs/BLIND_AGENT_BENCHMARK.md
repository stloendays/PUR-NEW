# Full-Agent blind multi-model benchmark

## Objective

Quantify how reliably the **full PUR-NEW decision Agent** recovers the formulation region later supported by wet-lab thermal-hold measurements while remaining blind to those held-out outcomes.

The benchmark asks:

> Given the information and tools genuinely available before the follow-up experiment — original-system rheology, structured uncertainty, uncertainty-aware actions, external PUR database/literature evidence, and an admissible candidate set — how often does the Agent prioritize the resin-modified formulation region that is later physically supported?

## 1. What "blind" means

Blindness applies to the **future outcome**, not to the Agent's legitimate scientific capabilities.

### The evaluated Agent SHOULD see in the primary condition

- original local temperature-sweep and thermal-hold evidence available before follow-up;
- process-state/missingness information;
- uncertainty-aware deterministic actions and their outputs;
- external PUR patent/literature/database evidence available before follow-up;
- admissible candidate set;
- workflow policy and scientific decision prompt.

### The evaluated Agent MUST NOT see

- F1/follow-up thermal-hold measurements;
- follow-up adjudication labels;
- benchmark target/success region;
- scoring labels;
- prose derived from the held-out follow-up result.

Thus the main experiment evaluates the Agent system, not a stripped-down plain LLM.

## 2. Primary full-Agent condition

Use `blind_pre_result` from `configs/evidence_access_profiles.json`.

The intended information flow is:

```text
original local evidence
+ structured uncertainty
+ deterministic actions
+ external database/literature retrieval
+ finite candidate set
------------------------------
Agent recommendation
```

Only the later wet-lab outcome is hidden.

Removing database evidence or action enrichment is reserved for ablation studies.

## 3. Database evidence contract

External database evidence is part of the Agent's intended capability and should be visible in the primary benchmark.

Preferred implementation:

```text
Agent/query layer
-> fixed retrieval/action rule
-> source rows/chunks with source_id + evidence_locator + limitations
-> Agent reasoning
```

A curated evidence summary may also be supplied if its construction is documented and does not use the held-out outcome.

For the strongest claim, preserve:

- retrieval query or filter;
- returned source IDs;
- evidence locators;
- raw retrieved rows/chunks;
- source limitations;
- timestamp/hash.

The database is a scientific evidence source, not a hidden scoring oracle.

## 4. Action contract

The primary benchmark should expose uncertainty-aware actions such as:

- `query_external_priors`;
- `inspect_formulation`;
- `get_hold_stability`;
- `get_repeatability_risk`;
- `get_temperature_support`;
- `audit_process_unknowns`;
- `candidate_profile`;
- `compare_candidate_to_priors`;
- `stress_test_candidate`;
- `rank_candidate_support`.

Whether implemented as true API/tool calls or as deterministic action outputs embedded in a frozen Agent context, the action layer must be the same across compared models.

Record an action/evidence trace for each run so the paper can distinguish a correct answer from a correct evidence-use path.

## 5. Candidate set

Generate the canonical candidate set with:

```bash
python scripts/build_candidate_set.py
```

Default total modifier grid:

```text
0, 5, 10, 15, 18, 20, 25 % normalized total
```

The generator uses the documented AC1920/TK100 split and normalized MDI assumption for this benchmark family. These are candidate-generation assumptions, not mechanistic laws.

The controller uses the held-out experiment only after model recommendations are frozen to score recovery. The evaluated Agent must not receive the scoring target.

## 6. Context construction

Build the main context with:

```bash
python scripts/build_agent_context.py \
  --candidate-set derived/candidate_set_external_prior_grid.json \
  --profile blind_pre_result \
  --output derived/agent_context_blind.json
```

Before any model call, audit the final payload/tool-access layer for leakage. The audit must specifically distinguish:

```text
allowed: pre-result database evidence, uncertainty actions, original experiments
forbidden: follow-up results, adjudication labels, benchmark target labels
```

## 7. Models and repetitions

Recommended protocol:

```text
pilot: 5 independent runs per model
full benchmark: >=30 independent runs per model
```

Use identical candidate set, action policy, database evidence policy, system prompt and decoding settings across models.

Record every run, including failures and abstentions.

## 8. Primary metrics

After recommendations are frozen, compute:

### Exact-grid Top-1 recovery

Top-1 equals the canonical 18% grid point.

### Supported-region Top-1 recovery

Top-1 modifier fraction lies in the controller-defined 15-21% region.

### Supported-region Top-3 recall

At least one Top-3 candidate lies in 15-21%.

### Near-experimental Top-3 recall

At least one Top-3 candidate lies in 17-20%.

### Selection distribution

Empirical distribution over candidate IDs and modifier fractions.

### Abstention and invalid-output rates

Report rather than discard them.

### Descriptive enrichment over random

Compare recovery frequency with the finite candidate-set random baseline without overstating independence across repeated LLM calls.

## 9. Evidence-use diagnostics

For each run, record whether the Agent:

- recognized original thermal-hold drift;
- recognized repeat/run variability;
- treated process history as uncertainty;
- used external database evidence;
- used action outputs/tools;
- distinguished analogue support from direct proof;
- invented any unsupported measurement or mechanism.

## 10. Ablations

The full-Agent condition is the primary result.

### A. Full Agent — primary

```text
local evidence + uncertainty actions + database evidence
```

### B. No external database

```text
local evidence + uncertainty actions
```

This estimates the incremental value of the external database.

### C. No action enrichment

```text
local evidence + database evidence
```

Remove deterministic action-derived summaries/tools while keeping the scientific objective and prompt quality otherwise matched.

### D. Literature-only sanity

```text
database evidence only
```

This is a diagnostic of the prior, not the main Agent benchmark.

## 11. Scientific interpretation

The strongest useful result is not that a plain LLM reproduces the exact source-parts recipe digit-for-digit.

The relevant result is that the **full evidence-using Agent** repeatedly concentrates recommendation mass in the same resin-modified region that is later supported by wet-lab measurements.

A defensible paper-facing statement, if supported by the measured benchmark frequencies, is:

> Under a held-out-outcome protocol, an uncertainty-aware Agent equipped with pre-result local evidence, database evidence and deterministic scientific actions repeatedly prioritized the resin-modified formulation region later supported by physical thermal-hold measurements.

The benchmark must remain capable of failing. Do not tune the retrieval rule, priors, candidate grid, prompt or scoring region after inspecting pilot outputs to improve apparent performance. Version any justified methodological change as a new benchmark.
