# Branch audit and realization-code anonymization, 2026-09-23

Scope: the state of `origin` at the point `af47a03` was pushed to
`agent-v5-implementation`, what the anonymization pass changed, and what is left
to decide. Every hash and count below was read from the repository, not carried
over from an earlier note.

## 1. Push

`af47a03` (*Freeze the Condition B chemistry-gate series*) was already the tip of
`origin/agent-v5-implementation`; the push was a no-op. The branch then received
the anonymization work and the unified manuscript merge described below.

## 2. Frozen Agent V5 material is unchanged

`results/`, `prompts/` and `derived/evidence_state.json` are byte-identical to
`af47a03` after every change in this pass.

| Condition | Arm | declared | attempted | completed | committed | failed |
|---|---|---:|---:|---:|---:|---:|
| A | V5_NO_GATE | 10 | 10 | 10 | 10 | 0 |
| A | V5_FULL | 10 | 10 | 10 | 10 | 0 |
| B | V5_NO_GATE | 10 | 10 | 10 | 10 | 0 |
| B | V5_FULL | 10 | 10 | 9 | 9 | 1 |

The Condition-B `V5_FULL` split — denominator 9 over committed, 10 over declared —
is preserved as reported. No run was added, replaced or re-scored.

## 3. Anonymization

`GJJ -> R01`, `ZYX -> R02`, `CHH -> R03` across 45 active artifacts: `data/`,
`derived/` (except the file in 3.2), `analysis/`, `docs/`, `manuscript/`,
`scripts/`, `src/` and the READMEs.

The change is a pure relabeling. Each file is byte-identical to its previous
revision once the substitution is reversed, so no measurement, fit, interval or
denominator moved. 71 tests pass; `check_manuscript_citations.py` reports OK.

The three R-rendered SVGs additionally needed their `textLength` recomputed:
with `lengthAdjust=spacingAndGlyphs`, the relabeled legend entries were still
being squeezed into the pre-anonymization glyph widths — `R01` into 11.27 px and
`R03` into 15.84 px, for strings of equal width. Values were recomputed from each
element's own font-family and size; the metric tables reproduce every untouched
label in those files to within 0.04 px.

### 3.1 Frozen run records are not rewritten

105 files under `results/` still carry the original labels. They are frozen
benchmark records, and `AGENTS.md` forbids editing them to propagate a fact.

**This is the open decision.** The repository is public, and the labels are
personal initials. Leaving them means the anonymization is cosmetic at the
repository level. Rewriting them means editing frozen records, which is the
thing the freeze exists to prevent. A third option is to keep the records intact
and make the repository private, or rewrite history, before submission. Not
resolved here.

### 3.2 derived/evidence_state.json is deliberately untouched

Its current sha256 is

```
8ca085b1529f94b2fc6ed3bfdd0f5fb938a4580159ed04ece39fac42c023bc81
```

which is the live `evidence_state_sha256` pin in **28** frozen manifests,
including every Agent V5 Condition A and Condition B series manifest and all four
`STAGE1_BLIND_REPLAY_*/STRATEGY_FROZEN.json` files. Relabeling it would
invalidate all of them at once. It is the only file outside `results/` that still
contains the original labels.

For contrast, the other pinned file that contains labels,
`src/pur_new/scientific_tools.py`, was already off its Stage-1 pin long before
this pass (pinned `24ba8d0e...`, actual at the freeze commit `62b69506...`), so
anonymizing it broke nothing that was still verifiable.

## 4. Unified manuscript merge

`origin/main` merged into `agent-v5-implementation`, so the manuscript exists in
one place. Two git conflicts:

- `AGENTS.md` — took main, a superset. Its Agent implementation rule still named
  tool version `3.5-verified-phosphoric-perturbation` while the merged tool is
  `3.6-state-anchor-bridge`; corrected.
- `analysis/figures/Figure2_state_conditioned_rheology.svg` — took this branch,
  same labels as main plus the corrected widths.

Three things the merge surfaced that git could not resolve:

- `configs/action_catalog.json` is a V4-defining input. Main's two edits to it
  arrived undeclared and failed
  `test_v4_inputs_and_frozen_results_are_unchanged_by_v5`. Declared as an
  amendment in `configs/v4_invariance_baseline.json`, baseline hash preserved.
  The change is inert for the deterministic layers — no VOI, gating,
  admissibility or scoring code reads `description`, `when_to_use` or
  `catalog_version` — but it is **not** inert for future runs: the text is
  model-visible, was written after both series were frozen, and makes any series
  launched under catalog_version 1.5.2 a new evidence version.
