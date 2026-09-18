# Does principled strategy revision make a scientific agent measurably better?

**Supersedes the framing of** `STAGE1_V1_TO_V4_FINAL_REPORT.md` (results unchanged; all runs preserved).

---

## 1. The question

The wet-lab experiment is **finished**. F1 was synthesised and measured, and that result is
not under test here. It is used as a **fixed measuring instrument**: a frozen, real-world
answer that never enters the agent runtime and is identical for every strategy version.

The question is therefore not *"did the agent find the recipe?"* but:

> Given a completed experiment as a frozen yardstick, does revising a scientific agent's
> **decision strategy** — using only general experimental-design principles and pre-result
> evidence — produce a **measurable, attributable** improvement in its pre-result decisions?

This is answerable without a single additional experiment. That is the point.

## 2. What varies and what is held constant

| held constant across all versions | varies |
|---|---|
| candidate lattice — 73 nodes, SHA-256 `2b92e5d976e76b67…`, byte-identical | the decision strategy only |
| pre-result evidence snapshot | |
| model `gpt-5.6-luna`, 5 real LLM stages | |
| structural evidence firewall (audit PASS every version) | |
| scoring metric and the 7.5 pp near-region threshold, fixed before any run | |

The held-out formulation is **not a node of the lattice**, so exact recovery is impossible by
construction and only direction/region quality is scorable. The nearest node is
`S1C41 (AC 15.0 / TK 5.0)` at **1.877 pp** — a hard floor.

## 3. The strategy ladder

| ver | strategy change | N | named | abstain | dual-axis | near-region | agent L1 | rule-only L1 | agent − rule |
|---|---|---|---|---|---|---|---|---|---|
| v1 | proximity-reward ranking (baseline) | 5 | 5 | 0 | **0/5** | 0/5 | 12.115 | 15.115 | +3.000 |
| v2 | min-intervention, no coverage gate | 3 | 1 | 1 | 0/1 | 0/1 | 15.623 | 2.615 | −13.009 |
| v3 | + intervention-coverage gate | 5 | 3 | 2 | **3/3** | 3/3 | 1.877 | 2.615 | +0.738 |
| v4 | + deterministic ranking withheld (pilot) | 5 | 4 | 1 | **4/4** | 4/4 | 2.061 | 2.615 | +0.553 |
| **v3h** | same as v4, confirmatory | **10** | 8 | 2 | **8/8** | 8/8 | 2.281 | 2.615 | +0.333 |

Selections:

```
v1    S1C49 (AC 20 / TK 0)  x3,  S1C59 (AC 25 / TK 0) x2
v2    S1C10 (AC 0  / TK 2.5) x1
v3    S1C41 (AC 15 / TK 5)  x3
v4    S1C41 x3,  S1C40 (AC 15 / TK 2.5) x1
v3h   S1C41 x6,  S1C46 (AC 17.5 / TK 5) x1,  S1C40 x1
```

Dual-axis recovery among named runs, 95 % Wilson:
`v1 0/5 [0.00,0.43]` → `v3 3/3 [0.44,1.00]` → `v4 4/4 [0.51,1.00]` → **`v3h 8/8 [0.68,1.00]`**.

v1 and v3h intervals do not overlap. That is the improvement claim, and it is the only
rate comparison here with enough N to carry one.

## 4. Attribution — rule layer vs model layer

Never conflate these. Computed by evaluating the deterministic rule layer alone on the same
lattice, with no LLM:

```
v1 rule-only baseline          15.115 pp
best rule-only baseline         2.615 pp    rule layer contributed  +12.500
best agent mean                 1.877 pp    agent layer contributed  +0.738
total closed                   13.238 pp -> rule 94.4 %  /  agent 5.6 %
lattice floor                   1.877 pp    hard bound
```

**94 % of the distance improvement is the deterministic rule rework, not the model.** Stating
otherwise would be false.

But the model layer is not noise, and it is not a lookup:

- The agent beat its own rule baseline in **every** version that ran to completion
  (+3.000, +0.738, +0.553, +0.333) — small, but consistent in sign across four independent
  strategy configurations.
- In v3h the deterministic rank-1 (`S1C40`) was **withheld from every model payload**, verified
  live in the run records, with all 36 full-coverage candidate identifiers appearing an
  identical number of times. The agent still deviated from it in **7 of 8** named runs and
  still landed on `S1C41` in 6 of 8.

