# Stage-1 Preexperimental Reconstruction — v2 Strategy Changes

**Base:** `stloendays/PUR-NEW` @ `662297b` ("Refactor Stage-1 into outcome-blind preexperimental reconstruction")
**Strategy frozen:** 2026-09-18T08:19:17Z · combined hash `5f4eb323668ec833…`
**Candidate space:** unchanged from v1 — `derived/stage1_blind_candidate_space_v1.json`, 73 nodes, SHA-256 `2b92e5d976e76b67…`
**Blindness audit:** `PASS` (0 critical, 0 high)

---

## 1. Honest framing, first

The v2 rule set was chosen **after** v1 was run and diagnosed. That is a real
post-hoc influence on *which rules were adopted*, and it must not be described as an
untouched blind prediction.

What makes v2 still interpretable:

- Every rule is justifiable from pre-result evidence or a general
  experimental-design principle, stated without reference to the outcome.
- No target coordinate (`AC1920 = 14.0044`, `TK100 = 4.1190`, source parts `17 / 5`)
  appears in any candidate, prompt, config, prior, threshold or tie-break.
- The candidate lattice is byte-identical to v1, and the validated formulation is
  still **not a node** of it.
- The rules were frozen with hashes before the first run and are not touched
  afterwards.

What this cannot be called: an independent second blind trial. It is a
**pre-registered strategy revision**, evaluated blind.

---

## 2. Changes made upstream in `662297b` (not by this session)

The refactor had already addressed most of items 2–6 before this session started.

| item | change |
|---|---|
| 1 | `parameters` JSON-Schema declared per action in `action_catalog.json`; specs passed to the Planner; `validate_planner_actions` validates args |
| 2 | scenario `hypothesis_test_first` split into `performance_mitigation` and `causal_isolation`; prompts instruct the Planner to classify experiment intent and forbid "clean attribution" as a universal reason to drop a supported secondary modifier |
| 3 | `active_axis_distance_pct_points` demoted to `audit_only_not_primary_rank_objective`; prompts state that analogue distance is audit metadata |
| 4 | `total_modifier_pct` added and minimised in tie-breaks; `MINIMUM_SUFFICIENT_INTERVENTION_V1` policy declared in `formulation_priors.json` |
| 5 | `supported_active_axis_count` added as a primary ranking objective, rewarding candidates whose *every* active axis is independently supported |
| 6 | the `-active_axis_distance` term removed from `_dominates` and from the scenario keys |
| — | leaking replay artifacts (`historical_replay_candidate_set.json`, `pre_result_replay_contract.json`, `replay_contract.py`, `run_pre_result_replay_agent.py`) deleted from the repository |
| — | `normalize_judge_output` added, independently reproducing the v1 fix |

## 3. Changes made in this session

All three are **evidence-plumbing** fixes. None touches scoring, ranking, priors,
thresholds or tie-breaks, and each is symmetric across the two modifier axes.

### C-01 — external evidence is retrieved unconditionally for both axes
`scripts/run_scientific_agent_v3.py::ensure_core_scientific_action`

The Planner requests actions but **never sees their results**; the tool trace goes to
the Proposer. A Planner that omits or misnames the external-evidence call therefore
silently deletes that evidence from the decision. In v1 this happened in 5/5 runs and
`query_external_priors` returned nothing at all.

`query_external_priors` is now injected once per modifier axis — acrylic and
tackifier — in identical form, exactly as the core rheology tool already was.
Symmetry is the point: retrieving one axis but not the other biases the decision
toward whichever axis survives.

*Justification:* `configs/agent_v3.json::required_scientific_sequence` already
declares "use external evidence to identify chemically plausible intervention
directions" as a required step. This makes the declared architecture actually happen.

### C-02 — a malformed action request no longer aborts the evidence trace
`src/pur_new/agent_v3.py::execute_planned_actions`

`validate_planner_actions` raises on a schema violation, and it was called on the
whole batch, so one bad argument name discarded every action including the valid
ones. Each request is now validated individually and a bad one is recorded as
`invalid_arguments` while the rest execute.

