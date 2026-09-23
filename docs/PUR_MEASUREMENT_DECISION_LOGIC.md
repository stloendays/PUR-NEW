# PUR measurement decision logic

## Purpose

This document keeps the Agent layer tied to the physical PUR experiment. The decision object is not an abstract benchmark action; it is a choice of what laboratory measurement should be performed next for a formulation under a specific scientific uncertainty.

## Rheological coordinates and measurements

The manuscript separates three rheological coordinates:

```text
eta_ref  = realized viscosity level
S_T      = temperature-response coordinate
S_t      = thermal-hold / residence-time coordinate
```

They map to laboratory measurements as follows:

| Scientific uncertainty | Measurement | Laboratory meaning |
|---|---|---|
| Where is the current realized viscosity level? | M-ANCHOR or M-SWEEP | locate the processing-viscosity state |
| Has the temperature-response shape changed after chemistry modification? | M-SWEEP | directly measure 80-130 C and re-establish the thermal response |
| Is the formulation stable during hot residence? | M-HOLD-120 | measure 15-60 min drift at 120 C |
| Is the realized state reproducible across preparations/process histories? | M-REPEAT | quantify between-realization displacement |

## Why the processing-window condition matters experimentally

For the audited unmodified local family, one-point calibration is useful because a shared local thermal-response shape has already been established.

A resin-modified formulation changes the chemistry. Before that modified chemistry has been swept directly, the old shared shape is an unverified assumption.

The processing-window decision is therefore:

```text
cheap route:
110 C anchor
-> assume old shared thermal shape
-> infer 120-130 C processing viscosity

direct route:
80, 90, 100, 110, 120, 130 C sweep
-> measure the modified chemistry directly
-> establish both viscosity level and thermal-response shape
```

The frozen CBES processing-window comparison deliberately made the cheap anchor numerically attractive. Its deterministic VOI was 0.7392 versus 0.6875 for the full sweep. The advice-only selector nevertheless chose M-SWEEP in 10/10 runs because chemistry transfer was unverified.

This result supports a concrete laboratory rule:

> **For the first processing-window characterization after a meaningful chemistry shift, measure the full temperature sweep before reusing a one-point calibration shortcut.**

If the modified chemistry is subsequently shown to preserve the local thermal-response shape, one-point state calibration can be reconsidered for nearby follow-up states.

## Relationship to the completed thermal-hold experiment

The processing-window decision and the 120 C hold decision answer different questions.

```text
M-SWEEP
-> eta_ref + S_T
-> Is the modified PUR in the right processing-viscosity window, and what thermal shape does it have?

M-HOLD-120
-> S_t
-> Does viscosity remain stable during residence at processing temperature?
```

The completed resin-modified hold experiment addresses the second question and shows low matched-window drift. A future/full temperature sweep of the resin-modified formulation would address the first question and test whether stabilization changes only the time coordinate or also changes the thermal-response regime.

## Reader-facing architecture names

Use these semantic names in manuscripts, SI, figures and presentations:

- **CRB** — Candidate-Recovery Benchmark
- **RGES** — Rule-Grounded Experiment Selection
- **CBES** — Chemistry-Bounded Experiment Selection

Internal numbered development labels remain repository provenance only.
