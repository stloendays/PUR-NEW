# Scientific claim-to-evidence map — reactive PUR manuscript

**Updated 2026-10-14.** This file is a repository-level submission
index, not text intended for the journal. Follow the source hierarchy:
raw measurements and originally frozen records -> verified analysis
scripts and outputs -> canonical manuscript and SI -> exported figures
and Word files. The canonical paper is in `manuscript/MAIN_TEXT_V5.md`
with `manuscript/SUPPLEMENTARY_INFORMATION_V5.md`.

## One-sentence scientific story

In reactive PUR hot melts, the realized viscosity level and local
viscosity–temperature response are separable from formulation-sensitive
thermal-hold drift, so chemical transfer boundaries and competing
stabilization hypotheses can determine **which experiment to measure**
rather than merely which formulation to predict.

## Claims, scope and source links

| Scientific claim | Evidence class and primary unit | Auditable value | Manuscript location | Verified source |
|---|---|---|---|---|
| Nominal E2 chemistry permits large viscosity-level differences | Direct source viscometer readings; three labelled realization curves R01–R03 | 2.80–3.57× across 80–130 °C | Results 2.1, Figure 2A | `data/temperature_sweeps.csv`, `data/realization_metadata.csv` |
| Realization intercept on shared quadratic thermal basis explains local variance | Statistical fit, six chemistry-audited complete curves / 36 points; same-order formulation-only comparator | Fitted $R^2$ 0.8553 to 0.9977; held-temperature error 1.423× to 1.058× | Results 2.1, Figure 2D; SI Notes 1–2 | `scripts/statistical_analysis.py`, `analysis/results/analysis_summary.json` |
| Between-realization variation is predominantly a log-viscosity level shift | Model-free SVD over six complete curves | PC1 99.63%, cosine 0.9998 to constant loading | Results 2.1, Fig. 2B–C; SI Note 2 | `analysis/results/local_model_free_state_shift_summary.json` |
| One actual viscosity anchor improves an unseen E2 realization prediction | Realization-level holdout with one 110 °C reading and colder/hotter held targets | 1.824× to 1.086× at 120/130 °C | Results 2.2, Figure 3B; SI Note 3 | `analysis/results/local_model_comparison.csv`; `analysis/results/upgrades_20261003/` |
| Temperature-response transfer is local and chemistry-bounded | Independent original rheometer readings from the 39-curve, 4559-observation Pugar workbook; 34 eligible held curves; two matched training curves per condition | Within-polyol different-isocyanate 1.076× versus across-polyol same-isocyanate 1.238× (68 targets); closer NCO subset 1.057× versus 1.166× (22 curves) | Results 2.4; SI Note 7 | `scripts/external_pur_raw_anchor.py`, `analysis/results/generality_20261014/pur_raw_anchor/summary.json`; original DOI 10.1039/D5DD00287G |
| Apparent flow temperature-sensitivity is not a chemical rate constant | Six chemistry-audited curves, descriptive slopes | $E_\eta$ = 42.05 ± 2.43 kJ mol⁻¹ | Results 2.3; SI Note 5 | `analysis/results/local_thermal_curve_fits.csv` |
| Same composition difference cannot be reduced to a 1–2 °C thermometric mismatch under the simple flow null | **Counterfactual model**, not a measured probe-temperature error; E2 R01 and R03 at six matched temperatures | 2 °C offset predicts 1.065–1.085× vs measured 2.796–3.569×; 24–35 °C model-equivalent offset needed | Repository-level physical robustness support, not independent molecular evidence | `scripts/pur_temperature_error_counterfactual.py`, `analysis/results/local_temperature_error_counterfactual_20261014/` |
| Viscosity evolution during hold is a separate formulation-dependent coordinate | Direct 120 °C measured trajectories E1/E5 | 15–60 min drift 9.51% vs 51.54%; 15–90 min fitted log-drift-rate ratio 4.29× | Results 2.3, Figure 5; SI Note 6 | `data/thermal_hold.csv`, `analysis/results/local_hold_dynamics.csv` |
| A resin-modified recommendation reduces thermal-hold drift relative to proportional-dilution null | Two measured F1 hold repeats plus a declared physical-null model | F1 signed drifts −0.16%, +3.04%; **mean absolute** 1.60%; H-CORE 7.79%, conditional simulation probability 0.010 | Results 2.7, Figure 5; SI Note 6 | `data/thermal_hold.csv`, `analysis/results/upgrades_20261003/hcore_uncertainty/`, `docs/EXPERIMENTAL_CHRONOLOGY.md` |
| Useful experiment selection depends strongly on explicit scientific rules | Frozen computational **decision runs**, not wet-lab replicates | Rule-complete 9/10 evidence-supported family, 0/10 zero discrimination; inverted order 10/10 zero discrimination | Results 2.5–2.6, Figure 4; SI Notes 8–17 | `derived/rges_rule_ablation_summary.json`, `docs/decision_architecture_provenance.md` |
| Withholding VOI changes the formulation selected | **Two sequential** N=5 computational blocks under unchanged settings, second initiated after reviewing first; combined N=10 only descriptive | Initial 0/5 dual-axis + 3/5 zero discrimination; extension 0/5 dual-axis + 0/5 zero discrimination; combined 0/10 and 3/10 | Results 2.6 (aggregate); SI Note 14 (blocks) | `analysis/results/upgrades_20261003/score_withheld_extension/RESULTS.md` |
| Chemistry applicability is relevant to measurement choice | Deterministic gate vs model advice-only; do not pool attempted and valid runs | In processing window, advice-only 10/10 selects full sweep; enforced 9/9 **valid** commitments select full sweep (1 invalid) | Results 2.6; SI Notes 19–21 | `derived/cbes_processing_window_condition_summary.json` |
| Level-shift geometry is observed beyond PUR within a restricted polymer-electrolyte comparison | **External conductivity** raw readings, distinct physical transport property; holdout by curve or by study DOI | 1.659× over 979 held readings within 20 °C (14 hosts); DOI holdout 1.705× over 767 readings (5 eligible hosts) | Results 2.9; SI Note 22 | `scripts/spe_raw_anchor_audit.py`, `analysis/results/generality_20261014/raw_anchor/summary.json`; source DOI 10.1021/acscentsci.2c01123 |
| Acrylic-only hold can adjudicate remaining resin-versus-dual-modifier question | **Registered but unmeasured follow-up**, not evidence of outcome | S1C39 ≤4.04% supports H-RESIN; ≥6.08% plus matched S1C41 ≤3.80% supports H-DUAL; other cases unresolved | Results 2.8; SI Note 23 | `experiments/prospective/S1C39_M-HOLD-120_20260920.md`; `experiments/supplementary_20261004/INTERPRETATION_RECONCILIATION_20261014.md` |

