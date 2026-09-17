# PUR-NEW data and model audit

## Purpose

This audit protects the paper's strongest claims from avoidable provenance and modeling confounds. It is not a search for additional significance. Analyses are chosen because they answer a pre-defined scientific question; whether the numerical result strengthens or weakens a claim is evaluated afterwards.

The main manuscript should emphasize only analyses that directly answer the paper's scientific questions. Exploratory or low-value checks need not be promoted to the main text, but a result is not silently deleted solely because it is unfavorable.

## 1. Realization labels and operator identity

GJJ, ZYX and CHH are run labels from the same operator. They are not operator categories. The compact dataset therefore treats them as opaque within-operator experimental realizations.

`data/realization_metadata.csv` now records this explicitly and also records what remains unknown, including parent-sample relations for one-day retests.

## 2. E1 `+P` chemistry flag

The E1 `+P` temperature sweep is explicitly described in the source table as a phosphoric-acid-labelled run. Because the exact additive identity/amount is not represented in `data/formulations.csv`, it is not a clean same-composition realization for a primary state-shift test.

The provenance-aware audit therefore treats E1 `+P` as `sensitivity_only` until the source chemistry is fully reconciled. The audited primary temperature dataset contains:

```text
36 temperature-viscosity points
6 complete realizations
3 nominal formulations
```

The original all-recorded-curves analysis remains reproducible, but the chemistry-audited result is the more conservative robustness check.

### Audited state-shift result

After excluding the chemistry-flagged E1 `+P` curve, the main structural result remains strong:

```text
formulation-only linear model:
  R2 ~= 0.852
  held-temperature multiplicative error ~= 1.442x

state-specific intercept + shared quadratic thermal shape:
  R2 ~= 0.9977
  held-temperature multiplicative error ~= 1.058x
```

Thus the state-shift conclusion is not created by the phosphoric-acid-labelled curve.

The audited apparent temperature-sensitivity descriptor remains concentrated:

```text
mean apparent E_eta ~= 42.05 kJ/mol
SD                  ~= 2.43 kJ/mol
CV                  ~= 5.77%
```

`E_eta` remains a rheological temperature-sensitivity descriptor, not a molecular reaction activation energy.

## 3. Model-free low-dimensional check

A model-free singular-value decomposition is applied to the six chemistry-audited complete log-viscosity curves after centering each temperature column.

The first between-realization mode explains approximately:

```text
99.63% of between-realization variance
```

and its loading vector has approximately:

```text
cosine similarity to a constant vertical shift ~= 0.9998
```

This provides a model-independent check of the same structural conclusion: within the current local chemistry family, the dominant realization-to-realization variation behaves approximately as a vertical log-viscosity shift across temperature.

This result should be used as supporting evidence rather than as a new mechanistic claim.

## 4. Leave-one-formulation-out one-point calibration

The earlier strict test left out one realization while retaining another realization of the same nominal formulation in training. A harder audit now removes an entire nominal formulation, learns the shared thermal shape from the remaining formulations, receives one anchor from the held formulation, and predicts its other temperatures.

At a 120 C anchor, the chemistry-audited multiplicative errors are approximately:

```text
held E1: 1.028x
held E2: 1.119x
held E3: 1.049x
```

Pooling all six held realizations gives approximately:

```text
1.099x multiplicative error
```

Across anchor temperatures, the pooled error remains roughly in the 1.06-1.10x range in the current dataset.

This supports a stronger but still local statement:

> Within the tested local chemistry family, a shared thermal-response shape can transfer across nominal formulations after one state-specific viscosity anchor is supplied.

The result remains interpolation within a narrow chemistry family, not universal extrapolation across PUR chemistry.

## 5. Day-1 retest provenance

The compact CSV identifies one-day retests but does not establish whether each retest is the same retained sample, a re-prepared aliquot, or an independent synthesis batch. Therefore:

- `retest_after_1d` is retained as provenance;
- day-1 rows are not automatically interpreted as independent batches;
- mixed-effects/hierarchical inference remains supporting rather than headline evidence;
- the main claims rely more heavily on curve structure, cross-validation and calibration tests.

If older notebook or lab records establish `parent_sample_id` or preparation batch identity, those fields should be added without rewriting the raw measurements.

## 6. External-database grouped validation

The 39 dense viscosity curves all belong to one external dataset source, so a literal leave-one-source-out test is impossible. A harder available check groups curves by `polyol_code x isocyanate_code` chemistry family.

One family contains an isocyanate category not represented anywhere else and is therefore structurally out-of-domain for categorical prediction. For the remaining predictable families, grouped-family validation is weaker than leave-one-curve-out validation, especially for the apparent thermal descriptor.

The consequence is methodological rather than damaging to the paper:

> External composition models should be used to describe the broad chemistry landscape and generalization boundary, not as the paper's main high-accuracy predictor.

The local state-shift/calibration result remains the primary quantitative modeling contribution.

Run the grouped audit only when the private/local HMPUR SQLite database is available:

```bash
python scripts/analysis_audit_v1.py \
  --external-db /path/to/hmpur_external.db \
  --output-dir derived/analysis_audit_v1
```

## 7. Time-window estimand

The current hold trajectories have different measurement schedules:

```text
E1/E5: 15, 30, 60, 90 min
validation formulation: 15, 30, 45, 60 min
```

Therefore the manuscript-facing comparison is fixed to the common **15-60 min endpoint stability index**. The E1/E5 fitted 15-90 min drift coefficients remain useful for demonstrating formulation dependence, but a 90 min value is never imputed for the validation formulation.

## 8. Agent scientific-tool integrity

V3 now routes `get_state_aware_rheology_summary` through `src/pur_new/scientific_tools.py`. The tool exposes the upstream state-shift model comparison, one-point calibration, thermal coordinate and E1/E5 hold contrast while excluding the validation formulation and outcome.

A unit test checks that the planner action receives the enriched tool result and that `F1` is absent from the tool payload.

## Reproducibility

Local audit:

```bash
python scripts/analysis_audit_v1.py \
  --output-dir derived/analysis_audit_v1
```

The script writes:

```text
provenance_aware_model_comparison.csv
leave_one_formulation_one_point.csv
leave_one_formulation_one_point_detail.csv
audit_summary.json
```

The audit is also executed in repository CI.
