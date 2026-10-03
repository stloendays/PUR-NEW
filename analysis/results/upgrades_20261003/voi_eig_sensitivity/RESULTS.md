# Bayesian EIG versus deterministic VOI, and global VOI weight sensitivity

Script: `scripts/voi_eig_and_global_sensitivity.py` (run with `PYTHONPATH=src`, interpreter `D:\Tools\pur_bridge_env\Scripts\python.exe`, runtime about 45 s). Seeds, sample sizes and the SHA-256 of every input are recorded in `summary.json`.

## Headline results

| Quantity | Result |
|---|---|
| Reproduced VOI table | 292 cards (73 × 4). Scores and components are identical to all 10 frozen `series_n10` `voi_full_ranking.json` files |
| Tied VOI top set | S1C41/46/51/56/61 :: M-HOLD-120, VOI = 0.6925 (15–25 wt% acrylic-like at 5 wt% tackifier-like) |
| One-at-a-time 0.5–1.5× sweep (repository tool) | Top set, family and measurement stable in 25/25 scenarios |
| Cards with EIG > 0 | 64/292, all of them M-HOLD-120 on modifier-containing candidates (the same 64 cards that have D_hyp > 0) |
| Primary EIG top set (uniform prior, σ = 2.0 %, point predictions) | S1C10 and S1C14 :: M-HOLD-120 (2.5 wt% single modifier), 0.533 bits. Overlap with the VOI top 5: **0/5** in all 40 EIG settings |
| EIG rank of the VOI top cards | 30–50 of 292. S1C41 has EIG 0.41 bits, against a maximum of 0.53 bits |
| Spearman / Kendall τ_b, EIG vs VOI | All cards: 0.70 / 0.52. Hold cards only: −0.10 / −0.10 (range over settings −0.13 to 0.20) |
| Spearman / Kendall τ_b, EIG vs D_hyp | All cards: 0.94 / 0.89 (0.99 under non-uniform priors). Hold cards only: 0.57 / 0.48 |
| EIG with the same risk penalties (0.30·EIG/H₀ − 0.10 X − 0.05 P) | Top card S1C11 (5 % tackifier-only) in 30/40 settings and S1C39 (15 % acrylic-only) in 10/40. Overlap with the VOI top 5 is 0/5. Hold-card Spearman vs VOI is 0.56 (range 0.45–0.90) |
| VOI with D_hyp replaced by EIG/H₀ (all other terms kept) | Unique top card **S1C41::M-HOLD-120 in 40/40 settings**. Spearman vs VOI is 0.999 on all cards and 0.97 on hold cards |
| Joint weights, U(0.5,1.5)⁶ (raw and renormalised) | 100 % same five-card top set, 100 % hold, 100 % dual-axis family, 0 % zero-D_hyp top card |
| Dirichlet κ = 100 / 30 / 10 | Same top set in 100 % / 99.998 % / 99.48 % of samples. Dual-axis family 100 % in all three |
| Flat Dirichlet | Same top set 79.25 %. The other 20.75 % is the same five candidates under M-REPEAT. Dual-axis family 100 % |
| Sobol indices, VOI margin (best dual-axis hold minus best other card), multipliers 0.5–1.5× | w_dec: S₁ = 1.00 [0.92, 1.08], S_T = 1.00 [0.98, 1.02]. Every other weight is below 10⁻³ |
| Sobol indices, indicator "top card is a dual-axis hold" | Not defined at 0.5–1.5×, because the indicator equals 1 in all 131,072 evaluations. At 0.1–3× (supplementary) it equals 0 in only 0.018 % of evaluations, so the indices cannot be estimated (bootstrap intervals span about ±1.5) |
| Single-weight break-even (others nominal) | The dual-axis family stays on top for any w_dec > 0. At w_dec = 0 it only ties with the single-axis holds. w_proc must rise ×11 (0.05 → 0.55) before dual-axis M-REPEAT ties the hold. w_ext = 0 widens the tie to 10 dual-axis hold cards. w_hyp, w_unc and w_int never change the top set over 0–20× |

## Outcome-blind construction

The held-out validation formulation F1 (PPG2000/PDP-70/AC1920/TK100/MDI = 39.60/39.60/17/5/20.19) and its measured 15–60 min drift (−0.16 %, +3.04 %) enter no prior, likelihood, noise level, weight or ranking in this analysis.

The inputs are the decision-time objects the VOI tool itself uses:

- the hypothesis registry, including the E1 reference drift of 9.51 % from the original E1/E5 hold data;
- the measurement catalog;
- the formulation priors;
- the outcome-blind 73-node candidate space.

The frozen `series_n10` VOI rankings are read only to verify the reproduction.

An audit hook logs every JSON or CSV file opened during the run. All of them are hashed in `summary.json`. The `evidence_firewall` structural check on the registry, catalog and candidate set returns no violations.

