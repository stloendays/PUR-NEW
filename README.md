# PUR-NEW

## State-conditioned rheological design and evidence-grounded Agent guidance for reactive polyurethane hot-melt adhesives

PUR-NEW asks one practical question:

> How should a reactive PUR formulation be selected when rheology depends on both composition and process realization, and when the selected decision must survive independent wet-lab testing?

The project treats each experiment as a **formulation-process state** rather than composition alone:

```text
formulation state
+ reaction / preparation history
+ thermal-hold state
+ observed variability
-> rheological response + structured uncertainty
```

## Scientific chronology

The manuscript follows the research team's confirmed order of work:

```text
original physical experiments
-> statistical / model findings
-> state-aware design theory
-> evidence-grounded Agent recommendation
-> freeze the validation formulation + rationale + criterion
-> human wet-lab execution
-> independent physical adjudication
-> support / reject / qualify the recommendation
-> update the next design state
```

The physical/statistical findings are **upstream of the Agent**. They establish why composition alone is insufficient, why process/realization state must remain explicit, and why temperature response and hold stability should be treated as separate design responses.

The current validation formulation was selected by the Agent **before its corresponding wet-lab result was known to the Agent**, according to the research team's confirmed chronology. The formulation is stored internally as `F1`; in manuscript prose it should be called the **Agent-selected validation formulation**.

The current repository does not yet contain the original contemporaneous freeze artifact. The author-confirmed chronology is documented transparently in [`docs/EXPERIMENTAL_CHRONOLOGY.md`](docs/EXPERIMENTAL_CHRONOLOGY.md); that later documentation is not presented as a substitute for an original timestamped record.

## Canonical workflow

```text
original local evidence
-> rheological state analysis
-> deterministic descriptors + uncertainty
-> evidence-grounded formulation hypothesis
-> scientific decision Agent
-> frozen candidate / probe / abstention + criterion
-> human wet-lab execution
-> separate physical adjudication
-> next-state update
```

The Agent is an **uncertainty-aware scientific recommender**. It does not synthesize material or operate rheology hardware.

## Original local evidence

The original chemistry uses PPG2000 / STEPANPOL PDP-70 / 4,4'-MDI and a five-point design around two axes:

- NCO:OH perturbation at fixed 50/50 PPG2000/PDP-70;
- PPG2000/PDP-70 composition perturbation at NCO:OH = 1.80.

At 120 C, two original formulations show strongly different hold-time drift:

| Formulation | 15 min | 60 min | 90 min | 15->60 drift | 15->90 drift |
|---|---:|---:|---:|---:|---:|
| E1 | 708.7 | 776.1 | 828.1 | +9.51% | +16.85% |
| E5 | 2210 | 3349 | 4267 | +51.54% | +93.08% |

These original measurements establish thermal-hold stability as a formulation-dependent design response rather than a single-point viscosity metadata field.

## Main statistical result: local state-shift master curve

Across repeated realizations, absolute viscosity changes strongly while the relative 80-130 C temperature-response shape is much more stable. A compact local model is:

```text
ln eta_r(T) = alpha_r + g(T) + epsilon
```

where `alpha_r` is a realization/state-specific viscosity scale and `g(T)` is a shared local thermal-response shape.

Key results:

```text
formulation-only R2                       ~= 0.895
state-shift shared-shape R2               ~= 0.998
held-temperature formulation-only error   ~= 1.406x
held-temperature state-aware error        ~= 1.055x
```

In a stricter leave-one-realization-out test, formulation identity plus temperature gives roughly **1.60x** multiplicative error for eligible E1/E2 realizations, whereas one viscosity anchor from the unseen realization reduces the error to about **1.065-1.098x**.

A model-light version of the same result is visible after normalizing every curve by its own 120 C viscosity: the seven relative curves collapse to only **3.4-10.3%** non-anchor CV.

The practical result is:

> Within the present local chemistry family, process/experimental realization mainly shifts viscosity scale; one state-specific anchor can calibrate the remaining measured temperature curve far better than formulation identity alone.

See:

- [`docs/STATISTICAL_ANALYSIS.md`](docs/STATISTICAL_ANALYSIS.md)
- [`docs/STATISTICAL_ROBUSTNESS.md`](docs/STATISTICAL_ROBUSTNESS.md)
- [`docs/MASTER_CURVE_COLLAPSE.md`](docs/MASTER_CURVE_COLLAPSE.md)

## Distinct rheological coordinates

The local apparent temperature-sensitivity descriptor is comparatively concentrated:

