---
name: manuscript-submission-qa
description: Submission-stage QA for scientific manuscripts, supplementary information, DOCX/PDF exports, figures, tables, equations, citations, and repository release artifacts. Use when ChatGPT must audit or export a journal manuscript, camera-ready paper, thesis chapter, SI package, or reviewer-ready Word/PDF; reconcile canonical Markdown/LaTeX with Word; diagnose Pandoc/LibreOffice conversion defects; verify cross-document consistency; or prevent known failures such as duplicate captions, collapsed tables, broken math, stale figures, internal version labels, missing references, placeholders, bad pagination, and uninspected exports.
---

# Manuscript Submission QA

Treat submission as a **release-engineering problem for scientific evidence**. A clean source file is not enough. The final deliverable passes only when the canonical text, figures, tables, references, exported Word/PDF, and rendered pages all agree.

Compose this skill with:
- `junbo-scientific-writing` for scientific-story, claim/evidence, statistics, terminology, and manuscript/SI decisions.
- `docx` for creation/editing and the mandatory DOCX render -> inspect -> iterate loop.

## Core principle

Use this order of trust when artifacts disagree:

1. Verified data and frozen experimental/analysis outputs.
2. Analysis code and regenerated machine-readable results.
3. Canonical manuscript and SI sources.
4. Versioned figure/table assets built from those results.
5. DOCX/PDF exports.
6. Old drafts, branch copies, screenshots, chat text, or office-app edits.

Never let a visually polished export override the canonical evidence. Never declare a manuscript final merely because conversion succeeded.

## Submission workflow

### 1. Freeze the release inputs

Before export, identify the exact canonical set:
- main manuscript source;
- SI source;
- bibliography;
- figure/table assets;
- analysis outputs that supply headline numbers;
- author/affiliation metadata;
- target journal template/style, if any;
- exact repository commit/tag when the project is versioned.

If the Word file and repository disagree, resolve the repository source first and regenerate Word.

Do not mix a new main text with stale figures, an older SI, or a bibliography from another branch.

### 2. Run source-level gates before conversion

Run `scripts/markdown_submission_audit.py` on the canonical sources before generating Word/PDF.

Block release for:
- `TODO`, `FIXME`, `AUTHOR_INPUT_NEEDED`, author notes, future-revision notes, or drafting comments;
- reader-facing development labels such as `V3`, `V4`, `V5`, branch nicknames, run-series codenames, or temporary filenames;
- missing image paths;
- missing or duplicate bibliography keys;
- citations absent from the bibliography;
- single-dollar display-math delimiters on their own lines;
- Markdown images with descriptive alt text immediately followed by a full authored caption when Pandoc will create a duplicate caption;
- stale figure/table numbering;
- literal implementation/provenance language that belongs in repository history rather than the paper.

Warnings that need human review:
- units placed entirely inside math mode;
- literal LaTeX-looking text outside math;
- manuscript/SI title mismatch;
- unusually dense table or figure inventory;
- cross-document headline values that are not obviously synchronized.

### 3. Audit cross-document consistency

Compare main text, SI, README/provenance index, figures, and exported documents.

At minimum verify:
- exact paper title;
- author names/affiliations/corresponding-author metadata;
- Abstract and keywords;
- Results headings;
- headline numerical values and denominators;
- equation definitions and units;
- figure numbers, panel letters, captions, and actual rendered panels;
- table numbers, headers, units, and footnotes;
- SI references from the main text;
- citation keys and bibliography entries;
- Data/Code Availability paths;
- reader-facing semantic names vs internal development names.

If a number exists in both main and SI, compare the underlying result artifact rather than manually reconciling prose.

### 4. Prepare source for Word export

Prefer:

`canonical Markdown/LaTeX -> Pandoc -> DOCX native OMML`

For equation-heavy papers, do not use Google Docs as the authoritative conversion path.

Before Pandoc:
- convert figure assets to a Word-compatible raster format only in the temporary export source when needed; keep vector originals canonical;
- blank Markdown image alt text in the temporary export source if a separate full caption paragraph already exists, otherwise Pandoc may create duplicate captions;
- remove drafting horizontal rules and internal release notes;
- keep variables/equations in math mode but prefer ordinary text for human-readable units such as `kJ mol⁻¹`, `J mol⁻¹ K⁻¹`, and `h⁻¹` when Word math typography would look unnatural;
- use `$$ ... $$` for display math, never a lone `$` delimiter line.

### 5. Normalize DOCX structurally

After Pandoc and before visual review:
- force the intended font family and black text unless the journal template overrides it;
- remove decorative title/heading borders introduced by Word styles;
- preserve native OMML equations;
- verify that figures are embedded rather than linked to temporary paths;
- set deterministic table widths and column proportions;
- use compact numeric columns and wider narrative columns;
- remove unresolved paragraph styles that cause LibreOffice column collapse;
- repeat header rows for multi-page tables when possible;
- keep figures with their full captions;
- keep captions together rather than splitting them across pages;
- unwrap bibliography-wide hyperlinks if the renderer introduces stray glyphs;
- compact bibliography paragraphs only when needed to prevent one-reference orphan pages.

