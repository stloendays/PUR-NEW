# Generalized Lessons from Prior Projects

These are reusable patterns, not project-specific scientific claims.

## Scientific manuscript projects

Across multiple manuscript workflows, the same classes of errors recurred:

- A repository could contain correct figures while the Word draft still lacked embedded images.
- Main text could be current while SI retained stale terminology, old panel inventories, or missing supporting evidence.
- Duplicate reference numbering and missing bibliography entries were invisible until a dedicated reference audit.
- Draft manuscripts could still contain placeholders for future figures, author notes, or incomplete sections even after the narrative seemed finished.
- Markdown/LaTeX sources could be scientifically correct but not yet represent a submission-ready ACS/RSC-style Word/PDF artifact.
- A final-looking PDF could hide that the DOCX itself contained raw LaTeX or broken native equations.
- Updating the manuscript without updating captions, README/provenance summaries, and Data Availability created cross-document drift.

## Word/PDF export projects

Repeated conversion lessons:

- Unicode superscripts and specialist symbols can render differently across Word, LibreOffice, and PDF.
- Native OMML is more reliable than visible LaTeX for equation-heavy Word submissions.
- Theme fonts and heading borders can override intended Times New Roman/black styling.
- Long captions and figures need explicit pagination rules.
- Bibliography spacing can create unnecessary final pages.
- Binary image generation is not enough: the final document must embed those assets.

## SI-heavy projects

SI is where release defects concentrate:

- long tables;
- dense formulas;
- robustness analyses;
- run-level records;
- stale development labels;
- figure/table numbering drift;
- references to assets that were planned but never embedded.

Therefore SI must be audited and visually rendered with the same rigor as the main paper.

## CV and formal-document projects

The same release-engineering principle also appeared outside manuscripts:

- visually restrained formatting can still fail because of overlap, tiny type, inconsistent alignment, or weak hierarchy;
- a document should be checked both visually and by text extraction;
- a one-page layout is not successful if it is cramped or unreadable;
- rules such as required competition/award names need deterministic content checks, not visual judgment alone;
- final QA benefits from both page-level visual inspection and semantic/content linting.

## Cross-project rule

Use both classes of validation:

1. **Semantic/deterministic checks** — source truth, required content, references, numbering, placeholders, equations, paths.
2. **Rendered visual checks** — pagination, clipping, table widths, fonts, figures, captions, spacing, glyphs.

Neither class can replace the other.