The pre-declared falsifiable prediction registered before v3h ran — *"S1C41 remains the modal
selection among non-abstaining runs"* — is **confirmed**.

## 4b. Baselines — what the architecture is being compared against

Same candidate lattice, same pre-result evidence, same model, same metric. The naive
baseline view is built by `scripts/build_naive_baseline_view.py` and verified to contain
no F1 row, no follow-up stage and none of the follow-up viscosity values.

| arm | N | named | near-region | modifier L1 | dual-axis |
|---|---:|---:|---|---:|---|
| naive single-pass LLM | 10 | 7 | **0/7** | **18.123** | 0/7 [0.00, 0.35] |
| transparent support ranker | 1 | 1 | 0/1 | 15.623 | 0/1 |
| uniform random over the lattice (exact) | — | — | **24.7 %** | 12.074 | 65.8 % |
| **agent (v3h)** | 10 | 8 | **8/8** | **2.281** | 8/8 [0.68, 1.00] |

The **near-region metric is the more discriminating lattice-level endpoint**: only 18 of
73 candidates (24.66 %) lie within the predeclared 7.5 percentage-point L1 region, whereas
48 of 73 (65.75 %) are merely nonzero on both modifier axes. Thus dual-axis recovery is best
read as directional intervention-family recovery, while near-region recovery and modifier-plane
L1 quantify whether the decision concentrated in the experimentally supported neighborhood.
Under independent uniform draws from the frozen lattice, eight consecutive near-region hits
would occur with probability approximately **1.37 × 10^-5**; this is a descriptive lattice
null, not a substitute for the predeclared benchmark analysis.

**The naive single-pass LLM performs worse than chance on both direction and region.** All 7
of its valid runs selected `S1C01` — the reactive-core-only E1 composition — so it never
left the measured chemistry and never entered the near region. The failure is systematic,
not noisy: the same wrong candidate every time.

This is the comparison that establishes the scaffolding is doing the work. Naive-LLM invalid
output rate was 3/10; three follow-up diagnostic invocations all succeeded, so those failures
are transient rather than systematic.

## 4c. Cross-model transfer

Identical protocol, deterministic ranking withheld, run on two further models from the same
endpoint.

| model | N | named | abstain | dual-axis | near-region | modifier L1 | selections |
|---|---:|---:|---:|---|---|---:|---|
| gpt-5.6-luna | 10 | 8 | 2 | 8/8 [0.68, 1.00] | 8/8 | 2.281 | S1C41 ×6, S1C46 ×1, S1C40 ×1 |
| gpt-5.5 | 5 | 4 | 0 | 4/4 [0.51, 1.00] | 4/4 | **1.877** | S1C41 ×4 |
| gpt-5.6-sol | 5 | 2 | 3 | 1/2 [0.09, 0.91] | 1/2 | 10.000 | S1C41 ×1, S1C02 ×1 |

`S1C41` is the modal selection for **every** model tested, and 13 of 14 named runs across all
three models selected a dual-axis candidate. Series are reported separately and never pooled.

Reliability, unlike direction, is model-dependent: gpt-5.6-sol abstained in 3 of 5 runs and
once selected a reactive-core-only composition. The intervention direction transfers across
models; the willingness to commit to a named candidate does not.

## 5. Failure modes were diagnosed and corrected without touching the target

This is the part that generalises.

| version | observed failure | diagnosis | correction (general principle only) |
|---|---|---|---|
| v1 | 0/5 dual-axis; locked on 20–25 % acrylic, TK = 0 | the ranking rewarded proximity to a literature anchor, so the axis with the tightest anchor cluster dominated | literature defines a supported *region*, not an optimum |
| v2 | zeroed a supported axis to cut modifier burden (`S1C10`, 15.6 pp) | minimum-sufficient-intervention applied *before* intervention sufficiency | sufficiency first, perturbation size only as a tie-break within sufficient candidates |
| v3 | agreement with a *shown* deterministic ranking is unfalsifiable | the answer was visible in the payload | withhold ordering; keep the gate and per-candidate evidence |

No correction used a target coordinate. `14.0044`, `4.1190`, `17`, `5` appear in no candidate,
prompt, config, prior, threshold or tie-break — verified by the automated blindness audit,
which returns PASS for every version.

Independent behavioural evidence of genuine blindness: across v1, **0/5 runs proposed the
45-minute time point and 5/5 proposed 90 minutes**. 45 min exists only in the follow-up
measurement; 90 min only in the original E1/E5 data. The agent reconstructed the *pre-result*
sampling grid, never the real experiment's.

