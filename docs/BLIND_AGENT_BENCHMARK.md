# Full-Agent held-out-result benchmark — V2

## Objective

PUR-NEW V2 asks a narrower and more defensible question than the earlier scalar-modifier benchmark:

> If the Agent is given the original local rheology, uncertainty-aware actions, an independently evidence-derived candidate hypothesis, and external PUR database/literature evidence — but is blinded to the current follow-up formulation and its wet-lab outcome — does it prioritize candidates that are compositionally close to the later successful follow-up region?

The benchmark evaluates the **full evidence-using Agent**, not a plain LLM.

## Historical status

V2 is a **retrospective held-out-result blind replay** for the already completed follow-up experiment.

The candidate-space hypothesis in `docs/CANDIDATE_SPACE_HYPOTHESIS.md` was formalized after the current follow-up result was already known. However, the V2 grid itself is rebuilt without using any numeric value from that follow-up recipe:

- the reactive core is anchored to original formulation E2;
- acrylic-like levels are independently anchored at 15, 20 and 25% by external evidence;
- minor tackifier-like levels are independently anchored at 5 and 10% by external evidence/guidance;
- the exact follow-up recipe is not one of the discrete generated candidates.

Therefore V2 can test whether the evidence stack is **consistent with** the held-out experiment, but it must not be described as prospective validation of V2 itself.

Once V2 is frozen, future design rounds can use the same structure prospectively.

---

## 1. What the evaluated Agent may see

Primary condition:

```text
original local evidence
+ formulation/process-state uncertainty
+ deterministic actions
+ evidence-derived candidate hypothesis
+ external PUR database/literature evidence
+ finite V2 candidate set
```

This includes source-level evidence that supports the candidate axes.

The Agent should be able to retrieve/inspect:

- original thermal-hold drift;
- original run/repeat spread;
- E2 as the central original reactive-core design point;
- literature/patent evidence for acrylic-modified PUR at 15, ~20 and 25%;
- literature/patent evidence for minor tackifier/hydrocarbon-resin levels around 5% and guidance up to about 10%;
- direct external evidence that acrylic functionality can alter hot-hold viscosity stability;
- process-history missingness and other uncertainty terms.

## 2. What the Agent must not see

The evaluated Agent must not receive:

```text
current follow-up formulation amounts
normalized current follow-up composition
follow-up thermal-hold measurements
follow-up adjudication labels
nearest-candidate label
controller-side distance threshold
any prose derived from the held-out result
```

The benchmark controller may use those values **only after model outputs are frozen**.

---

## 3. Candidate-space hypothesis

Read `docs/CANDIDATE_SPACE_HYPOTHESIS.md` for the full evidence chain.

### Reactive-core anchor

E2 is used because it is the geometric centre of the original five-point design:

```text
E1 / E2 / E3 : NCO:OH 1.70 / 1.80 / 1.90 at 50/50 PPG2000/PDP-70
E4 / E2 / E5 : composition perturbation around 50/50 at NCO:OH 1.80
```

The E2 reactive core normalizes to approximately:

```text
PPG2000 39.9047%
PDP-70  39.9047%
MDI     20.1907%
```

### Acrylic-like axis

Independent evidence anchors:

```text
0%   control
15%  peer-reviewed 2025 reactive-PUR formulation study
20%  repeated US20160215185A1 acrylic-tackifying-resin examples
25%  US6465104B1 acrylic-copolymer example with direct hot-hold stability data
```

### Minor tackifier-like axis

Independent evidence anchors:

```text
0%   control
5%   represents repeated ~4.8-6.4% resin examples in US5932680A
10%  conservative upper coarse level supported by published PUR formulation guidance
```

### V2 grid

```text
acrylic-like = {0, 15, 20, 25}%
minor tackifier-like = {0, 5, 10}%
```

Cartesian product: 12 candidates.

For each candidate, the E2 reactive core is scaled into the remaining formulation fraction. No final-experiment-derived MDI fraction or 80/20 modifier split is used.

Generate with:

```bash
python scripts/build_candidate_set.py
```

Default output:

```text
derived/candidate_set_hypothesis_v2.json
```

---

## 4. Why this is a hypothesis rather than an answer-shaped grid

V1 collapsed all modifiers into a single total-modifier axis and included an 18% candidate very close to the later follow-up total modifier fraction. V2 removes that design.

The new grid asks two independently motivated questions:

```text
How much acrylic-like modifier?
How much minor tackifier-like modifier?
```

The coarse levels are tied to external sources rather than to the later follow-up recipe.

A successful Agent run therefore means that the evidence stack naturally favors a region near the held-out formulation; it does not mean the correct recipe was preloaded as one discrete option.

`configs/blind_benchmark.json` is retained only as deprecated V1 history. All new runs and scoring use `configs/blind_benchmark_v2.json`.

---

## 5. Full-Agent information flow

