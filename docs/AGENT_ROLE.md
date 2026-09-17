# Agent role and evidence contract

## Position of the Agent

The Agent is an **uncertainty-aware scientific recommender** inside a human-in-the-loop experimental workflow.

It does not actuate laboratory hardware. Its job is to turn the current formulation/process/evidence state into a traceable recommendation about **what should be tested next and why**.

The canonical execution sequence is defined in `WORKFLOW.md`.

## 1. Inputs

The Agent receives four explicit blocks.

### Formulation state

```text
component identities
component amounts / fractions
stoichiometric descriptors when known
formulation-family context
```

### Process state

```text
reaction / preparation history
hold temperature and time
sample age / storage state when known
preparation or batch perturbation
measurement sequence
```

### Evidence state

```text
measured rheology
hold trajectories
replicate spread
missing fields
support range of available evidence
```

### Uncertainty state

```text
measurement
repeatability
process_history
extrapolation
evidence_coverage
```

Unknown information remains unknown. The Agent may reason about missingness; it may not silently replace it with zero.

## 2. What the Agent actually does

The Agent follows five decision steps:

```text
STATE -> AUDIT -> COMPARE -> RECOMMEND -> FREEZE
```

### STATE

Read the formulation-process state rather than composition alone.

### AUDIT

Identify missing information, unsupported extrapolation and dominant uncertainty sources.

### COMPARE

Compare admissible candidates using the current performance objective, robustness requirements and information value.

### RECOMMEND

Choose one of four actions:

```text
performance_candidate
robustness_probe
uncertainty_probe
abstain
```

### FREEZE

Store the selected candidate, alternatives, uncertainty vector, acceptance criterion and provenance before physical result inspection whenever a prospective claim is intended.

## 3. Decision objective

The Agent should not optimize viscosity magnitude alone.

The generic design loss is

```text
J_perf = w_eta * L_viscosity
       + w_T   * L_temperature_response
       + w_S   * L_hold_stability
       + w_R   * L_repeatability
       + feasibility_penalties
```

The ranking policy may further penalize uncertainty and reward information value:

```text
A(candidate) = -J_perf - lambda_U * U_penalty + beta_IG * information_value
```

These expressions define the structure of the decision problem. They do not imply that all numerical weights are already calibrated. Any numerical weights used for a prospective test must be frozen before seeing that result.

## 4. Recommendation contract

A paper-facing recommendation must contain at least:

```text
recommendation_id
created_utc
record_status
decision_mode
selected_candidate
alternatives_considered
constraints
structured uncertainty
selection_rationale
pre-result acceptance criterion
provenance
adjudication status
```

The machine-readable contract is `../schemas/agent_recommendation.schema.json`.

The most important scientific object is therefore not an Agent-generated paragraph. It is the linked pair:

```text
frozen pre-result recommendation
<->
human-executed post-result adjudication
```

## 5. Human execution and experimental authority

After the recommendation is frozen, a human operator performs the preparation and rheology measurement.

The laboratory result has authority over the recommendation. The Agent must be allowed to be wrong.

Possible adjudication states are:

```text
supported
partially_supported
falsified
out_of_domain
```

A falsified recommendation is not deleted. It becomes evidence for updating the uncertainty model or process-state representation.

## 6. Allowed Agent claims

The Agent may:

- compare candidate formulation-process states;
- quantify or summarize uncertainty;
- flag weakly supported extrapolation;
- recommend a performance candidate;
- recommend a robustness probe;
- recommend an uncertainty-reduction experiment;
- explain why one candidate is preferred;
- abstain when evidence is insufficient.

The Agent may not:

- claim that a sample was physically prepared when it was not;
- invent an unmeasured result;
- hide missing process history;
- convert a retrospective choice into a prospective prediction;
- rewrite an acceptance criterion after seeing the result;
- claim a molecular mechanism from rheology alone;
- present a fragile top-1 result as uniquely superior when the decision margin is negligible.

## 7. Current paper-facing interpretation

The current experiments show why this architecture is necessary: rheology changes with process realization and thermal-hold history, while the follow-up formulation shows a substantially flatter 120 °C response over the shared 15-60 min window.

The strongest Agent-specific wording depends on provenance. If a timestamped recommendation trace predating the follow-up measurement is available, the experiment may adjudicate that recommendation prospectively. If not, the result remains a valid Agent-guided closed-loop validation without retroactive preregistration language.
