# Stage-1 Preexperimental Reconstruction — v1 → v4 Final Report

**Repo:** `stloendays/PUR-NEW`, v1 @ `a6f61f5`, v2–v4 @ `662297b` + recorded changes
**Model:** `gpt-5.6-luna`, five real LLM stages per run, temperature not accepted by endpoint
**Candidate space:** identical across all versions — 73 nodes, SHA-256 `2b92e5d976e76b67…`
**Held-out truth:** AC1920 **14.0044** / TK100 **4.1190** wt% (normalized total). Not a lattice node.
**Blindness audit:** PASS (0 critical, 0 high) for every version.

---

## 1. Per-run selections

**v3** — coverage gate on, deterministic ranking **visible**

| run | frozen | mode | modifier-L1 | det rank-1 | proposer | robustness |
|---|---|---|---|---|---|---|
| 1 | — | abstain | — | S1C40 | S1C40 | S1C40 |
| 2 | S1C41 | performance_candidate | 1.877 | S1C40 | S1C40 | S1C41 |
| 3 | — | abstain | — | S1C40 | S1C40 | S1C40 |
| 4 | S1C41 | performance_candidate | 1.877 | S1C40 | S1C40 | S1C41 |
| 5 | S1C41 | performance_candidate | 1.877 | S1C40 | S1C40 | S1C41 |

**v4** — coverage gate on, deterministic ranking **hidden**

| run | frozen | mode | modifier-L1 | det rank-1 | proposer | robustness |
|---|---|---|---|---|---|---|
| 1 | S1C41 | performance_candidate | 1.877 | S1C40 | S1C40 | S1C41 |
| 2 | S1C40 | uncertainty_probe | 2.615 | S1C40 | S1C40 | S1C40 |
| 3 | S1C41 | uncertainty_probe | 1.877 | S1C40 | **S1C41** | S1C46 |
| 4 | — | abstain | — | S1C40 | S1C40 | S1C41 |
| 5 | S1C41 | performance_candidate | 1.877 | S1C40 | S1C40 | S1C41 |

`S1C41 = AC 15.0 / TK 5.0` · `S1C40 = AC 15.0 / TK 2.5` · `S1C46 = AC 17.5 / TK 5.0`

## 2. Headline comparison

| | v1 | v2 (truncated) | v3 | v4 |
|---|---|---|---|---|
| N frozen | 5 | 2 | 5 | 5 |
| ranking shown to model | yes | yes | yes | **no** |
| Level 1 thermal-hold objective | 5/5 | 2/2 | 5/5 | 5/5 |
| named a candidate | 5/5 | 1/2 | 3/5 | **4/5** |
| acrylic + minor tackifier (of named) | **0/5** | 0/1 | **3/3** | **4/4** |
| near-region ≤ 7.5 pp (of named) | 0/5 | 0/1 | 3/3 | 4/4 |
| modifier-plane L1 | 10.1–15.1 | 15.6 | **1.877** | 1.877 ×3, 2.615 ×1 |
| abstention | 0/5 | 1/2 | 2/5 | 1/5 |
| invalid | 0/5 | 0/2 | 0/5 | 0/5 |

95 % Wilson on the dual-axis rate among named runs: v3 3/3 → [0.44, 1.00]; v4 4/4 → [0.51, 1.00]. Small N; the intervals are wide and must be quoted.

## 3. Did recommendations concentrate in the moderate-acrylic / minor-tackifier region?

Yes, and tightly. Across v3+v4, **every** named run selected acrylic = 15.0 wt%, and 6 of 7 selected
tackifier = 5.0 wt%. Selection entropy collapsed from 0.971 bits (v1, over 20–25 % acrylic with
TK = 0) to essentially a single point.

## 4. Distance to the real formulation

`S1C41 (15.0, 5.0)` vs truth `(14.0044, 4.1190)`:

```
|ΔAC| = 0.996    |ΔTK| = 0.881
modifier-plane L1 = 1.877 pp    L2 = 1.330 pp
```

**1.877 pp is the lattice lower bound.** The truth is not a node; `S1C41` is the nearest node that
exists. The Agent has saturated what this candidate space permits. Further distance reduction
requires a finer lattice, not more rule tuning — and a finer lattice must be justified before the
outcome is consulted, not after.

## 5. Which change actually improved quantitative agreement

Measured, not asserted. Deterministic rank-1 on the identical lattice, no LLM:

