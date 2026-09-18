# Stage-1 Blindness Audit

**Audit date:** 2026-09-18
**Repository:** `stloendays/PUR-NEW`
**Audited commit:** `a6f61f54a2d577452fa865e18ef6b60cf08364ec` (+ one schema fix, see §6)
**Auditor tooling:** `scripts/audit_stage1_blindness.py` (programmatic, not prompt-based)
**Machine-readable verdicts:** `results/stage1_blind_replay_v1/blindness_audit_arm_{a,b}.json`

---

## 1. What this audit is for

The Stage-1 Agent is to be tested on whether it can, using **only pre-result
evidence**, identify the real unresolved rheological failure mode and recommend a
next formulation experiment that later turned out to be supported by wet-lab work.

That claim is only meaningful if the later wet-lab answer is provably unreachable
from inside the Agent runtime. This audit establishes reachability structurally —
by inspecting every artifact the runtime actually reads — rather than by trusting
the model not to look.

**Held-out truth (never loaded during any Stage-1 run):**

| quantity | value |
|---|---|
| source-reported parts | PPG2000 39.60 / PDP70 39.60 / AC1920 17 / TK100 5 / MDI 20.19 |
| normalized total wt% | PPG2000 32.6221 / PDP70 32.6221 / **AC1920 14.0044** / **TK100 4.1190** / MDI 16.6323 |
| 120 °C hold outcome | mean absolute SI₁₅→₆₀ = 1.60 % |

---

## 2. Runtime reachability map

`scripts/run_scientific_agent_v3.py` reads exactly the following at runtime. Files
not on this list (`docs/`, `manuscript/`, `README.md`, `records/`,
`configs/blind_benchmark_v2.json`) are **not reachable** by the Agent and cannot
leak, regardless of their content.

| surface | reachable | leakage status |
|---|---|---|
| `configs/agent_v3.json` | yes | clean |
| `configs/evidence_access_profiles.json` | yes | clean (control flags only, §5) |
| `configs/workflow.json` | yes | clean |
| `configs/action_catalog.json` | yes | clean |
| `configs/formulation_priors.json` | yes | clean of target coordinates |
| `prompts/agent_v3_*.txt` (×5) | yes | clean of target coordinates (but see §4, LEAK-5) |
| `derived/evidence_state.json` → firewall | yes | filtered, verified clean |
| `data/formulations.csv` | via action | **contains F1 (17/5)** — blocked, see LEAK-3 |
| `data/thermal_hold.csv` | via action | **contains F1 outcome** — blocked, see LEAK-3 |
| `data/temperature_sweeps.csv` | via action | no F1 rows |
| `data/external_evidence_hints.csv` | via action | genuine pre-result literature |
| candidate set (CLI argument) | yes | **arm-dependent — the decisive surface** |

---

## 3. Verdicts

| arm | candidate set | n | sha256 (prefix) | critical | high | verdict |
|---|---|---|---|---|---|---|
| **A — replay fidelity** | `configs/historical_replay_candidate_set.json` | 7 | `b80e1797ada48320` | 1 | 1 | **FAIL** |
| **B — target-blind** | `derived/stage1_blind_candidate_space_v1.json` | 73 | `2b92e5d976e76b67` | 0 | 0 | **PASS** |

**Only Arm B may be scored as independent pre-result discovery.** Arm A remains a
legitimate and useful experiment, but exclusively as *replay fidelity*, which is
also how the repository itself labels it.

---

## 4. Findings

### LEAK-1 — exact posterior coordinates in the replay candidate set — **CRITICAL**

`configs/historical_replay_candidate_set.json` → `RPL_C04`:

```json
"AC1920": 14.0044484718675,
"TK100":  4.11895543290222
```

These reproduce the held-out normalized truth to ~10 significant figures. A
selection of `RPL_C04` is not evidence of discovery; the answer is a coordinate in
the search space.

### LEAK-2 — the replay contract deterministically selects the answer — **CRITICAL**

`configs/pre_result_replay_contract.json` imposes:

```
require_resin_modified            : true
require_acrylic_like_modifier     : true
require_minor_tackifier_like_modifier : true
acrylic_pct_total_max             : 15.0
tackifier_pct_total_min / max     : 3.0 / 7.0
deterministic_tie_break[0]        : minimum_total_modifier_pct
```

Measured admissibility (`evaluate_contract`, no API):

```
eligible : ['RPL_C04', 'RPL_C07']
selected : RPL_C04
```

