# Computational upgrades, 2026-10-03

Seven local analyses that strengthen the claims of `manuscript/MAIN_TEXT_V5.md`. None of them modifies a frozen input, prompt or earlier result. Each subdirectory has a runnable script under `scripts/`, machine-readable outputs, and a `RESULTS.md` with headline numbers and proposed manuscript/SI text.

| Directory | Script | Manuscript section | One-line result |
|---|---|---|---|
| `crossmodel_sol/` | `crossmodel_stage_attribution.py` | 2.7–2.8, SI | Deterministic layer identical across base models; proposals agree; the second model's robustness stage redirects to the acrylic-only contrast or to replicated preparations |
| `hcore_uncertainty/` | `hcore_adjudication_uncertainty.py` | 2.9, 3.11 | P(H-CORE yields ≤ 1.60%) = 0.010 after propagating hold-drift repeatability |
| `external_state_shift/` | `external_state_shift_validation.py` | 2.2, 2.3, 2.5 | On 39 external curves, one-point anchor 1.04–1.08× within a polyol family, 1.21–1.29× across polyol families |
| `voi_eig_sensitivity/` | `voi_eig_and_global_sensitivity.py` | 2.6 | Top set stable under joint re-weighting; formal EIG in place of D_hyp resolves the tie to the card chosen in 9/10 runs |
| `hierarchical_state_model/` | `hierarchical_state_model.py` | 2.2–2.3 | Posterior predictive intervals and coverage for the one-point anchor; alternative thermal bases |
| `score_withheld_extension/` | `score_withheld_arm_extension.py` | 2.8, 3.10 | Score-withheld arm at N = 10: dual-axis selection 0/10 versus 9/10 rule-complete |

The cross-model run records live in `results/multimodel/gpt-5_6-sol/v4_benchmark/` on `agent-v5-implementation` (commit dc1f861). The score-withheld extension records are in `results/agent_v4_voi/series_ablation_voi_withheld_extension_n5/`. Both carry R01–R03 in their public copies; their `private_artifacts_index.json` files list each anonymized file with its original and public hashes.
