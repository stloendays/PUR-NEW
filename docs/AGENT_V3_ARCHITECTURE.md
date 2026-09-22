# PUR-NEW Discovery-to-Experiment Agent V3

## 1. Role in the paper

The Agent is a scientific decision layer downstream of the physical/model findings. Its job is to convert measured rheological structure into one useful, interpretable formulation-process experiment by combining sparse local evidence with paper-derived material rules and curated PUR literature/database knowledge.

The scientific chain is:

```text
measured rheology
-> state-aware material regularities
-> design implications
-> evidence-grounded intervention directions
-> Agent-selected formulation-process experiment
-> freeze
-> human wet-lab execution
-> physical adjudication
```

The Agent is therefore not evaluated primarily as an LLM architecture benchmark. Its main value is whether it uses the discovered material rules correctly and chooses an experiment that advances the formulation problem.

---

## 2. Canonical V3 decision architecture

```text
STRUCTURAL EVIDENCE FIREWALL
          |
          v
       Planner
          |
          v
  Evidence / Tool Layer
          |
          v
       Proposer
          |
          v
       Skeptic
          |
          v
Robustness Adjudicator
          |
          v
        Judge
          |
          v
        Freeze
          |
          v
 Human wet-lab execution
          |
          v
 Physical adjudication
```

This exact multi-stage sequence is implemented in `configs/agent_v3.json` and `scripts/run_scientific_agent_v3.py`.

### Stage 0 — structural evidence firewall

For outcome-blind preexperimental reconstruction, validation-formulation identity, follow-up measurements, post-result labels and controller-only targets are removed before any model call.

### Stage 1 — Planner

The Planner does not choose a candidate. It first defines:

- the physical failure mode;
- the upstream material regularities that matter;
- the design implication of those regularities;
- which evidence/actions are needed;
- which response must be measured to adjudicate the experiment.

### Stage 2 — Evidence / Tool Layer

The central scientific Action is:

```text
get_state_aware_rheology_summary()
```

This tool converts the paper's upstream analysis into machine-usable scientific evidence, including:

- formulation-only versus state-aware model performance;
- the state-shift master-curve representation;
- one-point state calibration;
- the comparatively concentrated local temperature-sensitivity descriptor;
- E1/E5 thermal-hold drift contrast;
- the verified E1 +P phosphoric-acid perturbation as a separate scale-versus-shape check;
- explicit experiment-design implications and claim boundaries.

The tool is required before candidate ranking. It contains no validation-formulation outcome.

Other Actions retrieve source-level external PUR evidence, candidate-space rationale, measured hold data, repeatability risk, temperature support, formulation composition and process-state unknowns.

The same layer also computes deterministic candidate profiles and transparent support/risk diagnostics. These are decision aids, not wet-lab property predictors.

### Stage 3 — Proposer

The Proposer ranks experiment points according to scientific usefulness. It must connect each leading candidate to:

- the observed failure mode;
- at least one measured material regularity;
- a chemically plausible intervention direction;
- a measurement plan capable of testing the intended claim.

### Stage 4 — Skeptic

The Skeptic tries to falsify the provisional recommendation. It checks whether the proposal:

- misuses the state-aware findings;
- substitutes static viscosity for hold stability;
- ignores realization/process-state uncertainty;
- overinterprets external analogue evidence;
- makes unsupported mechanistic claims;
- produces an experiment that would be difficult to interpret;
- leaks held-out information.

### Stage 5 — Robustness Adjudicator

The Robustness Adjudicator is a decision-quality gate, not an ablation condition.

It asks whether the proposed experiment remains scientifically useful when:

- reasonable evidence priorities change;
- process-state uncertainty is considered explicitly;
- the Skeptic's strongest objections are applied;
- nearby alternatives are considered;
- the proposed measurement plan is required to adjudicate the intended claim.

Its output is one of:

```text
accept_top
rerank
uncertainty_probe
abstain
```

### Stage 6 — Judge

The Judge receives the full evidence trace, Proposer, Skeptic and Robustness-Adjudicator records. It freezes one of:

