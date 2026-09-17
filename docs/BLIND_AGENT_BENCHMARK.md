# Full-Agent held-out-result replay benchmark — V2

## Objective

PUR-NEW now separates two evidence layers:

1. **primary Agent validation chronology** — the research team confirms that the Agent-selected validation formulation was recommended before its wet-lab result was known to the Agent, then physically tested by humans;
2. **secondary V2 replay benchmark** — a later formalized 12-candidate grid is used to test whether the reproducible evidence stack prioritizes a region compatible with that validation formulation when its composition/outcome is hidden from the evaluated model.

This document defines the second layer.

See `docs/EXPERIMENTAL_CHRONOLOGY.md` for the primary historical chronology.

## Historical status

The Agent-selected validation formulation is the internal `F1` formulation:

```text
PPG2000 = 39.60
PDP-70  = 39.60
AC1920  = 17
TK100   = 5
MDI     = 20.19
```

The research team confirms that this recommendation preceded knowledge of its corresponding wet-lab result.

However, the current exact V2 `4 x 3` grid was formalized later. Therefore V2 is a **secondary held-out-result replay / reproducibility benchmark**, not the artifact that establishes the historical prospective claim.

The two provenance questions are different:

```text
Was the validation formulation recommended before its result was known?
-> author-confirmed: yes

Did the current exact V2 software grid already exist in this form at that time?
-> not established by the current repository
```

## 1. Replay question

The V2 benchmark asks:

> If an evaluated Agent is given the original local rheology, state-aware descriptors, uncertainty-aware actions, external PUR evidence and the later formalized V2 candidate space — but is blinded to the Agent-selected validation formulation and its wet-lab outcome — does it prioritize candidates in a compatible acrylic/tackifier region?

This evaluates reproducibility and evidence integration, not historical timestamp provenance.

## 2. What the evaluated replay Agent may see

```text
original local evidence
+ state-aware rheology descriptors
+ formulation/process-state uncertainty
+ deterministic Actions
+ V2 evidence-derived candidate hypothesis
+ external PUR database/literature evidence
+ finite V2 candidate set
```

The Agent may inspect:

- original thermal-hold drift;
- original realization/repeat spread;
- E2 as the central reactive-core design point;
- external evidence for acrylic-modified PUR around 15, 20 and 25%;
- external evidence for minor tackifier/hydrocarbon-resin levels around 5% and guidance up to about 10%;
- evidence that acrylic functionality can alter hot-hold viscosity stability;
- process-history missingness and other uncertainty terms.

## 3. What the replay Agent must not see

```text
Agent-selected validation formulation amounts
normalized validation formulation composition
validation thermal-hold measurements
validation adjudication label
nearest-candidate label
controller-side distance threshold
any prose derived from the validation outcome
```

The controller may use those values only after replay outputs are frozen.

## 4. V2 candidate-space formalization

### Reactive-core anchor

E2 is the geometric centre of the original five-point design and normalizes to approximately:

```text
PPG2000 39.9047%
PDP-70  39.9047%
MDI     20.1907%
```

### Acrylic-like axis

```text
0%   control
15%  peer-reviewed reactive-PUR evidence anchor
20%  repeated acrylic-tackifying-resin examples
25%  acrylic-copolymer example with direct hot-hold stability data
```

### Minor tackifier-like axis

```text
0%   control
5%   repeated ~4.8-6.4% resin region
10%  conservative upper coarse level from published guidance
```

### V2 grid

```text
acrylic-like         = {0, 15, 20, 25}%
minor tackifier-like = {0, 5, 10}%
```

Cartesian product: 12 candidates.

For each candidate, the E2 reactive core is scaled into the remaining formulation fraction. The validation recipe is not inserted as an exact candidate and its numeric values are not used to generate the grid.

Generate with:

```bash
python scripts/build_candidate_set.py
```

## 5. Why V2 is still scientifically useful

V2 does not need to be the historical freeze interface to add value.

It provides:

- a reproducible evidence-to-candidate map;
- a clean benchmark for model comparison;
- ablations of database, Actions and explicit candidate-hypothesis context;
- deterministic baselines;
- a future-ready candidate representation for prospective rounds.

The benchmark therefore asks whether the later formalized evidence stack is structurally consistent with the successful validation region, not whether it recreates history by exact recipe memorization.

## 6. Full-Agent replay information flow

```text
original measurements
-> deterministic response descriptors
-> state-aware uncertainty decomposition
-> V2 evidence-derived candidate formalization
-> database retrieval / evidence Actions
-> candidate profiling
-> acrylic-axis and tackifier-axis analogue comparison
-> process-history audit
-> stress test
-> Agent recommendation + alternatives
-> freeze replay output
-> controller-only held-out scoring
```

Relevant Action families:

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

## 7. API output and ranking contract

Every API call should return structured JSON. The raw response is retained, normalized and frozen before scoring.

For a valid non-abstaining recommendation:

```text
Rank 1 = selected_candidate_id
Rank 2 = alternatives_considered[0]
Rank 3 = alternatives_considered[1]
```

Rules:

- alternatives are valid candidate IDs;
- alternatives are unique and strictly preference ordered;
- the selected candidate does not repeat among alternatives;
- `abstain` requires `selected_candidate_id = null`;
- alternatives attached to an abstention are diagnostic only and do not count as primary Top-1/Top-3 recovery.

## 8. Benchmark protocol

Use `configs/blind_benchmark_v2.json`.

Recommended protocol:

```text
pilot: 5 independent runs per model
full benchmark: >=30 runs per model
```

Use identical candidate set, evidence profile, Action policy, prompt and decoding settings across compared models.

Record valid recommendations, abstentions, invalid outputs and API failures; do not silently discard failures.

## 9. Controller-side scoring

After replay recommendations are frozen, the controller may compare rankings with the validation formulation in the two-dimensional modifier plane:

```text
(acrylic-like %, minor-tackifier-like %)
```

Primary replay metrics:

```text
nearest-candidate rank
nearest-candidate Top-1 recovery
nearest-candidate Top-3 recall
Top-1 L1 distance to validation coordinates
best Top-3 L1 distance
resin-modified Top-1 rate
selection distribution
abstention rate
scientific-boundary violation rate
```

Distance-based scoring is preferred over the old scalar combined-modifier target.

## 10. Baselines and ablations

Baselines:

```text
uniform_random
transparent_support_ranker
database_only_axis_ranker
```

Ablations:

```text
full_agent_v2
without_external_database
without_action_enrichment
literature_only_sanity
without_candidate_hypothesis_context
```

If a deterministic evidence ranker already places the validation-near cell first, the Agent contribution should be evaluated through evidence integration, uncertainty handling, robustness, abstention and alternative ranking rather than discovery alone.

## 11. Scientific interpretation

A defensible replay result is:

> A later formalized candidate hypothesis, constructed from the original local design and independent PUR evidence, defined a coarse acrylic/tackifier search space. When the Agent-selected validation formulation and its outcome were hidden, the evidence-using Agent preferentially ranked candidates in a compositionally compatible region.

Do **not** use the V2 replay itself as the provenance proof that the historical recommendation was prospective.

The historical Agent-to-lab claim is documented separately:

> The research team confirms that the validation formulation was recommended before its subsequent wet-lab result was known to the Agent; human execution then produced a low-drift response that supported the recommendation with respect to thermal-hold stability.

The current repository also states transparently that the original contemporaneous freeze artifact has not yet been recovered.
