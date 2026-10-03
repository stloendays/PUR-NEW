# External test of state-shift geometry and one-point anchor transfer

Script: `scripts/external_state_shift_validation.py` (run with the default `--db`).
Data: public dense prepolymer curves of Pugar et al. 2025 (39 curves, 4559 rows; local SQLite opened read-only, sha256 `2eaf52a6…c27a95`, full hash in `summary.json`).

## What was tested

The local claims (sections 2.2, 2.3 and 3.3–3.5) were re-run on external curves that played no part in building them, using the same conventions: z(T) = 1e3·(1/T − 1/Tref), multiplicative RMSE = exp(RMSE of ln η), and a 10,000-resample curve-level cluster bootstrap (seed 20261003).

- **Grid.** Every curve was put on a 2.5 °C grid from 42.5 to 77.5 °C (15 nodes). Tref is 60 °C. Grid values come from a tricube-weighted local quadratic in z (±2.5 °C). Isolated spikes were removed first with a Hampel filter, which removed 44 of 4559 points; curve ends were never filtered.
  - Every node lies inside every full-range curve's measured range (40.2–80.0 °C), so nothing is extrapolated.
  - A node is dropped when it falls in a data gap, meaning fewer than 3 points within ±1.25 °C.
  - Three curves lose nodes this way. P_TDS_10 loses 42.5/50/52.5/55/65 °C, D_W_9 loses 45/47.5/50/60/72.5 °C and D_I_9 loses 47.5/50/60/72.5 °C.
  - The smoother's residual is negligible: median per-curve RMS 0.0028 in ln η (0.28%), maximum 0.0097.
- **Curve sets.**
  - The primary set follows the manuscript §3.8 rule (R² ≥ 0.98), which excludes D_44M_6 and D_TD80_7 and leaves 37 curves.
  - The sensitivity sets are all 39 curves, and a regime-screened set (36 curves). The screened set also drops C_MLQ_4, whose own quadratic misfits by more than 1.05×. That curve shows a low-T upturn and a −45% drop between 60 and 64 °C.
- **Shape sources for the anchor test.** For each held curve, the shared quadratic g(T) was fitted (curve intercepts plus shared β1, β2) on one of four source sets:
  - (a) other curves in the same polyol × isocyanate family;
  - (b) the same polyol family with a different isocyanate;
  - (c) the same isocyanate with a different polyol family, i.e. a polyol-family holdout;
  - (d) all other curves.

  A single anchor value then placed the held curve on that shape. The "common" subset is the set of curves for which all four sources exist.

## Headline numbers (primary set, 37 curves)

| Test | Within one polyol family | Across polyol families |
|---|---|---|
| Spread not explained by a pure level shift (exp RMS of row-mean-removed, centred ln η matrix) | P 1.028×, D 1.055×, C 1.081×; polyol × iso families 1.012–1.098× | same isocyanate across polyols 1.064–1.141×; all pooled 1.133× |
| SVD mode 1 variance / cosine to constant | 0.9990–0.9998 / 0.997–0.9996 | 0.979–0.9985 / 0.981–0.9997; pooled 0.9965 / 0.9966 |
| R², family-level-only → curve-level + shared quadratic | P 0.249 → 0.999; D 0.384 → 0.998; C 0.383 → 0.996 | pooled 0.189 → 0.992 |
| One-point anchor at 60 °C, pooled ×RMSE [95% CI], common n = 31 | (a) 1.078 [1.047–1.112]; (b) 1.069 [1.038–1.104] | (c) 1.221 [1.186–1.257]; (d) 1.151 [1.122–1.189] |
| Same, over all 15 anchor temperatures | (a) 1.075–1.141; (b) 1.063–1.114 | (c) 1.221–1.488; (d) 1.151–1.309 |
| Strict: shape ≤57.5 °C, anchor 57.5 °C, predict 67.5/77.5 °C (n = 33 curves, 66 predictions) | (a) 1.128 [1.072–1.190]; (b) 1.115 [1.060–1.177]; median APE 4.4% / 3.2% | (c) 1.285 [1.229–1.356], median APE 18.7%; (d) 1.210 [1.147–1.289] |
| Strict, regime-screened set (32 curves) | (a) 1.070 [1.051–1.090]; (b) 1.061 [1.045–1.075] | (c) 1.258 [1.224–1.293]; (d) 1.167 [1.140–1.192] |
| Anchor at 60 °C, regime-screened set (30 curves) | (a) 1.054 [1.039–1.069]; (b) 1.044 [1.033–1.054] | (c) 1.206 [1.178–1.232]; (d) 1.133 [1.117–1.148] |

