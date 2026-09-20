# Agent V4: VOI-guided experiment selection — frozen run and adjudication

Run `EXP_V4_20260919T141726Z_50bdb5870e`, model `gpt-5.6-luna`, 5 real LLM stages,
98,350 tokens, 253 s of model latency. Blindness audit `PASS` (0 critical, 0 high).
73-node lattice, SHA-256 `2b92e5d976e76b67…`, byte-identical to the V3 series.

---

## 1. The decision

```
selected experiment      S1C41::M-HOLD-120
  formulation            AC1920 15.0 wt% / TK100 5.0 wt%, reactive mass fraction 0.8000
  measurement            120 °C matched-window thermal hold, 15/30/45/60 min, ≥2 repeats
  primary observable     SI_15_60 = (eta_60 − eta_15) / eta_15, percent
decision mode            committed_experiment
VOI                      0.6925, inside the tied top set
```

**Acceptance criterion (frozen):** mean SI_15_60 < 3.80% across ≥2 repeats, every
individual repeat < 7.61%. The threshold is half the H-CORE linear-dilution prediction
of 7.61% at φ_r = 0.8000.

**Falsification criterion (frozen):** mean ≥ 7.61% falsifies H-RESIN and contradicts
H-DUAL's low-drift prediction for this composition, leaving H-CORE consistent. Mean
< 3.80% falsifies H-CORE at the registered resolution. **3.80% ≤ mean < 7.61% is
declared non-decisive in advance** and falsifies neither.

**Next experiment if falsified (frozen):** acrylic-only 120 °C matched-window hold at
15 wt% acrylic, same sampling grid, ≥2 repeats, to separate H-RESIN from H-DUAL.

---

## 2. The deterministic layer ties, and the tie is load-bearing

The VOI tool returns a **five-way tie** with identical component vectors:

```
S1C41 (AC 15.0 / TK 5.0)   S1C46 (17.5 / 5.0)   S1C51 (20.0 / 5.0)
S1C56 (22.5 / 5.0)         S1C61 (25.0 / 5.0)        all × M-HOLD-120
margin to the first strictly lower experiment: 0.004583
```

The held-out composition sits at AC 14.00 / TK 4.12. A proximity-driven score would have
singled out `S1C41` uniquely; `S1C41` and `S1C61` instead carry **identical VOI and
identical components**, which `tests/test_voi.py` asserts directly. The selection inside
the tied set therefore cannot have been read off the ranking.

The Proposer broke the tie on minimum supported modifier burden:

> "S1C41 is selected because it uses the smallest acrylic loading and therefore the
> smallest supported total modifier burden while remaining inside the directly supported
> acrylic region and the repeatedly documented approximately 5% minor-tackifier region.
> It is the least departure from the characterized E2 reactive core among the tied cards."

---

## 3. Decision stability

25 scenarios, each weight term independently scaled ×0.5 → ×1.5 in five steps.

```
top_experiment_set_stability      1.000
top_experiment_set_mean_jaccard   1.000
intervention_family_stability     1.000
measurement_plan_stability        1.000
flipped scenarios                 0
flip boundary                     no single term flips the tied set anywhere in ×0.05 … ×3.00
```

Stability is measured over the tied **set**. Measuring it over one alphabetically chosen
member would also have returned 1.000 for a decision whose margin to its runner-up is
exactly zero. This is decision stability of a transparent score, not model confidence.

VOI by best card per measurement plan: `M-HOLD-120` 0.6925, `M-REPEAT` 0.3925,
`M-ANCHOR` 0.2075, `M-SWEEP` 0.2025. Only the hold measurement scores non-zero hypothesis
discrimination, because the other three observe coordinates the registry does not
disagree about.

---

## 4. What the Agent declared it could not do

The Judge reported `hypotheses_left_entangled: ["H-RESIN vs H-DUAL"]` before freeze, and
the Skeptic raised the matching high-severity objection:

> "The S1C41 composition activates both modifier axes simultaneously while also reducing
> the reactive mass fraction to 0.8000, so the experiment cannot attribute any observed
> drift change to either axis or their interaction."

The Robustness Adjudicator classified that objection as `changes_only_interpretation`,
not `changes_which_experiment_to_run`, and kept the selection. The Judge output contract
held without repair (`judge_normalization.applied = false`), so the V3 null-selection slip
did not recur.

---

## 5. Post-freeze adjudication

The blind phase was closed and the frozen file hashed before the held-out data were read.

```
held-out reactive mass fraction φ_r      0.818766
H-CORE linear-dilution prediction        7.7865 %
observed mean absolute SI_15_60          1.6036 %
observed / linear-dilution ratio         0.2059
drift reduction vs E1                    83.14 %
reduction explained by dilution alone    18.12 %
```

| hypothesis | pre-result prediction | verdict |
|---|---:|---|
| **H-CORE** reactive-core / stoichiometry-only | 7.79 % | **falsified** |
| **H-RESIN** superlinear suppression | 3.89 % | survives |
| **H-DUAL** tackifier required | 3.89 % | survives, **not separable by this composition** |

The selected measurement plan matched the measurement actually performed, so the frozen
criteria were directly checkable: the observed 1.60% clears the frozen acceptance
threshold of 3.80% and lands well outside the pre-declared non-decisive band.