```text
original measurements
-> deterministic response descriptors
-> uncertainty decomposition
-> E2-centered candidate-space hypothesis
-> database retrieval / evidence actions
-> candidate profiling
-> class-specific analogue comparison
-> process-history audit
-> stress test
-> Agent recommendation + alternatives
-> freeze
-> controller-only held-out scoring
```

Important action families:

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

The action/evidence trace should be retained for each run.

---

## 6. External stability evidence the Agent may use

Two pieces are especially relevant to the hypothesis.

### Low-OH acrylic versus higher-OH acrylic

US6465104B1 compares two formulations at the same 25 wt% acrylic loading. The lower-OH acrylic example showed a substantially slower viscosity rise at 121 C than the higher-OH analogue.

This supports:

```text
modifier functionality / effective reactive-group density
as a stability variable
```

It does **not** prove that AC1920 behaves identically.

### Functional tackifier / acrylic formulation series

US20030022973A1 reports different stability values across functional-tackifier/acrylic PUR formulations. Because several formulation variables change, these data are directional rather than causal.

The correct Agent use is:

> resin identity and functionality can matter enough to justify formulation-family testing.

---

## 7. API output and ranking contract

Every API call must return structured JSON only. The raw model response is preserved, then normalized and frozen by the runner.

For a valid non-abstaining recommendation:

```text
Rank 1 = selected_candidate_id
Rank 2 = alternatives_considered[0]
Rank 3 = alternatives_considered[1]
```

`alternatives_considered` is therefore not an unordered explanation list. It is a **strict descending preference ranking**.

Rules:

- alternatives must be valid candidate IDs from the supplied set;
- alternatives must be unique;
- the selected candidate must not appear again in alternatives;
- when at least three candidates exist, non-abstaining outputs must provide at least two alternatives;
- `abstain` requires `selected_candidate_id = null`;
- alternatives attached to an abstention are an uncertainty shortlist only and do **not** count toward primary Top-1 or Top-3 recovery.

This prevents a model from receiving benchmark credit merely for mentioning the held-out-near candidate somewhere in an unordered list.

---

## 8. Benchmark protocol

Use `configs/blind_benchmark_v2.json`.

Recommended protocol:

```text
pilot: 5 independent runs per model
full benchmark: >=30 runs per model
```

Use identical candidate set, evidence profile, action policy, prompt and decoding settings across models.

Record every run, including:

- valid recommendations;
- abstentions;
- invalid outputs;
- API failures.

Do not silently discard failures.

Each controller-side run row should retain at least:

```text
model
run_index
run_status
decision_mode
rank1_candidate_id
rank2_candidate_id
rank3_candidate_id
rank1 acrylic-like %
rank1 tackifier-like %
rank1 total modifier %
nearest-candidate rank
Top-1 distance
best Top-3 distance
abstain flag
invalid-output flag
API-failure flag
scientific-boundary-violation flag
```

The raw response, normalized frozen recommendation and action/evidence trace must remain available for audit.

---

## 9. Controller-side scoring

After recommendations are frozen, the controller may compare candidate rankings with the held-out follow-up formulation.

V2 uses a **two-dimensional modifier plane**:

```text
(acrylic-like %, minor-tackifier-like %)
```

Primary metrics:

```text
nearest-candidate rank
nearest-candidate Top-1 recovery
nearest-candidate Top-3 recall
Top-1 L1 distance to held-out modifier coordinates
best Top-3 L1 distance to held-out modifier coordinates
resin-modified Top-1 rate
selection distribution
abstention rate
scientific-boundary violation rate
```

Primary Top-3 recovery is evaluated only for valid non-abstaining recommendations. For abstentions, any listed alternatives are summarized separately as an **abstention shortlist diagnostic** and never credited as primary recovery.

Distance-based scoring is preferred over the old exact-18% scalar metric because V2 no longer encodes a total-modifier answer point.

The held-out target and distance threshold exist only in `configs/blind_benchmark_v2.json` on the controller side and must not enter the Agent payload.

---

## 10. Ablations

### Full Agent — primary

```text
local evidence + candidate hypothesis + uncertainty actions + external database
```

### Without external database

Tests incremental value of external evidence.

### Without action enrichment

Tests value of deterministic scientific tools/summaries.

### Literature-only sanity

Tests whether the external priors alone already rank the same formulation family.

### Without candidate-hypothesis context

Tests whether the explicit evidence-to-grid rationale helps the Agent use the candidate set correctly rather than treating candidate IDs as arbitrary options.

---

## 11. Scientific interpretation

If the full Agent repeatedly prioritizes candidates near the held-out modifier coordinates while the ablations degrade, a defensible result is:

> A formulation hypothesis constructed from the original local design and independent external PUR evidence defined a coarse acrylic/tackifier candidate space. In a held-out-result blind replay, the uncertainty-aware Agent preferentially ranked candidates compositionally close to the later wet-lab follow-up formulation.

Do not write:

> the Agent prospectively discovered the current follow-up formulation

unless a pre-result timestamped recommendation from the actual historical experiment is recovered.

The useful scientific contribution is the **evidence-to-hypothesis-to-decision chain**, not exact recipe memorization.