*Justification:* robustness only. `validate_planner_actions` keeps its raising
contract, so `tests/test_agent_v3.py` is unchanged.

### C-03 — evidence retrieval uses stem matching
`src/pur_new/actions.py::query_external_priors`

The filter was a literal substring match, so `"tackifier"` did **not** match
`"tackifying resin"` or `"tackifying agent"`. **H01 — the US5932680A 4.8 % example —
was unreachable**, as were H13 and H14. The acrylic axis was unaffected because
`"acrylic"` matches literally.

This is a silent, asymmetric evidence loss: the axis whose vocabulary happened to
match literally kept its sources; the other lost its primary quantitative example.
Matching is now done on morphological stems.

Retrieval after the fix:

```
acrylic   : H03 H04 H05 H06 H08 H09 H10 H11 H12   (9 rows; 15 / 19.4-20.0 / 25 %)
tackifier : H01 H02 H03 H04 H05 H06 H11 H12 H13 H14 (10 rows; 4.8 / 5.3 %, <10 % guidance)
```

*Justification:* a curated pre-result source row that exists in the table must be
retrievable. This restores evidence; it does not weight it.

---

## 4. What was deliberately NOT changed

**`_axis_support` still uses distance thresholds (`strong ≤ 5`, `moderate ≤ 10` pct
points) rather than the declared `evidence_region_policy` regions (`acrylic [15, 25]`,
`tackifier [3, 10]`).**

There is a genuine inconsistency here: `formulation_priors.json` declares supported
*regions* while the scorer bins by *distance*. Aligning them is arguably more correct.

It was not done, because the effect of doing it is to move the deterministic rank-1
from `S1C40` (15.0, 2.5) to `S1C41` (15.0, 5.0) — that is, from 2.615 pp to 1.877 pp
from the validated formulation. A change whose principal visible effect is to reduce
the distance to the known answer cannot be distinguished from tuning, even when an
independent argument for it exists. It is recorded here as a known inconsistency for
a future round that does not already know the answer.

Also unchanged: the candidate lattice, all evidence files, the firewall, the freeze
mechanics, and the Level-1/2/3 scoring definitions and the 7.5 pp near-region
threshold (which predates this work, from `configs/blind_benchmark_v2.json`).

---

## 5. Attribution: what actually moves the result

Deterministic diagnostics only, no LLM, same 73-node lattice, computed **before** the
v2 runs:

| rule set | `evidence_first` | `robustness_first` | mitigation / hypothesis | modifier-L1 to truth |
|---|---|---|---|---|
| v1 `a6f61f5` | S1C59 (25.0, 0.0) | S1C10 (0.0, 2.5) | S1C59 (25.0, 0.0) | **15.115 pp** |
| v2 `662297b` | S1C40 (15.0, 2.5) | S1C40 (15.0, 2.5) | S1C40 (15.0, 2.5) | **2.615 pp** |

The deterministic layer alone accounts for most of the expected improvement, and it
converges on a single candidate in 3 of 4 scenarios. **The LLM stages are therefore
operating on a much stronger prior than in v1**, and any v2 agreement with the real
formulation must be attributed largely to the rule change rather than to model
reasoning.

The measurable LLM contribution in v2 is whether the Agent follows, refines or
overrides `S1C40` — reported in the final results as agreement with, and deviation
from, the deterministic rank-1.

---

## 6. Residual bias check (item 6)

- The v1 pull toward 20–25 % acrylic with `TK = 0` is gone: `-active_axis_distance`
  no longer appears in `_dominates` or in any scenario key.
- `causal_isolation` still ranks a single-axis candidate first (`S1C10`, 0.0 / 2.5).
  That is correct behaviour for that scenario and is no longer the default; the
  Planner must declare `causal_isolation` intent for it to apply.
- Residual proximity sensitivity survives inside `support_value`: acrylic 10–12.5 %
  scores `moderate` while ≥ 15 % scores `strong`, so the strong/moderate boundary
  still favours ≥ 15 %. This is a coarsened distance reward and is declared, not
  removed — removing it is the §4 change that was refused.
- Prompt-level salience of thermal-hold stability (v1 audit LEAK-5) is unchanged.
