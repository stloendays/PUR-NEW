# Agent V4: VOI-guided experiment selection — frozen run and adjudication

> **The result.** Specifying the right deterministic rule is what converts a capable model
> into a correct scientific decision. Holding the model, the prompts, the hypothesis
> registry, the measurement catalog, the evidence contract and all 292 experiment cards
> fixed, and withholding only the deterministic value-of-information score, recovery of the
> evidence-supported intervention family falls from **9/10 to 0/5** (95% Wilson
> [0.596, 0.982] versus [0.000, 0.435], non-overlapping). Inverting the *order* of two
> correct rules is worse still: every run then commits to an experiment that can separate
> **no** registered hypothesis, and does so after its own Skeptic has said so at high
> severity. Sections 9 and 10 are the controlled ablations that measure this.

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

The Proposer broke the tie on minimum supported modifier burden. That rule was supplied to
the model rather than inferred by it; see section 8 for the provenance and for the measured
model-layer departure rate:

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

## 8. What the tie-break does and does not show

The Proposer broke the five-way tie on "smallest supported total modifier burden" in 9 of
10 runs. That rule is **not** an independent inference by the model. Near-identical wording
is present in `configs/formulation_priors.json` under `MINIMUM_SUFFICIENT_INTERVENTION_V1`:

> "Among candidates with comparable evidence coverage and interpretability, prefer the
> smallest sufficient total modifier burden and the smallest justified departure from the
> characterized local chemistry."

and that text verifiably reaches the model through the tool trace
(`tiebreak_baseline.json` → `policy_provenance.payload_sections_containing_the_policy`).
A run applying it is applying a supplied policy correctly. That is a competence result, not
an autonomy result, and it must not be reported as the latter.

Coding the supplied policy as a deterministic baseline makes the model-layer contribution
measurable instead of asserted (`scripts/voi_tiebreak_baseline.py`):

```
coded baseline    argmax VOI, then lowest total modifier percent, then lexicographic id
                  -> S1C41::M-HOLD-120 in 10/10, and it can never select S1C39
frozen series     S1C41 x9, S1C39 x1
matching baseline           9/10
departing from baseline     1/10          <- the measurable model-layer contribution
```

**The departure rate is 1/10, not 10/10.** Run 3 gave up 0.075 of VOI (0.6175 against the
0.6925 tied maximum) to select `S1C39`, an acrylic-only composition that the supplied
policy explicitly demotes, because zeroing an independently supported axis makes a
candidate a partial-coverage control rather than a default performance rank-1. It chose it
anyway, as a `discriminating_probe`, on the stated ground that an acrylic-only hold
separates H-RESIN from H-DUAL — the pair the other nine runs each declared entangled and
each nominated as their own `next_experiment_if_falsified`.

No VOI maximum and no minimum-burden rule produces that selection. It is the one result in
this series that requires the model layer to explain.

The concentration of the other nine runs is still worth reporting, for a different reason:
it shows the decision is reproducible under a fixed evidence contract, with zero
abstentions and zero output-contract repairs. Reproducibility and autonomy are separate
claims and are reported separately here.

---

## 9. What the rule layer contributes, measured by controlled ablation

Two arms, identical except for one thing. Held constant: the model and endpoint, all five
stage prompts, the hypothesis registry and its prediction rules, the measurement catalog and
its declared resolutions, the evidence access profile and structural firewall, the 73-node
lattice and the full 292-card experiment inventory. Manipulated: the deterministic VOI score,
its component vector, its ranking and tie set, the decision-stability sweep, and the
tool-generated acceptance and falsification criteria.

The ablated arm (`series_ablation_voi_withheld_n5`, N=5 declared at `2026-09-20T03:36:53Z`)
receives the same 292 experiments as a plain unscored inventory and must select and write its
own criteria. This is the direct analogue of the V3 `--hide-deterministic-ranking` condition,
taken one step further: V3 hid the ordering, V4 hides the score itself.