Paired contrasts (common subset, anchor 60 °C, ratio of log-RMSE):
- c/b = 2.99 [2.18–5.13]
- c/a = 2.67 [2.02–4.25]
- d/b = 2.11 [1.70–3.30]
- b/a = 0.89 [0.69–1.00]

A same-polyol shape from other isocyanates is at least as good as a same-family shape, probably because it is fitted on more curves.

The apparent E_η range across the 39 curves is 34.74–94.15 kJ mol⁻¹, with 37/39 curves at R² ≥ 0.98. This matches the manuscript's 34.7–94.2 kJ mol⁻¹. The range splits cleanly by polyol: P 34.7–44.6, C 56.8–76.8 and D 50.6–94.2 kJ mol⁻¹.

## How this maps onto the manuscript

- **§2.2 (state-shift geometry).** The geometry is reproduced externally within each chemistry family. Once each curve gets its own level, a shared quadratic explains 99.6–99.9% of ln η inside a polyol family, and only 25–38% with a single family level.
  - The SVD mode-1 fraction is above 0.99 everywhere, because the level spread is up to 230×. On its own it does not separate within-family from cross-family sets.
  - The discriminating quantity is the residual non-shift spread. It is 1.01–1.08× inside a family and rises to 1.06–1.14× across polyol families.
  - Within-family curves here differ in NCO content and isocyanate rather than being replicate realizations. Composition changes inside a polyol family therefore also act mainly as level shifts.
- **§2.3 (one-point anchor).** The anchor is reproduced when the shape comes from the same polyol family: 1.04–1.08× at 60 °C, which overlaps the local 1.06–1.10×. The strict +10/+20 °C analogue gives 1.06–1.13×, against 1.088× locally. Within this range, the family-pooled shape extrapolates better than a curve's own quadratic (1.18×).
- **§2.5 and the CBES applicability rule.** This is a direct anchor-level confirmation of the polyol-family boundary. Taking the shape from another polyol family roughly triples the log-error (1.22× at 60 °C, 1.29× in the strict test, median APE 19%), even when the isocyanate is the same. Changing the isocyanate within a polyol family costs nothing measurable. The admissibility condition "shared shape established within the polyol family" is therefore the operative one.

## Proposed manuscript / SI text

On 39 independent dense prepolymer curves (Pugar et al.), a curve-specific level on a shared quadratic thermal response explained 99.6–99.9% of log-viscosity variation within each polyol family, compared with 25–38% for a single family level. A one-point anchor reconstructed held curves with a pooled multiplicative error of 1.04–1.08× when the thermal shape came from the same polyol family, and 1.06–1.13× in a strict +10/+20 °C extrapolation test. When the shape was transferred from a different polyol family, error rose to 1.21–1.29× (median absolute error 19%) even with the isocyanate held fixed, whereas changing the isocyanate within a polyol family had no detectable cost. The one-point shortcut is therefore admissible inside a polyol family whose shared thermal shape has been established, and not across a polyol-family change.

## Files

- `curve_inventory_and_smoothing.csv`: per-curve range, E_η, R², spikes removed, smoother residual, grid nodes and set membership.
- `grid_ln_eta_smoothed.csv`: the compact 15-node grid. This is derived data, not the raw table.
- `family_svd_and_shape_models.csv`: per-family SVD, non-shift spread, R² of the three nested models and the nested F test. The F test is diagnostic only, because smoothed grid values are autocorrelated.
- `anchor_per_curve.csv`, `anchor_pooled_by_source_and_anchor.csv`, `anchor_paired_source_contrasts.csv`: the anchor-transfer results.
- `strict_extrapolation_per_prediction.csv`, `strict_extrapolation_pooled.csv`: the strict test at splits 47.5–57.5 °C. The primary split is 57.5 °C.
- `summary.json`: headline numbers, seeds, DB hash, row counts and curve inclusion lists.
- `external_state_shift_diagnostic.png`:
  - A: raw curves for polyol family P.
  - B: the same curves with their curve levels removed.
  - C: anchor error by shape source, with bootstrap 95% CIs.
