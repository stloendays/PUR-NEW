# Manuscript archive

This directory preserves reader-facing manuscript snapshots before later editorial compression or restructuring. Files here are provenance records and are not the active submission manuscript.

## 2026-09-26 pre-Agent-trim snapshot

- `MAIN_TEXT_2026-09-26_pre_agent_trim.md`
- `SUPPLEMENTARY_INFORMATION_2026-09-26_pre_agent_trim.md`

These snapshots were copied from the active manuscript state before the main-text Agent/decision sections were compressed to foreground the materials-science argument. The scientific data, figures and frozen decision records were not changed by the archival operation.

## 2026-09-26 post-Results-trim / pre-Methods-trim snapshot

- `MAIN_TEXT_2026-09-26_post_results_trim_pre_methods_trim.md`

This snapshot preserves the state after the Results discussion was compressed but before the decision-architecture Methods were shortened and moved toward the SI.

## 2026-09-26 pre-final-style-polish snapshot

- `MAIN_TEXT_2026-09-26_pre_final_style_polish.md`

This snapshot preserves the active manuscript immediately before the Introduction/Results transitions, Figure 1–5 captions and Conclusion were tightened for final-style readability.

## 2026-10-03 pre-computational-upgrades snapshot

- `MAIN_TEXT_2026-10-03_pre_computational_upgrades.md`
- `SUPPLEMENTARY_INFORMATION_2026-10-03_pre_computational_upgrades.md`

These snapshots preserve the active manuscript and SI immediately before the 2026-10-03 analyses (`analysis/results/upgrades_20261003/`) were incorporated. Those analyses are: cross-model replication, H-CORE uncertainty propagation, external state-shift validation, EIG and global weight sensitivity, the hierarchical state model, and the score-withheld arm at N = 10.

## Figure snapshot reference

The redesigned Figure 1–5 set reviewed with these manuscript snapshots is pinned by Git commit:

`bf771c7094114a953a0c232885eba914cf175925`

This commit contains the SVG/PDF/PNG files and the corresponding figure-generation scripts under `analysis/figures_composite/`. Later figure revisions must not erase the ability to recover this exact set.

## Preservation rule

- Do not overwrite or delete archived manuscript snapshots.
- Continue editing the active files in `manuscript/MAIN_TEXT_V5.md` and `manuscript/SUPPLEMENTARY_INFORMATION_V5.md` unless a later active alias is introduced.
- Historical `MAIN_TEXT_V2.md`, `MAIN_TEXT_V3.md`, `MAIN_TEXT_V4.md` and earlier SI files remain preserved in the manuscript root.
- Earlier rendered figure sets are retained in their existing analysis directories; current reader-facing figures remain under `analysis/figures_composite/`.

## 2026-10-08 pre-compression snapshot

- `MAIN_TEXT_2026-10-08_pre_compression.md`
- `SUPPLEMENTARY_INFORMATION_2026-10-08_pre_compression.md`

These snapshots preserve the active manuscript and SI immediately before the 2026-10-08 compression. That pass merged Results 2.1-2.2 and 2.7-2.8, moved duplicated model equations to Methods, added Section 2.8 (registered follow-up round) and Section 2.9 (level-shift structure in solid polymer electrolytes), named the language models in Methods 3.9, and added Supplementary Notes 22-23 with Tables S15-S17.
