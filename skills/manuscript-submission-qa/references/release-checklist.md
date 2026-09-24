# Final Release Checklist

Use this immediately before delivery.

## Canonical inputs
- [ ] Main manuscript source identified.
- [ ] SI source identified.
- [ ] Bibliography identified.
- [ ] Figure/table asset set identified.
- [ ] Analysis outputs supplying headline values identified.
- [ ] Exact commit/tag/run recorded.

## Scientific/content gate
- [ ] Main and SI title match.
- [ ] Author/affiliation/corresponding-author metadata are verified.
- [ ] Headline numbers match source outputs.
- [ ] Main and SI use the same sample counts, denominators, units, and terminology.
- [ ] Figure captions match actual panel content.
- [ ] Table headers/units/footnotes are current.
- [ ] References resolve; no duplicate bibliography keys.
- [ ] No unsupported mechanism claims.
- [ ] No TODO/FIXME/AUTHOR_INPUT_NEEDED/author notes.
- [ ] No reader-facing V-number/branch/run codenames unless scientifically necessary.

## Export-source gate
- [ ] No lone `$` display delimiters.
- [ ] No risky empty-base unit fragments such as `h$^{-1}$`.
- [ ] Image alt text will not create duplicate Pandoc captions.
- [ ] Figure paths exist.
- [ ] Temporary Word source removes drafting separators/notes.

## DOCX structural gate
- [ ] Expected figures are embedded.
- [ ] Native OMML equations are present where expected.
- [ ] No visible literal LaTeX commands.
- [ ] No unintended comments or tracked changes.
- [ ] Font/style normalization applied if needed.
- [ ] Tables have deterministic widths.
- [ ] Figures/captions have keep rules.

## Visual gate
- [ ] Every main-text page inspected at 100% zoom.
- [ ] Every SI page inspected at 100% zoom.
- [ ] No clipped/overlapping text.
- [ ] No collapsed tables.
- [ ] No duplicate/split captions.
- [ ] No broken equation boxes or strange math spacing.
- [ ] No missing/cropped figures.
- [ ] No unexplained large blank gaps.
- [ ] No orphan reference on an otherwise blank page.
- [ ] Fonts and colors are consistent.

## Delivery gate
- [ ] Final DOCX/PDF copied from the exact audited run.
- [ ] File names are reader-facing and do not expose internal development versions.
- [ ] Deliver only the requested final files; keep QA PNGs/PDFs internal unless requested.