The constraint box is drawn tightly around (14.00, 4.12), and the first tie-break
prefers the lower total modifier — `RPL_C04` (18.12 %) over `RPL_C07` (20.00 %).
Under `--selection-mode strict` the runner passes **one** candidate to the LLM
(`chosen_ids = ranked[:1]`), so the model has no decision to make at all.

*Arm A was therefore run in `audit` mode (2 candidates), which is the weakest
defensible form of this arm, and is still not independent discovery.*

### LEAK-3 — raw follow-up data reachable through the action layer — **CRITICAL, MITIGATED**

`inspect_formulation()` and `get_hold_stability()` read `data/formulations.csv` and
`data/thermal_hold.csv` with no internal stage filter, so `inspect_formulation("F1")`
would return `AC1920=17, TK100=5` directly.

Mitigation is present and was **verified by execution**, not assumed.
`execute_planned_actions()` blocks any request whose `formulation_id` is in
`blinded_target_formulation_ids` (`["F1"]`). Probe result:

```
inspect_formulation(F1)     -> blocked_by_evidence_firewall
get_hold_stability(F1)      -> blocked_by_evidence_firewall
get_repeatability_risk(F1)  -> blocked_by_evidence_firewall
get_temperature_support(F1) -> blocked_by_evidence_firewall
(all non-F1 probes -> ok)
```

Filtered evidence state under `blind_pre_result` exposes hold data for `E1, E5`
only, stage `original` only, `follow_up_mean_profiles = []`, and none of the eight
F1 viscosity values.

**Residual risk:** the block is enforced at the orchestration layer, not inside the
loader. Any future caller that invokes `execute_action()` directly would bypass it.

### LEAK-4 — pre-specified measurement plan and hold schedule — **HIGH / MODERATE**

`RPL_C04` alone carries:

```json
"measurement_plan": {"temperature_c": 120, "time_points_min": [15,30,45,60], "independent_repeats": 2}
```

This exactly matches the real validation experiment. Decisively, **45 min does not
exist anywhere in the pre-result data** — original E1/E5 holds are sampled at
15/30/60/90 min. The 45-min point can only have come from the follow-up
measurement. It is also a structural tell: it is the only candidate with the field.

Separately, all 7 replay candidates hard-code `hold_temperature_c = 120`,
`hold_time_min = 60`. That pre-announces *that the experiment is a thermal-hold
test*, which is precisely the Level-1 question the Agent is supposed to answer for
itself.

Arm B carries **no** `measurement_plan` and **no** hold schedule on any of its 73
candidates; every process field is `null`. The Agent must derive the experiment and
its own falsifiable acceptance criterion.

### LEAK-5 — soft prompt prior on the answer category — **MODERATE, NOT REMOVED**

The stage prompts repeatedly name thermal-hold stability as one of the decision
coordinates, e.g. planner: *"distinguish viscosity level, temperature response,
thermal-hold stability, and realization/process state"*, and *"when hot-hold drift
is the observed failure mode, do not optimize only a nominal viscosity value"*.

These are **conditional** framings inside a symmetric 4-way taxonomy, not
assertions that hot-hold drift *is* the failure mode. But they do raise the
salience of the correct category.

**This was deliberately left unmodified.** The task was to test the existing
strengthened Stage-1 Agent, not to rewrite it. The honest consequence is stated in
the interpretation rules below: Level-1 recovery is measured against a 1-of-4
uninformed baseline, not against a blank slate, and Level-1 alone is the weakest of
the three levels of evidence.

### LEAK-6 — residual metadata disclosure — **LOW**

The filtered payload retains `evidence_access_filter.blinded_formulation_ids = ["F1"]`
— the bare identifier of the blinded formulation, with no composition, no
measurement and no outcome. It discloses only *that* something is held out. Left
unmodified as part of the designed firewall's self-documentation.

### NOT a leak — control-flag names

`allow_post_result_adjudication`, `post_result_criteria_rewrite_allowed` and
similar contain post-result wording because they are the switches that keep that
information out. Their **values** are asserted closed by `audit_gate_values()`:
all three post-result gates are `false` for `blind_pre_result`, and
`post_result_criteria_rewrite_allowed` is `false`.

### NOT a leak — substring artifact

An earlier scanner pass flagged `'1189'` (an F1 viscosity) inside
`configs/historical_replay_candidate_set.json`. It was a substring of the leaked
coordinate `4.11895543290222`, not a viscosity value. The scanner now requires
digit boundaries. The underlying leak (LEAK-1) stands; the reported reason was
corrected.

