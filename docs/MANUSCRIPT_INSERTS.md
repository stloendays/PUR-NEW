# Manuscript-ready strengthened inserts

These sections are written to strengthen the non-Agent scientific contribution and the rigor of the Agent benchmark. Experimental follow-up conclusions can be inserted separately once the ongoing wet-lab analysis is finalized.

## Insert A — Results: process-state sensitivity separates viscosity level from temperature-response shape

### Realization-dependent viscosity level with conserved temperature-response shape

All recorded complete temperature sweeps showed a monotonic decrease in viscosity between 80 and 130 °C, but the absolute viscosity level was highly sensitive to experimental realization. This effect was most clearly resolved for the nominal E2 formulation, for which three non-retest runs were available over the same temperature interval. At 80 °C, the recorded viscosities ranged from 9462 to 27350, corresponding to a 2.89-fold max/min spread, while at 120 °C the range increased from 1955 to 6977, corresponding to a 3.57-fold spread. The sample coefficient of variation across the three E2 runs was 48.3% at 80 °C and 58.5% at 120 °C. These differences are substantially larger than would be expected from treating formulation identity as the sole state variable.

Despite this large variation in absolute level, the temperature-response shape was comparatively conserved. Each complete 80–130 °C realization was fitted descriptively using an Andrade/Arrhenius-like relation, ln(η) = a + b/T. The resulting apparent flow parameter, bR, averaged 41.87 kJ mol−1 with a sample standard deviation of 2.27 kJ mol−1 across seven complete realizations, corresponding to a coefficient of variation of approximately 5.4%. Individual fits remained strong (R² = 0.965–0.998). The apparent flow parameter is used here only as a compact descriptor of temperature sensitivity and is not interpreted as a molecular reaction activation energy.

The contrast between large vertical shifts in viscosity and comparatively stable temperature-response parameters indicates that the observed rheology contains at least two separable components: a temperature-dependent response shape that is relatively conserved over the measured window, and a realization-dependent viscosity level that is strongly affected by preparation or process history. Because the source labels associated with the different runs do not uniquely identify operator, batch, instrument, reaction time, or another causal factor, the present data do not assign the level shift to a specific physical mechanism. Instead, the run identity is treated as a latent proxy for an incompletely observed process state.

A leave-one-temperature-out diagnostic further illustrates the practical importance of this distinction. Across all complete realizations, an explanatory formulation-only temperature model gave a mean absolute percentage error of 26.4%, whereas conditioning on the observed realization reduced the error to 7.8%. Restricting the comparison to the three nominal E2 runs increased the contrast to 44.9% versus 11.0%, respectively. This diagnostic is not intended as a deployable predictor for unseen future batches because the realization label is known only after a run exists. Rather, it quantifies how much explanatory information is lost when process realization is collapsed into formulation identity alone. These observations motivate representing a PUR test point as a formulation–process state rather than as composition alone.

### Recommended interpretation sentence

> The principal rheological consequence of uncontrolled realization history in the present dataset is a large shift in viscosity magnitude superimposed on a comparatively conserved temperature-response shape, supporting explicit representation of process state in formulation design.

## Insert B — Methods/Results: benchmark rigor and discretization sensitivity

### Guarding against candidate-grid and literature-prior shortcuts

The blind Agent benchmark was designed to withhold the follow-up wet-lab outcome and all post-result adjudication labels from the evaluated model. However, because external analogue evidence independently places several acrylic-resin-modified PUR formulations near a 19–20% modifier fraction, recovery of the experimentally relevant region cannot by itself establish a unique contribution from language-model reasoning. The benchmark therefore includes deterministic baselines using the same permitted evidence, including a nearest-external-prior rule and a transparent support ranker, in addition to uniform random selection.

Candidate discretization is treated as a separate sensitivity factor. The default candidate set contains modifier fractions of 0, 5, 10, 15, 18, 20, and 25%, while the experimentally used formulation normalizes to approximately 18.12% combined AC1920 and TK100. To avoid over-interpreting recovery of one numerically convenient grid point, supported-region recovery is treated as the primary metric and exact 18% recovery as a secondary, discretization-sensitive metric. The benchmark is additionally repeated on a coarser grid that omits 18% entirely (0, 5, 10, 15, 20, and 25%) and on a shifted grid (2.5, 7.5, 12.5, 17.5, and 22.5%). A robust recommendation should remain concentrated in the same formulation region rather than depending on the presence of one exact candidate value.

Accordingly, the Agent contribution is not defined merely as selecting a resin-modified composition. If a deterministic literature-prior baseline already reaches the supported region, the additional value of the Agent must be demonstrated through evidence integration, uncertainty decomposition, ranking robustness, appropriate abstention, or selection of an informative next experiment. This comparison prevents the benchmark from conflating literature retrieval with scientific decision-making.

## Figure revision suggested by these inserts

### Revised Figure 2

Use four panels if space permits:

- **2A:** all measured 80–130 °C viscosity curves;
- **2B:** E2 max/min range and CV as a function of temperature;
- **2C:** apparent flow parameter for each realization with mean ± SD;
- **2D:** explanatory leave-one-temperature-out error for formulation-only versus realization-aware fits.

If Figure 2D makes the main figure too dense, move it to Supplementary Figure S2 and retain 2A–2C in the main text.

### Revised Agent benchmark figure/table

Report, for each benchmark condition:

- supported-region Top-1 recovery;
- supported-region Top-3 recall;
- abstention rate;
- deterministic prior baseline;
- transparent support-ranker baseline;
- result on the grid without the exact 18% candidate;
- result on the shifted grid;
- scientific-boundary violation rate.

Do not use exact-grid Top-1 as the headline metric.

## Claim boundary

The strengthened temperature analysis supports a statement about **state sensitivity and response-shape conservation**, but it does not identify the physical cause of the realization shift. The benchmark controls support a statement about **decision robustness beyond candidate discretization**, but only after the corresponding repeated Agent runs have actually been executed and reported.
