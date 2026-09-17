# Data

This directory contains the compact experimental dataset and provenance metadata used by the current repository narrative.

## Files

- `formulations.csv` — original E1-E5 formulation design plus the follow-up formulation. The `amount_basis` field prevents grams and source-reported parts from being mixed silently.
- `temperature_sweeps.csv` — long-form 80-130 °C source-reported viscosity values.
- `thermal_hold.csv` — long-form 120 °C hold data for E1, E5 and the two follow-up repeats.
- `realization_metadata.csv` — same-operator realization provenance, chemistry-comparability flags, retest caveats and analysis role.
- `external_evidence_hints.csv` — curated source-level external PUR evidence used only as directional prior information.
- `external_evidence_basis_audit.csv` — audit of whether reported modifier percentages are directly commensurate with a total-formulation basis.

## Important metadata rules

1. The absolute viscosity unit is not inferred here. The numeric values are stored as `viscosity_reported` until the original instrument/source metadata are confirmed.
2. GJJ, ZYX and CHH are retained as source run labels, but project metadata confirms that these records were produced by the **same operator**. Statistical analysis therefore treats them as opaque within-operator experimental realizations, not as operator categories.
3. Prime-marked runs in the source sheet are recorded through `retest_after_1d = true`. The compact table does not establish whether each day-1 retest is the same retained sample, a re-prepared aliquot or a new synthesis batch; parent-sample relation therefore remains unknown unless older lab records resolve it.
4. The E1 `+P` temperature sweep is explicitly phosphoric-acid-labelled in the source record. Because the additive identity/amount is not represented in `formulations.csv`, `realization_metadata.csv` flags this curve as `sensitivity_only` for the chemistry-audited primary state-shift analysis.
5. The follow-up formulation stops at 60 min. No 90 min follow-up value should be imputed.
6. No NCO:OH value is inferred for the follow-up formulation because it was not explicitly reported with that row.
7. Differences among realization labels are not assigned to a specific physical cause unless corresponding reaction/preparation metadata are available.
8. External modifier percentages are not assumed to share the same denominator. `external_evidence_basis_audit.csv` identifies which values are suitable as directly commensurate numeric anchors and which are only directional evidence.
