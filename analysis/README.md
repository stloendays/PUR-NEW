# Statistical analysis outputs

This directory contains compact, reproducible results used by `docs/STATISTICAL_ANALYSIS.md`.

## Primary local result

The strongest current model is a **realization/state-specific vertical offset plus a shared quadratic thermal-response shape**:

```text
ln(eta_r(T)) = alpha_r + beta1 * dx + beta2 * dx^2 + epsilon
```

It is compared against formulation-only and more flexible alternatives in `results/local_model_comparison.csv` and `results/local_nested_model_tests.csv`.

`results/local_validation.csv` contains held-temperature and one-point-anchor validation summaries. The one-point-anchor test learns the shared thermal shape without the held-out realization and uses one measured viscosity from that realization only to set its vertical offset.

## Secondary local result

`results/local_hold_dynamics.csv` summarizes isothermal-hold trajectories. The fitted logarithmic slopes are treated as **apparent rheological drift descriptors**, not reaction-rate constants.

## External context

`results/external_family_master_curve_summary.csv` and `results/external_static_viscosity_vs_stability_pairs.csv` contain only derived compact subsets from the external PUR database. The full external database is intentionally not copied into this repository.

## Reproduction

Run local analysis only:

```bash
python scripts/statistical_analysis.py
```

Run local analysis plus external-database context:

```bash
python scripts/statistical_analysis.py \
  --external-db /path/to/hmpur_external.db
```

The run labels GJJ, ZYX and CHH are treated as opaque within-operator realization labels. They are not interpreted as different operators.