| rule set | det rank-1 | L1 to truth |
|---|---|---|
| v1 `a6f61f5` | S1C59 (25.0, 0.0) | 15.115 pp |
| v2–v4 `662297b` | S1C40 (15.0, 2.5) | 2.615 pp |

1. **Deterministic diagnostics rework — largest effect (15.1 → 2.6 pp).** Removing the
   analogue-distance reward and ranking on `supported_active_axis_count` then `total_modifier_pct`.
   This was upstream in `662297b`, not this session.
2. **Coverage gate (v3) — prevented a regression, did not move rank-1.** v2 showed
   minimum-sufficient-intervention applied too early: run 1 chose `S1C10` (AC 0 / TK 2.5), zeroing a
   supported axis to cut burden, 15.6 pp away. The gate demoted that candidate from contender to
   **rank 37/73** while keeping it available as a labelled control.
3. **Evidence-plumbing fixes — necessary, not sufficient.** `query_external_priors` failed 5/5 in v1;
   H01 (the 4.8 % tackifier example) was unreachable because a literal substring match never matched
   `"tackifying resin"`. Without this the tackifier axis had no quantitative support to reason from.
4. **The LLM's own deviation — the last 0.74 pp, and it is real.** The deterministic rank-1 was
   `S1C40` in every single run of v3 and v4. The Agent chose `S1C41` instead in 3/3 named v3 runs and
   3/4 named v4 runs. **This survives hiding the ranking**: in v4 the model could not see that
   `S1C40` was rank-1, and still moved to `S1C41`. In v4 run 3 the Proposer itself produced `S1C41`
   independently. The Robustness Adjudicator is the stage that makes the switch in most runs.

The v4 result is what rules out "the agent is reading the answer off the deterministic layer".

## 6. Residual systematic bias

1. **Acrylic pinned to the lower boundary of the declared supported region.** 7/7 named runs chose
   exactly 15.0 wt%; 12.5 and 17.5 were never selected. `evidence_region_policy` declares the acrylic
   region as `[15, 25]`, so 15.0 is its floor. The truth (14.004) lies *below* that floor. **If the
   real optimum sits under the declared region, this configuration cannot reach it** — the apparent
   accuracy is partly the region boundary happening to sit near the answer.
2. **Both residual errors are positive.** ΔAC = +1.0, ΔTK = +0.88. The Agent overshoots on both axes,
   consistently, because both sit at region/lattice boundaries rather than at evidence optima.
3. **Judge null-selection persists.** 2/5 (v3) and 1/5 (v4) abstentions arise from the Judge emitting
   `selected_candidate_id: null` while its own Robustness stage names a preferred candidate. This is a
   prompt/freezer contract inconsistency, not scientific indecision. Left unfixed under the freeze rule.
4. **Robustness Adjudicator dominates the final decision** in every version — v1 (mode downgrade 5/5),
   v3 and v4 (candidate switch). The Proposer mostly tracks the deterministic layer.
5. **Prompt salience of thermal-hold stability** (v1 audit LEAK-5) is unchanged, so Level 1's
   uninformed baseline is 1-of-4, not zero.

## 7. Provenance honesty

The v2/v3 rules were selected **after** v1 was diagnosed, and v4 after v2's failure. Each rule is
justifiable from pre-result evidence or a general experimental-design principle and contains no target
coordinate, the lattice is byte-identical throughout, and the truth is not a node. But this is a
**pre-registered strategy-revision sequence evaluated blind**, not four independent blind trials. v4 is
the cleanest single arm: its design was fixed while v3 was still running and frozen before any v3
adjudication.

One inconsistency was deliberately **not** fixed: `_axis_support` bins by distance while
`formulation_priors.json` declares regions. Aligning them would move det rank-1 from 2.615 to 1.877 pp
— a change whose main visible effect is to shrink the distance to a known answer, which cannot be
distinguished from tuning. Recorded, not applied.

## 8. What is and is not supported

Supported:
> From pre-result evidence alone, the Stage-1 Agent identified high-temperature hold viscosity drift as
> the dominant unresolved failure mode (5/5 in every version), selected 120 °C and a matched hold window
> as the adjudicating measurement, entered the acrylic + minor-tackifier resin-modified family, and
> converged on the candidate closest to the later-validated formulation that its candidate space
> contained — including when the deterministic ranking was withheld.

Not supported:
> that the Agent reproduces the validated recipe (exact recovery was impossible by construction), that
> 1.877 pp reflects resolution finer than the lattice, or that the four versions are independent blind
> trials.
