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
-> Agent recommendation or abstention
-> frozen candidate + rationale + criterion
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

The repository now contains a reproducible V2 candidate-space abstraction built from:

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

The V2 grid remains useful for evidence-to-candidate formalization, ablation, replay benchmarking, and future design rounds.

See [`docs/CANDIDATE_SPACE_HYPOTHESIS.md`](docs/CANDIDATE_SPACE_HYPOTHESIS.md).

## Agent actions

The Agent may use deterministic scientific capabilities including:

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

The decision layer is intended to preserve evidence trace, uncertainty, alternatives, and a falsifiable criterion rather than returning only an unsupported recipe.

## Benchmark role

The later V2 12-candidate replay is a **secondary reproducibility/ablation benchmark**, not the sole evidence for the Agent-validation claim.

Its purpose is to ask whether the formalized evidence stack favors a region compatible with the validation formulation when that formulation/outcome is hidden from the evaluated model. The primary experimental chronology is already:

```text
state-aware theory
-> pre-result Agent recommendation
-> freeze
-> human experiment
-> physical adjudication
```

See:

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

Provenance boundary:

- the current repository does not yet contain the original contemporaneous freeze artifact;
- the later author-confirmed chronology should not be represented as an original timestamp;
- the current V2 4x3 grid is a later formalization and should not be conflated with the historical recommendation interface unless older evidence is recovered.

Not supported:

- that the local master curve is universal across reactive PUR chemistry;
- that thermal sensitivity and hold stability are universally statistically independent;
- that AC1920/TK100 stabilization is proven to arise from one specific molecular reaction pathway;
- that any external analogue percentage is a universal PUR optimum.
