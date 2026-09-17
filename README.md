# PUR-NEW

## Uncertainty-aware, evidence-grounded Agent design for reactive polyurethane hot-melt adhesives

PUR-NEW asks one practical question:

> How should a reactive PUR formulation be selected when rheology depends on both composition and process history, and when the final decision must still survive physical wet-lab testing?

The project treats each experiment as a **formulation-process state** rather than composition alone:

```text
formulation state
+ reaction / preparation history
+ thermal-hold state
+ observed variability
-> rheological response + structured uncertainty
```

## Canonical workflow

```text
original local evidence
-> deterministic rheology descriptors
-> structured uncertainty
-> evidence-derived candidate hypothesis
-> external database / literature retrieval
-> finite formulation-process candidate set
-> Agent recommendation or abstention
-> freeze rationale + alternatives + criterion + provenance
-> human wet-lab execution
-> separate physical adjudication
-> update next design round
```

The Agent is an **uncertainty-aware scientific recommender**. It does not operate laboratory hardware. Its value is judged by whether its evidence-grounded recommendation remains useful after human execution.

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

## V2 candidate-space hypothesis

The candidate space is now designed from **independent evidence rather than from the later follow-up recipe**.

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

The exact current follow-up recipe is **not** encoded as a discrete candidate.

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

Held-out follow-up formulation/outcome and controller-side scoring labels are excluded from the V2 replay payload.

## Benchmark status

The current V2 benchmark is explicitly a **retrospective held-out-result blind replay** for the already completed follow-up experiment.

Why: the formal V2 candidate-space hypothesis was written after the current follow-up result was already known.

Therefore V2 can test whether the evidence stack naturally prioritizes a region close to the held-out experiment, but it must not be described as prospectively validated for that already completed experiment.

Future rounds can become genuinely prospective once the V2 configuration is frozen before new experiments.

The V2 controller evaluates candidate rankings in a two-dimensional modifier plane:

```text
(acrylic-like %, minor-tackifier-like %)
```

rather than using the old exact-18%-total-modifier target.

See:

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
│  ├─ blind_benchmark.json                  # retained V1 history
│  └─ blind_benchmark_v2.json               # current benchmark policy
├─ docs/
│  ├─ CANDIDATE_SPACE_HYPOTHESIS.md         # why the V2 candidate region exists
│  ├─ BLIND_AGENT_BENCHMARK.md              # current V2 held-out benchmark
│  ├─ WORKFLOW.md
│  ├─ AGENT_RUNTIME.md
│  ├─ AGENT_EVALUATION.md
│  ├─ UNCERTAINTY_MODEL.md
│  ├─ RESEARCH_NARRATIVE.md
│  ├─ EXPERIMENTAL_EVIDENCE.md
│  └─ MANUSCRIPT_PLAN.md
├─ data/
│  ├─ external_evidence_hints.csv           # source-level analogue evidence + limitations
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
│  ├─ build_candidate_set.py                # V2 4x3 evidence-derived grid
│  ├─ build_agent_context.py
│  └─ run_agent_recommendation.py
└─ records/
```

## Claim boundary

Supported now:

- process state materially affects measured rheology;
- thermal-hold stability should be treated as a design response;
- the current follow-up formulation is much flatter over the matched hold window;
- independent external evidence justifies a coarse acrylic/tackifier candidate family;
- the V2 Agent can be tested in a held-out-result replay without exposing the follow-up result.

Not supported merely by the current repository:

- that V2 prospectively predicted the already completed follow-up experiment;
- that AC1920/TK100 stabilization is proven to arise from one specific molecular reaction pathway;
- that any external analogue percentage is a universal PUR optimum.

A prospective claim requires a timestamped frozen recommendation created before the corresponding future experiment is inspected.
