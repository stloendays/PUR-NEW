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

The run labels R01, R02 and R03 are treated as opaque within-operator realization labels. They are not interpreted as different operators.


## Strict local transfer and bounded extrapolation

The chemistry-audited transfer analysis now has two levels:

1. `local_leave_one_formulation_one_point.csv` and `local_leave_one_formulation_pooled.csv` test one-point reconstruction when an entire nominal formulation is absent from thermal-shape fitting.
2. `local_joint_formulation_temperature_extrapolation.csv` and `local_joint_formulation_temperature_extrapolation_summary.csv` apply a stricter joint holdout: the target formulation is absent from shape fitting, the shared shape is trained only through 110 C, one 110 C state anchor is supplied, and 120/130 C are predicted.

The second test gives a pooled multiplicative RMSE of approximately **1.088x** across 12 held predictions. It is reported only as **10-20 C short-range local extrapolation within the chemistry-audited E1-E3 neighborhood**.

Recompute the provenance-aware audit with:

```bash
python scripts/analysis_audit_v1.py --output-dir analysis/results
```

The V5 manuscript figures are built by the Python scripts under `analysis/figures_composite/` (see its README): one `make_figN.py` per figure, each writing SVG, PDF and PNG, plus `make_sheet.py` for a combined sheet. The R route below produced the earlier Figure 3 and is kept for the V3/V4 manuscripts, which still reference `analysis/figures/`.

Render the earlier Figure 3 with R:

```bash
Rscript scripts/figure3_local_transfer.R
```

The R script writes `analysis/figures/Figure3_local_transfer.pdf` and `analysis/figures/Figure3_local_transfer.svg`.