---

## 5. Arm B candidate-space provenance

Generator: `scripts/build_stage1_blind_candidate_space.py`
Per-candidate table: `derived/stage1_blind_candidate_provenance.csv`

| family | n | why admissible | evidence | dimension introduced | post-result influence |
|---|---|---|---|---|---|
| measured reactive-core-only (E1–E5) | 5 | exactly the measured local design points | `data/formulations.csv`, `temperature_sweeps.csv`, `thermal_hold.csv` | original local 5-point design | none |
| interpolated reactive-core-only | 4 | strict midpoints between measured points; no extrapolation | same | original local 5-point design | none |
| uniform modifier lattice on E2 core | 64 | chemically plausible resin-modified reactive PUR within externally documented loading ranges | H01–H06, H08, H09, H10, H13 | external curated PUR literature; the local E1–E5 design contains **no** resin modifier and cannot inform this axis | none |

**Generation rule (pre-registered, outcome-independent):**

- reactive core anchored on **E2**, read from `formulations.csv` — E2 is the
  geometric centre of the measured design (50/50, NCO:OH 1.80).
- acrylic-like axis: uniform lattice **0 → 30 wt%, step 2.5**. Upper bound = first
  node at or above the largest directly commensurate external anchor (25 wt%,
  US6465104B1 Ex. 10/11).
- tackifier-like axis: uniform lattice **0 → 10 wt%, step 2.5**. Upper bound =
  explicit "below about 10 wt%" guidance (US20070155859A1).
- both lattices anchored at zero with a fixed step; neither step nor bound is
  derived from any later measurement.

**Integrity properties:**

1. The held-out truth **is not a node of the lattice.** Nearest node is
   `S1C41` = (AC 15.0, TK 5.0), L1 distance **1.877 pct-points**. Exact composition
   recovery is therefore *impossible by construction* — only region and direction
   can be scored, which removes the "suspiciously exact hit" failure mode entirely.
2. Staying reactive-only is a **genuinely competitive** option: 9 of 73 candidates
   carry zero modifier, including all five measured formulations.
3. The deterministic scorecard layer pulls **away** from the truth, not toward it:
   `compare_candidate_to_priors` scores analogue support against literature anchors
   clustered at 19.4–20.0 % acrylic, so ~20 % scores better than ~14–15 %. Any
   movement toward the truth must come from the Agent's reasoning, not from the
   deterministic aids.
4. Candidate IDs (`S1C01`…`S1C73`) encode no rank, no coordinate and no historical
   identity. Ordering is lattice-systematic and identical across all runs.

---

## 6. Repository modifications made for this audit

Minimum necessary, per the instruction not to redesign the Agent.

| change | type | reason |
|---|---|---|
| `schemas/candidate_set.schema.json` +2/−1 | **bug fix** | `additionalProperties: false` rejected `RPL_C04.measurement_plan`, so `run_pre_result_replay_agent.py` crashed at `validate()`. The replay path could not execute at all. Field added as optional, documented as prohibited for blind discovery sets. |
| `scripts/build_stage1_blind_candidate_space.py` | new file | builds the Arm B space; touches nothing existing |
| `scripts/audit_stage1_blindness.py` | new file | this audit |
| `scripts/run_stage1_blind_replay.py` | new file | run driver |

**No existing Agent code, prompt, config or candidate set was modified.**
`configs/historical_replay_candidate_set.json` and
`configs/pre_result_replay_contract.json` are preserved byte-for-byte, deliberately,
so the replay arm remains reproducible as designed.

---

## 7. Interpretation rules binding on the final report

1. Arm A results may be reported **only** as replay fidelity. The phrases
   "independent discovery", "blind recovery" and "pre-result discovery" are not
   available to Arm A.
2. Arm B Level-3 quantitative agreement is a **distance**, never an exact match —
   the truth is not in the space.
3. Level-1 (thermal-hold objective) recovery must be reported alongside LEAK-5. The
   uninformed baseline is 1-of-4 across the prompt's own coordinate taxonomy, not
   zero.
4. A high Arm B exact-region hit rate is a **leakage signal to investigate**, not a
   success to celebrate.
5. Recommendations are frozen before unblinding. Post-result criterion rewriting is
   prohibited and is enforced by `workflow.json::post_result_criteria_rewrite_allowed = false`.
