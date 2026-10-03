# Score-withheld RGES arm extended to N = 10

Script: `scripts/score_withheld_arm_extension.py`. New series: `results/agent_v4_voi/series_ablation_voi_withheld_extension_n5`, declared as its own N = 5 contract on 2026-10-03.

**How the extension was run.**
- It was executed from the `rges_voi_withheld` replay tree. The 14 series input hashes, `derived/evidence_state.json` and the candidate set are all byte-identical to the original series.
- Same model (gpt-5.6-luna), same `--withhold-voi-scores` arm.
- All 5 runs completed; none failed.
- The public run records carry R01–R03. `private_artifacts_index.json` in the series directory lists the five anonymized files with both hashes.

**Reporting rule.** The extension was decided after the first block had been observed. Both blocks are kept in the repository and reported here separately. As for the rule-order arm, the manuscript reports the combined N = 10.

| Metric | Rule-complete (N=10) | Withheld, runs 1–5 | Withheld, runs 6–10 | **Withheld, combined N=10** |
|---|---|---|---|---|
| Evidence-supported dual-axis family | 9/10 | 0/5 | 0/5 | **0/10** (Wilson 0–0.278) |
| Matched-window 120 °C hold | 10/10 | 5/5 | 5/5 | **10/10** |
| Mean hypothesis discrimination | 0.667 | 0.267 | 0.667 | **0.467** |
| Zero-discrimination selections | 0/10 | 3/5 | 0/5 | **3/10** |
| Intervention family | dual-axis 9, acrylic-only 1 | reactive-core 3, acrylic-only 2 | acrylic-only 5 | **acrylic-only 7, reactive-core 3** |

## Reading

- **The decisive effect is now tighter.** Without the VOI score, no run in ten chose the evidence-supported dual-axis family. The rule-complete arm chose it in 9/10.
- **What replaces it.** With the score withheld, the model keeps the hold measurement and gravitates to single-modifier acrylic-only holds (7/10). These separate H-RESIN from H-DUAL, but they do not test the intervention most likely to deliver a low-drift formulation. Pure Bayesian EIG prefers the same single-modifier probes (see `../voi_eig_sensitivity/`). The decision-relevance term of the VOI is what moves the choice to the dual-axis intervention.
- **Manuscript sentence that changes (Section 2.8).** The old text reads "3/5 reverted to reactive-core-only compositions, mean discrimination 0.667 → 0.267". With N = 10 the numbers become 3/10 reactive-core-only and mean discrimination 0.467. The headline (dual-axis 9/10 → 0/10) is unchanged and its interval is narrower.

## Proposed manuscript text (Section 2.8, first paragraph)

> When the VOI score and ranking were withheld but the model, evidence, hypotheses, measurement catalog and 292-card inventory were kept fixed, all 10 runs still chose the 120 °C hold, but evidence-supported dual-axis selection fell from 9/10 to 0/10 (Wilson 95% interval 0–0.28). Seven selections moved to acrylic-only holds and three to reactive-core-only compositions, and mean hypothesis discrimination fell from 0.667 to 0.467.

Methods (3.10): "a score-withheld arm (N = 10)" replaces "(N = 5)".
