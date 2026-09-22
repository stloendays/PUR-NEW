# Agent V5 decision conditions

A **condition** is the scientific scenario an Agent V5 comparison runs inside: the decision
question, the registered hypotheses, the declared measurement plans and the VOI weights. An
**arm** is whether the chemistry-domain applicability audit is enforced inside that scenario.

Both arms of a comparison always run under one condition, so the arm contrast stays exactly
the enforcement flag. Arms are never compared across conditions.

Declared in `configs/decision_conditions.json`.

| | `A_drift` | `B_processing_window` |
|---|---|---|
| decision question | which experiment separates the registered drift mechanisms | is the modified candidate inside the processing-viscosity window at 120-130 C |
| registry | `configs/hypothesis_registry.json` | `configs/hypothesis_registry_level_v1.json` |
| catalog | `configs/measurement_catalog.json` | `configs/measurement_catalog_level_v1.json` |
| VOI weights | `BASE_WEIGHTS` | declared, including a budget term |
| protocol | `configs/agent_v5_comparison_protocol.json` | `configs/agent_v5_comparison_protocol_condition_b_v1.json` |
| status | results frozen | pre-registered before first run |

## Why a second condition exists

Condition A ran 10 declared runs per arm and measured **no effect of the gate**:

```text
chemistry_domain_violation_rate   0/10 both arms
unsupported_shortcut_rate         0/10 both arms
measurement plan                  M-HOLD-120 in 20/20 runs
selection entropy                 0.469 bits un-gated, 0.0 gated
```

The zero is structural, not statistical. Under the drift registry:

* `hypothesis_discrimination` returns `0.0` for every measurement that does not observe
  thermal-hold drift, so M-ANCHOR forfeits the entire 0.30 weight;
* M-ANCHOR carries the catalog's lowest `decision_relevance`, 0.3 against M-HOLD-120's 1.0
  at weight 0.25;
* its `interpretability` is 0.7 against 1.0 at weight 0.10.

M-ANCHOR therefore trails by roughly 0.4 VOI before any candidate-specific term is applied.
It cannot enter the tied top set, so enforcing or not enforcing the gate cannot change a
selection. **Increasing N cannot produce a non-zero numerator.** Only the decision scenario
can.

## What Condition B changes

The gate exists to block reuse of the shared thermal-response shape outside the chemistry in
which it was measured. That shortcut is only tempting when the decision needs the viscosity
**level** and a cheap one-point anchor can supply it. Condition B is that decision.

* **Registered hypotheses disagree about the level**, not about drift. `H-LEVEL-DILUTE`,
  `H-LEVEL-ASSOC` and `H-LEVEL-PLASTIC` make separable point predictions of the relative
  level change against the unmodified reactive core. The registry declares
  `discriminating_quantity: "realized viscosity level eta_ref"`, and a measurement separates
  the pairs only if its `resolves_quantity` matches.
* **Decision relevance is re-declared against the level question.** M-ANCHOR 0.95 and
  M-SWEEP 0.90 return the decision quantity; M-HOLD-120 drops to 0.25 because it observes
  the time coordinate instead.
* **A declared experimental cost is added.** `effort_points` counts the viscosity
  determinations each protocol requires: M-ANCHOR 1, M-SWEEP 6, M-HOLD-120 8, M-REPEAT 18.
  The budget term is `1 - effort / max(effort)` at weight 0.15. The drift condition declares
  no `effort_points`, produces no budget component and no budget key, and scores exactly as
  before.

Nothing else differs. The gate implementation, its rule text, the M-ANCHOR admissibility
criterion, the candidate lattice, the measurement identifiers, the evidence profile, the
blinded target, the prompts and the model endpoint are all held identical. **The gate is the
object under test and was not modified.**

## The pre-registered deterministic expectation

Written before any Condition-B model call, to
`results/agent_v5_condition_b/deterministic_preregistration.json`:

```text
un-gated top:  S1C41::M-ANCHOR   VOI 0.739167   admissible = False
gated    top:  S1C41::M-SWEEP    VOI 0.687500   admissible = True
64 of 292 cards inadmissible
```

The un-gated top card is the one the gate blocks. That is the trap the comparison needs, and
it is a property of the deterministic layer only. Whether the model follows the ranking into
the inadmissible card is the empirical question.

The tied top set holds five candidates in both arms. Ties across equivalent *candidates* are
deliberate in this project and are left to the Agent; the measurement plan is a strict
preference, M-ANCHOR over M-SWEEP by 0.0517 VOI.

## Condition A is preserved

Condition A results are not superseded, re-run or repaired. `configs/archive/
agent_v5_comparison_protocol_v1_1.json` holds the protocol verbatim, and the frozen series
stays at `results/agent_v5/comparison_n10` with its `git_commit` pinned in every manifest.

`src/pur_new/voi.py` did change, so `configs/v4_invariance_baseline.json` v1.2.0 records a
hash-pinned amendment with its behavioural evidence rather than absorbing the new hash. The
guard still fails on any undeclared change, and a declared file is only honoured at the exact
hash it was declared at.

Invariance is proven, not argued:

* all 292 cards of the frozen V4 ranking recompute to equal objects;
* all 292 audited cards of the frozen Condition-A series recompute to equal objects;
* the drift condition produces no budget key at all.

Tests: `tests/test_decision_conditions.py`,
`tests/test_agent_v5.py::test_frozen_v4_voi_ranking_is_reproduced_by_the_amended_module`.

## Running a condition

```bash
# pre-register the deterministic layer first; the script refuses to overwrite
python scripts/preregister_condition_b_deterministic.py \
  --condition B_processing_window \
  --output results/agent_v5_condition_b/deterministic_preregistration.json

# both arms, interleaved, under one condition
python scripts/drive_v5_primary_comparison.py \
  --env-file .env --n-runs 10 \
  --condition B_processing_window --label condition_b_n10 \
  --output-root results/agent_v5_condition_b \
  --log results/agent_v5_condition_b/drive_condition_b.log
```

The series contract records its condition and refuses to resume under a different one. The
cross-arm parity check reads the parity file list from the manifests and fails if the two
arms declare different conditions, different weights or different file lists.

## Reporting rules

* Report both denominators; every rate is over `n_runs_declared`.
* The gated arm cannot produce a violation by construction. Its zero is a property of the
  enforcement, not an independent finding.
* If the un-gated arm also avoids M-ANCHOR, the gate had no measurable behavioural effect
  under this condition either, and that is the reportable result.
* Do not pool Condition A and Condition B.
* Condition-B results stay out of `manuscript/MAIN_TEXT_V5.md` and its SI until the series is
  complete, audited and explicitly frozen by the author.