```text
mean apparent E_eta = 41.87 kJ/mol
SD                  = 2.27 kJ/mol
CV                  = 5.4%
```

whereas the fitted 120 C log-viscosity drift rates for E1 and E5 differ by about **4.29x**.

The project therefore uses the statement:

> **temperature response and thermal-hold stability are distinct, differently tunable rheological coordinates in the current design.**

It does not call them universally independent or orthogonal.

## External-database boundary

The external database contains 39 dense prepolymer curves and 4559 temperature-viscosity points. `ln(eta)` versus `1/T` is individually regular for most curves (median R2 about 0.9967), but the apparent thermal-sensitivity descriptor spans approximately **34.7-94.2 kJ/mol**.

Cross-validated composition models explain a substantial but incomplete fraction of the broad landscape:

```text
apparent thermal descriptor LOOCV R2 ~= 0.59-0.62
fitted 75 C log-viscosity LOOCV R2   ~= 0.80-0.82
```

The intended multiscale interpretation is:

```text
chemistry controls the broad rheological landscape
+
process / experimental state controls where a local realization sits within that landscape
```

## Agent-selected validation formulation

The current validation formulation is stored with internal ID `F1`:

```text
PPG2000 = 39.60
PDP-70  = 39.60
AC1920  = 17
TK100   = 5
MDI     = 20.19
```

The research team confirms that the Agent recommendation was made and frozen before the corresponding wet-lab outcome was known to the Agent.

The human experimental team then executed the formulation. Two 120 C hold repeats gave 15->60 min changes of:

```text
repeat 1: -0.16%
repeat 2: +3.04%
mean profile: approximately +1.47%
```

Compared on the same 15-60 min interval, this is substantially flatter than E1 (+9.51%) and E5 (+51.54%). The result is therefore treated as **physical support for the pre-result Agent recommendation with respect to thermal-hold stability**. It is not used as proof of one specific molecular mechanism.

## Evidence-constrained candidate-space formalization

The repository contains a reproducible V2 candidate-space abstraction built from:

```text
original E2 reactive core
+
independent acrylic-like evidence anchors
+
independent minor-tackifier-like evidence anchors
```

The formal grid is:

```text
acrylic-like modifier         = {0, 15, 20, 25}%
minor tackifier-like modifier = {0, 5, 10}%
```

for 12 coarse candidate cells.

Important provenance distinction:

- the **Agent-selected validation formulation** was recommended before its experimental outcome was known to the Agent;
- the **current exact software implementation of the V2 4x3 grid** was formalized later as a reproducible candidate-space/benchmark abstraction;
- therefore the grid should not be presented as the contemporaneous freeze artifact unless an older record establishes that.

See [`docs/CANDIDATE_SPACE_HYPOTHESIS.md`](docs/CANDIDATE_SPACE_HYPOTHESIS.md).

## Scientific Decision Agent V3

The paper-level Agent is no longer implemented as a single LLM call over a long prompt. V3 separates scientific decision making into auditable stages:

```text
STRUCTURAL EVIDENCE FIREWALL
          |
          v
       Planner
          |
          v
planner-selected scientific Actions
          |
          v
deterministic candidate analysis
(Pareto + robustness scenarios)
          |
          v
      Proposer
          |
          v
      Skeptic
(falsification / leakage / boundary audit)
          |
          v
       Judge
          |
          v
frozen recommendation / probe / abstention
```

The Planner decides what evidence is needed before selection. The Proposer ranks candidates. The Skeptic actively searches for reasons the provisional recommendation may be wrong or scientifically overstated. The Judge resolves those conflicts and may select a performance candidate, a robustness probe, an uncertainty probe, or abstain.

A dedicated deterministic Action exposes the paper's own pre-validation physical/model finding to the Agent:

```text
get_state_aware_rheology_summary
```

It recomputes realization spread, the 120 C-normalized curve collapse, apparent `E_eta` descriptors, and original E1/E5 hold-failure evidence directly from the original CSV files.

Other Actions include:

```text
query_external_priors
get_candidate_hypothesis
inspect_formulation
get_hold_stability
get_repeatability_risk
get_temperature_support
candidate_profile
compare_candidate_to_priors
audit_process_unknowns
stress_test_candidate
rank_candidate_support
```

See [`docs/AGENT_V3_ARCHITECTURE.md`](docs/AGENT_V3_ARCHITECTURE.md).

## Structural anti-leakage firewall

An audit of the earlier single-pass runner found that, although its precomputed Action context hid follow-up results, the runner also passed the complete `evidence_state.json` to the model. Because that file contains follow-up rows, an old blind replay could contain validation-outcome information in the raw evidence payload.

