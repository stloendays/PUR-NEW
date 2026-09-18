# Stage-1 Blind Historical Replay — Final Report (`stage1_blind_replay_v1`)

**Arm executed:** B (target-blind independent recovery), N = 5
**Arm A (replay fidelity):** audited `FAIL`, **not executed** (protocol amendment A-01)
**Model:** `gpt-5.6-luna`, five real LLM stages per run, 5/5 runs completed
**Blind phase closed:** 2026-09-18T07:35:31Z · **Unblinded:** 2026-09-18T07:35:56Z
**Repo:** `stloendays/PUR-NEW` @ `a6f61f5` · candidate space SHA-256 `2b92e5d976e76b67…`

---

## Headline

The Stage-1 Agent **recovered the scientific problem and the intervention family,
and failed the quantitative target.**

Without ever seeing the wet-lab result, it identified high-temperature isothermal
hold drift as the dominant unresolved failure mode in 5/5 runs, left the
reactive-only design space for a resin-modified formulation in 5/5, and chose the
acrylic axis in 5/5. It then **overshot acrylic loading and dropped the minor
tackifier axis entirely**, landing 10–15 percentage points away from the validated
formulation in the modifier plane. It also declined to make a performance claim at
all: 5/5 frozen records are `uncertainty_probe`, not `performance_candidate`.

This supports a bounded claim about pre-result problem discovery. It does **not**
support a claim that the Agent would have produced the validated recipe.

---

## Results

All rates are `k/5` with 95 % Wilson intervals. N = 5 is small; one run moves any
rate by 20 points.

| Level | Metric | Result | 95 % Wilson |
|---|---|---|---|
| **1** | thermal-hold objective recovery | **5/5** | [0.566, 1.000] |
| 1 | independently chose 120 °C | 5/5 | [0.566, 1.000] |
| 1 | independently chose a 15–60 min window | 4/5 | [0.376, 0.964] |
| **2** | resin-modification intervention | **5/5** | [0.566, 1.000] |
| 2 | acrylic-like modifier | **5/5** | [0.566, 1.000] |
| 2 | minor tackifier | **0/5** | [0.000, 0.434] |
| **3** | near-region hit (modifier L1 ≤ 7.5 pp) | **0/5** | [0.000, 0.434] |
| — | abstention rate | 0/5 | [0.000, 0.434] |
| — | invalid recommendation rate | 0/5 | [0.000, 0.434] |

**Selections:** `S1C49` (AC 20.0 / TK 0.0) ×3, `S1C59` (AC 25.0 / TK 0.0) ×2.
Selection entropy 0.971 bits over 73 admissible candidates.

**Distance to the validated formulation** (normalized total wt%; truth AC 14.0044 / TK 4.1190):

| run | candidate | \|ΔAC\| | \|ΔTK\| | modifier L1 | modifier L2 | overall L1 |
|---|---|---|---|---|---|---|
| 1 | S1C49 | 5.996 | 4.119 | 10.114 | 7.274 | 11.991 |
| 2 | S1C49 | 5.996 | 4.119 | 10.114 | 7.274 | 11.991 |
| 3 | S1C59 | 10.996 | 4.119 | 15.114 | 11.742 | 21.991 |
| 4 | S1C49 | 5.996 | 4.119 | 10.114 | 7.274 | 11.991 |
| 5 | S1C59 | 10.996 | 4.119 | 15.114 | 11.742 | 21.991 |

Every run overshot acrylic and carried the full 4.119 pp tackifier gap. The error is
**systematic, not scattered** — which points at a cause, not noise (see §"Why").

---

## The ten questions

**1. Most commonly identified failure mode.** Time-dependent viscosity drift during
a 120 °C isothermal hold, 5/5. The Planner grounded it in the correct pre-result
numbers, e.g. *"Hold instability ranges from modest for E1 (SI 0.095 at 60 min) …
to severe drift for E5 (SI 0.515 at 15–60 min; 0.931 at 15–90 min)"* — the true
values computable from `thermal_hold.csv` original rows.