| | full V4, rule layer supplied | ablated, score withheld |
|---|---|---|
| N declared | 10 | 5 |
| **evidence-supported family (dual-axis)** | **9/10** [0.596, 0.982] | **0/5** [0.000, 0.435] |
| reactive-core-only selections | 0/10 | **3/5** |
| acrylic-only selections | 1/10 | 2/5 |
| **failure-mode measurement (`M-HOLD-120`)** | **10/10** [0.723, 1.00] | **5/5** [0.566, 1.00] |
| selection inside the tied top set | 9/10 | **0/5** |
| mean post-hoc VOI of the selection | 0.6850 | 0.3931 |
| **selections with zero hypothesis discrimination** | **0/10** | **3/5** |

### The rule layer does not contribute uniformly, and that is the useful finding

**The measurement plan survives this ablation.** The full arm and the score-withheld arm
both select the matched-window 120 °C hold unanimously, 10/10 and 5/5. That choice follows
from the hypothesis registry and the declared failure mode, which are still supplied when
the score is withheld. A rule that encodes *what question is open* transfers without a
score attached to it.

It does **not** transfer through an inverted decision order. Section 10's order arm selects
the failure-mode measurement in only 7 of 10 runs, with 3 runs diverting to the
repeatability plan. So the two manipulations degrade different things: withholding the
score costs the composition choice and leaves the measurement intact, while inverting the
order costs the composition choice **and** partially costs the measurement choice.

**The composition choice does not survive.** Without the score, three of five runs fall back
to a reactive-core-only composition — the already-characterized chemistry, which by
construction separates **no** registered hypothesis. That is the same failure mode as the
naive single-pass baseline, which selected the reactive-core composition in 7 of 7 runs. The
model is not less capable in this arm; it is less constrained, and it spends the experiment
on a composition that cannot answer the question it correctly identified.

Mean hypothesis discrimination of the selected experiment drops by 0.40 between the arms.
The model picked the right measurement and the wrong thing to measure it on.

### What this licenses saying

The defensible claim is about rule design, not model autonomy:

> Under a fixed evidence contract, the deterministic rule layer is the dominant lever on
> decision quality. Encoding the open question as a hypothesis registry is sufficient to fix
> the measurement choice. Fixing the composition choice additionally requires an explicit
> value-of-information score over the candidate space; withholding it collapses
> evidence-supported recovery from 9/10 to 0/5 with non-overlapping 95% intervals, while
> leaving the model, prompts and evidence untouched.

This is consistent with the earlier V1→V3 strategy ladder, where reworking the deterministic
diagnostics moved rule-only distance from 15.115 to 2.615 pp and dual-axis recovery from 0/5
to 8/8, and where applying minimum perturbation *before* intervention sufficiency (v2) made
the agent zero a supported axis. Rule content and rule **order** both change the outcome.

Reproduce with `scripts/compare_rule_layer_arms.py`; the artifact is
`results/agent_v4_voi/rule_layer_ablation.json`.

---

## 10. Rule ORDER, measured as its own arm

Rule content is not the only lever. The earlier Stage-1 ladder recorded a V2 failure in
which minimum perturbation was applied *before* intervention sufficiency and the agent
zeroed an evidence-supported axis. That was a quoted observation from a previous series.
Here it is reproduced as a V4 arm, with order as the only manipulated variable.

Two lexicographic orders over the *same* cards and the *same* component vectors
(`src/pur_new/voi.py::rule_order_key`). Nothing else differs; the VOI score itself is
untouched and every existing frozen result remains reproducible.

```
sufficiency_first   coverage -> discrimination -> relevance -> burden
minimality_first    burden   -> coverage       -> discrimination -> relevance
```

The deterministic consequence is computable before any model runs:

| order | rank-1 | family | hypothesis discrimination | VOI |
|---|---|---|---:|---:|
| `sufficiency_first` | `S1C30::M-HOLD-120` | dual-axis resin-modified | **0.667** | 0.6621 |
| `minimality_first` | `S1C01::M-HOLD-120` | reactive-core-only | **0.000** | 0.2435 |

Inverting the order alone promotes an experiment that by construction separates **no**
registered hypothesis. Series `agent_v4_ablation_minimality_first_n5`, N=5 declared at
`2026-09-20T04:06:53Z` and extended on the record to N=10 at `2026-09-20T07:49:23Z`,
10/10 completed:

