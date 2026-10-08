# Level-shift geometry outside polyurethanes (2026-10-08)

`spe_state_shift/` applies the external Pugar test of `scripts/external_state_shift_validation.py`
to solid polymer electrolytes (Bradford et al. 2023; data and licence in
`data/external/bradford2023_spe/`). Command: `python scripts/external_spe_state_shift.py`
(seed 20261008, 10,000 curve-level bootstrap replicates).

- Families: polymer backbones with >= 8 curves sharing a common temperature window >= 30 C wide;
  14 families, 323 curves. Each curve is smoothed by its own quadratic in z(T) inside the window
  (interpolation only) and read on a 5 C grid.
- `family_svd_and_shape_models.csv`: per family, first-mode share of between-curve variance and its
  cosine to a uniform shift; R2 of family level only, curve level + shared quadratic shape, and
  curve-specific quadratic.
- `anchor_per_prediction.csv`: leave-one-curve-out; the shared shape comes from the family's other
  curves, the held curve's warmest grid value is the anchor, every colder grid value is predicted.
- `summary.json`: pooled values quoted in the manuscript.

| Quantity | Value |
|---|---|
| First-mode share, median (range) | 0.991 (0.760-0.997) |
| Cosine of first mode to a uniform shift, median (range) | 0.989 (0.872-0.9999) |
| R2, curve level + shared shape (range) | 0.926-0.994 |
| R2, family level only (range) | 0.062-0.798 |
| One anchor, predictions <= 20 C below it (n = 1292) | 1.68x (95% CI 1.57-1.81x), 90.0% within 2x |
| Family mean without anchor, same predictions | 12.0x |
