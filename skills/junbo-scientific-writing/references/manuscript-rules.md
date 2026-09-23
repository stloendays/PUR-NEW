# Manuscript Rules Reference

## 1. Story and claims

- Write the central claim in one sentence before drafting.
- Write 3-6 supporting claims in dependency order.
- Map every major claim to a decisive experiment, figure/table, statistical result, validated calculation, or citation.
- Prefer a small number of strong claims over many weak claims.
- Remove material that does not support the canonical story, reproducibility, or necessary context.
- When a new development line is still moving, keep it out of the canonical manuscript until frozen.

## 2. Abstract and keywords

Use this order where appropriate:

1. problem or failure mode;
2. unresolved gap;
3. main finding;
4. one to three decisive quantitative results;
5. mechanism or physical interpretation;
6. design/experiment-selection implication.

Default to a compact causal story rather than a numerical inventory. Roughly 150-220 words is a useful default unless the journal specifies otherwise. Remove secondary sample counts, candidate-space sizes, instrument details, implementation details, repeated denominators, and multiple metrics supporting the same point. Keep exact values only when they change the reader's belief in the central claim.

Do not hide the strongest baseline, null-model contrast, transfer result, or effect-size comparison if it materially changes how convincing the central claim is.

Use 4-6 keywords by default. Prefer one term each for the scientific object, central physical concept, major method, and decision/design concept. Delete redundant synonyms and generic AI vocabulary unless it is central to how the paper will be searched.

## 3. Introduction

- Move from field-level importance to the precise unresolved contradiction.
- Synthesize literature by scientific question, not author chronology.
- End with the study purpose and conceptual advance.
- Do not preview every result.
- If AI is downstream of a physical discovery, make the physical discovery lead the narrative.

## 4. Results

Default paragraph logic:

`Claim -> evidence -> comparison -> interpretation -> transition`.

- Put decisive numbers next to the claim they support.
- State denominators when a rate can otherwise be misread.
- Separate measured values, fitted descriptors, and post hoc adjudication.
- Do not let software names become the scientific headline.
- If a simple null model challenges a mechanism, compute it and report the contrast.
- Lead with what the result establishes scientifically; do not attach repository-development disclaimers to the same sentence unless chronology changes the scientific interpretation.

### Scientific-value protection

A later analysis can strengthen the scientific interpretation of an earlier workflow without being a historical input to that workflow.

**Bad main-text pattern**

`A single state anchor reduced prediction error substantially. This analysis was not part of the frozen Agent evidence contract.`

The second sentence is usually true but rhetorically misplaced: it converts a scientific result into an engineering-history disclaimer.

**Preferred main-text pattern**

`A single state-specific measurement reduced reconstruction error, demonstrating that formulation identity alone does not fully specify the realized state and that an in-domain anchor carries substantial state information.`

If chronology must be documented to protect causal attribution, place it in SI/provenance, for example:

`The frozen Agent series used evidence snapshot X; the later state-anchor analysis is reported independently and is not treated as a historical model input.`

The rule is: **do not retrofit later evidence into an earlier causal story, but do not demote an independently valid scientific result merely because it was obtained later.**

## 5. Discussion

- Explain observed behavior with evidence-supported chemistry/physics/process reasoning.
- Distinguish formulation-level mechanism from molecular mechanism.
- Distinguish mechanism from framework.
- State the correct generalization level without performative self-weakening.
- Translate the result into a reusable design principle where justified.

## 6. Conclusion

- State what understanding changed.
- State the principal mechanistic/conceptual distinction.
- State the design consequence.
- Do not repeat a list of methods and metrics.

## 7. Figures and tables

- Every main figure must answer a named scientific question.
- Every panel must support a claim, mechanism, comparison, or necessary context.
- Verify that every figure cited in the manuscript exists as a rendered artifact.
- Verify caption numbers and statistics after every analysis update.
- Do not leave a planned main figure only as a script or `Suggested content` note.
- Keep table captions bold in Junbo's house style unless the journal overrides it.

## 8. Terminology and engineering identifiers

Keep reader-facing scientific terminology stable. Keep these internal by default:

- run/job IDs;
- file paths;
- temporary aliases;
- commit hashes;
- branch names;
- prompt versions;
- engineering codenames;
- manuscript/architecture development labels such as V1/V2/V3/V4/V5.

Expose them only where reproducibility requires it.

### Final-stage semantic names

In the final manuscript and SI, replace internal development versions with names that describe scientific function. Use one stable name throughout Results, Methods, captions, tables, Data/Code Availability and exports.

Bad reader-facing sequence:

`V3 -> V4 -> V5`

Preferred scientific sequence:

`Candidate-Recovery Benchmark (CRB) -> Rule-Grounded Experiment Selection (RGES) -> Chemistry-Bounded Experiment Selection (CBES)`

Keep the historical mapping in repository provenance. If an internal filename contains a version label, cite a semantic alias or provenance index rather than exposing the implementation filename in the final reader-facing text.

## 9. Provenance

Maintain internally, where relevant:

- exact source datasets/releases;
- raw-to-processed lineage;
- analysis scripts;
- model/statistical settings;
- computation settings;
- repository commits/releases;
- checksums/manifests;
- final figure/table source files.

Do not dump this ledger into Results. Surface only the reproducibility subset through Methods, SI, Data/Code Availability, or repository documentation.

## 10. Canonical-story audit

Compare at minimum:

- title;
- Abstract;
- Introduction closing paragraph;
- Results section headings and headline numbers;
- Discussion/Conclusion;
- equations and notation;
- figure captions;
- table captions;
- SI summary/tables;
- Data/Code Availability;
- README manuscript-facing text;
- DOCX/PDF/Google Docs exports.

Resolve mismatches using verified current evidence, not older prose.

## 11. Language audit

Prefer precise verbs such as `shows`, `reveals`, `establishes`, `identifies`, `quantifies`, `demonstrates`, or `supports` when justified.

Avoid empty filler and AI-flavored title/prose terms when a concrete scientific phrase is available. Examples to question rather than automatically use:

- evidence-grounded;
- AI-guided;
- intelligent framework;
- holistic framework;
- comprehensive framework;
- paradigm;
- unprecedented;
- groundbreaking.

Do not weaken a supported mechanism merely to sound cautious.

## 12. Formatting audit

Unless a mandatory journal template overrides it:

- Times New Roman;
- black text;
- body text >= 10 pt;
- restrained layout;
- stable heading hierarchy;
- consistent equation, symbol, and unit typography.

## 13. Author metadata

- Use the current confirmed author order and affiliations from the project.
- Never invent corresponding-author email, ORCID, funding, affiliation, or company legal name.
- Verify official institution/company English names before submission when not confirmed.

## 14. Submission blockers

Do not call a manuscript submission-ready while any of these remain:

- Author notes / next-revision notes;
- TODO / FIXME;
- placeholder release/DOI language;
- missing main figures;
- stale figure captions;
- equation/prose mismatch with analysis code;
- unresolved author metadata;
- unverified bibliography metadata;
- raw LaTeX visible in Word;
- new exploratory results described as finalized evidence.