| | full V4 | score withheld | **order inverted** |
|---|---|---|---|
| N | 10 | 5 | 10 |
| evidence-supported family | 9/10 [0.596, 0.982] | 0/5 [0.000, 0.435] | **0/10 [0.000, 0.278]** |
| reactive-core-only selections | 0/10 | 3/5 | **10/10** |
| **zero-discrimination selections** | **0/10** | 3/5 | **10/10** |
| mean hypothesis discrimination | 0.667 | 0.267 | **0.000** |
| failure-mode measurement | 10/10 | 5/5 | **7/10** [0.397, 0.892] |
| selected candidate | `S1C41` ×9 | 4 distinct | `S1C02` ×10 |

**A correct score under an inverted order is worse than no score at all**: 10/10
zero-discrimination against 3/5. Order dominates presence, and the order arm's interval
does not overlap the full arm's.

The order arm is also the only arm whose *measurement* choice degrades: 7 of 10 runs keep
the matched-window hold, while 3 divert to the repeatability plan. Withholding the score
never did this. An inverted order therefore damages more of the decision than a missing
score does, not less.

**The extension is reported as an extension.** Runs 1-5 were pre-declared; runs 6-10 were
added after that block had been observed, and the manifest records this explicitly rather
than presenting a single pre-declared N=10. The two blocks are identical — 5/5 and 5/5
zero-discrimination, `reactive_core_only` in both — so the extension confirms the
pre-declared block rather than rescuing it. Both are reported separately in
`rule_layer_ablation.json` under `rule_order_blocks`.

### The model diagnosed the defect and followed the rule anyway

This is the part that generalises beyond this chemistry. The Skeptic raised a
**high-severity objection in 10 of 10 runs**, each time identifying the exact defect:

> "S1C02 is an unmodified E2 reactive-core hold with AC1920 = 0.0, TK100 = 0.0 and
> reactive_mass_fraction = 1.0000; therefore all three registry predictions collapse to
> 9.51% and the experiment cannot discriminate."

The Proposer said it too, unprompted, while proposing it:

> "this baseline experiment cannot separate the three mechanism hypotheses;
> modifier-containing hold experiments would be needed for that adjudication."

The Robustness Adjudicator went further in 5 of 10 runs and returned
`changes_which_experiment_to_run`. **All 10 runs committed to it regardless.**

| arm | high-severity objection | robustness said change experiment | committed anyway |
|---|---|---|---|
| full V4 | 10/10 | 1/10 | 10/10 |
| score withheld | 5/5 | 4/5 | 5/5 |
| order inverted | **10/10** | 5/10 | **10/10** |

The scientific judgement was intact throughout: the model correctly identified that the
experiment could not answer the question. The decision order overrode it.

### What this licenses saying

> A wrong rule order is not rescued by a competent model, and it is not rescued by a
> working critique stage. Across ten runs the Skeptic identified at high severity that the
> selected experiment could separate no registered hypothesis, and all ten runs committed
> to it (0/10 evidence-supported family, 95% Wilson [0.000, 0.278]). Adding a critic to an
> agent does not substitute for ordering its decision rules correctly.

For a group building scientific agents, the operational reading is that rule order belongs
in the same category as rule content: it must be declared, frozen, and ablated, not left
implicit in the sequence a prompt happens to describe.

Reproduce with `scripts/compare_rule_layer_arms.py`; artifact
`results/agent_v4_voi/rule_layer_ablation.json`.

---

## 11. Artifacts

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
scripts/voi_tiebreak_baseline.py          coded tie-break baseline and departure rate
scripts/compare_rule_layer_arms.py        controlled rule-layer ablation, full vs withheld
tests/test_voi.py                         13 tests, incl. the not-a-distance proof
results/agent_v4_voi/run_001/<rec-id>/    deliberation, recommendation, full 292-card
                                          VOI ranking, decision stability, blind-phase
                                          closure, adjudication
results/agent_v4_voi/v3_vs_v4.json        comparison output
```

Every V3 artifact and every original data file is unchanged.
