# Agent V4: VOI-guided experiment selection

**Thesis.** Rule design, not model autonomy, is the dominant lever on scientific decision
quality under a fixed evidence contract. V4 is built so that this can be measured rather
than argued: every rule is explicit, deterministic and ablatable, and the model layer's
contribution is reported at whatever rate the evidence supports.

A controlled ablation holding the model, prompts, hypothesis registry, measurement catalog,
evidence contract and all 292 experiment cards fixed, and withholding only the deterministic
value-of-information score, moves evidence-supported family recovery from **9/10 to 0/5**
(95% Wilson [0.596, 0.982] versus [0.000, 0.435]). See
`results/agent_v4_voi/AGENT_V4_REPORT.md` section 9.

V4 is an independent architecture. `configs/agent_v3.json`, `prompts/agent_v3_*.txt`,
`src/pur_new/agent_v3.py` and every frozen V3 run record are unchanged. No original
experimental data file was modified.

---

## 1. What changed

| | V3 | V4 |
|---|---|---|
| unit of decision | formulation candidate (73) | experiment card = formulation × measurement plan (292) |
| deterministic layer | scenario rankings, unique rank-1 | VOI score, ties reported as ties |
| what the model layer does | may depart from a rank-1 it can see or not see | must break a tie the tool cannot break |
| adjudication | modifier-plane distance to the held-out composition | survival of a registered mechanistic hypothesis |
| mechanism | stated as interpretation | registered pre-result with a falsification condition |

The candidate lattice is byte-identical to V3's (73 nodes, SHA-256 `2b92e5d976e76b67…`).
Continuous-space optimization and new wet-lab work are deliberately out of scope, so the
measured difference between V3 and V4 is the decision object and the VOI layer, not the
search space.

The stage sequence is unchanged and no role was added:

```
Planner → Evidence/Tool Layer (incl. deterministic VOI) → Proposer → Skeptic
        → Robustness Adjudicator → Judge → Freeze
```

VOI is a deterministic scientific tool (`src/pur_new/voi.py`), not a second language
model. The five LLM stages are the same five as V3.

---

## 2. The VOI formula

```
VOI = w_hyp · hypothesis_discrimination
    + w_unc · uncertainty_reduction
    + w_dec · decision_relevance
    + w_int · measurement_interpretability
    − w_ext · extrapolation_risk
    − w_proc · process_state_risk
```

Every component is normalized to [0, 1] by construction. Base weights:

| term | weight | definition |
|---|---:|---|
| `hypothesis_discrimination` | 0.30 | fraction of registered hypothesis pairs whose pre-result point predictions differ by at least the measurement's declared resolution |
| `uncertainty_reduction` | 0.20 | how unresolved the coordinate this measurement resolves currently is, discounted when the composition re-measures already-covered chemistry |
| `decision_relevance` | 0.25 | how directly the measurement observes the declared failure mode × whether the composition covers the externally supported intervention axes |
| `measurement_interpretability` | 0.10 | directly read observable (1.0) versus one inheriting a model fit (0.7) |
| `extrapolation_risk` | 0.10 | normalized distance outside the supported modifier regions; a zeroed axis carries zero risk because zero modifier is measured chemistry |
| `process_state_risk` | 0.05 | process/state ambiguity remaining after the measurement plan; a state-control plan cuts it to 20% |

**This is not a posterior.** The local design has six audited realizations and two
thermal-hold trajectories. That does not support a calibrated Bayesian expected-information
computation, so none is fabricated. Weight sensitivity is reported instead.

**This is not distance to any known answer.** No held-out coordinate enters any component,
weight or tie-break. `tests/test_voi.py::test_voi_is_not_distance_to_the_held_out_formulation`
loads the held-out composition purely to prove the score is independent of it: `S1C41`
(nearest lattice node to the held-out point) and `S1C61` (far from it on the acrylic axis)
carry an **identical component vector and identical VOI**.

---

## 3. Hypothesis registry

Three falsifiable, formulation-level mechanisms, registered before any V4 run and before
the held-out outcome was loaded. `φ_r` is the reactive mass fraction (polyols + MDI);
the reference is the measured E1 drift of 9.51% over the matched 15–60 min window.

| id | statement | pre-result prediction | falsified if |
|---|---|---|---|
| **H-CORE** | drift is set by the reactive core alone; modifiers are inert mass dilution | drift = 9.51 × φ_r | drift falls far below the dilution prediction |
| **H-RESIN** | resin modification suppresses drift more than dilution alone | drift ≤ 0.5 × 9.51 × φ_r | drift stays at or above the dilution prediction |
| **H-DUAL** | the acrylic axis moves viscosity level; the tackifier axis is required for drift suppression | low drift only when tackifier > 0 | an acrylic-only composition reaches the low-drift regime |

No hypothesis asserts a molecularly resolved pathway, and their adjudication does not
require chain-level characterization.

---

## 4. What the discrimination structure implies

A dual-axis composition separates {H-CORE, H-RESIN} and {H-CORE, H-DUAL} but leaves
H-RESIN and H-DUAL entangled. An acrylic-only composition separates {H-CORE, H-RESIN} and
{H-RESIN, H-DUAL} but leaves H-CORE and H-DUAL entangled. **No single experiment in this
space closes all three**, which the Agent is required to declare rather than paper over.

