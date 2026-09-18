# Stage-1 Blind Historical Replay Protocol (`stage1_blind_replay_v1`)

**Protocol frozen:** 2026-09-18, before any run was executed.
**Repository:** `stloendays/PUR-NEW` @ `a6f61f5` (+ one schema bug fix, audit §6)
**Prerequisite:** `docs/STAGE1_BLINDNESS_AUDIT.md` verdict for the scored arm must be `PASS`.

---

## 1. Question

> If we had only the pre-result evidence, would the strengthened Stage-1 scientific
> Agent have arrived on its own at the scientific direction that the later wet-lab
> experiment supported?

This is a blind historical replay / pre-result simulation. The Agent is restored to
the state of knowledge that existed **before** the validation formulation was made
or measured.

## 2. Two arms, two different claims

| | Arm A — replay fidelity | Arm B — target-blind recovery |
|---|---|---|
| candidate set | `configs/historical_replay_candidate_set.json` (unmodified) | `derived/stage1_blind_candidate_space_v1.json` |
| n candidates | 7 (2 contract-admissible) | 73 |
| contract | `configs/pre_result_replay_contract.json` (unmodified) | none beyond the Agent's own architecture |
| blindness verdict | **FAIL** (exact posterior coordinate present) | **PASS** |
| supports the claim | "the Agent reproduces the historical recommendation" | "the Agent independently recovers the scientific direction" |
| does **not** support | independent / blind discovery | exact recipe recovery (truth is not in the space) |

Both are run. They are frozen separately and never pooled.

## 3. Agent under test

The existing strengthened Stage-1 Agent, unchanged:

```
pre-result evidence
  → Planner
  → scientific Actions / evidence layer (+ deterministic scorecards, Pareto, robustness scenarios)
  → Proposer
  → Skeptic
  → Robustness adjudicator
  → Judge
  → programmatic freeze
```

Entry point `scripts/run_scientific_agent_v3.py`, architecture `configs/agent_v3.json`
v3.3.1, five real LLM stages. Not a single-pass LLM, not a deterministic mock, not
smoke mode.

## 4. Evidence available to the Agent

Profile `blind_pre_result`.

**Allowed:** original E1–E5 formulations; chemistry-audited temperature sweeps
(`E1 +P` retained as `sensitivity_only` because it is phosphoric-acid-labelled;
`GJJ`/`ZYX`/`CHH` treated as same-operator realization labels, not different
operators; `viscosity_reported` kept unit-free); original E1/E5 thermal-hold data;
the paper-derived state-aware rheology tool; curated external PUR
literature/patent evidence under the hierarchy
`local experiment > derived local model result > directly commensurate external > directional external`.

**Structurally removed before any payload is assembled:** the follow-up formulation
identity, its composition, its thermal-hold measurements, derived post-result
statistics, and adjudication labels. Enforcement is programmatic
(`filter_evidence_state`, `assert_blind_payload_clean`, action-layer blocking),
verified by execution, and re-verified by `scripts/audit_stage1_blindness.py`.

## 5. Task given to the Agent

The Agent is **not** told what the failure mode is. It receives the standing
architecture instruction to review formulation, temperature-dependent rheology,
thermal-history behaviour, state-aware analyses, uncertainty and external PUR
evidence; determine the most scientifically justified next formulation experiment;
identify the dominant unresolved failure mode; decide what property to improve;
recommend one actionable formulation or region; compare alternatives; state
uncertainty; and define a falsifiable acceptance criterion.

No candidate carries a measurement plan or hold schedule in Arm B, so the
measurement window and the acceptance threshold are the Agent's own output.

## 6. Run configuration

| item | value |
|---|---|
| runs per arm | 10 independent |
| model | `gpt-5.6-luna` (same model for all five stages, all runs) |
| temperature | **not sent** — endpoint rejects the parameter (verified: `400 Unsupported parameter: temperature`). Model default sampling retained; stochasticity comes from repeated independent calls. |
| seed | endpoint exposes none; `run_index` recorded instead |
| evidence snapshot | one `derived/evidence_state.json`, SHA-256 recorded in each arm manifest |
| candidate space | one per arm, SHA-256 recorded |
| prompts / tools / permissions | identical across all runs |
| retention | every attempt kept, including errors, abstentions and anomalous selections |

## 7. Freeze

Each run writes an immutable record containing `recommendation_id`, decision mode,
selected candidate and full composition, process state, alternatives considered,
constraints, decomposed uncertainty, selection rationale, falsifiable acceptance
criterion, model, `prompt_hash`, `input_hash`, `git_commit` and UTC timestamp,
alongside the complete five-stage `deliberation.json`.

