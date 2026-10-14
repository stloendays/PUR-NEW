# Digital Discovery submission preparation

**Status (14 October 2026):** nonexperimental editorial and submission
engineering checklist. This is a project working document, not journal
manuscript text. The public journal instructions are at
https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/digital-discovery
and RSC general data policy is at
https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/data-sharing.

## What is ready in the repository

- Canonical English main paper: `manuscript/MAIN_TEXT_V5.md`.
- Canonical SI: `manuscript/SUPPLEMENTARY_INFORMATION_V5.md`, with
  23 Notes, 17 Tables and two Supplementary Figures.
- Five main figure files each in source/rendered formats under
  `analysis/figures_composite/`. For separate journal upload,
  existing PDF vector formats are preferable where the system
  accepts them; do not upsample a low-resolution PNG and label it
  600 dpi.
- Public analysis code, numerical outputs, experimental-method
  metadata, reproducibility index and physical hypothesis records.
- Paired reading-level PUR / SPE generality checks on original
  source measurements, with pinned-source provenance and independent CI.
- An automated manuscript + SI Word conversion which checks native
  equations and image embedding and creates rendered page images.

## RSC / Digital Discovery requirements identified

1. **Full paper** is an eligible article type. The main Results must
   highlight the most meaningful scientific evidence rather than
   duplicate SI detail.
2. A **Data Availability Statement (DAS)** is required at submission.
   Code and data must be inspectable by referees. The public GitHub
   repository and source-data pointers are currently stated in the
   main manuscript. Digital Discovery expects a **persistent
   repository DOI** for custom code and data upon acceptance,
   including DOIs for the current and archived code versions.
   Plan a versioned Zenodo deposit after the submission snapshot is
   approved; **no DOI has yet been assigned**.
3. The journal requires a **table-of-contents graphical entry at the
   revision stage**: a distinct, originally authored graphic,
   ideally 8 cm wide × 4 cm high, plus 1–2 short sentences
   (maximum 250 characters). Do not simply reuse a main Figure 1
   panel as the graphical entry. Graphics must comply with the
   journal's intellectual-property and AI-artwork requirements.
4. The initial submission includes a **cover letter**, manuscript,
   Supplementary Information and appropriate figure assets.
   Reviewer suggestions are handled by the submission system.
5. RSC guidance states that **funding, relevant contributions and
   any use of AI tools** should be disclosed in Acknowledgements
   or the appropriate editorial statement. Because generative
   models are also subjects/instruments of the paper, distinguish
   methodological model use (already in Methods) from any separate
   author-assistance disclosure, using the authors' actual records.
6. Original laboratory records, archived decision inputs, reference
   metadata and re-usable code must remain accessible to reviewers.
   A future DOI deposit is a packaging task, not a substitute for
   filling gaps in source evidence.

## Draft graphical-entry text

> Polyurethane melts can share a local temperature response yet differ
> in viscosity level and thermal-hold drift. One measured anchor and
> chemistry-aware rules select experiments that distinguish
> stabilization mechanisms.

The TOC text is 219 characters when spaces and line wraps are
normalised, within the stated 250-character limit. It describes the
scientific finding rather than a particular proposed graphic; do not
put this explanatory text onto the graphic.

## Items requiring coauthor confirmation

- Author list, order and exact name spellings.
- Official English organizational affiliation and
  corresponding-author contact details.
- Funding and Acknowledgements, including AI-use disclosure,
  where applicable.
- Conflicts-of-interest declaration, particularly when
  commercial affiliations are present; do not infer a conflict
  merely from affiliation, and do not assume none without review.
- Historical contemporaneous record of the F1 recommendation,
  if recoverable (see `docs/EXPERIMENTAL_CHRONOLOGY.md`).
- Original graphical-entry artwork and explicit license/commercial
  reuse basis, if any AI-assisted drawing is contemplated.
- Author approval of the exact submission commit and persistent
  code/data deposition plan.

## Completion gate

Before declaring a journal-upload package ready, inspect **every**
rendered page of the **final** manuscript and SI, check title/authors/
references/panel captions/tables/equations, and compare outputs with
`docs/SUBMISSION_SCIENTIFIC_EVIDENCE_MAP.md`. A successful
automated DOCX/PDF rendering run alone is not proof that no visual
layout issues remain. Planned S1C39/S1C41 and F1 sweep outcomes
must remain distinct from measured results.
