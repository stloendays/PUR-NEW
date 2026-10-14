# A temperature-offset physical null for the local E2 state separation

**14 October 2026.** Source-derived, model-based counterfactual analysis.
**Not** a new measurement and **not** a claimed molecular mechanism.

## Question

Nominal E2 rheological realizations R01 and R03 contain the same
PPG2000 / STEPANPOL PDP-70 / MDI target recipe but show nearly threefold
or greater viscosity separation at the same reported measurement
temperature. Could a *small* temperature calibration difference by
itself account for the recorded separation?

This asks about the **temperature sensitivity of the observed
viscosity contrast**. It is distinct from (and narrower than) explaining
which reaction or sample-history variable caused the state offset.

## Source, model and calculation

- `data/temperature_sweeps.csv`:
  E2 R01 and E2 R03, first-day, no one-day retest, six paired
  80–130 °C observations each.
- `analysis/results/local_thermal_curve_fits.csv` with
  `data/realization_metadata.csv`: six audited E1–E3 temperature
  curves, excluding the deliberate H3PO4 perturbation.
- The measured local temperature-response *descriptor* is
  `E_eta = 42.052 ± 2.426 kJ mol^-1` (sample mean ± SD), **not** the
  chemical reaction activation energy.

Assume a simplified, locally constant Andrade/Arrhenius viscosity
response:

```text
eta(T) = C * exp[E_eta/(R*T)]

q = eta_E2_R03(T) / eta_E2_R01(T) > 1

DeltaT_equiv(T, q) = T - 1/[1/T + (R/E_eta)*ln(q)]
```

Here `T` is Kelvin; `DeltaT_equiv` is how far *colder* a
hypothetical measurement of the R01 response would need to be
to generate the observed R03/R01 ratio **if temperature bias were
the only effect**.

For comparison, the hypothetical viscosity ratio from a *2 °C colder
reading* is
`exp{(E_eta/R)*[1/(T-2)-1/T]}`.

## Computed results

| Nominal temperature (°C) | Measured E2 R03 / R01 | Equivalent colder displacement (°C) | Ratio for a hypothetical 2 °C bias |
|---:|---:|---:|---:|
| 80 | 2.891× | 24.37 | 1.085× |
| 90 | 2.815× | 25.12 | 1.080× |
| 100 | 2.796× | 26.31 | 1.076× |
| 110 | 3.011× | 29.53 | 1.072× |
| 120 | 3.569× | 35.38 | 1.068× |
| 130 | 3.339× | 35.34 | 1.065× |

For this specified simplified flow parameter, an error as small as
1–2 °C is not sufficient *in this null model* to account for the
observed high/low E2 scale contrast. The temperature displacement
required would vary substantially with temperature (about 24–35 °C)
rather than behaving like a single constant offset.

## Proper inference

The calculation challenges **one particular alternative explanation**:
that an ordinary *hypothetical* small temperature mismatch, acting
through the measured local apparent flow slope alone, generates the
whole same-formulation difference.

It does **not** independently verify actual sample or viscometer
temperature, and no 1 °C or 2 °C instrument accuracy specification
has been asserted. Changes in torque, spindle-speed protocol,
calibration, sample homogeneity, storage, synthesis conversion and
residual water could also alter the observed trajectory. These
potential effects are not represented by the temperature-only null.

Consequently this test motivates treating the realized rheological
level as meaningful for calibration and subsequent experimental design,
but cannot identify reaction kinetics, molecular-weight distribution
or a particular chemical origin of that level. It is a **supporting
sensitivity diagnostic**, not an independent mechanism demonstration.

To measure rather than model this alternative, record a calibrated
independent sample-temperature probe during two independently
synthesized same-recipe rheology sweeps, alongside precise
equilibration time, spindle/torque, preparation timing, Karl Fischer
water content and terminal NCO%; do not change existing frozen
protocols merely to accommodate these follow-up variables.

## Reproduce

```bash
python scripts/pur_temperature_error_counterfactual.py --check
```

Outputs:
- `per_temperature.csv` (six temperatures, exact source values,
  implied offsets and flow-parameter SD sensitivity);
- `summary.json` (independently rerun and versioned in this folder).

CI run passed on 14 October 2026:
https://github.com/stloendays/PUR-NEW/actions/runs/38521834731

The calculation is neither fed back into an earlier Agent's decision
contract nor treated as new wet-lab evidence.