**2. Was thermal-hold drift prioritised?** Yes, 5/5, and explicitly *against* the
alternatives. Runs distinguished it from static viscosity and from realization-state
effects: *"distinct from the expected monotonic temperature-driven viscosity
decrease"*, *"rather than a simple nominal-viscosity mismatch"*. The competing
coordinates were also named in the objective text (realization state 5/5,
temperature response 3/5, viscosity level 2/5), so this was a discrimination, not a
single-option default.

**3. Resin-modification intervention proposed autonomously?** Yes, 5/5. This was a
real choice: 9 of 73 candidates were reactive-core-only, including all five measured
formulations and four interpolations, and the Agent rejected all of them.

**4. Acrylic-like direction found?** Yes, 5/5 — but at 20–25 %, not the ~14 % that
worked.

**5. Minor tackifier found?** **No, 0/5.** Not overlooked — deliberately excluded.
The Proposer considered mixed-modifier candidates and rejected them for
single-variable attribution: *"It is preferable to selecting a mixed-modifier point
because the result can discriminate intervention direction while retaining the E2
reactive-core anchor"*, *"preserving a clean attribution to the acrylic-like axis"*.
That is defensible first-experiment design, and it is also the single largest source
of the Level-3 miss.

**6. Distance to the successful formulation.** Modifier-plane L1 = 10.11 pp (3 runs)
and 15.11 pp (2 runs); mean 12.11, median 10.11. No run reached the pre-declared
7.5 pp near-region threshold. Exact recovery was impossible by construction — the
truth is not a lattice node; the nearest node `S1C41` (15.0, 5.0) sits 1.877 pp away
and **was never selected**.

**7. Stability across runs.** High. Two adjacent candidates on one axis, entropy
0.971 bits, zero abstentions, zero invalid records, and `uncertainty_probe` in 5/5.
The Agent is consistent — consistently displaced.

**8. Which stage contributed most.** Two distinct answers:
- **Planner** produced the Level-1 discovery. The failure mode, the 120 °C target
  and the hold-vs-temperature separation are all present in its output before any
  candidate is ranked.
- **Robustness Adjudicator** controlled the final decision. The Proposer recommended
  `performance_candidate` in **5/5** runs; the Robustness Adjudicator downgraded to
  `uncertainty_probe` in **5/5**; the Judge followed it every time. It is the
  decisive stage, and it is what kept the Agent from overclaiming.

**9. Leakage risk.** Arm B audit verdict **PASS** (0 critical, 0 high). Beyond the
structural audit there is strong *behavioural* evidence of genuine blindness:

> **0/5 runs proposed the 45-minute time point; 5/5 proposed 90 minutes.**

45 min exists only in the follow-up measurement; 90 min exists only in the original
E1/E5 data. The Agent reconstructed the *pre-result* sampling grid and never the real
experiment's. A leaking agent would have done the opposite.

Residual risks, unremoved and declared: the prompts name thermal-hold stability
inside a symmetric four-coordinate taxonomy (audit LEAK-5), so Level-1's uninformed
baseline is 1-of-4, not zero; and the payload discloses the bare string `F1` as a
blinded id with no composition or outcome (LEAK-6).

**10. Does this support a "pre-result Agent-guided formulation decision" claim?**
**Partially — and only if the claim is stated at the level the evidence reaches.**

Supportable:
> From pre-result evidence alone, the Stage-1 Agent independently identified
> high-temperature hold viscosity drift as the dominant unresolved failure mode
> (5/5), independently selected 120 °C and a 15–60 min matched hold window as the
> adjudicating measurement (5/5 and 4/5), and moved out of the reactive-only
> formulation space into an acrylic-resin-modified family (5/5) — the same problem
> and the same intervention family that the later wet-lab work validated.

Not supportable:
> that the Agent would have produced, or come close to, the validated formulation.
> It overshot acrylic by 6–11 pp, omitted the tackifier axis in every run, reached
> the near-region threshold 0/5 times, and never issued a performance recommendation
> at all.

Reviewers will check the gap between those two statements. It should be written into
the manuscript, not argued around.

---

## Why the quantitative target was missed

Three causes, in order of contribution. All are diagnosable from the frozen records.

**1. The external-evidence action failed in every run — a genuine software defect.**

