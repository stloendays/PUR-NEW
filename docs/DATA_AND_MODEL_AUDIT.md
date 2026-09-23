# PUR-NEW data and model audit

## Purpose

This audit protects the paper's strongest claims from avoidable provenance and modeling confounds. It is not a search for additional significance. Analyses are chosen because they answer a pre-defined scientific question; whether the numerical result strengthens or weakens a claim is evaluated afterwards.

The main manuscript should emphasize only analyses that directly answer the paper's scientific questions. Exploratory or low-value checks need not be promoted to the main text, but a result is not silently deleted solely because it is unfavorable.

## 1. Realization labels and operator identity

R01, R02 and R03 are run labels from the same operator. They are not operator categories. The compact dataset therefore treats them as opaque within-operator experimental realizations.

`data/realization_metadata.csv` records the same-operator labels explicitly. Verified measurement metadata further establish that temperature-sweep repeatability used the same mother sample across temperatures within a sweep; distinct run labels are therefore not automatically interpreted as independent synthesis batches.

## 2. E1 `+P` verified phosphoric-acid perturbation

The chemistry of the E1 `+P` temperature sweep is now resolved from the laboratory record. The sample received **0.025 mmol H3PO4** from a **0.1 mol/L H3PO4 standard solution** during the **dehydration stage**. This corresponds to 0.25 mL of standard solution and 2.45 mg of H3PO4.

Because this is a deliberate chemical perturbation rather than nominal E1, it remains outside the primary same-composition state-shift population. It is now treated as a defined **chemical-perturbation check**, not as unresolved provenance. The audited primary temperature dataset remains:

```text
36 temperature-viscosity points
6 complete realizations
3 nominal formulations
```

The perturbation curve itself is informative. Its apparent thermal-response descriptor is:

```text
E1 +P apparent E_eta = 40.77 kJ/mol
ln(eta) vs 1/T R2    = 0.9979
```

The six-realization primary distribution is 42.05 ± 2.43 kJ/mol, placing E1 `+P` only 0.53 SD below the primary mean. When the thermal-shape coefficients learned from the six primary realizations are held fixed and only a curve-specific intercept is fitted to E1 `+P`, the multiplicative RMSE is 1.034×. Anchoring the same shared shape with only the 120 °C E1 `+P` viscosity predicts the other five temperatures with a multiplicative RMSE of 1.039×.

Relative to the available E1 R01 day-1 record, the `+P` viscosities are 9.5–17.1% lower across 80–130 °C, with a geometric mean ratio of 0.879. This comparator is retained as an observational reference rather than a paired treatment-control estimate because its parent-batch relationship is not established.

The scientific use of E1 `+P` is therefore specific: a defined low-dose acid perturbation leaves the temperature-response geometry compatible with the shared local shape while shifting the observed viscosity level. This strengthens the separation between viscosity scale and thermal-response shape without adding the perturbed curve to the primary same-composition fit.

Detailed records are in `data/experimental_perturbations.csv` and the numerical comparison is stored in `derived/e1_phosphoric_acid_perturbation.csv` and `derived/e1_phosphoric_acid_summary.csv`.

### Audited state-shift result

After excluding the chemistry-flagged E1 `+P` curve, the main structural result remains strong:

```text
formulation-only intercept + shared quadratic thermal shape:
  R2 ~= 0.8553
  held-temperature multiplicative error ~= 1.423x

realization-specific intercept + shared quadratic thermal shape:
  R2 ~= 0.9977
  held-temperature multiplicative error ~= 1.058x

linear-basis sensitivity check:
  formulation-only R2 ~= 0.8519
  state-conditioned R2 ~= 0.9943
```

Thus the state-shift conclusion is not created by the phosphoric-acid-labelled curve or by comparing different thermal-response orders.

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

## 5. Repeat-measurement provenance

Verified laboratory metadata establish that the temperature-sweep repeatability protocol used the same mother sample across temperatures within a sweep rather than independently resynthesizing material for each temperature point. The compact records still do not establish independent synthesis-batch identity across every distinct run label. Therefore:

- `retest_after_1d` is retained as provenance;
- temperature points within a sweep are treated as repeated rheological measurements on a common mother sample;
- distinct run labels are described as measurement realizations rather than assumed independent synthesis batches;
- mixed-effects/hierarchical inference remains supporting rather than headline evidence;
- the main claims rely on curve structure, cross-validation and calibration tests rather than an independence assumption that the source record does not establish.

The verified instrument, unit, equilibration, thermal-hold and sample-preparation conditions are versioned in `data/experimental_methods_metadata.csv`.

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