- `MAIN_TEXT_V5` section 3.12 said nominal F-test p values are "recorded in the
  repository". That stopped being true when main's Results began quoting them in
  2.1 and 2.4. Reworded to point at where they are reported; the
  not-primary-evidence stance is unchanged.
- `SUPPLEMENTARY_INFORMATION_V5` carried two LaTeX defects into the merged text:
  a missing backslash on `\qquad` in the shared-slope F test, and four display
  blocks in the new robustness notes opened and closed with a single `$` instead
  of `$$`. Both fixed. `audit_manuscript.py`, the checker main added the same day,
  now reports 0 blockers and 0 warnings on both `MAIN_TEXT_V5.md` and
  `SUPPLEMENTARY_INFORMATION_V5.md`.

The state-anchor evidence stays out of the old series. It lives in
`docs/STATE_ANCHOR_TO_AGENT_BRIDGE.md`, `derived/state_anchor_bridge/` and
Supplementary Note 3, and is cited in Results 2.3 as a property of the physical
data. Nothing in the merged manuscript claims it was visible to any frozen run.

## 5. Branch inventory

Ahead/behind are against `origin/main` at `3667e6e`. Leak counts are files still
containing the original labels, split by whether they are active artifacts or
frozen run records.

| Branch | ahead | behind | leak (active) | leak (results/) | last commit |
|---|---:|---:|---:|---:|---|
| `main` | 0 | 0 | 18 | 64 | 2026-09-23 |
| `agent-v5-implementation` | 14 | 42 | 1 | 105 | 2026-09-23 |
| `agent-v4-voi` | 0 | 187 | 26 | 49 | 2026-09-20 |
| `agent-v5-chemistry-gate-protocol` | 0 | 72 | 32 | 64 | 2026-09-22 |
| `agent-v5-protocol-v1-1-and-jev` | 0 | 43 | 34 | 64 | 2026-09-22 |
| `chemistry-first-ml-v1` | 0 | 83 | 32 | 64 | 2026-09-21 |
| `v5-chemistry-integrated` | 0 | 77 | 32 | 64 | 2026-09-22 |
| `manuscript-v3-audited-20260919` | 0 | 202 | 26 | 38 | 2026-09-19 |
| `stage1-outcome-blind-benchmark` | 0 | 270 | 19 | 38 | 2026-09-18 |
| `fix/purnew-rec-r1-workbook` | 0 | 331 | 16 | 0 | 2026-09-18 |
| `stage1-preexperimental-v2` | 28 | 276 | 16 | 0 | 2026-09-18 |
| `analysis/local-extrapolation-figure3` | 12 | 278 | 16 | 0 | 2026-09-18 |
| `manuscript-natcom-style-v3` | 2 | 258 | 21 | 38 | 2026-09-18 |
| `fix/figure3-panel-titles` | 1 | 277 | 16 | 0 | 2026-09-18 |
| `records/purnew-rec-r1-corrected` | 1 | 340 | 13 | 0 | 2026-09-18 |

The `agent-v5-implementation` row is the pushed remote tip before the merge
commit; after the merge it is ahead 15 and behind 0.

Eight branches are fully contained in `main` and hold nothing that is not already
in its history: `agent-v4-voi`, `agent-v5-chemistry-gate-protocol`,
`agent-v5-protocol-v1-1-and-jev`, `chemistry-first-ml-v1`,
`v5-chemistry-integrated`, `manuscript-v3-audited-20260919`,
`stage1-outcome-blind-benchmark`, `fix/purnew-rec-r1-workbook`. Deleting them
removes 8 of the 15 label-bearing refs at zero cost to provenance — except that
`manuscript-v3-audited-20260919` is cited by name in the Data and Code
Availability statement of `MAIN_TEXT_V5.md` and must be kept, or the statement
changed. Branch deletion is not done here.

Five branches still hold unique commits and need a decision before they can be
closed: `stage1-preexperimental-v2` (28), `analysis/local-extrapolation-figure3`
(12), `manuscript-natcom-style-v3` (2, the concise Nature Communications rewrite
of the V3 main text), `fix/figure3-panel-titles` (1),
`records/purnew-rec-r1-corrected` (1).
