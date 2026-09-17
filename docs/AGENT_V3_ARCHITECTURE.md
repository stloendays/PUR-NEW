# PUR-NEW Scientific Decision Agent V3

## 1. Why V3 exists

The Agent contribution should not be reduced to the statement that a language model read literature and happened to select a useful formulation region. The paper needs a stronger and falsifiable systems question:

> Does an evidence-grounded scientific decision architecture produce more reliable formulation decisions than a direct language model, a deterministic evidence heuristic, or a single-pass tool-enriched model when all conditions are blinded to the validation outcome?

V3 is therefore designed as a **scientific decision system**, not a longer prompt.

The physical/model findings remain upstream:

```text
original rheology
-> state-aware design theory
-> admissible candidate space
-> scientific decision Agent
-> frozen recommendation
-> human wet-lab execution
-> physical adjudication
```

The Agent operationalizes the state-aware theory; it does not replace the physical science.

---

## 2. Architecture

```text
STRUCTURAL EVIDENCE FIREWALL
          |
          v
      Planner
          |
          v
Planner-selected read-only scientific Actions
          |
          v
Deterministic candidate analysis
(Pareto front + robustness scenarios)
          |
          v
      Proposer
          |
          v
      Skeptic
(falsification + leakage + boundary audit)
          |
          v
       Judge
          |
          v
FROZEN recommendation / probe / abstention
```

### Stage 0 — structural evidence firewall

Blindness is enforced in code before the language model sees a payload.

For `blind_pre_result` runs:

- the validation formulation identity is removed;
- all `stage=follow_up` hold measurements are removed;
- follow-up mean-profile descriptors are removed;
- post-result adjudication labels are absent;
- controller-side held-out target coordinates are absent.

`src/pur_new/evidence_firewall.py` recursively audits payloads and raises an error if a forbidden target identity or follow-up result appears.

This is stronger than placing the result in context and instructing the model not to use it.

### Stage 1 — Planner

The Planner cannot select a final candidate. It must first define:

- the physical failure mode;
- scientific assumptions;
- which evidence/actions are decision-relevant;
- candidate-evaluation dimensions;
- abstention triggers;
- counterfactual checks.

The Planner may request read-only Actions such as:

```text
get_state_aware_rheology_summary
get_hold_stability
get_repeatability_risk
get_temperature_support
get_candidate_hypothesis
query_external_priors
inspect_formulation
```

This separates **what evidence should be acquired** from **which candidate should win**.

### Stage 2 — scientific Action execution

Only Planner-requested Actions are executed. Every call, error and firewall block is retained in the trace.

A central Action is:

```text
get_state_aware_rheology_summary()
```

which recomputes directly from the original pre-validation CSV files:

- matched-temperature realization spread;
- anchor-normalized master-curve collapse;
- apparent rheological temperature-sensitivity descriptors;
- original E1/E5 thermal-hold failure evidence;
- the state-aware design-theory boundary.

The Agent therefore has explicit access to the paper's physical/model finding rather than reasoning only from formulation priors.

### Stage 3 — deterministic candidate analysis

For every admissible candidate V3 constructs an outcome-blind scorecard containing:

- acrylic-like and tackifier-like analogue support separately;
- distance to independent evidence anchors;
- process-history missingness;
- transparent stress-test flags;
- whether the candidate actually tests the resin-modification hypothesis.

V3 then computes a **weight-free Pareto front** and three transparent ordinal robustness rankings:

```text
evidence_first
robustness_first
hypothesis_test_first
```

The purpose is not to create a hidden surrogate predictor. It is to expose whether the provisional choice depends on one arbitrary scalar weighting.

### Stage 4 — Proposer

The Proposer receives the Planner trace, tool outputs and deterministic diagnostics, and returns a ranked shortlist.

It must separately state:

- evidence supporting each candidate;
- evidence against it;
- key uncertainties;
- why its rank is justified.

### Stage 5 — Skeptic

The Skeptic is an explicit falsification layer. It attempts to break the provisional recommendation by checking:

- evidence leakage;
- unsupported mechanistic claims;
- confusion of external analogue evidence with local measurement;
- ignored process-history or stoichiometric uncertainty;
- dependence on one ranking heuristic;
- robustness-scenario failures;
- missing controls or uncertainty probes;
- non-falsifiable acceptance criteria.

The Skeptic may require reranking, an uncertainty probe, or abstention.

### Stage 6 — Judge and freeze

The Judge receives both the Proposer and Skeptic records. It may output:

```text
performance_candidate
robustness_probe
uncertainty_probe
abstain
```

A non-abstaining output must include ranked alternatives, decomposed uncertainty and a falsifiable pre-result acceptance criterion.

The frozen record stores:

- model;
- Git commit;
- evidence/input hashes;
- prompt hash;
- architecture/ablation version;
- candidate and alternatives;
- uncertainty;
- acceptance criterion.

The physical experiment is stored separately and can only adjudicate the frozen record later.

---

## 3. Why this is stronger than a single-pass Agent

A single-pass tool-enriched model mixes several logically different tasks in one generation:

