# PUR-NEW

## State-conditioned rheological design and evidence-grounded Agent guidance for reactive polyurethane hot-melt adhesives

PUR-NEW asks one practical question:

> How should a reactive PUR formulation be selected when rheology depends on both composition and process realization, and when the final decision must still survive physical wet-lab testing?

The project treats each experiment as a **formulation-process state** rather than composition alone:

```text
formulation state
+ reaction / preparation history
+ thermal-hold state
+ observed variability
-> rheological response + structured uncertainty
```

## Scientific chronology

The manuscript follows the actual order of the work:

```text
physical / model findings
-> state-aware design theory
-> evidence-constrained candidate space
-> Agent sees pre-result evidence only
-> Agent selects and freezes a new candidate + rationale + criterion
-> human wet-lab execution
-> independent physical adjudication
-> support / reject / qualify the recommendation
-> update the next design state
```

The physical/statistical findings are therefore **upstream of the Agent**. They establish why composition alone is insufficient, why process/realization state must remain explicit, and why temperature response and hold stability should be separate design responses.

The Agent is then asked to act on that theory. For the prospective validation round, the corresponding wet-lab outcome is not available to the Agent when the recommendation is made. The candidate, rationale, uncertainty assessment and falsifiable criterion are frozen before the human experiment is evaluated. The later experiment is the external physical adjudicator: it can support, partially support, reject, or render the recommendation inconclusive.

See [`docs/PROSPECTIVE_VALIDATION_PROTOCOL.md`](docs/PROSPECTIVE_VALIDATION_PROTOCOL.md).

## Canonical runtime workflow

```text
original local evidence
-> rheological state analysis
-> deterministic descriptors + uncertainty
-> evidence-derived candidate hypothesis
-> external database / literature retrieval
-> finite formulation-process candidate set
-> blinded Agent recommendation or abstention
-> freeze rationale + alternatives + criterion + provenance
-> human wet-lab execution
-> separate physical adjudication
-> update next design round
```

The Agent is an **uncertainty-aware scientific recommender**. It does not operate laboratory hardware. Its value is judged by whether its pre-frozen recommendation remains useful after human execution.

## Current local evidence

The original local chemistry uses PPG2000 / STEPANPOL PDP-70 / 4,4'-MDI and a five-point design around two axes:

- NCO:OH perturbation at fixed 50/50 PPG2000/PDP-70;
- PPG2000/PDP-70 composition perturbation at NCO:OH = 1.80.

At 120 C, the original formulations show substantial hold-time drift:

| Formulation | 15 min | 60 min | 90 min | 15->60 drift | 15->90 drift |
|---|---:|---:|---:|---:|---:|
| E1 | 708.7 | 776.1 | 828.1 | +9.51% | +16.85% |
| E5 | 2210 | 3349 | 4267 | +51.54% | +93.08% |

The already executed follow-up formulation gave two 120 C repeated 15->60 min changes of **-0.16%** and **+3.04%**; the mean profile changed by about **+1.47%**.

The direct local conclusion is therefore **rheological stabilization over the matched hold window**. A specific molecular mechanism is not claimed from rheology alone.

## Main statistical result: a local state-shift master curve

The temperature-sweep data show a stronger structure than simple run-to-run variability.

Across repeated realizations, absolute viscosity can change by several-fold, but the relative 80-130 C thermal-response shape is much more stable. A compact local model is:

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

A stricter test removes one complete realization from training. For E1/E2 cases where the nominal formulation remains represented, formulation identity plus temperature gives roughly **1.60x** multiplicative error, whereas one viscosity anchor from the held realization reduces the error to about **1.065-1.098x** across possible anchor temperatures.

A model-free version of the same result is visible by dividing every curve by its own 120 C viscosity. The seven normalized curves collapse to a narrow relative profile with only **3.4-10.3%** non-anchor CV across realizations.

This supports the practical statement:

> Within the present local chemistry family, a new process realization primarily changes viscosity scale; one state-specific anchor can calibrate the rest of the measured temperature curve far better than formulation identity alone.

