# Uncertainty model

## Why uncertainty is explicit

For this project, uncertainty is not a decorative confidence score. It is part of the design state because the measured PUR rheology depends on formulation, preparation history and time at temperature.

The Agent therefore reasons over a vector of uncertainty sources rather than one undifferentiated scalar.

## Canonical uncertainty vector

```text
U = {
  u_measurement,
  u_repeatability,
  u_process_history,
  u_extrapolation,
  u_evidence_coverage
}
```

### `u_measurement`

Uncertainty associated with the measurement itself, including instrument resolution/window, readout variability and method-specific limits when those are known.

If the instrument uncertainty is not reported, this field remains unknown rather than being assigned an arbitrary percentage.

### `u_repeatability`

Observed spread among repeated realizations of the same nominal formulation and nominal test condition.

Possible descriptive summaries include:

```text
CV = sd / mean
log_spread = log(max / min)
range = max - min
```

With only two repeats, these quantities are descriptive. They should not be presented as well-estimated population statistics.

### `u_process_history`

Uncertainty caused by incomplete or variable preparation/reaction history.

Examples include uncertainty in:

- reaction duration;
- reaction temperature;
- mixing / addition history;
- storage age;
- elapsed time before measurement;
- batch or preparation realization.

This term may be high even when instrumental repeatability is good.

### `u_extrapolation`

Penalty for asking the decision layer to reason outside directly observed temperature, hold-time, composition or stoichiometric support.

Default rule:

```text
inside observed support  -> low / none
near boundary            -> elevated
outside support          -> high or reject
```

The exact numerical mapping should be fixed before using it for a prospective decision.

### `u_evidence_coverage`

Represents how complete the evidence is for the claim being made.

Examples of low coverage:

- a candidate has no hold-time trajectory;
- process history is missing;
- only one realization exists;
- material identity/specification is incomplete;
- the recommendation depends on an unmeasured variable.

## No forced scalar confidence

The primary record should preserve the vector. A scalar penalty may be calculated for ranking only after the aggregation rule is declared.

For example:

```text
U_penalty = a_m * u_measurement
          + a_r * u_repeatability
          + a_p * u_process_history
          + a_x * u_extrapolation
          + a_e * u_evidence_coverage
```

This is a policy layer, not a scientific identity. The weights must not be tuned after seeing the result of the experiment they are meant to select.

## Decision margin

A recommendation should record not only the top candidate, but also how clearly it is preferred.

Conceptually:

```text
margin = acquisition(top_1) - acquisition(top_2)
```

A small margin means the decision is fragile even if top-1 is numerically defined. In that case the Agent may recommend a robustness or uncertainty probe rather than claiming a uniquely superior formulation.

## Uncertainty-aware decision modes

The same uncertainty state can justify different actions.

### Performance candidate

Use when evidence coverage is adequate and the candidate remains attractive after uncertainty penalties.

### Robustness probe

Use when the main scientific question is whether a promising formulation survives a realistic perturbation in reaction/preparation/hold history.

### Uncertainty probe

Use when the dominant limitation is an evidence gap and the most valuable experiment is the one expected to reduce that gap.

### Abstain / human review

Use when a recommendation would depend primarily on unsupported extrapolation, unknown material identity, incompatible measurements or an unresolved conflict in the evidence.

## Adjudicating uncertainty predictions

When the Agent states an uncertainty-aware expectation, the later experiment should answer a predeclared question such as:

```text
Does the measured 15-60 min hold drift remain within the stated stability criterion?
Does the candidate preserve its qualitative advantage across repeated realizations?
Does the observed variability fall inside the predeclared uncertainty band?
```

The experiment does not need to reproduce an exact point estimate for the recommendation to be useful. The adjudication should match the type of claim that was frozen.

## Current project implication

The observed spread among repeated original-system measurements and the large difference between E1 and E5 hold trajectories demonstrate why repeatability/process-history uncertainty and thermal-hold stability must remain explicit. The two repeated follow-up trajectories provide direct evidence that the selected follow-up formulation is much flatter over the shared 15-60 min window, but they do not by themselves identify which molecular kinetic pathway caused the stabilization.
