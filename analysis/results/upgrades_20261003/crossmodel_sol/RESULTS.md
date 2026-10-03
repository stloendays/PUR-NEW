# Cross-model replication: where gpt-5.6-sol and gpt-5.6-luna diverge

Source: `results/multimodel/gpt-5_6-sol/v4_benchmark/run_level_rows.csv` (agent-v5-implementation, commit dc1f861; 10 Sol replicates × 8 conditions, 80 runs). Only the base model changes. Every condition runs from a replay tree whose pinned inputs are byte-identical to the Luna series, and the Luna aggregates regenerate exactly from the frozen records (8/8 conditions pass). Script: `scripts/crossmodel_stage_attribution.py`.

## Headline

1. **The deterministic layer is model-independent.** VOI scores, the tied top set, the chemistry-applicability audit and the pre-enforcement payload hashes are identical across the two models.
2. **Both base models make the same proposal.** In the conditions where the deterministic layer is informative, the Sol Proposer chose the same measurement as the Luna Proposer in every valid run:
   - M-HOLD-120 in 9/9 RGES full runs;
   - M-SWEEP in 19/19 CBES processing-window runs;
   - an in-top-set hold card in 16/16 CBES thermal-hold runs.
3. **The models differ at the Robustness Adjudicator.** Luna's later stages left the proposal unchanged in 48/50 rule-complete and CBES runs. Sol's Robustness stage changed it in 33/44. It made three kinds of change:

| Robustness move (Sol) | Runs | Outcome |
|---|---|---|
| Acrylic-only 120 °C hold, separating H-RESIN from H-DUAL | 3 (RGES full) + 11 (CBES thermal-hold) | Committed, admissible. The CBES thermal-hold endpoint is satisfied (16/16 correct). |
| Replicated preparations (M-REPEAT) before the direct sweep | 8 (CBES processing-window) | Committed, admissible. Not the registered endpoint (M-SWEEP). |
| Contemporaneous E2 reference hold, a card outside the declared inventory | 4 (RGES full) | Rejected at the freeze stage. No inadmissible experiment was committed. |

4. **The changes follow the paper's own physics.**
   - The Sol Skeptic/Robustness rationale for M-REPEAT cites the 2.80–3.57× E2 realization spread of Section 2.1. It argues that a single-preparation sweep cannot resolve a 3.40-percentage-point level difference until preparation-state variability is measured.
   - The acrylic-only hold is the experiment that Section 2.10 and the Conclusions name as the next one needed.
   - Sol therefore spent its departures on two things: realization-state control, and the remaining hypothesis contrast.

## Per-arm table (scientific denominator = attempted − technical failures)

| Condition | Model | n | Correct | Proposer in tied top set | Final ≠ proposer | Invalid |
|---|---|---|---|---|---|---|
| RGES rule-complete | Luna | 10 | 9 | 10 | 1 | 0 |
| | Sol | 9 | 2 | 5 | 7 | 4 |
| RGES score withheld | Luna | 5 | 0 | 1 | 3 | 0 |
| | Sol | 8 | 0 | 0 | 7 | 0 |
| RGES rule-order inverted | Luna | 10 | 0 | 0 | 3 | 0 |
| | Sol | 9 | 0 | 0 | 0 | 0 |
| CBES thermal hold, advice | Luna | 10 | 10 | 10 | 1 | 0 |
| | Sol | 8 | 8 | 8 | 8 | 0 |
| CBES thermal hold, enforced | Luna | 10 | 10 | 10 | 0 | 0 |
| | Sol | 8 | 8 | 8 | 8 | 0 |
| CBES processing window, advice | Luna | 10 | 10 | 0* | 0 | 0 |
| | Sol | 9 | 5 | 0* | 4 | 0 |
| CBES processing window, enforced | Luna | 10 | 9 | 9 | 0 | 1 |
| | Sol | 10 | 4 | 10 | 6 | 0 |

\* In the advice-only processing-window arm the deterministic top card is the chemistry-inadmissible anchor (VOI 0.7392). Proposing the sweep there means rejecting the top set, which is the intended behaviour.

The rule ablations reproduce across models. With the score withheld, evidence-supported dual-axis selection is 0 under both models. With rule order inverted, both models select the reactive-core family with zero discrimination in every valid run.

## Proposed manuscript / SI text

> To test whether the decision results depend on one base model, the full comparison matrix was re-executed with a second model (gpt-5.6-sol; 10 replicates per condition) from replay trees whose inputs are byte-identical to the original series. The deterministic layer — VOI, tied top set and chemistry-applicability audit — was identical, and both rule ablations reproduced: score withholding and rule-order inversion again removed evidence-supported dual-axis selection. At the proposal stage the two models chose the same measurement in every valid run (thermal hold for the drift question, direct sweep for the processing-window question). They diverged at the robustness stage: the second model redirected most proposals either to an acrylic-only hold, the experiment that separates H-RESIN from H-DUAL, or to replicated preparations motivated by the realization spread of Section 2.1. Requests outside the declared experiment inventory were rejected at the freeze stage. The scientific rules therefore fix what is informative and admissible across models, while model-specific deliberation decides which admissible contrast to pursue next.