**H-CORE is falsified by a factor of 4.9.** Mass dilution accounts for 18.12 percentage
points of an 83.14-point reduction. The remaining suppression is not explained by
lowering the reaction-capable mass fraction.

---

## 6. V3 versus V4 on the identical lattice

| | V3 (v3h series) | V4 |
|---|---|---|
| decision object | formulation candidate, 73 options | experiment card, 292 options |
| deterministic layer | scenario rankings, unique rank-1 per scenario (`S1C40` for three of four scenarios, `S1C10` for causal isolation) | VOI over experiments, 5-way tie reported as a tie |
| model layer's task | may depart from a rank-1 | must break a tie the tool cannot break |
| frozen selections | 10 runs, 8 named, 2 abstained: `S1C41` ×6, `S1C46` ×1, `S1C40` ×1 | 1 run, committed: `S1C41::M-HOLD-120` |
| adjudication | modifier-plane distance to the held-out composition | survival of a registered mechanistic hypothesis |
| mechanism status | stated as interpretation | registered pre-result, one hypothesis falsified |

Both converge on the same composition from different objectives. V3 reached `S1C41` as
the modal selection of a distance-scored series; V4 reached it as a tie-break inside a set
that the score itself could not rank, and paired it with the measurement that decides a
registered hypothesis.

Modifier-plane L1 from the V4 selection to the held-out composition is reported in
`adjudication.json` for comparability with the V3 series only. It is not the V4 objective
and enters no component, weight or tie-break.

---

## 7. Confirmatory series, N = 10 declared before the first run

Series `agent_v4_voi_n10`, contract frozen `2026-09-19T15:22:50Z` at commit `9937398`,
model `gpt-5.6-luna`, 50 LLM calls, 1,031,460 tokens. 10 of 10 runs completed, 0 failed.
The pilot run in section 1 is reported separately and is **not** pooled with this series.

Two earlier attempts at this same N=10 declaration were terminated by controlling-session
teardown before run 1 froze anything. Both manifests are retained under
`_aborted_series_20260919T1426Z` and `_aborted_series_20260919T1517Z`, produced zero
recommendations, and are excluded from every statistic. N=10 was therefore declared three
times, always before any result existed.

### Blind phase

```
committed                 10 / 10      abstained 0 / 10
decision modes            committed_experiment 9, discriminating_probe 1
measurement plan          M-HOLD-120  10 / 10      (unanimous)
experiment selected       S1C41::M-HOLD-120  x9,  S1C39::M-HOLD-120  x1
inside the tied top set   9 / 10       95% Wilson [0.596, 0.982]
declared an entangled hypothesis pair   10 / 10
Judge output-contract repairs           0 / 10
```

Zero abstentions against 2 of 10 in the V3 confirmatory series, and zero Judge contract
repairs: the V4 output contract closed the `selected_*: null` slip V3 documented and left
unfixed.

### The run that left the tied set did so to close a different hypothesis pair

Run 3 selected `S1C39` — **acrylic-only**, AC 15.0 / TK 0 — as a `discriminating_probe`,
and declared its own entanglement correctly:

> "H-CORE versus H-DUAL: both predict approximately linear-dilution drift for an
> acrylic-only composition, so this experiment cannot distinguish reactive-core dilution
> from the tackifier-required claim when the acrylic-only result is high."

That is the mirror image of the entanglement the other nine runs declared, and it is the
experiment those nine runs each named as their own `next_experiment_if_falsified`. The
Agent reached that structural fact blind, from the registered prediction rules alone.

### Adjudication

The completed wet-lab experiment used a dual-axis composition. Run 3 chose a composition
that was never synthesised, so its frozen criteria are **not checkable** against this
measurement and it is reported as not adjudicable rather than scored.

```
adjudicable                    9 / 10       95% Wilson [0.596, 0.982]
measurement plan matched      10 / 10
modifier-plane L1 (9 runs)    min = median = mean = max = 1.8766 pp, zero variance
```

All nine adjudicable runs selected `S1C41`, the lattice construction floor. The hypothesis
verdict is a property of the completed measurement and the registered prediction rules, so
it is identical for every adjudicable run: **H-CORE falsified**, H-RESIN surviving, H-DUAL
not separable by a dual-axis composition.

---

## 8. Artifacts

```
configs/hypothesis_registry.json          3 registered hypotheses with prediction rules
configs/measurement_catalog.json          4 measurement plans with declared resolutions
configs/agent_v4.json                     architecture
src/pur_new/voi.py                        deterministic VOI tool + weight sweep
prompts/agent_v4_*.txt                    5 stage prompts
schemas/agent_v4_experiment.schema.json   frozen-record contract
scripts/run_agent_v4.py                   runner
scripts/adjudicate_agent_v4.py            post-freeze adjudication (only reader of held-out data)
scripts/compare_v3_v4.py                  deterministic V3/V4 comparison
tests/test_voi.py                         13 tests, incl. the not-a-distance proof
results/agent_v4_voi/run_001/<rec-id>/    deliberation, recommendation, full 292-card
                                          VOI ranking, decision stability, blind-phase
                                          closure, adjudication
results/agent_v4_voi/v3_vs_v4.json        comparison output
```

Every V3 artifact and every original data file is unchanged.