```
TOOL OK    : get_state_aware_rheology_summary 5,  get_candidate_hypothesis 5
TOOL ERROR : query_external_priors 5,  get_repeatability_risk 4,
             get_hold_stability 4,  get_temperature_support 3,  inspect_formulation 1
```

All failures are argument-name mismatches, e.g.
`query_external_priors() got an unexpected keyword argument 'scope'`,
`get_hold_stability() missing 1 required positional argument: 'formulation_id'`.

Root cause: `configs/action_catalog.json` documents action *names* and *when to use*
them but declares **no parameter schema**, and the Planner prompt passes only names.
The Planner therefore invents argument names.

Consequence: `query_external_priors` — which carries H01/H02, the concrete
4.8–5.3 % tackifier examples — returned **nothing in 5/5 runs**. The Agent reached
the acrylic anchors only through `get_candidate_hypothesis`, whose summary leads with
the acrylic grid. The tackifier axis lost its strongest evidential support at exactly
the moment it was being weighed against attribution cleanliness.

**2. Deterministic scorecards pull toward ~20 %, and the truth is at 14 %.**
`compare_candidate_to_priors` scores analogue support against literature anchors
clustered at 19.37–19.98 and 25.0. Candidates at 20 % score `strong_analogue_region`
with near-zero axis distance; 15 % scores strong but with 4.37 pp distance. The
deterministic layer therefore *rewards* the overshoot. This was noted before running
(audit §5.3) and is confirmed: the two selected candidates are exactly the two
strongest-analogue acrylic nodes.

**3. Single-axis attribution preference.** As quoted in Q5 — sound experimental
design, wrong answer here.

Note that causes 1 and 2 both push the same direction, which explains why the error
is systematic rather than scattered.

---

## What was not done, and what it costs

- **Arm A was not run.** No replay-fidelity claim may be made in either direction.
  The repository's replay artifacts are byte-for-byte unmodified and the arm remains
  runnable.
- **N = 5, not 10.** Every interval above is wide. 5/5 has a Wilson lower bound of
  0.566, not 1.0.
- **No v2.** The tool-schema defect is identified but **not fixed**, deliberately.
  Fixing it and re-running would produce a result obtained after seeing the outcome.
  Any fix belongs in `stage1_blind_replay_v2` with recorded changes; this v1 is not
  overwritten.

## Recommended next step

Fix `configs/action_catalog.json` to declare per-action parameter schemas and pass
them to the Planner, then run `stage1_blind_replay_v2` — pre-registered, N = 10,
same candidate space, same evidence snapshot. That tests one falsifiable hypothesis:

> the tackifier axis was dropped because its supporting evidence never loaded.

If v2 recovers the tackifier axis, the Level-2 result strengthens and the cause is
established. If it does not, the single-axis attribution preference is the real cause
and the Agent's quantitative reach is genuinely limited. Either outcome is
publishable; the current v1 result stands regardless.

---

## Artifacts

```
results/stage1_blind_replay_v1/
  blindness_audit_arm_a.json          FAIL — 1 critical, 1 high
  blindness_audit_arm_b.json          PASS — 0 critical, 0 high
  arm_b_blind/
    run_001..run_005/                 run_log.json + recommendation.json + deliberation.json
    run_manifest.json                 model, hashes, temperature policy, timings
    frozen_recommendations.csv
    blind_summary.json                computed with no access to the outcome
    BLIND_PHASE_CLOSED.json           closure timestamp, git SHA, per-record SHA-256
    post_unblind_adjudication.csv
    adjudication_summary.json
  _prefix_harness_failure_arm_b/      pre-fix failure, 0 frozen recommendations
  _aborted_run_006/                   aborted by amendment A-01, excluded from all statistics
docs/STAGE1_BLIND_REPLAY_PROTOCOL.md  protocol + amendment A-01
docs/STAGE1_BLINDNESS_AUDIT.md        full audit, LEAK-1..LEAK-6
```

Integrity: `adjudicate` refuses to run unless `BLIND_PHASE_CLOSED.json` exists and
re-verifies the SHA-256 of `frozen_recommendations.csv` against the closure record
before scoring. No recommendation was modified after closure.