## Five-figure narrative and what each figure proves

1. **Figure 1:** physical measurements precede registration of an
   informative experiment; deterministic rules and language-model stages
   must remain separately attributable.
2. **Figure 2:** E2 realization spread, concentration of curve-shift
   variance, and the same-basis formulation vs realization comparison.
   The displayed fourth E2 trajectory is a next-day retest, not a
   fourth independent synthesis batch.
3. **Figure 3:** one true in-domain viscosity measurement corrects the
   realized state and improves separate-temperature predictions.
4. **Figure 4:** experiment selection is constrained by measured
   chemistry-domain validity and explicit rule content/order.
5. **Figure 5:** the physically observed isothermal drift is a
   distinct response axis; F1 rejects the specified reactive-core-only
   dilution null while H-DUAL and H-RESIN remain unresolved.

External PUR raw-point matching and SPE study-held-out predictions
support the main generality arguments but do not constitute additional
local synthesis repeats.

## Experimental chronology and model claims

The research team **confirms** that the resin-modified F1 composition
was recommended before its wet-lab hold outcome was known. This was
recorded retrospectively; the repository does **not yet contain** an
independently timestamped contemporaneous original freeze artifact.
The formal RGES/CBES runs are documented, outcome-blind **replays** of
the pre-result decision problem and have their own frozen records.
Never imply they were the exact historic runtime of the original F1
selection or that subsequently computed physical analyses were
historical inputs to it. Detailed boundary:
`docs/EXPERIMENTAL_CHRONOLOGY.md`.

## Submission check and open author-level decisions

- **Machine verifiable:** local measurements, Pugar original workbook
  revision and SHA, simulation vs observation class, DOI-derived SPE
  source provenance, SI tables/figures, all five main figure files,
  bibliography citation keys, and Word equation/image embedding.
- **Requires author confirmation:** author order, legal English company
  name, affiliations/correspondence, conflicts/funding statements,
  and whether any old contemporaneous F1 recommendation artifact can
  be recovered. Do not infer these from AI output.
- **Requires full visual QA before journal upload:** examine *all*
  rendered pages of the exact exported manuscript and SI, especially
  SI tables, inline equation typography, figure/caption proximity and
  bibliography pagination.
- **Unmeasured:** S1C39/S1C41 contrast, F1 direct sweeps and newly
  planned independently synthesized repeats. Their simulated power
  and target values must never be represented as experimental outcomes.