Do not shrink body text merely to reduce page count. Fix layout structure first.

### 6. Run structural DOCX checks

Run `scripts/docx_structural_audit.py` before rendering.

Block release for:
- literal LaTeX commands visible in document XML;
- tracked changes/comments left in a clean submission copy when not intended;
- zero embedded media when figures are expected;
- too few native OMML equations for an equation-heavy source;
- placeholders or internal version labels in visible Word text;
- missing required font/style when explicitly requested.

Structural checks are necessary but not sufficient. They cannot detect visual clipping, awkward page breaks, or table collapse reliably.

### 7. Render every page and inspect visually

This is mandatory.

Use the `docx` skill renderer. Inspect **every page at 100% zoom**, not a sample.

Check for:
- clipped or missing glyphs;
- tables collapsed into narrow columns;
- figures cropped, blurry, or too small;
- image/caption separation;
- duplicate captions;
- captions split across pages;
- equation boxes, empty bases, raw LaTeX, or strange operator spacing;
- units rendered as widely spaced math variables;
- colored or stray hyperlink glyphs;
- excessive blank space before figures/tables;
- headings stranded at page bottoms;
- a single bibliography entry pushed to an otherwise blank final page;
- unexpected font or color changes;
- overflow beyond margins;
- SI tables with unreadably small text;
- figure-panel labels or legends that differ from the caption.

If any page fails, fix the source or deterministic export pipeline, regenerate, and inspect again. Do not hand-patch only the final DOCX if the same failure can recur next export.

### 8. Use a two-layer release gate

A release is ready only when both layers pass:

**Scientific/content gate**
- canonical story and claims frozen;
- numbers match source outputs;
- main/SI/captions synchronized;
- references complete;
- no unsupported mechanism language;
- no reader-facing development history.

**Artifact/render gate**
- source audits pass;
- DOCX structural audit passes;
- tests/CI pass when available;
- Word/PDF conversion succeeds;
- every rendered page has been visually inspected;
- final files are copied from the exact audited run, not an earlier successful run.

## Recurring failure patterns to avoid

Read `references/failure-catalog.md` when diagnosing an export or building a new release pipeline.

The highest-value recurring lessons are:

1. **Conversion success is not visual success.** Pandoc, Word, and LibreOffice can all produce a valid file with broken layout.
2. **Source-level correctness is not export-level correctness.** Inline math, alt text, styles, and hyperlinks can become visible defects only after conversion.
3. **Do not trust office-app defaults.** Font themes, title borders, table widths, hyperlink styles, and figure sizing drift across renderers.
4. **Do not fix one file by hand when the pipeline is wrong.** Encode the repair in preprocessing, postprocessing, or CI.
5. **Do not inspect only headline pages.** SI often contains the hardest tables, long equations, and stale development residue.
6. **Do not let internal project history leak into reader-facing artifacts.** Replace numbered development versions with stable scientific names.
7. **Do not treat figures as decoration.** Caption, panel content, file asset, source data, and manuscript claim must all agree.
8. **Do not silently leave placeholders for “later”.** Submission exports must fail loudly on unresolved markers.
9. **Do not confuse a clean PDF with a clean DOCX.** Verify both when Word is the submission artifact.
10. **Do not deliver until the final regenerated artifact itself has been inspected.** An earlier successful render does not validate a later commit.

## Reusable project patterns

Read `references/project-lessons.md` for lessons generalized from prior manuscript, SI, CV, and journal-export projects. Use those patterns to anticipate failures before they recur.

Common cross-project examples include:
- duplicate reference numbering or missing bibliography entries;
- figures present in the repository but absent from Word;
- SI inventory claiming figures/tables that were never embedded;
- stale placeholders surviving into a “final” draft;
- one project stage overwriting a newer canonical main text;
- Unicode superscripts/symbols displaying differently across Word/PDF renderers;
- tables that look fine in Markdown but collapse in LibreOffice;
- final page or section gaps caused by figure/caption/table pagination;
- over-styled office defaults conflicting with a restrained academic house style;
- binary figures generated correctly but linked rather than embedded;
- manuscript text updated without captions/README/Data Availability following it.

## Release report

When reporting completion, state only:
- what canonical files were audited;
- which deterministic gates passed;
- page counts after rendering;
- any remaining known issues;
- exact deliverable paths/links.

Do not call a file “final” while known render defects remain.

## Resources

- `scripts/markdown_submission_audit.py`: generic source-level audit for manuscript/SI/BibTeX/image paths and export-risk patterns.
- `scripts/docx_structural_audit.py`: structural DOCX audit for equations, media, placeholders, version labels, tracked changes/comments, and literal LaTeX.
- `references/failure-catalog.md`: detailed failure modes, causes, detection, and prevention.
- `references/release-checklist.md`: concise release gate to use immediately before delivery.
- `references/project-lessons.md`: generalized lessons from prior scientific manuscript, SI, CV, and journal-export projects.
