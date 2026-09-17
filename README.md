# PUR-NEW

## Uncertainty-aware, Agent-guided formulation design for reactive polyurethane hot-melt adhesives

PUR-NEW is organized around a single experimental question:

> How should a reactive PUR formulation be selected when the measured rheology depends on both composition and process history?

The project treats a test point as a **formulation-process state**, not composition alone:

```text
formulation state
+ reaction / preparation history
+ thermal hold state
+ observed variability
-> rheological response + structured uncertainty
```

## Canonical workflow

```text
1. ingest measured formulation + rheology evidence
2. construct formulation-process state
3. derive temperature / hold / repeatability descriptors
4. decompose uncertainty
5. generate an admissible candidate set
6. Agent recommends one candidate or abstains
7. freeze recommendation + criterion + provenance
8. human operator executes the wet-lab experiment
9. create a separate experimental adjudication record
10. update response evidence and uncertainty for the next round
```

The Agent is an **uncertainty-aware scientific recommender**. It does not physically prepare samples or operate the instrument. Its scientific value is judged by whether the recommendation remains useful after human execution.

The full contract is in [`docs/WORKFLOW.md`](docs/WORKFLOW.md), with runtime boundaries in [`docs/AGENT_RUNTIME.md`](docs/AGENT_RUNTIME.md) and a practical future-round procedure in [`docs/RUNBOOK.md`](docs/RUNBOOK.md).

## What uncertainty means here

The workflow keeps five sources separate:

```text
measurement
repeatability
process history
extrapolation
evidence coverage
```

This prevents a single confidence score from hiding why a recommendation is fragile. See [`docs/UNCERTAINTY_MODEL.md`](docs/UNCERTAINTY_MODEL.md).

The Agent may recommend one of three useful experiment types:

```text
performance_candidate  -> seek a practically strong formulation state
robustness_probe       -> test survival under process perturbation
uncertainty_probe      -> reduce the most consequential evidence gap
```

It may also abstain when the evidence does not support a defensible recommendation.

## Current experimental system

The local system uses **PPG2000 / STEPANPOL PDP-70 / 4,4'-MDI**. The original local design varies NCO:OH and PPG2000/PDP-70 ratio.

The measured temperature sweeps decrease monotonically with temperature, while repeated realizations show that absolute viscosity can depend strongly on preparation/run history. Thermal holding makes the practical stability problem especially clear.

At 120 °C:

| Formulation | 15 min | 60 min | 90 min | 15->60 drift | 15->90 drift |
|---|---:|---:|---:|---:|---:|
| E1 | 708.7 | 776.1 | 828.1 | +9.51% | +16.85% |
| E5 | 2210 | 3349 | 4267 | +51.54% | +93.08% |

The follow-up formulation is reported on the source parts basis:

| PPG2000 | PDP-70 | AC1920 | TK100 | MDI |
|---:|---:|---:|---:|---:|
| 39.60 | 39.60 | 17 | 5 | 20.19 |

Two repeated 120 °C hold measurements give 15->60 min changes of **-0.16%** and **+3.04%**; the mean profile changes by about **+1.47%**.

The direct experimental conclusion is **rheological stabilization over the matched hold window**. The explanation that the added resin components reduce the effective reactive fraction remains a formulation rationale rather than direct molecular-kinetic proof.

The Agent-facing evaluation framework is in [`docs/AGENT_EVALUATION.md`](docs/AGENT_EVALUATION.md).

## Executable support layer

Numerical descriptors are deterministic; the Agent is not asked to recalculate them in free-form language.

```text
raw CSVs
-> scripts/build_evidence_state.py
-> deterministic evidence-state JSON
-> scripts/build_candidate_set.py
-> finite candidate-set JSON
-> scripts/build_agent_context.py
-> action-enriched context with evidence-access control
-> scripts/run_agent_recommendation.py
-> immutable recommendation JSON
-> human experiment
-> separate adjudication JSON
```

The recommendation runner reads API credentials from environment variables only, selects only from the supplied candidate set or abstains, hashes its evidence/prompt inputs, and refuses to overwrite a frozen recommendation.

The Agent now has deterministic evidence actions for external-prior retrieval, hold stability, repeatability risk, temperature support, formulation profiling, process-history auditing, analogue-region comparison, stress testing, and transparent candidate support ranking. External evidence is used as a directional formulation prior, not as a hidden copy of the wet-lab outcome.

## Blind multi-model benchmark

A dedicated benchmark now tests whether GPT-family Agents can recover the later-supported resin-modified formulation region **without seeing the follow-up thermal-hold result**.