```text
performance_candidate
robustness_probe
uncertainty_probe
abstain
```

A non-abstaining decision must contain ranked alternatives, decomposed uncertainty and a falsifiable pre-result acceptance criterion.

### Stage 7 — Freeze

Freeze is programmatic rather than another model call. The runner validates the final JSON and stores:

- timestamp;
- Git commit;
- model identifiers;
- prompt hash;
- input hash;
- selected candidate state;
- uncertainty;
- acceptance criterion.

Physical results are stored separately and can only adjudicate the frozen recommendation later.

---

## 3. What makes V3 scientifically useful

V3 is designed around the paper's material findings rather than around generic Agent complexity.

### State-shift rule

The upstream analysis supports:

```text
ln eta_fr(T) = a_fr + g(T) + epsilon
```

where `a_fr` is the realized viscosity-scale intercept for realization `r` of formulation `f`; a candidate should therefore be treated as a formulation-process state rather than a composition-only point.

### One-point calibration rule

Within the supported local chemistry family, one state-specific viscosity anchor can calibrate the remaining measured temperature curve far better than formulation identity alone. The Agent can therefore use state anchors strategically rather than demanding a full curve for every realization.

### Distinct rheological-coordinate rule

Temperature response and thermal-hold stability are treated as distinct, differently tunable responses. If the design failure is thermal drift, the Agent must select a point and measurement window that directly test drift instead of relying on static viscosity.

### Defined chemical-perturbation rule

E1 `+P` is no longer an unresolved provenance flag. The verified condition is 0.025 mmol H3PO4 from a 0.1 mol/L standard solution added during dehydration. It remains outside the nominal same-composition primary fit, but the Agent may use it as a separate perturbation check: the observed viscosity level shifts while the thermal-response geometry remains closely compatible with the local shared shape. This distinction is exposed directly by the audited scientific tool.

### External-evidence rule

Database/literature evidence is converted into **machine-actionable scientific priors**. This layer is needed because the sparse E1-E5 local design can diagnose the thermal-hold failure but cannot by itself uniquely imply an acrylic/tackifier intervention outside the original reactive-core axes.

The evidence hierarchy is:

```text
local experiment -> diagnose failure and state uncertainty
paper-derived rheological rules -> define what response must be optimized
literature / PUR database -> define plausible intervention families and broad analogue regions
physical / uncertainty constraints -> control extrapolation
Agent judgment -> choose a testable next experiment
```

External evidence does not provide a guaranteed optimum and is not allowed to override contradictory local physical evidence. Directly commensurate numeric anchors, directional/noncommensurate evidence, and reconstructed conservative design principles must remain explicitly distinguished. No guidance rule may be derived from the held-out validation recipe or its later wet-lab outcome.

---

## 4. Why ablation is not the main paper question

The paper is not trying to prove that every internal software module is individually indispensable. The Skeptic and Robustness Adjudicator exist because they improve the usefulness and auditability of the experimental decision.

Accordingly, the primary validation logic is:

```text
physical/model discovery
-> Agent decision
-> frozen experiment point
-> human execution
-> physical result
```

The active Stage-1 study is a single outcome-blind preexperimental reconstruction. Repeated independent runs assess decision stability; they are not a separate replay-fidelity arm.

This avoids turning a materials-discovery paper into an LLM-systems paper.

---

## 5. Secondary reproducibility analysis

If repeated API runs are reported, they should answer a limited question:

> Under the same blinded evidence contract, does the full scientific workflow repeatedly prioritize a similar, defensible formulation region and produce scientifically valid rationales?

Useful secondary metrics include:

- selection distribution;
- Top-1/Top-3 region consistency;
- modifier-plane distance;
- abstention/failure rate;
- scientific-boundary violations;
- evidence/tool trace completeness.

These metrics support reproducibility. They do not replace physical validation.

---

## 6. Historical boundary

V3.3.1 is the current implementation of the discovery-to-experiment logic. It should not be described as the exact historical source code that generated the earlier validation formulation unless contemporaneous runtime provenance is recovered.