`run_scientific_agent_v3.py` refuses to overwrite an existing frozen run directory.
`workflow.json::post_result_criteria_rewrite_allowed = false`.

## 8. Unblinding sequence — strictly ordered

```
PRE-RESULT DATA → STAGE-1 AGENT → FROZEN RECOMMENDATION
                                        ↓
                               BLIND PHASE CLOSED
                     (timestamp + git SHA + per-record SHA-256)
                                        ↓
                          LOAD REAL EXPERIMENT → ADJUDICATE
```

`scripts/score_stage1_replay.py summarize` runs first and may not read the held-out
truth. It emits `frozen_recommendations.csv` and `blind_summary.json` and writes the
closure record. Only then does `... adjudicate` load the truth.

No recommendation may be modified after closure for any reason, including because
the real result is now known.

## 9. Adjudication levels

**Level 1 — scientific target recovery.** Did the Agent independently identify
*time-dependent viscosity drift under high-temperature isothermal hold* as the
dominant unresolved failure mode? Scored from the frozen rationale, acceptance
criterion and the Planner's stated failure mode. Reported together with audit
LEAK-5: the prompts name thermal-hold stability inside a symmetric four-coordinate
taxonomy, so the uninformed baseline is 1-of-4, not zero.

**Level 2 — intervention-family recovery.** Did the Agent leave pure
PPG/PDP/MDI reactive-core tuning for a resin-modified family? Sub-scored for
acrylic-like modifier and for a minor tackifier fraction. Determined from the
selected composition, not from prose.

**Level 3 — quantitative agreement.** Distance between the recommended composition
and the real successful formulation, on the **normalized-total wt% basis** for
`PPG2000, PDP70, AC1920, TK100, MDI`, plus the modifier plane `(acrylic wt%, tackifier wt%)`
reported separately because that is where the decisive intervention information lies.
Euclidean and L1 distances, plus absolute acrylic and tackifier differences.

Basis discipline: source parts `17 / 5` are **never** compared numerically with
normalized coordinates. The normalized equivalents are `14.0044 / 4.1190`.

Metrics are defined here, before unblinding, and are not adjusted afterwards to
improve the Agent's apparent performance.

## 10. Reported statistics (N = 10 per arm)

thermal-hold objective recovery rate · resin-modification intervention recovery
rate · acrylic-like modifier recovery rate · minor-tackifier recovery rate ·
near-region quantitative recovery rate · modifier-plane distance distribution ·
abstention rate · invalid recommendation rate · selection entropy.

## 11. Failure handling

If Arm B results are weak, they are reported as `stage1_blind_replay_v1` and kept.
Diagnosis attributes the failure to a named stage — Planner missed the failure
mode / insufficient Action evidence / state-aware result unused / external evidence
not connected to intervention / Proposer candidate space too narrow / Skeptic
vetoed the correct direction / Judge unstable / uncertainty drove over-abstention.
Any improvement is a **new** `stage1_blind_replay_v2` with recorded changes. v1 is never
overwritten and prompts are never silently tuned after seeing the outcome.

---

## 12. Protocol amendments (recorded, not retro-edited)

### A-01 — 2026-09-18, while still blind

**Change.** Arm B reduced from N = 10 to **N = 5**. Arm A (replay fidelity)
**cancelled** and not executed.

**Instructed by.** The user, mid-series.

**Blindness status at the time of the change.** Arm B run 1 was frozen and run 2
was in flight. `summarize` had **not** been executed, `blind_summary.json` did not
exist, the BLIND PHASE CLOSED record did not exist, and the held-out wet-lab truth
had **not** been loaded by any process. No adjudication of any kind had occurred.
The change therefore cannot have been informed by the outcome.

**Consequences, stated plainly.**

- N = 5 materially widens the uncertainty on every reported rate. A single run moves
  any rate by 20 percentage points. A 5/5 result has a 95 % Wilson lower bound of
  roughly 0.57, not 1.00. Rates must be reported as counts (`k/5`) with the interval,
  never as a bare percentage.
- Selection entropy and the stability claim in Section 10 are correspondingly weaker;
  five draws cannot distinguish a moderately stable policy from a strongly stable one.
- Arm A is audited (`FAIL`, see the audit document) but **unexecuted**. No
  replay-fidelity claim of any kind may be made, in either direction. The repository's
  replay artifacts remain byte-for-byte unmodified and the arm can be run later.
- The original N = 10 / two-arm design remains on record above. This amendment
  narrows what was delivered; it does not redefine what was planned.

**Not changed.** Candidate space, evidence snapshot, prompts, model, tool
permissions, freeze mechanics, Level-1/2/3 definitions and the near-region threshold
are all exactly as specified before the first run.