## Task A: EIG model

- **Hypothesis variable.** The variable is {H-CORE, H-RESIN, H-DUAL}. The primary prior is uniform. Sensitivity priors are core-favoured (0.5/0.25/0.25), modifier-favoured (0.2/0.4/0.4) and dual-favoured (0.25/0.25/0.5).
- **Likelihood for M-HOLD-120 cards.** The observed 15–60 min drift is the hypothesis prediction plus N(0, σ²).
  - The **point** encoding (primary) uses `voi.predict_drift` unchanged. H-CORE = 9.51·φ_r. H-RESIN = 0.5·9.51·φ_r whenever a modifier is present. H-DUAL gives the low value only when the tackifier is greater than 0, and the dilution value otherwise. The factor 0.5 is the registry's `suppression_factor_vs_linear_max`.
  - The **interval** encoding replaces each low-drift point with the registry's support criterion: drift uniform on [0, 0.5·9.51·φ_r], convolved with the noise.
- **Noise.** σ is the catalog's declared M-HOLD-120 resolution (`discrimination_threshold_pct` = 2.0 %), read as one standard deviation of the reported matched-window drift. Sensitivity runs use σ ∈ {0.5, 1, 2, 3, 4} %.
- **Non-hold cards.** M-REPEAT, M-ANCHOR and M-SWEEP do not address `thermal_hold_drift` in the catalog, and the registry makes no differential prediction for their observables. Their EIG about the hypothesis variable is therefore exactly 0. This follows from the configs; it was not imposed as a modelling choice.
- **Computation.** EIG is the mutual information I(H; Y), computed by 40,001-point quadrature. A Monte Carlo check (n = 400,000, fixed seed) agrees to within 0.0005 nats.

**What drives the disagreement.** EIG is driven entirely by the separation between the H-CORE and suppressed predictions, which is 0.5·9.51·φ_r. That separation is largest when the modifier load is smallest. Pure EIG therefore picks the lightest single-axis probes (2.5 wt%), whereas VOI picks the cards that cover both supported intervention axes inside the evidence region.

The two measures agree on the first-order question. Only the matched-window hold on a modifier-containing candidate carries any information about the registered hypotheses: Spearman ρ = 0.94–0.99 against D_hyp over all cards. They disagree inside the hold family, because EIG has no decision-relevance (coverage) or evidence-region term.

When EIG replaces D_hyp inside the VOI, all other terms kept, the five-way VOI tie resolves uniquely to S1C41 in every prior, σ and encoding setting. S1C41 is the minimum-burden card that the deterministic tie-break and 9/10 rule-complete runs selected. EIG combined with risk penalties alone, without decision relevance, selects single-axis holds instead. Under the modifier-favoured prior it selects S1C39, the acrylic-only hold chosen in the one departing run.

## Task B: weight sensitivity

The VOI is linear in the weights. The best competitor to the dual-axis hold set is the single-axis hold set (S1C11, S1C39, S1C44 …), which differs only in the coverage factor of R_dec (1.0 against 0.7). The margin is therefore exactly 0.3·w_dec, 0.075 at nominal weights, and the Sobol variance of the margin is carried entirely by w_dec.

The measurement axis is the only one that can move under extreme weights. Dual-axis M-REPEAT overtakes the hold only when w_proc is large relative to w_hyp and w_dec: 20.75 % of flat-Dirichlet samples, or w_proc ×11 alone. Even then the formulation family is unchanged.

Output files:

- `voi_eig_card_table.csv`: 292 cards with VOI components, hypothesis drift predictions and EIG (primary and the uniform-prior σ sweep).
- `eig_sensitivity.csv`: 40 EIG settings.
- `weight_sampling_summary.csv` and `weight_sampling_top_sets.csv`.
- `sobol_indices.csv`.
- `break_even_multipliers.csv`.
- `voi_eig_sensitivity_diagnostic.png`.
- `summary.json`.

## Proposed manuscript / SI text

> Under joint random re-weighting of all six VOI terms (100,000 draws each from independent 0.5–1.5× multipliers and from Dirichlet distributions centred on the nominal weights, κ = 10–100), the same five dual-axis hold cards formed the top set in ≥99.5% of draws, and the dual-axis family remained first in 100% of draws even under a flat Dirichlet. The variance of the dual-axis margin was carried entirely by the decision-relevance weight (Sobol total index 1.00), and the family ranking changed only if that weight was set to zero. As an independent check, a Bayesian expected-information-gain model built from the same registered hypothesis predictions and the declared 2.0% hold resolution assigned non-zero information only to matched-window hold cards on modifier-containing candidates (Spearman ρ = 0.94 with D_hyp over all 292 cards); substituting this expected information gain for D_hyp in the VOI resolved the five-way tie uniquely to the 15 wt% acrylic-like/5 wt% tackifier-like hold card in all 40 prior, noise and likelihood settings.