```text
interpret problem
+ decide what evidence matters
+ inspect evidence
+ rank candidates
+ challenge its own assumptions
+ write final answer
```

V3 makes those interfaces explicit and auditable.

The intended advantages are empirical hypotheses, not assumptions:

1. **planning hypothesis** — separating evidence acquisition from selection should improve evidence use;
2. **state-awareness hypothesis** — explicit access to the state-aware rheology Action should improve scientific problem framing;
3. **robustness hypothesis** — Pareto/scenario diagnostics should reduce dependence on one heuristic;
4. **falsification hypothesis** — the Skeptic should reduce unsupported claims and fragile selections;
5. **abstention hypothesis** — the Judge should abstain or request an uncertainty probe when evidence is genuinely insufficient;
6. **reproducibility hypothesis** — structural firewall + hashes + frozen records should make blind decisions auditable.

These hypotheses are tested by ablation rather than asserted from architecture alone.

---

## 4. Benchmark conditions

All language-model conditions use the same model, the same candidate set, the same blind outcome policy and the same original pre-result data.

### B0 — deterministic evidence ranker

No LLM.

Uses the transparent evidence-anchor/stress-test heuristic already implemented in `rank_candidate_support()`.

Purpose:

> determine how much of candidate recovery is already explained by the manually encoded evidence prior.

### B1 — direct LLM blind

Receives only:

```text
filtered original evidence
+ candidate set
```

No action catalog, no precomputed tool outputs, no external tool trace.

### B2 — single-pass tool-context model

Receives the same filtered evidence plus the action catalog and precomputed scientific/action context, including the same state-aware rheology summary available to V3.

This is the strongest fair single-pass baseline.

### A1 — V3 without Skeptic

Removes the falsification layer only.

### A2 — V3 without deterministic robustness

Removes Pareto/scenario diagnostics only.

### A3 — V3 without state-aware rheology Action

Planner cannot request `get_state_aware_rheology_summary()`.

### A4 — full V3

All stages enabled.

The key comparison is not only whether A4 picks the held-out-near region. It is whether it does so **more reliably and with fewer scientific failures** than B0-B2 and the architecture ablations.

---

## 5. Primary metrics

For repeated runs, report:

```text
nearest-candidate / held-out-region rank
Top-1 regional recovery
Top-3 regional recovery
L1 distance in (acrylic-like %, tackifier-like %) plane
selection entropy across repeated runs
abstention rate
scientific-boundary violation rate
structural evidence-leakage rate
evidence/tool trace completeness
tool call count and success fraction
```

Selection entropy is useful because one lucky Top-1 result is much weaker than repeated convergence on the same defensible region.

For V3 specifically also report:

```text
skeptic changes final decision? yes/no
skeptic boundary failures
skeptic leakage failures
robustness-scenario agreement
```

Use 3-5 runs only as a pilot. The manuscript benchmark should use at least 30 independent runs per stochastic model condition unless API cost or endpoint determinism makes a different design necessary and explicitly justified.

---

## 6. Leakage issue found and corrected

During the V3 audit, an important problem was identified in the earlier single-pass runner:

- `build_agent_context.py` correctly respected the blind profile;
- however, the old runner also placed the complete `evidence_state.json` in the model payload;
- `evidence_state.json` contains follow-up rows;
- therefore an earlier blind replay could contain target-result information even if the action context hid it.

This is now corrected.

Both the single-pass baselines and V3 pass the evidence state through the same structural firewall before payload construction. CI explicitly verifies that the blind state contains neither `F1` nor any `stage=follow_up` record.

Old benchmark results generated before this correction should not be used as primary evidence of Agent superiority unless their exact payload is independently shown to be leakage-free.

---

## 7. Paper-facing interpretation

The desired paper claim is conditional on benchmark results.

If full V3 outperforms strong baselines and ablations, a defensible formulation is:

> The state-aware physical model was operationalized through an evidence-firewalled scientific decision Agent that explicitly separated planning, scientific tool use, deterministic robustness analysis, proposal generation, falsification and final adjudication. Under identical pre-result evidence and candidate constraints, architecture ablations and single-pass baselines showed that the full decision pipeline improved the stability and scientific validity of candidate selection rather than merely reproducing a literature prior.

Do **not** claim this until the repeated benchmark supports it.

The physical validation claim and architecture claim are separate:

```text
physical claim:
pre-result Agent recommendation -> human experiment -> low-drift physical support

architecture claim:
full V3 > direct / deterministic / single-pass / ablated conditions under leakage-safe replay
```

Both together make the Agent contribution substantially stronger.

---

## 8. Historical boundary

V3 is the current, improved implementation of the scientific decision framework.

The project record supports the author-confirmed chronology that an Agent recommendation preceded the current validation experiment, but the repository does not currently contain the original historical frozen runtime record. Therefore:

- do not claim the present V3 code is the exact historical implementation that selected the validation formulation;
- use V3 to formalize, reproduce and benchmark the decision architecture rigorously now;
- keep the historical chronology and the current software-provenance claim distinct.