The main condition is `blind_pre_result`. The evaluated model may see original-system evidence, structured uncertainty, database/literature analogue priors, deterministic action outputs, and the finite candidate grid. It may not see follow-up hold measurements, adjudication labels, or benchmark success labels.

The canonical modifier grid is:

```text
0, 5, 10, 15, 18, 20, 25%
```

The follow-up wet-lab recipe normalizes to about 18.12% combined AC1920+TK100, so post-hoc benchmark scoring reports exact 18% grid recovery as well as region-level Top-1/Top-3 metrics. The target region is available only to the benchmark controller after model responses are frozen; it is never inserted into the evaluated Agent payload.

See [`docs/BLIND_AGENT_BENCHMARK.md`](docs/BLIND_AGENT_BENCHMARK.md) and [`configs/blind_benchmark.json`](configs/blind_benchmark.json). A ready-to-use local implementation/execution prompt is stored in [`prompts/local_gpt_benchmark_operator.md`](prompts/local_gpt_benchmark_operator.md).

## Repository structure

```text
PUR-NEW/
├─ README.md
├─ configs/
│  ├─ workflow.json                         # machine-readable decision policy
│  ├─ action_catalog.json                   # deterministic Agent action contract
│  ├─ evidence_access_profiles.json         # blind/closed-loop evidence gates
│  ├─ formulation_priors.json               # external analogue formulation priors
│  └─ blind_benchmark.json                  # frozen benchmark/scoring policy
├─ docs/
│  ├─ WORKFLOW.md                           # canonical closed-loop workflow
│  ├─ BLIND_AGENT_BENCHMARK.md              # multi-model held-out benchmark protocol
│  ├─ AGENT_RUNTIME.md                      # deterministic/Agent/human boundary
│  ├─ RUNBOOK.md                            # future prospective-round procedure
│  ├─ UNCERTAINTY_MODEL.md                  # uncertainty decomposition
│  ├─ AGENT_EVALUATION.md                   # physical evaluation of recommendations
│  ├─ PROJECT_STATE.md                      # current state and next work
│  ├─ RESEARCH_NARRATIVE.md                 # scientific narrative
│  ├─ AGENT_ROLE.md                         # Agent evidence contract
│  ├─ EXPERIMENTAL_EVIDENCE.md              # executed measurements
│  └─ MANUSCRIPT_PLAN.md                    # paper-facing structure
├─ data/
│  ├─ README.md
│  ├─ external_evidence_hints.csv           # curated patent/paper analogue hints
│  ├─ formulations.csv
│  ├─ temperature_sweeps.csv
│  └─ thermal_hold.csv
├─ prompts/
│  ├─ agent_system.txt                      # uncertainty-aware recommendation contract
│  └─ local_gpt_benchmark_operator.md       # prompt for local benchmark execution
├─ records/
│  └─ README.md                             # immutable recommendation/adjudication layout
├─ schemas/
│  ├─ design_state.schema.json              # formulation + process + evidence state
│  ├─ candidate_set.schema.json             # finite admissible candidate set
│  ├─ agent_recommendation.schema.json      # immutable pre-result recommendation
│  └─ experiment_adjudication.schema.json   # separate post-result record
├─ src/pur_new/
│  ├─ metrics.py                            # deterministic scientific descriptors
│  └─ actions.py                            # deterministic evidence/candidate actions
├─ scripts/
│  ├─ build_evidence_state.py               # builds deterministic evidence state
│  ├─ build_candidate_set.py                # generates canonical candidate grid
│  ├─ build_agent_context.py                # action-enriched evidence-gated context
│  └─ run_agent_recommendation.py           # API Agent -> validated frozen record
└─ tests/
   └─ test_metrics.py                       # locks current descriptor calculations
```

## Paper-level claim

> Known process-state variables such as reaction history, thermal holding time and preparation perturbation should be represented explicitly in reactive-PUR formulation design. An uncertainty-aware Agent can use those variables to recommend which formulation-process state should be tested, while human-executed wet-lab measurements provide the final physical adjudication and update the next design round.

## Claim boundary

The repository does not claim that the Agent autonomously operates a laboratory, that rheology alone proves a specific molecular reaction pathway, or that a recommendation written after seeing a result is prospective.

A manuscript claim of **prospective physical validation of an Agent recommendation** requires a timestamped, frozen recommendation record created before the corresponding result was inspected. Without that provenance, the same experiment remains valid as **Agent-guided closed-loop validation**.

For the retrospective blind benchmark, the stronger defensible statement is that an evaluated Agent repeatedly recovered or prioritized a formulation region later supported by held-out physical measurements, provided the anti-leakage protocol is respected and the measured hit/Top-k frequencies are reported directly.
