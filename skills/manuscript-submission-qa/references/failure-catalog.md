# Failure Catalog

Use this file when diagnosing a manuscript/SI export or designing a release pipeline. The pattern is: **symptom -> likely cause -> detection -> prevention**.

## 1. Canonical-source drift

### New main text + old SI / old figures / old bibliography
- **Symptom:** numbers, terminology, figure captions, or Data Availability disagree across artifacts.
- **Cause:** files were exported from different commits or branches.
- **Detect:** compare commit/source hashes; run cross-document audit; inspect figure generation metadata.
- **Prevent:** freeze one release input set and export everything from that exact state.

### Old Word silently overriding repository truth
- **Symptom:** a polished DOCX contains superseded wording or statistics.
- **Cause:** office edits became an accidental source of truth.
- **Prevent:** treat DOCX/PDF as derived artifacts unless the project explicitly makes them canonical.

## 2. Draft residue and development-history leakage

### TODO / FIXME / AUTHOR_INPUT_NEEDED / author notes
- **Symptom:** internal drafting instructions appear in a submission file.
- **Prevent:** make unresolved markers release blockers, not warnings.

### V3 / V4 / V5 / branch names in reader-facing prose
- **Symptom:** paper reads like project history rather than science.
- **Prevent:** use stable scientific-function names in manuscript/SI; preserve development labels only in provenance.

### Superseded figures/results still cited
- **Symptom:** obsolete intermediate results remain in captions, SI, README, or text.
- **Prevent:** reader-facing material should use only the current validated scientific basis unless history changes interpretation.

## 3. Pandoc / Markdown caption failures

### Duplicate figure captions
- **Symptom:** Word shows a short caption from image alt text plus the authored full caption.
- **Cause:** Pandoc interprets nonempty image alt text as a figure caption.
- **Detect:** source contains `![descriptive text](...)` followed by a separate full caption paragraph.
- **Prevent:** blank image alt text only in the temporary Word-export source while retaining the canonical descriptive alt text.

### Caption split across pages
- **Symptom:** half of a long caption is on one page and the rest on the next.
- **Prevent:** bind image paragraph to the following caption and set caption `keep_together`.

### Figure separated from discussion by large blank area
- **Symptom:** figure is pushed to the next page, leaving a large gap.
- **Prevent:** modestly resize the figure/caption, adjust keep rules, and fix local pagination rather than shrinking the entire manuscript.

## 4. Math and unit conversion failures

### Lone `$` display delimiters
- **Symptom:** visible raw LaTeX, broken formula fragments, or strange spacing.
- **Cause:** display math was written as a line containing a single `$` instead of `$$`.
- **Prevent:** reject single-dollar delimiter lines automatically.

### Empty-base superscript/subscript boxes
- **Symptom:** square box before `-1`, superscript, or unit exponent.
- **Cause:** fragments such as `h$^{-1}$` or `mol$^{-1}$` create an empty mathematical base in some Word/LibreOffice conversions.
- **Prevent:** write ordinary text units (`h⁻¹`, `mol⁻¹`) or a complete math expression when mathematically necessary.

### Units look like widely spaced variables
- **Symptom:** `k J m o l`-like spacing in Word.
- **Cause:** human-readable units were rendered inside math mode.
- **Prevent:** variables in math; ordinary scientific units in text when possible.

### Literal LaTeX survives conversion
- **Symptom:** `\\eta`, `\\frac`, `\\approx`, `\\mathrm` visible in Word.
- **Prevent:** inspect DOCX XML for literal LaTeX and require native OMML for equation-heavy documents.

### Unicode symbol mismatch across Word/PDF
- **Symptom:** superscripts, rho/kappa, minus signs, arrows, or special symbols render differently by viewer.
- **Prevent:** test the actual target DOCX and rendered PDF; prefer robust Unicode or native OMML deliberately rather than mixing styles unpredictably.

## 5. Table failures

### Markdown table collapses into narrow columns in LibreOffice
- **Symptom:** narrative columns become almost one word per line; table looks vertically stacked.
- **Cause:** percentage widths, unresolved styles, or renderer-specific interpretation of `tcW`/table grid.
- **Prevent:** rebuild/set deterministic table and cell widths; set fixed layout; use `cell.width` as well as OOXML width; remove unresolved styles; visually inspect every table.

