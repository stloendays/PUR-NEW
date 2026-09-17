# Data

This directory contains the compact experimental dataset used by the current repository narrative.

## Files

- `formulations.csv` — original E1-E5 formulation design plus the follow-up formulation. The `amount_basis` field prevents grams and source-reported parts from being mixed silently.
- `temperature_sweeps.csv` — long-form 80-130 °C source-reported viscosity values.
- `thermal_hold.csv` — long-form 120 °C hold data for E1, E5 and the two follow-up repeats.

## Important metadata rules

1. The absolute viscosity unit is not inferred here. The numeric values are stored as `viscosity_reported` until the original instrument/source metadata are confirmed.
2. GJJ, ZYX and CHH are preserved as run labels only; their semantic meaning is not inferred.
3. Prime-marked runs in the source sheet are recorded through `retest_after_1d = true`.
4. The follow-up formulation stops at 60 min. No 90 min follow-up value should be imputed.
5. No NCO:OH value is inferred for the follow-up formulation because it was not explicitly reported with that row.