This has been corrected at the infrastructure level.

For `blind_pre_result` runs, the code now removes **before any LLM call**:

```text
target validation formulation identity
follow-up hold rows
follow-up mean-profile descriptors
post-result adjudication labels
controller-side held-out scoring targets
```

CI fails if the structurally filtered blind evidence contains `F1` or any `stage=follow_up` record.

Benchmark results generated before this correction should not be used as primary evidence of Agent superiority unless their exact payload can be shown independently to be leakage-free.

## Architecture benchmark

The Agent contribution is evaluated against strong baselines rather than a weak prompt-only comparator:

```text
B0 deterministic evidence ranker
B1 direct LLM blind
B2 single-pass tool-context model
A1 V3 without Skeptic
A2 V3 without deterministic robustness
A3 V3 without state-aware rheology Action
A4 full V3
```

All language-model conditions use the same model, the same candidate set, and the same structurally filtered pre-result evidence. `B2` receives the same state-aware/action information available to V3, so any V3 advantage must come from the **decision architecture**, not from seeing more data.

Primary benchmark outputs include:

```text
held-out-region rank
Top-1 / Top-3 regional recovery
modifier-plane distance
selection entropy across repeated runs
abstention rate
scientific-boundary violations
structural leakage rate
evidence/tool-trace completeness
tool-call count and success rate
```

Use 3-5 repeated runs only as a pilot. The paper-facing stochastic benchmark should normally use at least 30 runs per condition.

The manual workflow is:

```text
.github/workflows/agent-v3-benchmark.yml
```

and the controller-side scorer is:

```text
scripts/summarize_agent_benchmark.py
```

The architecture advantage is **not assumed**. It should be claimed only if full V3 improves selection quality/stability and scientific validity over the deterministic, direct, single-pass and ablated conditions.

## Benchmark role versus physical validation

Two claims are deliberately separated:

```text
physical validation:
pre-result Agent recommendation
-> human experiment
-> low-drift physical support

architecture validation:
full V3
vs deterministic / direct / single-pass / ablated conditions
under the same leakage-safe replay
```

The first establishes that an Agent-guided experimental decision was physically useful. The second tests whether the advanced Agent architecture contributes beyond a generic LLM or encoded literature prior.

See:

- [`docs/AGENT_V3_ARCHITECTURE.md`](docs/AGENT_V3_ARCHITECTURE.md)
- [`docs/EXPERIMENTAL_CHRONOLOGY.md`](docs/EXPERIMENTAL_CHRONOLOGY.md)
- [`docs/PROSPECTIVE_VALIDATION_PROTOCOL.md`](docs/PROSPECTIVE_VALIDATION_PROTOCOL.md)
- [`docs/BLIND_AGENT_BENCHMARK.md`](docs/BLIND_AGENT_BENCHMARK.md)

## Claim boundary

Supported by the current physical/model evidence:

- process/experimental realization materially affects measured viscosity level;
- a shared local thermal-response shape plus a state-specific scale describes the local data substantially better than formulation identity alone;
- one state anchor reconstructs eligible held-out local realization curves to roughly 6-10% multiplicative error;
- thermal-hold stability is a separate design response and differs strongly across tested formulations;
- the Agent-selected validation formulation has a much flatter matched 15-60 min hold response than E1/E5;
- the research team confirms that the Agent recommendation preceded knowledge of that validation result.

Implemented now:

- structural pre-LLM evidence firewall;
- state-aware rheology Action;
- Planner -> Actions -> deterministic robustness -> Proposer -> Skeptic -> Judge architecture;
- deterministic/direct/tool-context baselines;
- module-level ablations;
- repeated-run benchmark metrics and GitHub Actions workflow.

Not yet supported until the repeated benchmark is run:

- that full V3 statistically or consistently outperforms all baselines;
- that any one V3 module is necessary for recovery of the held-out-near region.

Provenance boundary:

- the current repository does not contain the original contemporaneous historical freeze artifact;
- the later author-confirmed chronology should not be represented as an original timestamp;
- V3 is the current improved implementation and should not be called the exact historical code that selected F1 unless matching archived provenance is recovered.

Not supported scientifically:

- that the local master curve is universal across reactive PUR chemistry;
- that thermal sensitivity and hold stability are universally statistically independent;
- that AC1920/TK100 stabilization is proven to arise from one specific molecular reaction pathway;
- that any external analogue percentage is a universal PUR optimum.
