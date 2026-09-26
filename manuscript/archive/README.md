# Manuscript archive

This directory preserves reader-facing manuscript snapshots before later editorial compression or restructuring. Files here are provenance records and are not the active submission manuscript.

## 2026-09-26 pre-Agent-trim snapshot

- `MAIN_TEXT_2026-09-26_pre_agent_trim.md`
- `SUPPLEMENTARY_INFORMATION_2026-09-26_pre_agent_trim.md`

These snapshots were copied from the active manuscript state before the main-text Agent/decision sections were compressed to foreground the materials-science argument. The scientific data, figures and frozen decision records were not changed by the archival operation.

## 2026-09-26 post-Results-trim / pre-Methods-trim snapshot

- `MAIN_TEXT_2026-09-26_post_results_trim_pre_methods_trim.md`

This snapshot preserves the state after the Results discussion was compressed but before the decision-architecture Methods were shortened and moved toward the SI.

## Figure snapshot reference

The redesigned Figure 1–5 set reviewed with these manuscript snapshots is pinned by Git commit:

`bf771c7094114a953a0c232885eba914cf175925`

This commit contains the SVG/PDF/PNG files and the corresponding figure-generation scripts under `analysis/figures_composite/`. Later figure revisions must not erase the ability to recover this exact set.

## Preservation rule

- Do not overwrite or delete archived manuscript snapshots.
- Continue editing the active files in `manuscript/MAIN_TEXT_V5.md` and `manuscript/SUPPLEMENTARY_INFORMATION_V5.md` unless a later active alias is introduced.
- Historical `MAIN_TEXT_V2.md`, `MAIN_TEXT_V3.md`, `MAIN_TEXT_V4.md` and earlier SI files remain preserved in the manuscript root.
- Earlier rendered figure sets are retained in their existing analysis directories; current reader-facing figures remain under `analysis/figures_composite/`.