### Equal-width columns waste space
- **Symptom:** short numeric fields are too wide while narrative fields wrap excessively.
- **Prevent:** allocate compact widths to numbers/status fields and wider widths to narrative columns.

### SI table unreadable after fitting to page
- **Symptom:** font becomes tiny or cells clip.
- **Prevent:** allow multi-page tables with repeated headers; do not force every table onto one page.

## 6. Font/style drift

### Title becomes sans serif or colored
- **Symptom:** body is Times New Roman but title/headings switch fonts or colors.
- **Cause:** theme/style inheritance in Word or LibreOffice.
- **Prevent:** normalize paragraph styles and run-level font/color after conversion.

### Blue line below title
- **Symptom:** decorative horizontal rule appears under title.
- **Cause:** border stored in the Title style, not the paragraph itself.
- **Prevent:** remove paragraph borders from both direct formatting and style definitions.

### Unexpected hyperlink glyph or color in references
- **Symptom:** colored trailing symbol or odd hyperlink rendering.
- **Cause:** renderer-specific hyperlink styling.
- **Prevent:** unwrap bibliography-wide hyperlinks when they are visually defective while preserving text runs.

## 7. Figure asset failures

### Figure exists in repository but not Word
- **Symptom:** manuscript source points to a figure, but Word has no embedded media.
- **Cause:** linked path, unsupported format, stale export source, or missing resource path.
- **Prevent:** count embedded media in DOCX and inspect rendered pages.

### Stale screenshot exported instead of current vector/raster figure
- **Symptom:** caption statistics are current but plotted data/labels are old.
- **Prevent:** regenerate figure from versioned data and use one canonical figure path.

### Figure inventory says “complete” but files are missing
- **Symptom:** README/SI lists figures that never render or were placeholders.
- **Prevent:** inventory must be generated/checked against actual files, not plans.

### Constructed structure graphic presented as experimental evidence
- **Symptom:** illustrative molecular/structural render is read as measured mechanism.
- **Prevent:** caption explicitly states schematic/constructed context unless supported by direct characterization.

## 8. Reference and bibliography failures

### Duplicate numbering or missing reference key
- **Symptom:** repeated citation number or uncited/missing BibTeX entry.
- **Prevent:** use citeproc where possible; audit citation keys vs bibliography; reject duplicate BibTeX keys.

### Final reference alone on nearly blank last page
- **Symptom:** one citation spills onto a new page.
- **Prevent:** compact bibliography spacing before changing body typography.

### Reference metadata not verified
- **Symptom:** DOI/title/year mismatch.
- **Prevent:** verify metadata before submission; do not infer missing DOI or author details.

## 9. SI-specific failures

### Main text is polished but SI is stale
- **Symptom:** SI still contains old terminology, old sample counts, placeholders, obsolete panel inventory, or development labels.
- **Prevent:** SI receives the same final audit as main text and must be rendered page-by-page.

### Missing supporting figures/tables despite SI references
- **Symptom:** references to S15/S16 or panels that do not exist.
- **Prevent:** enforce continuous numbering and path existence.

### Robustness analysis appears stronger than evidence
- **Symptom:** sensitivity result is phrased as mechanistic proof.
- **Prevent:** keep robustness/sensitivity interpretation at its correct evidence level.

## 10. Release-process failures

### Earlier successful artifact delivered after later edits
- **Symptom:** user receives a file that predates the final fixes.
- **Prevent:** final deliverable must come from the exact commit/run that passed the last audit.

### CI is green but document is visually wrong
- **Symptom:** file opens and tests pass, but layout is broken.
- **Prevent:** rendering and human visual review are an independent gate.

### Manual one-off patch only in DOCX
- **Symptom:** next export reintroduces the defect.
- **Prevent:** fix preprocessing/postprocessing/CI whenever the defect is deterministic.

### “Final” claimed before visual QA
- **Symptom:** later review still finds clipping, broken equations, or spacing defects.
- **Prevent:** reserve “final” for the artifact that has itself been rendered and inspected.

### Audit script false positives from OOXML prefix matching
- **Symptom:** a structural checker reports tracked changes because it matches `<w:insideH>` as if it were `<w:ins>`, or reports comments because an empty `comments.xml` part exists.
- **Cause:** substring matching instead of tag-aware checks.
- **Prevent:** match complete OOXML tag names/boundaries and inspect whether comment elements actually exist; test the checker against a known-clean DOCX.