Only `M-HOLD-120` scores non-zero discrimination. The sweep, anchor and repeatability
plans observe coordinates the registry does not disagree about, so they score zero. That is
the intended scientific result: only the matched-window hold observes these mechanisms.

Deterministic VOI by best card per measurement plan:

| measurement | best VOI |
|---|---:|
| `M-HOLD-120` | 0.6925 |
| `M-REPEAT` | 0.3925 |
| `M-ANCHOR` | 0.2075 |
| `M-SWEEP` | 0.2025 |

---

## 5. Decision stability

Weight perturbation sweep, each term independently scaled over ×0.5 to ×1.5 in five steps
(25 scenarios including the base).

```
tied top set (5 experiments, identical component vectors):
  S1C41::M-HOLD-120   AC 15.0 / TK 5.0
  S1C46::M-HOLD-120   AC 17.5 / TK 5.0
  S1C51::M-HOLD-120   AC 20.0 / TK 5.0
  S1C56::M-HOLD-120   AC 22.5 / TK 5.0
  S1C61::M-HOLD-120   AC 25.0 / TK 5.0

top_experiment_set_stability        1.000
top_experiment_set_mean_jaccard     1.000
intervention_family_stability       1.000
measurement_plan_stability          1.000
margin to first strictly lower VOI  0.004583
recommendation flip boundary        no single term flips the tied set anywhere in ×0.05 … ×3.00
```

This is **decision stability** of a transparent score. It is not model confidence, not a
posterior probability, and not evidence that the chosen experiment is correct. A decision
can be perfectly stable and still be scientifically poor.

The stability metric is defined over the tied **set**, not over one arbitrarily chosen
member. Reporting stability of an alphabetical representative would have returned 1.000 for
a decision whose margin to its runner-up is exactly zero, which would overstate the result.

---

## 6. The tie is the point

The deterministic layer is genuinely indifferent across five compositions spanning
AC 15–25 wt%. The held-out composition sits at AC 14.00 / TK 4.12, so a distance-driven
score would have singled out `S1C41` uniquely. It does not.

Consequently, a selection inside the tied set **cannot have been read off the VOI ranking**.
It does not follow that the tie-break is independent model reasoning: the minimum-burden rule
the Proposer used is supplied in `configs/formulation_priors.json` and reaches the model
through the tool trace, so applying it is competence, not autonomy.

Coding that supplied policy as a baseline (`scripts/voi_tiebreak_baseline.py`) separates the
two. Over the N=10 confirmatory series the baseline and the Agent agree in 9 of 10 runs; the
measurable model-layer contribution is the **1 of 10** that departs, giving up 0.075 of VOI
to select an acrylic-only probe that closes the hypothesis pair the other nine leave
entangled. Both numbers are recorded in the frozen artifacts (`voi.tied_top_set`,
`voi.selected_is_in_tied_top_set`, the Proposer's `tie_break_justification`, and
`tiebreak_baseline.json`).

---

## 7. Freeze and adjudication order

```
pre-result evidence
  → experiment generation (73 × 4 = 292 cards)
  → deterministic VOI scoring + weight sweep
  → Planner → Proposer → Skeptic → Robustness → Judge
  → FREEZE (hashes of candidate set, hypothesis registry, measurement catalog,
             prompts and the full deliberation input)
  → BLIND_PHASE_CLOSED written, frozen file hashed
  → held-out composition and measurements loaded for the first time
  → retrospective adjudication
```

`scripts/adjudicate_agent_v4.py` is the only place in the V4 pipeline that reads the
held-out data. It refuses to run without a frozen recommendation on disk and re-hashes that
file before scoring, so the decision cannot be edited once the truth is visible.

One Judge contract slip that V3 documented and left unfixed — a named preference emitted
alongside `selected_*: null` — is repaired deterministically in V4 and the repair is logged
in `judge_normalization`, rather than being silently converted into an abstention.

---

## 8. Frozen run and adjudication

Run `EXP_V4_20260919T141726Z_50bdb5870e` selected `S1C41::M-HOLD-120` from inside the
tied set, declared `H-RESIN vs H-DUAL` entangled before freeze, and froze numeric
acceptance (<3.80%), falsification (>=7.61%) and non-decisive (3.80-7.61%) bands.

Post-freeze adjudication against the completed measurement: observed mean absolute
SI_15_60 = 1.6036% against a linear-dilution prediction of 7.7865% at phi_r = 0.818766.
**H-CORE is falsified**; H-RESIN survives; H-DUAL is not separable by a dual-axis
composition. Dilution accounts for 18.12 points of the 83.14-point drift reduction.

Full numbers, stage-by-stage deliberation and the V3 comparison are in
`results/agent_v4_voi/AGENT_V4_REPORT.md`.

---

## 9. Reproducing

```bash
# deterministic layer only, no API needed
PYTHONPATH=src python -m pytest tests/test_voi.py -q

# full run (requires OPENAI_API_KEY / OPENAI_MODEL / OPENAI_BASE_URL)
PYTHONPATH=src python scripts/run_agent_v4.py --output-dir results/agent_v4_voi/run_001

# after freeze only
PYTHONPATH=src python scripts/adjudicate_agent_v4.py --run-dir <frozen run dir>
PYTHONPATH=src python scripts/compare_v3_v4.py --v4-run-dir <frozen run dir> \
    --output results/agent_v4_voi/v3_vs_v4.json
```
