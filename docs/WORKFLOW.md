# Canonical workflow

## Purpose

This file is the single source of truth for how formulation design, Agent recommendation and wet-lab validation connect in PUR-NEW.

The workflow is built around one principle:

> The Agent does not need to actuate the laboratory to be scientifically useful. Its role is to represent uncertainty, compare formulation-process states, recommend the next test, and expose the reasoning before a human executes the experiment.

## 1. Design state

A design point is not only a chemical composition. It is a joint state

```text
S = {x_chem, z_proc, e_obs, u, p}
```

where:

```text
x_chem = formulation state
z_proc = process state
e_obs  = currently observed experimental evidence
u      = uncertainty state
p      = provenance / missingness state
```

### Formulation state `x_chem`

Where available, record:

- component identities;
- component amounts / fractions in their source units;
- NCO:OH or other stoichiometric descriptors;
- formulation family / role labels.

### Process state `z_proc`

Where available, record:

- reaction / preparation history;
- reaction temperature and duration;
- addition / mixing history;
- sample age or storage state;
- hold temperature;
- hold time;
- preparation / batch / run perturbation;
- measurement sequence.

Unknown fields remain `null` / unknown. Missing process information is not converted to zero and is carried forward as uncertainty.

## 2. Stage A — Evidence ingest and audit

Before any recommendation, the workflow builds an evidence table from the current formulation and rheology records.

Required checks:

1. preserve the source-reported unit or explicitly mark it as unknown;
2. preserve run labels without inventing their meaning;
3. distinguish formulation identity from process realization;
4. distinguish measured values from derived descriptors;
5. mark missing process history explicitly;
6. do not extrapolate beyond the measured temperature/time range unless the output is labelled as extrapolation.

The result is an auditable state table rather than a single cleaned target column.

## 3. Stage B — Response characterization

The deterministic layer derives compact descriptors that the Agent may reason over.

### Temperature response

For a temperature sweep, retain the measured curve and derive a temperature-sensitivity descriptor only inside the measured range.

A model such as `ln(eta)` versus `1/T` may be used as a descriptive fit when supported by the data, but the fitted parameter is not automatically treated as a molecular activation energy.

### Hold stability

For a fixed temperature:

```text
SI(T; t0,t1) = [eta(T,t1) - eta(T,t0)] / eta(T,t0)
```

For design decisions where both upward and downward drift are undesirable, the workflow may use

```text
L_hold = abs(SI)
```

or the maximum absolute relative deviation over the measured hold window.

### Repeat / preparation sensitivity

When repeated realizations exist, the workflow records spread separately from the nominal response. Depending on sample count and scale, this may include:

- coefficient of variation;
- log max/min spread;
- absolute range;
- replicate-specific trajectories.

With very small `n`, these are descriptive uncertainty measures, not inferential population estimates.

## 4. Stage C — Uncertainty decomposition

The Agent does not collapse every uncertainty source into one opaque confidence number.

It receives a structured uncertainty vector:

```text
U = {
  measurement,
  repeatability,
  process_history,
  extrapolation,
  evidence_coverage
}
```

The exact numerical estimator may evolve, but these dimensions remain separate so the recommendation can state *why* it is uncertain.

See `UNCERTAINTY_MODEL.md` for the contract.

## 5. Stage D — Candidate generation

Candidate states are generated from chemically and operationally admissible formulation-process combinations.

Each candidate must have a declared decision mode:

```text
performance_candidate   # expected to satisfy the practical objective
robustness_probe        # tests sensitivity to a known process perturbation
uncertainty_probe       # primarily reduces an important evidence gap
```

The workflow does not require every round to chase the nominal best formulation. A point may be valuable because it tests whether a recommendation survives realistic process variation.

## 6. Stage E — Agent recommendation

The Agent receives only the current state, derived descriptors, uncertainty vector, constraints and candidate set. It must produce an inspectable recommendation.

A generic performance loss is

```text
J_perf = w_eta  * L_viscosity
       + w_T    * L_temperature_response
       + w_S    * L_hold_stability
       + w_R    * L_repeatability
       + feasibility_penalties
```

The acquisition policy then trades performance, robustness and information value conceptually as

```text
A(candidate) = -J_perf - lambda_U * U_penalty + beta_IG * information_value
```

This equation defines the decision logic, not a claim that every term is already calibrated numerically. If a term cannot be estimated from available evidence, the Agent must expose that gap instead of inventing a value.

### Recommendation output

The primary recommendation record includes:

- selected candidate;
- decision mode;
- alternatives considered;
- uncertainty vector;
- selection rationale;
- process conditions to be held fixed / deliberately perturbed;
- pre-result acceptance criterion;
- provenance and timestamp;
- abstention reason if no candidate is adequately supported.

## 7. Stage F — Freeze before execution

Before a result can be called prospective evidence, the recommendation record is frozen before the corresponding result is inspected.

The frozen record is immutable. Experimental results are never written back into the original recommendation fields.

The workflow stores the later measurement as a separate adjudication object linked by `recommendation_id`.

## 8. Stage G — Human wet-lab execution

The human operator performs sample preparation and measurement.

The experiment should follow the recommended formulation/process state as closely as practicable and record deviations explicitly. The Agent is not credited with physical actuation.

The executed record should capture, where available:

- actual formulation amounts;
- actual preparation history;
- actual hold temperature/time;
- instrument / method metadata;
- deviations from the recommended state;
- raw measurements and replicate identity.

## 9. Stage H — Physical adjudication

The wet-lab result is the physical judge of the recommendation.

Adjudication states are:

```text
supported
partially_supported
falsified
out_of_domain
```

The label is determined against the pre-result acceptance criterion, not by rewriting the criterion after seeing the result.

A recommendation can still be scientifically useful when falsified if it identifies which uncertainty dimension or process variable must be updated.

## 10. Stage I — Closed-loop update

After adjudication, the workflow updates four things separately:

```text
response evidence
uncertainty calibration
process-state sensitivity
candidate priorities
```

The next recommendation is generated from the new state. Historical recommendation and adjudication records remain immutable.

## 11. Current paper-facing interpretation

The existing experiments already establish that thermal-hold response and preparation/run variation are important enough to be treated as design variables rather than incidental metadata.

The current follow-up formulation shows a much flatter 120 C hold response over the shared 15-60 min window than the unstable original cases. The strongest Agent-specific wording depends on chronology: a prospective-validation claim requires a recoverable pre-result recommendation record; otherwise the result is described as Agent-guided closed-loop validation.

## 12. Workflow invariants

The following rules should not change between iterations:

1. formulation and process state are distinct but jointly represented;
2. uncertainty sources remain decomposed;
3. unknown values are not silently imputed as zero;
4. measured and derived data remain distinguishable;
5. recommendation precedes adjudication;
6. the human performs the laboratory operation;
7. the wet-lab result is allowed to falsify the recommendation;
8. claim strength follows provenance strength;
9. mechanistic hypotheses are not upgraded to measured facts without direct evidence;
10. every new design round is traceable to the evidence state that produced it.
