# Solid polymer electrolyte ionic conductivity (Bradford et al. 2023)

- Citation: Bradford, G.; Lopez, J.; Ruza, J.; Stolberg, M. A.; Osterude, R.; Johnson, J. A.;
  Gomez-Bombarelli, R.; Shao-Horn, Y. Chemistry-Informed Machine Learning for Polymer Electrolyte
  Discovery. *ACS Central Science* **2023**, 9 (2), 206-216. doi:10.1021/acscentsci.2c01123
- Source repository: https://github.com/learningmatter-mit/Chem-prop-pred, commit
  `39b0c16f70c4142b32a67531a093718c767ad43d`, file `data/PolymerElectrolyteData.csv`
  (SHA-256 `5ad82b4b75b9bb95f8f402fd394686d69c97cd0edaa110ad9c330655268a9fab`).
- Licence: MIT (`LICENSE`, copied unchanged from the source repository).

`spe_neat_curves.csv` is a derived subset written by
`python scripts/external_spe_state_shift.py --raw <PolymerElectrolyteData.csv>`: neat polymer + one
salt (no second component, no inorganic filler), temperatures rounded to 0.5 C with duplicate
measurements averaged, curves with >= 5 temperatures spanning >= 30 C. 710 curves, 141 polymer
backbones. Columns: `curve_id`, `temperature_c`, `log10_sigma` (S/cm), `family` (polymer SMILES),
`salt` (SMILES), `molality` (mol salt per kg polymer), `doi`.
SHA-256 `1a16b66987a479066baf74ccc0e00c7462e320a6dcadd8d20fd333c03c27f823`.