## 6. The AI4Science claim

What this demonstrates as a method, independent of the PUR chemistry:

1. **Agent decision quality can be measured rather than asserted**, provided a frozen
   real-world outcome and a firewall enforced in code rather than in prompt text.
2. **Improvement can be attributed** between the deterministic rule layer and the model layer,
   by evaluating the rule layer alone on the identical candidate space. Without this
   decomposition, a 13 pp improvement would have been silently credited to the LLM; 94 % of it
   belongs to the rules.
3. **Agent failure modes are diagnosable and correctable by general design principles** —
   evidence-region-not-optimum, sufficiency-before-minimality, withhold-the-precomputed-answer —
   none of which reference the target.
4. **The entire ladder consumed zero additional wet-lab work.** Experiments are expensive and
   often unrepeatable; agent iteration is cheap. A completed experiment can therefore be
   converted into a reusable benchmark for agent development, which is where the practical
   value lies for a group that cannot simply run more experiments.

## 7. Limitations, stated hard

1. **n_targets = 1.** Every rate and distance is measured against a single held-out
   formulation. Four strategy revisions against one target is the central overfitting risk in
   this work, and no internal control removes it. The mitigations — no coordinates anywhere,
   general principles only, fixed lattice, truth not a node, rule/agent decomposition reported
   separately — reduce but do not eliminate it. **A second held-out formulation is the single
   most valuable thing this line of work could acquire.**
2. **Strategy selection was informed by seeing earlier versions fail.** Not by outcome values,
   but failure modes correlate with distance to the target. This is a pre-registered revision
   sequence evaluated blind, not five independent blind trials.
3. **The supported acrylic region floor (15 wt%) sits just above the true value (14.004).**
   All 18 named selections across v3/v4/v3h chose exactly 15.0. Part of the apparent accuracy
   is where that boundary was drawn. Had the true optimum been below the floor, this
   configuration could not have reached it.
4. **Residual errors are systematically positive on both axes** (ΔAC +1.0, ΔTK +0.88), because
   both sit at region/lattice boundaries rather than at evidence optima.
5. **Judge output-contract instability persists**: 10–40 % abstention across versions, caused by
   the Judge emitting `selected_candidate_id: null` while its own Robustness stage names a
   preferred candidate. A prompt/freezer inconsistency, not scientific indecision. Left unfixed
   under the freeze rule.
6. **1.877 pp is a floor, not a resolution.** Further distance reduction requires a finer
   lattice, whose justification must be fixed before consulting the outcome.

## 8. What may and may not be written

May:
> Using a completed wet-lab result as a frozen, outcome-blind benchmark, we show that revising a
> scientific agent's decision strategy using only general experimental-design principles moves
> its pre-result recommendations from 0/5 to 8/8 near-region recovery, with mean modifier-plane
> L1 distance reduced from 12.115 to 2.281 percentage points. Directional dual-axis recovery
> simultaneously moves from 0/5 to 8/8 (95 % Wilson [0.00,0.43] → [0.68,1.00]). A naive
> single-pass baseline on identical evidence recovers 0/7 near-region and 0/7 dual-axis
> decisions, while the frozen lattice itself contains 24.7 % near-region and 65.8 % dual-axis
> candidates under uniform random selection. We attribute 94 % of the accompanying distance improvement to the
> deterministic rule layer and the remainder to the language-model layer — the latter verified
> by withholding the precomputed ranking, after which the agent still departed from it in 7 of 8
> runs. The selected candidate is modal for all three models tested.

May not:
> that the agent validates the wet-lab result (it performs no measurement); that the five
> versions are independent blind trials; or that agreement at 1.877 pp reflects resolution finer
> than the candidate lattice permits.


## 9. Record-count provenance

The repository contains several different counting units that should not be conflated:

- **27 primary Luna strategy-ladder runs** (v1/v2/v3/v4/v3h), each using five LLM stages:
  **135 real LLM calls** and approximately **6.8 million tokens**.
- **36 frozen LLM recommendation records** when the two cross-model series are added.
- **38 total `recommendation.json` artifacts** in the frozen result commit because two
  additional records are deterministic-rule baselines rather than LLM Agent outputs.

Manuscript text should name the counting unit explicitly rather than describing all 38 files
as Agent recommendations tied to the 135-call statistic.
