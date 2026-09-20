# Manuscript Rules Reference

## 1. Story and claims

- Write the central claim in one sentence before drafting.
- Write 3-6 supporting claims in dependency order.
- Map every major claim to a decisive experiment, figure/table, statistical result, validated calculation, or citation.
- Prefer a small number of strong claims over many weak claims.
- Remove material that does not support the canonical story, reproducibility, or necessary context.
- When a new development line is still moving, keep it out of the canonical manuscript until frozen.

## 2. Abstract

Use this order where appropriate:

1. problem or failure mode;
2. unresolved gap;
3. main finding;
4. decisive quantitative evidence;
5. mechanism or physical interpretation;
6. design/experiment-selection implication.

Do not hide the strongest baseline or transfer result if it materially changes how convincing the central claim is.

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
- engineering codenames.

Expose them only where reproducibility requires it.

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
