# Data

This directory contains the compact experimental dataset and provenance metadata used by the current repository narrative.

## Files

- `formulations.csv` — original E1-E5 formulation design plus the follow-up formulation. The `amount_basis` field prevents grams and source-reported parts from being mixed silently.
- `temperature_sweeps.csv` — long-form 80-130 °C source-reported viscosity values.
- `thermal_hold.csv` — long-form 120 °C hold data for E1, E5 and the two follow-up repeats.
- `realization_metadata.csv` — same-operator realization provenance, chemistry-comparability flags, retest caveats and analysis role.
- `experimental_methods_metadata.csv` — verified viscometer, spindle, output unit, temperature-equilibration, thermal-hold and sample-preparation metadata.
- `external_evidence_hints.csv` — curated source-level external PUR evidence used only as directional prior information.
- `external_evidence_basis_audit.csv` — audit of whether reported modifier percentages are directly commensurate with a total-formulation basis.

## Important metadata rules

1. `viscosity_reported` is the instrument-reported viscosity in **mPa·s**, measured with an RV-SSR-H high-temperature rotational viscometer (Shanghai Fangrui Instrument Co., Ltd.), NKY-25 heater and No. 27 spindle. Rotation speed was adjusted to maintain approximately 40–60% torque; each temperature setpoint was equilibrated for 15 min before the displayed value was recorded.
2. R01, R02 and R03 are retained as source run labels, but project metadata confirms that these records were produced by the **same operator**. Statistical analysis therefore treats them as opaque within-operator experimental realizations, not as operator categories.
3. The temperature-sweep repeatability protocol used the same mother sample across temperatures within a sweep, so individual temperature points are not independent resyntheses. Prime-marked runs remain recorded through `retest_after_1d = true`; the available metadata do not establish independent synthesis-batch identities across distinct run labels.
4. The E1 `+P` temperature sweep is a defined chemical perturbation: 0.025 mmol H3PO4 delivered from a 0.1 mol/L standard solution during dehydration. It remains outside the primary same-composition state-shift analysis and is analyzed separately as a perturbation check.
5. The follow-up formulation stops at 60 min. No 90 min follow-up value should be imputed.
6. The resin-modified follow-up formulation has a reconciled NCO:OH equivalent ratio of 1.82; this verified value is used in the current manuscript and project handoff.
7. Differences among realization labels are not assigned to a specific physical cause unless corresponding reaction/preparation metadata are available.
8. External modifier percentages are not assumed to share the same denominator. `external_evidence_basis_audit.csv` identifies which values are suitable as directly commensurate numeric anchors and which are only directional evidence.
