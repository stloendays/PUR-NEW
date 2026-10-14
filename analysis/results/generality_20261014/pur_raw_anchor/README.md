# Actual-measurement one-anchor transfer in PUR prepolymers

**14 October 2026 | independently executed external-data reanalysis**

## Scientific question

The PUR manuscript reports a strong chemical-family boundary: viscosity
curves differ predominantly in level within a related prepolymer family,
whereas a change of polyol chemistry can change the thermal response.
An earlier calibration analysis smoothed **the entire held curve** before
obtaining the held curve's "one-point" temperature-grid anchor. That
representation is valid for **descriptive curve geometry** but does not
alone prove that **one independent original rheometer reading** is enough.

This experiment tests the stronger, practical statement and keeps the
comparison focused on PUR, using 39 published prepolymer curves.

## Original external data and public provenance

Pugar, Gang, Millan, Haider and Washburn, *Machine learning of polyurethane
prepolymer viscosity: a comparison of chemical and physicochemical
approaches*, **Digital Discovery** 4, 3652–3661 (2025),
DOI [10.1039/D5DD00287G](https://doi.org/10.1039/D5DD00287G).

Original data:
[joepugar/viscosity-modeling](https://github.com/joepugar/viscosity-modeling),
`ViscTempData.xlsx`, pinned Git revision
`57ede2b22f964a99d6467d627236c37d0a7231d2`.

Verified workbook SHA-256:
`bbec41da4ff3cae1231686e5d219ec217ac53d85e0f5fc561e408e78fdaf7085`.

The workbook contains 39 sample sheets and 4,559 positive-viscosity
source observations, mainly over 40–80 °C. The download and SHA are
checked at each independent analysis run.

**Data redistribution policy:** the original workbook remains at its
authors' public repository. This project commits only a derived
reproducible summary and the analysis script, while GitHub Actions
retains detailed per-prediction logs as an artifact. The associated
paper's Creative Commons licence should not be confused with a
blanket assertion about the separate source repository's data licence.

## Unseen-curve prediction contract

For each held-out formulation:

1. Record **one actually measured viscosity** closest to 60 °C, accepted
   only if its recorded temperature is within ±0.5 °C.
2. Test against four distinct **raw, actually measured** viscosities
   closest to 40, 50, 70 and 80 °C (each requires ±0.5 °C).
   The exact measured, not rounded, temperatures enter the model.
3. Fit a shared quadratic thermal response in centred inverse
   temperature from **other prepolymer formulation curves only**,
   with one free intercept per training curve and equal total weight
   per training curve. Neither the held curve's other readings nor
   a polynomial fitted to the held curve enters shape learning.
4. Construct two explicitly matched training sets, two curves each:
   - **Same polyol, different isocyanate**: retain base-polyol identity,
     change isocyanate.
   - **Different polyol, same isocyanate**: retain isocyanate identity,
     change base-polyol family.
   In each set, select the two other formulations with the closest
   reported NCO percentages to the held formulation, with stable ties
   resolved by source sample ID.
5. Both models predict exactly the same held formulation and temperature
   targets. Errors use `exp(RMSE(ln predicted - ln observed))`;
   repeatability and CIs are evaluated by complete held-formulation
   clusters (not 4,559 pseudo-independent readings).

The one-point calibration equation is

```text
z(T)       = 1000 * (1/T_K - 1/333.15)
ln(eta_hat(T)) = ln(eta_measured(T0))
             + b1*(z(T)-z(T0)) + b2*(z(T)^2-z(T0)^2)
```

**Eligible comparison:** 34 of 39 source curves. Two (D_I_9,
D_W_9) have no measurement within 0.5 °C of 60 °C; three P_TDS
curves do not have two independent other-polyol/same-isocyanate
training curves. These are *predefined availability restrictions*,
not removals based on prediction residual.

## Independent source-workbook results

| Held-out original readings | Same polyol / different isocyanate | Different polyol / same isocyanate |
|---|---:|---:|
| 50 and 70 °C (±10 °C), 68 tests from 34 curves | **1.076×** | **1.238×** |
| 40 and 80 °C (±20 °C), 68 tests from 34 curves | **1.429×** | **1.869×** |
| All four target temperatures, 136 tests from 34 curves | **1.294×** | **1.596×** |
| Fraction within 1.20×, ±10 °C | **95.6%** | **60.3%** |
| Curve-bootstrap 95% CI for ±10 °C | **1.033–1.112×** | **1.195–1.283×** |

At ±10 °C, the paired log-RMSE difference (cross-polyol minus
same-polyol) was **0.140**; 10,000 full-curve bootstrap replicates
(seed 20261014) gave **0.104–0.184** as the 95% interval. This
establishes a predictive gap under the defined, matched selection
policy. It is not a causal estimate of which polyol molecular feature
causes the difference.

The within-group sample-count comparison is matched, but mean
training-to-held NCO differences are not perfectly identical:
**0.54** percentage points in same-polyol training versus **0.72**
percentage points in cross-polyol training. A more closely
pNCO-matched subset (both training pools within 1.0 percentage point
in mean absolute NCO difference) is also provided in `summary.json`
and avoids interpreting the entire observed gap as caused by polyol
identity alone.

## Reporting limits

- These 34 formulations are publicly reported prepolymers with varied
  polyol, isocyanate and NCO content, not **34 independent replication
  syntheses of a single adhesive formulation**.
- Temperature points from a held formulation are never used to train
  shared shape. The 50 and 70 °C target predictions are repeated
  measures of **34 independent curve-level units**.
- The NCO-conditioned two-curve selection controls the number of
  training curves, but changing the chemistry pool may also change
  training-data diversity, molecular weight and pNCO similarity.
- Evidence of level/shape transfer in these 40–80 °C prepolymer
  viscosity curves does **not** establish equal transport physics
  in solid polymer electrolytes or prove that F1 (AC1920/TK100-modified
  reactive PUR) shares the unmodified 80–130 °C response.
- Thermal-hold drift is not measured in Pugar's source curves. Do
  **not** treat these source measurements as thermal-hold labels.

## Reproduce

```bash
python -m pip install numpy pandas openpyxl
python scripts/external_pur_raw_anchor.py --workbook /path/to/ViscTempData.xlsx --check
```

Runner: `.github/workflows/pugar-raw-anchor-validation.yml`. The
workflow downloads the pinned upstream workbook and verifies its
SHA-256, runs the complete source-measurement analysis and uploads:

- `raw_predictions.csv` (target-level raw reading and prediction errors)
- `scope_and_horizon_summary.csv`
- `summary.json`

Canonical summary: `analysis/results/generality_20261014/pur_raw_anchor/summary.json`.
Only the verified CI-derived summary is committed; source data and
source curve measurements remain at the originating repository.