See:

- [`docs/STATISTICAL_ANALYSIS.md`](docs/STATISTICAL_ANALYSIS.md)
- [`docs/STATISTICAL_ROBUSTNESS.md`](docs/STATISTICAL_ROBUSTNESS.md)
- [`docs/MASTER_CURVE_COLLAPSE.md`](docs/MASTER_CURVE_COLLAPSE.md)

## Two rheological coordinates

The local apparent temperature-sensitivity descriptor is comparatively concentrated:

```text
mean apparent E_eta = 41.87 kJ/mol
SD                  = 2.27 kJ/mol
CV                  = 5.4%
```

whereas the fitted 120 C log-viscosity drift rates for E1 and E5 differ by about **4.29x**, and F1 moves into a low-drift regime.

The intended claim is therefore:

> **temperature response and thermal-hold stability are distinct, differently tunable rheological coordinates in the current design.**

The project does not call them universally independent or orthogonal. The broad database also shows that apparent thermal sensitivity changes substantially across chemistry families.

## External-database boundary

The external database contains 39 dense prepolymer curves and 4559 temperature-viscosity points. `ln(eta)` versus `1/T` is individually regular for most curves (median R2 about 0.9967), but the apparent thermal-sensitivity descriptor spans approximately **34.7-94.2 kJ/mol**.

Cross-validated composition models explain a substantial but incomplete fraction of this broad landscape:

```text
apparent thermal descriptor LOOCV R2 ~= 0.59-0.62
fitted 75 C log-viscosity LOOCV R2   ~= 0.80-0.82
```

Thus the project distinguishes two levels:

```text
chemistry controls the broad rheological landscape
+
process / experimental state controls where a local realization sits within that landscape
```

The external thermal-curve dataset and the nine viscosity-rise-rate patent records do not share sample identifiers, so they are not used to claim direct external statistical independence between thermal sensitivity and stability.

## V2 candidate-space hypothesis

The candidate space is designed from **independent evidence rather than from the later follow-up recipe**.

### Local reactive-core anchor

E2 is the geometric centre of the original local five-point design. Its normalized reactive core is approximately:

```text
PPG2000 39.9047%
PDP-70  39.9047%
MDI     20.1907%
```

### Acrylic-like axis

Independent external PUR evidence provides coarse anchors at:

```text
0, 15, 20, 25%
```

- 15%: peer-reviewed high-temperature reactive-PUR study;
- ~20%: repeated acrylic-tackifying-resin patent examples;
- 25%: acrylic-copolymer example with direct hot-hold viscosity-stability data.

### Minor tackifier-like axis

Independent PUR formulation evidence supports:

```text
0, 5, 10%
```

- ~5% represents repeatedly documented ~4.8-6.4% tackifier/hydrocarbon-resin examples;
- 10% is a conservative coarse upper level supported by published formulation guidance.

### V2 finite grid

```text
{0,15,20,25}% acrylic-like
x
{0,5,10}% minor tackifier-like
= 12 candidates
```

For each candidate the original E2 reactive core is scaled into the remaining total-formulation fraction.

The exact historical F1 follow-up recipe is **not** encoded as a discrete candidate.

See [`docs/CANDIDATE_SPACE_HYPOTHESIS.md`](docs/CANDIDATE_SPACE_HYPOTHESIS.md).

## Agent evidence/actions

The full Agent may use legitimate scientific capabilities including:

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

The Agent is allowed to see pre-result database/literature evidence and uncertainty-aware actions. Those are core parts of the system, not leakage.

For a prospective experimental round, the target candidate's later wet-lab measurements and any outcome-derived controller labels are excluded until after the recommendation record is frozen.

## Retrospective replay versus prospective validation

Two different evaluation modes are kept separate.

### Historical F1 / V2 replay

The V2 replay of the already completed F1 follow-up is a **retrospective held-out-result blind replay**. It asks whether the evidence stack, when the known F1 outcome is hidden from the evaluated model, prioritizes a compatible region. It must not be described as prospective validation of that historical F1 experiment.

