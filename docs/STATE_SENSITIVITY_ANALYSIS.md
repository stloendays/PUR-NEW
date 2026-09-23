# State-sensitivity analysis

## Purpose

The temperature-sweep data contain a useful scientific result that should be separated from the Agent contribution: nominally similar PUR realizations can differ strongly in **absolute viscosity level** while retaining a comparatively stable **temperature-response shape**.

This analysis quantifies that distinction and strengthens the paper's formulation-process-state argument without assigning an unverified causal meaning to the run labels.

## 1. Absolute level is highly realization-sensitive

For the three non-retest E2 realizations, the same nominal formulation spans:

| Temperature | min | max | max/min | sample CV |
|---:|---:|---:|---:|---:|
| 80 °C | 9462 | 27350 | 2.89 | 48.3% |
| 90 °C | 5527 | 15560 | 2.82 | 46.4% |
| 100 °C | 3705 | 10360 | 2.80 | 46.4% |
| 110 °C | 2622 | 7895 | 3.01 | 49.0% |
| 120 °C | 1955 | 6977 | 3.57 | 58.5% |
| 130 °C | 1536 | 5128 | 3.34 | 54.1% |

The practical implication is that a formulation-only mapping is insufficient to explain the observed viscosity magnitude in this dataset.

## 2. Temperature-response shape is comparatively conserved

Each complete 80–130 °C realization was fitted descriptively as

```text
ln(eta) = a + b / T
```

where `T` is absolute temperature. For readability, `bR` is reported as an apparent flow parameter in kJ/mol. This is an Andrade/Arrhenius-like rheological descriptor only; it is **not** interpreted as a molecular reaction activation energy.

Across all seven complete recorded realizations:

```text
mean apparent flow parameter = 41.87 kJ/mol
sample SD                    = 2.27 kJ/mol
CV                           = 5.4%
range                        = 37.63–44.55 kJ/mol
per-curve R² range           = 0.965–0.998
```

Thus, the variation in absolute viscosity is much larger than the variation in the fitted temperature-response parameter.

This supports a two-part interpretation:

```text
response shape: comparatively stable over the measured temperature window
response level: strongly dependent on realization / preparation state
```

The data do not identify which physical subcomponent of the run history causes the level shift because R01/R02/R03 are retained only as source labels.

## 3. Explanatory leave-one-temperature-out diagnostic

A leave-one-temperature-out calculation was used to quantify how much of the recorded response is lost when realization identity is collapsed.

Across all recorded complete realizations:

| descriptive model | MAPE | log-RMSE |
|---|---:|---:|
| formulation-only | 26.4% | 0.341 |
| realization-aware | 7.8% | 0.103 |

For the three nominal non-retest E2 realizations only:

| descriptive model | MAPE | log-RMSE |
|---|---:|---:|
| formulation-only | 44.9% | 0.483 |
| realization-aware | 11.0% | 0.136 |

This is an **explanatory diagnostic**, not a deployable predictive benchmark. The realization-aware model is allowed to condition on run identity, which is a latent state proxy available only for an already observed realization. It therefore demonstrates the importance of state information but does not predict an unseen future batch from first principles.

## 4. Paper-facing interpretation

A concise defensible result is:

> Absolute melt-viscosity levels varied strongly across recorded realizations of the same nominal PUR formulation, whereas the fitted 80–130 °C temperature-response parameter remained comparatively conserved. This decoupling indicates that composition alone does not define the observed rheological state and motivates explicit representation of preparation/process realization in the design workflow.

A stronger mechanistic statement should not be made without metadata that identifies the actual origin of R01/R02/R03 differences.

## 5. Recommended placement

Use this analysis between the raw temperature-sweep figure and the thermal-hold section:

```text
Figure 2A  raw temperature-viscosity curves
Figure 2B  E2 absolute spread versus temperature
Figure 2C  apparent flow parameter by realization
Figure 2D  formulation-only vs realization-aware explanatory error
```

If the main paper becomes crowded, keep Figure 2A–C in the main text and move the leave-one-temperature-out diagnostic to the Supplementary Information.

## Reproducibility

The deterministic implementation is `scripts/analyze_state_sensitivity.py`. The script reads only:

- `data/temperature_sweeps.csv`
- `data/thermal_hold.csv`

and writes `derived/state_sensitivity_analysis.json` when executed.