### Prospective Agent-to-wet-lab cycle

The main validation chronology for a new candidate is stronger:

```text
state-aware theory established first
-> Agent blinded to the corresponding future wet-lab outcome
-> recommendation + criterion frozen
-> human experiment executed
-> result revealed only for adjudication
```

This is the chronology to use for a prospective Agent-validation claim.

See:

- [`docs/PROSPECTIVE_VALIDATION_PROTOCOL.md`](docs/PROSPECTIVE_VALIDATION_PROTOCOL.md)
- [`docs/BLIND_AGENT_BENCHMARK.md`](docs/BLIND_AGENT_BENCHMARK.md)
- [`configs/blind_benchmark_v2.json`](configs/blind_benchmark_v2.json)
- [`prompts/local_gpt_benchmark_operator.md`](prompts/local_gpt_benchmark_operator.md)

## Repository structure

```text
PUR-NEW/
├─ README.md
├─ configs/
│  ├─ workflow.json
│  ├─ action_catalog.json
│  ├─ evidence_access_profiles.json
│  ├─ formulation_priors.json
│  ├─ blind_benchmark.json
│  └─ blind_benchmark_v2.json
├─ docs/
│  ├─ STATISTICAL_ANALYSIS.md
│  ├─ STATISTICAL_ROBUSTNESS.md
│  ├─ MASTER_CURVE_COLLAPSE.md
│  ├─ CANDIDATE_SPACE_HYPOTHESIS.md
│  ├─ PROSPECTIVE_VALIDATION_PROTOCOL.md
│  ├─ BLIND_AGENT_BENCHMARK.md
│  ├─ WORKFLOW.md
│  ├─ AGENT_RUNTIME.md
│  ├─ AGENT_EVALUATION.md
│  ├─ UNCERTAINTY_MODEL.md
│  ├─ RESEARCH_NARRATIVE.md
│  ├─ EXPERIMENTAL_EVIDENCE.md
│  └─ MANUSCRIPT_PLAN.md
├─ data/
│  ├─ external_evidence_hints.csv
│  ├─ formulations.csv
│  ├─ temperature_sweeps.csv
│  └─ thermal_hold.csv
├─ prompts/
│  ├─ agent_system.txt
│  └─ local_gpt_benchmark_operator.md
├─ src/pur_new/
│  ├─ metrics.py
│  └─ actions.py
├─ scripts/
│  ├─ build_evidence_state.py
│  ├─ statistical_analysis.py
│  ├─ statistical_robustness.py
│  ├─ master_curve_collapse.py
│  ├─ build_candidate_set.py
│  ├─ build_agent_context.py
│  └─ run_agent_recommendation.py
└─ records/
```

## Claim boundary

Supported by the current physical/model evidence:

- process/experimental realization materially affects measured viscosity level;
- within the local measured chemistry family, a shared thermal-response shape plus a state-specific scale describes the data substantially better than formulation identity alone;
- one state anchor reconstructs held-out local realization curves to roughly 6-10% multiplicative error;
- thermal-hold stability is a separate design response and differs strongly across tested formulations;
- the historical F1 follow-up is much flatter over the matched hold window;
- independent external evidence justifies a coarse acrylic/tackifier candidate family.

Methodological chronology for prospective validation:

- state-aware design theory is established before the new Agent selection;
- the Agent does not see the corresponding future wet-lab outcome before freeze;
- the recommendation, rationale, uncertainty and criterion are frozen before adjudication;
- humans execute the experiment;
- the later experimental result independently supports, rejects, or qualifies the recommendation.

Not supported merely by the current repository:

- that the local master curve is universal across reactive PUR chemistry;
- that thermal sensitivity and hold stability are universally statistically independent;
- that the historical V2 replay prospectively predicted the already completed F1 experiment;
- that AC1920/TK100 stabilization is proven to arise from one specific molecular reaction pathway;
- that any external analogue percentage is a universal PUR optimum.
